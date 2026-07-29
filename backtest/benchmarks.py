"""Benchmark_Strategy (`backtest/benchmarks.py`) — tham chiếu long-only (Req 4).

Module này dựng các chiến lược THAM CHIẾU thuần long-only để đối chiếu với chiến
lược dựa trên mô hình. Điểm mấu chốt: benchmark **bỏ qua mọi dự đoán của mô hình**
(``pred_label``/``pred_proba_up``) — chúng luôn nắm giữ TẤT CẢ ticker có dữ liệu,
phân bổ vốn đều (Req 4.1, 4.2). Nhờ vậy phần lợi nhuận vượt trội (nếu có) của chiến
lược mô hình được quy về đúng giá trị của tín hiệu dự báo.

Hai benchmark:

- :func:`buy_and_hold_equal` — MUA đều toàn bộ ticker ở kỳ đầu và GIỮ suốt khoảng
  test (Req 4.1).
- :func:`equal_weight_rebalanced` — TÁI CÂN BẰNG đều mỗi kỳ trên toàn bộ ticker có
  dữ liệu trong kỳ đó (Req 4.2).

Cả hai trả về :class:`~backtest.strategy.StrategyResult` để đo bằng đúng
Performance_Evaluator (``evaluate_all``/các chỉ số trong :mod:`backtest.metrics`)
trên cùng khoảng test như chiến lược mô hình (Req 4.3).

Quy ước chi phí cho benchmark: benchmark được báo cáo ở kịch bản **gross** (không
áp Transaction_Cost). Do đó chuỗi ``period_returns_net`` được đặt trùng
``period_returns_gross`` và ``total_cost = 0.0``. ``turnover_by_period`` vẫn được
tính (buy + sell trên phần trọng số thay đổi) để phản ánh mức luân chuyển danh mục:
buy-and-hold chỉ luân chuyển ở kỳ đầu (mua vào) rồi ~0 các kỳ sau, còn equal-weight
tái cân bằng luân chuyển mỗi kỳ.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from backtest.costs import turnover
from backtest.strategy import (
    VN_MARKET_ASSUMPTIONS,
    StrategyResult,
    _equal_weights,
    portfolio_period_return,
)


def _build_benchmark_result(
    quarters: List[object],
    returns_by_quarter: List[float],
    holdings_by_period: Dict[object, Dict[str, float]],
) -> StrategyResult:
    """Lắp :class:`StrategyResult` cho một benchmark (kịch bản gross, Req 4.3).

    Vì benchmark báo cáo gross (không áp Transaction_Cost), chuỗi net được đặt
    trùng chuỗi gross và ``total_cost = 0.0``. ``turnover_by_period`` được tính từ
    thay đổi trọng số danh mục giữa các kỳ liên tiếp qua :func:`~backtest.costs.turnover`
    (kỳ đầu: ``prev_weights`` rỗng → toàn bộ là mua mới).

    Args:
        quarters: Danh sách ``quarter_id`` đã sắp tăng dần (thứ tự thời gian).
        returns_by_quarter: Lợi nhuận danh mục mỗi kỳ, cùng thứ tự với *quarters*.
        holdings_by_period: Ánh xạ ``quarter_id`` → trọng số danh mục của kỳ.

    Returns:
        :class:`StrategyResult` với gross = net, ``total_cost = 0.0`` và metadata
        giả định thị trường VN.
    """
    turnover_values: List[float] = []
    prev_weights: Dict[str, float] = {}
    for q in quarters:
        new_weights = holdings_by_period.get(q, {})
        buy_v, sell_v = turnover(prev_weights, new_weights)
        turnover_values.append(buy_v + sell_v)
        prev_weights = new_weights

    index = pd.Index(quarters, name="quarter_id")
    returns_series = pd.Series(returns_by_quarter, index=index, dtype=float)
    turnover_series = pd.Series(turnover_values, index=index, dtype=float)

    # Benchmark báo cáo gross: net trùng gross, total_cost = 0.0.
    return StrategyResult(
        period_returns=returns_series,
        period_returns_gross=returns_series.copy(),
        period_returns_net=returns_series.copy(),
        turnover_by_period=turnover_series,
        total_cost=0.0,
        holdings_by_period=holdings_by_period,
        market_assumptions=dict(VN_MARKET_ASSUMPTIONS),
    )


def buy_and_hold_equal(signals: pd.DataFrame) -> StrategyResult:
    """Benchmark buy-and-hold phân bổ đều, giữ suốt khoảng test (Req 4.1).

    Ngữ nghĩa (đơn giản, tường minh, xác định cho cấp dữ liệu theo quý):

    - **Mua ở kỳ đầu:** tập nắm giữ là *toàn bộ* ticker có dữ liệu ở kỳ (``quarter_id``)
      NHỎ NHẤT của tập test, phân bổ vốn đều — mỗi mã trọng số ``1/N`` (Req 4.1).
      Benchmark bỏ qua mọi dự đoán mô hình: dùng TẤT CẢ ticker, không lọc theo
      ``pred_label`` (thuần long-only, không short).
    - **Giữ (buy-and-hold):** KHÔNG tái cân bằng ở các kỳ sau. Lợi nhuận mỗi kỳ =
      trung bình cộng ``period_return`` trên các mã thuộc tập nắm giữ ban đầu mà
      *vẫn còn dữ liệu* ở kỳ đó (phân bổ đều — Req 4.1), tính qua
      :func:`~backtest.strategy.portfolio_period_return`. Đây là xấp xỉ "giữ và
      phân bổ đều": trọng số thực tế trôi theo giá giữa các kỳ, nhưng ở đơn vị quý
      với suất sinh lời kỳ, xấp xỉ trung bình-đều được dùng có chủ đích và ghi rõ
      là giả định đơn giản hóa. Kỳ không còn mã nào có dữ liệu → lợi nhuận kỳ = 0.

    ``holdings_by_period`` ghi trọng số đều ``1/N`` (N = kích thước tập ban đầu) cho
    các mã thuộc tập nắm giữ ban đầu còn dữ liệu ở mỗi kỳ (phản ánh vị thế nắm giữ
    còn hiệu lực); nhờ thế ``turnover_by_period`` cho thấy luân chuyển tập trung ở
    kỳ đầu (mua vào) và ~0 các kỳ sau (giữ).

    Args:
        signals: SignalFrame-like DataFrame, tối thiểu các cột ``ticker``,
            ``quarter_id``, ``period_return``. Các cột dự đoán (nếu có) bị bỏ qua.

    Returns:
        :class:`~backtest.strategy.StrategyResult` đo được bằng cùng
        Performance_Evaluator trên cùng khoảng test (Req 4.3).
    """
    quarters = sorted(signals["quarter_id"].unique())
    if not quarters:
        return _build_benchmark_result([], [], {})

    # Tập nắm giữ = toàn bộ ticker có dữ liệu ở kỳ đầu, sắp xác định theo ticker.
    first_q = quarters[0]
    first_slice = signals[signals["quarter_id"] == first_q]
    held_tickers = sorted(first_slice["ticker"].unique())

    # Trọng số đều 1/N cố định theo kích thước tập ban đầu (Req 4.1).
    n_held = len(held_tickers)
    base_weight = 1.0 / n_held if n_held > 0 else 0.0
    held_set = set(held_tickers)

    returns_by_quarter: List[float] = []
    holdings_by_period: Dict[object, Dict[str, float]] = {}

    for q in quarters:
        period_slice = signals[signals["quarter_id"] == q]
        # Chỉ các mã thuộc tập nắm giữ ban đầu và còn dữ liệu ở kỳ q.
        present = period_slice[period_slice["ticker"].isin(held_set)]
        present_tickers = sorted(present["ticker"].unique())

        # Lợi nhuận kỳ = trung bình period_return trên các mã còn nắm giữ (Req 4.1).
        selected_returns = (
            present[present["ticker"].isin(present_tickers)]["period_return"]
            .astype(float)
            .tolist()
        )
        returns_by_quarter.append(portfolio_period_return(selected_returns))

        # Trọng số đều 1/N cho các mã ban đầu còn dữ liệu (vị thế giữ còn hiệu lực).
        holdings_by_period[q] = {t: base_weight for t in present_tickers}

    return _build_benchmark_result(quarters, returns_by_quarter, holdings_by_period)


def equal_weight_rebalanced(signals: pd.DataFrame) -> StrategyResult:
    """Benchmark phân bổ đều, tái cân bằng mỗi kỳ (Req 4.2).

    Ngữ nghĩa: với mỗi ``quarter_id`` (duyệt tăng dần), chọn *toàn bộ* ticker có dữ
    liệu trong kỳ đó, phân bổ vốn đều — mỗi mã trọng số ``1/N`` (N = số mã có dữ liệu
    kỳ đó) — rồi tái cân bằng lại về đều ở kỳ kế tiếp (Req 4.2). Benchmark bỏ qua mọi
    dự đoán mô hình: dùng TẤT CẢ ticker, không lọc theo ``pred_label`` (thuần
    long-only, không short).

    Lợi nhuận danh mục mỗi kỳ = trung bình cộng ``period_return`` trên các mã có dữ
    liệu kỳ đó (Req 4.2), tính qua :func:`~backtest.strategy.portfolio_period_return`;
    kỳ không có mã nào → lợi nhuận kỳ = 0. ``holdings_by_period`` ghi trọng số đều
    mỗi kỳ; ``turnover_by_period`` phản ánh luân chuyển do tái cân bằng.

    Args:
        signals: SignalFrame-like DataFrame, tối thiểu các cột ``ticker``,
            ``quarter_id``, ``period_return``. Các cột dự đoán (nếu có) bị bỏ qua.

    Returns:
        :class:`~backtest.strategy.StrategyResult` đo được bằng cùng
        Performance_Evaluator trên cùng khoảng test (Req 4.3).
    """
    quarters = sorted(signals["quarter_id"].unique())

    returns_by_quarter: List[float] = []
    holdings_by_period: Dict[object, Dict[str, float]] = {}

    for q in quarters:
        period_slice = signals[signals["quarter_id"] == q]
        # Toàn bộ ticker có dữ liệu trong kỳ (thứ tự xác định theo ticker).
        tickers = sorted(period_slice["ticker"].unique())

        # Phân bổ vốn đều trên các mã có dữ liệu kỳ này (tái cân bằng — Req 4.2).
        holdings_by_period[q] = _equal_weights(tickers)

        # Lợi nhuận kỳ = trung bình period_return trên các mã kỳ đó (Req 4.2).
        selected_returns = (
            period_slice["period_return"].astype(float).tolist()
        )
        returns_by_quarter.append(portfolio_period_return(selected_returns))

    return _build_benchmark_result(quarters, returns_by_quarter, holdings_by_period)
