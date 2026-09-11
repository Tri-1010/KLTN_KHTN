"""Fixed browser-only FireAnt Markets context for VNINDEX dashboard views."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


FIREANT_MARKETS_WIDGET_URL = "https://www.fireant.vn/Widgets/Markets"
FIREANT_VNINDEX_URL = "https://fireant.vn/ma-chung-khoan/VNINDEX"
FIREANT_MARKETS_HEIGHT = 760


def build_fireant_markets_html() -> str:
    """Build fixed iframe markup without accepting runtime input."""
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
    src="{FIREANT_MARKETS_WIDGET_URL}"
    title="FireAnt Markets: VN-INDEX và bối cảnh thị trường"
    loading="lazy"
    sandbox="allow-scripts allow-same-origin"
    allow="fullscreen"
    referrerpolicy="strict-origin-when-cross-origin"
  ></iframe>
</body>
</html>"""


def render_fireant_vnindex() -> None:
    """Render fixed external Markets widget plus permanent native fallback."""
    st.markdown("#### VN-INDEX · Bối cảnh thị trường hiện tại từ FireAnt")
    st.caption(
        "EXTERNAL CURRENT MARKET CONTEXT · DISPLAY-ONLY · Ngoài validated historical bundle, historical "
        "`as_of`, evidence, model, monitoring, review và evaluation; không phải khuyến nghị đầu tư."
    )
    try:
        components.html(build_fireant_markets_html(), height=FIREANT_MARKETS_HEIGHT, scrolling=False)
    except Exception:
        st.warning("Không tải được FireAnt Markets widget. Dùng liên kết chính thức luôn hiển thị bên dưới.")
    st.link_button("Mở VNINDEX trên FireAnt", FIREANT_VNINDEX_URL, type="secondary")
    st.caption(
        "Trình duyệt kết nối trực tiếp tới FireAnt. EvidenceTrace không server fetch, proxy, parse, callback, "
        "postMessage, ghi state hoặc ingest nội dung provider."
    )
