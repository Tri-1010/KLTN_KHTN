# Requirements Document

## Introduction

Tính năng `text-feature-experiments` triển khai một loạt thí nghiệm mở rộng đặc trưng văn
bản trong khuôn khổ luận văn thạc sĩ Khoa học Dữ liệu về dự báo xu hướng giá cổ phiếu
HOSE-80, kết hợp đặc trưng kỹ thuật và đặc trưng trích xuất từ tin tức tài chính tiếng Việt.

Kết quả hiện tại của luận văn: giả thuyết H1 và H2 không được ủng hộ (đặc trưng từ khóa
không cải thiện dự báo), giả thuyết H3 được ủng hộ một phần. Tính năng theo đuổi hai mục
tiêu:

- **Hướng A — Củng cố kết quả âm:** Chứng minh kết quả âm không phải do phương pháp đo lường
  văn bản yếu, bằng cách thử nhiều tầng biểu diễn văn bản tinh vi hơn tần suất thô.
- **Hướng B — Tìm tín hiệu có điều kiện:** Chuyển kết luận nhị phân thành kết luận có điều
  kiện, xác định khi nào (ngành nào, nhóm vốn hóa nào, cấp độ granularity nào) tín hiệu văn
  bản xuất hiện.

Ràng buộc cốt lõi: mọi thí nghiệm PHẢI đi qua cùng pipeline huấn luyện hiện có để so sánh
công bằng với kết quả cũ (baseline v0), PHẢI tránh rò rỉ dữ liệu theo thời gian, và mỗi thí
nghiệm khi hoàn thành PHẢI tạo ra một báo cáo so sánh và phân tích đầy đủ với kết quả cũ
trong luận văn.

## Glossary

- **Experiment_System**: Toàn bộ hệ thống thí nghiệm đặc trưng văn bản được xây dựng trong
  tính năng này, bao trùm các mô-đun con bên dưới.
- **Baseline_Snapshotter**: Mô-đun tạo bản đóng băng bất biến của toàn bộ kết quả cũ vào
  `reports/baseline_v0/`.
- **Baseline_v0**: Tập kết quả cũ đã đóng băng, dùng làm mốc so sánh bất biến cho mọi thí
  nghiệm.
- **Feature_Column_Classifier**: Hàm `identify_feature_columns()` trong `task10_train.py`
  phân loại cột đặc trưng thành nhóm kỹ thuật (technical) và nhóm từ khóa (keyword).
- **Model_Trainer**: Pipeline huấn luyện hiện có (`task10_train.py`) huấn luyện 4 thuật toán
  và 2 baseline trên 3 cấu hình đặc trưng (Config_A, Config_B, Config_C).
- **Keyword_Feature_Extractor**: Mô-đun trích xuất đặc trưng từ khóa (`task9_kw_features.py`).
- **Negation_Matcher**: Thành phần A2 xử lý phủ định khi khớp từ khóa (đảo polarity).
- **Sentiment_Aggregator**: Thành phần A1 tổng hợp điểm sentiment có dấu theo nhóm chủ đề.
- **Velocity_Feature_Builder**: Thành phần A3 tính đặc trưng tốc độ và độ mới của tin tức.
- **LLM_Annotator**: Thành phần A6 gọi mô hình Gemini Flash để gán nhãn sentiment nội dung
  cho từng bài viết và lưu kết quả cố định.
- **TFIDF_CrossTicker_Builder**: Thành phần A4 (tùy chọn) tính TF-IDF cross-ticker.
- **Embedding_Builder**: Thành phần A5 (tùy chọn) tính đặc trưng nhúng bằng PhoBERT.
- **Segmentation_Analyzer**: Thành phần B3 chạy phân tích theo phân khúc ngành và vốn hóa.
- **Distant_Supervision_Module**: Thành phần B1 tạo nhãn nhiễu từ suất sinh lời ngắn hạn và
  huấn luyện bộ phân loại sentiment cấp bài viết.
- **Spillover_Builder**: Thành phần B4 (tùy chọn) tính đặc trưng lan tỏa tin tức liên ngành.
- **Anomaly_Detector**: Thành phần B5 (tùy chọn) phát hiện đột biến khối lượng tin tức.
- **Comparison_Reporter**: Mô-đun tạo báo cáo so sánh và phân tích của mỗi thí nghiệm với
  Baseline_v0.
- **Feature_Set_Version**: Tệp đặc trưng có hậu tố phiên bản (ví dụ `keyword_features_A2.csv`)
  cho mỗi biến thể thí nghiệm.
- **Train_Cutoff**: Ranh giới chia train/test theo thời gian, cố định tại `2025Q1`.
- **Period_q**: Một kỳ quý cụ thể trong chuỗi thời gian.
- **Noisy_Label**: Nhãn sentiment cấp bài viết được suy ra từ suất sinh lời ngắn hạn (dùng
  cho Distant_Supervision_Module).
- **BH_FDR**: Thủ tục hiệu chỉnh đa kiểm định Benjamini-Hochberg False Discovery Rate.
- **McNemar_Test**: Kiểm định McNemar so sánh dự đoán của hai mô hình trên cùng tập kiểm tra.
- **Delta_CA**: Chênh lệch balanced accuracy giữa Config_C và Config_A, tức Δ(C−A).

## Requirements

### Requirement 1: Đóng băng kết quả cũ làm baseline so sánh

**User Story:** Là một nghiên cứu sinh, tôi muốn đóng băng toàn bộ kết quả hiện tại của luận
văn trước khi chạy bất kỳ thí nghiệm nào, để mọi thí nghiệm mới có một mốc so sánh bất biến.

#### Acceptance Criteria

1. WHEN Baseline_Snapshotter được thực thi, THE Baseline_Snapshotter SHALL sao chép các tệp
   `model_comparison.csv`, `keyword_significance.csv`, `period_experiment.csv`,
   `metrics_breakdown.csv`, `news_density_analysis.csv`, và `shap_configc_keyword_ranking.csv`
   từ thư mục `reports/` vào thư mục `reports/baseline_v0/`.
2. WHERE một tệp nguồn không tồn tại trong `reports/`, THE Baseline_Snapshotter SHALL ghi
   một cảnh báo nêu tên tệp thiếu và tiếp tục sao chép các tệp còn lại.
3. IF thư mục `reports/baseline_v0/` đã chứa tệp đóng băng, THEN THE Baseline_Snapshotter
   SHALL giữ nguyên nội dung hiện có và ghi thông báo rằng baseline đã tồn tại.
4. THE Baseline_Snapshotter SHALL ghi vào `reports/baseline_v0/` một tệp siêu dữ liệu chứa
   ngày tạo snapshot và danh sách các tệp đã sao chép.
5. WHEN quá trình đóng băng hoàn tất, THE Experiment_System SHALL coi các tệp trong
   `reports/baseline_v0/` là bất biến và SHALL ghi mọi kết quả thí nghiệm mới vào các tệp có
   hậu tố phiên bản riêng biệt.

### Requirement 2: Version hóa tập đặc trưng để chạy song song

**User Story:** Là một nghiên cứu sinh, tôi muốn mỗi thí nghiệm ghi tập đặc trưng ra một tệp
có phiên bản riêng, để chạy nhiều biến thể song song mà không ghi đè baseline.

#### Acceptance Criteria

1. WHEN một thí nghiệm tạo tập đặc trưng từ khóa mới, THE Experiment_System SHALL ghi tập
   đặc trưng đó ra tệp `data/features/keyword_features_{experiment_id}.csv` với
   `{experiment_id}` là mã thí nghiệm (ví dụ `A2`, `A1a`, `A1b`, `A3`, `A6`, `B1`).
2. WHEN một thí nghiệm huấn luyện mô hình trên tập đặc trưng có phiên bản, THE Model_Trainer
   SHALL ghi bảng so sánh mô hình ra tệp `reports/model_comparison_{experiment_id}.csv`.
3. THE Experiment_System SHALL giữ nguyên tệp `data/features/keyword_features.csv` gốc làm
   phiên bản v0 mà không sửa đổi.
4. THE Experiment_System SHALL đặt tên mọi tệp đầu ra của một thí nghiệm với cùng một
   `{experiment_id}` nhất quán giữa tệp đặc trưng, tệp kết quả huấn luyện, và tệp báo cáo.

### Requirement 3: Nhận diện đúng nhóm đặc trưng mới

**User Story:** Là một nghiên cứu sinh, tôi muốn mọi cột đặc trưng văn bản mới được phân loại
đúng vào nhóm keyword, để chúng rơi vào đúng Config_B và Config_C khi so sánh với Config_A.

#### Acceptance Criteria

1. WHEN Feature_Column_Classifier nhận một DataFrame chứa cột đặc trưng văn bản mới, THE
   Feature_Column_Classifier SHALL phân loại cột đó vào nhóm keyword nếu cột thuộc một trong
   các tiền tố hoặc tên đặc trưng văn bản đã đăng ký.
2. THE Feature_Column_Classifier SHALL phân loại các cột có hậu tố phủ định của thành phần
   A2 vào nhóm keyword.
3. THE Feature_Column_Classifier SHALL phân loại các cột điểm sentiment theo nhóm chủ đề của
   thành phần A1 vào nhóm keyword.
4. THE Feature_Column_Classifier SHALL phân loại các cột velocity và novelty của thành phần
   A3 vào nhóm keyword.
5. THE Feature_Column_Classifier SHALL phân loại các cột điểm sentiment từ LLM của thành phần
   A6 vào nhóm keyword.
6. THE Feature_Column_Classifier SHALL giữ nguyên 16 đặc trưng kỹ thuật trong nhóm technical
   ở mọi thí nghiệm.
7. IF một cột không khớp với bất kỳ tiền tố hoặc tên đặc trưng văn bản đã đăng ký nào và
   không phải cột siêu dữ liệu, THEN THE Feature_Column_Classifier SHALL phân loại cột đó vào
   nhóm technical.

### Requirement 4: Ngăn rò rỉ dữ liệu theo thời gian

**User Story:** Là một nghiên cứu sinh, tôi muốn mọi đặc trưng và mọi bước huấn luyện tuân
thủ ranh giới thời gian nghiêm ngặt, để kết quả không bị nhiễm rò rỉ dữ liệu tương lai.

#### Acceptance Criteria

1. THE Model_Trainer SHALL chia train/test theo thời gian tại Train_Cutoff bằng `2025Q1` mà
   không xáo trộn thứ tự dữ liệu.
2. WHEN Model_Trainer chuẩn bị đặc trưng, THE Model_Trainer SHALL fit imputer và bộ chuẩn hóa
   chỉ trên tập train và SHALL áp dụng các tham số đã fit đó lên tập test.
3. WHEN Experiment_System tính một đặc trưng cho Period_q, THE Experiment_System SHALL chỉ sử
   dụng thông tin thuộc Period_q hoặc các kỳ trước Period_q.
4. THE Experiment_System SHALL không sử dụng bất kỳ thông tin nào thuộc kỳ liền sau Period_q
   khi tính đặc trưng cho Period_q.
5. WHERE một đặc trưng dựa trên kỳ trước (ví dụ velocity, novelty), THE Experiment_System
   SHALL tính đặc trưng đó chỉ từ dữ liệu của các kỳ có chỉ số thời gian nhỏ hơn Period_q.

### Requirement 5: A2 — Khớp từ khóa có nhận biết phủ định

**User Story:** Là một nghiên cứu sinh, tôi muốn hệ thống nhận biết phủ định khi khớp từ
khóa, để phân biệt "nợ xấu giảm" với "nợ xấu tăng" thay vì tính cả hai là một hit như nhau.

#### Acceptance Criteria

1. THE Negation_Matcher SHALL định nghĩa một danh sách các dấu hiệu phủ định tiếng Việt được
   khai báo tường minh.
2. WHEN Negation_Matcher khớp một từ khóa tại một vị trí trong văn bản, THE Negation_Matcher
   SHALL kiểm tra sự hiện diện của dấu hiệu phủ định trong cửa sổ 3 từ trước và 3 từ sau vị
   trí khớp.
3. IF một dấu hiệu phủ định xuất hiện trong cửa sổ 3 từ quanh một từ khóa được khớp, THEN THE
   Negation_Matcher SHALL đếm lần khớp đó vào một đặc trưng đảo polarity có hậu tố riêng thay
   vì đặc trưng từ khóa gốc.
4. THE Negation_Matcher SHALL thực hiện việc kiểm tra phủ định sau khi longest-first masking
   đã xác định các span khớp.
5. WHERE một từ khóa đã mang sẵn nghĩa phủ định trong danh sách từ khóa, THE Negation_Matcher
   SHALL đếm từ khóa đó theo polarity gốc mà không đảo thêm một lần nữa.
6. WHEN A2 hoàn tất, THE Negation_Matcher SHALL ghi tập đặc trưng ra
   `data/features/keyword_features_A2.csv`.
7. WHEN A2 hoàn tất, THE Comparison_Reporter SHALL báo cáo tỷ lệ phần trăm số lần khớp bị đảo
   polarity cho các từ khóa hay bị phủ định nhất.

### Requirement 6: A1 — Điểm sentiment có dấu theo nhóm chủ đề

**User Story:** Là một nghiên cứu sinh, tôi muốn tổng hợp điểm sentiment có dấu theo từng
nhóm chủ đề, để thay các đặc trưng tần suất rời rạc bằng các đặc trưng tổng hợp có ý nghĩa
kinh tế.

#### Acceptance Criteria

1. THE Sentiment_Aggregator SHALL tính một điểm sentiment có dấu cho mỗi nhóm chủ đề được
   định nghĩa trong `KEYWORD_GROUPS`, bằng tổng điểm chuẩn hóa của từ khóa tích cực trừ tổng
   điểm chuẩn hóa của từ khóa tiêu cực trong nhóm đó.
2. THE Sentiment_Aggregator SHALL chuẩn hóa mỗi điểm sentiment nhóm theo số lượng tin của
   `(ticker, Period_q)`.
3. WHERE biến thể A1a được chọn, THE Sentiment_Aggregator SHALL tạo tập đặc trưng chỉ gồm các
   điểm sentiment theo nhóm và ghi ra `data/features/keyword_features_A1a.csv`.
4. WHERE biến thể A1b được chọn, THE Sentiment_Aggregator SHALL tạo tập đặc trưng gồm các đặc
   trưng tần suất gốc cộng với các điểm sentiment theo nhóm và ghi ra
   `data/features/keyword_features_A1b.csv`.
5. WHEN A1 hoàn tất, THE Comparison_Reporter SHALL báo cáo số lượng đặc trưng của biến thể
   A1a và A1b để đối chiếu với số lượng đặc trưng của Baseline_v0.

### Requirement 7: A3 — Đặc trưng tốc độ và độ mới của tin tức

**User Story:** Là một nghiên cứu sinh, tôi muốn thêm đặc trưng tốc độ và độ mới của tin tức,
để kiểm tra liệu thông tin mới có giá trị dự báo cao hơn tần suất tĩnh không.

#### Acceptance Criteria

1. THE Velocity_Feature_Builder SHALL tính đặc trưng `news_velocity` cho mỗi
   `(ticker, Period_q)` bằng chênh lệch số lượng tin giữa Period_q và kỳ liền trước, chia cho
   số lượng tin kỳ liền trước cộng một.
2. THE Velocity_Feature_Builder SHALL tính đặc trưng `kw_novelty` bằng số từ khóa lần đầu
   xuất hiện ở Period_q mà chưa từng xuất hiện ở các kỳ trước của cùng ticker.
3. THE Velocity_Feature_Builder SHALL tính đặc trưng `kw_entropy` bằng entropy của phân phối
   từ khóa trong Period_q.
4. THE Velocity_Feature_Builder SHALL tính đặc trưng `pos_neg_shift` bằng thay đổi của
   sentiment_ratio giữa Period_q và kỳ liền trước.
5. THE Velocity_Feature_Builder SHALL tính mọi đặc trưng tốc độ và độ mới chỉ từ dữ liệu của
   Period_q và các kỳ trước Period_q.
6. WHEN A3 hoàn tất, THE Velocity_Feature_Builder SHALL ghi tập đặc trưng ra
   `data/features/keyword_features_A3.csv`.

### Requirement 8: A6 — Gán nhãn sentiment zero-shot bằng LLM

**User Story:** Là một nghiên cứu sinh, tôi muốn dùng Gemini Flash như một công cụ gán nhãn
sentiment nội dung cho từng bài viết và lưu kết quả cố định, để có tầng biểu diễn văn bản cao
nhất mà vẫn tái lập được.

#### Acceptance Criteria

1. WHEN LLM_Annotator xử lý một bài viết, THE LLM_Annotator SHALL gửi tiêu đề và mô tả của
   bài viết tới mô hình Gemini Flash và yêu cầu phân loại sentiment thành một trong ba giá
   trị `positive`, `negative`, `neutral` kèm mức độ tin cậy.
2. THE LLM_Annotator SHALL dùng prompt chỉ yêu cầu đánh giá polarity nội dung bài viết và
   SHALL cấm mô hình dự đoán diễn biến giá cổ phiếu.
3. THE LLM_Annotator SHALL gọi mô hình với temperature bằng 0.
4. WHEN LLM_Annotator hoàn tất một bài viết, THE LLM_Annotator SHALL lưu kết quả vào
   `data/news/annotated/llm_sentiment.csv` kèm mã băm nội dung đầu vào, kết quả đầu ra, phiên
   bản mô hình, dấu thời gian, và giá trị temperature.
5. WHILE tệp `data/news/annotated/llm_sentiment.csv` đã chứa kết quả cho một bài viết, THE
   LLM_Annotator SHALL dùng lại kết quả đã lưu thay vì gọi lại mô hình cho bài viết đó.
6. THE LLM_Annotator SHALL tổng hợp kết quả gán nhãn theo `(ticker, Period_q)` thành các đặc
   trưng `llm_pos_ratio`, `llm_neg_ratio`, và `llm_net_sentiment`.
7. WHEN A6 hoàn tất, THE LLM_Annotator SHALL ghi tập đặc trưng ra
   `data/features/keyword_features_A6.csv`.
8. IF một lời gọi tới mô hình Gemini Flash thất bại, THEN THE LLM_Annotator SHALL ghi lại bài
   viết bị lỗi và tiếp tục xử lý các bài còn lại.

### Requirement 9: A4 và A5 — Tầng biểu diễn văn bản tùy chọn

**User Story:** Là một nghiên cứu sinh, tôi muốn có thể mở rộng thêm hai tầng biểu diễn văn
bản tùy chọn khi còn thời gian, để tăng độ đầy đủ của bảng so sánh biểu diễn văn bản.

#### Acceptance Criteria

1. WHERE thành phần A4 được kích hoạt, THE TFIDF_CrossTicker_Builder SHALL tính trọng số
   TF-IDF cross-ticker và ghi tập đặc trưng ra `data/features/keyword_features_A4.csv`.
2. WHERE thành phần A5 được kích hoạt, THE Embedding_Builder SHALL tính đặc trưng nhúng bằng
   PhoBERT và ghi tập đặc trưng ra `data/features/keyword_features_A5.csv`.
3. WHERE thành phần A4 hoặc A5 được kích hoạt, THE Comparison_Reporter SHALL tạo báo cáo so
   sánh với Baseline_v0 giống như các thí nghiệm bắt buộc.

### Requirement 10: B3 — Phân tích theo phân khúc ngành và vốn hóa

**User Story:** Là một nghiên cứu sinh, tôi muốn chạy lại huấn luyện và kiểm định từ khóa
riêng cho từng ngành và nhóm vốn hóa, để tìm xem tín hiệu văn bản có mạnh hơn ở phân khúc cụ
thể không.

#### Acceptance Criteria

1. THE Segmentation_Analyzer SHALL gán một nhãn ngành cho mỗi ticker dựa trên ánh xạ ngành
   được khai báo tường minh.
2. THE Segmentation_Analyzer SHALL gán mỗi ticker vào một nhóm vốn hóa: large-cap (VN30) hoặc
   mid-cap (phần mở rộng HOSE-80).
3. WHEN Segmentation_Analyzer chạy phân tích cho một phân khúc, THE Segmentation_Analyzer
   SHALL huấn luyện lại Config_A, Config_B, và Config_C và tính Delta_CA chỉ trên các ticker
   thuộc phân khúc đó, dùng cùng Train_Cutoff và cùng quy trình chia thời gian.
4. WHEN Segmentation_Analyzer kiểm định ý nghĩa từ khóa cho một phân khúc, THE
   Segmentation_Analyzer SHALL áp dụng thủ tục BH_FDR trên tập từ khóa trong phân khúc đó.
5. THE Segmentation_Analyzer SHALL báo cáo số lượng mẫu của mỗi phân khúc trong kết quả.
6. WHEN B3 hoàn tất, THE Segmentation_Analyzer SHALL ghi kết quả ra
   `reports/segmentation_analysis.csv` và `reports/segmentation_keyword_sig.csv`.

### Requirement 11: B1 — Distant supervision từ suất sinh lời ngắn hạn

**User Story:** Là một nghiên cứu sinh, tôi muốn tạo nhãn nhiễu từ suất sinh lời ngắn hạn sau
ngày đăng bài và huấn luyện bộ phân loại sentiment cấp bài viết, để kiểm tra tín hiệu ở cấp
độ từng bài mà tổng hợp theo quý có thể làm mờ.

#### Acceptance Criteria

1. WHEN Distant_Supervision_Module xử lý một bài viết đăng vào ngày giao dịch d về ticker t,
   THE Distant_Supervision_Module SHALL tính suất sinh lời của ticker t trong khoảng ba ngày
   giao dịch từ d+1 đến d+3.
2. IF suất sinh lời trong khoảng d+1 đến d+3 lớn hơn hoặc bằng cộng hai phần trăm, THEN THE
   Distant_Supervision_Module SHALL gán Noisy_Label `positive` cho bài viết đó.
3. IF suất sinh lời trong khoảng d+1 đến d+3 nhỏ hơn hoặc bằng trừ hai phần trăm, THEN THE
   Distant_Supervision_Module SHALL gán Noisy_Label `negative` cho bài viết đó.
4. WHERE suất sinh lời trong khoảng d+1 đến d+3 nằm giữa trừ hai phần trăm và cộng hai phần
   trăm, THE Distant_Supervision_Module SHALL gán Noisy_Label `neutral` cho bài viết đó.
5. IF khoảng ngày giao dịch d+1 đến d+3 vượt qua ranh giới của Period_q chứa ngày d, THEN THE
   Distant_Supervision_Module SHALL cắt khoảng tính suất sinh lời tại ranh giới của Period_q
   đó.
6. THE Distant_Supervision_Module SHALL huấn luyện bộ phân loại sentiment cấp bài viết chỉ
   trên các bài viết đăng trong giai đoạn train, tức các kỳ trước Train_Cutoff.
7. WHEN Distant_Supervision_Module tạo đặc trưng cho Period_q, THE Distant_Supervision_Module
   SHALL tổng hợp xác suất dự đoán của bộ phân loại chỉ trên các bài đăng trong Period_q thành
   các đặc trưng `ds_pos_prob_mean` và `ds_net_sentiment`.
8. WHEN B1 hoàn tất, THE Distant_Supervision_Module SHALL ghi tập đặc trưng ra
   `data/features/keyword_features_B1.csv` và báo cáo AUC của bộ phân loại trên nhãn nhiễu ở
   cấp độ bài viết trong `reports/distant_supervision_report.md`.

### Requirement 12: B4 và B5 — Thí nghiệm có điều kiện tùy chọn

**User Story:** Là một nghiên cứu sinh, tôi muốn có thể chạy thêm hai thí nghiệm có điều kiện
tùy chọn khi còn thời gian, để mở rộng phân tích tín hiệu có điều kiện.

#### Acceptance Criteria

1. WHERE thành phần B4 được kích hoạt, THE Spillover_Builder SHALL tính điểm sentiment trung
   bình toàn ngành trong Period_q và gán ngược lại cho từng ticker trong ngành mà không dùng
   chính tin của ticker đó.
2. WHERE thành phần B4 được kích hoạt, THE Spillover_Builder SHALL chỉ dùng tin thuộc
   Period_q khi tính điểm sentiment ngành.
3. WHERE thành phần B5 được kích hoạt, THE Anomaly_Detector SHALL tính đặc trưng nhị phân
   `news_spike` bằng một khi số lượng tin của Period_q vượt trung bình cộng hai lần độ lệch
   chuẩn tính trên tập train.

### Requirement 13: So sánh và phân tích đầy đủ với kết quả cũ

**User Story:** Là một nghiên cứu sinh, tôi muốn mỗi thí nghiệm khi hoàn thành sinh ra một
báo cáo so sánh và phân tích đầy đủ với kết quả cũ, để có thể viết trực tiếp vào luận văn.

#### Acceptance Criteria

1. WHEN một thí nghiệm hoàn tất, THE Comparison_Reporter SHALL tạo một bảng so sánh trực tiếp
   đặt kết quả của thí nghiệm cạnh kết quả Baseline_v0, gồm balanced accuracy của Config_A,
   balanced accuracy của Config_C, và Delta_CA cho từng thuật toán trong bốn thuật toán
   LightGBM, Random Forest, XGBoost, và Logistic Regression.
2. WHEN một thí nghiệm hoàn tất, THE Comparison_Reporter SHALL báo cáo số lượng từ khóa hoặc
   đặc trưng đạt ý nghĩa sau BH_FDR trong thí nghiệm, đặt cạnh con số `0/71` của Baseline_v0.
3. WHEN một thí nghiệm hoàn tất, THE Comparison_Reporter SHALL báo cáo tỷ lệ đóng góp SHAP
   của nhóm đặc trưng văn bản trong thí nghiệm, đặt cạnh con số `32%` của Baseline_v0.
4. WHEN một thí nghiệm hoàn tất, THE Comparison_Reporter SHALL chạy McNemar_Test so sánh dự
   đoán của Config_C thí nghiệm với Config_C của Baseline_v0 trên cùng tập kiểm tra và SHALL
   báo cáo giá trị p.
5. WHEN một thí nghiệm hoàn tất, THE Comparison_Reporter SHALL viết nhận xét trả lời tường
   minh cho từng giả thuyết H1, H2, và H3 dựa trên kết quả thí nghiệm.
6. WHEN một thí nghiệm hoàn tất, THE Comparison_Reporter SHALL viết phân tích nguyên nhân
   liên hệ kết quả với ba giải thích lý thuyết: Semi-strong EMH, within-period absorption, và
   giới hạn corpus.
7. WHEN một thí nghiệm hoàn tất, THE Comparison_Reporter SHALL viết một kết luận nêu vị trí
   của kết quả trong cấu trúc luận văn và tác động tới kết luận Chương 5.
8. WHERE nhiều thí nghiệm Hướng A đã hoàn tất, THE Comparison_Reporter SHALL tạo một bảng
   tổng hợp Delta_CA của bốn tầng biểu diễn văn bản (tần suất thô v0, A2 negation, A1a group
   sentiment, A6 LLM sentiment) cho từng thuật toán.

### Requirement 14: So sánh công bằng qua cùng pipeline

**User Story:** Là một nghiên cứu sinh, tôi muốn mọi biến thể đặc trưng đi qua cùng một
pipeline huấn luyện, để so sánh chỉ phản ánh khác biệt về tập đặc trưng.

#### Acceptance Criteria

1. WHEN Model_Trainer huấn luyện trên một tập đặc trưng có phiên bản, THE Model_Trainer SHALL
   dùng cùng bốn thuật toán, cùng siêu tham số, và cùng quy trình chia thời gian như
   Baseline_v0.
2. THE Model_Trainer SHALL giữ nguyên tập 16 đặc trưng kỹ thuật của Config_A ở mọi thí
   nghiệm.
3. WHEN một thí nghiệm thay đổi tập đặc trưng từ khóa, THE Model_Trainer SHALL chỉ thay đổi
   Config_B và Config_C mà không thay đổi Config_A.

### Requirement 15: Khả năng tái lập và kiểm thử

**User Story:** Là một nghiên cứu sinh, tôi muốn các hàm mới có kiểm thử và các artifact phụ
thuộc bên ngoài được đóng băng, để kết quả tái lập được và bảo vệ trước hội đồng.

#### Acceptance Criteria

1. THE Experiment_System SHALL cung cấp kiểm thử tự động cho mỗi hàm mới xử lý đặc trưng, gồm
   hàm khớp phủ định A2, hàm tổng hợp sentiment nhóm A1, hàm velocity và novelty A3, và hàm
   gán nhãn nhiễu B1.
2. THE Experiment_System SHALL commit tệp `data/news/annotated/llm_sentiment.csv` vào kho mã
   nguồn cùng phiên bản mô hình được ghi trong tệp.
3. WHEN một kiểm thử kiểm tra hàm gán nhãn nhiễu B1, THE kiểm thử SHALL xác minh rằng khoảng
   tính suất sinh lời không vượt qua ranh giới Period_q chứa ngày đăng bài.
4. WHEN toàn bộ kiểm thử được chạy, THE Experiment_System SHALL không làm giảm số kiểm thử
   đang pass so với trước khi thêm tính năng.
