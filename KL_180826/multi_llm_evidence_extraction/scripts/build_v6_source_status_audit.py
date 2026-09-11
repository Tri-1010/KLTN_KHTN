"""Build V6 source-status artifacts without inferring no-news from zero-filled data.

The primary V6 feature grid is intentionally dense. This module creates a separate
status contract for confirmation/subgroup work, preserving mapping, extraction,
and eligibility failures instead of allowing them to look like no valid news.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import map_articles_to_effective_trading_date, sha256_file
from v6_artifacts import V6ArtifactError, atomic_write_json, portable_path, resolve_workspace_path

STATUS_VALUES = frozenset(
    {
        "valid_source_event",
        "no_valid_news",
        "missing_timestamp",
        "session_mapping_failed",
        "ticker_match_failed",
        "extraction_failed",
        "excluded_by_protocol",
    }
)
ERROR_STATUSES = frozenset(
    {
        "missing_timestamp",
        "session_mapping_failed",
        "ticker_match_failed",
        "extraction_failed",
        "excluded_by_protocol",
    }
)
_STATUS_PRIORITY = {
    "extraction_failed": 6,
    "ticker_match_failed": 5,
    "missing_timestamp": 4,
    "session_mapping_failed": 3,
    "excluded_by_protocol": 2,
    "valid_source_event": 1,
}


def _normalise_date(frame: pd.DataFrame, name: str) -> pd.Series:
    return pd.to_datetime(frame.get(name, pd.Series(pd.NaT, index=frame.index)), errors="coerce").dt.normalize()


def _normalise_text(frame: pd.DataFrame, name: str) -> pd.Series:
    return frame.get(name, pd.Series("", index=frame.index)).fillna("").astype(str).str.strip()


def _article_key(frame: pd.DataFrame) -> pd.Series:
    return (
        _normalise_text(frame, "url")
        + "|"
        + _normalise_text(frame, "ticker").str.upper()
        + "|"
        + _normalise_date(frame, "date").astype(str)
    )


def _processed_status_by_key(processed: pd.DataFrame) -> dict[str, str]:
    work = processed.copy()
    work["_key"] = _article_key(work)
    status = _normalise_text(work, "extraction_status").str.lower()
    priority = status.map({"failed": 3, "fetch_failed": 3, "error": 3, "partial": 2, "restricted": 2, "ok": 1}).fillna(0)
    work["_extraction_status"] = status
    work["_priority"] = priority
    selected = work.sort_values("_priority", ascending=False).drop_duplicates("_key")
    return dict(zip(selected["_key"], selected["_extraction_status"]))


def _consensus_eligibility(consensus: pd.DataFrame) -> dict[tuple[str, pd.Timestamp], bool]:
    work = consensus.copy()
    work["ticker"] = _normalise_text(work, "ticker").str.upper()
    work["article_date"] = _normalise_date(work, "article_date")
    if "analysis_eligible" in work:
        work["_eligible"] = work["analysis_eligible"].astype(str).str.lower().isin({"true", "1"})
    else:
        work["_eligible"] = False
    work = work.dropna(subset=["article_date"])
    return {
        (str(ticker), pd.Timestamp(article_date)): bool(group["_eligible"].any())
        for (ticker, article_date), group in work.groupby(["ticker", "article_date"], sort=False)
    }


def _classify_source_articles(
    prices: pd.DataFrame,
    matched: pd.DataFrame,
    processed: pd.DataFrame,
    consensus: pd.DataFrame,
) -> pd.DataFrame:
    work = matched.copy()
    work["source_row_id"] = range(len(work))
    work["ticker"] = _normalise_text(work, "ticker").str.upper()
    work["article_date"] = _normalise_date(work, "date")
    work["_key"] = _article_key(work)
    processed_status = _processed_status_by_key(processed)
    eligible_by_key = _consensus_eligibility(consensus)
    work["extraction_status"] = work["_key"].map(processed_status).fillna("")
    work["source_status"] = "pending_mapping"

    invalid_ticker = work["ticker"].isin({"", "UNKNOWN", "NAN"}) | _normalise_text(work, "match_confidence").str.lower().isin({"none", "unmatched"})
    missing_timestamp = work["article_date"].isna()
    extraction_failed = work["extraction_status"].isin({"failed", "fetch_failed", "error"})
    excluded = work["extraction_status"].isin({"partial", "restricted", "missing"}) | work["extraction_status"].eq("")
    work.loc[invalid_ticker, "source_status"] = "ticker_match_failed"
    work.loc[~invalid_ticker & missing_timestamp, "source_status"] = "missing_timestamp"
    work.loc[~invalid_ticker & ~missing_timestamp & extraction_failed, "source_status"] = "extraction_failed"
    work.loc[~invalid_ticker & ~missing_timestamp & ~extraction_failed & excluded, "source_status"] = "excluded_by_protocol"

    candidates = work[work["source_status"].eq("pending_mapping")].copy()
    work["effective_date"] = pd.NaT
    work["mapping_status"] = "not_attempted"
    if not candidates.empty:
        mapped = map_articles_to_effective_trading_date(candidates, prices[["ticker", "date"]])
        mapped["mapping_status"] = mapped["mapping_status"].fillna("session_mapping_failed")
        mapped.loc[mapped["mapping_status"].ne("ok"), "source_status"] = "session_mapping_failed"
        ok = mapped["mapping_status"].eq("ok")
        mapped.loc[ok, "source_status"] = [
            "valid_source_event" if eligible_by_key.get((str(row.ticker), pd.Timestamp(row.article_date)), False) else "excluded_by_protocol"
            for row in mapped.loc[ok].itertuples()
        ]
        mapping_by_id = mapped.set_index("source_row_id")
        for row_id, row in mapping_by_id.iterrows():
            index = work.index[work["source_row_id"].eq(row_id)]
            work.loc[index, "effective_date"] = row.get("effective_date")
            work.loc[index, "mapping_status"] = row.get("mapping_status")
            work.loc[index, "source_status"] = row.get("source_status")
    work["source_status"] = work["source_status"].replace("pending_mapping", "excluded_by_protocol")
    # Mapping/extraction errors with a valid source date are attributed to the
    # strict next trading session for visible panel-level audit; missing-timestamp
    # and ticker failures remain unassigned source errors.
    attributable = work["effective_date"].isna() & work["article_date"].notna() & work["source_status"].isin({"extraction_failed", "excluded_by_protocol"})
    if attributable.any():
        provisional = map_articles_to_effective_trading_date(work.loc[attributable].copy(), prices[["ticker", "date"]])
        for row in provisional.itertuples():
            index = work.index[work["source_row_id"].eq(row.source_row_id)]
            if getattr(row, "mapping_status", "") == "ok":
                work.loc[index, "effective_date"] = getattr(row, "effective_date")
                work.loc[index, "mapping_status"] = "ok"
    work["source_status"] = work["source_status"].fillna("excluded_by_protocol")
    if not work["source_status"].isin(STATUS_VALUES).all():
        raise V6ArtifactError("V6 source-status classifier emitted unknown state")
    return work[["source_row_id", "ticker", "article_date", "effective_date", "mapping_status", "source_status"]]


def build_source_status_audit(
    prices: pd.DataFrame,
    matched: pd.DataFrame,
    processed: pd.DataFrame,
    consensus: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return dense ticker/date statuses plus source errors not assignable to a row."""
    grid = prices[["ticker", "date"]].copy()
    grid["ticker"] = _normalise_text(grid, "ticker").str.upper()
    grid["date"] = _normalise_date(grid, "date")
    grid = grid.dropna(subset=["ticker", "date"]).drop_duplicates(["ticker", "date"])
    articles = _classify_source_articles(grid, matched, processed, consensus)
    mapped = articles.dropna(subset=["effective_date"]).copy()
    mapped["effective_date"] = pd.to_datetime(mapped["effective_date"], errors="coerce").dt.normalize()
    mapped["priority"] = mapped["source_status"].map(_STATUS_PRIORITY).fillna(0)
    selected = mapped.sort_values("priority", ascending=False).drop_duplicates(["ticker", "effective_date"])
    audit = grid.merge(
        selected[["ticker", "effective_date", "source_status"]].rename(columns={"effective_date": "date"}),
        on=["ticker", "date"],
        how="left",
        validate="one_to_one",
    )
    audit["source_status"] = audit["source_status"].fillna("no_valid_news")
    audit["source_status_error"] = audit["source_status"].isin(ERROR_STATUSES)
    audit["artifact_schema_version"] = "v6_source_status_audit_v2"
    errors = articles[articles["effective_date"].isna() & articles["source_status"].isin(ERROR_STATUSES)].copy()
    errors["artifact_schema_version"] = "v6_source_status_errors_v1"
    return audit.sort_values(["ticker", "date"]).reset_index(drop=True), errors.reset_index(drop=True)


def source_status_summary(audit: pd.DataFrame, errors: pd.DataFrame) -> list[dict[str, Any]]:
    grid_counts = audit["source_status"].value_counts().to_dict()
    error_counts = errors["source_status"].value_counts().to_dict() if not errors.empty else {}
    return [
        {
            "source_status": status,
            "panel_rows": int(grid_counts.get(status, 0)),
            "unassigned_source_errors": int(error_counts.get(status, 0)),
        }
        for status in sorted(STATUS_VALUES)
    ]


def _load_csv(root: Path, relative: str, label: str) -> tuple[pd.DataFrame, Path]:
    path = resolve_workspace_path(root, relative, field=label)
    return pd.read_csv(path, encoding="utf-8-sig"), path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build workspace-local V6 source-status artifacts.")
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--prices", required=True)
    parser.add_argument("--matched", required=True)
    parser.add_argument("--processed", required=True)
    parser.add_argument("--consensus", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--errors-output", default=None)
    args = parser.parse_args()
    root = args.workspace_root.resolve()
    prices, prices_path = _load_csv(root, args.prices, "prices")
    matched, matched_path = _load_csv(root, args.matched, "matched")
    processed, processed_path = _load_csv(root, args.processed, "processed")
    consensus, consensus_path = _load_csv(root, args.consensus, "consensus")
    output_path = resolve_workspace_path(root, args.output, field="output", require_file=False)
    errors_relative = args.errors_output or str(Path(args.output).with_name("v6_source_status_errors.csv"))
    errors_path = resolve_workspace_path(root, errors_relative, field="errors output", require_file=False)
    if output_path.exists() or errors_path.exists():
        raise FileExistsError("refusing to overwrite V6 source-status artifacts")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    errors_path.parent.mkdir(parents=True, exist_ok=True)
    audit, errors = build_source_status_audit(prices, matched, processed, consensus)
    audit.to_csv(output_path, index=False, encoding="utf-8-sig")
    errors.to_csv(errors_path, index=False, encoding="utf-8-sig")
    manifest = {
        "artifact_schema_version": "v6_source_status_manifest_v2",
        "outputs": [
            {"name": "status_audit", "path": portable_path(root, output_path), "sha256": sha256_file(output_path)},
            {"name": "unassigned_errors", "path": portable_path(root, errors_path), "sha256": sha256_file(errors_path)},
        ],
        "sources": [
            {"name": name, "path": portable_path(root, path), "sha256": sha256_file(path)}
            for name, path in (("prices", prices_path), ("matched", matched_path), ("processed", processed_path), ("consensus", consensus_path))
        ],
        "summary": source_status_summary(audit, errors),
    }
    atomic_write_json(output_path.with_suffix(".manifest.json"), manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
