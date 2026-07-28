from __future__ import annotations

from datetime import date

from research_ui.components.market_workspace import _format_value, historical_technical_view, selected_record_view


def test_selected_record_view_uses_only_initial_and_cutoff_monitor_fields():
    candidate = {
        "ticker": "FPT",
        "decision_id": "D1",
        "period_id": "2025Q1",
        "decision_date": "2025-03-31",
    }
    detail = {
        "ml_signal": {"pred_proba_up": 0.8, "rank_in_period": 2},
        "data_quality_flags": {"news_coverage": "high", "ticker_matching_confidence": "mixed", "missing_fields": ["lead"]},
        "top_drivers": [{"feature": "rsi", "direction": "context", "explanation": "within range"}],
        "news_evidence": [{"evidence_id": "N1"}],
        "post_hoc_outcome": {"realized_period_return": 0.5},
        "rubric_score": 5,
    }
    events = [
        {"action": "Watch", "event_date": "2025-04-01"},
        {"action": "Review Required", "event_date": "2025-04-02"},
    ]

    view = selected_record_view(candidate, detail, events, date(2025, 4, 2))

    assert view["state"] == "Review Required"
    assert view["watch_count"] == 1
    assert view["review_required_count"] == 1
    assert view["initial_evidence_count"] == 1
    assert "outcome" not in str(view).lower()
    assert "rubric" not in str(view).lower()


def test_historical_technical_view_copies_full_frozen_initial_context_only():
    detail = {
        "decision_id": "D1",
        "ticker": "FPT",
        "decision_date": "2025-03-31",
        "period_id": "2025Q1",
        "technical_snapshot": {"rsi_end_q": 55.0, "price_vs_sma20": None},
        "top_drivers": [
            {"feature": "rsi_end_q", "value": 55.0, "direction": "neutral", "explanation": "Trong vùng trung tính."},
            {"feature": "macd_hist_mean_q", "value": 0.2, "direction": "positive", "explanation": "Động lượng dương."},
        ],
        "provenance": {"name": "initial", "path": "initial.json", "sha256": "a" * 64, "zone": "initial"},
        "post_hoc_outcome": {"return": 0.5},
        "rubric_score": 5,
        "fireant": {"current": 100},
    }

    view = historical_technical_view(detail)

    assert view["decision_date"] == "2025-03-31"
    assert view["technical_snapshot"] == detail["technical_snapshot"]
    assert view["top_drivers"] == detail["top_drivers"]
    assert view["provenance"]["sha256"] == "a" * 64
    assert "outcome" not in str(view).lower()
    assert "rubric" not in str(view).lower()
    assert "fireant" not in str(view).lower()


def test_technical_value_format_keeps_missing_unavailable():
    assert _format_value(None, "number") == "Chưa có"
    assert _format_value(0.0, "number") == "0.0000"
    assert _format_value(0.125, "percent") == "12.50%"
