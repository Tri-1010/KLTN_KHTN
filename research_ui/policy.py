"""Trust-zone and no-overclaim policies for EvidenceTrace."""

from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any, Iterable

INITIAL_FORBIDDEN_MARKERS = (
    "outcome",
    "realized",
    "review_only",
    "benchmark_return",
    "excess_return",
    "future_return",
    "future_label",
)
INITIAL_TECHNICAL_FEATURES = frozenset(
    {
        "rsi_end_q",
        "macd_hist_mean_q",
        "price_vs_sma20",
        "return_2q_ago",
        "return_q",
        "return_prev_q",
        "volume_change_q",
        "return_mean_daily",
        "price_range_q",
        "sma20_end",
    }
)
INITIAL_ALLOWED_FIELDS = frozenset(
    {
        "decision_id",
        "snapshot_mode",
        "ticker",
        "decision_date",
        "period_id",
        "holding_horizon",
        "universe",
        "card_input_variant",
        "ml_signal",
        "technical_snapshot",
        "top_drivers",
        "news_evidence",
        "data_quality_flags",
        "guardrails",
        "provenance",
    }
)
INITIAL_TOP_DRIVER_FIELDS = frozenset({"feature", "value", "direction", "explanation"})
INITIAL_NEWS_FIELDS = frozenset(
    {
        "evidence_id",
        "published_at",
        "source",
        "title",
        "article_summary",
        "key_facts",
        "risk_flags",
        "event_type",
        "match_confidence",
        "evidence_span",
        "url",
        "content_hash",
        "extraction_status",
    }
)
INITIAL_KEY_FACT_FIELDS = frozenset({"fact_id", "fact", "evidence_quote", "fact_type", "direction", "confidence"})
INITIAL_ML_SIGNAL_FIELDS = frozenset(
    {"model_name", "pred_proba_up", "pred_label", "rank_in_period", "signal_class", "source_signal_class", "display_status"}
)
ARTIFACT_REFERENCE_FIELDS = frozenset(
    {"name", "path", "sha256", "zone", "record_count", "schema_version", "generated_at_utc", "provenance_status"}
)
INITIAL_GUARDRAIL_FIELDS = frozenset(
    {
        "full_text_excerpt_chars",
        "initial_prompt_safe",
        "news_cutoff",
        "news_evidence_excluded",
        "no_post_decision_data",
        "not_investment_advice",
    }
)
SELECT_ALLOWED_FIELDS = frozenset(
    {
        "decision_id",
        "ticker",
        "period_id",
        "decision_date",
        "display_status",
        "pred_proba_up",
        "rank_in_period",
        "data_quality",
        "monitoring_available",
        "review_available",
    }
)
DATA_QUALITY_FIELDS = frozenset(
    {"news_coverage", "ticker_matching_confidence", "full_text_coverage", "summary_coverage", "key_fact_coverage", "missing_fields"}
)
MONITOR_ALLOWED_FIELDS = frozenset(
    {
        "event_id",
        "news_id",
        "decision_id",
        "ticker",
        "decision_date",
        "event_date",
        "action",
        "reason",
        "source",
        "title",
        "event_type",
        "risk_flags",
        "match_confidence",
        "article_summary",
        "url",
        "content_hash",
        "consensus_join_status",
        "semantic_quality",
    }
)
SEMANTIC_QUALITY_FIELDS = frozenset(
    {
        "news_id",
        "ticker",
        "article_date",
        "consensus_method",
        "agreement_level",
        "analysis_eligible",
        "consensus_direction",
        "consensus_materiality",
        "consensus_event_type",
        "evidence_span",
        "disagreement_fields",
        "quality_flags",
        "requires_human_review",
        "review_flags",
        "artifact_schema_version",
    }
)
UPDATE_ALLOWED_FIELDS = frozenset(
    {"decision_id", "as_of", "initial_reference", "monitoring_events", "workflow_state", "proposed_analyst_questions", "persisted"}
)
UPDATE_INITIAL_REFERENCE_FIELDS = frozenset({"decision_date", "ticker"})
CARD_ALLOWED_FIELDS = frozenset(
    {
        "card_id",
        "decision_id",
        "card_type",
        "producer_run_id",
        "provider",
        "requested_model",
        "response_model",
        "vendor",
        "generated_at_utc",
        "prompt_sha256",
        "pack_sha256",
        "body_markdown",
    }
)
CARD_NEGATED_OUTCOME_ALLOWLIST = (
    re.compile(r"không (?:sử dụng|dùng|kết luận) outcome tương lai", re.IGNORECASE),
    re.compile(r"không có [^.\n]* sử dụng outcome tương lai", re.IGNORECASE),
    re.compile(
        r"không sử dụng (?:dự báo giá tuyệt đối, )?dữ liệu sau ngày quyết định hoặc outcome tương lai",
        re.IGNORECASE,
    ),
)
INITIAL_ZONE = "initial"
MONITOR_ZONE = "monitor"
UPDATE_ZONE = "update"
REVIEW_ZONE = "review"
EVALUATION_ZONE = "evaluation"

RESEARCH_DISCLAIMER = "Research prototype · Validated bundle has no live market data · External current market context is display-only · Not investment advice"
PSEUDO_LABEL_WARNING = "Model-derived pseudo-label; not human ground truth."
RUBRIC_WARNING = "Card-quality evaluation only; not investment performance, return, alpha, or causal evidence."


class PolicyViolation(ValueError):
    """Raised when a payload violates a trust-zone boundary."""


def parse_iso_date(value: Any) -> date:
    """Parse a date-like artifact value without accepting an empty value."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value.strip():
        raise PolicyViolation("Expected a non-empty ISO date")
    text = value.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:\d{2})?)?", text):
        raise PolicyViolation(f"Invalid ISO date: {value!r}")
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise PolicyViolation(f"Invalid ISO date: {value!r}") from exc


def find_forbidden_markers(value: Any, markers: Iterable[str] = INITIAL_FORBIDDEN_MARKERS, path: str = "$") -> list[str]:
    """Find forbidden field/value markers recursively in a JSON-compatible payload."""
    normalized_markers = tuple(marker.lower() for marker in markers)
    violations: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in normalized_markers):
                violations.append(f"{path}.{key}")
            violations.extend(find_forbidden_markers(nested, normalized_markers, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            violations.extend(find_forbidden_markers(nested, normalized_markers, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in normalized_markers):
            violations.append(path)
    return violations


def _reject_unknown_fields(actual: Iterable[str], allowed: frozenset[str], path: str) -> None:
    unknown = sorted(set(actual) - allowed)
    if unknown:
        raise PolicyViolation(f"Payload contains unknown fields at {path}: {', '.join(unknown)}")


def _require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PolicyViolation(f"{path} must be an object")
    return value


def _require_array(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise PolicyViolation(f"{path} must be an array")
    return value


def _find_runtime_forbidden_markers(value: Any, zone: str, path: str = "$") -> list[str]:
    """Scan runtime keys and display text, applying only documented path-specific exceptions."""
    violations: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            nested_path = f"{path}.{key}"
            if any(marker in str(key).lower() for marker in INITIAL_FORBIDDEN_MARKERS):
                violations.append(nested_path)
            violations.extend(_find_runtime_forbidden_markers(nested, zone, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            violations.extend(_find_runtime_forbidden_markers(nested, zone, f"{path}[{index}]"))
    elif isinstance(value, str):
        scanned = value
        if zone == "cards" and path.endswith(".body_markdown"):
            for allowed_pattern in CARD_NEGATED_OUTCOME_ALLOWLIST:
                scanned = allowed_pattern.sub("", scanned)
        if any(marker in scanned.lower() for marker in INITIAL_FORBIDDEN_MARKERS):
            violations.append(path)
    return violations


def _assert_runtime_markers_safe(payload: Any, zone: str) -> None:
    violations = _find_runtime_forbidden_markers(payload, zone)
    if violations:
        raise PolicyViolation(f"{zone} payload contains forbidden markers: {', '.join(violations[:5])}")


def _assert_data_quality(payload: Any, path: str) -> None:
    quality = _require_object(payload, path)
    _reject_unknown_fields(quality, DATA_QUALITY_FIELDS, path)


def _assert_semantic_quality(payload: Any, path: str) -> None:
    if payload is None:
        return
    semantic = _require_object(payload, path)
    _reject_unknown_fields(semantic, SEMANTIC_QUALITY_FIELDS, path)


def _assert_monitor_event(payload: Any, path: str) -> None:
    event = _require_object(payload, path)
    _reject_unknown_fields(event, MONITOR_ALLOWED_FIELDS, path)
    _assert_semantic_quality(event.get("semantic_quality"), f"{path}.semantic_quality")
    decision_date = parse_iso_date(event.get("decision_date"))
    event_date = parse_iso_date(event.get("event_date"))
    if event_date <= decision_date:
        raise PolicyViolation(f"{path}.event_date must be after decision_date")


def assert_initial_payload_safe(payload: dict[str, Any]) -> None:
    """Reject fields outside canonical initial schema and post-decision news."""
    _assert_runtime_markers_safe(payload, INITIAL_ZONE)
    _reject_unknown_fields(payload, INITIAL_ALLOWED_FIELDS, "$")

    ml_signal = _require_object(payload.get("ml_signal", {}), "$.ml_signal")
    _reject_unknown_fields(ml_signal, INITIAL_ML_SIGNAL_FIELDS, "$.ml_signal")
    technical_snapshot = _require_object(payload.get("technical_snapshot", {}), "$.technical_snapshot")
    _reject_unknown_fields(technical_snapshot, INITIAL_TECHNICAL_FEATURES, "$.technical_snapshot")

    for index, driver_value in enumerate(_require_array(payload.get("top_drivers", []), "$.top_drivers")):
        path = f"$.top_drivers[{index}]"
        driver = _require_object(driver_value, path)
        _reject_unknown_fields(driver, INITIAL_TOP_DRIVER_FIELDS, path)
        feature = driver.get("feature")
        if feature not in INITIAL_TECHNICAL_FEATURES:
            raise PolicyViolation(f"top_drivers[{index}].feature is not in model feature contract: {feature!r}")

    decision_date = parse_iso_date(payload.get("decision_date"))
    for index, evidence_value in enumerate(_require_array(payload.get("news_evidence", []), "$.news_evidence")):
        path = f"$.news_evidence[{index}]"
        evidence = _require_object(evidence_value, path)
        _reject_unknown_fields(evidence, INITIAL_NEWS_FIELDS, path)
        for fact_index, fact_value in enumerate(_require_array(evidence.get("key_facts", []), f"{path}.key_facts")):
            fact_path = f"{path}.key_facts[{fact_index}]"
            fact = _require_object(fact_value, fact_path)
            _reject_unknown_fields(fact, INITIAL_KEY_FACT_FIELDS, fact_path)
        published_at = parse_iso_date(evidence.get("published_at"))
        if published_at > decision_date:
            raise PolicyViolation(
                f"news_evidence[{index}].published_at {published_at.isoformat()} exceeds decision_date {decision_date.isoformat()}"
            )

    _assert_data_quality(payload.get("data_quality_flags", {}), "$.data_quality_flags")
    guardrails = _require_object(payload.get("guardrails", {}), "$.guardrails")
    _reject_unknown_fields(guardrails, INITIAL_GUARDRAIL_FIELDS, "$.guardrails")
    provenance = _require_object(payload.get("provenance", {}), "$.provenance")
    _reject_unknown_fields(provenance, ARTIFACT_REFERENCE_FIELDS, "$.provenance")


def assert_runtime_zone_safe(zone: str, payload: Any) -> None:
    """Validate every prompt/display-sensitive runtime zone recursively."""
    _assert_runtime_markers_safe(payload, zone)
    if zone == "initial":
        assert_initial_payload_safe(_require_object(payload, "$"))
        return
    if zone == "select":
        for index, row_value in enumerate(_require_array(payload, "$")):
            path = f"$[{index}]"
            row = _require_object(row_value, path)
            _reject_unknown_fields(row, SELECT_ALLOWED_FIELDS, path)
            _assert_data_quality(row.get("data_quality", {}), f"{path}.data_quality")
        return
    if zone == "monitor":
        for index, event in enumerate(_require_array(payload, "$")):
            _assert_monitor_event(event, f"$[{index}]")
        return
    if zone == "update":
        update = _require_object(payload, "$")
        _reject_unknown_fields(update, UPDATE_ALLOWED_FIELDS, "$")
        reference = _require_object(update.get("initial_reference", {}), "$.initial_reference")
        _reject_unknown_fields(reference, UPDATE_INITIAL_REFERENCE_FIELDS, "$.initial_reference")
        cutoff = parse_iso_date(update.get("as_of"))
        for index, event in enumerate(_require_array(update.get("monitoring_events", []), "$.monitoring_events")):
            path = f"$.monitoring_events[{index}]"
            _assert_monitor_event(event, path)
            if parse_iso_date(event.get("event_date")) > cutoff:
                raise PolicyViolation(f"{path}.event_date exceeds update as_of")
        return
    if zone == "cards":
        for index, card_value in enumerate(_require_array(payload, "$")):
            path = f"$[{index}]"
            card = _require_object(card_value, path)
            _reject_unknown_fields(card, CARD_ALLOWED_FIELDS, path)
        return
    raise PolicyViolation(f"No runtime leakage validator configured for zone: {zone}")


def validate_runtime_zones(zones: dict[str, list[Any]]) -> dict[str, Any]:
    """Run named zone checks and return evidence used by bundle validation report."""
    checks: list[dict[str, Any]] = []
    for zone in ("initial", "select", "monitor", "update", "cards"):
        payloads = zones.get(zone)
        if payloads is None:
            raise PolicyViolation(f"Missing required runtime validation zone: {zone}")
        for payload in payloads:
            assert_runtime_zone_safe(zone, payload)
        checks.append({"zone": zone, "payloads_checked": len(payloads), "passed": True})
    return {"checks": checks, "leakage_validation_passed": all(check["passed"] for check in checks)}


def filter_monitor_events(events: Iterable[dict[str, Any]], as_of: date | str) -> list[dict[str, Any]]:
    """Return historical monitoring events observable no later than `as_of`."""
    cutoff = parse_iso_date(as_of)
    filtered = [event for event in events if parse_iso_date(event.get("event_date")) <= cutoff]
    return sorted(filtered, key=lambda event: (str(event.get("event_date", "")), str(event.get("title", ""))), reverse=True)


def assert_review_payload(payload: dict[str, Any]) -> None:
    """Require review-only data to declare its post-hoc boundary."""
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict) or provenance.get("review_only") is not True:
        raise PolicyViolation("Review payload must declare provenance.review_only=true")


def display_signal_label(source_label: str | None) -> str:
    """Avoid trade-oriented language in analyst-facing UI."""
    if (source_label or "").strip().lower() == "buy candidate":
        return "Model candidate"
    return source_label or "Unavailable"
