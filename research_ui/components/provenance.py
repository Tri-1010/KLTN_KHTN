"""Provenance rendering for EvidenceTrace."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_provenance(reference: dict[str, Any], title: str = "Provenance") -> None:
    with st.expander(title, expanded=False):
        st.markdown('<div class="provenance-box">', unsafe_allow_html=True)
        st.write(f"**Artifact:** `{reference.get('name', 'unknown')}`")
        st.write(f"**Đường dẫn:** `{reference.get('path', 'unknown')}`")
        st.write(f"**SHA-256:** `{reference.get('sha256', 'unknown')}`")
        if reference.get("schema_version"):
            st.write(f"**Schema:** `{reference['schema_version']}`")
        if reference.get("record_count") is not None:
            st.write(f"**Số record:** {reference['record_count']}")
        if reference.get("provenance_status"):
            st.warning(f"Trạng thái provenance: {reference['provenance_status']}")
        st.markdown("</div>", unsafe_allow_html=True)
