from __future__ import annotations

from pathlib import Path

from research_ui.run_catalog import load_catalog, validate_catalog


def test_checked_in_catalog_validates_against_current_artifacts():
    catalog = load_catalog()

    assert validate_catalog(catalog) == []


def test_catalog_allows_exact_fireant_browser_displays_without_server_ingestion():
    external = load_catalog()["runtime_policy"]["external_context"]
    markets = external["fireant_markets_browser_display"]

    assert markets == {
        "enabled": True,
        "mode": "fixed_browser_embed_display_only",
        "widget_url": "https://www.fireant.vn/Widgets/Markets",
        "native_vnindex_fallback_url": "https://fireant.vn/ma-chung-khoan/VNINDEX",
        "server_fetch": False,
        "proxy": False,
        "provider_content_ingestion": False,
        "evidence_model_monitoring_review_evaluation_use": False,
    }
    assert external["fireant_selected_ticker_adapter"] == {
        "enabled": True,
        "mode": "selected_quote_browser_embed_display_only",
        "ticker_source": "validated_bundle_selected_decision",
        "widget_origin": "https://www.fireant.vn",
        "widget_path": "/Widgets/Quote",
        "widget_query_key": "symbols",
        "native_origin": "https://fireant.vn",
        "native_path_template": "/ma-chung-khoan/{TICKER}",
        "server_fetch": False,
        "proxy": False,
        "provider_content_ingestion": False,
        "evidence_model_monitoring_review_evaluation_use": False,
    }
    assert external["historical_technical_panel"] == {
        "enabled": True,
        "source": "validated_initial_bundle",
        "cutoff_field": "decision_date",
        "runtime_recomputation": False,
        "fireant_to_prompt": False,
    }


def test_catalog_reports_missing_rubric_path_without_key_error(tmp_path: Path):
    catalog = {
        "artifacts": [],
        "runs": [
            {
                "run_id": "broken-run",
                "rubric": {"expected_records": 75},
            }
        ],
    }

    issues = validate_catalog(catalog, tmp_path)

    assert any(issue.subject == "broken-run:rubric" and issue.message == "missing path" for issue in issues)


def test_catalog_reports_hash_mismatch(tmp_path: Path):
    artifact = tmp_path / "input.json"
    artifact.write_text("[]", encoding="utf-8")
    catalog = {
        "artifacts": [
            {
                "name": "input",
                "path": "input.json",
                "sha256": "0" * 64,
                "expected_records": 0,
            }
        ],
        "runs": [],
    }

    issues = validate_catalog(catalog, tmp_path)

    assert any(issue.message == "SHA-256 mismatch" for issue in issues)


def test_catalog_reports_csv_header_mismatch(tmp_path: Path):
    artifact = tmp_path / "prices.csv"
    artifact.write_text("ticker,date,close\nAAA,2025-01-01,10\n", encoding="utf-8")
    catalog = {
        "artifacts": [
            {
                "name": "prices",
                "path": "prices.csv",
                "expected_columns": ["ticker", "date", "open", "high", "low", "close", "volume"],
            }
        ],
        "runs": [],
    }

    issues = validate_catalog(catalog, tmp_path)

    assert any(issue.subject == "prices" and "expected columns" in issue.message for issue in issues)


def test_catalog_accepts_exact_csv_header(tmp_path: Path):
    artifact = tmp_path / "prices.csv"
    artifact.write_text("ticker,date,open,high,low,close,volume\nAAA,2025-01-01,10,11,9,10,100\n", encoding="utf-8")
    catalog = {
        "artifacts": [
            {
                "name": "prices",
                "path": "prices.csv",
                "expected_columns": ["ticker", "date", "open", "high", "low", "close", "volume"],
            }
        ],
        "runs": [],
    }

    assert validate_catalog(catalog, tmp_path) == []
