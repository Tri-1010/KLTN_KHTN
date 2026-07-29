"""Unit tests for B5 — news-volume anomaly detection (``experiments.b5_anomaly``).

Covers:

- Threshold computed on TRAIN only: rows with ``quarter_id >= cutoff`` must NOT
  influence mean/std, so a huge test-period value cannot change the threshold
  (Req 12.3, 4.1).
- ``news_spike`` correctly flags train rows above ``mean + 2·std`` and applies
  the train-derived threshold to test rows too (Req 12.3, 4.1).
- Exact threshold value on a small numeric fixture (``mean + 2·std`` with
  population std ``ddof=0``).
- ``news_spike`` classifies as a keyword column via ``is_keyword_column``.
- Builder output keyed/mergeable on ``(ticker, quarter_id)``, one row per key,
  and v0 ``keyword_features.csv`` untouched (Req 2.1, 2.3).
- Edge guard: empty train and zero-variance train produce no spurious spikes.

The pure-function tests build tiny frames directly. The builder unit tests use
``tmp_path``/``monkeypatch`` with a synthetic ``news_by_quarter.csv``.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from experiments.b5_anomaly import (
    build_b5_features,
    compute_news_spike,
    compute_spike_threshold,
)
from experiments.feature_registry import is_keyword_column

# ---------------------------------------------------------------------------
# (c) Exact threshold value on a small hand-built numeric fixture.
# ---------------------------------------------------------------------------


def test_threshold_exact_value_ddof0():
    """threshold == mean + 2·std of TRAIN news_count with population std (ddof=0)."""
    df = pd.DataFrame(
        {
            "ticker": ["A", "A", "A", "A"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q3", "2024Q4"],
            "news_count": [1.0, 2.0, 3.0, 4.0],
        }
    )
    # All rows are train (< 2025Q1). mean = 2.5, population std = sqrt(1.25).
    expected = 2.5 + 2.0 * math.sqrt(1.25)
    got = compute_spike_threshold(df, cutoff="2025Q1")
    assert math.isclose(got, expected, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# (a) Threshold uses TRAIN only — leakage guard (Req 12.3, 4.1).
# ---------------------------------------------------------------------------


def test_threshold_ignores_test_period_rows():
    """A huge test-period value must NOT change the train-derived threshold."""
    train_only = pd.DataFrame(
        {
            "ticker": ["A", "A", "A"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q3"],
            "news_count": [1.0, 2.0, 3.0],
        }
    )
    baseline = compute_spike_threshold(train_only, cutoff="2025Q1")

    # Same train rows, but add a giant test-period (>= cutoff) row.
    with_test = pd.DataFrame(
        {
            "ticker": ["A", "A", "A", "A"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q3", "2025Q2"],
            "news_count": [1.0, 2.0, 3.0, 100000.0],
        }
    )
    leaked = compute_spike_threshold(with_test, cutoff="2025Q1")

    # If the test row leaked, the threshold would be enormous. It must not.
    assert math.isclose(leaked, baseline, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# (b) news_spike flags train rows above threshold and applies to test rows.
# ---------------------------------------------------------------------------


def test_news_spike_flags_train_and_test_with_train_threshold():
    """Train rows above threshold flag 1; test rows use the same train threshold."""
    # Train news_count: 1,1,1,1,10 → mean=2.8, std(ddof=0)=sqrt(12.96)=3.6.
    # threshold = 2.8 + 2*3.6 = 10.0. Only values strictly > 10 spike.
    df = pd.DataFrame(
        {
            "ticker": ["A", "A", "A", "A", "A", "A", "A"],
            "quarter_id": [
                "2024Q1",
                "2024Q2",
                "2024Q3",
                "2024Q4",
                "2024Q1",  # duplicate quarter for another synthetic point
                "2025Q1",  # test row, value below threshold
                "2025Q2",  # test row, value above threshold
            ],
            "news_count": [1.0, 1.0, 1.0, 1.0, 10.0, 5.0, 50.0],
        }
    )
    threshold = compute_spike_threshold(df, cutoff="2025Q1")
    assert math.isclose(threshold, 10.0, rel_tol=1e-12)

    out = compute_news_spike(df, cutoff="2025Q1")
    spikes = out["news_spike"].tolist()

    # Train: 1,1,1,1,10 → none strictly > 10.0 → all 0.
    assert spikes[:5] == [0, 0, 0, 0, 0]
    # Test rows use the train threshold (10.0): 5 → 0, 50 → 1.
    assert spikes[5] == 0
    assert spikes[6] == 1


def test_news_spike_train_row_above_threshold_flags():
    """A train row strictly above mean+2std flags as a spike.

    With many small values and one moderately larger one, the outlier stays
    above its own threshold: train = nine 1's + one 10.
    mean = 1.9, population std = 2.7 → threshold = 1.9 + 2·2.7 = 7.3, so the
    10.0 row spikes while all the 1.0 rows do not.
    """
    counts = [1.0] * 9 + [10.0]
    df = pd.DataFrame(
        {
            "ticker": ["A"] * 10,
            "quarter_id": [f"2024Q{i % 4 + 1}" for i in range(10)],
            "news_count": counts,
        }
    )
    threshold = compute_spike_threshold(df, cutoff="2025Q1")
    assert math.isclose(threshold, 7.3, rel_tol=1e-9)

    out = compute_news_spike(df, cutoff="2025Q1").reset_index(drop=True)
    expected = [1 if v > threshold else 0 for v in counts]
    assert out["news_spike"].tolist() == expected
    assert out["news_spike"].sum() == 1  # only the 10.0 outlier spikes


# ---------------------------------------------------------------------------
# (f) Edge guards: empty train and zero-variance train → no spurious spikes.
# ---------------------------------------------------------------------------


def test_empty_train_produces_no_spikes():
    """When no train rows exist, threshold is +inf → zero spikes everywhere."""
    df = pd.DataFrame(
        {
            "ticker": ["A", "A"],
            "quarter_id": ["2025Q1", "2025Q2"],  # both >= cutoff → no train
            "news_count": [10.0, 999.0],
        }
    )
    assert compute_spike_threshold(df, cutoff="2025Q1") == math.inf
    out = compute_news_spike(df, cutoff="2025Q1")
    assert out["news_spike"].tolist() == [0, 0]


def test_zero_variance_train_produces_no_spikes():
    """Zero-variance train (all equal, incl. single row) → +inf → no spikes."""
    df = pd.DataFrame(
        {
            "ticker": ["A", "A", "A"],
            "quarter_id": ["2024Q1", "2024Q2", "2025Q1"],
            "news_count": [5.0, 5.0, 5.0],
        }
    )
    # Train is [5, 5] → std == 0 → threshold +inf.
    assert compute_spike_threshold(df, cutoff="2025Q1") == math.inf
    out = compute_news_spike(df, cutoff="2025Q1")
    assert out["news_spike"].tolist() == [0, 0, 0]


def test_single_train_row_produces_no_spikes():
    """A single train row has zero variance → threshold +inf → no spikes."""
    df = pd.DataFrame(
        {
            "ticker": ["A", "A"],
            "quarter_id": ["2024Q1", "2025Q1"],
            "news_count": [3.0, 100.0],
        }
    )
    assert compute_spike_threshold(df, cutoff="2025Q1") == math.inf
    out = compute_news_spike(df, cutoff="2025Q1")
    assert out["news_spike"].tolist() == [0, 0]


# ---------------------------------------------------------------------------
# (d) Column classification via feature_registry.
# ---------------------------------------------------------------------------


def test_news_spike_classifies_as_keyword_column():
    """``news_spike`` classifies as a keyword column; meta keys do not."""
    assert is_keyword_column("news_spike")
    assert not is_keyword_column("ticker")
    assert not is_keyword_column("quarter_id")


# ---------------------------------------------------------------------------
# Output shape: one row per key, binary integer column.
# ---------------------------------------------------------------------------


def test_news_spike_is_binary_integer_and_one_row_per_key():
    """Output is keyed on (ticker, quarter_id), one row per key, values in {0,1}."""
    df = pd.DataFrame(
        {
            "ticker": ["A", "B", "A", "B"],
            "quarter_id": ["2024Q1", "2024Q1", "2024Q2", "2024Q2"],
            "news_count": [1.0, 2.0, 3.0, 40.0],
        }
    )
    out = compute_news_spike(df, cutoff="2025Q1")
    assert list(out.columns) == ["ticker", "quarter_id", "news_spike"]
    assert not out.duplicated(subset=["ticker", "quarter_id"]).any()
    assert set(out["news_spike"].unique()).issubset({0, 1})
    assert pd.api.types.is_integer_dtype(out["news_spike"])


# ---------------------------------------------------------------------------
# Builder unit tests (Req 12.3, 2.1, 2.3).
# ---------------------------------------------------------------------------


def _write_small_news(path):
    """Write a tiny synthetic news_by_quarter.csv spanning train + test quarters."""
    df = pd.DataFrame(
        {
            "ticker": ["ACB", "ACB", "ACB", "ACB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q3", "2025Q1"],
            "news_count": [1, 1, 1, 50],
            "combined_text": [
                "lợi nhuận tăng doanh thu tăng",
                "nợ xấu tăng thua lỗ",
                "đại hội cổ đông họp hđqt",
                "phục hồi tăng trưởng mạnh chia cổ tức",
            ],
        }
    )
    df.to_csv(path, index=False, encoding="utf-8")


def test_build_b5_produces_news_spike_and_keys(tmp_path, monkeypatch):
    """B5 output is keyed on (ticker, quarter_id) with a news_spike column."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)

    features = build_b5_features(news_path=str(news_path))

    assert not features.empty
    assert {"ticker", "quarter_id"}.issubset(features.columns)
    assert "news_spike" in features.columns
    assert is_keyword_column("news_spike")
    assert set(features["news_spike"].unique()).issubset({0, 1})

    # Output file written to the versioned path.
    assert (tmp_path / "data" / "features" / "keyword_features_B5.csv").exists()


def test_build_b5_is_mergeable_on_keys(tmp_path, monkeypatch):
    """B5 merges cleanly with a technical frame on the keys (Req 2.1)."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)

    b5 = build_b5_features(news_path=str(news_path))

    # One row per (ticker, quarter_id).
    assert not b5.duplicated(subset=["ticker", "quarter_id"]).any()

    tech = pd.DataFrame(
        {
            "ticker": ["ACB", "ACB", "ACB", "ACB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q3", "2025Q1"],
            "return_q": [0.1, -0.2, 0.05, 0.2],
        }
    )
    merged = tech.merge(b5, on=["ticker", "quarter_id"], how="inner")
    assert len(merged) == 4
    # Train is [1,1,1] → zero variance → threshold +inf → no spikes anywhere,
    # including the large test-period value (leakage guard).
    assert merged["news_spike"].tolist() == [0, 0, 0, 0]


def test_build_b5_does_not_modify_v0(tmp_path, monkeypatch):
    """The original v0 keyword_features.csv is left untouched (Req 2.3)."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)

    v0_path = tmp_path / "data" / "features" / "keyword_features.csv"
    sentinel = "ticker,quarter_id,kw_x\nACB,2024Q1,1\n"
    v0_path.write_text(sentinel, encoding="utf-8")

    build_b5_features(news_path=str(news_path))

    assert v0_path.read_text(encoding="utf-8") == sentinel
