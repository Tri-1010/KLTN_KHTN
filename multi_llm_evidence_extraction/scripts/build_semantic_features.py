from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, ROOT, ensure_dirs, parse_string_list

CONSENSUS = OUTPUT_DIR / "pseudo_labels_consensus.csv"
PRICES = ROOT / "data" / "prices" / "all_vn30_prices.csv"
DAILY_OUT = OUTPUT_DIR / "semantic_features_daily.csv"
PERIOD_OUT = OUTPUT_DIR / "semantic_features_period.csv"
ROLLING_WINDOWS = (5, 20, 60)

SEMANTIC_FEATURE_COLUMNS = [
    "semantic_news_count", "direct_news_count", "high_materiality_count",
    "medium_materiality_count", "low_relevance_ratio", "support_count", "risk_count",
    "mixed_direction_count", "avg_materiality_score", "avg_uncertainty_score",
    "avg_novelty_score", "event_earnings_count", "event_debt_legal_count",
    "high_disagreement_ratio",
]
COUNT_COLUMNS = [col for col in SEMANTIC_FEATURE_COLUMNS if col.endswith("_count") or col == "semantic_news_count"]
SCORE_RATIO_COLUMNS = [col for col in SEMANTIC_FEATURE_COLUMNS if col not in COUNT_COLUMNS]


def load_prices() -> pd.DataFrame:
    df = pd.read_csv(PRICES, encoding="utf-8")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df["ticker"] = df["ticker"].astype(str).str.upper()
    return df.dropna(subset=["date", "ticker"]).sort_values(["ticker", "date"])


def next_trading_date(value: Any, trading_dates: Iterable[Any]) -> pd.Timestamp:
    value = pd.to_datetime(value, errors="coerce")
    if pd.isna(value):
        return pd.NaT
    dates = pd.to_datetime(pd.Index(trading_dates), errors="coerce")
    dates = dates[~dates.isna()].normalize().unique().sort_values()
    pos = dates.searchsorted(value.normalize(), side="right")
    return pd.NaT if pos >= len(dates) else pd.Timestamp(dates[pos])


def eligible_labels(labels: pd.DataFrame) -> pd.DataFrame:
    if "analysis_eligible" not in labels:
        return labels.copy()
    mask = labels["analysis_eligible"].astype(str).str.lower().isin(["true", "1"])
    return labels[mask].copy()


def map_to_trading_date(labels: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    labels = eligible_labels(labels)
    if labels.empty or prices.empty:
        return pd.DataFrame(columns=[*labels.columns, "effective_date", "date", "mapping_policy"])
    price_work = prices.copy()
    price_work["ticker"] = price_work["ticker"].astype(str).str.upper()
    price_work["date"] = pd.to_datetime(price_work["date"], errors="coerce").dt.normalize()
    price_dates = {ticker: group["date"].dropna().sort_values().unique() for ticker, group in price_work.groupby("ticker")}
    rows = []
    for _, row in labels.iterrows():
        ticker = str(row.get("ticker", "")).upper()
        mapped = next_trading_date(row.get("article_date"), price_dates.get(ticker, []))
        if pd.isna(mapped):
            continue
        item = dict(row)
        item["ticker"] = ticker
        item["effective_date"] = mapped
        item["date"] = mapped
        item["mapping_policy"] = "next_trading_day_missing_publication_time"
        rows.append(item)
    return pd.DataFrame(rows)


def aggregate_daily(labels: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    grid = prices[["ticker", "date"]].drop_duplicates().copy()
    grid["ticker"] = grid["ticker"].astype(str).str.upper()
    grid["date"] = pd.to_datetime(grid["date"], errors="coerce").dt.normalize()
    grid = grid.dropna(subset=["ticker", "date"])
    mapped = map_to_trading_date(labels, grid) if not labels.empty else pd.DataFrame()
    if mapped.empty:
        out = grid.copy()
        for col in SEMANTIC_FEATURE_COLUMNS:
            out[col] = 0.0
    else:
        defaults = {
            "consensus_ticker_relevance": "", "consensus_materiality": "",
            "consensus_direction": "", "consensus_event_type": "", "high_disagreement_fields": "",
        }
        for col, default in defaults.items():
            if col not in mapped:
                mapped[col] = default
        for col in ["consensus_materiality_score", "consensus_uncertainty_score", "consensus_novelty_score"]:
            mapped[col] = pd.to_numeric(mapped[col] if col in mapped else 0.0, errors="coerce")
        mapped["has_high_disagreement"] = mapped["high_disagreement_fields"].apply(lambda value: bool(parse_string_list(value)))
        grouped = mapped.groupby(["ticker", "date"], sort=True)
        daily = grouped.size().rename("semantic_news_count").reset_index()
        daily["direct_news_count"] = grouped["consensus_ticker_relevance"].apply(lambda s: (s == "direct").sum()).values
        daily["high_materiality_count"] = grouped["consensus_materiality"].apply(lambda s: (s == "high").sum()).values
        daily["medium_materiality_count"] = grouped["consensus_materiality"].apply(lambda s: (s == "medium").sum()).values
        daily["low_relevance_ratio"] = grouped["consensus_ticker_relevance"].apply(lambda s: s.isin(["irrelevant", "unclear", "disagreement"]).mean()).values
        daily["support_count"] = grouped["consensus_direction"].apply(lambda s: (s == "support").sum()).values
        daily["risk_count"] = grouped["consensus_direction"].apply(lambda s: (s == "risk").sum()).values
        daily["mixed_direction_count"] = grouped["consensus_direction"].apply(lambda s: s.isin(["mixed", "unclear", "disagreement"]).sum()).values
        daily["avg_materiality_score"] = grouped["consensus_materiality_score"].mean().values
        daily["avg_uncertainty_score"] = grouped["consensus_uncertainty_score"].mean().values
        daily["avg_novelty_score"] = grouped["consensus_novelty_score"].mean().values
        daily["event_earnings_count"] = grouped["consensus_event_type"].apply(lambda s: (s == "earnings").sum()).values
        daily["event_debt_legal_count"] = grouped["consensus_event_type"].apply(lambda s: s.isin(["debt", "legal", "governance"]).sum()).values
        daily["high_disagreement_ratio"] = grouped["has_high_disagreement"].mean().values
        out = grid.merge(daily, on=["ticker", "date"], how="left")
    for col in COUNT_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    for col in SCORE_RATIO_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    frames = []
    for _, group in out.sort_values(["ticker", "date"]).groupby("ticker", sort=False):
        group = group.copy()
        for window in ROLLING_WINDOWS:
            for col in COUNT_COLUMNS:
                group[f"{col}_roll_{window}d"] = group[col].rolling(window, min_periods=1).sum()
            for col in SCORE_RATIO_COLUMNS:
                group[f"{col}_roll_{window}d"] = group[col].rolling(window, min_periods=1).mean().fillna(0.0)
        last_high = None
        days_since = []
        for _, row in group.iterrows():
            if row["high_materiality_count"] > 0:
                last_high = row["date"]
                days_since.append(0.0)
            elif last_high is None:
                days_since.append(999.0)
            else:
                days_since.append(float((row["date"] - last_high).days))
        group["days_since_high_materiality_news"] = days_since
        for col in SCORE_RATIO_COLUMNS:
            group[col] = group[col].fillna(0.0)
        frames.append(group)
    result = pd.concat(frames, ignore_index=True) if frames else out
    result["artifact_schema_version"] = "semantic_daily_features_v2"
    return result


def aggregate_period(daily: pd.DataFrame) -> pd.DataFrame:
    work = daily.copy()
    work["quarter_id"] = work["date"].dt.to_period("Q").astype(str)
    feature_cols = [col for col in work.columns if col not in {"ticker", "date", "quarter_id", "artifact_schema_version"}]
    aggregation = {col: ("sum" if col.endswith("_count") or col == "semantic_news_count" else "mean") for col in feature_cols}
    result = work.groupby(["ticker", "quarter_id"], as_index=False).agg(aggregation)
    result["period_end"] = pd.PeriodIndex(result["quarter_id"], freq="Q").end_time.normalize()
    result["usage_scope"] = "descriptive_only"
    result["artifact_schema_version"] = "semantic_period_features_v2"
    return result


def main() -> int:
    ensure_dirs()
    prices = load_prices()
    labels = pd.read_csv(CONSENSUS, encoding="utf-8-sig") if CONSENSUS.exists() else pd.DataFrame()
    daily = aggregate_daily(labels, prices)
    period = aggregate_period(daily)
    daily.to_csv(DAILY_OUT, index=False, encoding="utf-8-sig")
    period.to_csv(PERIOD_OUT, index=False, encoding="utf-8-sig")
    print(f"saved {DAILY_OUT} rows={len(daily)}")
    print(f"saved {PERIOD_OUT} rows={len(period)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
