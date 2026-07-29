from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

import scripts.run_period_material_cache_universes as runner
import scripts.evaluate_period_material_hybrid as base

OUT_PREFIX = "reports/llm_semantic_period_material_filtered_universes"
PROFILE_PATH = "reports/liquid_material_universe_profile.csv"


def build_universes() -> dict[str, list[str]]:
    profile = pd.read_csv(PROFILE_PATH)
    universes = {}
    specs = [
        ("liquid50_mat5", 50, 5),
        ("liquid100_mat5", 100, 5),
        ("liquid100_mat10", 100, 10),
        ("liquid200_mat5", 200, 5),
    ]
    for name, min_value, min_material in specs:
        sub = profile[(profile["avg_value_bil_vnd"] >= min_value) & (profile["material_di"] >= min_material)].copy()
        universes[name] = sub["ticker"].astype(str).str.upper().tolist()
    return universes


def main() -> int:
    Path("reports").mkdir(exist_ok=True)
    base.UNITS = ["1week", "2week", "month", "2month", "quarter"]
    runner.OUT_PREFIX = OUT_PREFIX
    runner.CHECKPOINT_DIR = Path("data/experiments/llm_semantic/period_material_filtered_universes/checkpoints")
    universes = build_universes()
    all_results = []
    all_preds = []
    for universe, tickers in universes.items():
        print(f"universe={universe} tickers={len(tickers)}", flush=True)
        for relevance in ["direct", "direct_indirect", "any_relevance"]:
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
    runner.write_summary(results, stats)
    print(f"saved {OUT_PREFIX}_summary.md", flush=True)
    print(f"saved {OUT_PREFIX}_results.csv rows={len(results)}", flush=True)
    print(f"saved {OUT_PREFIX}_stats.csv rows={len(stats)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
