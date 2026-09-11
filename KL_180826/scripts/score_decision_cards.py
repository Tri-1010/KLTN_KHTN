"""Score decision-support cards with fixed rubric.

Scores rule-based baseline, LLM ML-only, and LLM full-evidence cards against
prompt-safe evidence packs. Uses official provider SDKs when available; offline
mode writes scoring prompt packs instead of fake scores.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from llm_provider import (
        SUPPORTED_PROVIDERS,
        artifact_ref,
        call_score,
        is_auth_error,
        load_env_file,
        make_llm_client,
        provider_sdk_name,
        provider_temperature,
        resolve_model,
        resolve_provider,
    )
except ModuleNotFoundError:  # pragma: no cover - import path when loaded as package in tests
    from scripts.llm_provider import (
        SUPPORTED_PROVIDERS,
        artifact_ref,
        call_score,
        is_auth_error,
        load_env_file,
        make_llm_client,
        provider_sdk_name,
        provider_temperature,
        resolve_model,
        resolve_provider,
    )

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "reports" / "decision_support" / "generated"
INITIAL_PACKS = GENERATED / "evidence_packs_initial.json"
RULE_BASED_CARDS = GENERATED / "decision_cards.md"

DEFAULT_MAX_TOKENS = 8000
DEFAULT_EFFORT = "high"

SYSTEM_PROMPT = """Bạn là người chấm chất lượng decision card trong nghiên cứu học thuật.
Chỉ chấm chất lượng hỗ trợ quyết định dựa trên evidence pack được cung cấp.
Không chấm return, không dùng outcome tương lai, không suy diễn ngoài evidence.
Trả JSON đúng schema.
"""

RUBRIC_PROMPT = """Chấm decision card theo rubric 1-5.

Tiêu chí:
1. faithfulness: bám sát evidence pack.
2. hallucination_control: không thêm dữ kiện ngoài evidence.
3. ml_explanation: giải thích xác suất/rank/drivers.
4. risk_awareness: nêu rủi ro cụ thể, bám evidence/data quality.
5. monitoring_usefulness: trigger theo dõi cụ thể và đo được.
6. clarity_usefulness: rõ ràng, hữu ích, dễ hậu kiểm.

Trả JSON với các field:
- faithfulness, hallucination_control, ml_explanation, risk_awareness, monitoring_usefulness, clarity_usefulness: số nguyên 1-5.
- overall: số nguyên 1-5.
- major_issue: string, "none" nếu không có.
- major_hallucinations: array string.
- missing_evidence_refs: array string.
- overall_comment: string.

Evidence pack prompt-safe:
{pack_json}

Decision card type: {card_type}

Decision card:
{card_markdown}
"""

RUBRIC_SCHEMA = {
    "type": "object",
    "properties": {
        "faithfulness": {"type": "integer", "minimum": 1, "maximum": 5},
        "hallucination_control": {"type": "integer", "minimum": 1, "maximum": 5},
        "ml_explanation": {"type": "integer", "minimum": 1, "maximum": 5},
        "risk_awareness": {"type": "integer", "minimum": 1, "maximum": 5},
        "monitoring_usefulness": {"type": "integer", "minimum": 1, "maximum": 5},
        "clarity_usefulness": {"type": "integer", "minimum": 1, "maximum": 5},
        "overall": {"type": "integer", "minimum": 1, "maximum": 5},
        "major_issue": {"type": "string"},
        "major_hallucinations": {"type": "array", "items": {"type": "string"}},
        "missing_evidence_refs": {"type": "array", "items": {"type": "string"}},
        "overall_comment": {"type": "string"},
    },
    "required": [
        "faithfulness",
        "hallucination_control",
        "ml_explanation",
        "risk_awareness",
        "monitoring_usefulness",
        "clarity_usefulness",
        "overall",
        "major_issue",
        "major_hallucinations",
        "missing_evidence_refs",
        "overall_comment",
    ],
    "additionalProperties": False,
}

SCORE_FIELDS = [
    "faithfulness",
    "hallucination_control",
    "ml_explanation",
    "risk_awareness",
    "monitoring_usefulness",
    "clarity_usefulness",
    "overall",
]


def sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def prefixed_path(output_prefix: str | None, name: str) -> Path:
    prefix = f"{output_prefix}_" if output_prefix else ""
    return GENERATED / f"{prefix}{name}"


def llm_jsonl_paths(output_prefix: str | None) -> tuple[Path, Path]:
    return prefixed_path(output_prefix, "llm_cards_ml_only.jsonl"), prefixed_path(output_prefix, "llm_cards_full_evidence.jsonl")


def score_output_paths(output_prefix: str | None) -> tuple[Path, Path, Path]:
    return (
        prefixed_path(output_prefix, "llm_rubric_scores.csv"),
        prefixed_path(output_prefix, "llm_rubric_summary.md"),
        prefixed_path(output_prefix, "llm_rubric_prompt_packs.jsonl"),
    )


def parse_rule_based_cards(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    marker = "\n## Decision Card: "
    chunks = text.split(marker)
    rows = []
    for chunk in chunks[1:]:
        first_line, _, rest = chunk.partition("\n")
        decision_id = first_line.strip()
        card = f"## Decision Card: {decision_id}\n{rest}".strip()
        rows.append({"decision_id": decision_id, "card_type": "rule_based_baseline", "card_markdown": card})
    return rows


def collect_cards(output_prefix: str | None = None, decision_ids: set[str] | None = None) -> list[dict[str, Any]]:
    cards = parse_rule_based_cards(RULE_BASED_CARDS)
    ml_only_jsonl, full_jsonl = llm_jsonl_paths(output_prefix)
    for row in read_jsonl(ml_only_jsonl):
        cards.append({"decision_id": row["decision_id"], "card_type": "llm_ml_only", "card_markdown": row["card_markdown"]})
    for row in read_jsonl(full_jsonl):
        cards.append({"decision_id": row["decision_id"], "card_type": "llm_full_evidence", "card_markdown": row["card_markdown"]})
    if decision_ids:
        cards = [card for card in cards if card["decision_id"] in decision_ids]
    return cards


def build_prompt(pack: dict[str, Any], card: dict[str, Any]) -> tuple[str, str]:
    pack_json = json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True)
    prompt = RUBRIC_PROMPT.format(
        pack_json=pack_json,
        card_type=card["card_type"],
        card_markdown=card["card_markdown"],
    )
    return prompt, sha256_text(SYSTEM_PROMPT + "\n" + prompt)


def clamp_score(value: int) -> int:
    return max(1, min(5, value))


def validate_score(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Scoring response must be a JSON object")
    missing = [field for field in RUBRIC_SCHEMA["required"] if field not in raw]
    if missing:
        raise ValueError(f"Scoring response missing required fields: {', '.join(missing)}")
    unexpected = sorted(set(raw) - set(RUBRIC_SCHEMA["properties"]))
    if unexpected:
        raise ValueError(f"Scoring response has unexpected fields: {', '.join(unexpected)}")
    for field in SCORE_FIELDS:
        value = raw[field]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"Scoring field `{field}` must be an integer")
        if not 1 <= value <= 5:
            raise ValueError(f"Scoring field `{field}` must be between 1 and 5")
    for field in ("major_issue", "overall_comment"):
        if not isinstance(raw[field], str):
            raise ValueError(f"Scoring field `{field}` must be a string")
    for field in ("major_hallucinations", "missing_evidence_refs"):
        value = raw[field]
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"Scoring field `{field}` must be an array of strings")
    return raw


def normalize_score(raw: dict[str, Any]) -> dict[str, Any]:
    result = dict(validate_score(raw))
    for field in SCORE_FIELDS:
        result[field] = clamp_score(result[field])
    return result


def write_scores_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "decision_id",
        "card_type",
        "faithfulness",
        "hallucination_control",
        "ml_explanation",
        "risk_awareness",
        "monitoring_usefulness",
        "clarity_usefulness",
        "overall",
        "major_issue",
        "major_hallucination_count",
        "missing_evidence_ref_count",
        "overall_comment",
        "provider",
        "model",
        "request_id",
        "scored_at_utc",
        "prompt_sha256",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, Any]], status: str, provider: str) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["card_type"]].append(row)
    lines = [
        "# LLM Decision Card Rubric Summary\n",
        f"\nStatus: `{status}`\n",
        f"\nProvider: `{provider}`\n",
        "\nRubric đo chất lượng hỗ trợ quyết định của card, không đo lợi nhuận và không chứng minh LLM tạo alpha.\n",
        "\n## Mean scores by card type\n\n",
        "| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |\n",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n",
    ]
    for card_type, items in sorted(grouped.items()):
        n = len(items)
        means = {field: sum(float(r[field]) for r in items) / n for field in SCORE_FIELDS}
        hallucinations = sum(int(r["major_hallucination_count"]) for r in items)
        missing_refs = sum(int(r["missing_evidence_ref_count"]) for r in items)
        lines.append(
            f"| {card_type} | {n} | {means['faithfulness']:.2f} | {means['hallucination_control']:.2f} | {means['ml_explanation']:.2f} | {means['risk_awareness']:.2f} | {means['monitoring_usefulness']:.2f} | {means['clarity_usefulness']:.2f} | {means['overall']:.2f} | {hallucinations} | {missing_refs} |\n"
        )
    if not rows:
        lines.append("| none | 0 | NA | NA | NA | NA | NA | NA | NA | NA | NA |\n")
    lines.extend(
        [
            "\n## Guardrails\n\n",
            "- Scoring dùng `evidence_packs_initial.json`, không dùng audit pack có outcome.\n",
            "- Initial decision cards không được chấm dựa trên realized return tương lai.\n",
            "- So sánh `llm_full_evidence` với `llm_ml_only` chỉ phản ánh chất lượng giải thích/risk/monitoring trong rubric.\n",
        ]
    )
    path.write_text("".join(lines), encoding="utf-8")


def write_offline_prompts(path: Path, cards: list[dict[str, Any]], packs_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for card in cards:
        pack = packs_by_id.get(card["decision_id"])
        if not pack:
            continue
        prompt, prompt_hash = build_prompt(pack, card)
        rows.append(
            {
                "decision_id": card["decision_id"],
                "card_type": card["card_type"],
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": prompt,
                "prompt_sha256": prompt_hash,
            }
        )
    write_jsonl(path, rows)
    return rows


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


def run_scoring(
    provider: str | None = None,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    effort: str = DEFAULT_EFFORT,
    offline: bool = False,
    env_file: Path | None = None,
    output_prefix: str | None = None,
    decision_ids: set[str] | None = None,
) -> dict[str, Any]:
    load_env_file(ROOT, env_file)
    resolved_provider = resolve_provider(provider)
    resolved_model = resolve_model(resolved_provider, model)
    out_scores, out_summary, out_prompts = score_output_paths(output_prefix)

    GENERATED.mkdir(parents=True, exist_ok=True)
    if not INITIAL_PACKS.exists():
        raise FileNotFoundError(f"Missing prompt-safe packs: {INITIAL_PACKS}")
    packs = read_json(INITIAL_PACKS)
    packs_by_id = {pack["decision_id"]: pack for pack in packs}
    cards = [card for card in collect_cards(output_prefix=output_prefix, decision_ids=decision_ids) if card["decision_id"] in packs_by_id]

    result: dict[str, Any] = {
        "status": "started",
        "provider": resolved_provider,
        "sdk": provider_sdk_name(resolved_provider),
        "requested_model": resolved_model,
        "temperature": provider_temperature(resolved_provider),
        "scored_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "num_cards": len(cards),
        "decision_ids_filter": sorted(decision_ids) if decision_ids else None,
        "outputs": [],
        "failures": [],
    }

    if offline:
        rows = write_offline_prompts(out_prompts, cards, packs_by_id)
        result.update({"status": "scoring_pending_offline", "prompt_packs": artifact_ref(ROOT, out_prompts), "num_prompt_packs": len(rows)})
        result["outputs"].append(artifact_ref(ROOT, out_prompts))
        write_scores_csv(out_scores, [])
        result["outputs"].append(artifact_ref(ROOT, out_scores))
        write_summary(out_summary, [], result["status"], resolved_provider)
        result["outputs"].append(artifact_ref(ROOT, out_summary))
        return result

    try:
        client, provider_module = make_llm_client(resolved_provider)
    except Exception as exc:
        rows = write_offline_prompts(out_prompts, cards, packs_by_id)
        result.update({"status": "scoring_pending_auth_or_dependency", "prompt_packs": artifact_ref(ROOT, out_prompts), "num_prompt_packs": len(rows)})
        result["failures"].append({"stage": "client_init", "error": str(exc)})
        result["outputs"].append(artifact_ref(ROOT, out_prompts))
        write_summary(out_summary, [], result["status"], resolved_provider)
        result["outputs"].append(artifact_ref(ROOT, out_summary))
        return result

    score_rows = []
    for card in cards:
        pack = packs_by_id[card["decision_id"]]
        prompt, prompt_hash = build_prompt(pack, card)
        try:
            scored = call_score(resolved_provider, client, provider_module, resolved_model, SYSTEM_PROMPT, prompt, max_tokens, effort, RUBRIC_SCHEMA)
            score = normalize_score(scored["parsed"])
            row = {
                "decision_id": card["decision_id"],
                "card_type": card["card_type"],
                **{field: score[field] for field in SCORE_FIELDS},
                "major_issue": score["major_issue"],
                "major_hallucination_count": len(score.get("major_hallucinations", [])),
                "missing_evidence_ref_count": len(score.get("missing_evidence_refs", [])),
                "overall_comment": score.get("overall_comment", ""),
                "provider": resolved_provider,
                "model": scored["response_model"],
                "request_id": scored["request_id"],
                "scored_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "prompt_sha256": prompt_hash,
            }
            score_rows.append(row)
        except Exception as exc:
            if is_auth_error(resolved_provider, exc, provider_module):
                rows = write_offline_prompts(out_prompts, cards, packs_by_id)
                result.update({"status": "scoring_pending_auth", "prompt_packs": artifact_ref(ROOT, out_prompts), "num_prompt_packs": len(rows)})
                result["outputs"].append(artifact_ref(ROOT, out_prompts))
                result["failures"].append({"stage": "score", "decision_id": card["decision_id"], "error": str(exc)})
                write_summary(out_summary, score_rows, result["status"], resolved_provider)
                result["outputs"].append(artifact_ref(ROOT, out_summary))
                if score_rows:
                    write_scores_csv(out_scores, score_rows)
                    result["outputs"].append(artifact_ref(ROOT, out_scores))
                return result
            result["failures"].append({"stage": "score", "decision_id": card["decision_id"], "error": str(exc)})

    if score_rows:
        write_scores_csv(out_scores, score_rows)
        result["outputs"].append(artifact_ref(ROOT, out_scores))
    write_summary(out_summary, score_rows, "completed" if not result["failures"] else "completed_with_failures", resolved_provider)
    result["outputs"].append(artifact_ref(ROOT, out_summary))
    result["num_scores"] = len(score_rows)
    result["status"] = "completed" if not result["failures"] else "completed_with_failures"
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score decision-support cards with rubric.")
    parser.add_argument("--provider", choices=sorted(SUPPORTED_PROVIDERS), default=None)
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--effort", default=DEFAULT_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-prefix", default=None)
    parser.add_argument("--decision-id", action="append", help="Decision ID or comma-separated IDs. Can repeat.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decision_ids = parse_decision_ids(args.decision_id)
    result = run_scoring(
        provider=args.provider,
        model=args.model,
        max_tokens=args.max_tokens,
        effort=args.effort,
        offline=args.offline,
        env_file=args.env_file,
        output_prefix=args.output_prefix,
        decision_ids=decision_ids,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"].startswith("completed") or (args.offline and result["status"] == "scoring_pending_offline"):
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
