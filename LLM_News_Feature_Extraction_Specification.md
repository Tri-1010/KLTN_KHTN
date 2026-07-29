# LLM News Feature Extraction Specification for Stock Prediction

Version: 1.0

## Research Objective

This specification defines how a Large Language Model (LLM) should
convert Vietnamese financial news into structured semantic features that
can be used together with technical indicators in a Machine Learning
model.

**The LLM is NOT the prediction model.**

The prediction model remains LightGBM, XGBoost, CatBoost, Random Forest,
Transformer, etc.

The purpose of the LLM is to determine whether semantic information
extracted from complete news articles provides additional predictive
power beyond traditional technical indicators.

------------------------------------------------------------------------

# Overall Architecture

``` text
Financial News
      │
      ▼
Large Language Model
      │
      ▼
Structured Feature Extraction
      │
      ▼
Daily Feature Aggregation
      │
      ▼
Merge with Technical Indicators
      │
      ▼
Machine Learning Model
      │
      ▼
Prediction
```

------------------------------------------------------------------------

# Research Hypothesis

H0: Technical indicators alone are sufficient.

H1: Semantic features extracted from financial news by LLM improve
predictive performance.

------------------------------------------------------------------------

# Design Principles

The LLM should:

-   Read the entire article.
-   Understand semantic meaning rather than keywords.
-   Produce structured outputs.
-   Avoid hallucination.
-   Never predict stock prices.

The LLM must NOT output:

-   Buy
-   Sell
-   Hold
-   Target price
-   Future EPS
-   Future revenue
-   Any unsupported assumption

------------------------------------------------------------------------

# Output Schema (JSON)

``` json
{
  "ticker": "HPG",
  "company_name": "Hoa Phat Group",
  "article_date": "2026-07-07",

  "is_stock_relevant": true,

  "sentiment": "positive",

  "importance_score": 4,

  "expected_impact_score": 3,

  "uncertainty_score": 2,

  "novelty_score": 4,

  "time_horizon": "short_term",

  "reasoning_confidence": 4,

  "summary": "Quarterly earnings exceeded market expectations.",

  "reason": "The article reports stronger operating results than previous quarters."
}
```

------------------------------------------------------------------------

# Field Specification

## ticker

Stock ticker directly affected.

Rules:

-   Never guess.
-   Return null if not identifiable.

------------------------------------------------------------------------

## company_name

Official company name.

------------------------------------------------------------------------

## article_date

Publication date.

------------------------------------------------------------------------

## is_stock_relevant

Whether the article directly concerns a listed company.

Allowed values

-   true
-   false

------------------------------------------------------------------------

## sentiment

Overall semantic polarity of the article.

Allowed values

-   positive
-   neutral
-   negative
-   mixed

Notes

This is NOT a stock recommendation.

It only describes the semantic tone.

------------------------------------------------------------------------

## importance_score

Scale

1--5

Meaning

1 = Minor information

2 = Low importance

3 = Medium

4 = High

5 = Extremely important

Evaluate according to business significance rather than article length.

------------------------------------------------------------------------

## expected_impact_score

Scale

1--5

Question:

"If investors believe this information, how large could the market
reaction reasonably be?"

This measures magnitude only.

Not direction.

------------------------------------------------------------------------

## uncertainty_score

Scale

1--5

1 = Highly certain

5 = Highly uncertain

Examples

Audited financial statement

→ 1

Rumor

→ 5

Management considering investment

→ 4

------------------------------------------------------------------------

## novelty_score

Scale

1--5

Measure whether the information is genuinely new.

1 = Widely repeated

5 = Completely new

Purpose

Reduce duplicated-news bias.

------------------------------------------------------------------------

## time_horizon

Allowed values

-   short_term
-   medium_term
-   long_term

Meaning

Expected duration of information usefulness.

------------------------------------------------------------------------

## reasoning_confidence

Scale

1--5

Confidence of the LLM regarding all extracted information.

------------------------------------------------------------------------

## summary

Maximum 30 words.

Objective summary.

No prediction.

------------------------------------------------------------------------

## reason

Maximum 50 words.

Explain why previous scores were assigned.

Only use evidence from the article.

------------------------------------------------------------------------

# Feature Engineering

After article-level extraction, aggregate by (ticker, trading_date).

Recommended features

Numeric

-   has_news
-   news_count
-   positive_ratio
-   negative_ratio
-   avg_importance_score
-   max_importance_score
-   avg_expected_impact_score
-   max_expected_impact_score
-   avg_uncertainty_score
-   avg_novelty_score
-   avg_reasoning_confidence

Categorical

-   dominant_sentiment
-   time_horizon

Temporal

-   days_since_last_news
-   rolling_news_count_3d
-   rolling_news_count_5d
-   rolling_importance_3d
-   rolling_importance_5d
-   impact_decay_3d
-   impact_decay_5d

------------------------------------------------------------------------

# Merge With Technical Indicators

Combine the above with

-   OHLCV
-   RSI
-   MACD
-   Moving Averages
-   Bollinger Bands
-   ATR
-   ADX
-   OBV
-   Volume
-   Momentum indicators

------------------------------------------------------------------------

# Recommended Experiments

Model A

Technical Indicators Only

Model B

Technical + News Availability

Model C

Technical + TF-IDF / Keyword Features

Model D

Technical + News Embeddings

Model E

Technical + LLM Semantic Features

Model F

Technical + LLM Features + Temporal Aggregation

------------------------------------------------------------------------

# Evaluation

Compare

-   Accuracy
-   Precision
-   Recall
-   F1-score
-   ROC-AUC (classification)
-   MAE / RMSE (regression)
-   Financial metrics if applicable

Perform ablation study to quantify the contribution of LLM-derived
features.

------------------------------------------------------------------------

# Future Extensions

This specification intentionally focuses on semantic feature extraction
only.

Potential future work:

-   Event ontology
-   Event clustering
-   Knowledge graph
-   Multi-article reasoning
-   LLM-based event database
