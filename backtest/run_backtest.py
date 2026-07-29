"""CLI orchestrator (`backtest/run_backtest.py`) — điểm chạy dòng lệnh (Req 10.5).

Module này cung cấp một giao diện dòng lệnh (CLI) để chạy từng thành phần của
backtest hoặc toàn bộ chuỗi (`--all`), sinh mọi artifact/báo cáo đưa thẳng vào
luận văn (Req 10.5). CLI **chỉ điều phối** — mọi logic nghiệp vụ nằm ở các module
thành phần (`signals`, `strategy`, `benchmarks`, `metrics`, `walk_forward`,
`interpret`, `leakage_audit`, `reporting`); ở đây không nhân bản logic.

Các cờ hành động:

- ``--all``        chạy toàn bộ chuỗi theo thứ tự cố định (xem dưới);
- ``--signals``    chỉ sinh Prediction_Signal (và mô phỏng chiến lược + benchmark
                   + chỉ số trên chính tín hiệu đó);
- ``--walk-forward`` chạy Walk_Forward_Evaluator qua nhiều cutoff;
- ``--interpret``  diễn giải mô hình (SHAP + permutation importance);
- ``--audit``      kiểm toán rò rỉ dữ liệu thời gian;
- ``--report``     sinh báo cáo Markdown tổng hợp từ các artifact hiện có.

Các tùy chọn: ``--model`` (mặc định ``"LightGBM"``), ``--cutoff`` (mặc định
``"2025Q1"``), ``--top-n`` (số mã tối đa mỗi kỳ theo xác suất, tùy chọn).

Thứ tự ``--all`` (theo design.md §CLI orchestrator, Req 10.5):

    signals → strategy+benchmarks → metrics → walk-forward → interpret → audit
    → report

Chịu lỗi theo từng giai đoạn: một giai đoạn lỗi được ghi log và bỏ qua để các
giai đoạn sau và báo cáo cuối (vốn degrade gracefully) vẫn chạy được, tạo ra tối
đa artifact có thể. Mã thoát khác 0 nếu có bất kỳ giai đoạn nào thất bại.

Ví dụ::

    python -m backtest.run_backtest --all
    python -m backtest.run_backtest --signals --model LightGBM
    python -m backtest.run_backtest --walk-forward
    python -m backtest.run_backtest --interpret --audit --report

Ghi chú về ``--interpret``: :func:`~backtest.interpret.interpret_technical_model`
cần một mô hình *đã fit* cùng ``X_test``/``y_test``/tên đặc trưng — những thứ mà
:func:`~backtest.signals.generate_signals` không trả về (nó chỉ trả nhãn + xác
suất). Để tránh sửa ``pipeline/task10_train.py``, hàm :func:`_fit_technical_model`
tái dùng ĐÚNG các helper cấp thấp của pipeline (giống hệt cách ``generate_signals``
làm) để huấn luyện lại ``Config_A`` một cách leakage-safe (imputer fit trên train,
transform test) và lấy ra ``(model, X_test, y_test, feature_names)``.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

import pandas as pd

from backtest.benchmarks import buy_and_hold_equal, equal_weight_rebalanced
from backtest.costs import CostConfig
from backtest.interpret import interpret_technical_model
from backtest.leakage_audit import audit_leakage
from backtest.metrics import evaluate_all
from backtest.reporting import generate_backtest_report
from backtest.signals import generate_signals
from backtest.strategy import StrategyConfig, simulate_strategy
from backtest.walk_forward import run_walk_forward
from pipeline.logging_config import setup_logger
from pipeline.task10_train import (
    KW_FEATURES_PATH,
    LABELS_PATH,
    TECH_FEATURES_PATH,
    build_ml_models,
    get_feature_configs,
    identify_feature_columns,
    load_and_merge_data,
    time_series_split,
)
from backtest.signals import _prepare_train_test_matrices  # helper leakage-safe

logger = setup_logger("BACKTEST_CLI")

# Đường dẫn artifact mặc định (đồng bộ với các module thành phần).
DEFAULT_SIGNALS_PATH = "reports/signals.csv"
DEFAULT_PERFORMANCE_PATH = "reports/backtest_performance.csv"


# ---------------------------------------------------------------------------
# Giai đoạn: tín hiệu (Req 1)
# ---------------------------------------------------------------------------

def run_signals_stage(
    model_name: str,
    cutoff: str,
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
    signals_path: str = DEFAULT_SIGNALS_PATH,
) -> pd.DataFrame:
    """Sinh Prediction_Signal và lưu ra CSV (Req 1).

    Huấn luyện Technical_Model trên ``Config_A`` với *model_name*/*cutoff* đã cho,
    trả về SignalFrame để các giai đoạn sau (chiến lược/benchmark) tái dùng, và
    ghi ``reports/signals.csv`` để tiện kiểm tra.

    Args:
        model_name: Thuật toán huấn luyện (``"auto"`` → chọn BA cao nhất).
        cutoff: Train_Cutoff.
        tech_path, kw_path, labels_path: đường dẫn dữ liệu đầu vào.
        signals_path: nơi lưu SignalFrame.

    Returns:
        SignalFrame (``pd.DataFrame``).
    """
    signals = generate_signals(
        tech_path=tech_path,
        kw_path=kw_path,
        labels_path=labels_path,
        cutoff=cutoff,
        model_name=model_name,
        config="Config_A",
    )

    # Ghi SignalFrame ra CSV để kiểm tra/tái dùng thủ công.
    from pathlib import Path

    out = Path(signals_path)
    if out.parent != Path(""):
        out.parent.mkdir(parents=True, exist_ok=True)
    signals.to_csv(out, index=False)

    n_up = int((signals["pred_label"] == 1).sum())
    logger.info(
        "Tín hiệu: %d hàng, %d mã dự báo 'tăng' (%.1f%%), %d kỳ → %s",
        len(signals),
        n_up,
        100.0 * n_up / max(len(signals), 1),
        signals["quarter_id"].nunique(),
        signals_path,
    )
    return signals


# ---------------------------------------------------------------------------
# Giai đoạn: chiến lược + benchmark + chỉ số (Req 2, 3, 4, 5)
# ---------------------------------------------------------------------------

def run_strategy_metrics_stage(
    signals: pd.DataFrame,
    top_n: Optional[int] = None,
    performance_path: str = DEFAULT_PERFORMANCE_PATH,
) -> pd.DataFrame:
    """Mô phỏng chiến lược mô hình + benchmark rồi chấm chỉ số (Req 2–5).

    Chạy :func:`~backtest.strategy.simulate_strategy` cho chiến lược mô hình (áp
    :class:`~backtest.costs.CostConfig` để có kịch bản net; dùng *top_n* nếu có),
    cùng hai benchmark long-only, rồi gọi
    :func:`~backtest.metrics.evaluate_all` để ghi
    ``reports/backtest_performance.csv``.

    Args:
        signals: SignalFrame từ giai đoạn tín hiệu.
        top_n: Biến thể top-N theo xác suất (``None`` → chọn mọi mã "tăng").
        performance_path: đường dẫn CSV chỉ số đầu ra.

    Returns:
        ``pd.DataFrame`` bảng chỉ số hiệu quả.
    """
    model_result = simulate_strategy(
        signals, StrategyConfig(top_n=top_n, cost=CostConfig())
    )
    bh_result = buy_and_hold_equal(signals)
    ew_result = equal_weight_rebalanced(signals)

    metrics_df = evaluate_all(
        {
            "model": model_result,
            "buy_hold_equal": bh_result,
            "equal_weight_rebalanced": ew_result,
        },
        output_path=performance_path,
    )
    logger.info(
        "Chỉ số hiệu quả: %d hàng (model + 2 benchmark × gross/net) → %s",
        len(metrics_df),
        performance_path,
    )
    return metrics_df


# ---------------------------------------------------------------------------
# Giai đoạn: diễn giải mô hình (Req 7)
# ---------------------------------------------------------------------------

def _fit_technical_model(
    model_name: str,
    cutoff: str,
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
):
    """Huấn luyện lại Config_A leakage-safe để lấy (model, X_test, y_test, cols).

    :func:`~backtest.signals.generate_signals` không trả về mô hình đã fit (chỉ
    trả nhãn + xác suất), trong khi
    :func:`~backtest.interpret.interpret_technical_model` cần mô hình *đã fit*
    cùng ``X_test``/``y_test``/tên đặc trưng. Để KHÔNG sửa
    ``pipeline/task10_train.py``, hàm này tái dùng đúng các helper cấp thấp của
    pipeline theo cùng quy trình mà ``generate_signals`` dùng: merge dữ liệu →
    ``Config_A`` → ``time_series_split`` → fit imputer trên train, transform test
    (leakage-safe) → fit mô hình đã chọn trên train.

    Args:
        model_name: Tên thuật toán trong ``build_ml_models`` (mặc định
            ``"LightGBM"``). Không hỗ trợ ``"auto"`` ở đây — cần một mô hình cụ
            thể để diễn giải.
        cutoff: Train_Cutoff.
        tech_path, kw_path, labels_path: đường dẫn dữ liệu đầu vào.

    Returns:
        Tuple ``(model, X_test, y_test, feature_names)`` — mô hình đã fit, ma
        trận test, nhãn test, và danh sách tên cột đặc trưng thực tế.

    Raises:
        ValueError: nếu dữ liệu rỗng hoặc chỉ một lớp nhãn.
        KeyError: nếu *model_name* không hợp lệ.
    """
    merged = load_and_merge_data(tech_path, kw_path, labels_path)
    if merged.empty:
        raise ValueError("No samples after merging; cannot fit model to interpret.")
    if merged["label_basic"].nunique() < 2:
        raise ValueError("Training data has only one label class; cannot fit model.")

    tech_cols, kw_cols = identify_feature_columns(merged)
    configs = get_feature_configs(tech_cols, kw_cols)
    feature_cols = configs["Config_A"]

    train_df, test_df = time_series_split(merged, cutoff=cutoff)

    # Fit imputer trên train, transform test; căn cột chung (leakage-safe, Req 8.4).
    X_train, y_train, X_test, y_test = _prepare_train_test_matrices(
        train_df, test_df, feature_cols
    )

    models = build_ml_models(y_train)
    if model_name not in models:
        raise KeyError(
            f"Unknown model_name {model_name!r}; available: {sorted(models)}"
        )
    model = models[model_name]
    model.fit(X_train, y_train)

    feature_names = list(X_test.columns)
    logger.info(
        "Đã fit %s trên Config_A (cutoff=%s) để diễn giải: %d đặc trưng, %d hàng test.",
        model_name,
        cutoff,
        len(feature_names),
        len(X_test),
    )
    return model, X_test, y_test, feature_names


def run_interpret_stage(
    model_name: str,
    cutoff: str,
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
) -> pd.DataFrame:
    """Diễn giải Technical_Model: SHAP + permutation importance (Req 7).

    Huấn luyện lại ``Config_A`` qua :func:`_fit_technical_model` để lấy mô hình đã
    fit cùng ``X_test``/``y_test``/tên đặc trưng, rồi gọi
    :func:`~backtest.interpret.interpret_technical_model` (ghi CSV + PNG).

    Args:
        model_name: Thuật toán cần diễn giải (mặc định ``"LightGBM"``).
        cutoff: Train_Cutoff.
        tech_path, kw_path, labels_path: đường dẫn dữ liệu đầu vào.

    Returns:
        ``pd.DataFrame`` bảng xếp hạng tầm quan trọng đặc trưng.
    """
    # "auto" không có nghĩa khi diễn giải một mô hình cụ thể → mặc định LightGBM.
    effective_name = "LightGBM" if model_name == "auto" else model_name
    model, X_test, y_test, feature_names = _fit_technical_model(
        effective_name, cutoff, tech_path, kw_path, labels_path
    )
    importance_df = interpret_technical_model(
        model, X_test, feature_names, y_test=y_test
    )
    logger.info(
        "Diễn giải mô hình hoàn tất: xếp hạng %d đặc trưng.", len(importance_df)
    )
    return importance_df


# ---------------------------------------------------------------------------
# Điều phối
# ---------------------------------------------------------------------------

def run_backtest(
    do_all: bool = False,
    do_signals: bool = False,
    do_walk_forward: bool = False,
    do_interpret: bool = False,
    do_audit: bool = False,
    do_report: bool = False,
    model_name: str = "LightGBM",
    cutoff: str = "2025Q1",
    top_n: Optional[int] = None,
) -> List[str]:
    """Điều phối các giai đoạn backtest theo cờ hành động (Req 10.5).

    Thứ tự ``--all`` (Req 10.5): signals → strategy+benchmarks → metrics →
    walk-forward → interpret → audit → report. Mỗi giai đoạn được bọc để một lỗi
    được ghi log và KHÔNG làm sập cả chuỗi — báo cáo cuối vẫn chạy để tạo tối đa
    artifact (reporter degrade gracefully).

    Args:
        do_all: chạy toàn bộ chuỗi theo thứ tự cố định.
        do_signals: chỉ chạy tín hiệu + chiến lược/benchmark/chỉ số.
        do_walk_forward: chạy walk-forward.
        do_interpret: chạy diễn giải mô hình.
        do_audit: chạy kiểm toán rò rỉ.
        do_report: sinh báo cáo tổng hợp.
        model_name: thuật toán (mặc định ``"LightGBM"``; ``"auto"`` → BA cao nhất).
        cutoff: Train_Cutoff (mặc định ``"2025Q1"``).
        top_n: biến thể top-N cho chiến lược mô hình (tùy chọn).

    Returns:
        Danh sách tên các giai đoạn thất bại (rỗng nếu mọi giai đoạn OK).
    """
    # Chuẩn hóa cờ: --all bật mọi giai đoạn theo đúng thứ tự.
    if do_all:
        do_signals = do_walk_forward = do_interpret = do_audit = do_report = True

    failures: List[str] = []
    signals: Optional[pd.DataFrame] = None

    # 1) signals (+ 2) strategy+benchmarks + 3) metrics) — gộp một giai đoạn tín hiệu.
    if do_signals:
        try:
            logger.info("[1/?] Giai đoạn tín hiệu (signals) …")
            signals = run_signals_stage(model_name, cutoff)
        except Exception as exc:  # noqa: BLE001 — cô lập lỗi từng giai đoạn.
            logger.exception("Giai đoạn 'signals' thất bại: %s", exc)
            failures.append("signals")

        if signals is not None:
            try:
                logger.info("[2/?] Giai đoạn chiến lược + benchmark + chỉ số …")
                run_strategy_metrics_stage(signals, top_n=top_n)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Giai đoạn 'strategy+metrics' thất bại: %s", exc)
                failures.append("strategy+metrics")

    # 4) walk-forward.
    if do_walk_forward:
        try:
            logger.info("[3/?] Giai đoạn walk-forward …")
            run_walk_forward(model_name=model_name)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Giai đoạn 'walk-forward' thất bại: %s", exc)
            failures.append("walk-forward")

    # 5) interpret.
    if do_interpret:
        try:
            logger.info("[4/?] Giai đoạn diễn giải mô hình (interpret) …")
            run_interpret_stage(model_name, cutoff)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Giai đoạn 'interpret' thất bại: %s", exc)
            failures.append("interpret")

    # 6) audit.
    if do_audit:
        try:
            logger.info("[5/?] Giai đoạn kiểm toán rò rỉ (audit) …")
            audit_leakage(cutoff=cutoff)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Giai đoạn 'audit' thất bại: %s", exc)
            failures.append("audit")

    # 7) report.
    if do_report:
        try:
            logger.info("[6/?] Giai đoạn báo cáo tổng hợp (report) …")
            generate_backtest_report()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Giai đoạn 'report' thất bại: %s", exc)
            failures.append("report")

    if failures:
        logger.warning(
            "Backtest hoàn tất với %d giai đoạn lỗi: %s",
            len(failures),
            ", ".join(failures),
        )
    else:
        logger.info("Backtest hoàn tất — mọi giai đoạn đã chạy thành công.")

    return failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Dựng parser argparse cho CLI backtest (Req 10.5)."""
    parser = argparse.ArgumentParser(
        prog="python -m backtest.run_backtest",
        description=(
            "Backtest ML kỹ thuật (HOSE-80) — điểm chạy dòng lệnh sinh mọi "
            "artifact/báo cáo (long-only, đặc thù thị trường cơ sở VN)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Thứ tự --all: signals → strategy+benchmarks → metrics → walk-forward →
              interpret → audit → report

Ví dụ:
  python -m backtest.run_backtest --all
  python -m backtest.run_backtest --signals --model LightGBM
  python -m backtest.run_backtest --walk-forward
  python -m backtest.run_backtest --interpret --audit --report
        """,
    )

    # Cờ hành động.
    parser.add_argument(
        "--all",
        dest="do_all",
        action="store_true",
        help="Chạy toàn bộ chuỗi backtest theo thứ tự cố định.",
    )
    parser.add_argument(
        "--signals",
        dest="do_signals",
        action="store_true",
        help="Sinh Prediction_Signal + mô phỏng chiến lược/benchmark + chỉ số.",
    )
    parser.add_argument(
        "--walk-forward",
        dest="do_walk_forward",
        action="store_true",
        help="Chạy Walk_Forward_Evaluator qua nhiều cutoff.",
    )
    parser.add_argument(
        "--interpret",
        dest="do_interpret",
        action="store_true",
        help="Diễn giải mô hình (SHAP + permutation importance).",
    )
    parser.add_argument(
        "--audit",
        dest="do_audit",
        action="store_true",
        help="Kiểm toán rò rỉ dữ liệu thời gian.",
    )
    parser.add_argument(
        "--report",
        dest="do_report",
        action="store_true",
        help="Sinh báo cáo Markdown tổng hợp từ các artifact hiện có.",
    )

    # Tùy chọn.
    parser.add_argument(
        "--model",
        dest="model_name",
        type=str,
        default="LightGBM",
        help="Thuật toán mô hình (mặc định LightGBM; 'auto' → chọn BA cao nhất).",
    )
    parser.add_argument(
        "--cutoff",
        type=str,
        default="2025Q1",
        help="Train_Cutoff — ranh giới chia train/test (mặc định 2025Q1).",
    )
    parser.add_argument(
        "--top-n",
        dest="top_n",
        type=int,
        default=None,
        help="Chỉ chọn top-N mã có xác suất 'tăng' cao nhất mỗi kỳ (tùy chọn).",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Điểm vào CLI cho ``python -m backtest.run_backtest`` (Req 10.5).

    Args:
        argv: danh sách tham số (mặc định ``None`` → dùng ``sys.argv``).

    Returns:
        Mã thoát: 0 nếu mọi giai đoạn OK; 1 nếu có giai đoạn thất bại; 2 nếu
        không cờ hành động nào được cung cấp (in help).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    action_flags = (
        args.do_all
        or args.do_signals
        or args.do_walk_forward
        or args.do_interpret
        or args.do_audit
        or args.do_report
    )
    if not action_flags:
        # Không có hành động → in help và thoát với mã 2 (lỗi sử dụng).
        parser.print_help()
        return 2

    failures = run_backtest(
        do_all=args.do_all,
        do_signals=args.do_signals,
        do_walk_forward=args.do_walk_forward,
        do_interpret=args.do_interpret,
        do_audit=args.do_audit,
        do_report=args.do_report,
        model_name=args.model_name,
        cutoff=args.cutoff,
        top_n=args.top_n,
    )

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
