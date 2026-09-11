"""Responsive, accessible light/dark visual tokens for the standalone V2 UI."""

from __future__ import annotations


V2_CSS = """
<style>
:root {
  --v2-page: #f6f8fb;
  --v2-surface: #ffffff;
  --v2-raised: #f0f4f8;
  --v2-ink: #172033;
  --v2-muted: #526176;
  --v2-border: #c8d2df;
  --v2-accent: #0f5cad;
  --v2-accent-ink: #ffffff;
  --v2-focus: #e06f00;
  --v2-positive: #0a7b5c;
  --v2-warning: #9a5b00;
  --v2-negative: #a23b3b;
}
@media (prefers-color-scheme: dark) {
  :root {
    --v2-page: #111827;
    --v2-surface: #192234;
    --v2-raised: #222d42;
    --v2-ink: #edf3fb;
    --v2-muted: #b9c5d6;
    --v2-border: #40506a;
    --v2-accent: #83b9ff;
    --v2-accent-ink: #122039;
    --v2-focus: #ffb45e;
    --v2-positive: #74d5b7;
    --v2-warning: #f6c270;
    --v2-negative: #ffaaa5;
  }
}
html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
.stApp { background: var(--v2-page); color: var(--v2-ink); }
.block-container { max-width: 1440px; padding: 1.25rem clamp(1rem, 3vw, 3rem) 2.5rem; }
[data-testid="stSidebar"] { background: var(--v2-surface); border-right: 1px solid var(--v2-border); }
[data-testid="stSidebar"] * { color: var(--v2-ink); }
.v2-banner, .v2-card, .v2-status, .v2-limitations {
  background: var(--v2-surface);
  border: 1px solid var(--v2-border);
  border-radius: .65rem;
  padding: .9rem 1rem;
  margin: .65rem 0;
}
.v2-banner { border-left: .3rem solid var(--v2-accent); }
.v2-status { border-left: .3rem solid var(--v2-warning); }
.v2-limitations { border-left: .3rem solid var(--v2-negative); }
.v2-kicker { color: var(--v2-muted); font-weight: 700; letter-spacing: .06em; text-transform: uppercase; font-size: .78rem; }
.v2-state-primary { color: var(--v2-accent); font-weight: 750; }
.v2-state-exploratory { color: var(--v2-warning); font-weight: 750; }
.v2-state-confirmation { color: var(--v2-positive); font-weight: 750; }
[data-testid="stMetric"] { background: var(--v2-surface); border: 1px solid var(--v2-border); border-radius: .55rem; padding: .65rem .8rem; }
[data-testid="stDataFrame"] { border: 1px solid var(--v2-border); border-radius: .55rem; overflow: hidden; }
[data-baseweb="tab-list"] { gap: .4rem; }
[data-baseweb="tab"] { color: var(--v2-muted); }
[data-baseweb="tab"][aria-selected="true"] { color: var(--v2-ink); border-bottom-color: var(--v2-accent) !important; }
button, a, input, select, textarea, [role="tab"], [role="radio"] { min-height: 2rem; }
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible,
[role="tab"]:focus-visible, [role="radio"]:focus-visible {
  outline: 3px solid var(--v2-focus) !important;
  outline-offset: 3px !important;
}
@media (max-width: 800px) {
  .block-container { padding: .75rem .85rem 1.5rem; }
  [data-testid="stHorizontalBlock"] { gap: .5rem; }
  [data-testid="stMetricValue"] { font-size: 1.35rem; }
}
</style>
"""
