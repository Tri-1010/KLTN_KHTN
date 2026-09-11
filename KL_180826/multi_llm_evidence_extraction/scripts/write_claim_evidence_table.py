from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import DATA_DIR, OUTPUT_DIR, REPORT_DIR, STUDY_DIR, ensure_dirs

OUT = REPORT_DIR / "claim_vs_evidence_table.md"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError, UnicodeDecodeError):
        return pd.DataFrame()


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(STUDY_DIR.resolve()).as_posix()
    except ValueError:
        return str(path)


def artifact_metadata(path: Path, upstreams: Iterable[Path] = ()) -> dict[str, Any]:
    existing_upstreams = [Path(item) for item in upstreams if Path(item).exists()]
    if not path.exists():
        return {"path": display_path(path), "sha256": None, "modified_utc": None, "latest_upstream_utc": None, "freshness": "missing"}
    latest = max((item.stat().st_mtime for item in existing_upstreams), default=None)
    modified = path.stat().st_mtime
    return {
        "path": display_path(path),
        "sha256": sha256_file(path),
        "modified_utc": datetime.fromtimestamp(modified, timezone.utc).isoformat(timespec="seconds"),
        "latest_upstream_utc": datetime.fromtimestamp(latest, timezone.utc).isoformat(timespec="seconds") if latest is not None else None,
        "freshness": "no_upstream_reference" if latest is None else ("fresh" if modified >= latest else "stale"),
    }


def schema_versions(frame: pd.DataFrame) -> list[str]:
    if frame.empty or "artifact_schema_version" not in frame:
        return []
    return sorted(frame["artifact_schema_version"].dropna().astype(str).unique().tolist())


def row_count(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return len(pd.read_csv(path, encoding="utf-8-sig", usecols=[0]))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError, UnicodeDecodeError, ValueError):
        return None


def consensus_summary(frame: pd.DataFrame) -> dict[str, Any]:
    methods = {str(k): int(v) for k, v in frame["consensus_method"].value_counts(dropna=False).items()} if "consensus_method" in frame else {}
    eligible = int(bool_series(frame["analysis_eligible"]).sum()) if "analysis_eligible" in frame else 0
    return {"rows": len(frame), "methods": methods, "eligible": eligible, "ineligible": len(frame) - eligible, "schema_versions": schema_versions(frame)}


def annotation_provenance(output_dir: Path = OUTPUT_DIR) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(output_dir.glob("annotation_manifest_*.json")):
        if path.name == "annotation_manifest_index.json":
            continue
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        annotator = str(manifest.get("annotator") or path.stem.rsplit("_", 1)[-1])
        label_path = output_dir / f"labels_annotator_{annotator}.jsonl"
        expected = (manifest.get("output_sha256") or {}).get("labels")
        actual = sha256_file(label_path)
        rows.append({
            "annotator": annotator,
            "api_provider": manifest.get("api_provider", manifest.get("provider", "unknown")),
            "requested_model": manifest.get("requested_model", manifest.get("model", "unknown")),
            "response_models": ",".join(map(str, manifest.get("response_models", []))) or manifest.get("response_model", "unknown"),
            "model_vendor": manifest.get("model_vendor", "unknown"),
            "route_mode": manifest.get("route_mode", "unknown"),
            "provenance_status": manifest.get("provenance_status", manifest.get("status", "unknown")),
            "prompt_version": manifest.get("prompt_version", "unknown"),
            "schema_version": manifest.get("schema_version", "unknown"),
            "input_sha256": manifest.get("input_sha256", "unknown"),
            "schema_sha256": manifest.get("schema_sha256", "unknown"),
            "labels_sha256": actual,
            "labels_hash_match": bool(expected and actual == expected),
            "manifest_sha256": sha256_file(path),
            "generated_at_utc": manifest.get("generated_at_utc"),
        })
    return rows


def event_test_summary(frame: pd.DataFrame) -> dict[str, Any]:
    required = {"p_value_bh", "diff_ci_low", "correction_method"}
    base = {"rows": len(frame), "schema_versions": schema_versions(frame), "gate_rule": "p_value_bh <= 0.05 AND diff_ci_low > 0 under Benjamini-Hochberg correction"}
    if frame.empty or not required.issubset(frame.columns):
        return {**base, "gate_available": False, "fdr_significant": 0, "positive_ci": 0, "robust_results": 0, "claim_gate_pass": False, "reported_flag_mismatches": None}
    p_bh = pd.to_numeric(frame["p_value_bh"], errors="coerce")
    ci_low = pd.to_numeric(frame["diff_ci_low"], errors="coerce")
    is_bh = frame["correction_method"].astype(str).str.strip().str.lower().eq("benjamini-hochberg")
    fdr = p_bh.le(0.05) & p_bh.notna() & is_bh
    positive = ci_low.gt(0) & ci_low.notna()
    computed_robust = fdr & positive
    reported_robust = bool_series(frame["robust_positive_effect"]) if "robust_positive_effect" in frame else None
    fdr_mismatches = int((bool_series(frame["reject_fdr_05"]) != fdr).sum()) if "reject_fdr_05" in frame else None
    robust_mismatches = int((reported_robust != computed_robust).sum()) if reported_robust is not None else None
    robust = reported_robust if reported_robust is not None and robust_mismatches == 0 else computed_robust
    return {
        **base, "gate_available": True, "fdr_significant": int(fdr.sum()),
        "positive_ci": int(positive.sum()), "robust_results": int(robust.sum()),
        "claim_gate_pass": bool(robust.any()), "reported_flag_mismatches": fdr_mismatches,
        "robust_flag_mismatches": robust_mismatches,
    }


def ml_fold_summary(frame: pd.DataFrame) -> dict[str, Any]:
    columns = ["fold_id", "train_start", "train_end", "test_start", "test_end", "purge_trading_days"]
    base = {"rows": len(frame), "schema_versions": schema_versions(frame)}
    if frame.empty or not set(columns + ["date"]).issubset(frame.columns):
        return {**base, "fold_count": 0, "folds": [], "purge_trading_days": [], "purged_oos_verified": False, "status": "unavailable", "configs": [], "models": []}
    unique = frame[columns].drop_duplicates().sort_values(columns)
    parsed = frame.copy()
    for column in ("date", "train_start", "train_end", "test_start", "test_end"):
        parsed[column] = pd.to_datetime(parsed[column], errors="coerce")
    purge = pd.to_numeric(parsed["purge_trading_days"], errors="coerce")
    business_day_gap = pd.Series(
        [
            np.busday_count(
                (train_end + pd.Timedelta(days=1)).date(),
                test_start.date(),
            )
            if pd.notna(train_end) and pd.notna(test_start)
            else -1
            for train_end, test_start in zip(parsed["train_end"], parsed["test_start"])
        ],
        index=parsed.index,
    )
    valid_fold_ids = parsed["fold_id"].notna() & parsed["fold_id"].astype(str).str.strip().ne("")
    verified = bool(
        len(unique)
        and valid_fold_ids.all()
        and unique.groupby("fold_id", dropna=False).size().eq(1).all()
        and parsed["train_end"].lt(parsed["test_start"]).all()
        and business_day_gap.ge(purge).all()
        and parsed["date"].ge(parsed["test_start"]).all()
        and parsed["date"].le(parsed["test_end"]).all()
        and purge.gt(0).all()
    )
    folds = [{column: None if pd.isna(row[column]) else str(row[column]) for column in columns} for _, row in unique.iterrows()]
    return {
        **base, "fold_count": int(unique["fold_id"].nunique()), "folds": folds,
        "purge_trading_days": sorted(pd.to_numeric(unique["purge_trading_days"], errors="coerce").dropna().astype(int).unique().tolist()),
        "purged_oos_verified": verified, "status": "verified_from_fold_metadata" if verified else "metadata_check_failed",
        "configs": sorted(frame["config"].dropna().astype(str).unique().tolist()) if "config" in frame else [],
        "models": sorted(frame["model"].dropna().astype(str).unique().tolist()) if "model" in frame else [],
    }


def topk_summary(frame: pd.DataFrame) -> dict[str, Any]:
    required = {"config", "model", "top_k", "strategy", "entry_date", "exit_date", "gross_return", "net_return", "gross_excess_return", "net_excess_return", "turnover", "transaction_cost", "round_trip_cost_rate"}
    base = {"rows": len(frame), "schema_versions": schema_versions(frame)}
    if frame.empty or not required.issubset(frame.columns):
        return {**base, "periods": 0, "non_overlapping": False, "turnover_cost_verified": False, "net_return_verified": False, "status": "unavailable", "strategies": [], "top_k": []}
    work = frame.copy()
    work["entry_date"] = pd.to_datetime(work["entry_date"], errors="coerce")
    work["exit_date"] = pd.to_datetime(work["exit_date"], errors="coerce")
    non_overlap = True
    for _, group in work.groupby(["config", "model", "top_k", "strategy"], dropna=False):
        periods = group[["entry_date", "exit_date"]].drop_duplicates().sort_values("entry_date")
        previous_exit = periods["exit_date"].shift(1)
        boundary_ok = previous_exit.isna() | periods["entry_date"].ge(previous_exit)
        direction_ok = periods["exit_date"].gt(periods["entry_date"])
        if periods.isna().any().any() or not boundary_ok.all() or not direction_ok.all():
            non_overlap = False
            break
    number = lambda name: pd.to_numeric(work[name], errors="coerce")
    nonnegative_cost_inputs = bool(
        number("turnover").ge(0).all()
        and number("round_trip_cost_rate").ge(0).all()
        and number("transaction_cost").ge(0).all()
    )
    cost_ok = bool(
        nonnegative_cost_inputs
        and np.isclose(number("transaction_cost"), number("turnover") * number("round_trip_cost_rate"), rtol=1e-9, atol=1e-12, equal_nan=False).all()
    )
    net_ok = bool(np.isclose(number("net_return"), number("gross_return") - number("transaction_cost"), rtol=1e-9, atol=1e-12, equal_nan=False).all() and np.isclose(number("net_excess_return"), number("gross_excess_return") - number("transaction_cost"), rtol=1e-9, atol=1e-12, equal_nan=False).all())
    verified = non_overlap and cost_ok and net_ok
    return {
        **base, "periods": int(work["entry_date"].nunique()), "non_overlapping": non_overlap,
        "turnover_cost_verified": cost_ok, "net_return_verified": net_ok,
        "status": "verified_nonoverlap_turnover_cost" if verified else "methodology_check_failed",
        "strategies": sorted(work["strategy"].dropna().astype(str).unique().tolist()),
        "top_k": sorted(pd.to_numeric(work["top_k"], errors="coerce").dropna().astype(int).unique().tolist()),
        "round_trip_cost_rates": sorted(number("round_trip_cost_rate").dropna().unique().tolist()),
        "holding_period_days": sorted(number("holding_period_days").dropna().astype(int).unique().tolist()) if "holding_period_days" in work else [],
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            for line in handle:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    rows.append(value)
    except (OSError, UnicodeDecodeError):
        return []
    return rows


def _cohen_kappa(pairs: list[tuple[Any, Any]]) -> float | None:
    if not pairs:
        return None
    total = len(pairs)
    observed = sum(left == right for left, right in pairs) / total
    left_counts = Counter(left for left, _ in pairs)
    right_counts = Counter(right for _, right in pairs)
    expected = sum((left_counts[label] / total) * (right_counts[label] / total) for label in set(left_counts) | set(right_counts))
    return None if expected == 1 else (observed - expected) / (1 - expected)


def annotation_agreement_summary(labels_by_annotator: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    fields = ["ticker_relevance", "materiality", "direction", "event_type", "time_horizon"]
    labels: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
    valid_counts: dict[str, int] = {}
    error_counts: dict[str, int] = {}
    for annotator, rows in sorted(labels_by_annotator.items()):
        valid = [row for row in rows if row.get("status") == "ok" and row.get("news_id") is not None]
        labels[annotator] = {
            (str(row["news_id"]), str(row.get("ticker") or "")): row
            for row in valid
        }
        valid_counts[annotator] = len(labels[annotator])
        error_counts[annotator] = sum(row.get("status") == "error" for row in rows)

    pairwise = []
    for left, right in itertools.combinations(labels, 2):
        common_ids = sorted(set(labels[left]) & set(labels[right]))
        for field in fields:
            pairs = [
                (labels[left][row_key].get(field), labels[right][row_key].get(field))
                for row_key in common_ids
                if str(labels[left][row_key].get(field) or "").strip()
                and str(labels[right][row_key].get(field) or "").strip()
            ]
            if not pairs:
                continue
            agree = sum(left_value == right_value for left_value, right_value in pairs)
            pairwise.append({
                "field": field,
                "pair": f"{left}-{right}",
                "agree": int(agree),
                "total": len(pairs),
                "agreement": agree / len(pairs),
                "cohen_kappa": _cohen_kappa(pairs),
            })
    return {
        "available": bool(pairwise),
        "valid_counts": valid_counts,
        "error_counts": error_counts,
        "pairwise": pairwise,
        "mean_agreement": (sum(row["agreement"] for row in pairwise) / len(pairwise)) if pairwise else None,
    }


def agreement_summary(output_dir: Path) -> dict[str, Any]:
    return annotation_agreement_summary({
        annotator: read_jsonl(output_dir / f"labels_annotator_{annotator}.jsonl")
        for annotator in "abc"
    })


def manual_sanity_summary(frame: pd.DataFrame) -> dict[str, Any]:
    check_columns = [
        "human_relevance_ok", "human_materiality_ok", "human_direction_ok",
        "human_event_type_ok", "human_evidence_span_ok",
    ]
    base = {"rows": len(frame), "filled_rows": 0, "checks": {}, "missing_columns": check_columns, "status": "unavailable"}
    available = [column for column in check_columns if column in frame]
    missing = [column for column in check_columns if column not in frame]
    if frame.empty or not available:
        return base
    normalized = frame[available].fillna("").astype(str).apply(lambda column: column.str.strip().str.lower())
    filled = normalized.ne("").any(axis=1)
    truthy = {"1", "true", "yes", "y", "ok", "đúng", "dung"}
    falsey = {"0", "false", "no", "n", "sai"}
    checks = {}
    for column in available:
        ok = int(normalized[column].isin(truthy).sum())
        not_ok = int(normalized[column].isin(falsey).sum())
        reviewed = ok + not_ok
        checks[column] = {
            "ok": ok, "not_ok": not_ok, "reviewed": reviewed,
            "ok_rate": ok / reviewed if reviewed else None,
        }
    status = "available" if not missing else "partial"
    return {**base, "filled_rows": int(filled.sum()), "checks": checks, "missing_columns": missing, "status": status}


def _classification_metrics(actual: pd.Series, predicted: pd.Series) -> tuple[float, float]:
    labels = sorted(set(actual.astype(str)) | set(predicted.astype(str)))
    accuracy = float((actual.astype(str) == predicted.astype(str)).mean())
    f1_values = []
    for label in labels:
        actual_label = actual.astype(str) == label
        predicted_label = predicted.astype(str) == label
        true_positive = int((actual_label & predicted_label).sum())
        false_positive = int((~actual_label & predicted_label).sum())
        false_negative = int((actual_label & ~predicted_label).sum())
        denominator = 2 * true_positive + false_positive + false_negative
        f1_values.append(0.0 if denominator == 0 else 2 * true_positive / denominator)
    return accuracy, sum(f1_values) / len(f1_values) if f1_values else 0.0


def rule_comparison_summary(rule_frame: pd.DataFrame, consensus_frame: pd.DataFrame) -> dict[str, Any]:
    pairs = [
        ("rule_direction", "consensus_direction"),
        ("rule_event_type", "consensus_event_type"),
        ("rule_materiality", "consensus_materiality"),
        ("rule_relevance", "consensus_ticker_relevance"),
    ]
    base = {"available": False, "compared_rows": 0, "metrics": []}
    keys = {"news_id", "ticker"}
    if rule_frame.empty or consensus_frame.empty or not keys.issubset(rule_frame.columns) or not keys.issubset(consensus_frame.columns):
        return base
    if "analysis_eligible" not in consensus_frame:
        return base
    eligible = bool_series(consensus_frame["analysis_eligible"])
    merged = rule_frame.merge(consensus_frame[eligible].copy(), on=["news_id", "ticker"], how="inner")
    metrics = []
    for rule_field, consensus_field in pairs:
        if rule_field not in merged or consensus_field not in merged:
            continue
        work = merged[[rule_field, consensus_field]].dropna()
        work = work[~work[consensus_field].astype(str).isin({"disagreement", "unclear"})]
        if work.empty:
            continue
        accuracy, macro_f1 = _classification_metrics(work[consensus_field], work[rule_field])
        metrics.append({
            "rule_field": rule_field,
            "consensus_field": consensus_field,
            "n": len(work),
            "accuracy": accuracy,
            "macro_f1": macro_f1,
        })
    return {"available": bool(metrics), "compared_rows": len(merged), "metrics": metrics}


def optional_robustness_summary(frames: dict[str, pd.DataFrame]) -> dict[str, Any]:
    placebo = frames.get("placebo", pd.DataFrame())
    paired = frames.get("ml_paired", pd.DataFrame())
    bootstrap = frames.get("ml_bootstrap", pd.DataFrame())
    topk_null = frames.get("topk_null", pd.DataFrame())
    topk_cost = frames.get("topk_cost", pd.DataFrame())
    family = frames.get("family_sensitivity", pd.DataFrame())

    ml_metrics: dict[str, dict[str, float | int | None | str]] = {}
    if not paired.empty and {"metric", "baseline_value", "comparison_value", "delta"}.issubset(paired.columns):
        dimensions = [col for col in ("baseline_config", "comparison_config", "model") if col in paired]
        group_columns = [*dimensions, "metric"]
        for key, group in paired.groupby(group_columns, dropna=False):
            values = key if isinstance(key, tuple) else (key,)
            identity = dict(zip(group_columns, values))
            metric_key = "|".join(str(identity[col]) for col in group_columns) if dimensions else str(identity["metric"])
            ml_metrics[metric_key] = {
                **identity,
                "rows": len(group),
                "baseline_mean": float(pd.to_numeric(group["baseline_value"], errors="coerce").mean()),
                "comparison_mean": float(pd.to_numeric(group["comparison_value"], errors="coerce").mean()),
                "delta_mean": float(pd.to_numeric(group["delta"], errors="coerce").mean()),
            }
    null_significant = None
    if not topk_null.empty and "one_sided_null_p_value" in topk_null:
        null_significant = int(pd.to_numeric(topk_null["one_sided_null_p_value"], errors="coerce").le(0.05).sum())
    cost_rates = []
    if not topk_cost.empty and "round_trip_cost_rate" in topk_cost:
        cost_rates = sorted(pd.to_numeric(topk_cost["round_trip_cost_rate"], errors="coerce").dropna().unique().tolist())
    return {
        "available": {name: not frame.empty for name, frame in frames.items()},
        "schema_versions": {name: schema_versions(frame) for name, frame in frames.items()},
        "placebo": event_test_summary(placebo),
        "ml_metrics": ml_metrics,
        "ml_bootstrap_rows": len(bootstrap),
        "topk_null_rows": len(topk_null),
        "topk_null_significant": null_significant,
        "topk_cost_rows": len(topk_cost),
        "topk_cost_rates": cost_rates,
        "family_sensitivity_rows": len(family),
    }


def validate_harmonized_manifest_artifacts(
    run_dir: Path,
    manifest: dict[str, Any],
    required_artifact_names: dict[str, set[str]],
) -> tuple[bool, bool, bool]:
    manifest_sections = ("code", "inputs", "outputs")
    entries_complete = all(isinstance(manifest.get(section), list) and manifest[section] for section in manifest_sections)
    section_names = {
        section: [Path(str(entry.get("path", ""))).name for entry in manifest.get(section, [])]
        for section in manifest_sections
    }
    artifact_membership_complete = entries_complete and all(
        len(section_names[section]) == len(set(section_names[section]))
        and set(section_names[section]) == required_artifact_names[section]
        for section in manifest_sections
    )
    run_identity_match = str(manifest.get("run_id", "")) == run_dir.name
    expected_paths = {
        "code": {
            "build_harmonized_comparison.py": STUDY_DIR / "scripts" / "build_harmonized_comparison.py",
            "run_harmonized_comparison.py": STUDY_DIR / "scripts" / "run_harmonized_comparison.py",
            "build_outperform_targets.py": STUDY_DIR / "scripts" / "build_outperform_targets.py",
            "common.py": STUDY_DIR / "scripts" / "common.py",
            "task8_keywords.py": STUDY_DIR.parent / "pipeline" / "task8_keywords.py",
            "task9_kw_features.py": STUDY_DIR.parent / "pipeline" / "task9_kw_features.py",
        },
        "inputs": {
            "harmonized_comparison_v5.json": STUDY_DIR / "config" / "harmonized_comparison_v5.json",
            "harmonized_build_manifest.json": run_dir / "harmonized_build_manifest.json",
            "harmonized_article_spine.csv": run_dir / "harmonized_article_spine.csv",
            "harmonized_panel.csv": run_dir / "harmonized_panel.csv",
            "harmonized_feature_manifest.csv": run_dir / "harmonized_feature_manifest.csv",
        },
        "outputs": {
            "harmonized_fold_manifest.csv": run_dir / "harmonized_fold_manifest.csv",
            "harmonized_fold_feature_manifest.csv": run_dir / "harmonized_fold_feature_manifest.csv",
            "harmonized_predictions.csv": run_dir / "harmonized_predictions.csv",
            "harmonized_fold_metrics.csv": run_dir / "harmonized_fold_metrics.csv",
            "harmonized_calibration.csv": run_dir / "harmonized_calibration.csv",
            "harmonized_paired_daily_deltas.csv": run_dir / "harmonized_paired_daily_deltas.csv",
            "harmonized_inference.csv": run_dir / "harmonized_inference.csv",
            "harmonized_topk_matched_deltas.csv": run_dir / "harmonized_topk_matched_deltas.csv",
            "harmonized_comparison_report.md": STUDY_DIR / "reports" / "harmonized" / run_dir.name / "harmonized_comparison_report.md",
            "canonical_summary.json": run_dir / "canonical_summary.json",
        },
    }
    manifest_hashes_match = artifact_membership_complete and run_identity_match
    if manifest_hashes_match:
        for section in manifest_sections:
            for entry in manifest[section]:
                raw_path = str(entry.get("path", ""))
                expected_hash = entry.get("sha256")
                name = Path(raw_path).name
                artifact = Path(raw_path)
                if not artifact.is_absolute():
                    artifact = STUDY_DIR.parent / artifact
                if artifact.resolve() != expected_paths[section][name].resolve():
                    manifest_hashes_match = False
                    break
                if not artifact.exists() or sha256_file(artifact) != expected_hash:
                    manifest_hashes_match = False
                    break
            if not manifest_hashes_match:
                break
        if manifest_hashes_match:
            try:
                from run_harmonized_comparison import load_and_validate_build_manifest
                load_and_validate_build_manifest(run_dir, run_dir.name, str(manifest.get("mode", "")))
            except (FileNotFoundError, ValueError, KeyError, OSError):
                manifest_hashes_match = False
    return entries_complete, artifact_membership_complete, manifest_hashes_match


def harmonized_run_summary(run_dir: Path | None) -> dict[str, Any]:
    base = {
        "available": False, "status": "missing", "mode": None, "run_id": None,
        "claim_level": None, "primary_gate_pass": False, "primary_rows": 0,
        "manifest_sha256": None, "inference_sha256": None,
    }
    if run_dir is None:
        return base
    manifest_path = run_dir / "harmonized_comparison_manifest.json"
    inference_path = run_dir / "harmonized_inference.csv"
    if not manifest_path.exists() or not inference_path.exists():
        return {**base, "status": "missing_or_incomplete", "run_dir": str(run_dir)}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {**base, "status": "invalid_manifest", "run_dir": str(run_dir)}
    inference = read_csv(inference_path)
    required = {
        "family", "baseline_config", "comparison_config", "model", "metric",
        "status", "p_value_bh", "bootstrap_ci_low",
    }
    if inference.empty or not required.issubset(inference.columns):
        return {**base, "status": "invalid_inference", "run_dir": str(run_dir)}
    primary = inference[
        inference["family"].eq("P1")
        & inference["baseline_config"].eq("B_technical_coverage_keyword")
        & inference["comparison_config"].eq("C_technical_coverage_semantic")
        & inference["model"].eq("RandomForest")
        & inference["metric"].eq("balanced_accuracy")
    ].copy()
    if len(primary) != 1:
        return {**base, "status": "invalid_primary_record", "run_dir": str(run_dir), "primary_rows": len(primary)}
    gate = (
        primary["status"].eq("ok")
        & pd.to_numeric(primary["p_value_bh"], errors="coerce").le(0.05)
        & pd.to_numeric(primary["bootstrap_ci_low"], errors="coerce").gt(0)
    )
    inference_gate = bool(gate.iloc[0])
    mode = manifest.get("mode")
    claim_level = manifest.get("claim_level")
    prohibited_full_claim = mode in {"pilot", "sample500"} and claim_level == "full_corpus"
    required_artifact_names = {
        "code": {
            "build_harmonized_comparison.py", "run_harmonized_comparison.py",
            "build_outperform_targets.py", "common.py",
            "task8_keywords.py", "task9_kw_features.py",
        },
        "inputs": {
            "harmonized_comparison_v5.json", "harmonized_build_manifest.json",
            "harmonized_article_spine.csv", "harmonized_panel.csv",
            "harmonized_feature_manifest.csv",
        },
        "outputs": {
            "harmonized_fold_manifest.csv", "harmonized_fold_feature_manifest.csv",
            "harmonized_predictions.csv", "harmonized_fold_metrics.csv",
            "harmonized_calibration.csv", "harmonized_paired_daily_deltas.csv",
            "harmonized_inference.csv", "harmonized_topk_matched_deltas.csv",
            "harmonized_comparison_report.md", "canonical_summary.json",
        },
    }
    entries_complete, artifact_membership_complete, manifest_hashes_match = validate_harmonized_manifest_artifacts(
        run_dir, manifest, required_artifact_names
    )
    output_entry = next(
        (
            entry for entry in manifest.get("outputs", [])
            if Path(str(entry.get("path", ""))).name == inference_path.name
        ),
        None,
    )
    output_hash_match = bool(output_entry) and output_entry.get("sha256") == sha256_file(inference_path)
    manifest_completed = manifest.get("status") == "completed"
    canonical = manifest.get("run_tier") == "canonical"
    audit_gate = manifest.get("coverage_audit_pass") is True and manifest.get("fold_audit_pass") is True
    declared_gate = manifest.get("primary_gate_any") is True and manifest.get("thesis_evidence_gate") is True
    gate_consistent = manifest.get("primary_gate_any") is inference_gate
    primary_gate_pass = all((manifest_hashes_match, output_hash_match, not prohibited_full_claim, manifest_completed, canonical, audit_gate, declared_gate, gate_consistent, inference_gate))
    if not entries_complete or not artifact_membership_complete:
        status = "incomplete_manifest_artifacts"
    elif not manifest_hashes_match:
        status = "manifest_artifact_hash_mismatch"
    elif not output_hash_match:
        status = "output_hash_mismatch"
    elif prohibited_full_claim:
        status = "invalid_claim_level"
    elif not manifest_completed:
        status = "incomplete_run"
    elif not canonical:
        status = "smoke_not_evidence" if manifest.get("run_tier") == "smoke" else "invalid_run_tier"
    elif not audit_gate:
        status = "audit_gate_failed"
    elif not gate_consistent:
        status = "gate_mismatch"
    elif not declared_gate or not inference_gate:
        status = "primary_gate_failed"
    else:
        status = "ok"
    return {
        **base, "available": True, "status": status,
        "mode": mode, "run_id": manifest.get("run_id"), "claim_level": claim_level,
        "run_tier": manifest.get("run_tier"), "primary_gate_pass": primary_gate_pass,
        "primary_rows": len(primary), "manifest_sha256": sha256_file(manifest_path),
        "inference_sha256": sha256_file(inference_path), "run_dir": str(run_dir),
    }


def build_artifact_snapshot(output_dir: Path = OUTPUT_DIR, data_dir: Path = DATA_DIR, harmonized_run_dir: Path | None = None) -> dict[str, Any]:
    paths = {
        "consensus": output_dir / "pseudo_labels_consensus.csv",
        "event_tests": output_dir / "event_window_stat_tests.csv",
        "ml_predictions": output_dir / "ml_predictions_outperform.csv",
        "topk": output_dir / "topk_portfolio_simulation.csv",
        "placebo": output_dir / "placebo_pre_event_stat_tests.csv",
        "ml_paired": output_dir / "ml_paired_daily_metrics_outperform.csv",
        "ml_bootstrap": output_dir / "ml_bootstrap_delta_outperform.csv",
        "topk_null": output_dir / "topk_random_null_summary.csv",
        "topk_cost": output_dir / "topk_cost_sensitivity_summary.csv",
        "family_sensitivity": output_dir / "consensus_family_sensitivity_summary.csv",
    }
    count_paths = {
        "annotation_sample": data_dir / "sample_news_for_annotation.csv", "consensus_labels": paths["consensus"],
        "rule_labels": output_dir / "rule_labels.csv", "semantic_daily": output_dir / "semantic_features_daily.csv",
        "event_windows": output_dir / "event_window_outcomes.csv", "event_tests": paths["event_tests"],
        "ml_predictions": paths["ml_predictions"], "topk_rows": paths["topk"],
        "case_candidates": output_dir / "case_study_candidates.csv", "outcome_reviews": output_dir / "outcome_review_labels.csv",
    }
    consensus = read_csv(paths["consensus"])
    event = read_csv(paths["event_tests"])
    ml = read_csv(paths["ml_predictions"])
    topk = read_csv(paths["topk"])
    robustness_frames = {name: read_csv(paths[name]) for name in (
        "placebo", "ml_paired", "ml_bootstrap", "topk_null", "topk_cost", "family_sensitivity"
    )}
    manual = read_csv(data_dir / "manual_sanity_check_sample.csv")
    rule_labels = read_csv(output_dir / "rule_labels.csv")
    return {
        "counts": {key: row_count(path) for key, path in count_paths.items()},
        "consensus": consensus_summary(consensus), "provenance": annotation_provenance(output_dir),
        "agreement": agreement_summary(output_dir), "manual_sanity": manual_sanity_summary(manual),
        "rule_comparison": rule_comparison_summary(rule_labels, consensus),
        "event_tests": event_test_summary(event), "ml": ml_fold_summary(ml), "topk": topk_summary(topk),
        "robustness": optional_robustness_summary(robustness_frames),
        "harmonized": harmonized_run_summary(harmonized_run_dir),
        "artifacts": {
            "consensus": artifact_metadata(paths["consensus"], [output_dir / f"labels_annotator_{x}.jsonl" for x in "abc"]),
            "event_tests": artifact_metadata(paths["event_tests"], [output_dir / "event_window_outcomes.csv"]),
            "ml_predictions": artifact_metadata(paths["ml_predictions"], [output_dir / "ml_panel_outperform.csv"]),
            "topk": artifact_metadata(paths["topk"], [paths["ml_predictions"], output_dir / "outperform_targets.csv"]),
            **{name: artifact_metadata(paths[name]) for name in robustness_frames},
        },
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    clean = lambda value: "unavailable" if value is None else str(value).replace("|", "\\|").replace("\n", " ")
    return "\n".join([
        "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |",
        *("| " + " | ".join(clean(value) for value in row) + " |" for row in rows),
    ])


def render_claim_evidence_table(snapshot: dict[str, Any]) -> str:
    consensus, event, ml, topk = snapshot["consensus"], snapshot["event_tests"], snapshot["ml"], snapshot["topk"]
    methods = ", ".join(f"{k}={v}" for k, v in sorted(consensus["methods"].items())) or "unavailable"
    robust_fraction = f"{event['robust_results']}/{event['rows']}" if event["rows"] else "0/0"
    claims = [
        ["Keyword/news-count thiếu ngữ cảnh", "reports/rule_vs_semantic_labels_report.md", "Rule baseline versus semantic pseudo-labels; not human ground truth", "Supported exploratory"],
        ["Annotation provenance", "outputs/annotation_manifest_*.json", f"manifest runs={len(snapshot['provenance'])}; provider, routed model vendor, and hashes below", "Descriptive limitation"],
        ["Consensus categorical labels", "outputs/pseudo_labels_consensus.csv", f"rows={consensus['rows']}; {methods}; eligible={consensus['eligible']}/{consensus['rows']}", "Descriptive"],
        ["Semantic event-window association", "outputs/event_window_stat_tests.csv", f"joint positive gate={robust_fraction}; FDR rows={event['fdr_significant']}; positive-CI rows={event['positive_ci']}; flag mismatches={event['reported_flag_mismatches']}", "Supported exploratory association" if event["claim_gate_pass"] else "No robust positive association after correction"],
        ["Point-in-time ML ranking", "outputs/ml_predictions_outperform.csv", f"rows={ml['rows']}; folds={ml['fold_count']}; purge={ml['purge_trading_days']}; status={ml['status']}; near-random metrics and paired deltas reported when available", "Exploratory" if ml["purged_oos_verified"] else "Metadata check failed"],
        ["Top-K simulation", "outputs/topk_portfolio_simulation.csv", f"rows={topk['rows']}; periods={topk['periods']}; non-overlap={topk['non_overlapping']}; turnover-cost={topk['turnover_cost_verified']}; net equations={topk['net_return_verified']}; random-null and cost sensitivity are required for performance interpretation", "Null/weak exploratory result" if topk["status"].startswith("verified") else "Methodology check failed"],
        ["Evidence cards and outcome review", "outputs/evidence_cards.*, outputs/outcome_review_labels.csv", f"outcome-review rows={snapshot['counts']['outcome_reviews']}; retrospective structured review only", "Technical traceability; not decision quality or ground truth"],
    ]
    rq_h_rows = [
        ["RQ-SM1", "H-SM1", "Representation limits", "rule comparison + error taxonomy", "Associational/descriptive"],
        ["RQ-SM2", "H-SM2", "Semantic schema and pseudo-label stability", "consensus + agreement + manual sanity", "Descriptive; 3 runs, 2 model families"],
        ["RQ-SM3", "H-SM3", "Outcome association", "event tests + placebo", "Exploratory association, not causal"],
        ["RQ-SM4", "H-SM4", "ML/ranking increment", "purged OOS metrics + paired/bootstrap deltas", "Secondary exploratory"],
        ["RQ-SM5", "H-SM5", "Top-K filtering", "random null + cost sensitivity", "Secondary exploratory; no alpha claim"],
        ["RQ-SM6", "H-SM6", "Evidence traceability", "cards + lineage + outcome review", "Technical traceability only"],
    ]
    provenance = [[row[key] for key in ("annotator", "api_provider", "requested_model", "response_models", "model_vendor", "route_mode", "provenance_status", "schema_version", "labels_hash_match", "input_sha256", "schema_sha256")] for row in snapshot["provenance"]]
    robustness = snapshot.get("robustness", {"schema_versions": {}})
    summary_schemas = {
        "consensus": consensus["schema_versions"], "event_tests": event["schema_versions"],
        "ml_predictions": ml["schema_versions"], "topk": topk["schema_versions"],
        **robustness.get("schema_versions", {}),
    }
    artifacts = [[name, ", ".join(summary_schemas.get(name, [])) or "unavailable", meta["sha256"], meta["modified_utc"], meta["latest_upstream_utc"], meta["freshness"]] for name, meta in snapshot["artifacts"].items()]
    folds = [[fold.get(key) for key in ("fold_id", "train_start", "train_end", "test_start", "test_end", "purge_trading_days")] for fold in ml["folds"]]
    return "\n".join([
        "# Claim vs evidence table", "", markdown_table(["Claim luận văn", "Evidence artifact", "Corrected result", "Claim level"], claims), "",
        "## RQ–hypothesis–evidence matrix", "", markdown_table(["Research question", "Hypothesis", "Focus", "Evidence", "Allowed interpretation"], rq_h_rows), "",
        "## Corrected event claim gate", "", f"Rule: `{event['gate_rule']}`. Available={event['gate_available']}; pass={event['claim_gate_pass']}; joint-positive fraction={robust_fraction}.", "",
        "## Annotator provenance", "", markdown_table(["annotator", "API provider", "requested", "response", "vendor", "route", "status", "schema", "label hash match", "input SHA256", "schema SHA256"], provenance) if provenance else "_No provenance manifests available._", "",
        "## Artifact integrity and freshness", "", markdown_table(["artifact", "schema version", "SHA256", "modified UTC", "latest upstream UTC", "freshness"], artifacts), "",
        "## Purged OOS fold metadata", "", markdown_table(["fold", "train start", "train end", "test start", "test end", "purge trading days"], folds) if folds else "_Fold metadata unavailable._", "",
        "## Optional robustness readers", "",
        f"Available={robustness.get('available', {})}; placebo robust-positive={robustness.get('placebo', {}).get('robust_results', 0)}/{robustness.get('placebo', {}).get('rows', 0)}; ML metrics/deltas={robustness.get('ml_metrics', {})}; ML bootstrap rows={robustness.get('ml_bootstrap_rows', 0)}; Top-K null significant={robustness.get('topk_null_significant')}/{robustness.get('topk_null_rows', 0)}; cost rows={robustness.get('topk_cost_rows', 0)} at rates={robustness.get('topk_cost_rates', [])}; family-sensitivity rows={robustness.get('family_sensitivity_rows', 0)}.", "",
        "Missing optional files remain unavailable and do not block core report generation.", "",
        "## Safe interpretation", "", "Consensus labels are pseudo-labels, not ground truth. Three annotation runs represent only two model families, not three independent systems. Manual review is a small quality-control sample. Outcome review is retrospective structured review, not semantic ground truth or decision-quality validation. Event-study reports associations, not causal effects. ML and Top-K results remain exploratory; near-random metrics, null comparisons, and transaction costs preclude alpha or investment claims.", "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Write claim-evidence report from structured artifacts.")
    parser.add_argument("--harmonized-run-dir", type=Path)
    args = parser.parse_args()
    ensure_dirs()
    OUT.write_text(
        render_claim_evidence_table(build_artifact_snapshot(harmonized_run_dir=args.harmonized_run_dir)),
        encoding="utf-8",
    )
    print(f"saved {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
