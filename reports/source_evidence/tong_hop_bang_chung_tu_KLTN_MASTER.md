# Tổng hợp bằng chứng đã trích từ KLTN_MASTER

Tài liệu này gom các kết quả cần giữ lại từ `KLTN_MASTER` để bản luận văn mới trong `KLTN_KHTN` không phụ thuộc vào thư mục cũ. Các file nguồn cũ chỉ dùng để đối chiếu trong quá trình chuyển đổi; có thể xóa `KLTN_MASTER` sau khi kiểm tra bản mới.

---

## 1. Kết quả ML kỹ thuật làm lõi định lượng

Nguồn cũ: `KLTN_MASTER/reports/technical_ml_backtest_report.md`, `KLTN_MASTER/reports/robustness_extended_tickers_report.md`.

### 1.1. Backtest HOSE-80

Bảng kết quả chính:

| strategy | cost_scenario | cumulative_return | mean_period_return | std_period_return | sharpe_ratio | max_drawdown | hit_rate | total_cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| model | gross | 0.620698 | 0.104646 | 0.0969415 | 1.07947 | 0 | 1 | 0 |
| model | net | 0.602964 | 0.102254 | 0.0972263 | 1.05171 | -0.00103525 | 0.8 | 0.0119571 |
| buy_hold_equal | gross | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |
| buy_hold_equal | net | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |
| equal_weight_rebalanced | gross | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |
| equal_weight_rebalanced | net | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |

Kết luận dùng trong luận văn:

- Chiến lược mô hình net return khoảng **60,3%**.
- Buy-and-hold/equal-weight benchmark khoảng **25,4%**.
- Sharpe ratio net của mô hình khoảng **1,05**.
- Mô hình vượt benchmark trong phạm vi giả định backtest.

### 1.2. Walk-forward stability

| cutoff | n_test | balanced_accuracy | auc_roc | strategy_cumulative_return_net | buy_hold_cumulative_return |
|---|---:|---:|---:|---:|---:|
| 2024Q3 | 556 | 0.722948 | 0.796966 | 0.656316 | 0.281762 |
| 2025Q1 | 400 | 0.7599 | 0.823509 | 0.602964 | 0.253502 |
| 2025Q3 | 240 | 0.639988 | 0.709755 | 0.118227 | 0.00719634 |

Kết luận dùng trong luận văn:

- Balanced Accuracy trung bình khoảng **0,7076**.
- Lợi nhuận tích lũy net của chiến lược mô hình dương ở **3/3 cutoff**.
- Chiến lược mô hình vượt buy-and-hold ở **3/3 cutoff**.

### 1.3. SHAP/feature importance kỹ thuật

Top technical drivers theo báo cáo cũ:

| rank | feature | mean_abs_shap | permutation_importance |
|---:|---|---:|---:|
| 1 | rsi_end_q | 1.67288 | 0.186028 |
| 2 | macd_hist_mean_q | 0.50877 | 0.0192105 |
| 3 | price_vs_sma20 | 0.446245 | 0.00300752 |
| 4 | return_2q_ago | 0.413385 | 0.00483709 |
| 5 | return_q | 0.322035 | 0.0128195 |
| 6 | return_prev_q | 0.305401 | 0.0148371 |
| 7 | volume_change_q | 0.283926 | 0.0107644 |
| 8 | return_mean_daily | 0.280323 | 0.00922306 |
| 9 | price_range_q | 0.265953 | 0.00533835 |
| 10 | sma20_end | 0.256022 | 0.0172055 |

Kết luận dùng trong luận văn:

- ML signal có thể giải thích bằng technical drivers.
- Các driver này đưa vào evidence pack để LLM tạo decision card.

### 1.4. Robustness trên 125 mã HOSE+HNX

| Mô hình | Balanced Acc | AUC-ROC | F1 Macro | n_train | n_test |
|---|---:|---:|---:|---:|---:|
| Baseline_Majority | 0.5000 | 0.5000 | 0.2973 | 1653 | 735 |
| Baseline_Stratified | 0.5223 | 0.5223 | 0.5186 | 1653 | 735 |
| Logistic_Regression | 0.6488 | 0.7036 | 0.6438 | 1653 | 735 |
| Random_Forest | 0.7607 | 0.8307 | 0.7573 | 1653 | 735 |
| XGBoost | 0.7531 | 0.8265 | 0.7502 | 1653 | 735 |
| LightGBM | 0.7530 | 0.8198 | 0.7509 | 1653 | 735 |

Benchmark VNINDEX trong robustness report:

| Chiến lược | Lợi nhuận tích lũy | Return TB/quý | Sharpe | Hit Rate |
|---|---:|---:|---:|---:|
| Mô hình Random Forest | 0.5746 | 0.0816 | 1.00 | 83.3% |
| VNINDEX buy-and-hold | 0.4212 | 0.0634 | — | — |

Kết luận dùng trong luận văn:

- Mở rộng universe lên 125 mã vẫn giữ BA khoảng **0,761** và AUC khoảng **0,831**.
- Mô hình vượt VNINDEX khoảng **15,3 điểm phần trăm** trong cùng giai đoạn test.
- Đây là bằng chứng giảm rủi ro overfit vào HOSE-80.

---

## 2. Leakage audit

Nguồn cũ: `KLTN_MASTER/reports/leakage_audit.md`.

Kết luận tổng thể: **PASS**.

Thông số:

- Feature file: `data/features/technical_features.csv`.
- Label file: `data/aggregated/master_with_labels.csv`.
- Train cutoff: `2025Q1`.
- Correlation threshold: `0.95`.
- Số feature kỹ thuật kiểm tra: **16**.
- Số hàng sau merge: **1428**.

Phân loại cửa sổ thời gian:

| Nhóm | Số lượng |
|---|---:|
| in-period | 14 |
| past | 2 |
| future | 0 |

Các feature in-period/past:

- `return_q`, `return_mean_daily`, `return_std_daily`, `volatility_q`, `price_range_q`, `volume_mean_q`, `volume_change_q`, `sma20_end`, `ema20_end`, `price_vs_sma20`, `rsi_mean_q`, `rsi_end_q`, `macd_hist_mean_q`, `bb_position_q`.
- `return_prev_q`, `return_2q_ago` là past.

Kiểm tra nhãn/return tương lai:

- Các cột `return`, `next_quarter_id`, `next_avg_close`, `label_basic`, `label_threshold` **không xuất hiện trong feature set**.

Kiểm tra tương quan feature-nhãn:

- Không feature nào có `|corr|` với `label_basic` vượt `0.95`.

Kết luận dùng trong luận văn:

- Có bằng chứng kiểm soát rò rỉ dữ liệu thời gian.
- Cần vẫn trình bày rõ: feature kỳ q dự báo nhãn kỳ q+1; decision card ban đầu không chứa outcome tương lai.

---

## 3. Kết quả text/news cũ và lý do chuyển news thành evidence layer

Nguồn cũ: `H1_experiment_report.md`, `H2_H3_validation_report.md`, `phan_tich_ket_qua_va_dinh_huong.md`, `experiment_A6_report.md`, `experiment_B1_report.md`, `distant_supervision_report.md`, `experiment_B3_report.md`.

### 3.1. H1 — Keyword/news feature không cải thiện forecast ổn định

Kết quả chính:

- Config_A kỹ thuật là nguồn dự báo chính.
- Config_B chỉ từ khóa gần mức ngẫu nhiên.
- Config_C kỹ thuật + từ khóa không cải thiện ổn định so với Config_A.
- Corpus mở rộng qua nhiều nguồn và nhiều granularity vẫn không đổi kết luận.

Một số kết quả cũ:

| Mô hình | Config_A kỹ thuật | Config_B từ khóa | Config_C kết hợp | C - A |
|---|---:|---:|---:|---:|
| Random Forest | 0.776 | 0.470 | 0.747 | -0.029 |
| XGBoost | 0.730 | 0.548 | 0.735 | +0.005 |
| LightGBM | 0.723 | 0.498 | 0.721 | -0.002 |
| Logistic Regression | 0.725 | 0.509 | 0.697 | -0.028 |

Kết luận dùng trong luận văn:

- Không nên định vị news/keyword là nguồn alpha chính.
- Tin tức phù hợp hơn với vai trò evidence/context cho LLM.

### 3.2. H2 — Từng từ khóa không significant sau BH-FDR

HOSE-80 quarterly:

- Từ khóa kiểm định: **71**.
- Significant sau BH-FDR: **0/71**.

Top raw p-value thấp:

| Từ khóa | Hướng | chi p-raw | chi p-adj | mw p-raw |
|---|---|---:|---:|---:|
| chia cổ tức | positive | 0.0089 | 0.333 | 0.0076 |
| giảm mạnh | negative | 0.0094 | 0.333 | 0.0056 |
| nợ xấu | negative | 0.0448 | 0.862 | 0.0337 |
| đại hội cổ đông | neutral | 0.0486 | 0.862 | 0.0339 |
| không chia cổ tức | negative | 0.0670 | 0.951 | 0.0551 |

Kết luận dùng trong luận văn:

- Có một số từ khóa có tín hiệu thô đáng chú ý, nhưng không đủ để claim quan hệ thống kê sau hiệu chỉnh đa kiểm định.
- Có thể dùng các từ khóa này làm event/evidence tags, không dùng làm bằng chứng alpha.

### 3.3. H3/SHAP Config_C — từ khóa có đóng góp một phần nhưng không cải thiện forecast

Kết quả cũ:

- Tổng feature từ khóa xếp hạng: **318**.
- Direction consistent: **80/318** (~25,2%).
- Tỷ lệ đóng góp SHAP: kỹ thuật khoảng **68,1%**, từ khóa khoảng **31,9%**.
- Top keyword theo SHAP gồm: `tăng trưởng`, `nợ xấu`, `báo lãi`, `chia cổ tức`, `tăng vốn điều lệ`.

Kết luận dùng trong luận văn:

- Mô hình có thể “dùng” từ khóa, nhưng tín hiệu không đủ ổn định để cải thiện out-of-sample performance.
- Đây là lý do chuyển từ news-as-feature sang news-as-evidence.

### 3.4. LLM sentiment A6

Kết quả cũ:

- Dùng Gemini Flash cho LLM sentiment.
- Prompt cấm dự đoán giá, chỉ gán sentiment nội dung.
- Temperature 0.
- Mean Δ(C−A) khoảng **-0.0061**.
- McNemar p khoảng **0.6177**.

Kết luận dùng trong luận văn:

- LLM sentiment không cải thiện forecast trong thiết kế cũ.
- Không nên claim LLM dự báo giá tốt hơn ML.
- LLM nên dùng để tạo thesis/explanation/review có kiểm soát.

### 3.5. Distant supervision B1

Kết quả cũ:

- Khoảng **28.519** bài.
- Nhãn noisy cấp bài: positive **25,4%**, neutral **50,8%**, negative **23,8%**.
- AUC macro one-vs-rest cấp bài khoảng **0,6797**.
- Khi gộp xác suất theo quý, Δ(C−A) khoảng **+0.0027**.
- McNemar p khoảng **0.5601**.

Kết luận dùng trong luận văn:

- Có tín hiệu yếu ở cấp bài viết nhưng tan biến khi tổng hợp theo kỳ.
- Điều này hỗ trợ ý tưởng dùng tin tức cho monitoring/event context thay vì predictor theo quý.

### 3.6. Segmentation B3

Kết quả cũ:

- Large-cap và mid-cap có Δ(C−A) âm, power cao hơn.
- Một số phân khúc dương như Transport/Technology có n nhỏ, không nhất quán giữa thuật toán.
- Không có keyword significant đáng tin ở các phân khúc.

Kết luận dùng trong luận văn:

- Không overclaim tín hiệu theo ngành.
- Nếu chọn case study, ưu tiên nhóm có đủ mẫu và coverage tốt.

---

## 4. Tiêu chí chọn cổ phiếu / universe

Nguồn cũ: `docs/stock_selection_criteria.md`, `dinh_huong_can_bang_luan_van.md`.

Tiêu chí HOSE-80 cũ:

- Sàn HOSE.
- Vốn hóa tối thiểu khoảng 2.000 tỷ VND.
- Thanh khoản đủ cao.
- Niêm yết liên tục từ 2022.
- Loại chứng quyền, ETF, cổ phiếu bị kiểm soát/cảnh báo kéo dài.
- Ưu tiên mã có độ phủ tin tức đủ dùng.

Robustness mở rộng:

- 125 mã HOSE+HNX.
- Tiêu chí volume trung bình >= 100.000 cổ/phiên.
- Tối thiểu 500 phiên từ 2022.

Kết luận dùng trong luận văn:

- Universe chính nên giữ HOSE-80 để đồng bộ kết quả cũ.
- Robustness 125 mã dùng làm kiểm tra phụ.

---

## 5. Giả định backtest thị trường Việt Nam

Nguồn cũ: `technical_ml_backtest_report.md`, `backtest/strategy.py`.

Giả định:

- Long-only, không bán khống.
- T+2.
- Biên độ HOSE ±7%/phiên chỉ là giả định nền.
- Lô tối thiểu 100 cổ phiếu.
- Giả định NAV đủ lớn để bỏ qua odd-lot rounding.
- Tính chi phí tường minh brokerage + sell tax.
- Bỏ qua slippage và market impact.
- Backtest theo kỳ, không mô phỏng khớp lệnh từng phiên.

Kết luận dùng trong luận văn:

- Kết quả backtest phục vụ học thuật, không phải khuyến nghị đầu tư.
- Cần ghi rõ giới hạn khi dùng return/Sharpe.

---

## 6. Narrative mới nên dùng

Từ bằng chứng trên, narrative luận văn mới:

1. ML kỹ thuật tạo tín hiệu định lượng có giá trị.
2. News/text không tạo alpha ổn định khi ép vào mô hình forecast.
3. Vì vậy news chuyển sang evidence layer để giải thích bối cảnh và theo dõi.
4. LLM không forecast; LLM tạo decision card có cấu trúc từ evidence pack.
5. Monitoring và outcome review đóng vòng phản hồi cho quyết định đầu tư.

Câu định vị:

> Luận văn không chứng minh LLM dự báo cổ phiếu tốt hơn ML. Luận văn xây dựng và đánh giá một quy trình hỗ trợ quyết định đầu tư, trong đó ML tạo tín hiệu, tin tức cung cấp bằng chứng, LLM tạo luận điểm có kiểm soát, và hệ thống theo dõi/hậu kiểm quyết định sau khuyến nghị.
