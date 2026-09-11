from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    OUTPUT_DIR,
    PROMPT_VERSION,
    ROOT,
    SCHEMA_VERSION,
    article_payload,
    article_text,
    assert_no_prompt_leakage,
    ensure_dirs,
    load_schema,
    llm_provider,
    provider_is_auth_error,
    clamp_int,
    read_jsonl,
    read_prompt,
    resolve_provider_model,
    sha256_file,
    sha256_text,
    infer_model_vendor,
    stable_news_id,
    utc_now,
    validate_json,
    validate_safe_identifier,
    write_json,
    write_jsonl,
)

SYSTEM_PROMPT = """Bạn là công cụ trích xuất semantic materiality từ tin tức tài chính tiếng Việt.
Chỉ dùng nội dung bài báo được cung cấp. Không dùng kiến thức ngoài.
Không dự báo giá cổ phiếu, không khuyến nghị mua/bán/nắm giữ.
Trả về DUY NHẤT một JSON object hợp lệ theo schema.
"""


def build_user_prompt(row: dict[str, Any], max_chars: int) -> tuple[str, dict[str, Any]]:
    payload = article_payload(row, max_chars=max_chars)
    assert_no_prompt_leakage(payload)
    prompt_template = read_prompt("annotation_prompt.md")
    prompt = prompt_template.replace("{{ARTICLE_PAYLOAD}}", json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return prompt, payload


def normalize_annotation(parsed: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "news_id", "ticker", "company_name", "article_date", "source", "title", "url",
        "ticker_relevance", "is_stock_relevant", "event_type", "event_subtype", "direction", "sentiment",
        "materiality", "materiality_score", "expected_impact_score", "uncertainty_score", "novelty_score",
        "time_horizon", "evidence_span", "summary", "reason", "reasoning_confidence",
        "requires_human_review", "data_quality_flags",
    }
    out = {k: v for k, v in dict(parsed).items() if k in allowed}
    out.setdefault("news_id", row.get("news_id") or stable_news_id(row))
    out.setdefault("ticker", str(row.get("ticker", "")).upper())
    out.setdefault("company_name", row.get("company_name") if row.get("company_name") else None)
    out.setdefault("article_date", str(row.get("date") or row.get("article_date") or "")[:10])
    out.setdefault("source", str(row.get("source", "")))
    out.setdefault("title", str(row.get("title", "")))
    out.setdefault("url", row.get("url") if row.get("url") else None)
    out.setdefault("ticker_relevance", "unclear")
    out.setdefault("event_type", "unclear")
    out.setdefault("event_subtype", None)
    out.setdefault("direction", "unclear")
    out.setdefault("sentiment", "unclear")
    out.setdefault("materiality", "unclear")
    out.setdefault("time_horizon", "unclear")
    out.setdefault("summary", str(row.get("title", "")) or "Semantic annotation requires review.")
    out.setdefault("reason", "Model output normalized to schema; review if confidence or evidence is weak.")
    out.setdefault("requires_human_review", False)
    out["is_stock_relevant"] = bool(out.get("is_stock_relevant", out.get("ticker_relevance") in {"direct", "indirect", "market_wide"}))
    for field in ["materiality_score", "expected_impact_score", "uncertainty_score", "novelty_score", "reasoning_confidence"]:
        out[field] = clamp_int(out.get(field), 1, 5, 3)
    for field, values in {
        "ticker_relevance": {"direct", "indirect", "market_wide", "irrelevant", "unclear"},
        "event_type": {"earnings", "dividend", "capital", "debt", "legal", "governance", "project", "product", "ma", "analyst", "market", "macro", "sector", "other", "unclear"},
        "direction": {"support", "risk", "neutral", "mixed", "unclear"},
        "sentiment": {"positive", "negative", "neutral", "mixed", "unclear"},
        "materiality": {"high", "medium", "low", "unclear"},
        "time_horizon": {"intraday", "short_term", "medium_term", "long_term", "unclear"},
    }.items():
        if out.get(field) not in values:
            out[field] = "unclear"
            out["requires_human_review"] = True
    flags = out.get("data_quality_flags")
    if not isinstance(flags, list):
        flags = []
    text = article_text(row)
    span = out.get("evidence_span")
    if span is not None:
        span = str(span).strip()
        if not span or span not in text:
            flags.append("evidence_span_not_found")
            span = None
            out["requires_human_review"] = True
    out["evidence_span"] = span
    if not text or len(text) < 300:
        flags.append("short_text" if text else "missing_full_text")
    if not flags:
        flags = ["none"]
    out["data_quality_flags"] = sorted(set(str(f) for f in flags if f))
    if out.get("materiality") == "high" and int(out.get("reasoning_confidence", 3) or 3) <= 2:
        out["requires_human_review"] = True
    if out.get("direction") in {"mixed", "unclear"} or out.get("ticker_relevance") == "unclear" or out.get("evidence_span") is None:
        out["requires_human_review"] = True
    return out


def annotation_paths(
    annotator: str,
    run_id: str | None = None,
    output_dir: Path | None = None,
) -> dict[str, Path]:
    if run_id or output_dir:
        root = output_dir or (OUTPUT_DIR / "annotation_runs" / str(run_id))
        return {
            "labels": root / f"labels_annotator_{annotator}.jsonl",
            "raw": root / f"raw_responses_annotator_{annotator}.jsonl",
            "prompts": root / f"prompt_packs_annotator_{annotator}.jsonl",
            "manifest": root / f"annotation_manifest_{annotator}.json",
            "batch": root / f"anthropic_batch_requests_{annotator}.jsonl",
        }
    return {
        "labels": OUTPUT_DIR / f"labels_annotator_{annotator}.jsonl",
        "raw": OUTPUT_DIR / f"raw_responses_annotator_{annotator}.jsonl",
        "prompts": OUTPUT_DIR / f"prompt_packs_annotator_{annotator}.jsonl",
        "manifest": OUTPUT_DIR / f"annotation_manifest_{annotator}.json",
    }


def resume_key(row: dict[str, Any]) -> tuple[str, ...]:
    return (
        str(row.get("news_id", "")), str(row.get("annotator", "")),
        str(row.get("input_sha256", "")), str(row.get("prompt_sha256", "")),
        str(row.get("schema_sha256", "")), str(row.get("provider", "")),
        str(row.get("requested_model", "")), str(row.get("run_id", "")),
    )


_ANTHROPIC_UNSUPPORTED_SCHEMA_KEYS = {
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern",
    "minItems", "maxItems", "uniqueItems", "contains", "minContains", "maxContains", "unevaluatedItems",
}


def _anthropic_api_schema(value: Any) -> Any:
    """Copy schema while leaving stricter unsupported checks for local validation."""
    if isinstance(value, dict):
        return {
            key: _anthropic_api_schema(item)
            for key, item in value.items()
            if key not in _ANTHROPIC_UNSUPPORTED_SCHEMA_KEYS
        }
    if isinstance(value, list):
        return [_anthropic_api_schema(item) for item in value]
    return value


def validate_resume_manifest(path: Path, expected: dict[str, Any], prompt_config: dict[str, Any]) -> None:
    if not path.exists():
        return
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("cannot resume from invalid annotation manifest") from exc
    fields = (
        "run_id", "annotator", "provider", "requested_model", "input_sha256",
        "schema_sha256", "prompt_version", "schema_version",
    )
    mismatches = [field for field in fields if str(manifest.get(field, "")) != str(expected.get(field, ""))]
    prior_config = manifest.get("command_config") or {}
    mismatches.extend(
        f"command_config.{field}"
        for field, value in prompt_config.items()
        if prior_config.get(field) != value
    )
    if mismatches:
        raise ValueError(f"annotation resume manifest mismatch: {sorted(mismatches)}")


def anthropic_batch_request(custom_id: str, model: str, system: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    """Return official Message Batches request shape; does not submit it."""
    return {
        "custom_id": custom_id,
        "params": {
            "model": model,
            "max_tokens": 1800,
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": _anthropic_api_schema(schema)}},
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        },
    }


def map_batch_results_by_custom_id(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for result in results:
        custom_id = str(result.get("custom_id", ""))
        if not custom_id or custom_id in mapped:
            raise ValueError("batch results require unique nonempty custom_id")
        mapped[custom_id] = result
    return mapped


def anthropic_count_tokens_params(model: str, system: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    """Official ``messages.count_tokens`` parameter shape; caller decides whether to submit."""
    return {
        "model": model,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {"format": {"type": "json_schema", "schema": _anthropic_api_schema(schema)}},
    }


def terminal_response_status(stop_reason: str | None) -> tuple[str, bool]:
    if stop_reason == "refusal": return "refusal", True
    if stop_reason in {"max_tokens", "model_context_window_exceeded"}: return "truncated", True
    if stop_reason in {"end_turn", "stop_sequence"}: return "ok", True
    return "nonterminal_or_unknown_stop_reason", False


def _sanitize_error_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"(?i)(authorization|api[_-]?key|token|bearer)\s*[:=]\s*\S+", r"\1=[redacted]", text)
    text = re.sub(r"(?i)sk-[A-Za-z0-9_-]{8,}", "[redacted-secret]", text)
    text = re.sub(r"(?i)AIza[0-9A-Za-z_-]{8,}", "[redacted-secret]", text)
    text = re.sub(r"(?i)https?://[^\s]*:[^\s]*@", "https://[redacted]@", text)
    return text[:1000]


def error_provenance(exc: Exception) -> dict[str, Any]:
    return {
        "error_type": type(exc).__name__,
        "error_message": _sanitize_error_text(exc),
        "request_id": str(getattr(exc, "request_id", "") or getattr(exc, "_request_id", "")),
        "http_status": getattr(exc, "status_code", None),
        "retryable": type(exc).__name__ in {"RateLimitError", "InternalServerError", "APIConnectionError", "APITimeoutError"},
    }


def endpoint_host(provider: str) -> str:
    if provider == "local_router":
        # Returns hostname[:port] only; never return URL_LOCAL's credential value.
        return llm_provider.local_router_endpoint_host()
    env_name = "ANTHROPIC_BASE_URL" if provider == "anthropic" else f"{provider.upper()}_BASE_URL"
    value = os.getenv(env_name, "")
    return urlparse(value).hostname or "default"


def route_provenance(provider: str, response_model: str | None = None) -> dict[str, str]:
    if provider == "local_router":
        return llm_provider.provider_route_provenance(provider, response_model)
    return model_provenance(provider, "", response_model)


def annotation_call_budget(rows_input: int, annotators: int) -> int:
    if rows_input < 0 or annotators < 1:
        raise ValueError("annotation call budget requires nonnegative rows and at least one annotator")
    return int(rows_input) * int(annotators)


def assert_confirmation_annotation_budget(rows_input: int, *, max_articles: int, annotators: int, max_calls: int) -> None:
    if rows_input > max_articles:
        raise ValueError(f"confirmation annotation article cap exceeded: {rows_input} > {max_articles}")
    calls = annotation_call_budget(rows_input, annotators)
    if calls > max_calls:
        raise ValueError(f"confirmation annotation call cap exceeded: {calls} > {max_calls}")


def validate_confirmation_local_router(provider: str, model: str) -> None:
    if provider != "local_router":
        raise ValueError("confirmation annotation requires the approved local_router provider")
    if model not in llm_provider.LOCAL_ROUTER_MODEL_ALLOWLIST:
        raise ValueError("confirmation annotation local-router model is not approved")
    llm_provider.local_router_endpoint_host()


def confirmation_annotation_manifest_fields(provider: str, response_model: str | None, rows_input: int) -> dict[str, Any]:
    return {
        "annotation_call_budget": annotation_call_budget(rows_input, 3),
        "credential_persisted": False,
        "route_provenance": route_provenance(provider, response_model),
    }


def run_confirmation_annotation_preflight(
    provider: str,
    model: str,
    rows_input: int,
    *,
    max_articles: int = 2000,
    annotators: int = 3,
    max_calls: int = 6000,
) -> dict[str, Any]:
    """Validate budget/router before any live annotation request is made."""
    assert_confirmation_annotation_budget(rows_input, max_articles=max_articles, annotators=annotators, max_calls=max_calls)
    validate_confirmation_local_router(provider, model)
    return {
        "provider": provider,
        "requested_model": model,
        "endpoint_host": endpoint_host(provider),
        "rows_input": int(rows_input),
        "planned_annotation_calls": annotation_call_budget(rows_input, annotators),
        "credential_persisted": False,
    }


def sdk_version(provider: str) -> str:
    sdk_name = llm_provider.provider_sdk_name(provider)
    package = {"anthropic-python": "anthropic", "google-genai": "google-genai"}.get(sdk_name, sdk_name)
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def model_provenance(provider: str, requested_model: str, response_model: str | None = None) -> dict[str, str]:
    model_vendor = infer_model_vendor(response_model or requested_model)
    provider_vendor = "deepseek" if provider == "deepseek" else provider
    routed = model_vendor not in {"unknown", provider_vendor}
    return {
        "api_provider": provider,
        "model_vendor": model_vendor,
        "route_mode": "gateway_or_proxy" if routed else "native",
        "provenance_status": "routed" if routed else ("verified" if model_vendor != "unknown" else "ambiguous"),
    }


def update_manifest_index(manifest_path: Path, manifest: dict[str, Any]) -> None:
    index_path = (
        OUTPUT_DIR / "annotation_manifest_index.json"
        if manifest_path.parent.resolve() == OUTPUT_DIR.resolve()
        else manifest_path.parent / "annotation_manifest_index.json"
    )
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            index = {"runs": []}
    else:
        index = {"runs": []}
    runs = [run for run in index.get("runs", []) if run.get("manifest") != str(manifest_path)]
    runs.append({
        "annotator": manifest.get("annotator"),
        "run_id": manifest.get("run_id"),
        "manifest": str(manifest_path),
        "status": manifest.get("status"),
        "generated_at_utc": manifest.get("generated_at_utc"),
    })
    write_json(index_path, {"generated_at_utc": utc_now(), "runs": sorted(runs, key=lambda run: str(run.get("annotator")))})


def reconstruct_legacy_manifests(input_path: Path) -> list[Path]:
    generated_at = utc_now()
    written = []
    for annotator in ("a", "b", "c"):
        paths = annotation_paths(annotator)
        rows = read_jsonl(paths["labels"])
        valid = [row for row in rows if row.get("status") == "ok"]
        if not rows:
            continue
        requested_models = sorted({str(row.get("requested_model")) for row in rows if row.get("requested_model")})
        response_models = sorted({str(row.get("response_model")) for row in rows if row.get("response_model")})
        providers = sorted({str(row.get("provider")) for row in rows if row.get("provider")})
        provider = providers[0] if len(providers) == 1 else "mixed"
        requested_model = requested_models[0] if len(requested_models) == 1 else ",".join(requested_models)
        response_model = response_models[0] if len(response_models) == 1 else ",".join(response_models)
        provenance = model_provenance(provider, requested_model, response_model)
        manifest = {
            "generated_at_utc": generated_at,
            "run_id": f"legacy-reconstructed-{annotator}",
            "annotator": annotator,
            "provider": provider,
            "model": requested_model,
            "requested_model": requested_model,
            "response_models": response_models,
            **provenance,
            "provenance_status": "legacy_reconstructed",
            "sdk_name": "unknown",
            "sdk_version": "unknown",
            "endpoint_host": "unknown",
            "input": str(input_path),
            "input_sha256": sha256_file(input_path) if input_path.exists() else "unknown",
            "schema_sha256": next((str(row.get("schema_sha256")) for row in rows if row.get("schema_sha256")), "unknown"),
            "prompt_version": next((str(row.get("prompt_version")) for row in rows if row.get("prompt_version")), PROMPT_VERSION),
            "schema_version": next((str(row.get("schema_version")) for row in rows if row.get("schema_version")), SCHEMA_VERSION),
            "rows_input": len(rows),
            "labels_ok": len(valid),
            "labels_error": sum(1 for row in rows if row.get("status") == "error"),
            "prompt_packs": len(read_jsonl(paths["prompts"])),
            "status": "legacy_reconstructed",
            "command_config": {"reconstructed_from_existing_labels": True},
            "outputs": {key: str(path) for key, path in paths.items()},
            "output_sha256": {
                key: sha256_file(path)
                for key, path in paths.items()
                if key != "manifest" and path.exists()
            },
        }
        write_json(paths["manifest"], manifest)
        update_manifest_index(paths["manifest"], manifest)
        written.append(paths["manifest"])
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Run semantic news annotation or write offline prompt packs.")
    parser.add_argument("--input", default="multi_llm_evidence_extraction/data/sample_news_for_annotation.csv")
    parser.add_argument("--annotator", choices=["a", "b", "c"])
    parser.add_argument("--reconstruct-legacy-manifests", action="store_true")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--max-articles", type=int, default=None)
    parser.add_argument("--max-article-chars", type=int, default=12000)
    parser.add_argument("--allow-pending", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--only-missing", action="store_true")
    parser.add_argument("--anthropic-batch", action="store_true")
    args = parser.parse_args()
    if args.run_id:
        args.run_id = validate_safe_identifier(args.run_id, "run_id")
    if args.live and args.anthropic_batch:
        parser.error("--live cannot be combined with --anthropic-batch; batch mode only writes offline requests")
    ensure_dirs()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if args.reconstruct_legacy_manifests:
        paths = reconstruct_legacy_manifests(input_path)
        print(json.dumps({"status": "legacy_reconstructed", "manifests": [str(path) for path in paths]}, ensure_ascii=False, indent=2))
        return 0
    if not args.annotator:
        parser.error("--annotator is required unless --reconstruct-legacy-manifests is used")
    schema = load_schema("semantic_news_annotation_schema.json")
    schema_hash = sha256_file(ROOT / "multi_llm_evidence_extraction" / "schemas" / "semantic_news_annotation_schema.json")
    provider, model = resolve_provider_model(args.provider, args.model)
    output_dir = args.output_dir
    if output_dir is not None and not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    paths = annotation_paths(args.annotator, args.run_id, output_dir)
    if args.run_id and output_dir is None:
        paths = annotation_paths(args.annotator, args.run_id, OUTPUT_DIR / "annotation_runs" / args.run_id)
    if (args.resume or args.only_missing) and not args.run_id:
        parser.error("--resume/--only-missing require --run-id so provenance identity is stable")
    if args.anthropic_batch and provider != "anthropic":
        parser.error("--anthropic-batch requires resolved Anthropic provider")
    if args.anthropic_batch and not (args.run_id or args.output_dir):
        parser.error("--anthropic-batch requires --run-id or --output-dir")
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    if args.max_articles:
        df = df.head(args.max_articles)
    if str(args.run_id or "").startswith("v6_h2_confirmation_"):
        preflight = run_confirmation_annotation_preflight(provider, model, len(df))
    else:
        preflight = None
    canonical_paths = set(annotation_paths(args.annotator).values())
    if (args.run_id or args.output_dir) and canonical_paths & set(paths.values()):
        parser.error("run-scoped outputs must not collide with canonical annotation artifacts")
    input_file_sha = sha256_file(input_path)
    if args.resume or args.only_missing:
        prior_artifacts_exist = any(paths[key].exists() for key in ("labels", "raw", "prompts"))
        if prior_artifacts_exist and not paths["manifest"].exists():
            raise ValueError("cannot resume annotation artifacts without manifest")
        validate_resume_manifest(
            paths["manifest"],
            {
                "run_id": args.run_id or "canonical_legacy",
                "annotator": args.annotator,
                "provider": provider,
                "requested_model": model,
                "input_sha256": input_file_sha,
                "schema_sha256": schema_hash,
                "prompt_version": PROMPT_VERSION,
                "schema_version": SCHEMA_VERSION,
            },
            {
                "anthropic_batch": bool(args.anthropic_batch),
                "max_articles": args.max_articles,
                "max_article_chars": args.max_article_chars,
            },
        )
    prior_labels = read_jsonl(paths["labels"]) if (args.resume or args.only_missing) else []
    prior_raws = read_jsonl(paths["raw"]) if (args.resume or args.only_missing) else []
    prior_prompts = read_jsonl(paths["prompts"]) if (args.resume or args.only_missing) else []
    completed_keys = {
        resume_key(row) for row in prior_labels
        if row.get("status") == "ok" or bool(row.get("terminal"))
    }
    labels: list[dict[str, Any]] = list(prior_labels)
    raws: list[dict[str, Any]] = list(prior_raws)
    prompts: list[dict[str, Any]] = list(prior_prompts)
    batch_requests: list[dict[str, Any]] = []
    client = provider_module = None
    live = bool(args.live and not args.offline)
    status = "ok"
    if live:
        try:
            client, provider_module = llm_provider.make_llm_client(provider)
        except Exception as exc:
            status = "pending_auth" if provider_is_auth_error(provider, exc) else "pending_provider_error"
            live = False
    for _, series in df.iterrows():
        row = dict(series)
        row["news_id"] = row.get("news_id") or stable_news_id(row)
        prompt, payload = build_user_prompt(row, args.max_article_chars)
        input_sha = sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        prompt_sha = sha256_text(SYSTEM_PROMPT + "\n" + prompt)
        base = {
            "annotator": args.annotator,
            "news_id": row["news_id"],
            "ticker": str(row.get("ticker", "")).upper(),
            "article_date": str(row.get("date", ""))[:10],
            "provider": provider,
            "requested_model": model,
            "prompt_version": PROMPT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "schema_sha256": schema_hash,
            "prompt_sha256": prompt_sha,
            "input_sha256": input_sha,
            "content_hash": str(row.get("content_hash", "")).strip(),
            "run_id": args.run_id or "canonical_legacy",
        }
        key = resume_key(base)
        if key in completed_keys:
            continue
        # Replace stale pending/error row for same exact provenance key.
        labels = [item for item in labels if resume_key(item) != key]
        raws = [item for item in raws if resume_key(item) != key]
        prompts = [item for item in prompts if resume_key(item) != key]
        custom_id = f"{args.run_id or 'canonical'}:{args.annotator}:{row['news_id']}"
        if args.anthropic_batch:
            batch_requests.append(anthropic_batch_request(custom_id, model, SYSTEM_PROMPT, prompt, schema))
        if not live:
            pending_status = status if status != "ok" else "pending_offline"
            prompts.append({**base, "custom_id": custom_id, "batch_mode": bool(args.anthropic_batch), "system_prompt": SYSTEM_PROMPT, "user_prompt": prompt, "payload": payload, "status": pending_status})
            if args.run_id or args.output_dir:
                labels.append({**base, "custom_id": custom_id, "status": pending_status, "terminal": False, "error": ""})
            continue
        try:
            result = llm_provider.call_score(provider, client, provider_module, model, SYSTEM_PROMPT, prompt, 1800, "low", schema)
            parsed = normalize_annotation(result["parsed"], row)
            validate_json(parsed, schema)
            response_status, terminal = terminal_response_status(result.get("stop_reason", "end_turn"))
            labels.append({**parsed, **base, "response_model": result.get("response_model", model), "request_id": result.get("request_id", ""), "usage": result.get("usage", {}), "stop_reason": result.get("stop_reason", ""), "status": response_status, "terminal": terminal, "error": ""})
            raws.append({**base, "raw": result, "status": response_status, "terminal": terminal})
        except Exception as exc:
            error = error_provenance(exc)
            lowered = error["error_message"].lower()
            error_status = "refusal" if "refusal while scoring" in lowered else ("truncated" if "response truncated" in lowered else "error")
            terminal = error_status in {"refusal", "truncated"} or not error["retryable"]
            labels.append({**base, **error, "status": error_status, "terminal": terminal, "error": error["error_message"]})
            raws.append({**base, **error, "raw_error": _sanitize_error_text(exc), "status": error_status, "terminal": terminal})
    write_jsonl(paths["labels"], labels)
    write_jsonl(paths["raw"], raws)
    write_jsonl(paths["prompts"], prompts)
    if args.anthropic_batch:
        write_jsonl(paths["batch"], batch_requests)
    response_models = sorted({str(row.get("response_model")) for row in labels if row.get("response_model")})
    response_model = response_models[0] if len(response_models) == 1 else (",".join(response_models) or model)
    provenance = route_provenance(provider, response_model)
    generated_at = utc_now()
    confirmation_fields = (
        confirmation_annotation_manifest_fields(provider, response_model, len(df))
        if preflight is not None
        else {}
    )
    run_id = args.run_id or f"{args.annotator}-{generated_at.replace(':', '').replace('+', '_')}"
    output_hashes = {
        key: sha256_file(path)
        for key, path in paths.items()
        if key != "manifest" and path.exists()
    }
    manifest = {
        "generated_at_utc": generated_at,
        "run_id": run_id,
        "annotator": args.annotator,
        "provider": provider,
        "model": model,
        "requested_model": model,
        "response_models": response_models,
        **provenance,
        "sdk_name": llm_provider.provider_sdk_name(provider),
        "sdk_version": sdk_version(provider),
        "endpoint_host": endpoint_host(provider),
        "input": str(input_path),
        "input_sha256": input_file_sha,
        "schema_sha256": schema_hash,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "rows_input": int(len(df)),
        "labels_ok": sum(1 for r in labels if r.get("status") == "ok"),
        "labels_error": sum(1 for r in labels if r.get("status") == "error"),
        "labels_terminal": sum(bool(r.get("terminal")) for r in labels),
        "labels_refusal": sum(r.get("status") == "refusal" for r in labels),
        "labels_truncated": sum(r.get("status") == "truncated" for r in labels),
        "retryable_failures": sum(r.get("status") == "error" and not bool(r.get("terminal")) for r in labels),
        "prompt_packs": len(prompts),
        "status": (
            ("live_completed_with_errors" if any(row.get("status") == "error" for row in labels) else "live_completed")
            if live and any(row.get("status") == "ok" for row in labels)
            else ("live_failed" if live else (status if status != "ok" else "pending_offline"))
        ),
        "command_config": {
            "offline": bool(args.offline),
            "live": bool(args.live),
            "run_id": args.run_id,
            "output_dir": str(output_dir) if output_dir else None,
            "resume": bool(args.resume),
            "only_missing": bool(args.only_missing),
            "anthropic_batch": bool(args.anthropic_batch),
            "batch_submit_enabled": False,
            "token_count_endpoint": "messages.count_tokens" if provider == "anthropic" else None,
            "max_articles": args.max_articles,
            "max_article_chars": args.max_article_chars,
            "confirmation_preflight": preflight,
        },
        **confirmation_fields,
        "outputs": {key: str(path) for key, path in paths.items()},
        "output_sha256": output_hashes,
    }
    write_json(paths["manifest"], manifest)
    update_manifest_index(paths["manifest"], manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if manifest["labels_error"]:
        return 2
    if manifest["status"].startswith("pending") and not args.allow_pending:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
