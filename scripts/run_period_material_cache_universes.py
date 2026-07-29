from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

import scripts.evaluate_period_material_hybrid as base

CACHE_PATH = "data/experiments/llm_semantic/article_semantics_cache.csv"
OUT_PREFIX = "reports/llm_semantic_period_material_cache_universes"
CHECKPOINT_DIR = Path("data/experiments/llm_semantic/period_material_cache_universes/checkpoints")

VN30 = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]


def hose80_tickers() -> list[str]:
    prices = pd.read_csv(base.PRICES_PATH, usecols=["ticker"], encoding="utf-8")
    return sorted(prices["ticker"].astype(str).str.upper().dropna().unique().tolist())


def checkpoint_paths(universe: str, relevance: str, unit: str) -> tuple[Path, Path]:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    tag = f"{universe}__{relevance}__{unit}"
    return CHECKPOINT_DIR / f"results__{tag}.csv", CHECKPOINT_DIR / f"predictions__{tag}.csv"


def checkpoint_ok(res_path: Path, pred_path: Path) -> bool:
    return res_path.exists() and pred_path.exists() and res_path.stat().st_size > 0 and pred_path.stat().st_size > 0


def run_combo(universe: str, tickers: list[str], relevance: str, unit: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    res_path, pred_path = checkpoint_paths(universe, relevance, unit)
    if checkpoint_ok(res_path, pred_path):
        res = pd.read_csv(res_path, encoding="utf-8")
        pred = pd.read_csv(pred_path, encoding="utf-8")
        print(f"skip universe={universe} relevance={relevance} unit={unit} results={len(res)}", flush=True)
        return res, pred

    base.VN30 = tickers
    base.ANNOTATION_PATH = CACHE_PATH
    res, pred = base.evaluate_unit(unit, base.THRESHOLD, relevance)
    if not res.empty:
        res.insert(0, "universe", universe)
    if not pred.empty:
        pred.insert(0, "universe", universe)
    res.to_csv(res_path, index=False, encoding="utf-8")
    pred.to_csv(pred_path, index=False, encoding="utf-8")
    print(f"done universe={universe} relevance={relevance} unit={unit} results={len(res)} predictions={len(pred)}", flush=True)
    return res, pred


def build_stats(results: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if results.empty or preds.empty:
        return pd.DataFrame(rows)
    for key, grp in preds.groupby(["universe", "relevance_variant", "unit", "model"], sort=True):
        wide = grp.pivot_table(index=["ticker", "period_id", "y_true"], columns="config", values="y_pred", aggfunc="first").reset_index()
        if not {"Config_A", "Config_Hybrid"}.issubset(wide.columns):
            continue
        y = wide["y_true"].astype(int).to_numpy()
        pa = wide["Config_A"].astype(int).to_numpy()
        ph = wide["Config_Hybrid"].astype(int).to_numpy()
        b = int(((pa == y) & (ph != y)).sum())
        c = int(((pa != y) & (ph == y)).sum())
        universe, relevance, unit, model = key
        rsub = results[
            results["universe"].eq(universe)
            & results["relevance_variant"].eq(relevance)
            & results["unit"].eq(unit)
            & results["model"].eq(model)
        ]
        a = rsub[rsub["config"].eq("Config_A")]
        h = rsub[rsub["config"].eq("Config_Hybrid")]
        if a.empty or h.empty:
            continue
        rows.append(
            {
                "universe": universe,
                "relevance_variant": relevance,
                "unit": unit,
                "model": model,
                "n_test": int(a["test_samples"].iloc[0]),
                "ba_a": float(a["balanced_accuracy"].iloc[0]),
                "ba_hybrid": float(h["balanced_accuracy"].iloc[0]),
                "delta_hybrid_minus_a": float(h["balanced_accuracy"].iloc[0] - a["balanced_accuracy"].iloc[0]),
                "b": b,
                "c": c,
                "n_discordant": b + c,
                "p_mid": base.midp_mcnemar(b, c),
            }
        )
    return pd.DataFrame(rows)


def write_summary(results: pd.DataFrame, stats: pd.DataFrame) -> None:
    lines = [
        "# Period-level material hybrid — cache total universes",
        "",
        f"- annotation_source: `{CACHE_PATH}`",
        "- universes: VN30, HOSE80/liquid universe",
        f"- units: {', '.join(base.UNITS)}",
        f"- relevance_variants: {', '.join(base.RELEVANCE_VARIANTS)}",
        f"- threshold: next_period_return > {base.THRESHOLD:.2%}",
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
    base.UNITS = ["1week", "2week", "month", "2month", "quarter"]
    universes = {"VN30": VN30, "HOSE80": hose80_tickers()}
    all_results = []
    all_preds = []
    for universe, tickers in universes.items():
        print(f"universe={universe} tickers={len(tickers)}", flush=True)
        for relevance in base.RELEVANCE_VARIANTS:
            for unit in base.UNITS:
                res, pred = run_combo(universe, tickers, relevance, unit)
                all_results.append(res)
                all_preds.append(pred)
    results = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    preds = pd.concat(all_preds, ignore_index=True) if all_preds else pd.DataFrame()
    stats = build_stats(results, preds)
    results.to_csv(f"{OUT_PREFIX}_results.csv", index=False, encoding="utf-8")
    preds.to_csv(f"{OUT_PREFIX}_predictions.csv", index=False, encoding="utf-8")
    stats.to_csv(f"{OUT_PREFIX}_stats.csv", index=False, encoding="utf-8")
    write_summary(results, stats)
    print(f"saved {OUT_PREFIX}_summary.md", flush=True)
    print(f"saved {OUT_PREFIX}_results.csv rows={len(results)}", flush=True)
    print(f"saved {OUT_PREFIX}_stats.csv rows={len(stats)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
