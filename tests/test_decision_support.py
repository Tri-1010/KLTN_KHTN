import json
from pathlib import Path

import pytest

from scripts import generate_decision_support_artifacts as artifacts


SAMPLE_PACK = {
    "decision_id": "2025Q1_ABC_01",
    "ticker": "ABC",
    "decision_date": "2025-03-31",
    "period_id": "2025Q1",
    "ml_signal": {"pred_proba_up": 0.91, "pred_label": 1, "rank_in_period": 1},
    "technical_snapshot": {"rsi_end_q": 60.0},
    "top_drivers": [{"feature": "rsi_end_q", "value": 60.0}],
    "news_evidence": [
        {
            "evidence_id": "N001",
            "published_at": "2025-03-01",
            "title": "ABC báo lãi",
            "article_summary": "ABC tăng lợi nhuận.",
            "key_facts": [{"fact_id": "N001-F01", "fact": "Lợi nhuận tăng"}],
            "risk_flags": ["governance"],
            "event_type": "earnings",
            "lead": "Lead",
            "full_text_ref": "hash1",
            "content_hash": "hash1",
            "full_text_chars": 1000,
            "full_text_excerpt": "ABC báo lãi nhờ doanh thu tăng.",
        }
    ],
    "data_quality_flags": {
        "news_coverage": "high",
        "full_text_coverage": 1,
        "summary_coverage": 1,
        "key_fact_coverage": 1,
    },
    "outcome_for_review_only": {
        "realized_period_return": 0.12,
        "outcome_label": "positive",
    },
    "nested": {"future_return": 0.5, "safe": "ok"},
}


def test_strip_initial_prompt_fields_removes_outcome():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    text = json.dumps(clean, ensure_ascii=False).lower()
    assert "outcome_for_review_only" not in clean
    assert "realized" not in text
    assert "future_return" not in text
    assert clean["nested"]["safe"] == "ok"


def test_initial_pack_has_no_realized_or_future_tokens():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    assert not artifacts.serialized_has_initial_leakage(clean)
    artifacts.assert_no_initial_leakage(clean)


def test_news_evidence_cutoff_published_at_le_decision_date():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    for news in clean["news_evidence"]:
        assert news["published_at"] <= clean["decision_date"]


def test_ml_only_variant_excludes_news_evidence():
    ml_only = artifacts.build_ml_only_pack(SAMPLE_PACK)
    assert "news_evidence" not in ml_only
    assert ml_only["ml_signal"] == SAMPLE_PACK["ml_signal"]
    assert ml_only["technical_snapshot"] == SAMPLE_PACK["technical_snapshot"]
    assert ml_only["data_quality_flags"]["news_evidence_removed_for_ablation"] is True
    assert not artifacts.serialized_has_initial_leakage(ml_only)


def test_full_evidence_uses_enriched_fields():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    news = clean["news_evidence"][0]
    for key in ["article_summary", "key_facts", "risk_flags", "lead", "full_text_ref", "content_hash", "full_text_chars", "full_text_excerpt"]:
        assert key in news
        assert news[key] not in (None, "", [])


def test_manifest_records_model_metadata_and_hashes(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("abc", encoding="utf-8")
    assert artifacts.sha256_file(source) == artifacts.sha256_text("abc")


def test_offline_mode_writes_prompts_not_fake_cards(tmp_path):
    from scripts import generate_llm_decision_cards as llm_cards

    prompt_path, rows = llm_cards.write_offline_prompts("ml_only", [artifacts.build_ml_only_pack(SAMPLE_PACK)], "pytest")
    try:
        assert prompt_path.exists()
        assert rows[0]["decision_id"] == SAMPLE_PACK["decision_id"]
        assert "card_markdown" not in rows[0]
        assert "outcome_for_review_only" not in rows[0]["user_prompt"]
    finally:
        if prompt_path.exists():
            prompt_path.unlink()
