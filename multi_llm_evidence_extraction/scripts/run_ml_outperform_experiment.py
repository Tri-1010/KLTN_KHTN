from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, REPORT_DIR, ROOT, ensure_dirs, markdown_table

TARGETS = OUTPUT_DIR / "outperform_targets.csv"
SEM = OUTPUT_DIR / "semantic_features_daily.csv"
TECH = ROOT / "data" / "features" / "technical_features.csv"
KW = ROOT / "data" / "features" / "keyword_features.csv"
PANEL = OUTPUT_DIR / "ml_panel_outperform.csv"
PRED = OUTPUT_DIR / "ml_predictions_outperform.csv"
PAIRED_DAILY = OUTPUT_DIR / "ml_paired_daily_metrics_outperform.csv"
BOOTSTRAP_DELTA = OUTPUT_DIR / "ml_bootstrap_delta_outperform.csv"
REPORT = REPORT_DIR / "ml_outperform_experiment_report.md"
HORIZON = 20
BOOTSTRAP_SEED = 42
BOOTSTRAP_SAMPLES = 2000
BOOTSTRAP_BLOCK_DATES = 20
MIN_PAIRED_DATES = 2
COMPARISONS = (
    ("A_technical", "B_technical_keyword"),
    ("A_technical", "C_technical_semantic"),
    ("A_technical", "D_all"),
    ("B_technical_keyword", "C_technical_semantic"),
    ("B_technical_keyword", "D_all"),
)
DAILY_METRICS = (
    "balanced_accuracy",
    "auc",
    "f1",
    "precision_at_10_by_date",
    "daily_rank_ic",
)
PAIRED_DAILY_COLUMNS = [
    "baseline_config", "comparison_config", "model", "fold_id", "date", "metric",
    "baseline_value", "comparison_value", "delta", "n_baseline_observations",
    "n_comparison_observations", "pair_status", "artifact_schema_version",
]
BOOTSTRAP_DELTA_COLUMNS = [
    "baseline_config", "comparison_config", "model", "metric", "mean_delta",
    "ci_lower_95", "ci_upper_95", "n_paired_dates", "n_folds", "date_start",
    "date_end", "bootstrap_samples", "bootstrap_block_dates", "rng_seed", "status",
    "artifact_schema_version",
]


def quarter_id(date: pd.Series) -> pd.Series:
    return pd.to_datetime(date).dt.to_period("Q").astype(str)


def lag_quarterly_features(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    if frame.empty:
        return frame
    work = frame.copy()
    work["quarter_id"] = work["quarter_id"].astype(str)
    period = pd.PeriodIndex(work["quarter_id"], freq="Q") + 1
    work["quarter_id"] = period.astype(str)
    rename = {col: f"{prefix}{col}" for col in work.columns if col not in {"ticker", "quarter_id"}}
    return work.rename(columns=rename)


def load_panel() -> pd.DataFrame:
    targets = pd.read_csv(TARGETS, encoding="utf-8-sig")
    targets["date"] = pd.to_datetime(targets["date"], errors="coerce")
    targets["quarter_id"] = quarter_id(targets["date"])
    panel = targets.copy()

    tech = pd.read_csv(TECH, encoding="utf-8") if TECH.exists() else pd.DataFrame()
    kw = pd.read_csv(KW, encoding="utf-8") if KW.exists() else pd.DataFrame()
    tech = lag_quarterly_features(tech, "tech_lag1q__") if not tech.empty else tech
    kw = lag_quarterly_features(kw, "kw_lag1q__") if not kw.empty else kw
    if not tech.empty:
        panel = panel.merge(tech, on=["ticker", "quarter_id"], how="left")
    if not kw.empty:
        panel = panel.merge(kw, on=["ticker", "quarter_id"], how="left")

    sem = pd.read_csv(SEM, encoding="utf-8-sig") if SEM.exists() else pd.DataFrame()
    if not sem.empty:
        sem["date"] = pd.to_datetime(sem["date"], errors="coerce")
        sem = sem.drop(columns=["artifact_schema_version"], errors="ignore")
        panel = panel.merge(sem, on=["ticker", "date"], how="left")
    panel["artifact_schema_version"] = "outperform_ml_panel_v2"
    return panel


def cols_for(df: pd.DataFrame, kind: str) -> list[str]:
    exclude = {
        "ticker", "date", "quarter_id", "stock_return_T20", "market_return_T20",
        "VNINDEX_return_T20", "excess_return_T20", "label_outperform_T20",
        "artifact_schema_version",
    }
    numeric = [col for col in df.columns if col not in exclude and pd.api.types.is_numeric_dtype(df[col])]
    tech = [col for col in numeric if col.startswith("tech_lag1q__")]
    keyword = [col for col in numeric if col.startswith("kw_lag1q__")]
    semantic = [col for col in numeric if col not in set(tech + keyword)]
    if kind == "A_technical":
        return tech
    if kind == "B_technical_keyword":
        return tech + keyword
    if kind == "C_technical_semantic":
        return tech + semantic
    return tech + keyword + semantic


def expanding_purged_splits(dates: pd.Series, n_splits: int = 3, purge: int = HORIZON) -> list[tuple[np.ndarray, np.ndarray, dict[str, object]]]:
    unique = np.array(sorted(pd.to_datetime(dates.dropna()).unique()))
    minimum_train = max(60, purge * 2)
    available = len(unique) - minimum_train - purge
    if available < n_splits:
        return []
    block = max(1, available // n_splits)
    output = []
    for fold in range(n_splits):
        test_start_idx = minimum_train + purge + fold * block
        test_end_idx = len(unique) if fold == n_splits - 1 else min(len(unique), test_start_idx + block)
        if test_start_idx >= len(unique) or test_end_idx <= test_start_idx:
            continue
        train_end_idx = test_start_idx - purge
        train_dates = unique[:train_end_idx]
        test_dates = unique[test_start_idx:test_end_idx]
        train_idx = dates.isin(train_dates).to_numpy().nonzero()[0]
        test_idx = dates.isin(test_dates).to_numpy().nonzero()[0]
        output.append((train_idx, test_idx, {
            "fold_id": fold + 1,
            "train_start": pd.Timestamp(train_dates[0]),
            "train_end": pd.Timestamp(train_dates[-1]),
            "test_start": pd.Timestamp(test_dates[0]),
            "test_end": pd.Timestamp(test_dates[-1]),
            "purge_trading_days": purge,
        }))
    return output


def precision_at_k_by_date(frame: pd.DataFrame, k: int = 10) -> float:
    values = []
    for _, group in frame.groupby("date"):
        selected = group.nlargest(min(k, len(group)), "pred_proba_outperform")
        if not selected.empty:
            values.append(float(selected["label_outperform_T20"].mean()))
    return float(np.mean(values)) if values else float("nan")


def daily_rank_ic(frame: pd.DataFrame) -> float:
    values = []
    for _, group in frame.groupby("date"):
        if len(group) >= 3 and group["pred_proba_outperform"].nunique() > 1:
            values.append(group["pred_proba_outperform"].corr(group["excess_return_T20"], method="spearman"))
    clean = [value for value in values if pd.notna(value)]
    return float(np.mean(clean)) if clean else float("nan")


def available_fold_features(train: pd.DataFrame, features: list[str]) -> list[str]:
    return [feature for feature in features if train[feature].notna().any()]



PRED_COLUMNS = [
    "ticker", "date", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20",
    "label_outperform_T20", "config", "model", "pred_proba_outperform", "pred_label",
    "fold_id", "train_start", "train_end", "test_start", "test_end", "purge_trading_days",
    "artifact_schema_version",
]


def _daily_metric(frame: pd.DataFrame, metric: str) -> float:
    y = frame["label_outperform_T20"].astype(int)
    proba = pd.to_numeric(frame["pred_proba_outperform"], errors="coerce")
    predicted = (proba >= 0.5).astype(int)
    if metric == "balanced_accuracy":
        return float(balanced_accuracy_score(y, predicted)) if y.nunique() == 2 else float("nan")
    if metric == "auc":
        return float(roc_auc_score(y, proba)) if y.nunique() == 2 else float("nan")
    if metric == "f1":
        return float(f1_score(y, predicted, zero_division=0))
    if metric == "precision_at_10_by_date":
        return float(frame.assign(pred_proba_outperform=proba).nlargest(min(10, len(frame)), "pred_proba_outperform")["label_outperform_T20"].mean())
    if len(frame) >= 3 and proba.nunique() > 1:
        return float(proba.corr(pd.to_numeric(frame["excess_return_T20"], errors="coerce"), method="spearman"))
    return float("nan")


def build_paired_daily_metrics(pred: pd.DataFrame) -> pd.DataFrame:
    required = {"ticker", "date", "fold_id", "config", "model", "label_outperform_T20", "pred_proba_outperform", "excess_return_T20"}
    if pred.empty or not required.issubset(pred.columns):
        return pd.DataFrame(columns=PAIRED_DAILY_COLUMNS)
    rows = []
    for baseline, comparison in COMPARISONS:
        for model in sorted(pred["model"].dropna().unique()):
            left = pred[pred["config"].eq(baseline) & pred["model"].eq(model)]
            right = pred[pred["config"].eq(comparison) & pred["model"].eq(model)]
            merged = left.merge(right, on=["ticker", "date", "fold_id"], suffixes=("_base", "_comp"))
            for (fold_id, date), group in merged.groupby(["fold_id", "date"], sort=True):
                base = pd.DataFrame({"label_outperform_T20": group["label_outperform_T20_base"], "pred_proba_outperform": group["pred_proba_outperform_base"], "excess_return_T20": group["excess_return_T20_base"]})
                comp = pd.DataFrame({"label_outperform_T20": group["label_outperform_T20_comp"], "pred_proba_outperform": group["pred_proba_outperform_comp"], "excess_return_T20": group["excess_return_T20_comp"]})
                for metric in DAILY_METRICS:
                    base_value, comp_value = _daily_metric(base, metric), _daily_metric(comp, metric)
                    status = "paired" if pd.notna(base_value) and pd.notna(comp_value) else "metric_undefined"
                    rows.append({"baseline_config": baseline, "comparison_config": comparison, "model": model, "fold_id": fold_id, "date": date, "metric": metric, "baseline_value": base_value, "comparison_value": comp_value, "delta": comp_value - base_value if status == "paired" else np.nan, "n_baseline_observations": len(base), "n_comparison_observations": len(comp), "pair_status": status, "artifact_schema_version": "outperform_ml_paired_daily_v1"})
    return pd.DataFrame(rows, columns=PAIRED_DAILY_COLUMNS)


def _circular_block_means(values: np.ndarray, samples: int, block_dates: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = len(values)
    block = max(1, min(block_dates, n))
    means = np.empty(samples, dtype=float)
    blocks_needed = int(np.ceil(n / block))
    offsets = np.arange(block)
    for index in range(samples):
        starts = rng.integers(0, n, size=blocks_needed)
        sampled = np.concatenate([values[(start + offsets) % n] for start in starts])[:n]
        means[index] = sampled.mean()
    return means


def build_bootstrap_deltas(paired: pd.DataFrame, samples: int = BOOTSTRAP_SAMPLES, block_dates: int = BOOTSTRAP_BLOCK_DATES, seed: int = BOOTSTRAP_SEED) -> pd.DataFrame:
    rows = []
    if paired.empty:
        return pd.DataFrame(columns=BOOTSTRAP_DELTA_COLUMNS)
    keys = ["baseline_config", "comparison_config", "model", "metric"]
    for key, group in paired.groupby(keys, sort=True):
        valid = group[group["pair_status"].eq("paired")].dropna(subset=["delta"]).sort_values("date")
        values = valid["delta"].to_numpy(dtype=float)
        status = "ok" if len(values) >= MIN_PAIRED_DATES else "insufficient_paired_dates"
        ci_low = ci_high = np.nan
        if status == "ok":
            draws = _circular_block_means(values, samples, block_dates, seed)
            ci_low, ci_high = np.percentile(draws, [2.5, 97.5])
        rows.append({**dict(zip(keys, key)), "mean_delta": float(values.mean()) if len(values) else np.nan, "ci_lower_95": ci_low, "ci_upper_95": ci_high, "n_paired_dates": len(values), "n_folds": int(valid["fold_id"].nunique()), "date_start": valid["date"].min() if len(valid) else "", "date_end": valid["date"].max() if len(valid) else "", "bootstrap_samples": samples, "bootstrap_block_dates": block_dates, "rng_seed": seed, "status": status, "artifact_schema_version": "outperform_ml_bootstrap_delta_v1"})
    return pd.DataFrame(rows, columns=BOOTSTRAP_DELTA_COLUMNS)


def write_robustness_artifacts(pred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    paired = build_paired_daily_metrics(pred)
    bootstrap = build_bootstrap_deltas(paired)
    paired.to_csv(PAIRED_DAILY, index=False, encoding="utf-8-sig")
    bootstrap.to_csv(BOOTSTRAP_DELTA, index=False, encoding="utf-8-sig")
    return paired, bootstrap

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast-models", action="store_true")
    args = parser.parse_args()
    ensure_dirs()
    if not TARGETS.exists():
        raise FileNotFoundError("Run build_outperform_targets.py first")
    panel = load_panel()
    panel.to_csv(PANEL, index=False, encoding="utf-8-sig")
    work = panel.dropna(subset=["label_outperform_T20", "date"]).sort_values("date").reset_index(drop=True)
    splits = expanding_purged_splits(work["date"])
    if work.empty or work["label_outperform_T20"].nunique() < 2 or not splits:
        REPORT.write_text("# ML outperform experiment report\n\nInsufficient variation/dates for purged walk-forward evaluation.\n", encoding="utf-8")
        pd.DataFrame(columns=PRED_COLUMNS).to_csv(PRED, index=False, encoding="utf-8-sig")
        write_robustness_artifacts(pd.DataFrame(columns=PRED_COLUMNS))
        return 0

    models = {
        "LogisticRegression": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced")),
        "RandomForest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=80 if args.fast_models else 200, random_state=42, class_weight="balanced")),
    }
    rows = []
    predictions = []
    for config in ["A_technical", "B_technical_keyword", "C_technical_semantic", "D_all"]:
        features = cols_for(work, config)
        if not features:
            continue
        for name, model in models.items():
            for train_idx, test_idx, metadata in splits:
                train = work.iloc[train_idx]
                test = work.iloc[test_idx]
                fold_features = available_fold_features(train, features)
                y_train = train["label_outperform_T20"].astype(int)
                y_test = test["label_outperform_T20"].astype(int)
                if not fold_features or y_train.nunique() < 2 or y_test.nunique() < 2:
                    continue
                model.fit(train[fold_features], y_train)
                proba = model.predict_proba(test[fold_features])[:, 1]
                predicted = (proba >= 0.5).astype(int)
                tmp = test[["ticker", "date", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20", "label_outperform_T20"]].copy()
                tmp["config"] = config
                tmp["model"] = name
                tmp["pred_proba_outperform"] = proba
                tmp["pred_label"] = predicted
                for key, value in metadata.items():
                    tmp[key] = value
                tmp["artifact_schema_version"] = "outperform_ml_predictions_v2"
                predictions.append(tmp)
                try:
                    auc = roc_auc_score(y_test, proba)
                except ValueError:
                    auc = float("nan")
                rows.append({
                    "config": config, "model": name, **metadata, "n_features": len(fold_features),
                    "n_train": len(train), "n_test": len(test),
                    "balanced_accuracy": balanced_accuracy_score(y_test, predicted),
                    "auc": auc, "f1": f1_score(y_test, predicted, zero_division=0),
                    "precision_at_10_by_date": precision_at_k_by_date(tmp, 10),
                    "daily_rank_ic": daily_rank_ic(tmp),
                    "confusion_matrix": confusion_matrix(y_test, predicted).tolist(),
                })
    pred = pd.concat(predictions, ignore_index=True) if predictions else pd.DataFrame()
    pred = pred.reindex(columns=PRED_COLUMNS)
    pred.to_csv(PRED, index=False, encoding="utf-8-sig")
    paired_daily, bootstrap_delta = write_robustness_artifacts(pred)
    result = pd.DataFrame(rows)
    lines = ["# ML outperform experiment report", "", "Purged expanding walk-forward only; all predictions are out-of-sample. Results remain exploratory, not alpha claims.", ""]
    if result.empty:
        lines.append("No model results generated.")
    else:
        lines += ["## Fold metrics", "", markdown_table(result.round(4)), ""]
        summary = result.groupby(["config", "model"], as_index=False)[["balanced_accuracy", "auc", "f1", "precision_at_10_by_date", "daily_rank_ic"]].agg(["mean", "std"])
        lines += ["## Walk-forward summary", "", markdown_table(summary.round(4)), ""]
    lines += ["## Paired daily config deltas", "", markdown_table(paired_daily.round(4)) if not paired_daily.empty else "No paired daily metrics generated.", ""]
    lines += ["## Date-block bootstrap config deltas", "", markdown_table(bootstrap_delta.round(4)) if not bootstrap_delta.empty else "No bootstrap deltas generated.", "", "Circular date-block bootstrap preserves local date dependence; intervals remain exploratory.", ""]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {PANEL}")
    print(f"saved {PRED}")
    print(f"saved {PAIRED_DAILY}")
    print(f"saved {BOOTSTRAP_DELTA}")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
