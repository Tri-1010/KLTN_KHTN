from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

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


artifacts = load("v6_artifacts")
audit = load("audit_v6_primary_run")
builder = load("build_v6_primary_panel")


def _protocol(root: Path, **overrides):
    paths = {
        "prices": "inputs/prices.csv",
        "benchmark": "inputs/benchmark.csv",
        "technical": "inputs/technical.csv",
        "keyword": "inputs/keyword.csv",
        "semantic_daily": "inputs/semantic.csv",
        "semantic_consensus": "inputs/consensus.csv",
        "news_matched": "inputs/matched.csv",
        "news_processed": "inputs/processed.csv",
    }
    hashes = {}
    for name, relative in paths.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name}\n", encoding="utf-8")
        hashes[name] = artifacts.sha256_file(path)
    base = {
        "protocol_version": "test-v1",
        "claim_level": "v6_full_price_panel_zero_fill_primary",
        "frozen_canonical_run_id": "canonical_150_v7",
        "frozen_v6_run_ids": ["v6_primary_20260909"],
        "input_paths": paths,
        "input_sha256": hashes,
        "primary": {"model": "RandomForest", "metric": "balanced_accuracy"},
        "inference": {"alpha": 0.05},
        "hypothesis_families": {
            "V6_H1_H2": {"hypotheses": [
                {"id": "H1", "baseline_config": "A_technical", "comparison_config": "B_technical_keyword"},
                {"id": "H2", "baseline_config": "A_technical", "comparison_config": "C_technical_semantic"},
            ]}
        },
    }
    base.update(overrides)
    return base


def test_declared_inputs_reject_hash_change_and_path_escape(tmp_path: Path):
    spec = _protocol(tmp_path)
    ledger = artifacts.validate_declared_inputs(spec, tmp_path)
    assert set(ledger) == set(spec["input_paths"])

    (tmp_path / "inputs/prices.csv").write_text("changed\n", encoding="utf-8")
    with pytest.raises(artifacts.V6ArtifactError, match="hash mismatch: prices"):
        artifacts.validate_declared_inputs(spec, tmp_path)

    escaped = _protocol(tmp_path / "second")
    escaped["input_paths"]["prices"] = "../outside.csv"
    with pytest.raises(artifacts.V6ArtifactError, match="escapes workspace root"):
        artifacts.validate_declared_inputs(escaped, tmp_path / "second")


@pytest.mark.parametrize("run_id", ["v6_primary_20260909", "canonical_150_v7"])
def test_frozen_ids_are_rejected(run_id: str, tmp_path: Path):
    with pytest.raises(artifacts.V6ArtifactError, match="frozen"):
        artifacts.validate_v6_run_id(run_id, _protocol(tmp_path))


def test_new_run_refuses_nonempty_or_manifested_directory(tmp_path: Path):
    spec = _protocol(tmp_path)
    output, report = tmp_path / "outputs/run", tmp_path / "reports/run"
    output.mkdir(parents=True)
    report.mkdir(parents=True)
    (output / "unrelated.csv").write_text("x", encoding="utf-8")
    with pytest.raises(artifacts.V6RunImmutableError, match="not empty"):
        artifacts.assert_new_v6_run_available("fresh", spec, output, report)

    for path in output.iterdir():
        path.unlink()
    (output / artifacts.INTENT_MANIFEST).write_text("{}", encoding="utf-8")
    with pytest.raises(artifacts.V6RunImmutableError, match="immutable manifest"):
        artifacts.assert_new_v6_run_available("fresh", spec, output, report)


def test_abort_uncompleted_v6_run_refuses_frozen_or_mismatched_targets(tmp_path: Path):
    spec = _protocol(tmp_path)
    locked_output = tmp_path / "KL_180826/multi_llm_evidence_extraction/outputs/v6_primary/v6_primary_20260909"
    locked_report = tmp_path / "KL_180826/multi_llm_evidence_extraction/reports/v6_primary/v6_primary_20260909"
    locked_output.mkdir(parents=True)
    locked_report.mkdir(parents=True)
    (locked_output / "keep.txt").write_text("locked", encoding="utf-8")
    with pytest.raises(artifacts.V6ArtifactError, match="frozen"):
        artifacts.abort_uncompleted_v6_run(
            locked_output,
            locked_report,
            workspace_root=tmp_path,
            run_id="v6_primary_20260909",
            spec=spec,
        )
    assert (locked_output / "keep.txt").read_text(encoding="utf-8") == "locked"

    output = tmp_path / "KL_180826/multi_llm_evidence_extraction/outputs/v6_primary/fresh"
    report = tmp_path / "KL_180826/multi_llm_evidence_extraction/reports/v6_primary/fresh"
    with pytest.raises(artifacts.V6ArtifactError, match="intent manifest"):
        artifacts.abort_uncompleted_v6_run(output, report, workspace_root=tmp_path, run_id="fresh", spec=spec)


def test_prepare_v6_run_requires_exact_workspace_destination(tmp_path: Path):
    spec = _protocol(tmp_path)
    protocol = tmp_path / "KL_180826/multi_llm_evidence_extraction/config/v6_technical_primary_v1.json"
    protocol.parent.mkdir(parents=True, exist_ok=True)
    protocol.write_text(json.dumps(spec), encoding="utf-8")
    ledger = artifacts.validate_declared_inputs(spec, tmp_path)
    wrong_output, wrong_report = tmp_path / "elsewhere/out", tmp_path / "elsewhere/report"
    with pytest.raises(artifacts.V6ArtifactError, match="must equal"):
        artifacts.prepare_v6_run("fresh", spec, wrong_output, wrong_report, tmp_path, ledger, protocol_path=protocol, horizon=20)

    output = tmp_path / "KL_180826/multi_llm_evidence_extraction/outputs/v6_primary/fresh"
    report = tmp_path / "KL_180826/multi_llm_evidence_extraction/reports/v6_primary/fresh"
    intent = artifacts.prepare_v6_run("fresh", spec, output, report, tmp_path, ledger, protocol_path=protocol, horizon=20)
    assert intent.is_file()
    assert json.loads(intent.read_text(encoding="utf-8"))["inputs"] == ledger
    with pytest.raises(artifacts.V6RunImmutableError):
        artifacts.prepare_v6_run("fresh", spec, output, report, tmp_path, ledger, protocol_path=protocol, horizon=20)


def test_prepare_v6_run_cleans_directories_when_manifest_write_fails(monkeypatch, tmp_path: Path):
    spec = _protocol(tmp_path)
    protocol = tmp_path / "KL_180826/multi_llm_evidence_extraction/config/v6_technical_primary_v1.json"
    protocol.parent.mkdir(parents=True, exist_ok=True)
    protocol.write_text(json.dumps(spec), encoding="utf-8")
    ledger = artifacts.validate_declared_inputs(spec, tmp_path)
    output = tmp_path / "KL_180826/multi_llm_evidence_extraction/outputs/v6_primary/fresh"
    report = tmp_path / "KL_180826/multi_llm_evidence_extraction/reports/v6_primary/fresh"
    monkeypatch.setattr(artifacts, "write_manifest_once", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError, match="boom"):
        artifacts.prepare_v6_run("fresh", spec, output, report, tmp_path, ledger, protocol_path=protocol, horizon=20)
    assert not output.exists()
    assert not report.exists()


def test_claim_gate_never_interprets_estimable_as_support(tmp_path: Path):
    spec = _protocol(tmp_path)
    h2 = {
        "hypothesis": "H2",
        "role": "primary",
        "baseline_config": "A_technical",
        "comparison_config": "C_technical_semantic",
        "model": "RandomForest",
        "metric": "balanced_accuracy",
        "status": "ok",
        "improvement_delta": -0.004248607815284229,
        "bootstrap_ci_low": -0.011200577414621025,
        "bootstrap_ci_high": 0.0018953157694729088,
        "p_value": 0.22997700229977003,
        "p_value_bh": 0.22997700229977003,
    }
    claims = artifacts.primary_claims([h2], spec, audit_pass=True, manifest_pass=True)
    assert claims[0]["claim_state"] == "unsupported"
    assert claims[0]["claim_gate_pass"] is False
    assert claims[0]["claim_gates"]["estimable"] is True


def test_retrospective_attestation_writes_outside_locked_run(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "workspace"
    study = workspace / "KL_180826/multi_llm_evidence_extraction"
    run = study / "outputs/v6_primary/v6_primary_20260909"
    report = study / "reports/v6_primary/v6_primary_20260909"
    config = study / "config"
    config.mkdir(parents=True)
    run.mkdir(parents=True)
    report.mkdir(parents=True)

    protocol = _protocol(workspace)
    protocol_path = config / "v6_technical_primary_v1.json"
    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
    inference = pd.DataFrame([
        {"hypothesis": "H1", "role": "primary", "baseline_config": "A_technical", "comparison_config": "B_technical_keyword", "model": "RandomForest", "metric": "balanced_accuracy", "status": "ok", "improvement_delta": -0.01, "bootstrap_ci_low": -0.02, "bootstrap_ci_high": 0.01, "p_value": .2, "p_value_bh": .2, "n_paired_dates": 10, "n_folds": 3},
        {"hypothesis": "H2", "role": "primary", "baseline_config": "A_technical", "comparison_config": "C_technical_semantic", "model": "RandomForest", "metric": "balanced_accuracy", "status": "ok", "improvement_delta": -0.004248607815284229, "bootstrap_ci_low": -0.011200577414621025, "bootstrap_ci_high": .0018953157694729088, "p_value": .22997700229977003, "p_value_bh": .22997700229977003, "n_paired_dates": 10, "n_folds": 3},
    ])
    inference.to_csv(run / "v6_inference.csv", index=False, encoding="utf-8-sig")
    summary = {"protocol_sha256": artifacts.sha256_file(protocol_path), "n_predictions": 2, "primary": inference[["hypothesis", "status", "improvement_delta", "bootstrap_ci_low", "bootstrap_ci_high", "p_value", "p_value_bh", "n_paired_dates", "n_folds"]].to_dict("records")}
    (run / "v6_run_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (run / "v6_build_summary.json").write_text(json.dumps({"protocol_sha256": artifacts.sha256_file(protocol_path)}), encoding="utf-8")
    pd.DataFrame([{"row_id": "a"}, {"row_id": "b"}]).to_csv(run / "v6_predictions.csv", index=False, encoding="utf-8-sig")
    (report / "v6_primary_report.md").write_text("report\n", encoding="utf-8")

    monkeypatch.setattr(audit, "STUDY_DIR", study)
    monkeypatch.setattr(audit, "SPEC_PATH", protocol_path)
    monkeypatch.setattr(audit, "load_v6_spec", lambda: protocol)
    before = {path.name: artifacts.sha256_file(path) for path in run.iterdir()}
    destination = study / "audits" / "v6_primary_20260909"
    result = audit.audit_locked_v6_run("v6_primary_20260909", workspace_root=workspace, audit_dir=destination)
    after = {path.name: artifacts.sha256_file(path) for path in run.iterdir()}
    assert result["claims"][1]["claim_state"] == "unsupported"
    assert (destination / "v6_retrospective_attestation.json").is_file()
    assert before == after


def test_schema_files_are_json_documents():
    for name in ("v6_release_manifest_schema.json", "v6_subgroup_protocol_schema.json"):
        path = BUNDLE_ROOT / "multi_llm_evidence_extraction/schemas" / name
        assert isinstance(json.loads(path.read_text(encoding="utf-8")), dict)
