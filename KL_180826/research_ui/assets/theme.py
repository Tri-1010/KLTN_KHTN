"""Research Command Center visual tokens and Vietnamese-first labels."""

from __future__ import annotations

APP_TITLE = "EvidenceTrace"
APP_SUBTITLE = "Nền tảng hỗ trợ phân tích có bằng chứng ngữ nghĩa và khả năng truy vết"

PAGE_LABELS = {
    "Overview": "Tổng quan",
    "Select": "Khám phá hồ sơ",
    "Explain": "Giải thích evidence",
    "Monitor": "Theo dõi lịch sử",
    "Update": "Cập nhật analyst",
    "Review": "Hậu kiểm",
    "Evaluation": "Đánh giá LLM",
    "Provenance": "Provenance & audit",
}

VARIANT_LABELS = {"full_evidence": "Đầy đủ bằng chứng", "ml_only": "Chỉ tín hiệu ML"}

CARD_TYPE_LABELS = {
    "rule_based_baseline": "Baseline theo luật",
    "llm_ml_only": "LLM chỉ dùng ML",
    "llm_full_evidence": "LLM dùng đầy đủ bằng chứng",
}

QUALITY_LABELS = {
    "high": "cao",
    "mixed": "hỗn hợp",
    "partial": "một phần",
    "low": "thấp",
    "none": "không có",
    "unavailable": "chưa có",
}

STATUS_TOKENS = {
    "Model candidate": {"icon": "◈", "label": "Ứng viên mô hình", "kind": "neutral"},
    "Initial": {"icon": "○", "label": "Trạng thái ban đầu", "kind": "neutral"},
    "Watch": {"icon": "◐", "label": "Theo dõi", "kind": "warning"},
    "Review Required": {"icon": "!", "label": "Cần rà soát", "kind": "critical"},
    "Evidence weak": {"icon": "?", "label": "Bằng chứng yếu", "kind": "muted"},
    "Requires human review": {"icon": "⚑", "label": "Cần con người kiểm tra", "kind": "warning"},
    "Unavailable": {"icon": "—", "label": "Chưa có dữ liệu", "kind": "muted"},
}

STATUS_COLORS = {"Initial": "#2563EB", "Watch": "#B45309", "Review Required": "#B91C1C"}
CARD_TYPE_COLORS = {"rule_based_baseline": "#0070C0", "llm_ml_only": "#7C3AED", "llm_full_evidence": "#00856A"}
RESEARCH_BLUE = "#2563EB"

CUSTOM_CSS = """
<style>
:root {
  --et-navy: #07111F;
  --et-ink: #F1F5F9;
  --et-muted: #8497AA;
  --et-page: #07111F;
  --et-surface: #0D1B2A;
  --et-raised: #13263A;
  --et-audit: #0A1725;
  --et-border: #2A4055;
  --et-accent: #7DD3FC;
  --et-focus: #7DD3FC;
}
html, body, [class*="css"] { font-family: Inter, system-ui, -apple-system, "Segoe UI", sans-serif; }
.stApp { background: var(--et-page); color: var(--et-ink); }
.block-container { max-width: none; padding: 1rem 1.5rem 2rem; }
[data-testid="stSidebar"] { background: #081523; min-width: 240px; border-right: 1px solid var(--et-border); }
[data-testid="stSidebar"] * { color: #E2E8F0; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #9FB1C2; }
[data-testid="stSidebar"] .stInfo { background: #102238; border-color: #28445D; }
[data-testid="stSidebar"] .stRadio label { font-size: .92rem; font-weight: 650; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #102238; border-color: #35526D; }
[data-baseweb="select"] > div, [data-testid="stDateInput"] input, [data-testid="stTextInput"] input { background: var(--et-raised) !important; border-color: var(--et-border) !important; color: var(--et-ink) !important; }
.research-banner, .trust-strip, .posthoc-banner, .cutoff-bar { border-radius: .5rem; padding: .65rem .8rem; margin-bottom: .75rem; line-height: 1.45; }
.research-banner { border-left: 3px solid var(--et-accent); background: #0B2032; color: var(--et-ink); }
.trust-strip { border: 1px solid #28445D; background: #0B1C2C; color: #DCEBFA; font-size: .86rem; }
.posthoc-banner { border-left: 3px solid #FB7185; background: #30131E; color: #FFD5DF; font-weight: 650; }
.cutoff-bar { border: 1px solid #24506D; background: #0A2334; color: #C6E9FF; }
.dashboard-card, .workspace-panel { background: var(--et-surface); border: 1px solid var(--et-border); border-radius: .55rem; padding: .8rem .9rem; margin-bottom: .75rem; }
.selected-record-panel { background: #102238; }
.workspace-panel h3 { margin-top: 0; letter-spacing: .02em; }
.metric-label { color: var(--et-muted); font-size: .84rem; }
[data-testid="stMetric"] { background: var(--et-surface); border: 1px solid var(--et-border); border-radius: .5rem; padding: .65rem .75rem; }
[data-testid="stMetricLabel"] { font-size: .82rem; color: var(--et-muted); }
[data-testid="stMetricValue"] { color: var(--et-ink); font-variant-numeric: tabular-nums; font-size: 1.55rem; }
.status-neutral, .status-warning, .status-critical, .status-muted { font-weight: 700; }
.status-neutral { color: #60A5FA; }
.status-warning { color: #FBBF24; }
.status-critical { color: #FB7185; }
.status-muted { color: #94A3B8; }
.provenance-box { border: 1px solid var(--et-border); padding: .75rem; border-radius: .45rem; background: var(--et-audit); color: var(--et-ink); font-size: .88rem; overflow-wrap: anywhere; }
.small-note, [data-testid="stCaptionContainer"] p { color: var(--et-muted); font-size: .84rem; line-height: 1.4; }
[data-testid="stDataFrame"] { border: 1px solid var(--et-border); border-radius: .45rem; overflow: hidden; }
[data-testid="stExpander"] { background: var(--et-surface); border: 1px solid var(--et-border); border-radius: .5rem; }
[data-testid="stTabs"] [data-baseweb="tab"] { color: var(--et-muted); }
[data-testid="stTabs"] [aria-selected="true"] { color: var(--et-ink) !important; border-bottom-color: var(--et-accent) !important; }
button[kind="secondary"], [data-testid="stButton"] button { border-color: #42607B !important; background: #122B41 !important; color: #EAF4FF !important; }
a:focus, button:focus, input:focus, [role="tab"]:focus { outline: 3px solid var(--et-focus) !important; outline-offset: 2px !important; }
@media (min-width: 1440px) { [data-testid="stMetricValue"] { font-size: 1.8rem; } }
@media (max-width: 1100px) { [data-testid="stSidebar"] { min-width: 220px; } .block-container { padding-left: 1rem; padding-right: 1rem; } }
</style>
"""
