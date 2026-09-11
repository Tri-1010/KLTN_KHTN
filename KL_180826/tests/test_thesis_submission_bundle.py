from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "thesis_submission"


def load_script(name: str):
    path = BUNDLE / "reproduction" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


builder = load_script("build_submission")
validator = load_script("validate_submission")


def test_submission_source_documents_exist_and_have_no_placeholders():
    for relative in (
        "README.md", "proposal/de_cuong.md", "thesis/luan_van.md",
        "governance/claim_evidence_matrix.md", "governance/data_dictionary.md",
        "governance/limitations.md", "governance/legacy_artifact_registry.md",
        "reproduction/README.md",
    ):
        path = BUNDLE / relative
        assert path.exists() and path.stat().st_size > 100
        assert not validator.PLACEHOLDER.search(path.read_text(encoding="utf-8"))


def test_primary_table_uses_structured_summary_values():
    summary = {
        "run_id": "canonical_150_v7",
        "primary": {
            "baseline_config": "B_technical_coverage_keyword",
            "comparison_config": "C_technical_coverage_semantic",
            "model": "RandomForest", "metric": "balanced_accuracy",
            "improvement_delta": 0.01, "bootstrap_ci_low": -0.01,
            "bootstrap_ci_high": 0.03, "p_value_bh": 0.2,
            "n_folds": 3, "gate_pass": False,
        },
    }
    table = builder.build_primary_table(summary)
    assert table.loc[0, "Delta"] == 0.01
    assert table.loc[0, "Gate"] == False  # noqa: E712
    assert "0.01" in builder.markdown_table(table)


def test_validator_primary_contract_matches_protocol():
    protocol = json.loads((ROOT / "multi_llm_evidence_extraction" / "config" / "harmonized_comparison_v5.json").read_text(encoding="utf-8"))
    expected = {
        "family": "P1",
        "baseline_config": "B_technical_coverage_keyword",
        "comparison_config": "C_technical_coverage_semantic",
        "model": "RandomForest",
        "metric": "balanced_accuracy",
        "topk": 10,
    }
    assert protocol["primary"] == expected
    validator_source = (BUNDLE / "reproduction" / "validate_submission.py").read_text(encoding="utf-8")
    for key, value in expected.items():
        assert repr(key) in validator_source or f'"{key}"' in validator_source
        assert repr(value) in validator_source or f'"{value}"' in validator_source


def test_build_submission_rejects_wrong_canonical_id(monkeypatch):
    monkeypatch.setattr("sys.argv", ["build_submission.py", "--run-id", "canonical_150_v1"])
    try:
        builder.main()
    except (ValueError, FileNotFoundError) as exc:
        assert "canonical_150_v7" in str(exc) or "completed canonical" in str(exc)
    else:
        raise AssertionError("wrong canonical ID must fail closed")


def test_submission_requires_generated_figure_artifacts():
    for relative in (
        "reproduction/generate_figures.py",
        "artifacts/figures/primary_delta_ci.png",
        "artifacts/figures/canonical_attrition.png",
        "artifacts/figure_data/primary_delta_ci.csv",
        "artifacts/figure_data/canonical_attrition.csv",
    ):
        assert relative in validator.MANDATORY
        path = BUNDLE / relative
        assert path.exists() and path.stat().st_size > 0


def test_submission_requires_claim_evidence_artifacts():
    for relative in (
        "canonical_results/manifests/harmonized_article_spine.csv",
        "canonical_results/manifests/harmonized_row_manifest.csv",
        "canonical_results/manifests/harmonized_fold_manifest.csv",
        "canonical_results/manifests/harmonized_fold_feature_manifest.csv",
        "canonical_results/tables/harmonized_paired_daily_deltas.csv",
    ):
        assert relative in validator.MANDATORY


def test_build_submission_runs_figure_generation():
    source = (BUNDLE / "reproduction" / "build_submission.py").read_text(encoding="utf-8")
    assert '"generate_figures.py"' in source
    assert "subprocess.run" in source
    assert "check=True" in source


def test_claim_evidence_references_resolve():
    matrix = (BUNDLE / "governance" / "claim_evidence_matrix.md").read_text(encoding="utf-8")
    for relative in validator.EVIDENCE_PATH.findall(matrix):
        assert (BUNDLE / relative).exists(), relative


def test_checksums_exclude_python_cache_files():
    checksums = (BUNDLE / "governance" / "checksums.sha256").read_text(encoding="utf-8")
    assert "__pycache__" not in checksums
    assert ".pyc" not in checksums
