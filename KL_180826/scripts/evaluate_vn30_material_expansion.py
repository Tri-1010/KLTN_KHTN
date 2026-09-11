from __future__ import annotations

import argparse
import logging
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

# Keep each worker single-threaded inside sklearn/xgboost/lightgbm to avoid CPU oversubscription.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

from pandas.errors import PerformanceWarning

warnings.filterwarnings("ignore", category=PerformanceWarning)
logging.disable(logging.INFO)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from scipy.stats import binom
from sklearn.metrics import balanced_accuracy_score

from pipeline.experiment_llm_semantic_features import (
    aggregate_daily_semantics,
    build_daily_technical,
    build_forward_labels,
    feature_sets,
    time_series_date_split,
)
from pipeline.task10_train import build_ml_models, evaluate_model, fit_imputer, prepare_features

VN30 = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]
MATERIAL_EVENTS = {"earnings", "dividend", "capital", "debt_risk", "legal_risk"}
ANN_PATH = "data/experiments/llm_semantic/focused_material_expanded_annotations_deepseek.csv"
PRICE_PATH = "data/prices/all_vn30_prices.csv"
OUT_PREFIX = "reports/llm_semantic_vn30_material_expansion"
CHECKPOINT_DIR = "data/experiments/llm_semantic/vn30_material_eval/checkpoints"
DEFAULT_HORIZONS = [1, 5, 10, 20, 60]
DEFAULT_WORKERS = 4
MODEL_FILTER: set[str] | None = None


def _slug(value: str) -> str:
    return str(value).replace("/", "_").replace("\\", "_").replace(" ", "_")


def _checkpoint_paths(checkpoint_dir: str, variant: str, scope: str, horizon: int) -> tuple[Path, Path]:
    base = Path(checkpoint_dir)
    tag = f"{_slug(variant)}__{_slug(scope)}__{horizon}d"
    return base / f"results__{tag}.csv", base / f"predictions__{tag}.csv"


def _checkpoint_ok(result_path: Path, pred_path: Path) -> bool:
    return result_path.exists() and pred_path.exists() and result_path.stat().st_size > 0 and pred_path.stat().st_size > 0


def _set_single_thread(model: Any) -> Any:
    if hasattr(model, "get_params") and hasattr(model, "set_params"):
        params = model.get_params()
        updates = {}
        for key in ("n_jobs", "nthread", "num_threads"):
            if key in params:
                updates[key] = 1
        if updates:
            model.set_params(**updates)
    return model


def load_prices() -> pd.DataFrame:
    prices = pd.read_csv(PRICE_PATH, encoding="utf-8")
    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    prices["ticker"] = prices["ticker"].astype(str).str.upper()
    prices = prices[prices["ticker"].isin(VN30)].dropna(subset=["date", "ticker", "close"]).copy()
    return prices.sort_values(["ticker", "date"]).reset_index(drop=True)


def load_annotations() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ann = pd.read_csv(ANN_PATH, encoding="utf-8")
    ann["ticker"] = ann["ticker"].astype(str).str.upper()
    ann["event_type"] = ann["event_type"].astype(str).str.lower()
    ann["relevance_to_ticker"] = ann["relevance_to_ticker"].astype(str).str.lower()
    ann = ann[ann["ticker"].isin(VN30) & ann["status"].astype(str).eq("ok")].copy()
    material = ann[ann["event_type"].isin(MATERIAL_EVENTS) & ann["relevance_to_ticker"].ne("irrelevant")].copy()
    direct = material[material["relevance_to_ticker"].eq("direct")].copy()
    return ann, material, direct


def select_variant_annotations(variant: str, material: pd.DataFrame, direct: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    if variant == "vn30_material":
        return material, False
    if variant == "vn30_direct_material":
        return direct, False
    if variant == "vn30_material_lag1":
        return material, True
    if variant == "vn30_direct_material_lag1":
        return direct, True
    raise ValueError(f"Unknown variant: {variant}")


def build_panel_with_horizons(prices: pd.DataFrame, annotations: pd.DataFrame, horizons: list[int]) -> pd.DataFrame:
    tech = build_daily_technical(prices)
    labels = build_forward_labels(prices, horizons)
    sem = aggregate_daily_semantics(annotations, prices)
    panel = tech.merge(labels, on=["ticker", "date"], how="inner").merge(sem, on=["ticker", "date"], how="left")
    for col in [c for c in panel.columns if c.startswith("llm_")]:
        panel[col] = pd.to_numeric(panel[col], errors="coerce").fillna(0.0)
    return panel.sort_values(["ticker", "date"]).reset_index(drop=True)


def shift_llm_one_trading_day(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.sort_values(["ticker", "date"]).copy()
    llm_cols = [c for c in out.columns if c.startswith("llm_")]
    out[llm_cols] = out.groupby("ticker", sort=False)[llm_cols].shift(1).fillna(0.0)
    return out


def evaluate_one_scope_horizon(panel: pd.DataFrame, horizon: int, scope_ticker: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    configs = feature_sets(panel)
    result_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    label_col = f"label_up_{horizon}d"
    if label_col not in panel.columns:
        return pd.DataFrame(), pd.DataFrame()
    work = panel.dropna(subset=[label_col]).copy()
    if work.empty:
        return pd.DataFrame(), pd.DataFrame()
    work["label_basic"] = work[label_col].astype(int)
    train_df, test_df = time_series_date_split(work)
    if train_df["label_basic"].nunique() < 2 or test_df["label_basic"].nunique() < 2:
        return pd.DataFrame(), pd.DataFrame()

    for config_name, cols in configs.items():
        numeric_cols = train_df[cols].select_dtypes(include=[np.number]).columns.tolist()
        usable = [c for c in numeric_cols if not train_df[c].isna().all()]
        if not usable:
            continue
        imputer, _ = fit_imputer(train_df, usable)
        X_train, y_train = prepare_features(train_df, usable, imputer=imputer)
        X_test, y_test = prepare_features(test_df, usable, imputer=imputer)
        common = [c for c in X_train.columns if c in X_test.columns]
        X_train = X_train[common]
        X_test = X_test[common]
        for model_name, model in build_ml_models(y_train).items():
            if MODEL_FILTER and model_name not in MODEL_FILTER:
                continue
            model = _set_single_thread(model)
            model.fit(X_train, y_train)
            res = evaluate_model(model, X_test, y_test, model_name, config_name)
            res.update(
                {
                    "horizon": f"{horizon}d",
                    "ticker": scope_ticker,
                    "n_train": int(len(train_df)),
                    "n_test": int(len(test_df)),
                    "n_features": int(len(common)),
                    "train_start": str(train_df["date"].min().date()),
                    "train_end": str(train_df["date"].max().date()),
                    "test_start": str(test_df["date"].min().date()),
                    "test_end": str(test_df["date"].max().date()),
                }
            )
            result_rows.append(res)
            preds = model.predict(X_test)
            for idx, y, pred in zip(X_test.index, y_test, preds):
                pred_rows.append(
                    {
                        "scope_ticker": scope_ticker,
                        "ticker": str(test_df.loc[idx, "ticker"]),
                        "date": str(pd.Timestamp(test_df.loc[idx, "date"]).date()),
                        "horizon": f"{horizon}d",
                        "model": model_name,
                        "config": config_name,
                        "y_true": int(y),
                        "y_pred": int(pred),
                    }
                )
    return pd.DataFrame(result_rows), pd.DataFrame(pred_rows)


def run_variant_job(job: dict[str, Any]) -> list[str]:
    variant = job["variant"]
    horizons = job["horizons"]
    run_per_ticker = job["run_per_ticker"]
    checkpoint_dir = job["checkpoint_dir"]
    force = job["force"]
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

    prices = load_prices()
    _, material, direct = load_annotations()
    annotations, lag = select_variant_annotations(variant, material, direct)
    panel = build_panel_with_horizons(prices, annotations, horizons)
    if lag:
        panel = shift_llm_one_trading_day(panel)

    scopes = ["ALL"]
    if run_per_ticker:
        scopes.extend(VN30)

    completed: list[str] = []
    for scope in scopes:
        scope_panel = panel if scope == "ALL" else panel[panel["ticker"].eq(scope)].copy()
        for horizon in horizons:
            result_path, pred_path = _checkpoint_paths(checkpoint_dir, variant, scope, horizon)
            if not force and _checkpoint_ok(result_path, pred_path):
                completed.append(f"skip:{variant}:{scope}:{horizon}d")
                continue
            res, pred = evaluate_one_scope_horizon(scope_panel, horizon, scope)
            if not res.empty:
                res.insert(0, "variant", variant)
            if not pred.empty:
                pred.insert(0, "variant", variant)
            res.to_csv(result_path, index=False, encoding="utf-8")
            pred.to_csv(pred_path, index=False, encoding="utf-8")
            completed.append(f"done:{variant}:{scope}:{horizon}d")
    return completed


def midp_mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    exact = min(1.0, float(2 * binom.cdf(k, n, 0.5)))
    obs_prob = float(binom.pmf(k, n, 0.5))
    return max(0.0, min(1.0, exact - obs_prob))


def bootstrap_delta_ci(y, pa, ph, n_boot: int = 1000) -> tuple[float, float, float]:
    y = np.asarray(y)
    pa = np.asarray(pa)
    ph = np.asarray(ph)
    n = len(y)
    rng = np.random.default_rng(20260708)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y[idx])) < 2:
            continue
        vals.append(balanced_accuracy_score(y[idx], ph[idx]) - balanced_accuracy_score(y[idx], pa[idx]))
    if not vals:
        return np.nan, np.nan, np.nan
    vals = np.asarray(vals)
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975)), float(vals.mean())


def load_checkpoint_csvs(checkpoint_dir: str, kind: str) -> pd.DataFrame:
    files = sorted(Path(checkpoint_dir).glob(f"{kind}__*.csv"))
    frames = []
    for path in files:
        if path.stat().st_size == 0:
            continue
        try:
            df = pd.read_csv(path, encoding="utf-8")
        except pd.errors.EmptyDataError:
            continue
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def build_stats(results: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if preds.empty or results.empty:
        return pd.DataFrame(rows)
    for key, grp in preds.groupby(["variant", "scope_ticker", "horizon", "model"], sort=True):
        wide = grp.pivot_table(
            index=["ticker", "date", "y_true"],
            columns="config",
            values="y_pred",
            aggfunc="first",
        ).reset_index()
        if not {"Config_A", "Config_Hybrid"}.issubset(wide.columns):
            continue
        y = wide["y_true"].astype(int).to_numpy()
        pa = wide["Config_A"].astype(int).to_numpy()
        ph = wide["Config_Hybrid"].astype(int).to_numpy()
        a_correct = pa == y
        h_correct = ph == y
        b = int((a_correct & ~h_correct).sum())
        c = int((~a_correct & h_correct).sum())
        ci_low, ci_high, boot_mean = bootstrap_delta_ci(y, pa, ph)
        variant, scope, horizon, model = key
        rsub = results[
            results["variant"].eq(variant)
            & results["ticker"].eq(scope)
            & results["horizon"].eq(horizon)
            & results["model"].eq(model)
        ]
        ba_a = float(rsub[rsub["config"].eq("Config_A")]["balanced_accuracy"].iloc[0]) if not rsub[rsub["config"].eq("Config_A")].empty else np.nan
        ba_h = float(rsub[rsub["config"].eq("Config_Hybrid")]["balanced_accuracy"].iloc[0]) if not rsub[rsub["config"].eq("Config_Hybrid")].empty else np.nan
        n_test = int(rsub["n_test"].max()) if not rsub.empty else len(wide)
        rows.append(
            {
                "variant": variant,
                "ticker": scope,
                "horizon": horizon,
                "model": model,
                "n_test": n_test,
                "ba_a": ba_a,
                "ba_hybrid": ba_h,
                "delta_hybrid_minus_a": ba_h - ba_a,
                "b": b,
                "c": c,
                "n_discordant": b + c,
                "p_mid": midp_mcnemar(b, c),
                "delta_ci_low": ci_low,
                "delta_ci_high": ci_high,
                "delta_boot_mean": boot_mean,
            }
        )
    return pd.DataFrame(rows)


def write_counts(path: str) -> tuple[int, int, int, int, int]:
    ann, material, direct = load_annotations()
    count_rows = []
    for name, df in [("all_ok", ann), ("material_events_only", material), ("direct_material_only", direct)]:
        grouped = df.groupby(["ticker", "event_type", "relevance_to_ticker"]).size().rename("n_articles").reset_index()
        grouped.insert(0, "variant", name)
        count_rows.append(grouped)
    pd.concat(count_rows, ignore_index=True).to_csv(path, index=False, encoding="utf-8")
    return len(ann), len(material), len(direct), material.ticker.nunique(), direct.ticker.nunique()


def write_summary(results: pd.DataFrame, stats: pd.DataFrame, counts: tuple[int, int, int, int, int], args: argparse.Namespace) -> None:
    ok_n, material_n, direct_n, material_tickers, direct_tickers = counts
    lines = [
        "# VN30 material-event semantic expansion",
        "",
        f"- universe: original VN30 ({len(VN30)} tickers)",
        f"- source annotations: `{ANN_PATH}`",
        f"- checkpoint_dir: `{args.checkpoint_dir}`",
        f"- workers: {args.workers}",
        f"- horizons: {','.join(str(h) + 'd' for h in args.horizons)} (20d ≈ 1 month, 60d ≈ 3 months)",
        f"- run_per_ticker: {args.run_per_ticker}",
        f"- ok_annotations_vn30: {ok_n}",
        f"- material_annotations_vn30: {material_n}",
        f"- direct_material_annotations_vn30: {direct_n}",
        f"- material_tickers: {material_tickers}",
        f"- direct_material_tickers: {direct_tickers}",
        "",
    ]
    if not stats.empty:
        pooled = stats[stats["ticker"].eq("ALL")].sort_values("delta_hybrid_minus_a", ascending=False).head(30)
        lines += [
            "## Pooled original VN30 — best Hybrid vs Technical deltas",
            "",
            "```text",
            pooled[["variant", "horizon", "model", "n_test", "ba_a", "ba_hybrid", "delta_hybrid_minus_a", "delta_ci_low", "delta_ci_high", "p_mid", "b", "c"]].round(4).to_string(index=False),
            "```",
            "",
        ]
        if stats[~stats["ticker"].eq("ALL")].shape[0] > 0:
            per = stats[~stats["ticker"].eq("ALL")].sort_values("delta_hybrid_minus_a", ascending=False).head(30)
            lines += [
                "## Per-ticker original VN30 — best Hybrid vs Technical deltas",
                "",
                "```text",
                per[["variant", "ticker", "horizon", "model", "n_test", "ba_a", "ba_hybrid", "delta_hybrid_minus_a", "delta_ci_low", "delta_ci_high", "p_mid", "b", "c"]].round(4).to_string(index=False),
                "```",
                "",
            ]
    if not results.empty:
        pivot = results.pivot_table(index=["variant", "horizon", "model"], columns="config", values="balanced_accuracy").reset_index()
        if {"Config_A", "Config_Hybrid"}.issubset(pivot.columns):
            pivot["delta_hybrid_minus_A"] = pivot["Config_Hybrid"] - pivot["Config_A"]
            lines += [
                "## All pooled deltas",
                "",
                "```text",
                pivot.sort_values("delta_hybrid_minus_A", ascending=False).round(4).to_string(index=False),
                "```",
                "",
            ]
    Path(f"{OUT_PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate VN30 material-event LLM features with checkpoints and parallel workers.")
    parser.add_argument("--horizons", default=",".join(str(h) for h in DEFAULT_HORIZONS), help="Trading-day horizons, e.g. 1,5,10,20,60")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Parallel variant workers")
    parser.add_argument("--checkpoint-dir", default=CHECKPOINT_DIR)
    parser.add_argument("--run-per-ticker", action="store_true", help="Also evaluate each VN30 ticker separately")
    parser.add_argument("--force", action="store_true", help="Ignore existing checkpoints and recompute")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    args.horizons = [int(x) for x in str(args.horizons).split(",") if str(x).strip()]
    Path("reports").mkdir(exist_ok=True)
    Path(args.checkpoint_dir).mkdir(parents=True, exist_ok=True)

    counts = write_counts(f"{OUT_PREFIX}_counts.csv")
    variants = ["vn30_material", "vn30_direct_material", "vn30_material_lag1", "vn30_direct_material_lag1"]
    jobs = [
        {
            "variant": variant,
            "horizons": args.horizons,
            "run_per_ticker": args.run_per_ticker,
            "checkpoint_dir": args.checkpoint_dir,
            "force": args.force,
        }
        for variant in variants
    ]

    print(f"start workers={args.workers} variants={len(jobs)} horizons={args.horizons} checkpoint_dir={args.checkpoint_dir}", flush=True)
    if args.workers <= 1:
        for job in jobs:
            completed = run_variant_job(job)
            print(f"job {job['variant']} completed {len(completed)} steps", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_variant = {executor.submit(run_variant_job, job): job["variant"] for job in jobs}
            for future in as_completed(future_to_variant):
                variant = future_to_variant[future]
                completed = future.result()
                print(f"job {variant} completed {len(completed)} steps", flush=True)

    results = load_checkpoint_csvs(args.checkpoint_dir, "results")
    preds = load_checkpoint_csvs(args.checkpoint_dir, "predictions")
    stats = build_stats(results, preds)
    results.to_csv(f"{OUT_PREFIX}_results.csv", index=False, encoding="utf-8")
    preds.to_csv(f"{OUT_PREFIX}_predictions.csv", index=False, encoding="utf-8")
    stats.to_csv(f"{OUT_PREFIX}_stats.csv", index=False, encoding="utf-8")
    write_summary(results, stats, counts, args)
    print(f"saved {OUT_PREFIX}_summary.md", flush=True)
    print(f"saved {OUT_PREFIX}_results.csv rows={len(results)}", flush=True)
    print(f"saved {OUT_PREFIX}_stats.csv rows={len(stats)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
