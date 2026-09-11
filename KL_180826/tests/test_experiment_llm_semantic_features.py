"""Tests for spec-compliant LLM semantic feature experiment."""

from __future__ import annotations

import pandas as pd
import pytest

from pipeline.experiment_llm_semantic_features import (
    CACHE_COLUMNS,
    SEMANTIC_SCHEMA,
    SYSTEM_PROMPT,
    SemanticAnnotation,
    _cache_key,
    annotate_articles,
    article_payload,
    aggregate_daily_semantics,
    build_forward_labels,
    feature_sets,
    time_series_date_split,
    validate_semantic,
)


def _prices() -> pd.DataFrame:
    dates = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-08", "2024-01-09"])
    rows = []
    for ticker in ["AAA", "BBB"]:
        for i, date in enumerate(dates):
            rows.append(
                {
                    "ticker": ticker,
                    "date": date,
                    "open": 10 + i,
                    "high": 11 + i,
                    "low": 9 + i,
                    "close": 10 + i,
                    "volume": 1000 + i,
                }
            )
    return pd.DataFrame(rows)


def _valid_payload() -> dict[str, object]:
    return {
        "ticker": "AAA",
        "company_name": "AAA Corp",
        "article_date": "2024-01-02",
        "is_stock_relevant": True,
        "sentiment": "positive",
        "importance_score": 4,
        "expected_impact_score": 3,
        "uncertainty_score": 2,
        "novelty_score": 3,
        "time_horizon": "short_term",
        "reasoning_confidence": 4,
        "summary": "Doanh thu tăng.",
        "reason": "Bài báo nêu kết quả kinh doanh tích cực.",
    }


def test_validate_semantic_accepts_spec_payload_and_rejects_legacy_fields():
    payload = _valid_payload()

    annotation = validate_semantic(payload)

    assert annotation.company_name == "AAA Corp"
    assert annotation.sentiment == "positive"
    assert annotation.sentiment_score == 1.0
    assert annotation.expected_impact_score == 3
    assert annotation.novelty_score == 3

    payload["sentiment"] = "bullish"
    with pytest.raises(ValueError):
        validate_semantic(payload)

    payload = _valid_payload()
    payload["is_stock_relevant"] = "false"
    with pytest.raises(ValueError):
        validate_semantic(payload)

    for legacy in ("sentiment_score", "information_magnitude_score", "novelty_hint_score", "event_type", "relevance_to_ticker"):
        payload = _valid_payload()
        payload[legacy] = "legacy"
        with pytest.raises(ValueError):
            validate_semantic(payload)


def test_schema_and_prompt_match_extraction_spec():
    required = set(SEMANTIC_SCHEMA["required"])
    assert {
        "ticker",
        "company_name",
        "article_date",
        "is_stock_relevant",
        "sentiment",
        "importance_score",
        "expected_impact_score",
        "uncertainty_score",
        "novelty_score",
        "time_horizon",
        "reasoning_confidence",
        "summary",
        "reason",
    }.issubset(required)

    forbidden = ["information_magnitude_score", "novelty_hint_score", "event_type", "relevance_to_ticker", "sentiment_score"]
    schema_text = str(SEMANTIC_SCHEMA)
    for field in forbidden:
        assert field not in SEMANTIC_SCHEMA["properties"]
        assert field in SYSTEM_PROMPT
        assert field in schema_text or field in SYSTEM_PROMPT
    assert "expected_impact_score" in SYSTEM_PROMPT
    assert "khuyến nghị mua/bán/nắm giữ" in SYSTEM_PROMPT


def test_article_payload_prefers_full_text_and_records_truncation():
    article = {
        "ticker": "AAA",
        "date": "2024-01-02",
        "title": "AAA title",
        "description": "short",
        "text_clean": "clean text",
        "full_text": "x" * 20,
        "url": "https://example.com/a",
    }

    payload = article_payload(article, max_chars=7)

    assert payload["article_text"] == "x" * 7
    assert payload["article_text_chars"] == 20
    assert payload["truncated"] is True
    assert "text_excerpt" not in payload


def test_aggregate_daily_semantics_excludes_irrelevant_articles_and_keeps_no_news_dates():
    prices = _prices()[_prices()["ticker"] == "AAA"].copy()
    annotations = pd.DataFrame(
        [
            {
                "status": "ok",
                "ticker": "AAA",
                "article_date": "2024-01-02",
                "is_stock_relevant": False,
                "sentiment": "positive",
                "sentiment_score": 1.0,
                "importance_score": 5,
                "expected_impact_score": 4,
                "uncertainty_score": 1,
                "novelty_score": 4,
                "reasoning_confidence": 5,
                "time_horizon": "short_term",
            },
            {
                "status": "ok",
                "ticker": "AAA",
                "article_date": "2024-01-03",
                "is_stock_relevant": True,
                "sentiment": "negative",
                "sentiment_score": -1.0,
                "importance_score": 4,
                "expected_impact_score": 4,
                "uncertainty_score": 2,
                "novelty_score": 3,
                "reasoning_confidence": 4,
                "time_horizon": "short_term",
            },
        ]
    )

    features = aggregate_daily_semantics(annotations, prices)

    assert features.iloc[0]["llm_news_count"] == 0
    assert features.iloc[1]["llm_news_count"] == 1
    assert features.iloc[1]["llm_sentiment_mean"] == -1.0
    assert features.iloc[1]["llm_expected_impact_mean"] == 4
    assert "llm_magnitude_mean" not in features.columns
    assert not any(col.startswith("llm_event_") for col in features.columns)
    assert "llm_direct_ratio" not in features.columns


def test_aggregate_daily_semantics_keeps_no_news_dates_and_rolls_past_only():
    prices = _prices()[_prices()["ticker"] == "AAA"].copy()
    annotations = pd.DataFrame(
        [
            {
                "status": "ok",
                "ticker": "AAA",
                "article_date": "2024-01-02",
                "is_stock_relevant": True,
                "sentiment": "positive",
                "sentiment_score": 1.0,
                "importance_score": 5,
                "expected_impact_score": 4,
                "uncertainty_score": 1,
                "novelty_score": 4,
                "reasoning_confidence": 5,
                "time_horizon": "short_term",
            }
        ]
    )

    features = aggregate_daily_semantics(annotations, prices)

    assert len(features) == len(prices)
    assert features.iloc[0]["llm_news_count"] == 1
    assert features.iloc[1]["llm_news_count"] == 0
    assert features.iloc[0]["llm_news_count_roll_3d"] == 1
    assert features.iloc[1]["llm_news_count_roll_3d"] == 1
    assert features.iloc[3]["llm_news_count_roll_3d"] == 0


def test_forward_labels_use_trading_day_shift():
    labels = build_forward_labels(_prices()[_prices()["ticker"] == "AAA"], horizons=(1, 5))

    labels = labels.sort_values("date").reset_index(drop=True)
    assert labels.loc[0, "label_up_1d"] == 1
    assert labels.loc[0, "label_up_5d"] == 1
    assert pd.isna(labels.loc[1, "label_up_5d"])


def test_date_split_has_no_overlap():
    df = _prices()[["ticker", "date", "close"]].copy()
    train, test = time_series_date_split(df, test_frac=0.34)

    assert set(train["date"]).isdisjoint(set(test["date"]))
    assert train["date"].max() < test["date"].min()


def test_annotate_articles_ignores_stale_cache_hashes(tmp_path):
    article = {
        "ticker": "AAA",
        "date": "2024-01-02",
        "title": "AAA công bố kết quả kinh doanh",
        "description": "Doanh thu tăng.",
        "text_clean": "AAA công bố doanh thu và lợi nhuận tăng trong quý.",
        "url": "https://example.com/a",
        "source": "test",
    }
    cache_key = _cache_key(article, "deepseek", "deepseek-chat")
    stale = {col: "" for col in CACHE_COLUMNS}
    stale.update(
        {
            "cache_key": cache_key,
            "content_hash": "stale-content",
            "ticker": "AAA",
            "company_name": "AAA Corp",
            "article_date": "2024-01-02",
            "is_stock_relevant": True,
            "sentiment": "positive",
            "sentiment_score": 1.0,
            "importance_score": 5,
            "expected_impact_score": 5,
            "uncertainty_score": 1,
            "novelty_score": 3,
            "reasoning_confidence": 5,
            "time_horizon": "short_term",
            "prompt_sha256": "stale-prompt",
            "input_sha256": "stale-input",
            "status": "ok",
        }
    )
    cache_path = tmp_path / "cache.csv"
    pd.DataFrame([stale], columns=CACHE_COLUMNS).to_csv(cache_path, index=False, encoding="utf-8")

    class FakeClient:
        def annotate(self, _article):
            return SemanticAnnotation(
                ticker="AAA",
                company_name="AAA Corp",
                article_date="2024-01-02",
                is_stock_relevant=True,
                sentiment="negative",
                sentiment_score=-1.0,
                importance_score=4,
                expected_impact_score=4,
                uncertainty_score=2,
                novelty_score=3,
                time_horizon="short_term",
                reasoning_confidence=4,
                summary="AAA tăng trưởng.",
                reason="Bài báo nêu doanh thu và lợi nhuận tăng.",
            )

    rows = annotate_articles(
        pd.DataFrame([article]),
        cache_path=str(cache_path),
        prompt_packs_path=str(tmp_path / "prompts.jsonl"),
        provider="deepseek",
        model="deepseek-chat",
        client=FakeClient(),
    )

    assert rows.iloc[0]["sentiment"] == "negative"
    assert rows.iloc[0]["expected_impact_score"] == 4


def test_feature_sets_exclude_future_columns():
    df = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "date": [pd.Timestamp("2024-01-02")],
            "return_1d": [0.1],
            "llm_sentiment_mean": [0.2],
            "future_return_5d": [0.3],
            "label_up_5d": [1],
        }
    )

    sets = feature_sets(df)

    assert "future_return_5d" not in sets["Config_Hybrid"]
    assert "label_up_5d" not in sets["Config_Hybrid"]
    assert sets["Config_A"] == ["return_1d"]
    assert sets["Config_LLM"] == ["llm_sentiment_mean"]
