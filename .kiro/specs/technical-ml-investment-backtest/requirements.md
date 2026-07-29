# Requirements Document

## Introduction

Tính năng `technical-ml-investment-backtest` nâng phần "machine learning trên đặc trưng kỹ
thuật" của luận văn thạc sĩ Khoa học Dữ liệu (dự báo xu hướng giá HOSE-80) từ mức *đánh giá
độ chính xác dự báo* lên mức *đánh giá giá trị đầu tư thực tế*. Đây là trụ đóng góp **dương**
của luận văn, đối trọng với trụ khám phá (đặc trưng văn bản — kết quả âm).

Hiện trạng: mô hình tốt nhất (LightGBM, Config_A chỉ đặc trưng kỹ thuật) đạt balanced accuracy
≈ 0,76 và AUC ≈ 0,82 trên tập test 400 mẫu (80 mã × 5 quý sau cutoff 2025Q1). Tuy nhiên luận
văn mới đo *accuracy*, chưa đo *lợi nhuận đầu tư* — trong khi mục tiêu đề tài là "hỗ trợ tăng
hiệu quả đầu tư". Tính năng này lấp bốn khoảng trống:

- **Backtest chiến lược đầu tư:** dùng dự đoán mô hình để mô phỏng quyết định mua/bán và đo
  lợi nhuận, so với các benchmark (mua-và-giữ, đều tay).
- **Kiểm tra độ ổn định theo thời gian:** đánh giá mô hình qua nhiều cutoff (walk-forward) để
  chứng minh kết quả không phụ thuộc một điểm chia.
- **Diễn giải mô hình kỹ thuật:** xác định đặc trưng kỹ thuật nào quan trọng nhất (SHAP /
  permutation importance) cho Config_A.
- **Xác minh chống rò rỉ dữ liệu:** kiểm tra tường minh rằng đặc trưng kỹ thuật của kỳ q
  không dùng thông tin của kỳ q+1, để bảo vệ con số accuracy cao trước hội đồng.

Ràng buộc cốt lõi: tái sử dụng pipeline huấn luyện hiện có (`pipeline/task10_train.py`) để so
sánh nhất quán; không sửa hành vi mặc định của pipeline sản xuất; mọi tính toán tuân thủ ranh
giới thời gian nghiêm ngặt (không rò rỉ tương lai); và mọi kết quả đều sinh ra artifact và báo
cáo có thể đưa trực tiếp vào luận văn.

**Đặc thù thị trường chứng khoán cơ sở Việt Nam (ràng buộc mô phỏng bắt buộc):** Thị trường
cơ sở VN chỉ cho phép kiếm lời **một chiều — mua (long-only)**; không có bán khống. Do đó
chiến lược backtest CHỈ được mua các mã dự báo "tăng", tuyệt đối không có vế bán khống mã dự
báo "giảm" (muốn short phải qua thị trường phái sinh — ngoài phạm vi). Ngoài ra: chu kỳ thanh
toán T+2 (cổ phiếu mua về tài khoản sau 2 ngày làm việc mới bán được), biên độ giá HOSE ±7%/
phiên, lô giao dịch tối thiểu 100 cổ phiếu. Vì backtest theo đơn vị quý và dùng suất sinh lời
kỳ, các ràng buộc T+2/biên độ/lô lẻ được xử lý bằng **giả định tường minh** (vốn đủ lớn để bỏ
qua hiệu ứng lô lẻ; không lướt sóng trong kỳ; bỏ qua trượt giá) và được ghi rõ trong báo cáo.

## Glossary

- **Backtest_System**: Toàn bộ hệ thống mới xây dựng trong tính năng này.
- **Technical_Model**: Mô hình ML huấn luyện trên Config_A (chỉ đặc trưng kỹ thuật) qua pipeline
  hiện có.
- **Strategy_Simulator**: Thành phần mô phỏng chiến lược đầu tư từ dự đoán của Technical_Model.
- **Benchmark_Strategy**: Chiến lược tham chiếu để so sánh — gồm buy-and-hold toàn danh mục và
  chiến lược phân bổ đều (equal-weight).
- **Performance_Evaluator**: Thành phần tính các chỉ số hiệu quả đầu tư (lợi nhuận tích lũy,
  CAGR, Sharpe, max drawdown, hit rate).
- **Walk_Forward_Evaluator**: Thành phần đánh giá độ ổn định của Technical_Model qua nhiều
  cutoff theo kiểu cửa sổ tịnh tiến.
- **Model_Interpreter**: Thành phần tính SHAP và permutation importance cho Config_A.
- **Leakage_Auditor**: Thành phần kiểm tra tường minh việc không rò rỉ dữ liệu thời gian trong
  đặc trưng kỹ thuật.
- **Backtest_Reporter**: Thành phần sinh báo cáo tổng hợp cho tính năng.
- **Prediction_Signal**: Nhãn dự đoán (tăng / không tăng) và/hoặc xác suất dự đoán của
  Technical_Model cho mỗi (ticker, Period_q) trong tập test.
- **Holding_Period**: Kỳ nắm giữ tương ứng một Period_q (quý), khớp định nghĩa nhãn "giá trung
  bình kỳ kế tiếp".
- **Period_q**: Một kỳ quý cụ thể trong chuỗi thời gian.
- **Train_Cutoff**: Ranh giới chia train/test theo thời gian, mặc định `2025Q1`.
- **Transaction_Cost**: Chi phí giao dịch mô phỏng, gồm hai cấu phần tách bạch: phí môi giới
  (brokerage) áp cho cả lượt mua và lượt bán, và thuế thu nhập cá nhân áp chỉ cho lượt bán.
- **Brokerage_Fee**: Phí môi giới trên giá trị giao dịch mỗi lượt (mua hoặc bán); mặc định
  0,15%, cấu hình được (trần quy định thị trường VN là 0,5%).
- **Sell_Tax**: Thuế thu nhập cá nhân trên giá trị bán, cố định 0,1% theo quy định VN, áp chỉ
  khi bán.
- **Period_Return**: Suất sinh lời của một (ticker, Period_q), lấy từ cột `return` trong
  `master_with_labels.csv` (suất sinh lời tới kỳ kế tiếp).
- **Cumulative_Return**: Lợi nhuận tích lũy của một chiến lược qua các kỳ test.
- **Sharpe_Ratio**: Tỷ số Sharpe của chuỗi lợi nhuận theo kỳ của một chiến lược.
- **Max_Drawdown**: Mức sụt giảm tối đa từ đỉnh tới đáy của đường lợi nhuận tích lũy.

## Requirements

### Requirement 1: Tạo tín hiệu dự đoán từ mô hình kỹ thuật

**User Story:** Là một nghiên cứu sinh, tôi muốn lấy được nhãn và xác suất dự đoán của mô hình
kỹ thuật cho từng (ticker, kỳ) trong tập test, để làm đầu vào cho mô phỏng đầu tư.

#### Acceptance Criteria

1. WHEN Backtest_System tạo tín hiệu dự đoán, THE Backtest_System SHALL huấn luyện Technical_Model
   trên Config_A qua pipeline hiện có với cùng Train_Cutoff và cùng quy trình chia thời gian như
   baseline.
2. WHEN Technical_Model dự đoán trên tập test, THE Backtest_System SHALL xuất cho mỗi
   (ticker, Period_q) trong tập test một Prediction_Signal gồm nhãn dự đoán và xác suất dự đoán
   lớp "tăng".
3. THE Backtest_System SHALL gắn mỗi Prediction_Signal với Period_Return tương ứng của cùng
   (ticker, Period_q) lấy từ `master_with_labels.csv`.
4. THE Backtest_System SHALL cho phép chọn thuật toán mô hình trong bốn thuật toán hiện có
   (LightGBM, Random Forest, XGBoost, Logistic Regression) và mặc định dùng mô hình có balanced
   accuracy cao nhất trên Config_A.
5. IF một (ticker, Period_q) trong tập test thiếu Period_Return, THEN THE Backtest_System SHALL
   loại (ticker, Period_q) đó khỏi mô phỏng và ghi lại số lượng bị loại.

### Requirement 2: Mô phỏng chiến lược đầu tư từ dự đoán (long-only)

**User Story:** Là một nghiên cứu sinh, tôi muốn chuyển dự đoán mô hình thành quyết định đầu tư
long-only theo kỳ đúng đặc thù thị trường cơ sở VN, để đo mô hình tạo ra bao nhiêu lợi nhuận
thay vì chỉ đo độ chính xác.

#### Acceptance Criteria

1. WHEN Strategy_Simulator chạy cho một Period_q trong tập test, THE Strategy_Simulator SHALL
   chọn danh mục gồm các ticker mà Technical_Model dự đoán "tăng" ở Period_q đó.
2. THE Strategy_Simulator SHALL chỉ thực hiện vị thế mua (long) và SHALL KHÔNG mô phỏng bất kỳ
   vị thế bán khống (short) nào, phản ánh đúng ràng buộc một chiều của thị trường cơ sở VN.
3. THE Strategy_Simulator SHALL phân bổ vốn đều cho các ticker được chọn trong mỗi Period_q.
4. WHERE không có ticker nào được dự đoán "tăng" trong một Period_q, THE Strategy_Simulator SHALL
   giữ tiền mặt cho kỳ đó với lợi nhuận kỳ bằng không.
5. THE Strategy_Simulator SHALL tính lợi nhuận danh mục của mỗi Period_q bằng trung bình
   Period_Return của các ticker được chọn trong kỳ đó.
6. THE Strategy_Simulator SHALL hỗ trợ một biến thể tùy chọn xếp hạng theo xác suất dự đoán và
   chỉ chọn top-N ticker có xác suất "tăng" cao nhất mỗi kỳ (vẫn thuần long-only).
7. THE Strategy_Simulator SHALL chỉ dùng thông tin của Period_q hoặc các kỳ trước Period_q khi
   ra quyết định cho Period_q.
8. THE Strategy_Simulator SHALL ghi rõ các giả định thị trường cơ sở VN được áp dụng: long-only,
   chu kỳ thanh toán T+2, biên độ giá HOSE ±7%, lô tối thiểu 100 cổ phiếu, giả định vốn đủ lớn
   để bỏ qua hiệu ứng lô lẻ và bỏ qua trượt giá.

### Requirement 3: Chi phí giao dịch

**User Story:** Là một nghiên cứu sinh, tôi muốn tính chi phí giao dịch sát thực tế thị trường
Việt Nam vào mô phỏng, để lợi nhuận báo cáo phản ánh điều kiện thực tế và tránh bị hội đồng
phản biện.

#### Acceptance Criteria

1. THE Strategy_Simulator SHALL mô hình hóa Transaction_Cost thành hai cấu phần tách bạch:
   Brokerage_Fee (mặc định 0,15%, cấu hình được) áp cho cả lượt mua và lượt bán, và Sell_Tax
   (mặc định 0,1%, cấu hình được) áp chỉ cho lượt bán.
2. WHEN Strategy_Simulator mua một phần vốn vào một ticker ở Period_q, THE Strategy_Simulator
   SHALL tính Brokerage_Fee trên giá trị mua đó.
3. WHEN Strategy_Simulator bán một phần vốn khỏi một ticker giữa Period_q và Period_q kế tiếp,
   THE Strategy_Simulator SHALL tính cả Brokerage_Fee và Sell_Tax trên giá trị bán đó.
4. WHEN thành phần danh mục ở Period_q khác với Period_q trước, THE Strategy_Simulator SHALL chỉ
   áp Transaction_Cost trên phần vốn thực sự được mua vào hoặc bán ra (phần thay đổi), không áp
   trên phần vốn giữ nguyên vị thế.
5. THE Strategy_Simulator SHALL báo cáo lợi nhuận của chiến lược ở cả hai kịch bản có và không
   có Transaction_Cost, và ghi rõ tổng chi phí giao dịch tích lũy cùng round-trip cost hiệu dụng
   (xấp xỉ 0,40% cho một vòng mua-bán ở mức mặc định).

### Requirement 4: Chiến lược tham chiếu (benchmark)

**User Story:** Là một nghiên cứu sinh, tôi muốn so sánh chiến lược dựa trên mô hình với các
chiến lược tham chiếu, để chứng minh giá trị tăng thêm của mô hình.

#### Acceptance Criteria

1. THE Backtest_System SHALL tính một Benchmark_Strategy buy-and-hold phân bổ đều cho toàn bộ
   80 ticker qua các kỳ test.
2. THE Backtest_System SHALL tính một Benchmark_Strategy phân bổ đều tái cân bằng mỗi kỳ trên
   toàn bộ ticker có dữ liệu trong kỳ.
3. THE Backtest_System SHALL đo cùng bộ chỉ số hiệu quả cho chiến lược mô hình và mọi
   Benchmark_Strategy trên cùng khoảng thời gian test.

### Requirement 5: Chỉ số hiệu quả đầu tư

**User Story:** Là một nghiên cứu sinh, tôi muốn báo cáo bộ chỉ số hiệu quả đầu tư chuẩn, để
đánh giá chiến lược một cách toàn diện chứ không chỉ nhìn lợi nhuận thô.

#### Acceptance Criteria

1. THE Performance_Evaluator SHALL tính Cumulative_Return của mỗi chiến lược qua các kỳ test.
2. THE Performance_Evaluator SHALL tính lợi nhuận trung bình theo kỳ và độ lệch chuẩn theo kỳ
   của mỗi chiến lược.
3. THE Performance_Evaluator SHALL tính Sharpe_Ratio của mỗi chiến lược từ chuỗi lợi nhuận theo
   kỳ với lãi suất phi rủi ro cấu hình được (mặc định bằng không).
4. THE Performance_Evaluator SHALL tính Max_Drawdown của mỗi chiến lược từ đường
   Cumulative_Return.
5. THE Performance_Evaluator SHALL tính hit rate bằng tỷ lệ số kỳ có lợi nhuận danh mục dương
   của chiến lược mô hình.
6. WHEN Performance_Evaluator tổng hợp kết quả, THE Performance_Evaluator SHALL ghi bảng chỉ số
   của mọi chiến lược ra `reports/backtest_performance.csv`.

### Requirement 6: Đánh giá độ ổn định theo thời gian (walk-forward)

**User Story:** Là một nghiên cứu sinh, tôi muốn đánh giá mô hình qua nhiều điểm chia thời gian,
để chứng minh kết quả không phụ thuộc một cutoff duy nhất.

#### Acceptance Criteria

1. THE Walk_Forward_Evaluator SHALL huấn luyện lại và đánh giá Technical_Model tại một tập nhiều
   Train_Cutoff cấu hình được, mỗi lần chỉ dùng dữ liệu trước cutoff để huấn luyện.
2. WHEN Walk_Forward_Evaluator đánh giá tại một cutoff, THE Walk_Forward_Evaluator SHALL tính
   balanced accuracy và AUC của Technical_Model trên tập test tương ứng cutoff đó.
3. THE Walk_Forward_Evaluator SHALL chạy Strategy_Simulator và Performance_Evaluator cho từng
   cutoff và báo cáo Cumulative_Return của chiến lược mô hình theo từng cutoff.
4. WHEN Walk_Forward_Evaluator hoàn tất, THE Walk_Forward_Evaluator SHALL ghi kết quả theo cutoff
   ra `reports/walk_forward_results.csv`.
5. THE Walk_Forward_Evaluator SHALL không dùng bất kỳ dữ liệu nào thuộc kỳ tại hoặc sau cutoff
   khi huấn luyện mô hình cho cutoff đó.

### Requirement 7: Diễn giải mô hình kỹ thuật

**User Story:** Là một nghiên cứu sinh, tôi muốn biết đặc trưng kỹ thuật nào quan trọng nhất
trong mô hình, để tăng tính giải thích được của luận văn.

#### Acceptance Criteria

1. THE Model_Interpreter SHALL tính giá trị SHAP cho Technical_Model trên Config_A và xếp hạng
   16 đặc trưng kỹ thuật theo mean(|SHAP|).
2. THE Model_Interpreter SHALL tính permutation importance trên tập test cho Technical_Model
   theo balanced accuracy.
3. WHEN Model_Interpreter hoàn tất, THE Model_Interpreter SHALL ghi bảng xếp hạng tầm quan trọng
   đặc trưng ra `reports/technical_feature_importance.csv`.
4. THE Model_Interpreter SHALL sinh một biểu đồ tóm tắt tầm quan trọng đặc trưng và lưu vào
   thư mục `reports/`.

### Requirement 8: Kiểm toán rò rỉ dữ liệu thời gian

**User Story:** Là một nghiên cứu sinh, tôi muốn xác minh tường minh rằng đặc trưng kỹ thuật
không rò rỉ dữ liệu tương lai, để bảo vệ độ tin cậy của kết quả trước hội đồng.

#### Acceptance Criteria

1. THE Leakage_Auditor SHALL xác minh rằng với mỗi (ticker, Period_q), mọi đặc trưng kỹ thuật
   được tính chỉ từ dữ liệu giá thuộc Period_q hoặc các kỳ trước Period_q.
2. THE Leakage_Auditor SHALL xác minh rằng nhãn của Period_q dựa trên suất sinh lời tới kỳ kế
   tiếp và không xuất hiện dưới dạng đặc trưng đầu vào của cùng kỳ.
3. WHEN Leakage_Auditor phát hiện một đặc trưng có tương quan bất thường với nhãn tương lai vượt
   ngưỡng cấu hình được, THE Leakage_Auditor SHALL đánh dấu đặc trưng đó để rà soát thủ công.
4. THE Model_Trainer SHALL fit imputer và bộ chuẩn hóa chỉ trên tập train và áp dụng lên tập
   test khi tạo tín hiệu dự đoán.
5. WHEN Leakage_Auditor hoàn tất, THE Leakage_Auditor SHALL ghi kết quả kiểm toán ra
   `reports/leakage_audit.md`.

### Requirement 9: Báo cáo tổng hợp cho luận văn

**User Story:** Là một nghiên cứu sinh, tôi muốn một báo cáo tổng hợp phần ML kỹ thuật, để đưa
trực tiếp vào chương kết quả của luận văn.

#### Acceptance Criteria

1. WHEN toàn bộ tính năng hoàn tất, THE Backtest_Reporter SHALL sinh một báo cáo Markdown tổng
   hợp gồm bảng chỉ số hiệu quả của chiến lược mô hình cạnh mọi Benchmark_Strategy.
2. THE Backtest_Reporter SHALL đưa vào báo cáo kết quả walk-forward và nhận xét về độ ổn định.
3. THE Backtest_Reporter SHALL đưa vào báo cáo bảng xếp hạng tầm quan trọng đặc trưng kỹ thuật
   và tóm tắt kết quả kiểm toán rò rỉ dữ liệu.
4. THE Backtest_Reporter SHALL viết nhận xét trả lời tường minh câu hỏi liệu mô hình có tạo ra
   giá trị đầu tư vượt các benchmark hay không, kèm cảnh báo về giả định và giới hạn.
5. THE Backtest_Reporter SHALL ghi báo cáo ra `reports/technical_ml_backtest_report.md`.

### Requirement 10: Tái sử dụng pipeline và khả năng tái lập

**User Story:** Là một nghiên cứu sinh, tôi muốn tính năng tái dùng pipeline hiện có và có kiểm
thử, để kết quả tái lập được và không phá vỡ code sản xuất.

#### Acceptance Criteria

1. THE Backtest_System SHALL tái sử dụng các hàm huấn luyện hiện có của `pipeline/task10_train.py`
   để tạo Technical_Model và Prediction_Signal mà không sửa hành vi mặc định của pipeline.
2. THE Backtest_System SHALL đặt mã nguồn trong một thư mục tách biệt với pipeline sản xuất và
   với `experiments/`.
3. THE Backtest_System SHALL cung cấp kiểm thử tự động cho các hàm thuần mới, gồm hàm tính lợi
   nhuận danh mục theo kỳ, hàm tính Sharpe_Ratio, hàm tính Max_Drawdown, và hàm áp
   Transaction_Cost.
4. WHEN toàn bộ kiểm thử được chạy, THE Backtest_System SHALL không làm giảm số kiểm thử đang
   pass so với trước khi thêm tính năng.
5. THE Backtest_System SHALL cung cấp một điểm chạy dòng lệnh để thực thi toàn bộ backtest và
   sinh mọi artifact/báo cáo.
