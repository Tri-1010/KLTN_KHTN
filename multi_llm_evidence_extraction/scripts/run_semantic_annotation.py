from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
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


def annotation_paths(annotator: str) -> dict[str, Path]:
    return {
        "labels": OUTPUT_DIR / f"labels_annotator_{annotator}.jsonl",
        "raw": OUTPUT_DIR / f"raw_responses_annotator_{annotator}.jsonl",
        "prompts": OUTPUT_DIR / f"prompt_packs_annotator_{annotator}.jsonl",
        "manifest": OUTPUT_DIR / f"annotation_manifest_{annotator}.json",
    }


def endpoint_host(provider: str) -> str:
    env_name = "ANTHROPIC_BASE_URL" if provider == "anthropic" else f"{provider.upper()}_BASE_URL"
    value = os.getenv(env_name, "")
    return urlparse(value).hostname or "default"


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
    index_path = OUTPUT_DIR / "annotation_manifest_index.json"
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
    args = parser.parse_args()
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
    paths = annotation_paths(args.annotator)
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    if args.max_articles:
        df = df.head(args.max_articles)
    labels: list[dict[str, Any]] = []
    raws: list[dict[str, Any]] = []
    prompts: list[dict[str, Any]] = []
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
        }
        if not live:
            prompts.append({**base, "system_prompt": SYSTEM_PROMPT, "user_prompt": prompt, "payload": payload, "status": status if status != "ok" else "pending_offline"})
            continue
        try:
            result = llm_provider.call_score(provider, client, provider_module, model, SYSTEM_PROMPT, prompt, 1800, "low", schema)
            parsed = normalize_annotation(result["parsed"], row)
            validate_json(parsed, schema)
            labels.append({**parsed, **base, "response_model": result.get("response_model", model), "request_id": result.get("request_id", ""), "status": "ok", "error": ""})
            raws.append({**base, "raw": result, "status": "ok"})
        except Exception as exc:
            labels.append({**base, "status": "error", "error": str(exc)[:1000]})
            raws.append({**base, "raw_error": str(exc)[:2000], "status": "error"})
    write_jsonl(paths["labels"], labels)
    write_jsonl(paths["raw"], raws)
    write_jsonl(paths["prompts"], prompts)
    response_models = sorted({str(row.get("response_model")) for row in labels if row.get("response_model")})
    response_model = response_models[0] if len(response_models) == 1 else (",".join(response_models) or model)
    provenance = model_provenance(provider, model, response_model)
    generated_at = utc_now()
    run_id = f"{args.annotator}-{generated_at.replace(':', '').replace('+', '_')}"
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
        "input_sha256": sha256_file(input_path),
        "schema_sha256": schema_hash,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "rows_input": int(len(df)),
        "labels_ok": sum(1 for r in labels if r.get("status") == "ok"),
        "labels_error": sum(1 for r in labels if r.get("status") == "error"),
        "prompt_packs": len(prompts),
        "status": "live_completed" if labels else (status if status != "ok" else "pending_offline"),
        "command_config": {
            "offline": bool(args.offline),
            "live": bool(args.live),
            "max_articles": args.max_articles,
            "max_article_chars": args.max_article_chars,
        },
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
