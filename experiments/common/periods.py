"""Tiện ích ranh giới kỳ (quý) dùng chung cho các thí nghiệm.

Module thuần (pure utility) không có tác dụng phụ, dùng để bảo đảm ràng buộc
chống rò rỉ dữ liệu tương lai (Requirements 4.3, 4.4, 4.5):

- ``quarter_bounds(quarter_id)`` trả về ``(start_date, end_date)`` của một quý.
- ``clip_return_window(d, horizon, quarter_id)`` cắt cửa sổ tính suất sinh lời
  ``[d, d + horizon]`` tại ``end_date`` của quý chứa ``d``, để giá của các kỳ
  sau không thể ảnh hưởng tới đặc trưng/nhãn tính cho kỳ hiện tại.

Được tái sử dụng bởi:
- A3 (Velocity_Feature_Builder) — shift/aggregate theo kỳ.
- B1 (Distant_Supervision_Module) — cắt cửa sổ return window (Req 11.5).

Định dạng ``quarter_id`` là chuỗi ``"YYYYQn"`` (ví dụ ``"2025Q1"``), khớp với
``pipeline/task5_aggregate.py::assign_quarter_id``. Q1: Jan–Mar, Q2: Apr–Jun,
Q3: Jul–Sep, Q4: Oct–Dec.
"""

from __future__ import annotations

import re

import pandas as pd

__all__ = ["quarter_bounds", "clip_return_window", "quarter_id_from_date"]

# Chấp nhận "YYYYQn" với n ∈ {1,2,3,4}. Cho phép chữ "q" thường/hoa.
_QUARTER_RE = re.compile(r"^(\d{4})[Qq]([1-4])$")

# Tháng bắt đầu và tháng kết thúc của từng quý.
_QUARTER_START_MONTH = {1: 1, 2: 4, 3: 7, 4: 10}
_QUARTER_END_MONTH = {1: 3, 2: 6, 3: 9, 4: 12}


def _parse_quarter_id(quarter_id: str) -> tuple[int, int]:
    """Phân tích ``quarter_id`` dạng ``"YYYYQn"`` thành ``(year, quarter)``.

    Raises:
        ValueError: nếu ``quarter_id`` không đúng định dạng ``"YYYYQn"``.
    """
    if not isinstance(quarter_id, str):
        raise ValueError(
            f"quarter_id phải là chuỗi 'YYYYQn', nhận được kiểu {type(quarter_id).__name__}"
        )
    match = _QUARTER_RE.match(quarter_id.strip())
    if match is None:
        raise ValueError(
            f"quarter_id không hợp lệ: {quarter_id!r}. Định dạng mong đợi 'YYYYQn' "
            "với n ∈ {1,2,3,4}, ví dụ '2025Q1'."
        )
    year = int(match.group(1))
    quarter = int(match.group(2))
    return year, quarter


def quarter_bounds(quarter_id: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Trả về ``(start_date, end_date)`` của quý ``quarter_id``.

    - ``start_date`` là ngày lịch đầu tiên của quý (ví dụ Q1 → 1 tháng 1).
    - ``end_date`` là ngày lịch cuối cùng của quý (ví dụ Q1 → 31 tháng 3),
      được tính bằng ngày cuối của tháng kết thúc quý nên tự động đúng với năm
      nhuận (ví dụ Q1 năm nhuận vẫn kết thúc 31/3, Q1 không phụ thuộc tháng 2).

    Args:
        quarter_id: chuỗi ``"YYYYQn"`` (ví dụ ``"2025Q1"``, ``"2024Q4"``).

    Returns:
        Cặp ``(start_date, end_date)`` là ``pd.Timestamp``.

    Raises:
        ValueError: nếu ``quarter_id`` không đúng định dạng.

    Validates: Requirements 4.3, 4.4, 4.5.
    """
    year, quarter = _parse_quarter_id(quarter_id)

    start_month = _QUARTER_START_MONTH[quarter]
    end_month = _QUARTER_END_MONTH[quarter]

    start_date = pd.Timestamp(year=year, month=start_month, day=1)
    # Ngày cuối của tháng kết thúc quý = (đầu tháng kết thúc) + MonthEnd(0).
    # MonthEnd tự xử lý số ngày trong tháng, bao gồm cả năm nhuận.
    end_date = pd.Timestamp(year=year, month=end_month, day=1) + pd.offsets.MonthEnd(0)

    return start_date, end_date


def quarter_id_from_date(d) -> str:
    """Suy ra ``quarter_id`` dạng ``"YYYYQn"`` từ một ngày.

    Tiện ích trợ giúp cho các nơi gọi chưa biết trước quý chứa ``d``. Chữ ký
    chính ``clip_return_window`` vẫn nhận ``quarter_id`` tường minh theo thiết kế.

    Args:
        d: ngày bất kỳ (chuỗi, ``datetime``, hoặc ``pd.Timestamp``).

    Returns:
        Chuỗi ``"YYYYQn"`` của quý chứa ``d``.

    Raises:
        ValueError: nếu ``d`` không thể ép thành ngày hợp lệ.
    """
    ts = pd.Timestamp(d)
    if pd.isna(ts):
        raise ValueError(f"Không thể chuyển {d!r} thành ngày hợp lệ.")
    quarter = (ts.month - 1) // 3 + 1
    return f"{ts.year}Q{quarter}"


def clip_return_window(
    d, horizon: int, quarter_id: str
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Cắt cửa sổ tính suất sinh lời tại ranh giới của quý chứa ``d``.

    Cửa sổ danh nghĩa là ``[d, d + horizon]`` (tính theo ngày lịch). Theo thiết
    kế và Req 11.5, điểm cuối cửa sổ phải bị cắt tại ``end_date`` của quý
    ``quarter_id`` (quý chứa ``d``) để giá của các kỳ sau không thể ảnh hưởng
    tới nhãn/đặc trưng của kỳ hiện tại. Điểm đầu cũng được kẹp vào ``start_date``
    của quý để cửa sổ luôn nằm trọn trong ranh giới quý.

    Args:
        d: ngày đăng bài (chuỗi, ``datetime`` hoặc ``pd.Timestamp``); sẽ được ép
            thành ``pd.Timestamp``.
        horizon: số ngày lịch của cửa sổ danh nghĩa (``>= 0``).
        quarter_id: chuỗi ``"YYYYQn"`` của quý chứa ``d``.

    Returns:
        Cặp ``(window_start, window_end)`` là ``pd.Timestamp``, bảo đảm nằm hoàn
        toàn trong ``quarter_bounds(quarter_id)`` và ``window_start <= window_end``.

    Raises:
        ValueError: nếu ``d`` không hợp lệ, ``horizon < 0``, hoặc ``quarter_id``
            sai định dạng.

    Validates: Requirements 4.3, 4.4, 4.5 (và 11.5 qua B1).
    """
    if horizon < 0:
        raise ValueError(f"horizon phải >= 0, nhận được {horizon}.")

    ts = pd.Timestamp(d)
    if pd.isna(ts):
        raise ValueError(f"Không thể chuyển {d!r} thành ngày hợp lệ.")

    quarter_start, quarter_end = quarter_bounds(quarter_id)

    # Kẹp điểm đầu vào ranh giới đầu quý và điểm cuối vào ranh giới cuối quý.
    window_start = max(ts, quarter_start)
    nominal_end = ts + pd.Timedelta(days=horizon)
    window_end = min(nominal_end, quarter_end)

    # Nếu d nằm ngoài quý (điểm đầu bị đẩy qua điểm cuối), kẹp lại để giữ bất
    # biến window_start <= window_end và cửa sổ vẫn nằm trong ranh giới quý.
    if window_start > window_end:
        window_start = window_end

    return window_start, window_end
