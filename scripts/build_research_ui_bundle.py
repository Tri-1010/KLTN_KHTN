"""Build a validated, physically partitioned artifact bundle for EvidenceTrace.

The browser-facing UI reads only the output bundle. Initial, monitoring, update,
review, semantic, evaluation, and provenance data are written to different files so
outcome data cannot be hidden merely by a frontend conditional.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from research_ui.contracts import (
        ArtifactReference,
        DataQuality,
        DatasetManifest,
        EvaluationBundle,
        EvaluationRecord,
        InitialDecisionDetail,
        MLSignal,
        MonitoringEvent,
        NewsEvidence,
        ReviewDetail,
        RuntimeMember,
        SelectCandidate,
        SemanticConsensusDetail,
        TechnicalDriver,
        UpdateDetail,
    )
    from research_ui.policy import (
        PSEUDO_LABEL_WARNING,
        RUBRIC_WARNING,
        assert_initial_payload_safe,
        assert_review_payload,
        display_signal_label,
        filter_monitor_events,
        parse_iso_date,
        validate_runtime_zones,
    )
    from research_ui.run_catalog import assert_catalog_valid, load_catalog, record_count, repo_root, sha256_file
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from scripts.research_ui.contracts import (  # type: ignore[no-redef]
        ArtifactReference,
        DataQuality,
        DatasetManifest,
        EvaluationBundle,
        EvaluationRecord,
        InitialDecisionDetail,
        MLSignal,
        MonitoringEvent,
        NewsEvidence,
        ReviewDetail,
        RuntimeMember,
        SelectCandidate,
        SemanticConsensusDetail,
        TechnicalDriver,
        UpdateDetail,
    )
    from scripts.research_ui.policy import (  # type: ignore[no-redef]
        PSEUDO_LABEL_WARNING,
        RUBRIC_WARNING,
        assert_initial_payload_safe,
        assert_review_payload,
        display_signal_label,
        filter_monitor_events,
        parse_iso_date,
        validate_runtime_zones,
    )
    from scripts.research_ui.run_catalog import assert_catalog_valid, load_catalog, record_count, repo_root, sha256_file  # type: ignore[no-redef]

BUNDLE_VERSION = "research-ui-v1"
MONITORING_MANIFEST_SCHEMA_VERSION = "monitoring-manifest-v1"
DEFAULT_OUTPUT = repo_root() / "ui_artifacts" / "current"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def runtime_members(output: Path) -> list[RuntimeMember]:
    """Hash every runtime JSON member except self-referential manifest."""
    return [
        RuntimeMember(path=path.relative_to(output).as_posix(), sha256=sha256_file(path))
        for path in sorted(output.rglob("*.json"))
        if path.name != "manifest.json"
    ]


def monitoring_horizon(
    root: Path,
    artifacts: dict[str, dict[str, Any]],
    timeline: dict[str, Any],
    producer_manifest_path: Path | None = None,
) -> date:
    """Validate authoritative producer manifest and return pinned horizon."""
    timeline_path = root / artifacts["monitoring_timeline"]["path"]
    manifest_reference = artifacts.get("monitoring_manifest") or {}
    default_manifest_path = root / str(manifest_reference.get("path") or timeline_path.with_name("monitoring_manifest.json"))
    producer_manifest = (producer_manifest_path or default_manifest_path).resolve()
    if not producer_manifest.is_file():
        raise ValueError(
            "Missing authoritative monitoring producer manifest: "
            f"{producer_manifest}. Regenerate monitoring artifacts with "
            "`python scripts/monitor_news_events.py --as-of-date YYYY-MM-DD` before building bundle."
        )
    metadata = read_json(producer_manifest)
    if not isinstance(metadata, dict):
        raise ValueError(f"Monitoring producer manifest must be a JSON object: {producer_manifest}")
    if metadata.get("schema_version") != MONITORING_MANIFEST_SCHEMA_VERSION:
        raise ValueError(f"Monitoring producer manifest has invalid schema_version: {producer_manifest}")
    try:
        horizon = parse_iso_date(metadata.get("as_of_date"))
        generated_at_text = str(metadata.get("generated_at_utc", ""))
        generated_at = datetime.fromisoformat(generated_at_text.replace("Z", "+00:00"))
        if "T" not in generated_at_text or generated_at.tzinfo is None:
            raise ValueError("generated_at_utc must be a timezone-aware timestamp")
    except ValueError as exc:
        raise ValueError(f"Monitoring producer manifest has invalid date metadata: {producer_manifest}") from exc

    expected_date = manifest_reference.get("expected_as_of_date")
    if expected_date and horizon != parse_iso_date(expected_date):
        raise ValueError(
            f"Monitoring producer manifest as_of_date does not match catalog: declared={horizon.isoformat()}, expected={expected_date}"
        )
    events = [event for decision_events in timeline.values() for event in decision_events]
    declared_count = metadata.get("num_monitoring_events")
    if not isinstance(declared_count, int) or declared_count != len(events):
        raise ValueError(
            "Monitoring producer manifest event count does not match timeline: "
            f"declared={declared_count!r}, actual={len(events)}"
        )
    expected_count = manifest_reference.get("expected_monitoring_events")
    if expected_count is not None and declared_count != expected_count:
        raise ValueError(
            f"Monitoring producer manifest event count does not match catalog: declared={declared_count}, expected={expected_count}"
        )

    input_hashes = metadata.get("input_hashes")
    if not isinstance(input_hashes, dict) or not input_hashes:
        raise ValueError(f"Monitoring producer manifest has no input_hashes: {producer_manifest}")
    for source_field in ("packs_source", "news_source"):
        relative_path = metadata.get(source_field)
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError(f"Monitoring producer manifest has invalid {source_field}: {producer_manifest}")
        source_path = (root / relative_path).resolve()
        try:
            source_path.relative_to(root.resolve())
        except ValueError as exc:
            raise ValueError(f"Monitoring producer manifest {source_field} escapes repository root") from exc
        if not source_path.is_file() or input_hashes.get(relative_path) != sha256_file(source_path):
            raise ValueError(f"Monitoring producer manifest input hash mismatch: {relative_path}")

    future_paths = [
        f"{decision_id}[{index}]"
        for decision_id, decision_events in timeline.items()
        for index, event in enumerate(decision_events)
        if parse_iso_date(event.get("event_date")) > horizon
    ]
    if future_paths:
        raise ValueError(
            f"Monitoring timeline contains events after producer as_of_date {horizon.isoformat()}: "
            + ", ".join(future_paths[:5])
        )
    return horizon


def artifact_by_name(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["name"]): item for item in catalog["artifacts"]}


def artifact_reference(item: dict[str, Any], root: Path) -> ArtifactReference:
    path = root / item["path"]
    return ArtifactReference(
        name=item["name"],
        path=item["path"],
        sha256=sha256_file(path),
        zone=item["zone"],
        record_count=record_count(path),
        schema_version=item.get("schema_version"),
        provenance_status=item.get("provenance_status"),
    )


def normalize_quality(raw: dict[str, Any]) -> DataQuality:
    return DataQuality(
        news_coverage=raw.get("news_coverage"),
        ticker_matching_confidence=raw.get("ticker_matching_confidence"),
        full_text_coverage=raw.get("full_text_coverage"),
        summary_coverage=raw.get("summary_coverage"),
        key_fact_coverage=raw.get("key_fact_coverage"),
        missing_fields=list(raw.get("missing_fields") or []),
    )


def normalize_news(raw: dict[str, Any]) -> NewsEvidence:
    return NewsEvidence(
        evidence_id=str(raw["evidence_id"]),
        published_at=str(raw["published_at"]),
        source=str(raw.get("source") or "unknown"),
        title=str(raw.get("title") or "Untitled evidence"),
        article_summary=raw.get("article_summary") or raw.get("summary"),
        key_facts=list(raw.get("key_facts") or []),
        risk_flags=[str(flag) for flag in raw.get("risk_flags") or []],
        event_type=raw.get("event_type"),
        match_confidence=raw.get("match_confidence"),
        evidence_span=raw.get("full_text_excerpt"),
        url=raw.get("url") or None,
        content_hash=raw.get("content_hash") or None,
        extraction_status=raw.get("extraction_status") or None,
    )


def build_initial_detail(pack: dict[str, Any], mode: str, provenance: ArtifactReference) -> InitialDecisionDetail:
    if mode == "ml_only":
        news = []
    else:
        news = [normalize_news(item) for item in pack.get("news_evidence", [])]
    source_signal = pack["ml_signal"]
    payload_for_policy = dict(pack)
    payload_for_policy["ml_signal"] = {
        "model_name": str(source_signal.get("model_name") or "Unavailable"),
        "pred_proba_up": float(source_signal["pred_proba_up"]),
        "pred_label": int(source_signal["pred_label"]),
        "rank_in_period": int(source_signal["rank_in_period"]),
        "source_signal_class": str(source_signal.get("signal_class") or "Unavailable"),
        "display_status": display_signal_label(source_signal.get("signal_class")),
    }
    payload_for_policy["news_evidence"] = [item.model_dump(mode="json") for item in news]
    payload_for_policy["data_quality_flags"] = normalize_quality(pack.get("data_quality_flags") or {}).model_dump(mode="json")
    payload_for_policy["provenance"] = provenance.model_dump(mode="json")
    assert_initial_payload_safe(payload_for_policy)
    detail = InitialDecisionDetail(
        decision_id=str(pack["decision_id"]),
        snapshot_mode=mode,
        ticker=str(pack["ticker"]),
        decision_date=str(pack["decision_date"]),
        period_id=str(pack["period_id"]),
        holding_horizon=str(pack.get("holding_horizon") or "Unavailable"),
        ml_signal=MLSignal(
            model_name=str(source_signal.get("model_name") or "Unavailable"),
            pred_proba_up=float(source_signal["pred_proba_up"]),
            pred_label=int(source_signal["pred_label"]),
            rank_in_period=int(source_signal["rank_in_period"]),
            source_signal_class=str(source_signal.get("signal_class") or "Unavailable"),
            display_status=display_signal_label(source_signal.get("signal_class")),
        ),
        technical_snapshot={str(key): value for key, value in (pack.get("technical_snapshot") or {}).items()},
        top_drivers=[TechnicalDriver(**driver) for driver in pack.get("top_drivers", [])],
        news_evidence=news,
        data_quality_flags=normalize_quality(pack.get("data_quality_flags") or {}),
        guardrails=dict(pack.get("guardrails") or {}),
        provenance=provenance,
    )
    assert_initial_payload_safe(detail.model_dump(mode="json"))
    return detail


def semantic_lookup(rows: list[dict[str, Any]]) -> dict[str, SemanticConsensusDetail]:
    """Index semantic consensus by stable canonical news ID."""
    result: dict[str, SemanticConsensusDetail] = {}
    for row in rows:
        result[str(row["news_id"])] = SemanticConsensusDetail(
            news_id=str(row["news_id"]),
            ticker=str(row.get("ticker") or "UNKNOWN"),
            article_date=str(row["article_date"]),
            consensus_method=str(row["consensus_method"]),
            agreement_level=str(row["agreement_level"]),
            analysis_eligible=bool(row["analysis_eligible"]),
            consensus_direction=str(row["consensus_direction"]),
            consensus_materiality=str(row["consensus_materiality"]),
            consensus_event_type=str(row["consensus_event_type"]),
            evidence_span=row.get("evidence_span"),
            disagreement_fields=list(row.get("disagreement_fields") or []),
            quality_flags=list(row.get("quality_flags") or []),
            requires_human_review=bool(row["requires_human_review"]),
            review_flags=list(row.get("review_flags") or []),
            artifact_schema_version=str(row["artifact_schema_version"]),
        )
    return result


def canonical_content_hash_lookup(
    rows: list[dict[str, Any]],
    semantic_by_news_id: dict[str, SemanticConsensusDetail],
) -> tuple[dict[str, str], set[str]]:
    """Return only canonical hash mappings that resolve to one semantic news ID."""
    candidates: dict[str, set[str]] = {}
    for row in rows:
        content_hash = str(row.get("content_hash") or "").strip()
        news_id = str(row.get("news_id") or "").strip()
        if content_hash and news_id:
            candidates.setdefault(content_hash, set()).add(news_id)
    unambiguous = {
        content_hash: next(iter(news_ids))
        for content_hash, news_ids in candidates.items()
        if len(news_ids) == 1 and next(iter(news_ids)) in semantic_by_news_id
    }
    ambiguous = {content_hash for content_hash, news_ids in candidates.items() if len(news_ids) > 1}
    return unambiguous, ambiguous


def split_csv_flags(value: str | None) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def build_monitor_event(
    raw: dict[str, Any],
    semantic_by_news_id: dict[str, SemanticConsensusDetail],
    news_id_by_content_hash: dict[str, str] | None = None,
    ambiguous_content_hashes: set[str] | None = None,
) -> MonitoringEvent:
    """Join by stable ID, then by validated unambiguous canonical content hash."""
    stable_news_id = str(raw.get("news_id") or "").strip()
    content_hash = str(raw.get("content_hash") or "").strip()
    semantic = semantic_by_news_id.get(stable_news_id) if stable_news_id else None
    resolved_news_id = stable_news_id if semantic else ""
    join_status = "joined" if semantic else "not_found"
    if semantic is None and content_hash and content_hash in (ambiguous_content_hashes or set()):
        join_status = "ambiguous"
    elif semantic is None and content_hash:
        resolved_news_id = (news_id_by_content_hash or {}).get(content_hash, "")
        semantic = semantic_by_news_id.get(resolved_news_id) if resolved_news_id else None
        if semantic is not None:
            join_status = "joined"
    return MonitoringEvent(
        event_id=str(content_hash or _stable_event_id(raw)),
        news_id=resolved_news_id or None,
        decision_id=str(raw["decision_id"]),
        ticker=str(raw["ticker"]),
        decision_date=str(raw["decision_date"]),
        event_date=str(raw["event_date"]),
        action=str(raw["action"]),
        reason=str(raw["reason"]),
        source=str(raw.get("source") or "unknown"),
        title=str(raw.get("title") or "Untitled event"),
        event_type=raw.get("event_type") or None,
        risk_flags=split_csv_flags(raw.get("risk_flags")),
        match_confidence=raw.get("match_confidence") or None,
        article_summary=raw.get("article_summary") or None,
        url=raw.get("url") or None,
        content_hash=content_hash or None,
        consensus_join_status=join_status,
        semantic_quality=semantic,
    )


def _stable_event_id(raw: dict[str, Any]) -> str:
    value = "|".join(str(raw.get(key, "")) for key in ("decision_id", "event_date", "url", "title"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_review_detail(raw: dict[str, Any]) -> ReviewDetail:
    detail = ReviewDetail(**raw)
    assert_review_payload(detail.model_dump(mode="json"))
    return detail


def load_card_rows(root: Path, catalog: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    artifacts = artifact_by_name(catalog)
    rule_path = root / artifacts["rule_based_cards"]["path"]
    rows.extend(read_json(rule_path))
    for run in catalog["runs"]:
        for variant, source in (run.get("cards") or {}).items():
            for raw in read_jsonl(root / source["path"]):
                rows.append(
                    {
                        "card_id": f"{run['run_id']}:{raw['card_type']}:{raw['decision_id']}",
                        "decision_id": raw["decision_id"],
                        "card_type": raw["card_type"],
                        "producer_run_id": run["run_id"],
                        "provider": raw.get("provider") or run.get("producer", {}).get("provider") or run.get("producer", {}).get("request_provider"),
                        "requested_model": raw.get("requested_model") or run.get("producer", {}).get("requested_model"),
                        "response_model": raw.get("response_model") or run.get("producer", {}).get("response_model"),
                        "vendor": run.get("producer", {}).get("vendor"),
                        "generated_at_utc": raw.get("generated_at_utc"),
                        "prompt_sha256": raw.get("prompt_sha256"),
                        "pack_sha256": raw.get("pack_sha256"),
                        "body_markdown": raw["card_markdown"],
                    }
                )
    return rows


def load_evaluation(root: Path, catalog: dict[str, Any], source_refs: dict[str, ArtifactReference]) -> list[EvaluationBundle]:
    bundles: list[EvaluationBundle] = []
    for run in catalog["runs"]:
        rubric = run.get("rubric")
        if not isinstance(rubric, dict):
            continue
        run_id = str(run["run_id"])
        records: list[EvaluationRecord] = []
        for raw in read_csv(root / rubric["path"]):
            records.append(
                EvaluationRecord(
                    card_id=f"{run_id}:{raw['card_type']}:{raw['decision_id']}",
                    decision_id=raw["decision_id"],
                    card_type=raw["card_type"],
                    evaluation_run_id=run_id,
                    judge_provider=str(rubric.get("judge_provider") or run.get("producer", {}).get("provider") or "unknown"),
                    judge_model=rubric.get("judge_model") or rubric.get("judge_response_model"),
                    faithfulness=int(raw["faithfulness"]),
                    hallucination_control=int(raw["hallucination_control"]),
                    ml_explanation=int(raw["ml_explanation"]),
                    risk_awareness=int(raw["risk_awareness"]),
                    monitoring_usefulness=int(raw["monitoring_usefulness"]),
                    clarity_usefulness=int(raw["clarity_usefulness"]),
                    overall=int(raw["overall"]),
                    major_issue=raw.get("major_issue") or None,
                    major_hallucination_count=int(raw.get("major_hallucination_count") or 0),
                    missing_evidence_ref_count=int(raw.get("missing_evidence_ref_count") or 0),
                )
            )
        provenance = ArtifactReference(
            name=f"{run_id}:rubric",
            path=rubric["path"],
            sha256=sha256_file(root / rubric["path"]),
            zone="evaluation",
            record_count=len(records),
            schema_version=str(rubric.get("rubric_version") or "decision-card-rubric-v1"),
        )
        bundles.append(
            EvaluationBundle(
                evaluation_run_id=run_id,
                card_count=len(records),
                rubric_warning=RUBRIC_WARNING,
                records=records,
                provenance=provenance,
            )
        )
    return bundles


def _build_bundle_contents(
    catalog_path: Path | None,
    output: Path,
    monitoring_manifest_path: Path | None = None,
) -> dict[str, Any]:
    root = repo_root()
    catalog = load_catalog(catalog_path)
    assert_catalog_valid(catalog, root)
    artifacts = artifact_by_name(catalog)
    output.mkdir(parents=True, exist_ok=True)

    refs = {name: artifact_reference(item, root) for name, item in artifacts.items() if (root / item["path"]).is_file()}
    full_packs = read_json(root / artifacts["initial_evidence"]["path"])
    ml_only_packs = read_json(root / artifacts["ml_only_evidence"]["path"])
    full_by_id = {pack["decision_id"]: pack for pack in full_packs}
    ml_by_id = {pack["decision_id"]: pack for pack in ml_only_packs}
    if set(full_by_id) != set(ml_by_id):
        raise ValueError("Initial full-evidence and ML-only decision IDs differ")

    select_rows: list[dict[str, Any]] = []
    initial_payloads: list[dict[str, Any]] = []
    monitor_payloads: list[list[dict[str, Any]]] = []
    update_payloads: list[dict[str, Any]] = []
    for decision_id in sorted(full_by_id):
        detail = build_initial_detail(full_by_id[decision_id], "full_evidence", refs["initial_evidence"])
        initial_payloads.append(detail.model_dump(mode="json"))
        select_rows.append(
            SelectCandidate(
                decision_id=detail.decision_id,
                ticker=detail.ticker,
                period_id=detail.period_id,
                decision_date=detail.decision_date,
                display_status=detail.ml_signal.display_status,
                pred_proba_up=detail.ml_signal.pred_proba_up,
                rank_in_period=detail.ml_signal.rank_in_period,
                data_quality=detail.data_quality_flags,
                monitoring_available=True,
                review_available=True,
            ).model_dump(mode="json")
        )
        write_json(output / "initial" / f"{decision_id}.json", detail.model_dump(mode="json"))
        ml_detail = build_initial_detail(ml_by_id[decision_id], "ml_only", refs["ml_only_evidence"])
        initial_payloads.append(ml_detail.model_dump(mode="json"))
        write_json(output / "initial_ml_only" / f"{decision_id}.json", ml_detail.model_dump(mode="json"))
    write_json(output / "select.json", select_rows)

    consensus_rows = read_jsonl(root / artifacts["semantic_consensus"]["path"])
    semantic_by_news_id = semantic_lookup(consensus_rows)
    canonical_rows = read_csv(root / artifacts["semantic_canonical_mapping"]["path"])
    news_id_by_content_hash, ambiguous_content_hashes = canonical_content_hash_lookup(
        canonical_rows,
        semantic_by_news_id,
    )
    for news_id, semantic in semantic_by_news_id.items():
        write_json(output / "semantic" / f"{news_id}.json", {"warning": PSEUDO_LABEL_WARNING, "record": semantic.model_dump(mode="json")})

    timeline = read_json(root / artifacts["monitoring_timeline"]["path"])
    monitor_as_of = monitoring_horizon(root, artifacts, timeline, monitoring_manifest_path)
    for decision_id in sorted(full_by_id):
        events = [
            build_monitor_event(raw, semantic_by_news_id, news_id_by_content_hash, ambiguous_content_hashes)
            for raw in timeline.get(decision_id, [])
        ]
        event_payloads = [event.model_dump(mode="json") for event in events]
        monitor_payloads.append(event_payloads)
        write_json(output / "monitor" / f"{decision_id}.json", event_payloads)
        default_as_of = max(monitor_as_of, parse_iso_date(full_by_id[decision_id]["decision_date"]))
        filtered = filter_monitor_events(event_payloads, default_as_of)
        state = "Review Required" if any(event["action"] == "Review Required" for event in filtered) else "Watch" if filtered else "Initial"
        update = UpdateDetail(
            decision_id=decision_id,
            as_of=default_as_of.isoformat(),
            initial_reference={"decision_date": full_by_id[decision_id]["decision_date"], "ticker": full_by_id[decision_id]["ticker"]},
            monitoring_events=[MonitoringEvent(**event) for event in filtered],
            workflow_state=state,
            proposed_analyst_questions=[
                "Evidence nào cần kiểm tra thủ công trước khi thay đổi trạng thái?",
                "Trigger nào đến từ rule và trigger nào có evidence trực tiếp?",
            ],
        )
        update_payload = update.model_dump(mode="json")
        update_payloads.append(update_payload)
        write_json(output / "update" / f"{decision_id}.json", update_payload)

    review_rows = read_json(root / artifacts["decision_outcome_reviews"]["path"])
    for raw in review_rows:
        detail = build_review_detail(raw)
        write_json(output / "review" / f"{detail.decision_id}.json", detail.model_dump(mode="json"))

    card_rows = load_card_rows(root, catalog)
    write_json(output / "cards.json", card_rows)
    leakage_validation = validate_runtime_zones(
        {
            "initial": initial_payloads,
            "select": [select_rows],
            "monitor": monitor_payloads,
            "update": update_payloads,
            "cards": [card_rows],
        }
    )
    leakage_validation_passed = leakage_validation["leakage_validation_passed"] is True
    if not leakage_validation_passed:
        raise ValueError("Runtime leakage validation did not pass")
    evaluation = load_evaluation(root, catalog, refs)
    write_json(output / "evaluation.json", [bundle.model_dump(mode="json") for bundle in evaluation])
    write_json(output / "provenance.json", {"catalog": catalog, "source_artifacts": [ref.model_dump(mode="json") for ref in refs.values()]})

    joined_events = sum(
        event.get("consensus_join_status") == "joined"
        for decision_events in monitor_payloads
        for event in decision_events
    )
    ambiguous_events = sum(
        event.get("consensus_join_status") == "ambiguous"
        for decision_events in monitor_payloads
        for event in decision_events
    )
    validation = {
        "bundle_version": BUNDLE_VERSION,
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "initial_records": len(full_by_id),
        "monitor_records": sum(len(events) for events in timeline.values()),
        "review_records": len(review_rows),
        "semantic_records": len(semantic_by_news_id),
        "semantic_joined_monitor_events": joined_events,
        "semantic_ambiguous_monitor_events": ambiguous_events,
        "evaluation_runs": {bundle.evaluation_run_id: bundle.card_count for bundle in evaluation},
        "semantic_join_status": "stable news_id first; unambiguous canonical content_hash fallback; title-only joins forbidden",
        "leakage_validation_checks": leakage_validation["checks"],
        "leakage_validation_passed": leakage_validation_passed,
    }
    write_json(output / "bundle_validation.json", validation)
    manifest = DatasetManifest(
        dataset_id=str(catalog["dataset_id"]),
        bundle_version=BUNDLE_VERSION,
        built_at_utc=datetime.now(timezone.utc),
        source_artifacts=list(refs.values()),
        runtime_members=runtime_members(output),
        monitor_as_of_date=monitor_as_of,
        leakage_validation_passed=leakage_validation_passed,
        validation_report_path="bundle_validation.json",
    )
    write_json(output / "manifest.json", manifest.model_dump(mode="json"))
    return validation


def build_bundle(
    catalog_path: Path | None = None,
    output_dir: Path | None = None,
    monitoring_manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Build and validate in staging, then publish atomically within output parent."""
    output = (output_dir or DEFAULT_OUTPUT).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent))
    backup = output.with_name(f".{output.name}.previous")
    try:
        validation = _build_bundle_contents(catalog_path, staging, monitoring_manifest_path)
        if backup.exists():
            shutil.rmtree(backup)
        if output.exists():
            output.replace(backup)
        try:
            staging.replace(output)
        except Exception:
            if backup.exists() and not output.exists():
                backup.replace(output)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return validation
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a validated EvidenceTrace UI artifact bundle.")
    parser.add_argument("--catalog", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--monitoring-manifest",
        type=Path,
        default=None,
        help="Authoritative monitoring producer manifest. Defaults beside monitoring_timeline.json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            build_bundle(args.catalog, args.output_dir, args.monitoring_manifest),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
