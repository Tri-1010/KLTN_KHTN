# Implementation Tasks — keyword-signal-validation

## Task List

- [x] 1. Góc 1: Xây dựng `experiment_keyword_significance.py` — kiểm định H2 từng từ khóa
  - [x] 1.1 Implement `apply_bh_correction(p_values, alpha)` sử dụng `statsmodels.stats.multitest.multipletests(method='fdr_bh')`; trả về mảng adjusted p-values cùng kích thước (Req 1.5, 6.1)
  - [x] 1.2 Implement `chi_square_or_fisher(occurrence, labels)`: xây bảng 2x2, nếu tần số kỳ vọng có ô <5 dùng `scipy.stats.fisher_exact`, ngược lại dùng `scipy.stats.chi2_contingency(correction=True)`; trả về `(statistic, p_value, test_used)` (Req 1.2, 1.9)
  - [x] 1.3 Implement `mann_whitney_test(norm_freq_up, norm_freq_not_up)`: dùng `scipy.stats.mannwhitneyu(alternative='two-sided')`; trả về `(statistic, p_value)`; xử lý an toàn khi một nhóm rỗng (Req 1.3)
  - [x] 1.4 Implement `logistic_univariate(occurrence, labels)`: dùng `statsmodels.api.Logit`; bắt `PerfectSeparationError` và `ConvergenceWarning` → trả về `(nan, nan, nan, nan)` thay vì crash; trả về `(coef, ci_lower, ci_upper, p_value)` (Req 1.4)
  - [x] 1.5 Implement `build_keyword_label_dataset(merged_df, keywords)`: trích xuất `kw_{k}` (Keyword_Occurrence = `kw_{k} > 0`) và `kw_norm_{k}` từ merged_df; loại từ khóa có tổng `kw_{k}` = 0 và ghi nhận vào danh sách bị loại (Req 1.1, 1.8)
  - [x] 1.6 Implement `run_keyword_significance(cutoff, alpha)`: gọi `load_and_merge_data()`, xây dataset, chạy 3 kiểm định cho mỗi từ khóa, áp dụng BH trên từng loại kiểm định riêng biệt, xây DataFrame output với đầy đủ cột theo thiết kế, lưu `reports/keyword_significance.csv`, in summary danh sách từ khóa significant (Req 1.1–1.10, 6.2–6.5, 7.1–7.5)
  - [x] 1.7 Thêm UTF-8 reconfigure block ở đầu file (giống pattern của các experiment script khác); thêm `if __name__ == "__main__": run_keyword_significance()` (Req 7.4)

- [x] 2. Góc 1: Viết unit tests `tests/test_keyword_significance.py` (Req 8.1–8.6)
  - [x] 2.1 `test_apply_bh_correction_known_example`: dùng ví dụ p-values = [0.01, 0.04, 0.10, 0.20] với alpha=0.05; xác minh kết quả adj_p khớp giá trị BH đã tính tay
  - [x] 2.2 `test_adjusted_pvalue_geq_raw`: property test — với bất kỳ mảng p-values ngẫu nhiên trong [0,1], mọi adj_p >= raw_p tương ứng (Req 8.3, 8.4)
  - [x] 2.3 `test_chi_selects_fisher_when_low_expected`: xây bảng 2x2 với ô kỳ vọng <5, xác minh `test_used == "fisher_exact"`
  - [x] 2.4 `test_chi_selects_chi_square_when_sufficient`: xây bảng 2x2 với tất cả ô kỳ vọng ≥5, xác minh `test_used == "chi_square"`
  - [x] 2.5 `test_all_zero_keyword_excluded`: từ khóa với tất cả `kw_{k} = 0` bị loại khỏi kiểm định (Req 8.5)
  - [x] 2.6 `test_single_class_label_no_exception`: khi tất cả labels = 0 hoặc tất cả = 1, hàm kiểm định không raise exception (Req 8.5)
  - [x] 2.7 `test_logistic_perfect_separation_returns_nan`: khi feature và label perfectly correlated, trả về (nan, nan, nan, nan) (Req 8.5)
  - [x] 2.8 Chạy toàn bộ test suite (`python -m pytest -q`) và xác nhận tất cả pass (Req 8.6)

- [x] 3. Góc 2: Xây dựng `experiment_metrics_breakdown.py` — phân rã thước đo (Req 2.1–2.7)
  - [x] 3.1 Implement `compute_per_class_metrics(y_true, y_pred, y_proba)`: dùng `sklearn.metrics.precision_recall_fscore_support(labels=[0,1])`, `balanced_accuracy_score`, `roc_auc_score`; trả về dict với keys `precision_class0`, `recall_class0`, `f1_class0`, `precision_class1`, `recall_class1`, `f1_class1`, `balanced_accuracy`, `auc_roc`; xử lý `y_proba=None` → `auc_roc=nan` (Req 2.2)
  - [x] 3.2 Implement `run_metrics_breakdown(cutoff, unit)`: load và merge data, time_series_split, với mỗi trong 4 thuật toán ML train Config_A và Config_C, gọi `compute_per_class_metrics`, thêm dòng delta (config="delta_C_minus_A"), ghi `unit` và `cutoff` vào output, lưu `reports/metrics_breakdown.csv` (Req 2.1–2.7, 6.3, 6.4)
  - [x] 3.3 Thêm UTF-8 block, `if __name__ == "__main__": run_metrics_breakdown()`, và docstring giải thích mục đích
  - [x] 3.4 Viết `tests/test_metrics_breakdown.py`: `test_compute_per_class_metrics_basic` (keys đúng, values trong [0,1]); `test_delta_rows_present` (có dòng delta); `test_records_unit_cutoff` (cột unit và cutoff được điền)

- [x] 4. Góc 3: Xây dựng `experiment_news_density.py` — phân tích theo mật độ tin (Req 3.1–3.6)
  - [x] 4.1 Implement `split_by_news_density(test_df)`: phân chia theo cột `has_min_news` có sẵn trong merged data; trả về `(dense_df, sparse_df)` (Req 3.1)
  - [x] 4.2 Implement `check_group_reliability(group_df, min_samples=20)`: trả về `(True, "")` nếu reliable, hoặc `(False, warning_msg)` nếu n_samples < 20 hoặc chỉ 1 lớp nhãn (Req 3.5)
  - [x] 4.3 Implement `run_news_density_analysis(cutoff)`: train Config_A và Config_C trên tập train đầy đủ; split test set theo mật độ tin; đánh giá mỗi config trên từng nhóm (gọi `check_group_reliability` trước, nếu not reliable vẫn tính nhưng đánh dấu warning); thêm cột `reliable` và `warning`; lưu `reports/news_density_analysis.csv` (Req 3.1–3.6, 6.6)
  - [x] 4.4 Thêm UTF-8 block, `if __name__ == "__main__": run_news_density_analysis()`
  - [x] 4.5 Viết `tests/test_news_density.py`: `test_split_by_density_correct_groups`; `test_check_reliability_low_samples`; `test_check_reliability_single_class`

- [x] 5. Góc 4: Xây dựng `experiment_shap_configc.py` — SHAP + permutation bắt buộc trên Config_C (Req 4.1–4.7)
  - [x] 5.1 Implement `train_configc_model(merged_df, tech_cols, kw_cols, cutoff, model_name, random_state)`: dùng `time_series_split`, `fit_imputer`, `prepare_features` từ task10_train; build model từ `build_ml_models`; huấn luyện trên Config_C = tech_cols + kw_cols; trả về `(model, X_train, y_train, X_test, y_test)` (Req 4.1, 6.3)
  - [x] 5.2 Implement `rank_keyword_features_by_shap(shap_values, feature_names, keywords_by_dir)`: dùng `task11_shap._extract_keyword_name` và `_is_keyword_feature` để lọc; tính `mean_shap` và `mean_abs_shap` cho mỗi từ khóa feature; ghi `direction` từ `keywords_by_dir`; kiểm tra `direction_consistent` (pos → mean_shap>0, neg → mean_shap<0); lưu `reports/shap_configc_keyword_ranking.csv` (Req 4.4, 4.6)
  - [x] 5.3 Implement `run_shap_configc(cutoff, model_name)`: (1) gọi `train_configc_model`; (2) gọi `task11_shap.compute_shap_values` để tính SHAP; (3) lưu beeswarm plot vào `reports/configc_shap_summary.png` (tái dùng `plot_shap_summary` với save_path khác); (4) tính permutation importance với `sklearn.inspection.permutation_importance` và lưu `reports/configc_permutation_importance.png`; (5) gọi `rank_keyword_features_by_shap`; (6) gọi `task11_shap.group_contribution_analysis` và log % đóng góp kw vs tech (Req 4.2, 4.3, 4.5, 4.7, 6.3)
  - [x] 5.4 Thêm UTF-8 block, `if __name__ == "__main__": run_shap_configc()`

- [x] 6. Tạo báo cáo tổng hợp `reports/H2_H3_validation_report.md` bằng tiếng Việt (Req 5.1–5.8)
  - [x] 6.1 Đọc `reports/keyword_significance.csv` và trích xuất: số từ khóa significant (chi/mw/logit), danh sách top từ khóa significant sắp xếp theo `chi_p_adj` tăng dần, phân bố significant theo hướng (positive/negative/neutral)
  - [x] 6.2 Đọc `reports/metrics_breakdown.csv` và trích xuất: bảng delta recall_class1 và precision_class1 cho từng algo, xác định các trường hợp recall tăng và precision giảm (đánh đổi)
  - [x] 6.3 Đọc `reports/news_density_analysis.csv` và trích xuất: bảng delta Config_C-A theo nhóm tin dày/thưa, đánh dấu các nhóm not reliable
  - [x] 6.4 Đọc `reports/shap_configc_keyword_ranking.csv` và trích xuất: top 10 từ khóa, % đóng góp kw vs tech, số từ khóa direction_consistent
  - [x] 6.5 Viết file markdown với 8 mục theo cấu trúc trong design; nêu rõ H1 là tiền đề đã chốt; kết luận H2 (ủng hộ/không ủng hộ tùy kết quả thực); kết luận H3; các sắc thái Góc 2 và 3; liệt kê giả định và giới hạn; liệt kê tệp kết quả (Req 5.2–5.8)

- [x] 7. Kiểm tra cuối cùng: chạy toàn bộ 4 experiment scripts và xác nhận output (Req 6.5, 7.1, 7.2)
  - [x] 7.1 Chạy `python -m pipeline.experiment_keyword_significance` và xác nhận `reports/keyword_significance.csv` được tạo, có đúng cấu trúc cột, không có lỗi encoding
  - [x] 7.2 Chạy `python -m pipeline.experiment_metrics_breakdown` và xác nhận `reports/metrics_breakdown.csv` có các dòng delta và đúng cấu trúc
  - [x] 7.3 Chạy `python -m pipeline.experiment_news_density` và xác nhận `reports/news_density_analysis.csv` có cột reliable và warning
  - [x] 7.4 Chạy `python -m pipeline.experiment_shap_configc` và xác nhận `reports/shap_configc_keyword_ranking.csv`, `reports/configc_shap_summary.png`, `reports/configc_permutation_importance.png` được tạo; xác nhận không ghi đè `reports/shap_summary.png` hay `reports/permutation_importance.png` của task11
  - [x] 7.5 Chạy `python -m pytest -q` và xác nhận toàn bộ bộ test pass (bao gồm 540 test cũ + test mới) (Req 8.6)
  - [x] 7.6 Xác nhận `reports/H2_H3_validation_report.md` đã được tạo, đọc được và có đủ 8 mục
