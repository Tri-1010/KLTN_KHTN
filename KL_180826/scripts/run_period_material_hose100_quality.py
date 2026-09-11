from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

import scripts.evaluate_period_material_hybrid as base
import scripts.run_period_material_cache_universes as runner

OUT_PREFIX = "reports/llm_semantic_period_material_hose100_quality"
PRICE_DIR = Path("data/prices_extended")
BASE_PRICE_PATH = "data/prices/all_vn30_prices.csv"
PRICE_PATH = "data/prices/hose100_quality_prices.csv"
TICKER_PATH = "reports/hose100_quality_selected_tickers.csv"


def load_tickers() -> list[str]:
    tickers = pd.read_csv(TICKER_PATH)["ticker"].astype(str).str.upper().tolist()
    return list(dict.fromkeys(tickers))


def build_price_panel(tickers: list[str]) -> pd.DataFrame:
    frames = []
    missing = []
    # Pre-load base price file so old HOSE80 tickers not in prices_extended still get data
    base_cache = {}
    if Path(BASE_PRICE_PATH).exists():
        base_df = pd.read_csv(BASE_PRICE_PATH, encoding="utf-8")
        base_df["date"] = pd.to_datetime(base_df["date"], errors="coerce")
        base_df["ticker"] = base_df["ticker"].astype(str).str.upper()
        for t, g in base_df.groupby("ticker"):
            base_cache[t] = g.copy()
    for ticker in tickers:
        path = PRICE_DIR / f"{ticker}.csv"
        if path.exists():
            df = pd.read_csv(path, encoding="utf-8")
        elif ticker in base_cache:
            df = base_cache[ticker]
        else:
            missing.append(ticker)
            continue
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date", "close", "volume"]).copy()
        if "ticker" in df.columns:
            df["ticker"] = ticker
        else:
            df.insert(0, "ticker", ticker)
        frames.append(df[["ticker", "date", "open", "high", "low", "close", "volume"]])
    if missing:
        print(f"missing_price={','.join(missing)}", flush=True)
    if not frames:
        raise RuntimeError("No price frames built for HOSE100")
    out = pd.concat(frames, ignore_index=True).sort_values(["ticker", "date"]).reset_index(drop=True)
    Path(PRICE_PATH).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(PRICE_PATH, index=False, encoding="utf-8")
    return out


def write_summary(results: pd.DataFrame, stats: pd.DataFrame, tickers: list[str], prices: pd.DataFrame) -> None:
    lines = [
        "# Period-level material hybrid — HOSE100 quality universe",
        "",
        f"- annotation_source: `{runner.CACHE_PATH}`",
        f"- price_source: `{PRICE_PATH}`",
        f"- universe: HOSE100 quality ({len(tickers)} tickers)",
        "- selection: original HOSE80 + 20 liquid HOSE tickers from `data/prices_extended`",
        f"- units: {', '.join(base.UNITS)}",
        f"- relevance_variants: {', '.join(base.RELEVANCE_VARIANTS)}",
        f"- threshold: next_period_return > {base.THRESHOLD:.2%}",
        f"- price_rows: {len(prices)}",
        "",
        "## Tickers",
        "",
        "```text",
        ",".join(tickers),
        "```",
        "",
    ]
    if not stats.empty:
        lines += [
            "## Best deltas",
            "",
            "```text",
            stats.sort_values("delta_hybrid_minus_a", ascending=False).head(80).round(4).to_string(index=False),
            "```",
            "",
        ]
    if not results.empty:
        pivot = results.pivot_table(index=["universe", "relevance_variant", "unit", "model"], columns="config", values="balanced_accuracy").reset_index()
        if {"Config_A", "Config_Hybrid"}.issubset(pivot.columns):
            pivot["delta_hybrid_minus_A"] = pivot["Config_Hybrid"] - pivot["Config_A"]
        lines += [
            "## Balanced accuracy",
            "",
            "```text",
            pivot.sort_values("delta_hybrid_minus_A", ascending=False).head(100).round(4).to_string(index=False),
            "```",
            "",
        ]
        meta_cols = ["universe", "relevance_variant", "unit", "n_samples", "n_periods", "test_samples", "positive_rate_test", "llm_nonzero_rows", "annotations"]
        meta = results[meta_cols].drop_duplicates().sort_values(["universe", "relevance_variant", "unit"])
        lines += [
            "## Coverage",
            "",
            "```text",
            meta.round(4).to_string(index=False),
            "```",
            "",
        ]
    Path(f"{OUT_PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    Path("reports").mkdir(exist_ok=True)
    tickers = load_tickers()
    prices = build_price_panel(tickers)
    base.PRICES_PATH = PRICE_PATH
    base.UNITS = ["1week", "2week", "month", "2month", "quarter"]
    runner.OUT_PREFIX = OUT_PREFIX
    runner.CHECKPOINT_DIR = Path("data/experiments/llm_semantic/period_material_hose100_quality/checkpoints")
    all_results = []
    all_preds = []
    universe = "HOSE100_quality"
    print(f"universe={universe} tickers={len(tickers)} price_rows={len(prices)}", flush=True)
    for relevance in base.RELEVANCE_VARIANTS:
        for unit in base.UNITS:
            res, pred = runner.run_combo(universe, tickers, relevance, unit)
            all_results.append(res)
            all_preds.append(pred)
    results = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    preds = pd.concat(all_preds, ignore_index=True) if all_preds else pd.DataFrame()
    stats = runner.build_stats(results, preds)
    results.to_csv(f"{OUT_PREFIX}_results.csv", index=False, encoding="utf-8")
    preds.to_csv(f"{OUT_PREFIX}_predictions.csv", index=False, encoding="utf-8")
    stats.to_csv(f"{OUT_PREFIX}_stats.csv", index=False, encoding="utf-8")
    write_summary(results, stats, tickers, prices)
    print(f"saved {OUT_PREFIX}_summary.md", flush=True)
    print(f"saved {OUT_PREFIX}_results.csv rows={len(results)}", flush=True)
    print(f"saved {OUT_PREFIX}_stats.csv rows={len(stats)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
