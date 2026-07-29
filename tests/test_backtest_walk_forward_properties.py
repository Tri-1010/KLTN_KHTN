"""Property-based tests for walk-forward time-safety — Property P9.

Hosts **Property 9: Không rò rỉ thời gian trong walk-forward** (no temporal
leakage in walk-forward evaluation).

The leakage-safety mechanism under test is
:func:`pipeline.task10_train.time_series_split`, the single boundary that
splits the merged dataset into a training set (rows strictly before a cutoff)
and a test set (rows at/after the cutoff). Property P9 is fundamentally about
this split boundary, so it is exercised here directly at the pure split level —
no LightGBM training required, which keeps the property fast and robust while
still proving the guarantee that matters:

  *For any* cutoff in the walk-forward set, the samples used to train the
  Technical_Model contain only samples with ``quarter_id < cutoff``; and
  changing the data of periods ``>= cutoff`` does NOT change the training set
  for that cutoff (train invariance to future data).

The property is exercised with Hypothesis. The suite-wide ``default`` profile
(see ``tests/conftest.py``) guarantees at least 100 iterations.

**Validates: Requirements 6.1, 6.5, 8.4**
"""

from __future__ import annotations

import pandas as pd
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from pandas.testing import assert_frame_equal

from pipeline.task10_train import time_series_split


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Full universe of quarter identifiers. Fixed-width "YYYYQn" with single-digit
# quarter (Q1..Q4) so plain string ordering matches chronological ordering —
# exactly the comparison ``time_series_split`` performs on ``quarter_id``.
ALL_QUARTERS = [f"{year}Q{q}" for year in range(2010, 2026) for q in range(1, 5)]

# Ticker symbols: short upper-case identifiers.
_TICKER = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=4)

# Bounded, finite feature/label values.
_FEATURE = st.floats(min_value=-100.0, max_value=100.0, allow_nan=False,
                     allow_infinity=False)
_LABEL = st.integers(min_value=0, max_value=1)

# Noise added to future rows when checking train invariance.
_NOISE = st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False,
                   allow_infinity=False)


@st.composite
def _multi_period_datasets(draw):
    """Build a random multi-period dataset plus a cutoff, exercising the
    primary (non-fallback) branch of :func:`time_series_split`.

    Returns ``(df, cutoff)`` where:

    - ``df`` has columns ``ticker``, ``quarter_id`` (string "YYYYQn"), two
      numeric feature columns ``f1``/``f2``, and a binary ``label`` column;
    - ``cutoff`` is one of the quarters present in ``df`` chosen so that at
      least one distinct quarter lies strictly *before* it (non-empty train)
      and at least four distinct quarters lie at/after it. Four test quarters
      guarantees ``time_series_split`` takes its primary ``quarter_id >=
      cutoff`` branch rather than the last-20% fallback.
    """
    # Distinct, chronologically ordered quarters. Need >= 5 so we can keep >= 1
    # train quarter and >= 4 test quarters around the cutoff.
    quarters = draw(
        st.lists(st.sampled_from(ALL_QUARTERS), min_size=5, max_size=14,
                 unique=True)
    )
    quarters = sorted(quarters)

    # cutoff index in [1, len-4]: >= 1 quarter below, >= 4 quarters at/after.
    cutoff_index = draw(st.integers(min_value=1, max_value=len(quarters) - 4))
    cutoff = quarters[cutoff_index]

    # Generate rows: at least one row per quarter (so every test quarter is
    # actually present in the data), plus a few extra random rows.
    rows = []
    for q in quarters:
        n_rows = draw(st.integers(min_value=1, max_value=3))
        for _ in range(n_rows):
            rows.append(
                {
                    "ticker": draw(_TICKER),
                    "quarter_id": q,
                    "f1": draw(_FEATURE),
                    "f2": draw(_FEATURE),
                    "label": draw(_LABEL),
                }
            )

    columns = ["ticker", "quarter_id", "f1", "f2", "label"]
    df = pd.DataFrame(rows, columns=columns)
    return df, cutoff


# ---------------------------------------------------------------------------
# Property 9a: the training set contains only past quarters.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(_multi_period_datasets())
def test_train_set_contains_only_past_quarters(data):
    """P9a: the train set for a cutoff holds only ``quarter_id < cutoff``.

    For any cutoff in the walk-forward set, every sample used to train the
    Technical_Model has a ``quarter_id`` strictly before the cutoff, and no
    sample at/after the cutoff leaks into training. The complementary test set
    holds only ``quarter_id >= cutoff``, and the split partitions the data with
    no overlap and no loss.

    **Validates: Requirements 6.1, 6.5, 8.4**
    """
    df, cutoff = data

    train_df, test_df = time_series_split(df, cutoff=cutoff)

    # Every training sample is strictly before the cutoff (no future leakage).
    assert (train_df["quarter_id"] < cutoff).all(), (
        f"train set contains quarter_id >= cutoff {cutoff!r}: "
        f"{sorted(train_df.loc[train_df['quarter_id'] >= cutoff, 'quarter_id'].unique())}"
    )

    # Every test sample is at/after the cutoff (primary branch, >= 4 quarters).
    assert (test_df["quarter_id"] >= cutoff).all(), (
        f"test set contains quarter_id < cutoff {cutoff!r}"
    )

    # The split is an exact partition: no overlap, no rows lost.
    assert len(train_df) + len(test_df) == len(df)
    # Non-trivial: the generator guarantees a non-empty train set.
    assert len(train_df) > 0


# ---------------------------------------------------------------------------
# Property 9b: the training set is invariant to future data.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(_multi_period_datasets(), _NOISE)
def test_train_set_invariant_to_future_data(data, noise):
    """P9b: mutating periods ``>= cutoff`` never changes the training set.

    Take the same dataset, arbitrarily mutate the feature/label values of every
    row at/after the cutoff (add noise to features, flip the label), then re-run
    the split. The resulting train set must be byte-for-byte identical to the
    original train set — proving that data from periods ``>= cutoff`` cannot
    influence what the model is trained on for that cutoff.

    **Validates: Requirements 6.1, 6.5, 8.4**
    """
    df, cutoff = data

    train_before, _ = time_series_split(df, cutoff=cutoff)

    # Arbitrarily mutate ONLY the future rows (quarter_id >= cutoff): perturb
    # the features and flip the label. quarter_id itself is left untouched so
    # the split boundary — and thus the test-quarter count / branch — is stable.
    mutated = df.copy()
    future_mask = mutated["quarter_id"] >= cutoff
    # Sanity: there really are future rows to mutate (primary branch).
    assume(future_mask.any())
    mutated.loc[future_mask, "f1"] = mutated.loc[future_mask, "f1"] + noise
    mutated.loc[future_mask, "f2"] = mutated.loc[future_mask, "f2"] * -1.0 - noise
    mutated.loc[future_mask, "label"] = 1 - mutated.loc[future_mask, "label"]

    train_after, _ = time_series_split(mutated, cutoff=cutoff)

    # The training set is unchanged: same rows, same values, same order.
    assert_frame_equal(
        train_before.reset_index(drop=True),
        train_after.reset_index(drop=True),
    )
