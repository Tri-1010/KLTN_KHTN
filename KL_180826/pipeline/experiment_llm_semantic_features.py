"""Experiment: LLM semantic news features at daily/rolling horizons.

This research script is intentionally separate from the production quarter-based
pipeline. It uses an LLM as an article-level feature extractor, aggregates those
semantic outputs to a ticker/trading-date panel, and tests whether they improve
future 1/5/10/20 trading-day direction prediction over daily technical features.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from pipeline.task7_tech_features import compute_daily_indicators, _find_column
from pipeline.task10_train import build_ml_models, evaluate_model, fit_imputer, prepare_features
from scripts import llm_provider

for _stream in (sys.stdout, sys.stderr):
    _rc = getattr(_stream, "reconfigure", None)
    if _rc is not None:
        try:
            _rc(encoding="utf-8", errors="replace")
        except Exception:
            pass

logger = logging.getLogger(__name__)

PRICES_PATH = "data/prices/all_vn30_prices.csv"
NEWS_PATH = "data/news/processed/all_news_processed.csv"
CACHE_PATH = "data/experiments/llm_semantic/article_semantics_cache_spec_v1.csv"
PROMPT_PACKS_PATH = "data/experiments/llm_semantic/article_semantic_prompt_packs_spec_v1.jsonl"
DAILY_FEATURE_PATH = "data/experiments/llm_semantic/daily_semantic_features.csv"
PANEL_PATH = "data/experiments/llm_semantic/daily_ml_panel.csv"
RESULT_PATH = "reports/llm_semantic_feature_experiment.csv"
SUMMARY_PATH = "reports/llm_semantic_feature_summary.md"
PROMPT_VERSION = "semantic_spec_v1_0"
DEFAULT_HORIZONS = (1, 5, 10, 20)
DEFAULT_ROLL_WINDOWS = (3, 5, 10, 20)
PILOT_TICKERS = ("FPT", "VCB", "HPG", "VNM", "SSI")

VALID_SENTIMENTS = {"positive", "neutral", "negative", "mixed"}
VALID_HORIZONS = {"short_term", "medium_term", "long_term"}
SENTIMENT_SCORE = {"positive": 1.0, "neutral": 0.0, "negative": -1.0, "mixed": 0.0}

CACHE_COLUMNS = [
    "cache_key",
    "content_hash",
    "ticker",
    "company_name",
    "article_date",
    "title",
    "url",
    "is_stock_relevant",
    "sentiment",
    "sentiment_score",
    "importance_score",
    "expected_impact_score",
    "uncertainty_score",
    "novelty_score",
    "reasoning_confidence",
    "time_horizon",
    "summary",
    "reason",
    "provider",
    "requested_model",
    "response_model",
    "request_id",
    "prompt_sha256",
    "input_sha256",
    "truncated",
    "article_text_chars",
    "extracted_at_utc",
    "status",
    "error",
]

FORBIDDEN_INPUT_TOKENS = (
    "label_basic",
    "future_return",
    "next_close",
    "realized",
    "prediction",
    "shap",
    "outcome",
    "target price",
    "buy recommendation",
    "sell recommendation",
)

SYSTEM_PROMPT = """Bạn là công cụ trích xuất đặc trưng ngữ nghĩa từ tin tức tài chính tiếng Việt.
Chỉ dùng nội dung bài báo được cung cấp. Không dùng kiến thức ngoài.
Đọc toàn bộ nội dung bài báo được cung cấp trước khi gán nhãn.
Trả về DUY NHẤT một JSON object hợp lệ theo schema yêu cầu.
Không dự báo giá cổ phiếu, không dự báo phản ứng thị trường, không đưa khuyến nghị mua/bán/nắm giữ.
Không xuất target price, future EPS, future revenue, hoặc giả định không có bằng chứng trong bài.
Không xuất sentiment_score, event_type, relevance_to_ticker, information_magnitude_score, novelty_hint_score.
expected_impact_score đo độ lớn tác động hợp lý nếu nhà đầu tư tin thông tin này; chỉ đo magnitude, không đo chiều tăng/giảm.
sentiment mô tả sắc thái ngữ nghĩa của bài viết, không phải khuyến nghị đầu tư.
Nếu bài không trực tiếp liên quan doanh nghiệp niêm yết/mã cổ phiếu đang xét, đặt is_stock_relevant=false và vẫn chấm điểm theo bằng chứng tối thiểu.
"""

SEMANTIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "ticker": {"type": ["string", "null"]},
        "company_name": {"type": ["string", "null"]},
        "article_date": {"type": "string"},
        "is_stock_relevant": {"type": "boolean"},
        "sentiment": {"type": "string", "enum": sorted(VALID_SENTIMENTS)},
        "importance_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "expected_impact_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "uncertainty_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "novelty_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "time_horizon": {"type": "string", "enum": sorted(VALID_HORIZONS)},
        "reasoning_confidence": {"type": "integer", "minimum": 1, "maximum": 5},
        "summary": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": [
        "ticker",
        "company_name",
        "article_date",
        "is_stock_relevant",
        "sentiment",
        "importance_score",
        "expected_impact_score",
        "uncertainty_score",
        "novelty_score",
        "time_horizon",
        "reasoning_confidence",
        "summary",
        "reason",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class SemanticAnnotation:
    ticker: str | None
    company_name: str | None
    article_date: str
    is_stock_relevant: bool
    sentiment: str
    sentiment_score: float
    importance_score: int
    expected_impact_score: int
    uncertainty_score: int
    novelty_score: int
    time_horizon: str
    reasoning_confidence: int
    summary: str
    reason: str
    provider: str = "mock"
    requested_model: str = "mock"
    response_model: str = "mock"
    request_id: str = ""


def _norm(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return re.sub(r"\s+", " ", str(value)).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clip_float(value: Any, low: float, high: float, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    if pd.isna(parsed):
        parsed = default
    return float(min(high, max(low, parsed)))


def _clip_int(value: Any, low: int = 1, high: int = 5, default: int = 3) -> int:
    try:
        parsed = int(round(float(value)))
    except (TypeError, ValueError):
        parsed = default
    return int(min(high, max(low, parsed)))


def _strict_bool(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"Invalid {field}: {value!r}")


def article_content_hash(article: dict[str, Any]) -> str:
    existing = _norm(article.get("content_hash"))
    if existing:
        return existing
    parts = [
        _norm(article.get("ticker")).upper(),
        _norm(article.get("date"))[:10],
        _norm(article.get("url")).lower(),
        _norm(article.get("title")).lower(),
        _norm(article.get("description")).lower(),
        _norm(article.get("full_text") or article.get("text_clean") or article.get("text_tokenized")).lower(),
    ]
    return sha256_text("\n".join(parts))


def _article_text(article: dict[str, Any]) -> str:
    text = _norm(article.get("full_text") or article.get("text_clean") or article.get("text_tokenized"))
    if not text:
        text = f"{_norm(article.get('title'))}. {_norm(article.get('description'))}".strip()
    return text


def article_payload(article: dict[str, Any], max_chars: int = 12000) -> dict[str, Any]:
    text = _article_text(article)
    return {
        "ticker": _norm(article.get("ticker")).upper(),
        "article_date": _norm(article.get("date"))[:10],
        "source": _norm(article.get("source")),
        "title": _norm(article.get("title")),
        "description": _norm(article.get("description")),
        "article_text": text[:max_chars],
        "article_text_chars": len(text),
        "truncated": len(text) > max_chars,
        "url": _norm(article.get("url")),
    }


def build_semantic_prompt(article: dict[str, Any], max_article_chars: int = 12000) -> str:
    payload = article_payload(article, max_article_chars)
    payload_text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    lower = payload_text.lower()
    leaked = [token for token in FORBIDDEN_INPUT_TOKENS if token in lower]
    if leaked:
        raise ValueError(f"Article payload contains forbidden token(s): {leaked}")
    return (
        "Hãy trích xuất đặc trưng ngữ nghĩa cho bài báo dưới đây.\n"
        "Trả về đúng các trường schema: ticker, company_name, article_date, is_stock_relevant, sentiment, "
        "importance_score, expected_impact_score, uncertainty_score, novelty_score, time_horizon, reasoning_confidence, summary, reason.\n"
        "Không xuất sentiment_score, event_type, relevance_to_ticker, information_magnitude_score, novelty_hint_score.\n"
        "Không dự báo giá, không dự báo phản ứng thị trường, không khuyến nghị mua/bán/nắm giữ.\n"
        "expected_impact_score đo magnitude tác động kỳ vọng, không đo chiều tăng/giảm.\n"
        "sentiment là sắc thái ngữ nghĩa, không phải khuyến nghị.\n"
        "Các điểm score là 1..5, trong đó 5 là cao nhất.\n\n"
        "Bài báo:\n"
        f"{payload_text}"
    )


def article_payload_meta(article: dict[str, Any], max_chars: int = 12000) -> dict[str, Any]:
    text = _article_text(article)
    return {"truncated": len(text) > max_chars, "article_text_chars": len(text)}


def _coerce_time_horizon(value: Any) -> str:
    raw = str(value or "short_term").strip().lower()
    if raw in VALID_HORIZONS:
        return raw
    if any(token in raw for token in ("short", "ngắn")):
        return "short_term"
    if any(token in raw for token in ("medium", "trung")):
        return "medium_term"
    if any(token in raw for token in ("long", "dài")):
        return "long_term"
    return "short_term"


def validate_semantic(payload: dict[str, Any]) -> SemanticAnnotation:
    missing = [field for field in SEMANTIC_SCHEMA["required"] if field not in payload]
    if missing:
        raise ValueError(f"Missing semantic field(s): {missing}")
    unexpected = {"sentiment_score", "event_type", "relevance_to_ticker", "information_magnitude_score", "novelty_hint_score"} & set(payload)
    if unexpected:
        raise ValueError(f"Unexpected legacy semantic field(s): {sorted(unexpected)}")
    sentiment = str(payload.get("sentiment", "neutral")).strip().lower()
    if sentiment not in VALID_SENTIMENTS:
        raise ValueError(f"Invalid sentiment: {sentiment!r}")
    is_stock_relevant = _strict_bool(payload.get("is_stock_relevant", False), "is_stock_relevant")
    return SemanticAnnotation(
        ticker=_norm(payload.get("ticker")).upper() or None,
        company_name=_norm(payload.get("company_name")) or None,
        article_date=_norm(payload.get("article_date"))[:10],
        is_stock_relevant=is_stock_relevant,
        sentiment=sentiment,
        sentiment_score=SENTIMENT_SCORE[sentiment],
        importance_score=_clip_int(payload.get("importance_score")),
        expected_impact_score=_clip_int(payload.get("expected_impact_score")),
        uncertainty_score=_clip_int(payload.get("uncertainty_score")),
        novelty_score=_clip_int(payload.get("novelty_score")),
        time_horizon=_coerce_time_horizon(payload.get("time_horizon")),
        reasoning_confidence=_clip_int(payload.get("reasoning_confidence")),
        summary=_norm(payload.get("summary"))[:240],
        reason=_norm(payload.get("reason"))[:400],
    )


class SemanticClient:
    def annotate(self, article: dict[str, Any]) -> SemanticAnnotation:  # pragma: no cover - protocol-like
        raise NotImplementedError


class ProviderSemanticClient(SemanticClient):
    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        max_tokens: int = 1200,
        effort: str = "low",
        max_article_chars: int = 12000,
    ) -> None:
        llm_provider.load_env_file(ROOT)
        self.provider = llm_provider.resolve_provider(provider)
        self.model = llm_provider.resolve_model(self.provider, model)
        self.max_tokens = max_tokens
        self.effort = effort
        self.max_article_chars = max_article_chars
        self.client, self.provider_module = llm_provider.make_llm_client(self.provider)

    def annotate(self, article: dict[str, Any]) -> SemanticAnnotation:  # pragma: no cover - API path
        prompt = build_semantic_prompt(article, self.max_article_chars)
        result = llm_provider.call_score(
            self.provider,
            self.client,
            self.provider_module,
            self.model,
            SYSTEM_PROMPT,
            prompt,
            self.max_tokens,
            self.effort,
            SEMANTIC_SCHEMA,
        )
        annotation = validate_semantic(result["parsed"])
        return SemanticAnnotation(
            **{k: getattr(annotation, k) for k in asdict(annotation) if k not in {"provider", "requested_model", "response_model", "request_id"}},
            provider=self.provider,
            requested_model=self.model,
            response_model=result.get("response_model", self.model),
            request_id=result.get("request_id", ""),
        )


def _cache_key(article: dict[str, Any], provider: str, model: str) -> str:
    parts = [PROMPT_VERSION, provider, model, article_content_hash(article), _norm(article.get("ticker")).upper(), _norm(article.get("date"))[:10]]
    return sha256_text("\n".join(parts))


def _load_cache(cache_path: str) -> pd.DataFrame:
    if not os.path.isfile(cache_path):
        return pd.DataFrame(columns=CACHE_COLUMNS)
    df = pd.read_csv(cache_path, encoding="utf-8", dtype={"cache_key": str, "content_hash": str})
    for col in CACHE_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df[CACHE_COLUMNS]


def _record(
    article: dict[str, Any],
    cache_key: str,
    annotation: SemanticAnnotation | None,
    prompt_hash: str,
    input_hash: str,
    status: str,
    error: str = "",
    max_article_chars: int = 12000,
) -> dict[str, Any]:
    payload_meta = article_payload_meta(article, max_article_chars)
    row = {col: "" for col in CACHE_COLUMNS}
    row.update(
        {
            "cache_key": cache_key,
            "content_hash": article_content_hash(article),
            "ticker": _norm(article.get("ticker")).upper(),
            "article_date": _norm(article.get("date"))[:10],
            "title": _norm(article.get("title")),
            "url": _norm(article.get("url")),
            "prompt_sha256": prompt_hash,
            "input_sha256": input_hash,
            "truncated": payload_meta["truncated"],
            "article_text_chars": payload_meta["article_text_chars"],
            "extracted_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": status,
            "error": error[:500],
        }
    )
    if annotation is not None:
        for key, value in asdict(annotation).items():
            if key in {"ticker", "article_date"}:
                continue
            row[key] = value
    return row


def _write_jsonl(path: str, rows: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def annotate_articles(
    articles: pd.DataFrame,
    cache_path: str = CACHE_PATH,
    prompt_packs_path: str = PROMPT_PACKS_PATH,
    provider: str | None = None,
    model: str | None = None,
    max_articles: int | None = None,
    live: bool = False,
    client: SemanticClient | None = None,
    max_article_chars: int = 12000,
) -> pd.DataFrame:
    provider_name = llm_provider.resolve_provider(provider)
    model_name = llm_provider.resolve_model(provider_name, model)
    cache = _load_cache(cache_path)
    ok_cache = cache[cache["status"].astype(str).eq("ok")]
    cached = {str(row["cache_key"]): row for _, row in ok_cache.drop_duplicates("cache_key", keep="last").iterrows()}

    rows: list[dict[str, Any]] = []
    new_rows: list[dict[str, Any]] = []
    prompt_rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    active_client = client

    for _, source_row in articles.iterrows():
        article = dict(source_row)
        key = _cache_key(article, provider_name, model_name)
        if key in seen:
            continue
        seen.add(key)

        input_json = json.dumps(article_payload(article, max_article_chars), ensure_ascii=False, sort_keys=True)
        input_hash = sha256_text(input_json)
        try:
            prompt = build_semantic_prompt(article, max_article_chars)
        except Exception as exc:  # noqa: BLE001 - guard failure should not abort batch
            row = _record(article, key, None, "", input_hash, "error", str(exc), max_article_chars)
            new_rows.append(row)
            continue
        prompt_hash = sha256_text(SYSTEM_PROMPT + "\n" + prompt)

        cached_row = cached.get(key)
        if cached_row is not None and str(cached_row.get("prompt_sha256", "")) == prompt_hash and str(cached_row.get("input_sha256", "")) == input_hash:
            rows.append({col: cached_row.get(col, "") for col in CACHE_COLUMNS})
            continue
        if max_articles is not None and len(new_rows) + len(prompt_rows) >= max_articles:
            continue
        if not live and active_client is None:
            prompt_rows.append(
                {
                    "cache_key": key,
                    "content_hash": article_content_hash(article),
                    "ticker": _norm(article.get("ticker")).upper(),
                    "article_date": _norm(article.get("date"))[:10],
                    "system_prompt": SYSTEM_PROMPT,
                    "user_prompt": prompt,
                    "prompt_sha256": prompt_hash,
                    "input_sha256": input_hash,
                    "provider": provider_name,
                    "model": model_name,
                    "status": "pending_offline",
                }
            )
            continue
        if active_client is None:
            active_client = ProviderSemanticClient(provider_name, model_name, max_article_chars=max_article_chars)
        try:
            annotation = active_client.annotate(article)
            row = _record(article, key, annotation, prompt_hash, input_hash, "ok", max_article_chars=max_article_chars)
            rows.append(row)
            new_rows.append(row)
        except Exception as exc:  # noqa: BLE001 - keep batch moving and cache errors
            row = _record(article, key, None, prompt_hash, input_hash, "error", str(exc), max_article_chars)
            new_rows.append(row)
            logger.warning("Semantic extraction failed for %s: %s", key, exc)

    if new_rows:
        os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
        new_df = pd.DataFrame(new_rows, columns=CACHE_COLUMNS)
        updated = new_df if cache.empty else pd.concat([cache, new_df], ignore_index=True)
        updated.to_csv(cache_path, index=False, encoding="utf-8")
    if prompt_rows:
        _write_jsonl(prompt_packs_path, prompt_rows)
        logger.warning("Wrote %d offline semantic prompt packs to %s", len(prompt_rows), prompt_packs_path)
    return pd.DataFrame(rows, columns=CACHE_COLUMNS)


def load_prices(path: str = PRICES_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "ticker", "close"]).copy()
    df["ticker"] = df["ticker"].astype(str).str.upper()
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


def load_news(path: str = NEWS_PATH, tickers: Iterable[str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "ticker"]).copy()
    df["ticker"] = df["ticker"].astype(str).str.upper()
    if tickers is not None:
        wanted = {t.upper() for t in tickers}
        df = df[df["ticker"].isin(wanted)].copy()
    return df.sort_values(["date", "ticker"]).reset_index(drop=True)


def build_daily_technical(prices: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for ticker, group in prices.groupby("ticker", sort=True):
        work = group.sort_values("date").copy()
        work = compute_daily_indicators(work)
        work["return_1d"] = work["close"].pct_change(1)
        for window in (5, 10, 20):
            work[f"return_{window}d"] = work["close"].pct_change(window)
            work[f"volatility_{window}d"] = work["daily_return"].rolling(window, min_periods=2).std() * np.sqrt(window)
        work["volume_change_5d"] = work["volume"].pct_change(5)
        vol_mean = work["volume"].rolling(20, min_periods=5).mean()
        vol_std = work["volume"].rolling(20, min_periods=5).std().replace(0, np.nan)
        work["volume_zscore_20d"] = (work["volume"] - vol_mean) / vol_std
        macd_col = _find_column(work, "MACDh_")
        bbl = _find_column(work, "BBL_")
        bbu = _find_column(work, "BBU_")
        work["macd_hist"] = work[macd_col] if macd_col else np.nan
        if bbl and bbu:
            rng = (work[bbu] - work[bbl]).replace(0, np.nan)
            work["bb_position"] = (work["close"] - work[bbl]) / rng
        else:
            work["bb_position"] = np.nan
        work["price_vs_sma20"] = (work["close"] - work["SMA_20"]) / work["SMA_20"].replace(0, np.nan)
        work["price_vs_sma50"] = (work["close"] - work["SMA_50"]) / work["SMA_50"].replace(0, np.nan)
        frames.append(work)
    return pd.concat(frames, ignore_index=True).sort_values(["ticker", "date"]).reset_index(drop=True)


def build_forward_labels(prices: pd.DataFrame, horizons: Iterable[int] = DEFAULT_HORIZONS) -> pd.DataFrame:
    frames = []
    for ticker, group in prices.groupby("ticker", sort=True):
        work = group[["ticker", "date", "close"]].sort_values("date").copy()
        for h in horizons:
            future = work["close"].shift(-h)
            work[f"future_return_{h}d"] = future / work["close"] - 1
            work[f"label_up_{h}d"] = np.where(work[f"future_return_{h}d"].notna(), (work[f"future_return_{h}d"] > 0).astype(int), np.nan)
        frames.append(work.drop(columns=["close"]))
    return pd.concat(frames, ignore_index=True)


def _map_article_to_trading_date(articles: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    price_dates = {ticker: sorted(group["date"].dt.normalize().unique()) for ticker, group in prices.groupby("ticker")}
    rows = []
    for _, row in articles.iterrows():
        ticker = str(row["ticker"]).upper()
        dates = price_dates.get(ticker, [])
        if not dates:
            continue
        article_date = pd.Timestamp(row["article_date"]).normalize()
        pos = np.searchsorted(dates, np.datetime64(article_date), side="left")
        if pos >= len(dates):
            continue
        out = dict(row)
        out["date"] = pd.Timestamp(dates[pos])
        rows.append(out)
    return pd.DataFrame(rows)


def aggregate_daily_semantics(annotations: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    grid = prices[["ticker", "date"]].drop_duplicates().copy()
    feature_cols: list[str] = []
    if annotations is None or annotations.empty:
        out = grid.copy()
    else:
        ok = annotations[annotations["status"].astype(str).eq("ok")].copy()
        if not ok.empty:
            if "is_stock_relevant" in ok.columns:
                relevant = ok["is_stock_relevant"].astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})
            else:
                relevant = pd.Series(False, index=ok.index)
            ok = ok[relevant].copy()
        if ok.empty:
            out = grid.copy()
        else:
            ok["article_date"] = pd.to_datetime(ok["article_date"], errors="coerce")
            ok = ok.dropna(subset=["article_date", "ticker"])
            ok = _map_article_to_trading_date(ok, prices)
            if ok.empty:
                out = grid.copy()
            else:
                for col in ("sentiment_score", "importance_score", "expected_impact_score", "uncertainty_score", "novelty_score", "reasoning_confidence"):
                    if col not in ok.columns:
                        ok[col] = 0.0
                    ok[col] = pd.to_numeric(ok[col], errors="coerce").fillna(0.0)
                ok["_weighted_sentiment"] = ok["sentiment_score"] * ok["importance_score"] * ok["reasoning_confidence"] / 25.0
                groups = ok.groupby(["ticker", "date"], sort=True)
                daily = groups.size().rename("llm_news_count").reset_index()
                daily["llm_has_news"] = 1.0
                daily = daily.merge(groups["sentiment_score"].mean().rename("llm_sentiment_mean").reset_index(), on=["ticker", "date"])
                daily = daily.merge(groups["_weighted_sentiment"].mean().rename("llm_sentiment_weighted_mean").reset_index(), on=["ticker", "date"])
                for source, prefix in (
                    ("importance_score", "llm_importance"),
                    ("expected_impact_score", "llm_expected_impact"),
                    ("uncertainty_score", "llm_uncertainty"),
                    ("novelty_score", "llm_novelty"),
                    ("reasoning_confidence", "llm_confidence"),
                ):
                    daily = daily.merge(groups[source].mean().rename(f"{prefix}_mean").reset_index(), on=["ticker", "date"])
                    if source in {"importance_score", "expected_impact_score"}:
                        daily = daily.merge(groups[source].max().rename(f"{prefix}_max").reset_index(), on=["ticker", "date"])

                def ratio(col: str, value: str, name: str) -> pd.DataFrame:
                    return groups[col].apply(lambda s: (s.astype(str).str.lower() == value).mean()).rename(name).reset_index()

                for value in ("positive", "negative", "mixed"):
                    daily = daily.merge(ratio("sentiment", value, f"llm_{value}_ratio"), on=["ticker", "date"])
                for value, name in (("short_term", "short"), ("medium_term", "medium"), ("long_term", "long")):
                    daily = daily.merge(ratio("time_horizon", value, f"llm_horizon_{name}_ratio"), on=["ticker", "date"])
                out = grid.merge(daily, on=["ticker", "date"], how="left")
    for col in out.columns:
        if col.startswith("llm_"):
            feature_cols.append(col)
    for col in feature_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    if "llm_has_news" not in out.columns:
        out["llm_has_news"] = 0.0
    if "llm_news_count" not in out.columns:
        out["llm_news_count"] = 0.0
    out = add_rolling_semantic_features(out)
    return out


def add_rolling_semantic_features(daily: pd.DataFrame, windows: Iterable[int] = DEFAULT_ROLL_WINDOWS) -> pd.DataFrame:
    out = daily.sort_values(["ticker", "date"]).copy()
    llm_cols = [c for c in out.columns if c.startswith("llm_") and not c.endswith(tuple(f"_roll_{w}d" for w in windows))]
    base_roll_cols = [c for c in llm_cols if c not in {"llm_has_news"}]
    frames = []
    for _, group in out.groupby("ticker", sort=True):
        g = group.copy()
        for w in windows:
            for col in base_roll_cols:
                if col == "llm_news_count" or col.endswith("_count"):
                    g[f"{col}_roll_{w}d"] = g[col].rolling(w, min_periods=1).sum()
                else:
                    g[f"{col}_roll_{w}d"] = g[col].rolling(w, min_periods=1).mean()
            g[f"llm_news_days_roll_{w}d"] = (g["llm_news_count"] > 0).astype(float).rolling(w, min_periods=1).sum()
        last_news_date = None
        days_since = []
        for _, row in g.iterrows():
            if row.get("llm_news_count", 0) > 0:
                last_news_date = row["date"]
                days_since.append(0.0)
            elif last_news_date is None:
                days_since.append(999.0)
            else:
                days_since.append(float((row["date"] - last_news_date).days))
        g["llm_days_since_last_news"] = days_since
        frames.append(g)
    return pd.concat(frames, ignore_index=True)


def build_panel(prices: pd.DataFrame, annotations: pd.DataFrame) -> pd.DataFrame:
    tech = build_daily_technical(prices)
    labels = build_forward_labels(prices)
    sem = aggregate_daily_semantics(annotations, prices)
    panel = tech.merge(labels, on=["ticker", "date"], how="inner").merge(sem, on=["ticker", "date"], how="left")
    for col in [c for c in panel.columns if c.startswith("llm_")]:
        panel[col] = pd.to_numeric(panel[col], errors="coerce").fillna(0.0)
    return panel.sort_values(["ticker", "date"]).reset_index(drop=True)


def time_series_date_split(df: pd.DataFrame, test_frac: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = sorted(pd.to_datetime(df["date"]).dropna().unique())
    n_test = max(1, int(len(dates) * test_frac))
    test_dates = set(dates[-n_test:])
    train = df[~df["date"].isin(test_dates)].copy()
    test = df[df["date"].isin(test_dates)].copy()
    return train, test


def feature_sets(panel: pd.DataFrame) -> dict[str, list[str]]:
    meta_prefixes = ("future_return_", "label_up_")
    excluded = {"ticker", "date", "open", "high", "low", "close", "volume"}
    candidates = [c for c in panel.columns if c not in excluded and not c.startswith(meta_prefixes)]
    llm_cols = [c for c in candidates if c.startswith("llm_")]
    tech_cols = [c for c in candidates if not c.startswith("llm_")]
    return {
        "Config_A": tech_cols,
        "Config_LLM": llm_cols,
        "Config_Hybrid": tech_cols + llm_cols,
    }


def evaluate_panel(panel: pd.DataFrame, horizons: Iterable[int], model_filter: set[str] | None = None) -> pd.DataFrame:
    configs = feature_sets(panel)
    rows: list[dict[str, Any]] = []
    for h in horizons:
        label_col = f"label_up_{h}d"
        work = panel.dropna(subset=[label_col]).copy()
        work["label_basic"] = work[label_col].astype(int)
        train_df, test_df = time_series_date_split(work)
        for config_name, cols in configs.items():
            numeric_cols = train_df[cols].select_dtypes(include=[np.number]).columns.tolist()
            usable = [c for c in numeric_cols if not train_df[c].isna().all()]
            if not usable:
                continue
            if train_df["label_basic"].nunique() < 2 or test_df["label_basic"].nunique() < 2:
                continue
            imputer, _ = fit_imputer(train_df, usable)
            X_train, y_train = prepare_features(train_df, usable, imputer=imputer)
            X_test, y_test = prepare_features(test_df, usable, imputer=imputer)
            common = [c for c in X_train.columns if c in X_test.columns]
            X_train = X_train[common]
            X_test = X_test[common]
            for model_name, model in build_ml_models(y_train).items():
                if model_filter and model_name not in model_filter:
                    continue
                model.fit(X_train, y_train)
                result = evaluate_model(model, X_test, y_test, model_name, config_name)
                result.update(
                    {
                        "horizon": f"{h}d",
                        "n_train": int(len(train_df)),
                        "n_test": int(len(test_df)),
                        "n_features": int(len(common)),
                        "train_start": str(train_df["date"].min().date()),
                        "train_end": str(train_df["date"].max().date()),
                        "test_start": str(test_df["date"].min().date()),
                        "test_end": str(test_df["date"].max().date()),
                    }
                )
                rows.append(result)
    return pd.DataFrame(rows)


def write_summary(results: pd.DataFrame, path: str = SUMMARY_PATH) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    lines = ["# LLM semantic feature experiment summary", ""]
    if results.empty:
        lines.append("No results generated.")
    else:
        pivot = results.pivot_table(index=["horizon", "model"], columns="config", values="balanced_accuracy").reset_index()
        if {"Config_A", "Config_Hybrid"}.issubset(pivot.columns):
            pivot["delta_hybrid_minus_A"] = pivot["Config_Hybrid"] - pivot["Config_A"]
        rounded = pivot.round(4)
        lines.append("```text")
        lines.append(rounded.to_string(index=False))
        lines.append("```")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def select_articles(news: pd.DataFrame, pilot: bool, max_articles: int | None, tickers: Iterable[str] | None) -> pd.DataFrame:
    work = news.copy()
    if tickers is not None:
        wanted = {t.upper() for t in tickers}
        work = work[work["ticker"].isin(wanted)].copy()
    work = work.sort_values(["date", "ticker", "title"]).reset_index(drop=True)
    if max_articles is not None and len(work) > max_articles:
        if pilot:
            # Evenly sample across time so both train and test date ranges receive
            # semantic signal; taking only latest news would make train all-zero.
            idx = np.linspace(0, len(work) - 1, max_articles).round().astype(int)
            work = work.iloc[sorted(set(idx))]
        else:
            work = work.head(max_articles)
    return work.reset_index(drop=True)


def run_experiment(args: argparse.Namespace) -> pd.DataFrame:
    live = args.live or os.environ.get("A8_LLM_SEMANTIC_LIVE", "").strip().lower() in {"1", "true", "yes", "y"}
    tickers = PILOT_TICKERS if args.pilot else None
    prices = load_prices(args.prices_path)
    if tickers is not None:
        prices = prices[prices["ticker"].isin(tickers)].copy()
    news = load_news(args.news_path, tickers=tickers)
    selected = select_articles(news, args.pilot, args.max_articles, tickers)
    annotations = annotate_articles(
        selected,
        cache_path=args.cache_path,
        prompt_packs_path=args.prompt_packs_path,
        provider=args.provider,
        model=args.model,
        max_articles=args.max_articles,
        live=live,
        max_article_chars=args.max_article_chars,
    )
    if not selected.empty and (annotations.empty or not annotations["status"].astype(str).eq("ok").any()):
        if not live:
            logger.warning("No live annotations generated; offline prompt packs only.")
            empty = pd.DataFrame()
            empty.attrs["offline_prompt_packs"] = True
            return empty
        raise RuntimeError("No successful semantic annotations generated; stop instead of evaluating all-zero LLM features.")
    panel = build_panel(prices, annotations)
    os.makedirs(os.path.dirname(args.daily_feature_path) or ".", exist_ok=True)
    semantic_cols = ["ticker", "date"] + [c for c in panel.columns if c.startswith("llm_")]
    panel[semantic_cols].to_csv(args.daily_feature_path, index=False, encoding="utf-8")
    panel.to_csv(args.panel_path, index=False, encoding="utf-8")
    horizons = [int(h) for h in args.horizons.split(",") if h.strip()]
    model_filter = None
    if args.fast_models:
        model_filter = {"Logistic_Regression", "Random_Forest"}
    results = evaluate_panel(panel, horizons, model_filter=model_filter)
    os.makedirs(os.path.dirname(args.result_path) or ".", exist_ok=True)
    results.to_csv(args.result_path, index=False, encoding="utf-8")
    write_summary(results, args.summary_path)
    return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM semantic news feature daily experiment")
    parser.add_argument("--prices-path", default=PRICES_PATH)
    parser.add_argument("--news-path", default=NEWS_PATH)
    parser.add_argument("--cache-path", default=CACHE_PATH)
    parser.add_argument("--prompt-packs-path", default=PROMPT_PACKS_PATH)
    parser.add_argument("--daily-feature-path", default=DAILY_FEATURE_PATH)
    parser.add_argument("--panel-path", default=PANEL_PATH)
    parser.add_argument("--result-path", default=RESULT_PATH)
    parser.add_argument("--summary-path", default=SUMMARY_PATH)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-articles", type=int, default=500)
    parser.add_argument("--max-article-chars", type=int, default=12000)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--horizons", default="5,20")
    parser.add_argument("--fast-models", action="store_true", help="Only run Logistic Regression and Random Forest")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    args = build_arg_parser().parse_args(argv)
    results = run_experiment(args)
    if results.empty:
        if results.attrs.get("offline_prompt_packs"):
            print(f"No experiment results generated. Saved offline prompts to {args.prompt_packs_path}")
            return 0
        print("No experiment results generated.")
        return 2
    pd.set_option("display.width", 180)
    print(results[["horizon", "model", "config", "balanced_accuracy", "auc_roc", "n_train", "n_test", "n_features"]].round(4).to_string(index=False))
    print(f"Saved results to {args.result_path}")
    print(f"Saved summary to {args.summary_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
