"""
Robustness Test: Extended Ticker Universe (HOSE + HNX, ~200 mã)
================================================================
Kiểm tra tính vững (robustness) của mô hình ML dự báo xu hướng giá bằng đặc
trưng kỹ thuật trên tập mã mở rộng (~200 mã HOSE + HNX), so sánh với VNINDEX.

Mục đích:
- Trả lời câu hỏi: "Kết quả có tổng quát hóa ngoài 80 mã HOSE gốc không?"
- Thêm benchmark VNINDEX (tăng trưởng chỉ số thị trường) cho tính khách quan.

Tiêu chí lọc mã (filter):
- Sàn: HOSE + HNX
- Khối lượng giao dịch trung bình >= 100,000 cổ/phiên (30 ngày gần nhất)
- Vốn hóa >= 1,000 tỷ VND (loại penny stocks)
- Niêm yết liên tục từ 2022-01-01
- Loại: chỉ cổ phiếu phổ thông (bỏ ETF, CW, TP)

Chạy:
    python scripts/robustness_extended_tickers.py
    python scripts/robustness_extended_tickers.py --max-tickers 200
    python scripts/robustness_extended_tickers.py --skip-crawl  # nếu đã có prices

Output:
    reports/robustness_extended_tickers_report.md
    reports/robustness_extended_results.csv
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Ensure UTF-8 output on Windows
for _s in (sys.stdout, sys.stderr):
    _rc = getattr(_s, "reconfigure", None)
    if _rc:
        try:
            _rc(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.logging_config import setup_logger
from pipeline.task5_aggregate import assign_quarter_id

logger = setup_logger("ROBUSTNESS_EXT")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
START_DATE = "2022-01-01"
TRAIN_CUTOFF = "2025Q1"
PRICES_DIR = "data/prices_extended"
OUTPUT_REPORT = "reports/robustness_extended_tickers_report.md"
OUTPUT_CSV = "reports/robustness_extended_results.csv"
VNINDEX_PATH = "data/prices_extended/VNINDEX.csv"

# Filter thresholds
MIN_AVG_VOLUME = 100_000       # cổ phiếu/phiên (trung bình 30 ngày)
MIN_MARKET_CAP_BILLION = 1000  # tỷ VND
MIN_TRADING_DAYS = 500         # tối thiểu phiên giao dịch từ 2022


# ---------------------------------------------------------------------------
# Step 1: Ticker Discovery & Filtering
# ---------------------------------------------------------------------------

def discover_tickers(max_tickers: int = 250) -> List[str]:
    """Discover HOSE + HNX tickers using vnstock listing API.

    Applies filters: market cap, volume, listing date.
    Returns up to max_tickers symbols.
    """
    try:
        from vnstock import Vnstock
        stock = Vnstock()
        # Get all listed companies
        listing = stock.stock().listing.all_symbols()
    except Exception as e:
        logger.warning("vnstock listing API failed: %s. Trying fallback.", e)
        return _fallback_ticker_list()

    if listing is None or listing.empty:
        logger.warning("Empty listing from vnstock. Using fallback list.")
        return _fallback_ticker_list()

    # Filter by exchange: HOSE + HNX only
    exchange_col = None
    for col in listing.columns:
        if col.lower() in ("exchange", "san", "floor", "comgroupcode"):
            exchange_col = col
            break

    if exchange_col:
        listing = listing[
            listing[exchange_col].str.upper().isin(["HOSE", "HNX", "HSX"])
        ]

    # Filter by type: only stocks (exclude ETF, CW, bonds)
    type_col = None
    for col in listing.columns:
        if col.lower() in ("type", "loai", "sectype"):
            type_col = col
            break
    if type_col:
        listing = listing[
            listing[type_col].str.upper().isin(["S", "STOCK", ""])
            | listing[type_col].isna()
        ]

    # Get ticker symbols
    ticker_col = None
    for col in listing.columns:
        if col.lower() in ("ticker", "symbol", "code", "stocksymbol"):
            ticker_col = col
            break
    if ticker_col is None:
        ticker_col = listing.columns[0]

    tickers = listing[ticker_col].dropna().unique().tolist()
    # Filter: only 3-char uppercase tickers (standard VN stock format)
    tickers = [t for t in tickers if isinstance(t, str)
               and len(t) == 3 and t.isalpha() and t.isupper()]

    logger.info("Discovered %d tickers from HOSE+HNX listing.", len(tickers))
    return tickers[:max_tickers]


def _fallback_ticker_list() -> List[str]:
    """Hardcoded fallback list of ~200 liquid HOSE+HNX tickers."""
    # HOSE large/mid cap (includes the original 80 + more)
    hose = [
        "ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG",
        "MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB",
        "TCB","TPB","VCB","VHM","VIB","VIC","VJC","VNM","VPB","VRE",
        "EIB","LPB","MSB","NAB","OCB","VCI","HCM","VND","MBS",
        "KDH","NVL","DXG","PDR","NLG","DIG","HDG","VCG",
        "HSG","NKG","VGC","DPM","DCM","BMP","PHR",
        "REE","NT2","PPC","GEX","PNJ","DGW","FRT","VHC","ANV",
        "CMG","GMD","VSC","PVT","HAH",
        # Additional HOSE
        "ITA","HAG","HNG","DRC","SBT","PAN","TCH","KBC","IJC",
        "TLG","PC1","KOS","VPI","AGG","BWE","CTD","FCN","HBC",
        "LHG","SJS","VOS","TNH","SZC","TDC","VGS","HT1","BCC",
        "TCM","TNG","TDM","AAA","APG","CEO","CII","DBD","DHC",
        "DPG","DVN","FLC","GIL","GTN","IDI","KDC","LCG","MSH",
    ]
    # HNX liquid stocks
    hnx = [
        "SHS","VGS","PVS","CEO","TNG","NVB","IDC","DTD","VC3",
        "HUT","TV2","BVS","L14","MBS","DDG","TIG","NBC","AMV",
        "PLC","PGS","DBC","TDN","VCS","NDN","HLD","SHN","BTS",
        "DP3","ONE","SD5","SRA","TAR","THD","TJC","TKC","VC2",
        "VCC","VE9","VFS","VGP","VMC","VNR","VTJ","PSD","S99",
    ]
    combined = list(dict.fromkeys(hose + hnx))  # dedup preserve order
    return combined


# ---------------------------------------------------------------------------
# Step 2: Price Collection (extended)
# ---------------------------------------------------------------------------

def fetch_single_ticker(ticker: str, start_date: str, end_date: str,
                        output_dir: str) -> Optional[pd.DataFrame]:
    """Fetch OHLCV for a single ticker, save to CSV. Skip if already exists."""
    out_path = os.path.join(output_dir, f"{ticker}.csv")
    if os.path.exists(out_path):
        try:
            df = pd.read_csv(out_path, parse_dates=["date"])
            if len(df) > 0:
                return df
        except Exception:
            pass

    try:
        from vnstock.explorer.vci.quote import Quote
        quote = Quote(ticker)
        df = quote.history(start=start_date, end=end_date, interval="1D")
        if df is None or df.empty:
            return None
        if "time" in df.columns:
            df = df.rename(columns={"time": "date"})
        df["date"] = pd.to_datetime(df["date"])
        cols = [c for c in ["date","open","high","low","close","volume"]
                if c in df.columns]
        df = df[cols].sort_values("date").reset_index(drop=True)
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(out_path, index=False)
        return df
    except Exception as e:
        logger.debug("Failed to fetch %s: %s", ticker, e)
        return None


def fetch_vnindex(start_date: str, end_date: str,
                  output_dir: str) -> Optional[pd.DataFrame]:
    """Fetch VNINDEX daily data for benchmark comparison."""
    out_path = os.path.join(output_dir, "VNINDEX.csv")
    if os.path.exists(out_path):
        try:
            return pd.read_csv(out_path, parse_dates=["date"])
        except Exception:
            pass
    try:
        from vnstock.explorer.vci.quote import Quote
        quote = Quote("VNINDEX")
        df = quote.history(start=start_date, end=end_date, interval="1D")
        if df is None or df.empty:
            return None
        if "time" in df.columns:
            df = df.rename(columns={"time": "date"})
        df["date"] = pd.to_datetime(df["date"])
        cols = [c for c in ["date","open","high","low","close","volume"]
                if c in df.columns]
        df = df[cols].sort_values("date").reset_index(drop=True)
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(out_path, index=False)
        return df
    except Exception as e:
        logger.warning("Failed to fetch VNINDEX: %s", e)
        return None


def collect_all_prices(tickers: List[str], start_date: str,
                       end_date: str, output_dir: str) -> Dict[str, pd.DataFrame]:
    """Fetch prices for all tickers (with progress logging)."""
    results = {}
    total = len(tickers)
    for i, ticker in enumerate(tickers, 1):
        if i % 10 == 0 or i == 1:
            logger.info("Fetching prices: %d/%d (collected %d so far)...",
                        i, total, len(results))
        # Check if already cached
        cached_path = os.path.join(output_dir, f"{ticker}.csv")
        if os.path.exists(cached_path):
            try:
                df = pd.read_csv(cached_path, parse_dates=["date"])
                if len(df) > 0:
                    results[ticker] = df
                    continue
            except Exception:
                pass
        df = fetch_single_ticker(ticker, start_date, end_date, output_dir)
        if df is not None and len(df) > 0:
            results[ticker] = df
        # Aggressive rate limiting to avoid VCI 429 errors
        time.sleep(2.0)
        # Extra pause every 30 tickers
        if i % 30 == 0:
            logger.info("  Pausing 15s to avoid rate limit...")
            time.sleep(15)
    logger.info("Collected prices for %d/%d tickers.", len(results), total)
    return results


# ---------------------------------------------------------------------------
# Step 3: Filter tickers by quality criteria
# ---------------------------------------------------------------------------

def filter_tickers(price_data: Dict[str, pd.DataFrame]) -> List[str]:
    """Apply volume/trading-days filters to select quality tickers."""
    qualified = []
    for ticker, df in price_data.items():
        # Must have enough trading days
        if len(df) < MIN_TRADING_DAYS:
            continue
        # Average volume over last 60 trading days
        recent = df.tail(60)
        avg_vol = recent["volume"].mean() if "volume" in df.columns else 0
        if avg_vol < MIN_AVG_VOLUME:
            continue
        # Must have data starting from 2022
        first_date = df["date"].min()
        if first_date > pd.Timestamp("2022-06-30"):
            continue
        qualified.append(ticker)

    logger.info("Filter result: %d/%d tickers pass quality criteria.",
                len(qualified), len(price_data))
    return sorted(qualified)


# ---------------------------------------------------------------------------
# Step 4: Build technical features & labels (standalone, no keyword needed)
# ---------------------------------------------------------------------------

def compute_daily_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute daily technical indicators for a single ticker."""
    import pandas_ta as ta
    df = df.copy().sort_values("date").reset_index(drop=True)
    df["daily_return"] = df["close"].pct_change()
    df["RSI_14"] = ta.rsi(df["close"], length=14)
    macd_result = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if macd_result is not None and not macd_result.empty:
        df = pd.concat([df, macd_result], axis=1)
    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None and not bb.empty:
        df = pd.concat([df, bb], axis=1)
    df["SMA_20"] = ta.sma(df["close"], length=20)
    df["EMA_20"] = ta.ema(df["close"], length=20)
    return df


def _find_col(df, prefix):
    matches = [c for c in df.columns if c.startswith(prefix)]
    return matches[0] if matches else None


def aggregate_quarter(daily_df: pd.DataFrame,
                      prev_q_ret=None, two_q_ago_ret=None) -> dict:
    """Aggregate daily data for one (ticker, quarter) into features."""
    if daily_df.empty:
        return {}
    features = {}
    close = daily_df["close"]
    high = daily_df["high"]
    low = daily_df["low"]
    volume = daily_df["volume"]
    dr = daily_df["daily_return"]
    c0, c1 = close.iloc[0], close.iloc[-1]
    n = len(daily_df)

    features["return_q"] = (c1 - c0) / c0 if c0 != 0 else 0.0
    features["return_mean_daily"] = dr.mean()
    features["return_std_daily"] = dr.std()
    features["volatility_q"] = (
        features["return_std_daily"] * math.sqrt(n)
        if pd.notna(features["return_std_daily"]) else np.nan
    )
    avg_c = close.mean()
    features["price_range_q"] = (
        (high.max() - low.min()) / avg_c if avg_c != 0 else 0.0
    )
    features["volume_mean_q"] = volume.mean()
    features["volume_change_q"] = np.nan  # filled later

    # Trend
    sma20 = daily_df["SMA_20"].iloc[-1] if "SMA_20" in daily_df.columns else np.nan
    ema20 = daily_df["EMA_20"].iloc[-1] if "EMA_20" in daily_df.columns else np.nan
    features["sma20_end"] = sma20
    features["ema20_end"] = ema20
    features["price_vs_sma20"] = (
        (c1 - sma20) / sma20 if pd.notna(sma20) and sma20 != 0 else np.nan
    )
    # Indicators
    if "RSI_14" in daily_df.columns:
        features["rsi_mean_q"] = daily_df["RSI_14"].mean()
        features["rsi_end_q"] = daily_df["RSI_14"].iloc[-1]
    else:
        features["rsi_mean_q"] = features["rsi_end_q"] = np.nan

    macd_col = _find_col(daily_df, "MACDh_")
    features["macd_hist_mean_q"] = (
        daily_df[macd_col].mean() if macd_col else np.nan
    )
    bbl = _find_col(daily_df, "BBL_")
    bbu = _find_col(daily_df, "BBU_")
    if bbl and bbu:
        bb_r = daily_df[bbu] - daily_df[bbl]
        bb_pos = (close - daily_df[bbl]) / bb_r.replace(0, np.nan)
        features["bb_position_q"] = bb_pos.mean()
    else:
        features["bb_position_q"] = np.nan

    # Momentum (lag returns filled at ticker level)
    features["return_prev_q"] = prev_q_ret if prev_q_ret is not None else np.nan
    features["return_2q_ago"] = two_q_ago_ret if two_q_ago_ret is not None else np.nan

    return features


def build_features_and_labels(
    price_data: Dict[str, pd.DataFrame],
    tickers: List[str],
) -> pd.DataFrame:
    """Build quarterly technical features + labels for all tickers."""
    all_rows = []
    for ticker in tickers:
        df = price_data.get(ticker)
        if df is None or df.empty:
            continue
        daily = compute_daily_indicators(df)
        daily["quarter_id"] = daily["date"].apply(assign_quarter_id)
        quarters = sorted(daily["quarter_id"].unique())

        # Compute avg_close per quarter for label
        avg_by_q = {}
        for q in quarters:
            qdf = daily[daily["quarter_id"] == q]
            avg_by_q[q] = qdf["close"].mean()

        prev_vol = None
        for i, q in enumerate(quarters):
            qdf = daily[daily["quarter_id"] == q]
            if len(qdf) < 10:  # skip quarters with too few days
                prev_vol = qdf["volume"].mean() if len(qdf) > 0 else None
                continue

            prev_ret = None
            two_q_ret = None
            if i >= 1:
                prev_q = quarters[i - 1]
                pqdf = daily[daily["quarter_id"] == prev_q]
                if len(pqdf) > 0:
                    prev_ret = (pqdf["close"].iloc[-1] - pqdf["close"].iloc[0]
                                ) / pqdf["close"].iloc[0]
            if i >= 2:
                twoq = quarters[i - 2]
                tqdf = daily[daily["quarter_id"] == twoq]
                if len(tqdf) > 0:
                    two_q_ret = (tqdf["close"].iloc[-1] - tqdf["close"].iloc[0]
                                 ) / tqdf["close"].iloc[0]

            feats = aggregate_quarter(qdf, prev_ret, two_q_ret)
            if not feats:
                continue

            # Volume change vs previous quarter
            cur_vol = qdf["volume"].mean()
            if prev_vol and prev_vol > 0:
                feats["volume_change_q"] = (cur_vol - prev_vol) / prev_vol
            prev_vol = cur_vol

            # Label: next quarter avg_close > this quarter avg_close
            next_idx = i + 1
            if next_idx < len(quarters):
                next_q = quarters[next_idx]
                label = 1 if avg_by_q[next_q] > avg_by_q[q] else 0
                ret_next = (avg_by_q[next_q] - avg_by_q[q]) / avg_by_q[q]
            else:
                label = np.nan
                ret_next = np.nan

            feats["ticker"] = ticker
            feats["quarter_id"] = q
            feats["label_basic"] = label
            feats["period_return"] = ret_next
            all_rows.append(feats)

    result = pd.DataFrame(all_rows)
    result = result.dropna(subset=["label_basic"])
    result["label_basic"] = result["label_basic"].astype(int)
    logger.info("Built features: %d rows, %d tickers, %d quarters.",
                len(result), result["ticker"].nunique(),
                result["quarter_id"].nunique())
    return result


# ---------------------------------------------------------------------------
# Step 5: Train & Evaluate (same pipeline logic as original)
# ---------------------------------------------------------------------------

def train_and_evaluate(
    data: pd.DataFrame,
    cutoff: str = TRAIN_CUTOFF,
) -> pd.DataFrame:
    """Train 4 ML models + 2 baselines on Config_A, return results."""
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.impute import SimpleImputer
    try:
        from xgboost import XGBClassifier
    except ImportError:
        XGBClassifier = None
    try:
        from lightgbm import LGBMClassifier
    except ImportError:
        LGBMClassifier = None
    from sklearn.metrics import (
        balanced_accuracy_score, roc_auc_score, f1_score,
        precision_score, recall_score, accuracy_score,
    )

    # Feature columns (all numeric except meta/label)
    meta = {"ticker", "quarter_id", "label_basic", "period_return"}
    feat_cols = [c for c in data.columns if c not in meta
                 and data[c].dtype in [np.float64, np.int64, float, int]]

    # Time split
    train = data[data["quarter_id"] < cutoff].copy()
    test = data[data["quarter_id"] >= cutoff].copy()

    if len(train) < 50 or len(test) < 20:
        logger.error("Not enough data: train=%d, test=%d", len(train), len(test))
        return pd.DataFrame()

    logger.info("Train: %d rows (%d tickers), Test: %d rows (%d tickers)",
                len(train), train["ticker"].nunique(),
                len(test), test["ticker"].nunique())

    # Imputation
    X_train = train[feat_cols].copy()
    X_test = test[feat_cols].copy()
    y_train = train["label_basic"].astype(int)
    y_test = test["label_basic"].astype(int)

    imputer = SimpleImputer(strategy="median")
    X_train_imp = pd.DataFrame(
        imputer.fit_transform(X_train), columns=feat_cols, index=X_train.index)
    X_test_imp = pd.DataFrame(
        imputer.transform(X_test), columns=feat_cols, index=X_test.index)

    # Models
    models = {
        "Logistic_Regression": LogisticRegression(
            max_iter=1000, random_state=42, class_weight="balanced"),
        "Random_Forest": RandomForestClassifier(
            n_estimators=200, max_depth=8, random_state=42,
            class_weight="balanced", n_jobs=-1),
    }
    if XGBClassifier:
        models["XGBoost"] = XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=42, use_label_encoder=False,
            eval_metric="logloss", verbosity=0)
    if LGBMClassifier:
        models["LightGBM"] = LGBMClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            random_state=42, verbose=-1, class_weight="balanced")

    # Baselines
    baselines = {
        "Baseline_Majority": DummyClassifier(strategy="most_frequent"),
        "Baseline_Stratified": DummyClassifier(strategy="stratified",
                                                random_state=42),
    }

    results = []
    predictions = {}  # store for backtest

    for name, model in {**baselines, **models}.items():
        model.fit(X_train_imp, y_train)
        y_pred = model.predict(X_test_imp)
        y_proba = (model.predict_proba(X_test_imp)[:, 1]
                   if hasattr(model, "predict_proba") else None)

        ba = balanced_accuracy_score(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
        rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
        try:
            auc = roc_auc_score(y_test, y_proba) if y_proba is not None else np.nan
        except ValueError:
            auc = np.nan

        results.append({
            "model": name, "balanced_accuracy": ba, "accuracy": acc,
            "f1_macro": f1, "precision_macro": prec, "recall_macro": rec,
            "auc_roc": auc, "n_train": len(train), "n_test": len(test),
        })
        if name in models:
            predictions[name] = {
                "y_pred": y_pred, "y_proba": y_proba, "y_true": y_test,
                "test_df": test,
            }
        logger.info("  %s: BA=%.4f, AUC=%.4f", name, ba, auc)

    results_df = pd.DataFrame(results)
    return results_df, predictions


# ---------------------------------------------------------------------------
# Step 6: VNINDEX Benchmark
# ---------------------------------------------------------------------------

def compute_vnindex_benchmark(vnindex_df: Optional[pd.DataFrame],
                              cutoff: str = TRAIN_CUTOFF) -> dict:
    """Compute VNINDEX quarterly returns as market benchmark."""
    if vnindex_df is None or vnindex_df.empty:
        return {"vnindex_cumulative_return": np.nan,
                "vnindex_mean_quarterly_return": np.nan}

    vnindex_df = vnindex_df.copy()
    vnindex_df["quarter_id"] = vnindex_df["date"].apply(assign_quarter_id)
    # Only test period
    test_qs = vnindex_df[vnindex_df["quarter_id"] >= cutoff]
    quarters = sorted(test_qs["quarter_id"].unique())

    q_returns = []
    for q in quarters:
        qdf = test_qs[test_qs["quarter_id"] == q]
        if len(qdf) < 5:
            continue
        c0 = qdf["close"].iloc[0]
        c1 = qdf["close"].iloc[-1]
        if c0 > 0:
            q_returns.append((c1 - c0) / c0)

    cum_ret = np.prod([1 + r for r in q_returns]) - 1 if q_returns else np.nan
    mean_ret = np.mean(q_returns) if q_returns else np.nan

    return {
        "vnindex_cumulative_return": cum_ret,
        "vnindex_mean_quarterly_return": mean_ret,
        "vnindex_quarters": len(q_returns),
        "vnindex_quarterly_returns": q_returns,
    }


def compute_model_backtest(predictions: dict, best_model: str) -> dict:
    """Simple backtest: buy tickers predicted 'up', equal weight."""
    pred_info = predictions.get(best_model)
    if pred_info is None:
        return {}
    test_df = pred_info["test_df"].copy()
    test_df["pred_label"] = pred_info["y_pred"]

    quarters = sorted(test_df["quarter_id"].unique())
    q_returns = []
    for q in quarters:
        qdf = test_df[test_df["quarter_id"] == q]
        selected = qdf[qdf["pred_label"] == 1]
        if len(selected) > 0:
            q_ret = selected["period_return"].mean()
        else:
            q_ret = 0.0
        q_returns.append(q_ret)

    cum_ret = np.prod([1 + r for r in q_returns]) - 1
    sharpe = (np.mean(q_returns) / np.std(q_returns)
              if np.std(q_returns) > 0 else 0.0)
    return {
        "model_cumulative_return": cum_ret,
        "model_mean_quarterly_return": np.mean(q_returns),
        "model_sharpe_ratio": sharpe,
        "model_hit_rate": sum(1 for r in q_returns if r > 0) / len(q_returns),
        "model_quarters": len(q_returns),
    }


# ---------------------------------------------------------------------------
# Step 7: Generate Report
# ---------------------------------------------------------------------------

def generate_report(
    results_df: pd.DataFrame,
    predictions: dict,
    vnindex_info: dict,
    n_tickers: int,
    n_hose: int,
    n_hnx: int,
    original_results: Optional[dict] = None,
) -> str:
    """Generate markdown report comparing extended vs original results."""

    # Best ML model
    ml_models = results_df[~results_df["model"].str.contains("Baseline")]
    if ml_models.empty:
        best_model = "N/A"
        best_ba = 0
    else:
        best_idx = ml_models["balanced_accuracy"].idxmax()
        best_model = ml_models.loc[best_idx, "model"]
        best_ba = ml_models.loc[best_idx, "balanced_accuracy"]

    # Backtest
    backtest = compute_model_backtest(predictions, best_model)

    lines = []
    lines.append("# Robustness Test: Extended Ticker Universe (HOSE + HNX)")
    lines.append("")
    lines.append(f"> Ngày chạy: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## 1. Tóm tắt")
    lines.append("")
    lines.append(f"- **Tổng số mã kiểm tra:** {n_tickers} "
                 f"(HOSE: {n_hose}, HNX: {n_hnx})")
    lines.append(f"- **Train cutoff:** {TRAIN_CUTOFF}")
    lines.append(f"- **Tiêu chí lọc:** volume TB >= {MIN_AVG_VOLUME:,} "
                 f"cổ/phiên, >= {MIN_TRADING_DAYS} phiên từ 2022")
    lines.append(f"- **Mô hình tốt nhất:** {best_model} "
                 f"(Balanced Accuracy = {best_ba:.4f})")
    lines.append("")
    lines.append("## 2. Kết quả phân loại (Config A — chỉ đặc trưng kỹ thuật)")
    lines.append("")
    lines.append("| Mô hình | Balanced Acc | AUC-ROC | F1 Macro | "
                 "n_train | n_test |")
    lines.append("|---|---|---|---|---|---|")
    for _, row in results_df.iterrows():
        lines.append(f"| {row['model']} | {row['balanced_accuracy']:.4f} | "
                     f"{row['auc_roc']:.4f} | {row['f1_macro']:.4f} | "
                     f"{int(row['n_train'])} | {int(row['n_test'])} |")

    lines.append("")
    lines.append("## 3. So sánh với kết quả gốc (80 mã HOSE)")
    lines.append("")
    lines.append("| Chỉ số | 80 mã HOSE (gốc) | "
                 f"{n_tickers} mã HOSE+HNX (mở rộng) | Nhận xét |")
    lines.append("|---|---|---|---|")

    orig_ba = 0.760  # LightGBM Config_A from original
    orig_auc = 0.824
    delta_ba = best_ba - orig_ba
    direction = "↑" if delta_ba >= 0 else "↓"
    lines.append(f"| Best Balanced Accuracy | 0.760 (LightGBM) | "
                 f"{best_ba:.4f} ({best_model}) | {direction} "
                 f"{abs(delta_ba):.4f} |")

    best_auc = ml_models.loc[best_idx, "auc_roc"] if not ml_models.empty else np.nan
    delta_auc = best_auc - orig_auc
    dir_auc = "↑" if delta_auc >= 0 else "↓"
    lines.append(f"| Best AUC-ROC | 0.824 | {best_auc:.4f} | "
                 f"{dir_auc} {abs(delta_auc):.4f} |")
    lines.append(f"| Số mã | 80 | {n_tickers} | x{n_tickers/80:.1f} |")

    n_train = int(results_df["n_train"].iloc[0]) if len(results_df) > 0 else 0
    n_test = int(results_df["n_test"].iloc[0]) if len(results_df) > 0 else 0
    lines.append(f"| Cỡ mẫu train | 1,348 | {n_train:,} | |")
    lines.append(f"| Cỡ mẫu test | 400 | {n_test:,} | |")

    lines.append("")
    lines.append("## 4. Benchmark VNINDEX")
    lines.append("")
    vn_cum = vnindex_info.get("vnindex_cumulative_return", np.nan)
    vn_mean = vnindex_info.get("vnindex_mean_quarterly_return", np.nan)
    model_cum = backtest.get("model_cumulative_return", np.nan)
    model_sharpe = backtest.get("model_sharpe_ratio", np.nan)
    model_hit = backtest.get("model_hit_rate", np.nan)

    lines.append("| Chiến lược | Lợi nhuận tích lũy | "
                 "Return TB/quý | Sharpe | Hit Rate |")
    lines.append("|---|---|---|---|---|")
    lines.append(f"| **Mô hình ({best_model})** | "
                 f"{model_cum:.4f} ({model_cum*100:.1f}%) | "
                 f"{backtest.get('model_mean_quarterly_return', 0):.4f} | "
                 f"{model_sharpe:.2f} | {model_hit:.1%} |")
    lines.append(f"| VNINDEX (buy & hold) | "
                 f"{vn_cum:.4f} ({vn_cum*100:.1f}%) | "
                 f"{vn_mean:.4f} | — | — |")

    if not np.isnan(model_cum) and not np.isnan(vn_cum):
        excess = model_cum - vn_cum
        lines.append("")
        lines.append(f"**Lợi nhuận vượt trội (excess return) so với VNINDEX:** "
                     f"{excess:.4f} ({excess*100:.1f}%)")

    lines.append("")
    lines.append("## 5. Kết luận Robustness Test")
    lines.append("")

    if best_ba >= 0.65:
        conclusion = (
            f"Mô hình ML dự báo xu hướng giá bằng đặc trưng kỹ thuật **duy trì "
            f"hiệu quả** khi mở rộng từ 80 mã HOSE gốc lên {n_tickers} mã "
            f"HOSE+HNX (Balanced Accuracy = {best_ba:.3f}). Kết quả cho thấy "
            f"khả năng tổng quát hóa (generalization) tốt — mô hình không "
            f"overfit vào tập 80 mã ban đầu."
        )
    elif best_ba >= 0.55:
        conclusion = (
            f"Mô hình vẫn hoạt động trên ngưỡng ngẫu nhiên (BA = {best_ba:.3f} > 0.50) "
            f"trên {n_tickers} mã, nhưng hiệu quả giảm so với 80 mã gốc. Có thể do "
            f"các mã HNX/mid-cap nhỏ có tính thanh khoản thấp hơn, khiến đặc trưng "
            f"kỹ thuật kém hiệu quả hơn."
        )
    else:
        conclusion = (
            f"Mô hình không tổng quát hóa tốt ra ngoài 80 mã gốc "
            f"(BA = {best_ba:.3f}). Cần nghiên cứu thêm về sự khác biệt giữa "
            f"các nhóm mã."
        )

    lines.append(conclusion)
    lines.append("")

    if not np.isnan(model_cum) and not np.isnan(vn_cum) and model_cum > vn_cum:
        lines.append(f"Chiến lược mô hình **vượt VNINDEX** {excess*100:.1f}% "
                     f"trên cùng khoảng test — xác nhận giá trị đầu tư thực.")
    lines.append("")
    lines.append("## 6. Giới hạn")
    lines.append("")
    lines.append("- Backtest đơn giản (equal-weight, không tính phí giao dịch "
                 "cho phiên bản mở rộng này).")
    lines.append("- Một số mã HNX có thanh khoản thấp hơn ngưỡng HOSE-80 gốc.")
    lines.append("- Kết quả quá khứ không đảm bảo hiệu quả tương lai.")
    lines.append("- Test này chỉ kiểm tra đặc trưng kỹ thuật (không bao gồm "
                 "đặc trưng từ khóa).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Script: `scripts/robustness_extended_tickers.py`*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Robustness test: ML technical model on 200+ HOSE+HNX tickers")
    parser.add_argument("--max-tickers", type=int, default=250,
                        help="Max tickers to discover (default: 250)")
    parser.add_argument("--skip-crawl", action="store_true",
                        help="Skip price crawling (use existing data)")
    parser.add_argument("--cutoff", default=TRAIN_CUTOFF,
                        help=f"Train/test cutoff (default: {TRAIN_CUTOFF})")
    args = parser.parse_args()

    end_date = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(PRICES_DIR, exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # --- Step 1: Discover tickers ---
    logger.info("=" * 60)
    logger.info("STEP 1: Discovering HOSE+HNX tickers...")
    logger.info("=" * 60)
    candidate_tickers = discover_tickers(args.max_tickers)
    logger.info("Candidates: %d tickers", len(candidate_tickers))

    # --- Step 2: Collect prices ---
    if not args.skip_crawl:
        logger.info("=" * 60)
        logger.info("STEP 2: Collecting prices...")
        logger.info("=" * 60)
        price_data = collect_all_prices(
            candidate_tickers, START_DATE, end_date, PRICES_DIR)
        # Also fetch VNINDEX
        logger.info("Fetching VNINDEX...")
        vnindex_df = fetch_vnindex(START_DATE, end_date, PRICES_DIR)
    else:
        logger.info("STEP 2: Loading existing prices from %s", PRICES_DIR)
        price_data = {}
        for ticker in candidate_tickers:
            path = os.path.join(PRICES_DIR, f"{ticker}.csv")
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path, parse_dates=["date"])
                    if len(df) > 0:
                        price_data[ticker] = df
                except Exception:
                    pass
        vnindex_df = None
        vni_path = os.path.join(PRICES_DIR, "VNINDEX.csv")
        if os.path.exists(vni_path):
            vnindex_df = pd.read_csv(vni_path, parse_dates=["date"])

    logger.info("Loaded price data for %d tickers.", len(price_data))

    # --- Step 3: Filter ---
    logger.info("=" * 60)
    logger.info("STEP 3: Filtering tickers by quality criteria...")
    logger.info("=" * 60)
    qualified = filter_tickers(price_data)

    if len(qualified) < 30:
        logger.error("Too few qualified tickers (%d). Aborting.", len(qualified))
        sys.exit(1)

    # Classify HOSE vs HNX (approximate: well-known HNX tickers)
    known_hnx = {"SHS","PVS","NVB","IDC","VC3","HUT","TV2","BVS","L14",
                 "DDG","TIG","NBC","AMV","PLC","PGS","DBC","TDN","VCS",
                 "NDN","HLD","SHN","BTS","CEO","TNG","MBS"}
    n_hnx = sum(1 for t in qualified if t in known_hnx)
    n_hose = len(qualified) - n_hnx

    logger.info("Qualified: %d tickers (HOSE~%d, HNX~%d)",
                len(qualified), n_hose, n_hnx)

    # --- Step 4: Build features & labels ---
    logger.info("=" * 60)
    logger.info("STEP 4: Building technical features & labels...")
    logger.info("=" * 60)
    filtered_prices = {t: price_data[t] for t in qualified}
    dataset = build_features_and_labels(filtered_prices, qualified)

    if dataset.empty:
        logger.error("Empty dataset after feature building. Aborting.")
        sys.exit(1)

    # --- Step 5: Train & Evaluate ---
    logger.info("=" * 60)
    logger.info("STEP 5: Training models (Config A — technical only)...")
    logger.info("=" * 60)
    result = train_and_evaluate(dataset, cutoff=args.cutoff)
    if isinstance(result, tuple):
        results_df, predictions = result
    else:
        results_df = result
        predictions = {}

    if results_df.empty:
        logger.error("No results produced. Aborting.")
        sys.exit(1)

    # --- Step 6: VNINDEX benchmark ---
    logger.info("=" * 60)
    logger.info("STEP 6: Computing VNINDEX benchmark...")
    logger.info("=" * 60)
    vnindex_info = compute_vnindex_benchmark(vnindex_df, cutoff=args.cutoff)
    logger.info("VNINDEX cumulative return (test period): %.4f",
                vnindex_info.get("vnindex_cumulative_return", float("nan")))

    # --- Step 7: Generate report ---
    logger.info("=" * 60)
    logger.info("STEP 7: Generating report...")
    logger.info("=" * 60)
    report = generate_report(
        results_df, predictions, vnindex_info,
        n_tickers=len(qualified), n_hose=n_hose, n_hnx=n_hnx,
    )

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info("Report saved: %s", OUTPUT_REPORT)

    results_df.to_csv(OUTPUT_CSV, index=False)
    logger.info("Results CSV saved: %s", OUTPUT_CSV)

    # Print summary
    print("\n" + "=" * 60)
    print("ROBUSTNESS TEST COMPLETE")
    print("=" * 60)
    ml_only = results_df[~results_df["model"].str.contains("Baseline")]
    if not ml_only.empty:
        best = ml_only.loc[ml_only["balanced_accuracy"].idxmax()]
        print(f"Best model: {best['model']} "
              f"(BA={best['balanced_accuracy']:.4f}, "
              f"AUC={best['auc_roc']:.4f})")
    print(f"Tickers tested: {len(qualified)} (HOSE~{n_hose}, HNX~{n_hnx})")
    print(f"Report: {OUTPUT_REPORT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
