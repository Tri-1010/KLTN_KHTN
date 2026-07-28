from __future__ import annotations

from datetime import date

import pytest

from research_ui.components.external_market_context import (
    ExternalProviderLink,
    render_external_market_context,
    resolve_fireant_link,
    validate_fireant_catalog,
    validate_fireant_link,
)


TODAY = date(2026, 7, 16)


def approved_link(ticker: str = "FPT") -> ExternalProviderLink:
    return ExternalProviderLink(
        ticker=ticker,
        url="https://fireant.vn/",
        approved_host="fireant.vn",
        official_source_url="https://fireant.vn/",
        reviewed_on=date(2026, 7, 1),
        review_expires_on=date(2026, 8, 1),
        status="enabled",
    )


def test_fireant_resolver_returns_only_exact_approved_catalog_entry():
    entry = approved_link()

    assert resolve_fireant_link(" fpt ", {"FPT": entry}, TODAY) is entry
    assert resolve_fireant_link("AAA", {"FPT": entry}, TODAY) is None
    assert resolve_fireant_link("FPT/../../x", {"FPT": entry}, TODAY) is None


def test_fireant_resolver_rejects_pending_expired_and_invalid_catalog_entries():
    pending = approved_link()
    pending = ExternalProviderLink(**{**pending.__dict__, "status": "pending_verification"})
    expired = approved_link()
    expired = ExternalProviderLink(**{**expired.__dict__, "review_expires_on": date(2026, 7, 15)})
    future_review = approved_link()
    future_review = ExternalProviderLink(**{**future_review.__dict__, "reviewed_on": date(2026, 7, 17)})
    outside_universe = approved_link("AAA")

    assert resolve_fireant_link("FPT", {"FPT": pending}, TODAY) is None
    assert resolve_fireant_link("FPT", {"FPT": expired}, TODAY) is None
    assert resolve_fireant_link("FPT", {"FPT": future_review}, TODAY) is None
    assert resolve_fireant_link("AAA", {"AAA": outside_universe}, TODAY) is None


@pytest.mark.parametrize(
    "url",
    [
        "http://fireant.vn/",
        "https://user@fireant.vn/",
        "https://fireant.vn:443/",
        "https://fireant.vn/?ticker=FPT",
        "https://fireant.vn/#chart",
        "https://127.0.0.1/",
        "https://evil-fireant.vn/",
        "https://fireant.vn/redirect/FPT",
        "https://fireant.vn/EXTERNAL/FPT",
    ],
)
def test_fireant_catalog_rejects_unapproved_url_shapes(url: str):
    entry = approved_link()
    malformed = ExternalProviderLink(**{**entry.__dict__, "url": url})

    with pytest.raises(ValueError):
        validate_fireant_link(malformed)


def test_fireant_catalog_uses_pipeline_ticker_universe_and_exact_key():
    entry = approved_link()
    vgc_entry = approved_link("VGC")

    validate_fireant_catalog({"FPT": entry, "VGC": vgc_entry})
    with pytest.raises(ValueError):
        validate_fireant_catalog({"MISMATCH": entry})


def test_fireant_resolver_fails_closed_when_any_catalog_entry_is_invalid():
    entry = approved_link()
    malformed = ExternalProviderLink(**{**approved_link("VGC").__dict__, "url": "http://fireant.vn/"})

    assert resolve_fireant_link("FPT", {"FPT": entry, "VGC": malformed}, TODAY) is None
    assert resolve_fireant_link("FPT", {"FPT": entry, "VGC": object()}, TODAY) is None


def test_renderer_uses_only_approved_outbound_link_without_state_mutation(monkeypatch):
    entry = approved_link()
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr("research_ui.components.external_market_context.st.markdown", lambda value: calls.append(("markdown", value)))
    monkeypatch.setattr("research_ui.components.external_market_context.st.caption", lambda value: calls.append(("caption", value)))
    monkeypatch.setattr("research_ui.components.external_market_context.st.info", lambda value: calls.append(("info", value)))
    monkeypatch.setattr(
        "research_ui.components.external_market_context.st.link_button",
        lambda label, url, type: calls.append(("link_button", (label, url, type))),
    )

    render_external_market_context("FPT", {"FPT": entry})

    assert ("link_button", ("Mở FireAnt", "https://fireant.vn/", "secondary")) in calls
    assert not any(kind == "info" for kind, _ in calls)


def test_renderer_shows_unavailable_state_without_unapproved_link(monkeypatch):
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr("research_ui.components.external_market_context.st.markdown", lambda value: calls.append(("markdown", value)))
    monkeypatch.setattr("research_ui.components.external_market_context.st.caption", lambda value: calls.append(("caption", value)))
    monkeypatch.setattr("research_ui.components.external_market_context.st.info", lambda value: calls.append(("info", value)))
    monkeypatch.setattr("research_ui.components.external_market_context.st.link_button", lambda *args, **kwargs: calls.append(("link_button", args)))

    render_external_market_context("FPT", {})

    assert any(kind == "info" for kind, _ in calls)
    assert not any(kind == "link_button" for kind, _ in calls)


def test_external_adapter_never_embeds_or_exposes_historical_fields():
    source = __import__("research_ui.components.external_market_context", fromlist=["unused"])
    module_source = open(source.__file__, encoding="utf-8").read()

    assert "components.html" not in module_source
    assert "<iframe" not in module_source
    assert "tradingview" not in module_source.lower()
    assert "pred_proba_up" not in module_source
    assert "outcome" not in module_source.lower()
    assert "as_of" not in module_source
    assert "requests" not in module_source
    assert "httpx" not in module_source
    assert "selenium" not in module_source
