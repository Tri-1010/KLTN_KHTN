"""Unit tests for TASK 2.2: shared period-boundary utilities.

Tests cover the pure quarter-boundary helpers in
``experiments.common.periods`` that guard against future-data leakage:

- ``quarter_bounds(quarter_id)`` returns the correct calendar start/end of each
  quarter, including year boundaries, the Q4→Q1 transition, and leap-year
  correctness (Req 4.3).
- ``clip_return_window(d, horizon, quarter_id)`` clips the nominal return window
  ``[d, d + horizon]`` to the quarter boundaries so later-period prices cannot
  influence current-period features/labels (Req 4.5).

Invalid inputs (bad quarter ids, negative horizon, unparseable dates) must raise
``ValueError``.
"""

import pandas as pd
import pytest

from experiments.common.periods import (
    clip_return_window,
    quarter_bounds,
    quarter_id_from_date,
)


# ---------------------------------------------------------------------------
# quarter_bounds
# ---------------------------------------------------------------------------


class TestQuarterBounds:
    """Ranh giới quý: đầu/cuối năm, chuyển Q4→Q1, năm nhuận (Req 4.3)."""

    def test_all_four_quarters_return_correct_bounds(self):
        """Q1..Q4 map to the correct calendar start/end dates."""
        assert quarter_bounds("2023Q1") == (
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-03-31"),
        )
        assert quarter_bounds("2023Q2") == (
            pd.Timestamp("2023-04-01"),
            pd.Timestamp("2023-06-30"),
        )
        assert quarter_bounds("2023Q3") == (
            pd.Timestamp("2023-07-01"),
            pd.Timestamp("2023-09-30"),
        )
        assert quarter_bounds("2023Q4") == (
            pd.Timestamp("2023-10-01"),
            pd.Timestamp("2023-12-31"),
        )

    def test_start_of_year_is_q1_start(self):
        """Q1 start is the first day of the year (Jan 1)."""
        start, _ = quarter_bounds("2025Q1")
        assert start == pd.Timestamp("2025-01-01")

    def test_end_of_year_is_q4_end(self):
        """Q4 end is the last day of the year (Dec 31)."""
        _, end = quarter_bounds("2025Q4")
        assert end == pd.Timestamp("2025-12-31")

    def test_q4_to_q1_transition_is_consecutive(self):
        """2024Q4 end and 2025Q1 start are adjacent days across the year boundary."""
        _, q4_end = quarter_bounds("2024Q4")
        q1_start, _ = quarter_bounds("2025Q1")
        assert q4_end == pd.Timestamp("2024-12-31")
        assert q1_start == pd.Timestamp("2025-01-01")
        # Adjacent / consecutive: exactly one day apart with no gap or overlap.
        assert q1_start - q4_end == pd.Timedelta(days=1)

    def test_q1_end_is_march_31_in_leap_year(self):
        """Leap year: Q1 still ends Mar 31 (independent of Feb length)."""
        _, end = quarter_bounds("2024Q1")  # 2024 is a leap year
        assert end == pd.Timestamp("2024-03-31")

    def test_q1_end_is_march_31_in_non_leap_year(self):
        """Non-leap year: Q1 also ends Mar 31."""
        _, end = quarter_bounds("2025Q1")  # 2025 is not a leap year
        assert end == pd.Timestamp("2025-03-31")

    def test_leap_year_february_quarter_bounds_match(self):
        """Q1 bounds are identical (day-of-month) in leap vs non-leap years."""
        leap_start, leap_end = quarter_bounds("2024Q1")
        nonleap_start, nonleap_end = quarter_bounds("2025Q1")
        assert (leap_start.month, leap_start.day) == (nonleap_start.month, nonleap_start.day)
        assert (leap_end.month, leap_end.day) == (nonleap_end.month, nonleap_end.day)

    def test_lowercase_q_is_accepted(self):
        """A lowercase 'q' in the id is accepted."""
        assert quarter_bounds("2023q2") == (
            pd.Timestamp("2023-04-01"),
            pd.Timestamp("2023-06-30"),
        )

    def test_surrounding_whitespace_is_stripped(self):
        """Surrounding whitespace is tolerated."""
        assert quarter_bounds("  2023Q3  ") == (
            pd.Timestamp("2023-07-01"),
            pd.Timestamp("2023-09-30"),
        )

    @pytest.mark.parametrize(
        "bad_id",
        [
            "2023Q5",  # quarter number out of range
            "2023Q0",  # quarter number out of range
            "23Q1",  # year not 4 digits
            "2023-Q1",  # wrong format
            "Q1",  # missing year
            "2023",  # missing quarter
            "abcdQ1",  # non-numeric year
            "",  # empty string
        ],
    )
    def test_invalid_quarter_id_string_raises(self, bad_id):
        """Malformed quarter id strings raise ValueError."""
        with pytest.raises(ValueError):
            quarter_bounds(bad_id)

    @pytest.mark.parametrize("bad_type", [None, 20231, 2023.1, ["2023Q1"]])
    def test_non_string_quarter_id_raises(self, bad_type):
        """Non-string quarter ids raise ValueError."""
        with pytest.raises(ValueError):
            quarter_bounds(bad_type)


# ---------------------------------------------------------------------------
# clip_return_window
# ---------------------------------------------------------------------------


class TestClipReturnWindow:
    """Cắt cửa sổ return đúng biên quý; bất biến start <= end (Req 4.5)."""

    def test_window_fully_inside_quarter_not_clipped(self):
        """A window that stays inside the quarter keeps its nominal end."""
        d = pd.Timestamp("2023-02-10")
        start, end = clip_return_window(d, horizon=5, quarter_id="2023Q1")
        assert start == d
        assert end == pd.Timestamp("2023-02-15")

    def test_window_crossing_quarter_end_is_clipped(self):
        """A window pushed past the quarter end is clipped to quarter_end.

        This is the key data-leakage-prevention behaviour (Req 4.5 / 11.5).
        """
        d = pd.Timestamp("2023-03-30")
        _, quarter_end = quarter_bounds("2023Q1")
        start, end = clip_return_window(d, horizon=10, quarter_id="2023Q1")
        assert start == d
        assert end == quarter_end  # 2023-03-31, not 2023-04-09

    def test_start_clamped_to_quarter_start_when_d_before_quarter(self):
        """When d precedes the quarter start, the start is clamped up."""
        d = pd.Timestamp("2022-12-20")  # before 2023Q1
        quarter_start, _ = quarter_bounds("2023Q1")
        start, end = clip_return_window(d, horizon=30, quarter_id="2023Q1")
        assert start == quarter_start  # 2023-01-01
        # Nominal end d+30 = 2023-01-19 is inside the quarter, so it is kept.
        assert end == pd.Timestamp("2023-01-19")
        assert start <= end

    def test_invariant_start_le_end_when_d_after_quarter(self):
        """When d is after the quarter end, the invariant start <= end holds."""
        d = pd.Timestamp("2023-05-01")  # after 2023Q1 end
        start, end = clip_return_window(d, horizon=3, quarter_id="2023Q1")
        assert start <= end

    def test_invariant_start_le_end_across_various_inputs(self):
        """window_start <= window_end for a spread of dates and horizons."""
        cases = [
            (pd.Timestamp("2023-01-01"), 0),
            (pd.Timestamp("2023-02-14"), 7),
            (pd.Timestamp("2023-03-31"), 100),
            (pd.Timestamp("2022-11-01"), 200),  # before quarter
            (pd.Timestamp("2023-06-01"), 5),  # after quarter
        ]
        for d, horizon in cases:
            start, end = clip_return_window(d, horizon=horizon, quarter_id="2023Q1")
            assert start <= end

    def test_zero_horizon_gives_zero_length_window(self):
        """horizon=0 yields a single-point window at d (inside the quarter)."""
        d = pd.Timestamp("2023-02-10")
        start, end = clip_return_window(d, horizon=0, quarter_id="2023Q1")
        assert start == d
        assert end == d

    def test_string_date_is_accepted(self):
        """A string date is coerced to a Timestamp."""
        start, end = clip_return_window("2023-02-10", horizon=5, quarter_id="2023Q1")
        assert start == pd.Timestamp("2023-02-10")
        assert end == pd.Timestamp("2023-02-15")

    def test_negative_horizon_raises(self):
        """A negative horizon raises ValueError."""
        with pytest.raises(ValueError):
            clip_return_window(pd.Timestamp("2023-02-10"), horizon=-1, quarter_id="2023Q1")

    def test_invalid_date_raises(self):
        """An unparseable date raises ValueError."""
        with pytest.raises(ValueError):
            clip_return_window("not-a-date", horizon=3, quarter_id="2023Q1")

    def test_invalid_quarter_id_raises(self):
        """A malformed quarter id raises ValueError."""
        with pytest.raises(ValueError):
            clip_return_window(pd.Timestamp("2023-02-10"), horizon=3, quarter_id="2023Q5")

    def test_clipped_window_stays_within_quarter_bounds(self):
        """The returned window always lies within quarter_bounds."""
        quarter_id = "2024Q4"
        quarter_start, quarter_end = quarter_bounds(quarter_id)
        d = pd.Timestamp("2024-12-28")
        start, end = clip_return_window(d, horizon=30, quarter_id=quarter_id)
        assert quarter_start <= start <= quarter_end
        assert quarter_start <= end <= quarter_end
        assert end == quarter_end  # 2024-12-31


# ---------------------------------------------------------------------------
# quarter_id_from_date (helper used by callers of clip_return_window)
# ---------------------------------------------------------------------------


class TestQuarterIdFromDate:
    """Helper deriving 'YYYYQn' from a date, consistent with quarter_bounds."""

    @pytest.mark.parametrize(
        "date,expected",
        [
            ("2023-01-01", "2023Q1"),
            ("2023-03-31", "2023Q1"),
            ("2023-04-01", "2023Q2"),
            ("2023-09-30", "2023Q3"),
            ("2023-10-01", "2023Q4"),
            ("2024-12-31", "2024Q4"),
        ],
    )
    def test_quarter_id_from_date(self, date, expected):
        assert quarter_id_from_date(date) == expected

    def test_derived_id_is_consistent_with_quarter_bounds(self):
        """A date's derived quarter id contains that date within its bounds."""
        d = pd.Timestamp("2024-02-29")  # leap day
        qid = quarter_id_from_date(d)
        start, end = quarter_bounds(qid)
        assert start <= d <= end

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            quarter_id_from_date("not-a-date")
