# ĐỀ CƯƠNG LUẬN VĂN

## 1. Thông tin đề tài

**Tên tiếng Việt:** Hệ thống hỗ trợ quyết định cổ phiếu dựa trên tín hiệu học máy và bằng chứng tin tức ngữ nghĩa có truy vết

**Tên tiếng Anh:** *Evidence-Grounded Stock Decision Support Using Machine Learning Signals and Semantic News Materiality*

**Học viên:** Ngô Minh Trí  
**Mã số học viên:** 24C01024  
**Ngành:** Khoa học Dữ liệu — mã số 8460108  
**Đơn vị:** Trường Đại học Khoa học Tự nhiên, Đại học Quốc gia Thành phố Hồ Chí Minh

## 2. Bối cảnh và vấn đề nghiên cứu

Dữ liệu kỹ thuật và tin tức phản ánh hai lớp thông tin khác nhau của thị trường chứng khoán. Chỉ báo kỹ thuật có cấu trúc và thuận tiện cho ML nhưng không giải thích đầy đủ bối cảnh doanh nghiệp. Keyword count dễ tái lập nhưng bỏ qua ticker relevance, materiality, event type, phủ định và bằng chứng nguyên văn. Semantic extraction bằng LLM tạo schema giàu hơn nhưng có rủi ro pseudo-label, hallucination, model drift và leakage thời gian.

Các thí nghiệm cũ trong repository chưa cho phép so sánh trực tiếp mọi phương pháp: quarterly keyword, daily semantic, period-material và technical backtest dùng unit, target, split hoặc universe khác nhau. Luận văn khắc phục điểm này bằng một canonical comparison: keyword và semantic phải dùng cùng article spine, observation rows, khoảng thời gian, target, folds, model và backtest.

## 3. Mục tiêu nghiên cứu

### 3.1. Mục tiêu tổng quát

Xây dựng và đánh giá hệ thống hỗ trợ quyết định cổ phiếu Việt Nam, trong đó ML tạo tín hiệu định lượng; semantic material-event tạo evidence có cấu trúc; decision card trình bày thesis, evidence, risk và monitoring; toàn bộ chuỗi có provenance và kiểm soát point-in-time.

### 3.2. Mục tiêu cụ thể

1. Đánh giá keyword và semantic trên cùng canonical sample và phương pháp ML.
2. Xây schema semantic gồm relevance, materiality, event type, direction, uncertainty, novelty và evidence span.
3. Kiểm soát leakage bằng effective date bảo thủ, target-exit-aware folds và train-only transforms.
4. So sánh keyword với semantic bằng paired OOS metrics và inference đã preregister.
5. So sánh Top-K keyword với semantic trên cùng candidate universe, ngày, K, holding period và cost.
6. Xây evidence pack, constrained LLM decision card, monitoring và outcome review có truy vết.
7. Công bố cả kết quả âm, `not_estimable` và giới hạn claim.

## 4. Câu hỏi nghiên cứu

- **RQ1:** Keyword representation tạo incremental predictive value ngoài technical và coverage features không?
- **RQ2:** Semantic representation tạo incremental predictive value ngoài technical và coverage features không?
- **RQ3:** Trên đúng cùng rows/folds/target/model, semantic có cải thiện so với keyword không?
- **RQ4:** Materiality/direction có liên hệ với VNINDEX-adjusted returns ở event windows nào?
- **RQ5:** Full-evidence decision cards có chất lượng rubric tốt hơn ML-only và rule cards trong cùng judge condition không?
- **RQ6:** Hệ thống có duy trì lineage point-in-time từ input tới signal, evidence, card, monitoring và outcome review không?

## 5. Giả thuyết và claim gate

### H1 — Keyword incremental value

`Technical + Coverage + Keyword` không cải thiện ổn định so với `Technical + Coverage` trong setting canonical.

### H2 — Semantic incremental value

`Technical + Coverage + Semantic` có thể cải thiện `Technical + Coverage` trong primary preregistered setting.

### H3 — Semantic so với keyword

Primary comparison:

```text
Baseline: B_technical_coverage_keyword
Comparison: C_technical_coverage_semantic
Model: RandomForest
Metric: balanced_accuracy
Target: label_outperform_T20
```

H3 chỉ pass khi đúng primary record có đủ ba folds, cùng rows/targets, audits pass, `p_value_bh <= 0.05` và bootstrap CI lower bound lớn hơn 0.

### H4 — Decision-card evidence value

Full-evidence cards đạt rubric tốt hơn ML-only và rule cards trong cùng automated judge condition. Không suy diễn thành tăng return hoặc human decision accuracy.

## 6. Dữ liệu và đơn vị quan sát

- Giá cổ phiếu: `data/prices/all_vn30_prices.csv`.
- Benchmark: `data/prices_extended/VNINDEX.csv`.
- Technical features: `data/features/technical_features.csv`.
- Article sample: 150 bài có hash cố định.
- Semantic consensus: pseudo-label consensus của ba annotation runs; 122 bài đủ điều kiện trước temporal mapping.
- Observation key: `(ticker, date, target_exit_date)`.
- Article key: `(news_id, ticker)`.

Canonical claim chỉ áp dụng cho common stratified article spine, không đại diện full corpus.

## 7. Phương pháp

### 7.1. Point-in-time mapping

Bài thiếu giờ xuất bản chỉ khả dụng từ phiên giao dịch kế tiếp. Article mapping lỗi vẫn nằm trong attrition audit nhưng không vào analytic features. Không dùng future outcome trong initial evidence hoặc feature construction.

### 7.2. Target

`label_outperform_T20 = 1` khi return cổ phiếu lớn hơn VNINDEX trên cùng entry và exit sessions, horizon 20 phiên benchmark. Thiếu exact stock/benchmark prices tạo status lỗi; không forward-fill.

### 7.3. Feature configurations

- `A_technical`
- `E_technical_coverage`
- `B_technical_coverage_keyword`
- `C_technical_coverage_semantic`
- `D_technical_coverage_keyword_semantic`

B và C dùng cùng technical/coverage features, chỉ khác text representation. Không dùng full-sample TF-IDF hoặc future-return-derived B1 features trong canonical family.

### 7.4. Temporal validation

Ba expanding folds. Train rows phải có `target_exit_date < test_start`. Imputer, scaler và feature availability chỉ fit trên train. Không fallback split, không chọn model theo test.

### 7.5. Mô hình và metrics

Primary model Random Forest: 300 trees, max depth 6, min samples leaf 5, balanced class weights, seed 42. Logistic Regression là secondary robustness.

Primary metric Balanced Accuracy. Secondary metrics: AUC, F1, Brier, log loss, Precision@10, rank IC và calibration.

### 7.6. Inference

Paired OOS daily deltas; fold-local block bootstrap 10.000 draws; sign-flip/permutation 10.000 draws; BH-FDR theo preregistered family.

### 7.7. Backtest

Primary Top-10, equal weight, T+20 non-overlap, cost `0.005 × turnover`. Keyword và semantic dùng cùng candidate universe, dates, exits, K và cost. Kết quả là mô phỏng exploratory, không gọi alpha.

## 8. Đóng góp dự kiến

1. Same-sample keyword–semantic comparison có executable protocol và fail-closed gates.
2. Semantic schema tiếng Việt gắn evidence spans và provenance.
3. Tách predictive evaluation, event association, card quality và traceability thành bốn lớp claim riêng.
4. Submission bundle tái lập với hashes, claim–evidence matrix và legacy registry.
5. Báo cáo trung thực kết quả âm hoặc không đủ dữ liệu.

## 9. Kế hoạch thực hiện

1. Khóa protocol và input hashes.
2. Build canonical targets, article spine, panel và manifests.
3. Chạy smoke test bằng run ID riêng.
4. Chạy canonical non-fast.
5. Xác thực same rows/folds/targets/backtest.
6. Sinh bảng, hình, claim matrix và checksums.
7. Hoàn thiện luận văn, phụ lục và audit bundle.

## 10. Giới hạn và đạo đức nghiên cứu

- Pseudo-label không phải human ground truth.
- Sample stratified nhỏ, chưa hỗ trợ full-corpus superiority.
- Agreement giữa model không thay expert annotation.
- Event study không xác định nhân quả.
- Top-K thiếu đầy đủ liquidity, spread và market-impact modeling.
- Automated rubric có judge bias.
- Không đưa khuyến nghị đầu tư, cam kết lợi nhuận hoặc tự động giao dịch.

## 11. Đầu ra

- Canonical structured results và manifests.
- Đề cương, luận văn Markdown, bảng, hình và phụ lục.
- Reproduction commands và validator.
- Claim–evidence–limitation matrix.
- EvidenceTrace prototype và selected case audits.
