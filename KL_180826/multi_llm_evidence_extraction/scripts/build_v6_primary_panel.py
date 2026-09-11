"""Build the fail-closed V6 prospective primary panel.

New V6 runs resolve every source beneath an explicit workspace root, validate all
protocol hashes before loading data, and publish immutable provenance manifests.
The locked historical run is read only and is audited separately.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_outperform_targets import build_session_aligned_targets
from build_v6_source_status_audit import (
    STATUS_VALUES,
    build_source_status_audit,
    source_status_summary,
)
from common import ROOT, STUDY_DIR, resolve_scoped_path, sha256_file, utc_now, validate_safe_identifier
from v6_artifacts import (
    INTENT_MANIFEST,
    V6ArtifactError,
    load_required_manifest,
    portable_path,
    prepare_v6_run,
    resolve_workspace_path,
    validate_declared_inputs,
    validate_target_manifest,
    validate_v6_run_id as validate_v6_artifact_run_id,
    write_target_manifest,
    write_v6_build_manifest,
    write_v6_failure_manifest,
)

WORKSPACE_ROOT = ROOT.parent
SPEC_PATH = STUDY_DIR / "config" / "v6_technical_primary_v1.json"
V6_CODE_PATHS = (
    Path(__file__).resolve(),
    SCRIPT_DIR / "run_v6_technical_primary.py",
    SCRIPT_DIR / "build_outperform_targets.py",
    SCRIPT_DIR / "build_v6_source_status_audit.py",
    SCRIPT_DIR / "common.py",
    SCRIPT_DIR / "v6_artifacts.py",
)


class V6WorkspacePaths(dict[str, Any]):
    """Resolved V6 protocol inputs together with their validated hash ledger."""

    @property
    def root(self) -> Path:
        return Path(self["__workspace_root__"])

    @property
    def ledger(self) -> dict[str, dict[str, str]]:
        return dict(self["__ledger__"])


def resolve_v6_workspace_root(value: Path | None = None) -> Path:
    root = (value or WORKSPACE_ROOT).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"V6 workspace root is missing: {root}")
    return root


def resolve_v6_protocol_path(workspace_root: Path | None = None) -> Path:
    return resolve_workspace_path(
        resolve_v6_workspace_root(workspace_root),
        "KL_180826/multi_llm_evidence_extraction/config/v6_technical_primary_v1.json",
        field="protocol",
    )


def load_v6_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise V6ArtifactError(f"V6 protocol must be a JSON object: {path}")
    return value


def resolve_v6_inputs(spec: dict[str, Any], workspace_root: Path | None = None) -> V6WorkspacePaths:
    root = resolve_v6_workspace_root(workspace_root)
    ledger = validate_declared_inputs(spec, root)
    result = V6WorkspacePaths(
        {
            name: resolve_workspace_path(root, entry["path"], field=f"input_paths.{name}")
            for name, entry in ledger.items()
        }
    )
    result["__workspace_root__"] = root
    result["__ledger__"] = ledger
    return result


def validate_v6_run_id(run_id: str, spec: dict[str, Any]) -> str:
    return validate_v6_artifact_run_id(run_id, spec)


def v6_output_dirs(run_id: str, workspace_root: Path | None = None) -> tuple[Path, Path]:
    root = resolve_v6_workspace_root(workspace_root)
    study_dir = resolve_v6_protocol_path(root).parent.parent
    return (
        resolve_scoped_path(study_dir / "outputs" / "v6_primary", run_id),
        resolve_scoped_path(study_dir / "reports" / "v6_primary", run_id),
    )


def resolve_input_path(raw: str, workspace_root: Path | None = None) -> Path:
    """Compatibility helper that only resolves below the explicit workspace root."""
    return resolve_workspace_path(resolve_v6_workspace_root(workspace_root), raw, field="input path")


def _assert_output_inside_workspace(workspace_root: Path, path: Path, field: str) -> Path:
    resolved = Path(path).resolve()
    portable_path(workspace_root, resolved)
    return resolved


def _workspace_copy_of(local_path: Path, workspace_root: Path) -> Path:
    try:
        relative = local_path.resolve().relative_to(WORKSPACE_ROOT.resolve())
    except ValueError:
        return local_path.resolve()
    candidate = (workspace_root / relative).resolve()
    return candidate if candidate.is_file() else local_path.resolve()


def _v6_code_paths(workspace_root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in V6_CODE_PATHS:
        candidate = _workspace_copy_of(path, workspace_root)
        if candidate.is_file():
            paths.append(candidate)
    return paths


def _build_output_paths(output_dir: Path) -> list[Path]:
    names = (
        "v6_primary_panel.csv",
        "v6_feature_manifest.csv",
        "v6_row_manifest.csv",
        "v6_coverage_audit.csv",
        "v6_source_status_audit.csv",
        "v6_source_status_errors.csv",
        "v6_build_summary.json",
    )
    return [output_dir / name for name in names]


def quarter_id_from_dates(dates: pd.Series) -> pd.Series:
    return pd.to_datetime(dates).dt.to_period("Q").astype(str)


def lag_quarterly_features(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    work = frame.copy()
    work["ticker"] = work["ticker"].astype(str).str.upper()
    work["quarter_id"] = (pd.PeriodIndex(work["quarter_id"].astype(str), freq="Q") + 1).astype(str)
    return work.rename(columns={column: f"{prefix}{column}" for column in work.columns if column not in {"ticker", "quarter_id"}})


def _coverage_names(spec: dict[str, Any]) -> set[str]:
    policy = spec.get("coverage_policy", {})
    return set(policy.get("keyword_columns", [])) | set(policy.get("semantic_columns", []))


def _tfidf_prefixes(spec: dict[str, Any]) -> tuple[str, ...]:
    return tuple(spec.get("keyword_feature_policy", {}).get("excluded_prefixes", ("tfidf_",)))


def _is_tfidf(name: str, prefixes: tuple[str, ...]) -> bool:
    return any(name.startswith(prefix) for prefix in prefixes)


def _strip_prefix(name: str, prefixes: tuple[str, ...]) -> str:
    for prefix in prefixes:
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


def normalize_targets(targets: pd.DataFrame) -> pd.DataFrame:
    work = targets.copy()
    if "date" not in work and "entry_date" in work:
        work["date"] = work["entry_date"]
    if "entry_date" not in work and "date" in work:
        work["entry_date"] = work["date"]
    work["date"] = pd.to_datetime(work["date"], errors="coerce").dt.normalize()
    work["entry_date"] = pd.to_datetime(work["entry_date"], errors="coerce").dt.normalize()
    work["target_exit_date"] = pd.to_datetime(work.get("target_exit_date"), errors="coerce").dt.normalize()
    if "target_status" not in work:
        work["target_status"] = np.where(work["label_outperform_T20"].notna(), "ok", "missing_label")
    work["ticker"] = work["ticker"].astype(str).str.upper()
    work["quarter_id"] = quarter_id_from_dates(work["date"])
    return work


def _merge_source_status(panel: pd.DataFrame, source_status: pd.DataFrame) -> pd.DataFrame:
    required = {"ticker", "date", "source_status"}
    missing = required - set(source_status.columns)
    if missing:
        raise V6ArtifactError(f"V6 source-status audit missing columns: {sorted(missing)}")
    audit = source_status[["ticker", "date", "source_status"]].copy()
    audit["ticker"] = audit["ticker"].astype(str).str.upper()
    audit["date"] = pd.to_datetime(audit["date"], errors="coerce").dt.normalize()
    if audit[["ticker", "date"]].isna().any().any() or audit.duplicated(["ticker", "date"]).any():
        raise V6ArtifactError("V6 source-status audit has invalid or duplicate ticker/date rows")
    if not audit["source_status"].isin(STATUS_VALUES).all():
        raise V6ArtifactError("V6 source-status audit has unknown status values")
    merged = panel.merge(
        audit.rename(columns={"source_status": "semantic_source_status"}),
        on=["ticker", "date"],
        how="left",
        validate="many_to_one",
    )
    if merged["semantic_source_status"].isna().any():
        raise V6ArtifactError("V6 source-status audit does not cover every panel row")
    return merged


def build_v6_primary_panel(
    targets: pd.DataFrame,
    technical: pd.DataFrame,
    keyword: pd.DataFrame,
    semantic: pd.DataFrame,
    spec: dict[str, Any],
    source_status: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build V6 features, zero-filling only rows verified as no valid news."""
    panel = normalize_targets(targets)
    coverage = _coverage_names(spec)
    tfidf_prefixes = _tfidf_prefixes(spec)

    tech = lag_quarterly_features(technical, "tech_lag1q__") if not technical.empty else technical
    keyword_lag = lag_quarterly_features(keyword, "kw_lag1q__") if not keyword.empty else keyword
    if not tech.empty:
        panel = panel.merge(tech, on=["ticker", "quarter_id"], how="left")
    if not keyword_lag.empty:
        panel = panel.merge(keyword_lag, on=["ticker", "quarter_id"], how="left")

    semantic_daily = semantic.copy()
    if not semantic_daily.empty:
        semantic_daily["ticker"] = semantic_daily["ticker"].astype(str).str.upper()
        semantic_daily["date"] = pd.to_datetime(semantic_daily["date"], errors="coerce").dt.normalize()
        semantic_daily = semantic_daily.drop(columns=["artifact_schema_version"], errors="ignore")
        semantic_daily = semantic_daily.rename(
            columns={column: f"sem_daily__{column}" for column in semantic_daily.columns if column not in {"ticker", "date"}}
        )
        panel = panel.merge(semantic_daily, on=["ticker", "date"], how="left")

    if source_status is not None:
        panel = _merge_source_status(panel, source_status)

    tech_columns = [column for column in panel.columns if column.startswith("tech_lag1q__")]
    keyword_columns = [column for column in panel.columns if column.startswith("kw_lag1q__")]
    semantic_columns = [column for column in panel.columns if column.startswith("sem_daily__")]
    panel["technical_available"] = panel[tech_columns].notna().any(axis=1) if tech_columns else False
    panel["panel_eligible"] = panel["target_status"].eq("ok") & panel["technical_available"]

    keyword_present = panel[keyword_columns].notna().any(axis=1) if keyword_columns else pd.Series(False, index=panel.index)
    panel["keyword_feature_status"] = np.where(keyword_present, "present", "no_news_zero_filled")

    semantic_predictors = [
        column
        for column in semantic_columns
        if _strip_prefix(column, ("sem_daily__",)) not in coverage
    ]
    keyword_predictors = [
        column
        for column in keyword_columns
        if _strip_prefix(column, ("kw_lag1q__",)) not in coverage
        and not _is_tfidf(_strip_prefix(column, ("kw_lag1q__",)), tfidf_prefixes)
    ]

    if source_status is None:
        semantic_present = panel[semantic_columns].notna().any(axis=1) if semantic_columns else pd.Series(False, index=panel.index)
        panel["semantic_feature_status"] = np.where(semantic_present, "present", "no_news_zero_filled")
        for column in semantic_predictors:
            panel[column] = pd.to_numeric(panel[column], errors="coerce").fillna(0.0)
    else:
        valid_event = panel["semantic_source_status"].eq("valid_source_event")
        verified_no_news = panel["semantic_source_status"].eq("no_valid_news")
        source_error = ~(valid_event | verified_no_news)
        panel["semantic_feature_status"] = np.select(
            [valid_event, verified_no_news],
            ["present", "no_news_zero_filled"],
            default="source_error_" + panel["semantic_source_status"].astype(str),
        )
        if semantic_predictors and panel.loc[valid_event, semantic_predictors].isna().any(axis=None):
            raise V6ArtifactError("valid semantic source event has missing semantic predictor values")
        for column in semantic_predictors:
            values = pd.to_numeric(panel[column], errors="coerce")
            panel.loc[verified_no_news, column] = values.loc[verified_no_news].fillna(0.0)
            panel.loc[valid_event, column] = values.loc[valid_event]
        # The V6 protocol permits source errors only when explicitly auditable.
        # A primary-eligible row with an unknown semantic source cannot silently
        # become zero or fold-imputed, so new primary builds fail closed.
        if bool((panel["panel_eligible"] & source_error).any()):
            counts = panel.loc[panel["panel_eligible"] & source_error, "semantic_source_status"].value_counts().to_dict()
            raise V6ArtifactError(f"V6 eligible rows have unresolved semantic source status: {counts}")

    for column in keyword_predictors:
        panel[column] = pd.to_numeric(panel[column], errors="coerce").fillna(0.0)

    panel["row_id"] = (
        panel["ticker"].astype(str)
        + "|"
        + panel["date"].dt.strftime("%Y-%m-%d")
        + "|"
        + panel["target_exit_date"].dt.strftime("%Y-%m-%d").fillna("NA")
    )
    panel["artifact_schema_version"] = "v6_primary_panel_v2" if source_status is not None else "v6_primary_panel_v1"
    return panel.sort_values(["ticker", "date"]).reset_index(drop=True)


def build_feature_manifest(panel: pd.DataFrame, spec: dict[str, Any]) -> pd.DataFrame:
    coverage = _coverage_names(spec)
    tfidf_prefixes = _tfidf_prefixes(spec)
    rows: list[dict[str, Any]] = []

    def add_rows(columns: list[str], family: str, prefix: str, configs: list[str]) -> None:
        for column in columns:
            source = _strip_prefix(column, (prefix,))
            is_coverage = source in coverage
            is_tfidf = family == "keyword" and _is_tfidf(source, tfidf_prefixes)
            rows.append(
                {
                    "feature": column,
                    "source_feature": source,
                    "family": family,
                    "predictor": not is_coverage and not is_tfidf,
                    "configs": json.dumps(configs if not is_coverage and not is_tfidf else []),
                    "exclusion_reason": "coverage_audit_only" if is_coverage else "precomputed_full_corpus_tfidf" if is_tfidf else "",
                }
            )

    add_rows([column for column in panel if column.startswith("tech_lag1q__")], "technical", "tech_lag1q__", ["A_technical", "B_technical_keyword", "C_technical_semantic"])
    add_rows([column for column in panel if column.startswith("kw_lag1q__")], "keyword", "kw_lag1q__", ["B_technical_keyword"])
    add_rows([column for column in panel if column.startswith("sem_daily__")], "semantic", "sem_daily__", ["C_technical_semantic"])
    return pd.DataFrame(rows)


def build_coverage_audit(panel: pd.DataFrame) -> pd.DataFrame:
    work = panel.copy()
    work["has_keyword"] = work.get("keyword_feature_status", pd.Series("", index=work.index)).eq("present")
    work["has_semantic"] = work.get("semantic_feature_status", pd.Series("", index=work.index)).eq("present")
    work["semantic_source_error"] = work.get("semantic_feature_status", pd.Series("", index=work.index)).astype(str).str.startswith("source_error_")
    return work.groupby("ticker", as_index=False).agg(
        rows=("date", "size"),
        eligible=("panel_eligible", "sum"),
        keyword_present=("has_keyword", "sum"),
        semantic_present=("has_semantic", "sum"),
        no_news_keyword=("keyword_feature_status", lambda values: int(values.eq("no_news_zero_filled").sum())),
        no_news_semantic=("semantic_feature_status", lambda values: int(values.eq("no_news_zero_filled").sum())),
        semantic_source_errors=("semantic_source_error", "sum"),
    )


def _alias_horizon_columns(targets: pd.DataFrame, horizon: int) -> pd.DataFrame:
    work = targets.copy()
    for source, alias in {
        f"stock_return_T{horizon}": "stock_return_T20",
        f"VNINDEX_return_T{horizon}": "VNINDEX_return_T20",
        f"excess_return_T{horizon}": "excess_return_T20",
        f"label_outperform_T{horizon}": "label_outperform_T20",
    }.items():
        if source in work:
            work[alias] = work[source]
    return work


def ensure_targets(
    spec: dict[str, Any],
    output_dir: Path,
    inputs: V6WorkspacePaths,
    workspace_root: Path,
    horizon: int = 20,
) -> tuple[pd.DataFrame, Path]:
    horizon = int(horizon)
    target_path = output_dir / "v6_outperform_targets.csv"
    target_builder = _workspace_copy_of(SCRIPT_DIR / "build_outperform_targets.py", workspace_root)
    if target_path.exists():
        target_manifest = validate_target_manifest(target_path, workspace_root, inputs.ledger, target_builder, horizon)
        cached = pd.read_csv(target_path, encoding="utf-8-sig")
        values = pd.to_numeric(cached.get("horizon_benchmark_sessions", pd.Series(dtype=float)), errors="coerce").dropna().unique()
        if len(values) == 1 and int(values[0]) != horizon:
            raise V6ArtifactError(f"cached V6 targets use horizon={int(values[0])}, expected={horizon}")
        return _alias_horizon_columns(cached, horizon), target_manifest

    targets = build_session_aligned_targets(
        pd.read_csv(inputs["prices"], encoding="utf-8"),
        pd.read_csv(inputs["benchmark"], encoding="utf-8"),
        horizon=horizon,
    )
    targets = _alias_horizon_columns(targets, horizon)
    if "date" not in targets:
        targets = targets.rename(columns={"entry_date": "date"})
    if "entry_date" not in targets:
        targets["entry_date"] = targets["date"]
    targets.to_csv(target_path, index=False, encoding="utf-8-sig")
    return targets, write_target_manifest(target_path, workspace_root, inputs.ledger, target_builder, horizon)


def _normalize_sensitivity_tag(tag: str | None) -> str | None:
    if tag is None:
        return None
    text = str(tag).strip().lower().replace(" ", "_")
    return validate_safe_identifier(text, "sensitivity_tag") if text else None


def _claim_level(horizon: int, sensitivity_tag: str | None, semantic_daily: str | Path | None, spec: dict[str, Any]) -> tuple[str, list[str]]:
    tag = _normalize_sensitivity_tag(sensitivity_tag)
    is_horizon = int(horizon) != 20
    is_feature = tag is not None or semantic_daily is not None
    if tag:
        level = f"v6_sensitivity_{tag}"
    elif is_horizon:
        level = f"v6_sensitivity_horizon_T{int(horizon)}"
    elif is_feature:
        level = "v6_sensitivity_densified_cache_semantic"
    else:
        level = str(spec["claim_level"])
    limitations: list[str] = []
    if is_horizon or is_feature:
        limitations.extend(["sensitivity_only_not_v6_primary", "does_not_replace_v6_primary_20260909"])
    if is_horizon:
        limitations.append(f"horizon_T{int(horizon)}_not_locked_primary_T20")
    if is_feature:
        limitations.extend(["single_model_cache_not_multi_llm_consensus", "adapter_approximates_consensus_schema"])
    return level, limitations


def write_build_artifacts(
    output_dir: Path,
    report_dir: Path,
    run_id: str,
    spec: dict[str, Any],
    horizon: int = 20,
    semantic_daily: str | Path | None = None,
    sensitivity_tag: str | None = None,
    *,
    workspace_root: Path | None = None,
    reserve_run: bool = True,
) -> dict[str, Any]:
    """Build one new V6 panel and write its immutable build manifest."""
    root = resolve_v6_workspace_root(workspace_root)
    output = _assert_output_inside_workspace(root, output_dir, "output directory")
    report = _assert_output_inside_workspace(root, report_dir, "report directory")
    inputs = resolve_v6_inputs(spec, root)
    protocol_path = resolve_v6_protocol_path(root)
    safe_run = validate_v6_run_id(run_id, spec)
    if reserve_run:
        prepare_v6_run(
            safe_run,
            spec,
            output,
            report,
            root,
            inputs.ledger,
            protocol_path=protocol_path,
            horizon=int(horizon),
            sensitivity_tag=sensitivity_tag,
        )
    else:
        intent = load_required_manifest(output, INTENT_MANIFEST)
        if intent.get("run_id") != safe_run:
            raise V6ArtifactError("V6 build requires an already-reserved matching intent manifest")
        if any(path.exists() for path in _build_output_paths(output)):
            raise V6ArtifactError("V6 build destination already contains immutable artifacts")
        if not report.is_dir():
            raise V6ArtifactError("V6 build requires an already-reserved report directory")

    try:
        prices = pd.read_csv(inputs["prices"], encoding="utf-8")
        matched = pd.read_csv(inputs["news_matched"], encoding="utf-8")
        processed = pd.read_csv(inputs["news_processed"], encoding="utf-8")
        consensus = pd.read_csv(inputs["semantic_consensus"], encoding="utf-8-sig")
        status_audit, status_errors = build_source_status_audit(prices, matched, processed, consensus)
        status_path = output / "v6_source_status_audit.csv"
        status_errors_path = output / "v6_source_status_errors.csv"
        if status_path.exists() or status_errors_path.exists():
            raise V6ArtifactError("refusing to overwrite existing V6 source-status artifacts")
        status_audit.to_csv(status_path, index=False, encoding="utf-8-sig")
        status_errors.to_csv(status_errors_path, index=False, encoding="utf-8-sig")

        targets, target_manifest = ensure_targets(spec, output, inputs, root, horizon=horizon)
        technical = pd.read_csv(inputs["technical"], encoding="utf-8")
        keyword = pd.read_csv(inputs["keyword"], encoding="utf-8")
        semantic_path = inputs["semantic_daily"] if semantic_daily is None else resolve_workspace_path(root, str(semantic_daily), field="semantic-daily override")
        if semantic_daily is not None and sha256_file(semantic_path) != inputs.ledger["semantic_daily"]["sha256"]:
            raise V6ArtifactError("semantic-daily override requires a separately versioned sensitivity protocol")
        semantic = pd.read_csv(semantic_path, encoding="utf-8-sig")
        panel = build_v6_primary_panel(targets, technical, keyword, semantic, spec, source_status=status_audit)

        feature_manifest = build_feature_manifest(panel, spec)
        coverage = build_coverage_audit(panel)
        row_columns = [
            name
            for name in (
                "row_id", "ticker", "date", "target_exit_date", "target_status", "panel_eligible",
                "technical_available", "keyword_feature_status", "semantic_feature_status",
                "semantic_source_status",
            )
            if name in panel
        ]
        panel_path = output / "v6_primary_panel.csv"
        feature_path = output / "v6_feature_manifest.csv"
        row_path = output / "v6_row_manifest.csv"
        coverage_path = output / "v6_coverage_audit.csv"
        for path in (panel_path, feature_path, row_path, coverage_path, output / "v6_build_summary.json", report / "v6_build_summary.md"):
            if path.exists():
                raise V6ArtifactError(f"refusing to overwrite existing V6 build artifact: {path.name}")
        panel.to_csv(panel_path, index=False, encoding="utf-8-sig")
        feature_manifest.to_csv(feature_path, index=False, encoding="utf-8-sig")
        panel[row_columns].to_csv(row_path, index=False, encoding="utf-8-sig")
        coverage.to_csv(coverage_path, index=False, encoding="utf-8-sig")

        claim_level, limitations = _claim_level(horizon, sensitivity_tag, semantic_daily, spec)
        summary = {
            "artifact_schema_version": "v6_primary_build_summary_v3",
            "generated_at_utc": utc_now(),
            "run_id": safe_run,
            "protocol_version": spec["protocol_version"],
            "protocol_path": portable_path(root, protocol_path),
            "protocol_sha256": sha256_file(protocol_path),
            "claim_level": claim_level,
            "horizon_benchmark_sessions": int(horizon),
            "semantic_daily": {"path": portable_path(root, semantic_path), "sha256": sha256_file(semantic_path)},
            "n_rows": int(len(panel)),
            "n_eligible": int(panel["panel_eligible"].sum()),
            "n_no_news_keyword": int(panel["keyword_feature_status"].eq("no_news_zero_filled").sum()),
            "n_no_news_semantic": int(panel["semantic_feature_status"].eq("no_news_zero_filled").sum()),
            "source_status_summary": source_status_summary(status_audit, status_errors),
            "outputs": {
                "panel": portable_path(root, panel_path),
                "feature_manifest": portable_path(root, feature_path),
                "row_manifest": portable_path(root, row_path),
                "coverage_audit": portable_path(root, coverage_path),
                "source_status_audit": portable_path(root, status_path),
                "source_status_errors": portable_path(root, status_errors_path),
            },
            "limitations": limitations,
        }
        summary_path = output / "v6_build_summary.json"
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        write_v6_build_manifest(
            output,
            safe_run,
            spec,
            root,
            inputs.ledger,
            _build_output_paths(output),
            _v6_code_paths(root),
            target_manifest=target_manifest,
            extra={"claim_level": claim_level, "source_status_summary": summary["source_status_summary"]},
        )
        title = "# V6 primary panel build" if claim_level == spec["claim_level"] else "# V6 sensitivity panel build"
        (report / "v6_build_summary.md").write_text(
            "\n".join(
                [
                    title,
                    "",
                    f"- Run: `{safe_run}`",
                    f"- Claim level: `{claim_level}`",
                    f"- Rows: `{summary['n_rows']}`",
                    f"- Eligible: `{summary['n_eligible']}`",
                    f"- Semantic no-news rows: `{summary['n_no_news_semantic']}`",
                    "",
                    "Semantic zeros are emitted only for verified `no_valid_news` rows.",
                    "Source timing/mapping/extraction errors are separately audited and block primary-eligible rows.",
                ]
            ) + "\n",
            encoding="utf-8",
        )
        return summary
    except Exception as exc:
        if output.is_dir():
            write_v6_failure_manifest(output, safe_run, "build_panel", exc)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a fail-closed V6 primary panel")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workspace-root", type=Path, default=WORKSPACE_ROOT)
    parser.add_argument("--horizon", type=int, default=20)
    parser.add_argument("--semantic-daily", default=None)
    parser.add_argument("--sensitivity-tag", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = resolve_v6_workspace_root(args.workspace_root)
    spec = load_v6_spec(resolve_v6_protocol_path(root))
    run_id = validate_v6_run_id(args.run_id, spec)
    output, report = v6_output_dirs(run_id, root)
    summary = write_build_artifacts(
        output,
        report,
        run_id,
        spec,
        horizon=args.horizon,
        semantic_daily=args.semantic_daily,
        sensitivity_tag=args.sensitivity_tag,
        workspace_root=root,
    )
    print(json.dumps({"status": "ok", "run_id": run_id, "n_eligible": summary["n_eligible"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
