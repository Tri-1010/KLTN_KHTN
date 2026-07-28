import json
import os
import sys
import types
from pathlib import Path

import pytest

from scripts import generate_decision_support_artifacts as artifacts
from scripts import llm_provider


SAMPLE_PACK = {
    "decision_id": "2025Q1_ABC_01",
    "ticker": "ABC",
    "decision_date": "2025-03-31",
    "period_id": "2025Q1",
    "ml_signal": {"pred_proba_up": 0.91, "pred_label": 1, "rank_in_period": 1},
    "technical_snapshot": {"rsi_end_q": 60.0},
    "top_drivers": [{"feature": "rsi_end_q", "value": 60.0}],
    "news_evidence": [
        {
            "evidence_id": "N001",
            "published_at": "2025-03-01",
            "title": "ABC báo lãi",
            "article_summary": "ABC tăng lợi nhuận.",
            "key_facts": [{"fact_id": "N001-F01", "fact": "Lợi nhuận tăng"}],
            "risk_flags": ["governance"],
            "event_type": "earnings",
            "lead": "Lead",
            "full_text_ref": "hash1",
            "content_hash": "hash1",
            "full_text_chars": 1000,
            "full_text_excerpt": "ABC báo lãi nhờ doanh thu tăng.",
        }
    ],
    "data_quality_flags": {
        "news_coverage": "high",
        "full_text_coverage": 1,
        "summary_coverage": 1,
        "key_fact_coverage": 1,
    },
    "outcome_for_review_only": {
        "realized_period_return": 0.12,
        "outcome_label": "positive",
    },
    "nested": {"future_return": 0.5, "safe": "ok"},
}


def test_strip_initial_prompt_fields_removes_outcome():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    text = json.dumps(clean, ensure_ascii=False).lower()
    assert "outcome_for_review_only" not in clean
    assert "realized" not in text
    assert "future_return" not in text
    assert clean["nested"]["safe"] == "ok"


def test_initial_pack_has_no_realized_or_future_tokens():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    assert not artifacts.serialized_has_initial_leakage(clean)
    artifacts.assert_no_initial_leakage(clean)


def test_news_evidence_cutoff_published_at_le_decision_date():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    for news in clean["news_evidence"]:
        assert news["published_at"] <= clean["decision_date"]


def test_ml_only_variant_excludes_news_evidence():
    ml_only = artifacts.build_ml_only_pack(SAMPLE_PACK)
    assert "news_evidence" not in ml_only
    assert ml_only["ml_signal"] == SAMPLE_PACK["ml_signal"]
    assert ml_only["technical_snapshot"] == SAMPLE_PACK["technical_snapshot"]
    assert ml_only["data_quality_flags"]["news_evidence_removed_for_ablation"] is True
    assert not artifacts.serialized_has_initial_leakage(ml_only)


def test_full_evidence_uses_enriched_fields():
    clean = artifacts.strip_initial_prompt_fields(SAMPLE_PACK)
    news = clean["news_evidence"][0]
    for key in ["article_summary", "key_facts", "risk_flags", "lead", "full_text_ref", "content_hash", "full_text_chars", "full_text_excerpt"]:
        assert key in news
        assert news[key] not in (None, "", [])


def test_manifest_records_model_metadata_and_hashes(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("abc", encoding="utf-8")
    assert artifacts.sha256_file(source) == artifacts.sha256_text("abc")


def test_offline_mode_writes_prompts_not_fake_cards(tmp_path, monkeypatch):
    from scripts import generate_llm_decision_cards as llm_cards

    monkeypatch.setattr(llm_cards, "GENERATED", tmp_path)
    prompt_path, rows = llm_cards.write_offline_prompts("ml_only", [artifacts.build_ml_only_pack(SAMPLE_PACK)], "pytest")

    assert prompt_path == tmp_path / "pytest_llm_prompt_packs_ml_only.jsonl"
    assert prompt_path.exists()
    assert rows[0]["decision_id"] == SAMPLE_PACK["decision_id"]
    assert "card_markdown" not in rows[0]
    assert "outcome_for_review_only" not in rows[0]["user_prompt"]


@pytest.mark.parametrize("field", ["post_hoc_outcome", "benchmark_return", "excess_return"])
def test_prompt_for_pack_rejects_all_outcome_markers(field):
    from scripts import generate_llm_decision_cards as llm_cards

    pack = artifacts.strip_initial_prompt_fields(SAMPLE_PACK) | {field: 0.1}
    with pytest.raises(ValueError, match="forbidden tokens"):
        llm_cards.prompt_for_pack(pack)


def test_provider_clis_accept_all_supported_providers(monkeypatch):
    from scripts import generate_llm_decision_cards as llm_cards
    from scripts import score_decision_cards as scorer

    for provider in sorted(llm_provider.SUPPORTED_PROVIDERS):
        monkeypatch.setattr(sys, "argv", ["generate_llm_decision_cards.py", "--provider", provider])
        assert llm_cards.parse_args().provider == provider
        monkeypatch.setattr(sys, "argv", ["score_decision_cards.py", "--provider", provider])
        assert scorer.parse_args().provider == provider


def test_provider_resolution_detects_deepseek_key(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

    assert llm_provider.resolve_provider(None) == "deepseek"
    assert llm_provider.resolve_model("deepseek", None) == llm_provider.DEFAULT_DEEPSEEK_MODEL
    assert llm_provider.provider_temperature("deepseek") == 0


def test_artifact_ref_is_repo_relative(tmp_path):
    nested = tmp_path / "reports" / "result.json"
    nested.parent.mkdir(parents=True)
    nested.write_text("{}", encoding="utf-8")

    assert llm_provider.artifact_ref(tmp_path, nested) == "reports/result.json"


def test_canonical_live_artifacts_are_consistent():
    import csv

    from scripts import generate_llm_decision_cards as llm_cards

    generated = Path(__file__).resolve().parents[1] / "reports" / "decision_support" / "generated"
    ml_rows = [json.loads(line) for line in (generated / "llm_cards_ml_only.jsonl").read_text(encoding="utf-8").splitlines() if line]
    full_rows = [json.loads(line) for line in (generated / "llm_cards_full_evidence.jsonl").read_text(encoding="utf-8").splitlines() if line]
    raw_rows = [json.loads(line) for line in (generated / "llm_raw_responses.jsonl").read_text(encoding="utf-8").splitlines() if line]
    manifest = json.loads((generated / "llm_generation_manifest.json").read_text(encoding="utf-8"))
    with (generated / "llm_rubric_scores.csv").open(encoding="utf-8-sig", newline="") as handle:
        score_rows = list(csv.DictReader(handle))

    assert len(ml_rows) == len(full_rows) == 25
    assert len({row["decision_id"] for row in ml_rows}) == 25
    assert {row["decision_id"] for row in ml_rows} == {row["decision_id"] for row in full_rows}
    assert len(raw_rows) == 50
    assert len(score_rows) == 75
    assert len({(row["decision_id"], row["card_type"]) for row in score_rows}) == 75
    assert {card_type: sum(row["card_type"] == card_type for row in score_rows) for card_type in {row["card_type"] for row in score_rows}} == {
        "rule_based_baseline": 25,
        "llm_ml_only": 25,
        "llm_full_evidence": 25,
    }
    assert manifest["status"] == "completed"
    assert len(manifest["cards"]) == 50
    assert manifest["scoring"]["num_scores"] == 75
    assert not manifest["failures"]
    assert all(not Path(path).is_absolute() for path in manifest["outputs"])

    packs_by_variant = {
        "llm_ml_only": json.loads((generated / "evidence_packs_ml_only.json").read_text(encoding="utf-8")),
        "llm_full_evidence": json.loads((generated / "evidence_packs_initial.json").read_text(encoding="utf-8")),
    }
    pack_hashes = {
        card_type: {pack["decision_id"]: llm_cards.prompt_for_pack(pack)[2] for pack in packs}
        for card_type, packs in packs_by_variant.items()
    }
    for row in ml_rows + full_rows:
        assert row["pack_sha256"] == pack_hashes[row["card_type"]][row["decision_id"]]
        assert len(row["prompt_sha256"]) == 64

    initial_text = (generated / "evidence_packs_initial.json").read_text(encoding="utf-8").lower()
    assert not any(token in initial_text for token in llm_cards.FORBIDDEN_PROMPT_TOKENS)


def test_env_file_loads_without_overriding_existing_env(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "# local secrets\nLLM_PROVIDER=gemini\nGEMINI_API_KEY='from-file'\nGEMINI_MODEL=gemini-from-file\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GEMINI_MODEL", "keep-existing")
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    loaded = llm_provider.load_env_file(tmp_path, env_path)

    assert loaded["LLM_PROVIDER"] == "gemini"
    assert loaded["GEMINI_API_KEY"] == "from-file"
    assert os.environ["LLM_PROVIDER"] == "gemini"
    assert os.environ["GEMINI_API_KEY"] == "from-file"
    assert os.environ["GEMINI_MODEL"] == "keep-existing"


def test_provider_resolution_prefers_cli_then_gemini_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert llm_provider.resolve_provider("gemini") == "gemini"

    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert llm_provider.resolve_provider(None) == "gemini"
    assert llm_provider.resolve_model("gemini", None) == llm_provider.DEFAULT_GEMINI_MODEL


def test_make_gemini_client_uses_env_key(monkeypatch):
    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key

    fake_genai = types.SimpleNamespace(Client=FakeClient)
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setenv("GEMINI_API_KEY", "secret-value")

    client, module = llm_provider.make_llm_client("gemini")

    assert client.api_key == "secret-value"
    assert module is fake_genai


def test_gemini_generation_wrapper_normalizes_response():
    class FakeModels:
        def generate_content(self, model, contents, config=None):
            assert model == "gemini-test"
            assert contents == "prompt"
            assert config is not None
            return types.SimpleNamespace(text="card text", model_version="gemini-test", usage_metadata={"tokens": 3})

    fake_client = types.SimpleNamespace(models=FakeModels())
    fake_module = types.SimpleNamespace(types=types.SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs))

    result = llm_provider.call_generate("gemini", fake_client, fake_module, "gemini-test", "system", "prompt", 100, "high")

    assert result["text"] == "card text"
    assert result["response_model"] == "gemini-test"
    assert "secret" not in json.dumps(result).lower()


def test_gemini_generation_fallback_preserves_system_prompt_boundary():
    calls = []

    def generate_config(**kwargs):
        if "system_instruction" in kwargs:
            raise TypeError("system_instruction unsupported")
        return kwargs

    class FakeModels:
        def generate_content(self, model, contents, config=None):
            calls.append({"contents": contents, "config": config})
            return types.SimpleNamespace(text="card text", candidates=[types.SimpleNamespace(finish_reason="STOP")])

    fake_client = types.SimpleNamespace(models=FakeModels())
    fake_module = types.SimpleNamespace(types=types.SimpleNamespace(GenerateContentConfig=generate_config))

    result = llm_provider.call_generate("gemini", fake_client, fake_module, "gemini-test", "system rules", "user data", 100, "high")

    assert result["text"] == "card text"
    assert len(calls) == 1
    assert calls[0]["contents"] == "<SYSTEM_INSTRUCTIONS>\nsystem rules\n</SYSTEM_INSTRUCTIONS>\n\n<USER_CONTENT>\nuser data\n</USER_CONTENT>"
    assert calls[0]["config"] == {"max_output_tokens": 100}


def test_gemini_generation_fallback_never_sends_unconfigured_request():
    calls = []

    def generate_config(**kwargs):
        if "system_instruction" in kwargs:
            raise TypeError("system_instruction unsupported")
        return kwargs

    class FakeModels:
        def generate_content(self, model, contents, config=None):
            calls.append({"contents": contents, "config": config})
            raise TypeError("config unsupported")

    fake_client = types.SimpleNamespace(models=FakeModels())
    fake_module = types.SimpleNamespace(types=types.SimpleNamespace(GenerateContentConfig=generate_config))

    with pytest.raises(RuntimeError, match="rejected required generation config"):
        llm_provider.call_generate("gemini", fake_client, fake_module, "gemini-test", "system rules", "user data", 100, "high")

    assert len(calls) == 1
    assert calls[0]["config"] == {"max_output_tokens": 100}
    assert "<SYSTEM_INSTRUCTIONS>\nsystem rules\n</SYSTEM_INSTRUCTIONS>" in calls[0]["contents"]


@pytest.mark.parametrize("finish_reason", ["MAX_TOKENS", "FinishReason.MAX_TOKENS", types.SimpleNamespace(name="MAX_TOKENS")])
def test_gemini_generation_rejects_token_truncation(finish_reason):
    class FakeModels:
        def generate_content(self, model, contents, config=None):
            return types.SimpleNamespace(
                text="partial card",
                candidates=[types.SimpleNamespace(finish_reason=finish_reason)],
            )

    fake_client = types.SimpleNamespace(models=FakeModels())
    fake_module = types.SimpleNamespace(types=types.SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs))

    with pytest.raises(RuntimeError, match="truncated at token limit"):
        llm_provider.call_generate("gemini", fake_client, fake_module, "gemini-test", "system", "prompt", 100, "high")


def test_anthropic_scoring_sanitizes_numeric_constraints_on_wire():
    from scripts import score_decision_cards as scorer

    captured = {}
    valid_score = {
        "faithfulness": 5,
        "hallucination_control": 5,
        "ml_explanation": 4,
        "risk_awareness": 3,
        "monitoring_usefulness": 2,
        "clarity_usefulness": 1,
        "overall": 5,
        "major_issue": "none",
        "major_hallucinations": [],
        "missing_evidence_refs": [],
        "overall_comment": "ok",
    }

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            return types.SimpleNamespace(
                content=[types.SimpleNamespace(type="text", text=json.dumps(valid_score))],
                stop_reason="end_turn",
                model="claude-test",
                _request_id="req-anthropic",
            )

    fake_client = types.SimpleNamespace(messages=FakeMessages())
    scored = llm_provider.call_score(
        "anthropic",
        fake_client,
        object(),
        "claude-test",
        "system",
        "prompt",
        100,
        "high",
        scorer.RUBRIC_SCHEMA,
    )

    wire_schema = captured["output_config"]["format"]["schema"]
    assert '"minimum"' not in json.dumps(wire_schema)
    assert '"maximum"' not in json.dumps(wire_schema)
    assert wire_schema["properties"]["faithfulness"] == {"type": "integer"}
    assert scorer.RUBRIC_SCHEMA["properties"]["faithfulness"] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 5,
    }
    assert scored["parsed"] == valid_score


@pytest.mark.parametrize(
    ("provider", "operation", "finish_reason"),
    [
        ("anthropic", "generate", "MoDeL_Context_Window_Exceeded"),
        ("anthropic", "score", "model_CONTEXT_window_EXCEEDED"),
        ("gemini", "generate", "contextWindowExceeded"),
        ("gemini", "score", "ModelContextWindowExceeded"),
        ("deepseek", "generate", "CoNtExT-LeNgTh ExCeEdEd"),
        ("deepseek", "score", "MAX context WINDOW"),
    ],
)
def test_provider_calls_reject_context_window_truncation(provider, operation, finish_reason):
    if provider == "anthropic":
        response = types.SimpleNamespace(
            content=[types.SimpleNamespace(type="text", text='{"overall": 5}')],
            stop_reason=finish_reason,
        )
        client = types.SimpleNamespace(messages=types.SimpleNamespace(create=lambda **kwargs: response))
        provider_module = object()
    elif provider == "gemini":
        class FakeModels:
            def generate_content(self, model, contents, config=None):
                return types.SimpleNamespace(
                    text='{"overall": 5}',
                    candidates=[types.SimpleNamespace(finish_reason=finish_reason)],
                )

        client = types.SimpleNamespace(models=FakeModels())
        provider_module = types.SimpleNamespace(types=types.SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs))
    else:
        class FakeRequests:
            @staticmethod
            def post(url, headers, json, timeout):
                return FakeDeepSeekResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": '{"overall": 5}'},
                                "finish_reason": finish_reason,
                            }
                        ]
                    }
                )

        client = {"api_key": "secret", "base_url": "https://api.deepseek.com/v1", "timeout": 12}
        provider_module = FakeRequests

    call = llm_provider.call_generate if operation == "generate" else llm_provider.call_score
    args = [provider, client, provider_module, f"{provider}-test", "system", "prompt", 100, "high"]
    if operation == "score":
        args.append({"type": "object"})

    with pytest.raises(RuntimeError, match="truncated at context window limit"):
        call(*args)


def test_gemini_scoring_wrapper_parses_json():
    class FakeModels:
        def generate_content(self, model, contents, config=None):
            assert config["response_mime_type"] == "application/json"
            return types.SimpleNamespace(
                text=json.dumps(
                    {
                        "faithfulness": 5,
                        "hallucination_control": 5,
                        "ml_explanation": 4,
                        "risk_awareness": 3,
                        "monitoring_usefulness": 2,
                        "clarity_usefulness": 1,
                        "overall": 1,
                        "major_issue": "none",
                        "major_hallucinations": [],
                        "missing_evidence_refs": [],
                        "overall_comment": "ok",
                    }
                ),
                model_version="gemini-test",
            )

    fake_client = types.SimpleNamespace(models=FakeModels())
    fake_module = types.SimpleNamespace(types=types.SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs))

    scored = llm_provider.call_score("gemini", fake_client, fake_module, "gemini-test", "system", "prompt", 100, "high", {})
    from scripts import score_decision_cards

    normalized = score_decision_cards.normalize_score(scored["parsed"])
    assert normalized["faithfulness"] == 5
    assert normalized["overall"] == 1
    assert scored["response_model"] == "gemini-test"


def test_gemini_scoring_rejects_token_truncation():
    class FakeModels:
        def generate_content(self, model, contents, config=None):
            return types.SimpleNamespace(
                text='{"overall": 5}',
                candidates=[types.SimpleNamespace(finish_reason=types.SimpleNamespace(name="MAX_TOKENS"))],
            )

    fake_client = types.SimpleNamespace(models=FakeModels())
    fake_module = types.SimpleNamespace(types=types.SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs))

    with pytest.raises(RuntimeError, match="truncated at token limit"):
        llm_provider.call_score("gemini", fake_client, fake_module, "gemini-test", "system", "prompt", 100, "high", {})


def test_scoring_requires_complete_typed_rubric():
    from scripts import score_decision_cards

    with pytest.raises(ValueError, match="missing required fields"):
        score_decision_cards.normalize_score({"overall": 5})

    complete = {
        "faithfulness": 5,
        "hallucination_control": 5,
        "ml_explanation": 4,
        "risk_awareness": 3,
        "monitoring_usefulness": 2,
        "clarity_usefulness": 1,
        "overall": 5,
        "major_issue": "none",
        "major_hallucinations": [],
        "missing_evidence_refs": [],
        "overall_comment": "ok",
    }
    with pytest.raises(ValueError, match="must be an integer"):
        score_decision_cards.normalize_score(complete | {"faithfulness": "5"})
    with pytest.raises(ValueError, match="array of strings"):
        score_decision_cards.normalize_score(complete | {"major_hallucinations": [1]})


@pytest.mark.parametrize("invalid_score", [0, 6, -10, 100])
def test_scoring_rejects_out_of_range_rubric_scores(invalid_score):
    from scripts import score_decision_cards

    complete = {
        "faithfulness": 5,
        "hallucination_control": 5,
        "ml_explanation": 4,
        "risk_awareness": 3,
        "monitoring_usefulness": 2,
        "clarity_usefulness": 1,
        "overall": 5,
        "major_issue": "none",
        "major_hallucinations": [],
        "missing_evidence_refs": [],
        "overall_comment": "ok",
    }

    with pytest.raises(ValueError, match="must be between 1 and 5"):
        score_decision_cards.normalize_score(complete | {"faithfulness": invalid_score})


@pytest.mark.parametrize("invalid_score", [True, False, 1.0, 4.5])
def test_scoring_rejects_non_integer_rubric_scores(invalid_score):
    from scripts import score_decision_cards

    complete = {
        "faithfulness": 5,
        "hallucination_control": 5,
        "ml_explanation": 4,
        "risk_awareness": 3,
        "monitoring_usefulness": 2,
        "clarity_usefulness": 1,
        "overall": 5,
        "major_issue": "none",
        "major_hallucinations": [],
        "missing_evidence_refs": [],
        "overall_comment": "ok",
    }

    with pytest.raises(ValueError, match="must be an integer"):
        score_decision_cards.normalize_score(complete | {"faithfulness": invalid_score})


def test_scoring_accepts_valid_score_boundaries_and_schema_declares_bounds():
    from scripts import score_decision_cards

    complete = {
        "faithfulness": 1,
        "hallucination_control": 5,
        "ml_explanation": 1,
        "risk_awareness": 5,
        "monitoring_usefulness": 1,
        "clarity_usefulness": 5,
        "overall": 1,
        "major_issue": "none",
        "major_hallucinations": [],
        "missing_evidence_refs": [],
        "overall_comment": "ok",
    }

    assert score_decision_cards.normalize_score(complete) == complete
    for field in score_decision_cards.SCORE_FIELDS:
        assert score_decision_cards.RUBRIC_SCHEMA["properties"][field] == {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
        }


def test_run_scoring_records_incomplete_rubric_as_failure(monkeypatch, tmp_path):
    from scripts import score_decision_cards as scorer

    monkeypatch.setattr(scorer, "GENERATED", tmp_path)
    monkeypatch.setattr(scorer, "INITIAL_PACKS", tmp_path / "evidence_packs_initial.json")
    monkeypatch.setattr(scorer, "RULE_BASED_CARDS", tmp_path / "decision_cards.md")
    scorer.INITIAL_PACKS.write_text('[{"decision_id":"2025Q1_ABC_01"}]', encoding="utf-8")
    scorer.RULE_BASED_CARDS.write_text(
        "# Cards\n\n## Decision Card: 2025Q1_ABC_01\nIncomplete score target",
        encoding="utf-8",
    )
    monkeypatch.setattr(scorer, "make_llm_client", lambda provider: (object(), object()))
    monkeypatch.setattr(
        scorer,
        "call_score",
        lambda *args, **kwargs: {"parsed": {"overall": 5}, "response_model": "gemini-test", "request_id": "req-1"},
    )

    result = scorer.run_scoring(provider="gemini", model="gemini-test")

    assert result["status"] == "completed_with_failures"
    assert result["num_scores"] == 0
    assert result["failures"][0]["stage"] == "score"
    assert "missing required fields" in result["failures"][0]["error"]
    assert not (tmp_path / "llm_rubric_scores.csv").exists()


def test_run_scoring_records_out_of_range_rubric_as_failure(monkeypatch, tmp_path):
    from scripts import score_decision_cards as scorer

    monkeypatch.setattr(scorer, "GENERATED", tmp_path)
    monkeypatch.setattr(scorer, "INITIAL_PACKS", tmp_path / "evidence_packs_initial.json")
    monkeypatch.setattr(scorer, "RULE_BASED_CARDS", tmp_path / "decision_cards.md")
    scorer.INITIAL_PACKS.write_text('[{"decision_id":"2025Q1_ABC_01"}]', encoding="utf-8")
    scorer.RULE_BASED_CARDS.write_text(
        "# Cards\n\n## Decision Card: 2025Q1_ABC_01\nOut-of-range score target",
        encoding="utf-8",
    )
    malformed_score = {
        "faithfulness": 6,
        "hallucination_control": 5,
        "ml_explanation": 4,
        "risk_awareness": 3,
        "monitoring_usefulness": 2,
        "clarity_usefulness": 1,
        "overall": 5,
        "major_issue": "none",
        "major_hallucinations": [],
        "missing_evidence_refs": [],
        "overall_comment": "ok",
    }
    monkeypatch.setattr(scorer, "make_llm_client", lambda provider: (object(), object()))
    monkeypatch.setattr(
        scorer,
        "call_score",
        lambda *args, **kwargs: {"parsed": malformed_score, "response_model": "gemini-test", "request_id": "req-1"},
    )

    result = scorer.run_scoring(provider="gemini", model="gemini-test")

    assert result["status"] == "completed_with_failures"
    assert result["num_scores"] == 0
    assert result["failures"][0]["stage"] == "score"
    assert "must be between 1 and 5" in result["failures"][0]["error"]
    assert not (tmp_path / "llm_rubric_scores.csv").exists()


class FakeDeepSeekResponse:
    status_code = 200
    text = ""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_make_deepseek_client_uses_env_key(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-secret")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://example.test/v1/")

    client, module = llm_provider.make_llm_client("deepseek")

    assert client["api_key"] == "deepseek-secret"
    assert client["base_url"] == "https://example.test/v1"
    assert module.__name__ == "requests"


def test_deepseek_generation_wrapper_normalizes_response():
    calls = []

    class FakeRequests:
        @staticmethod
        def post(url, headers, json, timeout):
            calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
            return FakeDeepSeekResponse(
                {
                    "id": "req-1",
                    "model": "deepseek-chat",
                    "choices": [{"message": {"content": "card text"}, "finish_reason": "stop"}],
                    "usage": {"total_tokens": 3},
                }
            )

    client = {"api_key": "secret", "base_url": "https://api.deepseek.com/v1", "timeout": 12}
    result = llm_provider.call_generate("deepseek", client, FakeRequests, "deepseek-chat", "system", "prompt", 100, "high")

    assert result["text"] == "card text"
    assert result["request_id"] == "req-1"
    assert result["response_model"] == "deepseek-chat"
    assert calls[0]["json"]["temperature"] == 0
    assert calls[0]["headers"]["Authorization"] == "Bearer secret"


def test_deepseek_scoring_wrapper_parses_json():
    class FakeRequests:
        @staticmethod
        def post(url, headers, json, timeout):
            assert json["response_format"] == {"type": "json_object"}
            user_content = json["messages"][1]["content"]
            assert "Conform to this JSON Schema exactly" in user_content
            assert "required" in user_content
            assert "overall" in user_content
            return FakeDeepSeekResponse(
                {
                    "id": "req-2",
                    "model": "deepseek-chat",
                    "choices": [{"message": {"content": '{"overall": 5}'}, "finish_reason": "stop"}],
                }
            )

    schema = {"type": "object", "properties": {"overall": {"type": "integer"}}, "required": ["overall"]}
    client = {"api_key": "secret", "base_url": "https://api.deepseek.com/v1", "timeout": 12}
    scored = llm_provider.call_score("deepseek", client, FakeRequests, "deepseek-chat", "system", "prompt", 100, "high", schema)

    assert scored["parsed"] == {"overall": 5}
    assert scored["request_id"] == "req-2"
    assert scored["response_model"] == "deepseek-chat"


def test_gitignore_ignores_local_env_files():
    gitignore = Path(__file__).resolve().parents[1] / ".gitignore"
    text = gitignore.read_text(encoding="utf-8")
    assert ".env" in text
    assert ".env.*" in text
    assert "!.env.example" in text
