"""Tests for A7 LLM scorecard feature extraction."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from experiments.a7_llm_scorecard import (
    LLM_FEATURE_COLS,
    META_COLS,
    ScorecardAnnotation,
    aggregate_scorecard_features,
    annotate_articles,
    build_a7_features,
    build_scorecard_prompt,
    validate_scorecard,
)


class FakeScorecardClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def annotate(self, article: dict) -> ScorecardAnnotation:
        self.calls.append(article)
        title = str(article.get("title", "")).lower()
        if "bad-json" in title:
            raise ValueError("invalid json")
        if "rủi ro" in title:
            return ScorecardAnnotation(
                sentiment="negative",
                sentiment_score=-0.8,
                materiality="high",
                materiality_score=1.0,
                risk_level="high",
                risk_score=0.9,
                event_type="legal_risk",
                relevance_to_ticker="direct",
                confidence=0.7,
                rationale="Bài viết nêu rủi ro pháp lý trực tiếp.",
            )
        return ScorecardAnnotation(
            sentiment="positive",
            sentiment_score=0.6,
            materiality="medium",
            materiality_score=0.6,
            risk_level="low",
            risk_score=0.2,
            event_type="earnings",
            relevance_to_ticker="direct",
            confidence=0.8,
            rationale="Bài viết nêu kết quả kinh doanh tích cực.",
        )


def _articles() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": "VCB",
                "date": "2024-01-10",
                "title": "VCB lợi nhuận tăng",
                "description": "Kết quả kinh doanh khả quan.",
                "url": "https://example.com/1",
            },
            {
                "ticker": "VCB",
                "date": "2024-01-15",
                "title": "VCB rủi ro pháp lý",
                "description": "Doanh nghiệp cần giải trình.",
                "url": "https://example.com/2",
            },
        ]
    )


def test_prompt_uses_only_article_fields_and_rejects_forbidden_tokens():
    prompt = build_scorecard_prompt(
        {
            "ticker": "VCB",
            "date": "2024-01-10",
            "title": "VCB lợi nhuận tăng",
            "description": "Kết quả kinh doanh khả quan.",
            "article_summary": "Lợi nhuận tăng so với cùng kỳ.",
        }
    )

    lower = prompt.lower()
    assert "vcb" in lower
    assert "lợi nhuận" in lower
    for token in ("label_basic", "next_avg_close", "realized", "shap", "outcome"):
        assert token not in lower

    with pytest.raises(ValueError):
        build_scorecard_prompt({"ticker": "VCB", "title": "future return leaked"})


def test_validate_scorecard_rejects_invalid_enum():
    with pytest.raises(ValueError):
        validate_scorecard(
            {
                "sentiment": "bullish",
                "sentiment_score": 1,
                "materiality": "high",
                "materiality_score": 1,
                "risk_level": "low",
                "risk_score": 0.2,
                "event_type": "earnings",
                "relevance_to_ticker": "direct",
                "confidence": 0.8,
                "rationale": "bad enum",
            }
        )


def test_annotate_articles_reuses_cache_and_avoids_duplicate_calls(tmp_path):
    cache_path = tmp_path / "llm_scorecard.csv"
    client = FakeScorecardClient()

    first = annotate_articles(_articles(), cache_path=str(cache_path), client=client)
    assert len(first) == 2
    assert len(client.calls) == 2

    second = annotate_articles(_articles(), cache_path=str(cache_path), client=client)
    assert len(second) == 2
    assert len(client.calls) == 2  # no new calls


def test_annotate_articles_writes_prompt_packs_when_client_unavailable(tmp_path):
    cache_path = tmp_path / "llm_scorecard.csv"
    prompts_path = tmp_path / "prompts.jsonl"
    manifest_path = tmp_path / "manifest.json"

    def failing_factory(_model):
        raise RuntimeError("no credentials")

    result = annotate_articles(
        _articles(),
        cache_path=str(cache_path),
        prompt_packs_path=str(prompts_path),
        manifest_path=str(manifest_path),
        client_factory=failing_factory,
    )

    assert result.empty
    rows = [json.loads(line) for line in prompts_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "llm_scorecard_pending_offline"


def test_annotate_articles_skips_bad_annotation_without_crashing(tmp_path):
    articles = pd.DataFrame(
        [
            {"ticker": "VCB", "date": "2024-01-10", "title": "good", "description": "ok", "url": "1"},
            {"ticker": "VCB", "date": "2024-01-11", "title": "bad-json", "description": "bad", "url": "2"},
        ]
    )
    client = FakeScorecardClient()
    result = annotate_articles(articles, cache_path=str(tmp_path / "cache.csv"), client=client)

    assert len(result) == 1
    assert result.iloc[0]["status"] == "ok"


def test_annotate_articles_skips_prompt_guard_failure_without_crashing(tmp_path):
    cache_path = tmp_path / "cache.csv"
    articles = pd.DataFrame(
        [
            {"ticker": "VCB", "date": "2024-01-10", "title": "good", "description": "ok", "url": "1"},
            {
                "ticker": "VCB",
                "date": "2024-01-11",
                "title": "future return leaked",
                "description": "bad prompt input",
                "url": "2",
            },
        ]
    )
    client = FakeScorecardClient()

    result = annotate_articles(articles, cache_path=str(cache_path), client=client)

    assert len(result) == 1
    assert result.iloc[0]["status"] == "ok"
    assert len(client.calls) == 1
    cached = pd.read_csv(cache_path, encoding="utf-8")
    assert set(cached["status"]) == {"ok", "error"}


def test_aggregate_scorecard_features_formulas_and_left_join():
    annotations = pd.DataFrame(
        [
            {
                "ticker": "VCB",
                "date": "2024-01-10",
                "sentiment": "positive",
                "sentiment_score": 0.6,
                "materiality": "medium",
                "materiality_score": 0.6,
                "risk_level": "low",
                "risk_score": 0.2,
                "event_type": "earnings",
                "relevance_to_ticker": "direct",
                "confidence": 0.8,
                "status": "ok",
            },
            {
                "ticker": "VCB",
                "date": "2024-01-15",
                "sentiment": "negative",
                "sentiment_score": -0.8,
                "materiality": "high",
                "materiality_score": 1.0,
                "risk_level": "high",
                "risk_score": 0.9,
                "event_type": "legal_risk",
                "relevance_to_ticker": "direct",
                "confidence": 0.7,
                "status": "ok",
            },
        ]
    )
    keys = pd.DataFrame(
        [
            {"ticker": "VCB", "quarter_id": "2024Q1"},
            {"ticker": "FPT", "quarter_id": "2024Q1"},
        ]
    )

    features = aggregate_scorecard_features(annotations, news_by_quarter_keys=keys)
    vcb = features[features["ticker"] == "VCB"].iloc[0]
    fpt = features[features["ticker"] == "FPT"].iloc[0]

    assert vcb["llm_score_news_count"] == 2
    assert vcb["llm_positive_ratio"] == 0.5
    assert vcb["llm_negative_ratio"] == 0.5
    assert vcb["llm_sentiment_mean"] == pytest.approx(-0.1)
    assert vcb["llm_sentiment_weighted_mean"] == pytest.approx(((0.6 * 0.6 * 1.0 * 0.8) + (-0.8 * 1.0 * 1.0 * 0.7)) / 2)
    assert vcb["llm_earnings_count"] == 1
    assert vcb["llm_legal_risk_count"] == 1
    assert fpt[LLM_FEATURE_COLS].sum() == 0


def test_build_a7_features_writes_numeric_feature_table(tmp_path):
    processed = tmp_path / "processed.csv"
    news_keys = tmp_path / "news_by_quarter.csv"
    output = tmp_path / "keyword_features_A7.csv"
    cache = tmp_path / "cache.csv"
    manifest = tmp_path / "manifest.json"

    _articles().to_csv(processed, index=False, encoding="utf-8")
    pd.DataFrame([{"ticker": "VCB", "quarter_id": "2024Q1"}]).to_csv(news_keys, index=False, encoding="utf-8")

    features = build_a7_features(
        enriched_news_path=str(tmp_path / "missing_enriched.csv"),
        processed_news_path=str(processed),
        news_by_quarter_path=str(news_keys),
        output_path=str(output),
        cache_path=str(cache),
        manifest_path=str(manifest),
        client=FakeScorecardClient(),
    )

    assert output.exists()
    assert manifest.exists()
    assert json.loads(manifest.read_text(encoding="utf-8"))["status"] == "llm_scorecard_features_ready"
    assert list(features.columns) == META_COLS + LLM_FEATURE_COLS
    non_numeric = features.drop(columns=META_COLS).select_dtypes(exclude=[np.number]).columns.tolist()
    assert non_numeric == []
