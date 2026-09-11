"""Adapt single-model LLM cache rows into consensus-shaped pseudo-labels.

Exploratory densification only. Does not replace multi-LLM consensus or V6 primary.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, ensure_dirs, sha256_file, utc_now

SENTIMENT_TO_DIRECTION = {
    "positive": "support",
    "negative": "risk",
    "mixed": "mixed",
    "neutral": "neutral",
}
# Cache categorical sentiment is often stuck at neutral; prefer numeric thresholds.
SENTIMENT_SCORE_SUPPORT = 0.25
SENTIMENT_SCORE_RISK = -0.25
EVENT_ALIASES = {
    "debt_risk": "debt",
    "legal_risk": "legal",
}
DEFAULT_CACHE = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "experiments"
    / "llm_semantic"
    / "article_semantics_cache.csv"
)
DEFAULT_EXTRA = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "experiments"
    / "llm_semantic"
    / "focused_material_expanded_annotations_deepseek.csv"
)
DEFAULT_OUT = OUTPUT_DIR / "cache_dense_pseudo_labels.csv"
DEFAULT_SUMMARY = OUTPUT_DIR / "cache_dense_pseudo_labels_summary.json"


def _truthy_relevant(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def _materiality_label(score: float) -> str:
    if pd.isna(score):
        return "low"
    if score >= 4:
        return "high"
    if score == 3:
        return "medium"
    return "low"


def _direction_from_sentiment(value: Any) -> str:
    key = str(value or "").strip().lower()
    return SENTIMENT_TO_DIRECTION.get(key, "unclear")


def _direction_from_sentiment_score(score: Any, sentiment: Any = None) -> str:
    """Prefer numeric sentiment_score; fall back to categorical sentiment."""
    numeric = pd.to_numeric(score, errors="coerce")
    if pd.notna(numeric):
        if numeric >= SENTIMENT_SCORE_SUPPORT:
            return "support"
        if numeric <= SENTIMENT_SCORE_RISK:
            return "risk"
        if abs(float(numeric)) < 1e-12:
            # Exact zero is ambiguous; use categorical if informative.
            categorical = _direction_from_sentiment(sentiment)
            return categorical if categorical != "unclear" else "neutral"
        return "mixed"
    return _direction_from_sentiment(sentiment)


def _event_alias(value: Any) -> str:
    key = str(value or "").strip().lower()
    return EVENT_ALIASES.get(key, key or "other")


def load_cache_frames(paths: Iterable[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        if path is None:
            continue
        path = Path(path)
        if not path.exists():
            continue
        frame = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
        frame["__source_path"] = str(path)
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def filter_ok_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    work = frame.copy()
    work = work[work["status"].astype(str).str.lower().eq("ok")].copy()
    if "is_stock_relevant" in work.columns:
        work = work[_truthy_relevant(work["is_stock_relevant"])].copy()
    return work


def dedupe_ok_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    work = frame.copy()
    work["ticker"] = work["ticker"].astype(str).str.upper()
    if "content_hash" not in work.columns:
        work["content_hash"] = ""
    work["content_hash"] = work["content_hash"].astype(str)
    # Prefer rows that already carry richer event/relevance fields; stable by source order.
    work = work.drop_duplicates(subset=["content_hash", "ticker"], keep="first")
    return work.reset_index(drop=True)


def adapt_cache_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "artifact_schema_version",
                "news_id",
                "ticker",
                "article_date",
                "content_hash",
                "consensus_ticker_relevance",
                "consensus_materiality",
                "consensus_direction",
                "consensus_event_type",
                "consensus_materiality_score",
                "consensus_uncertainty_score",
                "consensus_novelty_score",
                "high_disagreement_fields",
                "analysis_eligible",
                "adapter_source",
            ]
        )
    work = frame.copy()
    work["ticker"] = work["ticker"].astype(str).str.upper()
    work["article_date"] = pd.to_datetime(work["article_date"], errors="coerce")
    work["consensus_ticker_relevance"] = (
        work.get("relevance_to_ticker", pd.Series("", index=work.index))
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"": "unclear", "nan": "unclear"})
    )
    mag = pd.to_numeric(
        work.get("information_magnitude_score", pd.Series(1.0, index=work.index)),
        errors="coerce",
    ).fillna(1.0)
    work["consensus_materiality_score"] = mag
    work["consensus_materiality"] = mag.map(_materiality_label)
    sentiment_col = work.get("sentiment", pd.Series("", index=work.index))
    score_col = work.get("sentiment_score", pd.Series(pd.NA, index=work.index))
    work["consensus_direction"] = [
        _direction_from_sentiment_score(score, sentiment)
        for score, sentiment in zip(score_col.tolist(), sentiment_col.tolist())
    ]
    work["consensus_event_type"] = work.get(
        "event_type", pd.Series("other", index=work.index)
    ).map(_event_alias)
    work["consensus_uncertainty_score"] = pd.to_numeric(
        work.get("uncertainty_score", pd.Series(1.0, index=work.index)),
        errors="coerce",
    ).fillna(1.0)
    work["consensus_novelty_score"] = pd.to_numeric(
        work.get("novelty_hint_score", pd.Series(1.0, index=work.index)),
        errors="coerce",
    ).fillna(1.0)
    work["high_disagreement_fields"] = ""
    work["analysis_eligible"] = True
    if "content_hash" not in work.columns:
        work["content_hash"] = ""
    if "news_id" not in work.columns:
        work["news_id"] = work["content_hash"].astype(str).str.slice(0, 16)
    work["news_id"] = work["news_id"].astype(str)
    work["artifact_schema_version"] = "cache_dense_pseudo_label_v1"
    work["adapter_source"] = work.get("__source_path", "cache")
    cols = [
        "artifact_schema_version",
        "news_id",
        "ticker",
        "article_date",
        "content_hash",
        "consensus_ticker_relevance",
        "consensus_materiality",
        "consensus_direction",
        "consensus_event_type",
        "consensus_materiality_score",
        "consensus_uncertainty_score",
        "consensus_novelty_score",
        "high_disagreement_fields",
        "analysis_eligible",
        "adapter_source",
    ]
    return work[cols].dropna(subset=["ticker", "article_date"]).reset_index(drop=True)


def build_summary(
    raw: pd.DataFrame,
    adapted: pd.DataFrame,
    cache_paths: list[Path],
    out_path: Path,
) -> dict[str, Any]:
    ok_before = 0 if raw.empty else int(raw["status"].astype(str).str.lower().eq("ok").sum())
    return {
        "artifact_schema_version": "cache_dense_pseudo_labels_summary_v1",
        "generated_at_utc": utc_now(),
        "claim_level": "v6_sensitivity_densified_cache_semantic",
        "inputs": [str(p) for p in cache_paths if p and Path(p).exists()],
        "input_sha256": {
            str(p): sha256_file(Path(p)) for p in cache_paths if p and Path(p).exists()
        },
        "n_raw_rows": int(len(raw)),
        "n_status_ok": ok_before,
        "n_adapted_rows": int(len(adapted)),
        "n_tickers": int(adapted["ticker"].nunique()) if not adapted.empty else 0,
        "relevance_counts": (
            adapted["consensus_ticker_relevance"].value_counts().to_dict()
            if not adapted.empty
            else {}
        ),
        "direction_counts": (
            adapted["consensus_direction"].value_counts().to_dict()
            if not adapted.empty
            else {}
        ),
        "event_counts": (
            adapted["consensus_event_type"].value_counts().head(20).to_dict()
            if not adapted.empty
            else {}
        ),
        "output": str(out_path),
        "output_sha256": sha256_file(out_path) if out_path.exists() else None,
        "limitations": [
            "sensitivity_only_not_v6_primary",
            "does_not_replace_v6_primary_20260909",
            "single_model_cache_not_multi_llm_consensus",
            "adapter_approximates_consensus_schema",
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Adapt OK LLM cache rows into consensus-shaped pseudo-labels"
    )
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--extra", type=Path, default=DEFAULT_EXTRA)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument(
        "--no-extra",
        action="store_true",
        help="use only --cache and ignore focused DeepSeek material file",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ensure_dirs()
    args = parse_args(argv)
    paths = [args.cache]
    if not args.no_extra:
        paths.append(args.extra)
    raw = load_cache_frames(paths)
    filtered = filter_ok_rows(raw)
    deduped = dedupe_ok_rows(filtered)
    adapted = adapt_cache_rows(deduped)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    adapted.to_csv(args.out, index=False, encoding="utf-8-sig")
    summary = build_summary(raw, adapted, paths, args.out)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", **{k: summary[k] for k in (
        "n_adapted_rows", "n_tickers", "output", "claim_level"
    )}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
