"""Tests for project structure and core configuration (Task 1)."""

import json
import os

import yaml

from pipeline.logging_config import setup_logger


def test_pipeline_config_loads():
    """Verify pipeline_config.yaml loads and has all required keys."""
    with open("config/pipeline_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert "tickers" in config
    assert "start_date" in config
    assert "end_date" in config
    assert "train_cutoff" in config
    assert "label_threshold" in config
    assert "min_news_per_period" in config


def test_pipeline_config_tickers():
    """Verify all 30 VN30 tickers are present."""
    with open("config/pipeline_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    expected_tickers = [
        "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR",
        "HDB", "HPG", "MBB", "MSN", "MWG", "PLX", "POW", "SAB",
        "SHB", "SSB", "SSI", "STB", "TCB", "TPB", "VCB", "VHM",
        "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
    ]
    assert len(config["tickers"]) == 30
    assert sorted(config["tickers"]) == sorted(expected_tickers)


def test_pipeline_config_values():
    """Verify config values match spec."""
    with open("config/pipeline_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert config["start_date"] == "2022-01-01"
    assert config["end_date"] == "auto"
    assert config["label_threshold"] == 0.02
    assert config["min_news_per_period"] == 5


def test_directory_structure():
    """Verify all required directories exist."""
    required_dirs = [
        "config",
        "data/prices",
        "data/news/cafef",
        "data/news/vietstock",
        "data/news/tnck",
        "data/news/matched",
        "data/news/processed",
        "data/aggregated",
        "data/features",
        "models",
        "reports",
        "pipeline",
        "logs",
        "notebooks",
    ]
    for d in required_dirs:
        assert os.path.isdir(d), f"Directory missing: {d}"


def test_config_files_exist():
    """Verify all required config files exist."""
    required_files = [
        "config/pipeline_config.yaml",
        "config/keywords_finance.json",
        "config/keywords_by_group.json",
        "config/stopwords_finance.txt",
        "config/entity_aliases.json",
    ]
    for f in required_files:
        assert os.path.isfile(f), f"Config file missing: {f}"


def test_pipeline_modules_exist():
    """Verify all pipeline module files exist."""
    required_files = [
        "pipeline/__init__.py",
        "pipeline/run_pipeline.py",
        "pipeline/task1_prices.py",
        "pipeline/task2_scrape.py",
        "pipeline/task3_matching.py",
        "pipeline/task4_preprocess.py",
        "pipeline/task5_aggregate.py",
        "pipeline/task6_labels.py",
        "pipeline/task7_tech_features.py",
        "pipeline/task8_keywords.py",
        "pipeline/task9_kw_features.py",
        "pipeline/task10_train.py",
        "pipeline/task11_shap.py",
        "pipeline/logging_config.py",
    ]
    for f in required_files:
        assert os.path.isfile(f), f"Pipeline module missing: {f}"


def test_requirements_txt_exists():
    """Verify requirements.txt exists with expected dependencies."""
    assert os.path.isfile("requirements.txt")
    with open("requirements.txt", "r", encoding="utf-8") as f:
        content = f.read().lower()

    expected_deps = [
        "vnstock",
        "requests",
        "beautifulsoup4",
        "underthesea",
        "pandas",
        "pandas-ta",
        "scikit-learn",
        "xgboost",
        "lightgbm",
        "shap",
        "pyyaml",
        "matplotlib",
        "seaborn",
        "rapidfuzz",
    ]
    for dep in expected_deps:
        assert dep in content, f"Dependency missing in requirements.txt: {dep}"


def test_keywords_finance_json_structure():
    """Verify keywords_finance.json has correct structure."""
    with open("config/keywords_finance.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "positive" in data
    assert "negative" in data
    assert "neutral" in data
    assert isinstance(data["positive"], list)
    assert isinstance(data["negative"], list)
    assert isinstance(data["neutral"], list)


def test_keywords_by_group_json_structure():
    """Verify keywords_by_group.json has groups A-F."""
    with open("config/keywords_by_group.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for group in ["A", "B", "C", "D", "E", "F"]:
        assert group in data, f"Group {group} missing in keywords_by_group.json"


def test_stopwords_finance_txt():
    """Verify stopwords file has expected entries."""
    with open("config/stopwords_finance.txt", "r", encoding="utf-8") as f:
        lines = [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    expected_stopwords = [
        "công ty",
        "doanh nghiệp",
        "cho biết",
        "theo đó",
        "được biết",
    ]
    for sw in expected_stopwords:
        assert sw in lines, f"Stopword missing: {sw}"

    # Should have at least 23 custom stopwords per spec
    assert len(lines) >= 23


def test_logging_setup():
    """Verify logging configuration works correctly."""
    logger = setup_logger("TEST_TASK")
    assert logger is not None
    assert logger.name == "TEST_TASK"
    assert len(logger.handlers) >= 2  # file + console


def test_logging_format():
    """Verify log format includes task_name, timestamp, and level."""
    import logging

    logger = setup_logger("FORMAT_TEST")
    # Check that the filter injects task_name
    for handler in logger.handlers:
        for f in handler.filters:
            assert hasattr(f, "task_name")
            assert f.task_name == "FORMAT_TEST"
