from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import pytest

from research_ui.repository import BundleRepository, BundleRepositoryError, open_bundle
from research_ui.run_catalog import sha256_file
from scripts.build_research_ui_bundle import build_bundle


def _build_test_bundle(output: Path):
    root = Path.cwd()
    timeline = json.loads(
        (root / "reports/decision_support/generated/monitoring_timeline.json").read_text(encoding="utf-8")
    )
    sources = [
        "reports/decision_support/generated/evidence_packs_audit.json",
        "data/news/enriched/all_news_enriched.csv",
    ]
    manifest_path = output.parent / "synthetic_monitoring_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "monitoring-manifest-v1",
                "generated_at_utc": "2026-07-28T00:00:00+00:00",
                "as_of_date": "2026-07-28",
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
    return build_bundle(output_dir=output, monitoring_manifest_path=manifest_path)


def test_repository_reads_only_partitioned_bundle(tmp_path: Path):
    _build_test_bundle(tmp_path)
    repository = BundleRepository(tmp_path)

    detail = repository.initial("2025Q1_SCR_01")
    review = repository.review("2025Q1_SCR_01")

    assert detail["snapshot_mode"] == "full_evidence"
    assert "post_hoc_outcome" not in detail
    assert review["provenance"]["review_only"] is True


def test_repository_monitor_honors_as_of_filter(tmp_path: Path):
    _build_test_bundle(tmp_path)
    repository = BundleRepository(tmp_path)
    events = repository.monitor("2025Q1_SCR_01", date(2025, 4, 2))

    assert all(event["event_date"] <= "2025-04-02" for event in events)


def test_monitor_bounds_reach_manifest_as_of_when_no_event_occurs_on_horizon(tmp_path: Path):
    _build_test_bundle(tmp_path)
    events = json.loads((tmp_path / "monitor" / "2025Q1_SCR_01.json").read_text(encoding="utf-8"))
    last_event = max(event["event_date"] for event in events)
    repository = BundleRepository(tmp_path)

    lower, upper = repository.monitor_date_bounds("2025Q1_SCR_01")

    assert lower == date(2025, 3, 31)
    assert last_event < upper.isoformat()
    assert upper == date(2026, 7, 28)


def test_repository_fails_closed_when_monitor_horizon_missing(tmp_path: Path):
    _build_test_bundle(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["monitor_as_of_date"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(BundleRepositoryError, match="manifest violates validated contract"):
        BundleRepository(tmp_path)


def test_open_bundle_cache_invalidates_when_manifest_is_atomically_replaced(tmp_path: Path):
    _build_test_bundle(tmp_path)
    open_bundle.cache_clear()

    first = open_bundle(str(tmp_path))
    assert open_bundle(str(tmp_path.resolve())) is first

    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["built_at_utc"] = "2026-07-28T12:34:56Z"
    replacement = tmp_path / ".manifest.replacement.json"
    replacement.write_text(json.dumps(manifest), encoding="utf-8")
    replacement.replace(manifest_path)

    second = open_bundle(str(tmp_path))

    assert second is not first
    assert second.manifest["built_at_utc"] == "2026-07-28T12:34:56Z"


def test_repository_fails_closed_when_runtime_member_is_tampered(tmp_path: Path):
    _build_test_bundle(tmp_path)
    select_path = tmp_path / "select.json"
    select_path.write_text(select_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    repository = BundleRepository(tmp_path)

    with pytest.raises(BundleRepositoryError, match="integrity mismatch"):
        repository.candidates()


def test_repository_fails_closed_when_runtime_member_missing_from_manifest(tmp_path: Path):
    _build_test_bundle(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["runtime_members"] = [member for member in manifest["runtime_members"] if member["path"] != "select.json"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    repository = BundleRepository(tmp_path)

    with pytest.raises(BundleRepositoryError, match="not integrity-declared"):
        repository.candidates()


def test_repository_overview_and_presets_use_safe_zones(tmp_path: Path):
    _build_test_bundle(tmp_path)
    repository = BundleRepository(tmp_path)

    overview = repository.overview()
    presets = repository.demo_presets()

    assert overview["record_count"] == 25
    assert "outcome" not in str(overview).lower()
    assert presets
    assert {item["selection_inputs"] for item in presets} == {"select, monitor"}
    assert all(item["decision_id"] in {row["decision_id"] for row in repository.candidates()} for item in presets)
