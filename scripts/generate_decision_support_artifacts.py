"""Generate decision-support artifacts from existing ML/backtest/news outputs.

This script reads source CSV files from the project root, then writes
standalone artifacts into reports/decision_support/generated.

Outputs:
- evidence_packs_audit.json
- evidence_packs_initial.json
- evidence_packs_ml_only.json
- evidence_packs.json (backward-compatible audit copy)
- decision_cards.md
- outcome_reviews.md
- llm_rubric_scoring_template.csv
- monitoring_cases_summary.csv
- news_fulltext_coverage.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "reports" / "decision_support" / "generated"

SIGNALS = ROOT / "reports" / "signals.csv"
TECH = ROOT / "data" / "features" / "technical_features.csv"
NEWS_ENRICHED = ROOT / "data" / "news" / "enriched" / "all_news_enriched.csv"
NEWS_PROCESSED = ROOT / "data" / "news" / "processed" / "all_news_processed.csv"
NEWS_MATCHED = ROOT / "data" / "news" / "matched" / "all_news_matched.csv"

DEFAULT_TOP_K = 5
DEFAULT_MAX_NEWS_PER_PACK = 5
FULL_TEXT_EXCERPT_CHARS = 500

IMPORTANT_FEATURES = [
    "rsi_end_q",
    "macd_hist_mean_q",
    "price_vs_sma20",
    "return_2q_ago",
    "return_q",
    "return_prev_q",
    "volume_change_q",
    "return_mean_daily",
    "price_range_q",
    "sma20_end",
]

FEATURE_EXPLANATIONS = {
    "rsi_end_q": "RSI cuối kỳ là driver kỹ thuật quan trọng nhất trong mô hình.",
    "macd_hist_mean_q": "MACD histogram trung bình phản ánh động lượng xu hướng.",
    "price_vs_sma20": "Vị trí giá so với SMA20 phản ánh trạng thái trên/dưới đường trung bình.",
    "return_2q_ago": "Lợi suất trễ hai kỳ phản ánh động lượng/quán tính lịch sử.",
    "return_q": "Lợi suất trong kỳ hiện tại phản ánh xu hướng gần nhất.",
    "return_prev_q": "Lợi suất kỳ trước bổ sung thông tin động lượng.",
    "volume_change_q": "Thay đổi khối lượng phản ánh mức độ quan tâm của thị trường.",
    "return_mean_daily": "Lợi suất trung bình ngày phản ánh xu hướng ngắn trong kỳ.",
    "price_range_q": "Biên độ giá trong kỳ phản ánh biến động/rủi ro.",
    "sma20_end": "SMA20 cuối kỳ phản ánh mặt bằng xu hướng ngắn hạn.",
}

EVENT_KEYWORDS = {
    "dividend": ["cổ tức", "chia cổ tức", "trả cổ tức"],
    "earnings": ["lợi nhuận", "doanh thu", "báo lãi", "kết quả kinh doanh"],
    "debt_risk": ["nợ xấu", "nợ vay", "trái phiếu", "áp lực tài chính"],
    "capital": ["tăng vốn", "phát hành", "vốn điều lệ"],
    "legal_risk": ["xử phạt", "vi phạm", "điều tra", "kiểm toán"],
    "governance": ["hội đồng quản trị", "đại hội", "lãnh đạo", "ceo"],
}

FORBIDDEN_INITIAL_KEY_PARTS = (
    "outcome",
    "realized",
    "review_only",
    "benchmark_return",
    "excess_return",
    "future_return",
    "future_label",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def quarter_end_date(q: str) -> str:
    year = int(q[:4])
    qq = int(q[-1])
    return {
        1: f"{year}-03-31",
        2: f"{year}-06-30",
        3: f"{year}-09-30",
        4: f"{year}-12-31",
    }[qq]


def event_type(title: str, desc: str) -> str:
    text = f"{title} {desc}".lower()
    found = [k for k, kws in EVENT_KEYWORDS.items() if any(kw in text for kw in kws)]
    return ",".join(found) if found else "general_news"


def safe_float(v: Any) -> float | None:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def fmt4(v: Any) -> str:
    return "NA" if v is None else f"{float(v):.4f}"


def parse_json_list(value: Any) -> list:
    if not value or not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def short_text(value: Any, limit: int = FULL_TEXT_EXCERPT_CHARS) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit].rstrip()


def signal_class(pred_label: int, rank: int, top_k: int = DEFAULT_TOP_K) -> str:
    if pred_label != 1:
        return "Avoid"
    if rank <= top_k:
        return "Buy Candidate"
    return "Watchlist"


def technical_direction(feature: str, value: float | None) -> str:
    if value is None:
        return "unknown"
    if feature in {"rsi_end_q", "rsi_mean_q"}:
        if value >= 70:
            return "positive_but_overbought_risk"
        if value >= 50:
            return "supports_up_signal"
        return "weak_or_neutral"
    if feature in {
        "macd_hist_mean_q",
        "price_vs_sma20",
        "return_q",
        "return_prev_q",
        "return_2q_ago",
        "return_mean_daily",
        "volume_change_q",
    }:
        return "supports_up_signal" if value > 0 else "weak_or_negative"
    if feature in {"price_range_q"}:
        return "risk_high_volatility" if value > 0.35 else "normal"
    return "context"


def strip_initial_prompt_fields(obj: Any) -> Any:
    """Recursively remove outcome/review/future-only fields from prompt input."""
    if isinstance(obj, dict):
        clean: dict[str, Any] = {}
        for key, value in obj.items():
            key_lower = str(key).lower()
            if any(part in key_lower for part in FORBIDDEN_INITIAL_KEY_PARTS):
                continue
            clean[key] = strip_initial_prompt_fields(value)
        return clean
    if isinstance(obj, list):
        return [strip_initial_prompt_fields(item) for item in obj]
    return obj


def serialized_has_initial_leakage(obj: Any) -> bool:
    text = json.dumps(obj, ensure_ascii=False).lower()
    return any(part in text for part in FORBIDDEN_INITIAL_KEY_PARTS)


def assert_no_initial_leakage(pack: dict[str, Any]) -> None:
    if serialized_has_initial_leakage(pack):
        raise ValueError(f"Initial prompt pack leaks outcome/review fields: {pack.get('decision_id', '<unknown>')}")


def build_ml_only_pack(pack: dict[str, Any]) -> dict[str, Any]:
    """Create an ablation input with only ML and technical evidence."""
    clean = strip_initial_prompt_fields(pack)
    clean.pop("news_evidence", None)
    flags = dict(clean.get("data_quality_flags", {}))
    for key in [
        "news_coverage",
        "has_recent_news",
        "ticker_matching_confidence",
        "full_text_coverage",
        "summary_coverage",
        "key_fact_coverage",
        "num_title_only_articles",
    ]:
        flags.pop(key, None)
    flags["news_evidence_removed_for_ablation"] = True
    clean["data_quality_flags"] = flags
    clean["card_input_variant"] = "ml_only"
    clean["guardrails"] = {
        "initial_prompt_safe": True,
        "news_evidence_excluded": True,
        "not_investment_advice": True,
        "no_post_decision_data": True,
    }
    assert_no_initial_leakage(clean)
    return clean


def choose_news_path() -> Path:
    if NEWS_ENRICHED.exists():
        return NEWS_ENRICHED
    if NEWS_PROCESSED.exists():
        return NEWS_PROCESSED
    return NEWS_MATCHED


def normalize_key_facts(raw_value: str, evidence_id: str) -> list:
    key_facts = parse_json_list(raw_value)
    normalized = []
    for j, fact in enumerate(key_facts, start=1):
        if isinstance(fact, dict):
            item = dict(fact)
            item.setdefault("fact_id", f"{evidence_id}-F{j:02d}")
            normalized.append(item)
        elif fact:
            normalized.append({"fact_id": f"{evidence_id}-F{j:02d}", "fact": str(fact)})
    return normalized


def build_evidence_packs(top_k: int, max_news_per_pack: int, news_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    signals = read_csv(SIGNALS)
    tech_rows = read_csv(TECH)
    news_rows = read_csv(news_path)

    tech_by_key = {(r["ticker"], r["quarter_id"]): r for r in tech_rows}
    news_by_ticker: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in news_rows:
        news_by_ticker[r.get("ticker", "")].append(r)

    sig_by_q: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in signals:
        sig_by_q[r["quarter_id"]].append(r)

    audit_packs: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []
    for q in sorted(sig_by_q):
        rows = sig_by_q[q]
        rows.sort(key=lambda x: safe_float(x.get("pred_proba_up")) or -1, reverse=True)
        for rank, r in enumerate(rows[:top_k], start=1):
            ticker = r["ticker"]
            decision_date = quarter_end_date(q)
            pred_label = int(float(r["pred_label"]))
            proba = safe_float(r.get("pred_proba_up"))
            realized = safe_float(r.get("period_return"))
            tech = tech_by_key.get((ticker, q), {})

            top_drivers = []
            technical_snapshot: dict[str, float | None] = {}
            for feature in IMPORTANT_FEATURES:
                val = safe_float(tech.get(feature, ""))
                technical_snapshot[feature] = val
                if val is not None:
                    top_drivers.append(
                        {
                            "feature": feature,
                            "value": val,
                            "direction": technical_direction(feature, val),
                            "explanation": FEATURE_EXPLANATIONS.get(feature, "Technical driver."),
                        }
                    )

            selected_news = []
            for n in news_by_ticker.get(ticker, []):
                d = (n.get("date", "") or n.get("published_at_detail", ""))[:10]
                if d and d <= decision_date:
                    selected_news.append(n)
            selected_news.sort(key=lambda n: n.get("date", "") or n.get("published_at_detail", ""), reverse=True)
            selected_news = selected_news[:max_news_per_pack]

            evidence_news = []
            for i, n in enumerate(selected_news, start=1):
                evidence_id = f"N{i:03d}"
                article_summary = n.get("article_summary", "") or n.get("description", "")
                lead = n.get("lead", "")
                enriched_event_type = n.get("event_type_enriched", "")
                event_text = " ".join([n.get("title", ""), article_summary, lead, n.get("description", "")])
                full_text_available = parse_bool(n.get("full_text_available", False))
                evidence_news.append(
                    {
                        "evidence_id": evidence_id,
                        "published_at": (n.get("date", "") or n.get("published_at_detail", ""))[:10],
                        "source": n.get("source", ""),
                        "title": n.get("title", ""),
                        "summary": n.get("description", ""),
                        "lead": lead,
                        "article_summary": article_summary,
                        "key_facts": normalize_key_facts(n.get("key_facts_json", ""), evidence_id),
                        "risk_flags": parse_json_list(n.get("risk_flags_json", "")),
                        "url": n.get("url", ""),
                        "canonical_url": n.get("canonical_url", ""),
                        "event_type": enriched_event_type or event_type(n.get("title", ""), event_text),
                        "match_confidence": n.get("match_confidence", ""),
                        "relevance_hint": n.get("relevance_hint", ""),
                        "full_text_available": full_text_available,
                        "full_text_chars": int(safe_float(n.get("full_text_chars", "")) or 0),
                        "full_text_excerpt": short_text(n.get("full_text", ""), FULL_TEXT_EXCERPT_CHARS),
                        "full_text_ref": n.get("content_hash", "") or n.get("canonical_url", "") or n.get("url", ""),
                        "content_hash": n.get("content_hash", ""),
                        "extraction_status": n.get("extraction_status", ""),
                        "extractor_version": n.get("extractor_version", ""),
                    }
                )

            status = signal_class(pred_label, rank, top_k=top_k)
            decision_id = f"{q}_{ticker}_{rank:02d}"
            pack = {
                "decision_id": decision_id,
                "ticker": ticker,
                "decision_date": decision_date,
                "period_id": q,
                "holding_horizon": "next_quarter_or_period_return_in_signals",
                "universe": "Top-K from reports/signals.csv",
                "ml_signal": {
                    "model_name": "technical_Config_A_from_existing_pipeline",
                    "pred_proba_up": proba,
                    "pred_label": pred_label,
                    "rank_in_period": rank,
                    "signal_class": status,
                },
                "technical_snapshot": technical_snapshot,
                "top_drivers": top_drivers,
                "news_evidence": evidence_news,
                "data_quality_flags": {
                    "news_coverage": "high" if len(evidence_news) >= 3 else ("low" if evidence_news else "none"),
                    "has_recent_news": bool(evidence_news),
                    "ticker_matching_confidence": "mixed" if evidence_news else "none",
                    "full_text_coverage": sum(1 for n in evidence_news if n.get("full_text_available")),
                    "summary_coverage": sum(1 for n in evidence_news if n.get("article_summary")),
                    "key_fact_coverage": sum(1 for n in evidence_news if n.get("key_facts")),
                    "num_title_only_articles": sum(1 for n in evidence_news if not n.get("full_text_available")),
                    "missing_fields": [],
                },
                "outcome_for_review_only": {
                    "realized_period_return": realized,
                    "outcome_label": "positive" if (realized or 0) > 0 else "negative_or_neutral",
                },
                "guardrails": {
                    "audit_pack_may_contain_review_fields": True,
                    "news_cutoff": decision_date,
                    "not_investment_advice": True,
                    "full_text_excerpt_chars": FULL_TEXT_EXCERPT_CHARS,
                    "llm_prompt_uses_summary_key_facts_by_default": True,
                },
            }
            audit_packs.append(pack)
            case_rows.append(
                {
                    "decision_id": decision_id,
                    "ticker": ticker,
                    "period_id": q,
                    "rank": rank,
                    "pred_proba_up": proba,
                    "pred_label": pred_label,
                    "signal_class": status,
                    "news_count_in_pack": len(evidence_news),
                    "realized_period_return_review_only": realized,
                    "outcome": "positive" if (realized or 0) > 0 else "negative_or_neutral",
                }
            )

    initial_packs = []
    ml_only_packs = []
    for pack in audit_packs:
        initial = strip_initial_prompt_fields(pack)
        initial["card_input_variant"] = "full_evidence"
        initial["guardrails"] = {
            "initial_prompt_safe": True,
            "news_cutoff": initial["decision_date"],
            "not_investment_advice": True,
            "no_post_decision_data": True,
            "full_text_excerpt_chars": FULL_TEXT_EXCERPT_CHARS,
        }
        assert_no_initial_leakage(initial)
        initial_packs.append(initial)
        ml_only_packs.append(build_ml_only_pack(pack))

    return audit_packs, initial_packs, ml_only_packs, case_rows


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_rule_based_card_records(markdown: str, packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create browser-safe card records after deterministic Markdown generation.

    The UI reads this JSON artifact rather than parsing Markdown in a browser.
    """
    packs_by_id = {str(pack["decision_id"]): pack for pack in packs}
    marker = "\n## Decision Card: "
    records: list[dict[str, Any]] = []
    for chunk in markdown.split(marker)[1:]:
        decision_id, _, remainder = chunk.partition("\n")
        decision_id = decision_id.strip()
        pack = packs_by_id.get(decision_id)
        if pack is None:
            continue
        records.append(
            {
                "card_id": f"rule_based_baseline:{decision_id}",
                "decision_id": decision_id,
                "card_type": "rule_based_baseline",
                "producer_run_id": "deterministic-rule-based-baseline",
                "provider": "deterministic-template",
                "requested_model": None,
                "response_model": None,
                "vendor": "local",
                "generated_at_utc": None,
                "prompt_sha256": None,
                "pack_sha256": sha256_text(json.dumps(pack, ensure_ascii=False, sort_keys=True)),
                "body_markdown": f"## Decision Card: {decision_id}\n{remainder}".strip(),
            }
        )
    return records


def build_outcome_review_records(packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return review-only JSON records; never call this for initial prompt artifacts."""
    records: list[dict[str, Any]] = []
    for pack in packs:
        review = pack.get("outcome_for_review_only", {})
        realized_return = review.get("realized_period_return")
        records.append(
            {
                "decision_id": pack["decision_id"],
                "holding_period_complete": realized_return is not None,
                "review_date": None,
                "initial_snapshot_reference": {
                    "decision_date": pack.get("decision_date"),
                    "ticker": pack.get("ticker"),
                    "period_id": pack.get("period_id"),
                    "pred_proba_up": pack.get("ml_signal", {}).get("pred_proba_up"),
                    "rank_in_period": pack.get("ml_signal", {}).get("rank_in_period"),
                },
                "monitoring_summary": {},
                "post_hoc_outcome": {
                    "realized_period_return": realized_return,
                    "outcome_label": review.get("outcome_label"),
                    "benchmark_return": None,
                    "excess_return": None,
                },
                "review_narrative": "Post-hoc outcome review only; never used in initial selection, explanation, update, or initial-card scoring.",
                "provenance": {
                    "review_only": True,
                    "must_not_feed_initial_or_update": True,
                    "source_decision_pack": "evidence_packs_audit.json",
                },
            }
        )
    return records


def write_rule_based_cards(out: Path, packs: list[dict[str, Any]], top_k: int) -> None:
    cards = [
        "# Generated Decision Cards (Rule-based Baseline)\n",
        "\n> Các card này được sinh từ evidence pack thật, nhưng chưa phải output LLM. Dùng làm baseline và input cho chấm LLM sau này.\n",
    ]
    for p in packs:
        ml = p["ml_signal"]
        news_count = len(p.get("news_evidence", []))
        main_drivers = p.get("top_drivers", [])[:5]
        cards.append(f"\n---\n\n## Decision Card: {p['decision_id']}\n")
        cards.append(
            f"\n### 1. Tóm tắt tín hiệu\n\n- Ticker: **{p['ticker']}**\n- Decision date: {p['decision_date']}\n- Trạng thái: **{ml['signal_class']}**\n- Xác suất tăng theo ML: {ml['pred_proba_up']:.4f}\n- Rank trong kỳ: {ml['rank_in_period']}\n- Số news evidence trước decision date: {news_count}\n"
        )
        cards.append("\n### 2. Luận điểm đầu tư chính\n\n")
        cards.append(
            f"Mã {p['ticker']} được chọn vào Top-{top_k} của kỳ {p['period_id']} dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.\n"
        )
        cards.append("\n### 3. Yếu tố hỗ trợ\n\n")
        cards.append(
            f"1. Tín hiệu ML có xác suất tăng {ml['pred_proba_up']:.4f} và rank {ml['rank_in_period']} trong kỳ — Evidence: `ml_signal`.\n"
        )
        for i, d in enumerate(main_drivers[:3], start=2):
            cards.append(f"{i}. `{d['feature']}` = {fmt4(d['value'])}, hướng `{d['direction']}` — Evidence: `top_drivers`.\n")
        if p.get("news_evidence"):
            n = p["news_evidence"][0]
            summary_note = f" Tóm tắt: {n['article_summary']}" if n.get("article_summary") else ""
            cards.append(
                f"{len(main_drivers[:3]) + 2}. Tin gần decision date: {n['title']} ({n['source']}, {n['published_at']}).{summary_note} — Evidence: {n['evidence_id']}.\n"
            )
            for fact in n.get("key_facts", [])[:2]:
                if isinstance(fact, dict) and fact.get("fact"):
                    cards.append(f"   - Key fact {fact.get('fact_id', '')}: {fact['fact']}\n")
        else:
            cards.append(
                f"{len(main_drivers[:3]) + 2}. Không có news evidence trong pack; không nên tạo luận điểm định tính mạnh — Evidence: `data_quality_flags`.\n"
            )

        caution_drivers = [
            d
            for d in main_drivers
            if d["direction"] in {"weak_or_negative", "weak_or_neutral", "positive_but_overbought_risk", "risk_high_volatility"}
        ]
        risk_news = [n for n in p.get("news_evidence", []) if n["event_type"] not in {"general_news", "earnings", "dividend", "capital"}]
        cards.append("\n### 4. Rủi ro và điểm cần theo dõi\n\n")
        cards.append("- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.\n")
        cards.append("- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.\n")
        cards.append("- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.\n")
        for d in caution_drivers[:3]:
            cards.append(f"- Driver cần theo dõi: `{d['feature']}` = {fmt4(d['value'])}, hướng `{d['direction']}`.\n")
        for n in risk_news[:2]:
            cards.append(f"- News/event cần kiểm tra thủ công: `{n['event_type']}` — {n['title']} ({n['published_at']}).\n")
        if news_count == 0:
            cards.append("- News coverage bằng 0 trong pack, thesis định tính yếu.\n")
        elif p["data_quality_flags"].get("ticker_matching_confidence") == "mixed":
            cards.append("- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.\n")
        cards.append("\n### 5. Trigger theo dõi\n\n")
        cards.append("- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.\n")
        cards.append("- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.\n")
        cards.append("- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.\n")
        cards.append("- Drawdown vượt 8–10% từ decision price.\n")
        cards.append("- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.\n")
        cards.append("\n### 6. Disclaimer\n\nCard này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.\n")
    out.write_text("".join(cards), encoding="utf-8")


def write_outcome_reviews(out: Path, packs: list[dict[str, Any]]) -> None:
    reviews = ["# Generated Outcome Reviews\n", "\n> Outcome review được phép dùng realized return vì đây là bước hậu kiểm sau holding period.\n"]
    for p in packs:
        ml = p["ml_signal"]
        ret = p["outcome_for_review_only"]["realized_period_return"]
        main_drivers = p.get("top_drivers", [])[:5]
        caution_drivers = [
            d
            for d in main_drivers
            if d["direction"] in {"weak_or_negative", "weak_or_neutral", "positive_but_overbought_risk", "risk_high_volatility"}
        ]
        risk_news = [n for n in p.get("news_evidence", []) if n["event_type"] not in {"general_news", "earnings", "dividend", "capital"}]
        reviews.append(f"\n---\n\n## Outcome Review: {p['decision_id']}\n")
        reviews.append(
            f"\n- Ticker: {p['ticker']}\n- Period: {p['period_id']}\n- Initial status: {ml['signal_class']}\n- Predicted probability: {ml['pred_proba_up']:.4f}\n- Initial rank: {ml['rank_in_period']}\n- Realized period return: {fmt4(ret)}\n- Outcome: {'positive' if (ret or 0) > 0 else 'negative_or_neutral'}\n"
        )
        reviews.append("\n### Nhận xét hậu kiểm\n\n")
        if (ret or 0) > 0:
            reviews.append("Kết quả realized return dương, phù hợp với tín hiệu tăng ban đầu. Cần kiểm tra thêm benchmark cùng kỳ để đánh giá excess return.\n")
        else:
            reviews.append("Kết quả realized return không dương, cho thấy decision cần được phân tích lại qua technical drivers, news evidence và monitoring triggers.\n")
        if caution_drivers:
            reviews.append("\n### Technical flags cần xem lại\n\n")
            for d in caution_drivers[:5]:
                reviews.append(f"- `{d['feature']}` = {fmt4(d['value'])}, hướng `{d['direction']}`.\n")
        if risk_news:
            reviews.append("\n### News/event flags cần xem lại\n\n")
            for n in risk_news[:3]:
                reviews.append(f"- {n['published_at']}: `{n['event_type']}` — {n['title']} ({n['evidence_id']}).\n")
        reviews.append(
            "\n### Bài học\n\n- Không dùng outcome này trong prompt tạo decision card ban đầu.\n- Outcome chỉ dùng sau holding period để hậu kiểm thesis và trigger.\n- So sánh các flag ban đầu với kết quả thực tế để tinh chỉnh monitoring rules.\n"
        )
    out.write_text("".join(reviews), encoding="utf-8")


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not fieldnames:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_coverage_rows(news_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    coverage_rows = []
    source_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for n in news_rows:
        source_groups[n.get("source", "unknown")].append(n)
    for source, rows in sorted(source_groups.items()):
        total = len(rows)
        coverage_rows.append(
            {
                "source": source,
                "total_rows": total,
                "full_text_available": sum(1 for r in rows if parse_bool(r.get("full_text_available", False))),
                "article_summary_available": sum(1 for r in rows if r.get("article_summary")),
                "key_facts_available": sum(1 for r in rows if parse_json_list(r.get("key_facts_json", ""))),
                "risk_flags_available": sum(1 for r in rows if parse_json_list(r.get("risk_flags_json", ""))),
            }
        )
    return coverage_rows


def write_rubric_template(path: Path, packs: list[dict[str, Any]]) -> None:
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
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in packs:
            for card_type in ["rule_based_baseline", "llm_ml_only", "llm_full_evidence"]:
                writer.writerow({"decision_id": p["decision_id"], "card_type": card_type})


def write_generated_summary(out: Path, news_path: Path, top_k: int, packs: list[dict[str, Any]], case_rows: list[dict[str, Any]]) -> None:
    positive = sum(1 for r in case_rows if r["outcome"] == "positive")
    negative_or_neutral = len(case_rows) - positive
    periods = sorted({p["period_id"] for p in packs})
    summary = [
        "# Generated Decision-Support Artifact Summary\n",
        "\n## 1. Generation run\n\n",
        "- Script: `scripts/generate_decision_support_artifacts.py`\n",
        "- Output directory: `reports/decision_support/generated/`\n",
        "- Source files:\n",
        f"  - `{SIGNALS}`\n",
        f"  - `{TECH}`\n",
        f"  - `{news_path}`\n",
        f"- Top-K per period: {top_k}\n",
        f"- Periods covered: {', '.join(periods)}\n",
        f"- Number of evidence packs: {len(packs)}\n",
        f"- Positive realized return: {positive}\n",
        f"- Negative or neutral realized return: {negative_or_neutral}\n",
        "- Initial card type: rule-based baseline; LLM cards are generated by `scripts/generate_llm_decision_cards.py`.\n",
        "\n## 2. Output files\n\n",
        "| File | Purpose |\n",
        "|---|---|\n",
        "| `evidence_packs_audit.json` | Full audit packs; may include outcome fields for review only. |\n",
        "| `evidence_packs_initial.json` | Prompt-safe packs for initial LLM decision cards. |\n",
        "| `evidence_packs_ml_only.json` | ML/technical-only ablation packs. |\n",
        "| `evidence_packs.json` | Backward-compatible audit copy. |\n",
        "| `decision_cards.md` | Rule-based baseline cards generated from real evidence packs. |\n",
        "| `rule_based_cards.json` | Structured rule-based card records for the research UI. |\n",
        "| `outcome_reviews.md` | Outcome reviews that use realized return only after holding period. |\n",
        "| `outcome_reviews.json` | Structured review-only records for the research UI; never initial prompt input. |\n",
        "| `monitoring_cases_summary.csv` | Decisions, ranks, probabilities, news counts and outcomes. |\n",
        "| `news_fulltext_coverage.csv` | Full-text extraction and summary/key-fact coverage by source. |\n",
        "| `llm_rubric_scoring_template.csv` | Scoring sheet for rule-based and LLM card variants. |\n",
        "| `manifest.json` | Run metadata and source hashes. |\n",
        "\n## 3. Leakage guardrails\n\n",
        "- Initial prompt packs are stripped recursively before LLM generation.\n",
        "- Outcome reviews explicitly use realized return only after holding period.\n",
        "- News evidence in each initial pack is filtered with `published_at <= decision_date`.\n",
        "- Rule-based cards and LLM cards are decision-support artifacts, not investment recommendations.\n",
    ]
    out.write_text("".join(summary), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate decision-support artifacts.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--max-news-per-pack", type=int, default=DEFAULT_MAX_NEWS_PER_PACK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write-prompt-packs", action="store_true", help="Also write JSONL prompt-pack convenience files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    news_path = choose_news_path()
    if not SIGNALS.exists():
        raise FileNotFoundError(f"Missing signals file: {SIGNALS}")
    if not TECH.exists():
        raise FileNotFoundError(f"Missing technical features file: {TECH}")
    if not news_path.exists():
        raise FileNotFoundError(f"Missing news data: {news_path}")

    audit_packs, initial_packs, ml_only_packs, case_rows = build_evidence_packs(args.top_k, args.max_news_per_pack, news_path)
    for pack in initial_packs:
        assert_no_initial_leakage(pack)
    for pack in ml_only_packs:
        assert_no_initial_leakage(pack)

    write_json(out / "evidence_packs_audit.json", audit_packs)
    write_json(out / "evidence_packs_initial.json", initial_packs)
    write_json(out / "evidence_packs_ml_only.json", ml_only_packs)
    write_json(out / "evidence_packs.json", audit_packs)
    if args.write_prompt_packs:
        write_jsonl(out / "evidence_packs_initial.jsonl", initial_packs)
        write_jsonl(out / "evidence_packs_ml_only.jsonl", ml_only_packs)

    rule_cards_path = out / "decision_cards.md"
    outcome_reviews_path = out / "outcome_reviews.md"
    write_rule_based_cards(rule_cards_path, audit_packs, args.top_k)
    write_outcome_reviews(outcome_reviews_path, audit_packs)
    write_json(
        out / "rule_based_cards.json",
        parse_rule_based_card_records(rule_cards_path.read_text(encoding="utf-8"), audit_packs),
    )
    write_json(out / "outcome_reviews.json", build_outcome_review_records(audit_packs))
    write_csv_rows(out / "monitoring_cases_summary.csv", case_rows)

    news_rows = read_csv(news_path)
    write_csv_rows(
        out / "news_fulltext_coverage.csv",
        build_coverage_rows(news_rows),
        ["source", "total_rows", "full_text_available", "article_summary_available", "key_facts_available", "risk_flags_available"],
    )
    write_rubric_template(out / "llm_rubric_scoring_template.csv", audit_packs)
    write_generated_summary(out / "generated_summary.md", news_path, args.top_k, audit_packs, case_rows)

    source_files = [SIGNALS, TECH, news_path]
    positive = sum(1 for r in case_rows if r["outcome"] == "positive")
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_files": [str(p) for p in source_files],
        "source_sha256": {str(p): sha256_file(p) for p in source_files},
        "news_source_selected": str(news_path),
        "top_k_per_period": args.top_k,
        "max_news_per_pack": args.max_news_per_pack,
        "num_evidence_packs": len(audit_packs),
        "num_prompt_safe_packs": len(initial_packs),
        "positive_outcomes": positive,
        "negative_or_neutral_outcomes": len(case_rows) - positive,
        "artifact_sha256": {},
        "outputs": [
            "evidence_packs_audit.json",
            "evidence_packs_initial.json",
            "evidence_packs_ml_only.json",
            "evidence_packs.json",
            "decision_cards.md",
            "outcome_reviews.md",
            "rule_based_cards.json",
            "outcome_reviews.json",
            "monitoring_cases_summary.csv",
            "news_fulltext_coverage.csv",
            "llm_rubric_scoring_template.csv",
            "generated_summary.md",
        ],
        "backward_compatibility": {
            "evidence_packs.json": "audit_copy_contains_outcome_for_review_only",
        },
        "leakage_guardrails": {
            "initial_packs_strip_review_fields": True,
            "ml_only_packs_strip_review_fields": True,
            "news_cutoff_enforced": "published_at <= decision_date",
            "llm_initial_prompts_should_use": "evidence_packs_initial.json or evidence_packs_ml_only.json",
        },
        "note": "Rule-based decision cards are baselines; live LLM cards are generated separately.",
    }
    for output in manifest["outputs"]:
        p = out / output
        if p.exists():
            manifest["artifact_sha256"][output] = sha256_file(p)
    write_json(out / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
