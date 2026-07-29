"""CLI orchestrator cho tầng thí nghiệm đặc trưng văn bản (``experiments/``).

Module này cung cấp một giao diện dòng lệnh (CLI) để điều phối một thí nghiệm
đi qua **đúng cùng một pipeline huấn luyện** của baseline v0, wiring các thành
phần nền tảng đã hiện thực ở task 3–6:

- ``experiments.common.snapshot`` — Baseline_Snapshotter (đóng băng baseline_v0).
- ``experiments.common.runner`` — ExperimentRunner (cầu nối tới ``task10_train``).
- ``experiments.common.reporting`` — Comparison_Reporter (sinh báo cáo so sánh).

CLI này **chạy song song** và **không thay thế** ``pipeline/run_pipeline.py``;
nó không sửa đổi hành vi mặc định của các TASK sản xuất (1–11).

Các cách gọi (theo mục "Orchestration" của design):

.. code-block:: text

    python -m experiments.run_experiment --snapshot
    python -m experiments.run_experiment --experiment A2
    python -m experiments.run_experiment --experiment A1a
    python -m experiments.run_experiment --experiment B3 --report

Thứ tự điều phối khi có ``--experiment {id}`` (Req 1.5, 2.1, 2.2, 13.1):

1. Snapshot baseline nếu chưa có — gọi ``create_baseline_snapshot()`` (idempotent,
   tự no-op khi baseline đã tồn tại).
2. Build tập đặc trưng cho thí nghiệm — điều phối qua một **registry** ánh xạ
   ``experiment_id -> builder callable`` bằng **import mềm** (try/except
   ImportError). Các module feature-builder (a1/a2/a3/...) chưa hiện thực ở
   task 9+, nên nếu builder chưa có, kiểm tra xem tệp đặc trưng
   (``feature_path(id)``) đã tồn tại chưa; nếu có → tiếp tục, nếu không → log rõ
   ràng và dừng nhẹ nhàng.
3. Chạy runner — ``build_experiment_config(id, cutoff)`` rồi
   ``run_experiment_training(cfg)``.
4. Chạy Comparison_Reporter — ``generate_comparison_report(id, result, ...)``.

_Requirements: 1.5, 2.1, 2.2, 13.1_
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Callable, Optional

from experiments.common.reporting import (
    generate_comparison_report,
    generate_text_representation_table,
    write_text_representation_table,
)
from experiments.common.runner import (
    RunnerResult,
    build_experiment_config,
    feature_path,
    report_path,
    run_experiment_training,
)
from experiments.common.snapshot import create_baseline_snapshot

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_CUTOFF",
    "FeatureBuilder",
    "resolve_feature_builder",
    "run_snapshot",
    "run_experiment",
    "run_report_only",
    "build_arg_parser",
    "main",
]

# Train_Cutoff mặc định theo thời gian (Req 4.1). Trùng với mặc định của runner.
DEFAULT_CUTOFF = "2025Q1"

# Kiểu của một feature builder: hàm không đối số, ghi ra tệp đặc trưng version hóa.
FeatureBuilder = Callable[[], object]


# ---------------------------------------------------------------------------
# Feature builder registry — điều phối bằng import mềm (forward-compatible)
# ---------------------------------------------------------------------------

# Ánh xạ experiment_id -> (module_path, function_name) của builder tương ứng.
# Các module này CHƯA được hiện thực ở task hiện tại (task 9+), nên việc import
# được thực hiện "mềm" (lazy, có try/except) trong ``resolve_feature_builder``
# để ``run_experiment.py`` import sạch hôm nay và tương thích ngược về sau.
_FEATURE_BUILDER_REGISTRY: dict[str, tuple[str, str]] = {
    "A2": ("experiments.a2_negation", "build_a2_features"),
    "A1a": ("experiments.a1_group_sentiment", "build_a1a_features"),
    "A1b": ("experiments.a1_group_sentiment", "build_a1b_features"),
    "A3": ("experiments.a3_velocity", "build_a3_features"),
    "A6": ("experiments.a6_llm_sentiment", "build_a6_features"),
    "A7": ("experiments.a7_llm_scorecard", "build_a7_features"),
    "B1": ("experiments.b1_distant_supervision", "build_b1_features"),
    "B3": ("experiments.b3_segmentation", "build_b3_features"),
    "A4": ("experiments.a4_tfidf_crossticker", "build_a4_features"),
    "A5": ("experiments.a5_embeddings", "build_a5_features"),
    "B4": ("experiments.b4_spillover", "build_b4_features"),
    "B5": ("experiments.b5_anomaly", "build_b5_features"),
}


def resolve_feature_builder(experiment_id: str) -> Optional[FeatureBuilder]:
    """Trả về builder callable cho ``experiment_id`` nếu module đã hiện thực.

    Dùng **import mềm**: nếu module hoặc hàm builder chưa tồn tại (các thí nghiệm
    a1/a2/... hiện thực ở task 9+), trả về ``None`` thay vì ném ImportError. Nhờ
    đó ``run_experiment.py`` luôn import sạch và tương thích ngược.

    Args:
        experiment_id: Mã thí nghiệm (``"A2"``, ``"A1a"``, ...).

    Returns:
        Hàm builder không đối số nếu có sẵn; ngược lại ``None``.
    """
    entry = _FEATURE_BUILDER_REGISTRY.get(experiment_id)
    if entry is None:
        logger.info(
            "Không có builder đăng ký cho experiment_id='%s' trong registry.",
            experiment_id,
        )
        return None

    module_path, func_name = entry
    try:
        import importlib

        module = importlib.import_module(module_path)
    except ImportError:
        # Module builder chưa được hiện thực — hành vi mong đợi ở giai đoạn này.
        logger.info(
            "Module feature builder '%s' chưa được hiện thực (import mềm).",
            module_path,
        )
        return None

    builder = getattr(module, func_name, None)
    if builder is None or not callable(builder):
        logger.info(
            "Module '%s' chưa expose hàm builder '%s' (import mềm).",
            module_path,
            func_name,
        )
        return None
    return builder


# ---------------------------------------------------------------------------
# Các bước điều phối
# ---------------------------------------------------------------------------


def run_snapshot(force: bool = False) -> None:
    """Bước 1: đóng băng baseline_v0 (Req 1.5).

    Gọi ``create_baseline_snapshot()`` — idempotent, tự no-op khi baseline đã
    tồn tại (thỏa mãn "snapshot baseline nếu chưa có").

    Args:
        force: Nếu ``True``, ghi đè snapshot dù đã tồn tại.
    """
    result = create_baseline_snapshot(force=force)
    if result.already_existed:
        logger.info("Baseline_v0 đã tồn tại — giữ nguyên (không đóng băng lại).")
    else:
        logger.info(
            "Đã đóng băng Baseline_v0: %d tệp copied, %d tệp thiếu.",
            len(result.copied),
            len(result.missing),
        )


def _build_feature_set(experiment_id: str) -> bool:
    """Bước 2: build tập đặc trưng cho thí nghiệm (Req 2.1).

    - Nếu có builder đăng ký và import được → gọi builder để ghi tệp đặc trưng.
    - Nếu builder chưa hiện thực → kiểm tra tệp ``feature_path(id)`` đã có chưa:
      * đã có → tiếp tục (dùng lại tệp đặc trưng sẵn có);
      * chưa có → log rõ ràng rằng builder chưa hiện thực và báo không thể tiếp.

    Args:
        experiment_id: Mã thí nghiệm.

    Returns:
        ``True`` nếu tập đặc trưng đã sẵn sàng để chạy runner; ``False`` nếu
        không thể tiếp tục (builder chưa có và tệp đặc trưng cũng chưa tồn tại).
    """
    builder = resolve_feature_builder(experiment_id)
    fpath = feature_path(experiment_id)

    if builder is not None:
        logger.info("Đang build tập đặc trưng cho '%s' qua builder...", experiment_id)
        builder()
        if not Path(fpath).exists():
            logger.warning(
                "Builder cho '%s' đã chạy nhưng không thấy tệp đặc trưng '%s'.",
                experiment_id,
                fpath,
            )
            return False
        return True

    # Không có builder — thử dùng tệp đặc trưng đã tồn tại (nếu có).
    if Path(fpath).exists():
        logger.info(
            "Feature builder cho '%s' chưa hiện thực, nhưng tệp đặc trưng '%s' "
            "đã tồn tại — dùng lại và tiếp tục.",
            experiment_id,
            fpath,
        )
        return True

    logger.warning(
        "Feature builder cho experiment_id='%s' chưa được hiện thực và tệp đặc "
        "trưng '%s' cũng chưa tồn tại. Bỏ qua thí nghiệm này. (Các builder "
        "a1/a2/a3/... sẽ được thêm ở task 9+.)",
        experiment_id,
        fpath,
    )
    return False


def _count_feature_columns(csv_path: Path) -> Optional[int]:
    """Đếm số cột đặc trưng (loại trừ cột khóa) của một tệp feature CSV.

    Đọc chỉ dòng header để lấy danh sách cột, rồi loại ``ticker``/``quarter_id``
    (và ``label_basic`` nếu có). Trả về ``None`` nếu tệp thiếu hoặc lỗi đọc.
    """
    if not csv_path.exists():
        return None
    try:
        import pandas as pd

        cols = list(pd.read_csv(csv_path, nrows=0, encoding="utf-8").columns)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Không đọc được header tệp đặc trưng '%s': %s.", csv_path, exc)
        return None
    meta = {"ticker", "quarter_id", "label_basic"}
    return len([c for c in cols if c not in meta])


def _load_report_extras(experiment_id: str) -> dict:
    """Thu thập các tham số báo cáo tùy chọn theo từng thí nghiệm.

    - A2: nạp sidecar ``reports/experiment_A2_flip_stats.json`` do
      :func:`experiments.a2_negation.build_a2_features` ghi ra, chứa % số lần
      khớp bị đảo polarity (Req 5.7), truyền qua ``flip_stats``.
    - A1a/A1b: đếm số cột đặc trưng của tệp thí nghiệm đối chiếu tệp v0
      ``data/features/keyword_features.csv`` và truyền qua ``feature_counts``
      (Req 6.5).

    Trả về dict rỗng cho mọi thí nghiệm khác (giữ tương thích ngược).
    """
    extras: dict = {}
    if experiment_id == "A2":
        stats_path = Path("reports/experiment_A2_flip_stats.json")
        if stats_path.exists():
            try:
                import json

                extras["flip_stats"] = json.loads(
                    stats_path.read_text(encoding="utf-8")
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Không đọc được sidecar thống kê flip A2 '%s': %s.",
                    stats_path,
                    exc,
                )
    elif experiment_id in ("A1a", "A1b"):
        exp_count = _count_feature_columns(Path(feature_path(experiment_id)))
        v0_count = _count_feature_columns(
            Path("data/features/keyword_features.csv")
        )
        extras["feature_counts"] = {
            "exp_feature_count": exp_count,
            "v0_feature_count": v0_count,
        }
    return extras


def run_experiment(
    experiment_id: str,
    cutoff: str = DEFAULT_CUTOFF,
    with_report: bool = True,
) -> Optional[RunnerResult]:
    """Chạy toàn bộ luồng thí nghiệm cho ``experiment_id`` theo đúng thứ tự.

    Thứ tự (Req 1.5, 2.1, 2.2, 13.1):
    1. Snapshot baseline nếu chưa có (idempotent).
    2. Build tập đặc trưng (qua registry + import mềm; dùng lại tệp nếu có).
    3. Chạy runner: ``build_experiment_config`` → ``run_experiment_training``.
    4. Chạy Comparison_Reporter: ``generate_comparison_report`` (nếu
       ``with_report=True``).

    Args:
        experiment_id: Mã thí nghiệm (``"A2"``, ``"A1a"``, ``"B3"``, ...).
        cutoff: Train_Cutoff theo thời gian (mặc định ``"2025Q1"``).
        with_report: Nếu ``True``, chạy bước 4 (Comparison_Reporter). Bước báo
            cáo là yêu cầu quan trọng nhất nên mặc định luôn chạy.

    Returns:
        :class:`RunnerResult` của thí nghiệm nếu chạy được tới bước runner;
        ``None`` nếu dừng nhẹ nhàng ở bước build feature (builder chưa hiện thực).
    """
    logger.info("=== Bắt đầu thí nghiệm '%s' (cutoff=%s) ===", experiment_id, cutoff)

    # Bước 1: snapshot baseline nếu chưa có (idempotent).
    run_snapshot()

    # Bước 2: build tập đặc trưng.
    if not _build_feature_set(experiment_id):
        logger.warning(
            "Dừng thí nghiệm '%s' vì tập đặc trưng chưa sẵn sàng.", experiment_id
        )
        return None

    # Bước 3: chạy runner qua cùng pipeline huấn luyện (Req 14.1).
    cfg = build_experiment_config(experiment_id, cutoff=cutoff)
    logger.info("Đang chạy runner cho '%s'...", experiment_id)
    result = run_experiment_training(cfg)

    # Bước 4: sinh báo cáo so sánh với baseline_v0 (Req 13.1).
    if with_report:
        logger.info("Đang sinh báo cáo so sánh cho '%s'...", experiment_id)
        report_kwargs = _load_report_extras(experiment_id)
        out_path = generate_comparison_report(experiment_id, result, **report_kwargs)
        logger.info("Đã ghi báo cáo: '%s'.", out_path)
    else:
        logger.info(
            "Bỏ qua bước báo cáo cho '%s' (with_report=False).", experiment_id
        )

    logger.info("=== Hoàn tất thí nghiệm '%s' ===", experiment_id)
    return result


def run_report_only() -> str:
    """Chạy bước Comparison_Reporter độc lập: sinh bảng 4 tầng biểu diễn văn bản.

    Khi ``--report`` được dùng mà KHÔNG có ``--experiment``, tái sinh bảng tổng
    hợp Δ(C−A) của các tầng biểu diễn văn bản (v0, A2, A1a, A6) từ các tệp
    ``model_comparison*.csv`` sẵn có (Req 13.8). Không huấn luyện lại mô hình.

    Ngoài việc in bảng ra stdout, hàm còn **persist** bảng ra
    ``reports/text_representation_summary.md`` (qua
    :func:`write_text_representation_table`) để có thể trích thẳng vào luận văn.
    Bước persist được bọc chống lỗi: nếu ghi tệp thất bại, chỉ log cảnh báo mà
    không làm hỏng CLI.

    Returns:
        Chuỗi bảng Markdown đã sinh (cũng được in ra stdout).
    """
    logger.info("Đang sinh bảng tổng hợp các tầng biểu diễn văn bản...")
    table = generate_text_representation_table()
    print(table)

    # Persist bảng ra tệp báo cáo để dùng trong luận văn (Req 13.8). Bọc chống
    # lỗi để việc ghi tệp không bao giờ làm crash CLI.
    try:
        out_path = write_text_representation_table()
        logger.info("Đã persist bảng tổng hợp tầng biểu diễn: '%s'.", out_path)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(
            "Không persist được bảng tổng hợp tầng biểu diễn văn bản: %s.", exc
        )

    return table


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    """Dựng ``ArgumentParser`` cho CLI orchestrator.

    Returns:
        Parser với các đối số ``--snapshot``, ``--experiment``, ``--report``,
        ``--cutoff``.
    """
    parser = argparse.ArgumentParser(
        prog="python -m experiments.run_experiment",
        description=(
            "Điều phối một thí nghiệm đặc trưng văn bản qua cùng pipeline huấn "
            "luyện của baseline_v0. Chạy song song với pipeline/run_pipeline.py."
        ),
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Chỉ đóng băng baseline_v0 (create_baseline_snapshot).",
    )
    parser.add_argument(
        "--experiment",
        metavar="ID",
        default=None,
        help="Mã thí nghiệm cần chạy (ví dụ A2, A1a, A3, B3).",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help=(
            "Chạy bước Comparison_Reporter. Kèm --experiment: đảm bảo sinh báo "
            "cáo cho thí nghiệm. Đứng một mình: tái sinh bảng 4 tầng biểu diễn "
            "văn bản (generate_text_representation_table)."
        ),
    )
    parser.add_argument(
        "--cutoff",
        default=DEFAULT_CUTOFF,
        help=f"Train_Cutoff theo thời gian (mặc định {DEFAULT_CUTOFF}).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ép ghi đè baseline_v0 khi đóng băng (dùng với --snapshot).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Điểm vào CLI.

    Args:
        argv: Danh sách tham số dòng lệnh (mặc định ``None`` → dùng ``sys.argv``).

    Returns:
        Mã thoát: ``0`` thành công; ``2`` khi không có hành động nào được yêu cầu.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Trường hợp --snapshot: chỉ đóng băng baseline rồi thoát.
    if args.snapshot and args.experiment is None:
        run_snapshot(force=args.force)
        return 0

    # Trường hợp có --experiment: chạy toàn bộ luồng (bước báo cáo luôn chạy vì
    # là yêu cầu quan trọng nhất; --report chỉ nhấn mạnh ý định đó).
    if args.experiment is not None:
        # --snapshot đi kèm --experiment vẫn hợp lệ: bước 1 của luồng đã snapshot.
        run_experiment(
            args.experiment,
            cutoff=args.cutoff,
            with_report=True,
        )
        return 0

    # Trường hợp chỉ --report (không --experiment): bảng tổng hợp 4 tầng.
    if args.report:
        run_report_only()
        return 0

    # Không có hành động nào được yêu cầu.
    parser.print_help()
    logger.warning(
        "Không có hành động nào được yêu cầu. Dùng --snapshot, --experiment {id}, "
        "hoặc --report."
    )
    return 2


if __name__ == "__main__":  # pragma: no cover - entrypoint
    raise SystemExit(main())
