"""A7 — LLM scorecard feature extractor.

This experiment uses an LLM as an offline, point-in-time feature extractor for
Vietnamese financial news. It does **not** ask the LLM to forecast prices. Each
article is converted to a structured scorecard, cached, then aggregated to
``(ticker, quarter_id)`` features compatible with the existing experiment runner.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional, Protocol

import pandas as pd

from experiments.common.periods import quarter_id_from_date

try:  # pragma: no cover - package import path differs in tests/CLI
    from scripts import llm_provider
except ModuleNotFoundError:  # pragma: no cover
    import llm_provider  # type: ignore

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
ENRICHED_NEWS_PATH = "data/news/enriched/all_news_enriched.csv"
PROCESSED_NEWS_PATH = "data/news/processed/all_news_processed.csv"
NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
CACHE_PATH = "data/news/annotated/llm_scorecard.csv"
PROMPT_PACKS_PATH = "data/news/annotated/llm_scorecard_prompt_packs.jsonl"
MANIFEST_PATH = "data/news/annotated/llm_scorecard_manifest.json"
A7_OUTPUT_PATH = "data/features/keyword_features_A7.csv"

DEFAULT_MAX_TOKENS = 2048
DEFAULT_EFFORT = "high"
DEFAULT_TEXT_EXCERPT_CHARS = 4000

VALID_SENTIMENTS = ("positive", "negative", "neutral")
VALID_LEVELS = ("high", "medium", "low")
VALID_EVENT_TYPES = (
    "earnings",
    "dividend",
    "capital",
    "debt_risk",
    "legal_risk",
    "governance",
    "operation",
    "macro",
    "market",
    "other",
)
VALID_RELEVANCE = ("direct", "indirect", "irrelevant")

SENTIMENT_DEFAULT_SCORE = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}
LEVEL_DEFAULT_SCORE = {"high": 1.0, "medium": 0.6, "low": 0.3}
RELEVANCE_WEIGHT = {"direct": 1.0, "indirect": 0.5, "irrelevant": 0.0}

META_COLS = ["ticker", "quarter_id"]
LLM_FEATURE_COLS = [
    "llm_score_news_count",
    "llm_score_direct_ratio",
    "llm_score_irrelevant_ratio",
    "llm_sentiment_mean",
    "llm_sentiment_weighted_mean",
    "llm_positive_ratio",
    "llm_negative_ratio",
    "llm_materiality_mean",
    "llm_high_materiality_count",
    "llm_risk_mean",
    "llm_high_risk_count",
    "llm_confidence_mean",
    "llm_earnings_count",
    "llm_dividend_count",
    "llm_capital_count",
    "llm_debt_risk_count",
    "llm_legal_risk_count",
    "llm_governance_count",
]

CACHE_COLUMNS = [
    "content_hash",
    "ticker",
    "date",
    "title",
    "url",
    "sentiment",
    "sentiment_score",
    "materiality",
    "materiality_score",
    "risk_level",
    "risk_score",
    "event_type",
    "relevance_to_ticker",
    "confidence",
    "rationale",
    "provider",
    "requested_model",
    "response_model",
    "request_id",
    "prompt_sha256",
    "input_sha256",
    "annotated_at_utc",
    "status",
    "error",
]

FORBIDDEN_PROMPT_TOKENS = (
    "return",
    "label",
    "label_basic",
    "next_avg_close",
    "future",
    "realized",
    "prediction",
    "shap",
    "outcome",
)

SYSTEM_PROMPT = """Bạn là công cụ gán nhãn tin tức tài chính tiếng Việt.
Nhiệm vụ của bạn là đọc đúng nội dung bài báo được cung cấp và trả về JSON scorecard.
Chỉ sử dụng thông tin trong bài báo. Không dùng kiến thức ngoài. Không suy đoán giá cổ phiếu. Không đưa khuyến nghị mua/bán.
Nếu bài viết không liên quan trực tiếp tới ticker, đặt relevance_to_ticker = "irrelevant".
Trả về JSON hợp lệ, không thêm prose ngoài JSON.
"""

SCORECARD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": list(VALID_SENTIMENTS)},
        "sentiment_score": {"type": "number"},
        "materiality": {"type": "string", "enum": list(VALID_LEVELS)},
        "materiality_score": {"type": "number"},
        "risk_level": {"type": "string", "enum": list(VALID_LEVELS)},
        "risk_score": {"type": "number"},
        "event_type": {"type": "string", "enum": list(VALID_EVENT_TYPES)},
        "relevance_to_ticker": {"type": "string", "enum": list(VALID_RELEVANCE)},
        "confidence": {"type": "number"},
        "rationale": {"type": "string"},
    },
    "required": [
        "sentiment",
        "sentiment_score",
        "materiality",
        "materiality_score",
        "risk_level",
        "risk_score",
        "event_type",
        "relevance_to_ticker",
        "confidence",
        "rationale",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ScorecardAnnotation:
    sentiment: str
    sentiment_score: float
    materiality: str
    materiality_score: float
    risk_level: str
    risk_score: float
    event_type: str
    relevance_to_ticker: str
    confidence: float
    rationale: str
    provider: str = "mock"
    requested_model: str = "mock"
    response_model: str = "mock"
    request_id: str = ""


class ScorecardClient(Protocol):
    def annotate(self, article: dict[str, Any]) -> ScorecardAnnotation:
        """Return scorecard annotation for one article dict."""
        ...


ClientFactory = Callable[[str | None], ScorecardClient]


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return re.sub(r"\s+", " ", str(value)).strip()


def _safe_float(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(parsed):
        return default
    return max(-1.0, min(1.0, parsed)) if default < 0 else max(0.0, min(1.0, parsed))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_hash(article: dict[str, Any]) -> str:
    existing = _normalize_text(article.get("content_hash"))
    if existing:
        return existing
    parts = [
        _normalize_text(article.get("ticker")).upper(),
        _normalize_text(article.get("date"))[:10],
        _normalize_text(article.get("title")).lower(),
        _normalize_text(article.get("description")).lower(),
        _normalize_text(article.get("url")).lower(),
    ]
    return sha256_text("\n".join(parts))


def _article_payload(article: dict[str, Any], text_excerpt_chars: int = DEFAULT_TEXT_EXCERPT_CHARS) -> dict[str, Any]:
    full_text = _normalize_text(article.get("full_text"))
    excerpt = full_text[:text_excerpt_chars].rstrip()
    return {
        "ticker": _normalize_text(article.get("ticker")).upper(),
        "date": _normalize_text(article.get("date") or article.get("published_at_detail"))[:10],
        "source": _normalize_text(article.get("source")),
        "title": _normalize_text(article.get("title")),
        "description": _normalize_text(article.get("description")),
        "article_summary": _normalize_text(article.get("article_summary")),
        "lead": _normalize_text(article.get("lead")),
        "full_text_excerpt": excerpt,
        "match_confidence": _normalize_text(article.get("match_confidence")),
    }


def build_scorecard_prompt(article: dict[str, Any]) -> str:
    """Build prompt from point-in-time article fields and reject future tokens."""
    payload = _article_payload(article)
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    prompt = (
        "Hãy gán nhãn scorecard cho bài báo dưới đây.\n\n"
        "Các trường cần trả về:\n"
        "- sentiment: positive | negative | neutral\n"
        "- sentiment_score: số trong [-1, 1], positive gần +1, negative gần -1, neutral gần 0\n"
        "- materiality: high | medium | low\n"
        "- materiality_score: số trong [0, 1]\n"
        "- risk_level: high | medium | low\n"
        "- risk_score: số trong [0, 1]\n"
        "- event_type: earnings | dividend | capital | debt_risk | legal_risk | governance | operation | macro | market | other\n"
        "- relevance_to_ticker: direct | indirect | irrelevant\n"
        "- confidence: số trong [0, 1]\n"
        "- rationale: giải thích ngắn, bám sát bằng chứng trong bài\n\n"
        "Bài báo:\n"
        f"{payload_json}"
    )
    lower = prompt.lower()
    leaked = [token for token in FORBIDDEN_PROMPT_TOKENS if token in lower]
    if leaked:
        raise ValueError(f"Scorecard prompt contains forbidden token(s): {leaked}")
    return prompt


def _extract_json_object(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text or "", flags=re.DOTALL)
    if not match:
        raise ValueError("LLM response did not contain a JSON object")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON is not an object")
    return parsed


def validate_scorecard(payload: dict[str, Any]) -> ScorecardAnnotation:
    sentiment = str(payload.get("sentiment", "")).strip().lower()
    if sentiment not in VALID_SENTIMENTS:
        raise ValueError(f"Invalid sentiment: {sentiment!r}")

    materiality = str(payload.get("materiality", "")).strip().lower()
    if materiality not in VALID_LEVELS:
        raise ValueError(f"Invalid materiality: {materiality!r}")

    risk_level = str(payload.get("risk_level", "")).strip().lower()
    if risk_level not in VALID_LEVELS:
        raise ValueError(f"Invalid risk_level: {risk_level!r}")

    event_type = str(payload.get("event_type", "")).strip().lower()
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Invalid event_type: {event_type!r}")

    relevance = str(payload.get("relevance_to_ticker", "")).strip().lower()
    if relevance not in VALID_RELEVANCE:
        raise ValueError(f"Invalid relevance_to_ticker: {relevance!r}")

    return ScorecardAnnotation(
        sentiment=sentiment,
        sentiment_score=_safe_float(payload.get("sentiment_score"), SENTIMENT_DEFAULT_SCORE[sentiment]),
        materiality=materiality,
        materiality_score=_safe_float(payload.get("materiality_score"), LEVEL_DEFAULT_SCORE[materiality]),
        risk_level=risk_level,
        risk_score=_safe_float(payload.get("risk_score"), LEVEL_DEFAULT_SCORE[risk_level]),
        event_type=event_type,
        relevance_to_ticker=relevance,
        confidence=_safe_float(payload.get("confidence"), 0.5),
        rationale=_normalize_text(payload.get("rationale"))[:500],
    )


class ProviderScorecardClient:
    """Provider-backed scorecard client using existing scripts.llm_provider."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        effort: str = DEFAULT_EFFORT,
    ) -> None:
        llm_provider.load_env_file(ROOT)
        self.provider = llm_provider.resolve_provider(provider)
        self.model = llm_provider.resolve_model(self.provider, model)
        self.max_tokens = max_tokens
        self.effort = effort
        self.client, self.provider_module = llm_provider.make_llm_client(self.provider)

    def annotate(self, article: dict[str, Any]) -> ScorecardAnnotation:  # pragma: no cover - real API
        prompt = build_scorecard_prompt(article)
        try:
            result = llm_provider.call_score(
                self.provider,
                self.client,
                self.provider_module,
                self.model,
                SYSTEM_PROMPT,
                prompt,
                self.max_tokens,
                self.effort,
                SCORECARD_SCHEMA,
            )
            payload = result["parsed"]
        except Exception:
            # Some providers/models may not support schema enforcement reliably.
            result = llm_provider.call_generate(
                self.provider,
                self.client,
                self.provider_module,
                self.model,
                SYSTEM_PROMPT,
                prompt,
                self.max_tokens,
                self.effort,
            )
            payload = _extract_json_object(result["text"])

        annotation = validate_scorecard(payload)
        return ScorecardAnnotation(
            **{k: getattr(annotation, k) for k in asdict(annotation) if k not in {"provider", "requested_model", "response_model", "request_id"}},
            provider=self.provider,
            requested_model=self.model,
            response_model=result.get("response_model", self.model),
            request_id=result.get("request_id", ""),
        )


def _default_client_factory(model: str | None = None) -> ScorecardClient:
    return ProviderScorecardClient(model=model)


def _live_llm_enabled() -> bool:
    value = os.environ.get("A7_LLM_SCORECARD_LIVE", "").strip().lower()
    return value in {"1", "true", "yes", "y"}


def _offline_client_factory(_model: str | None = None) -> ScorecardClient:
    raise llm_provider.ProviderConfigError(
        "A7 live LLM calls are disabled by default. Set A7_LLM_SCORECARD_LIVE=1 "
        "to call the configured provider; otherwise prompt packs are written for offline execution."
    )


def _load_cache(cache_path: str) -> pd.DataFrame:
    if not os.path.isfile(cache_path):
        return pd.DataFrame(columns=CACHE_COLUMNS)
    df = pd.read_csv(cache_path, encoding="utf-8", dtype={"content_hash": str})
    for col in CACHE_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df[CACHE_COLUMNS]


def _row_to_cache_record(
    article: dict[str, Any],
    annotation: ScorecardAnnotation | None,
    prompt_hash: str,
    input_hash: str,
    status: str,
    error: str = "",
) -> dict[str, Any]:
    record = {col: "" for col in CACHE_COLUMNS}
    record.update(
        {
            "content_hash": content_hash(article),
            "ticker": _normalize_text(article.get("ticker")).upper(),
            "date": _normalize_text(article.get("date") or article.get("published_at_detail"))[:10],
            "title": _normalize_text(article.get("title")),
            "url": _normalize_text(article.get("url")),
            "prompt_sha256": prompt_hash,
            "input_sha256": input_hash,
            "annotated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": status,
            "error": error[:500],
        }
    )
    if annotation is not None:
        for key, value in asdict(annotation).items():
            record[key] = value
    return record


def _write_jsonl(path: str, rows: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_manifest(path: str, data: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _prompt_pack_row(article: dict[str, Any]) -> dict[str, Any]:
    prompt = build_scorecard_prompt(article)
    input_json = json.dumps(_article_payload(article), ensure_ascii=False, sort_keys=True)
    return {
        "content_hash": content_hash(article),
        "ticker": _normalize_text(article.get("ticker")).upper(),
        "date": _normalize_text(article.get("date") or article.get("published_at_detail"))[:10],
        "url": _normalize_text(article.get("url")),
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": prompt,
        "input_sha256": sha256_text(input_json),
        "prompt_sha256": sha256_text(SYSTEM_PROMPT + "\n" + prompt),
        "status": "pending_offline",
    }


def _dedupe_articles(articles: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _, row in articles.iterrows():
        article = dict(row)
        chash = content_hash(article)
        if chash in seen:
            continue
        seen.add(chash)
        rows.append(article)
    return rows


def annotate_articles(
    articles: pd.DataFrame,
    cache_path: str = CACHE_PATH,
    prompt_packs_path: str = PROMPT_PACKS_PATH,
    manifest_path: str = MANIFEST_PATH,
    model: str | None = None,
    client: Optional[ScorecardClient] = None,
    client_factory: ClientFactory | None = None,
) -> pd.DataFrame:
    """Annotate articles with cached LLM scorecards.

    Missing credentials do not create fake annotations. Instead, prompt packs are
    written and only existing valid cache rows are returned.
    """
    cache = _load_cache(cache_path)
    ok_cache = cache[cache["status"].astype(str).str.lower().eq("ok")]
    cached_by_hash = {str(row["content_hash"]): row for _, row in ok_cache.iterrows()}

    if articles is None or articles.empty:
        logger.warning("Không có bài viết nào để gán scorecard.")
        return pd.DataFrame(columns=CACHE_COLUMNS)

    result_rows: list[dict[str, Any]] = []
    new_cache_rows: list[dict[str, Any]] = []
    pending_articles: list[dict[str, Any]] = []

    for article in _dedupe_articles(articles):
        chash = content_hash(article)
        if chash in cached_by_hash:
            result_rows.append({col: cached_by_hash[chash][col] for col in CACHE_COLUMNS})
        else:
            pending_articles.append(article)

    valid_pending_articles: list[dict[str, Any]] = []
    for article in pending_articles:
        input_json = json.dumps(_article_payload(article), ensure_ascii=False, sort_keys=True)
        try:
            build_scorecard_prompt(article)
        except Exception as exc:  # noqa: BLE001 - prompt guard failure should not abort batch
            logger.warning("Bỏ qua bài không đạt prompt guard %s: %s", content_hash(article), exc)
            new_cache_rows.append(
                _row_to_cache_record(article, None, "", sha256_text(input_json), "error", str(exc))
            )
            continue
        valid_pending_articles.append(article)
    pending_articles = valid_pending_articles

    prompt_rows: list[dict[str, Any]] = []
    active_client = client
    factory = client_factory or (_default_client_factory if _live_llm_enabled() else _offline_client_factory)

    if pending_articles and active_client is None:
        try:
            active_client = factory(model)
        except Exception as exc:  # noqa: BLE001 - offline prompt fallback
            logger.warning("Không khởi tạo được LLM client; ghi prompt packs offline: %s", exc)
            prompt_rows = [_prompt_pack_row(article) for article in pending_articles]
            pending_articles = []

    for idx, article in enumerate(pending_articles):
        prompt = build_scorecard_prompt(article)
        input_json = json.dumps(_article_payload(article), ensure_ascii=False, sort_keys=True)
        prompt_hash = sha256_text(SYSTEM_PROMPT + "\n" + prompt)
        input_hash = sha256_text(input_json)
        try:
            assert active_client is not None
            annotation = active_client.annotate(article)
        except Exception as exc:  # noqa: BLE001 - keep batch moving
            provider = getattr(active_client, "provider", "")
            provider_module = getattr(active_client, "provider_module", None)
            if provider and llm_provider.is_auth_error(provider, exc, provider_module):
                logger.warning("LLM auth/provider error; ghi prompt packs offline: %s", exc)
                prompt_rows = [_prompt_pack_row(a) for a in pending_articles[idx:]]
                break
            logger.warning("Lỗi scorecard article %s: %s", content_hash(article), exc)
            new_cache_rows.append(
                _row_to_cache_record(article, None, prompt_hash, input_hash, "error", str(exc))
            )
            continue

        record = _row_to_cache_record(article, annotation, prompt_hash, input_hash, "ok")
        new_cache_rows.append(record)
        result_rows.append(record)

    if new_cache_rows:
        os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
        new_df = pd.DataFrame(new_cache_rows, columns=CACHE_COLUMNS)
        updated_cache = new_df if cache.empty else pd.concat([cache, new_df], ignore_index=True)
        updated_cache.to_csv(cache_path, index=False, encoding="utf-8")
        logger.info("Đã ghi %d dòng cache scorecard mới vào %s.", len(new_cache_rows), cache_path)

    if prompt_rows:
        _write_jsonl(prompt_packs_path, prompt_rows)
        _write_manifest(
            manifest_path,
            {
                "status": "llm_scorecard_pending_offline",
                "prompt_packs_path": prompt_packs_path,
                "pending_articles": len(prompt_rows),
                "cached_ok_articles": len(result_rows),
                "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
        )
        logger.warning("Đã ghi %d prompt scorecard offline vào %s.", len(prompt_rows), prompt_packs_path)

    return pd.DataFrame(result_rows, columns=CACHE_COLUMNS)


def _load_news_by_quarter_keys(news_path: str) -> Optional[pd.DataFrame]:
    if not os.path.isfile(news_path):
        return None
    df = pd.read_csv(news_path, encoding="utf-8")
    if not set(META_COLS).issubset(df.columns):
        return None
    return df[META_COLS].drop_duplicates()


def _safe_quarter(value: Any) -> Optional[str]:
    try:
        return quarter_id_from_date(value)
    except (ValueError, TypeError):
        return None


def _empty_features() -> pd.DataFrame:
    return pd.DataFrame(columns=META_COLS + LLM_FEATURE_COLS)


def aggregate_scorecard_features(
    annotations: pd.DataFrame,
    news_by_quarter_keys: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Aggregate article-level scorecards to ticker-quarter ML features."""
    if annotations is None or annotations.empty:
        agg = _empty_features()
    else:
        work = annotations[annotations["status"].astype(str).str.lower().eq("ok")].copy()
        if work.empty:
            agg = _empty_features()
        else:
            work["quarter_id"] = work["date"].map(_safe_quarter)
            work = work[work["quarter_id"].notna()].copy()
            for col in ("sentiment_score", "materiality_score", "risk_score", "confidence"):
                work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0.0)
            work["sentiment"] = work["sentiment"].astype(str).str.lower()
            work["materiality"] = work["materiality"].astype(str).str.lower()
            work["risk_level"] = work["risk_level"].astype(str).str.lower()
            work["event_type"] = work["event_type"].astype(str).str.lower()
            work["relevance_to_ticker"] = work["relevance_to_ticker"].astype(str).str.lower()
            work["_relevance_weight"] = work["relevance_to_ticker"].map(RELEVANCE_WEIGHT).fillna(0.0)
            work["_weighted_sentiment"] = (
                work["sentiment_score"]
                * work["materiality_score"]
                * work["_relevance_weight"]
                * work["confidence"]
            )

            rows: list[dict[str, Any]] = []
            for (ticker, quarter_id), group in work.groupby(META_COLS, sort=True):
                total = max(len(group), 1)
                row = {
                    "ticker": ticker,
                    "quarter_id": quarter_id,
                    "llm_score_news_count": float(len(group)),
                    "llm_score_direct_ratio": float((group["relevance_to_ticker"] == "direct").sum() / total),
                    "llm_score_irrelevant_ratio": float((group["relevance_to_ticker"] == "irrelevant").sum() / total),
                    "llm_sentiment_mean": float(group["sentiment_score"].mean()),
                    "llm_sentiment_weighted_mean": float(group["_weighted_sentiment"].sum() / total),
                    "llm_positive_ratio": float((group["sentiment"] == "positive").sum() / total),
                    "llm_negative_ratio": float((group["sentiment"] == "negative").sum() / total),
                    "llm_materiality_mean": float(group["materiality_score"].mean()),
                    "llm_high_materiality_count": float((group["materiality"] == "high").sum()),
                    "llm_risk_mean": float(group["risk_score"].mean()),
                    "llm_high_risk_count": float((group["risk_level"] == "high").sum()),
                    "llm_confidence_mean": float(group["confidence"].mean()),
                    "llm_earnings_count": float((group["event_type"] == "earnings").sum()),
                    "llm_dividend_count": float((group["event_type"] == "dividend").sum()),
                    "llm_capital_count": float((group["event_type"] == "capital").sum()),
                    "llm_debt_risk_count": float((group["event_type"] == "debt_risk").sum()),
                    "llm_legal_risk_count": float((group["event_type"] == "legal_risk").sum()),
                    "llm_governance_count": float((group["event_type"] == "governance").sum()),
                }
                rows.append(row)
            agg = pd.DataFrame(rows, columns=META_COLS + LLM_FEATURE_COLS)

    if news_by_quarter_keys is not None and not news_by_quarter_keys.empty:
        keys = news_by_quarter_keys[META_COLS].drop_duplicates()
        merged = keys.merge(agg, on=META_COLS, how="left")
        for col in LLM_FEATURE_COLS:
            merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)
        return merged[META_COLS + LLM_FEATURE_COLS].reset_index(drop=True)

    return agg[META_COLS + LLM_FEATURE_COLS].reset_index(drop=True)


def _select_article_source(enriched_path: str, processed_path: str) -> str:
    if os.path.isfile(enriched_path):
        return enriched_path
    return processed_path


def build_a7_features(
    enriched_news_path: str = ENRICHED_NEWS_PATH,
    processed_news_path: str = PROCESSED_NEWS_PATH,
    news_by_quarter_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = A7_OUTPUT_PATH,
    cache_path: str = CACHE_PATH,
    prompt_packs_path: str = PROMPT_PACKS_PATH,
    manifest_path: str = MANIFEST_PATH,
    model: str | None = None,
    client: Optional[ScorecardClient] = None,
    client_factory: ClientFactory | None = None,
) -> pd.DataFrame:
    """Build and write A7 scorecard features for the experiment runner."""
    source_path = _select_article_source(enriched_news_path, processed_news_path)
    if not os.path.isfile(source_path):
        logger.error("Không tìm thấy nguồn tin tức cho A7: %s", source_path)
        return _empty_features()

    articles = pd.read_csv(source_path, encoding="utf-8")
    logger.info("Đã nạp %d bài viết cho A7 từ %s.", len(articles), source_path)

    annotations = annotate_articles(
        articles,
        cache_path=cache_path,
        prompt_packs_path=prompt_packs_path,
        manifest_path=manifest_path,
        model=model,
        client=client,
        client_factory=client_factory,
    )
    if annotations.empty:
        logger.warning(
            "Chưa có annotation scorecard hợp lệ; không ghi %s để tránh chạy ML với feature giả.",
            output_path,
        )
        return _empty_features()

    news_keys = _load_news_by_quarter_keys(news_by_quarter_path)
    features = aggregate_scorecard_features(annotations, news_by_quarter_keys=news_keys)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    _write_manifest(
        manifest_path,
        {
            "status": "llm_scorecard_features_ready",
            "article_source_path": source_path,
            "cache_path": cache_path,
            "feature_path": output_path,
            "ok_annotations": int(len(annotations)),
            "feature_rows": int(len(features)),
            "feature_columns": LLM_FEATURE_COLS,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
    )
    logger.info("Đã ghi A7 features (%d hàng, %d cột) vào %s.", len(features), len(features.columns), output_path)
    return features


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    build_a7_features()
