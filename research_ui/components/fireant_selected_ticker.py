"""Browser-only FireAnt Quote widget for one validated selected ticker."""

from __future__ import annotations

from collections.abc import Collection

import streamlit as st
import streamlit.components.v1 as components

from .external_market_context import FireAntSelectedContext, resolve_fireant_selected_context


FIREANT_QUOTE_HEIGHT = 650


def build_fireant_quote_html(context: FireAntSelectedContext) -> str:
    """Build one iframe from a previously validated exact FireAnt context."""
    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    html, body {{ width: 100%; height: 100%; margin: 0; overflow: hidden; background: #07111f; }}
    iframe {{ display: block; width: 100%; height: 100%; border: 0; overflow: hidden; }}
  </style>
</head>
<body>
  <iframe
    src="{context.quote_widget_url}"
    title="FireAnt {context.ticker}: giá và biểu đồ lịch sử"
    loading="lazy"
    sandbox="allow-scripts allow-same-origin"
    allow="fullscreen"
    referrerpolicy="strict-origin-when-cross-origin"
  ></iframe>
</body>
</html>"""


def render_fireant_selected_ticker(ticker: str, allowed_tickers: Collection[str]) -> None:
    """Render selected Quote widget and permanent top-level native fallback."""
    context = resolve_fireant_selected_context(ticker, allowed_tickers)
    st.markdown(f"#### {ticker.strip().upper()} · Diễn biến hiện tại trên FireAnt")
    st.caption(
        "EXTERNAL CURRENT · DISPLAY-ONLY · Không theo historical `as_of`; không thuộc validated historical "
        "bundle và không dùng cho evidence, model, monitoring, review, evaluation hay LLM prompt."
    )
    if context is None:
        st.warning("Mã đang chọn không thuộc ticker allowlist đã validate. Không tải FireAnt.")
        return
    try:
        components.html(build_fireant_quote_html(context), height=FIREANT_QUOTE_HEIGHT, scrolling=False)
    except Exception:
        st.warning("Không tải được FireAnt Quote widget. Dùng liên kết chính thức bên dưới.")
    st.link_button(f"Mở {context.ticker} trên FireAnt", context.native_url, type="secondary")
    st.caption(
        "Trình duyệt kết nối trực tiếp tới FireAnt. EvidenceTrace không server fetch, proxy, parse, đọc iframe, "
        "callback, truyền message về parent, ghi state hoặc ingest nội dung provider."
    )
