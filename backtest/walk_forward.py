"""Walk_Forward_Evaluator (`backtest/walk_forward.py`) — độ ổn định thời gian (Req 6).

Module này đánh giá độ ổn định của Technical_Model qua NHIỀU điểm chia thời gian
(``cutoff``) theo kiểu cửa sổ tịnh tiến (walk-forward), thay vì chỉ dựa vào một
cutoff duy nhất. Với mỗi cutoff, hệ thống:

- **Huấn luyện lại + dự đoán** qua :func:`~backtest.signals.generate_signals`
  (tái dùng pipeline, chỉ train trên các kỳ ``< cutoff`` nhờ ``time_series_split``
  — Req 6.1, 6.5, 8.4);
- **Tính chỉ số phân loại** balanced accuracy và AUC trên tập test tương ứng cutoff
  (Req 6.2);
- **Mô phỏng chiến lược mô hình** (long-only, có phí) và benchmark buy-and-hold để
  đối chiếu, rồi lấy lợi nhuận tích lũy net của chiến lược và cumulative return của
  benchmark (Req 6.3);
- Gom kết quả theo cutoff và **ghi ra** ``reports/walk_forward_results.csv`` (Req 6.4).

Nguyên tắc chống rò rỉ thời gian được đảm bảo bởi ``time_series_split`` của pipeline:
mô hình cho một cutoff chỉ nhìn thấy dữ liệu của các kỳ trước cutoff đó (Req 6.5).

Xử lý lỗi (theo design "Error Handling"): nếu một cutoff cho tập test rỗng hoặc chỉ
có một lớp nhãn (``generate_signals`` ném :class:`ValueError`), ghi cảnh báo và BỎ
QUA cutoff đó thay vì làm sập toàn bộ walk-forward. AUC cũng được bảo vệ: khi tập
test chỉ còn một lớp thật (``roc_auc_score`` không xác định), AUC được đặt ``NaN``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Sequence, Union

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, roc_auc_score

from backtest.costs import CostConfig
from backtest.benchmarks import buy_and_hold_equal
from backtest.metrics import cumulative_return
from backtest.signals import generate_signals
from backtest.strategy import StrategyConfig, simulate_strategy
from pipeline.logging_config import setup_logger
from pipeline.task10_train import (
    KW_FEATURES_PATH,
    LABELS_PATH,
    TECH_FEATURES_PATH,
)

logger = setup_logger("BACKTEST_WALK_FORWARD")

# Đường dẫn báo cáo mặc định cho kết quả walk-forward (Req 6.4).
DEFAULT_WALK_FORWARD_PATH = "reports/walk_forward_results.csv"

# Tập cutoff mặc định — các quý đủ số kỳ test để chỉ số có ý nghĩa, phù hợp chuỗi
# 17 quý hiện có (design.md §6). Mỗi cutoff train trên kỳ < cutoff, test từ cutoff.
DEFAULT_CUTOFFS: List[str] = ["2024Q3", "2025Q1", "2025Q3"]

# Thứ tự cột chuẩn của reports/walk_forward_results.csv (design.md Data Models).
WALK_FORWARD_COLUMNS: List[str] = [
    "cutoff",
    "n_test",
    "balanced_accuracy",
    "auc_roc",
    "strategy_cumulative_return_net",
    "buy_hold_cumulative_return",
]


def _safe_auc(y_true: Sequence[int], pred_proba_up: Sequence[float]) -> float:
    """Tính AUC-ROC an toàn khi tập test chỉ có một lớp nhãn.

    ``roc_auc_score`` ném :class:`ValueError` nếu ``y_true`` chỉ chứa một lớp
    (AUC không xác định). Trong trường hợp đó trả về ``NaN`` thay vì ném lỗi để
    walk-forward không bị gián đoạn (design "Error Handling").

    Args:
        y_true: Nhãn thật (0/1) của tập test.
        pred_proba_up: Xác suất dự đoán lớp "tăng".

    Returns:
        AUC-ROC dạng ``float``; ``NaN`` khi chỉ có một lớp nhãn.
    """
    y = np.asarray(y_true)
    if np.unique(y).size < 2:
        return float("nan")
    try:
        return float(roc_auc_score(y, np.asarray(pred_proba_up, dtype=float)))
    except ValueError:
        return float("nan")


def run_walk_forward(
    cutoffs: Optional[Sequence[str]] = None,
    model_name: str = "LightGBM",
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
    cost: Optional[CostConfig] = None,
    output_path: Union[str, os.PathLike] = DEFAULT_WALK_FORWARD_PATH,
) -> pd.DataFrame:
    """Đánh giá Technical_Model qua nhiều cutoff (walk-forward) (Req 6).

    Với mỗi cutoff trong *cutoffs* (mặc định :data:`DEFAULT_CUTOFFS`):

    1. Sinh tín hiệu qua :func:`~backtest.signals.generate_signals` — huấn luyện chỉ
       trên kỳ ``< cutoff`` (Req 6.1, 6.5), dự đoán trên tập test tương ứng.
    2. Tính balanced accuracy và AUC-ROC trên tập test (Req 6.2). AUC được đặt
       ``NaN`` khi tập test chỉ còn một lớp nhãn (:func:`_safe_auc`).
    3. Mô phỏng chiến lược mô hình long-only có phí (:func:`~backtest.strategy.simulate_strategy`
       với :class:`~backtest.costs.CostConfig`) và lấy lợi nhuận tích lũy **net**;
       chạy benchmark :func:`~backtest.benchmarks.buy_and_hold_equal` để đối chiếu
       (Req 6.3).

    Cutoff cho tập test rỗng hoặc chỉ một lớp nhãn (``generate_signals`` ném
    :class:`ValueError`) → ghi cảnh báo và BỎ QUA, không làm sập toàn bộ run
    (design "Error Handling"). Kết quả các cutoff hợp lệ được ghi ra
    ``reports/walk_forward_results.csv`` (Req 6.4) và trả về dưới dạng ``DataFrame``.

    Args:
        cutoffs: Danh sách Train_Cutoff cần đánh giá. ``None`` → dùng
            :data:`DEFAULT_CUTOFFS`.
        model_name: Thuật toán huấn luyện Technical_Model (mặc định ``"LightGBM"``).
        tech_path: Đường dẫn tệp đặc trưng kỹ thuật.
        kw_path: Đường dẫn tệp đặc trưng từ khóa (giữ đúng tập mẫu như baseline).
        labels_path: Đường dẫn ``master_with_labels.csv``.
        cost: Cấu hình chi phí giao dịch cho chiến lược mô hình. ``None`` → dùng
            :class:`~backtest.costs.CostConfig` mặc định (phí VN) để lợi nhuận là NET.
        output_path: Đường dẫn CSV đầu ra (mặc định
            ``reports/walk_forward_results.csv``). Cho phép test chuyển hướng.

    Returns:
        ``pd.DataFrame`` các cột :data:`WALK_FORWARD_COLUMNS` — một hàng cho mỗi
        cutoff hợp lệ, cùng nội dung được ghi ra CSV.
    """
    if cutoffs is None:
        cutoffs = list(DEFAULT_CUTOFFS)

    # Phí mặc định (VN) để lợi nhuận chiến lược mô hình là NET (Req 6.3).
    if cost is None:
        cost = CostConfig()

    rows: List[dict] = []

    for cutoff in cutoffs:
        # Sinh tín hiệu; cutoff rỗng/một-lớp → generate_signals ném ValueError.
        try:
            signals = generate_signals(
                tech_path=tech_path,
                kw_path=kw_path,
                labels_path=labels_path,
                cutoff=cutoff,
                model_name=model_name,
                config="Config_A",
            )
        except ValueError as exc:
            logger.warning(
                "Bỏ qua cutoff %s: tập test rỗng hoặc chỉ một lớp nhãn (%s).",
                cutoff,
                exc,
            )
            continue

        if signals.empty:
            logger.warning("Bỏ qua cutoff %s: SignalFrame rỗng sau khi gắn return.", cutoff)
            continue

        n_test = int(len(signals))
        y_true = signals["y_true"].to_numpy()
        pred_label = signals["pred_label"].to_numpy()
        pred_proba_up = signals["pred_proba_up"].to_numpy()

        # Chỉ số phân loại (Req 6.2). AUC an toàn với tập một lớp.
        ba = float(balanced_accuracy_score(y_true, pred_label))
        auc = _safe_auc(y_true, pred_proba_up)

        # Chiến lược mô hình long-only có phí → cumulative return NET (Req 6.3).
        strat_result = simulate_strategy(signals, StrategyConfig(cost=cost))
        strat_cum_net = cumulative_return(strat_result.period_returns_net)

        # Benchmark buy-and-hold để đối chiếu (Req 6.3).
        bh_result = buy_and_hold_equal(signals)
        bh_cum = cumulative_return(bh_result.period_returns)

        logger.info(
            "Cutoff %s: n_test=%d, BA=%.4f, AUC=%.4f, strat_net=%.4f, buy_hold=%.4f",
            cutoff,
            n_test,
            ba,
            auc,
            strat_cum_net,
            bh_cum,
        )

        rows.append(
            {
                "cutoff": cutoff,
                "n_test": n_test,
                "balanced_accuracy": ba,
                "auc_roc": auc,
                "strategy_cumulative_return_net": strat_cum_net,
                "buy_hold_cumulative_return": bh_cum,
            }
        )

    df = pd.DataFrame(rows, columns=WALK_FORWARD_COLUMNS)

    # Tạo thư mục reports/ nếu thiếu rồi ghi CSV (không ghi index) (Req 6.4).
    out = Path(output_path)
    if out.parent != Path(""):
        out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    logger.info(
        "Walk-forward hoàn tất: %d/%d cutoff hợp lệ, ghi %s.",
        len(df),
        len(cutoffs),
        out,
    )

    return df
