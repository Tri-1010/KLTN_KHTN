from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPTS) not in sys.path: sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); return module


sampler = load("build_annotation_sample")
annotation = load("run_semantic_annotation")


def corpus(n: int = 30) -> pd.DataFrame:
    return sampler.normalize_columns(pd.DataFrame({
        "ticker": [f"T{i % 5}" for i in range(n)], "date": pd.date_range("2024-01-01", periods=n),
        "source": [f"s{i % 3}" for i in range(n)], "title": [f"Tin lợi nhuận tăng {i}" for i in range(n)],
        "description": ["lợi nhuận tăng"] * n, "full_text": ["lợi nhuận tăng " * (i + 30) for i in range(n)],
        "url": [f"https://example/{i}" for i in range(n)], "match_confidence": ["exact", "partial"] * (n // 2) + (["exact"] if n % 2 else []),
    }))


def test_deterministic_sampling_preserves_all_base_rows():
    frame, _ = sampler.dedup(corpus())
    initial = sampler.build_sample(frame, 10, 42)
    first = sampler.build_sample(frame, 20, 42, initial, "sample500_v1")
    second = sampler.build_sample(frame.sample(frac=1, random_state=9), 20, 42, initial, "sample500_v1")
    assert set(initial.news_id) <= set(first.news_id)
    assert first.news_id.tolist() == second.news_id.tolist()
    assert first.selection_origin.eq("base_preserved").sum() == 10
    assert set(first.sample_id) == {"sample500_v1"}


def test_legacy_sampler_preserves_original_output_contract():
    frame, _ = sampler.dedup(corpus())
    legacy = sampler.build_sample(frame, 10, 42)
    assert "sample_id" not in legacy and "selection_origin" not in legacy
    assert len(legacy) == 10


def test_sampler_rejects_future_outcome_fields():
    with pytest.raises(ValueError, match="future/outcome"):
        sampler.build_sample(corpus().assign(label_outperform_T20=1), 5, 42)


def test_run_scoped_paths_never_equal_canonical(tmp_path: Path):
    canonical = annotation.annotation_paths("a")
    scoped = annotation.annotation_paths("a", "sample500_a", tmp_path)
    assert scoped["labels"] != canonical["labels"]
    assert all(str(path).startswith(str(tmp_path)) for path in scoped.values())
    assert "batch" not in canonical and "batch" in scoped


def test_resume_key_batch_mapping_and_terminal_provenance():
    row = {"news_id": "n", "annotator": "a", "input_sha256": "i", "prompt_sha256": "p", "schema_sha256": "s", "provider": "anthropic", "requested_model": "claude-opus-5", "run_id": "r"}
    assert annotation.resume_key(row) == ("n", "a", "i", "p", "s", "anthropic", "claude-opus-5", "r")
    mapped = annotation.map_batch_results_by_custom_id([{"custom_id": "b", "x": 2}, {"custom_id": "a", "x": 1}])
    assert mapped["a"]["x"] == 1 and mapped["b"]["x"] == 2
    with pytest.raises(ValueError): annotation.map_batch_results_by_custom_id([{"custom_id": "a"}, {"custom_id": "a"}])
    assert annotation.terminal_response_status("refusal") == ("refusal", True)
    assert annotation.terminal_response_status("max_tokens") == ("truncated", True)
    assert annotation.terminal_response_status("tool_use")[1] is False


def test_confirmation_annotation_preflight_enforces_budget_and_local_router(monkeypatch):
    monkeypatch.setenv("URL_LOCAL", "http://localhost:20128/v1")
    monkeypatch.setenv("API_LOCAL", "secret")
    ready = annotation.run_confirmation_annotation_preflight("local_router", "claude-opus", 2000)
    assert ready["planned_annotation_calls"] == 6000
    assert ready["credential_persisted"] is False
    assert "secret" not in json.dumps(ready)
    with pytest.raises(ValueError, match="article cap"):
        annotation.run_confirmation_annotation_preflight("local_router", "claude-opus", 2001)
    with pytest.raises(ValueError, match="requires the approved local_router"):
        annotation.run_confirmation_annotation_preflight("anthropic", "claude-opus", 1)
    monkeypatch.setenv("URL_LOCAL", "http://remote.test/v1")
    with pytest.raises(Exception, match="localhost"):
        annotation.run_confirmation_annotation_preflight("local_router", "claude-opus", 1)


def test_confirmation_manifest_fields_do_not_persist_router_secret(monkeypatch):
    monkeypatch.setenv("URL_LOCAL", "http://127.0.0.1:20128/v1")
    monkeypatch.setenv("API_LOCAL", "do-not-write")
    fields = annotation.confirmation_annotation_manifest_fields("local_router", "router-model", 2)
    assert fields["annotation_call_budget"] == 6
    assert fields["credential_persisted"] is False
    assert fields["route_provenance"]["endpoint_host"] == "127.0.0.1:20128"
    assert "do-not-write" not in json.dumps(fields)


def test_confirmation_requires_all_three_strict_annotators(tmp_path: Path):
    consensus = load("build_consensus_labels")
    expected = tmp_path / "sample.csv"
    pd.DataFrame({"news_id": ["n1"], "ticker": ["AAA"]}).to_csv(expected, index=False)
    paths = []
    for annotator_id in ("a", "b"):
        path = tmp_path / f"{annotator_id}.jsonl"
        path.write_text(json.dumps(_strict_row("n1", "AAA", annotator_id)) + "\n", encoding="utf-8")
        paths.append(path)
    with pytest.raises(ValueError, match="annotator coverage"):
        consensus.validate_strict_expansion_rows(paths, expected, ("a", "b", "c"))


def test_anthropic_offline_manifest_uses_official_batch_and_count_shapes():
    schema_path = ROOT / "multi_llm_evidence_extraction" / "schemas" / "semantic_news_annotation_schema.json"
    schema_text = schema_path.read_text(encoding="utf-8")
    schema = json.loads(schema_text)
    request = annotation.anthropic_batch_request("run:a:n", "claude-opus-5", "system", "prompt", schema)
    assert request["custom_id"] == "run:a:n"
    params = request["params"]
    assert params["thinking"] == {"type": "adaptive"}
    api_schema = params["output_config"]["format"]["schema"]
    assert params["output_config"]["format"]["type"] == "json_schema"
    serialized = json.dumps(api_schema)
    assert not any(key in serialized for key in ("minimum", "maximum", "minLength", "uniqueItems"))
    assert api_schema["additionalProperties"] is False and "required" in api_schema
    count = annotation.anthropic_count_tokens_params("claude-opus-5", "system", "prompt", schema)
    assert count["output_config"]["format"]["schema"] == api_schema
    assert "max_tokens" not in count and count["messages"][0]["role"] == "user"
    assert schema_path.read_text(encoding="utf-8") == schema_text


def test_sampler_rejects_base_hash_drift_and_missing_hash():
    frame, _ = sampler.dedup(corpus(10))
    base = sampler.build_sample(frame, 5, 42)
    missing = base.drop(columns=["content_hash"])
    with pytest.raises(ValueError, match="missing required fields"):
        sampler.build_sample(frame, 8, 42, missing, "sample500_v1")
    changed = base.copy()
    changed.loc[changed.index[0], "content_hash"] = "changed"
    with pytest.raises(ValueError, match="content hash mismatch"):
        sampler.build_sample(frame, 8, 42, changed, "sample500_v1")


def test_resume_rejects_model_change_and_requires_run_id(tmp_path: Path):
    input_path = tmp_path / "sample.csv"; corpus(1).to_csv(input_path, index=False, encoding="utf-8-sig")
    out = tmp_path / "run"
    base = [sys.executable, str(SCRIPTS / "run_semantic_annotation.py"), "--input", str(input_path), "--annotator", "a", "--provider", "anthropic", "--offline", "--output-dir", str(out), "--only-missing"]
    missing_run = subprocess.run([*base, "--model", "claude-opus-5"], cwd=ROOT, capture_output=True, text=True)
    assert missing_run.returncode != 0 and "require --run-id" in missing_run.stderr
    first = subprocess.run([*base, "--model", "claude-opus-5", "--run-id", "r1"], cwd=ROOT, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    changed = subprocess.run([*base, "--model", "claude-opus-4-8", "--run-id", "r1"], cwd=ROOT, capture_output=True, text=True)
    assert changed.returncode != 0 and "resume manifest mismatch" in changed.stderr


def _strict_row(news_id: str, ticker: str, annotator: str) -> dict:
    return {"news_id": news_id, "ticker": ticker, "annotator": annotator, "status": "ok", "terminal": True, "input_sha256": "i", "content_hash": "a" * 64, "prompt_sha256": "p", "schema_sha256": "s", "requested_model": "m", "provider": "anthropic"}


def test_strict_consensus_requires_exact_expected_universe(tmp_path: Path):
    consensus = load("build_consensus_labels")
    expected = tmp_path / "sample.csv"
    pd.DataFrame({"news_id": ["n1", "n2"], "ticker": ["AAA", "BBB"]}).to_csv(expected, index=False)
    labels = []
    for annotator_id in ("a", "b", "c"):
        path = tmp_path / f"{annotator_id}.jsonl"
        path.write_text(json.dumps(_strict_row("n1", "AAA", annotator_id)) + "\n", encoding="utf-8")
        labels.append(path)
    with pytest.raises(ValueError, match="sample coverage mismatch"):
        consensus.validate_strict_expansion_rows(labels, expected)
    for annotator_id, path in zip(("a", "b", "c"), labels):
        rows = [_strict_row("n1", "AAA", annotator_id), _strict_row("n2", "BBB", annotator_id)]
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    assert len(consensus.validate_strict_expansion_rows(labels, expected)) == 6


def test_run_scoped_offline_resume_is_idempotent(tmp_path: Path):
    input_path = tmp_path / "sample.csv"; corpus(2).to_csv(input_path, index=False, encoding="utf-8-sig")
    out = tmp_path / "run"
    command = [sys.executable, str(SCRIPTS / "run_semantic_annotation.py"), "--input", str(input_path), "--annotator", "a", "--provider", "anthropic", "--model", "claude-opus-5", "--offline", "--run-id", "r1", "--output-dir", str(out), "--only-missing"]
    first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True); assert first.returncode == 0, first.stderr
    labels_path = out / "labels_annotator_a.jsonl"; before = labels_path.read_text(encoding="utf-8")
    second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True); assert second.returncode == 0, second.stderr
    assert labels_path.read_text(encoding="utf-8") == before
    manifest = json.loads((out / "annotation_manifest_a.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "pending_offline" and manifest["run_id"] == "r1"
    index = json.loads((out / "annotation_manifest_index.json").read_text(encoding="utf-8"))
    assert len(index["runs"]) == 1 and index["runs"][0]["run_id"] == "r1"


def test_run_scoped_output_rejects_canonical_collision(tmp_path: Path):
    input_path = tmp_path / "sample.csv"; corpus(1).to_csv(input_path, index=False)
    canonical = ROOT / "multi_llm_evidence_extraction" / "outputs" / "labels_annotator_a.jsonl"
    before = canonical.read_bytes()
    result = subprocess.run([sys.executable, str(SCRIPTS / "run_semantic_annotation.py"), "--input", str(input_path), "--annotator", "a", "--provider", "anthropic", "--model", "claude-opus-5", "--offline", "--run-id", "bad", "--output-dir", str(canonical.parent)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert canonical.read_bytes() == before


def test_terminal_resume_rows_are_not_reprocessed(tmp_path: Path):
    input_path = tmp_path / "sample.csv"; frame = corpus(1); frame.to_csv(input_path, index=False)
    out = tmp_path / "run"; out.mkdir()
    row = dict(frame.iloc[0]); row["news_id"] = annotation.stable_news_id(row)
    prompt, payload = annotation.build_user_prompt(row, 12000)
    schema_hash = annotation.sha256_file(ROOT / "multi_llm_evidence_extraction" / "schemas" / "semantic_news_annotation_schema.json")
    base = {"annotator": "a", "news_id": row["news_id"], "input_sha256": annotation.sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True)), "prompt_sha256": annotation.sha256_text(annotation.SYSTEM_PROMPT + "\n" + prompt), "schema_sha256": schema_hash, "provider": "anthropic", "requested_model": "claude-opus-5", "run_id": "r", "status": "refusal", "terminal": True}
    (out / "labels_annotator_a.jsonl").write_text(json.dumps(base) + "\n", encoding="utf-8")
    manifest = {"run_id": "r", "annotator": "a", "provider": "anthropic", "requested_model": "claude-opus-5", "input_sha256": annotation.sha256_file(input_path), "schema_sha256": schema_hash, "prompt_version": annotation.PROMPT_VERSION, "schema_version": annotation.SCHEMA_VERSION, "command_config": {"anthropic_batch": False, "max_articles": None, "max_article_chars": 12000}}
    (out / "annotation_manifest_a.json").write_text(json.dumps(manifest), encoding="utf-8")
    command = [sys.executable, str(SCRIPTS / "run_semantic_annotation.py"), "--input", str(input_path), "--annotator", "a", "--provider", "anthropic", "--model", "claude-opus-5", "--offline", "--run-id", "r", "--output-dir", str(out), "--resume"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True); assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in (out / "labels_annotator_a.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1 and rows[0]["status"] == "refusal"


def test_consensus_cli_honors_explicit_empty_outputs(tmp_path: Path):
    labels = tmp_path / "empty.jsonl"; labels.write_text("", encoding="utf-8")
    jsonl_out, csv_out = tmp_path / "c.jsonl", tmp_path / "c.csv"
    result = subprocess.run([sys.executable, str(SCRIPTS / "build_consensus_labels.py"), "--inputs", str(labels), "--jsonl-output", str(jsonl_out), "--csv-output", str(csv_out)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert jsonl_out.exists() and csv_out.exists()
