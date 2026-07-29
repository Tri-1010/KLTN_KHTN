from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, REPORT_DIR, ROOT, ensure_dirs, markdown_table
from run_event_window_stat_tests import benjamini_hochberg, bootstrap_ci, cliffs_delta, mann_whitney_u

EVENTS = OUTPUT_DIR / "event_window_outcomes.csv"
PRICES = ROOT / "data" / "prices" / "all_vn30_prices.csv"
VNINDEX = ROOT / "data" / "prices_extended" / "VNINDEX.csv"
DETAIL_OUT = OUTPUT_DIR / "placebo_pre_event_outcomes.csv"
OUT = OUTPUT_DIR / "placebo_pre_event_stat_tests.csv"
REPORT = REPORT_DIR / "placebo_pre_event_tests_report.md"
PRE_WINDOWS = (("T-20:T-1", -20, -1), ("T-60:T-21", -60, -21))
DETAIL_COLUMNS = [
    "artifact_schema_version", "news_id", "ticker", "effective_date", "placebo_window",
    "pre_window_start_offset", "pre_window_end_offset", "pre_window_start_date",
    "pre_window_end_date", "ticker_relevance", "materiality", "direction", "event_type",
    "raw_return", "benchmark_return", "market_adjusted_return",
]
TEST_COLUMNS = [
    "artifact_schema_version", "placebo_window", "pre_window_start_offset",
    "pre_window_end_offset", "comparison", "metric", "n_a", "n_b", "mean_a", "mean_b",
    "diff_mean", "mann_whitney_u", "z_score", "tie_corrected_variance", "p_value_raw",
    "cliffs_delta", "diff_ci_low", "diff_ci_high", "cliffs_delta_ci_low",
    "cliffs_delta_ci_high", "p_value_bh", "reject_fdr_05", "robust_positive_effect",
    "robust_negative_effect", "correction_method",
]


def trailing_return(frame: pd.DataFrame, effective_date: pd.Timestamp, start_offset: int, end_offset: int) -> tuple[float | None, pd.Timestamp | None, pd.Timestamp | None]:
    work = frame.sort_values("date").dropna(subset=["date", "close"]).reset_index(drop=True)
    event_pos = int(work["date"].searchsorted(effective_date, side="left"))
    start_pos, end_pos = event_pos + start_offset, event_pos + end_offset
    if start_pos < 0 or end_pos < start_pos or end_pos >= len(work):
        return None, None, None
    start, end = float(work.loc[start_pos, "close"]), float(work.loc[end_pos, "close"])
    if not start:
        return None, None, None
    return end / start - 1, pd.Timestamp(work.loc[start_pos, "date"]), pd.Timestamp(work.loc[end_pos, "date"])


def build_placebo_outcomes(events: pd.DataFrame, prices: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    required = {"news_id", "ticker", "effective_date", "materiality", "direction"}
    if events.empty or not required.issubset(events.columns):
        return pd.DataFrame(columns=DETAIL_COLUMNS)
    unique_events = events.drop_duplicates(["news_id", "ticker", "effective_date"]).copy()
    unique_events["effective_date"] = pd.to_datetime(unique_events["effective_date"], errors="coerce").dt.normalize()
    rows = []
    for _, event in unique_events.sort_values(["ticker", "effective_date", "news_id"]).iterrows():
        effective = event["effective_date"]
        ticker = str(event["ticker"]).upper()
        if pd.isna(effective):
            continue
        stock = prices[prices["ticker"].astype(str).str.upper().eq(ticker)]
        for name, start_offset, end_offset in PRE_WINDOWS:
            raw, start_date, end_date = trailing_return(stock, effective, start_offset, end_offset)
            market, market_start, market_end = trailing_return(benchmark, effective, start_offset, end_offset)
            if raw is None or market is None or start_date != market_start or end_date != market_end:
                continue
            rows.append({
                "artifact_schema_version": "placebo_pre_event_outcomes_v1", "news_id": event["news_id"],
                "ticker": ticker, "effective_date": effective, "placebo_window": name,
                "pre_window_start_offset": start_offset, "pre_window_end_offset": end_offset,
                "pre_window_start_date": start_date, "pre_window_end_date": end_date,
                "ticker_relevance": event.get("ticker_relevance"), "materiality": event.get("materiality"),
                "direction": event.get("direction"), "event_type": event.get("event_type"),
                "raw_return": raw, "benchmark_return": market, "market_adjusted_return": raw - market,
            })
    return pd.DataFrame(rows, columns=DETAIL_COLUMNS)


def non_overlapping_placebos(frame: pd.DataFrame) -> pd.DataFrame:
    selected = []
    for _, group in frame.sort_values("effective_date").groupby("ticker", sort=False):
        previous_end = None
        for _, row in group.iterrows():
            start = pd.to_datetime(row["pre_window_start_date"], errors="coerce")
            end = pd.to_datetime(row["pre_window_end_date"], errors="coerce")
            if pd.isna(start) or pd.isna(end) or end >= pd.to_datetime(row["effective_date"]):
                continue
            if previous_end is None or start > previous_end:
                selected.append(row)
                previous_end = end
    return pd.DataFrame(selected) if selected else frame.iloc[0:0].copy()


def compare_placebo(frame: pd.DataFrame, window: str, field_a: str, values_a: set[str], field_b: str, values_b: set[str]) -> dict[str, object] | None:
    sample = non_overlapping_placebos(frame[frame["placebo_window"].eq(window)].copy())
    first = pd.to_numeric(sample[sample[field_a].isin(values_a)]["market_adjusted_return"], errors="coerce").dropna().tolist()
    second = pd.to_numeric(sample[sample[field_b].isin(values_b)]["market_adjusted_return"], errors="coerce").dropna().tolist()
    if len(first) < 3 or len(second) < 3:
        return None
    u, p_value, z_score, variance = mann_whitney_u(first, second)
    start_offset, end_offset = next((start, end) for name, start, end in PRE_WINDOWS if name == window)
    return {
        "placebo_window": window, "pre_window_start_offset": start_offset,
        "pre_window_end_offset": end_offset,
        "comparison": f"{field_a}={'+'.join(sorted(values_a))} vs {field_b}={'+'.join(sorted(values_b))}",
        "metric": "market_adjusted_return", "n_a": len(first), "n_b": len(second),
        "mean_a": float(pd.Series(first).mean()), "mean_b": float(pd.Series(second).mean()),
        "diff_mean": float(pd.Series(first).mean() - pd.Series(second).mean()),
        "mann_whitney_u": u, "z_score": z_score, "tie_corrected_variance": variance,
        "p_value_raw": p_value, "cliffs_delta": cliffs_delta(first, second), **bootstrap_ci(first, second),
    }


def build_stat_tests(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if not detail.empty:
        for window, _, _ in PRE_WINDOWS:
            for result in (
                compare_placebo(detail, window, "direction", {"support"}, "direction", {"risk"}),
                compare_placebo(detail, window, "materiality", {"high", "medium"}, "materiality", {"low"}),
            ):
                if result:
                    rows.append(result)
    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(columns=TEST_COLUMNS)
    out["p_value_bh"] = benjamini_hochberg(out["p_value_raw"].fillna(1.0).tolist())
    out["reject_fdr_05"] = out["p_value_bh"] <= 0.05
    out["robust_positive_effect"] = out["reject_fdr_05"] & (out["diff_ci_low"] > 0)
    out["robust_negative_effect"] = out["reject_fdr_05"] & (out["diff_ci_high"] < 0)
    out["correction_method"] = "Benjamini-Hochberg"
    out["artifact_schema_version"] = "placebo_pre_event_tests_v1"
    return out.reindex(columns=TEST_COLUMNS)


def main() -> int:
    ensure_dirs()
    detail = pd.DataFrame(columns=DETAIL_COLUMNS)
    message = None
    if not EVENTS.exists() or not PRICES.exists() or not VNINDEX.exists():
        message = "Required event or price artifacts unavailable."
    else:
        try:
            events = pd.read_csv(EVENTS, encoding="utf-8-sig")
            prices = pd.read_csv(PRICES, encoding="utf-8")
            benchmark = pd.read_csv(VNINDEX, encoding="utf-8")
            prices["date"] = pd.to_datetime(prices["date"], errors="coerce").dt.normalize()
            benchmark["date"] = pd.to_datetime(benchmark["date"], errors="coerce").dt.normalize()
            detail = build_placebo_outcomes(events, prices, benchmark)
        except (pd.errors.EmptyDataError, KeyError, ValueError) as exc:
            message = f"Placebo inputs invalid: {exc}"
    tests = build_stat_tests(detail)
    detail.to_csv(DETAIL_OUT, index=False, encoding="utf-8-sig")
    tests.to_csv(OUT, index=False, encoding="utf-8-sig")
    lines = [
        "# Placebo pre-event tests", "",
        "Negative-control windows end before event effective date. Primary metric: VNINDEX-adjusted return. Non-overlapping samples, tie-corrected Mann–Whitney, BH-FDR, deterministic bootstrap CI. Exploratory only; no causal claim.", "",
    ]
    if message:
        lines += [message, ""]
    lines += ["## Results", "", markdown_table(tests.round(4)) if not tests.empty else "Insufficient data for placebo tests.", ""]
    if not tests.empty and (tests["robust_positive_effect"] | tests["robust_negative_effect"]).any():
        lines += ["Pre-event differences survive robustness gates. Treat corresponding post-event interpretation as potentially confounded by pre-trends.", ""]
    else:
        lines += ["No pre-event comparison survives BH-FDR 5% with bootstrap CI excluding zero; this does not prove absence of pre-trends.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {DETAIL_OUT} rows={len(detail)}")
    print(f"saved {OUT} rows={len(tests)}")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
