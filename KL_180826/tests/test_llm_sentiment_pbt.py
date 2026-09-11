"""Property-based tests for A6 LLM sentiment aggregation (Req 8.6).

Covers **Property 10** of ``experiments/a6_llm_sentiment.py``:

- **Property 10** — *Nhất quán tỷ lệ sentiment từ LLM*: for any set of LLM
  labels for a ``(ticker, Period_q)`` with at least one article, the ratios
  ``llm_pos_ratio`` and ``llm_neg_ratio`` together with the neutral ratio SHALL
  sum to 1, and ``llm_net_sentiment`` SHALL equal
  ``llm_pos_ratio − llm_neg_ratio``.

The property is exercised with Hypothesis. The suite-wide ``default`` Hypothesis
profile (see ``tests/conftest.py``) guarantees at least 100 iterations per
property.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from experiments.a6_llm_sentiment import aggregate_llm_features
from experiments.common.periods import quarter_id_from_date


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# quarter_id_from_date accepts anything pd.Timestamp() can parse. We build ISO
# date strings from constrained year/month/day ranges so every generated date is
# always valid (day <= 28 avoids month-length / leap-year edge cases).
_iso_dates = st.builds(
    lambda y, m, d: f"{y:04d}-{m:02d}-{d:02d}",
    st.integers(min_value=2015, max_value=2025),
    st.integers(min_value=1, max_value=12),
    st.integers(min_value=1, max_value=28),
)

_tickers = st.sampled_from(["AAA", "BBB", "CCC", "DDD"])
_sentiments = st.sampled_from(["positive", "negative", "neutral"])


@st.composite
def _llm_label_frames(draw):
    """Draw a DataFrame of LLM labels with at least one article.

    Each row carries the minimum columns ``aggregate_llm_features`` needs:
    ``ticker``, ``date`` and ``sentiment``.
    """
    n = draw(st.integers(min_value=1, max_value=40))
    tickers = draw(st.lists(_tickers, min_size=n, max_size=n))
    dates = draw(st.lists(_iso_dates, min_size=n, max_size=n))
    sentiments = draw(st.lists(_sentiments, min_size=n, max_size=n))
    return pd.DataFrame(
        {
            "ticker": tickers,
            "date": dates,
            "sentiment": sentiments,
        }
    )


# ---------------------------------------------------------------------------
# Property 10: sentiment ratios are consistent.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 10: for every (ticker, quarter_id)
# group with >= 1 article, llm_pos_ratio + llm_neg_ratio + neutral_ratio == 1
# and llm_net_sentiment == llm_pos_ratio - llm_neg_ratio.


@settings(max_examples=100)
@given(_llm_label_frames())
def test_llm_sentiment_ratios_are_consistent(labels):
    """Property 10: pos+neg+neutral == 1 and net == pos - neg per group.

    For any set of LLM labels (>= 1 article), each ``(ticker, quarter_id)``
    group in the aggregated result satisfies:

    - ``0 <= llm_pos_ratio, llm_neg_ratio <= 1`` and ``pos + neg <= 1``;
    - the neutral fraction ``1 - pos - neg`` matches the observed neutral
      fraction for that group, i.e. ``pos + neg + neutral == 1``;
    - ``llm_net_sentiment == llm_pos_ratio - llm_neg_ratio``.

    **Validates: Requirements 8.6**
    """
    result = aggregate_llm_features(labels)

    # With >= 1 article there is always at least one non-empty group.
    assert not result.empty

    # Recompute expected neutral fractions directly from the generated data so
    # the property is checked against ground truth, not the code under test.
    work = labels.copy()
    work["quarter_id"] = work["date"].map(quarter_id_from_date)
    work["sentiment"] = work["sentiment"].astype(str).str.strip().str.lower()

    for _, row in result.iterrows():
        pos = row["llm_pos_ratio"]
        neg = row["llm_neg_ratio"]
        net = row["llm_net_sentiment"]

        # Ratios are valid probabilities and pos + neg cannot exceed 1.
        assert 0.0 <= pos <= 1.0
        assert 0.0 <= neg <= 1.0
        assert pos + neg <= 1.0 + 1e-9

        # Observed neutral fraction for this exact group from the source data.
        group = work[
            (work["ticker"] == row["ticker"])
            & (work["quarter_id"] == row["quarter_id"])
        ]
        total = len(group)
        assert total >= 1  # every emitted group has at least one article
        observed_neutral = (group["sentiment"] == "neutral").sum() / total

        # pos + neg + neutral == 1 (neutral derived as the complement).
        neutral_from_ratios = 1.0 - pos - neg
        assert neutral_from_ratios == pytest.approx(observed_neutral, abs=1e-9)
        assert pos + neg + neutral_from_ratios == pytest.approx(1.0, abs=1e-9)

        # net == pos - neg.
        assert net == pytest.approx(pos - neg, abs=1e-9)
