from __future__ import annotations

from datetime import date
import inspect
from types import SimpleNamespace

from research_ui import app
from research_ui.components import overview
from research_ui.summary import (
    filter_candidates_historically,
    summarize_full_evidence_quality_by_period,
    summarize_workflow_by_period,
)


def _candidate(decision_id: str, period: str, decision_date: str) -> dict[str, object]:
    return {"decision_id": decision_id, "period_id": period, "decision_date": decision_date}


def test_overview_renders_fixed_fireant_markets_before_metrics():
    source = inspect.getsource(overview.render_overview)

    assert "render_fireant_vnindex()" in source
    assert source.index("render_fireant_vnindex()") < source.index("st.columns(4)")
    assert list(inspect.signature(overview.render_fireant_vnindex).parameters) == []


def test_monitor_syncs_selected_ticker_fireant_technical_and_llm_context():
    source = inspect.getsource(app._render_monitor)

    selected_call = source.index("render_fireant_selected_ticker(ticker, allowed_tickers)")
    record_call = source.index("render_selected_record_panel(workspace)")
    technical_call = source.index("render_historical_technical_analysis(technical)")
    fresh_call = source.index("_render_fresh_information_panel(repository, decision_id, ticker)")
    markets_call = source.index("render_fireant_vnindex()")

    assert selected_call < record_call < technical_call < fresh_call < markets_call
    assert 'allowed_tickers = {str(row["ticker"]).upper() for row in repository.candidates()}' in source
    assert "render_external_market_context" not in source
    assert "session_state" not in source
    assert list(inspect.signature(app.render_fireant_vnindex).parameters) == []


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _StreamlitRuntime:
    def __init__(self):
        self.session_state: dict[str, object] = {}
        self.sidebar = SimpleNamespace(expander=lambda *args, **kwargs: _Context())
        self.next_clicks: set[str] = set()

    def selectbox(self, _label, options, *, key, **_kwargs):
        value = self.session_state.get(key, options[0])
        if value not in options:
            value = options[0]
        self.session_state[key] = value
        return value

    def multiselect(self, _label, _options, *, default, key, **_kwargs):
        value = self.session_state.get(key, default)
        self.session_state[key] = value
        return value

    def number_input(self, _label, *, value, key, **_kwargs):
        selected = self.session_state.get(key, value)
        self.session_state[key] = selected
        return selected

    def checkbox(self, _label, *, key, value=False, **_kwargs):
        selected = self.session_state.get(key, value)
        self.session_state[key] = selected
        return selected

    def button(self, _label, *, key, **_kwargs):
        if key in self.next_clicks:
            self.next_clicks.remove(key)
            return True
        return False

    def expander(self, *_args, **_kwargs):
        return _Context()

    def spinner(self, *_args, **_kwargs):
        return _Context()

    def __getattr__(self, _name):
        return lambda *_args, **_kwargs: None


class _LiveServiceRuntime:
    def __init__(self):
        self.preview_requests = []
        self.run_requests = []

    def preview(self, request):
        self.preview_requests.append(request)
        sequence = len(self.preview_requests)
        return {
            "preview_digest": f"{sequence:064x}",
            "preview_nonce": f"nonce-{sequence:016d}",
            "expires_at_utc": "2999-01-01T00:00:00+00:00",
            "outcome_leakage_check": "passed",
            "cards_requested": 1,
            "details": [],
        }

    def run(self, request):
        self.run_requests.append(request)
        return SimpleNamespace(state="completed", run_directory="runs/live", job_id="live-1", message="ok")


class _FreshServiceRuntime:
    def __init__(self):
        self.preview_requests = []
        self.run_requests = []
        self.session_bindings = []

    def preview(self, request):
        self.preview_requests.append(request)
        sequence = len(self.preview_requests)
        return {
            "preview_digest": f"{sequence:064x}",
            "preview_nonce": f"nonce-{sequence:016d}",
            "expires_at_utc": "2999-01-01T00:00:00+00:00",
            "ticker": "FPT",
            "technical_cutoff": "2025-01-01",
            "technical_field_count": 1,
            "technical_driver_count": 1,
            "external_fireant_ingested": False,
            "external_calls": {"rss_requests_max": len(request.source_ids), "llm_requests": 1},
        }

    def run(self, request):
        self.run_requests.append(request)
        return SimpleNamespace(
            state="completed",
            run_directory="runs/fresh",
            snapshot_id="snapshot-1",
            retrieved_at_utc="2026-01-01T00:00:00Z",
            cited_evidence_ids=[],
            result_markdown="result",
        )


def test_live_panel_reuses_unconsumed_preview_and_clears_after_run_attempt(monkeypatch):
    runtime = _StreamlitRuntime()
    service = _LiveServiceRuntime()
    identities: list[str] = []
    monkeypatch.setattr(app, "st", runtime)
    monkeypatch.setattr(app, "LiveJobService", lambda **kwargs: identities.append(kwargs["session_binding"]) or service)

    app._render_live_job_panel(object(), "D1")
    app._render_live_job_panel(object(), "D1")
    assert len(service.preview_requests) == 1
    assert len(set(identities)) == 1

    runtime.session_state["live_confirm"] = True
    runtime.next_clicks.add("live_run")
    app._render_live_job_panel(object(), "D1")

    assert len(service.preview_requests) == 1
    assert service.run_requests[0].preview_digest == f"{1:064x}"
    assert service.run_requests[0].preview_nonce == "nonce-0000000000000001"
    assert "live_displayed_preview" not in runtime.session_state

    app._render_live_job_panel(object(), "D1")
    assert len(service.preview_requests) == 2


def test_live_panel_refreshes_stale_identity_after_input_change_or_expiry(monkeypatch):
    runtime = _StreamlitRuntime()
    service = _LiveServiceRuntime()
    monkeypatch.setattr(app, "st", runtime)
    monkeypatch.setattr(app, "LiveJobService", lambda **_kwargs: service)

    app._render_live_job_panel(object(), "D1")
    app._render_live_job_panel(object(), "D2")
    assert len(service.preview_requests) == 2

    runtime.session_state["live_displayed_preview"]["expires_at_utc"] = "2000-01-01T00:00:00+00:00"
    app._render_live_job_panel(object(), "D2")
    assert len(service.preview_requests) == 3


def test_live_panel_clears_displayed_identity_after_failed_run_attempt(monkeypatch):
    runtime = _StreamlitRuntime()
    service = _LiveServiceRuntime()
    monkeypatch.setattr(app, "st", runtime)
    monkeypatch.setattr(app, "LiveJobService", lambda **_kwargs: service)
    app._render_live_job_panel(object(), "D1")
    service.run = lambda _request: (_ for _ in ()).throw(RuntimeError("provider unavailable"))

    runtime.session_state["live_confirm"] = True
    runtime.next_clicks.add("live_run")
    app._render_live_job_panel(object(), "D1")

    assert "live_displayed_preview" not in runtime.session_state


def test_live_panel_uses_distinct_opaque_identity_per_streamlit_session(monkeypatch):
    service = _LiveServiceRuntime()
    identities: list[str] = []
    monkeypatch.setattr(app, "LiveJobService", lambda **kwargs: identities.append(kwargs["session_binding"]) or service)

    first_runtime = _StreamlitRuntime()
    monkeypatch.setattr(app, "st", first_runtime)
    app._render_live_job_panel(object(), "D1")
    app._render_live_job_panel(object(), "D1")

    second_runtime = _StreamlitRuntime()
    monkeypatch.setattr(app, "st", second_runtime)
    app._render_live_job_panel(object(), "D1")

    assert identities[0] == identities[1]
    assert identities[2] != identities[0]
    assert len(identities[0]) == 32
    assert identities[0] not in str(first_runtime.session_state.get("live_displayed_preview"))


def test_fresh_panel_persists_unconsumed_preview_and_allows_consecutive_runs(monkeypatch):
    runtime = _StreamlitRuntime()
    service = _FreshServiceRuntime()
    monkeypatch.setitem(app.UI_MODEL_ALLOWLIST, "deepseek", (app.UI_MODEL_ALLOWLIST["deepseek"][0], "deepseek-test-model"))
    monkeypatch.setattr(app, "st", runtime)

    def service_factory(**kwargs):
        service.session_bindings.append(kwargs["session_binding"])
        return service

    monkeypatch.setattr(app, "FreshInformationJobService", service_factory)

    app._render_fresh_information_panel(object(), "D1", "FPT")
    app._render_fresh_information_panel(object(), "D1", "FPT")
    assert len(service.preview_requests) == 1
    assert len(set(service.session_bindings)) == 1

    runtime.session_state["fresh_confirm"] = True
    runtime.next_clicks.add("fresh_run")
    app._render_fresh_information_panel(object(), "D1", "FPT")
    assert len(service.preview_requests) == 1
    assert service.run_requests[0].preview_digest == f"{1:064x}"
    assert service.run_requests[0].preview_nonce == "nonce-0000000000000001"
    assert "fresh_displayed_preview" not in runtime.session_state

    app._render_fresh_information_panel(object(), "D1", "FPT")
    assert len(service.preview_requests) == 2
    runtime.next_clicks.add("fresh_run")
    app._render_fresh_information_panel(object(), "D1", "FPT")
    assert service.run_requests[-1].preview_digest == f"{2:064x}"
    assert service.run_requests[-1].preview_nonce == "nonce-0000000000000002"
    assert "fresh_displayed_preview" not in runtime.session_state


def test_fresh_panel_uses_distinct_opaque_identity_per_streamlit_session(monkeypatch):
    service = _FreshServiceRuntime()
    identities: list[str] = []
    monkeypatch.setattr(app, "FreshInformationJobService", lambda **kwargs: identities.append(kwargs["session_binding"]) or service)

    first_runtime = _StreamlitRuntime()
    monkeypatch.setattr(app, "st", first_runtime)
    app._render_fresh_information_panel(object(), "D1", "FPT")
    app._render_fresh_information_panel(object(), "D1", "FPT")

    second_runtime = _StreamlitRuntime()
    monkeypatch.setattr(app, "st", second_runtime)
    app._render_fresh_information_panel(object(), "D1", "FPT")

    assert identities[0] == identities[1]
    assert identities[2] != identities[0]
    assert len(identities[0]) == 32
    assert identities[0] not in str(first_runtime.session_state.get("fresh_displayed_preview"))


def test_historical_candidate_filter_honors_cutoff_and_periods():
    candidates = [
        _candidate("q1", "2025Q1", "2025-03-31"),
        _candidate("q2", "2025Q2", "2025-06-30"),
    ]

    filtered = filter_candidates_historically(candidates, date(2025, 4, 1), ["2025Q1"])

    assert [row["decision_id"] for row in filtered] == ["q1"]


def test_workflow_summary_has_complete_state_matrix():
    candidates = [_candidate("a", "2025Q1", "2025-03-31"), _candidate("b", "2025Q1", "2025-03-31"), _candidate("c", "2025Q2", "2025-06-30")]
    events = {"a": [], "b": [{"action": "Watch"}], "c": [{"action": "Watch"}, {"action": "Review Required"}]}

    rows = summarize_workflow_by_period(candidates, events)

    assert rows == [
        {"period_id": "2025Q1", "Initial": 1, "Watch": 1, "Review Required": 0, "candidate_count": 2},
        {"period_id": "2025Q2", "Initial": 0, "Watch": 0, "Review Required": 1, "candidate_count": 1},
    ]


def test_evidence_quality_uses_weighted_article_denominator():
    details = [
        {
            "period_id": "2025Q1",
            "news_evidence": [{}, {}],
            "data_quality_flags": {"full_text_coverage": 2, "summary_coverage": 1, "key_fact_coverage": 1},
        },
        {
            "period_id": "2025Q1",
            "news_evidence": [],
            "data_quality_flags": {"full_text_coverage": 0, "summary_coverage": 0, "key_fact_coverage": 0},
        },
    ]

    rows = summarize_full_evidence_quality_by_period(details)

    assert rows == [
        {
            "period_id": "2025Q1",
            "numerator": 4,
            "denominator": 6,
            "candidate_count": 2,
            "evaluated_candidate_count": 1,
            "zero_evidence_candidate_count": 1,
            "unavailable_field_count": 0,
            "availability_pct": 66.67,
        }
    ]


def test_evidence_quality_marks_missing_fields_without_fake_zero():
    rows = summarize_full_evidence_quality_by_period(
        [{"period_id": "2025Q1", "news_evidence": [{}], "data_quality_flags": {"full_text_coverage": 1}}]
    )

    assert rows[0]["numerator"] == 1
    assert rows[0]["denominator"] == 3
    assert rows[0]["unavailable_field_count"] == 2
    assert rows[0]["availability_pct"] == 33.33
