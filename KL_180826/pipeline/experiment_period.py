"""
Experiment: does changing the time unit from quarter to 1-month or 2-month
periods change the keyword contribution (H1)?

This ad-hoc research script rebuilds technical features, keyword features and
the next-period up/down label at a configurable period granularity directly
from the raw price and processed-news data, then compares Config_A (technical
only) vs Config_C (technical + keyword) using the same time-series-aware
evaluation as TASK 10.

It does NOT touch the production pipeline outputs.

Usage:
    python -m pipeline.experiment_period
"""

from __future__ import annotations

import sys

for _stream in (sys.stdout, sys.stderr):
    _rc = getattr(_stream, "reconfigure", None)
    if _rc is not None:
        try:
            _rc(encoding="utf-8", errors="replace")
        except Exception:
            pass

import math
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from pipeline.task7_tech_features import compute_daily_indicators, _find_column
from pipeline.task9_kw_features import (
    compute_keyword_counts,
    compute_sentiment_scores,
    add_coverage_features,
)
from pipeline.task8_keywords import get_curated_keywords, get_all_keywords_flat
from pipeline.task10_train import (
    build_ml_models,
    evaluate_model,
    fit_imputer,
    prepare_features,
)

PRICES_PATH = "data/prices/all_vn30_prices.csv"
NEWS_PATH = "data/news/processed/all_news_processed.csv"

# Map a period unit name to the number of months per period.
PERIOD_MONTHS = {"month": 1, "2month": 2, "quarter": 3}

# Day-bucketed units (not aligned to calendar months). Value = days per period.
PERIOD_DAYS = {"1day": 1, "1week": 7, "2week": 14}

# Fixed epoch for day-bucketed period indexing. Earlier than any data so all
# indices are non-negative; the absolute value is irrelevant, only ordering.
_DAY_EPOCH = pd.Timestamp("2021-01-01")


# ---------------------------------------------------------------------------
# Period id assignment (calendar-month based)
# ---------------------------------------------------------------------------


def assign_period_id(date_val: pd.Timestamp, months_per: int) -> str:
    """Return a sortable period id for *date_val* given the period length.

    Format: 'YYYYPNN' where NN is a zero-padded period index within the year.
    - months_per=1  -> 12 periods/year (monthly)
    - months_per=2  -> 6 periods/year
    - months_per=3  -> 4 periods/year (quarterly)

    Zero-padding keeps lexicographic order aligned with chronological order.
    """
    period = (date_val.month - 1) // months_per + 1
    return f"{date_val.year}P{period:02d}"


def _next_period_id(period_id: str, months_per: int) -> str:
    """Return the period id immediately following a calendar-month *period_id*."""
    year = int(period_id[:4])
    p = int(period_id[5:])
    n_periods = 12 // months_per
    if p >= n_periods:
        return f"{year + 1}P01"
    return f"{year}P{p + 1:02d}"


# ---------------------------------------------------------------------------
# Period id assignment (fixed-length day buckets, e.g. 2-week)
# ---------------------------------------------------------------------------


def assign_day_period_id(date_val: pd.Timestamp, days_per: int) -> str:
    """Return a sortable id for a fixed-length day bucket.

    Format: 'D{index:05d}', where index = days_since_epoch // days_per.
    Independent of calendar month boundaries, so it works for 2-week periods.
    """
    delta_days = (date_val.normalize() - _DAY_EPOCH).days
    idx = delta_days // days_per
    return f"D{idx:05d}"


def _next_day_period_id(period_id: str) -> str:
    """Return the day-bucket id immediately following *period_id*."""
    idx = int(period_id[1:])
    return f"D{idx + 1:05d}"


def make_period_funcs(unit: str):
    """Return (assign_fn, next_fn) for the requested unit.

    assign_fn maps a Timestamp -> period id string.
    next_fn maps a period id -> the following period id.
    """
    if unit in PERIOD_MONTHS:
        m = PERIOD_MONTHS[unit]
        return (
            lambda d: assign_period_id(d, m),
            lambda pid: _next_period_id(pid, m),
        )
    if unit in PERIOD_DAYS:
        n = PERIOD_DAYS[unit]
        return (
            lambda d: assign_day_period_id(d, n),
            _next_day_period_id,
        )
    raise ValueError(f"Unknown period unit: {unit}")


# ---------------------------------------------------------------------------
# Technical features per period (mirrors TASK 7 aggregation, period-agnostic)
# ---------------------------------------------------------------------------


def _aggregate_period_tech(daily_df: pd.DataFrame) -> dict:
    """Aggregate one (ticker, period) of daily indicator data into features."""
    if daily_df.empty:
        return {}
    f: Dict[str, Any] = {}
    close = daily_df["close"]
    high = daily_df["high"]
    low = daily_df["low"]
    volume = daily_df["volume"]
    daily_return = daily_df["daily_return"]

    close_first = close.iloc[0]
    close_last = close.iloc[-1]
    n_days = len(daily_df)

    f["return_p"] = (close_last - close_first) / close_first if close_first else 0.0
    f["return_mean_daily"] = daily_return.mean()
    f["return_std_daily"] = daily_return.std()
    f["volatility_p"] = (
        f["return_std_daily"] * math.sqrt(n_days)
        if pd.notna(f["return_std_daily"]) else np.nan
    )
    avg_close = close.mean()
    f["price_range_p"] = (high.max() - low.min()) / avg_close if avg_close else 0.0
    f["volume_mean_p"] = volume.mean()
    f["volume_change_p"] = np.nan  # filled later

    sma20_end = daily_df["SMA_20"].iloc[-1] if "SMA_20" in daily_df else np.nan
    ema20_end = daily_df["EMA_20"].iloc[-1] if "EMA_20" in daily_df else np.nan
    f["sma20_end"] = sma20_end
    f["ema20_end"] = ema20_end
    f["price_vs_sma20"] = (
        (close_last - sma20_end) / sma20_end
        if pd.notna(sma20_end) and sma20_end else np.nan
    )

    if "RSI_14" in daily_df:
        f["rsi_mean_p"] = daily_df["RSI_14"].mean()
        f["rsi_end_p"] = daily_df["RSI_14"].iloc[-1]
    else:
        f["rsi_mean_p"] = f["rsi_end_p"] = np.nan

    mh = _find_column(daily_df, "MACDh_")
    f["macd_hist_mean_p"] = daily_df[mh].mean() if mh else np.nan

    bbl = _find_column(daily_df, "BBL_")
    bbu = _find_column(daily_df, "BBU_")
    if bbl and bbu:
        rng = (daily_df[bbu] - daily_df[bbl]).replace(0, np.nan)
        f["bb_position_p"] = ((close - daily_df[bbl]) / rng).mean()
    else:
        f["bb_position_p"] = np.nan

    f["avg_close"] = avg_close
    f["trading_days"] = n_days
    return f


def build_period_technical(prices_df: pd.DataFrame, assign_fn) -> pd.DataFrame:
    """Build per-(ticker, period) technical features + avg_close."""
    prices_df = prices_df.copy()
    prices_df["date"] = pd.to_datetime(prices_df["date"], errors="coerce")
    prices_df = prices_df.sort_values(["ticker", "date"])

    rows = []
    for ticker in prices_df["ticker"].unique():
        tdf = prices_df[prices_df["ticker"] == ticker].copy()
        tdf = compute_daily_indicators(tdf)
        tdf["period_id"] = tdf["date"].apply(assign_fn)

        per_rows = []
        for pid in sorted(tdf["period_id"].unique()):
            feats = _aggregate_period_tech(tdf[tdf["period_id"] == pid])
            feats["ticker"] = ticker
            feats["period_id"] = pid
            per_rows.append(feats)

        pf = pd.DataFrame(per_rows).sort_values("period_id").reset_index(drop=True)
        vol_prev = pf["volume_mean_p"].shift(1)
        pf["volume_change_p"] = (pf["volume_mean_p"] - vol_prev) / vol_prev.replace(0, np.nan)
        pf["return_prev_p"] = pf["return_p"].shift(1)
        pf["return_2p_ago"] = pf["return_p"].shift(2)
        rows.append(pf)

    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------------------
# News aggregation + keyword features per period
# ---------------------------------------------------------------------------


def build_period_news(news_df: pd.DataFrame, assign_fn) -> pd.DataFrame:
    """Aggregate processed news into (ticker, period) news_count + combined_text."""
    df = news_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["period_id"] = df["date"].apply(assign_fn)
    agg = (
        df.groupby(["ticker", "period_id"])
        .agg(
            news_count=("text_tokenized", "size"),
            combined_text=("text_tokenized", lambda ts: " ".join(
                str(t) for t in ts if pd.notna(t))),
        )
        .reset_index()
    )
    return agg


def build_period_keyword_features(news_agg: pd.DataFrame) -> pd.DataFrame:
    """Compute keyword features on a period-keyed news aggregation.

    Reuses TASK 9 counting/sentiment/coverage helpers. The helpers key on
    'quarter_id', so we temporarily rename period_id -> quarter_id.
    """
    kw_by_dir = get_curated_keywords()
    all_kw = get_all_keywords_flat()

    tmp = news_agg.rename(columns={"period_id": "quarter_id"}).copy()
    tmp = compute_keyword_counts(tmp, all_kw)
    tmp = compute_sentiment_scores(tmp, kw_by_dir)
    tmp = add_coverage_features(tmp)
    if "combined_text" in tmp.columns:
        tmp = tmp.drop(columns=["combined_text"])
    tmp = tmp.rename(columns={"quarter_id": "period_id"})
    return tmp


# ---------------------------------------------------------------------------
# Labels per period
# ---------------------------------------------------------------------------


def build_labels(tech_df: pd.DataFrame, next_fn) -> pd.DataFrame:
    """label_basic = 1 if next-period avg_close > current avg_close else 0."""
    close_lookup = tech_df.set_index(["ticker", "period_id"])["avg_close"]
    out = tech_df[["ticker", "period_id", "avg_close"]].copy()
    out["next_period_id"] = out["period_id"].apply(next_fn)
    out["next_avg_close"] = out.apply(
        lambda r: close_lookup.get((r["ticker"], r["next_period_id"]), np.nan), axis=1
    )
    out = out.dropna(subset=["next_avg_close"])
    out["label_basic"] = (out["next_avg_close"] > out["avg_close"]).astype(int)
    return out[["ticker", "period_id", "label_basic"]]


# ---------------------------------------------------------------------------
# Split / evaluate
# ---------------------------------------------------------------------------


def _period_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Time-series split: last 20% of periods (>=1) form the test set."""
    periods = sorted(df["period_id"].unique())
    n_test = max(1, int(len(periods) * 0.2))
    test_set = set(periods[-n_test:])
    train = df[~df["period_id"].isin(test_set)].copy()
    test = df[df["period_id"].isin(test_set)].copy()
    return train, test


def run_for_unit(unit: str) -> List[Dict[str, Any]]:
    assign_fn, next_fn = make_period_funcs(unit)
    prices = pd.read_csv(PRICES_PATH, encoding="utf-8")
    news = pd.read_csv(NEWS_PATH, encoding="utf-8")

    tech = build_period_technical(prices, assign_fn)
    news_agg = build_period_news(news, assign_fn)
    kw = build_period_keyword_features(news_agg)
    labels = build_labels(tech, next_fn)

    # Merge: technical + labels (inner) then keyword (inner) — same as TASK 10
    tech_cols = [
        "return_p", "return_mean_daily", "return_std_daily", "volatility_p",
        "price_range_p", "volume_mean_p", "volume_change_p", "sma20_end",
        "ema20_end", "price_vs_sma20", "rsi_mean_p", "rsi_end_p",
        "macd_hist_mean_p", "bb_position_p", "return_prev_p", "return_2p_ago",
    ]
    merged = tech.merge(labels, on=["ticker", "period_id"], how="inner")
    merged = merged.merge(kw, on=["ticker", "period_id"], how="inner")
    merged = merged.dropna(subset=["label_basic"])

    kw_cols = [c for c in kw.columns if c not in ("ticker", "period_id")]
    configs = {"Config_A": tech_cols, "Config_C": tech_cols + kw_cols}

    train_df, test_df = _period_split(merged)

    results: List[Dict[str, Any]] = []
    n_periods = merged["period_id"].nunique()
    for cname, cols in configs.items():
        avail = [c for c in cols if c in train_df.columns]
        numeric_avail = train_df[avail].select_dtypes(include=[np.number]).columns.tolist()
        usable = [c for c in numeric_avail if not train_df[c].isna().all()]
        if not usable:
            continue
        imp, _ = fit_imputer(train_df, usable)
        X_tr, y_tr = prepare_features(train_df, usable, imputer=imp)
        X_te, y_te = prepare_features(test_df, usable, imputer=imp)
        common = [c for c in X_tr.columns if c in X_te.columns]
        X_tr, X_te = X_tr[common], X_te[common]
        if y_tr.nunique() < 2 or y_te.nunique() < 2:
            continue
        for mname, model in build_ml_models(y_tr).items():
            model.fit(X_tr, y_tr)
            r = evaluate_model(model, X_te, y_te, mname, cname)
            r["unit"] = unit
            r["n_samples"] = len(merged)
            r["n_periods"] = n_periods
            r["test_samples"] = len(X_te)
            results.append(r)
    return results


def main() -> None:
    all_rows: List[Dict[str, Any]] = []
    for unit in ("1day", "1week", "2week", "month", "2month", "quarter"):
        all_rows.extend(run_for_unit(unit))

    df = pd.DataFrame(all_rows)
    pivot = df.pivot_table(
        index=["unit", "n_samples", "n_periods", "test_samples", "model"],
        columns="config",
        values="balanced_accuracy",
    ).reset_index()
    pivot["delta_C_minus_A"] = pivot["Config_C"] - pivot["Config_A"]

    out_path = "reports/period_experiment.csv"
    pivot.to_csv(out_path, index=False)

    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 20)
    print("\n" + "=" * 78)
    print("PERIOD EXPERIMENT — Config_A vs Config_C (Balanced Accuracy)")
    print("=" * 78)
    cols = ["unit", "n_samples", "test_samples", "model", "Config_A", "Config_C", "delta_C_minus_A"]
    print(pivot[cols].round(4).to_string(index=False))

    print("\n--- Mean by unit ---")
    summary = pivot.groupby("unit").agg(
        n_samples=("n_samples", "first"),
        n_periods=("n_periods", "first"),
        test_samples=("test_samples", "first"),
        mean_A=("Config_A", "mean"),
        mean_C=("Config_C", "mean"),
        mean_delta=("delta_C_minus_A", "mean"),
    ).round(4)
    summary_path = "reports/period_experiment_summary.csv"
    summary.to_csv(summary_path)
    print(summary.to_string())
    print(f"\nSaved detailed results to {out_path}")
    print(f"Saved summary results to {summary_path}")


if __name__ == "__main__":
    main()
