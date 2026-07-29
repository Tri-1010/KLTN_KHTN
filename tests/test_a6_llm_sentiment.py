"""Unit tests for A6 — LLM zero-shot sentiment annotation (``annotate_articles``).

These tests exercise :func:`experiments.a6_llm_sentiment.annotate_articles` with
a **mock** :class:`SentimentClient` — the real Gemini API is NEVER called. They
cover the behaviours required by task 13.1 / 13.4:

- **Cache reuse (Req 8.5):** an article already present in the cache (matched by
  ``content_hash``) is reused and the client is NOT invoked again for it.
- **API error handling (Req 8.8):** when a client call raises, the failing
  article is logged and skipped while the rest keep processing.
- **Cache fields (Req 8.4):** newly annotated rows persist every column of the
  cache schema, including ``content_hash``, ``model_version``, ``temperature``,
  and ``annotated_at``.
- **temperature / prompt guard (Req 8.2, 8.3):** the prompt only asks for
  content polarity and forbids price prediction; temperature is recorded as 0.

The tests use ``tmp_path`` for the cache so the committed
``data/news/annotated/llm_sentiment.csv`` is never touched.
"""

from __future__ import annotations

import pandas as pd
import pytest

from experiments.a6_llm_sentiment import (
    CACHE_COLUMNS,
    TEMPERATURE,
    VALID_SENTIMENTS,
    SentimentAnnotation,
    annotate_articles,
    build_sentiment_prompt,
    content_hash,
)


# ---------------------------------------------------------------------------
# Mock clients (NEVER call the real API)
# ---------------------------------------------------------------------------


class RecordingClient:
    """A mock client that records every call and returns a fixed annotation."""

    def __init__(self, sentiment="positive", confidence=0.9, model_version="mock-v1"):
        self.calls = []
        self._sentiment = sentiment
        self._confidence = confidence
        self._model_version = model_version

    def annotate(self, title, description):
        self.calls.append((title, description))
        return SentimentAnnotation(
            sentiment=self._sentiment,
            confidence=self._confidence,
            model_version=self._model_version,
        )


class FailingOnClient:
    """Mock client that raises for a specific title, succeeds otherwise."""

    def __init__(self, fail_title):
        self.calls = []
        self._fail_title = fail_title

    def annotate(self, title, description):
        self.calls.append((title, description))
        if title == self._fail_title:
            raise RuntimeError("simulated API failure")
        return SentimentAnnotation("neutral", 0.5, "mock-v1")


def _articles():
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "title": ["Tin tốt", "Tin xấu", "Tin trung tính"],
            "description": ["mô tả A", "mô tả B", ""],
            "ticker": ["AAA", "BBB", "CCC"],
        }
    )


# ---------------------------------------------------------------------------
# content_hash & prompt (Req 8.2, 8.4)
# ---------------------------------------------------------------------------


def test_content_hash_is_stable_and_normalized():
    """Hash is deterministic and insensitive to case / whitespace differences."""
    h1 = content_hash("Tiêu Đề", "Mô  tả")
    h2 = content_hash("  tiêu đề ", "mô tả")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex length


def test_content_hash_handles_nan_description():
    """A NaN/empty description does not raise and yields a stable hash."""
    h = content_hash("chỉ có tiêu đề", float("nan"))
    assert isinstance(h, str) and len(h) == 64


def test_prompt_forbids_price_prediction_and_requests_polarity():
    """Prompt asks only for content polarity and forbids price prediction (Req 8.2)."""
    prompt = build_sentiment_prompt("Tiêu đề", "Mô tả")
    assert "giá cổ phiếu" in prompt  # explicitly mentions price
    assert "KHÔNG" in prompt  # forbids something
    assert "positive" in prompt and "negative" in prompt and "neutral" in prompt


# ---------------------------------------------------------------------------
# Cache reuse (Req 8.5)
# ---------------------------------------------------------------------------


def test_cache_reuse_does_not_call_client_again(tmp_path):
    """Second run reuses cached rows and never re-invokes the client (Req 8.5)."""
    cache_path = str(tmp_path / "llm_sentiment.csv")
    articles = _articles()

    client1 = RecordingClient()
    first = annotate_articles(articles, cache_path=cache_path, client=client1)
    assert len(client1.calls) == 3  # all three annotated on first pass
    assert len(first) == 3

    # Second run with a fresh client: everything is cached → zero calls.
    client2 = RecordingClient()
    second = annotate_articles(articles, cache_path=cache_path, client=client2)
    assert len(client2.calls) == 0, "cached articles must not be re-annotated"
    assert len(second) == 3


def test_partial_cache_only_annotates_new_articles(tmp_path):
    """Only articles missing from the cache trigger a client call (Req 8.5)."""
    cache_path = str(tmp_path / "llm_sentiment.csv")
    articles = _articles()

    # Prime the cache with just the first article.
    annotate_articles(articles.iloc[[0]], cache_path=cache_path, client=RecordingClient())

    client = RecordingClient()
    annotate_articles(articles, cache_path=cache_path, client=client)
    # Only the two new articles are annotated.
    assert len(client.calls) == 2
    titles = {t for t, _ in client.calls}
    assert titles == {"Tin xấu", "Tin trung tính"}


# ---------------------------------------------------------------------------
# API error handling (Req 8.8)
# ---------------------------------------------------------------------------


def test_api_error_is_logged_and_processing_continues(tmp_path, caplog):
    """A failing call is logged and skipped; remaining articles still annotated."""
    cache_path = str(tmp_path / "llm_sentiment.csv")
    articles = _articles()

    client = FailingOnClient(fail_title="Tin xấu")
    with caplog.at_level("WARNING"):
        result = annotate_articles(articles, cache_path=cache_path, client=client)

    # All three attempted, one failed → two successful rows.
    assert len(client.calls) == 3
    assert len(result) == 2
    assert "Tin xấu" not in set(result["title"])

    # The failure was logged with a warning mentioning the content hash.
    failed_hash = content_hash("Tin xấu", "mô tả B")
    assert any(failed_hash in rec.message for rec in caplog.records)

    # Cache only contains the successful annotations.
    cached = pd.read_csv(cache_path, encoding="utf-8")
    assert len(cached) == 2


# ---------------------------------------------------------------------------
# Cache fields written correctly (Req 8.3, 8.4)
# ---------------------------------------------------------------------------


def test_cache_fields_written_correctly(tmp_path):
    """All cache columns persist with correct model_version / temperature (Req 8.4)."""
    cache_path = str(tmp_path / "llm_sentiment.csv")
    articles = _articles()

    client = RecordingClient(sentiment="positive", confidence=0.77, model_version="mock-v9")
    annotate_articles(articles, cache_path=cache_path, client=client)

    cached = pd.read_csv(cache_path, encoding="utf-8")
    # Exact schema and order.
    assert list(cached.columns) == CACHE_COLUMNS

    # temperature always 0 (Req 8.3), model version recorded (Req 8.4).
    assert (cached["temperature"] == TEMPERATURE).all()
    assert (cached["model_version"] == "mock-v9").all()
    assert (cached["confidence"] == 0.77).all()
    assert set(cached["sentiment"]).issubset(set(VALID_SENTIMENTS))

    # content_hash matches recomputation from the source article.
    expected = content_hash("Tin tốt", "mô tả A")
    row = cached[cached["title"] == "Tin tốt"].iloc[0]
    assert row["content_hash"] == expected
    # annotated_at is a non-empty ISO timestamp.
    assert isinstance(row["annotated_at"], str) and "T" in row["annotated_at"]


def test_lazy_client_factory_not_invoked_when_all_cached(tmp_path):
    """The default client factory is not called when nothing needs annotating."""
    cache_path = str(tmp_path / "llm_sentiment.csv")
    articles = _articles()
    annotate_articles(articles, cache_path=cache_path, client=RecordingClient())

    def exploding_factory(model):  # pragma: no cover - must never run
        raise AssertionError("factory should not be invoked when fully cached")

    # No explicit client; everything is cached → factory must never be called.
    result = annotate_articles(
        articles, cache_path=cache_path, client_factory=exploding_factory
    )
    assert len(result) == 3


def test_empty_articles_returns_empty_frame(tmp_path):
    """Empty input yields an empty, correctly-shaped frame without errors."""
    cache_path = str(tmp_path / "llm_sentiment.csv")
    result = annotate_articles(pd.DataFrame(), cache_path=cache_path, client=RecordingClient())
    assert result.empty
    assert list(result.columns) == CACHE_COLUMNS


# ---------------------------------------------------------------------------
# aggregate_llm_features & build_a6_features (Req 8.6, 8.7, 2.1)
# ---------------------------------------------------------------------------

from experiments.a6_llm_sentiment import (  # noqa: E402
    A6_OUTPUT_PATH,
    LLM_FEATURE_COLS,
    META_COLS,
    aggregate_llm_features,
    build_a6_features,
)


def _annotations():
    """Nhãn LLM mẫu: AAA có 3 bài (2 pos, 1 neg) trong 2024Q1; BBB có 2 neutral."""
    return pd.DataFrame(
        {
            "content_hash": ["h1", "h2", "h3", "h4", "h5"],
            "ticker": ["AAA", "AAA", "AAA", "BBB", "BBB"],
            "date": ["2024-01-05", "2024-02-10", "2024-03-01", "2024-04-01", "2024-05-01"],
            "title": ["t1", "t2", "t3", "t4", "t5"],
            "sentiment": ["positive", "positive", "negative", "neutral", "neutral"],
            "confidence": [0.9, 0.8, 0.7, 0.6, 0.6],
            "model_version": ["mock-v1"] * 5,
            "temperature": [0.0] * 5,
            "annotated_at": ["2024-01-01T00:00:00+00:00"] * 5,
        }
    )


def test_aggregate_grouping_and_ratio_math():
    """Gộp đúng theo (ticker, quarter_id) và tính đúng công thức tỷ lệ (Req 8.6)."""
    result = aggregate_llm_features(_annotations())

    assert list(result.columns) == META_COLS + LLM_FEATURE_COLS

    aaa = result[(result["ticker"] == "AAA") & (result["quarter_id"] == "2024Q1")].iloc[0]
    # 2 pos / 3, 1 neg / 3, net = 2/3 - 1/3
    assert aaa["llm_pos_ratio"] == pytest.approx(2 / 3)
    assert aaa["llm_neg_ratio"] == pytest.approx(1 / 3)
    assert aaa["llm_net_sentiment"] == pytest.approx(1 / 3)

    bbb = result[result["ticker"] == "BBB"].iloc[0]
    # cả hai neutral → pos=neg=0, net=0, quarter derived là 2024Q2
    assert bbb["quarter_id"] == "2024Q2"
    assert bbb["llm_pos_ratio"] == 0.0
    assert bbb["llm_neg_ratio"] == 0.0
    assert bbb["llm_net_sentiment"] == 0.0


def test_aggregate_derives_quarter_from_date():
    """quarter_id được suy ra đúng từ date theo quý lịch."""
    result = aggregate_llm_features(_annotations())
    quarters = set(result["quarter_id"])
    assert quarters == {"2024Q1", "2024Q2"}


def test_aggregate_left_join_fills_missing_keys_with_zero():
    """Left-join lên khung khóa: khóa không có nhãn được điền 0 (Req 2.1)."""
    keys = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB", "CCC"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q3"],
        }
    )
    result = aggregate_llm_features(_annotations(), news_by_quarter_keys=keys)

    # Mọi khóa trong keys đều xuất hiện.
    assert len(result) == 3
    ccc = result[result["ticker"] == "CCC"].iloc[0]
    assert ccc["llm_pos_ratio"] == 0.0
    assert ccc["llm_neg_ratio"] == 0.0
    assert ccc["llm_net_sentiment"] == 0.0


def test_aggregate_empty_returns_empty_frame():
    """Nhãn rỗng → DataFrame rỗng đúng schema."""
    result = aggregate_llm_features(pd.DataFrame())
    assert result.empty
    assert list(result.columns) == META_COLS + LLM_FEATURE_COLS


def test_build_a6_writes_mergeable_output(tmp_path):
    """build_a6_features gọi annotate + aggregate và ghi tệp keyed (Req 8.7, 2.1)."""
    processed = pd.DataFrame(
        {
            "date": ["2024-01-05", "2024-02-10", "2024-03-01"],
            "title": ["Tin tốt", "Tin tốt 2", "Tin xấu"],
            "description": ["a", "b", "c"],
            "ticker": ["AAA", "AAA", "AAA"],
        }
    )
    processed_path = tmp_path / "processed.csv"
    processed.to_csv(processed_path, index=False, encoding="utf-8")

    news_keys = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "ZZZ"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "news_count": [3, 0, 0],
            "combined_text": ["x", "", ""],
        }
    )
    news_path = tmp_path / "news_by_quarter.csv"
    news_keys.to_csv(news_path, index=False, encoding="utf-8")

    output_path = tmp_path / "keyword_features_A6.csv"
    cache_path = tmp_path / "llm_sentiment.csv"

    # Client trả positive cho mọi bài.
    features = build_a6_features(
        processed_news_path=str(processed_path),
        news_by_quarter_path=str(news_path),
        output_path=str(output_path),
        cache_path=str(cache_path),
        client=RecordingClient(sentiment="positive"),
    )

    # Tệp được ghi và có đúng khóa mergeable.
    assert output_path.is_file()
    written = pd.read_csv(output_path, encoding="utf-8")
    assert list(written.columns) == META_COLS + LLM_FEATURE_COLS

    # Mọi khóa trong news_by_quarter đều xuất hiện (left-join, Req 2.1).
    assert len(written) == 3
    aaa_q1 = written[(written["ticker"] == "AAA") & (written["quarter_id"] == "2024Q1")].iloc[0]
    assert aaa_q1["llm_pos_ratio"] == pytest.approx(1.0)
    assert aaa_q1["llm_net_sentiment"] == pytest.approx(1.0)

    # Khóa không có nhãn (AAA/2024Q2, ZZZ/2024Q1) được điền 0.
    zzz = written[written["ticker"] == "ZZZ"].iloc[0]
    assert zzz["llm_pos_ratio"] == 0.0
    assert features is not None


def test_build_a6_missing_input_returns_empty(tmp_path):
    """Thiếu tệp bài viết → trả DataFrame rỗng, không ném lỗi."""
    result = build_a6_features(
        processed_news_path=str(tmp_path / "nope.csv"),
        news_by_quarter_path=str(tmp_path / "nope2.csv"),
        output_path=str(tmp_path / "out.csv"),
        cache_path=str(tmp_path / "cache.csv"),
        client=RecordingClient(),
    )
    assert result.empty
    assert list(result.columns) == META_COLS + LLM_FEATURE_COLS


def test_a6_output_path_constant():
    """Hằng số đường dẫn đầu ra đúng quy ước version hóa (Req 2.1)."""
    assert A6_OUTPUT_PATH == "data/features/keyword_features_A6.csv"
