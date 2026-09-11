"""Unit tests for the Leakage_Auditor (`backtest/leakage_audit.py`) — Req 8.2, 8.3.

Covers :func:`backtest.leakage_audit.audit_leakage` and the helper
:func:`backtest.leakage_audit.classify_feature_window` on tiny deterministic
synthetic CSVs:

- CLEAN features (in-period/past names, only weakly correlated with the label) →
  audit PASSES: no ``"future"`` window, label not in features, no high-corr flag.
- LEAKAGE via a feature column literally named as a future-label column
  (e.g. ``return`` / ``label_basic``) → ``label_not_in_features is False`` and
  ``passed is False`` (Req 8.2).
- LEAKAGE via a benignly-named feature whose values equal ``label_basic``
  (perfect correlation) → shows up in ``high_corr_flags`` and ``passed is False``
  (Req 8.3).
- LEAKAGE via a future-named feature (``next_return``) → classified ``"future"``
  and ``passed is False`` (Req 8.1).
- Direct :func:`classify_feature_window` unit checks.

CSVs are written under pytest's ``tmp_path`` and ``output_path`` is directed
there too, so tests never read the real feature/label files nor touch the real
``reports/`` directory.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.leakage_audit import (
    FUTURE_LABEL_COLUMNS,
    LABEL_COLUMN,
    AuditResult,
    audit_leakage,
    classify_feature_window,
)

N_ROWS = 20
SEED = 12345


def _make_keys(n_rows: int = N_ROWS):
    """Return ``n_rows`` deterministic ``(ticker, quarter_id)`` key rows."""
    tickers = [f"TCK{i:02d}" for i in range(n_rows)]
    quarter_ids = ["2024Q1"] * n_rows
    return tickers, quarter_ids


def _make_labels_df(n_rows: int = N_ROWS, seed: int = SEED) -> pd.DataFrame:
    """Labels CSV frame with the ``master_with_labels.csv`` schema.

    ``label_basic`` alternates 0/1 so both classes are present.
    """
    rng = np.random.default_rng(seed)
    tickers, quarter_ids = _make_keys(n_rows)
    label_basic = np.array([i % 2 for i in range(n_rows)], dtype=int)
    return pd.DataFrame(
        {
            "ticker": tickers,
            "quarter_id": quarter_ids,
            "return": rng.normal(size=n_rows),
            "next_quarter_id": ["2024Q2"] * n_rows,
            "next_avg_close": rng.normal(loc=100.0, size=n_rows),
            "label_basic": label_basic,
            "label_threshold": rng.normal(size=n_rows),
        }
    )


def _make_clean_tech_df(
    labels: pd.DataFrame, seed: int = SEED
) -> pd.DataFrame:
    """Tech-features frame with clean in-period/past names, weakly correlated.

    Values are pure Gaussian noise (fixed seed) so they don't trip the 0.95
    correlation threshold against ``label_basic``.
    """
    rng = np.random.default_rng(seed + 1)
    n = len(labels)
    return pd.DataFrame(
        {
            "ticker": labels["ticker"].to_numpy(),
            "quarter_id": labels["quarter_id"].to_numpy(),
            "return_q": rng.normal(size=n),
            "volatility_q": rng.normal(size=n),
            "return_prev_q": rng.normal(size=n),
        }
    )


def _run_audit(tmp_path, tech_df: pd.DataFrame, labels_df: pd.DataFrame) -> AuditResult:
    """Write both CSVs into *tmp_path* and run the auditor there."""
    tech_path = tmp_path / "tech_features.csv"
    labels_path = tmp_path / "master_with_labels.csv"
    output_path = tmp_path / "reports" / "leakage_audit.md"
    tech_df.to_csv(tech_path, index=False)
    labels_df.to_csv(labels_path, index=False)

    return audit_leakage(
        tech_path=str(tech_path),
        labels_path=str(labels_path),
        cutoff="2025Q1",
        corr_threshold=0.95,
        output_path=str(output_path),
    ), output_path


def test_clean_features_pass(tmp_path):
    """Clean, weakly-correlated features → audit PASSES (Req 8.1-8.3)."""
    labels = _make_labels_df()
    tech = _make_clean_tech_df(labels)

    result, output_path = _run_audit(tmp_path, tech, labels)

    assert result.passed is True
    assert result.label_not_in_features is True
    assert result.high_corr_flags == []
    # No feature classified as "future".
    assert "future" not in result.feature_windows.values()
    # Windows are classified for exactly the feature columns (not the keys).
    assert set(result.feature_windows) == {"return_q", "volatility_q", "return_prev_q"}
    assert result.feature_windows["return_q"] == "in-period"
    assert result.feature_windows["return_prev_q"] == "past"
    # The markdown report was written.
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").strip() != ""


def test_label_column_in_features_flags_leakage(tmp_path):
    """A feature literally named as a future-label column → leakage (Req 8.2)."""
    labels = _make_labels_df()
    tech = _make_clean_tech_df(labels)
    # Inject a column named exactly like a forbidden future-label column.
    tech["return"] = labels["return"].to_numpy()
    assert "return" in FUTURE_LABEL_COLUMNS  # sanity: this name is forbidden

    result, _ = _run_audit(tmp_path, tech, labels)

    assert result.label_not_in_features is False
    assert result.passed is False


def test_feature_named_like_label_column_no_crash(tmp_path):
    """A feature literally named ``label_basic`` (collides with the label column
    on merge) must NOT crash the auditor and is reported as leakage (Req 8.2).

    Regression: previously ``tech.merge(label_frame, ...)`` produced
    ``label_basic_x``/``label_basic_y`` suffixes, so ``merged[LABEL_COLUMN]``
    raised ``KeyError`` before check (b) could report the leakage.
    """
    labels = _make_labels_df()
    tech = _make_clean_tech_df(labels)
    # Inject a feature column named exactly like the label column.
    tech[LABEL_COLUMN] = labels[LABEL_COLUMN].to_numpy()
    assert LABEL_COLUMN in FUTURE_LABEL_COLUMNS  # sanity: this name is forbidden

    # Must run without raising (KeyError regression).
    result, output_path = _run_audit(tmp_path, tech, labels)

    # Check (b) detects the label column in the feature set → leakage.
    assert result.label_not_in_features is False
    assert result.passed is False
    # Correlation for the colliding feature is still computed (equals the label
    # → |corr| ~ 1.0), so it is also flagged by check (c).
    flagged = {feat for feat, _ in result.high_corr_flags}
    assert LABEL_COLUMN in flagged
    # Report still written and the internal rename does not leak into the text.
    assert output_path.exists()
    assert "__label__" not in output_path.read_text(encoding="utf-8")


def test_high_correlation_feature_flagged(tmp_path):
    """A benignly-named feature equal to the label → high-corr flag (Req 8.3)."""
    labels = _make_labels_df()
    tech = _make_clean_tech_df(labels)
    # Perfect correlation with label_basic, but an innocent-looking name so the
    # (b) name/label checks do NOT catch it — only the (c) correlation check.
    tech["sneaky_feature"] = labels[LABEL_COLUMN].to_numpy()

    result, _ = _run_audit(tmp_path, tech, labels)

    flagged = {feat for feat, _ in result.high_corr_flags}
    assert "sneaky_feature" in flagged
    corr = dict(result.high_corr_flags)["sneaky_feature"]
    assert corr > 0.95
    assert corr == pytest.approx(1.0, abs=1e-9)
    # This feature name is benign, so it must not be treated as a label column.
    assert result.label_not_in_features is True
    assert result.passed is False


def test_future_named_feature_classified_future(tmp_path):
    """A feature named with a future pattern → classified 'future' (Req 8.1)."""
    labels = _make_labels_df()
    tech = _make_clean_tech_df(labels)
    tech["next_return"] = np.random.default_rng(SEED + 2).normal(size=len(labels))

    result, _ = _run_audit(tmp_path, tech, labels)

    assert result.feature_windows["next_return"] == "future"
    assert result.passed is False


def test_classify_feature_window_direct():
    """Direct unit checks for the window classifier (Req 8.1)."""
    assert classify_feature_window("return_q") == "in-period"
    assert classify_feature_window("return_prev_q") == "past"
    assert classify_feature_window("return_2q_ago") == "past"
    assert classify_feature_window("next_return") == "future"
