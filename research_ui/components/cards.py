"""Decision-card and run-scoped rubric renderers."""

from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from ..assets.theme import CARD_TYPE_COLORS, CARD_TYPE_LABELS
from ..policy import RUBRIC_WARNING
from ..summary import summarize_evaluation


RUBRIC_COLUMNS = (
    ("faithfulness_mean", "Faithfulness"),
    ("hallucination_control_mean", "Hallucination control"),
    ("ml_explanation_mean", "ML explanation"),
    ("risk_awareness_mean", "Risk awareness"),
    ("monitoring_usefulness_mean", "Monitoring usefulness"),
    ("clarity_usefulness_mean", "Clarity/usefulness"),
    ("overall_mean", "Overall"),
)


def render_cards(cards: list[dict[str, Any]], decision_id: str) -> None:
    selected = [card for card in cards if card["decision_id"] == decision_id]
    st.subheader("Các biến thể decision card")
    st.caption("Card sinh bởi model là nội dung nghiên cứu chưa được xác minh độc lập. Kiểm tra claim qua bằng chứng gốc.")
    if not selected:
        st.info("Chưa có card đã validate cho hồ sơ này.")
        return
    for card in selected:
        label = CARD_TYPE_LABELS.get(card["card_type"], card["card_type"])
        with st.expander(f"{label} · {card['producer_run_id']}", expanded=False):
            st.caption(f"Provider: `{card['provider']}` · Model yêu cầu: `{card.get('requested_model')}` · Model phản hồi: `{card.get('response_model')}`")
            if card.get("vendor"):
                st.caption(f"Vendor phản hồi: `{card['vendor']}`")
            st.markdown(card["body_markdown"], unsafe_allow_html=False)
            st.caption(f"Prompt hash: `{card.get('prompt_sha256') or 'Chưa có'}` · Pack hash: `{card.get('pack_sha256') or 'Chưa có'}`")


def render_evaluation(evaluation_bundles: list[dict[str, Any]]) -> None:
    st.subheader("Đánh giá chất lượng decision card")
    st.warning(RUBRIC_WARNING)
    if not evaluation_bundles:
        st.info("Chưa có evaluation run đã publish.")
        return
    options = [bundle["evaluation_run_id"] for bundle in evaluation_bundles]
    selected_id = st.selectbox("Evaluation run", options, key="evaluation_run")
    bundle = next(item for item in evaluation_bundles if item["evaluation_run_id"] == selected_id)
    judge = bundle["records"][0]["judge_provider"] if bundle["records"] else "Chưa có"
    st.markdown(f'<div class="trust-strip"><strong>Run-scoped comparison</strong> · Run: `{selected_id}` · Judge: `{judge}`<br>So sánh chỉ hợp lệ bên trong run và điều kiện judge này.</div>', unsafe_allow_html=True)
    if not bundle["records"]:
        st.info("Run này chưa có điểm rubric hoàn chỉnh. Không hiển thị điểm bằng 0 hoặc thay thế.")
        return
    summary = summarize_evaluation(bundle["records"])
    _render_rubric_chart(summary)
    st.dataframe(
        [
            {
                "Loại card": CARD_TYPE_LABELS.get(row["card_type"], row["card_type"]),
                "Số card": row["card_count"],
                "Faithfulness TB": row["faithfulness_mean"],
                "ML explanation TB": row["ml_explanation_mean"],
                "Risk awareness TB": row["risk_awareness_mean"],
                "Overall TB": row["overall_mean"],
                "Hallucination nghiêm trọng": row["major_hallucination_count"],
                "Thiếu evidence reference": row["missing_evidence_ref_count"],
            }
            for row in summary
        ],
        hide_index=True,
        width="stretch",
    )
    with st.expander("Chi tiết audit từng score", expanded=False):
        st.dataframe(bundle["records"], hide_index=True, width="stretch")


def _render_rubric_chart(summary: list[dict[str, Any]]) -> None:
    st.markdown("#### Rubric theo card type")
    st.caption("Thang 1–5 cố định. Màu cố định theo card type, không theo provider/run/rank. Có bảng dữ liệu thay thế bên dưới.")
    rows = [
        {
            "card_type": CARD_TYPE_LABELS.get(item["card_type"], item["card_type"]),
            "criterion": label,
            "mean_score": item[column],
        }
        for item in summary
        for column, label in RUBRIC_COLUMNS
    ]
    domain = [CARD_TYPE_LABELS[item["card_type"]] for item in summary]
    colors = [CARD_TYPE_COLORS[item["card_type"]] for item in summary]
    chart = (
        alt.Chart(pd.DataFrame(rows))
        .mark_bar()
        .encode(
            x=alt.X("criterion:N", title=None, sort=[label for _, label in RUBRIC_COLUMNS], axis=alt.Axis(labelAngle=-30)),
            xOffset="card_type:N",
            y=alt.Y("mean_score:Q", title="Điểm rubric trung bình", scale=alt.Scale(domain=[1, 5]), axis=alt.Axis(values=[1, 2, 3, 4, 5])),
            color=alt.Color("card_type:N", title="Loại card", scale=alt.Scale(domain=domain, range=colors)),
            tooltip=["criterion:N", "card_type:N", alt.Tooltip("mean_score:Q", format=".2f", title="Điểm TB")],
        )
        .properties(height=340)
    )
    st.altair_chart(chart, width="stretch")
    totals = st.columns(3)
    totals[0].metric("Tổng card", sum(item["card_count"] for item in summary))
    totals[1].metric("Hallucination nghiêm trọng", sum(item["major_hallucination_count"] for item in summary))
    totals[2].metric("Thiếu evidence reference", sum(item["missing_evidence_ref_count"] for item in summary))
    with st.expander("Bảng dữ liệu rubric chart", expanded=False):
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
