from __future__ import annotations

import inspect

import pytest

from research_ui.components import fireant_selected_ticker
from research_ui.components.external_market_context import (
    FireAntSelectedContext,
    resolve_fireant_selected_context,
    validate_fireant_selected_context,
)


def test_resolver_builds_exact_selected_ticker_contracts():
    context = resolve_fireant_selected_context(" fpt ", {"FPT", "VHM"})

    assert context == FireAntSelectedContext(
        ticker="FPT",
        quote_widget_url="https://www.fireant.vn/Widgets/Quote?symbols=FPT",
        native_url="https://fireant.vn/ma-chung-khoan/FPT",
    )
    assert resolve_fireant_selected_context("VHM", {"FPT", "VHM"}).ticker == "VHM"


@pytest.mark.parametrize("ticker", ["AAA", "FPT/../x", "FPT?x=1", "F PT", "ＦＰＴ", "FPTX", ""])
def test_resolver_rejects_unknown_or_hostile_ticker(ticker: str):
    assert resolve_fireant_selected_context(ticker, {"FPT", "VHM"}) is None


def test_validator_rejects_extra_query_even_when_blank():
    context = FireAntSelectedContext(
        ticker="FPT",
        quote_widget_url="https://www.fireant.vn/Widgets/Quote?symbols=FPT&extra=",
        native_url="https://fireant.vn/ma-chung-khoan/FPT",
    )

    with pytest.raises(ValueError):
        validate_fireant_selected_context(context)


def test_html_embeds_only_validated_quote_contract():
    context = resolve_fireant_selected_context("FPT", {"FPT"})
    html = fireant_selected_ticker.build_fireant_quote_html(context)

    assert html.count("<iframe") == 1
    assert 'src="https://www.fireant.vn/Widgets/Quote?symbols=FPT"' in html
    assert 'sandbox="allow-scripts allow-same-origin"' in html
    assert 'referrerpolicy="strict-origin-when-cross-origin"' in html
    assert "width: 100%" in html


def test_renderer_embeds_quote_and_keeps_native_fallback(monkeypatch):
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(fireant_selected_ticker.st, "markdown", lambda value: calls.append(("markdown", value)))
    monkeypatch.setattr(fireant_selected_ticker.st, "caption", lambda value: calls.append(("caption", value)))
    monkeypatch.setattr(fireant_selected_ticker.st, "warning", lambda value: calls.append(("warning", value)))
    monkeypatch.setattr(fireant_selected_ticker.st, "link_button", lambda label, url, type: calls.append(("link", (label, url, type))))
    monkeypatch.setattr(fireant_selected_ticker.components, "html", lambda value, height, scrolling: calls.append(("html", (value, height, scrolling))))

    fireant_selected_ticker.render_fireant_selected_ticker("FPT", {"FPT"})

    html_call = next(value for kind, value in calls if kind == "html")
    assert html_call[1:] == (fireant_selected_ticker.FIREANT_QUOTE_HEIGHT, False)
    assert "symbols=FPT" in html_call[0]
    assert ("link", ("Mở FPT trên FireAnt", "https://fireant.vn/ma-chung-khoan/FPT", "secondary")) in calls
    assert not any(kind == "warning" for kind, _ in calls)


def test_renderer_fails_closed_for_unknown_ticker(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(fireant_selected_ticker.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(fireant_selected_ticker.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(fireant_selected_ticker.st, "warning", lambda value: calls.append(value))
    monkeypatch.setattr(fireant_selected_ticker.st, "link_button", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("link forbidden")))
    monkeypatch.setattr(fireant_selected_ticker.components, "html", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("embed forbidden")))

    fireant_selected_ticker.render_fireant_selected_ticker("AAA", {"FPT"})

    assert calls


def test_renderer_preserves_fallback_when_component_raises(monkeypatch):
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(fireant_selected_ticker.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(fireant_selected_ticker.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(fireant_selected_ticker.st, "warning", lambda value: calls.append(("warning", value)))
    monkeypatch.setattr(fireant_selected_ticker.st, "link_button", lambda label, url, type: calls.append(("link", (label, url, type))))
    monkeypatch.setattr(fireant_selected_ticker.components, "html", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("unavailable")))

    fireant_selected_ticker.render_fireant_selected_ticker("FPT", {"FPT"})

    assert any(kind == "warning" for kind, _ in calls)
    assert any(kind == "link" for kind, _ in calls)


def test_component_has_no_server_or_iframe_message_path():
    source = inspect.getsource(fireant_selected_ticker).lower()
    for forbidden in ("requests", "httpx", "selenium", "postmessage", "onmessage", "session_state", "decision_id", "pred_proba_up", "outcome"):
        assert forbidden not in source
