# Design Document — keyword-signal-validation

## Overview

Spec này thêm 4 script thực nghiệm mới vào `pipeline/` và một báo cáo tổng hợp vào `reports/`, nhằm
kiểm định đầy đủ giả thuyết H2 và H3 trong luận văn thạc sĩ về dự báo xu hướng giá cổ phiếu VN30.
Không có thay đổi nào với production pipeline outputs. Mọi script đặt theo quy ước `experiment_*.py`
và tái sử dụng các hàm sẵn có từ `task8_keywords`, `task9_kw_features`, `task10_train`, `task11_shap`.

## Architecture

```
pipeline/
  experiment_keyword_significance.py  ← Góc 1: kiểm định H2 từng từ khóa
  experiment_metrics_breakdown.py     ← Góc 2: phân rã Precision/Recall/F1/AUC
  experiment_news_density.py          ← Góc 3: đóng góp từ khóa theo mật độ tin
  experiment_shap_configc.py          ← Góc 4: SHAP + permutation bắt buộc trên Config_C

tests/
  test_keyword_significance.py        ← unit tests Góc 1 (hàm thống kê)
  test_metrics_breakdown.py           ← unit tests Góc 2
  test_news_density.py                ← unit tests Góc 3

reports/
  keyword_significance.csv            ← output Góc 1
  metrics_breakdown.csv               ← output Góc 2
  news_density_analysis.csv           ← output Góc 3
  shap_configc_keyword_ranking.csv    ← output Góc 4
  configc_shap_summary.png            ← biểu đồ SHAP (tiền tố phân biệt task11)
  configc_permutation_importance.png  ← biểu đồ permutation
  H2_H3_validation_report.md         ← báo cáo tổng hợp tiếng Việt
```

## Data Flow

Tất cả 4 script dùng chung nguồn dữ liệu:
- `data/features/keyword_features.csv` + `data/features/technical_features.csv`
  + `data/aggregated/master_with_labels.csv` — merge qua `task10_train.load_and_merge_data()`
- `pipeline/task8_keywords.get_curated_keywords()` — danh sách từ khóa + hướng gán nhãn
- Chia train/test: `task10_train.time_series_split(cutoff="2025Q1")` — nhất quán với task10

## Component Design

### Góc 1 — `experiment_keyword_significance.py`

**Mục đích:** Kiểm định H2: "một số từ khóa có mối liên hệ thống kê với xu hướng tăng/giảm".

**Hàm công khai:**

```python
def build_keyword_label_dataset(merged_df: pd.DataFrame,
                                 keywords: List[str]) -> pd.DataFrame:
    """
    Trích xuất cột kw_{k} (đã có trong merged_df từ keyword_features.csv)
    và xây dựng:
      - keyword_occurrence_{k} = 1 nếu kw_{k} > 0 else 0
      - kw_norm_{k} (đã có)
      - label_basic
    Trả về DataFrame dạng dài với cột: keyword, direction, occurrence,
    norm_freq, label.
    """

def chi_square_or_fisher(occurrence: np.ndarray,
                          labels: np.ndarray) -> Tuple[float, float, str]:
    """
    Nếu tần số kỳ vọng của bảng 2x2 có ô < 5 → dùng Fisher exact test.
    Ngược lại → chi-square với correction=True.
    Trả về (statistic, p_value, test_used).
    """

def mann_whitney_test(norm_freq_up: np.ndarray,
                       norm_freq_not_up: np.ndarray) -> Tuple[float, float]:
    """Mann-Whitney U test, alternative='two-sided'. Trả về (statistic, p_value)."""

def logistic_univariate(occurrence: np.ndarray,
                         labels: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Logistic regression đơn biến (statsmodels.api.Logit).
    Trả về (coef, ci_lower, ci_upper, p_value).
    Nếu hoàn toàn separable → trả về (nan, nan, nan, nan) và log warning.
    """

def apply_bh_correction(p_values: np.ndarray,
                          alpha: float = 0.05) -> np.ndarray:
    """
    Hiệu chỉnh Benjamini-Hochberg trên mảng p-values.
    Dùng statsmodels.stats.multitest.multipletests(method='fdr_bh').
    Trả về mảng adjusted p-values cùng kích thước.
    """

def run_keyword_significance(cutoff: str = "2025Q1",
                               alpha: float = 0.05) -> pd.DataFrame:
    """Điểm vào chính. Trả về DataFrame đã lưu ra reports/keyword_significance.csv."""
```

**Output CSV — `reports/keyword_significance.csv`:**

| cột | mô tả |
|---|---|
| keyword | tên từ khóa |
| direction | positive / negative / neutral |
| n_occurrences | tổng số lần xuất hiện |
| n_excluded | 1 nếu bị loại (n_occurrences=0), else 0 |
| chi_statistic | thống kê chi-square hoặc Fisher |
| chi_p_raw | p-value thô của chi/Fisher |
| chi_p_adj | p-value sau BH |
| chi_test_used | "chi_square" hoặc "fisher_exact" |
| mw_statistic | thống kê Mann-Whitney |
| mw_p_raw | p-value thô Mann-Whitney |
| mw_p_adj | p-value sau BH |
| logit_coef | hệ số logistic |
| logit_ci_lower | CI 95% thấp |
| logit_ci_upper | CI 95% cao |
| logit_p_raw | p-value logistic |
| logit_p_adj | p-value sau BH |
| significant_chi | True nếu chi_p_adj < alpha |
| significant_mw | True nếu mw_p_adj < alpha |
| significant_logit | True nếu logit_p_adj < alpha |
| significant_any | True nếu ≥1 kiểm định significant |

---

### Góc 2 — `experiment_metrics_breakdown.py`

**Mục đích:** So sánh Config_A vs Config_C trên Precision/Recall/F1 theo lớp + AUC + Balanced Accuracy.
Trả lời: thêm từ khóa có làm recall lớp "tăng" tốt hơn không, và đánh đổi là gì?

**Hàm công khai:**

```python
def compute_per_class_metrics(y_true: np.ndarray,
                               y_pred: np.ndarray,
                               y_proba: Optional[np.ndarray]) -> Dict[str, float]:
    """
    Tính đầy đủ: precision/recall/f1 cho class 0 và class 1,
    balanced_accuracy, auc_roc (nếu y_proba có).
    Trả về dict với các key rõ ràng như precision_class1, recall_class1, ...
    """

def run_metrics_breakdown(cutoff: str = "2025Q1",
                           unit: str = "quarter") -> pd.DataFrame:
    """
    Điểm vào chính. Huấn luyện Config_A và Config_C trên tất cả 4 thuật toán ML
    với cùng Time_Series_Split. Tính per-class metrics cho mỗi (algo, config).
    Tính delta = Config_C - Config_A.
    Lưu reports/metrics_breakdown.csv. Trả về DataFrame.
    """
```

**Output CSV — `reports/metrics_breakdown.csv`:**

| cột | mô tả |
|---|---|
| model | tên thuật toán |
| config | Config_A hoặc Config_C |
| precision_class0 | precision lớp "không tăng" |
| recall_class0 | recall lớp "không tăng" |
| f1_class0 | F1 lớp "không tăng" |
| precision_class1 | precision lớp "tăng" |
| recall_class1 | recall lớp "tăng" |
| f1_class1 | F1 lớp "tăng" |
| balanced_accuracy | balanced accuracy |
| auc_roc | AUC-ROC |
| unit | đơn vị thời gian |
| cutoff | ngưỡng chia |

Thêm các dòng delta (config="delta_C_minus_A") để dễ so sánh.

---

### Góc 3 — `experiment_news_density.py`

**Mục đích:** Kiểm tra xem đóng góp của từ khóa có phụ thuộc vào mật độ tin không.
Cột `has_min_news` đã có sẵn trong keyword_features.csv (=1 nếu news_count >= 5).

**Hàm công khai:**

```python
def split_by_news_density(test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Phân chia test_df thành nhóm tin dày (has_min_news=1) và tin thưa (=0)."""

def check_group_reliability(group_df: pd.DataFrame,
                              min_samples: int = 20) -> Tuple[bool, str]:
    """
    Trả về (is_reliable, warning_message).
    Không đáng tin cậy nếu < 20 mẫu hoặc chỉ có 1 lớp nhãn.
    """

def run_news_density_analysis(cutoff: str = "2025Q1") -> pd.DataFrame:
    """
    Điểm vào chính. Huấn luyện Config_A, Config_C trên tập train đầy đủ.
    Đánh giá riêng trên test_dense và test_sparse.
    Lưu reports/news_density_analysis.csv. Trả về DataFrame.
    """
```

**Output CSV — `reports/news_density_analysis.csv`:**

| cột | mô tả |
|---|---|
| model | thuật toán |
| density_group | "dense" hoặc "sparse" |
| config | Config_A / Config_C / delta_C_minus_A |
| n_samples | số mẫu nhóm |
| reliable | True/False |
| warning | chuỗi cảnh báo hoặc rỗng |
| balanced_accuracy | điểm |
| recall_class1 | recall lớp "tăng" |
| precision_class1 | precision lớp "tăng" |

---

### Góc 4 — `experiment_shap_configc.py`

**Mục đích:** Trả lời H3 bằng cách BẮT BUỘC chạy SHAP + permutation trên Config_C,
không phụ thuộc vào best model metadata (task11 chỉ chạy trên Config_A vì best model = Config_A).

**Hàm công khai:**

```python
def train_configc_model(merged_df: pd.DataFrame,
                         tech_cols: List[str],
                         kw_cols: List[str],
                         cutoff: str = "2025Q1",
                         model_name: str = "Random_Forest",
                         random_state: int = 42
                        ) -> Tuple[Any, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Huấn luyện mô hình Random_Forest (hoặc model_name) trên Config_C.
    Trả về (model, X_train, y_train, X_test, y_test).
    Tái sử dụng task10_train.build_ml_models, fit_imputer, prepare_features,
    time_series_split.
    """

def compute_shap_configc(model, X_test, X_train) -> shap.Explanation:
    """Tái sử dụng task11_shap.compute_shap_values."""

def rank_keyword_features_by_shap(shap_values: shap.Explanation,
                                   feature_names: List[str],
                                   keywords_by_dir: Dict[str, List[str]]
                                  ) -> pd.DataFrame:
    """
    Xếp hạng tất cả đặc trưng từ khóa theo mean(|SHAP|).
    Ghi nhận: keyword name, direction, mean_shap (signed), mean_abs_shap,
    shap_direction (positive nếu mean_shap>0), direction_consistent.
    Lưu reports/shap_configc_keyword_ranking.csv.
    """

def compute_group_contribution_configc(shap_values, feature_names) -> Dict[str, float]:
    """
    Tính % đóng góp của nhóm kw vs tech trong Config_C.
    Tái sử dụng task11_shap.group_contribution_analysis.
    """

def run_shap_configc(cutoff: str = "2025Q1",
                      model_name: str = "Random_Forest") -> pd.DataFrame:
    """Điểm vào chính. Lưu kết quả ra reports/ với tiền tố 'configc_'."""
```

**Output files — Góc 4:**
- `reports/shap_configc_keyword_ranking.csv` — xếp hạng từ khóa theo SHAP
- `reports/configc_shap_summary.png` — beeswarm plot Config_C
- `reports/configc_permutation_importance.png` — permutation plot Config_C

---

### Báo cáo tổng hợp — `reports/H2_H3_validation_report.md`

Script `experiment_shap_configc.py` (hoặc một `generate_h2_h3_report.py` riêng) đọc các CSV từ 4
góc và tạo báo cáo markdown tiếng Việt với cấu trúc:

```
# Báo cáo kiểm định H2 và H3
## 1. Bối cảnh (H1 đã chốt không ủng hộ)
## 2. Góc 1 — Kiểm định H2: mối liên hệ thống kê từng từ khóa
   - Bảng từ khóa significant (top 20 theo adj p-value)
   - Kết luận H2
## 3. Góc 2 — Phân rã thước đo: recall lớp "tăng"
   - Bảng Precision/Recall/F1 lớp 1 cho mỗi algo
   - Mô tả đánh đổi
## 4. Góc 3 — Đóng góp từ khóa theo mật độ tin
   - Bảng delta Config_C-A theo nhóm tin dày/thưa
## 5. Góc 4 — Kiểm định H3: từ khóa đóng góp trong Config_C (SHAP)
   - Bảng top 10 từ khóa theo SHAP
   - % đóng góp kw vs tech
   - Kết luận H3
## 6. Kết luận tổng hợp
## 7. Giả định và giới hạn
## 8. Tệp kết quả
```

---

## Unit Test Design

### `tests/test_keyword_significance.py`

Kiểm thử các hàm thống kê trong Góc 1:

- `test_apply_bh_correction_known_example`: giá trị BH đã biết trước (ví dụ từ paper BH 1995)
- `test_adjusted_pvalue_geq_raw`: với mọi input hợp lệ, adj_p >= raw_p
- `test_chi_or_fisher_selects_fisher_when_low_expected`: mock bảng 2x2 có ô kỳ vọng <5
- `test_all_zero_keyword_excluded`: từ khóa không xuất hiện lần nào bị loại khỏi kiểm định
- `test_single_class_label_handled`: nhóm chỉ có 1 lớp nhãn không gây exception
- `test_logistic_univariate_perfect_separation_returns_nan`: perfect separation → trả về nan, không crash
- `test_bh_idempotent_on_uniform_pvalues`: p-values đồng đều → tất cả adj_p ≈ 1

### `tests/test_metrics_breakdown.py`

- `test_compute_per_class_metrics_basic`: output đúng keys, giá trị trong [0,1]
- `test_delta_rows_present_in_output`: CSV có dòng delta_C_minus_A
- `test_output_records_unit_and_cutoff`: các cột unit và cutoff được điền

### `tests/test_news_density.py`

- `test_split_by_density_correct_groups`: has_min_news=1 vào dense, =0 vào sparse
- `test_check_group_reliability_low_samples`: <20 mẫu → not reliable
- `test_check_group_reliability_single_class`: 1 lớp → not reliable + warning
- `test_full_run_produces_output_csv`: end-to-end với dữ liệu mock nhỏ

---

## Key Decisions

1. **Sử dụng BH-FDR thay vì Bonferroni**: BH ít bảo thủ hơn, phù hợp với exploratory research
   trong luận văn; Bonferroni sẽ quá khắt khe cho 100+ từ khóa.

2. **Dùng toàn bộ dataset (không chỉ tập test) cho Góc 1**: Kiểm định H2 về mối liên hệ thống kê
   là bài toán correlation/association, không phải bài toán dự báo — không cần time-split. Tuy nhiên
   phải ghi rõ trong báo cáo rằng đây là phân tích in-sample và không kết luận về khả năng dự báo
   out-of-sample.

3. **Chỉ báo cáo adj_p từ BH, không chọn lọc kết quả theo raw_p**: tránh p-hacking, tuân thủ Req 6.

4. **Dùng Random_Forest cho Góc 4**: nhất quán với best model, và TreeExplainer của SHAP cho kết quả
   ổn định hơn model-agnostic explainer.

5. **Tiền tố `configc_` cho output Góc 4**: tránh ghi đè `shap_summary.png`, `permutation_importance.png`
   của task11 (Production_Pipeline_Outputs).

6. **Random seed cố định = 42**: tái lập kết quả, nhất quán với toàn bộ pipeline.
