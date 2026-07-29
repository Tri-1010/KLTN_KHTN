# Implementation Plan: text-feature-experiments

## Overview

Kế hoạch triển khai xây dựng tầng thí nghiệm `experiments/` chồng lên pipeline hiện có, không
sửa hành vi mặc định của TASK 1–11. Thứ tự thực thi: (1) nền tảng dùng chung
(Baseline_Snapshotter, feature_registry + mở rộng `identify_feature_columns`, ExperimentRunner,
Comparison_Reporter, periods utility), (2) Hướng A theo ưu tiên A2 → A1 → A3 → A6, (3) Hướng B
theo B3 → B1. Các thí nghiệm tùy chọn A4/A5/B4/B5 được đánh dấu optional bằng `*`.

Mỗi thí nghiệm kết thúc bằng một task tạo báo cáo so sánh với `baseline_v0` qua
Comparison_Reporter — đây là yêu cầu quan trọng nhất. Property tests P1–P15 (định nghĩa trong
design) được đưa vào task tương ứng, gắn tag property, là **bắt buộc**, chạy tối thiểu 100
iterations bằng Hypothesis. Mọi task chỉ gồm viết/sửa/kiểm thử code.

Ngôn ngữ: **Python** (bám sát pipeline hiện có), property-based testing bằng **Hypothesis**.

## Tasks

- [x] 1. Thiết lập cấu trúc gói `experiments/` và khung kiểm thử property-based
  - Tạo `experiments/__init__.py`, `experiments/common/__init__.py`
  - Thêm `hypothesis` vào `requirements.txt` (hoặc file phụ thuộc dev tương đương) và cài đặt
  - Cấu hình Hypothesis profile mặc định `max_examples=100` (dùng `hypothesis.settings.register_profile` trong `tests/conftest.py`) để mọi property test chạy tối thiểu 100 iterations
  - Xác nhận `pytest` chạy được suite hiện có trước khi thêm code mới (baseline test count cho Req 15.4)
  - _Requirements: 15.1, 15.4_

- [x] 2. Tiện ích ranh giới kỳ dùng chung (`experiments/common/periods.py`)
  - [x] 2.1 Hiện thực `quarter_bounds(quarter_id)` trả về `(start_date, end_date)` của quý và `clip_return_window(d, horizon, quarter_id)` cắt cửa sổ return tại `end_date` của quý chứa `d`
    - Tái sử dụng cho A3 (shift theo kỳ) và B1 (cắt cửa sổ return)
    - _Requirements: 4.3, 4.4, 4.5_
  - [x] 2.2 Viết unit test cho `quarter_bounds` và `clip_return_window`
    - Kiểm tra ranh giới quý (đầu/cuối năm, chuyển Q4→Q1), cắt cửa sổ đúng biên
    - _Requirements: 4.3, 4.5_

- [x] 3. Baseline_Snapshotter (`experiments/common/snapshot.py`) — đóng băng kết quả cũ
  - [x] 3.1 Hiện thực `create_baseline_snapshot()` và dataclass `SnapshotResult`
    - Copy 6 tệp trong `SNAPSHOT_FILES` từ `reports/` vào `reports/baseline_v0/`
    - Tệp nguồn thiếu → log cảnh báo nêu tên tệp, tiếp tục (không ném exception)
    - `baseline_v0/` đã có tệp và `force=False` → giữ nguyên, log "đã tồn tại"
    - Ghi manifest `.snapshot_meta.json`: ngày tạo + danh sách tệp đã copy
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - [x] 3.2 Viết unit test cho Baseline_Snapshotter
    - Test copy đầy đủ, test tệp nguồn thiếu, test không ghi đè khi đã tồn tại, test manifest
    - Dùng thư mục tạm (`tmp_path`) để không đụng `reports/` thật
    - _Requirements: 1.2, 1.3, 1.4_

- [x] 4. Feature Registry và mở rộng Feature_Column_Classifier
  - [x] 4.1 Hiện thực `experiments/feature_registry.py`
    - Khai báo `NEW_KW_PREFIXES` (`sent_`, `llm_`, `ds_`, `sector_`, `emb_`, `tfidfx_`), `NEW_KW_EXACT` (`news_velocity`, `kw_novelty`, `kw_entropy`, `pos_neg_shift`, `news_spike`), `NEG_SUFFIX = "_NEG"`
    - Hiện thực `is_keyword_column(col)` bao trùm mọi nhóm trên
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [x] 4.2 Mở rộng `identify_feature_columns()` trong `pipeline/task10_train.py`
    - Import mềm (try/except) `is_keyword_column` từ registry với fallback để `task10_train` vẫn chạy độc lập khi vắng `experiments/`
    - Thêm nhánh `_is_new_keyword_column` xử lý hậu tố `_NEG` (cột kết thúc `_NEG` + tiền tố `kw_`) và các prefix/tên mới
    - Đảm bảo cột không khớp quy tắc keyword nào và không phải meta → rơi vào technical
    - _Requirements: 3.1, 3.6, 3.7, 14.2, 14.3_
  - [x] 4.3 Viết property test P1 — cột đặc trưng văn bản mới luôn thuộc nhóm keyword
    - **Property 1: Cột đặc trưng văn bản mới luôn thuộc nhóm keyword**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.7**
    - Sinh ngẫu nhiên DataFrame trộn cột meta/technical/văn-bản-mới; kiểm mọi cột văn bản mới vào nhóm keyword; tối thiểu 100 iterations
  - [x] 4.4 Viết property test P2 — bất biến tập đặc trưng kỹ thuật Config_A
    - **Property 2: Bất biến của tập đặc trưng kỹ thuật Config_A**
    - **Validates: Requirements 3.6, 14.2, 14.3**
    - Thêm tập keyword tùy ý vào 16 technical cố định; kiểm technical luôn đúng 16 cột; tối thiểu 100 iterations

- [x] 5. ExperimentRunner và mở rộng `run_model_training` để lấy predictions
  - [x] 5.1 Mở rộng `pipeline/task10_train.py::run_model_training`
    - Thêm tham số `comparison_path: str | None = None` (mặc định giữ `MODEL_COMPARISON_PATH`) và `return_predictions: bool = False`
    - Giữ nguyên chữ ký cũ và hành vi khi tham số mặc định (Req 14.1)
    - Thêm hàm cấp thấp `run_configs_return_predictions()` tái dùng `load_and_merge_data`, `identify_feature_columns`, `get_feature_configs`, `time_series_split`, `fit_imputer`, `prepare_features` để trả về `y_test` và predictions Config_A/Config_C trên cùng tập test
    - _Requirements: 14.1, 14.2, 14.3, 4.1, 4.2_
  - [x] 5.2 Hiện thực `experiments/common/runner.py`
    - Dataclass `ExperimentConfig` (experiment_id, kw_features_path, comparison_path, cutoff) và `RunnerResult` (results_df, test_index, y_test, pred_by_config)
    - `run_experiment_training(cfg)` gọi `run_model_training` với `kw_path`/`comparison_path` tùy biến và thu predictions cho McNemar
    - Xây dựng đường dẫn artifact từ `experiment_id` nhất quán (feature/results/report)
    - _Requirements: 2.1, 2.2, 2.4, 14.1_
  - [x] 5.3 Viết property test P3 — chia train/test giữ đúng thứ tự thời gian
    - **Property 3: Chia train/test giữ đúng thứ tự thời gian**
    - **Validates: Requirements 4.1**
    - Sinh tập `(ticker, quarter_id)` có ≥4 quý sau cutoff; kiểm mọi quarter train < cutoff ≤ mọi quarter test, không chồng lấn; tối thiểu 100 iterations
  - [x] 5.4 Viết property test P15 — nhất quán experiment_id giữa các artifact
    - **Property 15: Nhất quán mã thí nghiệm giữa các artifact**
    - **Validates: Requirements 2.1, 2.2, 2.4**
    - Sinh `experiment_id` hợp lệ ngẫu nhiên; kiểm tên tệp đặc trưng, tệp kết quả, tệp báo cáo cùng nhúng đúng một id; tối thiểu 100 iterations

- [x] 6. Comparison_Reporter (`experiments/common/reporting.py`)
  - [x] 6.1 Hiện thực `generate_comparison_report()`
    - Bảng Δ(C−A) 4 thuật toán (LightGBM, Random Forest, XGBoost, Logistic Regression) đặt cạnh `baseline_v0` (Req 13.1)
    - #keyword đạt BH_FDR vs `0/71` (Req 13.2); % SHAP text vs `32%` (Req 13.3)
    - McNemar giữa Config_C mới và Config_C baseline: tái tạo predictions v0 qua `run_configs_return_predictions()` với `keyword_features.csv` gốc, align theo `(ticker, quarter_id)`, dùng `statsmodels...mcnemar` (Req 13.4)
    - Viết nhận xét H1/H2/H3 (Req 13.5), phân tích 3 giải thích lý thuyết (Req 13.6), kết luận vị trí trong luận văn (Req 13.7)
    - Ghi `reports/experiment_{id}_report.md`
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_
  - [x] 6.2 Hiện thực `generate_text_representation_table()`
    - Bảng tổng hợp Δ(C−A) 4 tầng biểu diễn (v0, A2, A1a, A6) cho từng thuật toán
    - _Requirements: 13.8_
  - [x] 6.3 Viết unit test cho Comparison_Reporter
    - Dùng dữ liệu baseline/kết quả giả (fixture) kiểm cấu trúc bảng, giá trị Δ, align McNemar theo `(ticker, quarter_id)`
    - _Requirements: 13.1, 13.4_

- [x] 7. CLI orchestrator `experiments/run_experiment.py`
  - Hiện thực CLI: `--snapshot`, `--experiment {id}`, `--report`
  - Đảm bảo thứ tự: snapshot baseline nếu chưa có → build feature set → chạy runner → chạy Comparison_Reporter
  - Chạy song song, không thay thế `pipeline/run_pipeline.py`; wiring các thành phần nền tảng ở task 3–6
  - _Requirements: 1.5, 2.1, 2.2, 13.1_

- [x] 8. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. A2 — Negation-aware Keyword Matching (ưu tiên đầu Hướng A)
  - [x] 9.1 Hiện thực `experiments/a2_negation.py::compute_raw_counts_negation_aware`
    - Khai báo `NEGATION_CUES` tường minh và `NEGATION_WINDOW = 3`
    - Giữ longest-first masking; sau khi xác định span khớp, kiểm cửa sổ ±3 từ; nếu có cue phủ định và keyword chưa mang sẵn nghĩa phủ định → count vào `kw_{keyword}_NEG`, ngược lại count vào `kw_{keyword}`
    - `_already_negative(kw)` chống double-flip cho keyword thuộc nhóm `negative` hoặc đã chứa cue phủ định
    - Dùng `re.finditer` trên bản masked để lấy vị trí từng lần khớp trước khi mask span
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - [x] 9.2 Viết property test P5 — đảo polarity khi và chỉ khi có phủ định hợp lệ trong cửa sổ
    - **Property 5: Đảo polarity khi và chỉ khi có phủ định hợp lệ trong cửa sổ**
    - **Validates: Requirements 5.2, 5.3, 5.5**
    - Sinh văn bản + keyword + vị trí cue ngẫu nhiên; kiểm đếm vào `_NEG` iff có cue trong cửa sổ và keyword chưa mang sẵn nghĩa phủ định; tối thiểu 100 iterations
  - [x] 9.3 Viết property test P6 — bảo toàn số đếm, phủ định không gây đếm trùng
    - **Property 6: Bảo toàn số đếm — phủ định không gây đếm trùng**
    - **Validates: Requirements 5.4**
    - Kiểm tổng đếm `kw_{k}` + `kw_{k}_NEG` bằng đúng số span longest-first masking gốc; span đã khớp không bị substring đối nghịch đếm lại; tối thiểu 100 iterations
  - [x] 9.4 Hiện thực `build_a2_features()` và ghi `data/features/keyword_features_A2.csv`
    - Đọc `news_by_quarter.csv`, áp dụng matcher, giữ khung khóa `(ticker, quarter_id)` mergeable
    - Trả về thống kê % số hit bị flip cho các keyword hay bị phủ định (nợ xấu, lợi nhuận, tăng trưởng)
    - _Requirements: 5.6, 5.7, 2.1, 2.3_
  - [x] 9.5 Tạo báo cáo so sánh A2 với baseline_v0
    - Chạy ExperimentRunner với `keyword_features_A2.csv` → `reports/model_comparison_A2.csv`
    - Gọi Comparison_Reporter sinh `reports/experiment_A2_report.md`; đưa % hit bị flip vào báo cáo
    - _Requirements: 5.7, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 2.2_

- [x] 10. A1 — Signed Sentiment Score theo nhóm chủ đề
  - [x] 10.1 Hiện thực `experiments/a1_group_sentiment.py::compute_group_sentiment`
    - Với mỗi nhóm G ∈ KEYWORD_GROUPS: `sent_{G}` = Σ `kw_norm`(pos∈G) − Σ `kw_norm`(neg∈G), chuẩn hóa theo `news_count`
    - Tái dùng `compute_keyword_counts` để có `kw_norm_*`
    - _Requirements: 6.1, 6.2_
  - [x] 10.2 Viết property test P7 — công thức điểm sentiment theo nhóm
    - **Property 7: Công thức điểm sentiment theo nhóm**
    - **Validates: Requirements 6.1, 6.2**
    - Sinh giá trị `kw_norm_*` ngẫu nhiên; kiểm `sent_{G}` bằng công thức và tăng đơn điệu theo đóng góp tích cực khi giữ nguyên tiêu cực; tối thiểu 100 iterations
  - [x] 10.3 Hiện thực `build_a1a_features()` và `build_a1b_features()`
    - A1a: chỉ `sent_A..F` + coverage → `data/features/keyword_features_A1a.csv`
    - A1b: raw `kw_*`/`kw_norm_*`/`tfidf_*` của v0 + `sent_A..F` → `data/features/keyword_features_A1b.csv`
    - _Requirements: 6.3, 6.4, 2.1_
  - [x] 10.4 Tạo báo cáo so sánh A1a và A1b với baseline_v0
    - Chạy ExperimentRunner cho A1a và A1b → `model_comparison_A1a.csv`, `model_comparison_A1b.csv`
    - Gọi Comparison_Reporter sinh `experiment_A1a_report.md`, `experiment_A1b_report.md`; báo cáo số lượng đặc trưng A1a/A1b đối chiếu v0
    - _Requirements: 6.5, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 2.2_

- [x] 11. A3 — News Velocity & Novelty Features
  - [x] 11.1 Hiện thực `experiments/a3_velocity.py::build_velocity_features`
    - Sắp theo `(ticker, quarter_id)` tăng dần; dùng `groupby("ticker").shift(1)` cho kỳ trước
    - `news_velocity` = (nc[q]−nc[q−1])/(nc[q−1]+1); `pos_neg_shift` = sentiment_ratio[q]−sentiment_ratio[q−1]
    - `kw_novelty` = #keyword lần đầu xuất hiện ở q (expanding set các kỳ trước, loại trừ q); `kw_entropy` = entropy phân phối kw trong q
    - Chỉ dùng kỳ ≤ q
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [x] 11.2 Viết property test P8 — công thức velocity và pos_neg_shift
    - **Property 8: Công thức velocity và pos_neg_shift**
    - **Validates: Requirements 7.1, 7.4**
    - Sinh chuỗi kỳ đã sắp xếp với `news_count`/`sentiment_ratio`; kiểm công thức với kỳ liền trước; tối thiểu 100 iterations
  - [x] 11.3 Viết property test P9 — cận của kw_entropy
    - **Property 9: Cận của kw_entropy**
    - **Validates: Requirements 7.3**
    - Kiểm entropy = 0 khi tập trung một keyword, đạt cực đại khi phân phối đều, luôn không âm; tối thiểu 100 iterations
  - [x] 11.4 Viết property test P4 — nhân quả theo kỳ, không rò rỉ tương lai (A3)
    - **Property 4: Nhân quả theo kỳ — không rò rỉ tương lai**
    - **Validates: Requirements 4.3, 4.4, 4.5, 7.5**
    - Sinh dữ liệu nhiều kỳ; thay đổi dữ liệu kỳ > q không làm đổi đặc trưng A3 tại q; tối thiểu 100 iterations
  - [x] 11.5 Hiện thực build A3 và ghi `data/features/keyword_features_A3.csv`
    - Gộp velocity/novelty/entropy/shift + đặc trưng v0 base, giữ khung khóa mergeable
    - _Requirements: 7.6, 2.1_
  - [x] 11.6 Tạo báo cáo so sánh A3 với baseline_v0
    - Chạy ExperimentRunner → `model_comparison_A3.csv`; Comparison_Reporter → `experiment_A3_report.md`
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 2.2_

- [x] 12. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. A6 — LLM Zero-shot Sentiment (Gemini Flash)
  - [x] 13.1 Hiện thực `experiments/a6_llm_sentiment.py::annotate_articles`
    - Với mỗi bài chưa có trong cache: gọi Gemini Flash (temperature=0) hỏi sentiment {positive/negative/neutral} + confidence; prompt cấm dự đoán giá
    - Ghi cache `data/news/annotated/llm_sentiment.csv` kèm `content_hash`, `model_version`, `temperature`, `annotated_at`
    - Bài đã có trong cache → dùng lại; lỗi API → log bài lỗi và tiếp tục
    - Trừu tượng hóa lời gọi API qua một client injectable để test dùng được mock
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.8_
  - [x] 13.2 Hiện thực `aggregate_llm_features()` và ghi `data/features/keyword_features_A6.csv`
    - Gộp theo `(ticker, quarter_id)`: `llm_pos_ratio`, `llm_neg_ratio`, `llm_net_sentiment`
    - _Requirements: 8.6, 8.7, 2.1_
  - [x] 13.3 Viết property test P10 — nhất quán tỷ lệ sentiment từ LLM
    - **Property 10: Nhất quán tỷ lệ sentiment từ LLM**
    - **Validates: Requirements 8.6**
    - Sinh tập nhãn LLM ngẫu nhiên ≥1 bài; kiểm pos+neg+neutral = 1 và `llm_net_sentiment` = pos−neg; tối thiểu 100 iterations
  - [x] 13.4 Viết unit test cho annotate_articles dùng mock client
    - Mock client LLM (KHÔNG gọi API thật); kiểm cache reuse (không gọi lại), xử lý lỗi API (log + tiếp tục), ghi đủ trường cache
    - _Requirements: 8.5, 8.8_
  - [x] 13.5 Tạo báo cáo so sánh A6 với baseline_v0
    - Chạy ExperimentRunner → `model_comparison_A6.csv`; Comparison_Reporter → `experiment_A6_report.md`
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 2.2_

- [x] 14. Bảng tổng hợp 4 tầng biểu diễn văn bản (Hướng A)
  - Gọi `generate_text_representation_table(["v0", "A2", "A1a", "A6"])` sinh bảng Δ(C−A) tổng hợp
  - Wiring vào CLI orchestrator hoặc report tổng
  - _Requirements: 13.8_

- [x] 15. B3 — Segmentation theo Ngành & Vốn hóa (ưu tiên đầu Hướng B)
  - [x] 15.1 Hiện thực `experiments/common/segments.py`
    - Dataclass `SegmentInfo(ticker, sector, cap_group)`; ánh xạ sector từ `config/pipeline_config.yaml`; `cap_group` large_cap (30 VN30) vs mid_cap (50 mở rộng)
    - `assign_segments()` gán mỗi ticker đúng một sector và một cap_group
    - _Requirements: 10.1, 10.2_
  - [x] 15.2 Viết property test P11 — ánh xạ phân khúc phủ toàn bộ và duy nhất
    - **Property 11: Ánh xạ phân khúc phủ toàn bộ và duy nhất**
    - **Validates: Requirements 10.1, 10.2**
    - Sinh danh sách ticker cấu hình; kiểm mỗi ticker đúng một sector + một cap_group, hợp phủ toàn bộ, không ticker nào ở hai cap_group; tối thiểu 100 iterations
  - [x] 15.3 Hiện thực `experiments/b3_segmentation.py::run_segmentation_analysis`
    - Với mỗi phân khúc (từng sector, large-cap vs mid-cap): lọc merged theo ticker, retrain Config_A/B/C dùng `run_configs_return_predictions`, tính Delta_CA (cùng cutoff, cùng chia thời gian)
    - Kiểm định keyword significance + BH_FDR trong phân khúc; báo cáo `n_samples` mỗi phân khúc
    - Ghi `reports/segmentation_analysis.csv` và `reports/segmentation_keyword_sig.csv`
    - _Requirements: 10.3, 10.4, 10.5, 10.6_
  - [x] 15.4 Tạo báo cáo so sánh B3 với baseline_v0
    - Comparison_Reporter sinh `experiment_B3_report.md`: Δ(C−A) theo ngành/vốn hóa cạnh tổng hợp v0, nhấn mạnh statistical power (n mỗi nhóm)
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_

- [x] 16. B1 — Distant Supervision (Short-term Price Return Labeling)
  - [x] 16.1 Hiện thực `experiments/b1_distant_supervision.py::build_noisy_labels`
    - Với mỗi bài `(t, d)`: return `[d+1, d+3]` ngày giao dịch, cắt tại ranh giới kỳ chứa d qua `clip_return_window`
    - Gán `positive` nếu ≥ +2%, `negative` nếu ≤ −2%, `neutral` nếu ở giữa
    - Nguồn giá `data/prices/<TICKER>.csv`
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  - [x] 16.2 Viết property test P12 — gán nhãn nhiễu theo ngưỡng ±2%
    - **Property 12: Gán nhãn nhiễu theo ngưỡng ±2%**
    - **Validates: Requirements 11.2, 11.3, 11.4**
    - Sinh giá trị return ngẫu nhiên; kiểm ranh giới phân loại pos/neg/neutral; tối thiểu 100 iterations
  - [x] 16.3 Viết property test P13 — cửa sổ suất sinh lời bị cắt trong ranh giới kỳ
    - **Property 13: Cửa sổ suất sinh lời bị cắt trong ranh giới kỳ**
    - **Validates: Requirements 11.1, 11.5**
    - Sinh ngày đăng d và chuỗi giá; kiểm tập ngày dùng tính return nằm hoàn toàn trong kỳ chứa d, và thay đổi giá kỳ sau không đổi nhãn nhiễu; tối thiểu 100 iterations
  - [x] 16.4 Hiện thực `train_article_classifier()` chỉ trên bài của kỳ < cutoff
    - TF-IDF + Logistic Regression 3 lớp trên `text_tokenized`; lọc bài theo kỳ < Train_Cutoff trước khi fit
    - _Requirements: 11.6_
  - [x] 16.5 Viết property test P14 — bộ phân loại chỉ học trên bài của giai đoạn train
    - **Property 14: Bộ phân loại chỉ học trên bài của giai đoạn train**
    - **Validates: Requirements 11.6**
    - Sinh tập bài trải nhiều kỳ; kiểm tập train của classifier chỉ gồm bài kỳ < cutoff; tối thiểu 100 iterations
  - [x] 16.6 Hiện thực `build_b1_features()` và ghi `data/features/keyword_features_B1.csv`
    - Với mỗi `(ticker, quarter_id)`: aggregate `predict_proba` chỉ trên bài trong quý đó → `ds_pos_prob_mean`, `ds_net_sentiment`
    - Ghi `reports/distant_supervision_report.md`: phân phối noisy label, AUC classifier trên nhãn nhiễu cấp bài, granularity analysis
    - _Requirements: 11.7, 11.8, 2.1_
  - [x] 16.7 Viết property test P4 — nhân quả theo kỳ cho aggregation B1
    - **Property 4: Nhân quả theo kỳ — không rò rỉ tương lai (B1 aggregation)**
    - **Validates: Requirements 4.3, 4.4, 4.5, 11.7**
    - Thay đổi dữ liệu bài kỳ > q không làm đổi `ds_pos_prob_mean`/`ds_net_sentiment` tại q; tối thiểu 100 iterations
  - [x] 16.8 Tạo báo cáo so sánh B1 với baseline_v0
    - Chạy ExperimentRunner → `model_comparison_B1.csv`; Comparison_Reporter → `experiment_B1_report.md` kèm granularity analysis
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 2.2_

- [x] 17. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Thí nghiệm tùy chọn (mở rộng khi còn thời gian)
  - [x] 18.1 A4 — TFIDF cross-ticker (`experiments/a4_tfidf_crossticker.py`)
    - Tính trọng số TF-IDF cross-ticker → `data/features/keyword_features_A4.csv`; báo cáo so sánh với v0
    - _Requirements: 9.1, 9.3_
  - [x] 18.2 A5 — PhoBERT embeddings (`experiments/a5_embeddings.py`)
    - Tính đặc trưng nhúng `emb_*` → `data/features/keyword_features_A5.csv`; báo cáo so sánh với v0
    - _Requirements: 9.2, 9.3_
  - [x] 18.3 B4 — Cross-sector News Spillover (`experiments/b4_spillover.py`)
    - `sector_pos_score`, `sector_news_count` chỉ dùng tin kỳ q, không dùng chính ticker đó; báo cáo so sánh
    - _Requirements: 12.1, 12.2_
  - [x] 18.4 B5 — Anomaly Detection News Volume (`experiments/b5_anomaly.py`)
    - `news_spike` = 1 khi news_count[q] > mean + 2·std (tính trên train); báo cáo so sánh
    - _Requirements: 12.3_

- [x] 19. Checkpoint cuối — chạy toàn bộ test suite, xác nhận không giảm số test đang pass
  - Chạy `pytest` toàn bộ suite (bao gồm property tests P1–P15 với ≥100 iterations và test hiện có)
  - Xác nhận số test pass không giảm so với baseline ở task 1 (Req 15.4)
  - Xác nhận `data/news/annotated/llm_sentiment.csv` được commit kèm model_version (Req 15.2)
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Task đánh dấu `*` là tùy chọn (A4/A5/B4/B5 và các unit test bổ trợ), có thể bỏ để tăng tốc MVP.
- **Property tests P1–P15 là bắt buộc** (không đánh dấu `*`), chạy tối thiểu 100 iterations bằng Hypothesis.
- Mỗi thí nghiệm đều có task tạo báo cáo so sánh với `baseline_v0` qua Comparison_Reporter — yêu cầu quan trọng nhất.
- A6 dùng client LLM injectable + mock trong test (không gọi API thật khi test).
- B1 nhấn mạnh property test ràng buộc thời gian (P4, P13, P14) để chống rò rỉ dữ liệu.
- Mọi task tham chiếu requirements cụ thể và property liên quan; task build tăng dần trên task trước, không tạo orphan code.
- Config_A (16 đặc trưng kỹ thuật) là hằng số đối chứng, bất biến giữa mọi thí nghiệm.
```
