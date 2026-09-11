"""Streamlit renderer for the standalone, non-executing V6 results Dashboard V2."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import streamlit as st

from research_ui_v2.assets.theme import V2_CSS
from research_ui_v2.catalog import Locale, bilingual_text, status_label, tr
from research_ui_v2.repository import (
    PublicReleaseRepository,
    PublicReleaseRepositoryError,
    open_public_release,
    validate_v2_bundle_directory,
)

DEFAULT_BUNDLE = Path(__file__).resolve().parents[1] / "ui_artifacts" / "v2" / "default"


def resolve_bundle() -> Path:
    """Resolve and validate a V2-only bundle without exposing a UI path input."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--bundle", default=os.environ.get("V6_RESULTS_V2_BUNDLE", str(DEFAULT_BUNDLE)))
    args, _ = parser.parse_known_args()
    return validate_v2_bundle_directory(Path(args.bundle))


def _locale_selector() -> Locale:
    return st.sidebar.selectbox(
        tr("locale_label", "vi"),
        options=["vi", "en"],
        format_func=lambda value: "Tiếng Việt" if value == "vi" else "English",
        key="v2_locale",
    )


def _text(value: dict[str, str], locale: Locale) -> str:
    return bilingual_text(value, locale)


def _safe_markdown(text: str) -> None:
    st.markdown(text)


def _render_banner(repository: PublicReleaseRepository, locale: Locale) -> None:
    release = repository.release_artifact()
    _safe_markdown(f"### {tr('app_title', locale)}")
    st.caption(tr("app_subtitle", locale))
    st.info(tr("not_investment_advice", locale), icon="ℹ️")
    columns = st.columns(4)
    columns[0].metric(tr("release_status", locale), tr("locked", locale))
    columns[1].metric(tr("aggregate_only", locale), "Yes" if locale == "en" else "Có")
    columns[2].metric(tr("release_id", locale), release["release_id"])
    columns[3].metric(tr("runtime_integrity", locale), tr("passed", locale))


def _claim_rows(claims: list[dict[str, Any]], locale: Locale) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for claim in claims:
        result = claim.get("result")
        row = {
            tr("analysis_state", locale): tr(claim["analysis_state"], locale),
            tr("claim_status", locale): status_label(claim["status"], locale),
            "ID": claim["claim_id"],
            "Title": _text(claim["title"], locale),
            "Statement": _text(claim["statement"], locale),
        }
        if result is not None:
            row.update(
                {
                    tr("metric_estimate", locale): result["estimate"],
                    tr("ci_95", locale): f"[{result['ci_lower']:.7f}, {result['ci_upper']:.7f}]",
                    tr("bh_p", locale): result["bh_adjusted_p_value"],
                }
            )
        rows.append(row)
    return rows


def _render_result_chart_and_table(claims: list[dict[str, Any]], locale: Locale) -> None:
    chart_rows = [claim for claim in claims if claim.get("result") is not None]
    if not chart_rows:
        st.caption(tr("not_estimable", locale))
        return
    chart_data = {_text(claim["title"], locale): claim["result"]["estimate"] for claim in chart_rows}
    st.bar_chart(chart_data, horizontal=True)
    _safe_markdown(f"#### {tr('table_equivalent', locale)}")
    st.dataframe(_claim_rows(chart_rows, locale), hide_index=True, use_container_width=True)


def _render_claim_state(repository: PublicReleaseRepository, analysis_state: str, locale: Locale) -> None:
    claims = repository.claims(analysis_state)
    _safe_markdown(f"### {tr(analysis_state, locale)}")
    if analysis_state == "confirmation":
        st.warning(
            "H2 is not confirmed; the locked comparison is unsupported."
            if locale == "en"
            else "H2 chưa được xác nhận; so sánh đã khóa không được ủng hộ.",
            icon="⚠️",
        )
    _render_result_chart_and_table(claims, locale)
    if not any(claim.get("result") is not None for claim in claims):
        st.dataframe(_claim_rows(claims, locale), hide_index=True, use_container_width=True)


def _render_gates(repository: PublicReleaseRepository, locale: Locale) -> None:
    _safe_markdown(f"### {tr('gates', locale)}")
    st.dataframe(
        [
            {
                "ID": gate["gate_id"],
                tr("claim_status", locale): status_label(gate["status"], locale),
                "Gate": _text(gate["label"], locale),
                "Rationale": _text(gate["rationale"], locale),
            }
            for gate in repository.gates()
        ],
        hide_index=True,
        use_container_width=True,
    )


def _render_subgroups(repository: PublicReleaseRepository, locale: Locale) -> None:
    _safe_markdown(f"### {tr('subgroups', locale)}")
    rows: list[dict[str, Any]] = []
    for subgroup in repository.subgroup_results():
        row = {
            "ID": subgroup["subgroup_id"],
            tr("claim_status", locale): status_label(subgroup["status"], locale),
            "Subgroup": _text(subgroup["label"], locale),
            "Note": _text(subgroup["note"], locale),
        }
        if subgroup.get("result") is not None:
            row[tr("metric_estimate", locale)] = subgroup["result"]["estimate"]
        rows.append(row)
    st.dataframe(rows, hide_index=True, use_container_width=True)


def _render_provenance(repository: PublicReleaseRepository, locale: Locale) -> None:
    _safe_markdown(f"### {tr('source_status', locale)}")
    st.dataframe(
        [
            {
                "ID": status["source_id"],
                tr("release_status", locale): status_label(status["status"], locale),
                "Scope": status["scope"],
                "Source": _text(status["label"], locale),
                "Note": _text(status["note"], locale),
            }
            for status in repository.source_statuses()
        ],
        hide_index=True,
        use_container_width=True,
    )
    _safe_markdown(f"### {tr('limitations', locale)}")
    for limitation in repository.release_artifact()["limitations"]:
        st.write(f"- {_text(limitation, locale)}")
    _safe_markdown(f"### {tr('provenance', locale)}")
    manifest = repository.manifest
    st.dataframe(
        [{
            tr("bundle_id", locale): manifest["bundle_id"],
            tr("schema_version", locale): manifest["schema_version"],
            tr("member_count", locale): manifest["member_count"],
            tr("runtime_integrity", locale): tr("passed", locale),
        }],
        hide_index=True,
        use_container_width=True,
    )


def _render_operate_preview(repository: PublicReleaseRepository, locale: Locale) -> None:
    """Show fixed review presets only; it has no execution capability."""
    _safe_markdown(f"### {tr('operate_preview', locale)}")
    st.info(tr("non_executing", locale), icon="ℹ️")
    presets = repository.approved_presets()
    selected_id = st.selectbox(
        tr("preset_label", locale),
        options=[preset["preset_id"] for preset in presets],
        format_func=lambda preset_id: _text(next(item for item in presets if item["preset_id"] == preset_id)["label"], locale),
        key="v2_fixed_preset",
    )
    preset = next(item for item in presets if item["preset_id"] == selected_id)
    st.caption(_text(preset["description"], locale))
    selected_claims = set(preset["claim_ids"])
    st.dataframe(
        _claim_rows([claim for claim in repository.claims() if claim["claim_id"] in selected_claims], locale),
        hide_index=True,
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(page_title="V6 Study Results Dashboard", layout="wide")
    st.html(V2_CSS)
    try:
        repository = open_public_release(resolve_bundle())
    except PublicReleaseRepositoryError as exc:
        st.error(f"Không mở được V2 public release đã kiểm tra: {exc}")
        st.stop()
    locale = _locale_selector()
    _render_banner(repository, locale)
    pages = ["primary", "exploratory", "confirmation", "provenance", "operate_preview"]
    page = st.sidebar.radio(
        tr("claims", locale),
        pages,
        format_func=lambda value: tr(value, locale) if value != "operate_preview" else tr("operate_preview", locale),
    )
    if page in {"primary", "exploratory", "confirmation"}:
        _render_claim_state(repository, page, locale)
        if page == "confirmation":
            _render_gates(repository, locale)
        if page == "exploratory":
            _render_subgroups(repository, locale)
    elif page == "provenance":
        _render_provenance(repository, locale)
    else:
        _render_operate_preview(repository, locale)
    st.caption(tr("footer", locale))


if __name__ == "__main__":
    main()
