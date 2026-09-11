"""Research Command Center shell, context strip, and status components."""

from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from ..assets.theme import APP_SUBTITLE, APP_TITLE, CUSTOM_CSS, PAGE_LABELS, STATUS_TOKENS
from ..policy import RESEARCH_DISCLAIMER


def configure_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="◈", layout="wide", initial_sidebar_state="expanded")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_shell(manifest: dict[str, Any]) -> None:
    title, status = st.columns([3, 2])
    with title:
        st.title(APP_TITLE)
        st.caption(APP_SUBTITLE)
    with status:
        st.markdown(
            f'<div class="trust-strip"><strong>VALIDATED HISTORICAL BUNDLE</strong><br>'
            f'`{manifest["bundle_version"]}` · Build `{manifest["built_at_utc"]}`</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div class="research-banner"><strong>{RESEARCH_DISCLAIMER}</strong> · '
        "Historical evidence, monitoring và LLM evaluation không phải chỉ dẫn giao dịch.</div>",
        unsafe_allow_html=True,
    )


def render_context_strip(decision_id: str, decision_date: str, variant: str, as_of: date) -> None:
    st.markdown(
        f'<div class="trust-strip"><strong>Ngữ cảnh historical</strong> · Hồ sơ: `{decision_id}` · '
        f'Snapshot: `{decision_date}` · Variant: `{variant}` · Cutoff: `{as_of.isoformat()}`</div>',
        unsafe_allow_html=True,
    )


def render_status(status: str) -> None:
    token = STATUS_TOKENS.get(status, {"icon": "•", "label": status, "kind": "muted"})
    st.markdown(
        f'<span class="status-{token["kind"]}" aria-label="Trạng thái {token["label"]}">{token["icon"]} {token["label"]}</span>',
        unsafe_allow_html=True,
    )


def render_workflow_rail(active: str, decision_id: str, as_of: date) -> None:
    st.sidebar.markdown("## EvidenceTrace")
    st.sidebar.caption("Research Command Center · historical workspace")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Ngữ cảnh hiện tại")
    st.sidebar.caption(f"Route: **{PAGE_LABELS[active]}**")
    st.sidebar.caption(f"Hồ sơ: `{decision_id}`")
    st.sidebar.caption(f"Cutoff: `{as_of.isoformat()}`")
    st.sidebar.info("Outcome chỉ xuất hiện tại Hậu kiểm. FireAnt và external snapshot không đổi historical state.")
