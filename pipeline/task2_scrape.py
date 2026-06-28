"""
TASK 2: News_Scraper
Scrape financial news from CafeF, Vietstock, and Tinnhanhchungkhoan.

Provides base scraping infrastructure with:
- Differentiated rate limiting per domain (Req 2.6)
- Retry logic with exponential backoff (Req 2.7)
- Browser-like User-Agent headers (Req 2.11)
- Duplicate detection by URL (Req 2.8)

Source-specific scrapers:
- CafeF (Task 4.2): scrape_cafef()
- Vietstock (Task 4.3): scrape_vietstock()
"""

import os
import re
import time
from datetime import datetime
from html import unescape
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup

from pipeline.logging_config import setup_logger

logger = setup_logger("TASK_2")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Browser-like headers to reduce likelihood of being blocked (Req 2.11)
BROWSER_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Canonical VN30 ticker list
VN30_TICKERS: List[str] = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _load_config(config_path: str = "config/pipeline_config.yaml") -> dict:
    """Load pipeline configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_end_date(end_date: str) -> str:
    """Resolve 'auto' end_date to current date string YYYY-MM-DD."""
    if end_date == "auto":
        return datetime.now().strftime("%Y-%m-%d")
    return end_date


def _get_scraping_config(
    config_path: str = "config/pipeline_config.yaml",
) -> dict:
    """
    Extract scraping-specific configuration values.

    Returns a dict with keys:
        rate_limit_seconds, rate_limit_vietstock_seconds,
        max_retries, backoff_factor, request_timeout
    """
    config = _load_config(config_path)
    scraping = config.get("scraping", {})
    return {
        "rate_limit_seconds": scraping.get("rate_limit_seconds", 1.0),
        "rate_limit_vietstock_seconds": scraping.get(
            "rate_limit_vietstock_seconds", 1.5
        ),
        "max_retries": scraping.get("max_retries", 3),
        "backoff_factor": scraping.get("backoff_factor", 2),
        "request_timeout": scraping.get("request_timeout", 30),
    }


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    """
    Per-domain rate limiter with differentiated delays.

    Enforces a minimum delay between consecutive requests to the same domain.
    Vietstock gets a longer delay (1.5 s by default) than other domains (1.0 s).
    """

    def __init__(
        self,
        default_delay: float = 1.0,
        vietstock_delay: float = 1.5,
    ) -> None:
        self._default_delay = default_delay
        self._vietstock_delay = vietstock_delay
        # domain -> timestamp of last request
        self._last_request: Dict[str, float] = {}

    def _delay_for_domain(self, domain: str) -> float:
        """Return the required delay for *domain*."""
        if "vietstock" in domain.lower():
            return self._vietstock_delay
        return self._default_delay

    def wait(self, url: str) -> None:
        """
        Block until enough time has elapsed since the last request to the
        same domain.  Call this **before** making the HTTP request.
        """
        domain = urlparse(url).netloc.lower()
        required_delay = self._delay_for_domain(domain)
        last_ts = self._last_request.get(domain, 0.0)
        elapsed = time.monotonic() - last_ts
        if elapsed < required_delay:
            sleep_time = required_delay - elapsed
            logger.debug(
                "Rate-limiting %s: sleeping %.2fs", domain, sleep_time
            )
            time.sleep(sleep_time)
        self._last_request[domain] = time.monotonic()


# ---------------------------------------------------------------------------
# HTTP fetch with retry + exponential backoff
# ---------------------------------------------------------------------------

def fetch_with_retry(
    url: str,
    rate_limiter: Optional[RateLimiter] = None,
    max_retries: int = 3,
    backoff_factor: int = 2,
    timeout: int = 30,
    headers: Optional[Dict[str, str]] = None,
) -> Optional[requests.Response]:
    """
    Fetch a URL with retry logic and exponential backoff.

    Args:
        url: The URL to fetch.
        rate_limiter: Optional RateLimiter instance for per-domain throttling.
        max_retries: Maximum number of attempts (default 3).
        backoff_factor: Multiplier for exponential backoff (default 2).
            Delays are: backoff_factor**0, backoff_factor**1, ...
            i.e. 1 s, 2 s, 4 s for factor=2.
        timeout: Request timeout in seconds.
        headers: HTTP headers. Defaults to BROWSER_HEADERS.

    Returns:
        A requests.Response on success, or None after all retries are
        exhausted.
    """
    if headers is None:
        headers = BROWSER_HEADERS

    for attempt in range(max_retries):
        try:
            # Respect rate limit before each request
            if rate_limiter is not None:
                rate_limiter.wait(url)

            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            return response

        except requests.RequestException as exc:
            logger.warning(
                "Request failed for %s (attempt %d/%d): %s",
                url, attempt + 1, max_retries, exc,
            )
            if attempt < max_retries - 1:
                delay = backoff_factor ** attempt  # 1, 2, 4 …
                logger.info("Retrying in %ds…", delay)
                time.sleep(delay)

    logger.error(
        "All %d attempts failed for %s. Skipping.", max_retries, url
    )
    return None


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def load_existing_urls(filepath: str) -> Set[str]:
    """
    Load the set of article URLs already present in *filepath*.

    Returns an empty set if the file does not exist or cannot be read.
    """
    if not os.path.isfile(filepath):
        return set()
    try:
        df = pd.read_csv(filepath, usecols=["url"])
        return set(df["url"].dropna().unique())
    except Exception as exc:
        logger.warning(
            "Could not read existing URLs from %s: %s", filepath, exc
        )
        return set()


def is_duplicate(url: str, existing_urls: Set[str]) -> bool:
    """Return True if *url* is already in *existing_urls*."""
    return url in existing_urls


# ---------------------------------------------------------------------------
# Article validation
# ---------------------------------------------------------------------------

def validate_article(article: Dict) -> bool:
    """
    Validate that an article dict contains all required fields.

    Required fields: date, title, url, source.
    """
    required = ["date", "title", "url", "source"]
    if not all(article.get(field) for field in required):
        logger.warning(
            "Missing required fields in article: %s", article.get("url", "?")
        )
        return False
    return True


# ---------------------------------------------------------------------------
# Safe CSV writing (atomic)
# ---------------------------------------------------------------------------

def safe_write_csv(df: pd.DataFrame, path: str) -> None:
    """
    Write *df* to *path* atomically via a temporary file.

    Ensures that a partial write does not corrupt an existing checkpoint.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    temp_path = path + ".tmp"
    df.to_csv(temp_path, index=False, encoding="utf-8")
    os.replace(temp_path, path)
    logger.info("Saved %d rows to %s", len(df), path)


# ---------------------------------------------------------------------------
# CafeF scraper (Task 4.2)
# ---------------------------------------------------------------------------

# CafeF base URL pattern for ticker-specific news (Req 2.1)
CAFEF_BASE_URL = "https://cafef.vn/thi-truong-chung-khoan/{ticker}-ctck.chn"
# Pagination pattern — CafeF uses /trang-{page}.chn suffix
CAFEF_PAGE_URL = (
    "https://cafef.vn/thi-truong-chung-khoan/{ticker}-ctck/trang-{page}.chn"
)

# CafeF now serves ticker news via a JSON API (discovered from the live
# du-lieu page). This is far more robust than scraping rendered HTML.
#   GET https://cafef.vn/du-lieu/Ajax/PageNew/News.ashx
#       ?Symbol={ticker}&NewsType={type}&PageIndex={n}&PageSize={size}
# Response JSON: {"Data": [{"Title", "SubTitle", "DeployDate": "/Date(ms)/",
#                           "LinkDetail"}], "Success": true}
# NewsType: 1 = company disclosures/news, 2 = events (dividends, AGM, etc.).
# NOTE: If CafeF changes this endpoint, update CAFEF_NEWS_API / CAFEF_NEWS_TYPES.
CAFEF_NEWS_API = "https://cafef.vn/du-lieu/Ajax/PageNew/News.ashx"
CAFEF_NEWS_TYPES = (1, 2)
CAFEF_API_PAGE_SIZE = 20
# Headers required for the XHR JSON endpoint to return data
CAFEF_API_HEADERS: Dict[str, str] = {
    **BROWSER_HEADERS,
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://cafef.vn/du-lieu.chn",
}


def _parse_cafef_date(raw_date: str) -> Optional[str]:
    """
    Parse a date string from CafeF into YYYY-MM-DD format.

    CafeF uses several date formats:
    - ISO-like: "2024-01-15T10:30:00"
    - Vietnamese: "15/01/2024" or "15-01-2024"
    - With time: "15/01/2024 10:30"

    Returns None if parsing fails.
    """
    if not raw_date or not raw_date.strip():
        return None

    raw_date = raw_date.strip()

    # Try ISO format first (e.g. "2024-01-15T10:30:00")
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
    ):
        try:
            return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fallback: try to extract a date-like pattern from the string
    iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", raw_date)
    if iso_match:
        return iso_match.group(1)

    vn_match = re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})", raw_date)
    if vn_match:
        day, month, year = vn_match.groups()
        return f"{year}-{month}-{day}"

    logger.warning("Could not parse CafeF date: %s", raw_date)
    return None


def _parse_cafef_api_date(raw_date: str) -> Optional[str]:
    """Parse a CafeF JSON API date into YYYY-MM-DD.

    The API returns dates in ASP.NET format ``/Date(1754413200000)/`` where
    the number is milliseconds since the Unix epoch. Falls back to the
    generic :func:`_parse_cafef_date` for any other format.

    Returns None if parsing fails.
    """
    if not raw_date:
        return None
    m = re.search(r"/Date\((-?\d+)\)/", raw_date)
    if m:
        try:
            ts_ms = int(m.group(1))
            return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")
        except (ValueError, OSError, OverflowError):
            return None
    # Fall back to the generic parser for plain date strings
    return _parse_cafef_date(raw_date)


def _parse_cafef_page(
    html: str,
    existing_urls: Set[str],
    start_date: str,
) -> tuple:
    """
    Parse a single CafeF listing page and extract article metadata.

    Args:
        html: Raw HTML content of the page.
        existing_urls: Set of URLs already collected (for dedup).
        start_date: Earliest date to collect (YYYY-MM-DD).

    Returns:
        (articles, should_stop):
        - articles: list of article dicts with keys
          [date, title, description, url, source]
        - should_stop: True if we've gone past the start_date boundary
          and should stop paginating.
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    found_old_article = False

    # CafeF article listing selectors — the site uses several possible
    # structures.  We try multiple CSS selectors to be resilient to
    # minor layout changes.
    # NOTE: These selectors may need adjustment if CafeF changes its
    # page structure (Req 2.12).
    article_elements = soup.select(
        "div.tlitem, li.news-item, div.item-news, "
        "div.list-news > ul > li, div.news-list > div"
    )

    # Fallback: if no articles found with specific selectors, try
    # looking for common link patterns within the main content area.
    if not article_elements:
        # Try broader selectors
        article_elements = soup.select(
            "div.content-list-news li, div.list_news li, "
            "div.box-category-content li"
        )

    for elem in article_elements:
        try:
            # Extract title and URL from the first <a> with a title or
            # meaningful text
            link_tag = elem.select_one("a[title], h3 a, h2 a, a.title")
            if link_tag is None:
                # Try any <a> with href containing .chn
                link_tag = elem.select_one("a[href*='.chn']")
            if link_tag is None:
                continue

            title = (
                link_tag.get("title", "").strip()
                or link_tag.get_text(strip=True)
            )
            if not title:
                continue

            href = link_tag.get("href", "")
            if not href:
                continue

            # Build absolute URL
            url = href if href.startswith("http") else urljoin(
                "https://cafef.vn", href
            )

            # Skip duplicates (Req 2.8)
            if is_duplicate(url, existing_urls):
                continue

            # Extract description — usually in a <p> or <span> with
            # class containing "sapo", "desc", or "summary"
            desc_tag = elem.select_one(
                "p.sapo, span.sapo, p.description, div.summary, "
                "p.desc, span.desc, p.knswli-sapo"
            )
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Extract publication date — look for <span> or <time> with
            # date-like content
            date_str = None
            time_tag = elem.select_one(
                "time, span.time, span.date, span.knswli-time, "
                "span.publish-time, span.dateandcate"
            )
            if time_tag:
                date_str = (
                    time_tag.get("datetime", "")
                    or time_tag.get_text(strip=True)
                )

            # Fallback: search for date pattern in the element text
            if not date_str:
                elem_text = elem.get_text()
                date_match = re.search(
                    r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2})",
                    elem_text,
                )
                if date_match:
                    date_str = date_match.group(1)

            parsed_date = _parse_cafef_date(date_str) if date_str else None

            # Check date boundary — stop if article is before start_date
            if parsed_date and parsed_date < start_date:
                found_old_article = True
                continue

            article = {
                "date": parsed_date or "",
                "title": title,
                "description": description,
                "url": url,
                "source": "cafef",
            }

            if validate_article(article):
                articles.append(article)
                existing_urls.add(url)

        except Exception as exc:
            # If HTML structure cannot be parsed for this element,
            # log and skip (Req 2.12)
            logger.warning(
                "Failed to parse CafeF article element: %s", exc
            )
            continue

    return articles, found_old_article


def _parse_cafef_api_page(
    items: List[Dict],
    existing_urls: Set[str],
    start_date: str,
) -> Tuple[List[Dict], bool]:
    """Parse one page of CafeF JSON API items into article dicts.

    Args:
        items: The ``Data`` list from a News.ashx JSON response.
        existing_urls: Set of URLs already collected (for dedup), mutated.
        start_date: Earliest date to collect (YYYY-MM-DD).

    Returns:
        (articles, found_old_article) where found_old_article is True if any
        item predates start_date (signal to stop paginating, since the API
        returns items in reverse-chronological order).
    """
    articles: List[Dict] = []
    found_old_article = False

    for item in items:
        try:
            title = (item.get("Title") or "").strip()
            link = (item.get("LinkDetail") or "").strip()
            if not title or not link:
                continue

            # Strip any tracking query string and build an absolute URL
            link = link.split("?")[0]
            url = link if link.startswith("http") else urljoin(
                "https://cafef.vn", link
            )

            if is_duplicate(url, existing_urls):
                continue

            parsed_date = _parse_cafef_api_date(item.get("DeployDate"))

            # API returns newest-first; once we pass start_date we can stop.
            if parsed_date and parsed_date < start_date:
                found_old_article = True
                continue

            article = {
                "date": parsed_date or "",
                "title": title,
                "description": (item.get("SubTitle") or "").strip(),
                "url": url,
                "source": "cafef",
            }

            if validate_article(article):
                articles.append(article)
                existing_urls.add(url)

        except Exception as exc:
            logger.warning("Failed to parse CafeF API item: %s", exc)
            continue

    return articles, found_old_article


def scrape_cafef(
    ticker: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> pd.DataFrame:
    """
    Scrape articles from CafeF for a single VN30 ticker.

    Uses CafeF's JSON news API (``News.ashx``) rather than scraping rendered
    HTML, which is far more robust to layout changes. For each configured
    NewsType (company disclosures and corporate events), it paginates from the
    newest articles backwards until it reaches *start_date* or an empty page.

    Args:
        ticker: VN30 ticker symbol (e.g. "VNM").
        start_date: Earliest publication date to collect (YYYY-MM-DD).
        rate_limiter: RateLimiter instance for per-domain throttling.
        existing_urls: Set of already-collected URLs for dedup.
        scraping_cfg: Dict with max_retries, backoff_factor,
            request_timeout keys.

    Returns:
        DataFrame with columns [date, title, description, url, source].
        May be empty if scraping fails or no new articles are found.
    """
    all_articles: List[Dict] = []
    max_retries = scraping_cfg.get("max_retries", 3)
    backoff_factor = scraping_cfg.get("backoff_factor", 2)
    timeout = scraping_cfg.get("request_timeout", 30)

    # Cap pages to avoid runaway pagination; ~50 pages × 20 = 1000 items per
    # NewsType, which comfortably covers several years of history.
    max_pages = 50
    ticker_lower = ticker.lower()

    for news_type in CAFEF_NEWS_TYPES:
        for page in range(1, max_pages + 1):
            url = (
                f"{CAFEF_NEWS_API}?Symbol={ticker_lower}"
                f"&NewsType={news_type}"
                f"&PageIndex={page}&PageSize={CAFEF_API_PAGE_SIZE}"
            )

            logger.debug(
                "Fetching CafeF API (NewsType=%d) page %d for %s: %s",
                news_type, page, ticker, url,
            )

            response = fetch_with_retry(
                url,
                rate_limiter=rate_limiter,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                timeout=timeout,
                headers=CAFEF_API_HEADERS,
            )

            if response is None:
                logger.warning(
                    "Failed to fetch CafeF API (NewsType=%d) page %d for %s. "
                    "Stopping this NewsType.",
                    news_type, page, ticker,
                )
                break

            # Parse the JSON payload
            try:
                payload = response.json()
                items = payload.get("Data") or []
            except Exception as exc:
                # If the response is not valid JSON (e.g. CafeF changed the
                # endpoint), log and stop this NewsType rather than crashing
                # (Req 2.12). NOTE: update CAFEF_NEWS_API if the API changes.
                logger.warning(
                    "Failed to parse CafeF API JSON (NewsType=%d) page %d "
                    "for %s (URL: %s): %s. API format may have changed.",
                    news_type, page, ticker, url, exc,
                )
                break

            if not items:
                logger.debug(
                    "CafeF API: no items on NewsType=%d page %d for %s. "
                    "Stopping this NewsType.",
                    news_type, page, ticker,
                )
                break

            articles, should_stop = _parse_cafef_api_page(
                items, existing_urls, start_date
            )

            if articles:
                all_articles.extend(articles)
                logger.debug(
                    "CafeF API NewsType=%d page %d for %s: %d new articles",
                    news_type, page, ticker, len(articles),
                )

            if should_stop:
                logger.debug(
                    "Reached articles before %s on NewsType=%d page %d for "
                    "%s. Stopping this NewsType.",
                    start_date, news_type, page, ticker,
                )
                break

    logger.info(
        "CafeF: collected %d articles for %s", len(all_articles), ticker
    )

    if not all_articles:
        return pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

    # De-duplicate across NewsTypes (an article can appear in both)
    df = pd.DataFrame(all_articles)
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Vietstock scraper (Task 4.3)
# ---------------------------------------------------------------------------

# Vietstock URL patterns for ticker-specific news (Req 2.2).
# Vietstock is a JavaScript-heavy site.  The primary approach uses the
# tag-based search page which returns articles associated with a ticker.
# An alternative is the finance sub-domain ticker page.
#
# NOTE: These URL patterns may need adjustment if Vietstock restructures
# its site.  The tag endpoint is the most reliable for public access.
VIETSTOCK_TAG_URL = "https://vietstock.vn/tag/{ticker}"
VIETSTOCK_TAG_PAGE_URL = "https://vietstock.vn/tag/{ticker}/page/{page}"
# Alternative: finance sub-domain ticker news page
VIETSTOCK_FINANCE_URL = (
    "https://finance.vietstock.vn/{ticker}/tin-tuc.htm"
)

# Primary (working) endpoint: the finance sub-domain "tin mới nhất" page
# server-renders a #latest-news table with ~20 recent articles per ticker.
# This is robust (no JS needed). Discovered from the live site.
# NOTE: This page exposes only the latest ~20 articles (no deep pagination).
VIETSTOCK_LATEST_NEWS_URL = (
    "https://finance.vietstock.vn/{ticker}/tin-moi-nhat.htm"
)

# Deep-pagination endpoint (discovered from the latest-news page JS):
#   $('#latest-news').load("/View/PagingNewsContent",
#       {view:1, code, type:1, fromDate, toDate, channelID:-1, page, pageSize})
# Returns a lightweight HTML fragment (~8KB) listing ~20 articles per page,
# ordered newest-first, paginating years back into the past. This is far
# better than the latest-news page (which only shows ~20 recent items).
# NOTE: Update this if Vietstock changes the endpoint or its parameters.
VIETSTOCK_PAGING_URL = "https://finance.vietstock.vn/View/PagingNewsContent"
VIETSTOCK_PAGING_PAGE_SIZE = 20
VIETSTOCK_PAGING_MAX_PAGES = 200


def _parse_vietstock_date(raw_date: str) -> Optional[str]:
    """
    Parse a date string from Vietstock into YYYY-MM-DD format.

    Vietstock uses several date formats:
    - ISO-like: "2024-01-15T10:30:00"
    - Vietnamese: "15/01/2024" or "15-01-2024"
    - With time: "15/01/2024 10:30"
    - Relative: "2 giờ trước", "1 ngày trước" (not parsed — returns None)

    Returns None if parsing fails.
    """
    if not raw_date or not raw_date.strip():
        return None

    raw_date = raw_date.strip()

    # Try standard date formats
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
    ):
        try:
            return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fallback: try to extract a date-like pattern from the string
    iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", raw_date)
    if iso_match:
        return iso_match.group(1)

    vn_match = re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})", raw_date)
    if vn_match:
        day, month, year = vn_match.groups()
        return f"{year}-{month}-{day}"

    logger.warning("Could not parse Vietstock date: %s", raw_date)
    return None


def _parse_vietstock_page(
    html: str,
    existing_urls: Set[str],
    start_date: str,
) -> tuple:
    """
    Parse a single Vietstock listing page and extract article metadata.

    Vietstock is heavily JavaScript-rendered, so the raw HTML may contain
    limited content.  This parser attempts multiple CSS selector strategies
    to extract whatever is publicly visible.

    When content appears to be access-restricted (login wall), the parser
    collects only the publicly visible title and summary and logs a note
    (Req 2.3).

    Args:
        html: Raw HTML content of the page.
        existing_urls: Set of URLs already collected (for dedup).
        start_date: Earliest date to collect (YYYY-MM-DD).

    Returns:
        (articles, should_stop):
        - articles: list of article dicts with keys
          [date, title, description, url, source]
        - should_stop: True if we've gone past the start_date boundary
          and should stop paginating.

    NOTE: The CSS selectors below may need adjustment if Vietstock
    changes its page structure (Req 2.12).
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    found_old_article = False

    # --- Detect login wall / access restriction (Req 2.3) ---
    # Vietstock sometimes shows a login prompt or paywall overlay.
    # NOTE: These selectors may need adjustment if Vietstock changes
    # its login wall structure.
    login_indicators = soup.select(
        "div.login-required, div.paywall, div.modal-login, "
        "form[action*='login'], div.require-login, "
        "div.content-locked, div.premium-content"
    )
    if login_indicators:
        logger.info(
            "Vietstock: login wall detected — collecting only publicly "
            "visible title and summary (Req 2.3)."
        )

    # --- Article element selectors ---
    # Vietstock uses various container structures for article listings.
    # NOTE: These selectors may need adjustment if Vietstock changes
    # its page structure (Req 2.12).
    article_elements = soup.select(
        "div.news-item, li.news-item, div.item-news, "
        "article.story, div.story, div.article-item, "
        "div.m-b-15, div.single-news, div.content-news-item"
    )

    # Fallback: try broader selectors if specific ones yield nothing
    if not article_elements:
        # NOTE: These fallback selectors may need adjustment if
        # Vietstock changes its page structure (Req 2.12).
        article_elements = soup.select(
            "div.list-news li, div.news-list li, "
            "div.content-list li, div.search-result-item, "
            "div.tag-content div.m-b-10, div[class*='news'] li"
        )

    # Second fallback: look for any <a> tags with article-like hrefs
    # inside the main content area
    if not article_elements:
        main_content = soup.select_one(
            "div.content, div.main-content, div#content, "
            "div.container, main, section.news"
        )
        if main_content:
            article_elements = main_content.select("div, li, article")

    for elem in article_elements:
        try:
            # Extract title and URL from the first meaningful <a> tag
            # NOTE: These link selectors may need adjustment if
            # Vietstock changes its page structure (Req 2.12).
            link_tag = elem.select_one(
                "a[title], h3 a, h2 a, a.title, a.story-title, "
                "a[href*='.htm'], a[href*='vietstock.vn']"
            )
            if link_tag is None:
                continue

            title = (
                link_tag.get("title", "").strip()
                or link_tag.get_text(strip=True)
            )
            if not title:
                continue

            href = link_tag.get("href", "")
            if not href:
                continue

            # Build absolute URL
            url = href if href.startswith("http") else urljoin(
                "https://vietstock.vn", href
            )

            # Skip duplicates (Req 2.8)
            if is_duplicate(url, existing_urls):
                continue

            # Extract description — Vietstock uses various class names
            # for article summaries.
            # NOTE: These description selectors may need adjustment if
            # Vietstock changes its page structure (Req 2.12).
            desc_tag = elem.select_one(
                "p.sapo, p.description, p.summary, span.sapo, "
                "div.summary, div.description, p.excerpt, "
                "p.content-brief, span.desc"
            )
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Check for access-restricted content indicators on this
            # specific article (Req 2.3)
            restricted_tag = elem.select_one(
                "span.premium, span.vip, span.locked, "
                "i.fa-lock, span.icon-lock, div.premium-badge"
            )
            if restricted_tag:
                logger.debug(
                    "Vietstock: article is access-restricted, "
                    "collecting only public title/summary: %s", url
                )

            # Extract publication date
            # NOTE: These date selectors may need adjustment if
            # Vietstock changes its page structure (Req 2.12).
            date_str = None
            time_tag = elem.select_one(
                "time, span.time, span.date, span.publish-time, "
                "span.datetime, span.created-date, "
                "span[class*='time'], span[class*='date']"
            )
            if time_tag:
                date_str = (
                    time_tag.get("datetime", "")
                    or time_tag.get("content", "")
                    or time_tag.get_text(strip=True)
                )

            # Fallback: search for date pattern in the element text
            if not date_str:
                elem_text = elem.get_text()
                date_match = re.search(
                    r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2})",
                    elem_text,
                )
                if date_match:
                    date_str = date_match.group(1)

            parsed_date = (
                _parse_vietstock_date(date_str) if date_str else None
            )

            # Check date boundary — stop if article is before start_date
            if parsed_date and parsed_date < start_date:
                found_old_article = True
                continue

            article = {
                "date": parsed_date or "",
                "title": title,
                "description": description,
                "url": url,
                "source": "vietstock",
            }

            if validate_article(article):
                articles.append(article)
                existing_urls.add(url)

        except Exception as exc:
            # If HTML structure cannot be parsed for this element,
            # log and skip (Req 2.12)
            logger.warning(
                "Failed to parse Vietstock article element: %s. "
                "HTML selectors may need adjustment if page structure "
                "changed.",
                exc,
            )
            continue

    return articles, found_old_article


def _parse_vietstock_latest_news(
    html: str,
    existing_urls: Set[str],
    start_date: str,
) -> Tuple[List[Dict], bool]:
    """Parse the Vietstock finance ``#latest-news`` table.

    The ``finance.vietstock.vn/{ticker}/tin-moi-nhat.htm`` page server-renders
    a table where each row has::

        <tr><td class="col-date">22/06/2026</td>
            <td><a class="news-link" href="//vietstock.vn/..." title="...">...</a></td></tr>

    This is robust structured data (no JS rendering needed).

    Args:
        html: Raw HTML of the tin-moi-nhat page.
        existing_urls: Set of URLs already collected (for dedup), mutated.
        start_date: Earliest date to collect (YYYY-MM-DD).

    Returns:
        (articles, found_old_article).
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    found_old_article = False

    table = soup.select_one("#latest-news")
    if table is None:
        return articles, found_old_article

    for a in table.select("a.news-link, a.text-link, a[href]"):
        try:
            href = a.get("href", "")
            title = (a.get("title") or a.get_text(strip=True)).strip()
            if not href or not title:
                continue

            # Only keep real article links (they contain a /YYYY/MM/ path)
            if not re.search(r"/\d{4}/\d{2}/", href):
                continue

            url = href if href.startswith("http") else (
                "https:" + href if href.startswith("//")
                else urljoin("https://vietstock.vn", href)
            )

            if is_duplicate(url, existing_urls):
                continue

            # Date lives in the sibling <td class="col-date"> of the row
            date_str = None
            tr = a.find_parent("tr")
            if tr is not None:
                dtd = tr.select_one("td.col-date")
                if dtd:
                    date_str = dtd.get_text(strip=True)
            # Fallback: date is embedded in the URL path /YYYY/MM/
            if not date_str:
                m = re.search(r"/(\d{4})/(\d{2})/", href)
                if m:
                    date_str = f"{m.group(1)}-{m.group(2)}-01"

            parsed_date = _parse_vietstock_date(date_str) if date_str else None

            if parsed_date and parsed_date < start_date:
                found_old_article = True
                continue

            article = {
                "date": parsed_date or "",
                "title": title,
                "description": "",
                "url": url,
                "source": "vietstock",
            }

            if validate_article(article):
                articles.append(article)
                existing_urls.add(url)

        except Exception as exc:
            logger.warning(
                "Failed to parse Vietstock latest-news row: %s", exc
            )
            continue

    return articles, found_old_article


def _parse_vietstock_paging_page(
    html: str,
    existing_urls: Set[str],
    start_date: str,
) -> Tuple[List[Dict], bool]:
    """Parse one /View/PagingNewsContent HTML fragment into article dicts.

    The fragment lists article anchors whose href contains a '/YYYY/MM/' date
    path, plus an inline 'dd/mm/yyyy' date near each item. Returns
    (articles, found_old) where found_old signals an item older than
    start_date (the feed is newest-first, so we can stop paginating).

    NOTE: Selectors/patterns may need adjustment if Vietstock changes the
    fragment structure.
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    found_old = False
    seen_on_page: Set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Article detail URLs look like //vietstock.vn/2026/06/slug-123456.htm
        if not re.search(r"/\d{4}/\d{2}/", href):
            continue
        title = unescape((a.get("title") or a.get_text(strip=True)).strip())
        if not title or len(title) < 20:
            continue

        url = href
        if url.startswith("//"):
            url = "https:" + url
        elif not url.startswith("http"):
            url = urljoin("https://vietstock.vn", url)
        url = url.split("?")[0]

        if url in seen_on_page or is_duplicate(url, existing_urls):
            continue

        # Date: prefer a 'dd/mm/yyyy' near the anchor; fall back to the
        # '/YYYY/MM/' path in the URL (day defaults to 01).
        parsed_date = None
        node = a
        for _ in range(3):
            node = node.parent
            if node is None:
                break
            dm = re.search(r"(\d{2}/\d{2}/\d{4})", node.get_text(" ", strip=True))
            if dm:
                parsed_date = _parse_vietstock_date(dm.group(1))
                break
        if not parsed_date:
            pm = re.search(r"/(\d{4})/(\d{2})/", href)
            if pm:
                parsed_date = f"{pm.group(1)}-{pm.group(2)}-01"

        if parsed_date and parsed_date < start_date:
            found_old = True
            continue

        article = {
            "date": parsed_date or "",
            "title": title,
            "description": "",
            "url": url,
            "source": "vietstock",
        }
        if validate_article(article):
            articles.append(article)
            seen_on_page.add(url)
            existing_urls.add(url)

    return articles, found_old


def _scrape_vietstock_paging(
    ticker: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> List[Dict]:
    """Deep-scrape Vietstock company news via /View/PagingNewsContent.

    Paginates newest-first until reaching start_date or an empty page.
    Uses a session primed with the ticker's latest-news page so the AJAX
    endpoint returns content.
    """
    max_retries = scraping_cfg.get("max_retries", 3)
    backoff_factor = scraping_cfg.get("backoff_factor", 2)
    timeout = scraping_cfg.get("request_timeout", 30)
    ticker_upper = ticker.upper()

    headers = {
        **BROWSER_HEADERS,
        "Accept-Encoding": "gzip, deflate",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": VIETSTOCK_LATEST_NEWS_URL.format(ticker=ticker_upper),
    }

    all_articles: List[Dict] = []
    empty_streak = 0

    for page in range(1, VIETSTOCK_PAGING_MAX_PAGES + 1):
        params = {
            "view": 1, "code": ticker_upper, "type": 1,
            "fromDate": "", "toDate": "", "channelID": -1,
            "page": page, "pageSize": VIETSTOCK_PAGING_PAGE_SIZE,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{VIETSTOCK_PAGING_URL}?{query}"

        response = fetch_with_retry(
            url,
            rate_limiter=rate_limiter,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            timeout=timeout,
            headers=headers,
        )
        if response is None:
            logger.warning(
                "Vietstock paging: failed to fetch page %d for %s. Stopping.",
                page, ticker,
            )
            break

        try:
            articles, should_stop = _parse_vietstock_paging_page(
                response.text, existing_urls, start_date
            )
        except Exception as exc:
            logger.warning(
                "Vietstock paging: failed to parse page %d for %s: %s. "
                "Skipping page.", page, ticker, exc,
            )
            continue

        if articles:
            all_articles.extend(articles)
            empty_streak = 0
        else:
            empty_streak += 1

        if should_stop:
            break
        if empty_streak >= 2 and page > 1:
            break

    logger.info(
        "Vietstock paging for %s: %d articles", ticker, len(all_articles)
    )
    return all_articles


def scrape_vietstock(
    ticker: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> pd.DataFrame:
    """
    Scrape articles from Vietstock for a single VN30 ticker.

    Primary strategy: the finance sub-domain "tin mới nhất" page
    (``finance.vietstock.vn/{ticker}/tin-moi-nhat.htm``) server-renders a
    table of recent articles with clean dates — robust and JS-free. Falls
    back to the tag-based search page if the table is unavailable.

    Args:
        ticker: VN30 ticker symbol (e.g. "VNM").
        start_date: Earliest publication date to collect (YYYY-MM-DD).
        rate_limiter: RateLimiter instance for per-domain throttling.
        existing_urls: Set of already-collected URLs for dedup.
        scraping_cfg: Dict with max_retries, backoff_factor,
            request_timeout keys.

    Returns:
        DataFrame with columns [date, title, description, url, source].
        May be empty if scraping fails or no new articles are found.
    """
    all_articles: List[Dict] = []
    max_retries = scraping_cfg.get("max_retries", 3)
    backoff_factor = scraping_cfg.get("backoff_factor", 2)
    timeout = scraping_cfg.get("request_timeout", 30)

    ticker_upper = ticker.upper()

    # --- Strategy 0: deep pagination via /View/PagingNewsContent (primary) ---
    # This paginates years back, yielding far more than the ~20-item
    # latest-news table. Strategies 1/2 below remain as fallbacks.
    try:
        paging_articles = _scrape_vietstock_paging(
            ticker=ticker,
            start_date=start_date,
            rate_limiter=rate_limiter,
            existing_urls=existing_urls,
            scraping_cfg=scraping_cfg,
        )
        all_articles.extend(paging_articles)
    except Exception as exc:
        logger.warning(
            "Vietstock paging strategy failed for %s: %s. Falling back.",
            ticker, exc,
        )

    # --- Strategy 1: finance "tin mới nhất" table (fallback if paging empty) ---
    latest_url = VIETSTOCK_LATEST_NEWS_URL.format(ticker=ticker_upper)
    logger.debug("Fetching Vietstock latest-news for %s: %s", ticker, latest_url)

    response = fetch_with_retry(
        latest_url,
        rate_limiter=rate_limiter,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        timeout=timeout,
    ) if not all_articles else None

    if response is not None:
        try:
            articles, _ = _parse_vietstock_latest_news(
                response.text, existing_urls, start_date
            )
            all_articles.extend(articles)
            logger.debug(
                "Vietstock latest-news for %s: %d articles",
                ticker, len(articles),
            )
        except Exception as exc:
            logger.warning(
                "Failed to parse Vietstock latest-news for %s (URL: %s): %s. "
                "Falling back to tag search. Selectors may need adjustment "
                "if page structure changed.",
                ticker, latest_url, exc,
            )

    # --- Strategy 2: Tag-based search (fallback) ---
    if not all_articles:
        max_pages = 100
        logger.info(
            "Vietstock latest-news yielded no articles for %s. "
            "Trying tag-search fallback.",
            ticker,
        )
        for page in range(1, max_pages + 1):
            if page == 1:
                url = VIETSTOCK_TAG_URL.format(ticker=ticker_upper)
            else:
                url = VIETSTOCK_TAG_PAGE_URL.format(
                    ticker=ticker_upper, page=page
                )

            logger.debug(
                "Fetching Vietstock tag page %d for %s: %s",
                page, ticker, url,
            )

            response = fetch_with_retry(
                url,
                rate_limiter=rate_limiter,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                timeout=timeout,
            )

            if response is None:
                logger.warning(
                    "Failed to fetch Vietstock tag page %d for %s. "
                    "Stopping pagination.",
                    page, ticker,
                )
                break

            # Check for access-restricted response (Req 2.3)
            if response.status_code in (401, 403):
                logger.info(
                    "Vietstock: access restricted (HTTP %d) for %s. "
                    "Collecting only publicly visible content.",
                    response.status_code, ticker,
                )

            try:
                articles, should_stop = _parse_vietstock_page(
                    response.text, existing_urls, start_date
                )
            except Exception as exc:
                # If HTML structure cannot be parsed, log the URL and skip
                # that page rather than raising an unhandled exception
                # (Req 2.12). NOTE: The CSS selectors in _parse_vietstock_page
                # may need adjustment if Vietstock changes its page structure.
                logger.warning(
                    "Failed to parse Vietstock tag page %d for %s (URL: %s): "
                    "%s. Skipping page. HTML selectors may need adjustment "
                    "if page structure changed.",
                    page, ticker, url, exc,
                )
                continue

            if articles:
                all_articles.extend(articles)
                logger.debug(
                    "Vietstock tag page %d for %s: %d new articles",
                    page, ticker, len(articles),
                )

            # Stop conditions
            if should_stop:
                logger.debug(
                    "Reached articles before %s on Vietstock page %d for %s. "
                    "Stopping pagination.",
                    start_date, page, ticker,
                )
                break

            if not articles and page > 1:
                logger.debug(
                    "No new articles on Vietstock tag page %d for %s. "
                    "Stopping pagination.",
                    page, ticker,
                )
                break

    logger.info(
        "Vietstock: collected %d articles for %s",
        len(all_articles), ticker,
    )

    if not all_articles:
        return pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

    df = pd.DataFrame(all_articles)
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Tinnhanhchungkhoan (TNCK) scraper (Task 4.4)
# ---------------------------------------------------------------------------

# TNCK URL patterns for search and category pages (Req 2.4).
# TNCK is scraped broadly — entity matching is handled in TASK 3.
# The search endpoint returns server-rendered <article class="story">
# results with clean ISO datetimes. Discovered from the live site.
# NOTE: These URL patterns may need adjustment if TNCK restructures its site.
TNCK_SEARCH_URL = "https://www.tinnhanhchungkhoan.vn/tim-kiem.html"
TNCK_SEARCH_PAGE_URL = (
    "https://www.tinnhanhchungkhoan.vn/tim-kiem/trang-{page}.html"
)
TNCK_CATEGORY_URLS = [
    "https://www.tinnhanhchungkhoan.vn/chung-khoan/",
    "https://www.tinnhanhchungkhoan.vn/doanh-nghiep/",
    "https://www.tinnhanhchungkhoan.vn/ngan-hang/",
    "https://www.tinnhanhchungkhoan.vn/bat-dong-san/",
    "https://www.tinnhanhchungkhoan.vn/tai-chinh/",
]
TNCK_CATEGORY_PAGE_URL = "{category_url}page/{page}/"


def _parse_tnck_date(raw_date: str) -> Optional[str]:
    """
    Parse a date string from Tinnhanhchungkhoan into YYYY-MM-DD format.

    TNCK uses several date formats:
    - ISO-like: "2024-01-15T10:30:00"
    - Vietnamese: "15/01/2024" or "15-01-2024"
    - With time: "15/01/2024 10:30"
    - Relative: "2 giờ trước" (not parsed — returns None)

    Returns None if parsing fails.
    """
    if not raw_date or not raw_date.strip():
        return None

    raw_date = raw_date.strip()

    # Try standard date formats
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
        "%H:%M %d/%m/%Y",
    ):
        try:
            return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fallback: try to extract a date-like pattern from the string
    iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", raw_date)
    if iso_match:
        return iso_match.group(1)

    vn_match = re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})", raw_date)
    if vn_match:
        day, month, year = vn_match.groups()
        return f"{year}-{month}-{day}"

    logger.warning("Could not parse TNCK date: %s", raw_date)
    return None


def _parse_tnck_page(
    html: str,
    existing_urls: Set[str],
    start_date: str,
) -> tuple:
    """
    Parse a single TNCK listing/search page and extract article metadata.

    Args:
        html: Raw HTML content of the page.
        existing_urls: Set of URLs already collected (for dedup).
        start_date: Earliest date to collect (YYYY-MM-DD).

    Returns:
        (articles, should_stop):
        - articles: list of article dicts with keys
          [date, title, description, url, source]
        - should_stop: True if we've gone past the start_date boundary
          and should stop paginating.

    NOTE: The CSS selectors below may need adjustment if TNCK
    changes its page structure (Req 2.12).
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    found_old_article = False

    # --- Article element selectors ---
    # TNCK uses various container structures for article listings.
    # NOTE: These selectors may need adjustment if TNCK changes
    # its page structure (Req 2.12).
    article_elements = soup.select(
        "article.story, div.story, div.story__thumb, "
        "div.article-item, li.news-item, div.item-news, "
        "div.story-listing__story, div.highlight-item"
    )

    # Fallback: try broader selectors if specific ones yield nothing
    if not article_elements:
        # NOTE: These fallback selectors may need adjustment if
        # TNCK changes its page structure (Req 2.12).
        article_elements = soup.select(
            "div.list-news li, div.news-list li, "
            "div.content-list li, div.search-result li, "
            "div.zone--timeline article, div.cate-content article, "
            "div[class*='story'] a[href*='tinnhanhchungkhoan']"
        )

    # Second fallback: look for any article-like containers in main content
    if not article_elements:
        main_content = soup.select_one(
            "div.content, div.main-content, div#content, "
            "div.container, main, section.zone"
        )
        if main_content:
            article_elements = main_content.select(
                "article, div.story, div.item, li"
            )

    for elem in article_elements:
        try:
            # Extract title and URL from the first meaningful <a> tag
            # NOTE: These link selectors may need adjustment if
            # TNCK changes its page structure (Req 2.12).
            link_tag = elem.select_one(
                "a[title], h3 a, h2 a, a.story__title, a.cms-link, "
                "a[href*='tinnhanhchungkhoan.vn'], a.title"
            )
            if link_tag is None:
                # If the element itself is an <a> tag
                if elem.name == "a" and elem.get("href"):
                    link_tag = elem
                else:
                    continue

            title = (
                link_tag.get("title", "").strip()
                or link_tag.get_text(strip=True)
            )
            if not title:
                continue

            href = link_tag.get("href", "")
            if not href:
                continue

            # Build absolute URL
            url = href if href.startswith("http") else urljoin(
                "https://tinnhanhchungkhoan.vn", href
            )

            # Skip duplicates (Req 2.8)
            if is_duplicate(url, existing_urls):
                continue

            # Extract description — TNCK uses various class names
            # for article summaries.
            # NOTE: These description selectors may need adjustment if
            # TNCK changes its page structure (Req 2.12).
            desc_tag = elem.select_one(
                "p.sapo, p.description, p.summary, span.sapo, "
                "div.summary, div.description, p.excerpt, "
                "p.story__summary, div.story__summary, "
                "p.cms-desc, span.desc"
            )
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Extract publication date
            # NOTE: These date selectors may need adjustment if
            # TNCK changes its page structure (Req 2.12).
            date_str = None
            time_tag = elem.select_one(
                "time, span.time, span.date, span.publish-time, "
                "span.datetime, span.story__time, span.cms-date, "
                "span[class*='time'], span[class*='date']"
            )
            if time_tag:
                date_str = (
                    time_tag.get("datetime", "")
                    or time_tag.get("content", "")
                    or time_tag.get_text(strip=True)
                )

            # Fallback: search for date pattern in the element text
            if not date_str:
                elem_text = elem.get_text()
                date_match = re.search(
                    r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2})",
                    elem_text,
                )
                if date_match:
                    date_str = date_match.group(1)

            parsed_date = (
                _parse_tnck_date(date_str) if date_str else None
            )

            # Check date boundary — stop if article is before start_date
            if parsed_date and parsed_date < start_date:
                found_old_article = True
                continue

            article = {
                "date": parsed_date or "",
                "title": title,
                "description": description,
                "url": url,
                "source": "tnck",
            }

            if validate_article(article):
                articles.append(article)
                existing_urls.add(url)

        except Exception as exc:
            # If HTML structure cannot be parsed for this element,
            # log and skip (Req 2.12)
            logger.warning(
                "Failed to parse TNCK article element: %s. "
                "HTML selectors may need adjustment if page structure "
                "changed.",
                exc,
            )
            continue

    return articles, found_old_article


def _scrape_tnck_search(
    query: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> List[Dict]:
    """
    Scrape TNCK search results for a single query term.

    Args:
        query: Search term (ticker or company name).
        start_date: Earliest publication date to collect (YYYY-MM-DD).
        rate_limiter: RateLimiter instance for per-domain throttling.
        existing_urls: Set of already-collected URLs for dedup.
        scraping_cfg: Dict with max_retries, backoff_factor,
            request_timeout keys.

    Returns:
        List of article dicts.
    """
    all_articles: List[Dict] = []
    max_retries = scraping_cfg.get("max_retries", 3)
    backoff_factor = scraping_cfg.get("backoff_factor", 2)
    timeout = scraping_cfg.get("request_timeout", 30)
    max_pages = 50

    for page in range(1, max_pages + 1):
        if page == 1:
            url = TNCK_SEARCH_URL
        else:
            url = TNCK_SEARCH_PAGE_URL.format(page=page)

        # Add search query as a GET parameter
        search_url = f"{url}?q={requests.utils.quote(query)}"

        logger.debug(
            "Fetching TNCK search page %d for query '%s': %s",
            page, query, search_url,
        )

        response = fetch_with_retry(
            search_url,
            rate_limiter=rate_limiter,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            timeout=timeout,
        )

        if response is None:
            logger.warning(
                "Failed to fetch TNCK search page %d for query '%s'. "
                "Stopping pagination.",
                page, query,
            )
            break

        try:
            articles, should_stop = _parse_tnck_page(
                response.text, existing_urls, start_date
            )
        except Exception as exc:
            # If HTML structure cannot be parsed, log the URL and skip
            # that page rather than raising an unhandled exception
            # (Req 2.12).  Continue to next page — a single broken page
            # should not abort the entire search pagination.
            # NOTE: The CSS selectors in _parse_tnck_page may need
            # adjustment if TNCK changes its page structure.
            logger.warning(
                "Failed to parse TNCK search page %d for query '%s' "
                "(URL: %s): %s. Skipping page. HTML selectors may need "
                "adjustment if page structure changed.",
                page, query, search_url, exc,
            )
            continue

        if articles:
            all_articles.extend(articles)
            logger.debug(
                "TNCK search page %d for '%s': %d new articles",
                page, query, len(articles),
            )

        # Stop conditions
        if should_stop:
            logger.debug(
                "Reached articles before %s on TNCK search page %d "
                "for '%s'. Stopping pagination.",
                start_date, page, query,
            )
            break

        if not articles and page > 1:
            logger.debug(
                "No new articles on TNCK search page %d for '%s'. "
                "Stopping pagination.",
                page, query,
            )
            break

    return all_articles


def _scrape_tnck_category(
    category_url: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> List[Dict]:
    """
    Scrape TNCK category page for articles.

    Args:
        category_url: Base URL of the category page.
        start_date: Earliest publication date to collect (YYYY-MM-DD).
        rate_limiter: RateLimiter instance for per-domain throttling.
        existing_urls: Set of already-collected URLs for dedup.
        scraping_cfg: Dict with max_retries, backoff_factor,
            request_timeout keys.

    Returns:
        List of article dicts.
    """
    all_articles: List[Dict] = []
    max_retries = scraping_cfg.get("max_retries", 3)
    backoff_factor = scraping_cfg.get("backoff_factor", 2)
    timeout = scraping_cfg.get("request_timeout", 30)
    max_pages = 100

    for page in range(1, max_pages + 1):
        if page == 1:
            url = category_url
        else:
            url = TNCK_CATEGORY_PAGE_URL.format(
                category_url=category_url, page=page
            )

        logger.debug(
            "Fetching TNCK category page %d: %s", page, url,
        )

        response = fetch_with_retry(
            url,
            rate_limiter=rate_limiter,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            timeout=timeout,
        )

        if response is None:
            logger.warning(
                "Failed to fetch TNCK category page %d: %s. "
                "Stopping pagination.",
                page, url,
            )
            break

        try:
            articles, should_stop = _parse_tnck_page(
                response.text, existing_urls, start_date
            )
        except Exception as exc:
            # If HTML structure cannot be parsed, log the URL and skip
            # that page rather than raising an unhandled exception
            # (Req 2.12).  Continue to next page — a single broken page
            # should not abort the entire category pagination.
            # NOTE: The CSS selectors in _parse_tnck_page may need
            # adjustment if TNCK changes its page structure.
            logger.warning(
                "Failed to parse TNCK category page %d (URL: %s): %s. "
                "Skipping page. HTML selectors may need adjustment if "
                "page structure changed.",
                page, url, exc,
            )
            continue

        if articles:
            all_articles.extend(articles)
            logger.debug(
                "TNCK category page %d: %d new articles",
                page, len(articles),
            )

        # Stop conditions
        if should_stop:
            logger.debug(
                "Reached articles before %s on TNCK category page %d. "
                "Stopping pagination.",
                start_date, page,
            )
            break

        if not articles and page > 1:
            logger.debug(
                "No new articles on TNCK category page %d. "
                "Stopping pagination.",
                page,
            )
            break

    return all_articles


def _generate_monthly_report(articles_df: pd.DataFrame) -> None:
    """
    Generate and log a monthly article count report for TNCK coverage
    verification (Req 2.5).

    Args:
        articles_df: DataFrame with at least a 'date' column.
    """
    if articles_df.empty:
        logger.info("TNCK monthly report: no articles to report.")
        return

    df = articles_df.copy()
    df["date_parsed"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    df = df.dropna(subset=["date_parsed"])

    if df.empty:
        logger.info("TNCK monthly report: no articles with valid dates.")
        return

    df["year_month"] = df["date_parsed"].dt.to_period("M")
    monthly_counts = df.groupby("year_month").size().sort_index()

    logger.info("=" * 60)
    logger.info("TNCK MONTHLY ARTICLE COUNT REPORT")
    logger.info("=" * 60)
    for period, count in monthly_counts.items():
        logger.info("  %s: %d articles", period, count)
    logger.info("-" * 60)
    logger.info(
        "Total: %d articles across %d months",
        monthly_counts.sum(),
        len(monthly_counts),
    )
    if len(monthly_counts) > 0:
        logger.info(
            "Average: %.1f articles/month",
            monthly_counts.mean(),
        )
    logger.info("=" * 60)


def scrape_tnck(
    ticker: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> pd.DataFrame:
    """
    Scrape articles from Tinnhanhchungkhoan (TNCK) broadly.

    Unlike CafeF and Vietstock, TNCK is scraped without pre-assigning
    tickers — entity matching is handled in TASK 3 (Req 2.4).

    The scraper uses two strategies:
    1. **Search**: Query TNCK's search endpoint with each VN30 ticker
       symbol and company name to find relevant articles.
    2. **Category pages**: Scrape financial category pages (chung-khoan,
       doanh-nghiep, ngan-hang, bat-dong-san, tai-chinh) to capture
       broader market news.

    After scraping, a monthly article count report is generated to
    verify coverage (Req 2.5).

    Args:
        ticker: Ignored for TNCK (scrapes broadly). Pass "ALL" or any
            value.
        start_date: Earliest publication date to collect (YYYY-MM-DD).
        rate_limiter: RateLimiter instance for per-domain throttling.
        existing_urls: Set of already-collected URLs for dedup.
        scraping_cfg: Dict with max_retries, backoff_factor,
            request_timeout keys.

    Returns:
        DataFrame with columns [date, title, description, url, source].
        May be empty if scraping fails or no new articles are found.
    """
    all_articles: List[Dict] = []

    # --- Strategy: Search by VN30 ticker symbols ---
    # TNCK's search endpoint returns server-rendered <article class="story">
    # results with clean ISO datetimes. Searching by ticker symbol surfaces
    # company-relevant articles; entity matching (TASK 3) refines attribution.
    # Category-page scraping was removed — it produced mostly dateless,
    # irrelevant listings (high noise) while search is precise and reliable.
    logger.info("TNCK: searching by VN30 ticker symbols…")
    for vn30_ticker in VN30_TICKERS:
        articles = _scrape_tnck_search(
            query=vn30_ticker,
            start_date=start_date,
            rate_limiter=rate_limiter,
            existing_urls=existing_urls,
            scraping_cfg=scraping_cfg,
        )
        if articles:
            all_articles.extend(articles)
            logger.info(
                "TNCK search '%s': %d new articles",
                vn30_ticker, len(articles),
            )

    logger.info(
        "TNCK: collected %d total articles", len(all_articles)
    )

    if not all_articles:
        return pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

    articles_df = pd.DataFrame(all_articles)
    articles_df = articles_df.drop_duplicates(subset=["url"]).reset_index(drop=True)

    # Generate monthly article count report (Req 2.5)
    _generate_monthly_report(articles_df)

    return articles_df


# ---------------------------------------------------------------------------
# VietnamBiz scraper (news-source-expansion Task 3)
# ---------------------------------------------------------------------------

# VietnamBiz publishes server-rendered category pages with deep pagination.
# Like TNCK, it is scraped broadly (no per-ticker query) — entity matching in
# TASK 3 attributes articles to VN30 tickers.
# Category listing + pagination pattern (verified live):
#   page 1: https://vietnambiz.vn/chung-khoan.htm
#   page N: https://vietnambiz.vn/chung-khoan/trang-{N}.htm
# Real article anchors have href ending in '-<16-digit id>.htm'; the id begins
# with the publication date (YYYYMD...), and the listing also shows a
# 'HH:MM | dd/mm/yyyy' timestamp in the article's parent container.
# NOTE: Update these patterns/selectors if VietnamBiz restructures its site.
VIETNAMBIZ_CATEGORY_URLS = [
    "https://vietnambiz.vn/chung-khoan.htm",
    "https://vietnambiz.vn/doanh-nghiep.htm",
    "https://vietnambiz.vn/tai-chinh.htm",
]
VIETNAMBIZ_CATEGORY_PAGE_URL = "{base}/trang-{page}.htm"
# Matches real article URLs (trailing numeric id), excludes /chu-de/ topic links
_VIETNAMBIZ_ARTICLE_RE = re.compile(r"-(\d{8,})\.htm$")

# VietnamBiz serves Brotli-compressed HTML; if the optional 'brotli' package
# isn't installed, requests cannot decode 'br' and returns truncated/garbled
# content. Advertise only gzip/deflate (always supported) for this domain.
VIETNAMBIZ_HEADERS: Dict[str, str] = {
    **BROWSER_HEADERS,
    "Accept-Encoding": "gzip, deflate",
}


def _category_base(category_url: str) -> str:
    """Strip the trailing '.htm' so we can build '/trang-N.htm' page URLs."""
    return category_url[:-4] if category_url.endswith(".htm") else category_url


def _parse_vietnambiz_id_date(article_id: str) -> Optional[str]:
    """Parse the publication date embedded in a VietnamBiz article id.

    The id starts with YYYY then month and day with variable width, e.g.
    ``2026624182936535`` -> 2026-06-24. We parse year (4) then greedily try
    2-digit then 1-digit month/day combinations and validate via datetime.

    Returns YYYY-MM-DD or None.
    """
    if not article_id or len(article_id) < 6:
        return None
    try:
        year = int(article_id[:4])
    except ValueError:
        return None
    if not (2000 <= year <= 2100):
        return None
    rest = article_id[4:]
    # Try (month_len, day_len) combinations: 2+2, 2+1, 1+2, 1+1
    for mlen, dlen in ((2, 2), (2, 1), (1, 2), (1, 1)):
        if len(rest) < mlen + dlen:
            continue
        try:
            month = int(rest[:mlen])
            day = int(rest[mlen:mlen + dlen])
            return datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _parse_vietnambiz_page(
    html: str,
    existing_urls: Set[str],
    start_date: str,
) -> Tuple[List[Dict], bool]:
    """Parse one VietnamBiz category page into article dicts.

    Date is taken from the listing timestamp ('HH:MM | dd/mm/yyyy') when
    present, falling back to the date embedded in the article id.

    Returns (articles, found_old_article).
    NOTE: Selectors/patterns may need adjustment if VietnamBiz changes layout.
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    found_old = False
    seen_on_page: Set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = _VIETNAMBIZ_ARTICLE_RE.search(href)
        if not m:
            continue
        title = (a.get("title") or a.get_text(strip=True)).strip()
        if not title or len(title) < 20:
            continue
        title = unescape(title)  # decode HTML entities (&#253; etc.)

        url = href if href.startswith("http") else urljoin(
            "https://vietnambiz.vn", href
        )
        if url in seen_on_page or is_duplicate(url, existing_urls):
            continue

        # Date: prefer the listing 'HH:MM | dd/mm/yyyy' near the link,
        # fall back to the id-embedded date.
        parsed_date = None
        node = a
        for _ in range(3):
            node = node.parent
            if node is None:
                break
            dm = re.search(r"(\d{2}/\d{2}/\d{4})", node.get_text(" ", strip=True))
            if dm:
                parsed_date = _parse_tnck_date(dm.group(1))  # dd/mm/yyyy parser
                break
        if not parsed_date:
            parsed_date = _parse_vietnambiz_id_date(m.group(1))

        if parsed_date and parsed_date < start_date:
            found_old = True
            continue

        article = {
            "date": parsed_date or "",
            "title": title,
            "description": "",
            "url": url,
            "source": "vietnambiz",
        }
        if validate_article(article):
            articles.append(article)
            seen_on_page.add(url)
            existing_urls.add(url)

    return articles, found_old


def _scrape_vietnambiz_category(
    category_url: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> List[Dict]:
    """Scrape one VietnamBiz category with pagination until start_date."""
    all_articles: List[Dict] = []
    max_retries = scraping_cfg.get("max_retries", 3)
    backoff_factor = scraping_cfg.get("backoff_factor", 2)
    timeout = scraping_cfg.get("request_timeout", 30)
    max_pages = 250
    base = _category_base(category_url)
    empty_streak = 0

    for page in range(1, max_pages + 1):
        url = category_url if page == 1 else VIETNAMBIZ_CATEGORY_PAGE_URL.format(
            base=base, page=page
        )
        response = fetch_with_retry(
            url,
            rate_limiter=rate_limiter,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            timeout=timeout,
            headers=VIETNAMBIZ_HEADERS,
        )
        if response is None:
            logger.warning(
                "VietnamBiz: failed to fetch %s. Stopping this category.", url
            )
            break

        try:
            articles, should_stop = _parse_vietnambiz_page(
                response.text, existing_urls, start_date
            )
        except Exception as exc:
            # A single broken page should not abort pagination (Req 2.12).
            logger.warning(
                "VietnamBiz: failed to parse %s: %s. Skipping page. "
                "Selectors may need adjustment if layout changed.",
                url, exc,
            )
            continue

        if articles:
            all_articles.extend(articles)
            empty_streak = 0
            logger.debug(
                "VietnamBiz %s page %d: %d new articles", base, page, len(articles)
            )
        else:
            empty_streak += 1

        if should_stop:
            logger.debug(
                "VietnamBiz: reached articles before %s on %s page %d. Stopping.",
                start_date, base, page,
            )
            break
        # Stop if several consecutive pages yield nothing new.
        if empty_streak >= 3 and page > 1:
            logger.debug(
                "VietnamBiz: %d empty pages on %s. Stopping.", empty_streak, base
            )
            break

    return all_articles


def scrape_vietnambiz(
    ticker: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> pd.DataFrame:
    """Scrape VietnamBiz finance/stock category pages broadly.

    Like TNCK, articles are collected without pre-assigning tickers — TASK 3
    handles entity matching (Req 2.4). Iterates several finance categories,
    paginating each until reaching *start_date*.

    Args:
        ticker: Ignored (scrapes broadly). Pass "ALL".
        start_date: Earliest publication date (YYYY-MM-DD).
        rate_limiter: Per-domain throttle.
        existing_urls: Already-collected URLs for dedup.
        scraping_cfg: max_retries / backoff_factor / request_timeout.

    Returns:
        DataFrame [date, title, description, url, source].
    """
    all_articles: List[Dict] = []
    for category_url in VIETNAMBIZ_CATEGORY_URLS:
        logger.info("VietnamBiz: scraping category %s", category_url)
        articles = _scrape_vietnambiz_category(
            category_url=category_url,
            start_date=start_date,
            rate_limiter=rate_limiter,
            existing_urls=existing_urls,
            scraping_cfg=scraping_cfg,
        )
        if articles:
            all_articles.extend(articles)
            logger.info(
                "VietnamBiz category %s: %d new articles",
                category_url, len(articles),
            )

    logger.info("VietnamBiz: collected %d total articles", len(all_articles))

    if not all_articles:
        return pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

    df = pd.DataFrame(all_articles)
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# VnExpress scraper (news-source-expansion — reputable national source)
# ---------------------------------------------------------------------------

# VnExpress server-renders business category pages with deep pagination
# (`-p{N}`). Listing items are <article class="item-news"> with the title in
# h3.title-news > a and summary in p.description. The listing has NO date, so
# the publication date is read from the article detail page's
# <meta itemprop="datePublished"> (ISO 8601). Scraped broadly; TASK 3 maps to
# VN30. NOTE: Update selectors/patterns if VnExpress changes its layout.
VNEXPRESS_CATEGORY_URLS = [
    "https://vnexpress.net/kinh-doanh/chung-khoan",
    "https://vnexpress.net/kinh-doanh/doanh-nghiep",
    "https://vnexpress.net/kinh-doanh/vi-mo",
]
VNEXPRESS_PAGE_SUFFIX = "-p{page}"
VNEXPRESS_MAX_PAGES = 40
_VNEXPRESS_ARTICLE_RE = re.compile(r"-\d{6,}\.html$")


def _parse_vnexpress_detail_date(html: str) -> Optional[str]:
    """Extract YYYY-MM-DD from a VnExpress article page's meta tag."""
    soup = BeautifulSoup(html, "html.parser")
    for sel in (
        "meta[itemprop='datePublished']",
        "meta[property='article:published_time']",
    ):
        el = soup.select_one(sel)
        if el and el.get("content"):
            m = re.search(r"(\d{4}-\d{2}-\d{2})", el["content"])
            if m:
                return m.group(1)
    return None


def _parse_vnexpress_listing(html: str) -> List[Dict]:
    """Extract (title, url, description, date) from a VnExpress listing page.

    The publication date is recovered from the thumbnail image URL, which
    embeds a '/YYYY/MM/DD/' path (e.g. i1-kinhdoanh.vnecdn.net/2026/06/26/...).
    This avoids a costly per-article detail fetch. Items without a usable
    thumbnail date get an empty date (the caller may then fetch the detail
    page as a fallback).
    """
    soup = BeautifulSoup(html, "html.parser")
    items: List[Dict] = []
    seen: Set[str] = set()
    for art in soup.select("article.item-news"):
        a = art.select_one("h3.title-news a, h2.title-news a, .title-news a")
        if not a:
            continue
        href = a.get("href", "")
        if not _VNEXPRESS_ARTICLE_RE.search(href):
            continue
        title = unescape((a.get("title") or a.get_text(strip=True)).strip())
        if not title or len(title) < 20:
            continue
        url = href if href.startswith("http") else urljoin(
            "https://vnexpress.net", href
        )
        url = url.split("?")[0]
        if url in seen:
            continue
        seen.add(url)
        desc_el = art.select_one("p.description a, p.description")
        desc = unescape(desc_el.get_text(strip=True)) if desc_el else ""

        # Date from the thumbnail image URL: .../YYYY/MM/DD/...
        listing_date = ""
        img = art.select_one("img[src], source[srcset]")
        img_url = ""
        if img is not None:
            img_url = img.get("src") or img.get("srcset") or ""
        dm = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", img_url)
        if dm:
            listing_date = f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"

        items.append({
            "title": title, "url": url, "description": desc,
            "date": listing_date,
        })
    return items


def _scrape_vnexpress_category(
    category_url: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> List[Dict]:
    """Scrape one VnExpress category, fetching each article's date from detail.

    Stops paginating after consecutive pages whose articles are all older than
    start_date (detail dates are checked per article).
    """
    max_retries = scraping_cfg.get("max_retries", 3)
    backoff_factor = scraping_cfg.get("backoff_factor", 2)
    timeout = scraping_cfg.get("request_timeout", 30)

    all_articles: List[Dict] = []
    old_streak_pages = 0

    for page in range(1, VNEXPRESS_MAX_PAGES + 1):
        url = category_url if page == 1 else (
            category_url + VNEXPRESS_PAGE_SUFFIX.format(page=page)
        )
        resp = fetch_with_retry(
            url, rate_limiter=rate_limiter, max_retries=max_retries,
            backoff_factor=backoff_factor, timeout=timeout,
        )
        if resp is None:
            break

        try:
            listing = _parse_vnexpress_listing(resp.text)
        except Exception as exc:
            logger.warning("VnExpress: failed to parse %s: %s. Skipping.", url, exc)
            continue
        if not listing:
            break

        page_had_recent = False
        for item in listing:
            if is_duplicate(item["url"], existing_urls):
                continue
            # Prefer the date recovered from the thumbnail URL (no extra
            # request). Only fetch the detail page if the listing lacked one.
            parsed_date = item.get("date") or None
            if not parsed_date:
                d = fetch_with_retry(
                    item["url"], rate_limiter=rate_limiter,
                    max_retries=max_retries, backoff_factor=backoff_factor,
                    timeout=timeout,
                )
                parsed_date = (
                    _parse_vnexpress_detail_date(d.text) if d is not None else None
                )
            if parsed_date and parsed_date < start_date:
                continue
            if parsed_date:
                page_had_recent = True
            article = {
                "date": parsed_date or "",
                "title": item["title"],
                "description": item["description"],
                "url": item["url"],
                "source": "vnexpress",
            }
            if validate_article(article):
                all_articles.append(article)
                existing_urls.add(item["url"])

        # If a whole page had no article newer than start_date, the feed has
        # passed our window (VnExpress lists newest-first).
        if not page_had_recent:
            old_streak_pages += 1
        else:
            old_streak_pages = 0
        if old_streak_pages >= 2 and page > 1:
            break

    return all_articles


def scrape_vnexpress(
    ticker: str,
    start_date: str,
    rate_limiter: RateLimiter,
    existing_urls: Set[str],
    scraping_cfg: dict,
) -> pd.DataFrame:
    """Scrape VnExpress business categories broadly (TASK 3 maps to VN30)."""
    all_articles: List[Dict] = []
    for category_url in VNEXPRESS_CATEGORY_URLS:
        logger.info("VnExpress: scraping category %s", category_url)
        articles = _scrape_vnexpress_category(
            category_url=category_url,
            start_date=start_date,
            rate_limiter=rate_limiter,
            existing_urls=existing_urls,
            scraping_cfg=scraping_cfg,
        )
        if articles:
            all_articles.extend(articles)
            logger.info(
                "VnExpress category %s: %d new articles", category_url, len(articles)
            )

    logger.info("VnExpress: collected %d total articles", len(all_articles))
    if not all_articles:
        return pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )
    df = pd.DataFrame(all_articles)
    return df.drop_duplicates(subset=["url"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# scrape_source — base dispatcher (to be extended in tasks 4.2–4.4)
# ---------------------------------------------------------------------------
def scrape_source(
    source: str,
    ticker: str,
    start_date: str,
    config_path: str = "config/pipeline_config.yaml",
) -> pd.DataFrame:
    """
    Scrape articles from the specified *source* for *ticker*.

    This is the main entry point called by the pipeline runner.  It sets up
    shared infrastructure (rate limiter, scraping config, duplicate detection)
    and delegates to the source-specific scraper.

    Args:
        source: One of "cafef", "vietstock", or "tnck".
        ticker: VN30 ticker symbol (ignored for "tnck" which scrapes broadly).
        start_date: Earliest publication date to collect (YYYY-MM-DD).
        config_path: Path to pipeline_config.yaml.

    Returns:
        DataFrame with columns [date, title, description, url, source].
        May be empty if scraping fails or no new articles are found.
    """
    scraping_cfg = _get_scraping_config(config_path)

    rate_limiter = RateLimiter(
        default_delay=scraping_cfg["rate_limit_seconds"],
        vietstock_delay=scraping_cfg["rate_limit_vietstock_seconds"],
    )

    # Determine output path for duplicate detection
    output_path = _output_path_for(source, ticker)
    existing_urls = load_existing_urls(output_path)

    logger.info(
        "Scraping %s for ticker=%s from %s (existing URLs: %d)",
        source, ticker, start_date, len(existing_urls),
    )

    # Delegate to source-specific scraper
    # (Placeholder — actual implementations added in tasks 4.2–4.4)
    scraper_fn = _get_scraper(source)
    if scraper_fn is None:
        logger.error("Unknown source: %s", source)
        return pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )

    articles_df = scraper_fn(
        ticker=ticker,
        start_date=start_date,
        rate_limiter=rate_limiter,
        existing_urls=existing_urls,
        scraping_cfg=scraping_cfg,
    )

    # Persist results to the source-specific CSV. New articles are merged
    # with any previously-collected ones (the scraper already skipped URLs
    # present in `existing_urls`), and the combined set is de-duplicated by
    # URL before being written atomically. Without this step the scraped
    # data would never reach disk (TASK 3 reads these CSVs).
    if articles_df is not None and not articles_df.empty:
        if os.path.isfile(output_path):
            try:
                prior = pd.read_csv(output_path, encoding="utf-8")
                combined = pd.concat([prior, articles_df], ignore_index=True)
            except Exception as exc:
                logger.warning(
                    "Could not read existing file %s (%s); writing fresh.",
                    output_path, exc,
                )
                combined = articles_df
        else:
            combined = articles_df

        combined = combined.drop_duplicates(subset=["url"]).reset_index(drop=True)
        safe_write_csv(combined, output_path)
    else:
        logger.info(
            "No new articles for %s/%s — nothing written to %s.",
            source, ticker, output_path,
        )

    return articles_df


def _output_path_for(source: str, ticker: str) -> str:
    """Return the expected CSV output path for a given source and ticker."""
    source_lower = source.lower()
    if source_lower == "cafef":
        return f"data/news/cafef/{ticker}_cafef.csv"
    elif source_lower == "vietstock":
        return f"data/news/vietstock/{ticker}_vietstock.csv"
    elif source_lower == "tnck":
        return "data/news/tnck/tnck_raw.csv"
    elif source_lower == "vietnambiz":
        return "data/news/vietnambiz/vietnambiz_raw.csv"
    elif source_lower == "vnexpress":
        return "data/news/vnexpress/vnexpress_raw.csv"
    return f"data/news/{source_lower}/{ticker}_{source_lower}.csv"


def _get_scraper(source: str):
    """
    Return the scraper function for *source*, or None if not yet implemented.

    Source-specific scrapers are registered here as they are added in
    tasks 4.2 (CafeF), 4.3 (Vietstock), and 4.4 (TNCK).
    """
    scrapers = {
        "cafef": scrape_cafef,           # Task 4.2
        "vietstock": scrape_vietstock,   # Task 4.3
        "tnck": scrape_tnck,             # Task 4.4
        "vietnambiz": scrape_vietnambiz, # news-source-expansion
        "vnexpress": scrape_vnexpress,   # news-source-expansion
    }
    return scrapers.get(source.lower())


# ---------------------------------------------------------------------------
# Reporting helper
# ---------------------------------------------------------------------------

def print_scraping_report(
    source: str,
    results: Dict[str, pd.DataFrame],
) -> None:
    """
    Print a summary report after scraping completes for a source (Req 2.10).

    Reports per-ticker: number of articles collected and date range covered.

    Args:
        source: The news source name.
        results: Mapping of ticker -> DataFrame of scraped articles.
    """
    logger.info("=" * 60)
    logger.info("SCRAPING REPORT — %s", source.upper())
    logger.info("=" * 60)

    total_articles = 0
    for ticker in sorted(results.keys()):
        df = results[ticker]
        count = len(df)
        total_articles += count
        if df.empty:
            logger.info("  %-6s: 0 articles", ticker)
        else:
            # Safely parse dates — some articles may have empty or
            # unparseable date strings.
            dates = pd.to_datetime(df["date"], errors="coerce").dropna()
            if dates.empty:
                logger.info(
                    "  %-6s: %d articles (no valid dates)", ticker, count
                )
            else:
                date_min = dates.min().strftime("%Y-%m-%d")
                date_max = dates.max().strftime("%Y-%m-%d")
                logger.info(
                    "  %-6s: %d articles (%s to %s)",
                    ticker, count, date_min, date_max,
                )

    logger.info("-" * 60)
    logger.info("Total articles from %s: %d", source.upper(), total_articles)
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cfg = _load_config()
    tickers = cfg.get("tickers", VN30_TICKERS)
    start = cfg.get("start_date", "2022-01-01")

    for src in ["cafef", "vietstock", "tnck", "vietnambiz"]:
        results: Dict[str, pd.DataFrame] = {}
        if src == "tnck":
            # TNCK scrapes broadly — single call, keyed as "ALL"
            results["ALL"] = scrape_source(src, ticker="ALL", start_date=start)
        elif src == "vietnambiz":
            # VietnamBiz scrapes broadly — single call, keyed as "ALL"
            results["ALL"] = scrape_source(src, ticker="ALL", start_date=start)
        else:
            for t in tickers:
                results[t] = scrape_source(src, ticker=t, start_date=start)

        # Print per-source report: articles per ticker, date range (Req 2.10)
        print_scraping_report(src, results)
