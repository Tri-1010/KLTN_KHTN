"""Generate deterministic news-monitoring events for decision-support records.

Reads generated evidence packs and local enriched news only. Callers must supply an
explicit ``--as-of-date`` so every producer run has an honest, reproducible horizon.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
MONITORING_MANIFEST_SCHEMA_VERSION = "monitoring-manifest-v1"

RISK_EVENT_TYPES = {"debt_risk", "legal_risk", "governance"}
RISK_FLAGS = {"debt_risk", "legal_risk", "earnings_warning", "governance", "capital_dilution", "audit_issue"}
WATCH_EVENT_TYPES = {"capital", "dividend", "earnings", "debt_risk", "legal_risk", "governance"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_json_list(value: str) -> list[Any]:
    if not value or not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError):
        return []


def parse_date(value: str | date | None) -> date | None:
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None


def explicit_iso_date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an ISO date in YYYY-MM-DD format") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("must be an ISO date in YYYY-MM-DD format")
    return parsed


def _normalized(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def stable_news_id(row: dict[str, Any]) -> str:
    """Match semantic annotation canonical ID policy without importing LLM tooling."""
    parts = [
        _normalized(row.get("ticker")).upper(),
        _normalized(row.get("date") or row.get("article_date") or row.get("published_at"))[:10],
        _normalized(row.get("url")).lower(),
        _normalized(row.get("title")).lower(),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def event_types(row: dict[str, str]) -> set[str]:
    value = row.get("event_type_enriched") or row.get("event_type") or ""
    return {part.strip() for part in value.split(",") if part.strip()}


def risk_flags(row: dict[str, str]) -> set[str]:
    parsed = parse_json_list(row.get("risk_flags_json", ""))
    return {str(item) for item in parsed if str(item)}


def classify_action(types: set[str], flags: set[str], match_confidence: str) -> tuple[str, str]:
    risk_hits = sorted((types & RISK_EVENT_TYPES) | (flags & RISK_FLAGS))
    if risk_hits:
        return "Review Required", "risk flags: " + ", ".join(risk_hits)
    if types & WATCH_EVENT_TYPES:
        return "Watch", "event type: " + ", ".join(sorted(types & WATCH_EVENT_TYPES))
    if match_confidence in {"partial", "none", ""}:
        return "Watch", "weak ticker matching confidence"
    return "Keep", "no material risk trigger"


def generated_paths(root: Path, output_dir: Path | None = None) -> dict[str, Path]:
    generated = output_dir or (root / "reports" / "decision_support" / "generated")
    return {
        "generated": generated,
        "audit_packs": generated / "evidence_packs_audit.json",
        "legacy_packs": generated / "evidence_packs.json",
        "enriched_news": root / "data" / "news" / "enriched" / "all_news_enriched.csv",
        "matched_news": root / "data" / "news" / "matched" / "all_news_matched.csv",
        "events": generated / "monitoring_events.csv",
        "timeline": generated / "monitoring_timeline.json",
        "metadata": generated / "monitoring_manifest.json",
    }


def _source_identity(root: Path, path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def build_monitoring_events(
    root: Path,
    as_of_date: date,
    output_dir: Path | None = None,
) -> tuple[list[dict[str, str]], dict[str, list[dict[str, str]]], dict[str, Any]]:
    """Build monitoring records through supplied historical cutoff from local files."""
    paths = generated_paths(root, output_dir)
    packs_path = paths["audit_packs"] if paths["audit_packs"].exists() else paths["legacy_packs"]
    if not packs_path.exists():
        raise FileNotFoundError(f"Missing evidence packs: {packs_path}")
    news_path = paths["enriched_news"] if paths["enriched_news"].exists() else paths["matched_news"]
    if not news_path.exists():
        raise FileNotFoundError(f"Missing news data: {news_path}")

    packs = json.loads(packs_path.read_text(encoding="utf-8"))
    news_by_ticker: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(news_path):
        news_by_ticker.setdefault(row.get("ticker", ""), []).append(row)

    events: list[dict[str, str]] = []
    timeline: dict[str, list[dict[str, str]]] = {}
    for pack in packs:
        decision_id = str(pack["decision_id"])
        ticker = str(pack["ticker"])
        decision_date = parse_date(pack.get("decision_date"))
        if decision_date is None:
            continue
        for row in news_by_ticker.get(ticker, []):
            event_date = parse_date(row.get("date"))
            if event_date is None or not (decision_date < event_date <= as_of_date):
                continue
            types = event_types(row)
            flags = risk_flags(row)
            action, reason = classify_action(types, flags, row.get("match_confidence", ""))
            if action == "Keep":
                continue
            event = {
                "decision_id": decision_id,
                "news_id": stable_news_id(row),
                "ticker": ticker,
                "decision_date": decision_date.isoformat(),
                "event_date": event_date.isoformat(),
                "trigger_type": "news",
                "action": action,
                "reason": reason,
                "source": row.get("source", ""),
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "event_type": ",".join(sorted(types)) or "general_news",
                "risk_flags": ",".join(sorted(flags)),
                "match_confidence": row.get("match_confidence", ""),
                "article_summary": row.get("article_summary", row.get("description", "")),
                "content_hash": row.get("content_hash", ""),
            }
            events.append(event)
            timeline.setdefault(decision_id, []).append(event)

    events.sort(key=lambda event: (event["decision_id"], event["event_date"], event["title"]))
    for decision_id, decision_events in timeline.items():
        timeline[decision_id] = sorted(
            decision_events,
            key=lambda event: (event["event_date"], event["title"]),
            reverse=True,
        )

    packs_source = _source_identity(root, packs_path)
    news_source = _source_identity(root, news_path)
    metadata = {
        "schema_version": MONITORING_MANIFEST_SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "as_of_date": as_of_date.isoformat(),
        "historical_replay": True,
        "packs_source": packs_source,
        "news_source": news_source,
        "input_hashes": {
            packs_source: sha256_file(packs_path),
            news_source: sha256_file(news_path),
        },
        "num_decisions": len(packs),
        "num_monitoring_events": len(events),
    }
    return events, timeline, metadata


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_events(path: Path, events: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_monitoring_outputs(
    root: Path,
    events: list[dict[str, str]],
    timeline: dict[str, list[dict[str, str]]],
    metadata: dict[str, Any],
    output_dir: Path | None = None,
) -> dict[str, Path]:
    paths = generated_paths(root, output_dir)
    paths["generated"].mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "decision_id", "news_id", "ticker", "decision_date", "event_date", "trigger_type",
        "action", "reason", "source", "title", "url", "event_type",
        "risk_flags", "match_confidence", "article_summary", "content_hash",
    ]
    _atomic_write_events(paths["events"], events, fieldnames)
    _atomic_write_json(paths["timeline"], timeline)
    # Manifest is commit marker and is always atomically replaced after data files.
    _atomic_write_json(paths["metadata"], metadata)
    return {"events": paths["events"], "timeline": paths["timeline"], "metadata": paths["metadata"]}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic historical monitoring events.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root containing local data and reports.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for monitoring output artifacts.")
    parser.add_argument(
        "--as-of-date",
        type=explicit_iso_date,
        required=True,
        help="Required inclusive historical cutoff in YYYY-MM-DD format.",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    events, timeline, metadata = build_monitoring_events(root, args.as_of_date, args.output_dir)
    outputs = write_monitoring_outputs(root, events, timeline, metadata, args.output_dir)
    print(json.dumps({**metadata, "outputs": [str(path) for path in outputs.values()]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
