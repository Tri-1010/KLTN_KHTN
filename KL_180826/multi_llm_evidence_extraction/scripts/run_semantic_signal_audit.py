from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, REPORT_DIR, ROOT, ensure_dirs, markdown_table
from build_semantic_features import map_to_trading_date

CONSENSUS = OUTPUT_DIR / "pseudo_labels_consensus.csv"
PRICES = ROOT / "data" / "prices" / "all_vn30_prices.csv"
VNINDEX = ROOT / "data" / "prices_extended" / "VNINDEX.csv"
OUT = OUTPUT_DIR / "event_window_outcomes.csv"
REPORT = REPORT_DIR / "semantic_signal_audit_report.md"
WINDOWS = [1, 5, 20, 60]


def forward_return(frame: pd.DataFrame, start_date: pd.Timestamp, horizon: int) -> tuple[float | None, pd.Timestamp | None]:
    work = frame.sort_values("date").reset_index(drop=True)
    pos = work["date"].searchsorted(start_date, side="left")
    if pos >= len(work) or pos + horizon >= len(work):
        return None, None
    start = float(work.loc[pos, "close"])
    end = float(work.loc[pos + horizon, "close"])
    return (end / start - 1 if start else None), pd.Timestamp(work.loc[pos + horizon, "date"])


def forward_metrics(prices: pd.DataFrame, benchmark: pd.DataFrame, ticker: str, effective_date: pd.Timestamp, horizon: int) -> dict[str, object]:
    stock = prices[prices["ticker"].astype(str).str.upper().eq(ticker)].sort_values("date").reset_index(drop=True)
    pos = stock["date"].searchsorted(effective_date, side="left")
    if pos >= len(stock) or pos + horizon >= len(stock):
        return {"raw_return": None, "benchmark_return": None, "market_adjusted_return": None, "abnormal_volume": None, "volatility": None, "max_adverse_move": None, "window_end_date": None, "benchmark_window_end_date": None}
    start = float(stock.loc[pos, "close"])
    end = float(stock.loc[pos + horizon, "close"])
    window = stock.loc[pos:pos + horizon].copy()
    returns = window["close"].pct_change().dropna()
    base_volume = stock.loc[max(0, pos - 20):pos - 1, "volume"].mean() if pos > 0 else None
    raw = end / start - 1 if start else None
    stock_end = pd.Timestamp(stock.loc[pos + horizon, "date"])
    market, market_end = forward_return(benchmark, effective_date, horizon)
    adjusted = raw - market if raw is not None and market is not None else None
    return {
        "raw_return": raw,
        "benchmark_return": market,
        "market_adjusted_return": adjusted,
        "abnormal_volume": float(window["volume"].mean() / base_volume - 1) if base_volume and pd.notna(base_volume) else None,
        "volatility": float(returns.std()) if len(returns) else None,
        "max_adverse_move": float(window["close"].min() / start - 1) if start else None,
        "window_end_date": stock_end,
        "benchmark_window_end_date": market_end,
    }


def main() -> int:
    ensure_dirs()
    lines = ["# Semantic signal audit report", "", "Point-in-time next-trading-day mapping. Primary metric is VNINDEX-adjusted return; exploratory, not causal.", ""]
    if not CONSENSUS.exists():
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        lines.append("Consensus labels unavailable.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0
    labels = pd.read_csv(CONSENSUS, encoding="utf-8-sig")
    if "analysis_eligible" in labels:
        labels = labels[labels["analysis_eligible"].astype(str).str.lower().isin(["true", "1"])]
    prices = pd.read_csv(PRICES, encoding="utf-8")
    prices["date"] = pd.to_datetime(prices["date"], errors="coerce").dt.normalize()
    benchmark = pd.read_csv(VNINDEX, encoding="utf-8")
    benchmark["date"] = pd.to_datetime(benchmark["date"], errors="coerce").dt.normalize()
    mapped = map_to_trading_date(labels, prices)
    rows = []
    for _, row in mapped.iterrows():
        ticker = str(row.get("ticker", "")).upper()
        effective = pd.Timestamp(row["effective_date"])
        article = pd.to_datetime(row.get("article_date"), errors="coerce")
        for horizon in WINDOWS:
            metrics = forward_metrics(prices, benchmark, ticker, effective, horizon)
            rows.append({
                "artifact_schema_version": "event_window_outcomes_v2",
                "news_id": row.get("news_id"), "ticker": ticker,
                "article_date": str(article.date()) if pd.notna(article) else "",
                "effective_date": str(effective.date()), "event_date": str(effective.date()),
                "mapping_policy": row.get("mapping_policy"), "window": f"T+{horizon}",
                "ticker_relevance": row.get("consensus_ticker_relevance"),
                "materiality": row.get("consensus_materiality"),
                "direction": row.get("consensus_direction"),
                "event_type": row.get("consensus_event_type"), **metrics,
            })
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    lines.append(f"- Outcome rows: {len(out)}")
    if not out.empty:
        lines += ["", "## Mean VNINDEX-adjusted return by materiality/window", "", markdown_table(out.pivot_table(index="window", columns="materiality", values="market_adjusted_return", aggfunc="mean").round(4))]
        lines += ["", "## Mean VNINDEX-adjusted return by direction/window", "", markdown_table(out.pivot_table(index="window", columns="direction", values="market_adjusted_return", aggfunc="mean").round(4))]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {OUT} rows={len(out)}")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
