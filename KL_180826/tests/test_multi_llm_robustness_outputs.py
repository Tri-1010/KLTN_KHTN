from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
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


consensus = _load("run_consensus_family_sensitivity")
placebo = _load("run_placebo_pre_event_tests")
ml = _load("run_ml_outperform_experiment")
topk = _load("run_topk_simulation")


def test_family_sensitivity_keeps_single_member_known_vendor_and_versions_outputs():
    rows = [
        {"annotator": "a", "direction": "support"},
        {"annotator": "b", "direction": "support"},
        {"annotator": "c", "direction": "risk"},
    ]
    manifests = {
        "a": {"model_vendor": "deepseek", "manifest_status": "ok"},
        "b": {"model_vendor": "deepseek", "manifest_status": "ok"},
        "c": {"model_vendor": "openai", "manifest_status": "ok"},
    }
    labels, statuses, excluded = consensus.collapse_family_votes(rows, "direction", manifests)
    assert labels == {"deepseek": "support", "openai": "risk"}
    assert statuses["openai"] == "single_family_member"
    assert excluded == []
    assert consensus.family_balanced_consensus(labels)["status"] == "disagreement"

    detail = consensus.build_detail_rows(
        [{**row, "news_id": "1"} for row in rows], manifests,
        pd.DataFrame({"news_id": ["1"], "consensus_direction": ["support"]}),
    )
    assert detail
    assert {row["artifact_schema_version"] for row in detail} == {consensus.DETAIL_SCHEMA_VERSION}
    summary = consensus.build_summary_rows(detail, canonical_available=False)
    assert {row["artifact_schema_version"] for row in summary} == {consensus.SUMMARY_SCHEMA_VERSION}
    assert all(row["canonical_status"] == "missing" for row in summary)


def test_placebo_windows_end_strictly_before_event_and_keep_schema():
    dates = pd.bdate_range("2024-01-02", periods=90)
    prices = pd.DataFrame({"ticker": "AAA", "date": dates, "close": np.arange(100.0, 190.0)})
    benchmark = pd.DataFrame({"date": dates, "close": np.arange(200.0, 290.0)})
    events = pd.DataFrame({
        "news_id": ["n1"], "ticker": ["AAA"], "effective_date": [dates[70]],
        "ticker_relevance": ["direct"], "materiality": ["high"],
        "direction": ["support"], "event_type": ["earnings"],
    })
    detail = placebo.build_placebo_outcomes(events, prices, benchmark)
    assert list(detail.columns) == placebo.DETAIL_COLUMNS
    assert set(detail["placebo_window"]) == {"T-20:T-1", "T-60:T-21"}
    assert (pd.to_datetime(detail["pre_window_end_date"]) < pd.to_datetime(detail["effective_date"])).all()
    assert (detail["pre_window_end_offset"] < 0).all()
    assert set(detail["artifact_schema_version"]) == {"placebo_pre_event_outcomes_v1"}
    assert list(placebo.build_stat_tests(detail.iloc[0:0]).columns) == placebo.TEST_COLUMNS


def _prediction_rows() -> pd.DataFrame:
    rows = []
    for date_index, date in enumerate(pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])):
        labels = [0, 1, 1]
        for config, probs in (("A_technical", [0.2, 0.7, 0.8]), ("B_technical_keyword", [0.1, 0.8, 0.9])):
            for ticker_index, (ticker, label, proba) in enumerate(zip(["AAA", "BBB", "CCC"], labels, probs)):
                rows.append({
                    "ticker": ticker, "date": date, "fold_id": 1, "config": config,
                    "model": "M", "label_outperform_T20": label,
                    "pred_proba_outperform": proba + date_index * 0.001,
                    "excess_return_T20": [-0.02, 0.01, 0.03][ticker_index],
                })
    return pd.DataFrame(rows)


def test_ml_paired_daily_and_date_block_bootstrap_are_deterministic():
    paired = ml.build_paired_daily_metrics(_prediction_rows())
    assert list(paired.columns) == ml.PAIRED_DAILY_COLUMNS
    subset = paired[
        paired["baseline_config"].eq("A_technical")
        & paired["comparison_config"].eq("B_technical_keyword")
    ]
    assert not subset.empty
    assert set(subset["pair_status"]) <= {"paired", "metric_undefined"}
    assert (subset["n_baseline_observations"] == subset["n_comparison_observations"]).all()
    first = ml.build_bootstrap_deltas(subset, samples=100, block_dates=2, seed=7)
    second = ml.build_bootstrap_deltas(subset, samples=100, block_dates=2, seed=7)
    pd.testing.assert_frame_equal(first, second)
    assert list(first.columns) == ml.BOOTSTRAP_DELTA_COLUMNS
    ok = first[first["status"].eq("ok")]
    assert not ok.empty
    assert (ok["ci_lower_95"] <= ok["ci_upper_95"]).all()
    assert set(ok["artifact_schema_version"]) == {"outperform_ml_bootstrap_delta_v1"}


def test_topk_random_null_and_cost_sensitivity_have_stable_deterministic_outputs():
    dates = pd.to_datetime(["2024-01-02", "2024-02-01"])
    rows = []
    portfolio_rows = []
    for date_index, date in enumerate(dates):
        for ticker_index, ticker in enumerate(["AAA", "BBB", "CCC", "DDD", "EEE"]):
            rows.append({
                "config": "A", "model": "M", "date": date, "ticker": ticker,
                "stock_return_T20": 0.01 * (ticker_index + 1),
                "excess_return_T20": 0.005 * (ticker_index + 1),
            })
        portfolio_rows.append({
            "config": "A", "model": "M", "top_k": 5, "strategy": "model_topk",
            "entry_date": date, "gross_return": 0.03 + date_index * 0.01,
            "gross_excess_return": 0.02 + date_index * 0.01,
            "net_return": 0.025 + date_index * 0.01,
            "net_excess_return": 0.015 + date_index * 0.01,
            "turnover": 1.0 if date_index == 0 else 0.5,
        })
    pred = pd.DataFrame(rows)
    portfolio = pd.DataFrame(portfolio_rows)
    periods = [(dates[0], dates[0] + pd.Timedelta(days=20)), (dates[1], dates[1] + pd.Timedelta(days=20))]
    null_first = topk.build_random_null_summary(pred, periods, portfolio, draws=20)
    null_second = topk.build_random_null_summary(pred, periods, portfolio, draws=20)
    pd.testing.assert_frame_equal(null_first, null_second)
    assert list(null_first.columns) == topk.RANDOM_NULL_COLUMNS
    assert null_first["one_sided_null_p_value"].between(0, 1).all()
    costs = topk.build_cost_sensitivity_summary(portfolio)
    assert list(costs.columns) == topk.COST_SENSITIVITY_COLUMNS
    assert set(costs["round_trip_cost_rate"]) == set(topk.COST_SENSITIVITY_RATES)
    assert costs.groupby(["config", "model", "top_k"])["cumulative_net_return"].nunique().ge(2).all()


def test_empty_robustness_outputs_keep_declared_headers():
    assert list(ml.build_paired_daily_metrics(pd.DataFrame()).columns) == ml.PAIRED_DAILY_COLUMNS
    assert list(ml.build_bootstrap_deltas(pd.DataFrame()).columns) == ml.BOOTSTRAP_DELTA_COLUMNS
    assert list(topk.build_random_null_summary(pd.DataFrame(), [], pd.DataFrame()).columns) == topk.RANDOM_NULL_COLUMNS
    assert list(topk.build_cost_sensitivity_summary(pd.DataFrame()).columns) == topk.COST_SENSITIVITY_COLUMNS
