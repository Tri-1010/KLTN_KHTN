from __future__ import annotations

from research_ui.assets.theme import STATUS_TOKENS
from research_ui.summary import derive_demo_presets, derive_workflow_state, summarize_candidates, summarize_evaluation


def _candidate(decision_id: str, *, coverage: str = "high", matching: str = "high") -> dict[str, object]:
    return {
        "decision_id": decision_id,
        "ticker": decision_id.split("_")[1],
        "period_id": "2025Q1",
        "data_quality": {"news_coverage": coverage, "ticker_matching_confidence": matching, "missing_fields": []},
    }


def _score(card_type: str, overall: int, *, run: str = "run-a") -> dict[str, object]:
    return {
        "evaluation_run_id": run,
        "card_type": card_type,
        "faithfulness": overall,
        "hallucination_control": overall,
        "ml_explanation": overall,
        "risk_awareness": overall,
        "monitoring_usefulness": overall,
        "clarity_usefulness": overall,
        "overall": overall,
        "major_hallucination_count": 0,
        "missing_evidence_ref_count": 1,
    }


def test_workflow_state_uses_canonical_precedence():
    assert derive_workflow_state([]) == "Initial"
    assert derive_workflow_state([{"action": "Watch"}]) == "Watch"
    assert derive_workflow_state([{"action": "Watch"}, {"action": "Review Required"}]) == "Review Required"


def test_demo_presets_are_deterministic_and_safe_metadata_only():
    candidates = [
        _candidate("2025Q1_AAA_01"),
        _candidate("2025Q1_BBB_02", matching="mixed"),
        _candidate("2025Q1_CCC_03"),
    ]
    states = {"2025Q1_AAA_01": "Initial", "2025Q1_BBB_02": "Watch", "2025Q1_CCC_03": "Review Required"}

    presets = derive_demo_presets(candidates, states)

    assert [item["key"] for item in presets] == ["normal_evidence", "data_quality_limitation", "monitoring_escalation"]
    assert [item["decision_id"] for item in presets] == ["2025Q1_AAA_01", "2025Q1_BBB_02", "2025Q1_CCC_03"]
    assert {item["selection_inputs"] for item in presets} == {"select, monitor"}


def test_candidate_summary_excludes_outcome_and_counts_states():
    candidates = [_candidate("2025Q1_AAA_01"), _candidate("2025Q1_BBB_02", matching="mixed")]

    summary = summarize_candidates(candidates, {"2025Q1_AAA_01": "Initial", "2025Q1_BBB_02": "Watch"})

    assert summary["record_count"] == 2
    assert summary["workflow_states"] == {"Initial": 1, "Watch": 1, "Review Required": 0}
    assert "outcome" not in str(summary).lower()


def test_evaluation_summary_groups_single_supplied_run_by_card_type():
    summary = summarize_evaluation([_score("llm_ml_only", 2), _score("llm_ml_only", 4), _score("llm_full_evidence", 5)])

    assert [(row["card_type"], row["card_count"], row["overall_mean"]) for row in summary] == [
        ("llm_ml_only", 2, 3.0),
        ("llm_full_evidence", 1, 5.0),
    ]
    assert summarize_evaluation([]) == []


def test_status_labels_do_not_issue_trade_call_to_action():
    copy = " ".join(token["label"].lower() for token in STATUS_TOKENS.values())

    assert all(word not in copy for word in ("buy", "sell", "trade", "mua", "bán", "giao dịch"))
