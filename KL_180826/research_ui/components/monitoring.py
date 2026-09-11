"""Historical monitoring timeline and analyst update renderers."""

from __future__ import annotations

from collections import Counter
from typing import Any

import streamlit as st

from .shell import render_status


def render_monitoring(events: list[dict[str, Any]], as_of: str) -> None:
    st.markdown(f'<div class="cutoff-bar"><strong>Historical replay through `{as_of}`</strong><br>Event sau cutoff đã bị loại.</div>', unsafe_allow_html=True)
    if not events:
        st.info("Không có monitoring event quan sát được tại cutoff này.")
        return
    actions = sorted({event["action"] for event in events})
    selected = st.multiselect("Lọc trạng thái cảnh báo", actions, default=actions)
    visible = sorted((event for event in events if event["action"] in selected), key=lambda event: (event["event_date"], event["title"]))
    counts = Counter(event["action"] for event in visible)
    st.caption(" · ".join(f"{action}: {counts[action]}" for action in actions))
    st.markdown("#### Timeline evidence")
    for event in visible:
        with st.container(border=True):
            cols = st.columns([1, 4])
            with cols[0]:
                st.write(f"**{event['event_date']}**")
                render_status(event["action"])
            with cols[1]:
                st.write(f"**{event['title']}**")
                st.write(event["reason"])
                if event.get("article_summary"):
                    st.write(event["article_summary"])
                st.caption(f"Nguồn: {event['source']} · Matching: {event.get('match_confidence') or 'Chưa có'}")
                if event.get("risk_flags"):
                    st.warning("Risk flags: " + ", ".join(event["risk_flags"]))
                if event.get("url"):
                    st.link_button("Mở nguồn", event["url"], type="secondary")
                st.caption(f"Content hash: `{event.get('content_hash') or 'Chưa có'}`")
                if event.get("semantic_quality"):
                    with st.expander("Semantic consensus audit", expanded=False):
                        st.json(event["semantic_quality"])
                else:
                    st.caption("Không join semantic consensus. Title-only join bị cấm.")


def render_update(update: dict[str, Any]) -> None:
    state = update["workflow_state"]
    events = update["monitoring_events"]
    review_count = sum(event["action"] == "Review Required" for event in events)
    st.markdown(f'<div class="cutoff-bar"><strong>Observed through `{update["as_of"]}`</strong><br>Update read-only; không tự thay card hoặc quyết định giao dịch.</div>', unsafe_allow_html=True)
    st.markdown("#### Trạng thái analyst")
    render_status(state)
    st.caption({"Initial": "Chưa có event tại cutoff.", "Watch": "Có evidence cần theo dõi.", "Review Required": "Có trigger cần analyst rà soát thủ công."}[state])
    cols = st.columns(3)
    cols[0].metric("Event quan sát", len(events)); cols[1].metric("Trigger cần rà soát", review_count); cols[2].metric("Cutoff", update["as_of"])
    st.markdown("#### Bản ghi ban đầu — đóng băng")
    ref = update["initial_reference"]
    st.write(f"Mã: `{ref.get('ticker', 'Chưa có')}` · Snapshot: `{ref.get('decision_date', 'Chưa có')}`")
    st.markdown("#### Thay đổi quan sát được")
    render_monitoring(events, update["as_of"])
    st.markdown("#### Câu hỏi analyst")
    for question in update["proposed_analyst_questions"]:
        st.write(f"- {question}")
