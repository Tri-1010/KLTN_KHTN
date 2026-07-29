# Tổng hợp phương pháp, thực nghiệm và kết quả để trao đổi với giảng viên

## 0. Kết luận điều hành

Dự án đã thử nhiều hướng biểu diễn dữ liệu giá và tin tức cho bài toán dự báo xu hướng cổ phiếu Việt Nam. Kết quả hiện tại cho thấy:

1. **Technical ML** là nguồn tín hiệu định lượng mạnh nhất và ổn định nhất.
2. **Keyword/news features** không cải thiện dự báo ổn định so với technical-only baseline, dù đã mở rộng nguồn tin, dùng full text, xử lý phủ định và thử nhiều granularity.
3. **Sentiment nâng cao** gồm LLM sentiment A6 và distant supervision B1 không cải thiện forecast ở cấp quý.
4. **PhoBERT A5** có thiết kế/code tạo embedding, nhưng chưa thấy report/output kết quả chính trong repo; nếu muốn nói đã dùng trong luận văn cần chạy/xác nhận lại.
5. **LLM semantic features** có tín hiệu cục bộ trong vài cấu hình material-event/horizon, nhưng kết quả mixed, chưa đủ robust để làm main claim forecast.
6. **Decision-support prototype** là hướng bảo vệ tốt nhất: ML làm lõi định lượng, news/LLM làm evidence và decision-card layer, monitoring/outcome review làm hậu kiểm.

Câu trao đổi với giảng viên:

> Em đã kiểm thử từ baseline kỹ thuật, keyword, sentiment, distant supervision đến LLM semantic. Kết quả cho thấy tin tức khi ép thành feature dự báo trực tiếp không cải thiện ổn định. Vì vậy em đề xuất pivot: giữ ML kỹ thuật làm lõi dự báo/xếp hạng, dùng tin tức và LLM làm lớp bằng chứng, giải thích, monitoring và hậu kiểm quyết định.

---

## 1. Pipeline dữ liệu nền

### 1.1. Dữ liệu giá

- Dữ liệu OHLCV ngày.
- Tạo technical features theo kỳ.
- Tạo nhãn xu hướng tăng/không tăng cho kỳ kế tiếp.
- Đơn vị chính: quý; có thử tuần, 2 tuần, tháng, 2 tháng.
- Universe:
  - VN30 ban đầu.
  - HOSE-80 mở rộng.
  - HOSE+HNX-125 robustness.

### 1.2. Dữ liệu tin tức

Nguồn tin đã dùng/mở rộng:

- CafeF
- Vietstock
- Tinnhanhchungkhoan
- VietnamBiz
- VnExpress
- Kinh Tế Chứng Khoán

Quá trình mở rộng corpus:

- Ban đầu khoảng 7.5k–9.7k bài.
- Mở rộng lên 11k, 17.8k, 19.5k.
- Cuối cùng khoảng 28k bài, 6 nguồn cân bằng hơn.
- Sau full-text enrichment: gần như đầy đủ full text với coverage 99.96% unique URLs.

Ý nghĩa:

> Kết quả âm của keyword/news không phải vì thiếu dữ liệu nguồn hoặc chỉ dùng tiêu đề ngắn. Đã thử nhiều nguồn và gần như full text nhưng news-as-keyword vẫn không cải thiện forecast.

---

## 2. Phương pháp 1 — Technical ML baseline / Config_A

### 2.1. Mục tiêu

Kiểm tra xem đặc trưng kỹ thuật từ giá/khối lượng có tạo được tín hiệu dự báo xu hướng tăng/không tăng kỳ kế tiếp hay không.

### 2.2. Feature

Nhóm technical features gồm:

- return_q
- return_prev_q
- return_2q_ago
- return_mean_daily
- return_std_daily
- volatility_q
- price_range_q
- volume_mean_q
- volume_change_q
- sma20_end
- ema20_end
- price_vs_sma20
- rsi_mean_q
- rsi_end_q
- macd_hist_mean_q
- bb_position_q

### 2.3. Mô hình

- Logistic Regression
- Random Forest
- XGBoost
- LightGBM

### 2.4. Đánh giá

- Balanced Accuracy
- AUC-ROC
- F1 Macro
- Precision/Recall
- Backtest long-only
- Walk-forward
- Robustness test
- Leakage audit

### 2.5. Kết quả chính

Từ `reports/technical_ml_backtest_report.md`:

- Model net cumulative return: **0.602964** (~60.3%)
- Buy-hold/equal-weight return: **0.253502** (~25.4%)
- Net Sharpe: **1.05171**
- Hit rate: **0.8**
- Walk-forward thắng benchmark: **3/3 cutoff**

Walk-forward:

| Cutoff | n_test | BA | AUC | Model net return | Buy-hold return |
|---|---:|---:|---:|---:|---:|
| 2024Q3 | 556 | 0.7229 | 0.7970 | 0.6563 | 0.2818 |
| 2025Q1 | 400 | 0.7599 | 0.8235 | 0.6030 | 0.2535 |
| 2025Q3 | 240 | 0.6400 | 0.7098 | 0.1182 | 0.0072 |

Robustness 125 mã HOSE+HNX:

| Model | BA | AUC | F1 Macro | n_test |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.6488 | 0.7036 | 0.6438 | 735 |
| Random Forest | **0.7607** | **0.8307** | **0.7573** | 735 |
| XGBoost | 0.7531 | 0.8265 | 0.7502 | 735 |
| LightGBM | 0.7530 | 0.8198 | 0.7509 | 735 |

### 2.6. Leakage audit

Kết luận: **PASS**.

- 16 technical features kiểm tra.
- 14 in-period, 2 past, 0 future.
- Không có cột return/label tương lai trong feature set.
- Không feature nào có |corr| với label > 0.95.

### 2.7. Ý nghĩa

Technical ML là phần mạnh nhất.

Cách nói với giảng viên:

> Phần kỹ thuật tạo tín hiệu định lượng tốt và có kiểm tra leakage. Tuy nhiên em không claim đây là chiến lược đầu tư triển khai thật vì backtest còn theo kỳ, chưa mô phỏng đầy đủ slippage/liquidity/T+2/daily mark-to-market.

---

## 3. Phương pháp 2 — Keyword/news features baseline / Config_B, Config_C

### 3.1. Mục tiêu

Kiểm tra H1:

> Bổ sung đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt có cải thiện dự báo xu hướng giá so với chỉ dùng technical features không?

### 3.2. Thiết kế

- Config_A: technical-only.
- Config_B: keyword/news-only.
- Config_C: technical + keyword/news.

Keyword set curated gồm 106 cụm từ:

- 43 positive.
- 54 negative.
- 9 neutral.

Feature sinh ra:

- raw counts: `kw_*`
- normalized counts: `kw_norm_*`
- TF-IDF-like: `tfidf_*`
- aggregate: `pos_score`, `neg_score`, `sentiment_ratio`, `news_count_log`, `has_min_news`

### 3.3. Kết quả ban đầu VN30/quý

Từ `reports/H1_experiment_report.md`:

| Model | Config_A | Config_B | Config_C | C−A |
|---|---:|---:|---:|---:|
| Random Forest | **0.776** | 0.470 | 0.747 | -0.029 |
| XGBoost | 0.730 | 0.548 | 0.735 | +0.005 |
| LightGBM | 0.723 | 0.498 | 0.721 | -0.002 |
| Logistic Regression | 0.725 | 0.509 | 0.697 | -0.028 |

Kết luận: Config_B gần random; Config_C không cải thiện so với Config_A.

### 3.4. Nhiều cutoff thời gian

Delta trung bình C−A qua 5 cutoff:

| Cutoff | Delta trung bình |
|---|---:|
| 2024Q1 | -0.0004 |
| 2024Q3 | -0.0131 |
| 2025Q1 | -0.0130 |
| 2025Q3 | -0.0425 |
| 2026Q1 | -0.0425 |

Kết luận: H1 không được ủng hộ qua nhiều cách chia thời gian.

### 3.5. Nhiều granularity

Sau full-text enrichment:

| Đơn vị | n_samples | n_test | Mean Δ(C−A) |
|---|---:|---:|---:|
| 1 tuần | 10,788 | 2,764 | -0.0068 |
| 2 tuần | 7,090 | 1,660 | -0.0071 |
| 1 tháng | 3,815 | 785 | -0.0032 |
| 2 tháng | 2,042 | 400 | -0.0112 |
| Quý | 1,348 | 240 | +0.0094 |

Kết luận: 4/5 granularity âm; quý dương nhỏ nhưng không ổn định.

### 3.6. Mở rộng nguồn tin

Đã mở rộng corpus 5 lần:

- thêm VietnamBiz;
- đào sâu Vietstock;
- thêm VnExpress;
- thêm Kinh Tế Chứng Khoán;
- cân bằng 6 nguồn, corpus ~28k bài.

Kết quả cuối:

- McNemar RF tháng cuối: p = **0.430**, không significant.
- Không nguồn nào áp đảo quá 30%.
- Config_C vẫn không cải thiện.

### 3.7. Cải tiến đếm keyword

Cải tiến:

- xử lý phủ định;
- thêm từ đồng nghĩa;
- longest-first masking để tránh đếm trùng cụm con.

Kết quả sau cải tiến:

| Đơn vị | Delta sau cải tiến |
|---|---:|
| 2 tuần | -0.0143 |
| 1 tháng | -0.0087 |
| 2 tháng | +0.0047 |
| Quý | -0.0381 |

Một số cải thiện nhỏ ở 1–2 tháng, nhưng không nhất quán và không significant.

### 3.8. Full-text enrichment

Full text coverage gần đầy đủ:

- 45,949 / 45,968 unique URLs có full text.
- Coverage 99.96%.
- Average token/article ~714.8.

Kết quả quý production split sau full text:

| Model | Config_A | Config_B | Config_C | C−A |
|---|---:|---:|---:|---:|
| LightGBM | **0.7599** | 0.4510 | 0.7357 | -0.0242 |
| Logistic Regression | 0.7269 | 0.4999 | 0.7132 | -0.0138 |
| Random Forest | 0.7351 | 0.5053 | 0.6679 | -0.0672 |
| XGBoost | 0.7293 | 0.4792 | 0.7238 | -0.0055 |

Random Forest 1 tháng sau full text: Config_C tệ hơn Config_A có ý nghĩa, p = **0.0227**.

### 3.9. Kết luận keyword/news baseline

> Keyword/frequency features không cải thiện forecast ổn định, dù đã mở rộng corpus, thêm nguồn, dùng full text và cải tiến đếm.

Cách trao đổi:

> Em đã loại trừ các phản biện dễ nhất: không phải thiếu nguồn, không phải chỉ dùng title, không phải keyword list quá sơ sài, không phải chỉ một cutoff. Kết quả âm khá robust.

---

## 4. Phương pháp 3 — H2 keyword significance

### 4.1. Mục tiêu

Kiểm tra H2:

> Một số keyword riêng lẻ có liên hệ thống kê với nhãn tăng/không tăng không?

### 4.2. Kiểm định

Dùng:

- Chi-square / Fisher exact test.
- Mann-Whitney U test.
- Logistic regression đơn biến.
- Hiệu chỉnh đa kiểm định BH-FDR.

### 4.3. Kết quả

| Dataset | Rows | KW tested | Raw p<0.05 | Significant after BH |
|---|---:|---:|---:|---:|
| VN30 quý | 510 | 62 | 3 | 0 |
| VN30 tháng | 1,541 | 64 | 0 | 0 |
| HOSE-80 quý | 1,348 | 71 | 5 | 0 |

Top raw p-value có lặp lại:

- `chia cổ tức`
- `nợ xấu`
- `giảm mạnh`
- `đại hội cổ đông`
- `không chia cổ tức`

Nhưng sau BH-FDR: **0 keyword significant**.

### 4.4. Ý nghĩa

Không có keyword nào đủ mạnh về mặt thống kê sau hiệu chỉnh nhiều kiểm định.

Cách trao đổi:

> Có vài từ có tín hiệu raw, nhưng không vượt correction. Em không nên claim keyword nào thật sự có ý nghĩa thống kê; chỉ xem là gợi ý exploratory.

---

## 5. Phương pháp 4 — H3 SHAP / keyword contribution

### 5.1. Mục tiêu

Kiểm tra H3:

> Dù keyword không cải thiện forecast, mô hình có sử dụng keyword trong Config_C không?

### 5.2. Cách làm

- Huấn luyện Random Forest Config_C.
- Tính SHAP TreeExplainer.
- Tính permutation importance.
- Xếp keyword theo mean(|SHAP|).
- Kiểm tra direction consistency.

### 5.3. Kết quả

- Tổng keyword features xếp hạng: 318.
- Direction consistent: 80/318 (~25.2%).
- SHAP contribution:
  - technical ~68.1%.
  - keyword ~31.9%.

Top keyword theo SHAP:

- tăng trưởng
- nợ xấu
- báo lãi
- chia cổ tức
- tăng vốn điều lệ

### 5.4. Ý nghĩa

Mô hình có dùng keyword, nhưng dùng không đủ ổn định để cải thiện performance out-of-sample.

Cách trao đổi:

> SHAP cho thấy keyword có được mô hình khai thác, nhưng direction consistency thấp và BA không tăng. Do đó SHAP chỉ hỗ trợ phần giải thích, không chứng minh keyword có predictive power thật.

---

## 6. Phương pháp 5 — A6 LLM sentiment

### 6.1. Mục tiêu

Thay keyword sentiment thủ công bằng LLM sentiment.

### 6.2. Cách làm

- Dùng Gemini Flash.
- Prompt chỉ yêu cầu đánh giá polarity nội dung bài viết.
- Cấm mô hình dự đoán giá.
- Temperature = 0.
- Tổng hợp theo `(ticker, period)` thành:
  - `llm_pos_ratio`
  - `llm_neg_ratio`
  - `llm_net_sentiment`
- Ghi feature ra `keyword_features_A6.csv`.

### 6.3. Kết quả

Từ `reports/experiment_A6_report.md`:

| Model | Config_A | Config_C A6 | Δ(C−A) |
|---|---:|---:|---:|
| LightGBM | 0.7599 | 0.7461 | -0.0138 |
| Random Forest | 0.7351 | 0.7337 | -0.0014 |
| XGBoost | 0.7293 | 0.7411 | +0.0118 |
| Logistic Regression | 0.7269 | 0.7059 | -0.0211 |

Tổng hợp:

- Mean Δ(C−A): **-0.0061**.
- McNemar p: **0.6177**.
- Không significant.

### 6.4. Ý nghĩa

LLM sentiment không cải thiện forecast ở cấp quý.

Cách trao đổi:

> Em đã thử thay keyword sentiment bằng LLM sentiment. Kết quả vẫn gần 0 và không significant. Điều này cho thấy vấn đề không chỉ do keyword thô, mà có thể do aggregation theo kỳ hoặc tin tức đã phản ánh nhanh vào giá.

---

## 7. Phương pháp 6 — B1 Distant Supervision cấp bài viết

### 7.1. Mục tiêu

Kiểm tra giả thuyết:

> Tín hiệu news có thể tồn tại ở cấp bài viết/ngắn hạn, nhưng bị làm mờ khi tổng hợp theo quý.

### 7.2. Cách làm

- Tạo noisy label cho mỗi bài bằng return cửa sổ [d+1, d+3] ngày giao dịch.
- Ngưỡng ±2%:
  - positive;
  - neutral;
  - negative.
- Train classifier cấp bài viết.
- Lấy xác suất dự đoán và tổng hợp lên quý thành:
  - `ds_pos_prob_mean`
  - `ds_net_sentiment`

### 7.3. Kết quả cấp bài

Từ `reports/distant_supervision_report.md`:

| Label | Số bài | Tỷ lệ |
|---|---:|---:|
| negative | 6,789 | 23.8% |
| neutral | 14,495 | 50.8% |
| positive | 7,235 | 25.4% |
| tổng | 28,519 | 100% |

- Số bài train classifier: 14,016.
- Số bài bị loại: 6,447.
- AUC macro one-vs-rest cấp bài: **0.6797**.

### 7.4. Kết quả khi gộp lên quý

Từ `reports/experiment_B1_report.md`:

| Model | Config_A | Config_C B1 | Δ(C−A) |
|---|---:|---:|---:|
| LightGBM | 0.7599 | 0.7485 | -0.0114 |
| Random Forest | 0.7351 | 0.7380 | +0.0029 |
| XGBoost | 0.7293 | 0.7480 | +0.0187 |
| Logistic Regression | 0.7269 | 0.7274 | +0.0005 |

Tổng hợp:

- Mean Δ(C−A): **+0.0027**.
- McNemar p: **0.5601**.
- Không significant.

### 7.5. Ý nghĩa

Có tín hiệu yếu ở cấp bài viết, nhưng tan biến khi tổng hợp lên quý.

Cách trao đổi:

> B1 là kết quả quan trọng: article-level AUC 0.68 chứng tỏ không phải news hoàn toàn vô dụng. Nhưng khi aggregate theo quý, tín hiệu biến mất. Điều này ủng hộ hướng event-time/daily/weekly hoặc monitoring, không phải quarter-level predictor.

---

## 8. Phương pháp 7 — B3 segmentation theo ngành/vốn hóa

### 8.1. Mục tiêu

Kiểm tra H3 mở rộng:

> Text signal có thể bị pha loãng toàn thị trường, nhưng mạnh ở một số ngành hoặc nhóm vốn hóa?

### 8.2. Cách làm

- Chia theo sector.
- Chia theo cap group: large_cap, mid_cap.
- Huấn luyện lại Config_A/B/C trong từng phân khúc.
- Kiểm định keyword trong từng phân khúc.

### 8.3. Kết quả tổng hợp

Từ `reports/phan_tich_ket_qua_va_dinh_huong.md`:

| Phân khúc | n_samples | mean Δ(C−A) | Đánh giá |
|---|---:|---:|---|
| Banking | 425 | -0.0447 | Âm |
| Consumer | 170 | -0.0400 | Âm |
| Energy | 131 | -0.0250 | Âm |
| Industrial | 168 | -0.0848 | Âm |
| RealEstate | 220 | +0.0063 | Gần 0 |
| Securities | 101 | -0.0250 | Âm |
| Technology | 51 | -0.0208 | n nhỏ |
| Transport | 82 | +0.0414 | n nhỏ |
| large_cap | 510 | -0.0217 | Âm, power cao |
| mid_cap | 838 | -0.0187 | Âm, power cao |

### 8.4. Ý nghĩa

Không tìm thấy phân khúc có tín hiệu văn bản vững. Các phân khúc dương có sample nhỏ và không nhất quán giữa thuật toán.

Cách trao đổi:

> Em đã kiểm tra xem text signal có bị pha loãng khi gộp toàn thị trường không. Kết quả là không có phân khúc mạnh thật sự; nhóm có power cao vẫn âm. Điều này củng cố kết luận news-as-feature yếu.

---

## 9. Phương pháp 8 — A5 PhoBERT embeddings

### 9.1. Mục tiêu

Dùng PhoBERT để tạo dense semantic embeddings cho văn bản tiếng Việt, thay vì keyword count.

### 9.2. Cách làm theo code hiện có

File: `experiments/a5_embeddings.py`

- Model: `vinai/phobert-base`.
- Input: `combined_text` của mỗi `(ticker, quarter_id)` từ `news_by_quarter.csv`.
- Mean-pooling last hidden state.
- Output: 768 chiều:
  - `emb_0`
  - `emb_1`
  - ...
  - `emb_767`
- Merge với v0 keyword frame.
- Output dự kiến: `data/features/keyword_features_A5.csv`.

### 9.3. Trạng thái kết quả

Trong repo hiện tại:

- Có spec và code A5.
- Có tests cho A5.
- Chưa thấy file output/report chính như `keyword_features_A5.csv` hoặc `experiment_A5_report.md`.

### 9.4. Kết luận an toàn

Không nên nói PhoBERT đã chạy và không hiệu quả nếu chưa có report.

Cách nói với giảng viên:

> Em có thiết kế và code cho hướng PhoBERT embedding A5, dùng `vinai/phobert-base` để tạo vector 768 chiều cho văn bản theo ticker-quarter. Tuy nhiên hiện em chưa tìm thấy báo cáo kết quả A5 hoàn chỉnh trong repo, nên nếu muốn đưa vào luận văn như thực nghiệm đã làm, em cần chạy/xác nhận lại. Nếu không, nên để PhoBERT ở phần hướng mở rộng/baseline cần bổ sung.

---

## 10. Phương pháp 9 — A7 / LLM scorecard / DeepSeek pilot

### 10.1. Mục tiêu

Dùng LLM để tạo scorecard/semantic features giàu hơn sentiment đơn giản.

### 10.2. Biến thể đã có

- A7 pilot500.
- A7 pilot500 DeepSeek.
- LLM scorecard prompt packs.
- Annotated CSV trong `data/news/annotated/`.

### 10.3. Kết quả tổng hợp đã đọc trước đó

- A7 pilot500 mean Δ(C−A): khoảng **-0.0046**, p khoảng **0.1770**.
- A7 DeepSeek mean Δ(C−A): khoảng **-0.0081**, p khoảng **0.6989**.

### 10.4. Ý nghĩa

Pilot LLM scorecard chưa cải thiện forecast tổng quát.

Cách trao đổi:

> A7 cho thấy việc dùng LLM để chấm semantic/sentiment vẫn chưa tự động tạo forecast gain khi aggregate theo kỳ. Đây là lý do em không đặt LLM-as-feature làm claim chính.

---

## 11. Phương pháp 10 — LLM semantic material/event features

### 11.1. Mục tiêu

Không chỉ sentiment, mà trích xuất:

- event type;
- materiality;
- relevance to ticker;
- sentiment;
- information magnitude;
- novelty hint.

### 11.2. Kết quả tổng hợp

Các reports `llm_semantic_*summary.md` cho thấy:

Positive local evidence:

- Material-event RF: Δ khoảng +0.0318, p_mid ~0.0109.
- Direct material 10d RF: Δ khoảng +0.0310, p_mid ~0.0211.
- VN30 material expansion 60d RF: Δ khoảng +0.0293, p_mid ~0.0000.
- Một số config HOSE100 plus_macro_market cũng dương +0.02 đến +0.04.

Mixed/negative evidence:

- Mean delta toàn sweep gần 0.
- HOSE100 mean delta khoảng +0.0007.
- Nhiều config âm hoặc negative significant.
- Kết quả phụ thuộc horizon, model, event filter, universe.
- Rủi ro multiple testing/cherry-pick.

### 11.3. Ý nghĩa

LLM semantic features có tín hiệu có điều kiện, nhưng chưa robust.

Cách trao đổi:

> Đây là hướng có tiềm năng và có novelty, nhưng hiện chưa đủ để làm kết luận chính. Em nên trình bày là exploratory: một số cấu hình material-event có tín hiệu, nhưng chưa ổn định qua sweep. Cần preregister primary config, correction, holdout và human-labeled validation nếu muốn claim mạnh.

---

## 12. Phương pháp 11 — Decision-support prototype

### 12.1. Mục tiêu

Chuyển từ forecast output sang decision-support artifact.

Quy trình:

**select → explain → monitor → update → review**

### 12.2. Components

1. ML Signal Engine.
2. Evidence Pack Builder.
3. Rule-based Decision Cards.
4. LLM Decision Cards.
5. Monitoring Events.
6. Outcome Reviews.
7. Rubric Scoring.

### 12.3. Artifact hiện có

Từ `reports/decision_support/generated/generated_summary.md` và `validation_consistency_check.md`:

| Artifact | Số lượng |
|---|---:|
| Evidence packs | 25 |
| Prompt-safe full-evidence packs | 25 |
| ML-only packs | 25 |
| Rule-based cards | 25 |
| LLM ML-only cards | 25 |
| LLM full-evidence cards | 25 |
| Rubric scores | 75 |
| Monitoring news events | 3,838 |
| Positive realized returns | 19 |
| Negative/neutral realized returns | 6 |

### 12.4. LLM generation

- Provider: Gemini.
- Model: `gemini-2.5-pro`.
- Variants: `ml_only`, `full_evidence`.
- Generated cards: 50.
- Failures: 0.
- Outcome removed from prompt: true.

### 12.5. Rubric results

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LLM full-evidence | 25 | 5.00 | 5.00 | 5.00 | 4.96 | 5.00 | 5.00 | 5.00 | 0 | 0 |
| LLM ML-only | 25 | 1.28 | 1.00 | 4.72 | 2.04 | 4.56 | 2.12 | 1.16 | 43 | 114 |
| Rule-based baseline | 25 | 4.56 | 4.88 | 4.60 | 4.56 | 5.00 | 4.12 | 4.32 | 2 | 15 |

### 12.6. Ý nghĩa

Full-evidence LLM cards tốt hơn về chất lượng trình bày quyết định, nhưng không chứng minh cải thiện lợi nhuận.

Cách trao đổi:

> Decision-support là hướng mạnh nhất. Nó dùng kết quả âm của news-as-predictor để biện minh rằng news nên làm evidence layer. LLM tạo decision card có kiểm soát từ evidence pack, giúp người dùng hiểu ML signal, rủi ro, trigger theo dõi và outcome review.

---

## 13. Bảng tổng hợp toàn bộ phương pháp

| # | Phương pháp | Mục tiêu | Kết quả | Verdict |
|---:|---|---|---|---|
| 1 | Technical ML / Config_A | Dự báo xu hướng từ giá/kỹ thuật | BA ~0.76, AUC ~0.83, backtest tốt | Mạnh nhất, làm lõi định lượng |
| 2 | Keyword baseline / Config_B,C | Test news keyword có cải thiện forecast không | C không vượt A, B gần random | Negative finding robust |
| 3 | H2 keyword significance | Keyword riêng lẻ có liên hệ thống kê không | 0 keyword qua BH-FDR | Không ủng hộ H2 |
| 4 | H3 SHAP keyword | Model có dùng keyword không | Keyword ~32% SHAP nhưng BA không tăng | Ủng hộ một phần, chỉ giải thích |
| 5 | A6 LLM sentiment | LLM gán sentiment bài viết | Δ=-0.0061, p=0.6177 | Không hiệu quả forecast |
| 6 | B1 distant supervision | Article-level noisy label | AUC 0.6797 cấp bài, quý Δ=+0.0027 | Có tín hiệu ngắn hạn yếu, mất khi aggregate |
| 7 | B3 segmentation | Tìm ngành/cap có text signal | Nhóm power cao đều âm | Không tìm thấy tín hiệu có điều kiện vững |
| 8 | A5 PhoBERT | Dense embedding tiếng Việt | Có code/spec, chưa thấy report chính | Cần chạy/xác nhận hoặc để future work |
| 9 | A7 LLM scorecard | Semantic/sentiment pilot | Δ âm/không significant | Không đủ làm claim forecast |
| 10 | LLM semantic material/event | Event/materiality/relevance | Một số config dương, sweep mixed | Exploratory, có tiềm năng |
| 11 | Decision support | Evidence card + monitoring + review | 25 packs, 75 scores, LLM full-evidence overall 5.00 | Hướng bảo vệ tốt nhất |

---

## 14. Narrative nên trao đổi với giảng viên

### 14.1. Cách kể ngắn

> Em bắt đầu từ bài toán dự báo xu hướng cổ phiếu bằng technical features và news features. Technical ML cho kết quả tốt và robust. Sau đó em thử nhiều cách biểu diễn news: keyword, sentiment ratio, LLM sentiment, distant supervision, segmentation, LLM semantic. Kết quả cho thấy news khi ép thành predictor không cải thiện ổn định. Vì vậy em đề xuất pivot: ML làm lõi định lượng, news/LLM làm evidence và decision-support layer. Hệ thống sinh decision card, monitoring events và outcome review để quản trị vòng đời quyết định.

### 14.2. Cách kể có tính học thuật

> Kết quả âm của news-as-feature không phải thất bại, mà là đóng góp empirical. Nó cho thấy trong setting dữ liệu tiếng Việt và bài toán theo kỳ, keyword/sentiment features không tạo incremental predictive value so với technical baseline. Từ đó, luận văn đề xuất cách dùng news thực tế hơn: evidence-grounded decision support, thay vì alpha predictor.

### 14.3. Câu tránh overclaim

Không nói:

- LLM dự báo cổ phiếu tốt hơn.
- News tạo alpha ổn định.
- Decision card cải thiện return.
- PhoBERT đã không hiệu quả nếu chưa có result.

Nên nói:

- Technical ML là lõi định lượng.
- Keyword/news trực tiếp không cải thiện forecast ổn định.
- LLM semantic có tín hiệu exploratory nhưng chưa robust.
- LLM full-evidence cards cải thiện chất lượng decision-support theo rubric.
- Cần thêm human validation nếu muốn dùng LLM labels làm feature chính.

---

## 15. Đề xuất hướng làm tiếp

### Ưu tiên 1 — Hoàn thiện narrative luận văn

- Đặt tên theo ML-led decision support.
- Đưa negative findings thành đóng góp.
- Đưa LLM semantic vào exploratory/future work.
- Đưa decision cards/rubric vào đóng góp ứng dụng.

### Ưu tiên 2 — Nếu muốn làm mạnh phần NLP

- Chạy/xác nhận PhoBERT A5 nếu muốn nói đã dùng.
- Tạo human-labeled set 100–300 bài.
- So sánh keyword vs PhoBERT/XLM-R vs LLM.
- Báo macro-F1 cho relevance/materiality/sentiment.

### Ưu tiên 3 — Nếu muốn làm mạnh phần tài chính

- Thêm random Top-K benchmark.
- Thêm momentum/RSI/MACD rule benchmark.
- Calibration probability.
- Daily mark-to-market backtest.
- Slippage/liquidity/T+2 sensitivity.

### Ưu tiên 4 — Nếu muốn làm mạnh decision-support

- Chọn 3–5 case study sạch.
- Audit content-level leakage cho các case.
- Human review decision cards.
- So sánh rule-based vs LLM full-evidence bằng human preference.

---

## 16. Kết luận cuối cho buổi trao đổi

Hướng nên đề xuất với giảng viên:

> Giữ technical ML làm lõi định lượng, dùng negative results của keyword/sentiment/distant supervision để chứng minh news-as-predictor yếu, sau đó pivot sang ML-led decision support. LLM không đóng vai trò dự báo giá, mà tạo decision card có kiểm soát từ evidence pack. Đây là hướng vừa trung thực với kết quả, vừa có novelty và ý nghĩa thực tiễn.

Nếu giảng viên muốn nhấn LLM/news feature:

> Có thể nói LLM semantic là hướng mở rộng có tiềm năng, nhưng cần human labels, baseline PhoBERT/XLM-R, correction multiple testing và event-time evaluation trước khi làm claim chính.
