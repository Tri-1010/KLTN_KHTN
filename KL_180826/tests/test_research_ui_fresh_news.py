from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from research_ui.contracts import FreshInformationRequest
from research_ui import fresh_news
from research_ui.fresh_news import (
    FreshInformationError,
    FreshInformationJobService,
    _article_matches_ticker,
    _assert_no_advice_language,
    _safe_source_url,
    _validate_fresh_output,
)


def _write_pack(root: Path) -> None:
    generated = root / "reports" / "decision_support" / "generated"
    generated.mkdir(parents=True)
    (generated / "evidence_packs_initial.json").write_text(
        '[{"decision_id":"D1","ticker":"FPT","decision_date":"2025-01-01","technical_snapshot":{"rsi_end_q":55.0},"top_drivers":[{"feature":"rsi_end_q","value":55.0,"direction":"neutral","explanation":"within range"}],"news_evidence":[]}]', encoding="utf-8"
    )


def test_fresh_preview_uses_selected_pack_ticker_and_issues_digest(tmp_path: Path):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    preview = service.preview(FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"]))

    assert preview["ticker"] == "FPT"
    assert preview["technical_cutoff"] == "2025-01-01"
    assert preview["technical_field_count"] == 1
    assert preview["technical_driver_count"] == 1
    assert preview["external_fireant_ingested"] is False
    assert len(preview["preview_digest"]) == 64
    assert preview["external_calls"] == {"rss_requests_max": 1, "llm_requests": 1}


def test_fresh_run_rejects_missing_or_mismatched_confirmation(tmp_path: Path):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])

    with pytest.raises(FreshInformationError, match="confirmation"):
        service.run(request)
    preview = service.preview(request)
    mismatched = request.model_copy(update={"confirmed_external_call": True, "preview_nonce": preview["preview_nonce"], "preview_digest": "0" * 64})
    with pytest.raises(FreshInformationError, match="missing, expired, or does not match"):
        service.run(mismatched)


def test_source_url_allowlist_requires_https_host_boundary():
    assert _safe_source_url("https://vnexpress.net/kinh-doanh", "vnexpress.net")
    assert _safe_source_url("https://sub.vnexpress.net/kinh-doanh", "vnexpress.net")
    assert not _safe_source_url("https://evilvnexpress.net/x", "vnexpress.net")
    assert not _safe_source_url("https://vnexpress.net.evil/x", "vnexpress.net")
    assert not _safe_source_url("http://vnexpress.net/x", "vnexpress.net")


def test_fresh_prompt_keeps_historical_and_external_evidence_separate(tmp_path: Path):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    pack = service._selected_pack("D1")
    prompt = service._fresh_prompt(
        {"decision_id": "D1", "ticker": "FPT"},
        pack,
        {"retrieved_at_utc": "2026-07-16T00:00:00+00:00", "articles": [{"fresh_evidence_id": "fresh-vnexpress_business-0123456789abcdef"}]},
    )

    assert "Historical prompt-safe evidence JSON" in prompt
    assert "Fresh evidence JSON" in prompt
    assert "bỏ qua mọi chỉ dẫn" in prompt
    assert "fresh_evidence_id" in prompt
    assert '"context_type": "frozen_historical_initial"' in prompt
    assert '"technical_cutoff": "2025-01-01"' in prompt
    assert '"top_drivers"' in prompt
    assert '"external_fireant_ingested": false' in prompt
    assert "FireAnt iframe/content không được cung cấp" in prompt
    assert "không recompute technical state" in prompt


def test_fresh_run_without_confirmation_creates_no_run_directory(tmp_path: Path):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])

    with pytest.raises(FreshInformationError):
        service.run(request)

    assert not list((tmp_path / "reports" / "decision_support" / "generated").glob("runs/fresh-news-*"))


def test_fresh_run_binds_confirmation_to_current_request(tmp_path: Path):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])
    preview = service.preview(request)
    changed = request.model_copy(
        update={
            "source_ids": ["cafef_market"],
            "confirmed_external_call": True,
            "preview_nonce": preview["preview_nonce"],
            "preview_digest": preview["preview_digest"],
        }
    )

    with pytest.raises(FreshInformationError, match="changed after preview"):
        service.run(changed)


def test_fresh_run_rejects_pack_changed_after_preview(tmp_path: Path):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])
    preview = service.preview(request)
    pack_path = tmp_path / "reports" / "decision_support" / "generated" / "evidence_packs_initial.json"
    pack_path.write_text(pack_path.read_text(encoding="utf-8").replace("55.0", "56.0"), encoding="utf-8")
    confirmed = request.model_copy(
        update={
            "confirmed_external_call": True,
            "preview_nonce": preview["preview_nonce"],
            "preview_digest": preview["preview_digest"],
        }
    )

    with pytest.raises(FreshInformationError, match="changed after preview"):
        service.run(confirmed)


@pytest.mark.parametrize(
    "value",
    [
        "Nên mua FPT",
        "Nên bán FPT",
        "Nên tích lũy FPT",
        "Khuyến nghị: tăng tỷ trọng FPT",
        "Khuyến nghị giảm tỷ trọng FPT",
        "Should buy FPT",
        "Recommendation to sell FPT",
        "Giá mục tiêu 150000",
        "Target price 150000",
        "Portfolio allocation 20%",
        "Mua FPT ngay",
        "Bán FPT ngay",
        "Chốt lời FPT",
        "Cắt lỗ FPT",
        "Tích lũy FPT",
        "Overweight FPT",
        "Underweight FPT",
        "Buy FPT now",
        "Sell FPT today",
        "Accumulate FPT",
        "Take profits FPT",
        "Cut losses FPT",
        "Mua FPT",
        "Bán FPT",
        "Mua",
        "Bán!",
        "Mua **FPT**",
        "**Bán FPT!**",
        "- `Chốt lời`.",
        "### Cắt lỗ!",
        "Buy",
        "**Sell!**",
        "Overweight",
        "_Underweight_",
        "Buy: FPT.",
        "Sell (**FPT**)!",
        "- Đánh giá: Mua FPT ngay [fresh_evidence_id: fresh-vnexpress_business-0123456789abcdef]",
        "Kết luận: Sell FPT",
        "Hành động: (Mua FPT ngay)",
        'Conclusion: "Sell FPT"',
        "**Assessment:** `Buy FPT now`",
        "Action — [Underweight FPT]",
        "Thông tin trung lập. Buy FPT now",
        "Dữ liệu: **Bán FPT ngay**",
        "Tóm tắt; (Chốt lời FPT)",
        "Nhận định! 'Cut losses FPT'",
        "Đánh giá: Kết luận: Sell FPT",
    ],
)
def test_fresh_output_rejects_investment_advice(value: str):
    with pytest.raises(FreshInformationError, match="investment-advice"):
        _assert_no_advice_language(value)


@pytest.mark.parametrize(
    "value",
    [
        "FRT vận hành chuỗi bán lẻ FPT Shop",
        "Báo cáo đưa ra khuyến nghị bán lẻ cho ngành tiêu dùng",
        "Doanh thu bán hàng tăng",
        "doanh thu bán lẻ tăng 12%",
        "mua nguyên liệu cho nhà máy",
        "bán hàng qua kênh trực tuyến",
        "Doanh nghiệp mua nguyên liệu cho nhà máy",
        'Tiêu đề bài viết: "FPT mua nguyên liệu cho trung tâm dữ liệu"',
        'Tiêu đề bài viết: “Doanh thu bán lẻ FPT Shop phục hồi”',
        'Tiêu đề bài viết: "FPT mua nguyên liệu. Nhà máy tăng công suất"',
        'Bài báo viết: “Doanh nghiệp bán hàng qua kênh trực tuyến”',
        "Kết luận nghiên cứu: doanh thu bán lẻ tăng 12%",
        "Đánh giá hoạt động: doanh nghiệp mua nguyên liệu cho nhà máy",
        "Thông tin hiện tại cần được theo dõi · fresh-vnexpress_business-0123456789abcdef",
    ],
)
def test_fresh_output_allows_benign_market_language(value: str):
    _assert_no_advice_language(value)


def test_preview_reuses_nonce_for_same_session_scope_and_registry_is_bounded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path, session_binding="session-a")
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])
    with fresh_news._PREVIEW_LOCK:
        fresh_news._PREVIEWS.clear()
    first = service.preview(request)
    second = service.preview(request)
    assert second["preview_nonce"] == first["preview_nonce"]

    monkeypatch.setattr(fresh_news, "MAX_PREVIEWS", 2)
    service.preview(request.model_copy(update={"max_articles_per_source": 7}))
    service.preview(request.model_copy(update={"max_articles_per_source": 6}))
    with fresh_news._PREVIEW_LOCK:
        assert len(fresh_news._PREVIEWS) == 2


def test_preview_nonce_and_digest_are_isolated_between_sessions(tmp_path: Path):
    _write_pack(tmp_path)
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])
    with fresh_news._PREVIEW_LOCK:
        fresh_news._PREVIEWS.clear()

    first = FreshInformationJobService(tmp_path, session_binding="session-a").preview(request)
    second = FreshInformationJobService(tmp_path, session_binding="session-b").preview(request)

    assert first["preview_nonce"] != second["preview_nonce"]
    assert first["preview_digest"] != second["preview_digest"]
    assert "session-a" not in json.dumps(first)
    assert "session-b" not in json.dumps(second)


def test_preview_purges_expired_entries(tmp_path: Path):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])
    preview = service.preview(request)
    with fresh_news._PREVIEW_LOCK:
        fresh_news._PREVIEWS[preview["preview_nonce"]]["expires_at"] = datetime(2000, 1, 1, tzinfo=timezone.utc)
    replacement = service.preview(request)
    assert replacement["preview_nonce"] != preview["preview_nonce"]


def test_busy_fetch_lock_does_not_consume_valid_preview(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])
    preview = service.preview(request)
    confirmed = request.model_copy(update={"confirmed_external_call": True, "preview_nonce": preview["preview_nonce"], "preview_digest": preview["preview_digest"]})
    assert fresh_news._FETCH_LOCK.acquire(blocking=False)
    try:
        with pytest.raises(FreshInformationError, match="already running"):
            service.run(confirmed)
    finally:
        fresh_news._FETCH_LOCK.release()
    monkeypatch.setattr(service, "_run_confirmed", lambda current_request, scope: "ran")
    assert service.run(confirmed) == "ran"
    with pytest.raises(FreshInformationError, match="missing, expired"):
        service.run(confirmed)


def test_same_inputs_allow_second_intentional_preview_and_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path, session_binding="session-a")
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=["vnexpress_business"])
    runs: list[str] = []
    monkeypatch.setattr(service, "_run_confirmed", lambda current_request, scope: runs.append(current_request.preview_nonce) or "ran")

    first = service.preview(request)
    first_confirmed = request.model_copy(update={"confirmed_external_call": True, "preview_nonce": first["preview_nonce"], "preview_digest": first["preview_digest"]})
    assert service.run(first_confirmed) == "ran"

    second = service.preview(request)
    second_confirmed = request.model_copy(update={"confirmed_external_call": True, "preview_nonce": second["preview_nonce"], "preview_digest": second["preview_digest"]})
    assert service.run(second_confirmed) == "ran"

    assert second["preview_nonce"] != first["preview_nonce"]
    assert runs == [first["preview_nonce"], second["preview_nonce"]]


def test_ticker_relevance_uses_aliases_and_masks_other_issuer_aliases():
    aliases = {
        "FPT": ["FPT", "Tập đoàn FPT", "FPT Corporation", "công nghệ FPT"],
        "FRT": ["FRT", "FPT Retail", "FPT Shop", "Bán lẻ FPT"],
        "VBB": ["VBB", "Viet Capital Bank"],
        "BVB": ["BVB", "Viet Capital Bank"],
    }
    assert _article_matches_ticker("Tập đoàn FPT công bố kết quả", "FPT", aliases)
    assert _article_matches_ticker("FPT tăng trưởng", "FPT", aliases)
    assert not _article_matches_ticker("FPT Shop mở thêm cửa hàng", "FPT", aliases)
    assert _article_matches_ticker("FRT: FPT Shop mở thêm cửa hàng", "FRT", aliases)
    assert not _article_matches_ticker("Viet Capital Bank tăng vốn", "VBB", aliases)
    assert _article_matches_ticker("VBB: Viet Capital Bank tăng vốn", "VBB", aliases)
    assert not _article_matches_ticker("Dịch vụ fptcloud tăng trưởng", "FPT", aliases)


def test_output_validator_requires_citation_on_each_current_claim():
    evidence_id = "fresh-vnexpress_business-0123456789abcdef"
    valid = {evidence_id}
    historical = "## Bối cảnh lịch sử đã đóng băng\n- [HISTORICAL] RSI tại cutoff."
    current = f"## Thông tin hiện tại\n- Doanh thu tăng [{evidence_id}]"
    output = f"{historical}\n{current}\n- Biên lợi nhuận ổn định [{evidence_id}]"
    assert _validate_fresh_output(output, valid) == {evidence_id}

    with pytest.raises(FreshInformationError, match="same line"):
        _validate_fresh_output(f"{historical}\n{current}\n- Biên lợi nhuận ổn định", valid)
    with pytest.raises(FreshInformationError, match="one bullet"):
        _validate_fresh_output(f"{historical}\n## Thông tin hiện tại\nDoanh thu tăng [{evidence_id}]", valid)
    with pytest.raises(FreshInformationError, match="unknown"):
        _validate_fresh_output(f"{historical}\n## Thông tin hiện tại\n- Doanh thu tăng [fresh-cafef_market-ffffffffffffffff]", valid)
    with pytest.raises(FreshInformationError, match="historical-section"):
        _validate_fresh_output(f"## Bối cảnh lịch sử đã đóng băng\n- RSI tại cutoff.\n{current}", valid)
    with pytest.raises(FreshInformationError, match="only in the frozen historical section"):
        _validate_fresh_output(
            f"{historical}\n## Thông tin hiện tại\n- [HISTORICAL] Doanh thu tăng [{evidence_id}]",
            valid,
        )
    with pytest.raises(FreshInformationError, match="only in the frozen historical section"):
        _validate_fresh_output(
            f"{historical}\n## Thông tin hiện tại\n- Doanh thu tăng [HISTORICAL] [{evidence_id}]",
            valid,
        )


@pytest.mark.parametrize(
    "output",
    [
        "## Thông tin hiện tại\n- Claim [fresh-vnexpress_business-0123456789abcdef]",
        "## Bối cảnh lịch sử đã đóng băng\n- [HISTORICAL] Context",
        "## Bối cảnh lịch sử đóng băng\n- [HISTORICAL] Context\n## Thông tin hiện tại\n- Claim [fresh-vnexpress_business-0123456789abcdef]",
        "### Bối cảnh lịch sử đã đóng băng\n- [HISTORICAL] Context\n## Thông tin hiện tại\n- Claim [fresh-vnexpress_business-0123456789abcdef]",
        "## Bối cảnh lịch sử đã đóng băng\n- [HISTORICAL] Context\n## Thông tin hiện tại\n- Claim [fresh-vnexpress_business-0123456789abcdef]\n## Thông tin hiện tại\n- Claim [fresh-vnexpress_business-0123456789abcdef]",
        "## Thông tin hiện tại\n- Claim [fresh-vnexpress_business-0123456789abcdef]\n## Bối cảnh lịch sử đã đóng băng\n- [HISTORICAL] Context",
    ],
)
def test_output_validator_requires_exact_unique_ordered_headings(output: str):
    with pytest.raises(FreshInformationError, match="exact headings"):
        _validate_fresh_output(output, {"fresh-vnexpress_business-0123456789abcdef"})


class _FakeResponse:
    def __init__(self, chunks: list[bytes], *, redirect: bool = False):
        self.chunks = chunks
        self.is_redirect = redirect
        self.is_permanent_redirect = False

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int):
        assert chunk_size == 64 * 1024
        yield from self.chunks


def test_rss_fetch_keeps_stream_redirect_and_byte_defenses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    calls: list[dict[str, object]] = []
    rss = b"<rss><channel><item><title>FPT cong bo ket qua</title><description>FPT tang truong</description><link>https://vnexpress.net/fpt-ket-qua</link></item></channel></rss>"

    def get_ok(url: str, **kwargs):
        calls.append({"url": url, **kwargs})
        return _FakeResponse([rss])

    monkeypatch.setattr(fresh_news.requests, "get", get_ok)
    articles, attempt = service._fetch_rss("vnexpress_business", "FPT", 8, datetime.now(timezone.utc))
    assert len(articles) == 1
    assert attempt["state"] == "completed"
    assert calls[0]["allow_redirects"] is False
    assert calls[0]["stream"] is True
    assert calls[0]["timeout"] == (5, 15)

    monkeypatch.setattr(fresh_news.requests, "get", lambda *args, **kwargs: _FakeResponse([], redirect=True))
    articles, attempt = service._fetch_rss("vnexpress_business", "FPT", 8, datetime.now(timezone.utc))
    assert articles == []
    assert attempt["state"] == "failed"
    assert "redirects are not allowed" in attempt["error"]

    monkeypatch.setattr(fresh_news, "MAX_RESPONSE_BYTES", 3)
    monkeypatch.setattr(fresh_news.requests, "get", lambda *args, **kwargs: _FakeResponse([b"1234"]))
    articles, attempt = service._fetch_rss("vnexpress_business", "FPT", 8, datetime.now(timezone.utc))
    assert articles == []
    assert attempt["state"] == "failed"
    assert "byte cap" in attempt["error"]


def _stub_fetch(state: str, articles: list[dict[str, object]] | None = None):
    def fetch(source_id: str, ticker: str, limit: int, fetched_at: datetime):
        return articles or [], {"source_id": source_id, "url": f"https://{source_id}.example/rss", "state": state, "articles_found": len(articles or []), "error": "boom" if state == "failed" else None}
    return fetch


def _run_confirmed_request(service: FreshInformationJobService, source_ids: list[str]) -> tuple[object, Path]:
    request = FreshInformationRequest(decision_id="D1", provider="gemini", model="gemini-2.5-pro", source_ids=source_ids)
    preview = service.preview(request)
    confirmed = request.model_copy(update={"confirmed_external_call": True, "preview_nonce": preview["preview_nonce"], "preview_digest": preview["preview_digest"]})
    result = service.run(confirmed)
    return result, service.root / result.run_directory


def test_all_source_failures_return_failed_result_and_honest_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    monkeypatch.setattr(service, "_fetch_rss", _stub_fetch("failed"))
    result, run_dir = _run_confirmed_request(service, ["vnexpress_business", "cafef_market"])
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert result.state == "failed"
    assert manifest["state"] == "failed"
    assert {failure["source_id"] for failure in manifest["failures"]} == {"vnexpress_business", "cafef_market"}
    assert "result_artifact" not in manifest


def test_successful_fetch_with_zero_relevant_articles_is_partial_no_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_pack(tmp_path)
    service = FreshInformationJobService(tmp_path)
    monkeypatch.setattr(service, "_fetch_rss", _stub_fetch("completed"))
    result, run_dir = _run_confirmed_request(service, ["vnexpress_business"])
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert result.state == "partial"
    assert manifest["state"] == "partial"
    assert manifest["no_evidence"] is True
    assert manifest["snapshot_sha256"] == hashlib.sha256((run_dir / "snapshot.json").read_bytes()).hexdigest()
    result_ref = manifest["result_artifact"]
    assert result_ref["path"] == (run_dir / "result.json").relative_to(tmp_path).as_posix()
    assert result_ref["sha256"] == hashlib.sha256((run_dir / "result.json").read_bytes()).hexdigest()
