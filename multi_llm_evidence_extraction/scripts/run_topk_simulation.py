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
REPORT = REPORT_DIR / "topk_backtest_with_cost_report.md"
ROUND_TRIP_COST = 0.005
HORIZON = 20


def stable_rank_key(ticker: str, date: str, top_k: int) -> str:
    return hashlib.sha256(f"{ticker}|{date}|{top_k}".encode("utf-8")).hexdigest()


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


def main() -> int:
    ensure_dirs()
    lines = ["# Top-K backtest with turnover cost", "", "Secondary exploratory simulation using non-overlapping OOS T+20 periods; not investment recommendation.", ""]
    if not PRED.exists() or not TARGETS.exists():
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        lines.append("Predictions or targets unavailable.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0
    pred = pd.read_csv(PRED, encoding="utf-8-sig")
    targets = pd.read_csv(TARGETS, encoding="utf-8-sig")
    if pred.empty or "fold_id" not in pred:
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        lines.append("Valid OOS fold predictions unavailable; simulation skipped.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0
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
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    summary = summarize(out) if not out.empty else pd.DataFrame()
    lines += ["## Summary", "", markdown_table(summary.round(4)) if not summary.empty else "Insufficient OOS periods.", ""]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {OUT} rows={len(out)}")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
