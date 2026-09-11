"""Integration test for Prediction_Signal — :func:`backtest.signals.generate_signals`.

Unlike the property-based tests in the suite, this is a genuine **integration
test**: it runs ``generate_signals`` end-to-end on the real project data under
``data/`` with the default Train_Cutoff (``2025Q1``), training a real
Technical_Model (LightGBM on ``Config_A``). It is therefore comparatively slow,
which is expected and acceptable for an integration check.

It verifies the contract of the returned SignalFrame (Req 1.2, 1.3):

- the return value is a ``DataFrame`` with exactly the exported
  :data:`~backtest.signals.SIGNAL_COLUMNS`;
- its row count matches the test set produced by the pipeline's
  ``time_series_split`` (with the real data / default cutoff this is 400
  rows: 80 tickers x 5 quarters after 2025Q1) and is non-empty;
- ``pred_proba_up`` values all lie in [0, 1];
- ``pred_label`` and ``y_true`` values are all in {0, 1};
- no row has a missing ``period_return`` (rows missing it are dropped by the
  function).
"""

from __future__ import annotations

import os

import pandas as pd
import pytest

from backtest.signals import (
    SIGNAL_COLUMNS,
    generate_signals,
)
from pipeline.task10_train import (
    KW_FEATURES_PATH,
    LABELS_PATH,
    TECH_FEATURES_PATH,
    load_and_merge_data,
    time_series_split,
)

# The default cutoff and the expected test-set size on the full real dataset
# (80 tickers x 5 quarters after 2025Q1) documented by the smoke run.
DEFAULT_CUTOFF = "2025Q1"
EXPECTED_TEST_ROWS = 400

# Real data files required for this integration test. If any is missing the
# test is skipped (rather than failing) so the suite stays green in trimmed
# checkouts; a real CI checkout is expected to have them.
_REQUIRED_DATA = (TECH_FEATURES_PATH, KW_FEATURES_PATH, LABELS_PATH)

pytestmark = pytest.mark.skipif(
    not all(os.path.exists(p) for p in _REQUIRED_DATA),
    reason=(
        "real feature/label data under data/ is required for the "
        "generate_signals integration test"
    ),
)

# lightgbm is the default Technical_Model; skip cleanly if the optional
# training dependency is unavailable in this environment.
pytest.importorskip(
    "lightgbm",
    reason="lightgbm is required to train the default Technical_Model",
)


@pytest.fixture(scope="module")
def signals() -> pd.DataFrame:
    """Run ``generate_signals`` once with defaults; reuse across assertions.

    Module scope keeps the (slow) real training to a single execution.
    """
    return generate_signals(cutoff=DEFAULT_CUTOFF)


@pytest.fixture(scope="module")
def expected_test_row_count() -> int:
    """Number of test rows from the same split ``generate_signals`` uses.

    Derived from the real data with the default cutoff so the row-count check
    is robust against data changes, independent of the hard-coded 400.
    """
    merged = load_and_merge_data(TECH_FEATURES_PATH, KW_FEATURES_PATH, LABELS_PATH)
    _, test_df = time_series_split(merged, cutoff=DEFAULT_CUTOFF)
    return len(test_df)


def test_returns_dataframe_with_expected_columns(signals):
    """SignalFrame is a DataFrame with exactly SIGNAL_COLUMNS (Req 1.2, 1.3)."""
    assert isinstance(signals, pd.DataFrame)
    assert list(signals.columns) == SIGNAL_COLUMNS


def test_row_count_matches_test_set(signals, expected_test_row_count):
    """Row count is non-empty and matches the split's test-set size (Req 1.2).

    Every test row has a Period_Return on the full real dataset, so no rows are
    dropped and the SignalFrame length equals the split's test-set size, which
    on the default cutoff is the documented 400 rows.
    """
    assert len(signals) > 0
    assert len(signals) == expected_test_row_count
    assert expected_test_row_count == EXPECTED_TEST_ROWS


def test_pred_proba_up_within_unit_interval(signals):
    """pred_proba_up is a probability of the "up" class in [0, 1] (Req 1.2)."""
    proba = signals["pred_proba_up"]
    assert proba.notna().all()
    assert (proba >= 0.0).all()
    assert (proba <= 1.0).all()


def test_labels_are_binary(signals):
    """pred_label and y_true are binary labels in {0, 1} (Req 1.2)."""
    assert set(signals["pred_label"].unique()).issubset({0, 1})
    assert set(signals["y_true"].unique()).issubset({0, 1})


def test_no_missing_period_return(signals):
    """Every signal carries a Period_Return; missing ones are dropped (Req 1.3)."""
    assert signals["period_return"].notna().all()
