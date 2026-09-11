from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, REPORT_DIR, ensure_dirs, markdown_table

PRED = OUTPUT_DIR / "ml_predictions_outperform.csv"
TARGETS = OUTPUT_DIR / "outperform_targets.csv"
OUT = OUTPUT_DIR / "topk_portfolio_simulation.csv"
RANDOM_NULL_OUT = OUTPUT_DIR / "topk_random_null_summary.csv"
COST_SENSITIVITY_OUT = OUTPUT_DIR / "topk_cost_sensitivity_summary.csv"
REPORT = REPORT_DIR / "topk_backtest_with_cost_report.md"
ROUND_TRIP_COST = 0.005
COST_SENSITIVITY_RATES = (0.0, 0.0025, 0.005, 0.01)
RANDOM_NULL_DRAWS = 200
HORIZON = 20

RANDOM_NULL_COLUMNS = [
    "artifact_schema_version", "config", "model", "top_k", "draws", "periods",
    "model_cumulative_net_return", "null_cumulative_net_return_mean",
    "null_cumulative_net_return_std", "null_cumulative_net_return_p05",
    "null_cumulative_net_return_p50", "null_cumulative_net_return_p95",
    "model_percentile_vs_null", "one_sided_null_p_value",
    "null_mean_net_return_mean", "null_mean_net_return_std",
    "null_mean_net_excess_return_mean", "null_mean_net_excess_return_std",
    "round_trip_cost_rate", "holding_period_days",
]
COST_SENSITIVITY_COLUMNS = [
    "artifact_schema_version", "config", "model", "top_k", "strategy",
    "round_trip_cost_rate", "periods", "cumulative_net_return", "mean_net_return",
    "mean_net_excess_return", "annualized_sharpe", "annualization_factor",
    "max_drawdown", "hit_rate", "avg_turnover", "holding_period_days",
]
TOPK_PORTFOLIO_COLUMNS = [
    "artifact_schema_version", "config", "model", "entry_date", "exit_date", "date",
    "top_k", "strategy", "n", "tickers", "gross_return", "net_return",
    "gross_excess_return", "net_excess_return", "turnover", "transaction_cost",
    "round_trip_cost_rate", "holding_period_days",
]


def stable_rank_key(ticker: str, date: str, top_k: int, draw: int | None = None) -> str:
    suffix = "" if draw is None else f"|{draw}"
    return hashlib.sha256(f"{ticker}|{date}|{top_k}{suffix}".encode("utf-8")).hexdigest()


def portfolio_turnover(previous: dict[str, float], current: dict[str, float]) -> float:
    if not previous:
        return 1.0 if current else 0.0
    tickers = set(previous) | set(current)
    return 0.5 * sum(abs(current.get(ticker, 0.0) - previous.get(ticker, 0.0)) for ticker in tickers)


def weights_for(selected: pd.DataFrame) -> dict[str, float]:
    if selected.empty:
        return {}
    weight = 1.0 / len(selected)
    return {str(ticker): weight for ticker in selected["ticker"]}


def non_overlapping_rebalance_dates(dates: list[pd.Timestamp], calendar: list[pd.Timestamp], horizon: int = HORIZON) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    positions = {pd.Timestamp(date): index for index, date in enumerate(calendar)}
    output = []
    previous_exit = None
    for value in sorted(pd.Timestamp(date) for date in dates):
        if value not in positions:
            continue
        index = positions[value]
        if index + horizon >= len(calendar):
            continue
        exit_date = pd.Timestamp(calendar[index + horizon])
        if previous_exit is None or value >= previous_exit:
            output.append((value, exit_date))
            previous_exit = exit_date
    assert all(output[index][0] >= output[index - 1][1] for index in range(1, len(output)))
    return output


def max_drawdown(returns: pd.Series) -> float:
    values = pd.to_numeric(returns, errors="coerce").dropna()
    if values.empty:
        return float("nan")
    curve = (1 + values).cumprod()
    return float((curve / curve.cummax() - 1).min())


def summarize(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in frame.groupby(["config", "model", "top_k", "strategy"], dropna=False):
        returns = pd.to_numeric(group.sort_values("entry_date")["net_return"], errors="coerce").dropna()
        excess = pd.to_numeric(group["net_excess_return"], errors="coerce").dropna()
        std = returns.std(ddof=1)
        annualization = math.sqrt(252 / HORIZON)
        rows.append({
            "config": keys[0], "model": keys[1], "top_k": int(keys[2]), "strategy": keys[3],
            "periods": len(returns),
            "cumulative_net_return": float((1 + returns).prod() - 1) if len(returns) else np.nan,
            "mean_net_return": float(returns.mean()) if len(returns) else np.nan,
            "mean_net_excess_return": float(excess.mean()) if len(excess) else np.nan,
            "annualized_sharpe": float(returns.mean() / std * annualization) if len(returns) > 1 and std > 0 else np.nan,
            "annualization_factor": annualization,
            "max_drawdown": max_drawdown(returns), "hit_rate": float((returns > 0).mean()) if len(returns) else np.nan,
            "avg_turnover": float(group["turnover"].mean()), "holding_period_days": HORIZON,
        })
    return pd.DataFrame(rows)


def build_cost_sensitivity_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "strategy" not in frame or not frame["strategy"].eq("model_topk").any():
        return pd.DataFrame(columns=COST_SENSITIVITY_COLUMNS)
    model_rows = frame[frame["strategy"].eq("model_topk")].copy()
    results = []
    for rate in COST_SENSITIVITY_RATES:
        adjusted = model_rows.copy()
        adjusted["transaction_cost"] = pd.to_numeric(adjusted["turnover"], errors="coerce") * rate
        adjusted["net_return"] = pd.to_numeric(adjusted["gross_return"], errors="coerce") - adjusted["transaction_cost"]
        adjusted["net_excess_return"] = pd.to_numeric(adjusted["gross_excess_return"], errors="coerce") - adjusted["transaction_cost"]
        summary = summarize(adjusted)
        summary.insert(0, "artifact_schema_version", "topk_cost_sensitivity_v1")
        summary.insert(5, "round_trip_cost_rate", rate)
        results.append(summary)
    return pd.concat(results, ignore_index=True)[COST_SENSITIVITY_COLUMNS]


def _distribution_stats(values: list[float]) -> tuple[float, float, float, float, float]:
    series = pd.Series(values, dtype=float)
    return (
        float(series.mean()), float(series.std(ddof=1)), float(series.quantile(0.05)),
        float(series.quantile(0.50)), float(series.quantile(0.95)),
    )


def build_random_null_summary(
    pred: pd.DataFrame,
    periods: list[tuple[pd.Timestamp, pd.Timestamp]],
    portfolio_rows: pd.DataFrame,
    draws: int = RANDOM_NULL_DRAWS,
) -> pd.DataFrame:
    required = {"config", "model", "date", "ticker", "stock_return_T20", "excess_return_T20"}
    if pred.empty or not required.issubset(pred.columns) or draws <= 0:
        return pd.DataFrame(columns=RANDOM_NULL_COLUMNS)
    model_summary = summarize(portfolio_rows[portfolio_rows["strategy"].eq("model_topk")]) if not portfolio_rows.empty else pd.DataFrame()
    rows = []
    for (config, model), model_pred in pred.groupby(["config", "model"], dropna=False, sort=True):
        for top_k in (5, 10):
            cumulative_values = []
            mean_values = []
            excess_values = []
            period_counts = []
            for draw in range(draws):
                previous: dict[str, float] = {}
                net_returns = []
                net_excess = []
                for entry, _ in periods:
                    group = model_pred[model_pred["date"].eq(entry)].copy()
                    if len(group) < min(top_k, 3):
                        continue
                    group["_null_rank"] = group["ticker"].astype(str).map(
                        lambda ticker: stable_rank_key(ticker, str(entry.date()), top_k, draw)
                    )
                    selected = group.sort_values("_null_rank").head(top_k)
                    current = weights_for(selected)
                    turnover = portfolio_turnover(previous, current)
                    previous = current
                    cost = ROUND_TRIP_COST * turnover
                    net_returns.append(float(selected["stock_return_T20"].mean()) - cost)
                    net_excess.append(float(selected["excess_return_T20"].mean()) - cost)
                if net_returns:
                    cumulative_values.append(float(np.prod(1 + np.asarray(net_returns)) - 1))
                    mean_values.append(float(np.mean(net_returns)))
                    excess_values.append(float(np.mean(net_excess)))
                    period_counts.append(len(net_returns))
            if not cumulative_values:
                continue
            match = model_summary[
                model_summary["config"].eq(config)
                & model_summary["model"].eq(model)
                & model_summary["top_k"].eq(top_k)
            ]
            if match.empty:
                continue
            model_cumulative = float(match.iloc[0]["cumulative_net_return"])
            cumulative_stats = _distribution_stats(cumulative_values)
            mean_stats = _distribution_stats(mean_values)
            excess_stats = _distribution_stats(excess_values)
            rows.append({
                "artifact_schema_version": "topk_random_null_summary_v1",
                "config": config, "model": model, "top_k": top_k, "draws": len(cumulative_values),
                "periods": min(period_counts), "model_cumulative_net_return": model_cumulative,
                "null_cumulative_net_return_mean": cumulative_stats[0],
                "null_cumulative_net_return_std": cumulative_stats[1],
                "null_cumulative_net_return_p05": cumulative_stats[2],
                "null_cumulative_net_return_p50": cumulative_stats[3],
                "null_cumulative_net_return_p95": cumulative_stats[4],
                "model_percentile_vs_null": float(np.mean(np.asarray(cumulative_values) <= model_cumulative)) if pd.notna(model_cumulative) else np.nan,
                "one_sided_null_p_value": float((1 + np.sum(np.asarray(cumulative_values) >= model_cumulative)) / (len(cumulative_values) + 1)) if pd.notna(model_cumulative) else np.nan,
                "null_mean_net_return_mean": mean_stats[0], "null_mean_net_return_std": mean_stats[1],
                "null_mean_net_excess_return_mean": excess_stats[0], "null_mean_net_excess_return_std": excess_stats[1],
                "round_trip_cost_rate": ROUND_TRIP_COST, "holding_period_days": HORIZON,
            })
    return pd.DataFrame(rows, columns=RANDOM_NULL_COLUMNS)


def write_supplemental_artifacts(random_null: pd.DataFrame, cost_sensitivity: pd.DataFrame) -> None:
    random_null.reindex(columns=RANDOM_NULL_COLUMNS).to_csv(RANDOM_NULL_OUT, index=False, encoding="utf-8-sig")
    cost_sensitivity.reindex(columns=COST_SENSITIVITY_COLUMNS).to_csv(COST_SENSITIVITY_OUT, index=False, encoding="utf-8-sig")


def append_supplemental_report(lines: list[str], random_null: pd.DataFrame, cost_sensitivity: pd.DataFrame) -> None:
    lines += [
        "## Deterministic random-null distribution", "",
        markdown_table(random_null.round(4)) if not random_null.empty else "Random-null summary unavailable.", "",
        "Limitation: deterministic hash draws are a reproducible empirical null, not independent market realizations; overlapping names and limited OOS periods reduce inferential strength. Draw-level results are intentionally not stored.", "",
        "## Cost sensitivity", "",
        markdown_table(cost_sensitivity.round(4)) if not cost_sensitivity.empty else "Cost-sensitivity summary unavailable.", "",
        "Limitation: fixed proportional round-trip rates omit market impact, spread variation, taxes, liquidity constraints, and execution timing; gross returns and turnover are held unchanged across rates.", "",
    ]


def _write_early_exit(lines: list[str], message: str) -> int:
    pd.DataFrame(columns=TOPK_PORTFOLIO_COLUMNS).to_csv(OUT, index=False, encoding="utf-8-sig")
    random_null = pd.DataFrame(columns=RANDOM_NULL_COLUMNS)
    cost_sensitivity = pd.DataFrame(columns=COST_SENSITIVITY_COLUMNS)
    write_supplemental_artifacts(random_null, cost_sensitivity)
    lines.append(message)
    lines += ["", "## Summary", "", "Insufficient OOS periods.", ""]
    append_supplemental_report(lines, random_null, cost_sensitivity)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def main() -> int:
    ensure_dirs()
    lines = ["# Top-K backtest with turnover cost", "", "Secondary exploratory simulation using non-overlapping OOS T+20 periods; not investment recommendation.", ""]
    if not PRED.exists() or not TARGETS.exists():
        return _write_early_exit(lines, "Predictions or targets unavailable.")
    pred = pd.read_csv(PRED, encoding="utf-8-sig")
    targets = pd.read_csv(TARGETS, encoding="utf-8-sig")
    if pred.empty or "fold_id" not in pred:
        return _write_early_exit(lines, "Valid OOS fold predictions unavailable; simulation skipped.")
    pred["date"] = pd.to_datetime(pred["date"], errors="coerce")
    targets["date"] = pd.to_datetime(targets["date"], errors="coerce")
    pred = pred.drop(columns=["stock_return_T20", "VNINDEX_return_T20", "excess_return_T20"], errors="ignore")
    pred = pred.merge(targets[["ticker", "date", "stock_return_T20", "VNINDEX_return_T20", "excess_return_T20"]], on=["ticker", "date"], how="left")
    pred = pred.dropna(subset=["date", "ticker", "pred_proba_outperform", "stock_return_T20", "excess_return_T20"])
    pred = pred.drop_duplicates(["config", "model", "date", "ticker"], keep="last")
    calendar = sorted(pd.Timestamp(date) for date in targets["date"].dropna().unique())
    periods = non_overlapping_rebalance_dates(list(pred["date"].unique()), calendar)
    rows = []
    previous: dict[tuple[str, str, int, str], dict[str, float]] = {}
    for config, model, entry, exit_date in [
        (config, model, entry, exit_date)
        for config in pred["config"].unique()
        for model in pred[pred["config"].eq(config)]["model"].unique()
        for entry, exit_date in periods
    ]:
        group = pred[pred["config"].eq(config) & pred["model"].eq(model) & pred["date"].eq(entry)].copy()
        if group.empty:
            continue
        for top_k in (5, 10):
            ranked_sets = {
                "model_topk": group.nlargest(top_k, "pred_proba_outperform"),
                "equal_weight_universe": group,
            }
            random_group = group.assign(_rank=group.apply(lambda row: stable_rank_key(str(row["ticker"]), str(entry.date()), top_k), axis=1))
            ranked_sets["random_topk_deterministic"] = random_group.sort_values("_rank").head(top_k)
            for strategy, selected in ranked_sets.items():
                if len(selected) < min(top_k, 3):
                    continue
                current = weights_for(selected)
                key = (config, model, top_k, strategy)
                turnover = portfolio_turnover(previous.get(key, {}), current)
                previous[key] = current
                cost = ROUND_TRIP_COST * turnover
                gross = float(selected["stock_return_T20"].mean())
                gross_excess = float(selected["excess_return_T20"].mean())
                rows.append({
                    "artifact_schema_version": "topk_nonoverlap_v2", "config": config, "model": model,
                    "entry_date": entry, "exit_date": exit_date, "date": entry, "top_k": top_k,
                    "strategy": strategy, "n": len(selected), "tickers": ",".join(sorted(selected["ticker"].astype(str))),
                    "gross_return": gross, "net_return": gross - cost,
                    "gross_excess_return": gross_excess, "net_excess_return": gross_excess - cost,
                    "turnover": turnover, "transaction_cost": cost, "round_trip_cost_rate": ROUND_TRIP_COST,
                    "holding_period_days": HORIZON,
                })
    out = pd.DataFrame(rows, columns=TOPK_PORTFOLIO_COLUMNS)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    summary = summarize(out) if not out.empty else pd.DataFrame()
    lines += ["## Summary", "", markdown_table(summary.round(4)) if not summary.empty else "Insufficient OOS periods.", ""]
    random_null = build_random_null_summary(pred, periods, out)
    cost_sensitivity = build_cost_sensitivity_summary(out)
    write_supplemental_artifacts(random_null, cost_sensitivity)
    append_supplemental_report(lines, random_null, cost_sensitivity)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {OUT} rows={len(out)}")
    print(f"saved {RANDOM_NULL_OUT} rows={len(random_null)}")
    print(f"saved {COST_SENSITIVITY_OUT} rows={len(cost_sensitivity)}")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
