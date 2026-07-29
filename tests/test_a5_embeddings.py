"""Unit tests for A5 — PhoBERT embeddings (``experiments.a5_embeddings``).

These tests NEVER load the real PhoBERT/transformers model. Instead they inject
a lightweight *fake encoder* — a deterministic callable that maps each text to a
small fixed-dimension vector derived from text length — so the tests run fast
and without heavy optional dependencies.

Covers:

- ``compute_embedding_features`` yields exactly ``d`` ``emb_`` columns keyed on
  ``(ticker, quarter_id)`` (Req 9.2).
- The output is mergeable with a technical frame and has one row per key
  (Req 2.1).
- ``emb_`` columns classify as keyword columns via
  ``experiments.feature_registry.is_keyword_column`` (Req 3.x).
- ``import experiments.a5_embeddings`` succeeds even without ``transformers``
  installed (module-level import must not require torch) (Req 9.2).
- The original v0 ``keyword_features.csv`` is left untouched (Req 2.3).
"""

from __future__ import annotations

import importlib
import sys

import numpy as np
import pandas as pd

from experiments.a5_embeddings import (
    build_a5_features,
    compute_embedding_features,
)
from experiments.feature_registry import is_keyword_column

# ---------------------------------------------------------------------------
# Fake encoder — deterministic, tiny dimension, NO real PhoBERT.
# ---------------------------------------------------------------------------

FAKE_DIM = 4


def _fake_encoder(texts):
    """Deterministic encoder: each text → FAKE_DIM vector from its length.

    Returns a numpy array of shape (n_texts, FAKE_DIM). No model loading.
    """
    rows = []
    for t in texts:
        n = float(len(str(t)))
        rows.append([n, n / 2.0, n % 3, float(len(str(t).split()))])
    return np.asarray(rows, dtype=float)


def _toy_frame():
    return pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "combined_text": [
                "lợi nhuận tăng mạnh",
                "nợ xấu tăng thua lỗ",
                "đại hội cổ đông",
            ],
        }
    )


# ---------------------------------------------------------------------------
# compute_embedding_features (Req 9.2).
# ---------------------------------------------------------------------------


def test_compute_embedding_yields_d_emb_columns_keyed_on_keys():
    """Exactly d emb_ columns produced, keyed on (ticker, quarter_id) (Req 9.2)."""
    df = _toy_frame()
    out = compute_embedding_features(df, _fake_encoder)

    assert {"ticker", "quarter_id"}.issubset(out.columns)

    emb_cols = [c for c in out.columns if c.startswith("emb_")]
    assert len(emb_cols) == FAKE_DIM
    # Columns are named emb_0 .. emb_{d-1}.
    assert emb_cols == [f"emb_{i}" for i in range(FAKE_DIM)]

    # One row per input (ticker, quarter_id) key.
    assert len(out) == len(df)
    assert not out.duplicated(subset=["ticker", "quarter_id"]).any()

    # Values match the fake encoder deterministically for the first row.
    expected = _fake_encoder(df["combined_text"].tolist())
    np.testing.assert_allclose(
        out[[f"emb_{i}" for i in range(FAKE_DIM)]].to_numpy(), expected
    )


def test_emb_columns_classify_as_keyword_columns():
    """Every produced emb_ column classifies as a keyword column (Req 3.x)."""
    df = _toy_frame()
    out = compute_embedding_features(df, _fake_encoder)
    emb_cols = [c for c in out.columns if c.startswith("emb_")]
    assert emb_cols
    for col in emb_cols:
        assert is_keyword_column(col), f"{col} should classify as keyword column"
    # Meta keys are NOT keyword columns.
    assert not is_keyword_column("ticker")
    assert not is_keyword_column("quarter_id")


def test_module_import_does_not_require_transformers():
    """Importing the module must succeed even if transformers is absent (Req 9.2)."""
    # Simulate transformers/torch being unavailable during a fresh import.
    saved = {
        name: mod
        for name, mod in sys.modules.items()
        if name == "transformers" or name == "torch" or name.startswith(
            ("transformers.", "torch.")
        )
    }
    for name in list(saved):
        sys.modules[name] = None  # force ImportError if imported

    # Block re-import via a meta_path finder is overkill; setting to None makes
    # `import transformers` raise ImportError. Now reload our module.
    try:
        sys.modules.pop("experiments.a5_embeddings", None)
        mod = importlib.import_module("experiments.a5_embeddings")
        assert hasattr(mod, "build_a5_features")
        assert hasattr(mod, "PhoBERTEncoder")
        assert hasattr(mod, "compute_embedding_features")
    finally:
        # Restore original module state.
        for name in list(saved):
            if saved[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = saved[name]
        sys.modules.pop("experiments.a5_embeddings", None)
        importlib.import_module("experiments.a5_embeddings")


# ---------------------------------------------------------------------------
# Builder unit tests (Req 9.2, 2.1, 2.3).
# ---------------------------------------------------------------------------


def _write_small_news(path):
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


def test_build_a5_produces_emb_and_keys(tmp_path, monkeypatch):
    """A5 output is keyed on (ticker, quarter_id) with emb_ columns (Req 9.2)."""
    _setup_workspace(tmp_path, monkeypatch)

    features = build_a5_features(encoder=_fake_encoder)

    assert not features.empty
    assert {"ticker", "quarter_id"}.issubset(features.columns)

    emb_cols = [c for c in features.columns if c.startswith("emb_")]
    assert len(emb_cols) == FAKE_DIM
    for col in emb_cols:
        assert is_keyword_column(col)

    assert (tmp_path / "data" / "features" / "keyword_features_A5.csv").exists()


def test_build_a5_is_mergeable_on_keys(tmp_path, monkeypatch):
    """A5 merges cleanly with a technical frame; one row per key (Req 2.1)."""
    _setup_workspace(tmp_path, monkeypatch)

    a5 = build_a5_features(encoder=_fake_encoder)

    assert not a5.duplicated(subset=["ticker", "quarter_id"]).any()

    tech = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "return_q": [0.1, -0.2, 0.05],
        }
    )
    merged = tech.merge(a5, on=["ticker", "quarter_id"], how="inner")
    assert len(merged) == 3


def test_build_a5_does_not_modify_v0(tmp_path, monkeypatch):
    """The original v0 keyword_features.csv is left untouched (Req 2.3)."""
    _setup_workspace(tmp_path, monkeypatch)

    v0_path = tmp_path / "data" / "features" / "keyword_features.csv"
    sentinel = "ticker,quarter_id,kw_x\nAAA,2024Q1,1\n"
    v0_path.write_text(sentinel, encoding="utf-8")

    build_a5_features(encoder=_fake_encoder)

    assert v0_path.read_text(encoding="utf-8") == sentinel
