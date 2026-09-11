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


workspace_builder = load("prepare_v6_confirmation_workspace")
preflight = load("collect_v6_confirmation_inputs")
freezer = load("freeze_v6_confirmation_inputs")
confirmation_runner = load("run_v6_h2_confirmation")
provider = __import__("scripts.llm_provider", fromlist=["llm_provider"])


def _sha256(path: Path) -> str:
    return freezer.sha256_file(path)


def _predictions() -> pd.DataFrame:
    rows = []
    for day, date in enumerate(pd.bdate_range("2026-06-02", periods=3)):
        for ticker, label in (("AAA", 1), ("BBB", 0), ("CCC", 1), ("DDD", 0)):
            probability = 0.85 + day * 0.03 if ticker == "AAA" else 0.15 - day * 0.03 if ticker == "BBB" else 0.5
            for config, value in (("A_technical", 0.5), ("C_technical_semantic", probability)):
                rows.append({
                    "row_id": f"{ticker}-{day}", "ticker": ticker, "date": date, "fold_id": 1,
                    "target_exit_date": date + pd.offsets.BDay(20), "label_outperform_T20": label,
                    "config": config, "model": "RandomForest", "pred_proba_outperform": value,
                })
    return pd.DataFrame(rows)


def _panel() -> pd.DataFrame:
    rows = []
    for day, date in enumerate(pd.bdate_range("2026-06-02", periods=3)):
        for ticker, exposed in (("AAA", True), ("BBB", True), ("CCC", False), ("DDD", False)):
            rows.append({
                "row_id": f"{ticker}-{day}", "ticker": ticker, "date": date,
                "sem_daily__high_materiality_count": int(exposed and day == 0),
                "sem_daily__medium_materiality_count": 0,
                "semantic_source_status": "valid_source_event" if exposed else "no_valid_news",
            })
    return pd.DataFrame(rows)


def _write_protocol(workspace: Path) -> Path:
    path = workspace / "KL_180826/multi_llm_evidence_extraction/config/v6_h2_confirmation_20260602_20260810_v1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    value = json.loads((BUNDLE_ROOT / "multi_llm_evidence_extraction/config/v6_h2_confirmation_20260602_20260810_v1.json").read_text(encoding="utf-8"))
    value["inference"] = value["inference"] | {"bootstrap_samples": 20, "permutation_samples": 20, "block_dates": 1}
    value["gates"] = value["gates"] | {"required_folds": 1, "min_paired_dates": 2, "min_observations_per_group": 2}
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _write_consensus(workspace: Path) -> str:
    inputs = workspace / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    expected = inputs / "annotation_expected_sample.csv"
    expected.write_text("news_id,ticker\nn1,AAA\n", encoding="utf-8")
    labels = []
    for annotator in ("a", "b", "c"):
        label = inputs / f"labels_annotator_{annotator}.jsonl"
        label.write_text(json.dumps({"news_id": "n1", "ticker": "AAA", "annotator": annotator, "status": "ok", "terminal": True}) + "\n", encoding="utf-8")
        labels.append(label)
    consensus_csv = inputs / "pseudo_labels_consensus.csv"
    consensus_csv.write_text("news_id,ticker\nn1,AAA\n", encoding="utf-8")
    path = inputs / "annotation_consensus.json"
    path.write_text(
        json.dumps(
            {
                "artifact_schema_version": "v6_confirmation_annotation_consensus_v1",
                "status": "completed",
                "strict_expansion": True,
                "annotators": ["a", "b", "c"],
                "expected_sample": {"path": expected.relative_to(workspace).as_posix(), "sha256": _sha256(expected)},
                "inputs": [
                    {"path": label.relative_to(workspace).as_posix(), "sha256": _sha256(label)}
                    for label in labels
                ],
                "consensus_csv": {"path": consensus_csv.relative_to(workspace).as_posix(), "sha256": _sha256(consensus_csv)},
            }
        ),
        encoding="utf-8",
    )
    return path.relative_to(workspace).as_posix()


def _write_preflight(workspace: Path) -> None:
    protocol = workspace / "KL_180826/multi_llm_evidence_extraction/config/v6_h2_confirmation_20260602_20260810_v1.json"
    # The fixture has exactly three confirmation entry dates plus their twenty
    # future benchmark sessions, so the runner can reconcile frozen T+20 labels.
    dates = pd.bdate_range("2026-06-02", "2026-09-08")
    prices = pd.DataFrame(
        [
            {"ticker": ticker, "date": date, "close": (100 + index if label else 100 - index)}
            for ticker, label in (("AAA", 1), ("BBB", 0), ("CCC", 1), ("DDD", 0))
            for index, date in enumerate(dates)
        ]
    )
    benchmark = pd.DataFrame({"date": dates, "close": [100 + index / 2 for index in range(len(dates))]})
    source_frames = {
        "KL_180826/data/prices/all_vn30_prices.csv": prices,
        "KL_180826/data/prices_extended/VNINDEX.csv": benchmark,
        "KL_180826/data/news/matched/all_news_matched.csv": pd.DataFrame({"date": ["2026-06-02"], "url": ["u"], "ticker": ["AAA"]}),
        "KL_180826/data/news/processed/all_news_processed.csv": pd.DataFrame({"date": ["2026-06-02"], "url": ["u"], "ticker": ["AAA"], "extraction_status": ["ok"]}),
    }
    for relative, frame in source_frames.items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    path = workspace / "preflight" / "v6_confirmation_preflight.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "status": "ready",
        "protocol": {"sha256": _sha256(protocol)},
        "input_hashes": [{"path": item, "sha256": _sha256(workspace / item)} for item in source_frames],
    }), encoding="utf-8")


def _runner_workspace(tmp_path: Path) -> tuple[Path, str]:
    workspace = tmp_path / "runner-workspace"
    workspace.mkdir()
    _write_protocol(workspace)
    inputs = workspace / "inputs"
    inputs.mkdir()
    _predictions().to_csv(inputs / "predictions.csv", index=False, encoding="utf-8-sig")
    _panel().to_csv(inputs / "panel.csv", index=False, encoding="utf-8-sig")
    (inputs / "robustness.json").write_text(json.dumps({"status": "ok", "improvement_delta": -0.1, "bootstrap_ci_low": -0.01, "p_value_bh": 0.4}), encoding="utf-8")
    _write_preflight(workspace)
    freezer.freeze_confirmation_inputs(
        workspace,
        "runner-inputs",
        predictions_relative="inputs/predictions.csv",
        panel_relative="inputs/panel.csv",
        robustness_relative="inputs/robustness.json",
        annotation_consensus_relative=_write_consensus(workspace),
    )
    manifest = workspace / "KL_180826/multi_llm_evidence_extraction/outputs/v6_h2_confirmation_inputs/runner-inputs/v6_confirmation_input_manifest.json"
    return workspace, manifest.relative_to(workspace).as_posix()


def _source_root(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    for relative in workspace_builder.COPY_DIRECTORIES:
        directory = root / relative
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "marker.py").write_text("# source\n", encoding="utf-8")
    for relative in workspace_builder.COPY_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("dependency==1\n", encoding="utf-8")
    prices = pd.DataFrame({"ticker": ["AAA"] * 25, "date": pd.bdate_range("2026-06-02", periods=25), "open": 1.0, "high": 1.0, "low": 1.0, "close": range(1, 26), "volume": 1})
    benchmark = pd.DataFrame({"date": pd.bdate_range("2026-06-02", periods=25), "open": 1.0, "high": 1.0, "low": 1.0, "close": range(1, 26), "volume": 1})
    data = {
        "KL_180826/data/prices/all_vn30_prices.csv": prices,
        "KL_180826/data/prices_extended/VNINDEX.csv": benchmark,
        "KL_180826/data/features/technical_features.csv": pd.DataFrame({"ticker": ["AAA"], "quarter_id": ["2026Q2"]}),
        "data/features/keyword_features.csv": pd.DataFrame({"ticker": ["AAA"], "quarter_id": ["2026Q2"]}),
        "multi_llm_evidence_extraction/outputs/semantic_features_daily.csv": pd.DataFrame({"ticker": ["AAA"], "date": ["2026-06-02"]}),
        "KL_180826/multi_llm_evidence_extraction/outputs/pseudo_labels_consensus.csv": pd.DataFrame({"ticker": ["AAA"], "article_date": ["2026-06-02"]}),
        "KL_180826/data/news/matched/all_news_matched.csv": pd.DataFrame([{ "date": "2026-06-02", "url": "https://example.test/a", "ticker": "AAA", "match_confidence": "exact"}]),
        "KL_180826/data/news/processed/all_news_processed.csv": pd.DataFrame([{ "date": "2026-06-02", "url": "https://example.test/a", "ticker": "AAA", "extraction_status": "ok"}]),
    }
    for relative, frame in data.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    return root


def test_workspace_refuses_bundle_or_nonempty_target(tmp_path: Path):
    source = _source_root(tmp_path)
    with pytest.raises(Exception, match="outside KL_180826 bundle"):
        workspace_builder.prepare_confirmation_workspace(source / "KL_180826", source)
    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "keep.txt").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="empty"):
        workspace_builder.prepare_confirmation_workspace(nonempty, source)


def test_workspace_copies_and_hashes_snapshot_without_mutating_source(tmp_path: Path):
    source = _source_root(tmp_path)
    target = tmp_path / "confirmation-workspace"
    original = (source / "KL_180826/data/prices/all_vn30_prices.csv").read_bytes()
    result = workspace_builder.prepare_confirmation_workspace(target, source)
    assert result["status"] == "prepared"
    assert result["source_root"] == "not_persisted"
    assert str(source) not in json.dumps(result)
    assert (target / "KL_180826/data/prices/all_vn30_prices.csv").read_bytes() == original
    assert (source / "KL_180826/data/prices/all_vn30_prices.csv").read_bytes() == original


def test_preflight_blocks_incomplete_t20_and_never_persists_secret(tmp_path: Path, monkeypatch):
    source = _source_root(tmp_path)
    target = tmp_path / "confirmation-workspace"
    workspace_builder.prepare_confirmation_workspace(target, source)
    _write_protocol(target)
    monkeypatch.setenv("URL_LOCAL", "http://localhost:20128/v1")
    monkeypatch.setenv("API_LOCAL", "do-not-persist")
    result = preflight.preflight_confirmation_workspace(target)
    assert result["status"] == "blocked"
    assert "incomplete_t20_price_or_benchmark_coverage" in result["blockers"]
    assert "do-not-persist" not in json.dumps(result)


def test_preflight_enforces_article_and_call_caps():
    protocol = json.loads((BUNDLE_ROOT / "multi_llm_evidence_extraction/config/v6_h2_confirmation_20260602_20260810_v1.json").read_text(encoding="utf-8"))
    protocol["gates"] = protocol["gates"] | {"max_eligible_articles": 1, "max_annotation_calls": 3}
    matched = pd.DataFrame([
        {"date": "2026-06-02", "url": "https://example.test/a", "ticker": "AAA", "match_confidence": "exact"},
        {"date": "2026-06-03", "url": "https://example.test/b", "ticker": "AAA", "match_confidence": "exact"},
    ])
    result = preflight._eligible_article_count(matched, matched.assign(extraction_status="ok"), protocol)
    assert result["eligible_articles"] == 2
    assert not result["within_article_cap"]
    assert not result["within_call_cap"]


def test_local_router_remote_url_is_rejected(monkeypatch):
    monkeypatch.setenv("URL_LOCAL", "http://remote.example.test/v1")
    monkeypatch.setenv("API_LOCAL", "secret")
    with pytest.raises(provider.ProviderConfigError, match="localhost"):
        provider.make_llm_client("local_router")


def test_freezer_requires_root_contained_strict_annotation_consensus(tmp_path: Path):
    workspace, _ = _runner_workspace(tmp_path)
    with pytest.raises(FileExistsError):
        freezer.freeze_confirmation_inputs(
            workspace, "runner-inputs", predictions_relative="inputs/predictions.csv", panel_relative="inputs/panel.csv",
            robustness_relative="inputs/robustness.json", annotation_consensus_relative="inputs/annotation_consensus.json",
        )
    with pytest.raises(Exception, match="annotation consensus"):
        freezer.freeze_confirmation_inputs(
            workspace, "missing-consensus", predictions_relative="inputs/predictions.csv", panel_relative="inputs/panel.csv",
            robustness_relative="inputs/robustness.json", annotation_consensus_relative="inputs/missing-consensus.json",
        )


def test_freezer_rejects_minimal_or_tampered_consensus_provenance(tmp_path: Path):
    workspace, _ = _runner_workspace(tmp_path)
    minimal = workspace / "inputs" / "minimal-consensus.json"
    minimal.write_text(json.dumps({"status": "completed", "strict_expansion": True, "annotators": ["a", "b", "c"]}), encoding="utf-8")
    with pytest.raises(Exception, match="schema version"):
        freezer.freeze_confirmation_inputs(
            workspace, "minimal-consensus", predictions_relative="inputs/predictions.csv", panel_relative="inputs/panel.csv",
            robustness_relative="inputs/robustness.json", annotation_consensus_relative="inputs/minimal-consensus.json",
        )
    provenance = workspace / "inputs" / "annotation_consensus.json"
    payload = json.loads(provenance.read_text(encoding="utf-8"))
    payload["inputs"][0]["sha256"] = "0" * 64
    provenance.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(Exception, match="hash mismatch"):
        freezer.freeze_confirmation_inputs(
            workspace, "tampered-consensus", predictions_relative="inputs/predictions.csv", panel_relative="inputs/panel.csv",
            robustness_relative="inputs/robustness.json", annotation_consensus_relative="inputs/annotation_consensus.json",
        )


def test_confirmation_runner_writes_unsupported_result_from_frozen_inputs(tmp_path: Path):
    workspace, manifest = _runner_workspace(tmp_path)
    result = confirmation_runner.run_confirmation(workspace, "confirmation-test", input_manifest_relative=manifest)
    output = workspace / "KL_180826/multi_llm_evidence_extraction/outputs/v6_h2_confirmation/confirmation-test"
    assert result["state"] == "unsupported"
    assert (output / "v6_h2_confirmation_result.json").is_file()
    assert "confirmation_does_not_replace_locked_v6_primary" in result["limitations"]


def test_confirmation_runner_blocks_tampered_frozen_input(tmp_path: Path):
    workspace, manifest = _runner_workspace(tmp_path)
    predictions = workspace / "inputs/predictions.csv"
    predictions.write_text(predictions.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(Exception, match="hash mismatch"):
        confirmation_runner.run_confirmation(workspace, "confirmation-blocked", input_manifest_relative=manifest)
    failure = workspace / "KL_180826/multi_llm_evidence_extraction/outputs/v6_h2_confirmation/confirmation-blocked/v6_h2_confirmation_failure.json"
    assert failure.is_file()
    assert json.loads(failure.read_text(encoding="utf-8"))["status"] == "blocked"
    assert not (workspace / "KL_180826/multi_llm_evidence_extraction/outputs/v6_primary/v6_primary_20260909").exists()
