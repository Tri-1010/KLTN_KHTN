from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = BUNDLE_ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


builder = load("build_v6_primary_panel")
runner = load("run_v6_technical_primary")


def protocol() -> dict:
    return builder.load_v6_spec()


def synthetic_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    date = pd.Timestamp("2024-01-02")
    exit_date = pd.Timestamp("2024-01-30")
    targets = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "entry_date": [date, date],
            "target_exit_date": [exit_date, exit_date],
            "target_status": ["ok", "ok"],
            "stock_return_T20": [0.03, -0.01],
            "VNINDEX_return_T20": [0.01, 0.01],
            "excess_return_T20": [0.02, -0.02],
            "label_outperform_T20": pd.Series([1, 0], dtype="Int64"),
        }
    )
    technical = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "quarter_id": ["2023Q4", "2023Q4"],
            "momentum": [1.0, -1.0],
            "volume": [100.0, 200.0],
        }
    )
    # BBB establishes that 2023Q4 is inside the observed keyword source period;
    # AAA has no row and is therefore an auditable no-news zero-fill case.
    keyword = pd.DataFrame(
        {
            "ticker": ["BBB"],
            "quarter_id": ["2023Q4"],
            "news_count": [2],
            "news_count_log": [np.log(3)],
            "has_min_news": [0],
            "kw_profit": [3.0],
            "kw_norm_profit": [1.5],
            "tfidf_profit": [0.7],
        }
    )
    semantic = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "date": [date, date],
            "semantic_news_count": [0.0, 1.0],
            "semantic_news_count_roll_20d": [0.0, 1.0],
            "support_count": [0.0, 1.0],
            "risk_count": [0.0, 0.0],
            "artifact_schema_version": ["semantic_daily_features_v2"] * 2,
        }
    )
    return targets, technical, keyword, semantic


def test_protocol_lock_matches_v6_primary_contract():
    spec = protocol()
    assert spec["observation_key"] == ["ticker", "date", "target_exit_date"]
    assert spec["primary_row_rule"] == [
        "target_status == ok",
        "lagged_technical_features_available",
    ]
    assert list(spec["configs"]) == [
        "A_technical",
        "B_technical_keyword",
        "C_technical_semantic",
    ]
    rf = spec["models"]["random_forest"]
    assert rf == {
        "n_estimators": 300,
        "max_depth": 6,
        "min_samples_leaf": 5,
        "class_weight": "balanced",
        "random_state": 42,
        "n_jobs": -1,
    }
    assert spec["primary"] == {
        "model": "RandomForest",
        "metric": "balanced_accuracy",
        "hypothesis_family": "V6_H1_H2",
    }


def test_no_news_row_remains_eligible_and_news_predictors_are_zero_filled():
    targets, technical, keyword, semantic = synthetic_inputs()
    panel = builder.build_v6_primary_panel(
        targets, technical, keyword, semantic, protocol()
    )
    row = panel.loc[panel["ticker"].eq("AAA")].iloc[0]
    assert bool(row["panel_eligible"])
    assert row["keyword_feature_status"] == "no_news_zero_filled"
    assert row["kw_lag1q__kw_profit"] == 0.0
    assert row["kw_lag1q__kw_norm_profit"] == 0.0
    assert row["sem_daily__support_count"] == 0.0


def test_coverage_and_full_corpus_tfidf_are_not_predictors_or_eligibility_rules():
    targets, technical, keyword, semantic = synthetic_inputs()
    panel = builder.build_v6_primary_panel(
        targets, technical, keyword, semantic, protocol()
    )
    manifest = builder.build_feature_manifest(panel, protocol())
    excluded = manifest.set_index("source_feature")
    for column in (
        "news_count",
        "news_count_log",
        "has_min_news",
        "semantic_news_count",
        "semantic_news_count_roll_20d",
    ):
        assert not bool(excluded.loc[column, "predictor"])
        assert json.loads(excluded.loc[column, "configs"]) == []
    assert not bool(excluded.loc["tfidf_profit", "predictor"])
    assert excluded.loc["tfidf_profit", "exclusion_reason"] == (
        "precomputed_full_corpus_tfidf"
    )
    assert panel["panel_eligible"].all()


def test_target_and_technical_only_control_primary_eligibility():
    targets, technical, keyword, semantic = synthetic_inputs()
    keyword.loc[:, "news_count"] = 1000
    panel = builder.build_v6_primary_panel(
        targets, technical, keyword, semantic, protocol()
    )
    assert panel["panel_eligible"].all()

    targets.loc[targets["ticker"].eq("AAA"), "target_status"] = "missing_stock_exit"
    no_target = builder.build_v6_primary_panel(
        targets, technical, keyword, semantic, protocol()
    )
    assert not bool(no_target.loc[no_target["ticker"].eq("AAA"), "panel_eligible"].iloc[0])

    technical = technical[technical["ticker"].ne("BBB")]
    no_technical = builder.build_v6_primary_panel(
        synthetic_inputs()[0], technical, keyword, semantic, protocol()
    )
    assert not bool(
        no_technical.loc[no_technical["ticker"].eq("BBB"), "panel_eligible"].iloc[0]
    )


def prediction_fixture() -> pd.DataFrame:
    rows = []
    for config in protocol()["configs"]:
        for fold in (1, 2, 3):
            for ticker, label in (("AAA", 1), ("BBB", 0)):
                date = pd.Timestamp("2024-01-01") + pd.offsets.BDay(fold)
                rows.append(
                    {
                        "row_id": f"{ticker}-{fold}",
                        "ticker": ticker,
                        "date": date,
                        "target_exit_date": date + pd.offsets.BDay(20),
                        "fold_id": fold,
                        "label_outperform_T20": label,
                        "stock_return_T20": 0.02 if label else -0.01,
                        "VNINDEX_return_T20": 0.0,
                        "excess_return_T20": 0.02 if label else -0.01,
                        "config": config,
                        "model": "RandomForest",
                        "pred_proba_outperform": 0.8 if label else 0.2,
                        "pred_label": label,
                    }
                )
    return pd.DataFrame(rows)


def test_a_b_c_prediction_rows_are_identical_per_fold():
    pred = prediction_fixture()
    runner.validate_prediction_alignment(
        pred,
        configs=tuple(protocol()["configs"]),
        models=("RandomForest",),
        required_folds=3,
    )
    broken = pred.copy()
    mask = (
        broken["config"].eq("C_technical_semantic")
        & broken["fold_id"].eq(2)
        & broken["ticker"].eq("AAA")
    )
    broken.loc[mask, "row_id"] = "different"
    with pytest.raises(ValueError, match="prediction key mismatch"):
        runner.validate_prediction_alignment(
            broken,
            configs=tuple(protocol()["configs"]),
            models=("RandomForest",),
            required_folds=3,
        )


def test_target_exit_aware_purge_is_preferred_and_valid():
    dates = pd.bdate_range("2024-01-01", periods=48)
    panel = pd.DataFrame(
        {
            "date": dates,
            "target_exit_date": dates + pd.offsets.BDay(5),
        }
    )
    splits = runner.expanding_purged_splits(panel, protocol())
    assert len(splits) == 3
    assert all(meta["purge_method"] == "target_exit_date_before_test_start" for _, _, meta in splits)
    for train_index, _, metadata in splits:
        assert panel.iloc[train_index]["target_exit_date"].max() < metadata["test_start"]


def test_bh_is_applied_only_to_h1_h2_random_forest_balanced_accuracy():
    inference = pd.DataFrame(
        [
            {
                "hypothesis": "H1",
                "role": "primary",
                "model": "RandomForest",
                "metric": "balanced_accuracy",
                "p_value": 0.01,
            },
            {
                "hypothesis": "H2",
                "role": "primary",
                "model": "RandomForest",
                "metric": "balanced_accuracy",
                "p_value": 0.04,
            },
            {
                "hypothesis": "S_kw_sem",
                "role": "supplemental",
                "model": "RandomForest",
                "metric": "balanced_accuracy",
                "p_value": 0.001,
            },
            {
                "hypothesis": "H1",
                "role": "robustness",
                "model": "LogisticRegression",
                "metric": "balanced_accuracy",
                "p_value": 0.001,
            },
        ]
    )
    adjusted = runner.apply_primary_bh(inference, protocol())
    primary = adjusted.iloc[:2]
    assert list(primary["p_value_bh"].round(3)) == [0.02, 0.04]
    assert adjusted.iloc[2:]["p_value_bh"].isna().all()
    assert adjusted.iloc[:2]["primary_family_member"].all()
    assert not adjusted.iloc[2:]["primary_family_member"].any()


def test_canonical_run_id_and_paths_are_rejected():
    with pytest.raises(ValueError, match="frozen canonical"):
        runner.validate_v6_run_id("canonical_150_v7", protocol())
    with pytest.raises(ValueError, match="frozen canonical"):
        builder.validate_v6_run_id("canonical_150_v7", protocol())
    output, report = runner.resolve_run_dirs("v6_primary_test", protocol())
    assert output.parent.name == "v6_primary"
    assert report.parent.name == "v6_primary"
    assert "harmonized" not in output.parts
