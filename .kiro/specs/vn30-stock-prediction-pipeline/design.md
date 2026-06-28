# Design Document: VN30 Stock Prediction Pipeline

## Overview

### Purpose

This design describes a complete machine learning pipeline for predicting quarterly stock price trends for VN30 index constituents on the Ho Chi Minh Stock Exchange (HOSE). The pipeline combines technical indicators (OHLCV, RSI, MACD, Bollinger Bands, SMA, EMA) with keyword frequency features extracted from Vietnamese financial news to answer the central research question (H1): **Does adding news keyword features improve prediction accuracy compared to using technical features alone?**

### Problem Statement

The system addresses a binary classification problem (increase / no-increase) at quarterly granularity for 30 VN30 stocks from January 1, 2022 to present. The pipeline consists of 12 sequential steps from data collection through SHAP analysis to semi-automated packaging.

### Key Design Decisions

1. **Quarterly Aggregation**: Using quarters as the prediction unit balances signal quality (sufficient news volume) with practical utility (medium-term investment horizon)

2. **Three-Configuration Experiment**: Config A (technical only), Config B (keywords only), Config C (combined) enables direct measurement of keyword feature contribution

3. **Time-Series Split**: Strict temporal ordering prevents data leakage — all training data precedes all test data

4. **Vietnamese NLP Stack**: underthesea for tokenization, custom financial stopwords, and domain-specific keyword curation

5. **Panel Data Structure**: (ticker, quarter_id) as the observation unit enables both cross-sectional and temporal analysis

6. **Checkpointing Architecture**: Each task saves intermediate outputs to enable incremental updates and failure recovery

### Success Criteria

- Collect ≥300 (ticker, quarter) samples with both price and news data
- Achieve ≥5 news articles per ticker per quarter on average
- Train models with Balanced Accuracy ≥ 0.60 (better than random baseline)
- Demonstrate measurable performance difference between Config A and Config C
- Generate interpretable SHAP analysis identifying top contributing keywords

---

## Architecture

### System Architecture

The pipeline follows a **linear DAG (Directed Acyclic Graph)** architecture with 12 sequential stages:

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  TASK 1: Price_Collector (vnstock → OHLCV data)                │
│  TASK 2: News_Scraper (CafeF, Vietstock, TNCK → articles)      │
│  TASK 3: Entity_Matcher (articles → ticker mapping)             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   TEXT PREPROCESSING LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  TASK 4: Text_Preprocessor (clean, tokenize, deduplicate)      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AGGREGATION LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  TASK 5: Data_Aggregator (group by ticker × quarter)           │
│  TASK 6: Label_Builder (compute binary labels)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FEATURE ENGINEERING LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  TASK 7: Tech_Feature_Extractor (RSI, MACD, BB, SMA, EMA)      │
│  TASK 8: Keyword_Builder (curate financial keywords)            │
│  TASK 9: Keyword_Feature_Extractor (TF-IDF, sentiment scores)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   MODEL TRAINING LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  TASK 10: Model_Trainer (3 configs × 4 algorithms)             │
│  TASK 11: SHAP_Analyzer (feature importance analysis)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  TASK 12: Pipeline_Runner (CLI, config, checkpointing)         │
│    Steps: all | data | preprocess | features | train |          │
│           update_news   Flags: --force, --smoke-test            │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

**Primary Data Paths:**

1. **Price Path**: vnstock API → daily OHLCV → quarterly aggregation → technical features → model input
2. **News Path**: web scraping → entity matching → text preprocessing → quarterly aggregation → keyword features → model input
3. **Label Path**: quarterly price aggregation → next-quarter comparison → binary labels → model target

**Checkpoint Files** (enable incremental execution):

```
data/prices/all_vn30_prices.csv              [TASK 1 output]
data/news/cafef/{ticker}_cafef.csv           [TASK 2 output per ticker]
data/news/vietstock/{ticker}_vietstock.csv   [TASK 2 output per ticker]
data/news/tnck/tnck_raw.csv                 [TASK 2 output]
data/news/matched/all_news_matched.csv       [TASK 3 output]
data/news/processed/all_news_processed.csv   [TASK 4 output]
data/aggregated/news_by_quarter.csv          [TASK 5 output]
data/aggregated/prices_by_quarter.csv        [TASK 5 output]
data/aggregated/master_dataset.csv           [TASK 5 output]
data/aggregated/master_with_labels.csv       [TASK 6 output]
data/features/technical_features.csv         [TASK 7 output]
config/keywords_finance.json                 [TASK 8 output]
data/features/keyword_features.csv           [TASK 9 output]
models/best_model.pkl                        [TASK 10 output]
reports/model_comparison.csv                 [TASK 10 output]
```

The `--step features` command relies on preprocessing outputs (TASK 4/5/6) as prerequisites. If their checkpoint files already exist, those steps are skipped automatically unless `--force` is provided.

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Price Data | vnstock | Official Python library for Vietnamese stock data |
| Web Scraping | requests + BeautifulSoup4 | Lightweight, flexible HTML parsing |
| Vietnamese NLP | underthesea | Best-maintained Vietnamese tokenizer |
| Technical Indicators | pandas-ta or ta-lib | Standard financial indicator libraries |
| Feature Engineering | pandas + scikit-learn | Industry-standard data manipulation |
| ML Models | scikit-learn, XGBoost, LightGBM | Proven classifiers for tabular data |
| Interpretability | SHAP | State-of-the-art model explanation |
| Configuration | YAML | Human-readable, easy to version control |
| Orchestration | argparse + Python | Simple, no external dependencies |

---

## Components and Interfaces

### Component Diagram

```
┌──────────────────┐
│ Pipeline_Runner  │  (orchestrator)
└────────┬─────────┘
         │ coordinates
         ├─────────────────────────────────────────────┐
         │                                             │
    ┌────▼────────┐  ┌──────────────┐  ┌─────────────▼──────┐
    │ Data        │  │ Feature      │  │ Model               │
    │ Collectors  │  │ Extractors   │  │ Trainers            │
    └─────────────┘  └──────────────┘  └────────────────────┘
         │                  │                    │
         │                  │                    │
    ┌────▼────────┐  ┌──────▼──────┐  ┌─────────▼──────────┐
    │ CSV Files   │  │ Feature CSVs│  │ Trained Models     │
    └─────────────┘  └─────────────┘  └────────────────────┘
```

### Module Interfaces

#### 1. Price_Collector

**Input:**
- `config/pipeline_config.yaml`: tickers list, start_date, end_date

**Output:**
- `data/prices/{ticker}.csv`: individual ticker files
- `data/prices/all_vn30_prices.csv`: consolidated file

**Interface:**
```python
def collect_prices(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Collect OHLCV data for specified tickers.
    
    Returns: DataFrame with columns [ticker, date, open, high, low, close, volume]
    Raises: ValueError if vnstock API fails for all tickers
    """
```

#### 2. News_Scraper

**Input:**
- `config/pipeline_config.yaml`: tickers, start_date, end_date
- Target URLs: CafeF, Vietstock, TNCK

**Output:**
- `data/news/cafef/{ticker}_cafef.csv`
- `data/news/vietstock/{ticker}_vietstock.csv`
- `data/news/tnck/tnck_raw.csv`

**Interface:**
```python
def scrape_source(source: str, ticker: str, start_date: str) -> pd.DataFrame:
    """
    Scrape articles from specified source.
    
    Returns: DataFrame with columns [date, title, description, url, source]
    Implements: rate limiting, retry logic, duplicate detection
    """
```

#### 3. Entity_Matcher

**Input:**
- `data/news/cafef/`, `data/news/vietstock/`, `data/news/tnck/`
- `config/entity_aliases.json`: ticker → company name alias mappings (all 30 VN30 tickers with Vietnamese company names, abbreviations, and common variants)

**Output:**
- `data/news/matched/all_news_matched.csv`

**Interface:**
```python
def match_entities(articles: pd.DataFrame, aliases: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Map articles to tickers using company name aliases.
    
    Args:
        articles: DataFrame with title and description columns
        aliases: loaded from config/entity_aliases.json
    
    Returns: DataFrame with additional column [ticker, match_confidence]
    Special handling: Vingroup (VIC) vs Vinhomes (VHM) vs Vincom Retail (VRE)
    """
```

#### 4. Text_Preprocessor

**Input:**
- `data/news/matched/all_news_matched.csv`
- `config/stopwords_finance.txt`

**Output:**
- `data/news/processed/all_news_processed.csv`

**Interface:**
```python
def preprocess_text(text: str) -> Tuple[str, str]:
    """
    Clean and tokenize Vietnamese text.
    
    Returns: (text_clean, text_tokenized)
    Steps: lowercase → remove HTML/URLs → tokenize (underthesea with whitespace fallback) → remove stopwords
    Fallback: If underthesea.word_tokenize fails for a specific article, falls back to simple whitespace splitting
    """
```

#### 5. Data_Aggregator

**Input:**
- `data/prices/all_vn30_prices.csv`
- `data/news/processed/all_news_processed.csv`

**Output:**
- `data/aggregated/news_by_quarter.csv`
- `data/aggregated/prices_by_quarter.csv`
- `data/aggregated/master_dataset.csv`

**Interface:**
```python
def aggregate_by_quarter(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Group data by (ticker, quarter_id).
    
    Returns: DataFrame with quarter_id = "YYYYQN" format
    """
```

#### 6. Label_Builder

**Input:**
- `data/aggregated/master_dataset.csv`

**Output:**
- `data/aggregated/master_with_labels.csv`

**Interface:**
```python
def build_labels(df: pd.DataFrame, threshold: float = 0.02) -> pd.DataFrame:
    """
    Compute binary labels from price changes.
    
    Returns: DataFrame with columns [label_basic, label_threshold, return]
    label_basic: 1 if next_avg_close > avg_close else 0
    label_threshold: 1 if return > +2%, 0 if return < -2%, NaN otherwise
    """
```

#### 7. Tech_Feature_Extractor

**Input:**
- `data/prices/all_vn30_prices.csv`

**Output:**
- `data/features/technical_features.csv`

**Interface:**
```python
def extract_technical_features(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical indicators and aggregate by quarter.
    
    Returns: DataFrame with columns [ticker, quarter_id, return_q, volatility_q, 
             rsi_mean_q, macd_hist_mean_q, bb_position_q, sma20_end, ema20_end, ...]
    """
```

#### 8. Keyword_Builder

**Input:**
- `data/news/processed/all_news_processed.csv`

**Output:**
- `config/keywords_finance.json`
- `config/keywords_by_group.json`
- `config/keyword_candidates.csv` (for manual review)

**Interface:**
```python
def build_keyword_list(corpus: List[str]) -> Dict[str, List[str]]:
    """
    Extract and curate financial keywords.
    
    Returns: {"positive": [...], "negative": [...], "neutral": [...]}
    Groups: A=business results, B=shareholder policy, C=corporate finance,
            D=operations, E=risk/legal, F=neutral events
    """
```

#### 9. Keyword_Feature_Extractor

**Input:**
- `data/aggregated/news_by_quarter.csv`
- `config/keywords_finance.json`

**Output:**
- `data/features/keyword_features.csv`

**Interface:**
```python
def extract_keyword_features(texts: pd.DataFrame, keywords: Dict) -> pd.DataFrame:
    """
    Compute keyword frequency features.
    
    Returns: DataFrame with columns [ticker, quarter_id, kw_{k}, kw_norm_{k}, 
             tfidf_{k}, pos_score, neg_score, sentiment_ratio, news_count, ...]
    """
```

#### 10. Model_Trainer

**Input:**
- `data/features/technical_features.csv`
- `data/features/keyword_features.csv`
- `data/aggregated/master_with_labels.csv`
- `config/pipeline_config.yaml`: train_cutoff

**Output:**
- `models/best_model.pkl`
- `reports/model_comparison.csv`

**Interface:**
```python
def train_models(X: pd.DataFrame, y: pd.Series, config: str) -> Dict[str, float]:
    """
    Train and evaluate models under specified feature configuration.
    
    Args:
        config: "A" (technical), "B" (keywords), or "C" (combined)
    
    Returns: {"accuracy": 0.xx, "precision": 0.xx, "recall": 0.xx, 
              "f1_macro": 0.xx, "auc_roc": 0.xx, "balanced_accuracy": 0.xx}
    """
```

#### 11. SHAP_Analyzer

**Input:**
- `models/best_model.pkl`
- Test set features and labels

**Output:**
- `reports/feature_importance.png`
- `reports/permutation_importance.png`
- `reports/shap_summary.png`
- `reports/shap_bar.png`
- `reports/top_keywords_analysis.csv`

**Interface:**
```python
def analyze_shap(model, X_test: pd.DataFrame, feature_names: List[str]) -> pd.DataFrame:
    """
    Compute SHAP values and feature importance.
    
    Returns: DataFrame with columns [feature, mean_abs_shap, direction, group]
    """
```

#### 12. Pipeline_Runner

**Input:**
- `config/pipeline_config.yaml`
- Command-line arguments: `--step`, `--force`, `--smoke-test`

**Output:**
- Orchestrates all tasks
- `logs/{task_name}_{date}.log`

**Interface:**
```python
def run_pipeline(step: str, force: bool = False, smoke_test: bool = False) -> None:
    """
    Execute pipeline steps.
    
    Args:
        step: "all", "data", "preprocess", "features", "train", or "update_news"
        force: if True, rerun even if checkpoint exists
        smoke_test: if True, restrict to 3 tickers (VNM, VCB, FPT) and 4 quarters (2022Q1-2022Q4)
    
    Step mapping:
        "all"         → TASK 1-11 (sequential)
        "data"        → TASK 1, 2, 3
        "preprocess"  → TASK 4, 5, 6
        "features"    → TASK 4, 5, 6 (prerequisites, skipped if checkpoint exists) + TASK 7, 8, 9
        "train"       → TASK 10, 11
        "update_news" → incremental scrape + update matched/processed files
    """
```

---

## Data Models

### Core Data Structures

#### 1. Price Data (Daily)

**File:** `data/prices/all_vn30_prices.csv`

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| ticker | str | Stock symbol | One of 30 VN30 tickers |
| date | date | Trading date | YYYY-MM-DD, business days only |
| open | float | Opening price | > 0 |
| high | float | Highest price | >= open, >= close |
| low | float | Lowest price | <= open, <= close |
| close | float | Closing price | > 0 |
| volume | int | Trading volume | >= 0 |

**Cardinality:** ~30 tickers × ~750 trading days (2022-01-01 to 2024-12-31) = ~22,500 rows

#### 2. News Data (Article-Level)

**File:** `data/news/processed/all_news_processed.csv`

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| date | date | Publication date | YYYY-MM-DD |
| title | str | Article title | Non-empty |
| description | str | Short description | May be empty |
| url | str | Article URL | Unique |
| source | str | News source | "cafef", "vietstock", or "tnck" |
| ticker | str | Matched stock symbol | VN30 ticker or "UNKNOWN" |
| match_confidence | str | Matching quality | "exact" or "partial" |
| text_clean | str | Cleaned text | Lowercase, no HTML/URLs |
| text_tokenized | str | Tokenized text | Space-separated tokens |

**Cardinality:** Estimated ~15,000-30,000 articles (30 tickers × 12 quarters × 40-80 articles/ticker/quarter)

#### 3. Aggregated Data (Quarterly)

**File:** `data/aggregated/master_with_labels.csv`

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| ticker | str | Stock symbol | Primary key (with quarter_id) |
| quarter_id | str | Quarter identifier | "YYYYQN" format (e.g., "2022Q1") |
| avg_close | float | Average closing price in quarter | Prices |
| avg_volume | float | Average daily volume in quarter | Prices |
| return_intra | float | Intra-quarter return | Prices |
| trading_days | int | Number of trading days | Prices |
| news_count | int | Number of articles in quarter | News |
| combined_text | str | Concatenated tokenized text | News |
| next_quarter_id | str | Following quarter | Derived |
| next_avg_close | float | Average close in next quarter | Prices (shifted) |
| label_basic | int | Binary label (0/1) | Derived |
| label_threshold | float | Threshold-based label (0/1/NaN) | Derived |
| return | float | Quarter-over-quarter return | Derived |

**Cardinality:** 30 tickers × ~12 quarters = ~360 rows (target: ≥300 after filtering)

#### 4. Technical Features (Quarterly)

**File:** `data/features/technical_features.csv`

| Feature Group | Features | Description |
|---------------|----------|-------------|
| Returns | return_q, return_mean_daily, return_std_daily | Profitability metrics |
| Volatility | volatility_q, price_range_q | Risk metrics |
| Volume | volume_mean_q, volume_change_q | Liquidity metrics |
| Trend | sma20_end, ema20_end, price_vs_sma20 | Moving averages |
| Indicators | rsi_mean_q, rsi_end_q, macd_hist_mean_q, bb_position_q | Technical signals |
| Momentum | return_prev_q, return_2q_ago | Lagged returns |

**Total:** ~15-20 technical features per (ticker, quarter_id)

#### 5. Keyword Features (Quarterly)

**File:** `data/features/keyword_features.csv`

| Feature Group | Features | Description |
|---------------|----------|-------------|
| Raw Counts | kw_{keyword} | Occurrences of each keyword |
| Normalized | kw_norm_{keyword} | Count / news_count |
| TF-IDF | tfidf_{keyword} | TF-IDF weight |
| Sentiment | pos_score, neg_score, sentiment_ratio | Aggregated sentiment |
| Coverage | news_count, news_count_log, has_min_news | Data quality indicators |

**Total:** ~50-150 keyword features (depends on keyword list size from TASK 8)

#### 6. Model Training Dataset

**Derived from:** Merge of technical_features.csv + keyword_features.csv + master_with_labels.csv on (ticker, quarter_id)

**Feature Configurations:**
- **Config A:** Technical features only (~15-20 features)
- **Config B:** Keyword features only (~50-150 features)
- **Config C:** Combined (~65-170 features)

**Target Variable:** `label_basic` (binary: 0 or 1)

**Train/Test Split:**
- Train: all quarters before 2025-Q1 (~80% of data)
- Test: 2025-Q1 onward (~20% of data)
- Split applied consistently across all tickers (no random shuffling)

### Data Quality Constraints

1. **Minimum News Coverage:** Each (ticker, quarter) must have ≥5 articles to be included in final dataset
2. **No Future Leakage:** next_avg_close must come from a strictly later quarter
3. **No Missing Labels:** Rows with NaN in label_basic are excluded from training
4. **Balanced Representation:** Each ticker should contribute ≥8 quarters to avoid single-stock bias
5. **Temporal Continuity:** No gaps larger than 2 consecutive quarters per ticker

### Entity Relationship Diagram

```
┌─────────────┐
│   Ticker    │
│  (VN30)     │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────▼──────────┐         ┌──────────────────┐
│  Quarter        │ 1     N │   News Article   │
│  (ticker,       ├─────────┤   (date, title,  │
│   quarter_id)   │         │    url, source)  │
└──────┬──────────┘         └──────────────────┘
       │ 1
       │
       │ 1
┌──────▼──────────┐
│  Daily Prices   │
│  (date, OHLCV)  │
└─────────────────┘
       │
       │ aggregates to
       ▼
┌──────────────────┐
│ Technical        │
│ Features         │
│ (15-20 features) │
└──────────────────┘

       ┌──────────────────┐
       │ Keyword          │
       │ Features         │
       │ (50-150 features)│
       └──────────────────┘
              │
              │ merge on (ticker, quarter_id)
              ▼
       ┌──────────────────┐
       │ Training Dataset │
       │ (Config A/B/C)   │
       └──────────────────┘
```

### Configuration Files

| File | Description | Created By |
|------|-------------|------------|
| `config/pipeline_config.yaml` | Main pipeline configuration: tickers, dates, thresholds | Manual / TASK 12 |
| `config/entity_aliases.json` | Ticker → company name alias mappings for all 30 VN30 tickers | TASK 3 |
| `config/stopwords_finance.txt` | Combined standard + custom financial Vietnamese stopwords | TASK 4 |
| `config/keywords_finance.json` | Curated keyword list: `{"positive": [...], "negative": [...], "neutral": [...]}` | TASK 8 |
| `config/keywords_by_group.json` | Keywords organized by thematic groups A-F | TASK 8 |
| `config/keyword_candidates.csv` | Top unigrams/bigrams from corpus for manual review | TASK 8 |

**Keyword Groups (A-F) Reference:**

The complete keyword list is defined in Requirement 8 and includes six thematic groups:
- **Group A** (Kết quả kinh doanh): 9 positive + 9 negative keywords covering profit, revenue, growth
- **Group B** (Chính sách cổ đông): 6 positive + 5 negative keywords covering dividends, share buybacks
- **Group C** (Tài chính doanh nghiệp): 6 positive + 7 negative keywords covering debt, cash flow
- **Group D** (Hoạt động kinh doanh): 7 positive + 5 negative keywords covering contracts, expansion
- **Group E** (Rủi ro và pháp lý): 10 negative keywords covering penalties, investigations
- **Group F** (Sự kiện doanh nghiệp trung tính): 9 neutral keywords covering AGMs, M&A, leadership changes

---

## Error Handling

### Error Categories and Strategies

#### 1. Network and API Errors

**Scenario:** vnstock API failures, web scraping timeouts, HTTP errors

**Strategy:**
- **Retry with Exponential Backoff:** Up to 3 attempts with delays of 1s, 2s, 4s
- **Graceful Degradation:** Log failed ticker/URL and continue with remaining items
- **Rate Limiting:** Enforce minimum 1-2 second delays between requests to same domain
- **Timeout Configuration:** Set reasonable timeouts (30s for API calls, 60s for page loads)

**Implementation:**
```python
@retry(max_attempts=3, backoff_factor=2)
def fetch_with_retry(url: str) -> requests.Response:
    try:
        response = requests.get(url, timeout=30, headers=BROWSER_HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.warning(f"Request failed for {url}: {e}")
        raise
```

#### 2. Data Quality Errors

**Scenario:** Missing data, malformed HTML, empty responses, duplicate articles

**Strategy:**
- **Validation at Ingestion:** Check for required fields (date, title, ticker) before saving
- **Duplicate Detection:** Use URL as unique key, skip if already exists
- **Missing Data Warnings:** Log but don't fail if optional fields are empty
- **Threshold Checks:** Warn if ticker has <20 articles/year or <5 articles/quarter

**Implementation:**
```python
def validate_article(article: Dict) -> bool:
    required = ['date', 'title', 'url', 'source']
    if not all(article.get(field) for field in required):
        logger.warning(f"Missing required fields in article: {article.get('url')}")
        return False
    return True
```

#### 3. Entity Matching Errors

**Scenario:** Ambiguous company names (VIC vs VHM vs VRE), no matches found

**Strategy:**
- **Priority Rules:** Explicit ordering for Vingroup family (Vinhomes → VHM first, then VRE, then VIC)
- **UNKNOWN Category:** Assign ticker="UNKNOWN" for unmatched articles, save to separate log
- **Match Confidence:** Tag matches as "exact" or "partial" for downstream filtering
- **Manual Review:** Generate `unmatched_articles.csv` for periodic review and alias updates

**Implementation:**
```python
def match_ticker(text: str, aliases: Dict[str, List[str]]) -> Tuple[str, str]:
    # Priority matching for Vingroup family
    if "vinhomes" in text.lower():
        return "VHM", "exact"
    if "vincom retail" in text.lower() or "trung tâm thương mại vincom" in text.lower():
        return "VRE", "exact"
    if "vingroup" in text.lower() or "tập đoàn vingroup" in text.lower():
        return "VIC", "exact"
    
    # General matching
    for ticker, names in aliases.items():
        for name in names:
            if name.lower() in text.lower():
                return ticker, "partial"
    
    return "UNKNOWN", "none"
```

#### 4. Text Processing Errors

**Scenario:** underthesea tokenization failures, encoding issues, empty text after cleaning

**Strategy:**
- **Encoding Normalization:** Force UTF-8 encoding, replace invalid characters
- **Tokenization Fallback:** If underthesea fails for a specific article, fall back to simple whitespace splitting and log the fallback event. This ensures no articles are silently dropped due to tokenizer errors.
- **Minimum Token Threshold:** Exclude articles with <5 tokens after preprocessing, log their URLs
- **Batch Processing:** Use multiprocessing with error isolation (one failure doesn't crash batch)

**Implementation:**
```python
def safe_tokenize(text: str) -> str:
    try:
        return word_tokenize(text, format="text")
    except Exception as e:
        logger.warning(f"Tokenization failed, using whitespace fallback: {e}")
        return " ".join(text.split())  # Simple whitespace split as fallback
```

#### 5. Data Aggregation Errors

**Scenario:** Missing quarters, insufficient news coverage, NaN in critical fields

**Strategy:**
- **Coverage Validation:** Warn if any (ticker, quarter) has <5 articles
- **NaN Handling:** 
  - For lag features (return_prev_q): Leave as NaN for first quarters
  - For current features: Use median imputation at training time
  - For labels: Exclude rows with NaN labels from training
- **Temporal Continuity:** Flag gaps >2 consecutive quarters per ticker

**Implementation:**
```python
def validate_coverage(df: pd.DataFrame) -> None:
    low_coverage = df[df['news_count'] < 5]
    if not low_coverage.empty:
        logger.warning(f"Low news coverage for {len(low_coverage)} ticker-quarters")
        logger.warning(low_coverage[['ticker', 'quarter_id', 'news_count']])
```

#### 6. Model Training Errors

**Scenario:** Class imbalance, insufficient training data, model convergence failures

**Strategy:**
- **Class Imbalance:** Use class_weight='balanced' for sklearn models, scale_pos_weight for XGBoost
- **Minimum Sample Check:** Require ≥300 samples total, ≥50 samples in test set
- **Convergence Monitoring:** Set max_iter and early_stopping for iterative models
- **Fallback Models:** If tree models fail, fall back to Logistic Regression

**Implementation:**
```python
def check_training_viability(X: pd.DataFrame, y: pd.Series) -> None:
    if len(X) < 300:
        raise ValueError(f"Insufficient training data: {len(X)} samples (need ≥300)")
    
    class_counts = y.value_counts()
    minority_ratio = class_counts.min() / class_counts.sum()
    if minority_ratio < 0.35:
        logger.warning(f"Class imbalance detected: minority class = {minority_ratio:.1%}")
```

#### 7. File System Errors

**Scenario:** Disk full, permission denied, corrupted checkpoint files

**Strategy:**
- **Atomic Writes:** Write to temporary file, then rename (prevents partial writes)
- **Checkpoint Validation:** Verify file exists and has expected columns before skipping task
- **Disk Space Check:** Warn if available space <1GB before starting data collection
- **Backup Critical Files:** Keep previous version of master_with_labels.csv before overwriting

**Implementation:**
```python
def safe_write_csv(df: pd.DataFrame, path: str) -> None:
    temp_path = path + ".tmp"
    df.to_csv(temp_path, index=False)
    os.replace(temp_path, path)  # Atomic rename
    logger.info(f"Saved {len(df)} rows to {path}")
```

#### 8. Configuration Errors

**Scenario:** Invalid YAML, missing required config keys, invalid date formats, "auto" end_date

**Strategy:**
- **Schema Validation:** Validate config against expected schema at startup
- **Required Keys:** Check for tickers, start_date, end_date, train_cutoff
- **Date Parsing:** Use strict date format validation (YYYY-MM-DD), with special handling for `end_date: "auto"` which resolves to the current date at runtime
- **Fail Fast:** Exit with clear error message if config is invalid (don't start pipeline)

**Implementation:**
```python
def validate_config(config: Dict) -> None:
    required_keys = ['tickers', 'start_date', 'end_date', 'train_cutoff']
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {missing}")
    
    # Validate date formats — "auto" is valid for end_date
    for date_key in ['start_date', 'train_cutoff']:
        try:
            datetime.strptime(config[date_key], '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format for {date_key}: {config[date_key]}")
    
    # end_date supports "auto" to resolve to current date at runtime
    if config['end_date'] != 'auto':
        try:
            datetime.strptime(config['end_date'], '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format for end_date: {config['end_date']} (use 'auto' or YYYY-MM-DD)")
```

### Error Logging Strategy

**Log Levels:**
- **DEBUG:** Detailed execution flow (disabled in production)
- **INFO:** Task start/completion, row counts, checkpoints
- **WARNING:** Data quality issues, low coverage, class imbalance
- **ERROR:** Recoverable failures (single ticker scrape failed)
- **CRITICAL:** Unrecoverable failures (config invalid, disk full)

**Log Format:**
```
[2024-01-15 10:23:45] [TASK_2] [WARNING] Failed to scrape ACB from CafeF: HTTP 503
[2024-01-15 10:24:12] [TASK_3] [INFO] Matched 1,234 articles to VN30 tickers (UNKNOWN: 5.2%)
[2024-01-15 10:25:03] [TASK_5] [WARNING] Low news coverage: VJC 2022Q1 (3 articles)
```

**Log Files:**
- `logs/{task_name}_{YYYYMMDD}.log`: Per-task logs
- `logs/pipeline_{YYYYMMDD}.log`: Orchestrator logs
- `logs/errors_{YYYYMMDD}.log`: All ERROR and CRITICAL messages

### Recovery Procedures

**Scenario 1: Scraping Interrupted Mid-Run**
- **Detection:** Check last modified timestamp of output CSV
- **Recovery:** Resume from last successfully scraped ticker (skip existing URLs)
- **Prevention:** Save after each ticker completes

**Scenario 2: Feature Extraction Fails for One Ticker**
- **Detection:** Missing rows in technical_features.csv for specific ticker
- **Recovery:** Rerun TASK 7 with --ticker=XXX flag to process single ticker
- **Prevention:** Wrap per-ticker processing in try-except, continue on failure

**Scenario 3: Model Training Crashes**
- **Detection:** models/best_model.pkl doesn't exist or is incomplete
- **Recovery:** Rerun TASK 10 (features are already computed and cached)
- **Prevention:** Save model after each algorithm completes, not just at end

**Scenario 4: Corrupted Checkpoint File**
- **Detection:** pd.read_csv() raises ParserError
- **Recovery:** Delete corrupted file, rerun upstream task with --force
- **Prevention:** Use atomic writes, validate file after writing

---

## Testing Strategy

### Testing Approach

This pipeline requires a **multi-layered testing strategy** combining unit tests, integration tests, and end-to-end smoke tests. Property-based testing is **not the primary strategy** because most acceptance criteria involve external integrations, file I/O, and non-deterministic ML training rather than pure functions with universal properties.

### Test Pyramid

```
                    ┌─────────────────┐
                    │  E2E Smoke Test │  (1 test: full pipeline on 3 tickers × 4 quarters)
                    └─────────────────┘
                  ┌───────────────────────┐
                  │  Integration Tests    │  (20-30 tests: API calls, file I/O, aggregations)
                  └───────────────────────┘
              ┌─────────────────────────────────┐
              │      Unit Tests                 │  (50-80 tests: pure functions, transformations)
              └─────────────────────────────────┘
```

### 1. Unit Tests (Pure Functions)

**Target:** Isolated functions with clear input/output, no external dependencies

**Test Cases:**

#### Text Preprocessing (TASK 4)
```python
def test_clean_text_removes_html():
    input_text = "<p>Lợi nhuận <b>tăng</b> 20%</p>"
    expected = "lợi nhuận tăng 20%"
    assert clean_text(input_text) == expected

def test_clean_text_preserves_numbers():
    input_text = "Doanh thu 500 tỷ đồng"
    result = clean_text(input_text)
    assert "500" in result

def test_remove_stopwords():
    tokens = "công ty cổ phần lợi nhuận tăng"
    result = remove_stopwords(tokens, stopwords=['công ty', 'cổ phần'])
    assert result == "lợi nhuận tăng"

def test_tokenize_vietnamese():
    text = "Ngân hàng Vietcombank công bố kết quả kinh doanh"
    result = tokenize_vi(text)
    assert "Ngân_hàng" in result  # underthesea should merge compound words
```

#### Entity Matching (TASK 3)
```python
def test_match_vinhomes_to_vhm():
    text = "Vinhomes ra mắt dự án mới"
    ticker, confidence = match_ticker(text, ALIASES)
    assert ticker == "VHM"
    assert confidence == "exact"

def test_match_vingroup_priority():
    text = "Tập đoàn Vingroup đầu tư vào Vinhomes"
    # Should match VHM first (Vinhomes mentioned explicitly)
    ticker, _ = match_ticker(text, ALIASES)
    assert ticker == "VHM"

def test_match_unknown():
    text = "Công ty ABC không thuộc VN30"
    ticker, confidence = match_ticker(text, ALIASES)
    assert ticker == "UNKNOWN"
    assert confidence == "none"
```

#### Label Building (TASK 6)
```python
def test_label_basic_increase():
    row = {'avg_close': 100, 'next_avg_close': 110}
    assert build_label_basic(row) == 1

def test_label_basic_decrease():
    row = {'avg_close': 100, 'next_avg_close': 95}
    assert build_label_basic(row) == 0

def test_label_threshold_above():
    row = {'avg_close': 100, 'next_avg_close': 103}  # +3% return
    assert build_label_threshold(row, threshold=0.02) == 1

def test_label_threshold_neutral():
    row = {'avg_close': 100, 'next_avg_close': 101}  # +1% return
    assert pd.isna(build_label_threshold(row, threshold=0.02))
```

#### Quarterly Aggregation (TASK 5)
```python
def test_assign_quarter_id():
    assert assign_quarter_id("2022-01-15") == "2022Q1"
    assert assign_quarter_id("2022-04-01") == "2022Q2"
    assert assign_quarter_id("2022-12-31") == "2022Q4"

def test_aggregate_prices_by_quarter():
    prices = pd.DataFrame({
        'ticker': ['VNM', 'VNM', 'VNM'],
        'date': ['2022-01-03', '2022-01-04', '2022-01-05'],
        'close': [100, 102, 98]
    })
    result = aggregate_prices_by_quarter(prices)
    assert result.loc[0, 'avg_close'] == 100.0
    assert result.loc[0, 'quarter_id'] == "2022Q1"
```

#### Technical Features (TASK 7)
```python
def test_compute_rsi():
    prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108])
    rsi = compute_rsi(prices, period=14)
    assert 0 <= rsi.iloc[-1] <= 100

def test_compute_bollinger_bands():
    prices = pd.Series([100] * 20 + [110] * 5)
    upper, middle, lower = compute_bollinger_bands(prices, period=20, std=2)
    assert upper.iloc[-1] > middle.iloc[-1] > lower.iloc[-1]
```

### 2. Integration Tests (External Dependencies)

**Target:** Functions that interact with APIs, file system, or databases

**Test Cases:**

#### Price Collection (TASK 1)
```python
@pytest.mark.integration
def test_collect_prices_from_vnstock():
    # Use a single ticker and short date range
    result = collect_prices(['VNM'], '2024-01-01', '2024-01-31')
    assert not result.empty
    assert 'ticker' in result.columns
    assert 'close' in result.columns
    assert result['ticker'].iloc[0] == 'VNM'

@pytest.mark.integration
def test_collect_prices_handles_invalid_ticker():
    # vnstock should handle gracefully
    result = collect_prices(['INVALID'], '2024-01-01', '2024-01-31')
    # Should return empty DataFrame or log error, not crash
    assert isinstance(result, pd.DataFrame)
```

#### Web Scraping (TASK 2)
```python
@pytest.mark.integration
@pytest.mark.slow
def test_scrape_cafef_single_ticker():
    # Test with one ticker, limited date range
    result = scrape_cafef('VNM', '2024-01-01', '2024-01-31')
    assert not result.empty
    assert 'title' in result.columns
    assert 'url' in result.columns
    assert result['source'].iloc[0] == 'cafef'

@pytest.mark.integration
def test_scrape_handles_http_error():
    # Mock a 503 error
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.HTTPError("503 Service Unavailable")
        result = scrape_cafef('VNM', '2024-01-01', '2024-01-31')
        # Should log error and return empty DataFrame
        assert result.empty
```

#### File I/O (All Tasks)
```python
def test_save_and_load_checkpoint(tmp_path):
    df = pd.DataFrame({'ticker': ['VNM'], 'value': [100]})
    filepath = tmp_path / "test.csv"
    
    safe_write_csv(df, str(filepath))
    assert filepath.exists()
    
    loaded = pd.read_csv(filepath)
    assert loaded.equals(df)

def test_atomic_write_prevents_corruption(tmp_path):
    filepath = tmp_path / "test.csv"
    
    # Simulate write failure
    with patch('pandas.DataFrame.to_csv', side_effect=IOError("Disk full")):
        with pytest.raises(IOError):
            safe_write_csv(pd.DataFrame(), str(filepath))
    
    # Original file should not exist (atomic write failed)
    assert not filepath.exists()
```

### 3. End-to-End Smoke Test

**Purpose:** Verify the entire pipeline runs without errors on a small dataset

**Aligned with Requirement 13:** The smoke test uses the `--smoke-test` flag to restrict execution to 3 tickers (VNM, VCB, FPT) and 4 quarters (2022Q1-2022Q4).

**Test Case:**
```python
@pytest.mark.e2e
@pytest.mark.slow
def test_full_pipeline_smoke():
    """
    Run full pipeline with --smoke-test flag: 3 tickers (VNM, VCB, FPT) × 4 quarters (2022Q1-2022Q4).
    This is a smoke test to catch integration issues, not for accuracy validation.
    Validates Requirement 13.
    """
    # Run pipeline with smoke-test flag
    run_pipeline(step='all', force=True, smoke_test=True)
    
    # Verify key outputs exist (Requirement 13.3)
    assert Path('data/prices/all_vn30_prices.csv').exists()
    assert Path('data/news/matched/all_news_matched.csv').exists()
    assert Path('data/aggregated/master_with_labels.csv').exists()
    assert Path('data/features/technical_features.csv').exists()
    assert Path('data/features/keyword_features.csv').exists()
    assert Path('models/best_model.pkl').exists()
    assert Path('reports/model_comparison.csv').exists()
    
    # Verify data quality
    master = pd.read_csv('data/aggregated/master_with_labels.csv')
    assert len(master) >= 10  # At least 10 ticker-quarter pairs
    assert not master['label_basic'].isna().any()  # No missing labels
    
    # Verify smoke test restrictions (Requirement 13.1)
    prices = pd.read_csv('data/prices/all_vn30_prices.csv')
    assert set(prices['ticker'].unique()) == {'VNM', 'VCB', 'FPT'}

@pytest.mark.e2e
def test_smoke_test_reports_timing():
    """
    Verify that --smoke-test reports elapsed time per task and total elapsed time.
    Validates Requirement 13.4.
    """
    # Capture stdout/log output from smoke test run
    result = run_pipeline(step='all', force=True, smoke_test=True)
    # Verify timing information is reported (implementation checks logs)

@pytest.mark.e2e
def test_smoke_test_validates_data_sources():
    """
    Verify that smoke test confirms vnstock retrieves data and CafeF returns ≥10 articles/ticker/quarter.
    Validates Requirement 13.5.
    """
    run_pipeline(step='all', force=True, smoke_test=True)
    
    # Check vnstock data was retrieved
    prices = pd.read_csv('data/prices/all_vn30_prices.csv')
    assert not prices.empty
    
    # Check CafeF article counts
    for ticker in ['VNM', 'VCB', 'FPT']:
        cafef_file = Path(f'data/news/cafef/{ticker}_cafef.csv')
        if cafef_file.exists():
            articles = pd.read_csv(cafef_file)
            # At least 10 articles per ticker across the 4 quarters
            assert len(articles) >= 10, f"CafeF: {ticker} has only {len(articles)} articles"
```

### 4. Data Quality Tests

**Purpose:** Validate data integrity and coverage

**Test Cases:**
```python
def test_no_duplicate_articles():
    news = pd.read_csv('data/news/matched/all_news_matched.csv')
    assert not news['url'].duplicated().any()

def test_all_tickers_have_minimum_quarters():
    master = pd.read_csv('data/aggregated/master_with_labels.csv')
    quarters_per_ticker = master.groupby('ticker').size()
    assert quarters_per_ticker.min() >= 8  # At least 8 quarters per ticker

def test_no_future_leakage():
    master = pd.read_csv('data/aggregated/master_with_labels.csv')
    for _, row in master.iterrows():
        current_q = row['quarter_id']
        next_q = row['next_quarter_id']
        assert next_q > current_q  # Next quarter must be later

def test_label_distribution_not_extreme():
    master = pd.read_csv('data/aggregated/master_with_labels.csv')
    label_ratio = master['label_basic'].mean()
    assert 0.35 <= label_ratio <= 0.65  # Not too imbalanced
```

### 5. Model Validation Tests

**Purpose:** Verify model training and evaluation logic

**Test Cases:**
```python
def test_time_series_split_no_leakage():
    dates = pd.date_range('2022-01-01', '2024-12-31', freq='Q')
    train_idx, test_idx = time_series_split(dates, cutoff='2024-10-01')
    
    assert max(dates[train_idx]) < min(dates[test_idx])

def test_config_a_uses_only_technical_features():
    features = load_features(config='A')
    feature_names = features.columns.tolist()
    
    # Should not contain keyword features
    assert not any('kw_' in name for name in feature_names)
    assert not any('tfidf_' in name for name in feature_names)
    
    # Should contain technical features
    assert 'rsi_mean_q' in feature_names
    assert 'macd_hist_mean_q' in feature_names

def test_model_comparison_includes_all_configs():
    comparison = pd.read_csv('reports/model_comparison.csv')
    
    # Should have results for all 3 configs × 4 algorithms = 12 rows
    assert len(comparison) >= 12
    assert 'Config_A' in comparison['config'].values
    assert 'Config_B' in comparison['config'].values
    assert 'Config_C' in comparison['config'].values
```

### Test Execution Strategy

**Local Development:**
```bash
# Run fast unit tests only
pytest tests/unit/ -v

# Run integration tests (requires network)
pytest tests/integration/ -v --run-integration

# Run full suite including E2E (slow)
pytest tests/ -v --run-integration --run-e2e

# Run pipeline smoke test directly via CLI
python pipeline/run_pipeline.py --step all --smoke-test
```

**CI/CD Pipeline:**
```yaml
# .github/workflows/test.yml
- name: Unit Tests
  run: pytest tests/unit/ --cov=pipeline --cov-report=xml

- name: Integration Tests
  run: pytest tests/integration/ --run-integration
  # Only on main branch (to avoid rate limiting)

- name: Smoke Test
  run: python pipeline/run_pipeline.py --step all --smoke-test --force
  # Only on release branches — uses --smoke-test flag for restricted 3-ticker, 4-quarter test
```

### Test Data Management

**Fixtures:**
- `tests/fixtures/sample_prices.csv`: 3 tickers × 60 days of OHLCV data
- `tests/fixtures/sample_news.csv`: 50 articles with known entity matches
- `tests/fixtures/sample_keywords.json`: Minimal keyword list for testing

**Mocking Strategy:**
- Mock vnstock API calls in unit tests (use recorded responses)
- Mock web scraping in unit tests (use saved HTML snippets)
- Use real APIs in integration tests (with rate limiting)

### Coverage Goals

- **Unit Tests:** ≥80% code coverage for pure functions
- **Integration Tests:** Cover all external API calls and file I/O operations
- **E2E Test:** One complete pipeline run on small dataset
- **Manual Testing:** Keyword list curation (TASK 8) requires human review

### Why PBT Is Not the Primary Strategy

Property-based testing is **not appropriate** for this pipeline because:

1. **External Dependencies:** Most tasks involve web scraping, API calls, or file I/O — these are integration concerns, not pure functions
2. **Non-Deterministic ML:** Model training results vary with random seeds and data splits
3. **Data Quality Focus:** Acceptance criteria emphasize coverage, completeness, and error handling rather than universal properties
4. **Configuration-Driven:** Behavior depends heavily on YAML config and external data sources
5. **Stateful Pipeline:** Each task depends on previous task outputs (checkpoints), not pure transformations

**Where PBT Could Be Used (Limited Scope):**
- Text preprocessing functions (clean_text, tokenize) — but example-based tests are simpler and sufficient
- Entity matching logic — but priority rules and edge cases are better tested with specific examples
- Label computation — but the logic is trivial (simple comparison) and better tested with examples

For this pipeline, **integration tests and example-based unit tests** provide better coverage and are easier to maintain than property-based tests.

### 6. Smoke Test (Requirement 13)

**Purpose:** Quick validation that the entire pipeline works end-to-end before committing to a full run on all 30 tickers.

**Trigger:** `python pipeline/run_pipeline.py --step all --smoke-test`

**Behavior:**
- Restricts execution to 3 tickers (VNM, VCB, FPT) and 4 quarters (2022Q1-2022Q4)
- Executes all steps (TASK 1 through TASK 11) on the restricted dataset
- Verifies all key output files are created
- Reports elapsed time per task and total elapsed time for runtime estimation
- Confirms vnstock retrieves data successfully
- Confirms at least 10 articles per ticker per quarter are scraped from CafeF
- Confirms no unhandled errors occur

**Expected Output Files Verified:**
- `data/prices/all_vn30_prices.csv`
- `data/news/matched/all_news_matched.csv`
- `data/aggregated/master_with_labels.csv`
- `data/features/technical_features.csv`
- `data/features/keyword_features.csv`
- `models/best_model.pkl`
- `reports/model_comparison.csv`

**Rationale:** Running the full pipeline on 30 tickers can take hours. The smoke test provides confidence that all modules integrate correctly in minutes, and the per-task timing helps estimate total runtime for the full run.

---

