from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from scripts import llm_provider

BASE_CACHE_PATH = "data/experiments/llm_semantic/article_semantics_cache.csv"
OUT_CACHE_PATH = "data/experiments/llm_semantic/article_semantics_cache_hose100_extra.csv"
MATCHED_NEWS_PATH = "reports/hose_extra_candidate_matched_news.csv"
SELECTED_TICKERS_PATH = "reports/hose100_news_selected_tickers.csv"
PROMPT_PACKS_PATH = "data/experiments/llm_semantic/hose100_extra_material_prompt_packs.jsonl"
PROMPT_VERSION = "material_event_v1_hose100_extra"
SELECTED_TICKERS = [
    "KBC", "MSH", "CII", "HAG", "PAN", "PC1", "DHC", "TNG", "HBC", "APG",
    "CTD", "BWE", "AGG", "TNH", "LCG", "DBD", "DPG", "FCN", "KDC", "TCH",
]
MATERIAL_EVENTS = ["earnings", "dividend", "capital", "debt_risk", "legal_risk", "governance", "operation", "macro", "market", "other"]
VALID_RELEVANCE = ["direct", "indirect", "irrelevant"]
VALID_SENTIMENTS = ["positive", "neutral", "negative", "mixed"]
VALID_HORIZONS = ["short_term", "medium_term", "long_term", "unclear"]
SENTIMENT_SCORE = {"positive": 1.0, "neutral": 0.0, "negative": -1.0, "mixed": 0.0}
CACHE_COLUMNS = [
    "cache_key", "content_hash", "ticker", "article_date", "title", "url",
    "is_stock_relevant", "sentiment", "sentiment_score", "importance_score",
    "information_magnitude_score", "uncertainty_score", "novelty_hint_score",
    "reasoning_confidence", "time_horizon", "event_type", "relevance_to_ticker",
    "summary", "reason", "provider", "requested_model", "response_model", "request_id",
    "prompt_sha256", "input_sha256", "extracted_at_utc", "status", "error",
]

SYSTEM_PROMPT = """Bạn là công cụ trích xuất đặc trưng material-event từ tin tức tài chính tiếng Việt.
Chỉ dùng nội dung bài báo được cung cấp. Không dùng kiến thức ngoài.
Không dự báo giá cổ phiếu, không dự báo phản ứng thị trường, không đưa khuyến nghị mua/bán/nắm giữ.
Đánh giá bài báo cho đúng ticker đang xét.
Trả về DUY NHẤT một JSON object hợp lệ theo schema.
"""

SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "ticker": {"type": ["string", "null"]},
        "article_date": {"type": "string"},
        "is_stock_relevant": {"type": "boolean"},
        "sentiment": {"type": "string", "enum": VALID_SENTIMENTS},
        "sentiment_score": {"type": "number"},
        "importance_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "information_magnitude_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "uncertainty_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "novelty_hint_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "reasoning_confidence": {"type": "integer", "minimum": 1, "maximum": 5},
        "time_horizon": {"type": "string", "enum": VALID_HORIZONS},
        "event_type": {"type": "string", "enum": MATERIAL_EVENTS},
        "relevance_to_ticker": {"type": "string", "enum": VALID_RELEVANCE},
        "summary": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": [
        "ticker", "article_date", "is_stock_relevant", "sentiment", "sentiment_score",
        "importance_score", "information_magnitude_score", "uncertainty_score",
        "novelty_hint_score", "reasoning_confidence", "time_horizon", "event_type",
        "relevance_to_ticker", "summary", "reason",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class MaterialAnnotation:
    ticker: str | None
    article_date: str
    is_stock_relevant: bool
    sentiment: str
    sentiment_score: float
    importance_score: int
    information_magnitude_score: int
    uncertainty_score: int
    novelty_hint_score: int
    reasoning_confidence: int
    time_horizon: str
    event_type: str
    relevance_to_ticker: str
    summary: str
    reason: str
    provider: str = "mock"
    requested_model: str = "mock"
    response_model: str = "mock"
    request_id: str = ""


def norm(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return " ".join(str(value).split()).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clip_int(value: Any, default: int = 3) -> int:
    try:
        parsed = int(round(float(value)))
    except (TypeError, ValueError):
        parsed = default
    return max(1, min(5, parsed))


def clip_float(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(-1.0, min(1.0, parsed))


def content_hash(article: dict[str, Any]) -> str:
    existing = norm(article.get("content_hash"))
    if existing:
        return existing
    parts = [
        norm(article.get("ticker")).upper(), norm(article.get("date"))[:10], norm(article.get("url")).lower(),
        norm(article.get("title")).lower(), norm(article.get("description")).lower(), norm(article.get("full_text")).lower(),
    ]
    return sha256_text("\n".join(parts))


def cache_key(article: dict[str, Any], provider: str, model: str) -> str:
    parts = [PROMPT_VERSION, provider, model, content_hash(article), norm(article.get("ticker")).upper(), norm(article.get("date"))[:10]]
    return sha256_text("\n".join(parts))


def article_payload(article: dict[str, Any], max_chars: int = 12000) -> dict[str, Any]:
    text = norm(article.get("full_text"))
    if not text:
        text = f"{norm(article.get('title'))}. {norm(article.get('description'))}".strip()
    return {
        "ticker": norm(article.get("ticker")).upper(),
        "article_date": norm(article.get("date"))[:10],
        "source": norm(article.get("source")),
        "title": norm(article.get("title")),
        "description": norm(article.get("description")),
        "article_text": text[:max_chars],
        "url": norm(article.get("url")),
    }


def build_prompt(article: dict[str, Any]) -> str:
    payload = article_payload(article)
    return (
        "Hãy trích xuất material-event features cho bài báo dưới đây.\n"
        "event_type phải là một trong: earnings, dividend, capital, debt_risk, legal_risk, governance, operation, macro, market, other.\n"
        "relevance_to_ticker: direct nếu doanh nghiệp/mã là chủ thể chính; indirect nếu tác động qua ngành/vĩ mô/đối tác; irrelevant nếu chỉ nhắc tên không đáng kể.\n"
        "information_magnitude_score đo độ lớn thông tin kinh tế, không đo chiều giá.\n"
        "Không xuất target price, buy/sell/hold, future EPS/revenue.\n\n"
        f"Bài báo:\n{json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)}"
    )


def validate(payload: dict[str, Any]) -> MaterialAnnotation:
    sentiment = str(payload.get("sentiment", "neutral")).lower().strip()
    if sentiment not in VALID_SENTIMENTS:
        raise ValueError(f"Invalid sentiment: {sentiment}")
    event_type = str(payload.get("event_type", "other")).lower().strip()
    if event_type not in MATERIAL_EVENTS:
        event_type = "other"
    relevance = str(payload.get("relevance_to_ticker", "irrelevant")).lower().strip()
    if relevance not in VALID_RELEVANCE:
        relevance = "direct" if bool(payload.get("is_stock_relevant")) else "irrelevant"
    time_horizon = str(payload.get("time_horizon", "unclear")).lower().strip()
    if time_horizon not in VALID_HORIZONS:
        time_horizon = "unclear"
    is_stock_relevant = payload.get("is_stock_relevant")
    if not isinstance(is_stock_relevant, bool):
        raise ValueError(f"Invalid is_stock_relevant: {is_stock_relevant!r}")
    return MaterialAnnotation(
        ticker=norm(payload.get("ticker")).upper() or None,
        article_date=norm(payload.get("article_date"))[:10],
        is_stock_relevant=is_stock_relevant,
        sentiment=sentiment,
        sentiment_score=clip_float(payload.get("sentiment_score"), SENTIMENT_SCORE[sentiment]),
        importance_score=clip_int(payload.get("importance_score")),
        information_magnitude_score=clip_int(payload.get("information_magnitude_score")),
        uncertainty_score=clip_int(payload.get("uncertainty_score")),
        novelty_hint_score=clip_int(payload.get("novelty_hint_score")),
        reasoning_confidence=clip_int(payload.get("reasoning_confidence")),
        time_horizon=time_horizon,
        event_type=event_type,
        relevance_to_ticker=relevance,
        summary=norm(payload.get("summary"))[:240],
        reason=norm(payload.get("reason"))[:400],
    )


def load_existing_cache() -> pd.DataFrame:
    if Path(BASE_CACHE_PATH).exists():
        base = pd.read_csv(BASE_CACHE_PATH, encoding="utf-8")
    else:
        base = pd.DataFrame(columns=CACHE_COLUMNS)
    for col in CACHE_COLUMNS:
        if col not in base.columns:
            base[col] = pd.NA
    return base[CACHE_COLUMNS]


def record(article: dict[str, Any], key: str, annotation: MaterialAnnotation | None, prompt_hash: str, input_hash: str, provider: str, model: str, status: str, error: str = "") -> dict[str, Any]:
    row = {col: "" for col in CACHE_COLUMNS}
    row.update({
        "cache_key": key,
        "content_hash": content_hash(article),
        "ticker": norm(article.get("ticker")).upper(),
        "article_date": norm(article.get("date"))[:10],
        "title": norm(article.get("title")),
        "url": norm(article.get("url")),
        "provider": provider,
        "requested_model": model,
        "prompt_sha256": prompt_hash,
        "input_sha256": input_hash,
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "error": error[:500],
    })
    if annotation is not None:
        for k, v in asdict(annotation).items():
            if k in {"ticker", "article_date", "provider", "requested_model"}:
                continue
            row[k] = v
    return row


def select_articles(max_per_ticker: int = 60) -> pd.DataFrame:
    df = pd.read_csv(MATCHED_NEWS_PATH, encoding="utf-8")
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df = df[df["ticker"].isin(SELECTED_TICKERS)].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "ticker", "url"]).sort_values(["ticker", "date"])
    # Keep latest and broad coverage, capped per ticker to avoid one ticker dominating cost.
    selected = []
    for ticker, group in df.groupby("ticker", sort=False):
        selected.append(group.tail(max_per_ticker))
    out = pd.concat(selected, ignore_index=True) if selected else pd.DataFrame(columns=df.columns)
    if not out.empty:
        out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    return out


def write_jsonl(path: str, rows: list[dict[str, Any]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Annotate HOSE100 extra ticker news with material-event schema.")
    parser.add_argument("--provider", default="deepseek")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--max-per-ticker", type=int, default=60)
    parser.add_argument("--max-articles", type=int, default=None)
    args = parser.parse_args()

    llm_provider.load_env_file(ROOT)
    provider = llm_provider.resolve_provider(args.provider)
    model = llm_provider.resolve_model(provider, args.model)
    articles = select_articles(args.max_per_ticker)
    if args.max_articles is not None:
        articles = articles.head(args.max_articles)
    pd.DataFrame({"ticker": SELECTED_TICKERS}).to_csv(SELECTED_TICKERS_PATH, index=False, encoding="utf-8")
    base_cache = load_existing_cache()
    existing_ok = set(base_cache[base_cache["status"].astype(str).eq("ok")]["content_hash"].astype(str) + "|" + base_cache["ticker"].astype(str))
    new_rows = []
    prompt_rows = []
    client = provider_module = None
    if args.live:
        client, provider_module = llm_provider.make_llm_client(provider)

    for _, row in articles.iterrows():
        article = dict(row)
        identity = content_hash(article) + "|" + norm(article.get("ticker")).upper()
        if identity in existing_ok:
            continue
        payload_text = json.dumps(article_payload(article), ensure_ascii=False, sort_keys=True)
        input_hash = sha256_text(payload_text)
        prompt = build_prompt(article)
        prompt_hash = sha256_text(SYSTEM_PROMPT + "\n" + prompt)
        key = cache_key(article, provider, model)
        if not args.live:
            prompt_rows.append({
                "cache_key": key,
                "content_hash": content_hash(article),
                "ticker": norm(article.get("ticker")).upper(),
                "article_date": norm(article.get("date"))[:10],
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": prompt,
                "prompt_sha256": prompt_hash,
                "input_sha256": input_hash,
                "provider": provider,
                "model": model,
                "status": "pending_offline",
            })
            continue
        try:
            result = llm_provider.call_score(provider, client, provider_module, model, SYSTEM_PROMPT, prompt, 1200, "low", SCHEMA)
            annotation = validate(result["parsed"])
            annotation = MaterialAnnotation(
                **{k: getattr(annotation, k) for k in asdict(annotation) if k not in {"provider", "requested_model", "response_model", "request_id"}},
                provider=provider,
                requested_model=model,
                response_model=result.get("response_model", model),
                request_id=result.get("request_id", ""),
            )
            new_rows.append(record(article, key, annotation, prompt_hash, input_hash, provider, model, "ok"))
        except Exception as exc:
            new_rows.append(record(article, key, None, prompt_hash, input_hash, provider, model, "error", str(exc)))
            print(f"error ticker={article.get('ticker')} url={article.get('url')}: {exc}", flush=True)

    if prompt_rows:
        write_jsonl(PROMPT_PACKS_PATH, prompt_rows)
        print(f"saved prompts {PROMPT_PACKS_PATH} rows={len(prompt_rows)}", flush=True)
    combined = base_cache
    if new_rows:
        extra = pd.DataFrame(new_rows, columns=CACHE_COLUMNS)
        combined = pd.concat([base_cache, extra], ignore_index=True)
    Path(OUT_CACHE_PATH).parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUT_CACHE_PATH, index=False, encoding="utf-8")
    ok_new = sum(1 for r in new_rows if r.get("status") == "ok")
    err_new = sum(1 for r in new_rows if r.get("status") == "error")
    print(f"articles_selected={len(articles)} new_rows={len(new_rows)} ok={ok_new} error={err_new}", flush=True)
    print(f"saved {OUT_CACHE_PATH} rows={len(combined)}", flush=True)
    return 0 if err_new == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
