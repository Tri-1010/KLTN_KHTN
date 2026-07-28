from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from scripts import monitor_news_events as monitoring


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    generated = tmp_path / "reports" / "decision_support" / "generated"
    generated.mkdir(parents=True)
    packs_path = generated / "evidence_packs_audit.json"
    packs_path.write_text(
        json.dumps([{"decision_id": "2025Q1_ABC_01", "ticker": "ABC", "decision_date": "2025-03-31"}]),
        encoding="utf-8",
    )
    news_path = tmp_path / "data" / "news" / "enriched" / "all_news_enriched.csv"
    news_path.parent.mkdir(parents=True)
    _write_csv(
        news_path,
        [
            {
                "ticker": "ABC",
                "date": "2025-04-01",
                "event_type_enriched": "governance",
                "risk_flags_json": "[]",
                "match_confidence": "exact",
                "source": "test",
                "title": "Included",
                "url": "https://example.test/included",
                "article_summary": "Included summary",
                "content_hash": "a" * 64,
            },
            {
                "ticker": "ABC",
                "date": "2025-04-03",
                "event_type_enriched": "governance",
                "risk_flags_json": "[]",
                "match_confidence": "exact",
                "source": "test",
                "title": "Future",
                "url": "https://example.test/future",
                "article_summary": "Future summary",
                "content_hash": "b" * 64,
            },
        ],
    )
    return packs_path, news_path


def test_build_monitoring_events_respects_explicit_as_of_date_and_emits_stable_news_id(tmp_path: Path):
    packs_path, news_path = _write_inputs(tmp_path)

    events, timeline, metadata = monitoring.build_monitoring_events(tmp_path, monitoring.date(2025, 4, 2))

    assert [event["title"] for event in events] == ["Included"]
    assert events[0]["news_id"] == monitoring.stable_news_id(
        {
            "ticker": "ABC",
            "date": "2025-04-01",
            "url": "https://example.test/included",
            "title": "Included",
        }
    )
    assert len(events[0]["news_id"]) == 16
    assert timeline["2025Q1_ABC_01"][0]["action"] == "Review Required"
    assert metadata["schema_version"] == "monitoring-manifest-v1"
    assert metadata["as_of_date"] == "2025-04-02"
    assert metadata["historical_replay"] is True
    assert metadata["input_hashes"] == {
        "reports/decision_support/generated/evidence_packs_audit.json": monitoring.sha256_file(packs_path),
        "data/news/enriched/all_news_enriched.csv": monitoring.sha256_file(news_path),
    }


def test_parse_args_requires_explicit_as_of_date():
    with pytest.raises(SystemExit):
        monitoring.parse_args([])

    args = monitoring.parse_args(["--as-of-date", "2026-07-28"])

    assert args.as_of_date == monitoring.date(2026, 7, 28)


@pytest.mark.parametrize("value", ["2026-7-28", "not-a-date", "2026-02-30"])
def test_parse_args_rejects_noncanonical_or_invalid_date(value: str):
    with pytest.raises(SystemExit):
        monitoring.parse_args(["--as-of-date", value])


def test_write_monitoring_outputs_writes_atomic_manifest_last(tmp_path: Path, monkeypatch):
    event = {
        "decision_id": "2025Q1_ABC_01",
        "news_id": "news-1",
        "ticker": "ABC",
        "decision_date": "2025-03-31",
        "event_date": "2025-04-01",
        "trigger_type": "news",
        "action": "Watch",
        "reason": "test",
        "source": "test",
        "title": "Test",
        "url": "https://example.test",
        "event_type": "general_news",
        "risk_flags": "",
        "match_confidence": "exact",
        "article_summary": "summary",
        "content_hash": "c" * 64,
    }
    metadata = {
        "schema_version": "monitoring-manifest-v1",
        "generated_at_utc": "2025-04-01T00:00:00+00:00",
        "as_of_date": "2025-04-01",
        "historical_replay": True,
        "packs_source": "packs.json",
        "news_source": "news.csv",
        "input_hashes": {"packs.json": "a" * 64, "news.csv": "b" * 64},
        "num_decisions": 1,
        "num_monitoring_events": 1,
    }
    replacements: list[str] = []
    original_replace = monitoring.os.replace

    def record_replace(source, destination):
        replacements.append(Path(destination).name)
        original_replace(source, destination)

    monkeypatch.setattr(monitoring.os, "replace", record_replace)

    outputs = monitoring.write_monitoring_outputs(
        tmp_path,
        [event],
        {event["decision_id"]: [event]},
        metadata,
    )

    assert outputs["events"].exists()
    assert replacements == ["monitoring_events.csv", "monitoring_timeline.json", "monitoring_manifest.json"]
    assert json.loads(outputs["metadata"].read_text(encoding="utf-8")) == metadata
    assert not list(outputs["metadata"].parent.glob("*.tmp"))
