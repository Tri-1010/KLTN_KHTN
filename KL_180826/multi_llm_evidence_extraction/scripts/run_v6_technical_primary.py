"""V6 technical-primary evaluation runner (full price panel, zero-fill, H1/H2)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_v6_primary_panel import (  # noqa: E402
    SPEC_PATH,
    WORKSPACE_ROOT,
    _v6_code_paths,
    load_v6_spec,
    resolve_v6_protocol_path,
    resolve_v6_workspace_root,
    v6_output_dirs,
    validate_v6_run_id,
    write_build_artifacts,
)
from common import markdown_table, sha256_file, utc_now, validate_safe_identifier  # noqa: E402
from run_harmonized_comparison import (  # noqa: E402
    available_fold_features,
    bh_adjust,
    bootstrap_draws_estimable,
    fold_local_block_draws,
    json_value,
    metric_value,
)
from v6_artifacts import (  # noqa: E402
    V6ArtifactError,
    V6RunImmutableError,
    artifact_ledger,
    assert_new_v6_run_available,
    load_and_validate_build_manifest,
    portable_path,
    primary_claims,
    validate_artifact_ledger,
    write_v6_release_manifest,
    write_v6_run_manifest,
)

PRIMARY_MODELS = ("RandomForest", "LogisticRegression")
PRED_COLUMNS = [
    "row_id",
    "ticker",
    "date",
    "target_exit_date",
    "fold_id",
    "label_outperform_T20",
    "stock_return_T20",
    "VNINDEX_return_T20",
    "excess_return_T20",
    "config",
    "model",
    "pred_proba_outperform",
    "pred_label",
    "train_start",
    "train_end",
    "test_start",
    "test_end",
    "purge_method",
    "artifact_schema_version",
]
RUN_ARTIFACT_NAMES = (
    "v6_predictions.csv",
    "v6_fold_manifest.csv",
    "v6_fold_feature_manifest.csv",
    "v6_fold_metrics.csv",
    "v6_paired_daily_deltas.csv",
    "v6_inference.csv",
    "v6_run_summary.json",
)


def _config_names(spec: dict[str, Any] | Sequence[str]) -> tuple[str, ...]:
    if isinstance(spec, dict):
        configs = spec.get("configs", ())
        return tuple(configs) if isinstance(configs, dict) else tuple(configs)
    return tuple(spec)


def resolve_run_dirs(run_id: str, spec: dict[str, Any], workspace_root: Path | None = None) -> tuple[Path, Path]:
    safe = validate_v6_run_id(run_id, spec)
    return v6_output_dirs(safe, workspace_root)


def _key_frame(frame: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    work = frame.loc[:, list(columns)].copy()
    for name in ("row_id", "ticker"):
        if name in work:
            work[name] = work[name].astype(str)
    if "fold_id" in work:
        work["fold_id"] = pd.to_numeric(work["fold_id"], errors="coerce").astype("Int64")
    for name in ("date", "target_exit_date"):
        if name in work:
            work[name] = pd.to_datetime(work[name], errors="coerce").dt.normalize()
    return work.sort_values(list(columns)).reset_index(drop=True)


def validate_prediction_alignment(
    pred: pd.DataFrame,
    configs: Sequence[str] | dict[str, Any] = (),
    models: Sequence[str] = ("RandomForest",),
    required_folds: int = 3,
) -> None:
    config_names = _config_names(configs)
    if not config_names:
        raise ValueError("prediction key mismatch: no configs supplied")
    if pred.empty:
        raise ValueError("prediction key mismatch: empty predictions")
    key_columns = ["row_id", "ticker", "date", "target_exit_date", "fold_id"]
    target_columns = ["label_outperform_T20", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20"]
    missing = [name for name in key_columns if name not in pred]
    if missing:
        raise ValueError(f"prediction key mismatch: missing columns {missing}")
    work = pred.copy()
    work["fold_id"] = pd.to_numeric(work["fold_id"], errors="coerce").astype("Int64")
    expected_folds = set(range(1, int(required_folds) + 1))
    for model in models:
        model_frame = work[work["model"].eq(model)]
        for config in config_names:
            subset = model_frame[model_frame["config"].eq(config)]
            present = {int(value) for value in subset["fold_id"].dropna().unique()}
            if present != expected_folds:
                raise ValueError(f"prediction key mismatch: {config}/{model} folds {sorted(present)} != {sorted(expected_folds)}")
        for fold_id in sorted(expected_folds):
            keyed: dict[str, pd.DataFrame] = {}
            for config in config_names:
                subset = model_frame[model_frame["config"].eq(config) & model_frame["fold_id"].eq(fold_id)]
                keys = _key_frame(subset, key_columns)
                if keys.duplicated().any():
                    raise ValueError(f"prediction key mismatch: duplicate keys for {config}/{model} fold {fold_id}")
                keyed[config] = keys
            baseline = keyed[config_names[0]]
            for config in config_names[1:]:
                if not baseline.equals(keyed[config]):
                    raise ValueError(f"prediction key mismatch for {model} fold {fold_id}: {config_names[0]} vs {config}")
        left = model_frame[model_frame["config"].eq(config_names[0])]
        for config in config_names[1:]:
            right = model_frame[model_frame["config"].eq(config)]
            merged = left.merge(right, on=key_columns, suffixes=("_base", "_comp"), validate="one_to_one")
            for column in target_columns:
                if column not in left or column not in right:
                    continue
                a = pd.to_numeric(merged[f"{column}_base"], errors="coerce").to_numpy()
                b = pd.to_numeric(merged[f"{column}_comp"], errors="coerce").to_numpy()
                if not np.array_equal(a, b, equal_nan=True):
                    raise ValueError(f"prediction key mismatch: target {column} for {model}")


def _target_exit_expanding_splits(work: pd.DataFrame, n_splits: int) -> list[tuple[np.ndarray, np.ndarray, dict[str, Any]]]:
    dates = np.array(sorted(work["date"].dropna().unique()))
    if len(dates) < n_splits + 3:
        return []
    boundaries = np.array_split(dates, n_splits + 1)
    output: list[tuple[np.ndarray, np.ndarray, dict[str, Any]]] = []
    for fold in range(n_splits):
        test_dates = boundaries[fold + 1]
        if not len(test_dates):
            continue
        test_start, test_end = pd.Timestamp(test_dates[0]), pd.Timestamp(test_dates[-1])
        train_mask = (work["date"] < test_start) & (work["target_exit_date"] < test_start)
        test_mask = work["date"].isin(test_dates)
        if not train_mask.any() or not test_mask.any():
            continue
        train_idx = np.flatnonzero(train_mask.to_numpy())
        test_idx = np.flatnonzero(test_mask.to_numpy())
        train_exit_max = pd.Timestamp(work.iloc[train_idx]["target_exit_date"].max())
        if train_exit_max >= test_start:
            raise ValueError("target-exit purge failed")
        output.append((train_idx, test_idx, {
            "fold_id": fold + 1,
            "train_start": pd.Timestamp(work.iloc[train_idx]["date"].min()),
            "train_end": pd.Timestamp(work.iloc[train_idx]["date"].max()),
            "train_target_exit_max": train_exit_max,
            "test_start": test_start,
            "test_end": test_end,
            "purge_method": "target_exit_date_before_test_start",
        }))
    return output


def _date_purge_expanding_splits(work: pd.DataFrame, n_splits: int, purge: int = 20) -> list[tuple[np.ndarray, np.ndarray, dict[str, Any]]]:
    unique = np.array(sorted(work["date"].dropna().unique()))
    if len(unique) < n_splits + purge + 2:
        return []
    minimum_train = max(purge, len(unique) // (n_splits + 1))
    available = len(unique) - minimum_train - purge
    if available < n_splits:
        return []
    block = max(1, available // n_splits)
    output: list[tuple[np.ndarray, np.ndarray, dict[str, Any]]] = []
    for fold in range(n_splits):
        test_start_idx = minimum_train + purge + fold * block
        test_end_idx = len(unique) if fold == n_splits - 1 else min(len(unique), test_start_idx + block)
        if test_start_idx >= len(unique) or test_end_idx <= test_start_idx:
            continue
        train_end_idx = test_start_idx - purge
        if train_end_idx <= 0:
            continue
        train_dates = unique[:train_end_idx]
        test_dates = unique[test_start_idx:test_end_idx]
        train_idx = np.flatnonzero(work["date"].isin(train_dates).to_numpy())
        test_idx = np.flatnonzero(work["date"].isin(test_dates).to_numpy())
        if not len(train_idx) or not len(test_idx):
            continue
        output.append((train_idx, test_idx, {
            "fold_id": fold + 1,
            "train_start": pd.Timestamp(train_dates[0]),
            "train_end": pd.Timestamp(train_dates[-1]),
            "test_start": pd.Timestamp(test_dates[0]),
            "test_end": pd.Timestamp(test_dates[-1]),
            "purge_method": "date_based_20_session_purge",
            "purge_trading_days": int(purge),
        }))
    return output


def expanding_purged_splits(panel: pd.DataFrame, spec: dict[str, Any]) -> list[tuple[np.ndarray, np.ndarray, dict[str, Any]]]:
    n_splits = int(spec.get("folds", {}).get("count", 3))
    work = panel.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce").dt.normalize()
    has_exit = "target_exit_date" in work and pd.to_datetime(work["target_exit_date"], errors="coerce").notna().any()
    if has_exit:
        work["target_exit_date"] = pd.to_datetime(work["target_exit_date"], errors="coerce").dt.normalize()
        splits = _target_exit_expanding_splits(work, n_splits)
        if splits:
            return splits
    return _date_purge_expanding_splits(work, n_splits, purge=20)


def apply_primary_bh(inference_df: pd.DataFrame, spec: dict[str, Any]) -> pd.DataFrame:
    work = inference_df.copy()
    primary = spec.get("primary", {})
    family = spec.get("hypothesis_families", {}).get("V6_H1_H2", {})
    family_ids = {str(item.get("id")) for item in family.get("hypotheses", []) if item.get("id")} or {"H1", "H2"}
    hypothesis = work.get("hypothesis", pd.Series("", index=work.index)).astype(str)
    role = work.get("role", pd.Series("primary", index=work.index)).astype(str)
    model = work.get("model", pd.Series("", index=work.index)).astype(str)
    metric = work.get("metric", pd.Series("", index=work.index)).astype(str)
    mask = hypothesis.isin(family_ids) & role.eq("primary") & model.eq(str(primary.get("model", "RandomForest"))) & metric.eq(str(primary.get("metric", "balanced_accuracy")))
    work["primary_family_member"] = mask.astype(bool)
    work["p_value_bh"] = np.nan
    if bool(mask.any()):
        work.loc[mask, "p_value_bh"] = pd.to_numeric(bh_adjust(pd.to_numeric(work.loc[mask, "p_value"], errors="coerce")), errors="coerce").to_numpy()
    return work


def _eligible_mask(panel: pd.DataFrame) -> pd.Series:
    if "panel_eligible" not in panel:
        return pd.Series(True, index=panel.index)
    return panel["panel_eligible"].astype(str).str.lower().isin({"true", "1"})


def semantic_predictor_columns(manifest: pd.DataFrame) -> list[str]:
    if manifest.empty or "feature" not in manifest:
        return []
    family = manifest.get("family", pd.Series("", index=manifest.index)).astype(str).str.lower()
    predictor = manifest.get("predictor", pd.Series(True, index=manifest.index)).astype(str).str.lower().isin({"true", "1"})
    return [str(name) for name in manifest.loc[family.eq("semantic") & predictor, "feature"].tolist() if str(name)]


def semantic_nonzero_mask(panel: pd.DataFrame, manifest: pd.DataFrame) -> pd.Series:
    columns = [column for column in semantic_predictor_columns(manifest) if column in panel]
    if not columns:
        return pd.Series(False, index=panel.index)
    return panel.loc[:, columns].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs().gt(0.0).any(axis=1)


def predictors_by_config(manifest: pd.DataFrame, spec: dict[str, Any]) -> dict[str, list[str]]:
    declared = {name: [] for name in _config_names(spec)}
    if manifest.empty:
        return declared
    predictor = manifest.get("predictor", pd.Series(True, index=manifest.index)).astype(str).str.lower().isin({"true", "1"})
    for _, row in manifest.loc[predictor].iterrows():
        raw = row.get("configs", "[]")
        configs = json.loads(raw) if isinstance(raw, str) else list(raw or [])
        feature = str(row.get("feature", ""))
        for config in configs:
            if feature and config in declared:
                declared[config].append(feature)
    return declared


def _ensure_row_id(frame: pd.DataFrame) -> pd.DataFrame:
    if "row_id" in frame and frame["row_id"].notna().all():
        return frame
    work = frame.copy()
    date = pd.to_datetime(work["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    exit_date = pd.to_datetime(work.get("target_exit_date"), errors="coerce").dt.strftime("%Y-%m-%d").fillna("NA")
    work["row_id"] = work["ticker"].astype(str) + "|" + date + "|" + exit_date
    return work


def _models(spec: dict[str, Any], fast: bool) -> dict[str, Any]:
    lr, rf = spec["models"]["logistic_regression"], spec["models"]["random_forest"]
    return {
        "LogisticRegression": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=lr["C"], max_iter=lr["max_iter"], class_weight=lr["class_weight"], random_state=lr["random_state"])),
        "RandomForest": make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=50 if fast else rf["n_estimators"], max_depth=rf["max_depth"], min_samples_leaf=rf["min_samples_leaf"], class_weight=rf["class_weight"], random_state=rf["random_state"], n_jobs=rf["n_jobs"])),
    }


def _hypothesis_rows(spec: dict[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in spec.get("hypothesis_families", {}).get("V6_H1_H2", {}).get("hypotheses", []):
        result.append({"hypothesis": str(item["id"]), "role": "primary", "baseline_config": str(item["baseline_config"]), "comparison_config": str(item["comparison_config"])})
    for item in spec.get("hypothesis_families", {}).get("supplemental", {}).get("hypotheses", []):
        result.append({"hypothesis": str(item["id"]), "role": "supplemental", "baseline_config": str(item["baseline_config"]), "comparison_config": str(item["comparison_config"])})
    return result


def _role_for_model(model: str, hypothesis_role: str, spec: dict[str, Any]) -> str:
    if hypothesis_role == "primary" and model == str(spec["primary"]["model"]):
        return "primary"
    return "supplemental" if hypothesis_role == "supplemental" and model == str(spec["primary"]["model"]) else "robustness"


def run_models(panel: pd.DataFrame, manifest: pd.DataFrame, spec: dict[str, Any], fast: bool, row_filter: str = "primary") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mask = _eligible_mask(panel)
    if row_filter == "semantic_nonzero":
        mask &= semantic_nonzero_mask(panel, manifest)
    elif row_filter != "primary":
        raise ValueError(f"unsupported row_filter: {row_filter!r}")
    work = _ensure_row_id(panel.loc[mask].copy()).sort_values(["date", "ticker"]).reset_index(drop=True)
    if work.empty:
        raise ValueError(f"no rows for V6 evaluation under row_filter={row_filter}")
    splits = expanding_purged_splits(work, spec)
    required_folds = int(spec.get("minimums", {}).get("valid_folds", spec.get("folds", {}).get("count", 3)))
    if len(splits) != required_folds:
        raise ValueError(f"requires {required_folds} valid folds; got {len(splits)}")
    declared, models = predictors_by_config(manifest, spec), _models(spec, fast)
    predictions: list[pd.DataFrame] = []
    folds: list[dict[str, Any]] = []
    fold_features: list[dict[str, Any]] = []
    fold_metrics: list[dict[str, Any]] = []
    for train_idx, test_idx, meta in splits:
        train, test = work.iloc[train_idx], work.iloc[test_idx]
        folds.append({**meta, "n_train": int(len(train)), "n_test": int(len(test)), "status": "ok"})
        for config in _config_names(spec):
            features, audit = available_fold_features(train, declared.get(config, []))
            fold_features.extend({**meta, "config": config, **row} for row in audit)
            if not features:
                raise ValueError(f"no usable predictors for {config} fold {meta['fold_id']}")
            if train["label_outperform_T20"].nunique() < 2:
                raise ValueError(f"train fold {meta['fold_id']} lacks both classes")
            for model_name, template in models.items():
                estimator = clone(template)
                estimator.fit(train[features], train["label_outperform_T20"].astype(int))
                probability = estimator.predict_proba(test[features])[:, 1]
                keep = [name for name in ("row_id", "ticker", "date", "target_exit_date", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20", "label_outperform_T20") if name in test]
                tmp = test[keep].copy()
                tmp["config"], tmp["model"], tmp["fold_id"] = config, model_name, meta["fold_id"]
                tmp["pred_proba_outperform"] = probability
                tmp["pred_label"] = (probability >= 0.5).astype(int)
                tmp["train_start"], tmp["train_end"], tmp["test_start"], tmp["test_end"], tmp["purge_method"] = meta["train_start"], meta["train_end"], meta["test_start"], meta["test_end"], meta["purge_method"]
                tmp["artifact_schema_version"] = "v6_primary_predictions_v1"
                predictions.append(tmp)
                for metric in tuple(spec.get("metrics", {"balanced_accuracy": "higher"})):
                    value = metric_value(tmp, metric, int(spec["minimums"]["samples_per_class"]))
                    fold_metrics.append({"config": config, "model": model_name, "fold_id": meta["fold_id"], "metric": metric, "value": value, "status": "ok" if pd.notna(value) else "undefined"})
    pred = pd.concat(predictions, ignore_index=True)
    for column in PRED_COLUMNS:
        if column not in pred:
            pred[column] = pd.NA
    pred = pred[PRED_COLUMNS]
    validate_prediction_alignment(pred, configs=_config_names(spec), models=PRIMARY_MODELS, required_folds=required_folds)
    return pred, pd.DataFrame(folds), pd.DataFrame(fold_features), pd.DataFrame(fold_metrics)


def build_paired_inference(pred: pd.DataFrame, spec: dict[str, Any], fast: bool, bootstrap_samples: int | None = None, permutation_samples: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics, directions = tuple(spec.get("metrics", {"balanced_accuracy": "higher"})), spec.get("metrics", {})
    boot_count = bootstrap_samples or (200 if fast else int(spec["inference"]["bootstrap_samples"]))
    perm_count = permutation_samples or (200 if fast else int(spec["inference"]["permutation_samples"]))
    seed, block = int(spec["inference"]["seed"]), int(spec["inference"]["block_dates"])
    class_minimum, required_folds, min_paired = int(spec["minimums"]["samples_per_class"]), int(spec["minimums"]["valid_folds"]), int(spec["minimums"]["paired_dates"])
    daily_rows: list[dict[str, Any]] = []
    inference_rows: list[dict[str, Any]] = []
    for hypothesis in _hypothesis_rows(spec):
        baseline, comparison = hypothesis["baseline_config"], hypothesis["comparison_config"]
        for model in PRIMARY_MODELS:
            left = pred[(pred["config"] == baseline) & (pred["model"] == model)]
            right = pred[(pred["config"] == comparison) & (pred["model"] == model)]
            merged = left.merge(right, on=["row_id", "ticker", "date", "fold_id", "target_exit_date"], suffixes=("_base", "_comp"), validate="one_to_one")
            rows_for_pair: list[dict[str, Any]] = []
            for (fold_id, date), group in merged.groupby(["fold_id", "date"], sort=True):
                for metric in metrics:
                    base = pd.DataFrame({"label_outperform_T20": group["label_outperform_T20_base"], "pred_proba_outperform": group["pred_proba_outperform_base"], "excess_return_T20": group["excess_return_T20_base"]})
                    comp = pd.DataFrame({"label_outperform_T20": group["label_outperform_T20_comp"], "pred_proba_outperform": group["pred_proba_outperform_comp"], "excess_return_T20": group["excess_return_T20_comp"]})
                    a, b = metric_value(base, metric, class_minimum), metric_value(comp, metric, class_minimum)
                    raw = b - a
                    item = {"hypothesis": hypothesis["hypothesis"], "role": _role_for_model(model, hypothesis["role"], spec), "baseline_config": baseline, "comparison_config": comparison, "model": model, "fold_id": fold_id, "date": date, "metric": metric, "baseline_value": a, "comparison_value": b, "raw_delta": raw, "improvement_delta": -raw if directions.get(metric) == "lower" else raw, "status": "ok" if pd.notna(raw) else "undefined"}
                    daily_rows.append(item)
                    rows_for_pair.append(item)
            daily = pd.DataFrame(rows_for_pair)
            for metric, group in daily[daily["status"].eq("ok")].groupby("metric"):
                status = "ok" if group["fold_id"].nunique() == required_folds and len(group) >= min_paired else "not_estimable"
                boot = fold_local_block_draws(group, boot_count, block, seed) if status == "ok" else np.array([])
                perm = fold_local_block_draws(group, perm_count, block, seed, True) if status == "ok" else np.array([])
                if status == "ok" and not bootstrap_draws_estimable(boot):
                    status, boot, perm = "not_estimable_degenerate_bootstrap", np.array([]), np.array([])
                mean = group["improvement_delta"].mean() if len(group) else np.nan
                inference_rows.append({"hypothesis": hypothesis["hypothesis"], "role": _role_for_model(model, hypothesis["role"], spec), "baseline_config": baseline, "comparison_config": comparison, "model": model, "metric": metric, "raw_delta": group["raw_delta"].mean() if len(group) else np.nan, "improvement_delta": mean, "bootstrap_ci_low": np.percentile(boot, 2.5) if len(boot) else np.nan, "bootstrap_ci_high": np.percentile(boot, 97.5) if len(boot) else np.nan, "p_value": (np.sum(np.abs(perm) >= abs(mean)) + 1) / (len(perm) + 1) if len(perm) else np.nan, "n_paired_dates": int(len(group)), "n_folds": int(group["fold_id"].nunique()), "status": status})
    return pd.DataFrame(daily_rows), apply_primary_bh(pd.DataFrame(inference_rows), spec)


def _normalize_sensitivity_tag(tag: str | None) -> str | None:
    if tag is None:
        return None
    text = str(tag).strip().lower().replace(" ", "_")
    return validate_safe_identifier(text, "sensitivity_tag") if text else None


def _claim_level(horizon: int, row_filter: str, sensitivity_tag: str | None, spec: dict[str, Any]) -> tuple[str, list[str]]:
    tag = _normalize_sensitivity_tag(sensitivity_tag)
    is_row, is_horizon, is_tag = row_filter == "semantic_nonzero", int(horizon) != 20, tag is not None
    if is_tag:
        level = f"v6_sensitivity_{tag}"
    elif is_row and is_horizon:
        level = f"v6_sensitivity_semantic_nonzero_horizon_T{horizon}"
    elif is_row:
        level = "v6_sensitivity_semantic_nonzero_retrain"
    elif is_horizon:
        level = f"v6_sensitivity_horizon_T{horizon}"
    else:
        level = str(spec["claim_level"])
    limitations = ["no_causal_or_investment_advice_claim", "bh_adjustment_only_on_H1_H2_random_forest_balanced_accuracy"]
    if is_row or is_horizon or is_tag:
        limitations = ["sensitivity_only_not_v6_primary", "does_not_replace_v6_primary_20260909", *limitations]
    return level, limitations


def _run_artifact_paths(output_dir: Path) -> list[Path]:
    return [output_dir / name for name in RUN_ARTIFACT_NAMES]


def write_summaries(
    output_dir: Path,
    report_dir: Path,
    run_id: str,
    spec: dict[str, Any],
    pred: pd.DataFrame,
    folds: pd.DataFrame,
    fold_features: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    paired: pd.DataFrame,
    inference: pd.DataFrame,
    fast: bool,
    row_filter: str = "primary",
    n_eligible_rows: int | None = None,
    horizon: int | None = None,
    sensitivity_tag: str | None = None,
    *,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    root = resolve_v6_workspace_root(workspace_root)
    output, report = Path(output_dir).resolve(), Path(report_dir).resolve()
    portable_path(root, output)
    portable_path(root, report)
    safe_run = validate_v6_run_id(run_id, spec)
    load_and_validate_build_manifest(output, root, safe_run)
    destination_paths = [*_run_artifact_paths(output), report / "v6_primary_report.md"]
    existing = [path.name for path in destination_paths if path.exists()]
    if existing:
        raise V6ArtifactError(f"refusing to overwrite existing V6 run artifacts: {existing}")
    artifacts = {
        "v6_predictions.csv": pred,
        "v6_fold_manifest.csv": folds,
        "v6_fold_feature_manifest.csv": fold_features,
        "v6_fold_metrics.csv": fold_metrics,
        "v6_paired_daily_deltas.csv": paired,
        "v6_inference.csv": inference,
    }
    for name, frame in artifacts.items():
        frame.to_csv(output / name, index=False, encoding="utf-8-sig")
    resolved_horizon = int(horizon) if horizon is not None else 20
    claim_level, limitations = _claim_level(resolved_horizon, row_filter, sensitivity_tag, spec)
    if fast:
        limitations = ["fast_smoke_not_primary_evidence", *limitations]
    primary_rows = inference[
        inference["hypothesis"].isin(["H1", "H2"])
        & inference["role"].eq("primary")
        & inference["model"].eq(spec["primary"]["model"])
        & inference["metric"].eq(spec["primary"]["metric"])
        & inference["primary_family_member"].astype(bool)
    ] if not inference.empty else inference
    protocol_path = resolve_v6_protocol_path(root)
    summary = {
        "artifact_schema_version": "v6_primary_run_summary_v2",
        "generated_at_utc": utc_now(),
        "run_id": safe_run,
        "protocol_version": spec["protocol_version"],
        "protocol_path": portable_path(root, protocol_path),
        "protocol_sha256": sha256_file(protocol_path),
        "claim_level": claim_level,
        "row_filter": row_filter,
        "horizon_benchmark_sessions": resolved_horizon,
        "sensitivity_tag": _normalize_sensitivity_tag(sensitivity_tag),
        "fast": bool(fast),
        "n_eligible_rows": int(n_eligible_rows) if n_eligible_rows is not None else None,
        "n_predictions": int(len(pred)),
        "n_folds": int(len(folds)),
        "purge_methods": sorted({str(value) for value in folds.get("purge_method", pd.Series(dtype=str)).dropna().unique()}),
        "primary": [{
            "hypothesis": row["hypothesis"], "status": row["status"],
            "improvement_delta": json_value(row.get("improvement_delta")),
            "bootstrap_ci_low": json_value(row.get("bootstrap_ci_low")),
            "bootstrap_ci_high": json_value(row.get("bootstrap_ci_high")),
            "p_value": json_value(row.get("p_value")), "p_value_bh": json_value(row.get("p_value_bh")),
            "n_paired_dates": json_value(row.get("n_paired_dates")), "n_folds": json_value(row.get("n_folds")),
        } for row in primary_rows.to_dict("records")],
        "outputs": {path.name: portable_path(root, path) for path in _run_artifact_paths(output) if path.name != "v6_run_summary.json"},
        "limitations": limitations,
    }
    summary_path = output / "v6_run_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    report_lines = [
        "# V6 technical primary evaluation", "", f"- Run: `{safe_run}`", f"- Claim level: `{claim_level}`", f"- Protocol SHA256: `{summary['protocol_sha256']}`", "",
        "Primary family is H1 (B vs A) and H2 (C vs A) RandomForest balanced_accuracy. `status: ok` means estimable only; use explicit claim states in the release manifest.", "",
        "## Fold audit", "", markdown_table(folds), "", "## Inference", "", markdown_table(inference), "", "## Limitations", "", *[f"- {item}" for item in limitations],
    ]
    report_path = report / "v6_primary_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    run_manifest = write_v6_run_manifest(
        output, safe_run, spec, root, _run_artifact_paths(output), _v6_code_paths(root),
        extra={"build_manifest_sha256": sha256_file(output / "v6_build_manifest.json"), "claim_level": claim_level},
    )
    claims = primary_claims(inference.to_dict("records"), spec, audit_pass=True, manifest_pass=True)
    if fast:
        for claim in claims:
            claim["claim_state"] = "not_estimable"
            claim["claim_gate_pass"] = False
            claim["claim_gates"]["manifest_pass"] = False
            claim["limitations"] = ["fast_smoke_not_primary_evidence"]
    release = write_v6_release_manifest(
        output, safe_run, spec, root, [summary_path, report_path, output / "v6_inference.csv"], claims,
        limitations=limitations,
        extra={"build_manifest_sha256": sha256_file(output / "v6_build_manifest.json"), "run_manifest_sha256": sha256_file(run_manifest)},
    )
    return {**summary, "release_manifest": portable_path(root, release)}


def load_or_build_panel(
    output_dir: Path,
    report_dir: Path,
    run_id: str,
    spec: dict[str, Any],
    horizon: int | None = None,
    *,
    workspace_root: Path | None = None,
    reserved: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel_path, manifest_path = output_dir / "v6_primary_panel.csv", output_dir / "v6_feature_manifest.csv"
    build_horizon = int(horizon) if horizon is not None else 20
    if not panel_path.exists() or not manifest_path.exists():
        write_build_artifacts(output_dir, report_dir, run_id, spec, horizon=build_horizon, workspace_root=workspace_root, reserve_run=not reserved)
    else:
        load_and_validate_build_manifest(output_dir, resolve_v6_workspace_root(workspace_root), run_id)
    panel, manifest = pd.read_csv(panel_path, encoding="utf-8-sig"), pd.read_csv(manifest_path, encoding="utf-8-sig")
    for column in ("date", "entry_date", "target_exit_date"):
        if column in panel:
            panel[column] = pd.to_datetime(panel[column], errors="coerce")
    return panel, manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V6 technical-primary evaluation")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workspace-root", type=Path, default=WORKSPACE_ROOT, help="workspace root containing KL_180826 and hash-pinned V6 inputs")
    parser.add_argument("--fast", action="store_true", help="smaller RF and fewer inference samples; never primary evidence")
    parser.add_argument("--row-filter", choices=["primary", "semantic_nonzero"], default="primary")
    parser.add_argument("--horizon", type=int, default=None)
    parser.add_argument("--bootstrap-samples", type=int)
    parser.add_argument("--permutation-samples", type=int)
    parser.add_argument("--panel-from-run-id", help=argparse.SUPPRESS)
    parser.add_argument("--sensitivity-tag", default=None)
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    root = resolve_v6_workspace_root(args.workspace_root)
    spec = load_v6_spec(resolve_v6_protocol_path(root))
    run_id = validate_v6_run_id(args.run_id, spec)
    output_dir, report_dir = resolve_run_dirs(run_id, spec, root)
    assert_new_v6_run_available(run_id, spec, output_dir, report_dir)
    horizon = int(args.horizon) if args.horizon is not None else None
    if args.panel_from_run_id:
        raise V6ArtifactError("panel-from-run-id is disabled for immutable V6 releases; create a new build from validated inputs")
    # The builder creates both directories and its intent manifest atomically before
    # it writes a panel. Do not pre-create them here or the V6 manifest sequence
    # would lose its reservation marker.
    panel, manifest = load_or_build_panel(output_dir, report_dir, run_id, spec, horizon=horizon, workspace_root=root)
    if horizon is None and "horizon_benchmark_sessions" in panel:
        values = pd.to_numeric(panel["horizon_benchmark_sessions"], errors="coerce").dropna().unique()
        horizon = int(values[0]) if len(values) == 1 else 20
    horizon = horizon or 20
    mask = _eligible_mask(panel)
    if args.row_filter == "semantic_nonzero":
        mask &= semantic_nonzero_mask(panel, manifest)
    pred, folds, fold_features, fold_metrics = run_models(panel, manifest, spec, args.fast, row_filter=args.row_filter)
    paired, inference = build_paired_inference(pred, spec, args.fast, args.bootstrap_samples, args.permutation_samples)
    summary = write_summaries(output_dir, report_dir, run_id, spec, pred, folds, fold_features, fold_metrics, paired, inference, args.fast, row_filter=args.row_filter, n_eligible_rows=int(mask.sum()), horizon=horizon, sensitivity_tag=args.sensitivity_tag, workspace_root=root)
    print(json.dumps({"status": "ok", "run_id": run_id, "claim_level": summary["claim_level"], "n_predictions": summary["n_predictions"], "release_manifest": summary.get("release_manifest")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
