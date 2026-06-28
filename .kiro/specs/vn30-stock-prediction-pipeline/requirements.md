# Requirements Document

## Introduction

Pipeline ML hoàn chỉnh phục vụ luận văn thạc sĩ về dự báo xu hướng giá cổ phiếu VN30 dựa trên kết hợp đặc trưng kỹ thuật (OHLCV, RSI, MACD, Bollinger Bands, SMA, EMA) và đặc trưng tần suất từ khóa trích xuất từ tin tức tài chính tiếng Việt (CafeF, Vietstock, Tinnhanhchungkhoan). Câu hỏi nghiên cứu trọng tâm (H1): việc bổ sung đặc trưng từ khóa tin tức có cải thiện độ chính xác dự báo so với chỉ dùng đặc trưng kỹ thuật không?

Bài toán được thiết kế dưới dạng phân loại nhị phân (tăng / giảm-không-tăng) theo đơn vị quý, áp dụng cho 30 mã cổ phiếu thuộc chỉ số VN30 trên sàn HOSE, giai đoạn từ 01/01/2022 đến hiện tại. Pipeline bao gồm 12 bước từ thu thập dữ liệu, tiền xử lý, trích xuất đặc trưng, huấn luyện mô hình, phân tích SHAP đến đóng gói bán tự động.

Trước khi chạy toàn bộ pipeline, cần thực hiện smoke test trên 3 mã (VNM, VCB, FPT) trong 4 quý (2022Q1–2022Q4) để xác nhận pipeline chạy end-to-end không lỗi và ước lượng thời gian chạy toàn bộ.

## Glossary

- **Pipeline**: Chuỗi 12 bước xử lý tuần tự từ thu thập dữ liệu đến đóng gói kết quả.
- **Price_Collector**: Module thu thập dữ liệu giá OHLCV từ vnstock (TASK 1).
- **News_Scraper**: Module scrape tin tức từ CafeF, Vietstock, Tinnhanhchungkhoan (TASK 2).
- **Entity_Matcher**: Module gắn bài tin tức với mã cổ phiếu VN30 (TASK 3).
- **Text_Preprocessor**: Module tiền xử lý văn bản tiếng Việt bằng underthesea (TASK 4).
- **Data_Aggregator**: Module tổng hợp dữ liệu theo (ticker, quarter_id) (TASK 5).
- **Label_Builder**: Module xây dựng nhãn tăng/giảm từ avg_close (TASK 6).
- **Tech_Feature_Extractor**: Module tính chỉ báo kỹ thuật và tổng hợp theo quý (TASK 7).
- **Keyword_Builder**: Module xây dựng danh sách từ khóa tài chính phân nhóm (TASK 8).
- **Keyword_Feature_Extractor**: Module trích xuất đặc trưng tần suất từ khóa (TASK 9).
- **Model_Trainer**: Module huấn luyện và đánh giá mô hình ML (TASK 10).
- **SHAP_Analyzer**: Module phân tích SHAP và feature importance (TASK 11).
- **Pipeline_Runner**: Module đóng gói pipeline bán tự động với argparse (TASK 12).
- **VN30**: Rổ 30 mã cổ phiếu vốn hóa lớn trên HOSE: ACB, BCM, BID, BVH, CTG, FPT, GAS, GVR, HDB, HPG, MBB, MSN, MWG, PLX, POW, SAB, SHB, SSB, SSI, STB, TCB, TPB, VCB, VHM, VIB, VIC, VJC, VNM, VPB, VRE.
- **OHLCV**: Open, High, Low, Close, Volume — dữ liệu giá theo ngày.
- **quarter_id**: Chuỗi định danh quý, ví dụ "2022Q1", "2023Q4".
- **label_basic**: Nhãn nhị phân: 1 nếu avg_close(q+1) > avg_close(q), ngược lại 0.
- **label_threshold**: Nhãn nhị phân với ngưỡng ±2%: 1 nếu return > +2%, 0 nếu return < -2%, NaN nếu |return| ≤ 2%.
- **Config_A**: Cấu hình chỉ dùng đặc trưng kỹ thuật.
- **Config_B**: Cấu hình chỉ dùng đặc trưng từ khóa.
- **Config_C**: Cấu hình kết hợp đặc trưng kỹ thuật và từ khóa.
- **pos_score**: Tổng tần suất chuẩn hóa của các từ khóa nhóm positive trong một (ticker, quarter).
- **neg_score**: Tổng tần suất chuẩn hóa của các từ khóa nhóm negative trong một (ticker, quarter).
- **sentiment_ratio**: (pos_score - neg_score) / (pos_score + neg_score + 1e-6).
- **Time_Series_Split**: Phương pháp chia train/test theo thời gian: train = tất cả quý trước ngưỡng, test = từ ngưỡng trở đi.
- **Checkpoint**: File trạng thái lưu output của mỗi task để tránh chạy lại từ đầu.
- **vnstock**: Thư viện Python chính thức để lấy dữ liệu chứng khoán Việt Nam.
- **underthesea**: Thư viện NLP tiếng Việt dùng cho tách từ (word segmentation).
- **Sector_Mapping**: Phân nhóm ngành cho 30 mã VN30 — Banking: ACB, BID, CTG, HDB, MBB, SHB, SSB, STB, TCB, TPB, VCB, VIB, VPB; Real Estate: BCM, VHM, VIC, VRE; Energy/Resources: GAS, GVR, PLX, POW; Consumer/Food: MWG, SAB, VNM; Industrial: HPG; Finance/Insurance: BVH, SSI; Tech/Telecom: FPT.
- **Smoke_Test**: Chạy thử pipeline trên 3 mã (VNM, VCB, FPT) trong 4 quý (2022Q1–2022Q4) để xác nhận tính đúng đắn trước khi chạy toàn bộ.

---

## Requirements


### Requirement 1: Thu thập dữ liệu giá cổ phiếu VN30

**User Story:** As a researcher, I want to collect daily OHLCV data for all 30 VN30 tickers from 2022-01-01 to the current date, so that I can build technical features and price labels for the prediction model.

#### Acceptance Criteria

1. THE Price_Collector SHALL retrieve daily OHLCV data (date, open, high, low, close, volume) for all 30 VN30 tickers using the vnstock library (latest version).
2. THE Price_Collector SHALL validate the ticker list against the canonical VN30 list: ACB, BCM, BID, BVH, CTG, FPT, GAS, GVR, HDB, HPG, MBB, MSN, MWG, PLX, POW, SAB, SHB, SSB, SSI, STB, TCB, TPB, VCB, VHM, VIB, VIC, VJC, VNM, VPB, VRE.
3. WHEN a ticker fails to download, THE Price_Collector SHALL log the error with ticker name and timestamp, then continue processing the remaining tickers without interruption.
4. THE Price_Collector SHALL implement retry logic with exponential backoff (max 3 attempts, delays of 1s, 2s, 4s) for API failures.
5. THE Price_Collector SHALL save individual CSV files to `data/prices/{ticker}.csv` and a combined file to `data/prices/all_vn30_prices.csv` with a `ticker` column.
6. WHEN data collection completes, THE Price_Collector SHALL print a summary report showing the number of trading days, earliest date, and latest date for each ticker.
7. IF a ticker has more than 5% missing trading days compared to the expected calendar, THEN THE Price_Collector SHALL emit a warning identifying that ticker and the missing percentage.
8. THE Price_Collector SHALL collect data starting from 2022-01-01 up to and including the current date at time of execution.

---

### Requirement 2: Scrape tin tức tài chính từ ba nguồn

**User Story:** As a researcher, I want to scrape financial news articles (title, description, date, URL) from CafeF, Vietstock, and Tinnhanhchungkhoan from 2022 onward, so that I have a corpus of Vietnamese financial news to extract keyword features from.

#### Acceptance Criteria

1. THE News_Scraper SHALL collect article metadata (title, short description, publication date, URL, source) from CafeF for each VN30 ticker using the URL pattern `https://cafef.vn/thi-truong-chung-khoan/{ticker}-ctck.chn`, handling pagination to collect all articles from 2022-01-01 onward.
2. THE News_Scraper SHALL collect article metadata from Vietstock for each VN30 ticker using the URL pattern `https://vietstock.vn/{ticker}` or via search functionality.
3. WHEN Vietstock requires login to view full content, THE News_Scraper SHALL collect only the publicly visible title and summary, and log a note when articles are access-restricted.
4. THE News_Scraper SHALL collect article metadata from Tinnhanhchungkhoan (tinnhanhchungkhoan.vn) by searching via company name or ticker through the search bar or category pages, without pre-assigning tickers (entity matching is handled in TASK 3).
5. THE News_Scraper SHALL save results to `data/news/tnck/tnck_raw.csv` and additionally generate a monthly article count report to verify coverage.
6. WHEN making HTTP requests, THE News_Scraper SHALL apply a rate limit of at least 1 second between consecutive requests to the same domain (1.5 seconds for Vietstock) to avoid being blocked.
7. WHEN a network error occurs, THE News_Scraper SHALL retry the request up to 3 times using exponential backoff before logging the failure and continuing.
8. IF an article URL already exists in the output file, THEN THE News_Scraper SHALL skip that article to prevent duplicate entries.
9. THE News_Scraper SHALL save CafeF results to `data/news/cafef/{ticker}_cafef.csv` and Vietstock results to `data/news/vietstock/{ticker}_vietstock.csv`.
10. WHEN scraping completes for a source, THE News_Scraper SHALL print a report showing the number of articles collected per ticker and the date range covered.
11. THE News_Scraper SHALL use browser-like HTTP headers (User-Agent) on all requests to reduce the likelihood of being blocked.
12. IF the HTML structure of a page cannot be parsed, THEN THE News_Scraper SHALL log the URL and skip that page rather than raising an unhandled exception, noting in comments which parts may need adjustment if the page structure changes.

---

### Requirement 3: Gắn tin tức với mã cổ phiếu (Entity Matching)

**User Story:** As a researcher, I want to map each news article to one or more VN30 tickers based on company names and aliases in the title and description, so that I can aggregate news by ticker and quarter.

#### Acceptance Criteria

1. THE Entity_Matcher SHALL maintain a complete alias dictionary mapping all 30 VN30 tickers to Vietnamese company name aliases (full name, abbreviation, common variants), stored in `config/entity_aliases.json`. Example entries: "VNM": ["Vinamilk", "VNM", "Công ty Cổ phần Sữa Việt Nam", "Vietnam Dairy"], "VCB": ["Vietcombank", "VCB", "Ngân hàng Ngoại thương"], "VIC": ["Vingroup", "VIC", "Tập đoàn Vingroup"], "VHM": ["Vinhomes", "VHM"], "VRE": ["Vincom Retail", "VRE"], and similarly for all remaining tickers.
2. WHEN matching Vingroup-related tickers, THE Entity_Matcher SHALL apply priority rules: articles mentioning "Vinhomes" map to VHM (not VIC), articles mentioning "Vincom Retail" or "trung tâm thương mại Vincom" map to VRE, and only articles explicitly mentioning "Vingroup" or "tập đoàn Vingroup" map to VIC.
3. THE Entity_Matcher SHALL perform case-insensitive matching against the combined title and description fields of each article.
4. WHEN an article matches multiple tickers, THE Entity_Matcher SHALL create one output row per matched ticker (e.g., a banking comparison article creates rows for each matched bank ticker).
5. IF an article matches no ticker, THEN THE Entity_Matcher SHALL assign ticker = "UNKNOWN" and log the article URL to a separate unmatched log file.
6. THE Entity_Matcher SHALL save the matched output to `data/news/matched/all_news_matched.csv` with columns: date, title, description, url, source, ticker, match_confidence (exact/partial).
7. WHEN matching completes, THE Entity_Matcher SHALL report: total articles before and after matching, UNKNOWN rate, articles per ticker per source, and a warning for any ticker with fewer than 20 articles per year.

---

### Requirement 4: Tiền xử lý văn bản tiếng Việt

**User Story:** As a researcher, I want to clean, tokenize, and deduplicate Vietnamese news text, so that I have a high-quality corpus ready for keyword feature extraction.

#### Acceptance Criteria

1. THE Text_Preprocessor SHALL normalize each article's text by converting to lowercase, removing HTML tags, special characters, and URLs, while preserving numeric tokens (e.g., "tăng 20%", "lợi nhuận 500 tỷ") and normalizing Vietnamese diacritics.
2. THE Text_Preprocessor SHALL concatenate the title and description of each article into a single `text_clean` field before tokenization.
3. THE Text_Preprocessor SHALL tokenize Vietnamese text using `underthesea.word_tokenize(text, format="text")`, with a fallback to simple whitespace splitting if underthesea fails for a specific article.
4. THE Text_Preprocessor SHALL remove stopwords using a combined list of standard Vietnamese stopwords and a custom financial stopword list including: "công ty", "doanh nghiệp", "cho biết", "theo đó", "được biết", "chia sẻ", "theo ông", "theo bà", "tại đây", "trong đó", "hiện nay", "thời gian", "năm nay", "năm ngoái", "quý này", "tháng này", "ngày hôm nay", "vừa qua", "mới đây", "theo thông tin", "được biết thêm", "cụ thể", "đáng chú ý". The full list SHALL be saved to `config/stopwords_finance.txt` for easy editing.
5. WHEN the input corpus exceeds 10,000 articles, THE Text_Preprocessor SHALL use multiprocessing to parallelize the tokenization step.
6. THE Text_Preprocessor SHALL deduplicate articles by removing entries with identical URLs, and additionally flag articles whose titles have more than 90% fuzzy similarity (using fuzzywuzzy or rapidfuzz), retaining only the earliest publication date.
7. THE Text_Preprocessor SHALL save the processed output to `data/news/processed/all_news_processed.csv` with additional columns `text_clean` and `text_tokenized`.
8. WHEN preprocessing completes, THE Text_Preprocessor SHALL report: article count before and after deduplication, average token count per article, top 50 most frequent tokens after stopword removal (for quality verification), and a warning for any article with fewer than 5 tokens after processing.
9. IF an article has fewer than 5 tokens after processing, THEN THE Text_Preprocessor SHALL log that article's URL and exclude it from the output.

---

### Requirement 5: Tổng hợp dữ liệu theo cổ phiếu - quý

**User Story:** As a researcher, I want to aggregate news and price data by (ticker, quarter_id) into a master dataset, so that each row represents one stock-quarter observation ready for feature engineering and labeling.

#### Acceptance Criteria

1. THE Data_Aggregator SHALL assign a `quarter_id` label (format "YYYYQn", e.g., "2022Q1") to every row in both the price dataset and the news dataset, using the definition: Q1 = Jan-Mar, Q2 = Apr-Jun, Q3 = Jul-Sep, Q4 = Oct-Dec.
2. THE Data_Aggregator SHALL aggregate news per (ticker, quarter_id) by counting articles (`news_count`) and concatenating all `text_tokenized` values into a single `combined_text` field, saving to `data/aggregated/news_by_quarter.csv`.
3. THE Data_Aggregator SHALL aggregate prices per (ticker, quarter_id) computing: `avg_close` (mean closing price), `avg_volume` (mean daily volume), `return_intra` ((close_last - close_first) / close_first), and `trading_days` (count of trading days), saving to `data/aggregated/prices_by_quarter.csv`.
4. THE Data_Aggregator SHALL merge the news and price aggregations on (ticker, quarter_id), retaining only rows that have both price and news data, and add a `next_quarter_id` column and the corresponding `next_avg_close` value from the following quarter.
5. THE Data_Aggregator SHALL save the merged master dataset to `data/aggregated/master_dataset.csv`.
6. WHEN aggregation completes, THE Data_Aggregator SHALL report the number of (ticker, quarter) pairs per year, warn for any pair with `news_count` < 5, and warn if the total number of samples is below 300.
7. THE Data_Aggregator SHALL generate and save a coverage heatmap visualization (ticker rows x quarter columns, color intensity = news_count) to `reports/coverage_heatmap.png` to allow visual inspection of news coverage across all tickers and quarters.

---

### Requirement 6: Xây dựng nhãn tăng/giảm

**User Story:** As a researcher, I want to build binary classification labels indicating whether a stock's average price increases in the next quarter, so that I have a target variable for model training.

#### Acceptance Criteria

1. THE Label_Builder SHALL compute `label_basic` for each (ticker, quarter_id) row: 1 if `next_avg_close` > `avg_close`, otherwise 0.
2. THE Label_Builder SHALL compute `return` = (next_avg_close - avg_close) / avg_close and derive `label_threshold`: 1 if return > +0.02, 0 if return < -0.02, NaN if |return| <= 0.02.
3. THE Label_Builder SHALL save both label columns to `data/aggregated/master_with_labels.csv`.
4. WHEN label construction completes, THE Label_Builder SHALL report the overall ratio of label=1 to label=0, the ratio broken down by year, and the ratio broken down by sector using the following Sector_Mapping: Banking (ACB, BID, CTG, HDB, MBB, SHB, SSB, STB, TCB, TPB, VCB, VIB, VPB), Real Estate (BCM, VHM, VIC, VRE), Energy/Resources (GAS, GVR, PLX, POW), Consumer/Food (MWG, SAB, VNM), Industrial (HPG), Finance/Insurance (BVH, SSI), Tech/Telecom (FPT).
5. IF the minority class ratio falls below 35%, THEN THE Label_Builder SHALL emit a class imbalance warning recommending the use of class weighting or threshold adjustment during model training.
6. THE Label_Builder SHALL save a bar chart of label distribution by year and quarter to `reports/label_distribution.png`.

---

### Requirement 7: Trích xuất đặc trưng kỹ thuật

**User Story:** As a researcher, I want to compute technical indicators from daily OHLCV data and aggregate them by quarter, so that I have a structured set of technical features for each (ticker, quarter_id) observation.

#### Acceptance Criteria

1. THE Tech_Feature_Extractor SHALL compute the following daily indicators for each ticker using pandas-ta or ta-lib: RSI with period 14, MACD with parameters (fast=12, slow=26, signal=9) producing MACD line, signal line, and histogram, Bollinger Bands with parameters (period=20, std=2) producing upper, middle, and lower bands, SMA with periods 20 and 50, and EMA with period 20.
2. THE Tech_Feature_Extractor SHALL aggregate daily indicators into quarterly features per (ticker, quarter_id) organized into the following groups: Returns group (return_q: cumulative quarterly return, return_mean_daily: mean daily return, return_std_daily: standard deviation of daily returns), Volatility group (volatility_q: return_std_daily * sqrt(trading_days), price_range_q: (high_max - low_min) / avg_close), Liquidity group (volume_mean_q: mean daily volume, volume_change_q: volume change vs previous quarter), Trend group using end-of-quarter values (sma20_end, ema20_end, price_vs_sma20: (close_last - sma20_end) / sma20_end), Indicator group using quarterly means (rsi_mean_q, rsi_end_q, macd_hist_mean_q, bb_position_q: (close - BB_lower) / (BB_upper - BB_lower)), and Momentum group using lagged values (return_prev_q: lag 1 quarter, return_2q_ago: lag 2 quarters).
3. THE Tech_Feature_Extractor SHALL leave lag features as NaN for the first one or two quarters of each ticker's history rather than imputing them automatically.
4. THE Tech_Feature_Extractor SHALL save the quarterly technical features to `data/features/technical_features.csv` with columns: ticker, quarter_id, and all feature columns.
5. WHEN feature extraction completes, THE Tech_Feature_Extractor SHALL compute and print the correlation matrix of all features, and warn for any feature pair with absolute correlation greater than 0.95.

---

### Requirement 8: Xây dựng danh sách từ khóa tài chính

**User Story:** As a researcher, I want to build a curated list of Vietnamese financial keywords grouped by sentiment direction (positive/negative/neutral), so that I can extract quantitative keyword frequency features from news text.

#### Acceptance Criteria

1. THE Keyword_Builder SHALL analyze the full news corpus using CountVectorizer to extract the top 500 most frequent unigrams and top 300 most frequent bigrams after removing stopwords, saving the candidates to `config/keyword_candidates.csv` for manual review.
2. THE Keyword_Builder SHALL produce a structured keyword list organized into six thematic groups with each keyword assigned a `direction` attribute of "positive", "negative", or "neutral". The complete keyword list SHALL include at minimum the following:
   - Group A (Kết quả kinh doanh): positive: ["lợi nhuận tăng", "doanh thu tăng", "tăng trưởng mạnh", "vượt kế hoạch", "kỷ lục", "tăng trưởng", "lãi ròng", "lợi nhuận sau thuế tăng", "kết quả tích cực"]; negative: ["lợi nhuận giảm", "doanh thu giảm", "lợi nhuận âm", "thua lỗ", "lỗ ròng", "dưới kế hoạch", "sụt giảm", "kết quả tiêu cực", "lợi nhuận thấp hơn"]
   - Group B (Chính sách cổ đông): positive: ["chia cổ tức", "cổ tức cao", "mua lại cổ phiếu", "phát hành thưởng", "tăng vốn điều lệ", "cổ tức tiền mặt"]; negative: ["không chia cổ tức", "hủy cổ tức", "giảm cổ tức", "phát hành pha loãng", "chào bán giá thấp"]
   - Group C (Tài chính doanh nghiệp): positive: ["giảm nợ", "trả nợ", "cải thiện tài chính", "hệ số an toàn vốn", "dòng tiền dương", "tiền mặt dồi dào"]; negative: ["nợ xấu", "nợ vay tăng", "áp lực tài chính", "nợ quá hạn", "hệ số nợ cao", "thiếu thanh khoản", "dòng tiền âm"]
   - Group D (Hoạt động kinh doanh): positive: ["ký kết hợp đồng", "mở rộng thị trường", "dự án mới", "đầu tư mới", "hợp tác chiến lược", "thắng thầu", "xuất khẩu tăng"]; negative: ["hủy hợp đồng", "dự án trì hoãn", "thu hẹp hoạt động", "đóng cửa", "dừng dự án"]
   - Group E (Rủi ro và pháp lý): negative: ["bị phạt", "vi phạm", "bị thanh tra", "bị kiểm toán từ chối", "cảnh báo", "đình chỉ", "khởi tố", "điều tra", "tranh chấp pháp lý", "bị kiện"]
   - Group F (Sự kiện doanh nghiệp trung tính): neutral: ["đại hội cổ đông", "họp HĐQT", "thay đổi lãnh đạo", "thay CEO", "sáp nhập", "mua lại", "phát hành cổ phiếu mới", "niêm yết thêm", "thoái vốn"]
3. THE Keyword_Builder SHALL save the keyword list to `config/keywords_finance.json` with the structure `{"positive": [...], "negative": [...], "neutral": [...]}`.
4. THE Keyword_Builder SHALL also save a group-level breakdown to `config/keywords_by_group.json` organized by groups A through F.
5. WHEN keyword list construction completes, THE Keyword_Builder SHALL print the corpus frequency of each keyword to allow validation that the list is representative of the actual news corpus.

---

### Requirement 9: Trích xuất đặc trưng tần suất từ khóa

**User Story:** As a researcher, I want to extract keyword frequency features (raw count, normalized count, TF-IDF, pos_score, neg_score, sentiment_ratio) for each (ticker, quarter_id), so that I have a quantitative representation of news content to combine with technical features.

#### Acceptance Criteria

1. THE Keyword_Feature_Extractor SHALL compute for each (ticker, quarter_id) and each keyword k: raw count `kw_{k}` (occurrences in combined_text) and normalized count `kw_norm_{k}` (raw count divided by news_count).
2. THE Keyword_Feature_Extractor SHALL compute aggregate sentiment scores: `pos_score` (sum of kw_norm for all positive keywords), `neg_score` (sum of kw_norm for all negative keywords), and `sentiment_ratio` = (pos_score - neg_score) / (pos_score + neg_score + 1e-6).
3. THE Keyword_Feature_Extractor SHALL compute TF-IDF weights for each keyword using `TfidfVectorizer(vocabulary=keyword_list, min_df=2)` fitted on the full corpus of (ticker, quarter) combined texts, saving the result as `tfidf_{k}` columns.
4. THE Keyword_Feature_Extractor SHALL include coverage features: `news_count`, `news_count_log` = log(news_count + 1), and `has_min_news` = 1 if news_count >= 5 else 0.
5. THE Keyword_Feature_Extractor SHALL save all keyword features to `data/features/keyword_features.csv` with columns: ticker, quarter_id, and all feature columns.
6. WHEN feature extraction completes, THE Keyword_Feature_Extractor SHALL report: total number of features generated, top 20 keywords by corpus frequency, overall sparsity rate (percentage of zero-valued keyword-ticker-quarter cells), and distribution statistics for pos_score and neg_score.
7. IF a keyword has a sparsity rate above 95% across all (ticker, quarter) pairs, THEN THE Keyword_Feature_Extractor SHALL log that keyword as a candidate for removal from the keyword list.
8. THE Keyword_Feature_Extractor SHALL handle sparse features appropriately: many keywords having count = 0 is expected behavior and values SHALL be kept as-is (not imputed).

---

### Requirement 10: Huấn luyện và đánh giá mô hình

**User Story:** As a researcher, I want to train and evaluate multiple ML classifiers under three feature configurations (technical only, keyword only, combined) using time-series-aware splitting, so that I can compare model performance and answer the main research hypothesis H1.

#### Acceptance Criteria

1. THE Model_Trainer SHALL merge technical features, keyword features, and labels on (ticker, quarter_id), apply median imputation for NaN values per column, and remove ticker and quarter_id columns before training.
2. THE Model_Trainer SHALL split data using a time-series split: all quarters before 2025-Q1 form the training set, and 2025-Q1 onward (or the last 20% of quarters if fewer than 4 test quarters are available) forms the test set, applied consistently across all tickers with no random shuffling.
3. THE Model_Trainer SHALL train and evaluate models under three feature configurations: Config_A (technical features only), Config_B (keyword features only), and Config_C (technical + keyword features combined).
4. THE Model_Trainer SHALL include two baseline models for each configuration: a majority-class baseline (always predict the most frequent label) and a naive momentum baseline (predict next quarter label = current quarter label).
5. THE Model_Trainer SHALL train four ML algorithms for each configuration with the following hyperparameters: Logistic Regression (C=1.0, class_weight='balanced'), Random Forest (n_estimators=100, class_weight='balanced'), XGBoost (scale_pos_weight = neg_count / pos_count), and LightGBM (is_unbalance=True).
6. THE Model_Trainer SHALL compute for each model-configuration pair: Accuracy, Precision, Recall, F1-macro, AUC-ROC, Balanced Accuracy, and print the confusion matrix.
7. THE Model_Trainer SHALL save a consolidated comparison table to `reports/model_comparison.csv` with rows indexed by model-configuration (e.g., "XGBoost - Config_C") and columns for each metric.
8. WHEN evaluation completes, THE Model_Trainer SHALL highlight the best model by Balanced Accuracy, report the performance delta between Config_A and Config_C for each algorithm, and log a note if Config_C does not improve over Config_A (this is still a valid research finding).
9. THE Model_Trainer SHALL save the best trained model to `models/best_model.pkl`.

---

### Requirement 11: Phân tích SHAP và Feature Importance

**User Story:** As a researcher, I want to analyze feature importance using SHAP values, permutation importance, and tree-based importance for the best Config_C model, so that I can identify which keywords and technical indicators contribute most to predictions and provide empirical evidence for H1.

#### Acceptance Criteria

1. THE SHAP_Analyzer SHALL compute tree-based feature importance (gain-based) for the best XGBoost or LightGBM model from Config_C and plot the top 30 features with distinct colors for technical vs. keyword features, saving to `reports/feature_importance.png`.
2. THE SHAP_Analyzer SHALL compute permutation importance on the test set using `sklearn.inspection.permutation_importance`, plot the top 30 features with the same color scheme, and save to `reports/permutation_importance.png`.
3. THE SHAP_Analyzer SHALL compute SHAP values using `shap.TreeExplainer`, generate a beeswarm summary plot saved to `reports/shap_summary.png`, and a mean absolute SHAP bar plot saved to `reports/shap_bar.png`.
4. THE SHAP_Analyzer SHALL extract SHAP values for keyword features only, identify the top 20 most important keywords, and for each keyword record: direction label (positive/negative/neutral), mean SHAP value, and actual SHAP direction (positive or negative contribution to prediction).
5. THE SHAP_Analyzer SHALL save the top keyword analysis to `reports/top_keywords_analysis.csv` and verify whether positive-direction keywords have positive mean SHAP values, logging any mismatches as anomalies.
6. THE SHAP_Analyzer SHALL compute the total mean absolute SHAP contribution of the technical feature group vs. the keyword feature group, report the percentage share of each group, and save this summary as empirical evidence for H1.
7. WHERE at least 2 (ticker, quarter) pairs are correctly predicted by Config_C but not by Config_A, THE SHAP_Analyzer SHALL generate SHAP waterfall plots for up to 3 such cases and save them to `reports/shap_case_study_{ticker}_{quarter}.png`.

---

### Requirement 12: Đóng gói pipeline bán tự động

**User Story:** As a researcher, I want a semi-automated pipeline runner with argparse CLI, YAML configuration, checkpointing, and structured logging, so that I can reproduce experiments, run individual steps, and update data without re-running the entire pipeline from scratch.

#### Acceptance Criteria

1. THE Pipeline_Runner SHALL provide a CLI entry point at `pipeline/run_pipeline.py` accepting a `--step` argument with valid values: `all`, `data`, `preprocess`, `features`, `train`, and `update_news`.
2. WHEN `--step all` is specified, THE Pipeline_Runner SHALL execute TASK 1 through TASK 11 in sequential order (TASK 12 is the runner itself and is not executed as a step).
3. WHEN `--step data` is specified, THE Pipeline_Runner SHALL execute only TASK 1, TASK 2, and TASK 3.
4. WHEN `--step preprocess` is specified, THE Pipeline_Runner SHALL execute TASK 4 (text preprocessing), TASK 5 (aggregation), and TASK 6 (label building).
5. WHEN `--step features` is specified, THE Pipeline_Runner SHALL execute TASK 4, TASK 5, TASK 6 (preprocessing prerequisites), then TASK 7, TASK 8, and TASK 9 (feature extraction), skipping any step whose checkpoint already exists unless `--force` is provided.
6. WHEN `--step train` is specified, THE Pipeline_Runner SHALL execute only TASK 10 and TASK 11.
7. WHEN `--step update_news` is specified, THE Pipeline_Runner SHALL scrape new articles published since the last run date and update the matched and processed news files incrementally.
8. THE Pipeline_Runner SHALL load all configurable parameters from `config/pipeline_config.yaml`, including: tickers list, start_date, end_date (supporting "auto" to resolve to the current date at runtime), quarter_unit, min_news_per_period, train_cutoff, and label_threshold.
9. WHEN a task's output file already exists, THE Pipeline_Runner SHALL skip that task and log a skip message, unless the `--force` flag is provided.
10. THE Pipeline_Runner SHALL write structured logs for each task execution to `logs/{task_name}_{date}.log`, including: timestamp, input row count, output row count, warnings, and errors.
11. THE Pipeline_Runner SHALL maintain the following directory structure: `config/` (pipeline_config.yaml, keywords_finance.json, keywords_by_group.json, stopwords_finance.txt, entity_aliases.json), `data/prices/`, `data/news/cafef/`, `data/news/vietstock/`, `data/news/tnck/`, `data/news/matched/`, `data/news/processed/`, `data/aggregated/`, `data/features/`, `models/`, `reports/`, `pipeline/` (run_pipeline.py, task1_prices.py through task11_shap.py), `logs/`, and `notebooks/`.
12. IF a task fails with an unhandled exception, THEN THE Pipeline_Runner SHALL log the full stack trace to the task's log file, print a human-readable error summary to stdout, and exit with a non-zero return code without corrupting previously completed task outputs.

---

### Requirement 13: Smoke Test trước khi chạy toàn bộ

**User Story:** As a researcher, I want to run a quick smoke test on a small subset of data before executing the full pipeline, so that I can verify the pipeline works end-to-end and estimate total runtime.

#### Acceptance Criteria

1. THE Pipeline_Runner SHALL support a `--smoke-test` flag that restricts execution to 3 tickers (VNM, VCB, FPT) and 4 quarters (2022Q1 through 2022Q4).
2. WHEN `--smoke-test` is specified, THE Pipeline_Runner SHALL execute all steps (TASK 1 through TASK 11) on the restricted dataset.
3. WHEN the smoke test completes, THE Pipeline_Runner SHALL verify that all key output files exist: `data/prices/all_vn30_prices.csv`, `data/news/matched/all_news_matched.csv`, `data/aggregated/master_with_labels.csv`, `data/features/technical_features.csv`, `data/features/keyword_features.csv`, `models/best_model.pkl`, and `reports/model_comparison.csv`.
4. WHEN the smoke test completes, THE Pipeline_Runner SHALL report the elapsed time per task and total elapsed time to help estimate full pipeline runtime.
5. THE Pipeline_Runner SHALL confirm that vnstock retrieves data successfully, that at least 10 articles per ticker per quarter are scraped from CafeF, and that the pipeline produces no unhandled errors.