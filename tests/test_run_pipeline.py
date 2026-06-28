"""Integration tests for pipeline/run_pipeline.py (Task 19.8).

Tests CLI argument parsing, checkpoint skip logic, force flag behavior,
error handling, logging, and step-to-task mapping.

Requirements: 12.1, 12.2, 12.4, 12.5, 12.9, 12.12
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import yaml

from pipeline.run_pipeline import (
    SMOKE_TEST_QUARTERS,
    SMOKE_TEST_TICKERS,
    SMOKE_TEST_REQUIRED_OUTPUTS,
    STEP_TASKS,
    VALID_STEPS,
    build_parser,
    checkpoint_exists,
    load_config,
    resolve_end_date,
    run_pipeline,
    should_skip_task,
    validate_config,
    validate_smoke_test_data_sources,
    verify_directory_structure,
    verify_smoke_test_outputs,
)


# ---------------------------------------------------------------------------
# CLI argument parsing tests (Req 12.1)
# ---------------------------------------------------------------------------


class TestCLIParsing:
    """Test argparse CLI argument parsing."""

    def test_step_all(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "all"])
        assert args.step == "all"
        assert args.force is False
        assert args.smoke_test is False

    def test_step_data(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "data"])
        assert args.step == "data"

    def test_step_preprocess(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "preprocess"])
        assert args.step == "preprocess"

    def test_step_features(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "features"])
        assert args.step == "features"

    def test_step_train(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "train"])
        assert args.step == "train"

    def test_step_update_news(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "update_news"])
        assert args.step == "update_news"

    def test_force_flag(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "all", "--force"])
        assert args.force is True

    def test_smoke_test_flag(self):
        """Verify --smoke-test flag is accepted and parsed correctly."""
        parser = build_parser()
        args = parser.parse_args(["--step", "all", "--smoke-test"])
        assert args.smoke_test is True

    def test_combined_flags(self):
        parser = build_parser()
        args = parser.parse_args(["--step", "data", "--force", "--smoke-test"])
        assert args.step == "data"
        assert args.force is True
        assert args.smoke_test is True

    def test_invalid_step_rejected(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--step", "invalid"])

    def test_missing_step_rejected(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_all_valid_steps_accepted(self):
        """Every value in VALID_STEPS should be accepted by the parser."""
        parser = build_parser()
        for step in VALID_STEPS:
            args = parser.parse_args(["--step", step])
            assert args.step == step


# ---------------------------------------------------------------------------
# Step-to-task mapping tests (Req 12.2, 12.4, 12.5)
# ---------------------------------------------------------------------------


class TestStepTaskMapping:
    """Test that each --step value maps to the correct task sequence."""

    def test_step_all_runs_task_1_through_11(self):
        """--step all should run TASK 1 through TASK 11 (not TASK 12)."""
        tasks = STEP_TASKS["all"]
        expected = [f"TASK_{i}" for i in range(1, 12)]
        assert tasks == expected

    def test_step_data_runs_task_1_2_3(self):
        tasks = STEP_TASKS["data"]
        assert tasks == ["TASK_1", "TASK_2", "TASK_3"]

    def test_step_preprocess_runs_task_4_5_6(self):
        """--step preprocess should run TASK 4, 5, 6."""
        tasks = STEP_TASKS["preprocess"]
        assert tasks == ["TASK_4", "TASK_5", "TASK_6"]

    def test_step_features_includes_prerequisites(self):
        """--step features should include TASK 4/5/6 as prerequisites."""
        tasks = STEP_TASKS["features"]
        assert tasks == [
            "TASK_4", "TASK_5", "TASK_6",
            "TASK_7", "TASK_8", "TASK_9",
        ]

    def test_step_train_runs_task_10_11(self):
        tasks = STEP_TASKS["train"]
        assert tasks == ["TASK_10", "TASK_11"]

    def test_step_all_does_not_include_task_12(self):
        """TASK 12 is the runner itself and should not be in any step."""
        for step_name, tasks in STEP_TASKS.items():
            assert "TASK_12" not in tasks


# ---------------------------------------------------------------------------
# Checkpoint skip logic tests (Req 12.9)
# ---------------------------------------------------------------------------


class TestCheckpointing:
    """Test checkpoint detection and skip logic."""

    def test_checkpoint_missing_file(self, tmp_path):
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(tmp_path / "nonexistent.csv")]},
        ):
            assert checkpoint_exists("TASK_99") is False

    def test_checkpoint_existing_file(self, tmp_path):
        f = tmp_path / "output.csv"
        f.write_text("col1,col2\n1,2\n")
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(f)]},
        ):
            assert checkpoint_exists("TASK_99") is True

    def test_checkpoint_empty_file(self, tmp_path):
        f = tmp_path / "empty.csv"
        f.write_text("")
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(f)]},
        ):
            assert checkpoint_exists("TASK_99") is False

    def test_checkpoint_dir_with_csvs(self, tmp_path):
        d = tmp_path / "news"
        d.mkdir()
        (d / "VNM_cafef.csv").write_text("col1\nval1\n")
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(d)]},
        ):
            assert checkpoint_exists("TASK_99") is True

    def test_checkpoint_empty_dir(self, tmp_path):
        d = tmp_path / "empty_dir"
        d.mkdir()
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(d)]},
        ):
            assert checkpoint_exists("TASK_99") is False

    def test_skip_when_checkpoint_exists(self, tmp_path):
        f = tmp_path / "output.csv"
        f.write_text("col1\n1\n")
        mock_logger = MagicMock()
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(f)]},
        ):
            assert should_skip_task("TASK_99", False, mock_logger) is True
            mock_logger.info.assert_called()

    def test_no_skip_when_force(self, tmp_path):
        f = tmp_path / "output.csv"
        f.write_text("col1\n1\n")
        mock_logger = MagicMock()
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(f)]},
        ):
            assert should_skip_task("TASK_99", True, mock_logger) is False

    def test_no_skip_when_no_checkpoint(self, tmp_path):
        mock_logger = MagicMock()
        with patch.dict(
            "pipeline.run_pipeline.TASK_CHECKPOINTS",
            {"TASK_99": [str(tmp_path / "missing.csv")]},
        ):
            assert should_skip_task("TASK_99", False, mock_logger) is False


# ---------------------------------------------------------------------------
# Configuration tests (Req 12.8)
# ---------------------------------------------------------------------------


class TestConfigLoading:
    """Test configuration loading and validation."""

    def test_load_valid_config(self):
        config = load_config("config/pipeline_config.yaml")
        assert "tickers" in config
        assert "start_date" in config

    def test_load_missing_config_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(str(tmp_path / "nonexistent.yaml"))

    def test_validate_missing_key(self):
        incomplete = {"tickers": ["VNM"], "start_date": "2022-01-01"}
        with pytest.raises(ValueError, match="Missing required config key"):
            validate_config(incomplete)

    def test_validate_wrong_type(self):
        bad = {
            "tickers": "not_a_list",
            "start_date": "2022-01-01",
            "end_date": "auto",
            "train_cutoff": "2025-01-01",
            "label_threshold": 0.02,
            "min_news_per_period": 5,
        }
        with pytest.raises(ValueError, match="has type"):
            validate_config(bad)

    def test_validate_empty_tickers(self):
        bad = {
            "tickers": [],
            "start_date": "2022-01-01",
            "end_date": "auto",
            "train_cutoff": "2025-01-01",
            "label_threshold": 0.02,
            "min_news_per_period": 5,
        }
        with pytest.raises(ValueError, match="must not be empty"):
            validate_config(bad)

    def test_validate_invalid_date(self):
        bad = {
            "tickers": ["VNM"],
            "start_date": "not-a-date",
            "end_date": "auto",
            "train_cutoff": "2025-01-01",
            "label_threshold": 0.02,
            "min_news_per_period": 5,
        }
        with pytest.raises(ValueError, match="invalid date format"):
            validate_config(bad)

    def test_resolve_end_date_auto(self):
        from datetime import datetime
        result = resolve_end_date("auto")
        assert result == datetime.now().strftime("%Y-%m-%d")

    def test_resolve_end_date_explicit(self):
        assert resolve_end_date("2024-06-30") == "2024-06-30"

    def test_load_empty_config_raises(self, tmp_path):
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")
        with pytest.raises(ValueError, match="empty"):
            load_config(str(empty_file))


# ---------------------------------------------------------------------------
# Error handling tests (Req 12.12)
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Test error handling and recovery."""

    @patch("pipeline.run_pipeline.TASK_EXECUTORS", {
        "TASK_1": MagicMock(side_effect=RuntimeError("Simulated failure")),
    })
    @patch("pipeline.run_pipeline.STEP_TASKS", {"data": ["TASK_1"]})
    @patch("pipeline.run_pipeline.TASK_CHECKPOINTS", {"TASK_1": []})
    def test_task_failure_exits_nonzero(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(yaml.dump({
            "tickers": ["VNM"],
            "start_date": "2022-01-01",
            "end_date": "auto",
            "train_cutoff": "2025-01-01",
            "label_threshold": 0.02,
            "min_news_per_period": 5,
        }))
        with pytest.raises(SystemExit) as exc_info:
            run_pipeline(step="data", config_path=str(config_path))
        assert exc_info.value.code == 1

    @patch("pipeline.run_pipeline.TASK_EXECUTORS", {
        "TASK_1": MagicMock(side_effect=RuntimeError("Simulated failure")),
    })
    @patch("pipeline.run_pipeline.STEP_TASKS", {"data": ["TASK_1"]})
    @patch("pipeline.run_pipeline.TASK_CHECKPOINTS", {"TASK_1": []})
    def test_task_failure_prints_error(self, tmp_path, capsys):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(yaml.dump({
            "tickers": ["VNM"],
            "start_date": "2022-01-01",
            "end_date": "auto",
            "train_cutoff": "2025-01-01",
            "label_threshold": 0.02,
            "min_news_per_period": 5,
        }))
        with pytest.raises(SystemExit):
            run_pipeline(step="data", config_path=str(config_path))
        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "TASK_1" in captured.out


# ---------------------------------------------------------------------------
# Directory structure tests (Req 12.11)
# ---------------------------------------------------------------------------


class TestDirectoryStructure:
    """Test directory structure verification."""

    def test_creates_missing_dirs(self, tmp_path):
        mock_logger = MagicMock()
        test_dirs = [str(tmp_path / "test_dir")]
        with patch("pipeline.run_pipeline.REQUIRED_DIRECTORIES", test_dirs):
            with patch("pipeline.run_pipeline.REQUIRED_CONFIG_FILES", []):
                with patch("pipeline.run_pipeline.REQUIRED_PIPELINE_FILES", []):
                    verify_directory_structure(mock_logger)
        assert os.path.isdir(str(tmp_path / "test_dir"))

    def test_warns_missing_config(self, tmp_path):
        mock_logger = MagicMock()
        with patch("pipeline.run_pipeline.REQUIRED_DIRECTORIES", []):
            with patch(
                "pipeline.run_pipeline.REQUIRED_CONFIG_FILES",
                [str(tmp_path / "missing.yaml")],
            ):
                with patch("pipeline.run_pipeline.REQUIRED_PIPELINE_FILES", []):
                    result = verify_directory_structure(mock_logger)
        assert result is False
        mock_logger.warning.assert_called()


# ---------------------------------------------------------------------------
# Smoke test constants (Req 13.1)
# ---------------------------------------------------------------------------


class TestSmokeTestConfig:
    """Test smoke test configuration constants."""

    def test_smoke_test_tickers(self):
        assert SMOKE_TEST_TICKERS == ["VNM", "VCB", "FPT"]

    def test_smoke_test_quarters(self):
        assert SMOKE_TEST_QUARTERS == ["2022Q1", "2022Q2", "2022Q3", "2022Q4"]

    def test_smoke_tickers_in_vn30(self):
        config = load_config("config/pipeline_config.yaml")
        for ticker in SMOKE_TEST_TICKERS:
            assert ticker in config["tickers"]


# ---------------------------------------------------------------------------
# Smoke test output verification tests (Req 13.3 — Task 20.2)
# ---------------------------------------------------------------------------


class TestSmokeTestOutputVerification:
    """Test smoke test output file verification."""

    def test_required_outputs_list(self):
        """Verify the required outputs list contains all expected files."""
        expected = [
            "data/prices/all_vn30_prices.csv",
            "data/news/matched/all_news_matched.csv",
            "data/aggregated/master_with_labels.csv",
            "data/features/technical_features.csv",
            "data/features/keyword_features.csv",
            "models/best_model.pkl",
            "reports/model_comparison.csv",
        ]
        assert SMOKE_TEST_REQUIRED_OUTPUTS == expected

    def test_all_outputs_present(self, tmp_path):
        """When all output files exist, verification should pass."""
        mock_logger = MagicMock()
        # Create all required files in tmp_path
        files = []
        for rel_path in SMOKE_TEST_REQUIRED_OUTPUTS:
            full = tmp_path / rel_path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text("header\nrow1\n")
            files.append(str(full))

        with patch(
            "pipeline.run_pipeline.SMOKE_TEST_REQUIRED_OUTPUTS", files
        ):
            all_ok, present, missing = verify_smoke_test_outputs(mock_logger)

        assert all_ok is True
        assert len(present) == len(SMOKE_TEST_REQUIRED_OUTPUTS)
        assert len(missing) == 0

    def test_missing_outputs_detected(self, tmp_path):
        """When some output files are missing, verification should fail."""
        mock_logger = MagicMock()
        # Create only the first 3 files
        files = []
        for i, rel_path in enumerate(SMOKE_TEST_REQUIRED_OUTPUTS):
            full = tmp_path / rel_path
            full.parent.mkdir(parents=True, exist_ok=True)
            if i < 3:
                full.write_text("header\nrow1\n")
            files.append(str(full))

        with patch(
            "pipeline.run_pipeline.SMOKE_TEST_REQUIRED_OUTPUTS", files
        ):
            all_ok, present, missing = verify_smoke_test_outputs(mock_logger)

        assert all_ok is False
        assert len(present) == 3
        assert len(missing) == len(SMOKE_TEST_REQUIRED_OUTPUTS) - 3

    def test_empty_file_treated_as_missing(self, tmp_path):
        """Empty files should be treated as missing."""
        mock_logger = MagicMock()
        full = tmp_path / "empty.csv"
        full.write_text("")

        with patch(
            "pipeline.run_pipeline.SMOKE_TEST_REQUIRED_OUTPUTS", [str(full)]
        ):
            all_ok, present, missing = verify_smoke_test_outputs(mock_logger)

        assert all_ok is False
        assert len(missing) == 1


# ---------------------------------------------------------------------------
# Smoke test data source validation tests (Req 13.5 — Task 20.3)
# ---------------------------------------------------------------------------


class TestSmokeTestDataSourceValidation:
    """Test smoke test data source validation."""

    def test_vnstock_validation_with_valid_data(self, tmp_path):
        """vnstock validation passes when price data exists for all tickers."""
        mock_logger = MagicMock()
        import pandas as pd

        prices_path = tmp_path / "data" / "prices" / "all_vn30_prices.csv"
        prices_path.parent.mkdir(parents=True, exist_ok=True)
        prices_path.write_text(
            "ticker,date,open,high,low,close,volume\n"
            "VNM,2022-01-04,80000,81000,79000,80500,1000000\n"
            "VCB,2022-01-04,90000,91000,89000,90500,2000000\n"
            "FPT,2022-01-04,70000,71000,69000,70500,1500000\n"
        )

        matched_path = tmp_path / "data" / "news" / "matched" / "all_news_matched.csv"
        matched_path.parent.mkdir(parents=True, exist_ok=True)
        # Create enough CafeF articles (≥10 per ticker per quarter)
        rows = "date,title,description,url,source,ticker,match_confidence\n"
        for ticker in ["VNM", "VCB", "FPT"]:
            for month in ["01", "02", "03"]:
                for i in range(4):  # 4 articles per month × 3 months = 12 per quarter
                    rows += (
                        f"2022-{month}-{10+i},Title {i},Desc,http://url/{ticker}/{month}/{i},"
                        f"cafef,{ticker},exact\n"
                    )
        matched_path.write_text(rows)

        # Patch os.path.isfile and pd.read_csv to use our temp files
        prices_df = pd.read_csv(str(prices_path))
        news_df = pd.read_csv(str(matched_path))

        def isfile_side_effect(p):
            if "prices" in p and "all_vn30" in p:
                return True
            if "matched" in p and "all_news" in p:
                return True
            return os.path.isfile(p)

        with patch("pipeline.run_pipeline.os.path.isfile", side_effect=isfile_side_effect):
            with patch("pandas.read_csv") as mock_csv:
                def csv_side_effect(path):
                    if "prices" in str(path):
                        return prices_df
                    return news_df
                mock_csv.side_effect = csv_side_effect

                all_ok, details = validate_smoke_test_data_sources(
                    tickers=["VNM", "VCB", "FPT"],
                    logger=mock_logger,
                )

        assert details["vnstock"]["status"] == "OK"
        assert details["vnstock"]["total_rows"] == 3

    def test_vnstock_validation_missing_file(self):
        """vnstock validation fails when price file is missing."""
        mock_logger = MagicMock()

        with patch("pipeline.run_pipeline.os.path.isfile", return_value=False):
            all_ok, details = validate_smoke_test_data_sources(
                tickers=["VNM", "VCB", "FPT"],
                logger=mock_logger,
            )

        assert all_ok is False
        assert details["vnstock"]["status"] == "MISSING"

    def test_cafef_low_coverage_detected(self, tmp_path):
        """CafeF validation warns when article count < 10 per ticker per quarter."""
        mock_logger = MagicMock()
        import pandas as pd

        prices_df = pd.DataFrame({
            "ticker": ["VNM", "VCB", "FPT"],
            "date": ["2022-01-04"] * 3,
            "close": [80000, 90000, 70000],
        })

        # Only 3 articles for VNM in 2022Q1 (below threshold of 10)
        news_df = pd.DataFrame({
            "date": (
                ["2022-01-10", "2022-01-15", "2022-02-10"]
                + [f"2022-01-{10+i}" for i in range(10)]
                + [f"2022-01-{10+i}" for i in range(10)]
            ),
            "title": [f"Title {i}" for i in range(23)],
            "description": ["Desc"] * 23,
            "url": [f"http://url/{i}" for i in range(23)],
            "source": ["cafef"] * 23,
            "ticker": ["VNM", "VNM", "VNM"] + ["VCB"] * 10 + ["FPT"] * 10,
            "match_confidence": ["exact"] * 23,
        })

        def isfile_side_effect(p):
            return True

        with patch("pipeline.run_pipeline.os.path.isfile", side_effect=isfile_side_effect):
            with patch("pandas.read_csv") as mock_csv:
                def csv_side_effect(path):
                    if "prices" in str(path):
                        return prices_df
                    return news_df
                mock_csv.side_effect = csv_side_effect

                all_ok, details = validate_smoke_test_data_sources(
                    tickers=["VNM", "VCB", "FPT"],
                    logger=mock_logger,
                )

        assert all_ok is False
        assert details["cafef"]["status"] == "WARNING"
        assert len(details["cafef"]["low_coverage_pairs"]) > 0


# ---------------------------------------------------------------------------
# Smoke test integration in run_pipeline (Req 13.1, 13.2 — Task 20.1)
# ---------------------------------------------------------------------------


class TestSmokeTestIntegration:
    """Test that smoke test mode correctly restricts execution."""

    def test_smoke_test_restricts_tickers_in_config(self, tmp_path):
        """When smoke_test=True, config tickers should be restricted to 3."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(yaml.dump({
            "tickers": ["VNM", "VCB", "FPT", "HPG", "MBB"],
            "start_date": "2022-01-01",
            "end_date": "auto",
            "train_cutoff": "2025-01-01",
            "label_threshold": 0.02,
            "min_news_per_period": 5,
        }))

        # Mock all task executors to capture the config they receive
        captured_configs = {}

        def make_mock_executor(task_name):
            def executor(config, logger, smoke_test=False):
                captured_configs[task_name] = {
                    "tickers": config.get("tickers"),
                    "end_date": config.get("end_date"),
                }
            return executor

        mock_executors = {
            f"TASK_{i}": make_mock_executor(f"TASK_{i}") for i in range(1, 12)
        }

        with patch.dict("pipeline.run_pipeline.TASK_EXECUTORS", mock_executors):
            with patch.dict("pipeline.run_pipeline.TASK_CHECKPOINTS", {
                f"TASK_{i}": [] for i in range(1, 12)
            }):
                with patch("pipeline.run_pipeline.verify_smoke_test_outputs",
                           return_value=(True, [], [])):
                    with patch("pipeline.run_pipeline.validate_smoke_test_data_sources",
                               return_value=(True, {})):
                        run_pipeline(
                            step="all",
                            smoke_test=True,
                            config_path=str(config_path),
                        )

        # All tasks should have received the restricted ticker list
        for task_name, cfg in captured_configs.items():
            assert cfg["tickers"] == SMOKE_TEST_TICKERS, (
                f"{task_name} received wrong tickers: {cfg['tickers']}"
            )
            assert cfg["end_date"] == "2022-12-31", (
                f"{task_name} received wrong end_date: {cfg['end_date']}"
            )

    def test_smoke_test_runs_all_11_tasks(self, tmp_path):
        """Smoke test with --step all should execute TASK 1 through TASK 11."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(yaml.dump({
            "tickers": ["VNM"],
            "start_date": "2022-01-01",
            "end_date": "auto",
            "train_cutoff": "2025-01-01",
            "label_threshold": 0.02,
            "min_news_per_period": 5,
        }))

        executed_tasks = []

        def make_mock_executor(task_name):
            def executor(config, logger, smoke_test=False):
                executed_tasks.append(task_name)
            return executor

        mock_executors = {
            f"TASK_{i}": make_mock_executor(f"TASK_{i}") for i in range(1, 12)
        }

        with patch.dict("pipeline.run_pipeline.TASK_EXECUTORS", mock_executors):
            with patch.dict("pipeline.run_pipeline.TASK_CHECKPOINTS", {
                f"TASK_{i}": [] for i in range(1, 12)
            }):
                with patch("pipeline.run_pipeline.verify_smoke_test_outputs",
                           return_value=(True, [], [])):
                    with patch("pipeline.run_pipeline.validate_smoke_test_data_sources",
                               return_value=(True, {})):
                        run_pipeline(
                            step="all",
                            smoke_test=True,
                            config_path=str(config_path),
                        )

        expected = [f"TASK_{i}" for i in range(1, 12)]
        assert executed_tasks == expected
