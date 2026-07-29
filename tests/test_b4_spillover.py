"""Unit tests for B4 — cross-sector news spillover (``experiments.b4_spillover``).

Covers:

- Leave-one-out correctness within a sector, same quarter: each ticker's
  ``sector_pos_score`` equals the OTHER ticker's ``pos_score`` and
  ``sector_news_count`` equals the other's ``news_count`` (excludes itself)
  (Req 12.1).
- Same-quarter isolation: news in a different quarter does not affect a
  ticker's sector features for quarter q (Req 12.2).
- Singleton sector-quarter → ``sector_news_count == 0`` and ``sector_pos_score``
  is NaN (design error-handling: keep NaN, not imputed).
- ``sector_`` columns classify as keyword columns via ``is_keyword_column``.
- Builder output is keyed/mergeable on ``(ticker, quarter_id)`` and leaves the
  v0 ``keyword_features.csv`` untouched (Req 2.1, 2.3).

The pure-function tests inject a tiny sector mapping so they never depend on
``config/pipeline_config.yaml``. The builder unit tests use ``tmp_path``/
``monkeypatch`` with a synthetic ``news_by_quarter.csv``.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from experiments.b4_spillover import (
    build_b4_features,
    compute_spillover_features,
)
from experiments.feature_registry import is_keyword_column

# ---------------------------------------------------------------------------
# Leave-one-out correctness on a tiny injected mapping (Req 12.1).
# ---------------------------------------------------------------------------


def test_leave_one_out_two_tickers_same_sector_quarter():
    """Each ticker's sector features equal the OTHER ticker's values (Req 12.1)."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q1"],
            "news_count": [3.0, 7.0],
            "pos_score": [0.2, 0.8],
        }
    )
    sector_of = {"AAA": "Banking", "BBB": "Banking"}

    out = compute_spillover_features(df, sector_of).set_index("ticker")

    # AAA sees only BBB's news/sentiment (its own is excluded).
    assert out.loc["AAA", "sector_news_count"] == 7.0
    assert math.isclose(out.loc["AAA", "sector_pos_score"], 0.8, rel_tol=1e-9)

    # BBB sees only AAA's news/sentiment.
    assert out.loc["BBB", "sector_news_count"] == 3.0
    assert math.isclose(out.loc["BBB", "sector_pos_score"], 0.2, rel_tol=1e-9)


def test_leave_one_out_three_tickers_averages_others():
    """With 3 tickers, a ticker's pos_score is the mean of the OTHER two (Req 12.1)."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB", "CCC"],
            "quarter_id": ["2024Q1", "2024Q1", "2024Q1"],
            "news_count": [1.0, 2.0, 5.0],
            "pos_score": [0.0, 0.4, 1.0],
        }
    )
    sector_of = {"AAA": "Energy", "BBB": "Energy", "CCC": "Energy"}

    out = compute_spillover_features(df, sector_of).set_index("ticker")

    # AAA: news = 2 + 5 = 7; pos = mean(0.4, 1.0) = 0.7.
    assert out.loc["AAA", "sector_news_count"] == 7.0
    assert math.isclose(out.loc["AAA", "sector_pos_score"], 0.7, rel_tol=1e-9)
    # CCC: news = 1 + 2 = 3; pos = mean(0.0, 0.4) = 0.2.
    assert out.loc["CCC", "sector_news_count"] == 3.0
    assert math.isclose(out.loc["CCC", "sector_pos_score"], 0.2, rel_tol=1e-9)


def test_different_sectors_do_not_mix():
    """Tickers in different sectors don't contribute to each other (Req 12.1)."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB", "XXX"],
            "quarter_id": ["2024Q1", "2024Q1", "2024Q1"],
            "news_count": [3.0, 7.0, 100.0],
            "pos_score": [0.2, 0.8, 0.9],
        }
    )
    # XXX is in a different sector, so it must not leak into Banking.
    sector_of = {"AAA": "Banking", "BBB": "Banking", "XXX": "Energy"}

    out = compute_spillover_features(df, sector_of).set_index("ticker")

    assert out.loc["AAA", "sector_news_count"] == 7.0  # only BBB, not XXX
    assert math.isclose(out.loc["AAA", "sector_pos_score"], 0.8, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Same-quarter isolation (Req 12.2).
# ---------------------------------------------------------------------------


def test_same_quarter_isolation():
    """News in another quarter does not affect a ticker's features for q (Req 12.2)."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB", "BBB"],
            "quarter_id": ["2024Q1", "2024Q1", "2024Q2"],
            "news_count": [3.0, 7.0, 999.0],
            "pos_score": [0.2, 0.8, 0.5],
        }
    )
    sector_of = {"AAA": "Banking", "BBB": "Banking"}

    out = compute_spillover_features(df, sector_of).set_index(
        ["ticker", "quarter_id"]
    )

    # AAA in 2024Q1 only sees BBB's 2024Q1 news (7.0), never BBB's 2024Q2 (999).
    assert out.loc[("AAA", "2024Q1"), "sector_news_count"] == 7.0
    assert math.isclose(
        out.loc[("AAA", "2024Q1"), "sector_pos_score"], 0.8, rel_tol=1e-9
    )
    # BBB's 2024Q2 row is a singleton in that quarter → NaN / 0.
    assert out.loc[("BBB", "2024Q2"), "sector_news_count"] == 0.0
    assert np.isnan(out.loc[("BBB", "2024Q2"), "sector_pos_score"])


# ---------------------------------------------------------------------------
# Singleton sector-quarter (design error-handling: keep NaN).
# ---------------------------------------------------------------------------


def test_singleton_sector_quarter_is_zero_and_nan():
    """A lone ticker in its sector-quarter → count 0, pos_score NaN."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "quarter_id": ["2024Q1"],
            "news_count": [5.0],
            "pos_score": [0.3],
        }
    )
    sector_of = {"AAA": "Technology"}

    out = compute_spillover_features(df, sector_of).set_index("ticker")

    assert out.loc["AAA", "sector_news_count"] == 0.0
    assert np.isnan(out.loc["AAA", "sector_pos_score"])


def test_unmapped_ticker_treated_as_singleton():
    """A ticker without a sector mapping never leaks into any sector."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q1"],
            "news_count": [3.0, 7.0],
            "pos_score": [0.2, 0.8],
        }
    )
    # BBB has no mapping → its own isolated group.
    sector_of = {"AAA": "Banking"}

    out = compute_spillover_features(df, sector_of).set_index("ticker")

    # AAA is alone in Banking → singleton.
    assert out.loc["AAA", "sector_news_count"] == 0.0
    assert np.isnan(out.loc["AAA", "sector_pos_score"])
    # BBB unmapped → singleton too.
    assert out.loc["BBB", "sector_news_count"] == 0.0
    assert np.isnan(out.loc["BBB", "sector_pos_score"])


# ---------------------------------------------------------------------------
# Column classification (Req 3.x via feature_registry).
# ---------------------------------------------------------------------------


def test_sector_columns_classify_as_keyword_columns():
    """``sector_pos_score``/``sector_news_count`` classify as keyword columns."""
    assert is_keyword_column("sector_pos_score")
    assert is_keyword_column("sector_news_count")
    # Meta keys are NOT keyword columns.
    assert not is_keyword_column("ticker")
    assert not is_keyword_column("quarter_id")


# ---------------------------------------------------------------------------
# Builder unit tests (Req 12.1, 12.2, 2.1, 2.3).
# ---------------------------------------------------------------------------


def _write_small_news(path):
    """Write a tiny synthetic news_by_quarter.csv using real HOSE-80 tickers.

    ACB and BID are both Banking; FPT is Technology (a singleton here). Using
    real tickers means the builder's ``assign_segments()`` mapping covers them.
    """
    df = pd.DataFrame(
        {
            "ticker": ["ACB", "BID", "FPT"],
            "quarter_id": ["2024Q1", "2024Q1", "2024Q1"],
            "news_count": [3, 2, 1],
            "combined_text": [
                "lợi nhuận tăng doanh thu tăng tăng trưởng mạnh chia cổ tức",
                "nợ xấu tăng thua lỗ áp lực tài chính",
                "đại hội cổ đông họp hđqt phục hồi",
            ],
        }
    )
    df.to_csv(path, index=False, encoding="utf-8")


def _setup_workspace(tmp_path, monkeypatch):
    # Copy the real pipeline config so assign_segments() can resolve the
    # ticker universe from within the temporary working directory.
    real_config = Path("config/pipeline_config.yaml").resolve()
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config").mkdir(parents=True)
    shutil.copy(real_config, tmp_path / "config" / "pipeline_config.yaml")
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)
    return news_path


def test_build_b4_produces_sector_cols_and_keys(tmp_path, monkeypatch):
    """B4 output is keyed on (ticker, quarter_id) with sector_ columns (Req 12)."""
    _setup_workspace(tmp_path, monkeypatch)

    features = build_b4_features()

    assert not features.empty
    assert {"ticker", "quarter_id"}.issubset(features.columns)
    assert "sector_pos_score" in features.columns
    assert "sector_news_count" in features.columns
    assert is_keyword_column("sector_pos_score")
    assert is_keyword_column("sector_news_count")

    # Output file written to the versioned path.
    assert (tmp_path / "data" / "features" / "keyword_features_B4.csv").exists()


def test_build_b4_is_mergeable_on_keys(tmp_path, monkeypatch):
    """B4 merges cleanly with a technical frame on the keys (Req 2.1)."""
    _setup_workspace(tmp_path, monkeypatch)

    b4 = build_b4_features()

    # One row per (ticker, quarter_id) — keys are unique.
    assert not b4.duplicated(subset=["ticker", "quarter_id"]).any()

    tech = pd.DataFrame(
        {
            "ticker": ["ACB", "BID", "FPT"],
            "quarter_id": ["2024Q1", "2024Q1", "2024Q1"],
            "return_q": [0.1, -0.2, 0.05],
        }
    )
    merged = tech.merge(b4, on=["ticker", "quarter_id"], how="inner")
    assert len(merged) == 3

    # ACB and BID share the Banking sector → non-null spillover; FPT singleton NaN.
    merged = merged.set_index("ticker")
    assert not np.isnan(merged.loc["ACB", "sector_pos_score"])
    assert merged.loc["ACB", "sector_news_count"] == 2.0  # only BID's news
    assert np.isnan(merged.loc["FPT", "sector_pos_score"])
    assert merged.loc["FPT", "sector_news_count"] == 0.0


def test_build_b4_does_not_modify_v0(tmp_path, monkeypatch):
    """The original v0 keyword_features.csv is left untouched (Req 2.3)."""
    _setup_workspace(tmp_path, monkeypatch)

    v0_path = tmp_path / "data" / "features" / "keyword_features.csv"
    sentinel = "ticker,quarter_id,kw_x\nACB,2024Q1,1\n"
    v0_path.write_text(sentinel, encoding="utf-8")

    build_b4_features()

    assert v0_path.read_text(encoding="utf-8") == sentinel
