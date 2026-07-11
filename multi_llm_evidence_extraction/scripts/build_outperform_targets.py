from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, ROOT, ensure_dirs

PRICES = ROOT / "data" / "prices" / "all_vn30_prices.csv"
VNINDEX = ROOT / "data" / "prices_extended" / "VNINDEX.csv"
OUT = OUTPUT_DIR / "outperform_targets.csv"
HORIZON = 20


def main() -> int:
    ensure_dirs()
    prices = pd.read_csv(PRICES, encoding="utf-8")
    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    prices = prices.dropna(subset=["date", "ticker", "close"]).sort_values(["ticker", "date"])
    frames = []
    for ticker, g in prices.groupby("ticker"):
        work = g[["ticker", "date", "close"]].copy().reset_index(drop=True)
        work["stock_return_T20"] = work["close"].shift(-HORIZON) / work["close"] - 1
        frames.append(work.drop(columns=["close"]))
    out = pd.concat(frames, ignore_index=True)
    vnindex = pd.read_csv(VNINDEX, encoding="utf-8")
    vnindex["date"] = pd.to_datetime(vnindex["date"], errors="coerce")
    vnindex = vnindex.dropna(subset=["date", "close"]).sort_values("date").reset_index(drop=True)
    vnindex["VNINDEX_return_T20"] = vnindex["close"].shift(-HORIZON) / vnindex["close"] - 1
    out = out.merge(vnindex[["date", "VNINDEX_return_T20"]], on="date", how="left")
    out["excess_return_T20"] = out["stock_return_T20"] - out["VNINDEX_return_T20"]
    out["label_outperform_T20"] = (out["excess_return_T20"] > 0).astype("Int64")
    out.loc[out["excess_return_T20"].isna(), "label_outperform_T20"] = pd.NA
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"saved {OUT} rows={len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
