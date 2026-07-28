"""Fail-closed FireAnt outbound-link context for selected historical records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
import ipaddress
from types import MappingProxyType
from typing import Collection, Mapping
from urllib.parse import parse_qs, urlencode, urlsplit

import streamlit as st
import yaml


FIREANT_ALLOWED_HOSTS = frozenset({"fireant.vn", "www.fireant.vn"})
FIREANT_QUOTE_ORIGIN = "https://www.fireant.vn"
FIREANT_QUOTE_PATH = "/Widgets/Quote"
FIREANT_NATIVE_ORIGIN = "https://fireant.vn"
FIREANT_NATIVE_PATH_PREFIX = "/ma-chung-khoan/"


@dataclass(frozen=True)
class FireAntSelectedContext:
    """Exact browser-only FireAnt contracts for one validated selected ticker."""

    ticker: str
    quote_widget_url: str
    native_url: str


@dataclass(frozen=True)
class ExternalProviderLink:
    """One exact provider URL reviewed for display-only outbound navigation."""

    ticker: str
    url: str
    approved_host: str
    official_source_url: str
    reviewed_on: date
    review_expires_on: date
    status: str = "pending_verification"
    provider_id: str = "fireant"
    mode: str = "link_only"


# No FireAnt instrument URL is enabled until FireAnt publishes and confirms a public contract.
FIREANT_LINKS: Mapping[str, ExternalProviderLink] = MappingProxyType({})


@lru_cache(maxsize=1)
def configured_tickers() -> frozenset[str]:
    """Read configured ticker universe locally; failures disable FireAnt links."""
    config_path = Path(__file__).resolve().parents[2] / "config" / "pipeline_config.yaml"
    try:
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return frozenset()
    values = payload.get("tickers") if isinstance(payload, dict) else None
    if not isinstance(values, list):
        return frozenset()
    return frozenset(normalized for value in values if (normalized := _normalize_ticker(value)) is not None)


def validate_fireant_catalog(catalog: Mapping[str, ExternalProviderLink] = FIREANT_LINKS) -> None:
    """Validate exact catalog keys and entries without network access."""
    tickers = configured_tickers()
    for ticker, entry in catalog.items():
        if not isinstance(ticker, str) or not isinstance(entry, ExternalProviderLink):
            raise ValueError("FireAnt catalog entries must have string keys and link values")
        if ticker not in tickers:
            raise ValueError("FireAnt catalog ticker is outside configured universe")
        if entry.ticker != ticker:
            raise ValueError("FireAnt catalog key and ticker differ")
        validate_fireant_link(entry)


def resolve_fireant_link(
    ticker: str,
    catalog: Mapping[str, ExternalProviderLink] = FIREANT_LINKS,
    today: date | None = None,
) -> ExternalProviderLink | None:
    """Return a currently approved exact URL; reject all unreviewed inputs."""
    normalized = _normalize_ticker(ticker)
    if normalized is None:
        return None
    try:
        validate_fireant_catalog(catalog)
    except (AttributeError, TypeError, ValueError):
        return None
    entry = catalog.get(normalized)
    current_date = today or date.today()
    if entry is None or entry.status != "enabled":
        return None
    if entry.reviewed_on > current_date or current_date > entry.review_expires_on:
        return None
    return entry


def validate_fireant_link(entry: ExternalProviderLink) -> None:
    """Validate one static catalog entry without contacting FireAnt."""
    if entry.provider_id != "fireant" or entry.mode != "link_only":
        raise ValueError("FireAnt entries must be link_only")
    if _normalize_ticker(entry.ticker) != entry.ticker:
        raise ValueError("ticker must be normalized uppercase")
    if entry.status not in {"enabled", "pending_verification", "disabled"}:
        raise ValueError("invalid FireAnt entry status")
    if entry.reviewed_on > entry.review_expires_on:
        raise ValueError("review expiry precedes review date")
    _validate_exact_fireant_url(entry.url, entry.approved_host)
    _validate_exact_fireant_url(entry.official_source_url, entry.approved_host)


def render_external_market_context(ticker: str, catalog: Mapping[str, ExternalProviderLink] | None = None) -> None:
    """Render legacy exact outbound navigation without consuming provider data."""
    st.markdown("#### FireAnt market context")
    st.caption(
        "EXTERNAL LIVE DATA · Display-only. Không thuộc validated historical bundle và không dùng cho "
        "evidence, model, monitoring, review hoặc evaluation."
    )
    entry = resolve_fireant_link(ticker, FIREANT_LINKS if catalog is None else catalog)
    if entry is None:
        st.info("Chưa có URL FireAnt công khai đã được duyệt cho mã này. Không tải dữ liệu ngoài.")
        return
    st.link_button("Mở FireAnt", entry.url, type="secondary")
    st.caption("Mở FireAnt trong tab mới. Trình duyệt kết nối trực tiếp đến provider; không có dữ liệu quay lại EvidenceTrace.")


def resolve_fireant_selected_context(ticker: str, allowed_tickers: Collection[str]) -> FireAntSelectedContext | None:
    """Build exact Quote/native URLs for one allowlisted server-derived ticker."""
    normalized = _normalize_ticker(ticker)
    allowed = {_normalize_ticker(value) for value in allowed_tickers}
    allowed.discard(None)
    if normalized is None or normalized not in allowed:
        return None
    context = FireAntSelectedContext(
        ticker=normalized,
        quote_widget_url=f"{FIREANT_QUOTE_ORIGIN}{FIREANT_QUOTE_PATH}?{urlencode({'symbols': normalized})}",
        native_url=f"{FIREANT_NATIVE_ORIGIN}{FIREANT_NATIVE_PATH_PREFIX}{normalized}",
    )
    try:
        validate_fireant_selected_context(context)
    except ValueError:
        return None
    return context


def validate_fireant_selected_context(context: FireAntSelectedContext) -> None:
    """Reject any selected-ticker context outside verified FireAnt URL shapes."""
    if not isinstance(context, FireAntSelectedContext) or _normalize_ticker(context.ticker) != context.ticker:
        raise ValueError("invalid selected FireAnt ticker")

    quote = urlsplit(context.quote_widget_url)
    if (
        quote.scheme != "https"
        or quote.hostname != "www.fireant.vn"
        or quote.username
        or quote.password
        or quote.port is not None
        or quote.path != FIREANT_QUOTE_PATH
        or quote.fragment
        or parse_qs(quote.query, keep_blank_values=True, strict_parsing=True) != {"symbols": [context.ticker]}
    ):
        raise ValueError("invalid FireAnt Quote widget URL")

    native = urlsplit(context.native_url)
    if (
        native.scheme != "https"
        or native.hostname != "fireant.vn"
        or native.username
        or native.password
        or native.port is not None
        or native.path != f"{FIREANT_NATIVE_PATH_PREFIX}{context.ticker}"
        or native.query
        or native.fragment
    ):
        raise ValueError("invalid FireAnt native ticker URL")


def _normalize_ticker(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized if len(normalized) == 3 and normalized.isascii() and normalized.isalpha() else None


def _validate_exact_fireant_url(value: str, approved_host: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError("URL must be non-empty")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port is not None:
        raise ValueError("URL must be HTTPS without credentials or port")
    if parsed.query or parsed.fragment:
        raise ValueError("URL query and fragment are forbidden")
    host = (parsed.hostname or "").lower()
    approved = approved_host.lower()
    if not host or host != approved or host not in FIREANT_ALLOWED_HOSTS:
        raise ValueError("URL host is not approved")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("URL host cannot be an IP address")
    if not parsed.path.startswith("/"):
        raise ValueError("URL path is required")
    path_parts = {part.lower() for part in parsed.path.split("/") if part}
    if path_parts & {"redirect", "redirects", "wrapper", "wrappers", "outbound", "external"}:
        raise ValueError("URL redirect and wrapper paths are forbidden")
