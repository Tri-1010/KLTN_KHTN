"""Score decision-support cards with fixed rubric.

Scores rule-based baseline, LLM ML-only, and LLM full-evidence cards against
prompt-safe evidence packs. Uses official Anthropic SDK when available; offline
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

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "reports" / "decision_support" / "generated"
INITIAL_PACKS = GENERATED / "evidence_packs_initial.json"
RULE_BASED_CARDS = GENERATED / "decision_cards.md"
LLM_ML_ONLY_JSONL = GENERATED / "llm_cards_ml_only.jsonl"
LLM_FULL_JSONL = GENERATED / "llm_cards_full_evidence.jsonl"
OUT_SCORES = GENERATED / "llm_rubric_scores.csv"
OUT_SUMMARY = GENERATED / "llm_rubric_summary.md"
OUT_PROMPTS = GENERATED / "llm_rubric_prompt_packs.jsonl"

DEFAULT_MODEL = "claude-opus-4-8"
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
        "faithfulness": {"type": "integer"},
        "hallucination_control": {"type": "integer"},
        "ml_explanation": {"type": "integer"},
        "risk_awareness": {"type": "integer"},
        "monitoring_usefulness": {"type": "integer"},
        "clarity_usefulness": {"type": "integer"},
        "overall": {"type": "integer"},
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


def collect_cards() -> list[dict[str, Any]]:
    cards = parse_rule_based_cards(RULE_BASED_CARDS)
    for row in read_jsonl(LLM_ML_ONLY_JSONL):
        cards.append({"decision_id": row["decision_id"], "card_type": "llm_ml_only", "card_markdown": row["card_markdown"]})
    for row in read_jsonl(LLM_FULL_JSONL):
        cards.append({"decision_id": row["decision_id"], "card_type": "llm_full_evidence", "card_markdown": row["card_markdown"]})
    return cards


def make_client():
    try:
        import anthropic
    except ModuleNotFoundError as exc:
        raise RuntimeError("Missing dependency `anthropic`. Install requirements or use offline mode.") from exc
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


def build_prompt(pack: dict[str, Any], card: dict[str, Any]) -> tuple[str, str]:
    pack_json = json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True)
    prompt = RUBRIC_PROMPT.format(
        pack_json=pack_json,
        card_type=card["card_type"],
        card_markdown=card["card_markdown"],
    )
    return prompt, sha256_text(SYSTEM_PROMPT + "\n" + prompt)


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except Exception:
        return 1
    return max(1, min(5, score))


def normalize_score(raw: dict[str, Any]) -> dict[str, Any]:
    result = dict(raw)
    for field in SCORE_FIELDS:
        result[field] = clamp_score(result.get(field))
    result.setdefault("major_issue", "none")
    result.setdefault("major_hallucinations", [])
    result.setdefault("missing_evidence_refs", [])
    result.setdefault("overall_comment", "")
    return result


def call_scorer(client: Any, model: str, prompt: str, max_tokens: int, effort: str) -> dict[str, Any]:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": RUBRIC_SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )
    if getattr(response, "stop_reason", None) == "refusal":
        raise RuntimeError(f"Claude refusal while scoring: {getattr(response, 'stop_details', None)}")
    text_parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    if not text_parts:
        raise RuntimeError("Scorer response contained no text")
    parsed = json.loads("\n".join(text_parts))
    return {
        "score": normalize_score(parsed),
        "request_id": getattr(response, "_request_id", ""),
        "response_model": getattr(response, "model", model),
    }


def write_scores_csv(rows: list[dict[str, Any]]) -> None:
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
        "model",
        "request_id",
        "scored_at_utc",
        "prompt_sha256",
    ]
    with OUT_SCORES.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, Any]], status: str) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["card_type"]].append(row)
    lines = [
        "# LLM Decision Card Rubric Summary\n",
        f"\nStatus: `{status}`\n",
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
    OUT_SUMMARY.write_text("".join(lines), encoding="utf-8")


def write_offline_prompts(cards: list[dict[str, Any]], packs_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
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
    write_jsonl(OUT_PROMPTS, rows)
    return rows


def run_scoring(model: str = DEFAULT_MODEL, max_tokens: int = DEFAULT_MAX_TOKENS, effort: str = DEFAULT_EFFORT, offline: bool = False) -> dict[str, Any]:
    GENERATED.mkdir(parents=True, exist_ok=True)
    if not INITIAL_PACKS.exists():
        raise FileNotFoundError(f"Missing prompt-safe packs: {INITIAL_PACKS}")
    packs = read_json(INITIAL_PACKS)
    packs_by_id = {pack["decision_id"]: pack for pack in packs}
    cards = [card for card in collect_cards() if card["decision_id"] in packs_by_id]

    result: dict[str, Any] = {
        "status": "started",
        "provider": "anthropic",
        "requested_model": model,
        "temperature": "not_sent",
        "scored_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "num_cards": len(cards),
        "outputs": [],
        "failures": [],
    }

    if offline:
        rows = write_offline_prompts(cards, packs_by_id)
        result.update({"status": "scoring_pending_offline", "prompt_packs": str(OUT_PROMPTS), "num_prompt_packs": len(rows)})
        result["outputs"].append(str(OUT_PROMPTS))
        write_scores_csv([])
        result["outputs"].append(str(OUT_SCORES))
        write_summary([], result["status"])
        result["outputs"].append(str(OUT_SUMMARY))
        return result

    try:
        client, anthropic_module = make_client()
    except Exception as exc:
        rows = write_offline_prompts(cards, packs_by_id)
        result.update({"status": "scoring_pending_auth_or_dependency", "prompt_packs": str(OUT_PROMPTS), "num_prompt_packs": len(rows)})
        result["failures"].append({"stage": "client_init", "error": str(exc)})
        result["outputs"].append(str(OUT_PROMPTS))
        write_summary([], result["status"])
        result["outputs"].append(str(OUT_SUMMARY))
        return result

    score_rows = []
    for card in cards:
        pack = packs_by_id[card["decision_id"]]
        prompt, prompt_hash = build_prompt(pack, card)
        try:
            scored = call_scorer(client, model, prompt, max_tokens, effort)
            score = scored["score"]
            row = {
                "decision_id": card["decision_id"],
                "card_type": card["card_type"],
                **{field: score[field] for field in SCORE_FIELDS},
                "major_issue": score["major_issue"],
                "major_hallucination_count": len(score.get("major_hallucinations", [])),
                "missing_evidence_ref_count": len(score.get("missing_evidence_refs", [])),
                "overall_comment": score.get("overall_comment", ""),
                "model": scored["response_model"],
                "request_id": scored["request_id"],
                "scored_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "prompt_sha256": prompt_hash,
            }
            score_rows.append(row)
        except Exception as exc:
            if is_auth_error(exc, anthropic_module):
                rows = write_offline_prompts(cards, packs_by_id)
                result.update({"status": "scoring_pending_auth", "prompt_packs": str(OUT_PROMPTS), "num_prompt_packs": len(rows)})
                result["outputs"].append(str(OUT_PROMPTS))
                result["failures"].append({"stage": "score", "decision_id": card["decision_id"], "error": str(exc)})
                write_summary(score_rows, result["status"])
                result["outputs"].append(str(OUT_SUMMARY))
                if score_rows:
                    write_scores_csv(score_rows)
                    result["outputs"].append(str(OUT_SCORES))
                return result
            result["failures"].append({"stage": "score", "decision_id": card["decision_id"], "error": str(exc)})

    if score_rows:
        write_scores_csv(score_rows)
        result["outputs"].append(str(OUT_SCORES))
    write_summary(score_rows, "completed" if not result["failures"] else "completed_with_failures")
    result["outputs"].append(str(OUT_SUMMARY))
    result["num_scores"] = len(score_rows)
    result["status"] = "completed" if not result["failures"] else "completed_with_failures"
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score decision-support cards with rubric.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--effort", default=DEFAULT_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--offline", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_scoring(model=args.model, max_tokens=args.max_tokens, effort=args.effort, offline=args.offline)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"].startswith("completed") or (args.offline and result["status"] == "scoring_pending_offline"):
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
