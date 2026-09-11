"""Property-based tests for A3 Velocity_Feature_Builder (Req 7).

Covers two design properties of ``experiments/a3_velocity.py``:

- **Property 8** — the ``news_velocity`` and ``pos_neg_shift`` formulas, computed
  against the immediately-preceding period in time order.
- **Property 9** — the bounds of ``kw_entropy`` (zero when mass is concentrated on
  a single keyword, maximal for a uniform distribution, always non-negative).

Both properties are exercised with Hypothesis. The suite-wide ``default``
Hypothesis profile (see ``tests/conftest.py``) guarantees at least 100
iterations per property.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from experiments.a3_velocity import (
    compute_a3_features,
    shannon_entropy,
)


# ---------------------------------------------------------------------------
# Shared helpers / strategies
# ---------------------------------------------------------------------------


def _consecutive_quarters(n: int, start_year: int = 2018, start_q: int = 1) -> list[str]:
    """Build ``n`` consecutive ``"YYYYQn"`` ids starting at ``start_year``Q``start_q``.

    Consecutive quarters keep chronological order identical to lexical order,
    matching how ``compute_a3_features`` sorts (ticker, quarter_id).
    """
    ids: list[str] = []
    year, quarter = start_year, start_q
    for _ in range(n):
        ids.append(f"{year}Q{quarter}")
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1
    return ids


# A single-ticker sorted sequence of (news_count, sentiment_ratio) values.
@st.composite
def _single_ticker_series(draw):
    """Draw a per-ticker time series of news_count and sentiment_ratio.

    Returns a DataFrame with columns [ticker, quarter_id, news_count,
    sentiment_ratio] already in chronological order.
    """
    n = draw(st.integers(min_value=2, max_value=12))
    news_counts = draw(
        st.lists(
            st.integers(min_value=0, max_value=500),
            min_size=n,
            max_size=n,
        )
    )
    sentiment_ratios = draw(
        st.lists(
            st.floats(
                min_value=-1.0,
                max_value=1.0,
                allow_nan=False,
                allow_infinity=False,
            ),
            min_size=n,
            max_size=n,
        )
    )
    quarter_ids = _consecutive_quarters(n)
    df = pd.DataFrame(
        {
            "ticker": ["ABC"] * n,
            "quarter_id": quarter_ids,
            "news_count": news_counts,
            "sentiment_ratio": sentiment_ratios,
        }
    )
    return df


# ---------------------------------------------------------------------------
# Property 8: velocity and pos_neg_shift formulas.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 8: news_velocity and
# pos_neg_shift equal their closed-form definitions against the immediately
# preceding period in chronological order.


@settings(max_examples=100)
@given(_single_ticker_series())
def test_velocity_and_shift_formula(df):
    """Property 8: news_velocity and pos_neg_shift match their formulas.

    For each period q (with a preceding period q-1 in time order):
        news_velocity[q] == (nc[q] - nc[q-1]) / (nc[q-1] + 1)
        pos_neg_shift[q] == sentiment_ratio[q] - sentiment_ratio[q-1]
    The first period of the ticker has no q-1, so both features are NaN.

    **Validates: Requirements 7.1, 7.4**
    """
    # No keyword columns needed for this property.
    out = compute_a3_features(df, keyword_cols=[])
    # compute_a3_features sorts by (ticker, quarter_id); our input is already
    # sorted for a single ticker, so align by resetting index.
    out = out.reset_index(drop=True)

    nc = df["news_count"].to_numpy(dtype=float)
    sr = df["sentiment_ratio"].to_numpy(dtype=float)

    # First period: both features NaN (no q-1).
    assert math.isnan(out.loc[0, "news_velocity"])
    assert math.isnan(out.loc[0, "pos_neg_shift"])

    for q in range(1, len(df)):
        expected_velocity = (nc[q] - nc[q - 1]) / (nc[q - 1] + 1)
        expected_shift = sr[q] - sr[q - 1]

        assert out.loc[q, "news_velocity"] == pytest.approx(
            expected_velocity, rel=1e-9, abs=1e-12
        )
        assert out.loc[q, "pos_neg_shift"] == pytest.approx(
            expected_shift, rel=1e-9, abs=1e-12
        )


# ---------------------------------------------------------------------------
# Property 9: kw_entropy bounds.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 9: kw_entropy is 0 when mass is
# concentrated on a single keyword, maximal (log of #present keywords) for a
# uniform distribution, and always non-negative.


@settings(max_examples=100)
@given(
    st.lists(
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=20,
    )
)
def test_entropy_is_non_negative(counts):
    """Property 9 (part 1): entropy is always non-negative.

    **Validates: Requirements 7.3**
    """
    h = shannon_entropy(counts)
    assert h >= -1e-12  # allow tiny FP noise around zero


@settings(max_examples=100)
@given(
    n_keywords=st.integers(min_value=1, max_value=20),
    single_index=st.integers(min_value=0, max_value=19),
    mass=st.floats(min_value=1e-6, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_entropy_zero_when_single_keyword(n_keywords, single_index, mass):
    """Property 9 (part 2): entropy is 0 when all mass is on one keyword.

    **Validates: Requirements 7.3**
    """
    counts = [0.0] * n_keywords
    idx = single_index % n_keywords
    counts[idx] = mass
    h = shannon_entropy(counts)
    assert abs(h) < 1e-9


@settings(max_examples=100)
@given(
    n_present=st.integers(min_value=1, max_value=20),
    value=st.floats(min_value=1e-3, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_entropy_maximal_when_uniform(n_present, value):
    """Property 9 (part 3): entropy equals ln(n) for a uniform distribution.

    A uniform distribution over ``n`` present keywords attains the maximum
    entropy ``ln(n)``. We also verify no other distribution over the same
    number of present keywords can exceed this maximum.

    **Validates: Requirements 7.3**
    """
    uniform = [value] * n_present
    h_uniform = shannon_entropy(uniform)
    expected_max = math.log(n_present)
    assert h_uniform == pytest.approx(expected_max, rel=1e-9, abs=1e-12)

    # Any non-uniform distribution over the same support is <= the uniform max.
    skewed = [value] * n_present
    skewed[0] = value * 3.0  # perturb to make it non-uniform
    h_skewed = shannon_entropy(skewed)
    assert h_skewed <= h_uniform + 1e-9


@settings(max_examples=100)
@given(
    st.lists(
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=20,
    )
)
def test_entropy_upper_bounded_by_log_present(counts):
    """Property 9 (part 4): entropy never exceeds ln(#present keywords).

    **Validates: Requirements 7.3**
    """
    h = shannon_entropy(counts)
    n_present = int(np.count_nonzero(np.asarray(counts) > 0))
    if n_present <= 1:
        assert abs(h) < 1e-9
    else:
        assert h <= math.log(n_present) + 1e-9
