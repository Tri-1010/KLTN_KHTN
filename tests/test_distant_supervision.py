"""Unit tests for B1 Distant_Supervision_Module (Req 11).

Example/edge tests complementing the property-based tests in
``tests/test_distant_supervision_pbt.py``. These verify concrete behaviour of:

- ``build_noisy_labels`` return convention (base = close at/before d, end = close
  of last clipped trading day) and exclusion of articles without price / window
  (Req 11.1–11.5).
- ``train_article_classifier`` filtering to pre-cutoff articles and its degenerate
  guard (Req 11.6).
- ``aggregate_ds_features`` formulas and NaN for periods with no articles
  (Req 11.7).
- ``build_b1_features`` end-to-end on a tiny fixture writing the versioned feature
  CSV and the distant supervision report (Req 11.8, 2.1).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from experiments.b1_distant_supervision import (
    DS_FEATURE_COLS,
    aggregate_ds_features,
    build_b1_features,
    build_noisy_labels,
    classify_return,
    compute_clipped_return,
    train_article_classifier,
)


def _price_frame(dates, closes):
    return pd.DataFrame({"date": pd.to_datetime(dates), "close": closes})


# ---------------------------------------------------------------------------
# classify_return
# ---------------------------------------------------------------------------


def test_classify_return_examples():
    assert classify_return(0.03) == "positive"
    assert classify_return(0.02) == "positive"  # inclusive
    assert classify_return(-0.02) == "negative"  # inclusive
    assert classify_return(-0.05) == "negative"
    assert classify_return(0.0) == "neutral"
    assert classify_return(0.01) == "neutral"


# ---------------------------------------------------------------------------
# compute_clipped_return: base/end convention
# ---------------------------------------------------------------------------


def test_compute_clipped_return_base_and_end():
    # Trading days in 2023Q1.
    prices = _price_frame(
        ["2023-02-01", "2023-02-02", "2023-02-03", "2023-02-06"],
        [100.0, 102.0, 104.0, 110.0],
    )
    # Article posted on a trading day 2023-02-01 (base close = 100).
    # Window [d+1, d+3] trading days -> 02-02, 02-03, 02-06; end close = 110.
    ret = compute_clipped_return(prices, "2023-02-01", "2023Q1")
    assert ret == (110.0 - 100.0) / 100.0


def test_compute_clipped_return_clips_at_quarter_end():
    # Posting date near quarter end; only one trading day left inside the quarter.
    prices = _price_frame(
        ["2023-03-30", "2023-03-31", "2023-04-03", "2023-04-04"],
        [100.0, 105.0, 200.0, 300.0],
    )
    # d = 2023-03-30 (base=100). Quarter 2023Q1 ends 2023-03-31, so only 03-31
    # counts. The April prices must NOT be used (clipped).
    ret = compute_clipped_return(prices, "2023-03-30", "2023Q1")
    assert ret == (105.0 - 100.0) / 100.0


def test_compute_clipped_return_none_when_no_window():
    # d is the last trading day of the quarter -> no d+1..d+3 inside quarter.
    prices = _price_frame(
        ["2023-03-31", "2023-04-03"],
        [100.0, 500.0],
    )
    assert compute_clipped_return(prices, "2023-03-31", "2023Q1") is None


# ---------------------------------------------------------------------------
# build_noisy_labels
# ---------------------------------------------------------------------------


def test_build_noisy_labels_basic_and_exclusion():
    prices = {
        "AAA": _price_frame(
            ["2023-02-01", "2023-02-02", "2023-02-03"],
            [100.0, 100.0, 103.0],  # +3% -> positive
        )
    }
    articles = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],  # BBB has no price data -> excluded
            "date": ["2023-02-01", "2023-02-01"],
            "text_tokenized": ["tin tot", "tin xau"],
        }
    )
    labeled = build_noisy_labels(articles, prices)
    assert len(labeled) == 1
    row = labeled.iloc[0]
    assert row["ticker"] == "AAA"
    assert row["quarter_id"] == "2023Q1"
    assert row["noisy_label"] == "positive"


def test_build_noisy_labels_accepts_long_dataframe():
    long_prices = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "AAA"],
            "date": ["2023-02-01", "2023-02-02", "2023-02-03"],
            "close": [100.0, 100.0, 96.0],  # -4% -> negative
        }
    )
    articles = pd.DataFrame(
        {"ticker": ["AAA"], "date": ["2023-02-01"], "text_tokenized": ["x"]}
    )
    labeled = build_noisy_labels(articles, long_prices)
    assert len(labeled) == 1
    assert labeled.iloc[0]["noisy_label"] == "negative"


# ---------------------------------------------------------------------------
# train_article_classifier
# ---------------------------------------------------------------------------


def _labeled_fixture():
    return pd.DataFrame(
        {
            "ticker": ["T"] * 6,
            "quarter_id": ["2024Q1", "2024Q2", "2024Q3", "2025Q1", "2025Q2", "2025Q3"],
            "text_tokenized": [
                "loi nhuan tang truong tot",
                "co tuc cao lai rong",
                "thua lo no xau giam manh",
                "future article one",
                "future article two",
                "future article three",
            ],
            "noisy_label": [
                "positive",
                "positive",
                "negative",
                "neutral",
                "neutral",
                "neutral",
            ],
        }
    )


def test_train_article_classifier_uses_only_pre_cutoff():
    labeled = _labeled_fixture()
    clf = train_article_classifier(labeled, cutoff="2025Q1")
    # Only 3 pre-cutoff articles with 2 classes (positive/negative) were used.
    classes = set(clf.named_steps["clf"].classes_)
    assert classes == {"positive", "negative"}


def test_train_article_classifier_degenerate_raises():
    labeled = pd.DataFrame(
        {
            "ticker": ["T", "T"],
            "quarter_id": ["2024Q1", "2024Q2"],
            "text_tokenized": ["a b", "c d"],
            "noisy_label": ["neutral", "neutral"],  # single class
        }
    )
    try:
        train_article_classifier(labeled, cutoff="2025Q1")
    except ValueError:
        pass
    else:  # pragma: no cover
        assert False, "expected ValueError for single-class training set"


# ---------------------------------------------------------------------------
# aggregate_ds_features
# ---------------------------------------------------------------------------


def test_aggregate_ds_features_formula():
    probs = pd.DataFrame(
        {
            "ticker": ["T", "T", "T"],
            "quarter_id": ["2024Q1", "2024Q1", "2024Q2"],
            "pos_prob": [0.8, 0.4, 0.2],
            "neg_prob": [0.1, 0.1, 0.7],
        }
    )
    agg = aggregate_ds_features(probs)
    q1 = agg[agg["quarter_id"] == "2024Q1"].iloc[0]
    assert q1["ds_pos_prob_mean"] == (0.8 + 0.4) / 2
    assert q1["ds_net_sentiment"] == ((0.8 + 0.4) / 2) - ((0.1 + 0.1) / 2)


def test_aggregate_ds_features_nan_for_empty_periods():
    probs = pd.DataFrame(
        {
            "ticker": ["T"],
            "quarter_id": ["2024Q1"],
            "pos_prob": [0.5],
            "neg_prob": [0.2],
        }
    )
    keys = pd.DataFrame(
        {"ticker": ["T", "T"], "quarter_id": ["2024Q1", "2024Q2"]}
    )
    agg = aggregate_ds_features(probs, news_by_quarter_keys=keys)
    q2 = agg[agg["quarter_id"] == "2024Q2"].iloc[0]
    assert np.isnan(q2["ds_pos_prob_mean"])
    assert np.isnan(q2["ds_net_sentiment"])


# ---------------------------------------------------------------------------
# build_b1_features end-to-end on tiny fixture
# ---------------------------------------------------------------------------


def test_build_b1_features_end_to_end(tmp_path):
    prices_dir = tmp_path / "prices"
    prices_dir.mkdir()

    # Two tickers, price series across pre-cutoff quarters + one post-cutoff.
    for tk, trend in [("AAA", 1.0), ("BBB", -1.0)]:
        dates = pd.bdate_range("2024-01-02", periods=40)
        closes = 100.0 + trend * np.arange(len(dates))
        _price_frame(dates, closes).to_csv(prices_dir / f"{tk}.csv", index=False)

    articles = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB", "BBB"],
            "date": ["2024-01-02", "2024-02-01", "2024-01-02", "2024-02-01"],
            "text_tokenized": [
                "loi nhuan tang truong",
                "co tuc cao ky luc",
                "thua lo no xau",
                "giam manh rui ro",
            ],
        }
    )
    news_path = tmp_path / "news.csv"
    articles.to_csv(news_path, index=False)

    nbq = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q1"],
        }
    )
    nbq_path = tmp_path / "nbq.csv"
    nbq.to_csv(nbq_path, index=False)

    out_path = tmp_path / "keyword_features_B1.csv"
    report_path = tmp_path / "distant_supervision_report.md"

    features = build_b1_features(
        processed_news_path=str(news_path),
        news_by_quarter_path=str(nbq_path),
        prices_dir=str(prices_dir),
        output_path=str(out_path),
        cutoff="2025Q1",
        report_path=str(report_path),
    )

    assert out_path.exists()
    assert report_path.exists()
    assert set(DS_FEATURE_COLS).issubset(features.columns)
    assert {"ticker", "quarter_id"}.issubset(features.columns)
    # Keys mergeable with news_by_quarter.
    assert len(features) == 2
