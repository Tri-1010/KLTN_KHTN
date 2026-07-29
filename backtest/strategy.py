"""Strategy_Simulator (`backtest/strategy.py`) — mô phỏng đầu tư long-only (Req 2).

Module này chứa các thành phần thuần (pure) của tầng mô phỏng chiến lược:

- :class:`StrategyConfig` — cấu hình chiến lược dùng chung cho toàn tầng mô phỏng
  (biến thể top-N và cấu hình chi phí giao dịch).
- :func:`portfolio_period_return` — lợi nhuận danh mục một kỳ = trung bình cộng
  lợi nhuận các mã được chọn (Req 2.5); bằng 0 khi danh mục rỗng (Req 2.4).
- :func:`select_portfolio` — hàm chọn danh mục MUA cho một kỳ (thuần long-only).

Ràng buộc thiết kế cứng: chiến lược **thuần long-only** — chỉ mua các mã dự báo
"tăng" (``pred_label == 1``) và TUYỆT ĐỐI không mở vị thế với mã dự báo "giảm"
(``pred_label == 0``), phản ánh đặc thù một chiều của thị trường cơ sở VN
(Req 2.1, 2.2).

- :class:`StrategyResult` — kết quả mô phỏng: chuỗi lợi nhuận kỳ (net/gross),
  turnover theo kỳ, tổng chi phí, danh mục nắm giữ theo kỳ, và metadata các giả
  định thị trường cơ sở VN (Req 2.8).
- :func:`simulate_strategy` — vòng lặp mô phỏng long-only theo từng kỳ (Req 2, 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from backtest.costs import CostConfig, period_cost, turnover


@dataclass
class StrategyConfig:
    """Cấu hình chiến lược mô phỏng long-only, dùng chung cho tầng mô phỏng.

    Attributes:
        top_n: Biến thể chọn danh mục.

            - ``None`` → chọn *mọi* mã dự báo "tăng" (``pred_label == 1``)
              trong kỳ (Req 2.1).
            - ``k > 0`` → chỉ chọn top-``k`` mã có ``pred_proba_up`` cao nhất
              trong số các mã dự báo "tăng" (Req 2.6). Vẫn thuần long-only.
        cost: Cấu hình chi phí giao dịch (:class:`~backtest.costs.CostConfig`).

            - ``None`` → không áp phí (kịch bản gross).
            - có giá trị → áp Transaction_Cost (kịch bản net, Req 3).
    """

    top_n: Optional[int] = None
    cost: Optional[CostConfig] = None


def portfolio_period_return(selected_returns: Sequence[float]) -> float:
    """Tính lợi nhuận danh mục của một kỳ (Req 2.5, 2.4).

    Lợi nhuận danh mục bằng trung bình cộng ``Period_Return`` của các mã được
    chọn trong kỳ (phân bổ vốn đều — Req 2.3). Khi không có mã nào được chọn
    (danh mục rỗng → giữ tiền mặt), lợi nhuận kỳ bằng 0 (Req 2.4).

    Args:
        selected_returns: Dãy ``Period_Return`` của các mã được chọn trong kỳ.

    Returns:
        Trung bình cộng của ``selected_returns`` nếu không rỗng, ngược lại 0.0.
    """
    return float(np.mean(selected_returns)) if len(selected_returns) > 0 else 0.0


def select_portfolio(
    period_signals: pd.DataFrame,
    top_n: Optional[int] = None,
) -> List[str]:
    """Chọn danh mục MUA cho một kỳ từ tín hiệu dự đoán (long-only).

    Chỉ chọn các mã có ``pred_label == 1`` (dự báo "tăng"); TUYỆT ĐỐI không bao
    giờ chọn mã có ``pred_label == 0`` (không mở vị thế short — Req 2.1, 2.2).

    - Khi *top_n* là ``None`` → chọn *tất cả* mã dự báo "tăng" (Req 2.1).
    - Khi *top_n* = ``k > 0`` → chọn tập con ≤ k mã có ``pred_proba_up`` cao nhất
      trong số các mã dự báo "tăng" (Req 2.6).

    Kết quả được sắp xếp theo thứ tự xác định: ``pred_proba_up`` giảm dần, rồi
    ``ticker`` tăng dần (tie-break) để đầu ra ổn định, dễ kiểm thử.

    Args:
        period_signals: SignalFrame của một kỳ, cần tối thiểu các cột
            ``ticker``, ``pred_label``, ``pred_proba_up``.
        top_n: Số mã tối đa được chọn theo xác suất. ``None`` → chọn mọi mã dự
            báo "tăng". Giá trị ``<= 0`` được coi như không chọn mã nào.

    Returns:
        Danh sách ticker được chọn, theo thứ tự xác định (proba giảm dần, ticker
        tăng dần).
    """
    # Long-only: chỉ giữ mã dự báo "tăng"; loại hoàn toàn mã pred_label == 0.
    up = period_signals[period_signals["pred_label"] == 1]

    # Thứ tự xác định: proba giảm dần, ticker tăng dần (ổn định cho test).
    up = up.sort_values(
        by=["pred_proba_up", "ticker"],
        ascending=[False, True],
        kind="mergesort",
    )

    if top_n is not None:
        if top_n <= 0:
            return []
        up = up.head(top_n)

    return up["ticker"].tolist()


# Giả định thị trường chứng khoán cơ sở Việt Nam áp cho toàn bộ mô phỏng (Req 2.8).
# Được đính vào mọi StrategyResult để báo cáo ghi rõ phạm vi hiệu lực của kết quả.
VN_MARKET_ASSUMPTIONS: Dict[str, str] = {
    "position": "long-only (một chiều) — chỉ mua mã dự báo 'tăng', không bán khống",
    "settlement": "thanh toán T+2 (mua về sau 2 ngày làm việc mới bán được)",
    "price_band": "biên độ giá HOSE ±7%/phiên (giả định mọi lệnh khớp ở suất sinh lời kỳ)",
    "min_lot": "lô giao dịch tối thiểu 100 cổ phiếu",
    "capital": "giả định NAV đủ lớn để bỏ qua hiệu ứng lô lẻ (odd-lot rounding)",
    "slippage": "bỏ qua trượt giá (slippage); chỉ tính chi phí tường minh (brokerage + sell_tax)",
}


@dataclass
class StrategyResult:
    """Kết quả mô phỏng một chiến lược đầu tư theo kỳ (Req 2, 3).

    Attributes:
        period_returns: Chuỗi lợi nhuận kỳ *được báo cáo* (index = ``quarter_id``,
            sắp tăng dần). Là chuỗi **net** khi ``cfg.cost`` có giá trị, ngược lại
            trùng chuỗi **gross** (Req 3.5).
        period_returns_gross: Chuỗi lợi nhuận kỳ chưa trừ phí (kịch bản gross).
        period_returns_net: Chuỗi lợi nhuận kỳ đã trừ Transaction_Cost của kỳ đó
            (kịch bản net). Bằng gross khi không cấu hình phí.
        turnover_by_period: Chuỗi turnover mỗi kỳ = tổng phần trọng số thay đổi so
            với kỳ trước (``buy_value + sell_value``, chuẩn hóa NAV = 1).
        total_cost: Tổng chi phí giao dịch tích lũy qua các kỳ (NAV = 1). 0 khi
            không cấu hình phí.
        holdings_by_period: Ánh xạ ``quarter_id`` → dict trọng số danh mục
            (``ticker`` → trọng số đều). Kỳ giữ tiền mặt → dict rỗng ``{}``.
        market_assumptions: Các giả định thị trường cơ sở VN được áp dụng (Req 2.8).
    """

    period_returns: pd.Series
    period_returns_gross: pd.Series
    period_returns_net: pd.Series
    turnover_by_period: pd.Series
    total_cost: float
    holdings_by_period: Dict[object, Dict[str, float]]
    market_assumptions: Dict[str, str] = field(
        default_factory=lambda: dict(VN_MARKET_ASSUMPTIONS)
    )


def _equal_weights(tickers: Sequence[str]) -> Dict[str, float]:
    """Phân bổ vốn đều cho các ticker được chọn (Req 2.3).

    Mỗi mã trong *tickers* nhận trọng số ``1/N`` (N = số mã). Danh sách rỗng →
    dict rỗng (giữ tiền mặt — Req 2.4). Trọng số luôn không âm và tổng ≤ 1.
    """
    n = len(tickers)
    if n == 0:
        return {}
    w = 1.0 / n
    return {ticker: w for ticker in tickers}


def simulate_strategy(signals: "pd.DataFrame", cfg: StrategyConfig) -> StrategyResult:
    """Mô phỏng chiến lược đầu tư long-only theo từng kỳ (Req 2, 3).

    Duyệt các ``quarter_id`` của tập test theo thứ tự tăng dần (Req 2.7 — chỉ dùng
    thông tin ≤ q). Với mỗi kỳ:

    - chọn danh mục MUA bằng :func:`select_portfolio` (mã ``pred_label == 1``, hoặc
      top-N theo ``pred_proba_up``); TUYỆT ĐỐI không mở vị thế short (Req 2.1, 2.2, 2.6);
    - phân bổ vốn đều cho các mã được chọn (Req 2.3); danh mục rỗng → giữ tiền mặt,
      lợi nhuận kỳ = 0 (Req 2.4);
    - lợi nhuận **gross** của kỳ = trung bình ``period_return`` các mã được chọn
      (Req 2.5), tính qua :func:`portfolio_period_return`;
    - áp Transaction_Cost trên phần danh mục *thay đổi* so với kỳ trước (Req 3);
      lợi nhuận **net** của kỳ = gross − chi phí kỳ đó, có **sàn tại -1.0**: một
      kỳ không thể lỗ quá 100% NAV, nên khi NAV chạm 0 thì không tính lỗ/phí thêm
      (``net = max(gross − cost, -1.0)``). Kỳ đầu: toàn bộ danh mục là mua mới nên
      brokerage tính trên toàn phần vốn vào (:func:`period_cost` xử lý ``prev_w`` rỗng).

    Nếu ``cfg.cost is None`` → không áp phí, net trùng gross và ``total_cost = 0``.
    Chuỗi ``period_returns`` được báo cáo là net khi có cấu hình phí, ngược lại là
    gross (Req 3.5); cả hai chuỗi gross/net luôn sẵn có trong kết quả.

    Args:
        signals: SignalFrame với các cột ``ticker``, ``quarter_id``, ``pred_label``,
            ``pred_proba_up``, ``period_return``.
        cfg: :class:`StrategyConfig` — biến thể top-N và cấu hình chi phí.

    Returns:
        :class:`StrategyResult` chứa chuỗi lợi nhuận kỳ (net/gross), turnover theo
        kỳ, tổng chi phí, danh mục theo kỳ, và metadata giả định thị trường VN.
    """
    # Thứ tự thời gian tăng dần: chỉ dùng thông tin ≤ q cho quyết định kỳ q (Req 2.7).
    quarters = sorted(signals["quarter_id"].unique())

    gross_returns: List[float] = []
    net_returns: List[float] = []
    turnover_values: List[float] = []
    holdings_by_period: Dict[object, Dict[str, float]] = {}

    prev_weights: Dict[str, float] = {}
    total_cost = 0.0

    for q in quarters:
        # Lát cắt tín hiệu của đúng kỳ q (không nhìn sang kỳ khác).
        period_signals = signals[signals["quarter_id"] == q]

        # Chọn danh mục long-only cho kỳ (Req 2.1, 2.2, 2.6).
        selected = select_portfolio(period_signals, top_n=cfg.top_n)
        new_weights = _equal_weights(selected)  # phân bổ đều (Req 2.3, 2.4)
        holdings_by_period[q] = new_weights

        # Lợi nhuận gross của kỳ = mean(period_return của mã được chọn) (Req 2.5, 2.4).
        selected_returns = (
            period_signals[period_signals["ticker"].isin(selected)]["period_return"]
            .astype(float)
            .tolist()
        )
        gross = portfolio_period_return(selected_returns)

        # Chi phí giao dịch trên phần danh mục thay đổi so với kỳ trước (Req 3).
        buy_v, sell_v = turnover(prev_weights, new_weights)
        turnover_values.append(buy_v + sell_v)

        if cfg.cost is not None:
            cost_q = period_cost(prev_weights, new_weights, cfg.cost)
        else:
            cost_q = 0.0
        total_cost += cost_q

        # Net = gross trừ chi phí kỳ (chi phí là tỷ lệ trên NAV) (Req 3.5).
        # Sàn -1.0 cho net: khi NAV chạm 0 (lỗ 100%), không thể lỗ hay tính phí
        # thêm nữa; giữ (1 + net) >= 0 để toán lợi nhuận tích lũy không sai lệch.
        gross_returns.append(gross)
        net_returns.append(max(gross - cost_q, -1.0))

        prev_weights = new_weights

    index = pd.Index(quarters, name="quarter_id")
    gross_series = pd.Series(gross_returns, index=index, dtype=float)
    net_series = pd.Series(net_returns, index=index, dtype=float)
    turnover_series = pd.Series(turnover_values, index=index, dtype=float)

    # Chuỗi báo cáo: net khi có phí, ngược lại gross (Req 3.5).
    reported = net_series if cfg.cost is not None else gross_series

    return StrategyResult(
        period_returns=reported,
        period_returns_gross=gross_series,
        period_returns_net=net_series,
        turnover_by_period=turnover_series,
        total_cost=float(total_cost),
        holdings_by_period=holdings_by_period,
        market_assumptions=dict(VN_MARKET_ASSUMPTIONS),
    )
