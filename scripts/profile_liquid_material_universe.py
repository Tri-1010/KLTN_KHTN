from __future__ import annotations

import pandas as pd

VN30 = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]
MATERIAL_EVENTS = {"earnings", "dividend", "capital", "debt_risk", "legal_risk"}

prices = pd.read_csv("data/prices/all_vn30_prices.csv")
prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
prices["ticker"] = prices["ticker"].astype(str).str.upper()
end = prices["date"].max()
start = end - pd.Timedelta(days=183)
last = prices[(prices["date"] >= start) & (prices["date"] <= end)].copy()
last["value"] = last["close"] * last["volume"] * 1000
liq = last.groupby("ticker").agg(
    avg_value_vnd=("value", "mean"),
    avg_volume=("volume", "mean"),
    trading_days=("date", "nunique"),
).reset_index()

ann = pd.read_csv("data/experiments/llm_semantic/article_semantics_cache.csv")
ann["ticker"] = ann["ticker"].astype(str).str.upper()
ann["event_type"] = ann["event_type"].astype(str).str.lower()
ann["relevance_to_ticker"] = ann["relevance_to_ticker"].astype(str).str.lower()
ok = ann[ann["status"].astype(str).eq("ok")].copy()
mat = ok[ok["event_type"].isin(MATERIAL_EVENTS) & ok["relevance_to_ticker"].isin(["direct", "indirect"])].copy()

meta = liq.merge(ok.groupby("ticker").size().rename("ok_annotations"), on="ticker", how="left")
meta = meta.merge(mat.groupby("ticker").size().rename("material_di"), on="ticker", how="left")
meta = meta.fillna({"ok_annotations": 0, "material_di": 0})
meta["is_vn30"] = meta["ticker"].isin(VN30)
meta["avg_value_bil_vnd"] = meta["avg_value_vnd"] / 1e9
meta = meta.sort_values("avg_value_bil_vnd", ascending=False)
meta.to_csv("reports/liquid_material_universe_profile.csv", index=False, encoding="utf-8")

print(f"date_window={start.date()}->{end.date()}")
print(meta[["ticker", "is_vn30", "avg_value_bil_vnd", "avg_volume", "ok_annotations", "material_di"]].round(2).to_string(index=False))
print("\ncriteria counts")
for min_val in [50, 100, 200, 500]:
    for min_mat in [3, 5, 10]:
        sub = meta[(meta["avg_value_bil_vnd"] >= min_val) & (meta["material_di"] >= min_mat)]
        print(f"value>={min_val} mat>={min_mat} n={len(sub)} vn30={int(sub['is_vn30'].sum())}")
