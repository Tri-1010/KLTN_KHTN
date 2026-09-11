from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, f1_score, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SCRIPT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path: sys.path.insert(0, str(SCRIPT_DIR))
from common import STUDY_DIR, markdown_table, resolve_scoped_path, sha256_file, utc_now, validate_safe_identifier
from build_harmonized_comparison import SPEC_PATH, load_harmonized_spec

CONFIGS = ("A_technical", "E_technical_coverage", "B_technical_coverage_keyword", "C_technical_coverage_semantic", "D_technical_coverage_keyword_semantic")
MODELS = ("LogisticRegression", "RandomForest")
METRICS = ("balanced_accuracy", "auc", "f1", "brier", "log_loss", "precision_at_5", "precision_at_10", "rank_ic")


def json_value(value: Any) -> Any:
    if isinstance(value, (np.floating, float)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    return value


def repository_relative_path(path: Path) -> str:
    return path.resolve().relative_to(REPOSITORY_ROOT.resolve()).as_posix()


def portable_manifest_paths(value: Any) -> Any:
    if isinstance(value, dict):
        output = {key: portable_manifest_paths(item) for key, item in value.items()}
        path = output.get("path")
        if isinstance(path, str):
            candidate = Path(path)
            if candidate.is_absolute():
                output["path"] = repository_relative_path(candidate)
        return output
    if isinstance(value, list):
        return [portable_manifest_paths(item) for item in value]
    return value


def load_and_validate_build_manifest(output_dir: Path, run_id: str, mode: str) -> tuple[dict[str, Any], Path]:
    path = output_dir / "harmonized_build_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"harmonized build manifest missing: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("invalid harmonized build manifest") from exc
    if manifest.get("status") != "completed" or manifest.get("run_id") != run_id or manifest.get("mode") != mode:
        raise ValueError("harmonized build manifest run/mode/status mismatch")
    if manifest.get("protocol_sha256") != sha256_file(SPEC_PATH):
        raise ValueError("harmonized build protocol hash mismatch")
    expected_sources = {
        "sample", "consensus", "prices", "benchmark", "technical", "targets", "target_manifest",
    }
    expected_artifacts = {
        "harmonized_article_spine.csv", "harmonized_features_daily.csv",
        "harmonized_feature_manifest.csv", "harmonized_row_manifest.csv",
        "harmonized_coverage_audit.csv", "harmonized_panel.csv",
    }
    source_entries = manifest.get("sources")
    artifact_entries = manifest.get("artifacts")
    if not isinstance(source_entries, list) or not source_entries:
        raise ValueError("harmonized build manifest missing sources")
    if not isinstance(artifact_entries, list) or not artifact_entries:
        raise ValueError("harmonized build manifest missing artifacts")
    source_names = [str(entry.get("name", "")) for entry in source_entries]
    if len(source_names) != len(set(source_names)) or set(source_names) != expected_sources:
        raise ValueError("harmonized build source membership mismatch")
    artifact_names = [Path(str(entry.get("path", ""))).name for entry in artifact_entries]
    if len(artifact_names) != len(set(artifact_names)) or set(artifact_names) != expected_artifacts:
        raise ValueError("harmonized build artifact membership mismatch")
    spec = load_harmonized_spec(SPEC_PATH)
    expected_source_paths = {
        "prices": REPOSITORY_ROOT / spec["input_paths"]["prices"],
        "benchmark": REPOSITORY_ROOT / spec["input_paths"]["benchmark"],
        "technical": REPOSITORY_ROOT / spec["input_paths"]["technical"],
        "targets": output_dir / "harmonized_outperform_targets.csv",
        "target_manifest": output_dir / "harmonized_target_manifest.json",
    }
    if mode == "pilot":
        expected_source_paths.update({
            "sample": REPOSITORY_ROOT / spec["input_paths"]["pilot_sample"],
            "consensus": REPOSITORY_ROOT / spec["input_paths"]["pilot_consensus"],
        })
    else:
        expected_source_paths.update({
            "sample": STUDY_DIR / "data" / "sample_news_for_annotation_500_v1.csv",
            "consensus": output_dir / "pseudo_labels_consensus.csv",
        })
    for entry in source_entries:
        name = str(entry.get("name", ""))
        artifact = Path(str(entry.get("path", "")))
        if not artifact.is_absolute():
            artifact = REPOSITORY_ROOT / artifact
        if artifact.resolve() != expected_source_paths[name].resolve():
            raise ValueError(f"harmonized build source path mismatch: {name}")
        if not artifact.exists() or sha256_file(artifact) != entry.get("sha256"):
            raise ValueError(f"harmonized build source hash mismatch: {artifact}")
    for entry in artifact_entries:
        artifact = Path(str(entry.get("path", "")))
        expected_path = output_dir / artifact.name
        if artifact.resolve() != expected_path.resolve():
            raise ValueError(f"harmonized build artifact path mismatch: {artifact}")
        if not artifact.exists() or sha256_file(artifact) != entry.get("sha256"):
            raise ValueError(f"harmonized build artifact hash mismatch: {artifact}")
    return manifest, path


def target_exit_aware_splits(panel: pd.DataFrame, n_splits: int = 3) -> list[tuple[np.ndarray, np.ndarray, dict[str, Any]]]:
    work = panel.copy()
    work["date"] = pd.to_datetime(work["date"]).dt.normalize()
    work["target_exit_date"] = pd.to_datetime(work["target_exit_date"]).dt.normalize()
    dates = np.array(sorted(work["date"].dropna().unique()))
    if len(dates) < n_splits + 3: return []
    boundaries = np.array_split(dates, n_splits + 1)
    output = []
    for fold in range(n_splits):
        test_dates = boundaries[fold + 1]
        if not len(test_dates): continue
        test_start, test_end = pd.Timestamp(test_dates[0]), pd.Timestamp(test_dates[-1])
        train_mask = (work["date"] < test_start) & (work["target_exit_date"] < test_start)
        test_mask = work["date"].isin(test_dates)
        if not train_mask.any() or not test_mask.any(): continue
        train_idx, test_idx = np.flatnonzero(train_mask), np.flatnonzero(test_mask)
        meta = {"fold_id": fold + 1, "train_start": work.iloc[train_idx]["date"].min(), "train_end": work.iloc[train_idx]["date"].max(), "train_target_exit_max": work.iloc[train_idx]["target_exit_date"].max(), "test_start": test_start, "test_end": test_end}
        if meta["train_target_exit_max"] >= test_start: raise ValueError("target-exit purge failed")
        output.append((train_idx, test_idx, meta))
    return output


def available_fold_features(train: pd.DataFrame, declared: list[str]) -> tuple[list[str], list[dict[str, Any]]]:
    used, rows = [], []
    for feature in declared:
        exists = feature in train
        nonmissing = int(train[feature].notna().sum()) if exists else 0
        nonzero = int((pd.to_numeric(train[feature], errors="coerce").fillna(0) != 0).sum()) if exists else 0
        use = exists and nonmissing > 0 and pd.to_numeric(train[feature], errors="coerce").nunique(dropna=True) > 1
        if use: used.append(feature)
        rows.append({"feature": feature, "declared": True, "nonmissing_train": nonmissing, "nonzero_train": nonzero, "used": use, "drop_reason": "" if use else ("missing" if not exists else "constant_or_all_missing")})
    return used, rows


def stable_random_probability(seed: int, fold: int, ticker: str, date: Any) -> float:
    digest = hashlib.sha256(f"{seed}|{fold}|{ticker}|{pd.Timestamp(date).date()}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def _models(spec: dict[str, Any], fast: bool) -> dict[str, Any]:
    lr = spec["models"]["logistic_regression"]
    rf = spec["models"]["random_forest"]
    return {
        "LogisticRegression": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=lr["C"], max_iter=lr["max_iter"], class_weight=lr["class_weight"], random_state=lr["random_state"])),
        "RandomForest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=50 if fast else rf["n_estimators"], max_depth=rf["max_depth"], min_samples_leaf=rf["min_samples_leaf"], class_weight=rf["class_weight"], random_state=rf["random_state"], n_jobs=rf["n_jobs"])),
    }


def expected_calibration_error(y: pd.Series, probability: pd.Series, bins: int = 10) -> tuple[float, pd.DataFrame]:
    frame = pd.DataFrame({"y": y.astype(float), "p": probability.astype(float)})
    frame["bin"] = pd.cut(frame["p"], np.linspace(0, 1, bins + 1), include_lowest=True, labels=False)
    table = frame.groupby("bin", observed=False).agg(n=("y", "size"), observed=("y", "mean"), predicted=("p", "mean")).reset_index()
    table["abs_gap"] = (table["observed"] - table["predicted"]).abs()
    return float((table["abs_gap"] * table["n"] / len(frame)).sum()), table


def metric_value(frame: pd.DataFrame, metric: str, samples_per_class: int = 1) -> float:
    y = frame["label_outperform_T20"].astype(int); p = frame["pred_proba_outperform"].clip(1e-15, 1 - 1e-15); pred = (p >= .5).astype(int)
    class_minimum_met = y.value_counts().reindex([0, 1], fill_value=0).ge(samples_per_class).all()
    if metric == "balanced_accuracy": return float(balanced_accuracy_score(y, pred)) if class_minimum_met else np.nan
    if metric == "auc": return float(roc_auc_score(y, p)) if class_minimum_met else np.nan
    if metric == "f1": return float(f1_score(y, pred, zero_division=0))
    if metric == "brier": return float(brier_score_loss(y, p))
    if metric == "log_loss": return float(log_loss(y, p, labels=[0, 1]))
    if metric in {"precision_at_5", "precision_at_10"}:
        k = int(metric.rsplit("_", 1)[1])
        if len(frame) < k:
            return np.nan
        return float(frame.nlargest(k, "pred_proba_outperform")["label_outperform_T20"].mean())
    if metric == "rank_ic":
        return float(p.corr(pd.to_numeric(frame["excess_return_T20"], errors="coerce"), method="spearman")) if len(frame) >= 3 and p.nunique() > 1 else np.nan
    raise ValueError(f"unsupported metric: {metric}")


def bh_adjust(values: pd.Series) -> pd.Series:
    p = pd.to_numeric(values, errors="coerce"); valid = p.dropna().sort_values(); n = len(valid)
    if not n: return pd.Series(np.nan, index=values.index)
    adjusted = (valid * n / np.arange(1, n + 1)).iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    return adjusted.reindex(values.index)


def fold_local_block_draws(paired: pd.DataFrame, samples: int, block_dates: int, seed: int, sign_flip: bool = False) -> np.ndarray:
    rng = np.random.default_rng(seed); draws = np.zeros(samples); folds = [g.sort_values("date") for _, g in paired.groupby("fold_id")]
    for i in range(samples):
        values = []
        for group in folds:
            arr = group["improvement_delta"].to_numpy(float)
            adaptive_max = max(1, int(np.ceil(np.sqrt(len(arr)))))
            block = min(max(1, block_dates), adaptive_max)
            if sign_flip:
                for start in range(0, len(arr), block):
                    values.extend((arr[start:start + block] * rng.choice([-1, 1])).tolist())
                continue
            starts = np.arange(0, len(arr) - block + 1); chosen = []
            while len(chosen) < len(arr):
                start = int(rng.choice(starts))
                chosen.extend(arr[start:start + block].tolist())
            values.extend(chosen[:len(arr)])
        draws[i] = np.mean(values) if values else np.nan
    return draws


def bootstrap_draws_estimable(draws: np.ndarray) -> bool:
    finite = draws[np.isfinite(draws)]
    return len(finite) == len(draws) and len(finite) > 1 and np.unique(finite).size > 1


def build_paired_inference(
    pred: pd.DataFrame,
    spec: dict[str, Any],
    fast: bool,
    bootstrap_samples: int | None = None,
    permutation_samples: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    comparisons = [("P1", "B_technical_coverage_keyword", "C_technical_coverage_semantic"), ("S1", "E_technical_coverage", "B_technical_coverage_keyword"), ("S1", "E_technical_coverage", "C_technical_coverage_semantic"), ("S2", "A_technical", "E_technical_coverage")]
    daily_rows, inference = [], []
    bootstrap_samples = bootstrap_samples or (200 if fast else int(spec["inference"]["bootstrap_samples"]))
    permutation_samples = permutation_samples or (200 if fast else int(spec["inference"]["permutation_samples"]))
    seed = int(spec["inference"]["seed"]); block = int(spec["inference"]["block_dates"])
    for family, baseline, comparison in comparisons:
        for model in MODELS:
            left = pred[(pred.config == baseline) & (pred.model == model)]; right = pred[(pred.config == comparison) & (pred.model == model)]
            merged = left.merge(right, on=["ticker", "date", "fold_id", "target_exit_date"], suffixes=("_base", "_comp"), validate="one_to_one")
            for (fold, date), group in merged.groupby(["fold_id", "date"]):
                for metric in METRICS:
                    base = pd.DataFrame({"label_outperform_T20": group["label_outperform_T20_base"], "pred_proba_outperform": group["pred_proba_outperform_base"], "excess_return_T20": group["excess_return_T20_base"]})
                    comp = pd.DataFrame({"label_outperform_T20": group["label_outperform_T20_comp"], "pred_proba_outperform": group["pred_proba_outperform_comp"], "excess_return_T20": group["excess_return_T20_comp"]})
                    samples_per_class = int(spec["minimums"]["samples_per_class"])
                    a = metric_value(base, metric, samples_per_class)
                    b = metric_value(comp, metric, samples_per_class)
                    raw = b - a; improvement = -raw if spec["metrics"][metric] == "lower" else raw
                    daily_rows.append({"family": family, "baseline_config": baseline, "comparison_config": comparison, "model": model, "fold_id": fold, "date": date, "metric": metric, "baseline_value": a, "comparison_value": b, "raw_delta": raw, "improvement_delta": improvement, "status": "ok" if pd.notna(improvement) else "undefined"})
            daily = pd.DataFrame([r for r in daily_rows if r["family"] == family and r["baseline_config"] == baseline and r["comparison_config"] == comparison and r["model"] == model])
            for metric, group in daily[daily.status == "ok"].groupby("metric"):
                if group["fold_id"].nunique() != spec["minimums"]["valid_folds"] or len(group) < spec["minimums"]["paired_dates"]: status = "not_estimable"
                else: status = "ok"
                boot = fold_local_block_draws(group, bootstrap_samples, block, seed) if status == "ok" else np.array([])
                perm = fold_local_block_draws(group, permutation_samples, block, seed, True) if status == "ok" else np.array([])
                if status == "ok" and not bootstrap_draws_estimable(boot):
                    status = "not_estimable_degenerate_bootstrap"
                    boot = np.array([])
                    perm = np.array([])
                mean = group["improvement_delta"].mean() if len(group) else np.nan
                inference.append({"family": family, "baseline_config": baseline, "comparison_config": comparison, "model": model, "metric": metric, "raw_delta": group["raw_delta"].mean() if len(group) else np.nan, "improvement_delta": mean, "bootstrap_ci_low": np.percentile(boot, 2.5) if len(boot) else np.nan, "bootstrap_ci_high": np.percentile(boot, 97.5) if len(boot) else np.nan, "p_value": (np.sum(np.abs(perm) >= abs(mean)) + 1) / (len(perm) + 1) if len(perm) else np.nan, "n_paired_dates": len(group), "n_folds": group["fold_id"].nunique(), "status": status})
    inf = pd.DataFrame(inference)
    if not inf.empty: inf["p_value_bh"] = inf.groupby("family", group_keys=False)["p_value"].apply(bh_adjust)
    return pd.DataFrame(daily_rows), inf


def build_matched_topk(pred: pd.DataFrame, mode: str, cost: float, minimum_periods: int, required_folds: int = 3) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows, summary = [], []
    config_names = ("B_technical_coverage_keyword", "C_technical_coverage_semantic")
    for model in MODELS:
        for k in (5, 10):
            configs = {c: pred[(pred.config == c) & (pred.model == model)] for c in config_names}
            all_periods = set(map(tuple, configs[config_names[0]][["fold_id", "date"]].drop_duplicates().to_numpy())) | set(map(tuple, configs[config_names[1]][["fold_id", "date"]].drop_duplicates().to_numpy()))
            selected_periods = 0; last_exit = None; invalid_reason = ""; previous_weights: dict[str, dict[str, float]] = {c: {} for c in config_names}
            for fold, date in sorted(all_periods):
                pair = {c: f[(f.fold_id == fold) & (f.date == date)].copy() for c, f in configs.items()}
                left_keys = pair[config_names[0]][["ticker", "target_exit_date"]].sort_values(["ticker", "target_exit_date"]).reset_index(drop=True)
                right_keys = pair[config_names[1]][["ticker", "target_exit_date"]].sort_values(["ticker", "target_exit_date"]).reset_index(drop=True)
                if not left_keys.equals(right_keys):
                    invalid_reason = "candidate_universe_mismatch"; continue
                if len(left_keys) < k:
                    invalid_reason = "universe_below_k"; continue
                exit_values = pd.to_datetime(left_keys["target_exit_date"], errors="coerce").dropna().unique()
                if len(exit_values) != 1:
                    invalid_reason = "target_exit_mismatch"; continue
                exit_date = pd.Timestamp(exit_values[0])
                test_end = pd.to_datetime(pair[config_names[0]].get("test_end"), errors="coerce").max()
                if pd.isna(test_end) or exit_date > test_end:
                    invalid_reason = "exit_beyond_fold_test_boundary"; continue
                if last_exit is not None and pd.Timestamp(date) <= last_exit: continue
                period_returns = {}
                for config, frame in pair.items():
                    top = frame.nlargest(k, "pred_proba_outperform"); gross = top["stock_return_T20"].mean(); excess = top["excess_return_T20"].mean()
                    current_weights = {str(ticker): 1.0 / k for ticker in top["ticker"]}
                    previous = previous_weights[config]
                    turnover = 1.0 if not previous else 0.5 * sum(abs(current_weights.get(t, 0.0) - previous.get(t, 0.0)) for t in set(current_weights) | set(previous))
                    previous_weights[config] = current_weights
                    period_returns[config] = (gross - cost * turnover, excess - cost * turnover)
                    rows.append({"model": model, "k": k, "fold_id": fold, "date": date, "target_exit_date": exit_date, "config": config, "candidate_count": len(frame), "gross_return": gross, "net_return": gross - cost * turnover, "net_excess_return": excess - cost * turnover, "turnover": turnover, "status": "ok"})
                rows.append({"model": model, "k": k, "fold_id": fold, "date": date, "target_exit_date": exit_date, "config": "C_minus_B", "candidate_count": len(left_keys), "net_return": period_returns[config_names[1]][0] - period_returns[config_names[0]][0], "net_excess_return": period_returns[config_names[1]][1] - period_returns[config_names[0]][1], "status": "paired_delta"})
                selected_periods += 1; last_exit = exit_date
            selected_folds = {row["fold_id"] for row in rows if row["model"] == model and row["k"] == k and row["config"] == "C_minus_B"}
            enough_periods = selected_periods >= minimum_periods
            full_fold_coverage = len(selected_folds) == required_folds
            status = "ok" if enough_periods and full_fold_coverage else f"not_estimable_in_{mode}"
            if status == "ok":
                drop_reason = ""
            elif invalid_reason:
                drop_reason = invalid_reason
            elif not full_fold_coverage:
                drop_reason = "insufficient_fold_coverage"
            else:
                drop_reason = "insufficient_nonoverlap_periods"
            summary.append({"family": "T1", "model": model, "k": k, "periods": selected_periods, "folds": len(selected_folds), "status": status, "drop_reason": drop_reason})
    return pd.DataFrame(rows), summary


def validate_bc_prediction_alignment(pred: pd.DataFrame, required_folds: int = 3) -> None:
    key_columns = ["ticker", "date", "target_exit_date", "fold_id"]
    target_columns = ["label_outperform_T20", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20"]
    for model in MODELS:
        left = pred[(pred.config == "B_technical_coverage_keyword") & (pred.model == model)]
        right = pred[(pred.config == "C_technical_coverage_semantic") & (pred.model == model)]
        if left["fold_id"].nunique() != required_folds or right["fold_id"].nunique() != required_folds:
            raise ValueError(f"B/C require {required_folds} aligned folds for {model}")
        left_keys = left[key_columns].sort_values(key_columns).reset_index(drop=True)
        right_keys = right[key_columns].sort_values(key_columns).reset_index(drop=True)
        if not left_keys.equals(right_keys):
            raise ValueError(f"B/C prediction key mismatch for {model}")
        merged = left.merge(right, on=key_columns, suffixes=("_B", "_C"), validate="one_to_one")
        for column in target_columns:
            a = pd.to_numeric(merged[f"{column}_B"], errors="coerce").to_numpy()
            b = pd.to_numeric(merged[f"{column}_C"], errors="coerce").to_numpy()
            if not np.array_equal(a, b, equal_nan=True):
                raise ValueError(f"B/C target mismatch for {model}: {column}")


def build_topk_inference(
    topk: pd.DataFrame,
    spec: dict[str, Any],
    mode: str,
    fast: bool,
    bootstrap_samples: int | None = None,
    permutation_samples: int | None = None,
) -> pd.DataFrame:
    required = {"config", "model", "k", "fold_id", "date", "net_return", "net_excess_return"}
    if topk.empty or not required.issubset(topk.columns):
        return pd.DataFrame()
    delta = topk[topk["config"].eq("C_minus_B")].copy()
    rows = []
    bootstrap_samples = bootstrap_samples or (200 if fast else int(spec["inference"]["bootstrap_samples"]))
    permutation_samples = permutation_samples or (200 if fast else int(spec["inference"]["permutation_samples"]))
    minimum = int(spec["minimums"]["topk_periods"])
    for (model, k), group in delta.groupby(["model", "k"]):
        for metric in ("net_return", "net_excess_return"):
            paired = group[["fold_id", "date", metric]].dropna().rename(columns={metric: "improvement_delta"})
            enough_periods = len(paired) >= minimum
            full_fold_coverage = paired["fold_id"].nunique() == int(spec["minimums"]["valid_folds"])
            status = "ok" if enough_periods and full_fold_coverage else f"not_estimable_in_{mode}"
            boot = fold_local_block_draws(paired, bootstrap_samples, spec["inference"]["block_dates"], spec["inference"]["seed"]) if status == "ok" else np.array([])
            perm = fold_local_block_draws(paired, permutation_samples, spec["inference"]["block_dates"], spec["inference"]["seed"], True) if status == "ok" else np.array([])
            if status == "ok" and not bootstrap_draws_estimable(boot):
                status = "not_estimable_degenerate_bootstrap"
                boot = np.array([])
                perm = np.array([])
            mean = paired["improvement_delta"].mean() if len(paired) else np.nan
            rows.append({"family": "T1", "baseline_config": "B_technical_coverage_keyword", "comparison_config": "C_technical_coverage_semantic", "model": model, "metric": f"top{k}_{metric}", "raw_delta": mean, "improvement_delta": mean, "bootstrap_ci_low": np.percentile(boot, 2.5) if len(boot) else np.nan, "bootstrap_ci_high": np.percentile(boot, 97.5) if len(boot) else np.nan, "p_value": (np.sum(np.abs(perm) >= abs(mean)) + 1) / (len(perm) + 1) if len(perm) else np.nan, "n_paired_dates": len(paired), "n_folds": paired["fold_id"].nunique(), "status": status})
    result = pd.DataFrame(rows)
    if not result.empty:
        result["p_value_bh"] = bh_adjust(result["p_value"])
    return result


def run_models(panel: pd.DataFrame, feature_manifest: pd.DataFrame, spec: dict[str, Any], fast: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    work = panel[panel["panel_eligible"].astype(str).str.lower().isin({"true", "1"})].copy().sort_values("date").reset_index(drop=True)
    splits = target_exit_aware_splits(work, 3)
    if len(splits) != 3: raise ValueError(f"requires 3 valid folds; got {len(splits)}")
    declared = {config: feature_manifest[feature_manifest["configs"].apply(lambda value: config in json.loads(value))]["feature"].tolist() for config in CONFIGS}
    predictions, folds, fold_features, fold_metrics = [], [], [], []
    for train_idx, test_idx, meta in splits:
        train, test = work.iloc[train_idx], work.iloc[test_idx]
        folds.append({**meta, "n_train": len(train), "n_test": len(test), "status": "ok"})
        for config in CONFIGS:
            features, audit = available_fold_features(train, declared[config])
            for row in audit: fold_features.append({**meta, "config": config, **row})
            if not features or train["label_outperform_T20"].nunique() < 2: continue
            for model_name, estimator in _models(spec, fast).items():
                estimator.fit(train[features], train["label_outperform_T20"].astype(int)); probability = estimator.predict_proba(test[features])[:, 1]
                tmp = test[["ticker", "date", "target_exit_date", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20", "label_outperform_T20"]].copy()
                tmp["config"], tmp["model"], tmp["fold_id"], tmp["pred_proba_outperform"] = config, model_name, meta["fold_id"], probability
                tmp["test_end"] = meta["test_end"]
                tmp["pred_label"] = (probability >= .5).astype(int); predictions.append(tmp)
                for metric in METRICS:
                    value = metric_value(tmp, metric, int(spec["minimums"]["samples_per_class"]))
                    fold_metrics.append({"config": config, "model": model_name, "fold_id": meta["fold_id"], "metric": metric, "value": value, "status": "ok" if pd.notna(value) else "undefined"})
        prevalence = float(train["label_outperform_T20"].mean()); majority = int(prevalence >= .5)
        for baseline, probability in (("baseline_majority", float(majority)), ("baseline_prevalence", prevalence)):
            tmp = test[["ticker", "date", "target_exit_date", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20", "label_outperform_T20"]].copy(); tmp["config"] = baseline; tmp["model"] = "Baseline"; tmp["fold_id"] = meta["fold_id"]; tmp["pred_proba_outperform"] = probability; tmp["pred_label"] = int(probability >= .5); predictions.append(tmp)
        tmp = test[["ticker", "date", "target_exit_date", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20", "label_outperform_T20"]].copy(); tmp["config"] = "baseline_seeded_random"; tmp["model"] = "Baseline"; tmp["fold_id"] = meta["fold_id"]; tmp["pred_proba_outperform"] = [stable_random_probability(spec["inference"]["seed"], meta["fold_id"], r.ticker, r.date) for r in tmp.itertuples()]; tmp["pred_label"] = (tmp["pred_proba_outperform"] >= .5).astype(int); predictions.append(tmp)
    pred = pd.concat(predictions, ignore_index=True)
    validate_bc_prediction_alignment(pred, required_folds=3)
    return pred, pd.DataFrame(folds), pd.DataFrame(fold_features), pd.DataFrame(fold_metrics)


def write_report_and_manifest(output_dir: Path, report_dir: Path, mode: str, run_id: str, spec: dict[str, Any], inference: pd.DataFrame, topk_summary: list[dict[str, Any]], files: list[Path], fast: bool, build_manifest: dict[str, Any], build_manifest_path: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    protocol_hash = sha256_file(SPEC_PATH)
    claim = spec["claim_gates"][mode]
    canonical_run = (
        run_id == spec["canonical_run_id"]
        and mode == "pilot"
        and not fast
        and build_manifest.get("preregistered_input_match") is True
    )
    run_tier = "canonical" if canonical_run else "smoke" if fast else "exploratory"
    spine = pd.read_csv(output_dir / "harmonized_article_spine.csv", encoding="utf-8-sig")
    rows = pd.read_csv(output_dir / "harmonized_row_manifest.csv", encoding="utf-8-sig")
    folds = pd.read_csv(output_dir / "harmonized_fold_manifest.csv", encoding="utf-8-sig")
    coverage = pd.read_csv(output_dir / "harmonized_coverage_audit.csv", encoding="utf-8-sig")
    eligible_mask = spine["analysis_eligible"].astype(str).str.lower().isin({"true", "1"})
    mapped_mask = spine["mapping_status"].eq("ok")
    attrition = {
        "sampled_articles": len(spine), "joined_articles": int(spine["annotation_status"].eq("annotated").sum()),
        "eligible_articles": int(eligible_mask.sum()), "mapped_eligible_articles": int((eligible_mask & mapped_mask).sum()),
        "analytic_spine_articles": int(spine["analytic_spine_member"].astype(str).str.lower().isin({"true", "1"}).sum()),
        "panel_target_available_rows": int(rows["target_status"].eq("ok").sum()),
        "panel_eligible_rows": int(rows["panel_eligible"].astype(str).str.lower().isin({"true", "1"}).sum()),
    }
    coverage_audit_pass = bool(coverage["coverage_equal_B_C"].astype(str).str.lower().isin({"true", "1"}).all())
    fold_audit_pass = bool((pd.to_datetime(folds["train_target_exit_max"]) < pd.to_datetime(folds["test_start"])).all() and len(folds) == 3)
    inference["coverage_audit_pass"] = coverage_audit_pass
    inference["fold_audit_pass"] = fold_audit_pass
    primary = spec["primary"]
    primary_mask = (
        inference["family"].eq(primary["family"])
        & inference["baseline_config"].eq(primary["baseline_config"])
        & inference["comparison_config"].eq(primary["comparison_config"])
        & inference["model"].eq(primary["model"])
        & inference["metric"].eq(primary["metric"])
    )
    if int(primary_mask.sum()) != 1:
        raise ValueError(f"expected exactly one preregistered primary record; got {int(primary_mask.sum())}")
    inference["primary_gate_pass"] = (
        primary_mask & inference["status"].eq("ok")
        & pd.to_numeric(inference["p_value_bh"], errors="coerce").le(float(spec["alpha"]))
        & pd.to_numeric(inference["bootstrap_ci_low"], errors="coerce").gt(0)
        & coverage_audit_pass & fold_audit_pass
    )
    primary_gate_pass = bool(inference.loc[primary_mask, "primary_gate_pass"].iloc[0])
    inference.to_csv(output_dir / "harmonized_inference.csv", index=False, encoding="utf-8-sig")
    lines = ["# Harmonized keyword–semantic comparison", "", f"- Run: `{run_id}`", f"- Mode: `{mode}`", f"- Protocol SHA256: `{protocol_hash}`", f"- Run tier: `{run_tier}`", f"- Claim level: `{claim}`", f"- Coverage audit pass: `{coverage_audit_pass}`", f"- Fold audit pass: `{fold_audit_pass}`", "", "## Sample selection and spine attrition", "", markdown_table(pd.Series(attrition, name="count")), "", "## Target exit and fold audit", "", markdown_table(folds), "", "## Coverage equality audit", "", markdown_table(coverage), "", "## P1/S1/S2 paired inference", "", markdown_table(inference), "", "## Matched Top-K T1", "", markdown_table(topk_summary), "", "## Selection and provenance limitation", "", "Pilot sample was stratified using keyword-derived buckets. Canonical annotation manifests are legacy-reconstructed and represent three runs from two model families; this limits provenance and blocks full-corpus or superiority claims.", "", "## Allowed claims", "", "Only out-of-sample deltas on common stratified article spine. Pilot/sample500 cannot support full-corpus superiority, alpha, ground-truth, or causal claims.", "", "## Replication requirement", "", "Independent larger and full-corpus replication with same preregistered protocol is required."]
    report = report_dir / "harmonized_comparison_report.md"; report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    files.append(report)
    primary_record = inference.loc[primary_mask].iloc[0]
    canonical_summary = {
        "artifact_schema_version": "harmonized_canonical_summary_v1",
        "study_id": spec["study_id"],
        "protocol_version": spec["protocol_version"],
        "protocol_sha256": protocol_hash,
        "run_id": run_id,
        "mode": mode,
        "run_tier": run_tier,
        "claim_level": claim,
        "primary": {
            **primary,
            "status": primary_record["status"],
            "improvement_delta": json_value(primary_record["improvement_delta"]),
            "bootstrap_ci_low": json_value(primary_record["bootstrap_ci_low"]),
            "bootstrap_ci_high": json_value(primary_record["bootstrap_ci_high"]),
            "p_value": json_value(primary_record["p_value"]),
            "p_value_bh": json_value(primary_record["p_value_bh"]),
            "n_paired_dates": int(primary_record["n_paired_dates"]),
            "n_folds": int(primary_record["n_folds"]),
            "gate_pass": primary_gate_pass,
        },
        "audits": {"coverage": coverage_audit_pass, "folds": fold_audit_pass},
        "attrition": attrition,
        "topk": topk_summary,
        "limitations": [
            "common_stratified_article_spine_only",
            "semantic_labels_are_pseudo_labels",
            "topk_is_exploratory_not_alpha",
            "no_causal_or_investment_advice_claim",
        ],
    }
    summary_path = output_dir / "canonical_summary.json"
    summary_path.write_text(json.dumps(canonical_summary, ensure_ascii=False, indent=2, default=str, allow_nan=False), encoding="utf-8")
    files.append(summary_path)
    code_paths = [
        SCRIPT_DIR / "build_harmonized_comparison.py",
        SCRIPT_DIR / "run_harmonized_comparison.py",
        SCRIPT_DIR / "build_outperform_targets.py",
        SCRIPT_DIR / "common.py",
        REPOSITORY_ROOT / "pipeline" / "task8_keywords.py",
        REPOSITORY_ROOT / "pipeline" / "task9_kw_features.py",
    ]
    input_paths = [SPEC_PATH, build_manifest_path, output_dir / "harmonized_article_spine.csv", output_dir / "harmonized_panel.csv", output_dir / "harmonized_feature_manifest.csv"]
    manifest = {"artifact_schema_version": "harmonized_comparison_manifest_v1", "generated_at_utc": utc_now(), "study_id": spec["study_id"], "protocol_version": spec["protocol_version"], "protocol_sha256": protocol_hash, "run_id": run_id, "mode": mode, "seed": spec["inference"]["seed"], "run_tier": run_tier, "status": "completed", "claim_level": claim, "coverage_audit_pass": coverage_audit_pass, "fold_audit_pass": fold_audit_pass, "primary_gate_pass": primary_gate_pass, "primary_gate_any": primary_gate_pass, "thesis_evidence_gate": bool(canonical_run and primary_gate_pass), "preregistered_input_match": bool(build_manifest.get("preregistered_input_match")), "build_manifest_sha256": sha256_file(build_manifest_path), "source_inputs": build_manifest.get("sources", []), "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=STUDY_DIR, capture_output=True, text=True).stdout.strip(), "attrition": attrition, "code": [{"path": repository_relative_path(p), "sha256": sha256_file(p)} for p in code_paths], "inputs": [{"path": repository_relative_path(p), "sha256": sha256_file(p)} for p in input_paths], "outputs": [{"path": repository_relative_path(p), "sha256": sha256_file(p)} for p in files if p.exists()]}
    manifest = portable_manifest_paths(manifest)
    (output_dir / "harmonized_comparison_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--mode", choices=["pilot", "sample500"], required=True); parser.add_argument("--run-id", required=True); parser.add_argument("--output-dir", type=Path); parser.add_argument("--fast", action="store_true"); parser.add_argument("--bootstrap-samples", type=int); parser.add_argument("--permutation-samples", type=int); args = parser.parse_args()
    run_id = validate_safe_identifier(args.run_id, "run_id")
    spec = load_harmonized_spec(); output_dir = resolve_scoped_path(STUDY_DIR / "outputs" / "harmonized", run_id); report_dir = resolve_scoped_path(STUDY_DIR / "reports" / "harmonized", run_id)
    if args.output_dir is not None and args.output_dir.resolve() != output_dir:
        raise ValueError("harmonized output_dir must equal outputs/harmonized/<run-id>")
    if run_id == spec["canonical_run_id"] and args.fast:
        raise ValueError("canonical run_id forbids --fast")
    if run_id == spec["canonical_run_id"] and (args.bootstrap_samples is not None or args.permutation_samples is not None):
        raise ValueError("canonical run_id forbids inference sample overrides")
    if (output_dir / "harmonized_comparison_manifest.json").exists():
        raise FileExistsError(f"harmonized run is immutable after completion: {output_dir}")
    build_manifest, build_manifest_path = load_and_validate_build_manifest(output_dir, run_id, args.mode)
    panel = pd.read_csv(output_dir / "harmonized_panel.csv", encoding="utf-8-sig"); manifest = pd.read_csv(output_dir / "harmonized_feature_manifest.csv", encoding="utf-8-sig")
    for col in ("date", "target_exit_date"): panel[col] = pd.to_datetime(panel[col], errors="coerce")
    pred, folds, fold_features, metrics = run_models(panel, manifest, spec, args.fast)
    paired, inference = build_paired_inference(
        pred, spec, args.fast, args.bootstrap_samples, args.permutation_samples
    ); topk, topk_summary = build_matched_topk(pred, args.mode, spec["topk"]["transaction_cost"], spec["minimums"]["topk_periods"])
    topk_inference = build_topk_inference(topk, spec, args.mode, args.fast, args.bootstrap_samples, args.permutation_samples)
    inference = pd.concat([inference, topk_inference], ignore_index=True, sort=False)
    calibration = []
    for key, group in pred.groupby(["config", "model", "fold_id"]):
        ece, table = expected_calibration_error(group["label_outperform_T20"], group["pred_proba_outperform"])
        for row in table.to_dict("records"): calibration.append({"config": key[0], "model": key[1], "fold_id": key[2], "ece": ece, **row})
    artifacts = {"harmonized_fold_manifest.csv": folds, "harmonized_fold_feature_manifest.csv": fold_features, "harmonized_predictions.csv": pred, "harmonized_fold_metrics.csv": metrics, "harmonized_calibration.csv": pd.DataFrame(calibration), "harmonized_paired_daily_deltas.csv": paired, "harmonized_inference.csv": inference, "harmonized_topk_matched_deltas.csv": topk}
    files = []
    for name, frame in artifacts.items(): path = output_dir / name; frame.to_csv(path, index=False, encoding="utf-8-sig"); files.append(path)
    write_report_and_manifest(output_dir, report_dir, args.mode, run_id, spec, inference, topk_summary, files, args.fast, build_manifest, build_manifest_path)
    print(json.dumps({"run_id": run_id, "predictions": len(pred), "inference": len(inference), "topk": len(topk)}, indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())
