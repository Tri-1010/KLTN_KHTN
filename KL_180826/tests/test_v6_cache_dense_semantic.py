from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = BUNDLE_ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


adapter = load("adapt_cache_to_semantic_labels")
features = load("build_semantic_features")
builder = load("build_v6_primary_panel")
runner = load("run_v6_technical_primary")


def test_direction_from_sentiment_score_thresholds():
    assert adapter._direction_from_sentiment_score(0.4, "neutral") == "support"
    assert adapter._direction_from_sentiment_score(-0.4, "neutral") == "risk"
    assert adapter._direction_from_sentiment_score(0.0, "positive") == "support"
    assert adapter._direction_from_sentiment_score(0.1, "neutral") == "mixed"
    assert adapter._direction_from_sentiment_score(None, "mixed") == "mixed"


def test_adapt_cache_rows_maps_schema():
    raw = pd.DataFrame(
        [
            {
                "status": "ok",
                "ticker": "VCB",
                "article_date": "2024-01-02",
                "content_hash": "abc",
                "is_stock_relevant": True,
                "relevance_to_ticker": "direct",
                "information_magnitude_score": 5,
                "sentiment": "neutral",
                "sentiment_score": 0.6,
                "event_type": "debt_risk",
                "uncertainty_score": 2,
                "novelty_hint_score": 3,
            },
            {
                "status": "ok",
                "ticker": "FPT",
                "article_date": "2024-01-03",
                "content_hash": "def",
                "is_stock_relevant": True,
                "relevance_to_ticker": "indirect",
                "information_magnitude_score": 3,
                "sentiment": "neutral",
                "sentiment_score": -0.5,
                "event_type": "legal_risk",
                "uncertainty_score": 1,
                "novelty_hint_score": 2,
            },
        ]
    )
    adapted = adapter.adapt_cache_rows(raw)
    assert list(adapted["consensus_ticker_relevance"]) == ["direct", "indirect"]
    assert list(adapted["consensus_materiality"]) == ["high", "medium"]
    assert list(adapted["consensus_direction"]) == ["support", "risk"]
    assert list(adapted["consensus_event_type"]) == ["debt", "legal"]
    assert adapted["analysis_eligible"].astype(bool).all()
    assert (adapted["high_disagreement_fields"] == "").all()


def test_feature_builder_refuses_locked_daily_with_override_labels(tmp_path: Path):
    labels = tmp_path / "labels.csv"
    labels.write_text("ticker,article_date,analysis_eligible\n", encoding="utf-8")
    locked = tmp_path / "semantic_features_daily.csv"
    with pytest.raises(SystemExit):
        features.main(
            [
                "--labels",
                str(labels),
                "--output-daily",
                str(locked),
                "--output-period",
                str(tmp_path / "period.csv"),
            ]
        )


def test_feature_builder_allows_alternate_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    labels = tmp_path / "labels.csv"
    labels.write_text(
        "ticker,article_date,analysis_eligible,consensus_ticker_relevance,"
        "consensus_materiality,consensus_direction,consensus_event_type,"
        "consensus_materiality_score,consensus_uncertainty_score,consensus_novelty_score,"
        "high_disagreement_fields\n"
        "AAA,2024-01-02,True,direct,high,support,earnings,5,1,1,\n",
        encoding="utf-8",
    )
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
        }
    )
    monkeypatch.setattr(features, "load_prices", lambda: prices)
    daily_out = tmp_path / "semantic_features_daily_cache_dense.csv"
    period_out = tmp_path / "semantic_features_period_cache_dense.csv"
    rc = features.main(
        [
            "--labels",
            str(labels),
            "--output-daily",
            str(daily_out),
            "--output-period",
            str(period_out),
        ]
    )
    assert rc == 0
    assert daily_out.exists()
    assert period_out.exists()


def test_runner_sensitivity_tag_forces_non_primary_claim_level():
    claim_level, limitations = runner._claim_level(
        20,
        "primary",
        "densified_cache_semantic",
        builder.load_v6_spec(),
    )
    assert claim_level == "v6_sensitivity_densified_cache_semantic"
    assert "sensitivity_only_not_v6_primary" in limitations
    assert "does_not_replace_v6_primary_20260909" in limitations
    assert "no_causal_or_investment_advice_claim" in limitations


def test_write_summaries_rejects_paths_outside_declared_workspace(tmp_path: Path):
    pred = pd.DataFrame()
    folds = pd.DataFrame()
    with pytest.raises(Exception, match="escapes workspace root"):
        runner.write_summaries(
            tmp_path / "out",
            tmp_path / "rep",
            "v6_sens_sem_feat_20260909",
            builder.load_v6_spec(),
            pred,
            folds,
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            fast=True,
        )


def test_panel_builder_sensitivity_tag_helper():
    assert builder._normalize_sensitivity_tag(" densified_cache_semantic ") == "densified_cache_semantic"
    assert runner._normalize_sensitivity_tag("densified_cache_semantic") == "densified_cache_semantic"
