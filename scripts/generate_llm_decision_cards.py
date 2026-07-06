"""Generate LLM decision cards from prompt-safe evidence packs.

Uses official Anthropic Python SDK. If credentials are unavailable, writes prompt
packs for offline/manual execution and records pending status instead of creating
fake LLM outputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "reports" / "decision_support" / "generated"
INITIAL_PACKS = GENERATED / "evidence_packs_initial.json"
ML_ONLY_PACKS = GENERATED / "evidence_packs_ml_only.json"
OUT_MANIFEST = GENERATED / "llm_generation_manifest.json"
RAW_RESPONSES = GENERATED / "llm_raw_responses.jsonl"

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 12000
DEFAULT_EFFORT = "high"

VARIANT_TO_INPUT = {
    "ml_only": ML_ONLY_PACKS,
    "full_evidence": INITIAL_PACKS,
}

VARIANT_TO_CARD_TYPE = {
    "ml_only": "llm_ml_only",
    "full_evidence": "llm_full_evidence",
}

SYSTEM_PROMPT = """Bạn là trợ lý phân tích đầu tư trong nghiên cứu học thuật.
Nhiệm vụ của bạn là tạo decision card từ evidence pack đã cho.

Ràng buộc bắt buộc:
- Chỉ sử dụng thông tin trong evidence pack.
- Không thêm dữ kiện ngoài evidence pack.
- Không dự báo giá tuyệt đối.
- Không cam kết lợi nhuận.
- Không đưa ra khuyến nghị đầu tư chắc chắn.
- Mỗi luận điểm chính phải dẫn evidence_id hoặc tên trường dữ liệu liên quan.
- Nếu evidence thiếu, yếu hoặc mâu thuẫn, phải ghi rõ.
- Không được sử dụng outcome tương lai nếu prompt tạo decision card ban đầu.
- Văn phong thận trọng, rõ ràng, phục vụ hỗ trợ quyết định.
"""

CARD_PROMPT = """Hãy tạo một decision card bằng tiếng Việt từ evidence pack dưới đây.

Yêu cầu output theo đúng cấu trúc:
1. Tóm tắt tín hiệu
2. Luận điểm đầu tư chính
3. Yếu tố hỗ trợ
4. Yếu tố cần lưu ý / rủi ro
5. Trigger theo dõi
6. Thời điểm review
7. Kết luận hỗ trợ quyết định
8. Disclaimer

Quy tắc:
- Không sử dụng thông tin ngoài evidence pack.
- Không dự báo giá tuyệt đối.
- Không dùng từ ngữ chắc chắn như “sẽ tăng”, “chắc chắn mua”.
- Mỗi supporting factor và risk phải có evidence reference.
- Với tin tức, ưu tiên `article_summary`, `key_facts`, `risk_flags` và `event_type`; không suy diễn vượt quá các trường này.
- `full_text_ref`, `content_hash`, `full_text_chars` chỉ là metadata audit; không được giả định nội dung toàn văn nếu full text không nằm trong prompt.
- Nếu không đủ evidence định tính, ghi rõ “evidence tin tức chưa đủ mạnh”.
- Không được nhắc đến realized return hoặc outcome tương lai.

Evidence pack:
{pack_json}
"""

FORBIDDEN_PROMPT_TOKENS = ("outcome_for_review_only", "realized", "review_only", "future_return", "future_label")


def sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def selected_variants(variant: str) -> list[str]:
    if variant == "both":
        return ["ml_only", "full_evidence"]
    return [variant]


def parse_decision_ids(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    result: set[str] = set()
    for value in values:
        for part in value.split(","):
            part = part.strip()
            if part:
                result.add(part)
    return result or None


def select_packs(packs: list[dict[str, Any]], max_packs: int | None, decision_ids: set[str] | None) -> list[dict[str, Any]]:
    if decision_ids:
        packs = [p for p in packs if p.get("decision_id") in decision_ids]
    if max_packs is not None and max_packs > 0:
        packs = packs[:max_packs]
    return packs


def prompt_for_pack(pack: dict[str, Any]) -> tuple[str, str, str]:
    pack_json = json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True)
    lower = pack_json.lower()
    leaked = [token for token in FORBIDDEN_PROMPT_TOKENS if token in lower]
    if leaked:
        raise ValueError(f"Prompt pack leaks forbidden tokens for {pack.get('decision_id')}: {leaked}")
    prompt = CARD_PROMPT.format(pack_json=pack_json)
    return prompt, pack_json, sha256_text(pack_json)


def output_paths(variant: str, output_prefix: str | None) -> tuple[Path, Path, Path]:
    suffix = variant
    prefix = f"{output_prefix}_" if output_prefix else ""
    md = GENERATED / f"{prefix}llm_cards_{suffix}.md"
    jsonl = GENERATED / f"{prefix}llm_cards_{suffix}.jsonl"
    prompts = GENERATED / f"{prefix}llm_prompt_packs_{suffix}.jsonl"
    return md, jsonl, prompts


def write_offline_prompts(variant: str, packs: list[dict[str, Any]], output_prefix: str | None) -> tuple[Path, list[dict[str, Any]]]:
    _, _, prompts_path = output_paths(variant, output_prefix)
    rows = []
    for pack in packs:
        prompt, pack_json, pack_hash = prompt_for_pack(pack)
        rows.append(
            {
                "decision_id": pack["decision_id"],
                "card_type": VARIANT_TO_CARD_TYPE[variant],
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": prompt,
                "pack_sha256": pack_hash,
                "prompt_sha256": sha256_text(SYSTEM_PROMPT + "\n" + prompt),
                "pack_json": pack_json,
            }
        )
    write_jsonl(prompts_path, rows)
    return prompts_path, rows


def make_client():
    try:
        import anthropic
    except ModuleNotFoundError as exc:
        raise RuntimeError("Missing dependency `anthropic`. Install requirements or run offline mode.") from exc
    return anthropic.Anthropic(), anthropic


def is_auth_error(exc: Exception, anthropic_module: Any | None) -> bool:
    if anthropic_module is not None and isinstance(exc, (anthropic_module.AuthenticationError, anthropic_module.PermissionDeniedError)):
        return True
    message = str(exc).lower()
    auth_markers = (
        "no active credentials",
        "invalid api key",
        "invalid x-api-key",
        "authentication",
        "permission denied",
        "unauthorized",
        "401",
        "403",
    )
    return any(marker in message for marker in auth_markers)


def call_anthropic(client: Any, anthropic_module: Any, model: str, prompt: str, max_tokens: int, effort: str) -> dict[str, Any]:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}],
    )
    request_id = getattr(response, "_request_id", "")
    if getattr(response, "stop_reason", None) == "refusal":
        details = getattr(response, "stop_details", None)
        raise RuntimeError(f"Claude refusal: {details}")
    text_parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    text = "\n".join(text_parts).strip()
    if not text:
        raise RuntimeError("Claude response contained no text block")
    return {
        "text": text,
        "request_id": request_id,
        "response_model": getattr(response, "model", model),
        "stop_reason": getattr(response, "stop_reason", None),
        "usage": response.usage.to_dict() if hasattr(getattr(response, "usage", None), "to_dict") else str(getattr(response, "usage", "")),
    }


def generate_variant(
    variant: str,
    packs: list[dict[str, Any]],
    client: Any,
    anthropic_module: Any,
    model: str,
    max_tokens: int,
    effort: str,
    output_prefix: str | None,
) -> tuple[list[dict[str, Any]], Path, Path]:
    md_path, jsonl_path, _ = output_paths(variant, output_prefix)
    card_type = VARIANT_TO_CARD_TYPE[variant]
    if md_path.exists():
        md_path.unlink()
    if jsonl_path.exists():
        jsonl_path.unlink()
    cards_md = [
        f"# LLM Decision Cards — {card_type}\n\n",
        f"> Generated with Anthropic SDK model `{model}` from prompt-safe `{variant}` evidence packs. Outcome fields removed.\n\n",
    ]
    rows: list[dict[str, Any]] = []
    for pack in packs:
        prompt, pack_json, pack_hash = prompt_for_pack(pack)
        prompt_hash = sha256_text(SYSTEM_PROMPT + "\n" + prompt)
        generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        result = call_anthropic(client, anthropic_module, model, prompt, max_tokens, effort)
        row = {
            "decision_id": pack["decision_id"],
            "card_type": card_type,
            "card_markdown": result["text"],
            "requested_model": model,
            "response_model": result["response_model"],
            "request_id": result["request_id"],
            "generated_at_utc": generated_at,
            "pack_sha256": pack_hash,
            "prompt_sha256": prompt_hash,
            "stop_reason": result["stop_reason"],
        }
        rows.append(row)
        append_jsonl(jsonl_path, row)
        append_jsonl(
            RAW_RESPONSES,
            {
                "decision_id": pack["decision_id"],
                "card_type": card_type,
                "request_id": result["request_id"],
                "response_model": result["response_model"],
                "usage": result["usage"],
                "recorded_at_utc": generated_at,
            },
        )
        cards_md.append(f"\n---\n\n## {pack['decision_id']}\n\n")
        cards_md.append(result["text"].strip() + "\n")
    md_path.write_text("".join(cards_md), encoding="utf-8")
    return rows, md_path, jsonl_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate LLM decision cards from decision-support evidence packs.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-packs", type=int, default=None, help="Limit packs per variant; omit for all packs.")
    parser.add_argument("--decision-id", action="append", help="Decision ID or comma-separated IDs. Can repeat.")
    parser.add_argument("--variant", choices=["ml_only", "full_evidence", "both"], default="both")
    parser.add_argument("--offline", action="store_true", help="Write prompt packs only; do not call API.")
    parser.add_argument("--score", action="store_true", help="Run rubric scorer after generation.")
    parser.add_argument("--output-prefix", default=None)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--effort", default=DEFAULT_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    GENERATED.mkdir(parents=True, exist_ok=True)
    if RAW_RESPONSES.exists():
        RAW_RESPONSES.unlink()
    decision_ids = parse_decision_ids(args.decision_id)
    variants = selected_variants(args.variant)
    manifest: dict[str, Any] = {
        "status": "started",
        "provider": "anthropic",
        "sdk": "anthropic-python",
        "requested_model": args.model,
        "max_tokens": args.max_tokens,
        "thinking": {"type": "adaptive"},
        "effort": args.effort,
        "temperature": "not_sent",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "variants": variants,
        "max_packs": args.max_packs,
        "decision_ids_filter": sorted(decision_ids) if decision_ids else None,
        "outcome_removed_from_prompt": True,
        "outputs": [],
        "cards": [],
        "prompt_packs": [],
        "failures": [],
    }

    packs_by_variant: dict[str, list[dict[str, Any]]] = {}
    for variant in variants:
        input_path = VARIANT_TO_INPUT[variant]
        if not input_path.exists():
            raise FileNotFoundError(f"Missing input pack for {variant}: {input_path}")
        packs = select_packs(read_json(input_path), args.max_packs, decision_ids)
        packs_by_variant[variant] = packs
        manifest.setdefault("input_packs", {})[variant] = {
            "path": str(input_path),
            "sha256": sha256_file(input_path),
            "selected_count": len(packs),
        }

    if args.offline:
        for variant, packs in packs_by_variant.items():
            prompts_path, rows = write_offline_prompts(variant, packs, args.output_prefix)
            manifest["prompt_packs"].append({"variant": variant, "path": str(prompts_path), "count": len(rows)})
            manifest["outputs"].append(str(prompts_path))
        manifest["status"] = "llm_run_pending_offline"
        write_json(OUT_MANIFEST, manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    client = None
    anthropic_module = None
    try:
        client, anthropic_module = make_client()
    except Exception as exc:
        for variant, packs in packs_by_variant.items():
            prompts_path, rows = write_offline_prompts(variant, packs, args.output_prefix)
            manifest["prompt_packs"].append({"variant": variant, "path": str(prompts_path), "count": len(rows)})
            manifest["outputs"].append(str(prompts_path))
        manifest["status"] = "llm_run_pending_auth_or_dependency"
        manifest["failures"].append({"stage": "client_init", "error": str(exc)})
        write_json(OUT_MANIFEST, manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 2

    auth_failed = False
    for variant, packs in packs_by_variant.items():
        try:
            rows, md_path, jsonl_path = generate_variant(
                variant,
                packs,
                client,
                anthropic_module,
                args.model,
                args.max_tokens,
                args.effort,
                args.output_prefix,
            )
            manifest["cards"].extend(
                {
                    "decision_id": row["decision_id"],
                    "card_type": row["card_type"],
                    "request_id": row["request_id"],
                    "response_model": row["response_model"],
                    "pack_sha256": row["pack_sha256"],
                    "prompt_sha256": row["prompt_sha256"],
                }
                for row in rows
            )
            manifest["outputs"].extend([str(md_path), str(jsonl_path)])
        except Exception as exc:
            if is_auth_error(exc, anthropic_module):
                auth_failed = True
                prompts_path, rows = write_offline_prompts(variant, packs, args.output_prefix)
                manifest["prompt_packs"].append({"variant": variant, "path": str(prompts_path), "count": len(rows)})
                manifest["outputs"].append(str(prompts_path))
            manifest["failures"].append({"stage": f"generate_{variant}", "error": str(exc)})
            if not auth_failed:
                continue

    if auth_failed and not manifest["cards"]:
        manifest["status"] = "llm_run_pending_auth"
    elif manifest["failures"]:
        manifest["status"] = "completed_with_failures"
    else:
        manifest["status"] = "completed"
    if RAW_RESPONSES.exists():
        manifest["outputs"].append(str(RAW_RESPONSES))
    write_json(OUT_MANIFEST, manifest)

    if args.score and manifest["cards"]:
        try:
            from score_decision_cards import run_scoring

            score_result = run_scoring(model=args.model, max_tokens=8000, effort=args.effort, offline=False)
            manifest["scoring"] = score_result
            manifest["outputs"].extend(score_result.get("outputs", []))
            write_json(OUT_MANIFEST, manifest)
        except Exception as exc:
            manifest["failures"].append({"stage": "score", "error": str(exc)})
            if manifest["status"] == "completed":
                manifest["status"] = "completed_generation_score_failed"
            write_json(OUT_MANIFEST, manifest)

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["status"].startswith("completed") else 2


if __name__ == "__main__":
    sys.exit(main())
