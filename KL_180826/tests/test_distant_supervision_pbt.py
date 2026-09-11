"""Property-based tests for B1 Distant_Supervision_Module (Req 11).

Covers four design properties of ``experiments/b1_distant_supervision.py``:

- **Property 12** — noisy-label thresholding at ±2% (``classify_return``).
- **Property 13** — the return window is clipped inside the period containing the
  posting date, and mutating prices of later periods does not change the label.
- **Property 14** — the article classifier is trained only on articles from
  periods strictly before the cutoff (``select_training_articles``).
- **Property 4 (B1 aggregation)** — mutating article data of periods q' > q does
  not change ``ds_pos_prob_mean`` / ``ds_net_sentiment`` at q (metamorphic,
  ``aggregate_ds_features``).

All properties are exercised with Hypothesis. The suite-wide ``default``
Hypothesis profile (see ``tests/conftest.py``) guarantees at least 100 iterations
per property.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from experiments.b1_distant_supervision import (
    DEFAULT_THRESHOLD,
    aggregate_ds_features,
    build_noisy_labels,
    classify_return,
    select_return_trading_days,
    select_training_articles,
)
from experiments.common.periods import quarter_bounds, quarter_id_from_date


# ---------------------------------------------------------------------------
# Property 12: noisy-label thresholding at ±2%.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 12: classify_return assigns
# "positive" iff return >= +threshold, "negative" iff return <= -threshold, and
# "neutral" strictly between the two thresholds (inclusive boundaries).


@settings(max_examples=100)
@given(
    ret=st.floats(
        min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False
    ),
    threshold=st.floats(
        min_value=0.001, max_value=0.2, allow_nan=False, allow_infinity=False
    ),
)
def test_classify_return_threshold(ret, threshold):
    """Property 12: pos/neg/neutral boundaries hold for arbitrary returns.

    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    label = classify_return(ret, threshold)
    if ret >= threshold:
        assert label == "positive"
    elif ret <= -threshold:
        assert label == "negative"
    else:
        assert label == "neutral"
        # Strictly inside the band.
        assert -threshold < ret < threshold


@settings(max_examples=100)
@given(
    threshold=st.floats(
        min_value=0.001, max_value=0.2, allow_nan=False, allow_infinity=False
    )
)
def test_classify_return_inclusive_boundaries(threshold):
    """Property 12 (boundary): exact ±threshold are inclusive.

    A return exactly equal to +threshold is positive; exactly -threshold is
    negative (Req 11.2, 11.3 use "greater than or equal" / "less than or equal").

    **Validates: Requirements 11.2, 11.3, 11.4**
    """
    assert classify_return(threshold, threshold) == "positive"
    assert classify_return(-threshold, threshold) == "negative"


# ---------------------------------------------------------------------------
# Shared strategies for price / date generation (Property 13).
# ---------------------------------------------------------------------------


@st.composite
def _quarter_and_posting_date(draw):
    """Draw a quarter_id and a posting date d inside that quarter.

    Biases towards dates near the end of the quarter to exercise the window
    clipping branch (Property 13 edge case from the design prework).
    """
    year = draw(st.integers(min_value=2019, max_value=2024))
    quarter = draw(st.integers(min_value=1, max_value=4))
    quarter_id = f"{year}Q{quarter}"
    q_start, q_end = quarter_bounds(quarter_id)
    span_days = int((q_end - q_start).days)
    # Bias: sometimes pick a date very close to the quarter end.
    if draw(st.booleans()):
        offset = draw(st.integers(min_value=max(0, span_days - 4), max_value=span_days))
    else:
        offset = draw(st.integers(min_value=0, max_value=span_days))
    d = q_start + pd.Timedelta(days=offset)
    return quarter_id, d


@st.composite
def _daily_trading_dates(draw, start, end):
    """Draw a sorted set of trading dates (a subset of business days) in a range."""
    all_days = pd.bdate_range(start=start, end=end)
    if len(all_days) == 0:
        return pd.Series([], dtype="datetime64[ns]")
    # Keep each business day with high probability so windows have days to use.
    keep_flags = draw(
        st.lists(
            st.booleans(), min_size=len(all_days), max_size=len(all_days)
        )
    )
    kept = [day for day, keep in zip(all_days, keep_flags) if keep]
    if not kept:
        kept = [all_days[0]]
    return pd.Series(pd.to_datetime(kept)).sort_values().reset_index(drop=True)


# ---------------------------------------------------------------------------
# Property 13: return window clipped inside the period + metamorphic label.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 13: the trading days used to
# compute the return lie entirely within the quarter containing d, and mutating
# prices of later quarters does not change the noisy label.


@settings(max_examples=100)
@given(data=st.data())
def test_return_window_within_quarter(data):
    """Property 13 (part 1): selected trading days lie within d's quarter.

    **Validates: Requirements 11.1, 11.5**
    """
    quarter_id, d = data.draw(_quarter_and_posting_date())
    q_start, q_end = quarter_bounds(quarter_id)
    # Trading dates spanning well beyond the quarter end (into future quarters),
    # so that clipping is actually exercised.
    dates = data.draw(
        _daily_trading_dates(
            start=q_start, end=q_end + pd.Timedelta(days=120)
        )
    )

    selected = select_return_trading_days(dates, d, quarter_id)
    for day in selected:
        assert q_start <= day <= q_end, (
            f"Trading day {day} used for return is outside quarter "
            f"{quarter_id} [{q_start}, {q_end}]"
        )
        assert day > pd.Timestamp(d)  # strictly after posting date
    # At most the horizon (3) trading days.
    assert len(selected) <= 3


@settings(max_examples=100)
@given(data=st.data())
def test_later_quarter_prices_do_not_change_label(data):
    """Property 13 (part 2): mutating later-quarter prices keeps the label.

    Build a single article at date d in quarter q. Compute its noisy label with
    a base price series, then arbitrarily mutate every close price strictly
    after the quarter end. The label must be unchanged.

    **Validates: Requirements 11.1, 11.5**
    """
    quarter_id, d = data.draw(_quarter_and_posting_date())
    q_start, q_end = quarter_bounds(quarter_id)

    # Trading dates covering the quarter and beyond into later quarters.
    dates = data.draw(
        _daily_trading_dates(
            start=q_start, end=q_end + pd.Timedelta(days=150)
        )
    )
    n = len(dates)
    closes = data.draw(
        st.lists(
            st.floats(
                min_value=1.0, max_value=500.0, allow_nan=False, allow_infinity=False
            ),
            min_size=n,
            max_size=n,
        )
    )
    prices = pd.DataFrame({"date": dates, "close": closes})

    ticker = "TST"
    articles = pd.DataFrame(
        {"ticker": [ticker], "date": [pd.Timestamp(d)], "text_tokenized": ["x y z"]}
    )

    base = build_noisy_labels(articles, {ticker: prices})

    # Mutate every close strictly after the quarter end (later quarters).
    mutated_prices = prices.copy()
    later_mask = mutated_prices["date"] > q_end
    n_later = int(later_mask.sum())
    if n_later:
        new_vals = data.draw(
            st.lists(
                st.floats(
                    min_value=1.0,
                    max_value=1000.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
                min_size=n_later,
                max_size=n_later,
            )
        )
        mutated_prices.loc[later_mask, "close"] = new_vals

    mutated = build_noisy_labels(articles, {ticker: mutated_prices})

    # Both either produce a label or both are excluded (empty).
    assert base.empty == mutated.empty
    if not base.empty:
        assert (
            base.iloc[0]["noisy_label"] == mutated.iloc[0]["noisy_label"]
        ), "Label changed after mutating later-quarter prices"
        assert base.iloc[0]["noisy_return"] == mutated.iloc[0]["noisy_return"]


# ---------------------------------------------------------------------------
# Property 14: classifier trains only on pre-cutoff articles.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 14: select_training_articles keeps
# only articles whose quarter_id is strictly before the cutoff.


def _consecutive_quarters(n, start_year=2020):
    ids = []
    year, quarter = start_year, 1
    for _ in range(n):
        ids.append(f"{year}Q{quarter}")
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1
    return ids


@settings(max_examples=100)
@given(
    n=st.integers(min_value=1, max_value=24),
    cutoff_idx=st.integers(min_value=0, max_value=23),
)
def test_training_articles_only_pre_cutoff(n, cutoff_idx):
    """Property 14: training set contains only quarters < cutoff.

    **Validates: Requirements 11.6**
    """
    quarters = _consecutive_quarters(n + 1)
    cutoff = quarters[cutoff_idx % len(quarters)]

    # One article per quarter (label irrelevant for this selection property).
    labeled = pd.DataFrame(
        {
            "ticker": ["T"] * n,
            "quarter_id": quarters[:n],
            "text_tokenized": ["a b"] * n,
            "noisy_label": ["neutral"] * n,
        }
    )

    train = select_training_articles(labeled, cutoff)
    # Every selected article is strictly before cutoff.
    assert (train["quarter_id"].astype(str) < str(cutoff)).all()
    # No pre-cutoff article is dropped.
    expected = labeled[labeled["quarter_id"].astype(str) < str(cutoff)]
    assert len(train) == len(expected)


# ---------------------------------------------------------------------------
# Property 4 (B1 aggregation): period causality — no future leakage.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 4: mutating article probabilities
# of periods strictly after q does not change ds_pos_prob_mean / ds_net_sentiment
# computed at q (aggregate_ds_features).

_DS_COLS = ["ds_pos_prob_mean", "ds_net_sentiment"]


@st.composite
def _article_probs_frame(draw):
    """Draw a per-article probability frame across multiple quarters/tickers."""
    n_tickers = draw(st.integers(min_value=1, max_value=3))
    frames = []
    for t in range(n_tickers):
        n_q = draw(st.integers(min_value=2, max_value=6))
        quarters = _consecutive_quarters(n_q)
        rows = []
        for q in quarters:
            # Several articles per quarter.
            n_art = draw(st.integers(min_value=1, max_value=4))
            for _ in range(n_art):
                pos = draw(
                    st.floats(
                        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
                    )
                )
                neg = draw(
                    st.floats(
                        min_value=0.0,
                        max_value=1.0 - pos if pos <= 1.0 else 0.0,
                        allow_nan=False,
                        allow_infinity=False,
                    )
                )
                rows.append(
                    {
                        "ticker": f"T{t}",
                        "quarter_id": q,
                        "pos_prob": pos,
                        "neg_prob": neg,
                    }
                )
        frames.append(pd.DataFrame(rows))
    return pd.concat(frames, ignore_index=True)


def _row_for(df, ticker, quarter_id):
    mask = (df["ticker"] == ticker) & (df["quarter_id"] == quarter_id)
    sub = df[mask]
    assert len(sub) == 1
    return sub.iloc[0]


@settings(max_examples=100)
@given(_article_probs_frame(), st.data())
def test_future_periods_do_not_affect_ds_aggregation(df, data):
    """Property 4 (B1): later periods cannot change ds features at period q.

    Pick a (ticker, q). Mutate/add article probabilities for every period
    strictly after q (same ticker). The aggregated ds_pos_prob_mean and
    ds_net_sentiment at (ticker, q) must be identical before and after.

    **Validates: Requirements 4.3, 4.4, 4.5, 11.7**
    """
    baseline = aggregate_ds_features(df)

    tickers = sorted(df["ticker"].unique())
    ticker = data.draw(st.sampled_from(tickers))
    quarters = sorted(df[df["ticker"] == ticker]["quarter_id"].unique())
    if len(quarters) < 2:
        return
    q_pos = data.draw(st.integers(min_value=0, max_value=len(quarters) - 2))
    q = quarters[q_pos]
    later_quarters = quarters[q_pos + 1 :]

    mutated = df.copy()
    # Mutate probabilities of later-quarter rows for this ticker.
    for lq in later_quarters:
        mask = (mutated["ticker"] == ticker) & (mutated["quarter_id"] == lq)
        n_rows = int(mask.sum())
        if n_rows:
            new_pos = data.draw(
                st.lists(
                    st.floats(
                        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
                    ),
                    min_size=n_rows,
                    max_size=n_rows,
                )
            )
            new_neg = data.draw(
                st.lists(
                    st.floats(
                        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
                    ),
                    min_size=n_rows,
                    max_size=n_rows,
                )
            )
            mutated.loc[mask, "pos_prob"] = new_pos
            mutated.loc[mask, "neg_prob"] = new_neg

    mutated_agg = aggregate_ds_features(mutated)

    before = _row_for(baseline, ticker, q)
    after = _row_for(mutated_agg, ticker, q)
    for col in _DS_COLS:
        assert math.isclose(
            float(before[col]), float(after[col]), rel_tol=1e-9, abs_tol=1e-12
        ), f"{col} at ({ticker}, {q}) changed after mutating later periods"
