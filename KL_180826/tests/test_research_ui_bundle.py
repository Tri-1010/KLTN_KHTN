from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_ui.policy import INITIAL_FORBIDDEN_MARKERS, PolicyViolation, find_forbidden_markers
from scripts import build_research_ui_bundle as bundle_builder
from research_ui.run_catalog import sha256_file
from scripts.build_research_ui_bundle import (
    build_bundle,
    build_monitor_event,
    canonical_content_hash_lookup,
    monitoring_horizon,
    semantic_lookup,
)


def _synthetic_monitoring_manifest(tmp_path: Path, as_of_date: str = "2026-07-28") -> Path:
    root = Path.cwd()
    timeline = json.loads(
        (root / "reports/decision_support/generated/monitoring_timeline.json").read_text(encoding="utf-8")
    )
    sources = [
        "reports/decision_support/generated/evidence_packs_audit.json",
        "data/news/enriched/all_news_enriched.csv",
    ]
    path = tmp_path / "synthetic_monitoring_manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "monitoring-manifest-v1",
                "generated_at_utc": "2026-07-28T00:00:00+00:00",
                "as_of_date": as_of_date,
                "historical_replay": True,
                "packs_source": sources[0],
                "news_source": sources[1],
                "input_hashes": {source: sha256_file(root / source) for source in sources},
                "num_decisions": 25,
                "num_monitoring_events": sum(len(events) for events in timeline.values()),
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_horizon_fixture(tmp_path: Path, as_of_date: str, event_count: int) -> tuple[dict, Path]:
    generated = tmp_path / "generated"
    generated.mkdir(exist_ok=True)
    timeline_path = generated / "monitoring_timeline.json"
    timeline_path.write_text("{}", encoding="utf-8")
    packs = tmp_path / "packs.json"
    news = tmp_path / "news.csv"
    packs.write_text("[]", encoding="utf-8")
    news.write_text("ticker,date\n", encoding="utf-8")
    manifest = generated / "monitoring_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "monitoring-manifest-v1",
                "generated_at_utc": "2026-07-28T00:00:00+00:00",
                "as_of_date": as_of_date,
                "historical_replay": True,
                "packs_source": "packs.json",
                "news_source": "news.csv",
                "input_hashes": {
                    "packs.json": sha256_file(packs),
                    "news.csv": sha256_file(news),
                },
                "num_decisions": 0,
                "num_monitoring_events": event_count,
            }
        ),
        encoding="utf-8",
    )
    return {"monitoring_timeline": {"path": "generated/monitoring_timeline.json"}}, manifest


def _build_test_bundle(output: Path):
    return build_bundle(
        output_dir=output,
        monitoring_manifest_path=_synthetic_monitoring_manifest(output.parent),
    )


def test_bundle_builds_physically_partitioned_artifacts(tmp_path: Path):
    result = _build_test_bundle(tmp_path)

    assert result["initial_records"] == 25
    assert result["review_records"] == 25
    assert result["evaluation_runs"]["common-local-judge-gemini-cards-2026-07"] == 75
    assert (tmp_path / "select.json").is_file()
    assert (tmp_path / "initial" / "2025Q1_SCR_01.json").is_file()
    assert (tmp_path / "monitor" / "2025Q1_SCR_01.json").is_file()
    assert (tmp_path / "update" / "2025Q1_SCR_01.json").is_file()
    assert (tmp_path / "review" / "2025Q1_SCR_01.json").is_file()

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    member_paths = {member["path"] for member in manifest["runtime_members"]}
    expected_paths = {
        path.relative_to(tmp_path).as_posix()
        for path in tmp_path.rglob("*.json")
        if path.name != "manifest.json"
    }
    assert member_paths == expected_paths
    assert all(len(member["sha256"]) == 64 for member in manifest["runtime_members"])
    assert manifest["monitor_as_of_date"]

    update = json.loads((tmp_path / "update" / "2025Q1_SCR_01.json").read_text(encoding="utf-8"))
    assert update["as_of"] == manifest["monitor_as_of_date"]


def test_monitoring_horizon_uses_producer_as_of_date_after_last_event(tmp_path: Path):
    artifacts, _ = _write_horizon_fixture(tmp_path, "2025-04-30", 1)
    timeline = {"D1": [{"event_date": "2025-04-01"}]}

    assert monitoring_horizon(tmp_path, artifacts, timeline).isoformat() == "2025-04-30"


def test_monitoring_horizon_fails_closed_without_producer_manifest(tmp_path: Path):
    generated = tmp_path / "generated"
    generated.mkdir()
    artifacts = {"monitoring_timeline": {"path": "generated/monitoring_timeline.json"}}

    with pytest.raises(ValueError, match="Missing authoritative monitoring producer manifest"):
        monitoring_horizon(tmp_path, artifacts, {})


def test_monitoring_horizon_rejects_count_mismatch_and_future_events(tmp_path: Path):
    artifacts, manifest = _write_horizon_fixture(tmp_path, "2025-04-30", 0)
    timeline = {"D1": [{"event_date": "2025-05-01"}]}

    with pytest.raises(ValueError, match="event count does not match"):
        monitoring_horizon(tmp_path, artifacts, timeline)

    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    metadata["num_monitoring_events"] = 1
    manifest.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(ValueError, match="events after producer as_of_date"):
        monitoring_horizon(tmp_path, artifacts, timeline)


def test_monitoring_horizon_rejects_source_hash_mismatch(tmp_path: Path):
    artifacts, manifest = _write_horizon_fixture(tmp_path, "2025-04-30", 0)
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    metadata["input_hashes"]["news.csv"] = "0" * 64
    manifest.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="input hash mismatch"):
        monitoring_horizon(tmp_path, artifacts, {})


def test_monitoring_horizon_rejects_catalog_date_and_count_mismatch(tmp_path: Path):
    artifacts, _ = _write_horizon_fixture(tmp_path, "2025-04-30", 0)
    artifacts["monitoring_manifest"] = {
        "path": "generated/monitoring_manifest.json",
        "expected_as_of_date": "2025-05-01",
        "expected_monitoring_events": 1,
    }

    with pytest.raises(ValueError, match="as_of_date does not match catalog"):
        monitoring_horizon(tmp_path, artifacts, {})

    artifacts["monitoring_manifest"]["expected_as_of_date"] = "2025-04-30"
    with pytest.raises(ValueError, match="event count does not match catalog"):
        monitoring_horizon(tmp_path, artifacts, {})


def test_monitoring_horizon_rejects_non_timestamp_generated_at(tmp_path: Path):
    artifacts, manifest = _write_horizon_fixture(tmp_path, "2025-04-30", 0)
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    metadata["generated_at_utc"] = "2026-07-28"
    manifest.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid date metadata"):
        monitoring_horizon(tmp_path, artifacts, {})


def _semantic_row(news_id: str) -> dict:
    return {
        "news_id": news_id,
        "ticker": "ABC",
        "article_date": "2025-04-01",
        "consensus_method": "unanimous",
        "agreement_level": "high",
        "analysis_eligible": True,
        "consensus_direction": "support",
        "consensus_materiality": "high",
        "consensus_event_type": "earnings",
        "requires_human_review": False,
        "artifact_schema_version": "pseudo_label_consensus_v2",
    }


def _monitor_event(**overrides) -> dict:
    return {
        "decision_id": "D1",
        "ticker": "ABC",
        "decision_date": "2025-03-31",
        "event_date": "2025-04-01",
        "action": "Watch",
        "reason": "test",
        "source": "test",
        "title": "Test",
        "content_hash": "h1",
        **overrides,
    }


def test_semantic_join_prefers_news_id_and_uses_only_unambiguous_hash_fallback():
    semantics = semantic_lookup([_semantic_row("n1"), _semantic_row("n2")])
    hash_lookup, ambiguous = canonical_content_hash_lookup(
        [
            {"content_hash": "h1", "news_id": "n1"},
            {"content_hash": "h2", "news_id": "n1"},
            {"content_hash": "h2", "news_id": "n2"},
            {"content_hash": "h3", "news_id": "n1"},
            {"content_hash": "h3", "news_id": "missing"},
        ],
        semantics,
    )

    direct = build_monitor_event(_monitor_event(news_id="n2"), semantics, hash_lookup, ambiguous)
    fallback = build_monitor_event(_monitor_event(), semantics, hash_lookup, ambiguous)
    ambiguous_event = build_monitor_event(_monitor_event(content_hash="h2"), semantics, hash_lookup, ambiguous)
    missing_semantic_collision = build_monitor_event(_monitor_event(content_hash="h3"), semantics, hash_lookup, ambiguous)

    assert direct.consensus_join_status == "joined"
    assert direct.semantic_quality.news_id == "n2"
    assert fallback.consensus_join_status == "joined"
    assert fallback.news_id == "n1"
    assert ambiguous_event.consensus_join_status == "ambiguous"
    assert ambiguous_event.semantic_quality is None
    assert missing_semantic_collision.consensus_join_status == "ambiguous"
    assert missing_semantic_collision.semantic_quality is None


def test_checked_in_monitoring_artifacts_have_expected_nonzero_semantic_joins(tmp_path: Path):
    result = _build_test_bundle(tmp_path)

    assert result["monitor_records"] == 3839
    assert result["semantic_joined_monitor_events"] == 13
    assert result["semantic_ambiguous_monitor_events"] == 0


def test_build_failure_preserves_previously_published_bundle(tmp_path: Path, monkeypatch):
    output = tmp_path / "current"
    output.mkdir()
    sentinel = output / "sentinel.txt"
    sentinel.write_text("keep", encoding="utf-8")
    manifest_path = _synthetic_monitoring_manifest(tmp_path)
    original_load_card_rows = bundle_builder.load_card_rows

    def leaking_cards(root, catalog):
        cards = original_load_card_rows(root, catalog)
        cards[0]["post_hoc_outcome"] = {"realized_return": 1.0}
        return cards

    monkeypatch.setattr(bundle_builder, "load_card_rows", leaking_cards)
    with pytest.raises(PolicyViolation, match="cards payload contains forbidden markers"):
        build_bundle(output_dir=output, monitoring_manifest_path=manifest_path)

    assert sentinel.read_text(encoding="utf-8") == "keep"
    assert not (output / "manifest.json").exists()


def test_initial_bundle_payloads_contain_no_review_or_future_markers(tmp_path: Path):
    _build_test_bundle(tmp_path)

    for path in (tmp_path / "initial").glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert find_forbidden_markers(payload, INITIAL_FORBIDDEN_MARKERS) == []


def test_review_bundle_is_separate_and_declares_review_only_boundary(tmp_path: Path):
    _build_test_bundle(tmp_path)

    review = json.loads((tmp_path / "review" / "2025Q1_SCR_01.json").read_text(encoding="utf-8"))
    initial = json.loads((tmp_path / "initial" / "2025Q1_SCR_01.json").read_text(encoding="utf-8"))

    assert review["provenance"]["review_only"] is True
    assert "post_hoc_outcome" in review
    assert "post_hoc_outcome" not in initial
    assert "outcome_for_review_only" not in initial


def test_evaluation_bundle_keeps_common_judge_as_separate_run(tmp_path: Path):
    _build_test_bundle(tmp_path)

    evaluations = json.loads((tmp_path / "evaluation.json").read_text(encoding="utf-8"))
    counts = {bundle["evaluation_run_id"]: bundle["card_count"] for bundle in evaluations}

    assert counts == {
        "gemini-full-2026-07": 75,
        "local-router-claude2-2026-07": 75,
        "common-local-judge-gemini-cards-2026-07": 75,
    }
