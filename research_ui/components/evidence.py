"""Evidence-first point-in-time decision-record rendering."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ..assets.theme import QUALITY_LABELS, VARIANT_LABELS
from .provenance import render_provenance


def render_initial_detail(detail: dict[str, Any]) -> None:
    st.subheader(f"{detail['ticker']} · {detail['decision_id']}")
    st.markdown(
        f'<div class="trust-strip"><strong>POINT-IN-TIME · OUTCOME EXCLUDED</strong> · '
        f'Snapshot: `{detail["decision_date"]}` · Variant: `{VARIANT_LABELS[detail["snapshot_mode"]]}` · '
        f'News cutoff: `{detail["guardrails"].get("news_cutoff", "Chưa có")}`</div>',
        unsafe_allow_html=True,
    )
    signal = detail["ml_signal"]
    quality = detail["data_quality_flags"]
    metrics = st.columns(4)
    metrics[0].metric("Evidence coverage", QUALITY_LABELS.get(str(quality.get("news_coverage")).lower(), quality.get("news_coverage")))
    metrics[1].metric("Matching confidence", QUALITY_LABELS.get(str(quality.get("ticker_matching_confidence")).lower(), quality.get("ticker_matching_confidence")))
    metrics[2].metric("Xác suất mô hình", f"{signal['pred_proba_up']:.4f}")
    metrics[3].metric("Thứ hạng", signal["rank_in_period"])
    st.caption("Ứng viên mô hình, xác suất và thứ hạng là metadata mô hình lịch sử; không phải khuyến nghị đầu tư.")

    st.markdown("#### Evidence và quality")
    _render_quality_summary(quality, detail["guardrails"])
    if not detail["news_evidence"]:
        st.warning("Ablation ML-only. News evidence được loại có chủ đích khỏi biến thể đầu vào này; đây không phải evidence thiếu ngẫu nhiên.")
    else:
        for evidence in detail["news_evidence"]:
            _render_evidence(evidence)

    st.markdown("#### Tín hiệu ML và technical drivers")
    st.write(f"Trạng thái analyst: **{signal['display_status']}** · Nhãn nguồn thô được giữ trong audit, không dùng làm CTA analyst.")
    st.dataframe(detail["top_drivers"], hide_index=True, width="stretch")

    with st.expander("Technical snapshot đầy đủ", expanded=False):
        st.dataframe([{"field": key, "value": value} for key, value in detail["technical_snapshot"].items()], hide_index=True, width="stretch")
    with st.expander("Quality, guardrail và provenance audit", expanded=False):
        st.json({"data_quality_flags": quality, "guardrails": detail["guardrails"]})
        render_provenance(detail["provenance"], "Provenance initial pack")


def _render_quality_summary(quality: dict[str, Any], guardrails: dict[str, Any]) -> None:
    full_text = quality.get("full_text_coverage")
    summary = quality.get("summary_coverage")
    facts = quality.get("key_fact_coverage")
    st.info(
        f"Full text: `{full_text if full_text is not None else 'Chưa có'}` · "
        f"Summary: `{summary if summary is not None else 'Chưa có'}` · "
        f"Key facts: `{facts if facts is not None else 'Chưa có'}` · "
        f"prompt-safe: `{guardrails.get('initial_prompt_safe', False)}`"
    )
    missing = quality.get("missing_fields") or []
    if missing:
        st.warning("Trường evidence còn thiếu: " + ", ".join(str(field) for field in missing))


def _render_evidence(evidence: dict[str, Any]) -> None:
    title = f"{evidence['evidence_id']} · {evidence['source']} · {evidence['published_at']}"
    with st.expander(title, expanded=False):
        st.markdown(f"**{evidence['title']}**")
        if evidence.get("article_summary"):
            st.write(evidence["article_summary"])
        if evidence.get("evidence_span"):
            st.markdown("**Evidence span**")
            st.write(evidence["evidence_span"])
        cols = st.columns(3)
        cols[0].write(f"Event type: `{evidence.get('event_type') or 'Chưa có'}`")
        cols[1].write(f"Matching: `{evidence.get('match_confidence') or 'Chưa có'}`")
        cols[2].write(f"Extraction: `{evidence.get('extraction_status') or 'Chưa có'}`")
        if evidence.get("risk_flags"):
            st.warning("Risk flags: " + ", ".join(evidence["risk_flags"]))
        if evidence.get("key_facts"):
            st.dataframe(evidence["key_facts"], hide_index=True, width="stretch")
        if evidence.get("url"):
            st.link_button("Mở nguồn HTTPS", evidence["url"], type="secondary")
        st.caption(f"Content hash: `{evidence.get('content_hash') or 'Chưa có'}`")
