"""Generate news-monitoring events for decision-support records.

Reads generated evidence packs and enriched news. Emits post-decision news events
that should trigger Watch/Review Required states.
"""

from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(r"C:\Users\User\KLTN_KHTN")
GENERATED = ROOT / "reports" / "decision_support" / "generated"
AUDIT_PACKS_PATH = GENERATED / "evidence_packs_audit.json"
LEGACY_PACKS_PATH = GENERATED / "evidence_packs.json"
ENRICHED_NEWS = ROOT / "data" / "news" / "enriched" / "all_news_enriched.csv"
MATCHED_NEWS = ROOT / "data" / "news" / "matched" / "all_news_matched.csv"
OUT_CSV = GENERATED / "monitoring_events.csv"
OUT_JSON = GENERATED / "monitoring_timeline.json"

RISK_EVENT_TYPES = {"debt_risk", "legal_risk", "governance"}
RISK_FLAGS = {"debt_risk", "legal_risk", "earnings_warning", "governance", "capital_dilution", "audit_issue"}
WATCH_EVENT_TYPES = {"capital", "dividend", "earnings", "debt_risk", "legal_risk", "governance"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_json_list(value: str) -> list:
    if not value or not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value[:10]).date()
    except Exception:
        return None


def event_types(row: dict[str, str]) -> set[str]:
    value = row.get("event_type_enriched") or row.get("event_type") or ""
    return {part.strip() for part in value.split(",") if part.strip()}


def risk_flags(row: dict[str, str]) -> set[str]:
    parsed = parse_json_list(row.get("risk_flags_json", ""))
    return {str(x) for x in parsed if str(x)}


def classify_action(types: set[str], flags: set[str], match_confidence: str) -> tuple[str, str]:
    risk_hits = sorted((types & RISK_EVENT_TYPES) | (flags & RISK_FLAGS))
    if risk_hits:
        return "Review Required", "risk flags: " + ", ".join(risk_hits)
    if types & WATCH_EVENT_TYPES:
        return "Watch", "event type: " + ", ".join(sorted(types & WATCH_EVENT_TYPES))
    if match_confidence in {"partial", "none", ""}:
        return "Watch", "weak ticker matching confidence"
    return "Keep", "no material risk trigger"


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    packs_path = AUDIT_PACKS_PATH if AUDIT_PACKS_PATH.exists() else LEGACY_PACKS_PATH
    if not packs_path.exists():
        raise FileNotFoundError(f"Missing evidence packs: {packs_path}")
    news_path = ENRICHED_NEWS if ENRICHED_NEWS.exists() else MATCHED_NEWS
    if not news_path.exists():
        raise FileNotFoundError(f"Missing news data: {news_path}")

    packs = json.loads(packs_path.read_text(encoding="utf-8"))
    news_rows = read_csv(news_path)
    news_by_ticker: dict[str, list[dict[str, str]]] = {}
    for row in news_rows:
        news_by_ticker.setdefault(row.get("ticker", ""), []).append(row)

    today = date.today()
    events: list[dict[str, str]] = []
    timeline: dict[str, list[dict[str, str]]] = {}

    for pack in packs:
        decision_id = pack["decision_id"]
        ticker = pack["ticker"]
        decision_date = parse_date(pack.get("decision_date", ""))
        if decision_date is None:
            continue

        for row in news_by_ticker.get(ticker, []):
            event_date = parse_date(row.get("date", ""))
            if event_date is None or not (decision_date < event_date <= today):
                continue
            types = event_types(row)
            flags = risk_flags(row)
            action, reason = classify_action(types, flags, row.get("match_confidence", ""))
            if action == "Keep":
                continue

            event = {
                "decision_id": decision_id,
                "ticker": ticker,
                "decision_date": pack.get("decision_date", ""),
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

    events.sort(key=lambda e: (e["decision_id"], e["event_date"], e["title"]))
    fieldnames = [
        "decision_id", "ticker", "decision_date", "event_date", "trigger_type",
        "action", "reason", "source", "title", "url", "event_type",
        "risk_flags", "match_confidence", "article_summary", "content_hash",
    ]
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

    OUT_JSON.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "packs_source": str(packs_path),
        "news_source": str(news_path),
        "num_decisions": len(packs),
        "num_monitoring_events": len(events),
        "outputs": [str(OUT_CSV), str(OUT_JSON)],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
