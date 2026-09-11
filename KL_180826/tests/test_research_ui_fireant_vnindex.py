from __future__ import annotations

import inspect

from research_ui.components import fireant_vnindex


def test_widget_html_uses_only_fixed_official_fireant_markets_contract():
    html = fireant_vnindex.build_fireant_markets_html()

    assert html.count("<iframe") == 1
    assert f'src="{fireant_vnindex.FIREANT_MARKETS_WIDGET_URL}"' in html
    assert 'sandbox="allow-scripts allow-same-origin"' in html
    assert 'allow="fullscreen"' in html
    assert 'referrerpolicy="strict-origin-when-cross-origin"' in html
    assert 'width: 100%' in html
    assert 'overflow: hidden' in html
    assert list(inspect.signature(fireant_vnindex.build_fireant_markets_html).parameters) == []
    assert list(inspect.signature(fireant_vnindex.render_fireant_vnindex).parameters) == []


def test_renderer_embeds_markets_and_always_keeps_native_fallback(monkeypatch):
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(fireant_vnindex.st, "markdown", lambda value: calls.append(("markdown", value)))
    monkeypatch.setattr(fireant_vnindex.st, "caption", lambda value: calls.append(("caption", value)))
    monkeypatch.setattr(fireant_vnindex.st, "warning", lambda value: calls.append(("warning", value)))
    monkeypatch.setattr(
        fireant_vnindex.st,
        "link_button",
        lambda label, url, type: calls.append(("link_button", (label, url, type))),
    )
    monkeypatch.setattr(
        fireant_vnindex.components,
        "html",
        lambda value, height, scrolling: calls.append(("html", (value, height, scrolling))),
    )

    fireant_vnindex.render_fireant_vnindex()

    html_call = next(value for kind, value in calls if kind == "html")
    assert html_call[1:] == (fireant_vnindex.FIREANT_MARKETS_HEIGHT, False)
    assert fireant_vnindex.FIREANT_MARKETS_WIDGET_URL in html_call[0]
    assert (
        "link_button",
        ("Mở VNINDEX trên FireAnt", fireant_vnindex.FIREANT_VNINDEX_URL, "secondary"),
    ) in calls
    captions = " ".join(str(value) for kind, value in calls if kind == "caption")
    for boundary in ("DISPLAY-ONLY", "validated historical bundle", "as_of", "evidence", "model", "review", "evaluation", "khuyến nghị"):
        assert boundary in captions
    assert not any(kind == "warning" for kind, _ in calls)


def test_renderer_preserves_fallback_when_component_raises(monkeypatch):
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(fireant_vnindex.st, "markdown", lambda value: calls.append(("markdown", value)))
    monkeypatch.setattr(fireant_vnindex.st, "caption", lambda value: calls.append(("caption", value)))
    monkeypatch.setattr(fireant_vnindex.st, "warning", lambda value: calls.append(("warning", value)))
    monkeypatch.setattr(
        fireant_vnindex.st,
        "link_button",
        lambda label, url, type: calls.append(("link_button", (label, url, type))),
    )
    monkeypatch.setattr(
        fireant_vnindex.components,
        "html",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("component unavailable")),
    )

    fireant_vnindex.render_fireant_vnindex()

    assert any(kind == "warning" for kind, _ in calls)
    assert (
        "link_button",
        ("Mở VNINDEX trên FireAnt", fireant_vnindex.FIREANT_VNINDEX_URL, "secondary"),
    ) in calls


def test_component_has_no_runtime_input_or_server_side_data_path():
    source = inspect.getsource(fireant_vnindex).lower()

    assert source.count("https://www.fireant.vn/widgets/markets") == 1
    assert source.count("https://fireant.vn/ma-chung-khoan/vnindex") == 1
    for forbidden in (
        "ticker:",
        "url:",
        "raw_html",
        "decision_id",
        "pred_proba_up",
        "outcome",
        "requests",
        "httpx",
        "urllib.request",
        "selenium",
        "onmessage",
        "addeventlistener",
        "session_state",
    ):
        assert forbidden not in source
