from __future__ import annotations

import inspect
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import streamlit as st

KLTN_ROOT = Path(__file__).resolve().parents[1]
if str(KLTN_ROOT) not in sys.path:
    sys.path.insert(0, str(KLTN_ROOT))

from research_ui_v2 import app
from research_ui_v2.catalog import LOCALE_CATALOG, SUPPORTED_LOCALES, validate_locale_catalog
from research_ui_v2.fixtures.public_release import public_release_fixture


class _FixtureRepository:
    """In-memory aggregate fixture for renderer tests; never writes artifacts."""

    def __init__(self) -> None:
        self._release = public_release_fixture()
        self.manifest = {
            "bundle_id": "fixture-runtime",
            "schema_version": "v6-runtime-bundle-v1",
            "member_count": 1,
        }

    def release_artifact(self):
        return self._release

    def claims(self, analysis_state=None):
        claims = self._release["claims"]
        return claims if analysis_state is None else [claim for claim in claims if claim["analysis_state"] == analysis_state]

    def gates(self):
        return self._release["gates"]

    def source_statuses(self):
        return self._release["source_statuses"]

    def subgroup_results(self):
        return self._release["subgroup_results"]

    def approved_presets(self):
        return self._release["approved_presets"]


def test_locale_catalog_is_complete_for_bilingual_ui():
    assert validate_locale_catalog() == []
    assert all(set(value) == set(SUPPORTED_LOCALES) for value in LOCALE_CATALOG.values())


def test_v2_app_separates_lanes_and_keeps_h2_unsupported():
    source = inspect.getsource(app)
    assert 'pages = ["primary", "exploratory", "confirmation", "provenance", "operate_preview"]' in source
    assert 'if page in {"primary", "exploratory", "confirmation"}' in source
    assert 'if analysis_state == "confirmation"' in source
    assert "H2 is not confirmed; the locked comparison is unsupported." in source
    assert "H2 chưa được xác nhận; so sánh đã khóa không được ủng hộ." in source
    assert "st.dataframe(_claim_rows(chart_rows, locale)" in source


def test_v2_operate_preview_has_no_execution_controls_or_freeform_inputs():
    source = inspect.getsource(app)
    forbidden = (
        "subprocess",
        "os.system",
        "Popen",
        "st.button",
        "st.form",
        "st.text_input",
        "st.text_area",
        "st.file_uploader",
        "unsafe_allow_html",
    )
    assert "non-executing" in source
    assert all(token not in source for token in forbidden)


def test_v2_does_not_import_or_reference_legacy_evidencetrace_runtime():
    source = inspect.getsource(app)
    assert "research_ui." not in source
    assert "ui_artifacts/current" not in source
    assert "EVIDENCETRACE" not in source


def test_render_paths_use_streamlit_supported_icons(monkeypatch):
    repository = _FixtureRepository()
    icons: list[str | None] = []

    monkeypatch.setattr(st, "markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "caption", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "columns", lambda count: [SimpleNamespace(metric=lambda *_args, **_kwargs: None) for _ in range(count)])
    monkeypatch.setattr(st, "info", lambda *_args, **kwargs: icons.append(kwargs.get("icon")))
    monkeypatch.setattr(st, "warning", lambda *_args, **kwargs: icons.append(kwargs.get("icon")))
    monkeypatch.setattr(st, "bar_chart", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "dataframe", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "write", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(st, "selectbox", lambda _label, options, **_kwargs: options[0])

    app._render_banner(repository, "en")
    app._render_claim_state(repository, "confirmation", "en")
    app._render_operate_preview(repository, "en")

    assert icons == ["ℹ️", "⚠️", "ℹ️"]


def test_v2_app_smoke_runs_default_bundle_without_streamlit_exception():
    AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
    page = KLTN_ROOT / "research_ui_v2" / "app.py"
    at = AppTest.from_file(str(page)).run(timeout=20)
    assert not at.exception
