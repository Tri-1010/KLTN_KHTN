"""EvidenceTrace Research Command Center entry point.

Run: streamlit run research_ui/app.py -- --bundle ui_artifacts/current
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from research_ui.assets.theme import PAGE_LABELS, VARIANT_LABELS
from research_ui.components.cards import render_cards, render_evaluation
from research_ui.components.evidence import render_initial_detail
from research_ui.components.fireant_selected_ticker import render_fireant_selected_ticker
from research_ui.components.fireant_vnindex import render_fireant_vnindex
from research_ui.components.market_workspace import (
    historical_technical_view,
    render_evidence_summary,
    render_historical_technical_analysis,
    render_selected_record_panel,
    selected_record_view,
)
from research_ui.components.monitoring import render_monitoring, render_update
from research_ui.components.overview import render_overview
from research_ui.components.provenance import render_provenance
from research_ui.components.shell import configure_page, render_context_strip, render_shell, render_workflow_rail
from research_ui.contracts import FreshInformationRequest, LiveJobRequest
from research_ui.fresh_news import FreshInformationError, FreshInformationJobService
from research_ui.live_jobs import LiveJobError, LiveJobService
from research_ui.repository import BundleRepositoryError, open_bundle
from scripts.llm_provider import UI_MODEL_ALLOWLIST


def resolve_bundle() -> str:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--bundle", default=os.environ.get("EVIDENCETRACE_BUNDLE", "ui_artifacts/current"))
    args, _ = parser.parse_known_args()
    return str(Path(args.bundle).resolve())


def external_context_enabled() -> bool:
    """Require an explicit opt-in before rendering or preparing external features."""
    return os.environ.get("EVIDENCETRACE_ENABLE_LIVE", "0").strip().lower() in {"1", "true", "yes"}


def _apply_preset_selection() -> None:
    """Synchronize global record context when a safe demo preset changes."""
    preset = st.session_state.get("context_preset")
    eligible = set(st.session_state.get("context_eligible_ids", []))
    if preset and preset != "manual" and preset in eligible:
        st.session_state["context_decision_id"] = preset


def _request_fingerprint(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _expiry_passed(expires_at: object) -> bool:
    if not expires_at:
        return False
    try:
        return datetime.fromisoformat(str(expires_at).replace("Z", "+00:00")) <= datetime.now(timezone.utc)
    except ValueError:
        return True


def _session_preview_identity() -> str:
    state_key = "_opaque_preview_session_id"
    identity = st.session_state.get(state_key)
    if not isinstance(identity, str) or not identity:
        identity = uuid.uuid4().hex
        st.session_state[state_key] = identity
    return identity


def _displayed_preview(
    state_key: str,
    fingerprint_payload: dict[str, Any],
    create_preview: Callable[[], dict[str, Any]],
    *,
    ttl: timedelta | None = None,
) -> tuple[dict[str, Any], bool]:
    fingerprint = _request_fingerprint(fingerprint_payload)
    stored = st.session_state.get(state_key)
    if (
        isinstance(stored, dict)
        and stored.get("request_fingerprint") == fingerprint
        and isinstance(stored.get("preview"), dict)
        and not _expiry_passed(stored.get("expires_at_utc"))
    ):
        return stored["preview"], False
    preview = create_preview()
    expires_at = preview.get("expires_at_utc")
    if not expires_at and ttl is not None:
        expires_at = (datetime.now(timezone.utc) + ttl).isoformat()
    st.session_state[state_key] = {
        "request_fingerprint": fingerprint,
        "preview": preview,
        "expires_at_utc": expires_at,
    }
    return preview, True


def main() -> None:
    configure_page()
    try:
        repository = open_bundle(resolve_bundle())
    except BundleRepositoryError as exc:
        st.error(f"Không mở được bundle đã validate: {exc}")
        st.code("python scripts/build_research_ui_bundle.py --output-dir ui_artifacts/current")
        st.stop()

    render_shell(repository.manifest)
    enable_external_context = external_context_enabled()
    selected_id, selected_periods, as_of = _render_global_context(repository)
    candidate = next(row for row in repository.candidates() if str(row["decision_id"]) == selected_id)
    render_context_strip(selected_id, str(candidate["decision_date"]), "full_evidence", as_of)

    pages = ["Overview", "Select", "Explain", "Monitor", "Update", "Review", "Evaluation", "Provenance"]
    page = st.sidebar.radio("Không gian nghiên cứu", pages, format_func=lambda value: PAGE_LABELS[value])
    render_workflow_rail(page, selected_id, as_of)
    if enable_external_context:
        _render_live_job_panel(repository, selected_id)
    else:
        with st.sidebar.expander("Nâng cao: gọi LLM qua API ngoài", expanded=False):
            st.caption("Offline mode đang bật. Đặt `EVIDENCETRACE_ENABLE_LIVE=1` và cấu hình `.env` để bật tính năng ngoài.")

    if page == "Overview":
        render_overview(repository, selected_id, selected_periods, as_of, enable_external_context=enable_external_context)
    elif page == "Select":
        _render_select(repository, selected_periods, as_of)
    elif page == "Explain":
        mode = st.radio("Biến thể đầu vào", ["full_evidence", "ml_only"], format_func=lambda value: VARIANT_LABELS[value], horizontal=True)
        render_initial_detail(repository.initial(selected_id, mode))
        render_cards(repository._read_json("cards.json"), selected_id)
    elif page == "Monitor":
        _render_monitor(repository, selected_id, as_of, enable_external_context=enable_external_context)
    elif page == "Update":
        _render_update(repository, selected_id, as_of)
    elif page == "Review":
        _render_review(repository.review(selected_id))
    elif page == "Evaluation":
        render_evaluation(repository.evaluations())
    else:
        _render_provenance(repository)


def _render_global_context(repository) -> tuple[str, list[str], date]:
    st.markdown("#### Bộ lọc historical")
    candidates = repository.candidates()
    periods = repository.periods()
    presets = repository.demo_presets()
    preset_options = ["manual"] + [item["decision_id"] for item in presets]
    preset_labels = {"manual": "Tự chọn hồ sơ"} | {item["decision_id"]: f"{item['label']} · {item['decision_id']}" for item in presets}
    columns = st.columns([1.25, 1.15, 1.8, 1.2])
    selected_periods = columns[1].multiselect("Kỳ dữ liệu", periods, default=periods, key="context_periods")
    scoped = [row for row in candidates if str(row["period_id"]) in selected_periods]
    displayed_periods = selected_periods
    if not scoped:
        st.warning("Không có hồ sơ trong các kỳ đã chọn. Hiển thị toàn bộ kỳ để tiếp tục.")
        scoped = candidates
        displayed_periods = periods
    by_id = {str(row["decision_id"]): row for row in scoped}
    option_ids = list(by_id)
    st.session_state["context_eligible_ids"] = option_ids
    chosen_preset = columns[0].selectbox(
        "Kịch bản demo", preset_options, format_func=lambda value: preset_labels[value], key="context_preset", on_change=_apply_preset_selection
    )
    if chosen_preset != "manual" and chosen_preset in by_id:
        st.session_state["context_decision_id"] = chosen_preset
    if st.session_state.get("context_decision_id") not in by_id:
        st.session_state["context_decision_id"] = option_ids[0]
    selected_id = columns[2].selectbox(
        "Hồ sơ · đồng bộ FireAnt, technical và LLM",
        option_ids,
        index=option_ids.index(st.session_state["context_decision_id"]),
        format_func=lambda value: f"{by_id[value]['ticker']} · {value}",
        key="context_decision_id",
    )
    minimum, maximum = repository.monitor_date_bounds(selected_id)
    as_of = columns[3].date_input("Dữ liệu quan sát đến", value=maximum, min_value=minimum, max_value=maximum, key="context_as_of")
    st.caption(
        f"Phạm vi áp dụng: `{', '.join(displayed_periods)}` · Hồ sơ: `{selected_id}` · historical cutoff: `{as_of.isoformat()}`. "
        "Decision/event sau cutoff không xuất hiện trong Tổng quan, Theo dõi hoặc Cập nhật."
    )
    return selected_id, displayed_periods, as_of


def _render_live_job_panel(repository, decision_id: str) -> None:
    with st.sidebar.expander("Nâng cao: gọi LLM qua API ngoài", expanded=False):
        st.caption("Tùy chọn ngoài luồng demo offline. Tối đa hai card/job, có thể phát sinh chi phí; output nằm trong run directory riêng.")
        provider = st.selectbox("Nhà cung cấp", ["gemini", "anthropic", "deepseek"], key="live_provider")
        model = st.selectbox("Model", UI_MODEL_ALLOWLIST[provider], key="live_model")
        variant = st.selectbox("Biến thể đầu vào", ["full_evidence", "ml_only"], format_func=lambda value: VARIANT_LABELS[value], key="live_variant")
        include_score = st.checkbox("Chấm rubric sau khi tạo", value=True, key="live_score")
        confirmed = st.checkbox("Tôi xác nhận gửi yêu cầu nghiên cứu qua API ngoài và chấp nhận chi phí có thể phát sinh.", key="live_confirm")
        request = LiveJobRequest(decision_ids=[decision_id], variant=variant, provider=provider, model=model, score=include_score, confirmed_external_call=confirmed)
        service = LiveJobService(
            bundle_repository=repository,
            max_cards=2,
            session_binding=_session_preview_identity(),
        )
        fingerprint_payload = {
            "decision_ids": [decision_id],
            "provider": provider,
            "model": model,
            "variant": variant,
            "score": include_score,
        }
        try:
            preview, preview_refreshed = _displayed_preview(
                "live_displayed_preview",
                fingerprint_payload,
                lambda: service.preview(request),
                ttl=timedelta(minutes=10),
            )
            st.caption(
                f"Kiểm tra leakage: `{preview['outcome_leakage_check']}` · Số card: {preview['cards_requested']} · "
                "Technical đóng băng theo `decision_date` · FireAnt ingested: `false`."
            )
            st.caption(
                f"Preview bind token: `{preview['preview_nonce']}` · digest: `{preview['preview_digest']}` · "
                f"hết hạn `{preview['expires_at_utc']}`."
            )
            with st.expander("Chi tiết hash prompt/pack", expanded=False):
                st.json(preview["details"])
            request = request.model_copy(
                update={
                    "preview_digest": preview["preview_digest"],
                    "preview_nonce": preview["preview_nonce"],
                }
            )
        except LiveJobError as exc:
            st.error(str(exc))
            return
        run_clicked = st.button("Chạy job đã xác nhận", disabled=not confirmed, key="live_run")
        if run_clicked and preview_refreshed:
            st.warning("Preview vừa được tạo mới. Kiểm tra identity hiển thị rồi bấm chạy lại.")
        elif run_clicked:
            try:
                with st.spinner("Đang gọi provider ngoài. Không đóng phiên này."):
                    status = service.run(request)
            except Exception as exc:
                st.error(f"Không thể khởi tạo live job: {exc}")
                return
            finally:
                st.session_state.pop("live_displayed_preview", None)
            if status.state == "completed":
                st.success(f"Hoàn thành: `{status.run_directory}`")
            else:
                st.error(f"Job thất bại trung thực: {status.message}")
            st.caption(f"Job ID: `{status.job_id}` · trạng thái: `{status.state}`")


def _render_select(repository, selected_periods: list[str], as_of: date) -> None:
    st.subheader("Khám phá hồ sơ nghiên cứu lịch sử")
    ticker_filter = st.text_input("Lọc mã cổ phiếu").strip().upper()
    quality_filter = st.checkbox("Chỉ hiện confidence ghép mã hỗn hợp/thấp")
    scope = repository.dashboard_scope(as_of, selected_periods)
    rows = []
    for row in scope["candidates"]:
        quality = row["data_quality"]
        if ticker_filter and ticker_filter not in str(row["ticker"]).upper():
            continue
        if quality_filter and str(quality.get("ticker_matching_confidence", "")).lower() not in {"mixed", "partial", "none", "low"}:
            continue
        events = scope["events_by_id"][str(row["decision_id"])]
        state = "Review Required" if any(event["action"] == "Review Required" for event in events) else "Watch" if events else "Initial"
        rows.append({
            "Mã": row["ticker"], "Kỳ": row["period_id"], "Ngày snapshot": row["decision_date"], "Hồ sơ": row["decision_id"],
            "Xác suất mô hình": round(float(row["pred_proba_up"]), 4), "Thứ hạng": row["rank_in_period"],
            "Coverage tin": quality.get("news_coverage"), "Confidence ghép mã": quality.get("ticker_matching_confidence"), "Trạng thái theo dõi": state,
        })
    st.caption(f"{len(rows)} hồ sơ trong historical scope. Ứng viên mô hình là metadata lịch sử, không phải khuyến nghị đầu tư.")
    st.dataframe(rows, hide_index=True, width="stretch")


def _render_monitor(repository, decision_id: str, as_of: date, *, enable_external_context: bool = False) -> None:
    candidate = next(row for row in repository.candidates() if str(row["decision_id"]) == decision_id)
    detail = repository.initial(decision_id)
    events = repository.monitor(decision_id, as_of)
    ticker = str(candidate["ticker"])
    workspace = selected_record_view(candidate, detail, events, as_of)
    technical = historical_technical_view(detail)
    allowed_tickers = {str(row["ticker"]).upper() for row in repository.candidates()}

    center, context = st.columns([8, 4], gap="medium")
    with center:
        if enable_external_context:
            render_fireant_selected_ticker(ticker, allowed_tickers)
        else:
            st.caption("OFFLINE MODE · FireAnt display-only context đang tắt.")
    with context:
        render_selected_record_panel(workspace)

    technical_col, timeline = st.columns([5, 7], gap="medium")
    with technical_col:
        render_historical_technical_analysis(technical)
    with timeline:
        render_monitoring(events, as_of.isoformat())

    evidence, current = st.columns([5, 7], gap="medium")
    with evidence:
        render_evidence_summary(detail)
    with current:
        if enable_external_context:
            with st.expander("Thông tin hiện tại và LLM", expanded=False):
                _render_fresh_information_panel(repository, decision_id, ticker)
        else:
            st.caption("OFFLINE MODE · RSS, LLM và dữ liệu thị trường bên ngoài đang tắt.")

    if enable_external_context:
        with st.expander("VN-INDEX · Bối cảnh thị trường hiện tại từ FireAnt", expanded=False):
            render_fireant_vnindex()


def _render_fresh_information_panel(repository, decision_id: str, ticker: str) -> None:
    st.markdown('<div class="trust-strip"><strong>EXTERNAL SNAPSHOT · NOT PART OF VALIDATED HISTORICAL BUNDLE</strong><br>Tin mới và output LLM không thay evidence lịch sử, timeline monitoring, decision state, review hay evaluation.</div>', unsafe_allow_html=True)
    st.caption(f"Hồ sơ read-only: `{decision_id}` · Ticker derive server-side: `{ticker}`. Tối đa 2 RSS sources, 8 bài/source, 1 LLM call.")
    provider = st.selectbox("Provider snapshot", ["gemini", "anthropic", "deepseek"], key="fresh_provider")
    model = st.selectbox("Model snapshot", UI_MODEL_ALLOWLIST[provider], key="fresh_model")
    source_ids = st.multiselect("Nguồn RSS allowlist", ["vnexpress_business", "cafef_market"], default=["vnexpress_business", "cafef_market"], key="fresh_sources")
    max_articles_per_source = st.number_input("Số bài tối đa mỗi nguồn", min_value=1, max_value=10, value=8, step=1, key="fresh_max_articles")
    if not source_ids:
        st.info("Chọn ít nhất một nguồn RSS để tạo preview.")
        return
    service = FreshInformationJobService(
        bundle_repository=repository,
        session_binding=_session_preview_identity(),
    )
    base_request = FreshInformationRequest(
        decision_id=decision_id,
        provider=provider,
        model=model,
        source_ids=source_ids,
        max_articles_per_source=max_articles_per_source,
    )
    fingerprint_payload = {
        "decision_id": decision_id,
        "provider": provider,
        "model": model,
        "source_ids": sorted(source_ids),
        "max_articles_per_source": base_request.max_articles_per_source,
    }
    try:
        preview, preview_refreshed = _displayed_preview(
            "fresh_displayed_preview",
            fingerprint_payload,
            lambda: service.preview(base_request),
        )
    except FreshInformationError as exc:
        st.error(str(exc))
        return
    if preview["ticker"] != ticker.upper():
        st.error("Ticker UI không khớp prompt-safe historical pack. Dừng external snapshot.")
        return
    st.caption(
        f"Technical cutoff `{preview['technical_cutoff']}` · {preview['technical_field_count']} fields · "
        f"{preview['technical_driver_count']} drivers · FireAnt ingested: `{str(preview['external_fireant_ingested']).lower()}`."
    )
    st.caption(
        f"Network tối đa: {preview['external_calls']['rss_requests_max']} RSS requests · "
        f"{preview['external_calls']['llm_requests']} LLM call · hết hạn `{preview['expires_at_utc']}`"
    )
    st.caption(
        f"Preview bind token: `{preview['preview_nonce']}` · digest: `{preview['preview_digest']}`. "
        "Run chỉ dùng đúng preview này; thay đổi request hoặc historical pack sẽ bị từ chối."
    )
    confirmed = st.checkbox("Tôi xác nhận fetch RSS bên ngoài và gọi LLM cho snapshot hiện tại; có thể phát sinh chi phí.", key="fresh_confirm")
    request = base_request.model_copy(update={"confirmed_external_call": confirmed, "preview_digest": preview["preview_digest"], "preview_nonce": preview["preview_nonce"]})
    run_clicked = st.button("Tạo external snapshot", disabled=not confirmed, key="fresh_run")
    if run_clicked and preview_refreshed:
        st.warning("Preview vừa được tạo mới. Kiểm tra nonce/digest hiển thị rồi bấm chạy lại.")
    elif run_clicked:
        try:
            with st.spinner("Đang fetch nguồn allowlist và gọi LLM. Không đóng phiên này."):
                result = service.run(request)
        except Exception as exc:
            st.error(f"Fresh snapshot thất bại trung thực: {exc}")
            return
        finally:
            st.session_state.pop("fresh_displayed_preview", None)
        if result.result_markdown:
            st.success(f"Snapshot {result.state}: `{result.run_directory}`")
            st.markdown(result.result_markdown, unsafe_allow_html=False)
        else:
            st.warning(f"Snapshot {result.state}, chưa có bài phù hợp. Run: `{result.run_directory}`")
        st.caption(f"Snapshot ID: `{result.snapshot_id}` · Retrieved: `{result.retrieved_at_utc}` · Evidence IDs: `{', '.join(result.cited_evidence_ids) or 'Không có'}`")


def _render_update(repository, decision_id: str, as_of: date) -> None:
    st.subheader("Cập nhật hồ sơ lịch sử")
    render_update(repository.update(decision_id, as_of))


def _render_review(review: dict[str, object]) -> None:
    st.subheader("Hậu kiểm outcome")
    if not review["holding_period_complete"]:
        st.info("Chưa thể hậu kiểm: holding period chưa hoàn tất.")
        return
    st.markdown('<div class="posthoc-banner">POST-HOC · REVIEW ONLY<br>Outcome chỉ xuất hiện sau kỳ nắm giữ; không có ở Select, Explain, Monitor, Update hoặc initial card.</div>', unsafe_allow_html=True)
    reference = review["initial_snapshot_reference"]
    outcome = review.get("post_hoc_outcome") or {}
    cols = st.columns(3)
    cols[0].metric("Mã", reference.get("ticker", "Chưa có"))
    cols[1].metric("Ngày snapshot", reference.get("decision_date", "Chưa có"))
    cols[2].metric("Lợi suất hậu kiểm", f"{float(outcome.get('realized_period_return', 0)):.2%}" if outcome.get("realized_period_return") is not None else "Chưa có")
    st.markdown("#### Nhãn outcome")
    st.write(outcome.get("outcome_label") or "Chưa có")
    st.caption(str(review.get("review_narrative") or ""))
    with st.expander("Dữ liệu audit thô — chỉ hậu kiểm", expanded=False):
        st.json(review)


def _render_provenance(repository) -> None:
    st.subheader("Provenance & audit")
    validation = repository.validation()
    passed = validation.get("leakage_validation_passed") is True
    st.markdown(
        f'<div class="trust-strip"><strong>Bundle validation: {"PASSED" if passed else "FAILED"}</strong> · '
        f'Initial records: `{validation.get("initial_records", "Chưa có")}` · '
        f'Review records: `{validation.get("review_records", "Chưa có")}` · '
        f'Semantic records: `{validation.get("semantic_records", "Chưa có")}`</div>',
        unsafe_allow_html=True,
    )
    provenance = repository.provenance()
    for reference in provenance["source_artifacts"]:
        render_provenance(reference, reference["name"])
    with st.expander("Kết quả validation bundle thô", expanded=False):
        st.json(validation)


if __name__ == "__main__":
    main()
