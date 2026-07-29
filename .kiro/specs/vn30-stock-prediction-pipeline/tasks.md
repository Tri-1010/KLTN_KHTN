# Implementation Plan: VN30 Stock Prediction Pipeline

## Overview

This implementation plan breaks down the VN30 stock prediction pipeline into 12 sequential modules organized across 5 layers: data collection, text preprocessing, aggregation, feature engineering, and model training. The pipeline combines technical indicators with Vietnamese news keyword features to predict quarterly stock price trends for 30 VN30 constituents.

The implementation follows a linear DAG architecture with checkpoint files at each stage, enabling incremental execution and failure recovery. Each task builds on previous outputs and validates core functionality through code.

## Tasks

- [x] 1. Set up project structure and core configuration
  - Create directory structure: `config/` (pipeline_config.yaml, keywords_finance.json, keywords_by_group.json, stopwords_finance.txt, entity_aliases.json), `data/prices/`, `data/news/cafef/`, `data/news/vietstock/`, `data/news/tnck/`, `data/news/matched/`, `data/news/processed/`, `data/aggregated/`, `data/features/`, `models/`, `reports/`, `pipeline/` (run_pipeline.py, task1_prices.py through task11_shap.py), `logs/`, `notebooks/`
  - Create `config/pipeline_config.yaml` with VN30 tickers list (all 30: ACB, BCM, BID, BVH, CTG, FPT, GAS, GVR, HDB, HPG, MBB, MSN, MWG, PLX, POW, SAB, SHB, SSB, SSI, STB, TCB, TPB, VCB, VHM, VIB, VIC, VJC, VNM, VPB, VRE), date ranges (start_date: "2022-01-01", end_date: "auto"), train_cutoff, label_threshold (0.02), min_news_per_period (5)
  - Create `requirements.txt` with dependencies: vnstock, requests, beautifulsoup4, underthesea, pandas, pandas-ta, scikit-learn, xgboost, lightgbm, shap, pyyaml, matplotlib, seaborn, fuzzywuzzy (or rapidfuzz)
  - Set up logging configuration with format: `[timestamp] [task_name] [level] message`
  - _Requirements: 12.10, 12.11_

- [ ] 2. Implement Price_Collector module (TASK 1)
  - [x] 2.1 Create `pipeline/task1_prices.py` with `collect_prices()` function
    - Use vnstock library (latest version) to retrieve daily OHLCV data (date, open, high, low, close, volume) for all 30 VN30 tickers
    - Validate the ticker list against the canonical VN30 list: ACB, BCM, BID, BVH, CTG, FPT, GAS, GVR, HDB, HPG, MBB, MSN, MWG, PLX, POW, SAB, SHB, SSB, SSI, STB, TCB, TPB, VCB, VHM, VIB, VIC, VJC, VNM, VPB, VRE
    - Collect data from 2022-01-01 up to and including the current date at time of execution
    - Implement retry logic with exponential backoff (max 3 attempts, delays of 1s, 2s, 4s) for API failures
    - Save individual ticker files to `data/prices/{ticker}.csv` and consolidated file to `data/prices/all_vn30_prices.csv` with ticker column
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.8_
  
  - [x] 2.2 Add error handling and validation
    - Log errors with ticker name and timestamp when download fails, continue with remaining tickers
    - Validate data completeness: detect and warn if any ticker has >5% missing trading days compared to expected calendar
    - Print summary report: number of trading days, earliest date, latest date per ticker
    - _Requirements: 1.3, 1.6, 1.7_
  
  - [x] 2.3 Write unit tests for price collection
    - Test date range validation
    - Test handling of invalid ticker symbols
    - Test CSV output format and column presence
    - Test VN30 ticker list validation
    - Test retry logic with exponential backoff
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Checkpoint - Verify price data collection
  - Ensure price data files exist and contain expected date ranges, ask the user if questions arise.

- [ ] 4. Implement News_Scraper module (TASK 2)
  - [x] 4.1 Create `pipeline/task2_scrape.py` with base scraping infrastructure
    - Implement `scrape_source()` function with differentiated rate limiting: at least 1 second between requests to the same domain, 1.5 seconds for Vietstock
    - Add retry logic with exponential backoff (max 3 attempts) for network errors
    - Use browser-like User-Agent headers on all requests to reduce likelihood of being blocked
    - Implement duplicate detection by URL — skip article if URL already exists in output file
    - _Requirements: 2.6, 2.7, 2.8, 2.11_
  
  - [x] 4.2 Implement CafeF scraper
    - Scrape articles from `https://cafef.vn/thi-truong-chung-khoan/{ticker}-ctck.chn` for each VN30 ticker
    - Extract: title, short description, publication date, URL, source="cafef"
    - Handle pagination to collect all articles from 2022-01-01 onward
    - Save to `data/news/cafef/{ticker}_cafef.csv`
    - _Requirements: 2.1, 2.9_
  
  - [x] 4.3 Implement Vietstock scraper
    - Scrape articles from Vietstock using URL pattern `https://vietstock.vn/{ticker}` or via search functionality
    - When Vietstock requires login to view full content, collect only publicly visible title and summary; log a note when articles are access-restricted
    - Extract same metadata fields as CafeF
    - Save to `data/news/vietstock/{ticker}_vietstock.csv`
    - Add comments in code noting which HTML selectors may need adjustment if page structure changes
    - _Requirements: 2.2, 2.3, 2.9, 2.12_
  
  - [x] 4.4 Implement Tinnhanhchungkhoan scraper
    - Scrape articles from tinnhanhchungkhoan.vn by searching via company name or ticker through the search bar or category pages, without pre-assigning tickers (entity matching handled in TASK 3)
    - Extract metadata and save to `data/news/tnck/tnck_raw.csv`
    - Additionally generate a monthly article count report to verify coverage
    - _Requirements: 2.4, 2.5_
  
  - [x] 4.5 Add error handling and reporting
    - If HTML structure of a page cannot be parsed, log the URL and skip that page rather than raising an unhandled exception; note in comments which parts may need adjustment if page structure changes
    - Print report per source: number of articles collected per ticker, date range covered
    - _Requirements: 2.10, 2.12_
  
  - [x] 4.6 Write unit tests for news scraping
    - Test rate limiting enforcement (including 1.5s for Vietstock)
    - Test retry logic with mocked HTTP errors
    - Test duplicate URL detection
    - Test HTML parsing with sample fixtures
    - _Requirements: 2.6, 2.7, 2.8_

- [x] 5. Checkpoint - Verify news data collection
  - Ensure news files exist with reasonable article counts (≥20 articles/ticker/year), ask the user if questions arise.

- [ ] 6. Implement Entity_Matcher module (TASK 3)
  - [x] 6.1 Create `config/entity_aliases.json` and `pipeline/task3_matching.py` with entity matching logic
    - Create `config/entity_aliases.json` with a complete alias dictionary mapping all 30 VN30 tickers to Vietnamese company name aliases (full name, abbreviation, common variants). Example entries: "VNM": ["Vinamilk", "VNM", "Công ty Cổ phần Sữa Việt Nam", "Vietnam Dairy"], "VCB": ["Vietcombank", "VCB", "Ngân hàng Ngoại thương"], "VIC": ["Vingroup", "VIC", "Tập đoàn Vingroup"], "VHM": ["Vinhomes", "VHM"], "VRE": ["Vincom Retail", "VRE"], and similarly for all remaining 25 tickers
    - Load aliases from `config/entity_aliases.json` in the matching module
    - Include special handling for Vingroup family: "Vinhomes" → VHM, "Vincom Retail" or "trung tâm thương mại Vincom" → VRE, "Vingroup" or "tập đoàn Vingroup" → VIC
    - Implement `match_entities()` function with case-insensitive matching against title + description + enriched summary/key facts when available
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 6.2 Handle multi-ticker and unmatched articles
    - Create one output row per matched ticker when article matches multiple tickers
    - Assign ticker="UNKNOWN" and log article URL to separate unmatched log file when no match found
    - Add match_confidence column: "exact" or "partial"
    - _Requirements: 3.4, 3.5, 3.6_
  
  - [x] 6.3 Save matched output and generate report
    - Save to `data/news/matched/all_news_matched.csv` with columns: date, title, description, url, source, ticker, match_confidence
    - Report: total articles before/after matching, UNKNOWN rate, articles per ticker per source
    - Warn for any ticker with <20 articles per year
    - _Requirements: 3.6, 3.7_
  
  - [x] 6.4 Write unit tests for entity matching
    - Test Vinhomes → VHM priority matching
    - Test Vingroup family disambiguation
    - Test UNKNOWN assignment for non-VN30 companies
    - Test multi-ticker article expansion
    - Test alias loading from config/entity_aliases.json
    - _Requirements: 3.1, 3.2, 3.4, 3.5_

- [x] 6B. Implement Article Full-Text Enrichment module (TASK 2B)
  - [x] Create `pipeline/task2b_enrich_articles.py` to fetch article detail pages after entity matching
  - [x] Extract `full_text`, `lead`, `author`, `published_at_detail`, `canonical_url`, `content_hash`, `full_text_available`, and `extraction_status`
  - [x] Generate compact downstream evidence fields: `article_summary`, `key_facts_json`, `event_type_enriched`, `risk_flags_json`, and `relevance_hint`
  - [x] Save `data/news/enriched/all_news_enriched.csv`, preserving duplicate ticker rows for multi-ticker articles while caching fetches by URL
  - [x] Add runner support via `TASK_2B` and `--step enrich_news`; TASK 4 reads enriched output when present

- [ ] 7. Implement Text_Preprocessor module (TASK 4)
  - [x] 7.1 Create `pipeline/task4_preprocess.py` with text cleaning functions
    - Implement `clean_text()`: lowercase, remove HTML tags, special characters, URLs, preserve numeric tokens (e.g., "tăng 20%", "lợi nhuận 500 tỷ"), normalize Vietnamese diacritics
    - Concatenate title + enriched full_text/lead/article_summary/key_facts_json into single `text_clean` field, with description fallback for legacy rows
    - _Requirements: 4.1, 4.2_
  
  - [x] 7.2 Implement Vietnamese tokenization
    - Implement `tokenize_vi()` using `underthesea.word_tokenize(text, format="text")`
    - Add fallback to simple whitespace splitting if underthesea fails for a specific article; log the fallback event
    - Use multiprocessing for batches >10,000 articles
    - _Requirements: 4.3, 4.5_
  
  - [x] 7.3 Implement stopword removal
    - Load standard Vietnamese stopwords and custom financial stopwords from `config/stopwords_finance.txt`
    - Create custom financial stopword list: ["công ty", "doanh nghiệp", "cho biết", "theo đó", "được biết", "chia sẻ", "theo ông", "theo bà", "tại đây", "trong đó", "hiện nay", "thời gian", "năm nay", "năm ngoái", "quý này", "tháng này", "ngày hôm nay", "vừa qua", "mới đây", "theo thông tin", "được biết thêm", "cụ thể", "đáng chú ý"]
    - Save full stopword list to `config/stopwords_finance.txt` for easy editing
    - Implement `remove_stopwords()` function
    - _Requirements: 4.4_
  
  - [x] 7.4 Implement deduplication and save output
    - Remove articles with identical URLs
    - Flag articles with >90% fuzzy title similarity using fuzzywuzzy or rapidfuzz, retain earliest publication date
    - Exclude articles with <5 tokens after processing, log their URLs
    - Save to `data/news/processed/all_news_processed.csv` with columns: text_clean, text_tokenized
    - _Requirements: 4.6, 4.7, 4.9_
  
  - [x] 7.5 Generate preprocessing report
    - Report: article count before/after deduplication, average token count per article, top 50 frequent tokens after stopword removal
    - Warn for articles with <5 tokens
    - _Requirements: 4.8_
  
  - [x] 7.6 Write unit tests for text preprocessing
    - Test HTML tag removal
    - Test numeric token preservation
    - Test Vietnamese diacritics normalization
    - Test Vietnamese tokenization with compound words
    - Test tokenization fallback to whitespace splitting
    - Test stopword removal
    - Test fuzzy deduplication with fuzzywuzzy/rapidfuzz
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6_

- [x] 8. Checkpoint - Verify text preprocessing
  - Ensure processed news file exists with clean tokenized text, ask the user if questions arise.

- [ ] 9. Implement Data_Aggregator module (TASK 5)
  - [x] 9.1 Create `pipeline/task5_aggregate.py` with quarter assignment
    - Implement `assign_quarter_id()`: map dates to "YYYYQN" format (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
    - Add quarter_id column to both price and news datasets
    - _Requirements: 5.1_
  
  - [x] 9.2 Aggregate news by (ticker, quarter_id)
    - Count articles: `news_count`
    - Concatenate all `text_tokenized` values into `combined_text`
    - Save to `data/aggregated/news_by_quarter.csv`
    - _Requirements: 5.2_
  
  - [x] 9.3 Aggregate prices by (ticker, quarter_id)
    - Compute: `avg_close` (mean closing price), `avg_volume` (mean daily volume), `return_intra` ((close_last - close_first) / close_first), `trading_days` (count)
    - Save to `data/aggregated/prices_by_quarter.csv`
    - _Requirements: 5.3_
  
  - [x] 9.4 Create master dataset
    - Merge news and price aggregations on (ticker, quarter_id), retain only rows with both
    - Add `next_quarter_id` column and corresponding `next_avg_close` value
    - Save to `data/aggregated/master_dataset.csv`
    - _Requirements: 5.4, 5.5_
  
  - [x] 9.5 Generate aggregation report and coverage heatmap
    - Report: number of (ticker, quarter) pairs per year, warn for pairs with news_count < 5, warn if total samples < 300
    - Generate heatmap: ticker (rows) × quarter (cols), color = news_count
    - Save heatmap to `reports/coverage_heatmap.png`
    - _Requirements: 5.6, 5.7_
  
  - [x] 9.6 Write unit tests for aggregation
    - Test quarter_id assignment for edge dates
    - Test price aggregation calculations
    - Test news concatenation
    - Test next_quarter_id derivation
    - _Requirements: 5.1, 5.3, 5.4_

- [ ] 10. Implement Label_Builder module (TASK 6)
  - [x] 10.1 Create `pipeline/task6_labels.py` with label computation
    - Implement `build_label_basic()`: 1 if next_avg_close > avg_close, else 0
    - Implement `build_label_threshold()`: compute return = (next_avg_close - avg_close) / avg_close; 1 if return > +0.02, 0 if return < -0.02, NaN if |return| ≤ 0.02
    - Save both label columns to `data/aggregated/master_with_labels.csv`
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 10.2 Analyze label distribution
    - Compute overall ratio of label=1 to label=0
    - Break down ratio by year and by sector (Banking: ACB, BID, CTG, HDB, MBB, SHB, SSB, STB, TCB, TPB, VCB, VIB, VPB; Real Estate: BCM, VHM, VIC, VRE; Energy/Resources: GAS, GVR, PLX, POW; Consumer/Food: MWG, SAB, VNM; Industrial: HPG; Finance/Insurance: BVH, SSI; Tech/Telecom: FPT)
    - Warn if minority class ratio < 35%
    - _Requirements: 6.4, 6.5_
  
  - [x] 10.3 Generate label distribution visualization
    - Create bar chart of label distribution by year × quarter
    - Save to `reports/label_distribution.png`
    - _Requirements: 6.6_
  
  - [x] 10.4 Write unit tests for label building
    - Test label_basic for increase/decrease cases
    - Test label_threshold for above/below/neutral cases
    - Test return calculation
    - _Requirements: 6.1, 6.2_

- [x] 11. Checkpoint - Verify master dataset with labels
  - Ensure master_with_labels.csv exists with balanced label distribution, ask the user if questions arise.

- [ ] 12. Implement Tech_Feature_Extractor module (TASK 7)
  - [x] 12.1 Create `pipeline/task7_tech_features.py` with daily indicator computation
    - Use pandas-ta or ta-lib to compute daily indicators with explicit parameters: RSI with period 14, MACD with parameters (fast=12, slow=26, signal=9) producing MACD line, signal line, and histogram, Bollinger Bands with parameters (period=20, std=2) producing upper, middle, and lower bands, SMA with periods 20 and 50, EMA with period 20
    - _Requirements: 7.1_
  
  - [x] 12.2 Aggregate indicators by quarter into named feature groups
    - For each (ticker, quarter_id) compute features organized into named groups:
      - **Returns group**: `return_q` (cumulative quarterly return), `return_mean_daily` (mean daily return), `return_std_daily` (std dev of daily returns)
      - **Volatility group**: `volatility_q` (return_std_daily * sqrt(trading_days)), `price_range_q` ((high_max - low_min) / avg_close)
      - **Liquidity group**: `volume_mean_q` (mean daily volume), `volume_change_q` (volume change vs previous quarter)
      - **Trend group** (end-of-quarter values): `sma20_end`, `ema20_end`, `price_vs_sma20` ((close_last - sma20_end) / sma20_end)
      - **Indicator group** (quarterly means): `rsi_mean_q`, `rsi_end_q`, `macd_hist_mean_q`, `bb_position_q` ((close - BB_lower) / (BB_upper - BB_lower))
      - **Momentum group** (lagged values): `return_prev_q` (lag 1), `return_2q_ago` (lag 2)
    - Leave lag features as NaN for first quarters (no automatic imputation)
    - _Requirements: 7.2, 7.3_
  
  - [x] 12.3 Save technical features and check correlations
    - Save to `data/features/technical_features.csv` with columns: ticker, quarter_id, all feature columns
    - Compute correlation matrix, warn for feature pairs with |correlation| > 0.95
    - _Requirements: 7.4, 7.5_
  
  - [x] 12.4 Write unit tests for technical features
    - Test RSI computation bounds (0-100) with period=14
    - Test MACD computation with parameters (12,26,9)
    - Test Bollinger Bands ordering (upper > middle > lower) with parameters (20,2)
    - Test quarterly aggregation calculations per named group
    - Test lag feature generation
    - _Requirements: 7.1, 7.2_

- [ ] 13. Implement Keyword_Builder module (TASK 8)
  - [x] 13.1 Create `pipeline/task8_keywords.py` with keyword candidate extraction
    - Use CountVectorizer to extract top 500 unigrams and top 300 bigrams after stopword removal
    - Save candidates to `config/keyword_candidates.csv` for manual review
    - _Requirements: 8.1_
  
  - [x] 13.2 Build curated keyword list with sentiment direction
    - Create structured keyword list organized into 6 thematic groups with COMPLETE keyword lists:
      - **Group A (Kết quả kinh doanh)**: positive: ["lợi nhuận tăng", "doanh thu tăng", "tăng trưởng mạnh", "vượt kế hoạch", "kỷ lục", "tăng trưởng", "lãi ròng", "lợi nhuận sau thuế tăng", "kết quả tích cực"]; negative: ["lợi nhuận giảm", "doanh thu giảm", "lợi nhuận âm", "thua lỗ", "lỗ ròng", "dưới kế hoạch", "sụt giảm", "kết quả tiêu cực", "lợi nhuận thấp hơn"]
      - **Group B (Chính sách cổ đông)**: positive: ["chia cổ tức", "cổ tức cao", "mua lại cổ phiếu", "phát hành thưởng", "tăng vốn điều lệ", "cổ tức tiền mặt"]; negative: ["không chia cổ tức", "hủy cổ tức", "giảm cổ tức", "phát hành pha loãng", "chào bán giá thấp"]
      - **Group C (Tài chính doanh nghiệp)**: positive: ["giảm nợ", "trả nợ", "cải thiện tài chính", "hệ số an toàn vốn", "dòng tiền dương", "tiền mặt dồi dào"]; negative: ["nợ xấu", "nợ vay tăng", "áp lực tài chính", "nợ quá hạn", "hệ số nợ cao", "thiếu thanh khoản", "dòng tiền âm"]
      - **Group D (Hoạt động kinh doanh)**: positive: ["ký kết hợp đồng", "mở rộng thị trường", "dự án mới", "đầu tư mới", "hợp tác chiến lược", "thắng thầu", "xuất khẩu tăng"]; negative: ["hủy hợp đồng", "dự án trì hoãn", "thu hẹp hoạt động", "đóng cửa", "dừng dự án"]
      - **Group E (Rủi ro và pháp lý)**: negative: ["bị phạt", "vi phạm", "bị thanh tra", "bị kiểm toán từ chối", "cảnh báo", "đình chỉ", "khởi tố", "điều tra", "tranh chấp pháp lý", "bị kiện"]
      - **Group F (Sự kiện doanh nghiệp trung tính)**: neutral: ["đại hội cổ đông", "họp HĐQT", "thay đổi lãnh đạo", "thay CEO", "sáp nhập", "mua lại", "phát hành cổ phiếu mới", "niêm yết thêm", "thoái vốn"]
    - Assign direction attribute: "positive", "negative", or "neutral" to each keyword
    - _Requirements: 8.2_
  
  - [x] 13.3 Save keyword lists and generate frequency report
    - Save to `config/keywords_finance.json` with structure: {"positive": [...], "negative": [...], "neutral": [...]}
    - Save group-level breakdown to `config/keywords_by_group.json` organized by groups A through F
    - Print corpus frequency of each keyword for validation
    - _Requirements: 8.3, 8.4, 8.5_

- [ ] 14. Implement Keyword_Feature_Extractor module (TASK 9)
  - [x] 14.1 Create `pipeline/task9_kw_features.py` with raw and normalized counts
    - For each (ticker, quarter_id) and keyword k: compute `kw_{k}` (raw count in combined_text) and `kw_norm_{k}` (raw count / news_count)
    - _Requirements: 9.1_
  
  - [x] 14.2 Compute aggregate sentiment scores
    - Compute `pos_score` (sum of kw_norm for positive keywords), `neg_score` (sum of kw_norm for negative keywords), `sentiment_ratio` = (pos_score - neg_score) / (pos_score + neg_score + 1e-6)
    - _Requirements: 9.2_
  
  - [x] 14.3 Compute TF-IDF features
    - Use TfidfVectorizer(vocabulary=keyword_list, min_df=2) fitted on full corpus
    - Transform to get `tfidf_{k}` columns for each keyword
    - _Requirements: 9.3_
  
  - [x] 14.4 Add coverage features and save output
    - Include: `news_count`, `news_count_log` = log(news_count + 1), `has_min_news` = 1 if news_count >= 5 else 0
    - Save to `data/features/keyword_features.csv` with columns: ticker, quarter_id, all feature columns
    - _Requirements: 9.4, 9.5_
  
  - [x] 14.5 Generate keyword feature report and handle sparsity
    - Report: total features generated, top 20 keywords by frequency, overall sparsity rate (percentage of zero-valued keyword-ticker-quarter cells), pos_score and neg_score distributions
    - Log keywords with sparsity > 95% as removal candidates
    - Handle sparse features: many keywords having count = 0 is expected behavior — values SHALL be kept as-is (not imputed)
    - _Requirements: 9.6, 9.7, 9.8_
  
  - [x] 14.6 Write unit tests for keyword features
    - Test raw count extraction
    - Test normalized count calculation
    - Test sentiment score aggregation
    - Test TF-IDF computation
    - Test sparsity rate calculation
    - _Requirements: 9.1, 9.2, 9.3, 9.8_

- [x] 15. Checkpoint - Verify feature extraction
  - Ensure technical_features.csv and keyword_features.csv exist with expected feature counts, ask the user if questions arise.

- [ ] 16. Implement Model_Trainer module (TASK 10)
  - [x] 16.1 Create `pipeline/task10_train.py` with data preparation
    - Merge technical_features.csv, keyword_features.csv, and master_with_labels.csv on (ticker, quarter_id)
    - Apply median imputation for NaN values per column
    - Remove ticker and quarter_id columns before training
    - _Requirements: 10.1_
  
  - [x] 16.2 Implement time-series split
    - Sort by quarter_id ascending
    - Train: all quarters before 2025-Q1
    - Test: 2025-Q1 onward (or last 20% if fewer than 4 test quarters)
    - Apply consistently across all tickers (no random shuffling)
    - _Requirements: 10.2_
  
  - [x] 16.3 Implement three feature configurations
    - Config_A: technical features only
    - Config_B: keyword features only
    - Config_C: technical + keyword features combined
    - _Requirements: 10.3_
  
  - [x] 16.4 Implement baseline models
    - Majority-class baseline: predict most frequent label
    - Naive momentum baseline: predict next quarter label = current quarter label
    - Evaluate both baselines on all three configurations
    - _Requirements: 10.4_
  
  - [x] 16.5 Train ML algorithms
    - Logistic Regression (C=1.0, class_weight='balanced')
    - Random Forest (n_estimators=100, class_weight='balanced')
    - XGBoost (scale_pos_weight = neg_count / pos_count)
    - LightGBM (is_unbalance=True)
    - Train each algorithm on all three configurations
    - _Requirements: 10.5_
  
  - [x] 16.6 Evaluate and save results
    - Compute for each model-configuration pair: Accuracy, Precision, Recall, F1-macro, AUC-ROC, Balanced Accuracy
    - Print confusion matrix for each
    - Save consolidated comparison table to `reports/model_comparison.csv` with rows = model-configuration, columns = metrics
    - _Requirements: 10.6, 10.7_
  
  - [x] 16.7 Highlight best model and Config comparison
    - Identify best model by Balanced Accuracy
    - Report performance delta between Config_A and Config_C for each algorithm
    - Log note if Config_C does not improve over Config_A (still a valid research finding)
    - Save best model to `models/best_model.pkl`
    - _Requirements: 10.8, 10.9_
  
  - [x] 16.8 Write unit tests for model training
    - Test time-series split ensures no future leakage
    - Test Config_A uses only technical features
    - Test Config_B uses only keyword features
    - Test Config_C uses combined features
    - Test class weight computation
    - _Requirements: 10.2, 10.3_

- [ ] 17. Implement SHAP_Analyzer module (TASK 11)
  - [x] 17.1 Create `pipeline/task11_shap.py` with tree-based feature importance
    - Load best model from Config_C (XGBoost or LightGBM)
    - Extract feature_importances_ (gain-based)
    - Plot top 30 features with distinct colors for technical vs. keyword features
    - Save to `reports/feature_importance.png`
    - _Requirements: 11.1_
  
  - [x] 17.2 Compute permutation importance
    - Use sklearn.inspection.permutation_importance on test set
    - Plot top 30 features with same color scheme
    - Save to `reports/permutation_importance.png`
    - _Requirements: 11.2_
  
  - [x] 17.3 Compute SHAP values and generate plots
    - Use shap.TreeExplainer for best model
    - Generate beeswarm summary plot, save to `reports/shap_summary.png`
    - Generate mean absolute SHAP bar plot, save to `reports/shap_bar.png`
    - _Requirements: 11.3_
  
  - [x] 17.4 Analyze top keywords
    - Extract SHAP values for keyword features only
    - Identify top 20 most important keywords
    - For each keyword record: direction label (positive/negative/neutral), mean SHAP value, actual SHAP direction
    - Verify positive-direction keywords have positive mean SHAP values, log mismatches as anomalies
    - Save to `reports/top_keywords_analysis.csv`
    - _Requirements: 11.4, 11.5_
  
  - [x] 17.5 Compute group contribution analysis
    - Calculate total mean absolute SHAP contribution of technical feature group vs. keyword feature group
    - Report percentage share of each group as empirical evidence for H1
    - _Requirements: 11.6_
  
  - [x] 17.6 Generate SHAP case studies
    - Identify 2-3 (ticker, quarter) pairs correctly predicted by Config_C but not Config_A
    - Generate SHAP waterfall plots for each case
    - Save to `reports/shap_case_study_{ticker}_{quarter}.png`
    - _Requirements: 11.7_

- [x] 18. Checkpoint - Verify model training and analysis
  - Ensure best_model.pkl, model_comparison.csv, and SHAP reports exist, ask the user if questions arise.

- [ ] 19. Implement Pipeline_Runner orchestrator (TASK 12)
  - [x] 19.1 Create `pipeline/run_pipeline.py` with argparse CLI
    - Accept `--step` argument with values: "all", "data", "preprocess", "features", "train", "update_news"
    - Accept `--force` flag to rerun even if checkpoint exists
    - Accept `--smoke-test` flag to restrict execution to 3 tickers (VNM, VCB, FPT) and 4 quarters (2022Q1-2022Q4)
    - _Requirements: 12.1, 13.1_
  
  - [x] 19.2 Implement step execution logic
    - `--step all`: execute TASK 1 through TASK 11 in sequential order (TASK 12 is the runner itself and is not executed as a step)
    - `--step data`: execute TASK 1, 2, 3 only
    - `--step preprocess`: execute TASK 4 (text preprocessing), TASK 5 (aggregation), TASK 6 (label building)
    - `--step features`: execute TASK 4, 5, 6 (preprocessing prerequisites, skipped if checkpoint exists unless --force) then TASK 7, 8, 9 (feature extraction)
    - `--step train`: execute TASK 10, 11 only
    - `--step update_news`: scrape new articles since last run, update matched and processed files incrementally
    - _Requirements: 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_
  
  - [x] 19.3 Implement configuration loading
    - Load all parameters from `config/pipeline_config.yaml`: tickers, start_date, end_date (support "auto" to resolve to current date at runtime), quarter_unit, min_news_per_period, train_cutoff, label_threshold
    - Validate config against expected schema at startup; fail fast with clear error message if config is invalid
    - _Requirements: 12.8_
  
  - [x] 19.4 Implement checkpointing logic
    - Check if task output file exists before running
    - Skip task and log skip message if output exists, unless `--force` flag provided
    - _Requirements: 12.9_
  
  - [x] 19.5 Implement structured logging
    - Write logs to `logs/{task_name}_{date}.log` for each task
    - Include: timestamp, input row count, output row count, warnings, errors
    - _Requirements: 12.10_
  
  - [x] 19.6 Add error handling and recovery
    - Catch unhandled exceptions, log full stack trace to task log file
    - Print human-readable error summary to stdout
    - Exit with non-zero return code without corrupting previous task outputs
    - _Requirements: 12.12_
  
  - [x] 19.7 Verify directory structure and model saving
    - Ensure all required directories and config files exist per Requirement 12.11: `config/` (pipeline_config.yaml, keywords_finance.json, keywords_by_group.json, stopwords_finance.txt, entity_aliases.json), `data/prices/`, `data/news/cafef/`, `data/news/vietstock/`, `data/news/tnck/`, `data/news/matched/`, `data/news/processed/`, `data/aggregated/`, `data/features/`, `models/`, `reports/`, `pipeline/` (run_pipeline.py, task1_prices.py through task11_shap.py), `logs/`, `notebooks/`
    - Save best trained model to `models/best_model.pkl` after TASK 10
    - _Requirements: 12.11_
  
  - [x] 19.8 Write integration tests for pipeline runner
    - Test CLI argument parsing (including --smoke-test flag)
    - Test checkpoint skip logic
    - Test force flag behavior
    - Test error handling and logging
    - Test --step preprocess runs TASK 4+5+6
    - Test --step features includes prerequisites TASK 4/5/6
    - Test --step all runs TASK 1-11 (not 1-12)
    - _Requirements: 12.1, 12.2, 12.4, 12.5, 12.9, 12.12_

- [ ] 20. Implement Smoke Test (Requirement 13)
  - [x] 20.1 Implement `--smoke-test` flag behavior in Pipeline_Runner
    - When `--smoke-test` is specified, restrict execution to 3 tickers (VNM, VCB, FPT) and 4 quarters (2022Q1 through 2022Q4)
    - Execute all steps (TASK 1 through TASK 11) on the restricted dataset
    - _Requirements: 13.1, 13.2_
  
  - [x] 20.2 Add smoke test output verification
    - Verify all key output files exist after smoke test: `data/prices/all_vn30_prices.csv`, `data/news/matched/all_news_matched.csv`, `data/aggregated/master_with_labels.csv`, `data/features/technical_features.csv`, `data/features/keyword_features.csv`, `models/best_model.pkl`, `reports/model_comparison.csv`
    - _Requirements: 13.3_
  
  - [x] 20.3 Add timing report and data source validation
    - Report elapsed time per task and total elapsed time to help estimate full pipeline runtime
    - Confirm vnstock retrieves data successfully
    - Confirm at least 10 articles per ticker per quarter are scraped from CafeF
    - Confirm pipeline produces no unhandled errors
    - _Requirements: 13.4, 13.5_

- [x] 21. Final checkpoint - End-to-end verification
  - Run `python pipeline/run_pipeline.py --step all --smoke-test` to verify all modules integrate correctly on 3 tickers (VNM, VCB, FPT) for 4 quarters (2022Q1-2022Q4), ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- The pipeline follows a linear DAG architecture with checkpoint files enabling failure recovery
- Testing strategy emphasizes integration tests and example-based unit tests over property-based tests due to external dependencies (APIs, web scraping, file I/O) and non-deterministic ML training
- Vietnamese NLP processing uses underthesea library with custom financial stopwords; tokenization falls back to whitespace splitting if underthesea fails
- Three-configuration experiment (Config A/B/C) enables direct measurement of keyword feature contribution to answer research hypothesis H1
- Time-series split prevents data leakage by ensuring all training data precedes all test data
- The complete keyword list (Groups A-F) contains 73 keywords: 28 positive, 36 negative, 9 neutral — all must be implemented exactly as specified in Requirement 8.2
- Entity aliases for all 30 VN30 tickers are stored in `config/entity_aliases.json` for easy maintenance
- The `--smoke-test` flag (Requirement 13) provides a quick end-to-end validation before committing to a full pipeline run
