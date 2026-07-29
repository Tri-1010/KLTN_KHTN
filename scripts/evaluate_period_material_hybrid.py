from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from scipy.stats import binom
from sklearn.metrics import balanced_accuracy_score

warnings.filterwarnings("ignore", category=PerformanceWarning)
logging.disable(logging.INFO)

from pipeline.experiment_period import (  # noqa: E402
    PERIOD_MONTHS,
    build_period_technical,
    make_period_funcs,
    _period_split,
)
from pipeline.task10_train import build_ml_models, evaluate_model, fit_imputer, prepare_features  # noqa: E402

PRICES_PATH = "data/prices/all_vn30_prices.csv"
ANNOTATION_PATH = "data/experiments/llm_semantic/focused_material_expanded_annotations_deepseek.csv"
OUT_PREFIX = "reports/llm_semantic_period_material_relevance_variants"
VN30 = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]
UNITS = ["1week", "2week", "month", "2month", "quarter"]
RELEVANCE_VARIANTS = ["direct", "direct_indirect", "any_relevance", "indirect_only"]
THRESHOLD = 0.02
MATERIAL_EVENTS = {"earnings", "dividend", "capital", "debt_risk", "legal_risk"}
TECH_COLS = [
    "return_p", "return_mean_daily", "return_std_daily", "volatility_p",
    "price_range_p", "volume_mean_p", "volume_change_p", "sma20_end",
    "ema20_end", "price_vs_sma20", "rsi_mean_p", "rsi_end_p",
    "macd_hist_mean_p", "bb_position_p", "return_prev_p", "return_2p_ago",
]


def load_prices() -> pd.DataFrame:
    prices = pd.read_csv(PRICES_PATH, encoding="utf-8")
    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    prices["ticker"] = prices["ticker"].astype(str).str.upper()
    prices = prices[prices["ticker"].isin(VN30)].dropna(subset=["date", "ticker", "close"]).copy()
    return prices.sort_values(["ticker", "date"]).reset_index(drop=True)


def load_material_annotations(relevance_variant: str) -> pd.DataFrame:
    ann = pd.read_csv(ANNOTATION_PATH, encoding="utf-8")
    ann["ticker"] = ann["ticker"].astype(str).str.upper()
    ann["article_date"] = pd.to_datetime(ann["article_date"], errors="coerce")
    ann["event_type"] = ann["event_type"].astype(str).str.lower()
    ann["relevance_to_ticker"] = ann["relevance_to_ticker"].astype(str).str.lower()
    ann["sentiment"] = ann["sentiment"].astype(str).str.lower()
    base = ann[
        ann["ticker"].isin(VN30)
        & ann["status"].astype(str).eq("ok")
        & ann["event_type"].isin(MATERIAL_EVENTS)
    ].copy()
    if relevance_variant == "direct":
        base = base[base["relevance_to_ticker"].eq("direct")].copy()
    elif relevance_variant == "direct_indirect":
        base = base[base["relevance_to_ticker"].isin({"direct", "indirect"})].copy()
    elif relevance_variant == "any_relevance":
        base = base[base["relevance_to_ticker"].isin({"direct", "indirect", "irrelevant"})].copy()
    elif relevance_variant == "indirect_only":
        base = base[base["relevance_to_ticker"].eq("indirect")].copy()
    else:
        raise ValueError(f"Unknown relevance_variant: {relevance_variant}")
    for col in ["sentiment_score", "importance_score", "information_magnitude_score", "uncertainty_score", "novelty_hint_score", "reasoning_confidence"]:
        base[col] = pd.to_numeric(base[col], errors="coerce")
    return base.dropna(subset=["article_date", "ticker"])


def build_threshold_labels(tech_df: pd.DataFrame, next_fn, threshold: float) -> pd.DataFrame:
    close_lookup = tech_df.set_index(["ticker", "period_id"])["avg_close"]
    out = tech_df[["ticker", "period_id", "avg_close"]].copy()
    out["next_period_id"] = out["period_id"].apply(next_fn)
    out["next_avg_close"] = out.apply(lambda r: close_lookup.get((r["ticker"], r["next_period_id"]), np.nan), axis=1)
    out = out.dropna(subset=["next_avg_close"])
    out["next_period_return"] = out["next_avg_close"] / out["avg_close"] - 1.0
    out["label_basic"] = (out["next_period_return"] > threshold).astype(int)
    return out[["ticker", "period_id", "next_period_return", "label_basic"]]


def _safe_ratio(values: pd.Series, wanted: str) -> float:
    if len(values) == 0:
        return 0.0
    return float((values.astype(str).str.lower() == wanted).mean())


def build_period_llm_features(annotations: pd.DataFrame, assign_fn) -> pd.DataFrame:
    ann = annotations.copy()
    ann["period_id"] = ann["article_date"].apply(assign_fn)
    ann["is_direct"] = ann["relevance_to_ticker"].eq("direct").astype(float)
    ann["is_positive"] = ann["sentiment"].eq("positive").astype(float)
    ann["is_negative"] = ann["sentiment"].eq("negative").astype(float)
    ann["weighted_sentiment"] = ann["sentiment_score"] * ann["importance_score"] * ann["reasoning_confidence"] / 25.0

    group = ann.groupby(["ticker", "period_id"], sort=True)
    out = group.size().rename("llm_material_count").reset_index()
    out = out.merge(group["is_direct"].sum().rename("llm_direct_material_count").reset_index(), on=["ticker", "period_id"])
    out = out.merge(group["is_direct"].mean().rename("llm_direct_ratio").reset_index(), on=["ticker", "period_id"])
    out = out.merge(group["is_positive"].mean().rename("llm_positive_ratio").reset_index(), on=["ticker", "period_id"])
    out = out.merge(group["is_negative"].mean().rename("llm_negative_ratio").reset_index(), on=["ticker", "period_id"])
    out = out.merge(group["weighted_sentiment"].mean().rename("llm_weighted_sentiment_mean").reset_index(), on=["ticker", "period_id"])

    for source, prefix in [
        ("importance_score", "llm_importance"),
        ("information_magnitude_score", "llm_magnitude"),
        ("uncertainty_score", "llm_uncertainty"),
        ("novelty_hint_score", "llm_novelty"),
        ("reasoning_confidence", "llm_confidence"),
    ]:
        out = out.merge(group[source].mean().rename(f"{prefix}_mean").reset_index(), on=["ticker", "period_id"])
        if source in {"importance_score", "information_magnitude_score"}:
            out = out.merge(group[source].max().rename(f"{prefix}_max").reset_index(), on=["ticker", "period_id"])

    for event in sorted(MATERIAL_EVENTS):
        event_counts = group["event_type"].apply(lambda s, e=event: int((s.astype(str).str.lower() == e).sum())).rename(f"llm_{event}_count").reset_index()
        out = out.merge(event_counts, on=["ticker", "period_id"])

    return out


def add_llm_lags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values(["ticker", "period_id"]).copy()
    llm_cols = [c for c in out.columns if c.startswith("llm_")]
    lagged = out.groupby("ticker", sort=False)[llm_cols].shift(1).fillna(0.0)
    lagged.columns = [f"{c}_lag1" for c in lagged.columns]
    return pd.concat([out, lagged], axis=1)


def build_dataset(unit: str, threshold: float, relevance_variant: str) -> tuple[pd.DataFrame, list[str], list[str], dict[str, int]]:
    assign_fn, next_fn = make_period_funcs(unit)
    prices = load_prices()
    annotations = load_material_annotations(relevance_variant)
    tech = build_period_technical(prices, assign_fn)
    labels = build_threshold_labels(tech, next_fn, threshold)
    llm = build_period_llm_features(annotations, assign_fn)

    merged = tech.merge(labels, on=["ticker", "period_id"], how="inner")
    merged = merged.merge(llm, on=["ticker", "period_id"], how="left")
    llm_cols = [c for c in merged.columns if c.startswith("llm_")]
    for col in llm_cols:
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)
    merged = add_llm_lags(merged)
    llm_cols = [c for c in merged.columns if c.startswith("llm_")]
    merged = merged.dropna(subset=["label_basic"])

    counts = {
        "n_samples": int(len(merged)),
        "n_periods": int(merged["period_id"].nunique()),
        "llm_nonzero_rows": int((merged[[c for c in llm_cols if c == "llm_material_count"]].sum(axis=1) > 0).sum()) if "llm_material_count" in llm_cols else 0,
        "annotations": int(len(annotations)),
    }
    return merged, TECH_COLS, llm_cols, counts


def evaluate_unit(unit: str, threshold: float, relevance_variant: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    merged, tech_cols, llm_cols, counts = build_dataset(unit, threshold, relevance_variant)
    configs = {
        "Config_A": tech_cols,
        "Config_LLM": llm_cols,
        "Config_Hybrid": tech_cols + llm_cols,
    }
    train_df, test_df = _period_split(merged)
    result_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    for config_name, cols in configs.items():
        avail = [c for c in cols if c in train_df.columns]
        numeric_avail = train_df[avail].select_dtypes(include=[np.number]).columns.tolist()
        usable = [c for c in numeric_avail if not train_df[c].isna().all()]
        if not usable:
            continue
        imp, _ = fit_imputer(train_df, usable)
        X_tr, y_tr = prepare_features(train_df, usable, imputer=imp)
        X_te, y_te = prepare_features(test_df, usable, imputer=imp)
        common = [c for c in X_tr.columns if c in X_te.columns]
        X_tr, X_te = X_tr[common], X_te[common]
        if y_tr.nunique() < 2 or y_te.nunique() < 2:
            continue
        for model_name, model in build_ml_models(y_tr).items():
            model.fit(X_tr, y_tr)
            res = evaluate_model(model, X_te, y_te, model_name, config_name)
            res.update(
                {
                    "relevance_variant": relevance_variant,
                    "unit": unit,
                    "threshold": threshold,
                    "n_samples": counts["n_samples"],
                    "n_periods": counts["n_periods"],
                    "test_samples": len(X_te),
                    "n_features": len(common),
                    "llm_nonzero_rows": counts["llm_nonzero_rows"],
                    "annotations": counts["annotations"],
                    "positive_rate_test": float(y_te.mean()),
                }
            )
            result_rows.append(res)
            preds = model.predict(X_te)
            for idx, y, pred in zip(X_te.index, y_te, preds):
                pred_rows.append(
                    {
                        "relevance_variant": relevance_variant,
                        "unit": unit,
                        "model": model_name,
                        "config": config_name,
                        "ticker": str(test_df.loc[idx, "ticker"]),
                        "period_id": str(test_df.loc[idx, "period_id"]),
                        "y_true": int(y),
                        "y_pred": int(pred),
                    }
                )
    return pd.DataFrame(result_rows), pd.DataFrame(pred_rows)


def midp_mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    exact = min(1.0, float(2 * binom.cdf(k, n, 0.5)))
    return max(0.0, min(1.0, exact - float(binom.pmf(k, n, 0.5))))


def build_stats(results: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, grp in preds.groupby(["relevance_variant", "unit", "model"], sort=True):
        wide = grp.pivot_table(index=["ticker", "period_id", "y_true"], columns="config", values="y_pred", aggfunc="first").reset_index()
        if not {"Config_A", "Config_Hybrid"}.issubset(wide.columns):
            continue
        y = wide["y_true"].astype(int).to_numpy()
        pa = wide["Config_A"].astype(int).to_numpy()
        ph = wide["Config_Hybrid"].astype(int).to_numpy()
        b = int(((pa == y) & (ph != y)).sum())
        c = int(((pa != y) & (ph == y)).sum())
        relevance_variant, unit, model = key
        rsub = results[
            results["relevance_variant"].eq(relevance_variant)
            & results["unit"].eq(unit)
            & results["model"].eq(model)
        ]
        a = rsub[rsub["config"].eq("Config_A")]
        h = rsub[rsub["config"].eq("Config_Hybrid")]
        if a.empty or h.empty:
            continue
        rows.append(
            {
                "relevance_variant": relevance_variant,
                "unit": unit,
                "model": model,
                "n_test": int(a["test_samples"].iloc[0]),
                "ba_a": float(a["balanced_accuracy"].iloc[0]),
                "ba_hybrid": float(h["balanced_accuracy"].iloc[0]),
                "delta_hybrid_minus_a": float(h["balanced_accuracy"].iloc[0] - a["balanced_accuracy"].iloc[0]),
                "b": b,
                "c": c,
                "n_discordant": b + c,
                "p_mid": midp_mcnemar(b, c),
            }
        )
    return pd.DataFrame(rows)


def write_summary(results: pd.DataFrame, stats: pd.DataFrame) -> None:
    lines = [
        "# Period-level LLM material-event hybrid experiment",
        "",
        f"- universe: original VN30 ({len(VN30)} tickers)",
        f"- units: {', '.join(UNITS)}",
        f"- threshold: next_period_return > {THRESHOLD:.2%}",
        f"- annotation_source: `{ANNOTATION_PATH}`",
        "- Config_A: technical indicators only",
        "- Config_LLM: period-aggregated LLM material-event features only",
        "- Config_Hybrid: technical + LLM material-event features",
        "",
    ]
    if not stats.empty:
        lines += [
            "## Hybrid vs Technical deltas",
            "",
            "```text",
            stats.sort_values("delta_hybrid_minus_a", ascending=False).round(4).to_string(index=False),
            "```",
            "",
        ]
    if not results.empty:
        pivot = results.pivot_table(index=["relevance_variant", "unit", "model"], columns="config", values="balanced_accuracy").reset_index()
        if {"Config_A", "Config_Hybrid"}.issubset(pivot.columns):
            pivot["delta_hybrid_minus_A"] = pivot["Config_Hybrid"] - pivot["Config_A"]
        lines += [
            "## Balanced accuracy table",
            "",
            "```text",
            pivot.sort_values("delta_hybrid_minus_A", ascending=False).round(4).to_string(index=False),
            "```",
            "",
        ]
        meta_cols = ["relevance_variant", "unit", "n_samples", "n_periods", "test_samples", "positive_rate_test", "llm_nonzero_rows", "annotations"]
        meta = results[meta_cols].drop_duplicates().sort_values(["relevance_variant", "unit"])
        lines += [
            "## Dataset coverage",
            "",
            "```text",
            meta.round(4).to_string(index=False),
            "```",
            "",
        ]
    Path(f"{OUT_PREFIX}_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    Path("reports").mkdir(exist_ok=True)
    all_results = []
    all_preds = []
    for relevance_variant in RELEVANCE_VARIANTS:
        for unit in UNITS:
            res, pred = evaluate_unit(unit, THRESHOLD, relevance_variant)
            all_results.append(res)
            all_preds.append(pred)
            print(f"done relevance={relevance_variant} unit={unit} results={len(res)} predictions={len(pred)}", flush=True)
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
