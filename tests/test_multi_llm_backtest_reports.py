from __future__ import annotations

import importlib.util
import math
import os
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


backtest = _load("run_topk_simulation")
claim_writer = _load("write_claim_evidence_table")
final_writer = _load("write_final_reports")
lineage = _load("build_lineage_manifest")


def test_turnover_for_unchanged_and_disjoint_holdings():
    same = {"AAA": 0.5, "BBB": 0.5}
    assert backtest.portfolio_turnover(same, same) == 0
    assert backtest.portfolio_turnover({"AAA": 1.0}, {"BBB": 1.0}) == 1.0
    assert backtest.portfolio_turnover({}, {"AAA": 1.0}) == 1.0


def test_rebalance_windows_do_not_overlap():
    calendar = list(pd.bdate_range("2024-01-02", periods=70))
    periods = backtest.non_overlapping_rebalance_dates(calendar, calendar, horizon=20)
    assert periods
    assert all(periods[index][0] >= periods[index - 1][1] for index in range(1, len(periods)))


def test_summary_annualizes_twenty_day_sharpe():
    frame = pd.DataFrame({
        "config": ["A"] * 3, "model": ["M"] * 3, "top_k": [5] * 3, "strategy": ["model_topk"] * 3,
        "entry_date": pd.to_datetime(["2024-01-02", "2024-02-01", "2024-03-01"]),
        "net_return": [0.01, 0.02, 0.03], "net_excess_return": [0.0, 0.01, 0.02], "turnover": [1.0, 0.5, 0.5],
    })
    row = backtest.summarize(frame).iloc[0]
    assert row["annualization_factor"] == math.sqrt(252 / 20)
    assert row["holding_period_days"] == 20


def test_event_claim_gate_requires_fdr_and_positive_ci():
    frame = pd.DataFrame({
        "p_value_bh": [0.01, 0.01, 0.20],
        "diff_ci_low": [0.1, -0.2, 0.3],
        "correction_method": ["Benjamini-Hochberg"] * 3,
        "reject_fdr_05": [True, True, False],
        "robust_positive_effect": [True, False, False],
        "artifact_schema_version": ["event_window_tests_v3"] * 3,
    })
    summary = claim_writer.event_test_summary(frame)
    assert summary["fdr_significant"] == 2
    assert summary["positive_ci"] == 2
    assert summary["robust_results"] == 1
    assert summary["claim_gate_pass"]
    assert summary["reported_flag_mismatches"] == 0
    assert summary["robust_flag_mismatches"] == 0

    frame.loc[0, "robust_positive_effect"] = False
    fallback = claim_writer.event_test_summary(frame)
    assert fallback["robust_flag_mismatches"] == 1
    assert fallback["robust_results"] == 1
    assert fallback["claim_gate_pass"]

    split_gate = pd.DataFrame({
        "p_value_bh": [0.01, 0.20, 0.01],
        "diff_ci_low": [-0.1, 0.3, 0.4],
        "correction_method": ["Benjamini-Hochberg", "Benjamini-Hochberg", "other"],
    })
    rejected = claim_writer.event_test_summary(split_gate)
    assert rejected["fdr_significant"] == 1
    assert rejected["positive_ci"] == 2
    assert rejected["robust_results"] == 0
    assert not rejected["claim_gate_pass"]


def test_ml_fold_summary_verifies_purged_oos_metadata():
    frame = pd.DataFrame({
        "date": ["2024-02-01", "2024-02-02"], "fold_id": [1, 1],
        "train_start": ["2023-01-02"] * 2, "train_end": ["2024-01-01"] * 2,
        "test_start": ["2024-02-01"] * 2, "test_end": ["2024-03-01"] * 2,
        "purge_trading_days": [20, 20], "config": ["A", "A"], "model": ["M", "M"],
        "artifact_schema_version": ["outperform_ml_predictions_v2"] * 2,
    })
    summary = claim_writer.ml_fold_summary(frame)
    assert summary["fold_count"] == 1
    assert summary["purged_oos_verified"]
    assert summary["status"] == "verified_from_fold_metadata"

    insufficient_purge = frame.copy()
    insufficient_purge["train_end"] = "2024-01-31"
    insufficient_purge["test_start"] = "2024-02-01"
    assert not claim_writer.ml_fold_summary(insufficient_purge)["purged_oos_verified"]

    missing_fold = frame.copy()
    missing_fold["fold_id"] = None
    missing_summary = claim_writer.ml_fold_summary(missing_fold)
    assert missing_summary["fold_count"] == 0
    assert not missing_summary["purged_oos_verified"]


def test_topk_summary_checks_nonoverlap_and_turnover_cost():
    frame = pd.DataFrame({
        "config": ["A", "A"], "model": ["M", "M"], "top_k": [5, 5], "strategy": ["model_topk"] * 2,
        "entry_date": ["2024-01-02", "2024-02-01"], "exit_date": ["2024-02-01", "2024-03-01"],
        "gross_return": [0.02, 0.03], "net_return": [0.015, 0.0275],
        "gross_excess_return": [0.01, 0.02], "net_excess_return": [0.005, 0.0175],
        "turnover": [1.0, 0.5], "transaction_cost": [0.005, 0.0025], "round_trip_cost_rate": [0.005, 0.005],
        "holding_period_days": [20, 20], "artifact_schema_version": ["topk_nonoverlap_v2"] * 2,
    })
    summary = claim_writer.topk_summary(frame)
    assert summary["non_overlapping"]
    assert summary["turnover_cost_verified"]
    assert summary["net_return_verified"]
    assert summary["status"] == "verified_nonoverlap_turnover_cost"

    overlap = frame.copy()
    overlap.loc[1, "entry_date"] = "2024-01-20"
    assert not claim_writer.topk_summary(overlap)["non_overlapping"]

    bad_cost = frame.copy()
    bad_cost.loc[0, "transaction_cost"] = 0.001
    assert not claim_writer.topk_summary(bad_cost)["turnover_cost_verified"]

    bad_net = frame.copy()
    bad_net.loc[0, "net_return"] = 0.02
    assert not claim_writer.topk_summary(bad_net)["net_return_verified"]

    reversed_period = frame.iloc[[0]].copy()
    reversed_period.loc[reversed_period.index[0], "entry_date"] = "2024-03-01"
    reversed_period.loc[reversed_period.index[0], "exit_date"] = "2024-02-01"
    assert not claim_writer.topk_summary(reversed_period)["non_overlapping"]

    negative_cost = frame.copy()
    negative_cost.loc[0, "turnover"] = -1.0
    negative_cost.loc[0, "transaction_cost"] = -0.005
    assert not claim_writer.topk_summary(negative_cost)["turnover_cost_verified"]


def test_artifact_metadata_reports_hash_and_freshness(tmp_path):
    upstream = tmp_path / "upstream.csv"
    artifact = tmp_path / "artifact.csv"
    upstream.write_text("value\n1\n", encoding="utf-8")
    artifact.write_text("value\n2\n", encoding="utf-8")
    metadata = claim_writer.artifact_metadata(artifact, [upstream])
    assert metadata["sha256"] == claim_writer.sha256_file(artifact)
    assert metadata["freshness"] == "fresh"
    future = artifact.stat().st_mtime + 10
    os.utime(upstream, (future, future))
    assert claim_writer.artifact_metadata(artifact, [upstream])["freshness"] == "stale"


def test_final_report_targets_canonical_thesis_report():
    assert final_writer.MAIN.name == "ket_qua_luan_van_semantic_news_materiality.md"


def test_annotation_agreement_summary_tracks_errors_and_intersection():
    rows = {
        "a": [
            {"status": "ok", "news_id": "1", "ticker": "AAA", "direction": "support"},
            {"status": "ok", "news_id": "1", "ticker": "BBB", "direction": "risk"},
            {"status": "ok", "news_id": "2", "ticker": "AAA", "direction": ""},
            {"status": "error", "news_id": "3"},
        ],
        "b": [
            {"status": "ok", "news_id": "1", "ticker": "AAA", "direction": "support"},
            {"status": "ok", "news_id": "1", "ticker": "BBB", "direction": "support"},
            {"status": "ok", "news_id": "2", "ticker": "AAA", "direction": "risk"},
        ],
    }
    summary = claim_writer.annotation_agreement_summary(rows)
    metric = next(row for row in summary["pairwise"] if row["field"] == "direction")
    assert summary["available"]
    assert summary["valid_counts"] == {"a": 3, "b": 3}
    assert summary["error_counts"] == {"a": 1, "b": 0}
    assert metric["agree"] == 1
    assert metric["total"] == 2
    assert metric["agreement"] == 0.5
    assert metric["cohen_kappa"] == 0.0

    degenerate = claim_writer.annotation_agreement_summary({
        "a": [{"status": "ok", "news_id": "1", "ticker": "AAA", "direction": "support"}],
        "b": [{"status": "ok", "news_id": "1", "ticker": "AAA", "direction": "support"}],
    })
    degenerate_metric = next(row for row in degenerate["pairwise"] if row["field"] == "direction")
    assert degenerate_metric["cohen_kappa"] is None


def test_manual_sanity_summary_normalizes_boolean_values():
    frame = pd.DataFrame({
        "human_relevance_ok": ["ok", "sai", ""],
        "human_materiality_ok": ["đúng", "no", None],
    })
    summary = claim_writer.manual_sanity_summary(frame)
    assert summary["rows"] == 3
    assert summary["filled_rows"] == 2
    assert summary["checks"]["human_relevance_ok"]["ok"] == 1
    assert summary["checks"]["human_relevance_ok"]["not_ok"] == 1
    assert summary["checks"]["human_materiality_ok"]["ok"] == 1
    assert summary["checks"]["human_materiality_ok"]["not_ok"] == 1
    assert summary["status"] == "partial"
    assert "human_direction_ok" in summary["missing_columns"]


def test_rule_comparison_summary_filters_ineligible_and_unclear():
    rule = pd.DataFrame({
        "news_id": ["1", "2", "3", "4"],
        "ticker": ["AAA"] * 4,
        "rule_direction": ["support", "risk", "support", "risk"],
    })
    consensus = pd.DataFrame({
        "news_id": ["1", "2", "3", "4"],
        "ticker": ["AAA"] * 4,
        "analysis_eligible": [True, True, False, True],
        "consensus_direction": ["support", "risk", "support", "unclear"],
    })
    summary = claim_writer.rule_comparison_summary(rule, consensus)
    assert summary["compared_rows"] == 3
    assert summary["metrics"][0]["n"] == 2
    assert summary["metrics"][0]["accuracy"] == 1.0

    missing_eligibility = claim_writer.rule_comparison_summary(rule, consensus.drop(columns=["analysis_eligible"]))
    assert not missing_eligibility["available"]
    assert missing_eligibility["compared_rows"] == 0


def test_report_renderers_use_dynamic_snapshot_without_writing(tmp_path):
    output_dir = tmp_path / "outputs"
    data_dir = tmp_path / "data"
    output_dir.mkdir()
    data_dir.mkdir()
    pd.DataFrame({
        "news_id": ["1", "2"], "ticker": ["AAA", "AAA"],
        "consensus_method": ["unanimous", "majority_vote"], "analysis_eligible": [True, False],
        "consensus_direction": ["support", "risk"],
        "artifact_schema_version": ["pseudo_label_consensus_v2"] * 2,
    }).to_csv(output_dir / "pseudo_labels_consensus.csv", index=False)
    pd.DataFrame({
        "news_id": ["1", "2"], "ticker": ["AAA", "AAA"],
        "rule_direction": ["support", "support"],
    }).to_csv(output_dir / "rule_labels.csv", index=False)
    pd.DataFrame({
        "human_relevance_ok": ["ok", "sai"],
        "human_materiality_ok": ["yes", "no"],
    }).to_csv(data_dir / "manual_sanity_check_sample.csv", index=False)
    for annotator, direction in (("a", "support"), ("b", "support")):
        (output_dir / f"labels_annotator_{annotator}.jsonl").write_text(
            '{"status":"ok","news_id":"1","direction":"' + direction + '"}\n',
            encoding="utf-8",
        )
    snapshot = claim_writer.build_artifact_snapshot(output_dir, data_dir)
    claim = claim_writer.render_claim_evidence_table(snapshot)
    report = final_writer.render_main_report(snapshot)
    assert "unanimous=1" in claim
    assert "eligible=1/2" in claim
    assert "Consensus rows=2" in report
    assert "## Annotation agreement" in report
    assert "## Manual sanity check" in report
    assert "## Keyword/rule baseline versus semantic pseudo-labels" in report
    assert "## Semantic signal audit and corrected event-window tests" in report
    assert "## Claim-vs-evidence summary" in report
    assert "## Conclusion" in report
    assert "macro-F1" in report
    assert "Top-K" in report
    assert "RQ–hypothesis–evidence matrix" in report
    assert "two model families" in report
    assert "retrospective" in report
    assert "joint-positive fraction" in claim
    assert not list(tmp_path.rglob("*.md"))


def test_optional_robustness_readers_preserve_missing_fallbacks(tmp_path):
    output_dir = tmp_path / "outputs"
    data_dir = tmp_path / "data"
    output_dir.mkdir()
    data_dir.mkdir()
    snapshot = claim_writer.build_artifact_snapshot(output_dir, data_dir)
    assert not any(snapshot["robustness"]["available"].values())
    assert snapshot["robustness"]["topk_null_significant"] is None
    assert snapshot["artifacts"]["family_sensitivity"]["freshness"] == "missing"
    report = final_writer.render_main_report(snapshot)
    assert "Missing optional artifacts remain unavailable" in report


def test_optional_robustness_summary_reports_ml_deltas_and_topk_null():
    summary = claim_writer.optional_robustness_summary({
        "placebo": pd.DataFrame(),
        "ml_paired": pd.DataFrame({
            "metric": ["auc", "auc"], "baseline_value": [0.49, 0.51],
            "comparison_value": [0.50, 0.50], "delta": [0.01, -0.01],
        }),
        "ml_bootstrap": pd.DataFrame({"delta": [0.0]}),
        "topk_null": pd.DataFrame({"one_sided_null_p_value": [0.04, 0.40]}),
        "topk_cost": pd.DataFrame({"round_trip_cost_rate": [0.0, 0.005]}),
        "family_sensitivity": pd.DataFrame(),
    })
    assert summary["ml_metrics"]["auc"]["baseline_mean"] == 0.5
    assert summary["ml_metrics"]["auc"]["delta_mean"] == 0.0
    assert summary["topk_null_significant"] == 1
    assert summary["topk_cost_rates"] == [0.0, 0.005]


def test_lineage_manifest_records_hash_and_missing_optional(tmp_path):
    available = tmp_path / "available.csv"
    missing = tmp_path / "missing.csv"
    available.write_text("value\n1\n", encoding="utf-8")
    manifest = lineage.build_manifest([available, missing], tmp_path)
    assert manifest["manifest_schema_version"] == "semantic_report_lineage_v1"
    assert manifest["available_count"] == 1
    assert manifest["missing_optional_count"] == 1
    assert manifest["artifacts"][0]["sha256"] == lineage.sha256_file(available)
    assert manifest["artifacts"][1]["status"] == "missing_optional"
