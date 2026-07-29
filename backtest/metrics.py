"""Performance_Evaluator (`backtest/metrics.py`) — chỉ số hiệu quả đầu tư (Req 5).

Module này chứa các *pure function* tính chỉ số hiệu quả từ một chuỗi lợi nhuận
theo kỳ (Period_Return theo quý). Mọi hàm nhận đầu vào dạng ``pd.Series`` hoặc
array-like/list (chuyển bằng :func:`numpy.asarray`) và trả về ``float`` thuần —
không phụ thuộc trạng thái, dễ kiểm thử bằng property test (P6, P7, P8, P10).

Các chỉ số (Req 5.1–5.5):

- :func:`cumulative_return` — lợi nhuận tích lũy ``∏(1 + r) − 1`` (Req 5.1).
- :func:`mean_std_period` — trung bình và độ lệch chuẩn theo kỳ, std ddof=1 (Req 5.2).
- :func:`sharpe_ratio` — ``mean(r − rf) / std(r)``, std ddof=1 (Req 5.3).
- :func:`max_drawdown` — sụt giảm tối đa từ đường equity ``E_t = ∏(1 + r_i)`` (Req 5.4).
- :func:`hit_rate` — tỷ lệ số kỳ có lợi nhuận dương (Req 5.5).

Quy ước xử lý biên (nhất quán để property test P6–P10 đi qua):

- **Chuỗi rỗng:** :func:`cumulative_return` = 0.0 (tích rỗng = 1 → 1−1 = 0);
  :func:`hit_rate` = 0.0 (không có kỳ dương); :func:`mean_std_period` = (0.0, 0.0);
  :func:`sharpe_ratio` = 0.0; :func:`max_drawdown` = 0.0 (không có sụt giảm).
- **std = 0** (mọi lợi nhuận bằng nhau, gồm cả chuỗi một phần tử với ddof=1):
  :func:`sharpe_ratio` trả về 0.0 có kiểm soát — KHÔNG chia cho 0, không ném lỗi.
- **Chuỗi một phần tử:** std ddof=1 không xác định → :func:`mean_std_period` trả
  std = 0.0 (thay cho NaN) để đảm bảo Sharpe an toàn và các chỉ số ổn định.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Sequence, Tuple, Union

import numpy as np
import pandas as pd

if TYPE_CHECKING:  # tránh import vòng ở runtime; chỉ dùng cho type-hint.
    from backtest.strategy import StrategyResult

ArrayLike = Union[Sequence[float], np.ndarray, "object"]

# Đường dẫn báo cáo mặc định cho bảng chỉ số tổng hợp (Req 5.6).
DEFAULT_PERFORMANCE_PATH = "reports/backtest_performance.csv"

# Thứ tự cột chuẩn của reports/backtest_performance.csv (theo design.md Data Models).
PERFORMANCE_COLUMNS = [
    "strategy",
    "cost_scenario",
    "cumulative_return",
    "mean_period_return",
    "std_period_return",
    "sharpe_ratio",
    "max_drawdown",
    "hit_rate",
    "total_cost",
]


def _as_array(period_returns: ArrayLike) -> np.ndarray:
    """Chuyển đầu vào (pd.Series / list / ndarray) thành mảng float 1 chiều.

    Chấp nhận cả ``pd.Series`` (tầng chiến lược sinh ra, index = quarter_id) lẫn
    list/tuple/ndarray. Trả về mảng ``float`` để tính toán số học ổn định.

    Args:
        period_returns: Chuỗi lợi nhuận theo kỳ, dạng array-like bất kỳ.

    Returns:
        Mảng ``numpy`` 1 chiều kiểu float (có thể rỗng).
    """
    arr = np.asarray(period_returns, dtype=float)
    return np.ravel(arr)


def cumulative_return(period_returns: ArrayLike) -> float:
    """Tính lợi nhuận tích lũy ``∏(1 + r_t) − 1`` (Req 5.1).

    Lợi nhuận tích lũy phản ánh mức tăng trưởng gộp (compounded) của một đồng vốn
    qua toàn bộ chuỗi kỳ. Với chuỗi rỗng, tích rỗng bằng 1 nên kết quả là 0.0;
    với chuỗi toàn số 0, kết quả cũng bằng 0.0.

    Args:
        period_returns: Chuỗi lợi nhuận theo kỳ (array-like hoặc ``pd.Series``).

    Returns:
        Lợi nhuận tích lũy dạng ``float``.
    """
    r = _as_array(period_returns)
    if r.size == 0:
        return 0.0
    return float(np.prod(1.0 + r) - 1.0)


def mean_std_period(period_returns: ArrayLike) -> Tuple[float, float]:
    """Tính trung bình và độ lệch chuẩn của lợi nhuận theo kỳ (Req 5.2).

    Độ lệch chuẩn dùng ``ddof=1`` (ước lượng mẫu không chệch). Với chuỗi rỗng trả
    về ``(0.0, 0.0)``; với chuỗi một phần tử, std ddof=1 không xác định nên được
    quy ước bằng 0.0 (thay vì NaN) để giữ tính nhất quán và an toàn cho Sharpe.
    Khi mọi phần tử bằng nhau (phương sai thực bằng 0), std được trả về đúng 0.0
    kể cả khi tính toán số thực (floating point) sinh sai số rất nhỏ.

    Args:
        period_returns: Chuỗi lợi nhuận theo kỳ (array-like hoặc ``pd.Series``).

    Returns:
        Cặp ``(mean, std)`` dạng ``float``.
    """
    r = _as_array(period_returns)
    if r.size == 0:
        return 0.0, 0.0
    mean = float(np.mean(r))
    # Mọi phần tử bằng nhau (gồm cả chuỗi một phần tử) → phương sai thực bằng 0.
    # Dùng peak-to-peak (max−min) để phát hiện chính xác, tránh sai số của np.std.
    if r.size < 2 or np.ptp(r) == 0.0:
        return mean, 0.0
    std = float(np.std(r, ddof=1))
    return mean, std


def sharpe_ratio(period_returns: ArrayLike, rf: float = 0.0) -> float:
    """Tính Sharpe_Ratio ``mean(r − rf) / std(r)`` với std ddof=1 (Req 5.3).

    Lãi suất phi rủi ro ``rf`` cấu hình được, mặc định 0. Khi độ lệch chuẩn bằng 0
    (mọi lợi nhuận kỳ bằng nhau, gồm cả chuỗi một phần tử hoặc rỗng), hàm trả về
    0.0 có kiểm soát — KHÔNG chia cho 0 và không ném lỗi.

    Args:
        period_returns: Chuỗi lợi nhuận theo kỳ (array-like hoặc ``pd.Series``).
        rf: Lãi suất phi rủi ro theo kỳ (mặc định 0.0).

    Returns:
        Sharpe_Ratio dạng ``float``; 0.0 khi std = 0 hoặc chuỗi rỗng.
    """
    r = _as_array(period_returns)
    if r.size == 0:
        return 0.0
    # Dùng chung logic phát hiện std=0 với mean_std_period (an toàn số thực).
    _, std = mean_std_period(r)
    if std == 0.0:
        return 0.0
    return float(np.mean(r - rf) / std)


def max_drawdown(period_returns: ArrayLike) -> float:
    """Tính Max_Drawdown từ đường equity ``E_t = ∏(1 + r_i)`` (Req 5.4).

    Dựng đường vốn tích lũy ``E_t``, theo dõi đỉnh chạy (running peak)
    ``max_{s≤t} E_s``, và lấy mức sụt giảm sâu nhất
    ``MDD = min_t (E_t / max_{s≤t} E_s − 1)``.

    Giá trị luôn nằm trong ``[−1, 0]``: bằng 0 khi mọi lợi nhuận kỳ không âm (không
    có sụt giảm), và không thấp hơn −1 (mất tối đa toàn bộ vốn). Thêm các kỳ có lợi
    nhuận bằng 0 ở cuối chuỗi không làm thay đổi kết quả (P7). Chuỗi rỗng trả 0.0.

    Args:
        period_returns: Chuỗi lợi nhuận theo kỳ (array-like hoặc ``pd.Series``).

    Returns:
        Max_Drawdown dạng ``float`` trong khoảng ``[−1, 0]``.
    """
    r = _as_array(period_returns)
    if r.size == 0:
        return 0.0
    equity = np.cumprod(1.0 + r)
    running_peak = np.maximum.accumulate(equity)
    drawdowns = equity / running_peak - 1.0
    return float(np.min(drawdowns))


def hit_rate(period_returns: ArrayLike) -> float:
    """Tính hit rate — tỷ lệ số kỳ có lợi nhuận dương (Req 5.5).

    Bằng ``(số kỳ có r > 0) / (tổng số kỳ)``, luôn nằm trong ``[0, 1]``. Chuỗi rỗng
    trả 0.0 (không có kỳ nào dương).

    Args:
        period_returns: Chuỗi lợi nhuận theo kỳ (array-like hoặc ``pd.Series``).

    Returns:
        Hit rate dạng ``float`` trong khoảng ``[0, 1]``.
    """
    r = _as_array(period_returns)
    if r.size == 0:
        return 0.0
    return float(np.count_nonzero(r > 0.0) / r.size)


def _metrics_row(
    strategy: str,
    cost_scenario: str,
    period_returns: ArrayLike,
    total_cost: float,
    rf: float = 0.0,
) -> Dict[str, object]:
    """Dựng một hàng chỉ số cho một (chiến lược, kịch bản chi phí).

    Gộp toàn bộ pure function chỉ số (Req 5.1–5.5) trên cùng một chuỗi lợi nhuận
    kỳ, kèm nhãn ``strategy``/``cost_scenario`` và tổng chi phí ``total_cost``.

    Args:
        strategy: Tên chiến lược (``model`` / ``buy_hold_equal`` / ...).
        cost_scenario: ``gross`` (không phí) hoặc ``net`` (có phí).
        period_returns: Chuỗi lợi nhuận kỳ tương ứng kịch bản (gross hoặc net).
        total_cost: Tổng chi phí giao dịch tích lũy gán cho hàng này (kịch bản
            ``net`` dùng ``StrategyResult.total_cost``; ``gross`` dùng 0.0).
        rf: Lãi suất phi rủi ro theo kỳ cho Sharpe (mặc định 0.0).

    Returns:
        Dict ánh xạ tên cột → giá trị, theo đúng schema :data:`PERFORMANCE_COLUMNS`.
    """
    mean, std = mean_std_period(period_returns)
    return {
        "strategy": strategy,
        "cost_scenario": cost_scenario,
        "cumulative_return": cumulative_return(period_returns),
        "mean_period_return": mean,
        "std_period_return": std,
        "sharpe_ratio": sharpe_ratio(period_returns, rf=rf),
        "max_drawdown": max_drawdown(period_returns),
        "hit_rate": hit_rate(period_returns),
        "total_cost": float(total_cost),
    }


def evaluate_all(
    strategies: Dict[str, "StrategyResult"],
    output_path: Union[str, os.PathLike] = DEFAULT_PERFORMANCE_PATH,
    rf: float = 0.0,
) -> pd.DataFrame:
    """Bảng chỉ số mọi chiến lược → ``reports/backtest_performance.csv`` (Req 5.6).

    Với mỗi chiến lược trong *strategies*, sinh HAI hàng — một cho kịch bản
    ``gross`` (tính chỉ số trên :attr:`StrategyResult.period_returns_gross`) và một
    cho kịch bản ``net`` (tính trên :attr:`StrategyResult.period_returns_net`) —
    để đối chiếu tác động của Transaction_Cost (Req 3.5). Hàng ``gross`` có
    ``total_cost = 0.0`` (chưa áp phí); hàng ``net`` mang ``total_cost`` =
    :attr:`StrategyResult.total_cost` (tổng chi phí tích lũy).

    Bảng gồm các cột theo :data:`PERFORMANCE_COLUMNS`: ``strategy``,
    ``cost_scenario``, ``cumulative_return``, ``mean_period_return``,
    ``std_period_return``, ``sharpe_ratio``, ``max_drawdown``, ``hit_rate``,
    ``total_cost``. Kết quả được ghi ra CSV tại *output_path* (tự tạo thư mục cha
    nếu thiếu) và đồng thời trả về dưới dạng ``pd.DataFrame`` để tầng gọi tái dùng.

    Thứ tự hàng bám theo thứ tự khóa của *strategies*: mỗi chiến lược xuất hiện
    liên tiếp với hàng ``gross`` trước, ``net`` sau — ổn định, dễ kiểm thử.

    Args:
        strategies: Ánh xạ tên chiến lược → :class:`~backtest.strategy.StrategyResult`.
        output_path: Đường dẫn CSV đầu ra (mặc định
            ``reports/backtest_performance.csv``). Cho phép test chuyển hướng.
        rf: Lãi suất phi rủi ro theo kỳ dùng cho Sharpe (mặc định 0.0).

    Returns:
        ``pd.DataFrame`` bảng chỉ số (2 hàng cho mỗi chiến lược), cùng nội dung
        được ghi ra CSV.
    """
    rows = []
    for name, result in strategies.items():
        # Kịch bản gross: chưa áp phí nên total_cost = 0.0 (Req 3.5, 5.6).
        rows.append(
            _metrics_row(name, "gross", result.period_returns_gross, 0.0, rf=rf)
        )
        # Kịch bản net: total_cost = tổng chi phí giao dịch tích lũy.
        rows.append(
            _metrics_row(
                name, "net", result.period_returns_net, result.total_cost, rf=rf
            )
        )

    df = pd.DataFrame(rows, columns=PERFORMANCE_COLUMNS)

    # Tạo thư mục reports/ nếu thiếu rồi ghi CSV (không ghi index).
    out = Path(output_path)
    if out.parent != Path(""):
        out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    return df
