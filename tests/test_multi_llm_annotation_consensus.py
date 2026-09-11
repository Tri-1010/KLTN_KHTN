from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


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


consensus = _load("build_consensus_labels")
annotation = _load("run_semantic_annotation")


def _row(annotator: str, direction: str = "support", evidence: str = "evidence", input_hash: str = "same") -> dict:
    return {
        "annotator": annotator,
        "news_id": "n1",
        "ticker": "AAA",
        "article_date": "2024-01-01",
        "content_hash": "a" * 64,
        "ticker_relevance": "direct",
        "materiality": "high",
        "direction": direction,
        "event_type": "earnings",
        "time_horizon": "short_term",
        "is_stock_relevant": True,
        "materiality_score": 4,
        "expected_impact_score": 4,
        "uncertainty_score": 2,
        "novelty_score": 3,
        "reasoning_confidence": 4,
        "evidence_span": evidence,
        "data_quality_flags": ["none"],
        "input_sha256": input_hash,
        "prompt_sha256": "prompt",
        "schema_sha256": "schema",
        "status": "ok",
    }


def test_vote_distinguishes_unanimous_majority_and_disagreement():
    assert consensus.vote(["a", "a", "a"])["status"] == "unanimous"
    assert consensus.vote(["a", "a", "b"])["status"] == "majority"
    assert consensus.vote(["a", "b", "c"])["status"] == "disagreement"
    assert consensus.vote(["a", "a"])["status"] == "agreement_2"


def test_consensus_row_uses_majority_not_unanimous_for_two_of_three():
    out = consensus.consensus_for("n1", [_row("a"), _row("b"), _row("c", direction="risk")])
    assert out["consensus_method"] == "majority_vote"
    assert "direction" in out["majority_fields"]
    assert out["artifact_schema_version"] == "pseudo_label_consensus_v2"


def test_consensus_requires_evidence_majority():
    out = consensus.consensus_for("n1", [_row("a", evidence="one"), _row("b", evidence="two"), _row("c", evidence="three")])
    assert out["evidence_span"] is None
    assert "evidence_unavailable" in out["exclusion_reasons"]
    assert not out["analysis_eligible"]


def test_consensus_detects_provenance_conflict():
    out = consensus.consensus_for("n1", [_row("a"), _row("b", input_hash="different"), _row("c")])
    assert "provenance_conflict" in out["quality_flags"]
    assert "provenance_conflict" in out["exclusion_reasons"]
    with pytest.raises(ValueError, match="content_hash provenance conflict"):
        consensus.consensus_for(
            "n1",
            [_row("a"), {**_row("b"), "content_hash": "b" * 64}, _row("c")],
        )


def test_annotation_loader_preserves_same_news_id_across_tickers(tmp_path):
    paths = []
    for annotator in ("a", "b", "c"):
        path = tmp_path / f"{annotator}.jsonl"
        rows = [_row(annotator), {**_row(annotator), "ticker": "BBB"}]
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
        paths.append(path)
    loaded = consensus.load_annotation_rows(paths)
    assert len(loaded) == 6
    grouped = {}
    for row in loaded:
        grouped.setdefault((row["news_id"], row["ticker"]), []).append(row)
    assert set(grouped) == {("n1", "AAA"), ("n1", "BBB")}
    assert all(len(group) == 3 for group in grouped.values())


def test_manifest_paths_are_per_annotator():
    a = annotation.annotation_paths("a")["manifest"]
    b = annotation.annotation_paths("b")["manifest"]
    assert a != b
    assert a.name == "annotation_manifest_a.json"


def test_routed_model_provenance_is_not_anthropic_model():
    value = annotation.model_provenance("anthropic", "cx/gpt-5.4-mini", "gpt-5.4-mini")
    assert value["api_provider"] == "anthropic"
    assert value["model_vendor"] == "openai"
    assert value["route_mode"] == "gateway_or_proxy"


def test_reconstruct_legacy_manifests_preserves_labels(tmp_path, monkeypatch):
    monkeypatch.setattr(annotation, "OUTPUT_DIR", tmp_path)
    sample = tmp_path / "sample.csv"
    sample.write_text("news_id,ticker\nn1,AAA\n", encoding="utf-8")
    for annotator, provider, requested, response in [
        ("a", "deepseek", "deepseek-chat", "deepseek-v4-flash"),
        ("b", "deepseek", "deepseek-chat", "deepseek-v4-flash"),
        ("c", "anthropic", "cx/gpt-5.4-mini", "gpt-5.4-mini"),
    ]:
        label_path = tmp_path / f"labels_annotator_{annotator}.jsonl"
        label = {
            "annotator": annotator, "news_id": "n1", "status": "ok",
            "provider": provider, "requested_model": requested, "response_model": response,
            "schema_sha256": "schema", "prompt_version": "prompt-v1", "schema_version": "schema-v1",
        }
        label_path.write_text(json.dumps(label) + "\n", encoding="utf-8")
        (tmp_path / f"raw_responses_annotator_{annotator}.jsonl").write_text("", encoding="utf-8")
        (tmp_path / f"prompt_packs_annotator_{annotator}.jsonl").write_text("", encoding="utf-8")

    before = {path.name: path.read_bytes() for path in tmp_path.glob("labels_annotator_*.jsonl")}
    manifests = annotation.reconstruct_legacy_manifests(sample)

    assert len(manifests) == 3
    assert before == {path.name: path.read_bytes() for path in tmp_path.glob("labels_annotator_*.jsonl")}
    c_manifest = json.loads((tmp_path / "annotation_manifest_c.json").read_text(encoding="utf-8"))
    assert c_manifest["provenance_status"] == "legacy_reconstructed"
    assert c_manifest["model_vendor"] == "openai"
    index = json.loads((tmp_path / "annotation_manifest_index.json").read_text(encoding="utf-8"))
    assert [run["annotator"] for run in index["runs"]] == ["a", "b", "c"]
