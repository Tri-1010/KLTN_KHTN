"""Fail-closed preflight and explicit collection gate for V6 H2 confirmation.

Preflight is read-only. A future collection adapter may run only with --execute,
inside a prepared workspace, after every structural and cost gate passes. This
module deliberately does not invoke the legacy root-bound pipeline.
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
if str(SCRIPT_DIR.parents[2]) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.parents[2]))

from common import sha256_file, utc_now
from scripts import llm_provider
from v6_artifacts import V6ArtifactError, atomic_write_json, portable_path, resolve_workspace_path


REQUIRED_SNAPSHOT_INPUTS = (
    "KL_180826/data/prices/all_vn30_prices.csv",
    "KL_180826/data/prices_extended/VNINDEX.csv",
    "KL_180826/data/news/matched/all_news_matched.csv",
    "KL_180826/data/news/processed/all_news_processed.csv",
)


def load_confirmation_protocol(workspace: Path) -> tuple[dict[str, Any], Path]:
    path = resolve_workspace_path(
        workspace,
        "KL_180826/multi_llm_evidence_extraction/config/v6_h2_confirmation_20260602_20260810_v1.json",
        field="confirmation protocol",
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise V6ArtifactError("confirmation protocol must be a JSON object")
    return value, path


def _load_workspace_manifest(workspace: Path) -> dict[str, Any]:
    path = workspace / "confirmation_workspace_manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"workspace manifest missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("status") != "prepared":
        raise V6ArtifactError("confirmation workspace is not prepared")
    snapshots = value.get("snapshot_inputs")
    if not isinstance(snapshots, list) or not snapshots:
        raise V6ArtifactError("confirmation workspace lacks frozen snapshot inputs")
    for entry in snapshots:
        if not isinstance(entry, dict) or not isinstance(entry.get("snapshot_path"), str) or not isinstance(entry.get("snapshot_sha256"), str):
            raise V6ArtifactError("confirmation workspace snapshot entry is invalid")
        path = resolve_workspace_path(workspace, entry["snapshot_path"], field="confirmation snapshot input")
        if sha256_file(path) != entry["snapshot_sha256"]:
            raise V6ArtifactError(f"confirmation workspace snapshot hash mismatch: {entry['snapshot_path']}")
        if entry.get("size_bytes") is not None and path.stat().st_size != int(entry["size_bytes"]):
            raise V6ArtifactError(f"confirmation workspace snapshot size mismatch: {entry['snapshot_path']}")
    return value


def _read_csv(workspace: Path, relative: str, label: str) -> tuple[pd.DataFrame, Path]:
    path = resolve_workspace_path(workspace, relative, field=label)
    return pd.read_csv(path, encoding="utf-8-sig"), path


def _coverage_check(prices: pd.DataFrame, benchmark: pd.DataFrame, protocol: dict[str, Any]) -> dict[str, Any]:
    dates = protocol["confirmation_oos"]
    start = pd.Timestamp(dates["start_date"]).normalize()
    end = pd.Timestamp(dates["end_date"]).normalize()
    horizon = int(dates["label_horizon_benchmark_sessions"])
    stock = prices.copy()
    stock["ticker"] = stock["ticker"].astype(str).str.upper()
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce").dt.normalize()
    bench = benchmark.copy()
    bench["date"] = pd.to_datetime(bench["date"], errors="coerce").dt.normalize()
    if stock[["ticker", "date", "close"]].isna().any().any() or bench[["date", "close"]].isna().any().any():
        return {"complete": False, "reason": "missing_required_price_fields"}
    bench_dates = sorted(bench["date"].unique())
    entries = [date for date in bench_dates if start <= pd.Timestamp(date) <= end]
    if not entries:
        return {"complete": False, "reason": "no_benchmark_entries_in_confirmation_window"}
    exit_dates: dict[pd.Timestamp, pd.Timestamp] = {}
    for index, date in enumerate(bench_dates):
        date = pd.Timestamp(date)
        if date in entries and index + horizon < len(bench_dates):
            exit_dates[date] = pd.Timestamp(bench_dates[index + horizon])
    missing_entry_exit = [date for date in entries if date not in exit_dates]
    required_pairs = [(ticker, entry, exit_date) for ticker, group in stock.groupby("ticker") for entry, exit_date in exit_dates.items() if entry in set(group["date"]) ]
    stock_pairs = {(ticker, date) for ticker, date in stock[["ticker", "date"]].itertuples(index=False, name=None)}
    missing_stock_exit = [pair for pair in required_pairs if (pair[0], pair[2]) not in stock_pairs]
    return {
        "complete": not missing_entry_exit and not missing_stock_exit,
        "entry_dates": len(entries),
        "entry_dates_with_t20_exit": len(exit_dates),
        "missing_benchmark_exit_dates": [pd.Timestamp(date).date().isoformat() for date in missing_entry_exit],
        "missing_stock_exit_count": len(missing_stock_exit),
        "latest_benchmark_date": pd.Timestamp(max(bench_dates)).date().isoformat(),
    }


def _eligible_article_count(matched: pd.DataFrame, processed: pd.DataFrame, protocol: dict[str, Any]) -> dict[str, Any]:
    start = pd.Timestamp(protocol["confirmation_oos"]["start_date"]).normalize()
    end = pd.Timestamp(protocol["confirmation_oos"]["end_date"]).normalize()
    matched_work = matched.copy()
    matched_work["date"] = pd.to_datetime(matched_work["date"], errors="coerce").dt.normalize()
    matched_window = matched_work[matched_work["date"].between(start, end)].copy()
    if "url" not in matched_window:
        raise V6ArtifactError("confirmation matched-news input lacks URL")
    processed_work = processed.copy()
    processed_work["date"] = pd.to_datetime(processed_work["date"], errors="coerce").dt.normalize()
    for frame, label in ((processed_work, "processed"), (matched_window, "matched")):
        if "ticker" not in frame:
            raise V6ArtifactError(f"confirmation {label}-news input lacks ticker")
        if "url" not in frame:
            raise V6ArtifactError(f"confirmation {label}-news input lacks URL")
    processed_work["_key"] = processed_work["url"].fillna("").astype(str) + "|" + processed_work["ticker"].fillna("").astype(str)
    matched_window["_key"] = matched_window["url"].fillna("").astype(str) + "|" + matched_window["ticker"].fillna("").astype(str)
    if "extraction_status" not in processed_work:
        processed_work["extraction_status"] = ""
    joined = matched_window.merge(processed_work[["_key", "extraction_status"]].drop_duplicates("_key"), on="_key", how="left", validate="many_to_one")
    eligible = joined[
        joined["date"].notna()
        & joined.get("ticker", pd.Series("", index=joined.index)).fillna("").astype(str).str.strip().ne("")
        & joined.get("extraction_status", pd.Series("", index=joined.index)).fillna("").astype(str).str.lower().isin({"ok", ""})
    ].drop_duplicates(["url", "ticker"])
    max_articles = int(protocol["gates"]["max_eligible_articles"])
    annotators = protocol["gates"]["annotators"]
    calls = len(eligible) * len(annotators)
    return {
        "eligible_articles": int(len(eligible)),
        "max_eligible_articles": max_articles,
        "within_article_cap": len(eligible) <= max_articles,
        "annotators": list(annotators),
        "planned_annotation_calls": int(calls),
        "max_annotation_calls": int(protocol["gates"]["max_annotation_calls"]),
        "within_call_cap": calls <= int(protocol["gates"]["max_annotation_calls"]),
    }


def preflight_confirmation_workspace(workspace: Path) -> dict[str, Any]:
    root = workspace.resolve()
    manifest = _load_workspace_manifest(root)
    protocol, protocol_path = load_confirmation_protocol(root)
    prices, prices_path = _read_csv(root, "KL_180826/data/prices/all_vn30_prices.csv", "prices")
    benchmark, benchmark_path = _read_csv(root, "KL_180826/data/prices_extended/VNINDEX.csv", "benchmark")
    matched, matched_path = _read_csv(root, "KL_180826/data/news/matched/all_news_matched.csv", "matched news")
    processed, processed_path = _read_csv(root, "KL_180826/data/news/processed/all_news_processed.csv", "processed news")
    coverage = _coverage_check(prices, benchmark, protocol)
    article_budget = _eligible_article_count(matched, processed, protocol)
    router = protocol["collection"]["local_router"]
    configured_model = llm_provider.resolve_model(str(router["provider"]), None)
    endpoint_host = llm_provider.local_router_endpoint_host()
    router_ok = configured_model in set(router["allowed_models"]) and endpoint_host.split(":", 1)[0] in set(router["allowed_hosts"])
    blockers: list[str] = []
    if not coverage["complete"]:
        blockers.append("incomplete_t20_price_or_benchmark_coverage")
    if not article_budget["within_article_cap"]:
        blockers.append("eligible_article_cap_exceeded")
    if not article_budget["within_call_cap"]:
        blockers.append("annotation_call_cap_exceeded")
    if not router_ok:
        blockers.append("local_router_contract_mismatch")
    inputs = [prices_path, benchmark_path, matched_path, processed_path]
    result = {
        "artifact_schema_version": "v6_confirmation_preflight_v1",
        "status": "ready" if not blockers else "blocked",
        "generated_at_utc": utc_now(),
        "workspace_manifest": {"path": "confirmation_workspace_manifest.json", "status": manifest["status"]},
        "protocol": {"path": portable_path(root, protocol_path), "sha256": sha256_file(protocol_path)},
        "confirmation_oos": protocol["confirmation_oos"],
        "input_hashes": [{"path": portable_path(root, path), "sha256": sha256_file(path)} for path in inputs],
        "coverage": coverage,
        "annotation_budget": article_budget,
        "local_router": {
            "provider": router["provider"],
            "endpoint_host": endpoint_host,
            "requested_model": configured_model,
            "loopback_valid": router_ok,
            "credential_persisted": False,
        },
        "blockers": blockers,
        "network_execution": "not_run",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run read-only V6 H2 confirmation preflight.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="reserved; collection adapter is intentionally not implemented in v1")
    args = parser.parse_args()
    if args.execute:
        raise V6ArtifactError("network collection is not implemented by this preflight command; no network request was sent")
    result = preflight_confirmation_workspace(args.workspace)
    output = args.workspace.resolve() / "preflight" / "v6_confirmation_preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite preflight result: {output}")
    atomic_write_json(output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
