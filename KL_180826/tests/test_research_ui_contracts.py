from __future__ import annotations

from copy import deepcopy

import pytest

from research_ui.contracts import EvaluationRecord, FreshInformationRequest, LiveJobRequest
from research_ui.run_catalog import CatalogValidationError, assert_catalog_valid, load_catalog


def test_live_job_requires_explicit_external_call_confirmation():
    request = LiveJobRequest(
        decision_ids=["2025Q1_SCR_01"],
        variant="full_evidence",
        provider="gemini",
        model="gemini-2.5-pro",
    )

    assert request.confirmed_external_call is False


def test_live_and_fresh_requests_reject_non_allowlisted_models():
    with pytest.raises(Exception, match="not allowlisted"):
        LiveJobRequest(
            decision_ids=["2025Q1_SCR_01"],
            variant="full_evidence",
            provider="gemini",
            model="gemini-unreviewed",
        )
    with pytest.raises(Exception, match="not allowlisted"):
        FreshInformationRequest(
            decision_id="2025Q1_SCR_01",
            provider="anthropic",
            model="claude-unreviewed",
            source_ids=["vnexpress_business"],
        )


def test_evaluation_scores_reject_out_of_range_values():
    with pytest.raises(Exception):
        EvaluationRecord(
            card_id="run:llm_full_evidence:2025Q1_SCR_01",
            decision_id="2025Q1_SCR_01",
            card_type="llm_full_evidence",
            evaluation_run_id="run",
            judge_provider="gemini",
            faithfulness=6,
            hallucination_control=5,
            ml_explanation=5,
            risk_awareness=5,
            monitoring_usefulness=5,
            clarity_usefulness=5,
            overall=5,
            major_hallucination_count=0,
            missing_evidence_ref_count=0,
        )


def test_catalog_rejects_incorrect_common_judge_score_count():
    catalog = deepcopy(load_catalog())
    for run in catalog["runs"]:
        if run["run_id"] == "common-local-judge-gemini-cards-2026-07":
            run["rubric"]["expected_records"] = 74

    with pytest.raises(CatalogValidationError, match="expected 74 score rows, found 75"):
        assert_catalog_valid(catalog)
