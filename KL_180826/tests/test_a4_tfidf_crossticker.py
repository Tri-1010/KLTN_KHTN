"""Unit tests for A4 — cross-ticker TF-IDF (``experiments.a4_tfidf_crossticker``).

Covers:

- The cross-ticker TF-IDF math on a tiny hand-built fixture: a keyword common to
  every ticker gets ~0 IDF weight, while a keyword unique to one ticker gets a
  strictly higher weight (Req 9.1).
- The output frame is keyed on ``(ticker, quarter_id)`` and mergeable with a
  technical frame (Req 2.1).
- ``tfidfx_`` columns are produced and classify as keyword columns via
  ``experiments.feature_registry.is_keyword_column`` (Req 9.1, 3.x).
- The original v0 ``keyword_features.csv`` is left untouched (Req 2.3).

The builder unit tests use ``tmp_path``/``monkeypatch`` with a tiny synthetic
``news_by_quarter.csv`` and never touch the real v0 features.
"""

from __future__ import annotations

import math

import pandas as pd

from experiments.a4_tfidf_crossticker import (
    build_a4_features,
    compute_crossticker_idf,
    compute_crossticker_tfidf,
)
from experiments.feature_registry import is_keyword_column

# ---------------------------------------------------------------------------
# Cross-ticker TF-IDF math on a tiny hand-built fixture.
# ---------------------------------------------------------------------------


def _toy_frame():
    """Hand-built frame: 3 tickers, keyword ``common`` in all, ``rare`` in one.

    - ``kw_common`` appears in every ticker → ticker_df == n_tickers → idf 0.
    - ``kw_rare`` appears only in ticker AAA → ticker_df == 1 → idf ln(3).
    """
    return pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB", "CCC"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1", "2024Q1"],
            "kw_common": [2, 1, 3, 4],
            "kw_rare": [5, 0, 0, 0],
            "doc_length": [10, 10, 10, 10],
        }
    )


def test_crossticker_idf_common_zero_rare_high():
    """Keyword in every ticker → idf 0; keyword in one ticker → idf ln(n) (Req 9.1)."""
    df = _toy_frame()
    idf = compute_crossticker_idf(df, ["common", "rare"])

    # common appears in all 3 tickers → ln(3/3) == 0.
    assert idf["common"] == 0.0
    # rare appears in exactly 1 ticker → ln(3/1) == ln(3).
    assert math.isclose(idf["rare"], math.log(3), rel_tol=1e-9)
    # A discriminative keyword must weigh strictly more than a ubiquitous one.
    assert idf["rare"] > idf["common"]


def test_crossticker_tfidf_weights():
    """tfidfx_{k} = (kw / doc_length) * idf_x[k]; common ~0, rare high (Req 9.1)."""
    df = _toy_frame()
    out = compute_crossticker_tfidf(df, ["common", "rare"])

    # Common keyword contributes zero weight everywhere (idf == 0).
    assert (out["tfidfx_common"] == 0.0).all()

    # Rare keyword: AAA/2024Q1 has kw_rare=5, doc_length=10 → tf=0.5, idf=ln(3).
    row = out.set_index(["ticker", "quarter_id"]).loc[("AAA", "2024Q1")]
    assert math.isclose(row["tfidfx_rare"], 0.5 * math.log(3), rel_tol=1e-9)

    # Rows without the rare keyword get zero weight for it.
    assert out.set_index(["ticker", "quarter_id"]).loc[("BBB", "2024Q1")][
        "tfidfx_rare"
    ] == 0.0


def test_tfidfx_columns_classify_as_keyword_columns():
    """Every produced tfidfx_ column classifies as a keyword column (Req 9.1)."""
    df = _toy_frame()
    out = compute_crossticker_tfidf(df, ["common", "rare"])
    tfidfx_cols = [c for c in out.columns if c.startswith("tfidfx_")]
    assert tfidfx_cols  # at least one produced
    for col in tfidfx_cols:
        assert is_keyword_column(col), f"{col} should classify as keyword column"
    # Meta keys are NOT keyword columns.
    assert not is_keyword_column("ticker")
    assert not is_keyword_column("quarter_id")


# ---------------------------------------------------------------------------
# Builder unit tests (Req 9.1, 2.1, 2.3).
# ---------------------------------------------------------------------------


def _write_small_news(path):
    """Write a tiny synthetic news_by_quarter.csv over curated keywords."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
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
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    (tmp_path / "reports").mkdir(parents=True)
    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)
    return news_path


def test_build_a4_produces_tfidfx_and_keys(tmp_path, monkeypatch):
    """A4 output is keyed on (ticker, quarter_id) with tfidfx_ columns (Req 9.1)."""
    _setup_workspace(tmp_path, monkeypatch)

    features = build_a4_features()

    assert not features.empty
    assert {"ticker", "quarter_id"}.issubset(features.columns)

    tfidfx_cols = [c for c in features.columns if c.startswith("tfidfx_")]
    assert tfidfx_cols
    for col in tfidfx_cols:
        assert is_keyword_column(col)

    # Output file written to the versioned path.
    assert (tmp_path / "data" / "features" / "keyword_features_A4.csv").exists()


def test_build_a4_is_mergeable_on_keys(tmp_path, monkeypatch):
    """A4 merges cleanly with a technical frame on the keys (Req 2.1)."""
    _setup_workspace(tmp_path, monkeypatch)

    a4 = build_a4_features()

    # One row per (ticker, quarter_id) — keys are unique.
    assert not a4.duplicated(subset=["ticker", "quarter_id"]).any()

    tech = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "return_q": [0.1, -0.2, 0.05],
        }
    )
    merged = tech.merge(a4, on=["ticker", "quarter_id"], how="inner")
    assert len(merged) == 3


def test_build_a4_does_not_modify_v0(tmp_path, monkeypatch):
    """The original v0 keyword_features.csv is left untouched (Req 2.3)."""
    _setup_workspace(tmp_path, monkeypatch)

    v0_path = tmp_path / "data" / "features" / "keyword_features.csv"
    sentinel = "ticker,quarter_id,kw_x\nAAA,2024Q1,1\n"
    v0_path.write_text(sentinel, encoding="utf-8")

    build_a4_features()

    assert v0_path.read_text(encoding="utf-8") == sentinel
