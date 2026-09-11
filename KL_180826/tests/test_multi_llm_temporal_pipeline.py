from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


features = _load("build_semantic_features")
ml = _load("run_ml_outperform_experiment")


def _prices() -> pd.DataFrame:
    return pd.DataFrame({
        "ticker": ["AAA"] * 7,
        "date": pd.to_datetime(["2024-01-04", "2024-01-05", "2024-01-08", "2024-01-09", "2024-01-10", "2024-01-11", "2024-01-12"]),
    })


def _label(date: str) -> dict:
    return {
        "ticker": "AAA", "article_date": date, "analysis_eligible": True,
        "consensus_ticker_relevance": "direct", "consensus_materiality": "high",
        "consensus_direction": "support", "consensus_event_type": "earnings",
        "consensus_materiality_score": 4, "consensus_uncertainty_score": 2,
        "consensus_novelty_score": 3, "high_disagreement_fields": "[]",
    }


def test_article_maps_to_strict_next_trading_day():
    mapped = features.map_to_trading_date(pd.DataFrame([_label("2024-01-05")]), _prices())
    assert mapped.iloc[0]["date"] == pd.Timestamp("2024-01-08")
    weekend = features.map_to_trading_date(pd.DataFrame([_label("2024-01-06")]), _prices())
    assert weekend.iloc[0]["date"] == pd.Timestamp("2024-01-08")


def test_future_article_does_not_change_past_features():
    base = features.aggregate_daily(pd.DataFrame([_label("2024-01-04")]), _prices())
    extended = features.aggregate_daily(pd.DataFrame([_label("2024-01-04"), _label("2024-01-10")]), _prices())
    cutoff = pd.Timestamp("2024-01-10")
    cols = [col for col in base.columns if col not in {"artifact_schema_version"}]
    pd.testing.assert_frame_equal(
        base[base["date"] < cutoff][cols].reset_index(drop=True),
        extended[extended["date"] < cutoff][cols].reset_index(drop=True),
    )


def test_quarterly_features_are_shifted_to_next_quarter():
    frame = pd.DataFrame({"ticker": ["AAA"], "quarter_id": ["2024Q1"], "return_q": [0.2]})
    shifted = ml.lag_quarterly_features(frame, "tech_lag1q__")
    assert shifted.iloc[0]["quarter_id"] == "2024Q2"
    assert shifted.iloc[0]["tech_lag1q__return_q"] == 0.2


def test_walk_forward_split_has_twenty_day_purge():
    dates = pd.Series(pd.bdate_range("2023-01-02", periods=180))
    splits = ml.expanding_purged_splits(dates, n_splits=3, purge=20)
    assert splits
    for train_idx, test_idx, metadata in splits:
        assert dates.iloc[train_idx].max() < dates.iloc[test_idx].min()
        assert metadata["purge_trading_days"] == 20
        unique = list(dates)
        train_end = unique.index(dates.iloc[train_idx].max())
        test_start = unique.index(dates.iloc[test_idx].min())
        assert test_start - train_end - 1 >= 20


def test_fold_feature_filter_excludes_all_missing_training_columns():
    train = pd.DataFrame({"usable": [1.0, None], "all_missing": [None, None]})
    assert ml.available_fold_features(train, list(train)) == ["usable"]
