"""Property-based tests for the ExperimentRunner layer.

Covers two design properties:

- **Property 3** — ``time_series_split`` preserves temporal order: every train
  ``quarter_id`` is strictly before the cutoff and every test ``quarter_id`` is
  at/after the cutoff, with no temporal overlap.
- **Property 15** — experiment_id consistency: the feature, results, and report
  artifact paths built from an ``experiment_id`` all embed exactly that one id.

Both properties are exercised with Hypothesis. The suite-wide ``default``
Hypothesis profile (see ``tests/conftest.py``) guarantees at least 100
iterations per property.

Neither property invokes actual model training or reads real data — P3 only
exercises the pure ``time_series_split`` split logic, and P15 only exercises the
pure path-builder helpers — so the suite runs without heavy dependencies.
"""

from __future__ import annotations

import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from experiments.common.runner import (
    comparison_path,
    feature_path,
    report_path,
)
from pipeline.task10_train import time_series_split


# ---------------------------------------------------------------------------
# Property 3: train/test split preserves temporal order.
# ---------------------------------------------------------------------------
# Validates: Requirements 4.1

CUTOFF = "2025Q1"

# Quarter pools around the fixed cutoff. ``time_series_split`` compares
# ``quarter_id`` strings lexicographically; for the ``"YYYYQn"`` format this is
# equivalent to chronological order, so string comparison against the cutoff is
# well-defined.
_PRE_CUTOFF_QUARTERS = [
    f"{year}Q{q}" for year in (2023, 2024) for q in range(1, 5)
]  # 2023Q1 .. 2024Q4  (all < "2025Q1")
_POST_CUTOFF_QUARTERS = [
    f"{year}Q{q}" for year in (2025, 2026) for q in range(1, 5)
]  # 2025Q1 .. 2026Q4  (all >= "2025Q1")

_TICKERS = [f"T{i}" for i in range(6)]


@st.composite
def _temporal_frame(draw):
    """Build a DataFrame with >= 4 unique quarters at/after the cutoff.

    Ensures the fallback branch in ``time_series_split`` (which triggers when
    there are fewer than 4 test quarters) is NOT taken, so the property tests
    the intended cutoff behaviour. Includes a ``label_basic`` column and one
    feature column so the frame is a valid training frame.
    """
    # At least 4 distinct post-cutoff quarters so no fallback.
    post = draw(
        st.lists(
            st.sampled_from(_POST_CUTOFF_QUARTERS),
            min_size=4,
            max_size=len(_POST_CUTOFF_QUARTERS),
            unique=True,
        )
    )
    # Any number of pre-cutoff quarters (possibly none) for the train side.
    pre = draw(
        st.lists(
            st.sampled_from(_PRE_CUTOFF_QUARTERS),
            min_size=0,
            max_size=len(_PRE_CUTOFF_QUARTERS),
            unique=True,
        )
    )
    tickers = draw(
        st.lists(st.sampled_from(_TICKERS), min_size=1, max_size=len(_TICKERS), unique=True)
    )

    quarters = pre + post
    rows = []
    for i, (t, q) in enumerate(
        (t, q) for t in tickers for q in quarters
    ):
        rows.append(
            {
                "ticker": t,
                "quarter_id": q,
                "feat1": float(i % 7),
                "label_basic": i % 2,
            }
        )
    return pd.DataFrame(rows)


@given(_temporal_frame())
def test_time_series_split_preserves_temporal_order(df):
    """Property 3: train quarters < cutoff <= test quarters, no overlap.

    **Validates: Requirements 4.1**
    """
    train_df, test_df = time_series_split(df, cutoff=CUTOFF)

    train_quarters = set(train_df["quarter_id"].unique())
    test_quarters = set(test_df["quarter_id"].unique())

    # Every train quarter is strictly before the cutoff.
    for q in train_quarters:
        assert q < CUTOFF, f"train quarter {q!r} is not < cutoff {CUTOFF!r}"

    # Every test quarter is at/after the cutoff.
    for q in test_quarters:
        assert q >= CUTOFF, f"test quarter {q!r} is not >= cutoff {CUTOFF!r}"

    # No temporal overlap between the two sets.
    assert train_quarters.isdisjoint(test_quarters), (
        f"temporal overlap: {train_quarters & test_quarters}"
    )

    # Strongest form: max train quarter is strictly before min test quarter
    # (only meaningful when both sides are non-empty).
    if train_quarters and test_quarters:
        assert max(train_quarters) < min(test_quarters)


# ---------------------------------------------------------------------------
# Property 15: experiment_id consistency across artifacts.
# ---------------------------------------------------------------------------
# Validates: Requirements 2.1, 2.2, 2.4

# Real experiment-id convention: a leading A/B, a digit, an optional lowercase
# letter (e.g. A2, A1a, A1b, A3, A6, B1).
_experiment_ids = st.from_regex(r"\A[AB][0-9][a-z]?\Z")


def _extract_from_feature_path(path: str) -> str:
    """Recover the experiment id embedded in a feature path."""
    assert path.startswith("data/features/keyword_features_")
    assert path.endswith(".csv")
    return path[len("data/features/keyword_features_") : -len(".csv")]


def _extract_from_comparison_path(path: str) -> str:
    """Recover the experiment id embedded in a comparison path."""
    assert path.startswith("reports/model_comparison_")
    assert path.endswith(".csv")
    return path[len("reports/model_comparison_") : -len(".csv")]


def _extract_from_report_path(path: str) -> str:
    """Recover the experiment id embedded in a report path."""
    assert path.startswith("reports/experiment_")
    assert path.endswith("_report.md")
    return path[len("reports/experiment_") : -len("_report.md")]


@given(_experiment_ids)
def test_experiment_id_consistent_across_artifacts(experiment_id):
    """Property 15: all artifact paths embed exactly the one experiment id.

    **Validates: Requirements 2.1, 2.2, 2.4**
    """
    fpath = feature_path(experiment_id)
    cpath = comparison_path(experiment_id)
    rpath = report_path(experiment_id)

    # Each built path must contain the id.
    assert experiment_id in fpath
    assert experiment_id in cpath
    assert experiment_id in rpath

    # Extracting the id back from each path yields the same value.
    assert _extract_from_feature_path(fpath) == experiment_id
    assert _extract_from_comparison_path(cpath) == experiment_id
    assert _extract_from_report_path(rpath) == experiment_id
