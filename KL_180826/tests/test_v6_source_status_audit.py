from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


status = load("build_v6_source_status_audit")


def test_source_status_preserves_error_categories_and_verified_no_news():
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(["2026-06-02", "2026-06-03", "2026-06-04"]),
        }
    )
    matched = pd.DataFrame(
        [
            {"date": "2026-06-01", "url": "u-ok", "ticker": "AAA", "match_confidence": "exact"},
            {"date": "bad-date", "url": "u-time", "ticker": "AAA", "match_confidence": "exact"},
            {"date": "2026-06-02", "url": "u-extract", "ticker": "AAA", "match_confidence": "exact"},
            {"date": "2026-06-02", "url": "u-match", "ticker": "UNKNOWN", "match_confidence": "none"},
        ]
    )
    processed = pd.DataFrame(
        [
            {"date": "2026-06-01", "url": "u-ok", "ticker": "AAA", "extraction_status": "ok"},
            {"date": "bad-date", "url": "u-time", "ticker": "AAA", "extraction_status": "ok"},
            {"date": "2026-06-02", "url": "u-extract", "ticker": "AAA", "extraction_status": "fetch_failed"},
            {"date": "2026-06-02", "url": "u-match", "ticker": "UNKNOWN", "extraction_status": "ok"},
        ]
    )
    consensus = pd.DataFrame(
        [{"ticker": "AAA", "article_date": "2026-06-01", "analysis_eligible": True}]
    )

    audit, errors = status.build_source_status_audit(prices, matched, processed, consensus)

    by_date = audit.set_index("date")["source_status"].to_dict()
    # The valid Jun 1 article maps to Jun 2; the failed Jun 2 article maps
    # strictly to Jun 3 and takes precedence over an otherwise no-news row.
    assert by_date[pd.Timestamp("2026-06-02")] == "valid_source_event"
    assert by_date[pd.Timestamp("2026-06-03")] == "extraction_failed"
    assert by_date[pd.Timestamp("2026-06-04")] == "no_valid_news"
    assert set(errors["source_status"]) >= {"missing_timestamp", "ticker_match_failed"}
    assert audit["source_status"].isin(status.STATUS_VALUES).all()


def test_source_status_summary_does_not_relabel_errors_as_no_news():
    audit = pd.DataFrame(
        {
            "source_status": ["no_valid_news", "extraction_failed"],
        }
    )
    errors = pd.DataFrame({"source_status": ["missing_timestamp", "ticker_match_failed"]})
    summary = {row["source_status"]: row for row in status.source_status_summary(audit, errors)}

    assert summary["no_valid_news"]["panel_rows"] == 1
    assert summary["missing_timestamp"]["unassigned_source_errors"] == 1
    assert summary["ticker_match_failed"]["unassigned_source_errors"] == 1
