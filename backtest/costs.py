"""Transaction_Cost (`backtest/costs.py`) — mô hình phí giao dịch thị trường VN.

Chi phí giao dịch gồm hai cấu phần tách bạch (Req 3.1):

- **Brokerage_Fee**: phí môi giới áp cho *cả* lượt mua và lượt bán (mặc định 0,15%).
- **Sell_Tax**: thuế thu nhập cá nhân, áp *chỉ* cho lượt bán (mặc định 0,1%).

Phí chỉ được tính trên phần vốn *thực sự thay đổi* vị thế giữa hai kỳ (Req 3.4).
Ở mức mặc định, một vòng mua–bán (round-trip) tốn xấp xỉ 0,40%:
mua 0,15% + bán (0,15% + 0,10%).

Các trọng số danh mục được chuẩn hóa theo NAV = 1, nên `buy_value`/`sell_value`
trả về từ :func:`turnover` là phần trọng số (tỷ lệ trên NAV) chứ không phải giá
trị tuyệt đối.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostConfig:
    """Cấu hình chi phí giao dịch, bất biến (frozen) để an toàn khi tái dùng.

    Attributes:
        brokerage: Phí môi giới trên giá trị mỗi lượt mua/bán (Req 3.1). Mặc định
            0,15% (trần quy định thị trường VN là 0,5%).
        sell_tax: Thuế thu nhập cá nhân trên giá trị bán, chỉ áp khi bán (Req 3.1).
            Mặc định 0,1% theo quy định VN.
    """

    brokerage: float = 0.0015  # 0,15% mỗi lượt mua/bán
    sell_tax: float = 0.0010   # 0,1% chỉ khi bán


def turnover(
    prev_weights: dict[str, float],
    new_weights: dict[str, float],
) -> tuple[float, float]:
    """Tính giá trị mua và bán giữa hai cấu hình trọng số danh mục.

    Với mỗi ticker, so sánh trọng số mới và trọng số cũ (mặc định 0 nếu vắng mặt):
    phần trọng số *tăng* được cộng vào ``buy_value`` (mua thêm), phần trọng số
    *giảm* được cộng vào ``sell_value`` (bán bớt). Chỉ phần thay đổi được tính
    (Req 3.4). Trọng số chuẩn hóa theo NAV = 1.

    Kỳ đầu tiên (``prev_weights`` rỗng) → toàn bộ ``new_weights`` là mua mới, nên
    ``buy_value`` bằng tổng trọng số danh mục mới và ``sell_value`` bằng 0.

    Args:
        prev_weights: Trọng số danh mục kỳ trước, ánh xạ ticker → trọng số.
        new_weights: Trọng số danh mục kỳ hiện tại, ánh xạ ticker → trọng số.

    Returns:
        Cặp ``(buy_value, sell_value)``: tổng trọng số tăng (mua) và giảm (bán).
    """
    buy_value = 0.0
    sell_value = 0.0
    for ticker in prev_weights.keys() | new_weights.keys():
        delta = new_weights.get(ticker, 0.0) - prev_weights.get(ticker, 0.0)
        if delta > 0.0:
            buy_value += delta
        elif delta < 0.0:
            sell_value += -delta
    return buy_value, sell_value


def period_cost(
    prev_w: dict[str, float],
    new_w: dict[str, float],
    cfg: CostConfig,
) -> float:
    """Tính chi phí giao dịch cho một kỳ khi chuyển từ ``prev_w`` sang ``new_w``.

    Brokerage_Fee áp trên phần mua *và* phần bán; Sell_Tax áp thêm trên phần bán
    (Req 3.2, 3.3). Với kỳ đầu (``prev_w`` rỗng), toàn bộ vốn vào được coi là mua
    mới nên brokerage tính trên toàn phần inflow.

    Args:
        prev_w: Trọng số danh mục kỳ trước.
        new_w: Trọng số danh mục kỳ hiện tại.
        cfg: Cấu hình chi phí (:class:`CostConfig`).

    Returns:
        Tổng chi phí giao dịch của kỳ, chuẩn hóa theo NAV = 1. Luôn không âm.
    """
    buy_v, sell_v = turnover(prev_w, new_w)
    return buy_v * cfg.brokerage + sell_v * (cfg.brokerage + cfg.sell_tax)
