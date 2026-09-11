from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


harm = load("build_harmonized_comparison")
targets = load("build_outperform_targets")
runner = load("run_harmonized_comparison")
common = load("common")


def sample() -> pd.DataFrame:
    return pd.DataFrame([{
        "news_id": "n1", "ticker": "AAA", "date": "2024-01-01", "source": "s",
        "title": "lợi nhuận không tăng", "description": "", "full_text": "lợi nhuận không tăng",
        "content_hash": "h1", "sample_bucket": "earnings_business_result",
    }])


def consensus(eligible: bool = True) -> pd.DataFrame:
    return pd.DataFrame([{
        "news_id": "n1", "ticker": "AAA", "article_date": "2024-01-01", "content_hash": "h1",
        "analysis_eligible": eligible, "exclusion_reasons": "[]" if eligible else "['ineligible']",
        "consensus_ticker_relevance": "direct", "consensus_materiality": "high",
        "consensus_direction": "support", "consensus_event_type": "earnings",
        "consensus_materiality_score": 4, "consensus_uncertainty_score": 2,
        "consensus_novelty_score": 3, "high_disagreement_fields": "[]",
    }])


def spec() -> dict:
    return harm.load_harmonized_spec()


def prices(periods: int = 30) -> pd.DataFrame:
    dates = pd.bdate_range("2024-01-01", periods=periods)
    return pd.DataFrame({"ticker": "AAA", "date": dates, "close": range(100, 100 + periods)})


def test_spine_outer_join_rejects_missing_duplicate_hash_and_date_mismatch():
    with pytest.raises(ValueError, match="key mismatch"):
        harm.build_common_article_spine(sample(), pd.DataFrame(columns=consensus().columns), spec(), "r", "pilot")
    with pytest.raises(ValueError, match="duplicate"):
        harm.build_common_article_spine(pd.concat([sample(), sample()]), consensus(), spec(), "r", "pilot")
    with pytest.raises(ValueError, match="missing consensus content hash"):
        harm.build_common_article_spine(sample(), consensus().drop(columns=["content_hash"]), spec(), "r", "pilot")
    other = consensus().assign(content_hash="different")
    with pytest.raises(ValueError, match="hash mismatch"):
        harm.build_common_article_spine(sample(), other, spec(), "r", "pilot")
    wrong_date = consensus().assign(article_date="2024-01-02")
    with pytest.raises(ValueError, match="article date mismatch"):
        harm.build_common_article_spine(sample(), wrong_date, spec(), "r", "pilot")


def test_ineligible_and_unannotated_never_become_semantic_zero():
    spine = harm.build_common_article_spine(sample(), consensus(False), spec(), "r", "pilot")
    assert not spine.loc[0, "analytic_spine_member"]
    assert spine.loc[0, "analytic_spine_reason"] == "consensus_ineligible"
    missing = common.map_articles_to_effective_trading_date(spine, prices())
    daily = harm.aggregate_harmonized_daily_features(missing, prices())
    assert daily["common_article_count"].sum() == 0
    assert not any(col.startswith("semantic_") for col in daily.columns)


def test_shared_effective_date_and_longest_first_keyword_count():
    spine = harm.build_common_article_spine(sample(), consensus(), spec(), "r", "pilot")
    mapped = harm.map_spine_to_effective_dates(spine, prices())
    assert mapped.loc[0, "effective_date"] == pd.Timestamp("2024-01-02")
    keyword = harm.build_keyword_article_features(mapped)
    assert keyword.loc[0, "keyword_negative_count"] == 1
    assert keyword.loc[0, "keyword_positive_count"] == 0


def test_future_article_does_not_change_past_and_ratios_use_rolling_totals():
    spine = harm.build_common_article_spine(sample(), consensus(), spec(), "r", "pilot")
    mapped = harm.map_spine_to_effective_dates(spine, prices())
    base = harm.aggregate_harmonized_daily_features(mapped, prices())
    future_sample = sample().assign(news_id="n2", date="2024-01-10", content_hash="h2", title="lợi nhuận tăng", full_text="lợi nhuận tăng")
    future_consensus = consensus().assign(news_id="n2", article_date="2024-01-10", content_hash="h2", consensus_direction="risk")
    extended_spine = harm.build_common_article_spine(pd.concat([sample(), future_sample]), pd.concat([consensus(), future_consensus]), spec(), "r", "pilot")
    extended = harm.aggregate_harmonized_daily_features(harm.map_spine_to_effective_dates(extended_spine, prices()), prices())
    cols = sorted(set(base.columns) & set(extended.columns))
    pd.testing.assert_frame_equal(base[base.date < "2024-01-10"][cols].reset_index(drop=True), extended[extended.date < "2024-01-10"][cols].reset_index(drop=True))
    row = base[base.date == pd.Timestamp("2024-01-02")].iloc[0]
    assert row["semantic_direction_support_roll_5d"] == 1.0


def test_feature_manifest_membership_is_explicit(tmp_path: Path):
    spine = harm.map_spine_to_effective_dates(harm.build_common_article_spine(sample(), consensus(), spec(), "r", "pilot"), prices())
    daily = harm.aggregate_harmonized_daily_features(spine, prices())
    target = targets.build_harmonized_targets(prices(), pd.DataFrame({"date": pd.bdate_range("2024-01-01", periods=30), "close": range(200, 230)}))
    tech = pd.DataFrame({"ticker": ["AAA"], "quarter_id": ["2023Q4"], "x": [1.0]})
    panel = harm.build_harmonized_panel(daily, target, tech)
    harm.write_harmonized_manifests(tmp_path, spine, daily, panel, spec())
    manifest = pd.read_csv(tmp_path / "harmonized_feature_manifest.csv")
    configs = {name for value in manifest["configs"] for name in json.loads(value)}
    assert {"A_technical", "E_technical_coverage", "B_technical_coverage_keyword", "C_technical_coverage_semantic", "D_technical_coverage_keyword_semantic"} <= configs


def test_harmonized_target_uses_same_twentieth_benchmark_session_and_no_forward_fill():
    benchmark = pd.DataFrame({"date": pd.bdate_range("2024-01-01", periods=25), "close": range(200, 225)})
    stock = pd.DataFrame({"ticker": "AAA", "date": benchmark["date"], "close": range(100, 125)})
    result = targets.build_harmonized_targets(stock, benchmark)
    assert result.loc[0, "target_exit_date"] == benchmark.loc[20, "date"]
    assert result.loc[0, "target_status"] == "ok"
    suspended = stock[stock.date != benchmark.loc[20, "date"]]
    missing = targets.build_harmonized_targets(suspended, benchmark)
    assert missing.loc[0, "target_status"] == "missing_stock_exit"
    assert pd.isna(missing.loc[0, "label_outperform_T20"])
    with pytest.raises(ValueError, match="requires horizon=20"):
        targets.build_harmonized_targets(stock, benchmark, horizon=5)


def test_target_exit_aware_purge_and_train_only_feature_filter():
    frame = pd.DataFrame({
        "date": pd.bdate_range("2024-01-01", periods=40),
        "target_exit_date": pd.bdate_range("2024-01-01", periods=40) + pd.offsets.BDay(5),
        "usable": list(range(40)), "constant": 1,
    })
    splits = runner.target_exit_aware_splits(frame, 3)
    assert len(splits) == 3
    for train_idx, _, metadata in splits:
        assert metadata["train_target_exit_max"] < metadata["test_start"]
        used, audit = runner.available_fold_features(frame.iloc[train_idx], ["usable", "constant", "missing"])
        assert used == ["usable"]
        assert {row["drop_reason"] for row in audit if not row["used"]} == {"constant_or_all_missing", "missing"}


def test_metric_minimum_samples_per_class_is_enforced():
    assert tuple(spec()["metrics"]) == runner.METRICS
    thin = pd.DataFrame({
        "label_outperform_T20": [0, 1],
        "pred_proba_outperform": [0.1, 0.9],
        "excess_return_T20": [-0.1, 0.1],
    })
    assert pd.isna(runner.metric_value(thin, "balanced_accuracy", samples_per_class=2))
    thick = pd.concat([thin, thin], ignore_index=True)
    assert runner.metric_value(thick, "balanced_accuracy", samples_per_class=2) == 1.0
    ranked = pd.DataFrame({
        "label_outperform_T20": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        "pred_proba_outperform": list(reversed([value / 10 for value in range(10)])),
        "excess_return_T20": list(range(10)),
    })
    assert runner.metric_value(ranked, "precision_at_5") == 1.0
    assert runner.metric_value(ranked, "precision_at_10") == 0.5
    assert pd.isna(runner.metric_value(ranked.head(3), "precision_at_5"))
    assert pd.isna(runner.metric_value(ranked.head(9), "precision_at_10"))


def test_fold_local_draws_deterministic_no_wrap_and_metric_direction():
    paired = pd.DataFrame({"fold_id": [1, 1, 1, 2, 2, 2], "date": pd.bdate_range("2024-01-01", periods=6), "improvement_delta": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0]})
    first = runner.fold_local_block_draws(paired, 20, 2, 42)
    second = runner.fold_local_block_draws(paired, 20, 2, 42)
    assert list(first) == list(second)
    assert all(7.0 <= value <= 17.5 for value in first)
    assert runner.bootstrap_draws_estimable(first)
    short_folds = pd.DataFrame({
        "fold_id": [1] * 4 + [2] * 9 + [3] * 12,
        "date": pd.bdate_range("2024-01-01", periods=25),
        "improvement_delta": np.linspace(-0.02, 0.03, 25),
    })
    short_draws = runner.fold_local_block_draws(short_folds, 200, 20, 42)
    assert runner.bootstrap_draws_estimable(short_draws)
    frame = pd.DataFrame({"label_outperform_T20": [0, 1], "pred_proba_outperform": [0.1, 0.9], "excess_return_T20": [-0.1, 0.1]})
    assert runner.metric_value(frame, "brier") < runner.metric_value(frame.assign(pred_proba_outperform=[0.4, 0.6]), "brier")


def test_bh_adjustment_and_topk_not_estimable_status():
    adjusted = runner.bh_adjust(pd.Series([0.01, 0.04, 0.5]))
    assert list(adjusted.round(3)) == [0.03, 0.06, 0.5]
    empty = pd.DataFrame(columns=["config", "model", "fold_id", "date"])
    _, summary = runner.build_matched_topk(empty, "pilot", 0.005, 3)
    assert summary and all(row["status"] == "not_estimable_in_pilot" for row in summary)


def test_topk_inference_requires_all_folds_and_non_degenerate_bootstrap():
    rows = []
    for fold in (1, 2):
        for offset in range(3):
            rows.append({
                "config": "C_minus_B", "model": "RandomForest", "k": 10,
                "fold_id": fold, "date": pd.Timestamp("2024-01-01") + pd.offsets.BDay(fold * 10 + offset),
                "net_return": 0.01 * (fold + offset), "net_excess_return": 0.005 * (fold + offset),
            })
    incomplete = runner.build_topk_inference(pd.DataFrame(rows), spec(), "pilot", True)
    assert set(incomplete["status"]) == {"not_estimable_in_pilot"}
    assert incomplete["bootstrap_ci_low"].isna().all()

    constant = pd.DataFrame([
        {
            "config": "C_minus_B", "model": "RandomForest", "k": 10,
            "fold_id": fold, "date": pd.Timestamp("2024-01-01") + pd.offsets.BDay(fold),
            "net_return": 0.01, "net_excess_return": 0.01,
        }
        for fold in (1, 2, 3)
    ])
    degenerate = runner.build_topk_inference(constant, spec(), "pilot", True)
    assert set(degenerate["status"]) == {"not_estimable_degenerate_bootstrap"}
    assert degenerate["bootstrap_ci_low"].isna().all()
    assert degenerate["p_value"].isna().all()


def test_bc_alignment_rejects_equal_counts_with_different_keys_and_missing_folds():
    rows = []
    for config in ("B_technical_coverage_keyword", "C_technical_coverage_semantic"):
        for model in runner.MODELS:
            for fold in (1, 2, 3):
                rows.append({"config": config, "model": model, "fold_id": fold, "ticker": "AAA", "date": pd.Timestamp(f"2024-0{fold}-01"), "target_exit_date": pd.Timestamp(f"2024-0{fold}-29"), "label_outperform_T20": 1, "stock_return_T20": .1, "VNINDEX_return_T20": .05, "excess_return_T20": .05})
    aligned = pd.DataFrame(rows)
    runner.validate_bc_prediction_alignment(aligned)
    mismatched = aligned.copy()
    idx = mismatched[(mismatched.config == "C_technical_coverage_semantic") & (mismatched.model == "LogisticRegression")].index[0]
    mismatched.loc[idx, "ticker"] = "BBB"
    with pytest.raises(ValueError, match="key mismatch"):
        runner.validate_bc_prediction_alignment(mismatched)
    missing = aligned[~((aligned.config == "C_technical_coverage_semantic") & (aligned.model == "RandomForest") & (aligned.fold_id == 3))]
    with pytest.raises(ValueError, match="3 aligned folds"):
        runner.validate_bc_prediction_alignment(missing)
    near_equal = aligned.copy()
    idx = near_equal[(near_equal.config == "C_technical_coverage_semantic") & (near_equal.model == "RandomForest")].index[0]
    near_equal.loc[idx, "stock_return_T20"] += 1e-12
    with pytest.raises(ValueError, match="target mismatch"):
        runner.validate_bc_prediction_alignment(near_equal)


def test_panel_eligibility_requires_lagged_technical_feature():
    daily = pd.DataFrame({"ticker": ["AAA"], "date": [pd.Timestamp("2024-01-02")], "common_article_count_roll_60d": [1.0]})
    target = pd.DataFrame({"ticker": ["AAA"], "entry_date": [pd.Timestamp("2024-01-02")], "target_status": ["ok"]})
    no_technical = harm.build_harmonized_panel(daily, target, pd.DataFrame())
    assert not no_technical.loc[0, "panel_eligible"]
    tech = pd.DataFrame({"ticker": ["AAA"], "quarter_id": ["2023Q4"], "x": [1.0]})
    with_technical = harm.build_harmonized_panel(daily, target, tech)
    assert with_technical.loc[0, "panel_eligible"]


def test_topk_rejects_divergent_universe_and_fold_boundary():
    rows = []
    for config, tickers in (("B_technical_coverage_keyword", ["A", "B", "C", "D", "E"]), ("C_technical_coverage_semantic", ["A", "B", "C", "D", "X"])):
        for model in runner.MODELS:
            for index, ticker in enumerate(tickers):
                rows.append({"config": config, "model": model, "fold_id": 1, "date": pd.Timestamp("2024-01-02"), "ticker": ticker, "target_exit_date": pd.Timestamp("2024-02-01"), "test_end": pd.Timestamp("2024-01-31"), "pred_proba_outperform": 1 - index / 10, "stock_return_T20": .01, "excess_return_T20": .005})
    topk, summary = runner.build_matched_topk(pd.DataFrame(rows), "pilot", .005, 1)
    assert topk.empty
    assert all(row["status"] == "not_estimable_in_pilot" for row in summary)
    assert all(row["drop_reason"] == "candidate_universe_mismatch" for row in summary)


def test_topk_summary_requires_all_folds_even_with_enough_periods():
    rows = []
    for config in ("B_technical_coverage_keyword", "C_technical_coverage_semantic"):
        for model in runner.MODELS:
            for fold, date in ((1, "2024-01-02"), (2, "2024-03-04")):
                for index, ticker in enumerate(("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")):
                    rows.append({
                        "config": config, "model": model, "fold_id": fold, "date": pd.Timestamp(date),
                        "ticker": ticker, "target_exit_date": pd.Timestamp(date) + pd.offsets.BDay(20),
                        "test_end": pd.Timestamp(date) + pd.offsets.BDay(25),
                        "pred_proba_outperform": 1 - index / 20, "stock_return_T20": .01, "excess_return_T20": .005,
                    })
    _, summary = runner.build_matched_topk(pd.DataFrame(rows), "pilot", .005, 2, required_folds=3)
    assert all(row["status"] == "not_estimable_in_pilot" for row in summary)
    assert all(row["drop_reason"] == "insufficient_fold_coverage" for row in summary)


def test_build_manifest_hashes_exact_sources_and_artifacts(tmp_path: Path):
    protocol = spec()
    sources = {
        "sample": ROOT / protocol["input_paths"]["pilot_sample"],
        "consensus": ROOT / protocol["input_paths"]["pilot_consensus"],
        "prices": ROOT / protocol["input_paths"]["prices"],
        "benchmark": ROOT / protocol["input_paths"]["benchmark"],
        "technical": ROOT / protocol["input_paths"]["technical"],
        "targets": tmp_path / "harmonized_outperform_targets.csv",
        "target_manifest": tmp_path / "harmonized_target_manifest.json",
    }
    sources["targets"].write_text("x\n1\n", encoding="utf-8")
    sources["target_manifest"].write_text("{}\n", encoding="utf-8")
    for name in (
        "harmonized_article_spine.csv", "harmonized_features_daily.csv", "harmonized_feature_manifest.csv",
        "harmonized_row_manifest.csv", "harmonized_coverage_audit.csv", "harmonized_panel.csv",
    ):
        (tmp_path / name).write_text("x\n1\n", encoding="utf-8")
    path = harm.write_harmonized_build_manifest(tmp_path, protocol, "run1", "pilot", sources, True)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["preregistered_input_match"]
    assert {entry["name"] for entry in manifest["sources"]} == set(sources)
    assert len(manifest["artifacts"]) == 6
    loaded, loaded_path = runner.load_and_validate_build_manifest(tmp_path, "run1", "pilot")
    assert loaded == manifest and loaded_path == path
    (tmp_path / "harmonized_panel.csv").write_text("x\n2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        runner.load_and_validate_build_manifest(tmp_path, "run1", "pilot")
    (tmp_path / "harmonized_panel.csv").write_text("x\n1\n", encoding="utf-8")
    manifest["artifacts"] = manifest["artifacts"][:-1]
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="artifact membership mismatch"):
        runner.load_and_validate_build_manifest(tmp_path, "run1", "pilot")
    path = harm.write_harmonized_build_manifest(tmp_path, protocol, "run1", "pilot", sources, True)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["sources"][0]["path"] = str(tmp_path / "wrong_sample.csv")
    (tmp_path / "wrong_sample.csv").write_bytes(sources["sample"].read_bytes())
    manifest["sources"][0]["sha256"] = common.sha256_file(tmp_path / "wrong_sample.csv")
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="source path mismatch"):
        runner.load_and_validate_build_manifest(tmp_path, "run1", "pilot")


def test_pilot_cli_rejects_input_overrides(tmp_path: Path):
    script = SCRIPTS / "build_harmonized_comparison.py"
    for flag in ("--sample", "--consensus", "--targets"):
        result = subprocess.run(
            [sys.executable, str(script), "--mode", "pilot", "--run-id", "override_test", flag, str(tmp_path / "x.csv"), "--validate-only"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "input overrides are forbidden" in result.stderr


def test_claim_modes_never_upgrade_to_full_corpus():
    gates = spec()["claim_gates"]
    assert "only" in gates["pilot"]
    assert "only" in gates["sample500"]
    assert "replication" in gates["full"]


def test_target_cli_rejects_non_preregistered_sources(tmp_path: Path):
    script = SCRIPTS / "build_outperform_targets.py"
    canonical_output = ROOT / "multi_llm_evidence_extraction" / "outputs" / "harmonized" / f"target_cli_{tmp_path.name}" / "harmonized_outperform_targets.csv"
    assert not canonical_output.exists()
    result = subprocess.run(
        [sys.executable, str(script), "--mode", "harmonized", "--output", str(canonical_output), "--prices", str(tmp_path / "other.csv")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "preregistered prices and benchmark" in result.stderr


def test_json_value_rejects_nonfinite_numbers():
    assert runner.json_value(float("nan")) is None
    assert runner.json_value(float("inf")) is None
    assert runner.json_value(0.25) == 0.25


def test_primary_contract_is_fixed_before_run():
    primary = spec()["primary"]
    assert primary == {
        "family": "P1",
        "baseline_config": "B_technical_coverage_keyword",
        "comparison_config": "C_technical_coverage_semantic",
        "model": "RandomForest",
        "metric": "balanced_accuracy",
        "topk": 10,
    }
    assert spec()["canonical_run_id"] == "canonical_150_v7"
    assert spec()["observation_key"] == ["ticker", "date", "target_exit_date"]


def test_canonical_run_id_rejects_fast(tmp_path: Path):
    script = SCRIPTS / "run_harmonized_comparison.py"
    result = subprocess.run(
        [sys.executable, str(script), "--mode", "pilot", "--run-id", "canonical_150_v7", "--fast"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "canonical run_id forbids --fast" in result.stderr


@pytest.mark.parametrize("flag", ("--bootstrap-samples", "--permutation-samples"))
def test_canonical_run_id_rejects_inference_sample_overrides(flag: str):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_harmonized_comparison.py"), "--mode", "pilot", "--run-id", "canonical_150_v7", flag, "100"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "canonical run_id forbids inference sample overrides" in result.stderr


def test_manifest_path_helpers_are_repository_relative():
    absolute = ROOT / "multi_llm_evidence_extraction" / "config" / "harmonized_comparison_v5.json"
    assert runner.repository_relative_path(absolute) == "multi_llm_evidence_extraction/config/harmonized_comparison_v5.json"
    portable = runner.portable_manifest_paths({"sources": [{"path": str(absolute), "sha256": "x"}]})
    assert portable["sources"][0]["path"] == "multi_llm_evidence_extraction/config/harmonized_comparison_v5.json"
    assert not Path(portable["sources"][0]["path"]).is_absolute()


def test_completed_harmonized_run_is_immutable(tmp_path: Path):
    run_id = f"immutable_{tmp_path.name}"
    run_dir = ROOT / "multi_llm_evidence_extraction" / "outputs" / "harmonized" / run_id
    assert not run_dir.exists()
    run_dir.mkdir(parents=True)
    marker = run_dir / "harmonized_comparison_manifest.json"
    marker.write_text("{}", encoding="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "run_harmonized_comparison.py"), "--mode", "pilot", "--run-id", run_id],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "immutable after completion" in result.stderr
    finally:
        marker.unlink(missing_ok=True)
        run_dir.rmdir()
