"""
Unit tests for pipeline/experiment_metrics_breakdown.py

Tests cover:
- compute_per_class_metrics: correct keys, values in [0, 1] (Req 2.2, 8.1)
- delta rows present in output DataFrame (Req 2.3)
- unit and cutoff columns present and filled (Req 2.7)
"""

import os

import numpy as np
import pandas as pd
import pytest

from pipeline.experiment_metrics_breakdown import compute_per_class_metrics


# ---------------------------------------------------------------------------
# Expected output keys
# ---------------------------------------------------------------------------

EXPECTED_KEYS = {
    "precision_class0",
    "recall_class0",
    "f1_class0",
    "precision_class1",
    "recall_class1",
    "f1_class1",
    "balanced_accuracy",
    "auc_roc",
}


# ---------------------------------------------------------------------------
# 3.1 — test_compute_per_class_metrics_basic
# ---------------------------------------------------------------------------


class TestComputePerClassMetricsBasic:
    """Verify compute_per_class_metrics returns correct keys and valid values."""

    def _make_synthetic_data(self, seed: int = 42, n: int = 100):
        """Generate synthetic binary classification data."""
        rng = np.random.RandomState(seed)
        y_true = rng.randint(0, 2, size=n)
        # Imperfect predictions — mix some errors
        y_pred = rng.randint(0, 2, size=n)
        y_proba = rng.uniform(0, 1, size=n)
        return y_true, y_pred, y_proba

    def test_returns_dict_with_all_expected_keys(self):
        """Result dict must contain all 8 expected keys."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)

        assert isinstance(result, dict)
        missing = EXPECTED_KEYS - set(result.keys())
        assert not missing, f"Missing keys: {missing}"

    def test_no_unexpected_keys(self):
        """Result dict must not contain extra unexpected keys."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)

        extra = set(result.keys()) - EXPECTED_KEYS
        assert not extra, f"Unexpected extra keys: {extra}"

    def test_metric_values_in_unit_interval(self):
        """All metric values (except auc_roc when nan) must be in [0, 1]."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)

        for key, val in result.items():
            if np.isnan(val):
                continue  # nan is acceptable (e.g. auc_roc when single class)
            assert 0.0 <= val <= 1.0, (
                f"metric '{key}' = {val:.4f} is outside [0, 1]"
            )

    def test_precision_class0_in_unit_interval(self):
        """precision_class0 must be in [0, 1]."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)
        assert 0.0 <= result["precision_class0"] <= 1.0

    def test_recall_class1_in_unit_interval(self):
        """recall_class1 must be in [0, 1]."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)
        assert 0.0 <= result["recall_class1"] <= 1.0

    def test_balanced_accuracy_in_unit_interval(self):
        """balanced_accuracy must be in [0, 1]."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)
        assert 0.0 <= result["balanced_accuracy"] <= 1.0

    def test_auc_roc_in_unit_interval_when_proba_provided(self):
        """auc_roc must be in [0, 1] when y_proba is provided."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)
        if not np.isnan(result["auc_roc"]):
            assert 0.0 <= result["auc_roc"] <= 1.0

    def test_auc_roc_is_nan_when_proba_is_none(self):
        """auc_roc must be np.nan when y_proba=None."""
        y_true, y_pred, _ = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba=None)
        assert np.isnan(result["auc_roc"]), (
            f"Expected auc_roc=nan when y_proba=None, got {result['auc_roc']}"
        )

    def test_perfect_predictions_give_metrics_near_one(self):
        """Perfect predictions (y_pred == y_true) should give metrics close to 1.0."""
        rng = np.random.RandomState(7)
        y_true = rng.randint(0, 2, size=50)
        y_pred = y_true.copy()
        y_proba = y_true.astype(float)

        result = compute_per_class_metrics(y_true, y_pred, y_proba)

        assert result["balanced_accuracy"] == pytest.approx(1.0, abs=1e-6)
        assert result["recall_class0"] == pytest.approx(1.0, abs=1e-6)
        assert result["recall_class1"] == pytest.approx(1.0, abs=1e-6)

    def test_all_wrong_predictions_give_low_balanced_accuracy(self):
        """All-wrong predictions (flipped) give low balanced accuracy."""
        # Labels are alternating 0 and 1 so both classes are present
        y_true = np.array([0, 1] * 20)
        y_pred = 1 - y_true  # completely wrong
        y_proba = y_pred.astype(float)

        result = compute_per_class_metrics(y_true, y_pred, y_proba)

        # balanced_accuracy of ~0.0 for completely inverted predictions
        assert result["balanced_accuracy"] < 0.1

    def test_with_two_samples_minimum(self):
        """Function must work with just 2 samples (boundary case)."""
        y_true = np.array([0, 1])
        y_pred = np.array([0, 1])
        y_proba = np.array([0.2, 0.8])

        result = compute_per_class_metrics(y_true, y_pred, y_proba)
        assert set(result.keys()) == EXPECTED_KEYS

    def test_zero_division_handled_gracefully(self):
        """When a class is never predicted, zero_division=0 returns 0.0, not error."""
        # Model always predicts class 0 (never class 1)
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_pred = np.zeros(6, dtype=int)  # always predicts class 0

        result = compute_per_class_metrics(y_true, y_pred, y_proba=None)

        # precision_class1 = 0 (never predicted class 1, no TP or FP)
        assert result["precision_class1"] == pytest.approx(0.0, abs=1e-6)
        # recall_class1 = 0 (class 1 never predicted)
        assert result["recall_class1"] == pytest.approx(0.0, abs=1e-6)

    def test_all_values_are_float(self):
        """All values in the returned dict must be Python floats (or nan)."""
        y_true, y_pred, y_proba = self._make_synthetic_data()
        result = compute_per_class_metrics(y_true, y_pred, y_proba)

        for key, val in result.items():
            assert isinstance(val, float), (
                f"Value for key '{key}' is {type(val)}, expected float"
            )


# ---------------------------------------------------------------------------
# 3.2 — test_delta_rows_present (integration, uses run_metrics_breakdown)
# ---------------------------------------------------------------------------


class TestDeltaRowsPresent:
    """Verify that output DataFrame contains delta_C_minus_A rows."""

    def test_delta_rows_present_in_output(self, tmp_path, monkeypatch):
        """Output DataFrame must have rows with config='delta_C_minus_A'."""
        import copy

        import numpy as np
        import pandas as pd

        # Build minimal synthetic merged DataFrame
        n = 40
        rng = np.random.RandomState(0)
        # Make a quarter column that will produce a valid train/test split
        quarters = (
            ["2023Q1"] * 10 + ["2023Q2"] * 10
            + ["2024Q1"] * 10 + ["2025Q1"] * 10
        )
        df = pd.DataFrame({
            "ticker": ["AAA"] * n,
            "quarter_id": quarters,
            "label_basic": rng.randint(0, 2, size=n).astype(float),
            "rsi": rng.uniform(20, 80, size=n),
            "macd": rng.uniform(-1, 1, size=n),
            "kw_tang_truong": rng.randint(0, 3, size=n),
            "kw_norm_tang_truong": rng.uniform(0, 1, size=n),
            "has_min_news": rng.randint(0, 2, size=n),
            "news_count": rng.randint(1, 10, size=n),
        })

        # Monkeypatch load_and_merge_data so we don't hit disk
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: df)
        # Monkeypatch output path to tmp_path
        monkeypatch.setattr(
            emb, "OUTPUT_PATH",
            str(tmp_path / "metrics_breakdown.csv")
        )
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        result_df = emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")

        delta_rows = result_df[result_df["config"] == "delta_C_minus_A"]
        assert len(delta_rows) > 0, (
            "Expected rows with config='delta_C_minus_A' in output DataFrame"
        )

    def test_delta_rows_count_equals_model_count(self, tmp_path, monkeypatch):
        """Number of delta rows must equal number of ML models."""
        import numpy as np
        import pandas as pd

        n = 40
        rng = np.random.RandomState(1)
        quarters = (
            ["2023Q1"] * 10 + ["2023Q2"] * 10
            + ["2024Q1"] * 10 + ["2025Q1"] * 10
        )
        df = pd.DataFrame({
            "ticker": ["BBB"] * n,
            "quarter_id": quarters,
            "label_basic": rng.randint(0, 2, size=n).astype(float),
            "rsi": rng.uniform(20, 80, size=n),
            "macd": rng.uniform(-1, 1, size=n),
            "kw_tang_truong": rng.randint(0, 3, size=n),
            "kw_norm_tang_truong": rng.uniform(0, 1, size=n),
            "has_min_news": rng.randint(0, 2, size=n),
            "news_count": rng.randint(1, 10, size=n),
        })

        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: df)
        monkeypatch.setattr(
            emb, "OUTPUT_PATH",
            str(tmp_path / "metrics_breakdown.csv")
        )
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        result_df = emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")

        n_models = result_df["model"].nunique()
        n_delta = len(result_df[result_df["config"] == "delta_C_minus_A"])
        assert n_delta == n_models, (
            f"Expected {n_models} delta rows (one per model), got {n_delta}"
        )


# ---------------------------------------------------------------------------
# 3.3 — test_records_unit_cutoff (integration)
# ---------------------------------------------------------------------------


class TestRecordsUnitCutoff:
    """Verify unit and cutoff columns are present and filled in all rows."""

    def _make_df(self, seed: int = 0) -> "pd.DataFrame":
        import numpy as np
        import pandas as pd

        n = 40
        rng = np.random.RandomState(seed)
        quarters = (
            ["2023Q1"] * 10 + ["2023Q2"] * 10
            + ["2024Q1"] * 10 + ["2025Q1"] * 10
        )
        return pd.DataFrame({
            "ticker": ["CCC"] * n,
            "quarter_id": quarters,
            "label_basic": rng.randint(0, 2, size=n).astype(float),
            "rsi": rng.uniform(20, 80, size=n),
            "macd": rng.uniform(-1, 1, size=n),
            "kw_tang_truong": rng.randint(0, 3, size=n),
            "kw_norm_tang_truong": rng.uniform(0, 1, size=n),
            "has_min_news": rng.randint(0, 2, size=n),
            "news_count": rng.randint(1, 10, size=n),
        })

    def test_unit_column_present(self, tmp_path, monkeypatch):
        """Output DataFrame must have a 'unit' column."""
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: self._make_df())
        monkeypatch.setattr(
            emb, "OUTPUT_PATH",
            str(tmp_path / "metrics_breakdown.csv")
        )
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        result_df = emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")
        assert "unit" in result_df.columns

    def test_cutoff_column_present(self, tmp_path, monkeypatch):
        """Output DataFrame must have a 'cutoff' column."""
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: self._make_df())
        monkeypatch.setattr(
            emb, "OUTPUT_PATH",
            str(tmp_path / "metrics_breakdown.csv")
        )
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        result_df = emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")
        assert "cutoff" in result_df.columns

    def test_unit_column_filled_correctly(self, tmp_path, monkeypatch):
        """All rows in the 'unit' column must equal the provided unit value."""
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: self._make_df())
        monkeypatch.setattr(
            emb, "OUTPUT_PATH",
            str(tmp_path / "metrics_breakdown.csv")
        )
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        result_df = emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")
        assert (result_df["unit"] == "quarter").all(), (
            "Expected all rows to have unit='quarter'"
        )

    def test_cutoff_column_filled_correctly(self, tmp_path, monkeypatch):
        """All rows in the 'cutoff' column must equal the provided cutoff value."""
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: self._make_df())
        monkeypatch.setattr(
            emb, "OUTPUT_PATH",
            str(tmp_path / "metrics_breakdown.csv")
        )
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        result_df = emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")
        assert (result_df["cutoff"] == "2025Q1").all(), (
            "Expected all rows to have cutoff='2025Q1'"
        )

    def test_no_null_values_in_unit_cutoff(self, tmp_path, monkeypatch):
        """The unit and cutoff columns must not contain any null values."""
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: self._make_df())
        monkeypatch.setattr(
            emb, "OUTPUT_PATH",
            str(tmp_path / "metrics_breakdown.csv")
        )
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        result_df = emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")
        assert result_df["unit"].notna().all(), "Found null values in 'unit' column"
        assert result_df["cutoff"].notna().all(), "Found null values in 'cutoff' column"

    def test_csv_file_created(self, tmp_path, monkeypatch):
        """The output CSV file must be created at the expected path."""
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: self._make_df())
        output_path = str(tmp_path / "metrics_breakdown.csv")
        monkeypatch.setattr(emb, "OUTPUT_PATH", output_path)
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        emb.run_metrics_breakdown(cutoff="2025Q1", unit="quarter")
        assert os.path.exists(output_path), (
            f"Expected CSV file at {output_path} but it was not created"
        )

    def test_custom_unit_value_written_to_csv(self, tmp_path, monkeypatch):
        """Custom unit value must be written to the CSV correctly."""
        import pipeline.experiment_metrics_breakdown as emb
        monkeypatch.setattr(emb, "load_and_merge_data", lambda: self._make_df())
        output_path = str(tmp_path / "metrics_breakdown.csv")
        monkeypatch.setattr(emb, "OUTPUT_PATH", output_path)
        monkeypatch.setattr(emb, "REPORTS_DIR", str(tmp_path))

        emb.run_metrics_breakdown(cutoff="2024Q1", unit="month")

        saved_df = pd.read_csv(output_path)
        assert (saved_df["unit"] == "month").all()
        assert (saved_df["cutoff"] == "2024Q1").all()
