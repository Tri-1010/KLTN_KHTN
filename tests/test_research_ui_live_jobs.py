from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from research_ui.contracts import LiveJobRequest
from research_ui.live_jobs import LiveJobError, LiveJobService


def _request(**overrides):
    values = {
        "decision_ids": ["2025Q1_SCR_01"],
        "variant": "full_evidence",
        "provider": "gemini",
        "model": "gemini-2.5-pro",
        "score": False,
        "confirmed_external_call": False,
    }
    values.update(overrides)
    return LiveJobRequest(**values)


def _pack(rsi: float = 55.0) -> dict[str, object]:
    return {
        "decision_id": "2025Q1_SCR_01",
        "ticker": "SCR",
        "decision_date": "2025-03-31",
        "period_id": "2025Q1",
        "holding_horizon": "next_quarter",
        "ml_signal": {
            "model_name": "test-model",
            "pred_proba_up": 0.7,
            "pred_label": 1,
            "rank_in_period": 1,
            "signal_class": "Buy Candidate",
        },
        "technical_snapshot": {"rsi_end_q": rsi},
        "top_drivers": [],
        "news_evidence": [],
        "data_quality_flags": {},
        "guardrails": {},
    }


def _write_packs(root: Path, rsi: float = 55.0) -> Path:
    generated = root / "reports" / "decision_support" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    pack_path = generated / "evidence_packs_initial.json"
    pack_text = json.dumps([_pack(rsi)], ensure_ascii=False)
    pack_path.write_text(pack_text, encoding="utf-8")
    (generated / "evidence_packs_ml_only.json").write_text(pack_text, encoding="utf-8")
    return pack_path


def _confirmed(request: LiveJobRequest, preview: dict[str, object]) -> LiveJobRequest:
    return request.model_copy(
        update={
            "confirmed_external_call": True,
            "preview_digest": preview["preview_digest"],
            "preview_nonce": preview["preview_nonce"],
        }
    )


def test_live_job_preview_validates_prompt_safe_pack_without_calling_provider():
    preview = LiveJobService(max_cards=2).preview(_request())

    assert preview["cards_requested"] == 1
    assert preview["outcome_leakage_check"] == "passed"
    detail = preview["details"][0]
    assert detail["decision_id"] == "2025Q1_SCR_01"
    assert detail["technical_cutoff"] == "2025-03-31"
    assert detail["technical_field_count"] > 0
    assert detail["technical_driver_count"] > 0
    assert detail["external_fireant_ingested"] is False
    assert len(preview["preview_digest"]) == 64


def test_live_job_requires_explicit_confirmation_before_external_call():
    service = LiveJobService(max_cards=2)

    with pytest.raises(LiveJobError, match="Explicit external-call confirmation"):
        service.run(_request())


def test_live_job_enforces_bounded_card_limit():
    service = LiveJobService(max_cards=1)

    with pytest.raises(LiveJobError, match="Live job limit"):
        service.preview(_request(variant="both"))


def test_live_job_rejects_pack_changed_after_displayed_preview(monkeypatch, tmp_path: Path):
    service = LiveJobService(root=tmp_path, max_cards=2)
    generated = tmp_path / "reports" / "decision_support" / "generated"
    pack_path = _write_packs(tmp_path)
    request = _request()
    displayed_preview = service.preview(request)
    pack_path.write_text(json.dumps([_pack(56.0)]), encoding="utf-8")
    provider_called = False

    def fail_if_called(*args, **kwargs):
        nonlocal provider_called
        provider_called = True
        raise AssertionError("provider must not be called for stale preview")

    monkeypatch.setattr("research_ui.live_jobs.make_llm_client", fail_if_called)
    confirmed = _confirmed(request, displayed_preview)

    with pytest.raises(LiveJobError, match="changed after displayed preview"):
        service.run(confirmed)

    assert provider_called is False
    assert not (generated / "runs").exists()


def test_live_preview_isolated_between_sessions_and_rejects_cross_session_use(monkeypatch, tmp_path: Path):
    _write_packs(tmp_path)
    request = _request()
    first_service = LiveJobService(root=tmp_path, session_binding="session-a")
    second_service = LiveJobService(root=tmp_path, session_binding="session-b")

    first = first_service.preview(request)
    second = second_service.preview(request)

    assert first["preview_nonce"] != second["preview_nonce"]
    assert first["preview_digest"] != second["preview_digest"]
    monkeypatch.setattr(first_service, "_run_confirmed", lambda *_args: "ran")
    monkeypatch.setattr(second_service, "_run_confirmed", lambda *_args: "ran")
    with pytest.raises(LiveJobError, match="session, or prompt-safe pack changed"):
        second_service.run(_confirmed(request, first))


def test_live_preview_is_one_time_and_replay_is_rejected(monkeypatch, tmp_path: Path):
    _write_packs(tmp_path)
    service = LiveJobService(root=tmp_path, session_binding="session-a")
    request = _request()
    preview = service.preview(request)
    confirmed = _confirmed(request, preview)
    monkeypatch.setattr(service, "_run_confirmed", lambda *_args: "ran")

    assert service.run(confirmed) == "ran"
    with pytest.raises(LiveJobError, match="missing, expired"):
        service.run(confirmed)


def test_live_preview_expiry_rejects_without_provider_call(monkeypatch, tmp_path: Path):
    from research_ui import live_jobs

    _write_packs(tmp_path)
    service = LiveJobService(root=tmp_path, session_binding="session-a")
    request = _request()
    preview = service.preview(request)
    with live_jobs._PREVIEW_LOCK:
        live_jobs._PREVIEWS[preview["preview_nonce"]]["expires_at"] = datetime(2000, 1, 1, tzinfo=timezone.utc)
    provider_called = False

    def fail_if_called(*_args, **_kwargs):
        nonlocal provider_called
        provider_called = True
        raise AssertionError("provider must not be called for expired preview")

    monkeypatch.setattr("research_ui.live_jobs.make_llm_client", fail_if_called)
    with pytest.raises(LiveJobError, match="missing, expired"):
        service.run(_confirmed(request, preview))
    assert provider_called is False


def test_live_job_accepts_unchanged_displayed_preview(monkeypatch, tmp_path: Path):
    service = LiveJobService(root=tmp_path, max_cards=2)
    generated = tmp_path / "reports" / "decision_support" / "generated"
    _write_packs(tmp_path)
    request = _request()
    displayed_preview = service.preview(request)
    monkeypatch.setattr("research_ui.live_jobs.load_env_file", lambda *args, **kwargs: {})
    monkeypatch.setattr("research_ui.live_jobs.make_llm_client", lambda *args, **kwargs: (object(), object()))
    monkeypatch.setattr(
        "research_ui.live_jobs.call_generate",
        lambda *args, **kwargs: {
            "text": "complete card",
            "response_model": "gemini-test",
            "request_id": "req-1",
            "stop_reason": "STOP",
            "usage": {},
        },
    )
    confirmed = _confirmed(request, displayed_preview)

    status = service.run(confirmed)

    assert status.state == "completed"
    manifest = next((generated / "runs").glob("*/manifest.json"))
    assert json.loads(manifest.read_text(encoding="utf-8"))["cards"][0]["card_markdown"] == "complete card"


def test_live_job_records_honest_provider_failure(monkeypatch, tmp_path: Path):
    service = LiveJobService(root=tmp_path, max_cards=2)
    generated = tmp_path / "reports" / "decision_support" / "generated"
    _write_packs(tmp_path)
    monkeypatch.setattr("research_ui.live_jobs.load_env_file", lambda *args, **kwargs: {})
    monkeypatch.setattr("research_ui.live_jobs.resolve_model", lambda *args, **kwargs: "gemini-test")
    monkeypatch.setattr("research_ui.live_jobs.make_llm_client", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("provider unavailable")))
    request = _request()
    displayed_preview = service.preview(request)
    confirmed = _confirmed(request, displayed_preview)

    status = service.run(confirmed)
    manifest = next((tmp_path / "reports" / "decision_support" / "generated" / "runs").glob("*/manifest.json"))

    assert status.state == "failed"
    assert "provider unavailable" in status.message
    assert "provider unavailable" in manifest.read_text(encoding="utf-8")
