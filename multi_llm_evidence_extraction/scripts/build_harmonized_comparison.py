from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common import MAPPING_POLICY, STUDY_DIR, article_text, content_hash, map_articles_to_effective_trading_date, parse_string_list, resolve_scoped_path, sha256_file, validate_safe_identifier
from pipeline.task8_keywords import KEYWORD_GROUPS, get_curated_keywords
from pipeline.task9_kw_features import compute_raw_counts

SPEC_PATH = STUDY_DIR / "config" / "harmonized_comparison_v5.json"
WINDOWS = (1, 5, 20, 60)
SEMANTIC_EVENT_TYPES = (
    "earnings", "dividend", "capital", "debt", "legal", "governance", "project",
    "product", "ma", "analyst", "market", "macro", "sector", "other", "unclear", "disagreement",
)
SEMANTIC_SCORE_FIELDS = (
    "materiality_score", "expected_impact_score", "uncertainty_score", "novelty_score", "reasoning_confidence",
)
SPINE_COLUMNS = [
    "artifact_schema_version", "study_id", "run_id", "mode", "news_id", "ticker",
    "article_date", "effective_date", "mapping_policy", "mapping_status", "content_hash",
    "sample_bucket", "source", "annotation_status", "analysis_eligible", "exclusion_reasons",
    "analytic_spine_member", "analytic_spine_reason",
]
BUILD_MANIFEST_NAME = "harmonized_build_manifest.json"


def assert_build_run_mutable(output_dir: Path) -> None:
    """Refuse writes after a run has a completed build manifest."""
    manifest_path = output_dir / BUILD_MANIFEST_NAME
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"existing harmonized build manifest is invalid: {manifest_path}") from exc
    if manifest.get("status") == "completed":
        raise FileExistsError(f"completed harmonized build run is immutable: {manifest_path}")
    raise FileExistsError(f"harmonized build manifest already exists: {manifest_path}")


def load_harmonized_spec(path: Path = SPEC_PATH) -> dict[str, Any]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "study_id", "protocol_version", "canonical_run_id", "observation_key", "primary",
        "effective_date_policy", "windows", "configs", "input_paths", "input_sha256",
    }
    missing = required - set(spec)
    if missing:
        raise ValueError(f"harmonized spec missing fields: {sorted(missing)}")
    if spec["effective_date_policy"] != MAPPING_POLICY:
        raise ValueError("effective-date policy differs from shared mapping helper")
    if tuple(spec["windows"]) != WINDOWS:
        raise ValueError("harmonized windows differ from preregistered windows")
    primary = spec["primary"]
    expected_primary = {
        "family": "P1",
        "baseline_config": "B_technical_coverage_keyword",
        "comparison_config": "C_technical_coverage_semantic",
        "model": "RandomForest",
        "metric": "balanced_accuracy",
        "topk": 10,
    }
    if primary != expected_primary:
        raise ValueError("harmonized primary comparison differs from preregistered contract")
    if spec["observation_key"] != ["ticker", "date", "target_exit_date"]:
        raise ValueError("harmonized observation key differs from preregistered contract")
    return spec


def validate_preregistered_inputs(spec: dict[str, Any], root: Path, keys: tuple[str, ...]) -> dict[str, str]:
    actual: dict[str, str] = {}
    for key in keys:
        path = (root / spec["input_paths"][key]).resolve()
        if not path.exists():
            raise FileNotFoundError(path)
        digest = sha256_file(path)
        expected = spec["input_sha256"].get(key)
        if not expected or digest != expected:
            raise ValueError(f"preregistered input hash mismatch: {key}")
        actual[key] = digest
    return actual


def _resolved_input_path(path: Path) -> Path:
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def write_harmonized_build_manifest(
    output_dir: Path,
    spec: dict[str, Any],
    run_id: str,
    mode: str,
    source_paths: dict[str, Path],
    preregistered_input_match: bool,
) -> Path:
    artifact_names = (
        "harmonized_article_spine.csv",
        "harmonized_features_daily.csv",
        "harmonized_feature_manifest.csv",
        "harmonized_row_manifest.csv",
        "harmonized_coverage_audit.csv",
        "harmonized_panel.csv",
    )
    artifacts = []
    for name in artifact_names:
        path = output_dir / name
        if not path.exists():
            raise FileNotFoundError(f"harmonized build artifact missing: {path}")
        artifacts.append({"path": str(path.resolve()), "sha256": sha256_file(path)})
    manifest = {
        "artifact_schema_version": "harmonized_build_manifest_v1",
        "study_id": spec["study_id"],
        "protocol_version": spec["protocol_version"],
        "protocol_sha256": sha256_file(SPEC_PATH),
        "run_id": run_id,
        "mode": mode,
        "status": "completed",
        "preregistered_input_match": preregistered_input_match,
        "claim_level": spec["claim_gates"][mode],
        "sources": [
            {"name": name, "path": str(path.resolve()), "sha256": sha256_file(path)}
            for name, path in source_paths.items()
        ],
        "artifacts": artifacts,
    }
    path = output_dir / "harmonized_build_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_article_universe(sample_path: Path, consensus_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = pd.read_csv(sample_path, encoding="utf-8-sig")
    consensus = pd.read_csv(consensus_path, encoding="utf-8-sig") if consensus_path.exists() else pd.DataFrame()
    return sample, consensus


def _prepare_keys(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    work = frame.copy()
    if work.empty:
        if not {"news_id", "ticker"}.issubset(work.columns):
            work = pd.DataFrame(columns=[*work.columns, "news_id", "ticker"])
        return work
    if not {"news_id", "ticker"}.issubset(work.columns):
        raise ValueError(f"{name} missing news_id/ticker")
    work["news_id"] = work["news_id"].astype(str)
    work["ticker"] = work["ticker"].astype(str).str.upper()
    if work.duplicated(["news_id", "ticker"]).any():
        raise ValueError(f"duplicate {name} article keys")
    return work


def build_common_article_spine(
    sample: pd.DataFrame,
    consensus: pd.DataFrame,
    spec: dict[str, Any],
    run_id: str,
    mode: str,
) -> pd.DataFrame:
    sample = _prepare_keys(sample, "sample")
    consensus = _prepare_keys(consensus, "consensus")
    merged = sample.merge(consensus, on=["news_id", "ticker"], how="outer", suffixes=("_sample", "_consensus"), indicator=True, validate="one_to_one")
    if not merged.empty and (merged["_merge"] != "both").any():
        counts = merged["_merge"].value_counts().to_dict()
        raise ValueError(f"sample/consensus key mismatch: {counts}")
    sample_hash = merged.get("content_hash_sample", merged.get("content_hash", pd.Series("", index=merged.index))).fillna("").astype(str)
    consensus_hash = merged.get("content_hash_consensus", pd.Series("", index=merged.index)).fillna("").astype(str)
    if sample_hash.eq("").any():
        raise ValueError("missing sample content hash")
    if consensus_hash.eq("").any():
        raise ValueError("missing consensus content hash")
    if sample_hash.ne(consensus_hash).any():
        raise ValueError("sample/consensus content hash mismatch")
    sample_date = pd.to_datetime(
        merged.get("date", merged.get("article_date_sample", pd.Series(pd.NaT, index=merged.index))), errors="coerce"
    ).dt.normalize()
    consensus_date = pd.to_datetime(
        merged.get("article_date", merged.get("article_date_consensus", pd.Series(pd.NaT, index=merged.index))), errors="coerce"
    ).dt.normalize()
    if ((sample_date.notna() & consensus_date.notna()) & sample_date.ne(consensus_date)).any():
        raise ValueError("sample/consensus article date mismatch")
    analysis = merged.get("analysis_eligible", pd.Series(False, index=merged.index)).astype(str).str.lower().isin({"true", "1"})
    reasons = merged.get("exclusion_reasons", pd.Series("", index=merged.index)).apply(parse_string_list)
    article_date = sample_date.fillna(consensus_date)
    spine = pd.DataFrame({
        "artifact_schema_version": "harmonized_article_spine_v1",
        "study_id": spec["study_id"], "run_id": run_id, "mode": mode,
        "news_id": merged["news_id"], "ticker": merged["ticker"],
        "article_date": pd.to_datetime(article_date, errors="coerce").dt.normalize(),
        "content_hash": sample_hash, "sample_bucket": merged.get("sample_bucket", ""),
        "source": merged.get("source", ""), "annotation_status": np.where(merged["_merge"].eq("both"), "annotated", "missing"),
        "analysis_eligible": analysis, "exclusion_reasons": reasons,
        "analytic_spine_member": analysis & merged["_merge"].eq("both"),
        "analytic_spine_reason": np.where(analysis, "eligible_consensus", "consensus_ineligible"),
    })
    for col in consensus.columns:
        if col not in {"news_id", "ticker", "article_date", "content_hash", "analysis_eligible", "exclusion_reasons"}:
            spine[col] = merged.get(col, merged.get(f"{col}_consensus"))
    for col in ("title", "description", "full_text", "article_summary", "url", "match_confidence"):
        if col in merged:
            spine[f"_source_{col}"] = merged[col]
    return spine


def validate_common_article_spine(spine: pd.DataFrame) -> dict[str, int]:
    if spine.duplicated(["news_id", "ticker"]).any():
        raise ValueError("duplicate harmonized spine keys")
    if spine["content_hash"].fillna("").eq("").any():
        raise ValueError("missing sample content hash")
    if ((spine["annotation_status"] != "annotated") & spine["analytic_spine_member"]).any():
        raise ValueError("unannotated article entered analytic spine")
    return {
        "sampled": len(spine), "joined": int(spine["annotation_status"].eq("annotated").sum()),
        "eligible": int(spine["analysis_eligible"].sum()), "analytic_spine": int(spine["analytic_spine_member"].sum()),
    }


def map_spine_to_effective_dates(spine: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    mapped = map_articles_to_effective_trading_date(spine, prices)
    mapped["analytic_spine_member"] = mapped["analytic_spine_member"].fillna(False) & mapped["mapping_status"].eq("ok")
    mapped.loc[mapped["mapping_status"].ne("ok"), "analytic_spine_reason"] = mapped.loc[mapped["mapping_status"].ne("ok"), "mapping_status"]
    return mapped


def build_keyword_article_features(spine: pd.DataFrame) -> pd.DataFrame:
    registry = get_curated_keywords()
    all_keywords = registry["positive"] + registry["negative"] + registry["neutral"]
    rows = []
    for _, row in spine.iterrows():
        text = article_text({key.replace("_source_", ""): value for key, value in row.items() if key.startswith("_source_")})
        counts = compute_raw_counts(text, all_keywords)
        item: dict[str, Any] = {"news_id": row["news_id"], "ticker": row["ticker"], "effective_date": row["effective_date"]}
        for direction, keywords in registry.items():
            item[f"keyword_{direction}_count"] = sum(counts[word] for word in keywords)
        for group_id, group in KEYWORD_GROUPS.items():
            words = sum((group.get(direction, []) for direction in ("positive", "negative", "neutral")), [])
            item[f"keyword_group_{group_id.lower()}_count"] = sum(counts.get(word, 0) for word in words)
        item["keyword_occurrence_count"] = sum(counts.values())
        item["keyword_unique_count"] = sum(value > 0 for value in counts.values())
        item["keyword_matched"] = int(item["keyword_occurrence_count"] > 0)
        item["keyword_direction_num"] = item["keyword_positive_count"] - item["keyword_negative_count"]
        item["keyword_direction_den"] = item["keyword_positive_count"] + item["keyword_negative_count"]
        rows.append(item)
    return pd.DataFrame(rows)


def build_semantic_article_features(spine: pd.DataFrame) -> pd.DataFrame:
    fixed_columns = [
        "news_id", "ticker", "effective_date", "semantic_relevance_direct_num", "semantic_relevance_den",
        "semantic_materiality_high_num", "semantic_materiality_den", "semantic_direction_support_num",
        "semantic_direction_risk_num", "semantic_direction_den", "semantic_high_disagreement_num",
        "semantic_disagreement_den",
        *(f"semantic_{field}_num" for field in SEMANTIC_SCORE_FIELDS),
        *(f"semantic_{field}_den" for field in SEMANTIC_SCORE_FIELDS),
        *(f"semantic_event_{event}_count" for event in SEMANTIC_EVENT_TYPES),
    ]
    rows = []
    for _, row in spine.iterrows():
        direction = str(row.get("consensus_direction", ""))
        relevance = str(row.get("consensus_ticker_relevance", ""))
        materiality = str(row.get("consensus_materiality", ""))
        event = str(row.get("consensus_event_type", ""))
        event = event if event in SEMANTIC_EVENT_TYPES else "unclear"
        item: dict[str, Any] = {
            "news_id": row["news_id"], "ticker": row["ticker"], "effective_date": row["effective_date"],
            "semantic_relevance_direct_num": int(relevance == "direct"),
            "semantic_relevance_den": int(relevance not in {"", "nan"}),
            "semantic_materiality_high_num": int(materiality == "high"),
            "semantic_materiality_den": int(materiality not in {"", "nan"}),
            "semantic_direction_support_num": int(direction == "support"),
            "semantic_direction_risk_num": int(direction == "risk"),
            "semantic_direction_den": int(direction in {"support", "risk", "neutral", "mixed"}),
            "semantic_high_disagreement_num": int(bool(parse_string_list(row.get("high_disagreement_fields")))),
            "semantic_disagreement_den": 1,
        }
        for field in SEMANTIC_SCORE_FIELDS:
            value = pd.to_numeric(row.get(f"consensus_{field}"), errors="coerce")
            available = int(pd.notna(value))
            item[f"semantic_{field}_num"] = float(value) if available else 0.0
            item[f"semantic_{field}_den"] = available
        for allowed_event in SEMANTIC_EVENT_TYPES:
            item[f"semantic_event_{allowed_event}_count"] = int(event == allowed_event)
        rows.append(item)
    return pd.DataFrame(rows, columns=fixed_columns)


def aggregate_harmonized_daily_features(spine: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    analytic = spine[spine["analytic_spine_member"] & spine["mapping_status"].eq("ok")].copy()
    grid = prices[["ticker", "date"]].copy()
    grid["ticker"] = grid["ticker"].astype(str).str.upper()
    grid["date"] = pd.to_datetime(grid["date"], errors="coerce").dt.normalize()
    grid = grid.dropna().drop_duplicates().sort_values(["ticker", "date"])
    keyword = build_keyword_article_features(analytic)
    semantic = build_semantic_article_features(analytic)
    article = keyword.merge(semantic, on=["news_id", "ticker", "effective_date"], validate="one_to_one") if not analytic.empty else pd.DataFrame()
    if article.empty:
        daily = pd.DataFrame(columns=["ticker", "date"])
    else:
        article = article.rename(columns={"effective_date": "date"})
        numeric = [col for col in article if col not in {"news_id", "ticker", "date"}]
        daily = article.groupby(["ticker", "date"], as_index=False)[numeric].sum()
    out = grid.merge(daily, on=["ticker", "date"], how="left")
    feature_base = [col for col in out if col not in {"ticker", "date"}]
    out[feature_base] = out[feature_base].fillna(0.0)
    counts = analytic.groupby(["ticker", "effective_date"]).size().rename("common_article_count").reset_index().rename(columns={"effective_date": "date"}) if not analytic.empty else pd.DataFrame(columns=["ticker", "date", "common_article_count"])
    out = out.merge(counts, on=["ticker", "date"], how="left")
    out["common_article_count"] = pd.to_numeric(out["common_article_count"], errors="coerce").fillna(0.0)
    frames = []
    for _, group in out.groupby("ticker", sort=False):
        group = group.sort_values("date").copy()
        rolling: dict[str, pd.Series] = {}
        for window in WINDOWS:
            for col in [*feature_base, "common_article_count"]:
                rolling[f"{col}_roll_{window}d"] = group[col].rolling(window, min_periods=1).sum()
            rolling[f"common_has_article_roll_{window}d"] = (rolling[f"common_article_count_roll_{window}d"] > 0).astype(int)
            for prefix, num, den in (
                ("keyword_direction", "keyword_direction_num", "keyword_direction_den"),
                ("semantic_relevance_direct", "semantic_relevance_direct_num", "semantic_relevance_den"),
                ("semantic_materiality_high", "semantic_materiality_high_num", "semantic_materiality_den"),
                ("semantic_direction_support", "semantic_direction_support_num", "semantic_direction_den"),
                ("semantic_direction_risk", "semantic_direction_risk_num", "semantic_direction_den"),
                *((f"semantic_{field}", f"semantic_{field}_num", f"semantic_{field}_den") for field in SEMANTIC_SCORE_FIELDS),
                ("semantic_high_disagreement", "semantic_high_disagreement_num", "semantic_disagreement_den"),
            ):
                if num in group and den in group:
                    numerator = group[num].rolling(window, min_periods=1).sum()
                    denominator = group[den].rolling(window, min_periods=1).sum()
                    rolling[f"{prefix}_roll_{window}d"] = numerator.div(denominator.replace(0, np.nan)).fillna(0.0)
        group = pd.concat([group, pd.DataFrame(rolling, index=group.index)], axis=1)
        frames.append(group)
    result = pd.concat(frames, ignore_index=True) if frames else out
    result["artifact_schema_version"] = "harmonized_features_daily_v1"
    return result


def build_harmonized_panel(daily: pd.DataFrame, targets: pd.DataFrame, technical: pd.DataFrame | None = None) -> pd.DataFrame:
    target = targets.copy().rename(columns={"entry_date": "date"})
    target["date"] = pd.to_datetime(target["date"], errors="coerce").dt.normalize()
    panel = target.merge(daily, on=["ticker", "date"], how="left", validate="one_to_one")
    if technical is not None and not technical.empty:
        tech = technical.copy()
        tech["quarter_id"] = (pd.PeriodIndex(tech["quarter_id"].astype(str), freq="Q") + 1).astype(str)
        tech = tech.rename(columns={col: f"tech_lag1q__{col}" for col in tech if col not in {"ticker", "quarter_id"}})
        panel["quarter_id"] = panel["date"].dt.to_period("Q").astype(str)
        panel = panel.merge(tech, on=["ticker", "quarter_id"], how="left", validate="many_to_one")
    technical_columns = [col for col in panel if col.startswith("tech_lag1q__")]
    technical_available = panel[technical_columns].notna().any(axis=1) if technical_columns else pd.Series(False, index=panel.index)
    panel["lagged_technical_features_available"] = technical_available
    panel["panel_eligible"] = panel["target_status"].eq("ok") & panel.get("common_article_count_roll_60d", 0).gt(0) & technical_available
    panel["artifact_schema_version"] = "harmonized_panel_v1"
    return panel


def _feature_family(name: str) -> str:
    if name.startswith("tech_lag1q__"): return "technical"
    if name.startswith("common_"): return "coverage"
    if name.startswith("keyword_"): return "keyword"
    if name.startswith("semantic_"): return "semantic"
    return "other"


def write_harmonized_manifests(output_dir: Path, spine: pd.DataFrame, daily: pd.DataFrame, panel: pd.DataFrame, spec: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_spine = spine[[col for col in SPINE_COLUMNS if col in spine]].copy()
    clean_spine.to_csv(output_dir / "harmonized_article_spine.csv", index=False, encoding="utf-8-sig")
    daily.to_csv(output_dir / "harmonized_features_daily.csv", index=False, encoding="utf-8-sig")
    features = []
    for col in panel.columns:
        family = _feature_family(col)
        if family == "other": continue
        configs = [config for config, families in spec["configs"].items() if family in families]
        features.append({"feature": col, "family": family, "configs": json.dumps(configs), "declared": True, "artifact_schema_version": "harmonized_feature_manifest_v1"})
    pd.DataFrame(features).to_csv(output_dir / "harmonized_feature_manifest.csv", index=False, encoding="utf-8-sig")
    panel[[col for col in ["ticker", "date", "target_exit_date", "target_status", "panel_eligible"] if col in panel]].to_csv(output_dir / "harmonized_row_manifest.csv", index=False, encoding="utf-8-sig")
    coverage = panel.groupby("ticker", as_index=False).agg(rows=("date", "size"), panel_eligible=("panel_eligible", "sum"), common_60d=("common_article_count_roll_60d", "sum"))
    coverage_columns = [col for col in panel if _feature_family(col) == "coverage"]
    declared_b = set(feature["feature"] for feature in features if "B_technical_coverage_keyword" in json.loads(feature["configs"]))
    declared_c = set(feature["feature"] for feature in features if "C_technical_coverage_semantic" in json.loads(feature["configs"]))
    coverage["coverage_feature_count"] = len(coverage_columns)
    coverage["coverage_equal_B_C"] = bool(coverage_columns) and set(coverage_columns).issubset(declared_b) and set(coverage_columns).issubset(declared_c)
    coverage.to_csv(output_dir / "harmonized_coverage_audit.csv", index=False, encoding="utf-8-sig")
    panel.to_csv(output_dir / "harmonized_panel.csv", index=False, encoding="utf-8-sig")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build harmonized common-spine comparison inputs")
    parser.add_argument("--mode", choices=["pilot", "sample500"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--sample", type=Path)
    parser.add_argument("--consensus", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--fast", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = load_harmonized_spec()
    run_id = validate_safe_identifier(args.run_id, "run_id")
    scoped_output = resolve_scoped_path(STUDY_DIR / "outputs" / "harmonized", run_id)
    if args.output_dir is not None and args.output_dir.resolve() != scoped_output:
        raise ValueError("harmonized output_dir must equal outputs/harmonized/<run-id>")
    output_dir = scoped_output
    if not args.validate_only:
        assert_build_run_mutable(output_dir)
    if args.mode == "pilot":
        if args.sample is not None or args.consensus is not None or args.targets is not None:
            raise ValueError("pilot mode uses preregistered sample/consensus and run-scoped targets; input overrides are forbidden")
        validate_preregistered_inputs(spec, ROOT, ("pilot_sample", "pilot_consensus", "prices", "benchmark", "technical"))
        sample = (ROOT / spec["input_paths"]["pilot_sample"]).resolve()
        consensus = (ROOT / spec["input_paths"]["pilot_consensus"]).resolve()
        preregistered_input_match = True
    else:
        expected_sample = (STUDY_DIR / "data" / "sample_news_for_annotation_500_v1.csv").resolve()
        sample = _resolved_input_path(args.sample or expected_sample)
        if sample != expected_sample:
            raise ValueError("sample500 sample must equal data/sample_news_for_annotation_500_v1.csv")
        if args.consensus is None:
            raise ValueError("--consensus is required for sample500 mode; canonical consensus cannot be reused")
        consensus = _resolved_input_path(args.consensus)
        expected_consensus = (output_dir / "pseudo_labels_consensus.csv").resolve()
        if consensus != expected_consensus:
            raise ValueError("sample500 consensus must equal outputs/harmonized/<run-id>/pseudo_labels_consensus.csv")
        preregistered_input_match = False
    targets_path = output_dir / "harmonized_outperform_targets.csv"
    if args.mode == "sample500" and args.targets is not None:
        requested_target = _resolved_input_path(args.targets)
        if requested_target != targets_path.resolve():
            raise ValueError("sample500 targets must equal outputs/harmonized/<run-id>/harmonized_outperform_targets.csv")
    prices_path = (ROOT / spec["input_paths"]["prices"]).resolve()
    benchmark_path = (ROOT / spec["input_paths"]["benchmark"]).resolve()
    technical_path = (ROOT / spec["input_paths"]["technical"]).resolve()
    sample_df, consensus_df = load_article_universe(sample, consensus)
    spine = build_common_article_spine(sample_df, consensus_df, spec, run_id, args.mode)
    audit = validate_common_article_spine(spine)
    prices = pd.read_csv(prices_path, encoding="utf-8")
    mapped = map_spine_to_effective_dates(spine, prices)
    mapped_eligible = int((mapped["mapping_status"].eq("ok") & mapped["analysis_eligible"].fillna(False)).sum())
    if args.validate_only:
        print(json.dumps({
            "sampled_articles": audit["sampled"], "joined_articles": audit["joined"],
            "eligible_articles": audit["eligible"], "mapped_eligible_articles": mapped_eligible,
            "analytic_spine_articles": int(mapped["analytic_spine_member"].fillna(False).sum()),
        }, indent=2))
        return 0
    if not targets_path.exists():
        raise FileNotFoundError(f"harmonized targets missing: {targets_path}")
    target_manifest_path = output_dir / "harmonized_target_manifest.json"
    if not target_manifest_path.exists():
        raise FileNotFoundError(f"harmonized target manifest missing: {target_manifest_path}")
    target_manifest = json.loads(target_manifest_path.read_text(encoding="utf-8"))
    expected_target_sources = {"prices": prices_path, "benchmark": benchmark_path}
    for name, source_path in expected_target_sources.items():
        entry = target_manifest.get("sources", {}).get(name, {})
        if Path(str(entry.get("path", ""))).resolve() != source_path or entry.get("sha256") != sha256_file(source_path):
            raise ValueError(f"harmonized target source mismatch: {name}")
    target_entry = target_manifest.get("target", {})
    if Path(str(target_entry.get("path", ""))).resolve() != targets_path.resolve() or target_entry.get("sha256") != sha256_file(targets_path):
        raise ValueError("harmonized target artifact mismatch")
    targets = pd.read_csv(targets_path, encoding="utf-8-sig")
    technical = pd.read_csv(technical_path, encoding="utf-8") if technical_path.exists() else pd.DataFrame()
    daily = aggregate_harmonized_daily_features(mapped, prices)
    panel = build_harmonized_panel(daily, targets, technical)
    write_harmonized_manifests(output_dir, mapped, daily, panel, spec)
    write_harmonized_build_manifest(
        output_dir,
        spec,
        run_id,
        args.mode,
        {
            "sample": sample,
            "consensus": consensus,
            "prices": prices_path,
            "benchmark": benchmark_path,
            "technical": technical_path,
            "targets": targets_path,
            "target_manifest": target_manifest_path,
        },
        preregistered_input_match,
    )
    print(json.dumps({
        "sampled_articles": audit["sampled"], "joined_articles": audit["joined"],
        "eligible_articles": audit["eligible"], "mapped_eligible_articles": mapped_eligible,
        "analytic_spine_articles": int(mapped["analytic_spine_member"].fillna(False).sum()),
        "panel_rows": len(panel), "panel_eligible_rows": int(panel["panel_eligible"].fillna(False).sum()),
        "output_dir": str(output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
