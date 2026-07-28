"""Dense, trust-zone-safe selected-record panel for Market workspace."""

from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from ..assets.theme import QUALITY_LABELS
from .shell import render_status


def selected_record_view(candidate: dict[str, Any], detail: dict[str, Any], events: list[dict[str, Any]], as_of: date) -> dict[str, Any]:
    """Prepare only select/initial/monitor fields; review and external data never enter."""
    state = "Review Required" if any(event["action"] == "Review Required" for event in events) else "Watch" if events else "Initial"
    quality = detail["data_quality_flags"]
    return {
        "ticker": candidate["ticker"],
        "decision_id": candidate["decision_id"],
        "period_id": candidate["period_id"],
        "decision_date": candidate["decision_date"],
        "as_of": as_of.isoformat(),
        "state": state,
        "probability": detail["ml_signal"]["pred_proba_up"],
        "rank": detail["ml_signal"]["rank_in_period"],
        "news_coverage": quality.get("news_coverage"),
        "matching_confidence": quality.get("ticker_matching_confidence"),
        "missing_fields": list(quality.get("missing_fields") or []),
        "watch_count": sum(event["action"] == "Watch" for event in events),
        "review_required_count": sum(event["action"] == "Review Required" for event in events),
        "initial_evidence_count": len(detail.get("news_evidence") or []),
    }


def render_selected_record_panel(view: dict[str, Any]) -> None:
    """Render compact selected-record context without post-hoc or external content."""
    st.markdown('<div class="workspace-panel selected-record-panel">', unsafe_allow_html=True)
    st.markdown(f"### {view['ticker']}")
    st.caption(f"`{view['decision_id']}` · {view['period_id']} · Snapshot `{view['decision_date']}`")
    render_status(view["state"])
    st.caption(f"Historical cutoff: `{view['as_of']}`")

    metrics = st.columns(2)
    metrics[0].metric("Xác suất mô hình", f"{float(view['probability']):.4f}")
    metrics[1].metric("Thứ hạng historical", view["rank"])
    st.caption("Metadata mô hình historical, không phải khuyến nghị đầu tư.")

    st.markdown("#### Evidence quality")
    st.markdown(
        f"- Coverage: **{QUALITY_LABELS.get(str(view['news_coverage']).lower(), view['news_coverage'])}**\n"
        f"- Matching: **{QUALITY_LABELS.get(str(view['matching_confidence']).lower(), view['matching_confidence'])}**\n"
        f"- Evidence initial: **{view['initial_evidence_count']}**"
    )
    if view["missing_fields"]:
        st.warning("Thiếu: " + ", ".join(str(field) for field in view["missing_fields"]))

    st.markdown("#### Monitoring historical")
    alerts = st.columns(2)
    alerts[0].metric("Watch", view["watch_count"])
    alerts[1].metric("Cần rà soát", view["review_required_count"])
    st.caption("Counts chỉ gồm events quan sát được qua historical cutoff.")
    st.markdown("</div>", unsafe_allow_html=True)


def historical_technical_view(detail: dict[str, Any]) -> dict[str, Any]:
    """Project frozen initial technical fields without monitor, review or external data."""
    provenance = detail.get("provenance") or {}
    return {
        "decision_id": detail["decision_id"],
        "ticker": detail["ticker"],
        "decision_date": detail["decision_date"],
        "period_id": detail["period_id"],
        "technical_snapshot": dict(detail.get("technical_snapshot") or {}),
        "top_drivers": [dict(driver) for driver in detail.get("top_drivers") or []],
        "provenance": {
            key: provenance.get(key)
            for key in ("name", "path", "sha256", "zone", "generated_at_utc", "provenance_status")
            if provenance.get(key) is not None
        },
    }


def render_historical_technical_analysis(view: dict[str, Any]) -> None:
    """Render frozen technical context with explicit cutoff and provenance."""
    snapshot = view["technical_snapshot"]
    st.markdown('<div class="workspace-panel historical-technical-panel">', unsafe_allow_html=True)
    st.markdown("#### Phân tích kỹ thuật tại snapshot lịch sử")
    st.caption(
        f"FROZEN HISTORICAL INITIAL · Technical cutoff `{view['decision_date']}` · FireAnt current display "
        "bị loại khỏi phân tích, evidence và model input."
    )

    metrics = st.columns(3)
    metrics[0].metric("RSI cuối kỳ", _format_value(snapshot.get("rsi_end_q"), "number"))
    metrics[1].metric("MACD histogram", _format_value(snapshot.get("macd_hist_mean_q"), "number"))
    metrics[2].metric("Giá / SMA20", _format_value(snapshot.get("price_vs_sma20"), "percent"))

    labels = {
        "return_q": ("Lợi suất kỳ", "percent"),
        "return_mean_daily": ("Lợi suất ngày trung bình", "percent"),
        "return_std_daily": ("Độ lệch chuẩn lợi suất ngày", "percent"),
        "volatility_q": ("Biến động kỳ", "percent"),
        "price_range_q": ("Biên độ giá kỳ", "percent"),
        "volume_mean_q": ("Khối lượng trung bình", "number"),
        "volume_change_q": ("Thay đổi khối lượng", "percent"),
        "sma20_end": ("SMA20 cuối kỳ", "price"),
        "ema20_end": ("EMA20 cuối kỳ", "price"),
        "price_vs_sma20": ("Giá so với SMA20", "percent"),
        "rsi_mean_q": ("RSI trung bình", "number"),
        "rsi_end_q": ("RSI cuối kỳ", "number"),
        "macd_hist_mean_q": ("MACD histogram trung bình", "number"),
        "bb_position_q": ("Vị trí Bollinger", "number"),
        "return_prev_q": ("Lợi suất kỳ trước", "percent"),
        "return_2q_ago": ("Lợi suất hai kỳ trước", "percent"),
    }
    rows = []
    for key, value in snapshot.items():
        label, kind = labels.get(key, (key, "number"))
        rows.append({"Chỉ báo": label, "Trường": key, "Giá trị": _format_value(value, kind), "Loại": kind})
    st.dataframe(rows, hide_index=True, width="stretch")

    st.markdown("**Rule-based historical drivers**")
    drivers = view["top_drivers"]
    if drivers:
        st.dataframe(
            [
                {
                    "Feature": driver.get("feature"),
                    "Value": _format_value(driver.get("value"), "number"),
                    "Direction": driver.get("direction"),
                    "Explanation": driver.get("explanation"),
                }
                for driver in drivers
            ],
            hide_index=True,
            width="stretch",
        )
    else:
        st.info("Chưa có driver lịch sử đã validate.")

    provenance = view["provenance"]
    with st.expander("Provenance technical snapshot", expanded=False):
        st.json(provenance)
    st.markdown("</div>", unsafe_allow_html=True)


def _format_value(value: Any, kind: str) -> str:
    if value is None:
        return "Chưa có"
    numeric = float(value)
    if kind == "percent":
        return f"{numeric:.2%}"
    if kind == "price":
        return f"{numeric:,.2f}"
    return f"{numeric:,.4f}"


def render_evidence_summary(detail: dict[str, Any]) -> None:
    """Show a short point-in-time evidence list; full detail remains in Explain."""
    st.markdown('<div class="workspace-panel">', unsafe_allow_html=True)
    st.markdown("#### Evidence tại snapshot")
    st.caption(f"POINT-IN-TIME · OUTCOME EXCLUDED · News cutoff `{detail['guardrails'].get('news_cutoff', 'Chưa có')}`")
    evidence_rows = detail.get("news_evidence") or []
    if not evidence_rows:
        st.info("Không có news evidence trong biến thể initial này.")
    else:
        for evidence in evidence_rows[:3]:
            st.markdown(f"**{evidence['evidence_id']} · {evidence['source']} · {evidence['published_at']}**")
            st.write(evidence["title"])
            if evidence.get("article_summary"):
                st.caption(evidence["article_summary"])
    st.markdown("</div>", unsafe_allow_html=True)
