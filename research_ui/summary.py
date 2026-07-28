"""Safe, presentation-ready summaries derived from validated UI bundle zones."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from statistics import fmean
from typing import Any, Iterable

from .policy import parse_iso_date

CARD_TYPE_ORDER = ("rule_based_baseline", "llm_ml_only", "llm_full_evidence")
PRESET_ORDER = ("normal_evidence", "data_quality_limitation", "monitoring_escalation")


def derive_workflow_state(events: Iterable[dict[str, Any]]) -> str:
    """Return canonical state precedence without consulting review data."""
    actions = {str(event.get("action") or "") for event in events}
    if "Review Required" in actions:
        return "Review Required"
    if "Watch" in actions:
        return "Watch"
    return "Initial"


def summarize_candidates(candidates: Iterable[dict[str, Any]], states_by_id: dict[str, str]) -> dict[str, Any]:
    """Summarize select-zone metadata and monitor-zone states only."""
    rows = list(candidates)
    periods = sorted({str(row["period_id"]) for row in rows})
    quality_counts = Counter(
        str((row.get("data_quality") or {}).get("ticker_matching_confidence") or "unavailable")
        for row in rows
    )
    state_counts = Counter(states_by_id.get(str(row["decision_id"]), "Initial") for row in rows)
    return {
        "record_count": len(rows),
        "period_count": len(periods),
        "periods": periods,
        "ticker_count": len({str(row["ticker"]) for row in rows}),
        "matching_confidence": dict(sorted(quality_counts.items())),
        "workflow_states": {state: state_counts.get(state, 0) for state in ("Initial", "Watch", "Review Required")},
    }


def derive_demo_presets(candidates: Iterable[dict[str, Any]], states_by_id: dict[str, str]) -> list[dict[str, str]]:
    """Pick deterministic safe demo records from select and monitor metadata.

    Selection intentionally excludes review, outcome, return, and rubric data.
    """
    rows = sorted((dict(row) for row in candidates), key=lambda row: str(row["decision_id"]))
    if not rows:
        return []

    def matching(row: dict[str, Any]) -> str:
        return str((row.get("data_quality") or {}).get("ticker_matching_confidence") or "").lower()

    def coverage(row: dict[str, Any]) -> str:
        return str((row.get("data_quality") or {}).get("news_coverage") or "").lower()

    normal = next(
        (
            row
            for row in rows
            if states_by_id.get(str(row["decision_id"]), "Initial") != "Review Required"
            and coverage(row) == "high"
            and matching(row) not in {"mixed", "partial", "low", "none"}
        ),
        None,
    )
    limitation = next(
        (
            row
            for row in rows
            if matching(row) in {"mixed", "partial", "low", "none"}
            or coverage(row) in {"low", "none"}
            or bool((row.get("data_quality") or {}).get("missing_fields"))
        ),
        None,
    )
    escalation = next(
        (row for row in rows if states_by_id.get(str(row["decision_id"])) == "Review Required"),
        None,
    )

    selected_ids: set[str] = set()

    def choose(preferred: dict[str, Any] | None) -> dict[str, Any]:
        if preferred is not None and str(preferred["decision_id"]) not in selected_ids:
            choice = preferred
        else:
            choice = next((row for row in rows if str(row["decision_id"]) not in selected_ids), rows[0])
        selected_ids.add(str(choice["decision_id"]))
        return choice

    selections = {
        "normal_evidence": choose(normal or next((row for row in rows if coverage(row) == "high"), None)),
        "data_quality_limitation": choose(limitation),
        "monitoring_escalation": choose(escalation or next((row for row in rows if states_by_id.get(str(row["decision_id"])) == "Watch"), None)),
    }
    labels = {
        "normal_evidence": "Luồng giải thích evidence",
        "data_quality_limitation": "Minh họa giới hạn dữ liệu",
        "monitoring_escalation": "Minh họa cảnh báo theo dõi",
    }
    return [
        {
            "key": key,
            "label": labels[key],
            "decision_id": str(selections[key]["decision_id"]),
            "selection_inputs": "select, monitor",
        }
        for key in PRESET_ORDER
    ]


def filter_candidates_historically(candidates: Iterable[dict[str, Any]], as_of: date | str, periods: Iterable[str] | None = None) -> list[dict[str, Any]]:
    """Return select-zone candidates observable at a historical cutoff."""
    cutoff = parse_iso_date(as_of)
    selected_periods = {str(period) for period in periods} if periods is not None else None
    return [
        dict(candidate)
        for candidate in candidates
        if parse_iso_date(candidate["decision_date"]) <= cutoff
        and (selected_periods is None or str(candidate["period_id"]) in selected_periods)
    ]


def summarize_workflow_by_period(candidates: Iterable[dict[str, Any]], events_by_id: dict[str, Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Count candidate workflow states by decision period from monitor-zone events."""
    rows = list(candidates)
    periods = sorted({str(candidate["period_id"]) for candidate in rows})
    counts = {period: Counter() for period in periods}
    for candidate in rows:
        decision_id = str(candidate["decision_id"])
        counts[str(candidate["period_id"])][derive_workflow_state(events_by_id.get(decision_id, []))] += 1
    return [
        {
            "period_id": period,
            "Initial": counts[period]["Initial"],
            "Watch": counts[period]["Watch"],
            "Review Required": counts[period]["Review Required"],
            "candidate_count": sum(counts[period].values()),
        }
        for period in periods
    ]


def summarize_full_evidence_quality_by_period(details: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Measure full-evidence field availability from prompt-safe initial payloads only."""
    aggregates: dict[str, dict[str, int]] = defaultdict(lambda: {"numerator": 0, "denominator": 0, "candidate_count": 0, "evaluated_candidate_count": 0, "zero_evidence_candidate_count": 0, "unavailable_field_count": 0})
    for detail in details:
        period = str(detail["period_id"])
        aggregate = aggregates[period]
        aggregate["candidate_count"] += 1
        evidence_count = len(detail.get("news_evidence") or [])
        if evidence_count == 0:
            aggregate["zero_evidence_candidate_count"] += 1
            continue
        aggregate["evaluated_candidate_count"] += 1
        quality = detail.get("data_quality_flags") or {}
        available = 0
        for field in ("full_text_coverage", "summary_coverage", "key_fact_coverage"):
            value = quality.get(field)
            if value is None:
                aggregate["unavailable_field_count"] += 1
                continue
            available += min(max(int(value), 0), evidence_count)
        aggregate["numerator"] += available
        aggregate["denominator"] += 3 * evidence_count
    return [
        {
            "period_id": period,
            **aggregate,
            "availability_pct": round(100 * aggregate["numerator"] / aggregate["denominator"], 2) if aggregate["denominator"] else None,
        }
        for period, aggregate in sorted(aggregates.items())
    ]


def summarize_evaluation(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize exactly one evaluation run by card type."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["card_type"])].append(record)

    summary: list[dict[str, Any]] = []
    for card_type in CARD_TYPE_ORDER:
        rows = grouped.get(card_type, [])
        if not rows:
            continue
        summary.append(
            {
                "card_type": card_type,
                "card_count": len(rows),
                "faithfulness_mean": round(fmean(float(row["faithfulness"]) for row in rows), 2),
                "hallucination_control_mean": round(fmean(float(row["hallucination_control"]) for row in rows), 2),
                "ml_explanation_mean": round(fmean(float(row["ml_explanation"]) for row in rows), 2),
                "risk_awareness_mean": round(fmean(float(row["risk_awareness"]) for row in rows), 2),
                "monitoring_usefulness_mean": round(fmean(float(row["monitoring_usefulness"]) for row in rows), 2),
                "clarity_usefulness_mean": round(fmean(float(row["clarity_usefulness"]) for row in rows), 2),
                "overall_mean": round(fmean(float(row["overall"]) for row in rows), 2),
                "major_hallucination_count": sum(int(row.get("major_hallucination_count") or 0) for row in rows),
                "missing_evidence_ref_count": sum(int(row.get("missing_evidence_ref_count") or 0) for row in rows),
            }
        )
    return summary
