"""
Unit tests for TASK 2 base scraping infrastructure.

Tests cover:
- Rate limiting enforcement (including 1.5s for Vietstock) — Req 2.6
- Retry logic with mocked HTTP errors — Req 2.7
- Duplicate URL detection — Req 2.8
- Browser-like headers — Req 2.11
- Article validation
- Safe CSV writing
"""

import os
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from pipeline.task2_scrape import (
    BROWSER_HEADERS,
    RateLimiter,
    fetch_with_retry,
    is_duplicate,
    load_existing_urls,
    safe_write_csv,
    validate_article,
    _output_path_for,
)


# ---------------------------------------------------------------------------
# RateLimiter tests
# ---------------------------------------------------------------------------

class TestRateLimiter:
    """Tests for per-domain rate limiting (Req 2.6)."""

    def test_default_delay_at_least_one_second(self):
        """First request should pass immediately; second should be delayed."""
        rl = RateLimiter(default_delay=1.0, vietstock_delay=1.5)
        url = "https://cafef.vn/some-page"

        start = time.monotonic()
        rl.wait(url)
        first_elapsed = time.monotonic() - start
        # First request should not wait
        assert first_elapsed < 0.1

        start = time.monotonic()
        rl.wait(url)
        second_elapsed = time.monotonic() - start
        # Second request should wait ~1 second
        assert second_elapsed >= 0.9

    def test_vietstock_gets_longer_delay(self):
        """Vietstock domain should enforce 1.5s delay."""
        rl = RateLimiter(default_delay=1.0, vietstock_delay=1.5)
        url = "https://vietstock.vn/VNM"

        rl.wait(url)  # first — no wait

        start = time.monotonic()
        rl.wait(url)
        elapsed = time.monotonic() - start
        assert elapsed >= 1.4  # ~1.5s

    def test_different_domains_independent(self):
        """Requests to different domains should not block each other."""
        rl = RateLimiter(default_delay=1.0, vietstock_delay=1.5)

        rl.wait("https://cafef.vn/page1")

        # Immediately request a different domain — should not wait
        start = time.monotonic()
        rl.wait("https://tinnhanhchungkhoan.vn/page1")
        elapsed = time.monotonic() - start
        assert elapsed < 0.1

    def test_same_domain_different_paths(self):
        """Different paths on the same domain share the rate limit."""
        rl = RateLimiter(default_delay=1.0, vietstock_delay=1.5)

        rl.wait("https://cafef.vn/page1")

        start = time.monotonic()
        rl.wait("https://cafef.vn/page2")
        elapsed = time.monotonic() - start
        assert elapsed >= 0.9


# ---------------------------------------------------------------------------
# fetch_with_retry tests
# ---------------------------------------------------------------------------

class TestFetchWithRetry:
    """Tests for retry logic with exponential backoff (Req 2.7)."""

    @patch("pipeline.task2_scrape.requests.get")
    def test_success_on_first_attempt(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_with_retry(
            "https://cafef.vn/test", max_retries=3, timeout=10
        )

        assert result is not None
        assert result.status_code == 200
        assert mock_get.call_count == 1

    @patch("pipeline.task2_scrape.time.sleep")
    @patch("pipeline.task2_scrape.requests.get")
    def test_retries_on_network_error(self, mock_get, mock_sleep):
        """Should retry up to max_retries times on network errors."""
        mock_get.side_effect = requests.ConnectionError("Connection refused")

        result = fetch_with_retry(
            "https://cafef.vn/test", max_retries=3, backoff_factor=2, timeout=10
        )

        assert result is None
        assert mock_get.call_count == 3
        # Backoff delays: 2^0=1, 2^1=2 (only 2 sleeps for 3 attempts)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1

    @patch("pipeline.task2_scrape.time.sleep")
    @patch("pipeline.task2_scrape.requests.get")
    def test_success_after_transient_failure(self, mock_get, mock_sleep):
        """Should succeed if a later attempt works."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_get.side_effect = [
            requests.ConnectionError("timeout"),
            mock_response,
        ]

        result = fetch_with_retry(
            "https://cafef.vn/test", max_retries=3, timeout=10
        )

        assert result is not None
        assert result.status_code == 200
        assert mock_get.call_count == 2

    @patch("pipeline.task2_scrape.requests.get")
    def test_http_error_triggers_retry(self, mock_get):
        """HTTP 503 should trigger retry."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "503 Service Unavailable"
        )
        mock_get.return_value = mock_response

        with patch("pipeline.task2_scrape.time.sleep"):
            result = fetch_with_retry(
                "https://cafef.vn/test", max_retries=3, timeout=10
            )

        assert result is None
        assert mock_get.call_count == 3

    @patch("pipeline.task2_scrape.requests.get")
    def test_uses_browser_headers_by_default(self, mock_get):
        """Requests should include browser-like User-Agent (Req 2.11)."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetch_with_retry("https://cafef.vn/test", max_retries=1, timeout=10)

        _, kwargs = mock_get.call_args
        assert kwargs["headers"] == BROWSER_HEADERS
        assert "User-Agent" in kwargs["headers"]
        assert "Mozilla" in kwargs["headers"]["User-Agent"]

    @patch("pipeline.task2_scrape.requests.get")
    def test_rate_limiter_called_before_request(self, mock_get):
        """Rate limiter wait() should be called before each HTTP request."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        rl = MagicMock(spec=RateLimiter)

        fetch_with_retry(
            "https://cafef.vn/test",
            rate_limiter=rl,
            max_retries=1,
            timeout=10,
        )

        rl.wait.assert_called_once_with("https://cafef.vn/test")


# ---------------------------------------------------------------------------
# Duplicate detection tests
# ---------------------------------------------------------------------------

class TestDuplicateDetection:
    """Tests for URL-based duplicate detection (Req 2.8)."""

    def test_is_duplicate_true(self):
        existing = {"https://cafef.vn/article-1.chn", "https://cafef.vn/article-2.chn"}
        assert is_duplicate("https://cafef.vn/article-1.chn", existing) is True

    def test_is_duplicate_false(self):
        existing = {"https://cafef.vn/article-1.chn"}
        assert is_duplicate("https://cafef.vn/article-new.chn", existing) is False

    def test_load_existing_urls_from_csv(self, tmp_path):
        csv_path = str(tmp_path / "articles.csv")
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-02"],
            "title": ["Title A", "Title B"],
            "url": ["https://cafef.vn/a.chn", "https://cafef.vn/b.chn"],
            "source": ["cafef", "cafef"],
        })
        df.to_csv(csv_path, index=False)

        urls = load_existing_urls(csv_path)
        assert urls == {"https://cafef.vn/a.chn", "https://cafef.vn/b.chn"}

    def test_load_existing_urls_missing_file(self, tmp_path):
        urls = load_existing_urls(str(tmp_path / "nonexistent.csv"))
        assert urls == set()

    def test_load_existing_urls_empty_file(self, tmp_path):
        csv_path = str(tmp_path / "empty.csv")
        pd.DataFrame(columns=["url"]).to_csv(csv_path, index=False)

        urls = load_existing_urls(csv_path)
        assert urls == set()


# ---------------------------------------------------------------------------
# Article validation tests
# ---------------------------------------------------------------------------

class TestValidateArticle:
    def test_valid_article(self):
        article = {
            "date": "2024-01-01",
            "title": "Test article",
            "url": "https://cafef.vn/test.chn",
            "source": "cafef",
            "description": "Some description",
        }
        assert validate_article(article) is True

    def test_missing_title(self):
        article = {
            "date": "2024-01-01",
            "title": "",
            "url": "https://cafef.vn/test.chn",
            "source": "cafef",
        }
        assert validate_article(article) is False

    def test_missing_url(self):
        article = {
            "date": "2024-01-01",
            "title": "Test",
            "source": "cafef",
        }
        assert validate_article(article) is False

    def test_missing_date(self):
        article = {
            "title": "Test",
            "url": "https://cafef.vn/test.chn",
            "source": "cafef",
        }
        assert validate_article(article) is False


# ---------------------------------------------------------------------------
# Safe CSV writing tests
# ---------------------------------------------------------------------------

class TestSafeWriteCsv:
    def test_writes_csv_correctly(self, tmp_path):
        df = pd.DataFrame({
            "date": ["2024-01-01"],
            "title": ["Test"],
            "url": ["https://cafef.vn/test.chn"],
            "source": ["cafef"],
        })
        path = str(tmp_path / "output.csv")
        safe_write_csv(df, path)

        assert os.path.isfile(path)
        loaded = pd.read_csv(path)
        assert len(loaded) == 1
        assert loaded["title"].iloc[0] == "Test"

    def test_no_temp_file_left_behind(self, tmp_path):
        df = pd.DataFrame({"a": [1]})
        path = str(tmp_path / "output.csv")
        safe_write_csv(df, path)

        # .tmp file should not exist after successful write
        assert not os.path.isfile(path + ".tmp")

    def test_creates_parent_directories(self, tmp_path):
        path = str(tmp_path / "sub" / "dir" / "output.csv")
        df = pd.DataFrame({"a": [1]})
        safe_write_csv(df, path)
        assert os.path.isfile(path)


# ---------------------------------------------------------------------------
# Output path mapping tests
# ---------------------------------------------------------------------------

class TestOutputPathFor:
    def test_cafef_path(self):
        assert _output_path_for("cafef", "VNM") == "data/news/cafef/VNM_cafef.csv"

    def test_vietstock_path(self):
        assert (
            _output_path_for("vietstock", "FPT")
            == "data/news/vietstock/FPT_vietstock.csv"
        )

    def test_tnck_path(self):
        assert _output_path_for("tnck", "ALL") == "data/news/tnck/tnck_raw.csv"


# ---------------------------------------------------------------------------
# CafeF scraper tests (Task 4.2)
# ---------------------------------------------------------------------------

from pipeline.task2_scrape import (
    _parse_cafef_date,
    _parse_cafef_api_date,
    _parse_cafef_page,
    _parse_cafef_api_page,
    scrape_cafef,
    CAFEF_BASE_URL,
    CAFEF_PAGE_URL,
    CAFEF_NEWS_API,
)


class TestParseCafefDate:
    """Tests for CafeF date parsing."""

    def test_iso_datetime(self):
        assert _parse_cafef_date("2024-01-15T10:30:00") == "2024-01-15"

    def test_iso_date_only(self):
        assert _parse_cafef_date("2024-01-15") == "2024-01-15"

    def test_vietnamese_slash_format(self):
        assert _parse_cafef_date("15/01/2024") == "2024-01-15"

    def test_vietnamese_slash_with_time(self):
        assert _parse_cafef_date("15/01/2024 10:30") == "2024-01-15"

    def test_dash_format(self):
        assert _parse_cafef_date("15-01-2024") == "2024-01-15"

    def test_iso_with_space_time(self):
        assert _parse_cafef_date("2024-01-15 10:30:00") == "2024-01-15"

    def test_empty_string_returns_none(self):
        assert _parse_cafef_date("") is None

    def test_none_returns_none(self):
        assert _parse_cafef_date(None) is None

    def test_whitespace_only_returns_none(self):
        assert _parse_cafef_date("   ") is None

    def test_unparseable_returns_none(self):
        assert _parse_cafef_date("not a date") is None

    def test_embedded_iso_date(self):
        """Should extract date from a string containing an ISO date."""
        assert _parse_cafef_date("Published 2024-03-20 at noon") == "2024-03-20"

    def test_embedded_vn_date(self):
        """Should extract date from a string containing a VN-format date."""
        assert _parse_cafef_date("Ngày 20/03/2024") == "2024-03-20"


class TestParseCafefPage:
    """Tests for CafeF HTML page parsing."""

    def _make_html(self, articles_html: str) -> str:
        """Wrap article HTML in a minimal page structure."""
        return f"""
        <html><body>
        <div class="list-news">
            <ul>{articles_html}</ul>
        </div>
        </body></html>
        """

    def test_extracts_article_with_title_and_date(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/article-123.chn" title="VNM tăng mạnh">VNM tăng mạnh</a>
            <p class="sapo">Cổ phiếu VNM tăng 5% trong phiên hôm nay.</p>
            <span class="time">2024-03-15T10:00:00</span>
        </li>
        """)
        articles, should_stop = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["title"] == "VNM tăng mạnh"
        assert articles[0]["date"] == "2024-03-15"
        assert articles[0]["description"] == "Cổ phiếu VNM tăng 5% trong phiên hôm nay."
        assert articles[0]["url"] == "https://cafef.vn/article-123.chn"
        assert articles[0]["source"] == "cafef"

    def test_skips_duplicate_urls(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="https://cafef.vn/article-1.chn" title="Article 1">Article 1</a>
            <span class="time">2024-03-15T10:00:00</span>
        </li>
        """)
        existing = {"https://cafef.vn/article-1.chn"}
        articles, _ = _parse_cafef_page(html, existing, "2022-01-01")
        assert len(articles) == 0

    def test_stops_on_old_articles(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/old-article.chn" title="Old article">Old article</a>
            <span class="time">2021-06-15T10:00:00</span>
        </li>
        """)
        articles, should_stop = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 0
        assert should_stop is True

    def test_handles_missing_description(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/no-desc.chn" title="No description">No description</a>
            <span class="time">2024-01-10T08:00:00</span>
        </li>
        """)
        articles, _ = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["description"] == ""

    def test_handles_absolute_url(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="https://cafef.vn/full-url-article.chn"
               title="Full URL">Full URL</a>
            <span class="time">2024-02-20T12:00:00</span>
        </li>
        """)
        articles, _ = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["url"] == "https://cafef.vn/full-url-article.chn"

    def test_multiple_articles(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/a1.chn" title="Article 1">Article 1</a>
            <span class="time">2024-03-01T10:00:00</span>
        </li>
        <li class="news-item">
            <a href="/a2.chn" title="Article 2">Article 2</a>
            <span class="time">2024-02-28T09:00:00</span>
        </li>
        """)
        articles, _ = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 2

    def test_empty_page_returns_no_articles(self):
        html = "<html><body><div>No articles here</div></body></html>"
        articles, should_stop = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 0
        assert should_stop is False

    def test_tlitem_selector(self):
        """CafeF sometimes uses div.tlitem for article containers."""
        html = """
        <html><body>
        <div class="tlitem">
            <h3><a href="/tlitem-article.chn" title="TL Item">TL Item</a></h3>
            <p class="sapo">Description here</p>
            <span class="time" datetime="2024-05-10T14:00:00">10/05/2024</span>
        </div>
        </body></html>
        """
        articles, _ = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["title"] == "TL Item"

    def test_date_fallback_from_element_text(self):
        """When no time tag exists, should extract date from element text."""
        html = self._make_html("""
        <li class="news-item">
            <a href="/fallback-date.chn" title="Fallback date">Fallback date</a>
            <span>Ngày 15/03/2024 - Tin tức</span>
        </li>
        """)
        articles, _ = _parse_cafef_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["date"] == "2024-03-15"


class TestScrapeCafef:
    """Tests for the full CafeF scraper function using the JSON News API."""

    def _make_json_response(self, articles):
        """Build a mock CafeF News.ashx JSON response.

        Args:
            articles: list of (title, link, date_str) where date_str is
                YYYY-MM-DD; converted to the /Date(ms)/ ASP.NET format.
        """
        import time as _time

        data = []
        for title, link, date_str in articles:
            ms = int(_time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
            data.append({
                "Title": title,
                "SubTitle": f"Description for {title}",
                "DeployDate": f"/Date({ms})/",
                "LinkDetail": link,
            })
        resp = MagicMock()
        resp.json.return_value = {"Data": data, "Message": None, "Success": True}
        return resp

    def _empty_response(self):
        resp = MagicMock()
        resp.json.return_value = {"Data": [], "Message": None, "Success": True}
        return resp

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_collects_articles_from_single_page(self, mock_fetch):
        """Should collect articles from a single API page per NewsType."""
        page = self._make_json_response([
            ("Article 1", "/du-lieu/VNM-1/a1.chn", "2024-01-10"),
            ("Article 2", "/du-lieu/VNM-2/a2.chn", "2024-01-09"),
        ])
        # Each NewsType: first page has data, second page empty.
        empty = self._empty_response()
        mock_fetch.side_effect = [page, empty, empty]

        rl = MagicMock(spec=RateLimiter)
        result = scrape_cafef(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert len(result) == 2
        assert list(result.columns) == ["date", "title", "description", "url", "source"]
        assert result["source"].unique().tolist() == ["cafef"]

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_stops_on_old_articles(self, mock_fetch):
        """Should stop paginating when articles predate start_date."""
        page = self._make_json_response([
            ("Old article", "/du-lieu/VNM-9/old.chn", "2021-06-15"),
        ])
        mock_fetch.return_value = page

        rl = MagicMock(spec=RateLimiter)
        result = scrape_cafef(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert result.empty

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_handles_fetch_failure(self, mock_fetch):
        """Should return empty DataFrame when fetch fails."""
        mock_fetch.return_value = None

        rl = MagicMock(spec=RateLimiter)
        result = scrape_cafef(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert result.empty
        assert list(result.columns) == ["date", "title", "description", "url", "source"]

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_skips_existing_urls(self, mock_fetch):
        """Should skip articles whose URLs are already collected."""
        page = self._make_json_response([
            ("New article", "/du-lieu/VNM-1/new.chn", "2024-01-10"),
            ("Existing article", "/du-lieu/VNM-2/existing.chn", "2024-01-09"),
        ])
        empty = self._empty_response()
        mock_fetch.side_effect = [page, empty, empty]

        rl = MagicMock(spec=RateLimiter)
        result = scrape_cafef(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls={"https://cafef.vn/du-lieu/VNM-2/existing.chn"},
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert len(result) == 1
        assert result.iloc[0]["title"] == "New article"

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_paginates_multiple_pages(self, mock_fetch):
        """Should fetch multiple pages until an empty page is returned."""
        page1 = self._make_json_response([
            ("Page 1 Article", "/du-lieu/FPT-1/p1.chn", "2024-03-01"),
        ])
        page2 = self._make_json_response([
            ("Page 2 Article", "/du-lieu/FPT-2/p2.chn", "2024-02-15"),
        ])
        empty = self._empty_response()
        # NewsType 1: page1, page2, empty; NewsType 2: empty
        mock_fetch.side_effect = [page1, page2, empty, empty]

        rl = MagicMock(spec=RateLimiter)
        result = scrape_cafef(
            ticker="FPT",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert len(result) == 2

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_uses_json_api_endpoint(self, mock_fetch):
        """Should call the CafeF JSON News API with lowercase ticker."""
        mock_fetch.return_value = None

        rl = MagicMock(spec=RateLimiter)
        scrape_cafef(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        first_call_url = mock_fetch.call_args_list[0][0][0]
        assert CAFEF_NEWS_API in first_call_url
        assert "Symbol=vnm" in first_call_url


class TestParseCafefApiDate:
    """Tests for the CafeF JSON API date parser."""

    def test_aspnet_date(self):
        # 1704844800000 ms = 2024-01-10 (local-time dependent; check year-month)
        result = _parse_cafef_api_date("/Date(1704844800000)/")
        assert result is not None
        assert result.startswith("2024-01")

    def test_invalid_returns_none(self):
        assert _parse_cafef_api_date("garbage") is None

    def test_empty_returns_none(self):
        assert _parse_cafef_api_date("") is None

    def test_falls_back_to_plain_date(self):
        assert _parse_cafef_api_date("2024-01-15") == "2024-01-15"


class TestParseCafefApiPage:
    """Tests for parsing a page of CafeF JSON API items."""

    def _item(self, title, link, ms):
        return {
            "Title": title,
            "SubTitle": "sub",
            "DeployDate": f"/Date({ms})/",
            "LinkDetail": link,
        }

    def test_builds_absolute_url_and_strips_query(self):
        items = [self._item("T1", "/du-lieu/VNM-1/a.chn?utm_source=du-lieu", 1704844800000)]
        articles, _ = _parse_cafef_api_page(items, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["url"] == "https://cafef.vn/du-lieu/VNM-1/a.chn"
        assert articles[0]["source"] == "cafef"

    def test_skips_existing(self):
        items = [self._item("T1", "/du-lieu/VNM-1/a.chn", 1704844800000)]
        existing = {"https://cafef.vn/du-lieu/VNM-1/a.chn"}
        articles, _ = _parse_cafef_api_page(items, existing, "2022-01-01")
        assert articles == []

    def test_flags_old_article(self):
        # 2021-06-15 timestamp (ms) — predates start_date
        old_ms = int(time.mktime(datetime.strptime("2021-06-15", "%Y-%m-%d").timetuple())) * 1000
        items = [self._item("Old", "/du-lieu/VNM-1/old.chn", old_ms)]
        articles, found_old = _parse_cafef_api_page(items, set(), "2022-01-01")
        assert articles == []
        assert found_old is True


class TestScrapeCafefIntegration:
    """Integration test: scrape_source dispatches to scrape_cafef."""

    @patch("pipeline.task2_scrape.scrape_cafef")
    def test_scrape_source_dispatches_to_cafef(self, mock_scrape_cafef):
        """scrape_source('cafef', ...) should call scrape_cafef."""
        from pipeline.task2_scrape import scrape_source

        mock_scrape_cafef.return_value = pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

        scrape_source("cafef", "VNM", "2022-01-01")

        mock_scrape_cafef.assert_called_once()
        call_kwargs = mock_scrape_cafef.call_args
        assert call_kwargs[1]["ticker"] == "VNM" or call_kwargs[0][0] == "VNM"


# ---------------------------------------------------------------------------
# Vietstock scraper tests (Task 4.3)
# ---------------------------------------------------------------------------

from pipeline.task2_scrape import (
    _parse_vietstock_date,
    _parse_vietstock_page,
    _parse_vietstock_latest_news,
    scrape_vietstock,
    VIETSTOCK_TAG_URL,
    VIETSTOCK_TAG_PAGE_URL,
    VIETSTOCK_FINANCE_URL,
    VIETSTOCK_LATEST_NEWS_URL,
)


class TestParseVietstockDate:
    """Tests for Vietstock date parsing."""

    def test_iso_datetime(self):
        assert _parse_vietstock_date("2024-01-15T10:30:00") == "2024-01-15"

    def test_iso_date_only(self):
        assert _parse_vietstock_date("2024-01-15") == "2024-01-15"

    def test_vietnamese_slash_format(self):
        assert _parse_vietstock_date("15/01/2024") == "2024-01-15"

    def test_vietnamese_slash_with_time(self):
        assert _parse_vietstock_date("15/01/2024 10:30") == "2024-01-15"

    def test_dash_format(self):
        assert _parse_vietstock_date("15-01-2024") == "2024-01-15"

    def test_iso_with_space_time(self):
        assert _parse_vietstock_date("2024-01-15 10:30:00") == "2024-01-15"

    def test_empty_string_returns_none(self):
        assert _parse_vietstock_date("") is None

    def test_none_returns_none(self):
        assert _parse_vietstock_date(None) is None

    def test_whitespace_only_returns_none(self):
        assert _parse_vietstock_date("   ") is None

    def test_unparseable_returns_none(self):
        assert _parse_vietstock_date("2 giờ trước") is None

    def test_embedded_iso_date(self):
        assert _parse_vietstock_date("Published 2024-03-20 at noon") == "2024-03-20"

    def test_embedded_vn_date(self):
        assert _parse_vietstock_date("Ngày 20/03/2024") == "2024-03-20"


class TestParseVietstockPage:
    """Tests for Vietstock HTML page parsing."""

    def _make_html(self, articles_html: str, login_wall: bool = False) -> str:
        """Wrap article HTML in a minimal Vietstock-like page structure."""
        login_div = (
            '<div class="login-required">Vui lòng đăng nhập</div>'
            if login_wall else ""
        )
        return f"""
        <html><body>
        {login_div}
        <div class="content">
            <div class="list-news">
                <ul>{articles_html}</ul>
            </div>
        </div>
        </body></html>
        """

    def test_extracts_article_with_title_and_date(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/vnm-tang-manh-123.htm" title="VNM tăng mạnh">VNM tăng mạnh</a>
            <p class="sapo">Cổ phiếu VNM tăng 5% trong phiên hôm nay.</p>
            <span class="time">2024-03-15T10:00:00</span>
        </li>
        """)
        articles, should_stop = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["title"] == "VNM tăng mạnh"
        assert articles[0]["date"] == "2024-03-15"
        assert articles[0]["description"] == "Cổ phiếu VNM tăng 5% trong phiên hôm nay."
        assert articles[0]["source"] == "vietstock"

    def test_builds_absolute_url(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/article-456.htm" title="Test article">Test article</a>
            <span class="time">2024-01-10T08:00:00</span>
        </li>
        """)
        articles, _ = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["url"] == "https://vietstock.vn/article-456.htm"

    def test_handles_absolute_url(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="https://vietstock.vn/full-url.htm"
               title="Full URL">Full URL</a>
            <span class="time">2024-02-20T12:00:00</span>
        </li>
        """)
        articles, _ = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["url"] == "https://vietstock.vn/full-url.htm"

    def test_skips_duplicate_urls(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="https://vietstock.vn/dup.htm" title="Dup">Dup</a>
            <span class="time">2024-03-15T10:00:00</span>
        </li>
        """)
        existing = {"https://vietstock.vn/dup.htm"}
        articles, _ = _parse_vietstock_page(html, existing, "2022-01-01")
        assert len(articles) == 0

    def test_stops_on_old_articles(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/old.htm" title="Old article">Old article</a>
            <span class="time">2021-06-15T10:00:00</span>
        </li>
        """)
        articles, should_stop = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 0
        assert should_stop is True

    def test_handles_missing_description(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/no-desc.htm" title="No description">No description</a>
            <span class="time">2024-01-10T08:00:00</span>
        </li>
        """)
        articles, _ = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["description"] == ""

    def test_multiple_articles(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/a1.htm" title="Article 1">Article 1</a>
            <span class="time">2024-03-01T10:00:00</span>
        </li>
        <li class="news-item">
            <a href="/a2.htm" title="Article 2">Article 2</a>
            <span class="time">2024-02-28T09:00:00</span>
        </li>
        """)
        articles, _ = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 2

    def test_empty_page_returns_no_articles(self):
        html = "<html><body><div>No articles here</div></body></html>"
        articles, should_stop = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 0
        assert should_stop is False

    def test_login_wall_still_collects_public_content(self):
        """When login wall is present, should still collect visible titles."""
        html = self._make_html(
            """
            <li class="news-item">
                <a href="/restricted.htm" title="Restricted article">
                    Restricted article
                </a>
                <p class="sapo">Public summary only</p>
                <span class="time">2024-05-01T10:00:00</span>
                <span class="premium">VIP</span>
            </li>
            """,
            login_wall=True,
        )
        articles, _ = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["title"] == "Restricted article"
        assert articles[0]["description"] == "Public summary only"

    def test_date_fallback_from_element_text(self):
        """When no time tag exists, should extract date from element text."""
        html = self._make_html("""
        <li class="news-item">
            <a href="/fallback-date.htm" title="Fallback date">Fallback date</a>
            <span>Ngày 15/03/2024 - Tin tức</span>
        </li>
        """)
        articles, _ = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["date"] == "2024-03-15"

    def test_article_story_selector(self):
        """Vietstock sometimes uses article.story for containers."""
        html = """
        <html><body>
        <div class="content">
            <article class="story">
                <h3><a href="/story-article.htm" title="Story">Story</a></h3>
                <p class="description">Story description</p>
                <span class="datetime">2024-05-10T14:00:00</span>
            </article>
        </div>
        </body></html>
        """
        articles, _ = _parse_vietstock_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["title"] == "Story"
        assert articles[0]["description"] == "Story description"


class TestScrapeVietstock:
    """Tests for the full Vietstock scraper function with mocked HTTP."""

    def _make_latest_news_html(self, articles):
        """Build a Vietstock #latest-news table from (title, url, date dd/mm/yyyy)."""
        rows = []
        for title, url, date in articles:
            rows.append(
                f'<tr><td class="col-date">{date}</td>'
                f'<td><a class="news-link" href="{url}" title="{title}">{title}</a></td></tr>'
            )
        return f'<html><body><table id="latest-news"><tbody>{"".join(rows)}</tbody></table></body></html>'

    def _make_page_html(self, articles):
        """Build a Vietstock tag-page (fallback) HTML from (title, url, date)."""
        items = []
        for title, url, date in articles:
            items.append(f"""
            <li class="news-item">
                <a href="{url}" title="{title}">{title}</a>
                <p class="sapo">Description for {title}</p>
                <span class="time">{date}</span>
            </li>
            """)
        return f"""
        <html><body>
        <div class="content">
            <div class="list-news"><ul>{"".join(items)}</ul></div>
        </div>
        </body></html>
        """

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_collects_articles_from_latest_news(self, mock_fetch):
        """Should collect articles from the finance latest-news table."""
        page_html = self._make_latest_news_html([
            ("Article 1", "//vietstock.vn/2024/01/a1-1.htm", "10/01/2024"),
            ("Article 2", "//vietstock.vn/2024/01/a2-2.htm", "09/01/2024"),
        ])
        mock_response = MagicMock()
        mock_response.text = page_html
        mock_response.status_code = 200
        mock_fetch.return_value = mock_response

        rl = MagicMock(spec=RateLimiter)
        result = scrape_vietstock(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert len(result) == 2
        assert list(result.columns) == ["date", "title", "description", "url", "source"]
        assert result["source"].unique().tolist() == ["vietstock"]

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_handles_fetch_failure(self, mock_fetch):
        """Should return empty DataFrame when all fetches fail."""
        mock_fetch.return_value = None

        rl = MagicMock(spec=RateLimiter)
        result = scrape_vietstock(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert result.empty
        assert list(result.columns) == ["date", "title", "description", "url", "source"]

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_skips_existing_urls(self, mock_fetch):
        """Should skip articles whose URLs are already collected."""
        page_html = self._make_latest_news_html([
            ("New article", "//vietstock.vn/2024/01/new-1.htm", "10/01/2024"),
            ("Existing", "//vietstock.vn/2024/01/existing-2.htm", "09/01/2024"),
        ])
        mock_response = MagicMock()
        mock_response.text = page_html
        mock_response.status_code = 200
        mock_fetch.return_value = mock_response

        rl = MagicMock(spec=RateLimiter)
        result = scrape_vietstock(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls={"https://vietstock.vn/2024/01/existing-2.htm"},
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert len(result) == 1
        assert result.iloc[0]["title"] == "New article"

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_falls_back_to_tag_search(self, mock_fetch):
        """When latest-news yields nothing, should try the tag-search fallback."""
        empty_response = MagicMock()
        empty_response.text = "<html><body></body></html>"
        empty_response.status_code = 200
        tag_response = MagicMock()
        tag_response.text = self._make_page_html([
            ("Tag article", "/tag-a1.htm", "2024-02-01T10:00:00"),
        ])
        tag_response.status_code = 200
        tag_empty = MagicMock()
        tag_empty.text = "<html><body></body></html>"
        tag_empty.status_code = 200

        # latest-news (empty) → tag page1 (article) → tag page2 (empty)
        mock_fetch.side_effect = [empty_response, tag_response, tag_empty]

        rl = MagicMock(spec=RateLimiter)
        result = scrape_vietstock(
            ticker="FPT",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert len(result) == 1
        assert result.iloc[0]["title"] == "Tag article"

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_uses_latest_news_url_first(self, mock_fetch):
        """First request should target the finance latest-news page."""
        mock_fetch.return_value = None

        rl = MagicMock(spec=RateLimiter)
        scrape_vietstock(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        first_call_url = mock_fetch.call_args_list[0][0][0]
        assert first_call_url == VIETSTOCK_LATEST_NEWS_URL.format(ticker="VNM")

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_stops_on_old_articles(self, mock_fetch):
        """Articles before start_date should be excluded."""
        page_html = self._make_latest_news_html([
            ("Old article", "//vietstock.vn/2021/06/old-9.htm", "15/06/2021"),
        ])
        mock_response = MagicMock()
        mock_response.text = page_html
        mock_response.status_code = 200
        # latest-news returns only an old article → empty result → fallback
        # tag pages also empty.
        empty = MagicMock()
        empty.text = "<html><body></body></html>"
        empty.status_code = 200
        mock_fetch.side_effect = [mock_response, empty, empty]

        rl = MagicMock(spec=RateLimiter)
        result = scrape_vietstock(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert result.empty


class TestScrapeVietstockIntegration:
    """Integration test: scrape_source dispatches to scrape_vietstock."""

    @patch("pipeline.task2_scrape.scrape_vietstock")
    def test_scrape_source_dispatches_to_vietstock(self, mock_scrape_vs):
        """scrape_source('vietstock', ...) should call scrape_vietstock."""
        from pipeline.task2_scrape import scrape_source

        mock_scrape_vs.return_value = pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

        scrape_source("vietstock", "VNM", "2022-01-01")

        mock_scrape_vs.assert_called_once()
        call_kwargs = mock_scrape_vs.call_args
        assert call_kwargs[1]["ticker"] == "VNM" or call_kwargs[0][0] == "VNM"

# ---------------------------------------------------------------------------
# TNCK scraper tests (Task 4.4)
# ---------------------------------------------------------------------------

from pipeline.task2_scrape import (
    _parse_tnck_date,
    _parse_tnck_page,
    _generate_monthly_report,
    scrape_tnck,
    TNCK_SEARCH_URL,
    TNCK_CATEGORY_URLS,
)


class TestParseTnckDate:
    """Tests for TNCK date parsing."""

    def test_iso_datetime(self):
        assert _parse_tnck_date("2024-01-15T10:30:00") == "2024-01-15"

    def test_iso_date_only(self):
        assert _parse_tnck_date("2024-01-15") == "2024-01-15"

    def test_vietnamese_slash_format(self):
        assert _parse_tnck_date("15/01/2024") == "2024-01-15"

    def test_vietnamese_slash_with_time(self):
        assert _parse_tnck_date("15/01/2024 10:30") == "2024-01-15"

    def test_dash_format(self):
        assert _parse_tnck_date("15-01-2024") == "2024-01-15"

    def test_iso_with_space_time(self):
        assert _parse_tnck_date("2024-01-15 10:30:00") == "2024-01-15"

    def test_time_before_date_format(self):
        assert _parse_tnck_date("10:30 15/01/2024") == "2024-01-15"

    def test_empty_string_returns_none(self):
        assert _parse_tnck_date("") is None

    def test_none_returns_none(self):
        assert _parse_tnck_date(None) is None

    def test_whitespace_only_returns_none(self):
        assert _parse_tnck_date("   ") is None

    def test_unparseable_returns_none(self):
        assert _parse_tnck_date("2 giờ trước") is None

    def test_embedded_iso_date(self):
        assert _parse_tnck_date("Published 2024-03-20 at noon") == "2024-03-20"

    def test_embedded_vn_date(self):
        assert _parse_tnck_date("Ngày 20/03/2024") == "2024-03-20"


class TestParseTnckPage:
    """Tests for TNCK HTML page parsing."""

    def _make_html(self, articles_html: str) -> str:
        """Wrap article HTML in a minimal TNCK-like page structure."""
        return f"""
        <html><body>
        <div class="content">
            <div class="list-news">
                <ul>{articles_html}</ul>
            </div>
        </div>
        </body></html>
        """

    def test_extracts_article_with_title_and_date(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/chung-khoan/vnm-tang-manh-123.html"
               title="VNM tăng mạnh">VNM tăng mạnh</a>
            <p class="sapo">Cổ phiếu VNM tăng 5% trong phiên hôm nay.</p>
            <span class="time">2024-03-15T10:00:00</span>
        </li>
        """)
        articles, should_stop = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["title"] == "VNM tăng mạnh"
        assert articles[0]["date"] == "2024-03-15"
        assert articles[0]["description"] == "Cổ phiếu VNM tăng 5% trong phiên hôm nay."
        assert articles[0]["source"] == "tnck"

    def test_builds_absolute_url(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/doanh-nghiep/article-456.html"
               title="Test article">Test article</a>
            <span class="time">2024-01-10T08:00:00</span>
        </li>
        """)
        articles, _ = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["url"] == "https://tinnhanhchungkhoan.vn/doanh-nghiep/article-456.html"

    def test_handles_absolute_url(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="https://tinnhanhchungkhoan.vn/full-url.html"
               title="Full URL">Full URL</a>
            <span class="time">2024-02-20T12:00:00</span>
        </li>
        """)
        articles, _ = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["url"] == "https://tinnhanhchungkhoan.vn/full-url.html"

    def test_skips_duplicate_urls(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="https://tinnhanhchungkhoan.vn/dup.html"
               title="Dup">Dup</a>
            <span class="time">2024-03-15T10:00:00</span>
        </li>
        """)
        existing = {"https://tinnhanhchungkhoan.vn/dup.html"}
        articles, _ = _parse_tnck_page(html, existing, "2022-01-01")
        assert len(articles) == 0

    def test_stops_on_old_articles(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/old-article.html" title="Old article">Old article</a>
            <span class="time">2021-06-15T10:00:00</span>
        </li>
        """)
        articles, should_stop = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 0
        assert should_stop is True

    def test_handles_missing_description(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/no-desc.html" title="No description">No description</a>
            <span class="time">2024-01-10T08:00:00</span>
        </li>
        """)
        articles, _ = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["description"] == ""

    def test_multiple_articles(self):
        html = self._make_html("""
        <li class="news-item">
            <a href="/a1.html" title="Article 1">Article 1</a>
            <span class="time">2024-03-01T10:00:00</span>
        </li>
        <li class="news-item">
            <a href="/a2.html" title="Article 2">Article 2</a>
            <span class="time">2024-02-28T09:00:00</span>
        </li>
        """)
        articles, _ = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 2

    def test_empty_page_returns_no_articles(self):
        html = "<html><body><div>No articles here</div></body></html>"
        articles, should_stop = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 0
        assert should_stop is False

    def test_article_story_selector(self):
        """TNCK sometimes uses article.story for article containers."""
        html = """
        <html><body>
        <article class="story">
            <h3><a href="/story-article.html" title="Story Item">Story Item</a></h3>
            <p class="story__summary">Description here</p>
            <span class="story__time" datetime="2024-05-10T14:00:00">10/05/2024</span>
        </article>
        </body></html>
        """
        articles, _ = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["title"] == "Story Item"
        assert articles[0]["description"] == "Description here"

    def test_date_fallback_from_element_text(self):
        """When no time tag exists, should extract date from element text."""
        html = self._make_html("""
        <li class="news-item">
            <a href="/fallback-date.html" title="Fallback date">Fallback date</a>
            <span>Ngày 15/03/2024 - Tin tức</span>
        </li>
        """)
        articles, _ = _parse_tnck_page(html, set(), "2022-01-01")
        assert len(articles) == 1
        assert articles[0]["date"] == "2024-03-15"


class TestGenerateMonthlyReport:
    """Tests for the TNCK monthly article count report (Req 2.5)."""

    def test_report_with_valid_data(self, caplog):
        """Should log monthly counts for articles with valid dates."""
        import logging

        df = pd.DataFrame({
            "date": [
                "2024-01-10", "2024-01-15", "2024-01-20",
                "2024-02-05", "2024-02-10",
                "2024-03-01",
            ],
            "title": ["A", "B", "C", "D", "E", "F"],
            "url": [f"https://tnck.vn/{i}" for i in range(6)],
            "source": ["tnck"] * 6,
        })

        with caplog.at_level(logging.INFO):
            _generate_monthly_report(df)

        log_text = caplog.text
        assert "TNCK MONTHLY ARTICLE COUNT REPORT" in log_text
        assert "2024-01" in log_text
        assert "2024-02" in log_text
        assert "2024-03" in log_text

    def test_report_with_empty_dataframe(self, caplog):
        """Should handle empty DataFrame gracefully."""
        import logging

        df = pd.DataFrame(
            columns=["date", "title", "url", "source"]
        )

        with caplog.at_level(logging.INFO):
            _generate_monthly_report(df)

        assert "no articles to report" in caplog.text

    def test_report_with_invalid_dates(self, caplog):
        """Should handle articles with unparseable dates."""
        import logging

        df = pd.DataFrame({
            "date": ["not-a-date", "", "also-bad"],
            "title": ["A", "B", "C"],
            "url": [f"https://tnck.vn/{i}" for i in range(3)],
            "source": ["tnck"] * 3,
        })

        with caplog.at_level(logging.INFO):
            _generate_monthly_report(df)

        assert "no articles with valid dates" in caplog.text


class TestScrapeTnck:
    """Tests for the full TNCK scraper function with mocked HTTP."""

    def _make_page_html(self, articles):
        """Build a TNCK-like HTML page from a list of (title, url, date) tuples."""
        items = []
        for title, url, date in articles:
            items.append(f"""
            <li class="news-item">
                <a href="{url}" title="{title}">{title}</a>
                <p class="sapo">Description for {title}</p>
                <span class="time">{date}</span>
            </li>
            """)
        return f"""
        <html><body>
        <div class="list-news"><ul>{"".join(items)}</ul></div>
        </body></html>
        """

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_collects_articles_from_search_and_categories(self, mock_fetch):
        """Should collect articles from both search and category pages."""
        page_html = self._make_page_html([
            ("Article 1", "/a1.html", "2024-01-10T10:00:00"),
        ])
        mock_response = MagicMock()
        mock_response.text = page_html
        # Empty page to stop pagination
        empty_response = MagicMock()
        empty_response.text = "<html><body></body></html>"

        # Use a function to return responses dynamically:
        # - First search returns content, then empty to stop pagination
        # - All other searches return empty on page 1 (stop immediately)
        # - Category pages return empty (stop immediately)
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return mock_response  # First ticker search page 1
            elif call_count["n"] == 2:
                return empty_response  # First ticker search page 2 (stop)
            else:
                return empty_response  # All other requests

        mock_fetch.side_effect = side_effect

        rl = MagicMock(spec=RateLimiter)
        result = scrape_tnck(
            ticker="ALL",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert not result.empty
        assert "source" in result.columns
        assert (result["source"] == "tnck").all()

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_returns_empty_when_all_fetches_fail(self, mock_fetch):
        """Should return empty DataFrame when all fetches fail."""
        mock_fetch.return_value = None

        rl = MagicMock(spec=RateLimiter)
        result = scrape_tnck(
            ticker="ALL",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert result.empty
        assert list(result.columns) == ["date", "title", "description", "url", "source"]

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_deduplicates_across_search_and_categories(self, mock_fetch):
        """Articles found in search should not be duplicated from categories."""
        # Same article appears in both search and category
        page_html = self._make_page_html([
            ("Shared Article", "https://tinnhanhchungkhoan.vn/shared.html",
             "2024-01-10T10:00:00"),
        ])
        mock_response = MagicMock()
        mock_response.text = page_html
        empty_response = MagicMock()
        empty_response.text = "<html><body></body></html>"

        # Use a function: all requests return the same article page
        # but dedup should prevent duplicates
        def side_effect(*args, **kwargs):
            return mock_response

        mock_fetch.side_effect = side_effect

        rl = MagicMock(spec=RateLimiter)
        result = scrape_tnck(
            ticker="ALL",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        # The article should appear only once due to URL dedup
        shared_count = len(
            result[result["url"] == "https://tinnhanhchungkhoan.vn/shared.html"]
        )
        assert shared_count == 1

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_skips_existing_urls(self, mock_fetch):
        """Should skip articles whose URLs are already collected."""
        page_html = self._make_page_html([
            ("New article", "/new.html", "2024-01-10T10:00:00"),
            ("Existing article", "https://tinnhanhchungkhoan.vn/existing.html",
             "2024-01-09T09:00:00"),
        ])
        mock_response = MagicMock()
        mock_response.text = page_html
        empty_response = MagicMock()
        empty_response.text = "<html><body></body></html>"

        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return mock_response  # First search page
            return empty_response

        mock_fetch.side_effect = side_effect

        rl = MagicMock(spec=RateLimiter)
        result = scrape_tnck(
            ticker="ALL",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls={"https://tinnhanhchungkhoan.vn/existing.html"},
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        urls = result["url"].tolist()
        assert "https://tinnhanhchungkhoan.vn/existing.html" not in urls
        assert any("new.html" in u for u in urls)


class TestScrapeTnckIntegration:
    """Integration test: scrape_source dispatches to scrape_tnck."""

    @patch("pipeline.task2_scrape.scrape_tnck")
    def test_scrape_source_dispatches_to_tnck(self, mock_scrape_tnck):
        """scrape_source('tnck', ...) should call scrape_tnck."""
        from pipeline.task2_scrape import scrape_source

        mock_scrape_tnck.return_value = pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

        scrape_source("tnck", "ALL", "2022-01-01")

        mock_scrape_tnck.assert_called_once()


# ---------------------------------------------------------------------------
# Error handling tests (Task 4.5 — Req 2.12)
# ---------------------------------------------------------------------------

from pipeline.task2_scrape import print_scraping_report


class TestErrorHandlingCafeF:
    """Tests that the CafeF JSON scraper handles bad responses gracefully (Req 2.12)."""

    def _json_resp(self, articles):
        data = []
        for title, link, date_str in articles:
            ms = int(time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())) * 1000
            data.append({
                "Title": title,
                "SubTitle": "sub",
                "DeployDate": f"/Date({ms})/",
                "LinkDetail": link,
            })
        resp = MagicMock()
        resp.json.return_value = {"Data": data, "Success": True}
        return resp

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_invalid_json_is_skipped_not_raised(self, mock_fetch):
        """When a response is not valid JSON, the NewsType is stopped gracefully."""
        good = self._json_resp([("Good article", "/du-lieu/VNM-1/good.chn", "2024-01-10")])
        bad = MagicMock()
        bad.json.side_effect = ValueError("Simulated JSON parse failure")
        empty = MagicMock()
        empty.json.return_value = {"Data": [], "Success": True}
        # NewsType 1: good page, then empty (stop). NewsType 2: bad JSON (stop).
        mock_fetch.side_effect = [good, empty, bad]

        rl = MagicMock(spec=RateLimiter)
        result = scrape_cafef(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        assert len(result) >= 1
        assert result.iloc[0]["title"] == "Good article"

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_malformed_item_skipped(self, mock_fetch):
        """Items missing title/link should be skipped without raising."""
        resp = MagicMock()
        resp.json.return_value = {
            "Data": [
                {"Title": "", "LinkDetail": "/du-lieu/VNM-1/no-title.chn", "DeployDate": "/Date(1704844800000)/"},
                {"Title": "Valid", "LinkDetail": "/du-lieu/VNM-2/valid.chn", "DeployDate": "/Date(1704844800000)/", "SubTitle": "s"},
            ],
            "Success": True,
        }
        empty = MagicMock()
        empty.json.return_value = {"Data": [], "Success": True}
        mock_fetch.side_effect = [resp, empty, empty]

        rl = MagicMock(spec=RateLimiter)
        result = scrape_cafef(
            ticker="VNM",
            start_date="2022-01-01",
            rate_limiter=rl,
            existing_urls=set(),
            scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
        )

        # Only the valid item should be collected — no unhandled exception
        assert len(result) == 1
        assert result.iloc[0]["title"] == "Valid"


class TestErrorHandlingVietstock:
    """Tests that Vietstock scraper handles bad pages gracefully (Req 2.12)."""

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_unparseable_latest_news_falls_back(self, mock_fetch):
        """If latest-news parsing raises, scraper falls back to tag search."""
        bad_resp = MagicMock()
        bad_resp.text = "<html><body><table id='latest-news'></table></body></html>"
        bad_resp.status_code = 200
        tag_resp = MagicMock()
        tag_resp.text = """
        <html><body>
        <div class="content"><div class="list-news"><ul>
        <li class="news-item">
            <a href="/good.htm" title="Good article">Good article</a>
            <span class="time">2024-01-10T10:00:00</span>
        </li>
        </ul></div></div>
        </body></html>
        """
        tag_resp.status_code = 200
        empty_resp = MagicMock()
        empty_resp.text = "<html><body></body></html>"
        empty_resp.status_code = 200
        # latest-news (parse raises) → tag page1 (good) → tag page2 (empty)
        mock_fetch.side_effect = [bad_resp, tag_resp, empty_resp]

        with patch(
            "pipeline.task2_scrape._parse_vietstock_latest_news",
            side_effect=ValueError("Simulated parse failure"),
        ):
            rl = MagicMock(spec=RateLimiter)
            result = scrape_vietstock(
                ticker="VNM",
                start_date="2022-01-01",
                rate_limiter=rl,
                existing_urls=set(),
                scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
            )

        # Should not raise; should collect the tag-search article
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 1


class TestErrorHandlingTnck:
    """Tests that TNCK scraper handles unparseable HTML gracefully (Req 2.12)."""

    @patch("pipeline.task2_scrape.fetch_with_retry")
    def test_unparseable_search_page_is_skipped(self, mock_fetch):
        """When _parse_tnck_page raises during search, scraper should continue."""
        valid_html = """
        <html><body>
        <div class="list-news"><ul>
        <li class="news-item">
            <a href="/good.html" title="Good article">Good article</a>
            <span class="time">2024-01-10T10:00:00</span>
        </li>
        </ul></div>
        </body></html>
        """
        good_resp = MagicMock()
        good_resp.text = valid_html
        empty_resp = MagicMock()
        empty_resp.text = "<html><body></body></html>"

        # Return good response for first search, then empty for rest
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return good_resp
            return empty_resp

        mock_fetch.side_effect = side_effect

        # Patch _parse_tnck_page to raise on the first call, then work normally
        parse_count = {"n": 0}
        original_parse = __import__(
            "pipeline.task2_scrape", fromlist=["_parse_tnck_page"]
        )._parse_tnck_page

        def patched_parse(html, existing_urls, start_date):
            parse_count["n"] += 1
            if parse_count["n"] == 1:
                raise ValueError("Simulated HTML parse failure")
            return original_parse(html, existing_urls, start_date)

        with patch("pipeline.task2_scrape._parse_tnck_page", side_effect=patched_parse):
            rl = MagicMock(spec=RateLimiter)
            # Should not raise — errors are caught and logged
            result = scrape_tnck(
                ticker="ALL",
                start_date="2022-01-01",
                rate_limiter=rl,
                existing_urls=set(),
                scraping_cfg={"max_retries": 3, "backoff_factor": 2, "request_timeout": 30},
            )

        # Should not raise an unhandled exception
        assert isinstance(result, pd.DataFrame)


# ---------------------------------------------------------------------------
# Scraping report tests (Task 4.5 — Req 2.10)
# ---------------------------------------------------------------------------


class TestPrintScrapingReport:
    """Tests for the per-source scraping report (Req 2.10)."""

    def test_report_with_articles(self, caplog):
        """Should log per-ticker article count and date range."""
        import logging

        results = {
            "VNM": pd.DataFrame({
                "date": ["2024-01-10", "2024-03-15"],
                "title": ["A", "B"],
                "url": ["https://cafef.vn/a.chn", "https://cafef.vn/b.chn"],
                "source": ["cafef", "cafef"],
            }),
            "FPT": pd.DataFrame({
                "date": ["2024-02-01"],
                "title": ["C"],
                "url": ["https://cafef.vn/c.chn"],
                "source": ["cafef"],
            }),
        }

        with caplog.at_level(logging.INFO):
            print_scraping_report("cafef", results)

        log_text = caplog.text
        assert "SCRAPING REPORT" in log_text
        assert "CAFEF" in log_text
        assert "VNM" in log_text
        assert "FPT" in log_text
        assert "2 articles" in log_text
        assert "1 articles" in log_text  # FPT has 1 article
        assert "Total articles from CAFEF: 3" in log_text

    def test_report_with_empty_ticker(self, caplog):
        """Should report 0 articles for tickers with no results."""
        import logging

        results = {
            "VNM": pd.DataFrame(
                columns=["date", "title", "url", "source"]
            ),
        }

        with caplog.at_level(logging.INFO):
            print_scraping_report("cafef", results)

        assert "0 articles" in caplog.text

    def test_report_with_no_valid_dates(self, caplog):
        """Should handle articles with unparseable dates gracefully."""
        import logging

        results = {
            "VNM": pd.DataFrame({
                "date": ["", "not-a-date"],
                "title": ["A", "B"],
                "url": ["https://cafef.vn/a.chn", "https://cafef.vn/b.chn"],
                "source": ["cafef", "cafef"],
            }),
        }

        with caplog.at_level(logging.INFO):
            print_scraping_report("cafef", results)

        log_text = caplog.text
        assert "2 articles" in log_text
        assert "no valid dates" in log_text

    def test_report_with_mixed_valid_invalid_dates(self, caplog):
        """Should report date range from valid dates, ignoring invalid ones."""
        import logging

        results = {
            "VNM": pd.DataFrame({
                "date": ["2024-01-10", "", "2024-03-15"],
                "title": ["A", "B", "C"],
                "url": [f"https://cafef.vn/{i}.chn" for i in range(3)],
                "source": ["cafef"] * 3,
            }),
        }

        with caplog.at_level(logging.INFO):
            print_scraping_report("cafef", results)

        log_text = caplog.text
        assert "3 articles" in log_text
        assert "2024-01-10" in log_text
        assert "2024-03-15" in log_text

    def test_report_with_empty_results(self, caplog):
        """Should handle completely empty results dict."""
        import logging

        with caplog.at_level(logging.INFO):
            print_scraping_report("cafef", {})

        log_text = caplog.text
        assert "SCRAPING REPORT" in log_text
        assert "Total articles from CAFEF: 0" in log_text

    def test_report_multiple_tickers_sorted(self, caplog):
        """Tickers should be reported in sorted order."""
        import logging

        results = {
            "VNM": pd.DataFrame({
                "date": ["2024-01-10"],
                "title": ["A"],
                "url": ["https://cafef.vn/a.chn"],
                "source": ["cafef"],
            }),
            "ACB": pd.DataFrame({
                "date": ["2024-02-01"],
                "title": ["B"],
                "url": ["https://cafef.vn/b.chn"],
                "source": ["cafef"],
            }),
            "FPT": pd.DataFrame({
                "date": ["2024-03-01"],
                "title": ["C"],
                "url": ["https://cafef.vn/c.chn"],
                "source": ["cafef"],
            }),
        }

        with caplog.at_level(logging.INFO):
            print_scraping_report("cafef", results)

        log_text = caplog.text
        # ACB should appear before FPT, which should appear before VNM
        acb_pos = log_text.index("ACB")
        fpt_pos = log_text.index("FPT")
        vnm_pos = log_text.index("VNM")
        assert acb_pos < fpt_pos < vnm_pos


# ---------------------------------------------------------------------------
# VietnamBiz scraper tests (news-source-expansion)
# ---------------------------------------------------------------------------

from pipeline.task2_scrape import (
    _parse_vietnambiz_id_date,
    _parse_vietnambiz_page,
)


class TestVietnamBizIdDate:
    """Tests for parsing the date embedded in a VietnamBiz article id."""

    def test_two_digit_month_day(self):
        # 2026 / 06 / 24
        assert _parse_vietnambiz_id_date("2026624182936535") == "2026-06-24"

    def test_two_digit_month_two_digit_day(self):
        assert _parse_vietnambiz_id_date("20261115093000111") == "2026-11-15"

    def test_invalid_returns_none(self):
        assert _parse_vietnambiz_id_date("") is None
        assert _parse_vietnambiz_id_date("abc") is None

    def test_implausible_year_returns_none(self):
        assert _parse_vietnambiz_id_date("1500101000000") is None


class TestVietnamBizParsePage:
    """Tests for parsing a VietnamBiz category listing page."""

    SAMPLE_HTML = """
    <html><body>
      <div class="list">
        <div class="news-item">
          <span class="time">Chứng khoán-19:48 | 24/06/2026</span>
          <h3><a href="/tu-doanh-gom-manh-co-phieu-nao-2026624182936535.htm"
                 title="Tự doanh gom mạnh cổ phiếu nào hôm nay">
              Tự doanh gom mạnh cổ phiếu nào hôm nay</a></h3>
        </div>
        <div class="news-item">
          <span class="time">Doanh nghiệp-08:00 | 10/01/2026</span>
          <h3><a href="/vingroup-chuyen-nhuong-co-phieu-vinhomes-2026110080000222.htm"
                 title="Vingroup chuyển nhượng cổ phiếu Vinhomes cho đối tác">
              Vingroup chuyển nhượng cổ phiếu Vinhomes cho đối tác</a></h3>
        </div>
        <a href="/chu-de/sua-doi-luat-chung-khoan-487.htm" title="Sửa đổi Luật Chứng khoán topic">topic link</a>
      </div>
    </body></html>
    """

    def test_extracts_real_articles_only(self):
        # The /chu-de/ topic link has no numeric id and must be excluded.
        articles, _ = _parse_vietnambiz_page(self.SAMPLE_HTML, set(), "2022-01-01")
        assert len(articles) == 2
        urls = {a["url"] for a in articles}
        assert all("/chu-de/" not in u for u in urls)

    def test_fields_present_and_sourced(self):
        articles, _ = _parse_vietnambiz_page(self.SAMPLE_HTML, set(), "2022-01-01")
        a = articles[0]
        assert a["source"] == "vietnambiz"
        assert a["date"] == "2026-06-24"
        assert a["url"].startswith("https://vietnambiz.vn/")
        assert a["title"]

    def test_date_boundary_filters_old(self):
        # start_date after the second article's date -> it is filtered out.
        articles, found_old = _parse_vietnambiz_page(
            self.SAMPLE_HTML, set(), "2026-06-01"
        )
        dates = {a["date"] for a in articles}
        assert "2026-01-10" not in dates
        assert found_old is True

    def test_duplicate_urls_skipped(self):
        seen = {"https://vietnambiz.vn/tu-doanh-gom-manh-co-phieu-nao-2026624182936535.htm"}
        articles, _ = _parse_vietnambiz_page(self.SAMPLE_HTML, seen, "2022-01-01")
        # Only the non-duplicate article remains.
        assert len(articles) == 1
