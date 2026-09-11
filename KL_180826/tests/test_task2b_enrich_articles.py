import pandas as pd

from pipeline import task2b_enrich_articles as t2b


def test_pending_cap_existing_is_not_reusable():
    cfg = {"retry_failed": False, "extractor_version": t2b.EXTRACTOR_VERSION}
    assert not t2b._is_reusable_existing({"extraction_status": "pending_max_articles_cap"}, cfg)
    assert not t2b._is_reusable_existing({"extraction_status": "pending_resume"}, cfg)
    assert not t2b._is_reusable_existing({"extraction_status": ""}, cfg)
    assert not t2b._is_reusable_existing({"extraction_status": "ok", "full_text_available": True}, cfg)
    assert t2b._is_reusable_existing({"extraction_status": "ok", "full_text_available": True, "extractor_version": t2b.EXTRACTOR_VERSION}, cfg)
    assert not t2b._is_reusable_existing({"extraction_status": "fetch_failed"}, cfg)
    assert not t2b._is_reusable_existing({"extraction_status": "failed"}, cfg)
    assert t2b._is_reusable_existing({"extraction_status": "fetch_failed", "extractor_version": t2b.EXTRACTOR_VERSION}, cfg)
    assert t2b._is_reusable_existing({"extraction_status": "failed", "extractor_version": t2b.EXTRACTOR_VERSION}, cfg)
    assert not t2b._is_reusable_existing({"extraction_status": "fetch_failed", "extractor_version": t2b.EXTRACTOR_VERSION}, {"retry_failed": True, "extractor_version": t2b.EXTRACTOR_VERSION})
    assert not t2b._is_reusable_existing({"extraction_status": "failed", "extractor_version": t2b.EXTRACTOR_VERSION}, {"retry_failed": True, "extractor_version": t2b.EXTRACTOR_VERSION})


def test_reusable_existing_honors_version_and_retry_flags():
    assert not t2b._is_reusable_existing(
        {"extraction_status": "ok", "full_text_available": True, "extractor_version": "old"},
        {"extractor_version": "new"},
    )
    assert not t2b._is_reusable_existing(
        {"extraction_status": "failed", "extractor_version": "old"},
        {"extractor_version": "new"},
    )
    assert not t2b._is_reusable_existing(
        {"extraction_status": "partial", "extractor_version": "new"},
        {"extractor_version": "new", "retry_partial": True},
    )
    assert not t2b._is_reusable_existing(
        {"extraction_status": "restricted", "extractor_version": "new"},
        {"extractor_version": "new", "retry_restricted": True},
    )


def test_detail_headers_disable_brotli():
    headers = t2b.detail_headers_for_url("https://vietnambiz.vn/a")
    assert headers["Accept-Encoding"] == "gzip, deflate"
    assert "br" not in headers["Accept-Encoding"]
    assert headers["Referer"] == "https://vietnambiz.vn/"


def test_extract_article_text_ignores_nav_login_when_body_exists():
    html = """
    <html><body><nav><a>Đăng nhập</a></nav>
    <article><p>Đây là đoạn nội dung chính đủ dài về doanh nghiệp, lợi nhuận, kế hoạch kinh doanh và triển vọng thị trường trong năm nay.</p>
    <p>Đoạn thứ hai bổ sung thêm bối cảnh tài chính, dòng tiền, cổ tức và những yếu tố hỗ trợ cho cổ phiếu.</p></article>
    </body></html>
    """
    out = t2b.extract_article_text(html, url="https://cafef.vn/a", source="cafef", min_full_text_chars=80)
    assert out["extraction_status"] == "ok"
    assert not out["paywall_or_restricted"]
    assert "nội dung chính" in out["full_text"]


def test_extract_article_text_marks_strong_paywall_restricted():
    html = "<html><body><article>Vui lòng đăng nhập để xem tiếp nội dung dành cho hội viên.</article></body></html>"
    out = t2b.extract_article_text(html, url="https://example.com/a", source="cafef")
    assert out["extraction_status"] == "restricted"
    assert out["paywall_or_restricted"]


def test_extract_article_text_uses_jsonld_article_body():
    body = "Đây là articleBody từ JSON-LD với nhiều thông tin về doanh thu, lợi nhuận và kế hoạch kinh doanh của doanh nghiệp trong kỳ báo cáo. " * 3
    html = f'<html><head><script type="application/ld+json">{{"@type":"NewsArticle","articleBody":"{body}"}}</script></head><body></body></html>'
    out = t2b.extract_article_text(html, url="https://example.com/a", source="cafef")
    assert out["extraction_status"] == "ok"
    assert out["extractor_strategy"] == "jsonld"
    assert "articleBody" in out["full_text"]


def test_build_output_expands_duplicate_ticker_rows():
    source_df = pd.DataFrame([
        {"date": "2025-01-01", "title": "A", "description": "D", "url": "https://cafef.vn/a", "source": "cafef", "ticker": "AAA", "match_confidence": "exact"},
        {"date": "2025-01-01", "title": "A", "description": "D", "url": "https://cafef.vn/a", "source": "cafef", "ticker": "BBB", "match_confidence": "exact"},
    ])
    enriched_by_url = {
        "https://cafef.vn/a": {
            **{col: "" for col in t2b.ENRICHED_COLUMNS},
            "url": "https://cafef.vn/a",
            "source": "cafef",
            "full_text_available": True,
            "extraction_status": "ok",
        }
    }

    out = t2b._build_output_df(source_df, enriched_by_url)

    assert len(out) == 2
    assert out["ticker"].tolist() == ["AAA", "BBB"]
    assert out["full_text_available"].tolist() == [True, True]


def test_pending_row_has_resume_status_and_summary():
    row = pd.Series({
        "date": "2025-01-01",
        "title": "Doanh nghiệp báo lãi 100 tỷ đồng",
        "description": "Lợi nhuận tăng mạnh trong quý.",
        "url": "https://example.com/a",
        "source": "example",
        "ticker": "AAA",
        "match_confidence": "exact",
    })

    pending = t2b._pending_row(row, "pending_resume")

    assert pending["extraction_status"] == "pending_resume"
    assert pending["article_summary"]
    assert pending["event_type_enriched"] == "earnings"
    assert pending["content_hash"]


def test_longest_container_fallback_prefers_article_body():
    article_text = "Đây là nội dung phân tích kết quả kinh doanh, lợi nhuận, doanh thu và kế hoạch đầu tư của doanh nghiệp trong quý mới. " * 5
    sidebar_text = "Tin đọc nhiều ngắn. " * 5
    html = f"""
    <html><body>
    <div class="sidebar"><p>{sidebar_text}</p></div>
    <div class="main-detail"><p>{article_text}</p></div>
    </body></html>
    """

    out = t2b.extract_article_text(html, url="https://example.com/a", source="unknown")

    assert out["extraction_status"] == "ok"
    assert out["extractor_strategy"] == "longest_container"
    assert "kết quả kinh doanh" in out["full_text"]
    assert "Tin đọc nhiều" not in out["full_text"]


def test_cafef_candidate_detail_urls_adds_root_variant():
    candidates = t2b._cafef_candidate_detail_urls(
        "https://cafef.vn/du-lieu/VNM-1/vnm-thong-bao-kiem-toan.chn?utm_source=du-lieu"
    )

    assert candidates[0] == "https://cafef.vn/du-lieu/VNM-1/vnm-thong-bao-kiem-toan.chn"
    assert "https://cafef.vn/vnm-thong-bao-kiem-toan.chn" in candidates


def test_cafef_api_payload_builds_partial_text_from_title_subtitle():
    row = pd.Series({"title": "Tin VNM", "description": "Mô tả ngắn", "url": "https://cafef.vn/du-lieu/VNM-1/a.chn", "date": "2025-01-01"})
    item = {
        "Title": "Tin VNM",
        "SubTitle": "Doanh nghiệp công bố kết quả kinh doanh quý mới.",
        "DeployDate": "/Date(1735689600000)/",
        "LinkDetail": "/du-lieu/VNM-1/a.chn",
    }

    out = t2b._cafef_item_to_extracted(item, row, min_full_text_chars=300)

    assert out["extraction_status"] == "partial"
    assert out["extractor_strategy"] == "cafef_api_payload"
    assert "Tin VNM" in out["full_text"]
    assert "kết quả kinh doanh" in out["full_text"]


def test_cafef_api_payload_prefers_content_field():
    body = "<p>Doanh nghiệp ghi nhận doanh thu, lợi nhuận và dòng tiền tăng trưởng tích cực trong quý này.</p>" * 5
    row = pd.Series({"title": "Tin VNM", "description": "Mô tả", "url": "https://cafef.vn/du-lieu/VNM-1/a.chn", "date": "2025-01-01"})
    item = {"Title": "Tin VNM", "Content": body, "LinkDetail": "/du-lieu/VNM-1/a.chn"}

    out = t2b._cafef_item_to_extracted(item, row, min_full_text_chars=120)

    assert out["extraction_status"] == "ok"
    assert "<p>" not in out["full_text"]
    assert "dòng tiền tăng trưởng" in out["full_text"]


def test_enrich_cafef_uses_api_fallback_when_detail_disabled(monkeypatch):
    row = pd.Series({
        "date": "2025-01-01",
        "title": "Tin VNM",
        "description": "Mô tả ngắn",
        "url": "https://cafef.vn/du-lieu/VNM-1/a.chn",
        "source": "cafef",
        "ticker": "VNM",
        "match_confidence": "exact",
    })
    item = {"Title": "Tin VNM", "SubTitle": "Nội dung từ API CafeF", "LinkDetail": "/du-lieu/VNM-1/a.chn"}

    def fail_if_called(*args, **kwargs):
        raise AssertionError("detail fetch should be skipped for CafeF disclosure URLs")

    monkeypatch.setattr(t2b, "_fetch_extract_detail", fail_if_called)
    monkeypatch.setattr(t2b, "_get_cafef_api_item_for_row", lambda *args, **kwargs: item)

    out = t2b.enrich_single_article(row, t2b.RateLimiter(), {
        "max_text_chars": 12000,
        "summary_max_chars": 1200,
        "min_full_text_chars": 300,
        "store_full_text": True,
        "extractor_version": t2b.EXTRACTOR_VERSION,
        "cafef_try_detail_for_disclosures": False,
    })

    assert out["full_text_available"] is True
    assert out["extractor_strategy"] == "cafef_api_payload"
    assert out["extraction_status"] == "partial"


def test_enrich_cafef_tries_root_variant_before_api_fallback(monkeypatch):
    row = pd.Series({
        "date": "2025-01-01",
        "title": "Tin VNM",
        "description": "Mô tả ngắn",
        "url": "https://cafef.vn/du-lieu/VNM-1/a.chn",
        "source": "cafef",
        "ticker": "VNM",
        "match_confidence": "exact",
    })
    calls = []

    def fake_fetch(url, source, rate_limiter, cfg):
        calls.append(url)
        if url == "https://cafef.vn/a.chn":
            return {
                "full_text": "Nội dung đầy đủ về doanh thu, lợi nhuận và triển vọng doanh nghiệp. " * 5,
                "lead": "",
                "author": "",
                "published_at_detail": "",
                "canonical_url": url,
                "extraction_status": "ok",
                "paywall_or_restricted": False,
                "extractor_strategy": "selector",
            }
        return None

    monkeypatch.setattr(t2b, "_fetch_extract_detail", fake_fetch)
    monkeypatch.setattr(t2b, "_get_cafef_api_item_for_row", lambda *args, **kwargs: None)

    out = t2b.enrich_single_article(row, t2b.RateLimiter(), {
        "max_text_chars": 12000,
        "summary_max_chars": 1200,
        "min_full_text_chars": 300,
        "store_full_text": True,
        "extractor_version": t2b.EXTRACTOR_VERSION,
        "cafef_try_detail_for_disclosures": True,
    })

    assert calls == ["https://cafef.vn/du-lieu/VNM-1/a.chn", "https://cafef.vn/a.chn"]
    assert out["extraction_status"] == "ok"
    assert out["extractor_strategy"].startswith("cafef_detail_url_variant")


def test_domain_normalization_strips_www():
    assert t2b._domain_for_url("https://www.cafef.vn/a") == "cafef.vn"
    assert t2b._domain_for_url("https://vietstock.vn/a") == "vietstock.vn"


def test_enrich_ktck_uses_listing_metadata_without_detail_fetch(monkeypatch):
    row = pd.Series({
        "date": "2026-03-11",
        "title": "co phieu nhom vingroup but pha manh vn index lay lai moc 1 700 diem 1433515.html",
        "description": "",
        "url": "https://kinhtechungkhoan.vn/co-phieu-nhom-vingroup-but-pha-manh-vn-index-lay-lai-moc-1-700-diem-1433515.html",
        "source": "kinhtechungkhoan",
        "ticker": "VIC",
        "match_confidence": "exact",
    })

    def fail_if_called(*args, **kwargs):
        raise AssertionError("KTCK dead detail URLs should not be fetched")

    monkeypatch.setattr(t2b, "_fetch_extract_detail", fail_if_called)

    out = t2b.enrich_single_article(row, t2b.RateLimiter(), {
        "max_text_chars": 12000,
        "summary_max_chars": 1200,
        "store_full_text": True,
        "extractor_version": t2b.EXTRACTOR_VERSION,
    })

    assert out["full_text_available"] is True
    assert out["extraction_status"] == "partial"
    assert out["extractor_strategy"] == "ktck_listing_metadata"
    assert "vingroup" in out["full_text"]
