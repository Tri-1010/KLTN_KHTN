# Requirements Document

## Introduction

Tài liệu này đặc tả yêu cầu cho việc triển khai và kiểm định đầy đủ các **kết quả dương còn khai thác được** trong khung đề cương luận văn thạc sĩ về dự báo xu hướng giá cổ phiếu VN30 kết hợp đặc trưng kỹ thuật và tần suất từ khóa tin tức tài chính tiếng Việt.

Bối cảnh: Giả thuyết **H1** (kết hợp từ khóa cải thiện độ chính xác tổng thể so với chỉ dùng đặc trưng kỹ thuật) đã được kiểm chứng triệt để qua nhiều ngưỡng thời gian, 4 đơn vị thời gian, 5 lần mở rộng corpus (9.7k → 28k bài), 6 nguồn cân bằng và cải tiến cách đếm từ (phủ định + đồng nghĩa). Kết quả: **H1 không được ủng hộ** và đây là kết luận đã chốt, KHÔNG làm lại trong spec này. Đề cương tách rõ 3 giả thuyết và cho phép kết quả "không cải thiện" vẫn là kết quả hợp lệ; tuy nhiên **H2** và **H3** vẫn là các hướng kết quả dương chưa được khai thác đầy đủ.

Spec này triển khai 4 góc phân tích:

- **Góc 1 — Kiểm định H2 theo từng từ khóa:** kiểm định thống kê mối liên hệ giữa sự xuất hiện/tần suất mỗi từ khóa và nhãn xu hướng, có hiệu chỉnh đa kiểm định.
- **Góc 2 — Phân rã thước đo:** phân tích lại Config_A vs Config_C trên Precision/Recall/F1/AUC theo từng lớp (đặc biệt recall lớp "tăng"), trình bày như "giá trị bổ sung có điều kiện".
- **Góc 3 — Phân tích theo mật độ tin:** so sánh đóng góp từ khóa (Config_C − Config_A) trên nhóm tin dày (`has_min_news=1`) vs nhóm tin thưa.
- **Góc 4 — Kiểm định H3 / diễn giải:** chạy SHAP và permutation importance **bắt buộc trên Config_C** để xác định và xếp hạng các từ khóa đóng góp nhiều nhất, sửa giới hạn của phân tích SHAP hiện tại (task11 chỉ chạy trên best model = Config_A).

Spec này chỉ tạo các script thực nghiệm mới trong `pipeline/` và xuất kết quả ra `reports/`. Spec KHÔNG được phá vỡ production pipeline outputs, KHÔNG dùng sentiment analysis nâng cao, word embedding, hay mô hình ngôn ngữ mới — tuân thủ cam kết của đề cương về hướng đếm tần suất từ khóa.

## Glossary

- **System**: Tập hợp các script thực nghiệm và hàm thống kê được tạo bởi spec này (Góc 1–4), thuộc package `pipeline/`.
- **Keyword_Significance_Analyzer**: Thành phần thực hiện kiểm định thống kê H2 theo từng từ khóa (Góc 1), tạo trong `pipeline/experiment_keyword_significance.py`.
- **Metrics_Breakdown_Analyzer**: Thành phần phân rã thước đo Config_A vs Config_C (Góc 2), tạo trong `pipeline/experiment_metrics_breakdown.py`.
- **News_Density_Analyzer**: Thành phần phân tích đóng góp từ khóa theo mật độ tin (Góc 3), tạo trong `pipeline/experiment_news_density.py`.
- **ConfigC_Interpretability_Analyzer**: Thành phần chạy SHAP và permutation importance trên Config_C để trả lời H3 (Góc 4), tạo trong `pipeline/experiment_shap_configc.py`.
- **Config_A**: Cấu hình đặc trưng chỉ gồm 16 đặc trưng kỹ thuật.
- **Config_C**: Cấu hình đặc trưng kết hợp gồm đặc trưng kỹ thuật và đặc trưng từ khóa.
- **Keyword_Occurrence**: Biến nhị phân cho một (mã, kỳ), bằng 1 nếu từ khóa xuất hiện ít nhất một lần (`kw_{k} > 0`), bằng 0 nếu không.
- **Normalized_Keyword_Frequency**: Tần suất từ khóa chuẩn hóa `kw_norm_{k} = kw_{k} / news_count`.
- **Up_Label**: Nhãn xu hướng "tăng" (`label_basic = 1`); giá trung bình kỳ kế tiếp lớn hơn kỳ hiện tại.
- **Not_Up_Label**: Nhãn xu hướng "không tăng" (`label_basic = 0`).
- **Chi_Square_Test**: Kiểm định chi-square về tính độc lập giữa Keyword_Occurrence và nhãn xu hướng.
- **Mann_Whitney_Test**: Kiểm định Mann-Whitney U so sánh phân phối Normalized_Keyword_Frequency giữa nhóm Up_Label và nhóm Not_Up_Label.
- **BH_FDR_Correction**: Hiệu chỉnh đa kiểm định Benjamini-Hochberg kiểm soát tỷ lệ phát hiện sai (False Discovery Rate).
- **Raw_P_Value**: Giá trị p chưa hiệu chỉnh của một kiểm định đơn lẻ.
- **Adjusted_P_Value**: Giá trị p sau khi áp dụng BH_FDR_Correction.
- **Significance_Level**: Ngưỡng ý nghĩa thống kê α, mặc định 0.05.
- **SHAP_Value**: Giá trị đóng góp của một đặc trưng vào dự đoán theo phương pháp SHAP.
- **Permutation_Importance**: Mức giảm điểm số mô hình khi giá trị một đặc trưng bị hoán vị ngẫu nhiên.
- **has_min_news**: Cờ nhị phân có sẵn trong dữ liệu, bằng 1 khi `news_count >= 5` (nhóm tin dày), bằng 0 khi tin thưa.
- **Time_Series_Split**: Cách chia train/test theo thời gian, toàn bộ kỳ huấn luyện đứng trước kỳ kiểm tra để tránh rò rỉ dữ liệu.
- **Validation_Report**: Báo cáo tổng hợp kết quả 4 góc bằng tiếng Việt tại `reports/H2_H3_validation_report.md`.
- **Production_Pipeline_Outputs**: Các tệp đầu ra do pipeline sản xuất sinh ra (ví dụ `data/features/*.csv`, `models/best_model.pkl`, `reports/model_comparison.csv`) mà spec này không được ghi đè.

## Requirements

### Requirement 1: Kiểm định H2 theo từng từ khóa (Góc 1)

**User Story:** Là nghiên cứu sinh, tôi muốn kiểm định thống kê mối liên hệ giữa mỗi từ khóa và nhãn xu hướng giá, để xác định danh sách từ khóa có ý nghĩa thống kê làm bằng chứng cho giả thuyết H2.

#### Acceptance Criteria

1. THE Keyword_Significance_Analyzer SHALL xây dựng bộ dữ liệu (mã, kỳ) gồm Keyword_Occurrence, Normalized_Keyword_Frequency cho mỗi từ khóa, và nhãn xu hướng, sử dụng hàm đếm `pipeline.task9_kw_features.compute_raw_counts` và danh sách từ khóa từ `pipeline.task8_keywords.get_curated_keywords`.
2. WHEN bộ dữ liệu đã được xây dựng, THE Keyword_Significance_Analyzer SHALL thực hiện Chi_Square_Test giữa Keyword_Occurrence và nhãn xu hướng cho mỗi từ khóa.
3. WHEN bộ dữ liệu đã được xây dựng, THE Keyword_Significance_Analyzer SHALL thực hiện Mann_Whitney_Test so sánh Normalized_Keyword_Frequency giữa nhóm Up_Label và nhóm Not_Up_Label cho mỗi từ khóa.
4. THE Keyword_Significance_Analyzer SHALL ước lượng một mô hình logistic regression đơn biến cho mỗi từ khóa và báo cáo hệ số, khoảng tin cậy và Raw_P_Value của hệ số đó.
5. WHEN tất cả Raw_P_Value của một loại kiểm định đã được tính, THE Keyword_Significance_Analyzer SHALL áp dụng BH_FDR_Correction để tính Adjusted_P_Value cho loại kiểm định đó.
6. THE Keyword_Significance_Analyzer SHALL đánh dấu một từ khóa là significant WHERE Adjusted_P_Value của từ khóa đó nhỏ hơn Significance_Level.
7. THE Keyword_Significance_Analyzer SHALL xuất một tệp CSV tại `reports/keyword_significance.csv` chứa, cho mỗi từ khóa: tên từ khóa, hướng gán nhãn, thống kê và Raw_P_Value của từng kiểm định, Adjusted_P_Value tương ứng, hệ số logistic regression, và cờ significant.
8. IF một từ khóa có số lần xuất hiện bằng 0 trên toàn bộ dữ liệu, THEN THE Keyword_Significance_Analyzer SHALL loại từ khóa đó khỏi các kiểm định và ghi nhận từ khóa đó trong danh sách bị loại kèm lý do.
9. IF một bảng tần số của Chi_Square_Test chứa ô có tần số kỳ vọng nhỏ hơn 5, THEN THE Keyword_Significance_Analyzer SHALL áp dụng Fisher exact test thay cho Chi_Square_Test và ghi rõ kiểm định đã dùng cho từ khóa đó.
10. THE Keyword_Significance_Analyzer SHALL báo cáo tổng số từ khóa significant và danh sách các từ khóa đó được sắp xếp theo Adjusted_P_Value tăng dần.

### Requirement 2: Phân rã thước đo đánh giá Config_A vs Config_C (Góc 2)

**User Story:** Là nghiên cứu sinh, tôi muốn so sánh Config_A và Config_C trên nhiều thước đo theo từng lớp thay vì chỉ Balanced Accuracy, để phát hiện giá trị bổ sung có điều kiện của đặc trưng từ khóa.

#### Acceptance Criteria

1. THE Metrics_Breakdown_Analyzer SHALL huấn luyện và đánh giá Config_A và Config_C trên cùng một Time_Series_Split, tái sử dụng các hàm huấn luyện và chia dữ liệu trong `pipeline.task10_train`.
2. THE Metrics_Breakdown_Analyzer SHALL tính Precision, Recall và F1 cho cả lớp Up_Label và lớp Not_Up_Label, cùng với AUC và Balanced Accuracy, cho mỗi cấu hình và mỗi thuật toán.
3. THE Metrics_Breakdown_Analyzer SHALL tính hiệu số từng thước đo giữa Config_C và Config_A cho mỗi thuật toán.
4. THE Metrics_Breakdown_Analyzer SHALL báo cáo riêng Recall của lớp Up_Label cho Config_A và Config_C cùng hiệu số tương ứng cho mỗi thuật toán.
5. WHERE Config_C có Recall lớp Up_Label cao hơn Config_A đối với một thuật toán, THE Metrics_Breakdown_Analyzer SHALL báo cáo đồng thời thay đổi của Precision lớp Up_Label cho thuật toán đó để thể hiện đánh đổi báo động giả.
6. THE Metrics_Breakdown_Analyzer SHALL xuất một tệp CSV tại `reports/metrics_breakdown.csv` chứa toàn bộ thước đo theo lớp cho mỗi (thuật toán, cấu hình) và các hiệu số Config_C − Config_A.
7. THE Metrics_Breakdown_Analyzer SHALL ghi rõ đơn vị thời gian và ngưỡng chia train/test được dùng cho mỗi kết quả trong tệp đầu ra.

### Requirement 3: Phân tích đóng góp từ khóa theo mật độ tin (Góc 3)

**User Story:** Là nghiên cứu sinh, tôi muốn so sánh đóng góp của đặc trưng từ khóa giữa nhóm (mã, kỳ) tin dày và nhóm tin thưa, để kiểm tra giả thuyết rằng tin tức không đủ dày là nguyên nhân làm từ khóa kém hiệu quả.

#### Acceptance Criteria

1. THE News_Density_Analyzer SHALL phân chia tập kiểm tra thành nhóm tin dày WHERE `has_min_news` bằng 1 và nhóm tin thưa WHERE `has_min_news` bằng 0.
2. THE News_Density_Analyzer SHALL tính các thước đo đánh giá của Config_A và Config_C riêng cho từng nhóm mật độ tin.
3. THE News_Density_Analyzer SHALL tính hiệu số Config_C − Config_A cho mỗi nhóm mật độ tin và mỗi thuật toán.
4. THE News_Density_Analyzer SHALL báo cáo số mẫu của mỗi nhóm mật độ tin trong tập kiểm tra.
5. IF một nhóm mật độ tin có ít hơn 20 mẫu hoặc chỉ chứa một lớp nhãn, THEN THE News_Density_Analyzer SHALL đánh dấu kết quả của nhóm đó là không đáng tin cậy và ghi rõ cảnh báo trong đầu ra.
6. THE News_Density_Analyzer SHALL xuất một tệp CSV tại `reports/news_density_analysis.csv` chứa các thước đo, hiệu số và số mẫu theo từng nhóm mật độ tin và thuật toán.

### Requirement 4: Kiểm định H3 và diễn giải trên Config_C (Góc 4)

**User Story:** Là nghiên cứu sinh, tôi muốn chạy SHAP và permutation importance bắt buộc trên mô hình Config_C, để xác định và xếp hạng các từ khóa đóng góp nhiều nhất và trả lời đúng giả thuyết H3.

#### Acceptance Criteria

1. THE ConfigC_Interpretability_Analyzer SHALL huấn luyện một mô hình trên cấu hình Config_C bất kể best model toàn cục là cấu hình nào.
2. THE ConfigC_Interpretability_Analyzer SHALL tính SHAP_Value cho mô hình Config_C trên tập kiểm tra, tái sử dụng các hàm SHAP trong `pipeline.task11_shap` ở những nơi áp dụng được.
3. THE ConfigC_Interpretability_Analyzer SHALL tính Permutation_Importance cho mô hình Config_C trên tập kiểm tra với thước đo Balanced Accuracy.
4. THE ConfigC_Interpretability_Analyzer SHALL xếp hạng các đặc trưng từ khóa theo trung bình giá trị tuyệt đối của SHAP_Value và xuất bảng xếp hạng ra `reports/shap_configc_keyword_ranking.csv`.
5. THE ConfigC_Interpretability_Analyzer SHALL báo cáo tỷ lệ phần trăm đóng góp của nhóm đặc trưng từ khóa so với nhóm đặc trưng kỹ thuật theo tổng trung bình giá trị tuyệt đối SHAP_Value.
6. WHEN một đặc trưng từ khóa nằm trong danh sách xếp hạng cao nhất, THE ConfigC_Interpretability_Analyzer SHALL ghi nhận hướng gán nhãn của từ khóa và dấu trung bình SHAP_Value để kiểm tra tính nhất quán về hướng.
7. THE ConfigC_Interpretability_Analyzer SHALL lưu các biểu đồ SHAP và permutation importance với tiền tố tên tệp phân biệt với đầu ra của task11 để tránh ghi đè Production_Pipeline_Outputs.

### Requirement 5: Báo cáo tổng hợp 4 góc

**User Story:** Là nghiên cứu sinh, tôi muốn một báo cáo tổng hợp bằng tiếng Việt cho 4 góc, để đưa trực tiếp vào luận văn với kết luận trung thực.

#### Acceptance Criteria

1. THE System SHALL tạo Validation_Report tại `reports/H2_H3_validation_report.md` bằng tiếng Việt.
2. THE Validation_Report SHALL trình bày kết quả của cả 4 góc, mỗi góc một mục riêng kèm bảng số liệu.
3. THE Validation_Report SHALL nêu rõ kết luận H1 không được ủng hộ là tiền đề đã chốt và không nằm trong phạm vi kiểm định lại của spec này.
4. WHERE Góc 1 tìm được các từ khóa significant sau BH_FDR_Correction, THE Validation_Report SHALL trình bày danh sách đó như bằng chứng ủng hộ giả thuyết H2.
5. WHERE Góc 4 xác định được các từ khóa đóng góp đáng kể trong mô hình Config_C, THE Validation_Report SHALL trình bày kết quả đó như bằng chứng ủng hộ giả thuyết H3.
6. THE Validation_Report SHALL mô tả các sắc thái có điều kiện từ Góc 2 và Góc 3, gồm cả các trường hợp đánh đổi và các trường hợp không có giá trị bổ sung.
7. THE Validation_Report SHALL liệt kê các giả định và giới hạn của từng góc phân tích.
8. THE Validation_Report SHALL liệt kê đường dẫn các tệp kết quả CSV và biểu đồ tương ứng với từng góc.

### Requirement 6: Tính trung thực khoa học và kiểm soát chất lượng thống kê

**User Story:** Là nghiên cứu sinh, tôi muốn mọi phân tích thống kê tuân thủ chuẩn mực trung thực khoa học, để kết quả luận văn không bị nghi ngờ p-hacking và có thể tái lập.

#### Acceptance Criteria

1. WHEN nhiều kiểm định thống kê được thực hiện song song trên tập từ khóa, THE System SHALL áp dụng BH_FDR_Correction trước khi tuyên bố bất kỳ từ khóa nào là significant.
2. THE System SHALL báo cáo đồng thời Raw_P_Value và Adjusted_P_Value cho mọi kiểm định để giữ tính minh bạch.
3. THE System SHALL cố định và ghi lại random seed cho mọi quy trình có yếu tố ngẫu nhiên để đảm bảo tái lập kết quả.
4. THE System SHALL sử dụng Time_Series_Split cho mọi đánh giá mô hình để tránh rò rỉ dữ liệu từ tương lai.
5. THE System SHALL ghi rõ kích thước mẫu, đơn vị thời gian, ngưỡng chia, và Significance_Level đã dùng trong mỗi đầu ra kết quả.
6. WHERE một kết quả không đạt Significance_Level, THE System SHALL trình bày kết quả đó một cách trung thực thay vì loại bỏ hoặc che giấu.
7. THE System SHALL ghi rõ phương pháp đa kiểm định, các giả định của từng kiểm định thống kê, và điều kiện áp dụng trong tài liệu hoặc docstring của mỗi hàm thống kê.
8. THE System SHALL không thực hiện chọn lọc ngưỡng, đơn vị thời gian, hay tập con dữ liệu chỉ nhằm tối đa hóa số kết quả significant.

### Requirement 7: Bảo toàn pipeline sản xuất và môi trường thực thi

**User Story:** Là nghiên cứu sinh, tôi muốn các script thực nghiệm mới không phá vỡ pipeline sản xuất và chạy đúng trong môi trường Windows tiếng Việt, để bảo toàn các kết quả đã có và tránh lỗi mã hóa.

#### Acceptance Criteria

1. THE System SHALL chỉ ghi tệp kết quả mới vào `reports/` với tên tệp không trùng với Production_Pipeline_Outputs hiện có.
2. THE System SHALL không ghi đè các tệp trong `data/features/`, `models/`, và các tệp báo cáo do pipeline sản xuất tạo ra.
3. THE System SHALL đặt mọi script thực nghiệm mới trong thư mục `pipeline/` theo quy ước đặt tên `experiment_*.py`.
4. WHEN một script thực nghiệm ghi ra luồng stdout hoặc stderr, THE System SHALL cấu hình mã hóa UTF-8 để hiển thị đúng ký tự tiếng Việt trên Windows.
5. THE System SHALL đọc dữ liệu đầu vào với mã hóa UTF-8 từ các tệp dữ liệu có sẵn trong `data/`.
6. THE System SHALL sử dụng thư viện trong tập cho phép gồm scikit-learn, scipy.stats, statsmodels, shap, pandas và numpy, và không sử dụng embedding hay transformer.

### Requirement 8: Kiểm thử các hàm thống kê mới

**User Story:** Là nghiên cứu sinh, tôi muốn mọi hàm thống kê mới có unit test theo phong cách của dự án, để đảm bảo tính đúng đắn và giữ bộ test luôn pass.

#### Acceptance Criteria

1. THE System SHALL cung cấp unit test cho mỗi hàm thống kê mới được tạo trong 4 góc.
2. THE System SHALL kiểm thử BH_FDR_Correction với một ví dụ đã biết kết quả mong đợi để xác minh tính đúng đắn.
3. WHERE một hàm thống kê có thuộc tính bất biến hoặc round-trip kiểm thử được, THE System SHALL cung cấp property-based test cho thuộc tính đó theo phong cách kiểm thử của dự án.
4. THE System SHALL kiểm thử rằng Adjusted_P_Value luôn lớn hơn hoặc bằng Raw_P_Value tương ứng cho mọi đầu vào hợp lệ.
5. THE System SHALL kiểm thử hành vi với đầu vào biên gồm tập rỗng, từ khóa có tần suất bằng 0, và nhóm chỉ chứa một lớp nhãn.
6. WHEN bộ test mới được chạy cùng bộ test hiện có, THE System SHALL giữ toàn bộ bộ test ở trạng thái pass.
