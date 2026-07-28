from __future__ import annotations

from copy import deepcopy
from datetime import date

import pytest

from research_ui.policy import (
    PolicyViolation,
    assert_initial_payload_safe,
    assert_review_payload,
    assert_runtime_zone_safe,
    display_signal_label,
    filter_monitor_events,
    find_forbidden_markers,
    parse_iso_date,
    RESEARCH_DISCLAIMER,
)


INITIAL_PAYLOAD = {
    "decision_id": "2025Q1_ABC_01",
    "snapshot_mode": "full_evidence",
    "ticker": "ABC",
    "decision_date": "2025-03-31",
    "period_id": "2025Q1",
    "holding_horizon": "next_quarter",
    "ml_signal": {
        "model_name": "test",
        "pred_proba_up": 0.5,
        "pred_label": 0,
        "rank_in_period": 1,
        "source_signal_class": "Watch",
        "display_status": "Watch",
    },
    "technical_snapshot": {"rsi_end_q": 55.0},
    "top_drivers": [
        {"feature": "rsi_end_q", "value": 55.0, "direction": "neutral", "explanation": "canonical"}
    ],
    "news_evidence": [
        {
            "evidence_id": "N001",
            "published_at": "2025-03-31",
            "source": "test",
            "title": "Point-in-time evidence",
            "article_summary": None,
            "key_facts": [],
            "risk_flags": [],
            "event_type": None,
            "match_confidence": None,
            "evidence_span": None,
            "url": None,
            "content_hash": None,
            "extraction_status": None,
        }
    ],
    "data_quality_flags": {
        "news_coverage": None,
        "ticker_matching_confidence": None,
        "full_text_coverage": None,
        "summary_coverage": None,
        "key_fact_coverage": None,
        "missing_fields": [],
    },
    "guardrails": {},
    "provenance": {
        "name": "test",
        "path": "test.json",
        "sha256": "0" * 64,
        "zone": "initial",
        "record_count": 1,
        "schema_version": None,
        "generated_at_utc": None,
        "provenance_status": None,
    },
}


def test_disclaimer_separates_validated_bundle_from_external_chart():
    assert "Validated bundle has no live market data" in RESEARCH_DISCLAIMER
    assert "External current market context is display-only" in RESEARCH_DISCLAIMER
    assert "Not investment advice" in RESEARCH_DISCLAIMER


def test_parse_iso_date_rejects_trailing_text():
    assert parse_iso_date("2025-01-02T09:30:00Z") == date(2025, 1, 2)
    with pytest.raises(PolicyViolation, match="Invalid ISO date"):
        parse_iso_date("2025-01-02junk")


def test_initial_payload_rejects_outcome_leakage():
    payload = deepcopy(INITIAL_PAYLOAD)
    payload["outcome_for_review_only"] = {"value": 0.1}

    with pytest.raises(PolicyViolation, match="forbidden markers"):
        assert_initial_payload_safe(payload)


def test_initial_payload_allows_news_at_decision_cutoff():
    assert_initial_payload_safe(INITIAL_PAYLOAD)


def test_initial_payload_rejects_news_after_decision_cutoff():
    payload = deepcopy(INITIAL_PAYLOAD)
    payload["news_evidence"][0]["published_at"] = "2025-04-01"

    with pytest.raises(PolicyViolation, match="exceeds decision_date"):
        assert_initial_payload_safe(payload)


@pytest.mark.parametrize("future_key", ["return_next_q", "next_period_gain", "label_after_horizon"])
def test_initial_payload_rejects_renamed_future_technical_fields(future_key: str):
    payload = deepcopy(INITIAL_PAYLOAD)
    payload["technical_snapshot"][future_key] = 0.25

    with pytest.raises(PolicyViolation, match="unknown fields.*technical_snapshot"):
        assert_initial_payload_safe(payload)


def test_initial_payload_rejects_unknown_top_driver_feature():
    payload = deepcopy(INITIAL_PAYLOAD)
    payload["top_drivers"][0]["feature"] = "label_after_horizon"

    with pytest.raises(PolicyViolation, match="model feature contract"):
        assert_initial_payload_safe(payload)


def test_find_forbidden_markers_descends_nested_values():
    assert find_forbidden_markers({"safe": {"note": "future_label unavailable"}}) == ["$.safe.note"]


def test_monitor_events_filter_by_as_of_and_sort_descending():
    events = [
        {"event_date": "2025-04-02", "title": "Later"},
        {"event_date": "2025-04-01", "title": "Earlier"},
        {"event_date": "2025-04-03", "title": "Future"},
    ]

    actual = filter_monitor_events(events, "2025-04-02")

    assert [event["title"] for event in actual] == ["Later", "Earlier"]


def test_review_payload_requires_explicit_post_hoc_boundary():
    with pytest.raises(PolicyViolation, match="review_only"):
        assert_review_payload({"provenance": {}})

    assert_review_payload({"provenance": {"review_only": True}})


def test_runtime_select_rejects_nested_unknown_outcome_field():
    row = {
        "decision_id": "D1",
        "ticker": "ABC",
        "period_id": "2025Q1",
        "decision_date": "2025-03-31",
        "display_status": "Watch",
        "pred_proba_up": 0.5,
        "rank_in_period": 1,
        "data_quality": {
            "news_coverage": None,
            "ticker_matching_confidence": None,
            "full_text_coverage": None,
            "summary_coverage": None,
            "key_fact_coverage": None,
            "missing_fields": [],
            "post_hoc_outcome": 1,
        },
        "monitoring_available": True,
        "review_available": True,
    }

    with pytest.raises(PolicyViolation, match="select payload contains forbidden markers"):
        assert_runtime_zone_safe("select", [row])


def test_runtime_monitor_and_update_enforce_schema_and_cutoff():
    event = {
        "event_id": "E1",
        "decision_id": "D1",
        "ticker": "ABC",
        "decision_date": "2025-03-31",
        "event_date": "2025-04-02",
        "action": "Watch",
        "reason": "new evidence",
        "source": "test",
        "title": "Event",
        "event_type": None,
        "risk_flags": [],
        "match_confidence": None,
        "article_summary": None,
        "url": None,
        "content_hash": None,
        "consensus_join_status": "not_found",
        "semantic_quality": None,
    }
    assert_runtime_zone_safe("monitor", [event])

    update = {
        "decision_id": "D1",
        "as_of": "2025-04-01",
        "initial_reference": {"decision_date": "2025-03-31", "ticker": "ABC"},
        "monitoring_events": [event],
        "workflow_state": "Watch",
        "proposed_analyst_questions": [],
        "persisted": False,
    }
    with pytest.raises(PolicyViolation, match="event_date exceeds update as_of"):
        assert_runtime_zone_safe("update", update)

    event["semantic_quality"] = {"news_id": "N1", "future_label": 1}
    with pytest.raises(PolicyViolation, match="monitor payload contains forbidden markers"):
        assert_runtime_zone_safe("monitor", [event])


def test_runtime_cards_allow_only_verified_negated_outcome_language():
    card = {
        "card_id": "C1",
        "decision_id": "D1",
        "card_type": "llm_ml_only",
        "producer_run_id": "R1",
        "provider": "test",
        "requested_model": None,
        "response_model": None,
        "vendor": None,
        "generated_at_utc": None,
        "prompt_sha256": None,
        "pack_sha256": None,
        "body_markdown": "Không sử dụng outcome tương lai.",
    }
    assert_runtime_zone_safe("cards", [card])
    card["body_markdown"] = "Không sử dụng dữ liệu sau ngày quyết định hoặc outcome tương lai."
    assert_runtime_zone_safe("cards", [card])

    card["body_markdown"] = "Outcome thực tế đạt 20%."
    with pytest.raises(PolicyViolation, match="cards payload contains forbidden markers"):
        assert_runtime_zone_safe("cards", [card])

    card["post_hoc_outcome"] = None
    with pytest.raises(PolicyViolation, match="cards payload contains forbidden markers"):
        assert_runtime_zone_safe("cards", [card])


def test_display_signal_label_avoids_trade_cta():
    assert display_signal_label("Buy Candidate") == "Model candidate"
    assert display_signal_label(None) == "Unavailable"
