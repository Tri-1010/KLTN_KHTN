"""
HOSE-80 Expansion Crawl Script
================================
Crawl prices and news for the 50 new tickers added in the HOSE-80 expansion.
VN30 tickers already have data and are skipped.

Steps:
  1. Collect prices for 50 new tickers (task1)
  2. Scrape CafeF news for each new ticker (task2)
  3. Scrape Vietstock news for each new ticker (task2)

Run from workspace root:
    python crawl_expansion.py
"""
from __future__ import annotations
import sys, os

for _s in (sys.stdout, sys.stderr):
    _rc = getattr(_s, "reconfigure", None)
    if _rc:
        try: _rc(encoding="utf-8", errors="replace")
        except: pass

import time
import yaml
import pandas as pd
from pipeline.logging_config import setup_logger

logger = setup_logger("EXPANSION")

# ------------------------------------------------------------------
# Tickers
# ------------------------------------------------------------------
VN30 = {
    'ACB','BCM','BID','BVH','CTG','FPT','GAS','GVR','HDB','HPG',
    'MBB','MSN','MWG','PLX','POW','SAB','SHB','SSB','SSI','STB',
    'TCB','TPB','VCB','VHM','VIB','VIC','VJC','VNM','VPB','VRE',
}

cfg = yaml.safe_load(open("config/pipeline_config.yaml", encoding="utf-8"))
ALL_TICKERS = cfg["tickers"]
NEW_TICKERS = [t for t in ALL_TICKERS if t not in VN30]
START_DATE  = cfg.get("start_date", "2022-01-01")

logger.info("HOSE-80 Expansion: %d new tickers to crawl", len(NEW_TICKERS))
logger.info("New tickers: %s", ", ".join(NEW_TICKERS))
logger.info("Start date: %s", START_DATE)

# ------------------------------------------------------------------
# Step 1 — Prices
# ------------------------------------------------------------------
def run_prices():
    logger.info("=" * 60)
    logger.info("STEP 1: Collecting prices for %d new tickers", len(NEW_TICKERS))
    logger.info("=" * 60)

    from pipeline.task1_prices import collect_prices

    # Only crawl tickers that don't already have a price file
    missing = [t for t in NEW_TICKERS
               if not os.path.exists(f"data/prices/{t}.csv")]
    existing = [t for t in NEW_TICKERS if t not in missing]

    if existing:
        logger.info("Already have prices for: %s — skipping", ", ".join(existing))
    if not missing:
        logger.info("All new tickers already have price files — skipping step 1")
        return

    logger.info("Collecting prices for: %s", ", ".join(missing))
    try:
        collect_prices(
            tickers=missing,
            start_date=START_DATE,
            end_date="auto",
        )
        logger.info("Step 1 complete")
    except Exception as e:
        logger.error("Step 1 failed: %s", e)
        raise

# ------------------------------------------------------------------
# Step 2 — CafeF news
# ------------------------------------------------------------------
def run_cafef():
    logger.info("=" * 60)
    logger.info("STEP 2: Scraping CafeF for %d new tickers", len(NEW_TICKERS))
    logger.info("=" * 60)

    from pipeline.task2_scrape import scrape_source

    failed = []
    for i, ticker in enumerate(NEW_TICKERS, 1):
        out_path = f"data/news/cafef/{ticker}_cafef.csv"
        if os.path.exists(out_path):
            existing = pd.read_csv(out_path, encoding="utf-8")
            logger.info("[%d/%d] %s — CafeF already has %d articles, extending",
                        i, len(NEW_TICKERS), ticker, len(existing))
        else:
            logger.info("[%d/%d] %s — CafeF new crawl", i, len(NEW_TICKERS), ticker)

        try:
            df = scrape_source("cafef", ticker=ticker, start_date=START_DATE)
            n = len(df) if df is not None else 0
            logger.info("  CafeF %s: %d articles collected", ticker, n)
        except Exception as e:
            logger.error("  CafeF %s FAILED: %s", ticker, e)
            failed.append(ticker)

        time.sleep(1.0)  # Rate limiting

    if failed:
        logger.warning("CafeF failed for: %s", ", ".join(failed))
    logger.info("Step 2 complete")
    return failed

# ------------------------------------------------------------------
# Step 3 — Vietstock news
# ------------------------------------------------------------------
def run_vietstock():
    logger.info("=" * 60)
    logger.info("STEP 3: Scraping Vietstock for %d new tickers", len(NEW_TICKERS))
    logger.info("=" * 60)

    from pipeline.task2_scrape import scrape_source

    failed = []
    for i, ticker in enumerate(NEW_TICKERS, 1):
        out_path = f"data/news/vietstock/{ticker}_vietstock.csv"
        if os.path.exists(out_path):
            existing = pd.read_csv(out_path, encoding="utf-8")
            logger.info("[%d/%d] %s — Vietstock already has %d articles, extending",
                        i, len(NEW_TICKERS), ticker, len(existing))
        else:
            logger.info("[%d/%d] %s — Vietstock new crawl", i, len(NEW_TICKERS), ticker)

        try:
            df = scrape_source("vietstock", ticker=ticker, start_date=START_DATE)
            n = len(df) if df is not None else 0
            logger.info("  Vietstock %s: %d articles collected", ticker, n)
        except Exception as e:
            logger.error("  Vietstock %s FAILED: %s", ticker, e)
            failed.append(ticker)

        time.sleep(1.5)  # Vietstock needs more delay

    if failed:
        logger.warning("Vietstock failed for: %s", ", ".join(failed))
    logger.info("Step 3 complete")
    return failed

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HOSE-80 expansion crawl")
    parser.add_argument("--step", choices=["prices","cafef","vietstock","all"],
                        default="all", help="Which step to run (default: all)")
    args = parser.parse_args()

    if args.step in ("prices", "all"):
        run_prices()

    if args.step in ("cafef", "all"):
        run_cafef()

    if args.step in ("vietstock", "all"):
        run_vietstock()

    logger.info("=" * 60)
    logger.info("EXPANSION CRAWL COMPLETE")
    logger.info("Next steps:")
    logger.info("  1. python -m pipeline.run_pipeline --step preprocess --force")
    logger.info("  2. python -m pipeline.run_pipeline --step features --force")
    logger.info("  3. python -m pipeline.run_pipeline --step train --force")
    logger.info("  4. python -m pipeline.experiment_keyword_significance")
    logger.info("=" * 60)
