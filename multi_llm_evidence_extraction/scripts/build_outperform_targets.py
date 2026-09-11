from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, ROOT, ensure_dirs, sha256_file

PRICES = ROOT / "data" / "prices" / "all_vn30_prices.csv"
VNINDEX = ROOT / "data" / "prices_extended" / "VNINDEX.csv"
OUT = OUTPUT_DIR / "outperform_targets.csv"
HORIZON = 20
HARMONIZED_SCHEMA_VERSION = "harmonized_outperform_targets_v1"
HARMONIZED_OUTPUT_ROOT = OUTPUT_DIR / "harmonized"


def _write_target_manifest(output: Path, prices: Path, benchmark: Path, rows: int) -> Path:
    manifest = {
        "artifact_schema_version": "harmonized_target_manifest_v1",
        "status": "completed",
        "horizon_benchmark_sessions": HORIZON,
        "sources": {
            "prices": {"path": str(prices.resolve()), "sha256": sha256_file(prices)},
            "benchmark": {"path": str(benchmark.resolve()), "sha256": sha256_file(benchmark)},
        },
        "target": {"path": str(output.resolve()), "sha256": sha256_file(output), "rows": rows},
    }
    path = output.with_name("harmonized_target_manifest.json")
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    return path


def _validate_harmonized_cli_paths(output: Path, prices: Path, benchmark: Path) -> None:
    resolved_output = output.resolve()
    try:
        relative = resolved_output.relative_to(HARMONIZED_OUTPUT_ROOT.resolve())
    except ValueError as exc:
        raise ValueError("harmonized output must be under outputs/harmonized/<run-id>") from exc
    if len(relative.parts) != 2 or relative.name != "harmonized_outperform_targets.csv":
        raise ValueError("harmonized output must equal outputs/harmonized/<run-id>/harmonized_outperform_targets.csv")
    if prices.resolve() != PRICES.resolve() or benchmark.resolve() != VNINDEX.resolve():
        raise ValueError("harmonized mode requires preregistered prices and benchmark")
    run_dir = resolved_output.parent
    if (run_dir / "harmonized_build_manifest.json").exists() or (run_dir / "harmonized_comparison_manifest.json").exists():
        raise FileExistsError(f"harmonized run artifacts are immutable after build: {run_dir}")
    if resolved_output.exists() or (run_dir / "harmonized_target_manifest.json").exists():
        raise FileExistsError(f"harmonized targets are immutable after creation: {resolved_output}")


def _clean_prices(frame: pd.DataFrame, require_ticker: bool = True) -> pd.DataFrame:
    work = frame.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce").dt.normalize()
    work["close"] = pd.to_numeric(work["close"], errors="coerce")
    required = ["date", "close"] + (["ticker"] if require_ticker else [])
    work = work.dropna(subset=required)
    if require_ticker:
        work["ticker"] = work["ticker"].astype(str).str.upper()
        if work.duplicated(["ticker", "date"]).any():
            raise ValueError("duplicate stock ticker/date rows")
        return work.sort_values(["ticker", "date"])
    if work.duplicated(["date"]).any():
        raise ValueError("duplicate benchmark dates")
    return work.sort_values("date")


def build_legacy_targets(prices: pd.DataFrame, benchmark: pd.DataFrame, horizon: int = HORIZON) -> pd.DataFrame:
    prices = _clean_prices(prices)
    frames = []
    for _, group in prices.groupby("ticker"):
        work = group[["ticker", "date", "close"]].copy().reset_index(drop=True)
        work[f"stock_return_T{horizon}"] = work["close"].shift(-horizon) / work["close"] - 1
        frames.append(work.drop(columns=["close"]))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    benchmark = _clean_prices(benchmark, require_ticker=False)
    benchmark[f"VNINDEX_return_T{horizon}"] = benchmark["close"].shift(-horizon) / benchmark["close"] - 1
    out = out.merge(benchmark[["date", f"VNINDEX_return_T{horizon}"]], on="date", how="left")
    out[f"excess_return_T{horizon}"] = out[f"stock_return_T{horizon}"] - out[f"VNINDEX_return_T{horizon}"]
    label = f"label_outperform_T{horizon}"
    out[label] = (out[f"excess_return_T{horizon}"] > 0).astype("Int64")
    out.loc[out[f"excess_return_T{horizon}"].isna(), label] = pd.NA
    return out


def build_harmonized_targets(
    prices: pd.DataFrame,
    benchmark: pd.DataFrame,
    horizon: int = HORIZON,
) -> pd.DataFrame:
    """Build stock and benchmark returns on identical benchmark entry/exit sessions."""
    if horizon != HORIZON:
        raise ValueError(f"harmonized protocol requires horizon={HORIZON}")
    stocks = _clean_prices(prices)
    bench = _clean_prices(benchmark, require_ticker=False).reset_index(drop=True)
    bench["target_exit_date"] = bench["date"].shift(-horizon)
    bench["benchmark_exit_close"] = bench["close"].shift(-horizon)
    bench["benchmark_session_index"] = range(len(bench))
    entries = bench.rename(columns={"date": "entry_date", "close": "benchmark_entry_close"})[
        ["entry_date", "target_exit_date", "benchmark_entry_close", "benchmark_exit_close", "benchmark_session_index"]
    ]
    stock_entries = stocks.rename(columns={"date": "entry_date", "close": "stock_entry_close"})
    out = stock_entries.merge(entries, on="entry_date", how="left", validate="many_to_one")
    exits = stocks.rename(columns={"date": "target_exit_date", "close": "stock_exit_close"})[
        ["ticker", "target_exit_date", "stock_exit_close"]
    ]
    out = out.merge(exits, on=["ticker", "target_exit_date"], how="left", validate="many_to_one")
    out["horizon_benchmark_sessions"] = horizon
    out["target_status"] = "ok"
    out.loc[out["benchmark_entry_close"].isna(), "target_status"] = "missing_benchmark_entry"
    out.loc[out["target_exit_date"].isna(), "target_status"] = "missing_benchmark_exit"
    out.loc[out["stock_exit_close"].isna() & out["target_exit_date"].notna(), "target_status"] = "missing_stock_exit"
    ok = out["target_status"] == "ok"
    out["stock_return_T20"] = pd.NA
    out["VNINDEX_return_T20"] = pd.NA
    out["excess_return_T20"] = pd.NA
    out.loc[ok, "stock_return_T20"] = out.loc[ok, "stock_exit_close"] / out.loc[ok, "stock_entry_close"] - 1
    out.loc[ok, "VNINDEX_return_T20"] = out.loc[ok, "benchmark_exit_close"] / out.loc[ok, "benchmark_entry_close"] - 1
    out.loc[ok, "excess_return_T20"] = out.loc[ok, "stock_return_T20"] - out.loc[ok, "VNINDEX_return_T20"]
    out["label_outperform_T20"] = pd.Series(pd.NA, index=out.index, dtype="Int64")
    out.loc[ok, "label_outperform_T20"] = (pd.to_numeric(out.loc[ok, "excess_return_T20"]) > 0).astype("Int64")
    out["artifact_schema_version"] = HARMONIZED_SCHEMA_VERSION
    if out.duplicated(["ticker", "entry_date"]).any():
        raise ValueError("duplicate harmonized target keys")
    return out.drop(columns=["benchmark_session_index"]).sort_values(["ticker", "entry_date"]).reset_index(drop=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build T+20 outperform targets")
    parser.add_argument("--mode", choices=["legacy", "harmonized"], default="legacy")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--prices", type=Path, default=PRICES)
    parser.add_argument("--benchmark", type=Path, default=VNINDEX)
    parser.add_argument("--horizon", type=int, default=HORIZON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    if args.mode == "legacy":
        output = args.output or OUT
    else:
        if args.output is None:
            raise ValueError("--output is required for harmonized mode")
        output = args.output
        _validate_harmonized_cli_paths(output, args.prices, args.benchmark)
    prices = pd.read_csv(args.prices, encoding="utf-8")
    benchmark = pd.read_csv(args.benchmark, encoding="utf-8")
    if args.mode == "legacy":
        result = build_legacy_targets(prices, benchmark, args.horizon)
    else:
        result = build_harmonized_targets(prices, benchmark, args.horizon)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, encoding="utf-8-sig")
    if args.mode == "harmonized":
        try:
            _write_target_manifest(output, args.prices, args.benchmark, len(result))
        except Exception:
            output.unlink(missing_ok=True)
            output.with_name("harmonized_target_manifest.json").unlink(missing_ok=True)
            output.with_name("harmonized_target_manifest.json.tmp").unlink(missing_ok=True)
            raise
    print(f"saved {output} rows={len(result)} mode={args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
