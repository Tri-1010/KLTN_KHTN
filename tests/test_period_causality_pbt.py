"""Property-based tests for period causality — no future leakage (Req 4).

This file hosts **Property 4** (metamorphic): mutating data of periods strictly
later than a chosen period q must NOT change the period-dependent features
computed at q. Property 4 is shared across period-dependent experiments; only
the A3 portion is exercised here (B1 aggregation will be added later, per the
design testing strategy).

The property is exercised with Hypothesis. The suite-wide ``default`` Hypothesis
profile (see ``tests/conftest.py``) guarantees at least 100 iterations.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from experiments.a3_velocity import A3_FEATURE_COLUMNS, compute_a3_features


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_KEYWORD_COLS = ["kw_a", "kw_b", "kw_c", "kw_d"]


def _consecutive_quarters(n: int, start_year: int = 2018) -> list[str]:
    """Return ``n`` consecutive ``"YYYYQn"`` ids from ``start_year``Q1."""
    ids: list[str] = []
    year, quarter = start_year, 1
    for _ in range(n):
        ids.append(f"{year}Q{quarter}")
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1
    return ids


@st.composite
def _multi_period_frame(draw):
    """Draw a multi-period, multi-ticker A3 input frame.

    Returns ``(df, keyword_cols)`` where ``df`` has columns
    [ticker, quarter_id, news_count, sentiment_ratio, kw_a..kw_d] with each
    ticker's rows already in chronological order.
    """
    n_tickers = draw(st.integers(min_value=1, max_value=3))
    frames = []
    for t in range(n_tickers):
        n = draw(st.integers(min_value=2, max_value=8))
        quarter_ids = _consecutive_quarters(n)
        row_data = {
            "ticker": [f"T{t}"] * n,
            "quarter_id": quarter_ids,
            "news_count": draw(
                st.lists(st.integers(min_value=0, max_value=300), min_size=n, max_size=n)
            ),
            "sentiment_ratio": draw(
                st.lists(
                    st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
                    min_size=n,
                    max_size=n,
                )
            ),
        }
        for col in _KEYWORD_COLS:
            row_data[col] = draw(
                st.lists(st.integers(min_value=0, max_value=50), min_size=n, max_size=n)
            )
        frames.append(pd.DataFrame(row_data))
    df = pd.concat(frames, ignore_index=True)
    return df


def _feature_row_for(features: pd.DataFrame, ticker: str, quarter_id: str) -> pd.Series:
    """Return the single A3 feature row for a (ticker, quarter_id)."""
    mask = (features["ticker"] == ticker) & (features["quarter_id"] == quarter_id)
    sub = features[mask]
    assert len(sub) == 1
    return sub.iloc[0]


def _series_equal_nan(a: pd.Series, b: pd.Series) -> bool:
    """Compare two feature rows treating NaN == NaN as equal."""
    for col in A3_FEATURE_COLUMNS:
        av, bv = a[col], b[col]
        if isinstance(av, float) and math.isnan(av):
            if not (isinstance(bv, float) and math.isnan(bv)):
                return False
        else:
            if not np.isclose(av, bv, rtol=1e-9, atol=1e-12):
                return False
    return True


# ---------------------------------------------------------------------------
# Property 4: period causality — no future leakage (A3).
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 4: mutating data of periods
# strictly after q does not change the A3 features (news_velocity, kw_novelty,
# kw_entropy, pos_neg_shift) computed at q.


@settings(max_examples=100)
@given(_multi_period_frame(), st.data())
def test_future_periods_do_not_affect_current_a3_features(df, data):
    """Property 4: later periods cannot change A3 features at period q.

    Pick one (ticker, q). Arbitrarily mutate the news_count, sentiment_ratio,
    and keyword counts of every period strictly later than q (same ticker).
    The A3 features computed for (ticker, q) must be identical before and after.

    **Validates: Requirements 4.3, 4.4, 4.5, 7.5**
    """
    baseline = compute_a3_features(df, keyword_cols=_KEYWORD_COLS)

    # Choose a ticker and a period index within that ticker's sorted series.
    tickers = sorted(df["ticker"].unique())
    ticker = data.draw(st.sampled_from(tickers))
    ticker_rows = (
        df[df["ticker"] == ticker]
        .sort_values("quarter_id", kind="mergesort")
        .reset_index()  # keep original index in a column named "index"
    )
    n = len(ticker_rows)
    # q must have at least one strictly-later period to mutate.
    if n < 2:
        return
    q_pos = data.draw(st.integers(min_value=0, max_value=n - 2))
    q_quarter = ticker_rows.loc[q_pos, "quarter_id"]

    # Mutate every strictly-later period for this ticker.
    mutated = df.copy()
    for later_pos in range(q_pos + 1, n):
        orig_idx = ticker_rows.loc[later_pos, "index"]
        mutated.at[orig_idx, "news_count"] = data.draw(
            st.integers(min_value=0, max_value=1000)
        )
        mutated.at[orig_idx, "sentiment_ratio"] = data.draw(
            st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)
        )
        for col in _KEYWORD_COLS:
            mutated.at[orig_idx, col] = data.draw(
                st.integers(min_value=0, max_value=100)
            )

    mutated_features = compute_a3_features(mutated, keyword_cols=_KEYWORD_COLS)

    before = _feature_row_for(baseline, ticker, q_quarter)
    after = _feature_row_for(mutated_features, ticker, q_quarter)

    assert _series_equal_nan(before, after), (
        f"A3 features at ({ticker}, {q_quarter}) changed after mutating later "
        f"periods.\nbefore={before[A3_FEATURE_COLUMNS].to_dict()}\n"
        f"after={after[A3_FEATURE_COLUMNS].to_dict()}"
    )
