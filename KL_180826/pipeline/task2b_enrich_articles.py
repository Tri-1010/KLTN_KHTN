"""TASK 2B: Article full-text enrichment.

Fetch article detail pages for matched news rows, extract full text, and create
compact structured evidence for downstream LLM decision-support workflows.

Inputs:
    data/news/matched/all_news_matched.csv

Outputs:
    data/news/enriched/all_news_enriched.csv
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from queue import Empty, Queue
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse

import pandas as pd
import yaml
from bs4 import BeautifulSoup

from pipeline.logging_config import setup_logger
from pipeline.task2_scrape import (
    BROWSER_HEADERS,
    CAFEF_API_HEADERS,
    CAFEF_API_PAGE_SIZE,
    CAFEF_NEWS_API,
    CAFEF_NEWS_TYPES,
    RateLimiter,
    _parse_cafef_api_date,
    fetch_with_retry,
)

INPUT_PATH = "data/news/matched/all_news_matched.csv"
OUTPUT_PATH = "data/news/enriched/all_news_enriched.csv"
CONFIG_PATH = "config/pipeline_config.yaml"
EXTRACTOR_VERSION = "fulltext_v3_cafef_api_fallback"

BASE_COLUMNS = [
    "date",
    "title",
    "description",
    "url",
    "source",
    "ticker",
    "match_confidence",
]

ENRICHED_COLUMNS = BASE_COLUMNS + [
    "full_text",
    "full_text_available",
    "full_text_chars",
    "lead",
    "author",
    "published_at_detail",
    "canonical_url",
    "content_hash",
    "detail_fetched_at",
    "extraction_status",
    "paywall_or_restricted",
    "extractor_version",
    "extractor_strategy",
    "article_summary",
    "key_facts_json",
    "event_type_enriched",
    "risk_flags_json",
    "relevance_hint",
]

EVENT_KEYWORDS: Dict[str, List[str]] = {
    "dividend": ["cổ tức", "chia cổ tức", "trả cổ tức", "tạm ứng cổ tức"],
    "earnings": ["lợi nhuận", "doanh thu", "báo lãi", "kết quả kinh doanh", "kqkd"],
    "debt_risk": ["nợ xấu", "nợ vay", "trái phiếu", "dư nợ", "áp lực tài chính"],
    "capital": ["tăng vốn", "phát hành", "vốn điều lệ", "chào bán cổ phiếu"],
    "legal_risk": ["xử phạt", "vi phạm", "điều tra", "kiểm toán", "giải trình"],
    "governance": ["hội đồng quản trị", "đại hội", "lãnh đạo", "ceo", "bổ nhiệm", "miễn nhiệm"],
    "market": ["vn-index", "thị trường", "khối ngoại", "thanh khoản"],
}

RISK_EVENT_TYPES = {"debt_risk", "legal_risk", "governance"}

SOURCE_SELECTORS: Dict[str, List[str]] = {
    "cafef": [
        "div.detail-content",
        "div.detail__content",
        "div.contentdetail",
        "div.knc-content",
        "div#mainContent",
        "div.article-content",
        "div.article__body",
        "div.newscontent",
        "div.tindnd-content",
        "div[data-role='content']",
        "article",
    ],
    "vietstock": [
        "div.article-content",
        "div.content-detail",
        "div#vst_detail",
        "div.single-post-content",
        "article",
    ],
    "tnck": [
        "div.cms-body",
        "div.article__body",
        "div.detail-content",
        "article",
    ],
    "vietnambiz": [
        "div.detail-content",
        "div.detail__content",
        "div.article-content",
        "div.article__body",
        "div.content-detail",
        "div.entry-content",
        "div.main-detail",
        "div.cms-body",
        "div[data-role='content']",
        "article",
    ],
    "vnexpress": [
        "article.fck_detail",
        "div.fck_detail",
        "div.sidebar-1",
        "article",
    ],
    "kinhtechungkhoan": [
        "div.detail-content",
        "div.detail__content",
        "div.article-content",
        "div.article__body",
        "div.content-detail",
        "div.entry-content",
        "div.main-detail",
        "div.cms-body",
        "div.newscontent",
        "div[data-role='content']",
        "article",
    ],
}

DROP_SELECTORS = [
    "script",
    "style",
    "noscript",
    "iframe",
    "form",
    "nav",
    "footer",
    "header",
    "aside",
    ".related-news",
    ".related",
    ".ads",
    ".advertisement",
    ".social",
    ".share",
]

_SENTENCE_RE = re.compile(r"(?<=[.!?。])\s+|(?<=\.)\s+|(?<=\?)\s+|(?<=!)\s+")
_SPACE_RE = re.compile(r"\s+")
_NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:%|tỷ|triệu|nghìn|đồng|cp|cổ phiếu|trái phiếu)?", re.IGNORECASE)


def _load_config(path: str = CONFIG_PATH) -> dict:
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _enrichment_config(config: dict) -> dict:
    cfg = config.get("article_enrichment", {}) or {}
    scraping = config.get("scraping", {}) or {}
    return {
        "enabled": cfg.get("enabled", True),
        "store_full_text": cfg.get("store_full_text", True),
        "max_articles_per_run": int(cfg.get("max_articles_per_run", 0) or 0),
        "detail_rate_limit_seconds": float(cfg.get("detail_rate_limit_seconds", scraping.get("rate_limit_seconds", 1.0))),
        "max_text_chars": int(cfg.get("max_text_chars", 12000)),
        "summary_max_chars": int(cfg.get("summary_max_chars", 1200)),
        "max_retries": int(cfg.get("max_retries", scraping.get("max_retries", 3))),
        "backoff_factor": int(cfg.get("backoff_factor", scraping.get("backoff_factor", 2))),
        "request_timeout": int(cfg.get("request_timeout", scraping.get("request_timeout", 30))),
        "extractor_version": cfg.get("extractor_version", EXTRACTOR_VERSION),
        "parallel_domains": max(1, int(cfg.get("parallel_domains", 1) or 1)),
        "checkpoint_every": max(0, int(cfg.get("checkpoint_every", 0) or 0)),
        "cache_by_url": bool(cfg.get("cache_by_url", True)),
        "retry_failed": bool(cfg.get("retry_failed", False)),
        "retry_partial": bool(cfg.get("retry_partial", False)),
        "retry_restricted": bool(cfg.get("retry_restricted", False)),
        "min_full_text_chars": int(cfg.get("min_full_text_chars", 300)),
        "retry_sources": set(str(s).lower() for s in (cfg.get("retry_sources", []) or [])),
        "cafef_api_fallback_enabled": bool(cfg.get("cafef_api_fallback_enabled", True)),
        "cafef_api_fallback_max_pages": int(cfg.get("cafef_api_fallback_max_pages", 50) or 50),
        "cafef_api_fallback_news_types": tuple(cfg.get("cafef_api_fallback_news_types", CAFEF_NEWS_TYPES) or CAFEF_NEWS_TYPES),
        "cafef_try_detail_for_disclosures": bool(cfg.get("cafef_try_detail_for_disclosures", False)),
    }


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return _SPACE_RE.sub(" ", text.replace("\xa0", " ")).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", errors="ignore")).hexdigest()


def _safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _parse_json_list(value: str) -> list:
    if not value or not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def detail_headers_for_url(url: str) -> Dict[str, str]:
    headers = dict(BROWSER_HEADERS)
    # Avoid Brotli in detail-page enrichment. Several Vietnamese news sites
    # returned garbled Brotli bytes to requests in long repair runs.
    headers["Accept-Encoding"] = "gzip, deflate"
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    parsed = urlparse(str(url or ""))
    if parsed.netloc:
        headers["Referer"] = f"{parsed.scheme or 'https'}://{parsed.netloc}/"
    return headers


def _is_cafef_source(source: str) -> bool:
    return str(source or "").strip().lower() == "cafef"


def _is_ktck_source(source: str) -> bool:
    return str(source or "").strip().lower() == "kinhtechungkhoan"


def _cafef_normalize_url_key(url: str) -> str:
    parsed = urlparse(str(url or "").strip())
    if not parsed.netloc and parsed.path:
        parsed = urlparse(urljoin("https://cafef.vn", str(url)))
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    path = parsed.path.rstrip("/").lower()
    return f"{domain}{path}"


def _cafef_candidate_detail_urls(url: str) -> List[str]:
    raw = str(url or "").strip()
    if not raw:
        return []
    absolute = raw if raw.startswith("http") else urljoin("https://cafef.vn", raw)
    candidates = [absolute]
    parsed = urlparse(absolute)
    if parsed.scheme == "http":
        candidates.append(parsed._replace(scheme="https").geturl())
    match = re.match(r"^/du-lieu/[^/]+/([^/?#]+\.chn)$", parsed.path, flags=re.IGNORECASE)
    if match:
        candidates.append(f"https://cafef.vn/{match.group(1)}")
    seen = set()
    unique = []
    for candidate in candidates:
        key = _cafef_normalize_url_key(candidate)
        if key and key not in seen:
            seen.add(key)
            unique.append(candidate.split("?")[0])
    return unique


def _cafef_title_key(value: str) -> str:
    return re.sub(r"\W+", " ", normalize_text(str(value or "")).lower(), flags=re.UNICODE).strip()


def _html_to_text(value: str) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    text = str(value or "")
    if not text:
        return ""
    if "<" not in text and ">" not in text:
        return normalize_text(text)
    return normalize_text(BeautifulSoup(text, "html.parser").get_text(" ", strip=True))


def _cafef_fragment_add(fragments: List[str], seen: set, value: str) -> None:
    text = _html_to_text(value)
    if not text:
        return
    key = text.lower()
    if key in seen:
        return
    seen.add(key)
    fragments.append(text)


def _cafef_item_text(item: Dict[str, Any], row: pd.Series) -> str:
    fragments: List[str] = []
    seen = set()
    _cafef_fragment_add(fragments, seen, item.get("Title") or row.get("title", ""))
    for field in ("Content", "NewsContent", "Body", "FullContent", "Description", "SubTitle"):
        _cafef_fragment_add(fragments, seen, item.get(field, ""))
    _cafef_fragment_add(fragments, seen, row.get("description", ""))
    return normalize_text("\n".join(fragments))


def _cafef_item_to_extracted(item: Dict[str, Any], row: pd.Series, min_full_text_chars: int) -> Dict[str, Any]:
    full_text = _cafef_item_text(item, row)
    lead = _html_to_text(item.get("SubTitle") or row.get("description", ""))
    link = str(item.get("LinkDetail") or row.get("url", "") or "")
    canonical = link if link.startswith("http") else urljoin("https://cafef.vn", link)
    status = "ok" if len(full_text) >= min_full_text_chars else "partial"
    return {
        "full_text": full_text,
        "lead": lead,
        "author": "",
        "published_at_detail": _parse_cafef_api_date(str(item.get("DeployDate") or "")) or str(row.get("date", "") or ""),
        "canonical_url": canonical.split("?")[0],
        "extraction_status": status,
        "paywall_or_restricted": False,
        "extractor_strategy": "cafef_api_payload",
    }


def _listing_metadata_extracted(row: pd.Series, strategy: str) -> Dict[str, Any]:
    fragments: List[str] = []
    seen = set()
    _cafef_fragment_add(fragments, seen, row.get("title", ""))
    _cafef_fragment_add(fragments, seen, row.get("description", ""))
    full_text = normalize_text("\n".join(fragments))
    return {
        "full_text": full_text,
        "lead": normalize_text(str(row.get("description", "") or "")),
        "author": "",
        "published_at_detail": str(row.get("date", "") or ""),
        "canonical_url": str(row.get("url", "") or ""),
        "extraction_status": "partial" if full_text else "failed",
        "paywall_or_restricted": False,
        "extractor_strategy": strategy if full_text else "none",
    }


def _cafef_listing_metadata_extracted(row: pd.Series) -> Dict[str, Any]:
    return _listing_metadata_extracted(row, "cafef_listing_metadata")


def _ktck_listing_metadata_extracted(row: pd.Series) -> Dict[str, Any]:
    return _listing_metadata_extracted(row, "ktck_listing_metadata")


def _cafef_index_item(cache: Dict[str, Any], ticker: str, item: Dict[str, Any]) -> None:
    link = str(item.get("LinkDetail") or "")
    for candidate in _cafef_candidate_detail_urls(link):
        key = _cafef_normalize_url_key(candidate)
        if key:
            cache["by_url"][key] = item
    date = _parse_cafef_api_date(str(item.get("DeployDate") or "")) or ""
    title = _cafef_title_key(str(item.get("Title") or ""))
    if ticker and date and title:
        cache["by_title"][(ticker.lower(), date, title)] = item


def _cafef_api_cache(cfg: dict) -> Dict[str, Any]:
    cache = cfg.setdefault("_cafef_api_cache", {})
    cache.setdefault("loaded_tickers", set())
    cache.setdefault("by_url", {})
    cache.setdefault("by_title", {})
    return cache


def _load_cafef_api_items_for_ticker(ticker: str, rate_limiter: RateLimiter, cfg: dict) -> None:
    ticker = str(ticker or "").strip().lower()
    if not ticker:
        return
    cache = _cafef_api_cache(cfg)
    if ticker in cache["loaded_tickers"]:
        return
    cache["loaded_tickers"].add(ticker)
    for news_type in cfg.get("cafef_api_fallback_news_types", CAFEF_NEWS_TYPES):
        for page in range(1, int(cfg.get("cafef_api_fallback_max_pages", 50)) + 1):
            api_url = (
                f"{CAFEF_NEWS_API}?Symbol={ticker}"
                f"&NewsType={int(news_type)}&PageIndex={page}&PageSize={CAFEF_API_PAGE_SIZE}"
            )
            response = fetch_with_retry(
                api_url,
                rate_limiter=rate_limiter,
                max_retries=cfg["max_retries"],
                backoff_factor=cfg["backoff_factor"],
                timeout=cfg["request_timeout"],
                headers=CAFEF_API_HEADERS,
            )
            if response is None:
                break
            try:
                payload = response.json()
                items = payload.get("Data") or []
            except Exception:
                break
            if not items:
                break
            for item in items:
                if isinstance(item, dict):
                    _cafef_index_item(cache, ticker, item)


def _get_cafef_api_item_for_row(row: pd.Series, rate_limiter: RateLimiter, cfg: dict) -> Dict[str, Any] | None:
    if not cfg.get("cafef_api_fallback_enabled", True):
        return None
    ticker = str(row.get("ticker", "") or "").strip().lower()
    _load_cafef_api_items_for_ticker(ticker, rate_limiter, cfg)
    cache = _cafef_api_cache(cfg)
    for candidate in _cafef_candidate_detail_urls(str(row.get("url", "") or "")):
        item = cache["by_url"].get(_cafef_normalize_url_key(candidate))
        if item:
            return item
    title_key = _cafef_title_key(str(row.get("title", "") or ""))
    date = str(row.get("date", "") or "")[:10]
    return cache["by_title"].get((ticker, date, title_key))


def _better_extraction(candidate: Dict[str, Any], current: Dict[str, Any] | None) -> Dict[str, Any]:
    if current is None:
        return candidate
    if candidate.get("extraction_status") == "ok" and current.get("extraction_status") != "ok":
        return candidate
    if len(str(candidate.get("full_text", "") or "")) > len(str(current.get("full_text", "") or "")):
        return candidate
    return current


def _fetch_extract_detail(url: str, source: str, rate_limiter: RateLimiter, cfg: dict) -> Dict[str, Any] | None:
    response = fetch_with_retry(
        url,
        rate_limiter=rate_limiter,
        max_retries=cfg["max_retries"],
        backoff_factor=cfg["backoff_factor"],
        timeout=cfg["request_timeout"],
        headers=detail_headers_for_url(url),
    )
    if response is None:
        return None
    return extract_article_text(
        response.text,
        url=url,
        source=source,
        min_full_text_chars=cfg["min_full_text_chars"],
    )


def _enrich_cafef_article(row: pd.Series, rate_limiter: RateLimiter, cfg: dict) -> Dict[str, Any]:
    source = str(row.get("source", "") or "")
    best: Dict[str, Any] | None = None
    candidates = _cafef_candidate_detail_urls(str(row.get("url", "") or ""))
    should_try_detail = cfg.get("cafef_try_detail_for_disclosures", False)
    if should_try_detail or not re.search(r"/du-lieu/", str(row.get("url", "") or ""), flags=re.IGNORECASE):
        for candidate_url in candidates:
            extracted = _fetch_extract_detail(candidate_url, source, rate_limiter, cfg)
            if extracted is None:
                continue
            if candidate_url != str(row.get("url", "") or ""):
                extracted["extractor_strategy"] = f"cafef_detail_url_variant:{extracted.get('extractor_strategy', 'unknown')}"
            best = _better_extraction(extracted, best)
            if best.get("extraction_status") == "ok":
                return best

    item = _get_cafef_api_item_for_row(row, rate_limiter, cfg)
    if item:
        best = _better_extraction(
            _cafef_item_to_extracted(item, row, cfg["min_full_text_chars"]),
            best,
        )
    metadata = _cafef_listing_metadata_extracted(row)
    best = _better_extraction(metadata, best)
    return best or metadata


def _clean_soup(soup: BeautifulSoup) -> None:
    for selector in DROP_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()


def _extract_meta(soup: BeautifulSoup, name: str) -> str:
    tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
    if tag and tag.get("content"):
        return normalize_text(tag.get("content", ""))
    return ""


def _canonical_url(soup: BeautifulSoup, fallback_url: str) -> str:
    link = soup.find("link", rel=lambda x: x and "canonical" in x)
    if link and link.get("href"):
        return link.get("href", "").strip()
    return fallback_url


def _extract_author(soup: BeautifulSoup) -> str:
    for key in ("author", "article:author"):
        val = _extract_meta(soup, key)
        if val:
            return val
    for selector in (".author", ".article-author", ".detail-author", "p.author"):
        tag = soup.select_one(selector)
        if tag:
            text = normalize_text(tag.get_text(" ", strip=True))
            if text:
                return text
    return ""


def _extract_published_at(soup: BeautifulSoup) -> str:
    for key in ("article:published_time", "pubdate", "date", "publishdate"):
        val = _extract_meta(soup, key)
        if val:
            return val
    time_tag = soup.find("time")
    if time_tag:
        return normalize_text(time_tag.get("datetime") or time_tag.get_text(" ", strip=True))
    return ""


_BOILERPLATE_MARKERS = [
    "xem thêm", "đọc thêm", "theo dõi", "chia sẻ", "tag:", "nguồn:",
    "bạn đang đọc", "tin liên quan", "cùng chuyên mục", "quay lại",
]

_STRONG_RESTRICTED_MARKERS = [
    "đăng nhập để đọc tiếp",
    "đăng nhập để xem tiếp",
    "vui lòng đăng nhập để xem tiếp",
    "nội dung dành cho hội viên",
    "nội dung dành riêng",
    "trả phí",
    "paywall",
]

_RESTRICTED_SELECTORS = [
    ".paywall",
    ".premium-content",
    ".login-required",
    ".content-locked",
    ".require-login",
]


def _is_boilerplate(text: str) -> bool:
    lower = (text or "").lower()
    return any(marker in lower for marker in _BOILERPLATE_MARKERS)


def _paragraphs_from_container(container) -> List[str]:
    paragraphs: List[str] = []
    seen = set()
    for tag in container.find_all(["p", "h2", "h3", "li"]):
        text = normalize_text(tag.get_text(" ", strip=True))
        if len(text) < 30 or _is_boilerplate(text):
            continue
        if text in seen:
            continue
        seen.add(text)
        paragraphs.append(text)
    if not paragraphs:
        text = normalize_text(container.get_text(" ", strip=True))
        if len(text) >= 80 and not _is_boilerplate(text):
            paragraphs.append(text)
    return paragraphs


def _safe_soup(html: str) -> BeautifulSoup:
    raw = html or ""
    for parser in ("lxml", "html5lib", "html.parser"):
        try:
            return BeautifulSoup(raw, parser)
        except Exception:
            continue
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", raw)
    for parser in ("lxml", "html5lib", "html.parser"):
        try:
            return BeautifulSoup(cleaned, parser)
        except Exception:
            continue
    return BeautifulSoup("", "html.parser")


def _jsonld_article_body(soup: BeautifulSoup) -> str:
    bodies: List[str] = []
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text(" ", strip=True)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except Exception:
            continue
        stack = parsed if isinstance(parsed, list) else [parsed]
        while stack:
            item = stack.pop(0)
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                body = item.get("articleBody") or item.get("description")
                if isinstance(body, str) and len(normalize_text(body)) >= 120:
                    bodies.append(normalize_text(body))
                graph = item.get("@graph")
                if isinstance(graph, list):
                    stack.extend(graph)
    return max(bodies, key=len) if bodies else ""


def _container_score(container) -> tuple[int, List[str]]:
    paragraphs = _paragraphs_from_container(container)
    text_len = len(" ".join(paragraphs))
    if text_len < 120:
        return 0, paragraphs
    link_text = normalize_text(" ".join(a.get_text(" ", strip=True) for a in container.find_all("a")))
    link_ratio = len(link_text) / max(text_len, 1)
    penalty = int(link_ratio * 1000)
    score = text_len + len(paragraphs) * 80 - penalty
    return score, paragraphs


def _best_container_paragraphs(soup: BeautifulSoup) -> List[str]:
    best_score = 0
    best_paragraphs: List[str] = []
    candidates = soup.select("article, main, div.detail-content, div.article-content, div.entry-content, div.cms-body, div[class*='content'], div[class*='article'], div[class*='detail']")
    for container in candidates[:200]:
        score, paragraphs = _container_score(container)
        if score > best_score:
            best_score = score
            best_paragraphs = paragraphs
    return best_paragraphs


def _is_restricted_page(soup: BeautifulSoup, full_text: str) -> bool:
    if len(full_text) >= 300:
        return False
    if any(soup.select_one(selector) for selector in _RESTRICTED_SELECTORS):
        return True
    text = normalize_text(soup.get_text(" ", strip=True)).lower()
    return any(marker in text for marker in _STRONG_RESTRICTED_MARKERS)


def extract_article_text(html: str, url: str, source: str, min_full_text_chars: int = 300) -> Dict[str, Any]:
    soup = _safe_soup(html or "")
    jsonld_body = _jsonld_article_body(soup)
    _clean_soup(soup)

    selectors = SOURCE_SELECTORS.get((source or "").lower(), []) + ["article", "main"]
    best_paragraphs: List[str] = []
    strategy = "none"
    for selector in selectors:
        container = soup.select_one(selector)
        if not container:
            continue
        paragraphs = _paragraphs_from_container(container)
        if len(" ".join(paragraphs)) > len(" ".join(best_paragraphs)):
            best_paragraphs = paragraphs
            strategy = "selector"
        if len(" ".join(best_paragraphs)) >= 500:
            break

    if len(jsonld_body) > len(" ".join(best_paragraphs)):
        best_paragraphs = [jsonld_body]
        strategy = "jsonld"

    fallback_paragraphs = _best_container_paragraphs(soup)
    if len(" ".join(fallback_paragraphs)) > len(" ".join(best_paragraphs)):
        best_paragraphs = fallback_paragraphs
        strategy = "longest_container"

    if not best_paragraphs:
        best_paragraphs = [
            normalize_text(p.get_text(" ", strip=True))
            for p in soup.find_all("p")
            if len(normalize_text(p.get_text(" ", strip=True))) >= 30
            and not _is_boilerplate(normalize_text(p.get_text(" ", strip=True)))
        ]
        if best_paragraphs:
            strategy = "paragraphs"

    full_text = normalize_text("\n".join(best_paragraphs))
    lead = _extract_meta(soup, "og:description") or (best_paragraphs[0] if best_paragraphs else "")
    restricted = _is_restricted_page(soup, full_text)

    if full_text:
        status = "ok" if len(full_text) >= min_full_text_chars else "partial"
    else:
        status = "restricted" if restricted else "failed"

    return {
        "full_text": full_text,
        "lead": normalize_text(lead),
        "author": _extract_author(soup),
        "published_at_detail": _extract_published_at(soup),
        "canonical_url": _canonical_url(soup, url),
        "extraction_status": status,
        "paywall_or_restricted": bool(restricted),
        "extractor_strategy": strategy,
    }


def _sentences(text: str) -> List[str]:
    parts = _SENTENCE_RE.split(normalize_text(text))
    return [p.strip() for p in parts if len(p.strip()) >= 30]


def classify_event_type(text: str) -> str:
    text_lower = (text or "").lower()
    found = [key for key, kws in EVENT_KEYWORDS.items() if any(kw in text_lower for kw in kws)]
    return ",".join(found) if found else "general_news"


def detect_risk_flags(text: str, event_type: str) -> List[str]:
    text_lower = (text or "").lower()
    flags = []
    for ev in event_type.split(","):
        if ev in RISK_EVENT_TYPES:
            flags.append(ev)
    extra = {
        "earnings_warning": ["lợi nhuận giảm", "doanh thu giảm", "lỗ", "sụt giảm", "kém khả quan"],
        "capital_dilution": ["pha loãng", "chào bán cổ phiếu", "phát hành thêm"],
        "audit_issue": ["kiểm toán", "ngoại trừ", "nhấn mạnh", "giải trình"],
    }
    for flag, keywords in extra.items():
        if any(kw in text_lower for kw in keywords):
            flags.append(flag)
    return sorted(set(flags))


def summarize_article_rule_based(title: str, description: str, full_text: str, max_chars: int = 1200) -> str:
    candidates = []
    for text in (description, full_text):
        candidates.extend(_sentences(text or ""))
    summary = " ".join(candidates[:3])
    if not summary:
        summary = normalize_text(title or description or "")
    return summary[:max_chars].strip()


def _fact_type(sentence: str) -> str:
    et = classify_event_type(sentence)
    return et.split(",")[0] if et else "general_news"


def _direction(fact_type: str) -> str:
    if fact_type in {"debt_risk", "legal_risk"}:
        return "risk"
    if fact_type in {"earnings", "dividend", "capital"}:
        return "support_or_context"
    return "neutral"


def extract_key_facts_rule_based(text: str, max_facts: int = 5) -> List[Dict[str, str]]:
    facts: List[Dict[str, str]] = []
    for sent in _sentences(text or ""):
        event = _fact_type(sent)
        has_keyword = event != "general_news"
        has_number = bool(_NUMBER_RE.search(sent))
        if not (has_keyword or has_number):
            continue
        fact_id = f"F{len(facts) + 1:02d}"
        quote = sent[:240]
        facts.append({
            "fact_id": fact_id,
            "fact": sent[:300],
            "evidence_quote": quote,
            "fact_type": event,
            "direction": _direction(event),
            "confidence": "medium" if has_keyword else "low",
        })
        if len(facts) >= max_facts:
            break
    return facts


def relevance_hint(title: str, full_text: str, ticker: str) -> str:
    text = f"{title} {full_text}".lower()
    ticker = (ticker or "").lower()
    if ticker and ticker in text:
        return "ticker_mentioned"
    return "needs_manual_check"


def _row_base(row: pd.Series) -> Dict[str, Any]:
    return {col: row.get(col, "") for col in BASE_COLUMNS}


def _existing_by_url(path: str) -> Dict[str, Dict[str, Any]]:
    if not os.path.isfile(path):
        return {}
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except Exception:
        return {}
    rows = {}
    for _, row in df.iterrows():
        url = str(row.get("url", "") or "")
        if url:
            rows[url] = {col: row.get(col, "") for col in df.columns}
    return rows


def _domain_for_url(url: str) -> str:
    parsed = urlparse(str(url or ""))
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain or "unknown"


def _status(value: Any) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def _is_reusable_existing(record: Dict[str, Any], cfg: dict) -> bool:
    status = _status(record.get("extraction_status", ""))
    if not status:
        return False
    if status in {"pending_max_articles_cap", "pending_resume"}:
        return False
    cached_version = _status(record.get("extractor_version", ""))
    if cached_version != cfg.get("extractor_version", EXTRACTOR_VERSION):
        return False
    full_text_available = str(record.get("full_text_available", "")).lower() in {"true", "1"}
    if status == "ok" and full_text_available:
        return True
    if status in {"failed", "fetch_failed"} and cfg.get("retry_failed", False):
        return False
    if status == "partial" and cfg.get("retry_partial", False):
        return False
    if status == "restricted" and cfg.get("retry_restricted", False):
        return False
    return True


def _pending_row(row: pd.Series, status: str) -> Dict[str, Any]:
    pending = {col: "" for col in ENRICHED_COLUMNS}
    for col in BASE_COLUMNS:
        pending[col] = row.get(col, "")
    pending["canonical_url"] = row.get("url", "")
    pending["detail_fetched_at"] = datetime.now().isoformat(timespec="seconds")
    pending["extraction_status"] = status
    pending["extractor_version"] = EXTRACTOR_VERSION
    pending["article_summary"] = summarize_article_rule_based(
        str(row.get("title", "") or ""),
        str(row.get("description", "") or ""),
        "",
    )
    combined = normalize_text(" ".join([
        str(row.get("title", "") or ""),
        str(row.get("description", "") or ""),
    ]))
    event_type = classify_event_type(combined)
    pending["event_type_enriched"] = event_type
    pending["risk_flags_json"] = _safe_json(detect_risk_flags(combined, event_type))
    pending["key_facts_json"] = _safe_json(extract_key_facts_rule_based(combined))
    pending["content_hash"] = content_hash(combined)
    pending["relevance_hint"] = relevance_hint(str(row.get("title", "") or ""), "", str(row.get("ticker", "") or ""))
    return pending


def _build_output_df(source_df: pd.DataFrame, enriched_by_url: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for _, row in source_df.iterrows():
        url = str(row.get("url", "") or "")
        existing = enriched_by_url.get(url)
        enriched = dict(existing) if existing is not None else _pending_row(row, "pending_resume")
        for col in BASE_COLUMNS:
            enriched[col] = row.get(col, enriched.get(col, ""))
        rows.append(enriched)
    return pd.DataFrame(rows, columns=ENRICHED_COLUMNS)


def _write_enrichment_output(
    source_df: pd.DataFrame,
    enriched_by_url: Dict[str, Dict[str, Any]],
    output_path: str,
) -> pd.DataFrame:
    out_df = _build_output_df(source_df, enriched_by_url)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    temp_path = f"{output_path}.{os.getpid()}.{stamp}.tmp"
    out_df.to_csv(
        temp_path,
        index=False,
        encoding="utf-8",
        quoting=csv.QUOTE_MINIMAL,
        escapechar="\\",
        lineterminator="\n",
    )
    last_error = None
    for attempt in range(5):
        try:
            os.replace(temp_path, output_path)
            return out_df
        except PermissionError as exc:
            last_error = exc
            time.sleep(2 * (attempt + 1))
    raise last_error


def _coverage_snapshot(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"unique_urls": 0, "full_text": 0, "coverage_pct": 0.0, "status_counts": {}, "by_source": {}}
    unique = df.drop_duplicates(subset=["url"])
    ok = unique["full_text_available"].astype(str).str.lower().isin(["true", "1"])
    status_counts = unique["extraction_status"].fillna("").value_counts().to_dict()
    by_source = {}
    for source, group in unique.assign(_ok=ok).groupby("source"):
        total = int(len(group))
        full_text = int(group["_ok"].sum())
        by_source[str(source)] = {
            "total": total,
            "full_text": full_text,
            "coverage_pct": round(full_text / total * 100, 2) if total else 0.0,
        }
    return {
        "unique_urls": int(len(unique)),
        "full_text": int(ok.sum()),
        "coverage_pct": round(float(ok.mean() * 100), 2) if len(unique) else 0.0,
        "status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "by_source": by_source,
    }


def _log_coverage(logger, label: str, df: pd.DataFrame) -> None:
    snapshot = _coverage_snapshot(df)
    logger.info(
        "%s coverage: %d/%d unique URLs with full text (%.2f%%). Status: %s. By source: %s",
        label,
        snapshot["full_text"],
        snapshot["unique_urls"],
        snapshot["coverage_pct"],
        snapshot["status_counts"],
        snapshot["by_source"],
    )


def enrich_single_article(row: pd.Series, rate_limiter: RateLimiter, cfg: dict) -> Dict[str, Any]:
    base = _row_base(row)
    url = str(base.get("url", "") or "")
    source = str(base.get("source", "") or "")
    now = datetime.now().isoformat(timespec="seconds")

    if not url:
        result = {**base, "detail_fetched_at": now, "extraction_status": "missing_url"}
    elif _is_cafef_source(source):
        extracted = _enrich_cafef_article(row, rate_limiter, cfg)
        result = {**base, **extracted, "detail_fetched_at": now}
    elif _is_ktck_source(source):
        # Many older Kinh tế Chứng khoán URLs now return 404/timeout, but the
        # sitemap slug still carries ticker-relevant title text. Preserve it as
        # auditable partial evidence instead of burning hours on dead pages.
        result = {**base, **_ktck_listing_metadata_extracted(row), "detail_fetched_at": now}
    else:
        extracted = _fetch_extract_detail(url, source, rate_limiter, cfg)
        if extracted is None:
            result = {**base, "detail_fetched_at": now, "extraction_status": "fetch_failed"}
        else:
            result = {**base, **extracted, "detail_fetched_at": now}

    full_text = normalize_text(str(result.get("full_text", "") or ""))
    max_text_chars = cfg["max_text_chars"]
    if len(full_text) > max_text_chars:
        full_text = full_text[:max_text_chars].rstrip()
    if not cfg.get("store_full_text", True):
        stored_text = ""
    else:
        stored_text = full_text

    combined_for_analysis = normalize_text(" ".join([
        str(base.get("title", "") or ""),
        str(base.get("description", "") or ""),
        full_text,
    ]))
    summary = summarize_article_rule_based(
        str(base.get("title", "") or ""),
        str(base.get("description", "") or ""),
        full_text,
        max_chars=cfg["summary_max_chars"],
    )
    event_type = classify_event_type(combined_for_analysis)
    risk_flags = detect_risk_flags(combined_for_analysis, event_type)
    key_facts = extract_key_facts_rule_based(combined_for_analysis)
    digest = content_hash(full_text or combined_for_analysis)

    enriched = {col: "" for col in ENRICHED_COLUMNS}
    enriched.update(base)
    enriched.update({
        "full_text": stored_text,
        "full_text_available": bool(full_text),
        "full_text_chars": len(full_text),
        "lead": result.get("lead", ""),
        "author": result.get("author", ""),
        "published_at_detail": result.get("published_at_detail", ""),
        "canonical_url": result.get("canonical_url", url),
        "content_hash": digest,
        "detail_fetched_at": now,
        "extraction_status": result.get("extraction_status", ""),
        "paywall_or_restricted": bool(result.get("paywall_or_restricted", False)),
        "extractor_version": cfg.get("extractor_version", EXTRACTOR_VERSION),
        "extractor_strategy": result.get("extractor_strategy", ""),
        "article_summary": summary,
        "key_facts_json": _safe_json(key_facts),
        "event_type_enriched": event_type,
        "risk_flags_json": _safe_json(risk_flags),
        "relevance_hint": relevance_hint(str(base.get("title", "") or ""), full_text, str(base.get("ticker", "") or "")),
    })
    return enriched


def run_enrichment(
    input_path: str = INPUT_PATH,
    output_path: str = OUTPUT_PATH,
    config_path: str = CONFIG_PATH,
    force: bool = False,
) -> pd.DataFrame:
    logger = setup_logger("TASK_2B")
    logger.info("Starting Article Full-Text Enrichment (TASK 2B)...")

    config = _load_config(config_path)
    cfg = _enrichment_config(config)
    cfg["_cafef_api_cache"] = {}
    if not cfg.get("enabled", True):
        logger.info("Article enrichment disabled in config.")
        return pd.DataFrame(columns=ENRICHED_COLUMNS)

    if not os.path.isfile(input_path):
        logger.warning("Input file not found: %s", input_path)
        return pd.DataFrame(columns=ENRICHED_COLUMNS)

    source_df = pd.read_csv(input_path, encoding="utf-8")
    if source_df.empty:
        logger.warning("No rows to enrich.")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        empty = pd.DataFrame(columns=ENRICHED_COLUMNS)
        empty.to_csv(output_path, index=False, encoding="utf-8")
        return empty

    # Fetch once per URL but preserve all ticker rows emitted by matching.
    unique_df = source_df.drop_duplicates(subset=["url"], keep="first").reset_index(drop=True)
    existing = {} if force or not cfg.get("cache_by_url", True) else _existing_by_url(output_path)
    max_articles = cfg.get("max_articles_per_run", 0)
    parallel_domains = cfg.get("parallel_domains", 1)
    checkpoint_every = cfg.get("checkpoint_every", 0)

    enriched_by_url: Dict[str, Dict[str, Any]] = {}
    pending_rows: List[pd.Series] = []

    for _, row in unique_df.iterrows():
        url = str(row.get("url", "") or "")
        if url and url in existing:
            # Keep old row as baseline while queued for repair; this preserves
            # previous full text through checkpoints and interrupted repair runs.
            enriched_by_url[url] = existing[url]
            retry_sources = cfg.get("retry_sources", set())
            source = str(row.get("source", "") or "").lower()
            if retry_sources and source not in retry_sources:
                continue
            if _is_reusable_existing(existing[url], cfg):
                continue
        pending_rows.append(row)

    if max_articles:
        for row in pending_rows[max_articles:]:
            url = str(row.get("url", "") or "")
            enriched_by_url[url] = _pending_row(row, "pending_max_articles_cap")
        pending_rows = pending_rows[:max_articles]

    domain_groups: Dict[str, List[pd.Series]] = defaultdict(list)
    for row in pending_rows:
        domain_groups[_domain_for_url(str(row.get("url", "") or ""))].append(row)

    domain_counts = Counter({domain: len(rows) for domain, rows in domain_groups.items()})
    logger.info(
        "Article enrichment queue: %d matched rows, %d unique URLs, %d reusable cached, %d pending.",
        len(source_df),
        len(unique_df),
        len(enriched_by_url),
        len(pending_rows),
    )
    if domain_counts:
        logger.info("Pending by domain: %s", ", ".join(f"{d}={n}" for d, n in domain_counts.most_common()))
    worker_count = min(parallel_domains, len(domain_groups)) if domain_groups else 0
    logger.info(
        "Running article enrichment with %d domain workers, %.2fs per-domain delay.",
        worker_count,
        cfg["detail_rate_limit_seconds"],
    )

    processed_new = 0

    def enrich_domain(domain: str, rows_for_domain: List[pd.Series], queue: Queue) -> None:
        try:
            limiter = RateLimiter(default_delay=cfg["detail_rate_limit_seconds"])
            for row in rows_for_domain:
                url = str(row.get("url", "") or "")
                try:
                    queue.put((domain, enrich_single_article(row, limiter, cfg), None))
                except Exception as exc:
                    queue.put((domain, _pending_row(row, "failed"), exc))
                    logger.warning("Article enrichment failed for %s: %s", url, exc)
        except Exception as exc:
            logger.warning("Domain enrichment worker failed for %s: %s", domain, exc)
        finally:
            queue.put((domain, None, None))

    if domain_groups:
        results_queue: Queue = Queue()
        active_domains = set(domain_groups)
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            for domain, rows in domain_groups.items():
                executor.submit(enrich_domain, domain, rows, results_queue)

            while active_domains:
                try:
                    domain, enriched, exc = results_queue.get(timeout=5)
                except Empty:
                    continue

                if enriched is None:
                    active_domains.discard(domain)
                    continue

                url = str(enriched.get("url", "") or "")
                previous = enriched_by_url.get(url)
                old_has_text = str((previous or {}).get("full_text_available", "")).lower() in {"true", "1"}
                new_has_text = bool(enriched.get("full_text_available"))
                if previous is not None and old_has_text and not new_has_text:
                    preserved = dict(previous)
                    preserved["detail_fetched_at"] = enriched.get("detail_fetched_at", preserved.get("detail_fetched_at", ""))
                    preserved["extractor_version"] = cfg.get("extractor_version", EXTRACTOR_VERSION)
                    preserved["extractor_strategy"] = "preserved_previous_full_text"
                    enriched_by_url[url] = preserved
                else:
                    enriched_by_url[url] = enriched
                processed_new += 1
                if exc is not None:
                    logger.warning("Stored pending resume for %s after worker error.", url)
                if processed_new % 50 == 0:
                    logger.info(
                        "Enriched %d/%d pending articles...",
                        processed_new,
                        len(pending_rows),
                    )
                if checkpoint_every and processed_new % checkpoint_every == 0:
                    checkpoint_df = _write_enrichment_output(source_df, enriched_by_url, output_path)
                    logger.info("Checkpoint saved after %d new articles.", processed_new)
                    _log_coverage(logger, "Checkpoint", checkpoint_df)

    out_df = _write_enrichment_output(source_df, enriched_by_url, output_path)

    snapshot = _coverage_snapshot(out_df)
    logger.info(
        "Saved enriched news to %s (%d rows, %d/%d unique URLs with full text, %.2f%% coverage, %d new fetched). Status counts: %s",
        output_path,
        len(out_df),
        snapshot["full_text"],
        snapshot["unique_urls"],
        snapshot["coverage_pct"],
        processed_new,
        snapshot["status_counts"],
    )
    _log_coverage(logger, "Final", out_df)
    return out_df


if __name__ == "__main__":
    run_enrichment()
