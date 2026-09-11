"""Research Command Center landing view from validated historical bundle zones."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from ..assets.theme import CARD_TYPE_LABELS, QUALITY_LABELS, STATUS_COLORS, STATUS_TOKENS
from ..summary import summarize_evaluation
from .fireant_vnindex import render_fireant_vnindex


def render_overview(repository, selected_id: str, selected_periods: list[str], as_of: date, *, enable_external_context: bool = False) -> None:
    scope = repository.dashboard_scope(as_of, selected_periods)
    workflow_rows = scope["workflow_by_period"]
    quality_rows = scope["evidence_quality_by_period"]
    states = {state: sum(row[state] for row in workflow_rows) for state in ("Initial", "Watch", "Review Required")}
    flagged_events = sum(len(events) for events in scope["events_by_id"].values())

    st.subheader("Research Command Center")
    if enable_external_context:
        st.caption("Validated historical bundle không chứa live market data; chart ngoài bên dưới chỉ display-only, không phải khuyến nghị đầu tư.")
        render_fireant_vnindex()
    else:
        st.caption("OFFLINE MODE · Chỉ dùng validated historical bundle; FireAnt và dữ liệu ngoài đang tắt.")
    metrics = st.columns(4)
    metrics[0].metric("Hồ sơ trong scope", len(scope["candidates"]))
    metrics[1].metric("Kỳ represented", len({row["period_id"] for row in scope["candidates"]}))
    metrics[2].metric("Monitoring event có cờ", flagged_events)
    metrics[3].metric("Cần rà soát", states["Review Required"])

    st.markdown("#### Vòng đời decision record")
    st.markdown(
        "**Chọn hồ sơ** — initial an toàn · **Giải thích** — evidence point-in-time · "
        "**Theo dõi** — event đến cutoff · **Cập nhật** — read-only analyst state · "
        "**Hậu kiểm** — post-hoc outcome riêng biệt"
    )
    st.caption("Preset demo chỉ chọn bằng metadata `select, monitor`; không dùng outcome hoặc rubric để chọn case.")

    workflow_col, quality_col = st.columns(2)
    with workflow_col:
        _render_workflow_chart(workflow_rows, as_of)
    with quality_col:
        _render_evidence_quality_chart(quality_rows, as_of)

    st.markdown("#### Trạng thái quality và demo")
    left, right = st.columns(2)
    with left:
        st.markdown("**Confidence ghép mã trong scope**")
        confidence: dict[str, int] = {}
        for candidate in scope["candidates"]:
            value = str((candidate.get("data_quality") or {}).get("ticker_matching_confidence") or "unavailable")
            confidence[value] = confidence.get(value, 0) + 1
        for value, count in sorted(confidence.items()):
            st.write(f"{QUALITY_LABELS.get(value.lower(), value)}: **{count}**")
    with right:
        preset = next((item for item in repository.demo_presets() if item["decision_id"] == selected_id), None)
        if preset:
            st.success(f"Preset đang chọn: **{preset['label']}** · `{selected_id}`")
        else:
            st.info(f"Hồ sơ tự chọn: `{selected_id}`")
        for state, count in states.items():
            token = STATUS_TOKENS[state]
            st.write(f"{token['icon']} **{token['label']}**: {count}")

    _render_evaluation_mirror(repository)


def _render_workflow_chart(rows: list[dict[str, object]], as_of: date) -> None:
    st.markdown("#### Workflow state theo kỳ")
    st.caption(f"State hồ sơ tại historical cutoff `{as_of.isoformat()}`. Đây là count decision record, không phải số lượng event hay hiệu quả đầu tư.")
    if not rows:
        st.info("Không có hồ sơ phù hợp cutoff/kỳ đã chọn.")
        return
    frame = pd.DataFrame(rows).set_index("period_id")
    st.bar_chart(frame[["Initial", "Watch", "Review Required"]], stack=True, color=[STATUS_COLORS["Initial"], STATUS_COLORS["Watch"], STATUS_COLORS["Review Required"]])
    st.caption("○ Trạng thái ban đầu · ◐ Theo dõi · ! Cần rà soát")
    with st.expander("Bảng dữ liệu workflow chart", expanded=False):
        st.dataframe(frame.reset_index(), hide_index=True, width="stretch")


def _render_evidence_quality_chart(rows: list[dict[str, object]], as_of: date) -> None:
    st.markdown("#### Full-evidence field availability")
    st.caption(
        f"Availability tại `{as_of.isoformat()}` = (full text + summary + key facts) / (3 × article evidence). "
        "Record không có evidence hiển thị riêng, không bị gán 0%."
    )
    evaluable = [row for row in rows if row["availability_pct"] is not None]
    if not evaluable:
        st.info("Không có article evidence đủ điều kiện để tính availability.")
    else:
        frame = pd.DataFrame(evaluable).set_index("period_id")
        st.line_chart(frame[["availability_pct"]], color="#2563EB")
        st.caption("Thang đo: 0–100%. Bảng dữ liệu bên dưới ghi rõ tử số/mẫu số để audit.")
    with st.expander("Bảng dữ liệu evidence chart", expanded=False):
        st.dataframe(rows, hide_index=True, width="stretch")


def _render_evaluation_mirror(repository) -> None:
    st.markdown("#### Card-quality evaluation")
    st.warning("Rubric đo chất lượng card, không đo return, alpha, causal impact hoặc provider superiority.")
    bundles = [bundle for bundle in repository.evaluations() if bundle["records"]]
    if not bundles:
        st.info("Chưa có điểm rubric hoàn chỉnh. Không hiển thị KPI bằng 0 hoặc điểm thay thế.")
        return
    selected_id = st.selectbox("Evaluation run tóm tắt", [bundle["evaluation_run_id"] for bundle in bundles], key="overview_evaluation_run")
    bundle = next(item for item in bundles if item["evaluation_run_id"] == selected_id)
    st.caption(f"Judge: `{bundle['records'][0]['judge_provider']}` · Chỉ so sánh card type trong run/judge này.")
    rows = summarize_evaluation(bundle["records"])
    st.dataframe(
        [
            {
                "Loại card": CARD_TYPE_LABELS.get(row["card_type"], row["card_type"]),
                "Số card": row["card_count"],
                "Overall TB": row["overall_mean"],
                "Hallucination nghiêm trọng": row["major_hallucination_count"],
                "Thiếu evidence reference": row["missing_evidence_ref_count"],
            }
            for row in rows
        ],
        hide_index=True,
        width="stretch",
    )
    st.caption("Biểu đồ rubric chi tiết nằm tại Đánh giá LLM; bảng này không xếp hạng các run/provider.")
