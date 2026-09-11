"""
TASK 12: Pipeline_Runner
Semi-automated pipeline orchestrator with argparse CLI, YAML configuration,
checkpointing, and structured logging.

Usage:
    python pipeline/run_pipeline.py --step all
    python pipeline/run_pipeline.py --step data
    python pipeline/run_pipeline.py --step preprocess
    python pipeline/run_pipeline.py --step features
    python pipeline/run_pipeline.py --step train
    python pipeline/run_pipeline.py --step update_news
    python pipeline/run_pipeline.py --step enrich_news
    python pipeline/run_pipeline.py --step all --smoke-test
    python pipeline/run_pipeline.py --step all --force
"""

import argparse
import math
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Ensure UTF-8 output on Windows. Some dependencies (e.g. vnstock) print
# banners containing emoji; the default Windows console encoding (cp1252)
# raises UnicodeEncodeError on those characters and aborts the task. Forcing
# UTF-8 on stdout/stderr keeps the pipeline running regardless of locale.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from pipeline.logging_config import setup_logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_STEPS = ("all", "data", "preprocess", "features", "train", "update_news", "enrich_news")

SMOKE_TEST_TICKERS = ["VNM", "VCB", "FPT"]
SMOKE_TEST_QUARTERS = ["2022Q1", "2022Q2", "2022Q3", "2022Q4"]

CONFIG_PATH = "config/pipeline_config.yaml"

# Required config keys and their expected types
REQUIRED_CONFIG_KEYS = {
    "tickers": list,
    "start_date": str,
    "end_date": str,
    "train_cutoff": str,
    "label_threshold": (int, float),
    "min_news_per_period": int,
}

# Checkpoint files: maps task name to its primary output file(s)
TASK_CHECKPOINTS: Dict[str, List[str]] = {
    "TASK_1": ["data/prices/all_vn30_prices.csv"],
    "TASK_2": [
        "data/news/cafef",  # directory with per-ticker files
        "data/news/vietstock",
        "data/news/tnck/tnck_raw.csv",
        "data/news/vietnambiz/vietnambiz_raw.csv",
        "data/news/vnexpress/vnexpress_raw.csv",
        "data/news/kinhtechungkhoan/kinhtechungkhoan_raw.csv",
    ],
    "TASK_2B": ["data/news/enriched/all_news_enriched.csv"],
    "TASK_3": ["data/news/matched/all_news_matched.csv"],
    "TASK_4": ["data/news/processed/all_news_processed.csv"],
    "TASK_5": [
        "data/aggregated/news_by_quarter.csv",
        "data/aggregated/prices_by_quarter.csv",
        "data/aggregated/master_dataset.csv",
    ],
    "TASK_6": ["data/aggregated/master_with_labels.csv"],
    "TASK_7": ["data/features/technical_features.csv"],
    "TASK_8": ["config/keywords_finance.json"],
    "TASK_9": ["data/features/keyword_features.csv"],
    "TASK_10": ["models/best_model.pkl", "reports/model_comparison.csv"],
    "TASK_11": ["reports/shap_summary.png"],
}

# Step → task mapping
STEP_TASKS: Dict[str, List[str]] = {
    "all": [
        "TASK_1", "TASK_2", "TASK_3", "TASK_2B", "TASK_4", "TASK_5", "TASK_6",
        "TASK_7", "TASK_8", "TASK_9", "TASK_10", "TASK_11",
    ],
    "data": ["TASK_1", "TASK_2", "TASK_3", "TASK_2B"],
    "enrich_news": ["TASK_2B"],
    "preprocess": ["TASK_4", "TASK_5", "TASK_6"],
    "features": [
        "TASK_4", "TASK_5", "TASK_6",  # prerequisites
        "TASK_7", "TASK_8", "TASK_9",  # feature extraction
    ],
    "train": ["TASK_10", "TASK_11"],
}

# Required directories per Requirement 12.11
REQUIRED_DIRECTORIES = [
    "config",
    "data/prices",
    "data/news/cafef",
    "data/news/vietstock",
    "data/news/tnck",
    "data/news/vietnambiz",
    "data/news/vnexpress",
    "data/news/kinhtechungkhoan",
    "data/news/matched",
    "data/news/processed",
    "data/news/enriched",
    "data/aggregated",
    "data/features",
    "models",
    "reports",
    "pipeline",
    "logs",
    "notebooks",
]

# Required config files per Requirement 12.11
REQUIRED_CONFIG_FILES = [
    "config/pipeline_config.yaml",
    "config/entity_aliases.json",
]

# Required pipeline module files per Requirement 12.11
REQUIRED_PIPELINE_FILES = [
    "pipeline/run_pipeline.py",
    "pipeline/task1_prices.py",
    "pipeline/task2_scrape.py",
    "pipeline/task2b_enrich_articles.py",
    "pipeline/task3_matching.py",
    "pipeline/task4_preprocess.py",
    "pipeline/task5_aggregate.py",
    "pipeline/task6_labels.py",
    "pipeline/task7_tech_features.py",
    "pipeline/task8_keywords.py",
    "pipeline/task9_kw_features.py",
    "pipeline/task10_train.py",
    "pipeline/task11_shap.py",
]


# ---------------------------------------------------------------------------
# Configuration loading and validation (Req 12.8)
# ---------------------------------------------------------------------------

def load_config(config_path: str = CONFIG_PATH) -> Dict[str, Any]:
    """Load and validate pipeline configuration from YAML.

    Args:
        config_path: Path to pipeline_config.yaml.

    Returns:
        Validated configuration dictionary.

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config is missing required keys or has invalid types.
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            "Please create it before running the pipeline."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        raise ValueError(f"Configuration file is empty: {config_path}")

    validate_config(config)
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """Validate config against expected schema. Fail fast with clear message.

    Args:
        config: Parsed YAML configuration dictionary.

    Raises:
        ValueError: If validation fails.
    """
    errors: List[str] = []

    for key, expected_type in REQUIRED_CONFIG_KEYS.items():
        if key not in config:
            errors.append(f"Missing required config key: '{key}'")
        elif not isinstance(config[key], expected_type):
            errors.append(
                f"Config key '{key}' has type {type(config[key]).__name__}, "
                f"expected {expected_type}"
            )

    # Validate tickers list is non-empty
    if "tickers" in config and isinstance(config["tickers"], list):
        if len(config["tickers"]) == 0:
            errors.append("Config key 'tickers' must not be empty")

    # Validate date format for start_date
    if "start_date" in config and isinstance(config["start_date"], str):
        try:
            datetime.strptime(config["start_date"], "%Y-%m-%d")
        except ValueError:
            errors.append(
                f"Config key 'start_date' has invalid date format: "
                f"'{config['start_date']}' (expected YYYY-MM-DD)"
            )

    # Validate end_date is either "auto" or a valid date
    if "end_date" in config and isinstance(config["end_date"], str):
        if config["end_date"] != "auto":
            try:
                datetime.strptime(config["end_date"], "%Y-%m-%d")
            except ValueError:
                errors.append(
                    f"Config key 'end_date' has invalid value: "
                    f"'{config['end_date']}' (expected 'auto' or YYYY-MM-DD)"
                )

    # Validate label_threshold is positive
    if "label_threshold" in config:
        val = config["label_threshold"]
        if isinstance(val, (int, float)) and val <= 0:
            errors.append(
                f"Config key 'label_threshold' must be positive, got {val}"
            )

    if errors:
        raise ValueError(
            "Pipeline configuration validation failed:\n  - "
            + "\n  - ".join(errors)
        )


def resolve_end_date(end_date: str) -> str:
    """Resolve 'auto' end_date to current date string."""
    if end_date == "auto":
        return datetime.now().strftime("%Y-%m-%d")
    return end_date


# ---------------------------------------------------------------------------
# Directory structure verification (Req 12.11)
# ---------------------------------------------------------------------------

def verify_directory_structure(logger) -> bool:
    """Ensure all required directories and files exist.

    Creates missing directories automatically. Warns about missing config files.

    Returns:
        True if all critical files exist, False otherwise.
    """
    all_ok = True

    # Create directories
    for d in REQUIRED_DIRECTORIES:
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
            logger.info("Created missing directory: %s", d)

    # Check config files
    for f in REQUIRED_CONFIG_FILES:
        if not os.path.isfile(f):
            logger.warning("Required config file missing: %s", f)
            all_ok = False

    # Check pipeline modules
    for f in REQUIRED_PIPELINE_FILES:
        if not os.path.isfile(f):
            logger.warning("Required pipeline module missing: %s", f)
            all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Checkpointing logic (Req 12.9)
# ---------------------------------------------------------------------------

def checkpoint_exists(task_name: str) -> bool:
    """Check if a task's checkpoint output file(s) exist.

    For TASK_2, checks that at least one source directory has CSV files.
    For other tasks, checks that the primary output file exists and is non-empty.

    Args:
        task_name: Task identifier (e.g., "TASK_1").

    Returns:
        True if checkpoint exists, False otherwise.
    """
    paths = TASK_CHECKPOINTS.get(task_name, [])
    if not paths:
        return False

    for path in paths:
        if os.path.isdir(path):
            # For directories, check if they contain any CSV files
            csv_files = [f for f in os.listdir(path) if f.endswith(".csv")]
            if csv_files:
                return True
        elif os.path.isfile(path) and os.path.getsize(path) > 0:
            return True

    return False


def should_skip_task(task_name: str, force: bool, logger) -> bool:
    """Determine if a task should be skipped based on checkpoint.

    Args:
        task_name: Task identifier.
        force: If True, never skip.
        logger: Logger instance.

    Returns:
        True if task should be skipped.
    """
    if force:
        return False

    if checkpoint_exists(task_name):
        logger.info(
            "SKIP %s — checkpoint exists. Use --force to rerun.", task_name
        )
        return True

    return False


# ---------------------------------------------------------------------------
# Task execution functions
# ---------------------------------------------------------------------------

def _count_rows(path: str) -> Optional[int]:
    """Count rows in a CSV file (excluding header). Returns None if file missing."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f) - 1  # subtract header
    except Exception:
        return None


def execute_task_1(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 1: Price Collection."""
    from pipeline.task1_prices import collect_prices

    tickers = SMOKE_TEST_TICKERS if smoke_test else config.get("tickers")
    start_date = config.get("start_date", "2022-01-01")
    end_date = resolve_end_date(config.get("end_date", "auto"))

    if smoke_test:
        end_date = "2022-12-31"

    collect_prices(tickers=tickers, start_date=start_date, end_date=end_date)


def execute_task_2(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 2: News Scraping."""
    from pipeline.task2_scrape import print_scraping_report, scrape_source

    tickers = SMOKE_TEST_TICKERS if smoke_test else config.get("tickers")
    start_date = config.get("start_date", "2022-01-01")

    for src in ["cafef", "vietstock", "tnck", "vietnambiz", "vnexpress", "kinhtechungkhoan"]:
        results = {}
        if src in ("tnck", "vietnambiz", "vnexpress", "kinhtechungkhoan"):
            results["ALL"] = scrape_source(src, ticker="ALL", start_date=start_date)
        else:
            for t in tickers:
                results[t] = scrape_source(src, ticker=t, start_date=start_date)
        print_scraping_report(src, results)


def execute_task_2b(config: Dict[str, Any], logger, smoke_test: bool = False, force: bool = False) -> None:
    """Execute TASK 2B: Article Full-Text Enrichment."""
    from pipeline.task2b_enrich_articles import run_enrichment

    run_enrichment(force=force)


def execute_task_3(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 3: Entity Matching."""
    from pipeline.task3_matching import run_matching

    run_matching()


def execute_task_4(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 4: Text Preprocessing."""
    from pipeline.task4_preprocess import run_preprocessing

    run_preprocessing()


def execute_task_5(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 5: Data Aggregation."""
    from pipeline.task5_aggregate import run_aggregation

    run_aggregation()


def execute_task_6(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 6: Label Building."""
    from pipeline.task6_labels import run_label_builder

    run_label_builder()


def execute_task_7(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 7: Technical Feature Extraction."""
    from pipeline.task7_tech_features import run_tech_features

    run_tech_features()


def execute_task_8(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 8: Keyword Building."""
    from pipeline.task8_keywords import run_keyword_builder

    run_keyword_builder()


def execute_task_9(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 9: Keyword Feature Extraction."""
    from pipeline.task9_kw_features import run_keyword_feature_extraction

    run_keyword_feature_extraction()


def execute_task_10(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 10: Model Training."""
    from pipeline.task10_train import run_model_training

    run_model_training()


def execute_task_11(config: Dict[str, Any], logger, smoke_test: bool = False) -> None:
    """Execute TASK 11: SHAP Analysis."""
    from pipeline.task11_shap import run_shap_analysis

    run_shap_analysis()


# Map task names to execution functions
TASK_EXECUTORS = {
    "TASK_1": execute_task_1,
    "TASK_2": execute_task_2,
    "TASK_2B": execute_task_2b,
    "TASK_3": execute_task_3,
    "TASK_4": execute_task_4,
    "TASK_5": execute_task_5,
    "TASK_6": execute_task_6,
    "TASK_7": execute_task_7,
    "TASK_8": execute_task_8,
    "TASK_9": execute_task_9,
    "TASK_10": execute_task_10,
    "TASK_11": execute_task_11,
}

# Human-readable task descriptions
TASK_DESCRIPTIONS = {
    "TASK_1": "Price Collection (vnstock OHLCV)",
    "TASK_2": "News Scraping (CafeF, Vietstock, TNCK, VietnamBiz, VnExpress, Kinhtechungkhoan)",
    "TASK_2B": "Article Full-Text Enrichment (detail pages → summaries/key facts)",
    "TASK_3": "Entity Matching (articles → tickers)",
    "TASK_4": "Text Preprocessing (clean, tokenize, deduplicate)",
    "TASK_5": "Data Aggregation (group by ticker × quarter)",
    "TASK_6": "Label Building (binary classification labels)",
    "TASK_7": "Technical Feature Extraction (RSI, MACD, BB, SMA, EMA)",
    "TASK_8": "Keyword Building (curate financial keywords)",
    "TASK_9": "Keyword Feature Extraction (TF-IDF, sentiment scores)",
    "TASK_10": "Model Training (3 configs × 4 algorithms)",
    "TASK_11": "SHAP Analysis (feature importance)",
}


# ---------------------------------------------------------------------------
# Structured logging helpers (Req 12.10)
# ---------------------------------------------------------------------------

def log_task_start(task_name: str, task_logger) -> None:
    """Log structured task start information."""
    task_logger.info("=" * 60)
    task_logger.info(
        "START %s: %s", task_name, TASK_DESCRIPTIONS.get(task_name, "")
    )
    task_logger.info("Timestamp: %s", datetime.now().isoformat())
    task_logger.info("=" * 60)

    # Log input row counts for tasks that read from known files
    input_files = _get_input_files(task_name)
    for inp in input_files:
        row_count = _count_rows(inp)
        if row_count is not None:
            task_logger.info("Input: %s (%d rows)", inp, row_count)


def log_task_end(task_name: str, task_logger, elapsed: float) -> None:
    """Log structured task completion information."""
    task_logger.info("-" * 60)
    task_logger.info(
        "END %s — completed in %.1f seconds", task_name, elapsed
    )

    # Log output row counts
    output_files = TASK_CHECKPOINTS.get(task_name, [])
    for out in output_files:
        if os.path.isfile(out):
            row_count = _count_rows(out)
            if row_count is not None:
                task_logger.info("Output: %s (%d rows)", out, row_count)

    task_logger.info("=" * 60)


def _get_input_files(task_name: str) -> List[str]:
    """Return known input files for a task."""
    mapping = {
        "TASK_2B": ["data/news/matched/all_news_matched.csv"],
        "TASK_3": [
            "data/news/cafef",
            "data/news/vietstock",
            "data/news/tnck/tnck_raw.csv",
            "data/news/vietnambiz/vietnambiz_raw.csv",
            "data/news/vnexpress/vnexpress_raw.csv",
            "data/news/kinhtechungkhoan/kinhtechungkhoan_raw.csv",
        ],
        "TASK_4": ["data/news/enriched/all_news_enriched.csv", "data/news/matched/all_news_matched.csv"],
        "TASK_5": ["data/prices/all_vn30_prices.csv", "data/news/processed/all_news_processed.csv"],
        "TASK_6": ["data/aggregated/master_dataset.csv"],
        "TASK_7": ["data/prices/all_vn30_prices.csv"],
        "TASK_8": ["data/news/processed/all_news_processed.csv"],
        "TASK_9": ["data/aggregated/news_by_quarter.csv"],
        "TASK_10": [
            "data/features/technical_features.csv",
            "data/features/keyword_features.csv",
            "data/aggregated/master_with_labels.csv",
        ],
        "TASK_11": ["models/best_model.pkl"],
    }
    return mapping.get(task_name, [])


# ---------------------------------------------------------------------------
# Update news (Req 12.7)
# ---------------------------------------------------------------------------

def execute_update_news(config: Dict[str, Any], force: bool, logger) -> None:
    """Scrape new articles since last run and update matched/processed files.

    This is an incremental update: it scrapes new articles, re-runs entity
    matching, and re-runs text preprocessing on the updated corpus.
    """
    from pipeline.task2_scrape import print_scraping_report, scrape_source
    from pipeline.task2b_enrich_articles import run_enrichment
    from pipeline.task3_matching import run_matching
    from pipeline.task4_preprocess import run_preprocessing

    tickers = config.get("tickers", [])
    start_date = config.get("start_date", "2022-01-01")

    logger.info("=" * 60)
    logger.info("UPDATE NEWS: Incremental scrape + update")
    logger.info("=" * 60)

    # Step 1: Scrape new articles (duplicate detection built into scrape_source)
    for src in ["cafef", "vietstock", "tnck", "vietnambiz", "vnexpress", "kinhtechungkhoan"]:
        results = {}
        if src in ("tnck", "vietnambiz", "vnexpress", "kinhtechungkhoan"):
            results["ALL"] = scrape_source(src, ticker="ALL", start_date=start_date)
        else:
            for t in tickers:
                results[t] = scrape_source(src, ticker=t, start_date=start_date)
        print_scraping_report(src, results)

    # Step 2: Re-run entity matching on full corpus
    logger.info("Re-running entity matching on updated corpus...")
    run_matching()

    # Step 3: Enrich matched news with full article text and structured evidence
    logger.info("Enriching matched news with full article text...")
    run_enrichment(force=force)

    # Step 4: Re-run text preprocessing on updated matched/enriched corpus
    logger.info("Re-running text preprocessing on updated corpus...")
    run_preprocessing()

    logger.info("UPDATE NEWS complete.")


# ---------------------------------------------------------------------------
# Main pipeline execution (Req 12.2-12.7)
# ---------------------------------------------------------------------------

def run_pipeline(
    step: str,
    force: bool = False,
    smoke_test: bool = False,
    config_path: str = CONFIG_PATH,
) -> None:
    """Execute pipeline steps.

    Args:
        step: One of "all", "data", "preprocess", "features", "train",
              or "update_news".
        force: If True, rerun even if checkpoint exists.
        smoke_test: If True, restrict to 3 tickers and 4 quarters.
        config_path: Path to pipeline_config.yaml.
    """
    # Set up main pipeline logger
    logger = setup_logger("PIPELINE")

    logger.info("=" * 60)
    logger.info("VN30 Stock Prediction Pipeline")
    logger.info("Step: %s | Force: %s | Smoke Test: %s", step, force, smoke_test)
    logger.info("=" * 60)

    # Load and validate configuration (Req 12.8)
    config = load_config(config_path)
    logger.info("Configuration loaded and validated from %s", config_path)

    # Resolve end_date
    config["end_date"] = resolve_end_date(config["end_date"])

    # Apply smoke test restrictions (Req 13.1)
    if smoke_test:
        config["tickers"] = SMOKE_TEST_TICKERS
        config["end_date"] = "2022-12-31"
        logger.info(
            "SMOKE TEST mode: restricted to tickers=%s, end_date=%s",
            SMOKE_TEST_TICKERS,
            config["end_date"],
        )

    # Verify directory structure (Req 12.11)
    verify_directory_structure(logger)

    # Handle update_news separately (Req 12.7)
    if step == "update_news":
        execute_update_news(config, force, logger)
        return

    # Get task list for the requested step
    tasks = STEP_TASKS.get(step)
    if tasks is None:
        raise ValueError(
            f"Unknown step: '{step}'. Valid steps: {', '.join(VALID_STEPS)}"
        )

    logger.info("Tasks to execute: %s", ", ".join(tasks))

    pipeline_start = time.time()
    task_timings: List[Dict[str, Any]] = []

    for task_name in tasks:
        # Check checkpoint (Req 12.9)
        if should_skip_task(task_name, force, logger):
            task_timings.append({
                "task": task_name,
                "status": "skipped",
                "elapsed": 0.0,
            })
            continue

        # Set up per-task logger (Req 12.10)
        task_logger = setup_logger(task_name)
        log_task_start(task_name, task_logger)

        executor = TASK_EXECUTORS.get(task_name)
        if executor is None:
            task_logger.error("No executor found for %s", task_name)
            continue

        task_start = time.time()
        try:
            if task_name == "TASK_2B":
                executor(config, task_logger, smoke_test=smoke_test, force=force)
            else:
                executor(config, task_logger, smoke_test=smoke_test)
            elapsed = time.time() - task_start
            log_task_end(task_name, task_logger, elapsed)
            task_timings.append({
                "task": task_name,
                "status": "completed",
                "elapsed": elapsed,
            })
            logger.info(
                "✓ %s completed in %.1f seconds", task_name, elapsed
            )
        except Exception as exc:
            elapsed = time.time() - task_start
            # Log full stack trace to task log file (Req 12.12)
            task_logger.error(
                "TASK FAILED: %s after %.1f seconds", task_name, elapsed
            )
            task_logger.error("Exception: %s", str(exc))
            task_logger.error("Stack trace:\n%s", traceback.format_exc())

            # Print human-readable error summary to stdout (Req 12.12)
            print(f"\n{'='*60}")
            print(f"ERROR in {task_name}: {TASK_DESCRIPTIONS.get(task_name, '')}")
            print(f"{'='*60}")
            print(f"Error: {exc}")
            print(f"Elapsed: {elapsed:.1f}s")
            print(f"See log file for full stack trace: logs/{task_name}_*.log")
            print(f"{'='*60}\n")

            task_timings.append({
                "task": task_name,
                "status": "failed",
                "elapsed": elapsed,
            })

            # Exit with non-zero return code without corrupting previous outputs
            _print_timing_report(task_timings, time.time() - pipeline_start)
            sys.exit(1)

    # Print timing report
    total_elapsed = time.time() - pipeline_start
    _print_timing_report(task_timings, total_elapsed)

    # Run smoke test verification if in smoke test mode (Req 13.3, 13.5)
    if smoke_test:
        # Check that no tasks failed
        failed_tasks = [t for t in task_timings if t["status"] == "failed"]
        if not failed_tasks:
            # Verify output files exist (Req 13.3)
            outputs_ok, _, missing = verify_smoke_test_outputs(logger)

            # Validate data sources (Req 13.5)
            sources_ok, _ = validate_smoke_test_data_sources(
                tickers=config.get("tickers", SMOKE_TEST_TICKERS),
                logger=logger,
            )

            if outputs_ok and sources_ok:
                logger.info("Smoke test PASSED — all verifications successful.")
                print("Smoke test PASSED ✓")
            else:
                logger.warning("Smoke test completed with warnings.")
                if missing:
                    print(f"Smoke test WARNING: {len(missing)} output file(s) missing.")

    logger.info("Pipeline completed successfully in %.1f seconds.", total_elapsed)


def _print_timing_report(
    task_timings: List[Dict[str, Any]], total_elapsed: float
) -> None:
    """Print a summary timing report for all tasks."""
    print(f"\n{'='*60}")
    print("Pipeline Timing Report")
    print(f"{'='*60}")
    for entry in task_timings:
        task = entry["task"]
        status = entry["status"]
        elapsed = entry["elapsed"]
        desc = TASK_DESCRIPTIONS.get(task, "")
        if status == "skipped":
            print(f"  {task}: SKIPPED (checkpoint exists) — {desc}")
        elif status == "completed":
            print(f"  {task}: {elapsed:>7.1f}s — {desc}")
        elif status == "failed":
            print(f"  {task}: FAILED after {elapsed:.1f}s — {desc}")
    print(f"{'─'*60}")
    print(f"  Total: {total_elapsed:.1f}s")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Smoke test output verification (Req 13.3)
# ---------------------------------------------------------------------------

# Key output files that must exist after a successful smoke test
SMOKE_TEST_REQUIRED_OUTPUTS = [
    "data/prices/all_vn30_prices.csv",
    "data/news/matched/all_news_matched.csv",
    "data/aggregated/master_with_labels.csv",
    "data/features/technical_features.csv",
    "data/features/keyword_features.csv",
    "models/best_model.pkl",
    "reports/model_comparison.csv",
]


def verify_smoke_test_outputs(logger) -> Tuple[bool, List[str], List[str]]:
    """Verify all key output files exist after smoke test (Req 13.3).

    Returns:
        Tuple of (all_ok, present_files, missing_files).
    """
    present: List[str] = []
    missing: List[str] = []

    for path in SMOKE_TEST_REQUIRED_OUTPUTS:
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            present.append(path)
        else:
            missing.append(path)

    all_ok = len(missing) == 0

    # Print verification report
    print(f"\n{'='*60}")
    print("Smoke Test Output Verification (Req 13.3)")
    print(f"{'='*60}")
    for path in present:
        size = os.path.getsize(path)
        print(f"  ✓ {path} ({size:,} bytes)")
    for path in missing:
        print(f"  ✗ MISSING: {path}")
    print(f"{'─'*60}")
    if all_ok:
        print("  Result: ALL output files present")
    else:
        print(f"  Result: {len(missing)} file(s) MISSING")
    print(f"{'='*60}\n")

    # Log results
    if all_ok:
        logger.info("Smoke test output verification PASSED: all %d files present.",
                     len(present))
    else:
        logger.warning("Smoke test output verification FAILED: %d file(s) missing: %s",
                        len(missing), ", ".join(missing))

    return all_ok, present, missing


# ---------------------------------------------------------------------------
# Smoke test data source validation (Req 13.4, 13.5)
# ---------------------------------------------------------------------------

def validate_smoke_test_data_sources(
    tickers: List[str],
    logger,
) -> Tuple[bool, Dict[str, Any]]:
    """Validate data sources after smoke test (Req 13.5).

    Checks:
    - vnstock retrieved price data successfully
    - At least 10 articles per ticker per quarter from CafeF
    - Pipeline produced no unhandled errors (inferred from successful completion)

    Args:
        tickers: List of smoke test tickers.
        logger: Logger instance.

    Returns:
        Tuple of (all_ok, validation_details).
    """
    import pandas as pd

    issues: List[str] = []
    details: Dict[str, Any] = {}

    # --- Check 1: vnstock data retrieval ---
    prices_path = "data/prices/all_vn30_prices.csv"
    if os.path.isfile(prices_path):
        try:
            prices_df = pd.read_csv(prices_path)
            tickers_found = sorted(prices_df["ticker"].unique().tolist()) if "ticker" in prices_df.columns else []
            total_rows = len(prices_df)
            details["vnstock"] = {
                "status": "OK",
                "tickers_found": tickers_found,
                "total_rows": total_rows,
            }
            if total_rows == 0:
                issues.append("vnstock returned 0 price rows")
            else:
                # Check each smoke test ticker has data
                for t in tickers:
                    ticker_rows = len(prices_df[prices_df["ticker"] == t]) if "ticker" in prices_df.columns else 0
                    if ticker_rows == 0:
                        issues.append(f"vnstock returned 0 rows for ticker {t}")
        except Exception as e:
            details["vnstock"] = {"status": "ERROR", "error": str(e)}
            issues.append(f"Failed to read price data: {e}")
    else:
        details["vnstock"] = {"status": "MISSING", "error": "File not found"}
        issues.append("Price data file not found: " + prices_path)

    # --- Check 2: CafeF article counts (≥10 per ticker per quarter) ---
    matched_path = "data/news/matched/all_news_matched.csv"
    if os.path.isfile(matched_path):
        try:
            news_df = pd.read_csv(matched_path)
            cafef_articles = news_df[news_df["source"] == "cafef"] if "source" in news_df.columns else pd.DataFrame()

            if "date" in cafef_articles.columns and len(cafef_articles) > 0:
                cafef_articles = cafef_articles.copy()
                cafef_articles["date"] = pd.to_datetime(cafef_articles["date"], errors="coerce")
                cafef_articles["quarter_id"] = cafef_articles["date"].apply(
                    lambda d: f"{d.year}Q{math.ceil(d.month / 3)}" if pd.notna(d) else None
                )
                # Filter to smoke test quarters
                cafef_filtered = cafef_articles[
                    cafef_articles["quarter_id"].isin(SMOKE_TEST_QUARTERS)
                    & cafef_articles["ticker"].isin(tickers)
                ]
                ticker_quarter_counts = (
                    cafef_filtered.groupby(["ticker", "quarter_id"]).size().reset_index(name="count")
                )
                low_coverage = ticker_quarter_counts[ticker_quarter_counts["count"] < 10]
                details["cafef"] = {
                    "status": "OK" if low_coverage.empty else "WARNING",
                    "total_articles": len(cafef_filtered),
                    "ticker_quarter_counts": ticker_quarter_counts.to_dict("records"),
                    "low_coverage_pairs": low_coverage.to_dict("records") if not low_coverage.empty else [],
                }
                if not low_coverage.empty:
                    for _, row in low_coverage.iterrows():
                        issues.append(
                            f"CafeF: {row['ticker']} {row['quarter_id']} has only "
                            f"{row['count']} articles (need ≥10)"
                        )
            else:
                details["cafef"] = {"status": "NO_DATA", "total_articles": 0}
                issues.append("No CafeF articles found in matched news data")
        except Exception as e:
            details["cafef"] = {"status": "ERROR", "error": str(e)}
            issues.append(f"Failed to validate CafeF data: {e}")
    else:
        details["cafef"] = {"status": "MISSING", "error": "File not found"}
        issues.append("Matched news file not found: " + matched_path)

    all_ok = len(issues) == 0

    # Print validation report
    print(f"\n{'='*60}")
    print("Smoke Test Data Source Validation (Req 13.5)")
    print(f"{'='*60}")

    # vnstock summary
    vs = details.get("vnstock", {})
    if vs.get("status") == "OK":
        print(f"  ✓ vnstock: {vs['total_rows']} price rows for "
              f"{len(vs['tickers_found'])} tickers")
    else:
        print(f"  ✗ vnstock: {vs.get('status', 'UNKNOWN')} — {vs.get('error', '')}")

    # CafeF summary
    cf = details.get("cafef", {})
    if cf.get("status") in ("OK", "WARNING"):
        print(f"  {'✓' if cf['status'] == 'OK' else '⚠'} CafeF: "
              f"{cf['total_articles']} articles matched to smoke test tickers/quarters")
        if cf.get("low_coverage_pairs"):
            for pair in cf["low_coverage_pairs"]:
                print(f"    ⚠ {pair['ticker']} {pair['quarter_id']}: "
                      f"{pair['count']} articles (< 10)")
    else:
        print(f"  ✗ CafeF: {cf.get('status', 'UNKNOWN')} — {cf.get('error', '')}")

    # No unhandled errors (confirmed by reaching this point)
    print(f"  ✓ Pipeline completed with no unhandled errors")

    print(f"{'─'*60}")
    if all_ok:
        print("  Result: ALL data source validations PASSED")
    else:
        print(f"  Result: {len(issues)} issue(s) found")
        for issue in issues:
            print(f"    - {issue}")
    print(f"{'='*60}\n")

    # Log results
    if all_ok:
        logger.info("Smoke test data source validation PASSED.")
    else:
        for issue in issues:
            logger.warning("Smoke test validation issue: %s", issue)

    return all_ok, details


# ---------------------------------------------------------------------------
# CLI (Req 12.1, 13.1)
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argparse CLI parser."""
    parser = argparse.ArgumentParser(
        description="VN30 Stock Prediction Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps:
  all          Execute TASK 1 through TASK 11 in sequential order
  data         Execute TASK 1, 2, 3, 2B (data collection + article enrichment)
  enrich_news  Execute TASK 2B only (full-text article enrichment)
  preprocess   Execute TASK 4, 5, 6 (text preprocessing + aggregation + labels)
  features     Execute TASK 4-6 (prerequisites) then TASK 7, 8, 9 (features)
  train        Execute TASK 10, 11 (model training + SHAP analysis)
  update_news  Scrape new articles, update matched and processed files

Examples:
  python pipeline/run_pipeline.py --step all
  python pipeline/run_pipeline.py --step data --force
  python pipeline/run_pipeline.py --step all --smoke-test
        """,
    )

    parser.add_argument(
        "--step",
        type=str,
        required=True,
        choices=VALID_STEPS,
        help="Pipeline step to execute.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Force rerun even if checkpoint exists.",
    )

    parser.add_argument(
        "--smoke-test",
        action="store_true",
        default=False,
        help=(
            "Restrict execution to 3 tickers (VNM, VCB, FPT) and "
            "4 quarters (2022Q1-2022Q4) for quick validation."
        ),
    )

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        run_pipeline(
            step=args.step,
            force=args.force,
            smoke_test=args.smoke_test,
        )
    except (FileNotFoundError, ValueError) as exc:
        # Configuration or validation errors — print and exit
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
