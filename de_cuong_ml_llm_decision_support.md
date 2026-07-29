# Đề cương nghiên cứu luận văn thạc sĩ

## Tên đề tài dự kiến

**Ứng dụng hỗ trợ quyết định đầu tư cổ phiếu Việt Nam dựa trên tín hiệu học máy, LLM tạo luận điểm đầu tư và theo dõi sau khuyến nghị**

Tên tiếng Anh dự kiến:

**An ML-Led Investment Decision Support System for Vietnamese Stocks with LLM-Based Investment Thesis Generation and Post-Recommendation Monitoring**

---

## 1. Bối cảnh nghiên cứu

Các nghiên cứu dự báo cổ phiếu thường tập trung vào việc dự báo xu hướng giá hoặc xác suất tăng/giảm trong một kỳ tương lai. Mô hình học máy có thể khai thác tốt dữ liệu kỹ thuật như lợi suất, động lượng, độ biến động, RSI, MACD, đường trung bình, Bollinger Bands và khối lượng giao dịch. Tuy nhiên, trong thực tế đầu tư, tín hiệu dự báo tích cực chưa đủ để tạo thành một quyết định đầu tư có thể sử dụng.

Nhà đầu tư không chỉ cần biết mã nào có xác suất tăng cao, mà còn cần hiểu vì sao mã đó được chọn, luận điểm đầu tư ban đầu là gì, thông tin nào ủng hộ hoặc làm suy yếu luận điểm, khi nào cần xem xét lại quyết định, và sau kỳ nắm giữ thì quyết định đúng hay sai vì nguyên nhân nào. Khoảng cách giữa **tín hiệu mô hình** và **quyết định đầu tư có thể quản trị** là vấn đề nghiên cứu chính của đề tài.

Kết quả thực nghiệm hiện có trong dự án cho thấy mô hình học máy dựa trên đặc trưng kỹ thuật có hiệu quả định lượng tốt: chiến lược mô hình đạt lợi nhuận tích lũy net khoảng 60,3% so với benchmark buy-and-hold khoảng 25,4%, Sharpe ratio khoảng 1,05, và walk-forward vượt benchmark ở 3/3 cutoff. Robustness test trên 125 mã HOSE+HNX cho Balanced Accuracy khoảng 0,761 và AUC khoảng 0,831. Ngược lại, các đặc trưng tin tức dạng tần suất từ khóa và cả các biểu diễn văn bản/LLM sentiment không cải thiện dự báo một cách ổn định. Vì vậy, đề tài mới không tiếp tục ép tin tức làm biến dự báo trực tiếp, mà chuyển tin tức thành lớp bằng chứng định tính phục vụ giải thích, theo dõi và hậu kiểm.

---

## 2. Mục tiêu nghiên cứu

### 2.1. Mục tiêu tổng quát

Xây dựng và đánh giá một prototype hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam kết hợp tín hiệu học máy, tin tức công khai và LLM nhằm tạo, theo dõi và hậu kiểm luận điểm đầu tư theo vòng đời quyết định.

### 2.2. Mục tiêu cụ thể

1. Tái sử dụng và đóng gói mô hình học máy dựa trên đặc trưng kỹ thuật để tạo tín hiệu định lượng và xếp hạng cổ phiếu.
2. Đánh giá tín hiệu ML bằng chỉ số phân loại và backtest đầu tư long-only trên thị trường cổ phiếu Việt Nam.
3. Thiết kế lớp evidence pack gồm ML score, rank, technical drivers, SHAP/feature importance và tin tức liên quan theo nguyên tắc point-in-time.
4. Thiết kế cơ chế LLM tạo investment thesis/decision card có cấu trúc, chỉ dựa trên evidence pack.
5. Thiết kế cơ chế monitoring sau khuyến nghị để phát hiện thay đổi tín hiệu, thay đổi bối cảnh tin tức và rủi ro cần xem xét.
6. Thiết kế outcome review/hậu kiểm sau kỳ nắm giữ để đánh giá kết quả và rút kinh nghiệm.
7. Đánh giá hệ thống trên hai nhóm tiêu chí: hiệu quả định lượng của ML signal và chất lượng hỗ trợ quyết định của LLM decision card.

---

## 3. Câu hỏi nghiên cứu

**RQ1.** Mô hình học máy dựa trên đặc trưng kỹ thuật có tạo tín hiệu hữu ích cho việc lựa chọn cổ phiếu Việt Nam hay không?

**RQ2.** Chiến lược đầu tư long-only dựa trên ML signal/Top-K ranking có vượt benchmark như buy-and-hold, equal-weight hoặc VNINDEX theo các chỉ số return, Sharpe ratio và drawdown hay không?

**RQ3.** LLM decision card được tạo từ evidence pack có bám sát dữ liệu đầu vào, hạn chế hallucination, giải thích rõ tín hiệu ML và nêu rủi ro hữu ích cho người dùng hay không?

**RQ4.** Cơ chế monitoring và outcome review có giúp phát hiện các trường hợp tín hiệu suy yếu, bối cảnh thay đổi hoặc luận điểm đầu tư cần xem xét lại hay không?

---

## 4. Phạm vi nghiên cứu

| Tiêu chí | Phạm vi |
|---|---|
| Thị trường | Cổ phiếu Việt Nam, trọng tâm HOSE-80; robustness có thể dùng HOSE+HNX-125 đã kiểm thử |
| Giai đoạn dữ liệu | 2022–2026 theo dữ liệu hiện có |
| Dữ liệu giá | OHLCV ngày, tổng hợp theo kỳ dự báo |
| Dữ liệu tin tức | Tin tức công khai đã gắn ticker, ngày, nguồn, tiêu đề/tóm tắt/nội dung xử lý |
| Mô hình ML | Logistic Regression, Random Forest, XGBoost, LightGBM; trọng tâm mô hình kỹ thuật Config_A |
| LLM | Dùng để tạo thesis, update và review; không dùng để dự báo giá trực tiếp |
| Hình thức hệ thống | Prototype nghiên cứu, không phải hệ thống giao dịch tự động |
| Quyết định đầu tư | Long-only, hỗ trợ quyết định; nhà đầu tư là người ra quyết định cuối |

Đề tài không đưa ra khuyến nghị đầu tư thực tế và không cam kết lợi nhuận tương lai. Kết quả backtest chỉ có giá trị học thuật trong phạm vi dữ liệu, giả định và chi phí mô phỏng.

---

## 5. Đóng góp dự kiến

### 5.1. Chuyển từ dự báo cổ phiếu sang quản trị quyết định đầu tư

Đề tài không dừng ở dự báo tăng/giảm, mà tổ chức quy trình quyết định theo vòng đời:

**select → explain → monitor → update → review**

Mỗi khuyến nghị được lưu thành decision record có tín hiệu ML, bằng chứng, luận điểm, rủi ro, trigger theo dõi và hậu kiểm.

### 5.2. ML signal làm lõi định lượng

Mô hình học máy kỹ thuật cung cấp xác suất, rank và danh sách cổ phiếu ứng viên. Kết quả ML được đánh giá bằng Balanced Accuracy, AUC, backtest return, Sharpe ratio, max drawdown, hit rate và walk-forward.

### 5.3. Tin tức như evidence layer

Kết quả cũ cho thấy đặc trưng tin tức/từ khóa không cải thiện dự báo ổn định. Do đó, tin tức được dùng làm bằng chứng định tính cho LLM, không phải biến dự báo chính.

### 5.4. LLM decision card có kiểm soát

LLM không được tự do đưa ra dự báo. LLM chỉ được tạo decision card từ evidence pack, với yêu cầu trích dẫn evidence ID và không thêm thông tin ngoài input.

### 5.5. Monitoring và hậu kiểm

Hệ thống theo dõi sau khuyến nghị: thay đổi ML score/rank, tín hiệu kỹ thuật, tin mới, drawdown và outcome sau kỳ nắm giữ. Hậu kiểm giúp rút kinh nghiệm và đánh giá chất lượng luận điểm ban đầu.

---

## 6. Kiến trúc hệ thống đề xuất

### 6.1. ML Signal Engine

Đầu vào:

- Dữ liệu giá và khối lượng.
- Đặc trưng kỹ thuật: RSI, MACD, SMA, EMA, Bollinger Bands, return, volatility, volume, lag return.

Đầu ra:

- `pred_proba_up`.
- `pred_label`.
- Rank cổ phiếu.
- Buy Candidate / Watchlist / Avoid.
- Feature importance hoặc SHAP drivers.

### 6.2. News Evidence Layer

Mỗi tin gồm:

- `evidence_id`.
- `ticker`.
- `published_at`.
- `source`.
- `title`.
- `summary`.
- `event_type` nếu xác định được.
- `relevance` nếu được chấm thủ công hoặc rule-based.

### 6.3. Evidence Pack Builder

Với mỗi mã cổ phiếu ứng viên tại thời điểm ra quyết định, evidence pack gồm:

- ticker, decision date, holding horizon.
- ML probability/rank/signal class.
- technical snapshot.
- top drivers từ SHAP/feature importance.
- news evidence trước decision date.
- các cảnh báo dữ liệu: thiếu tin, coverage thấp, ticker matching không chắc chắn.

### 6.4. LLM Investment Thesis Generator

LLM sinh decision card gồm:

- mã cổ phiếu và ngày ra quyết định.
- trạng thái hỗ trợ quyết định.
- luận điểm đầu tư chính.
- yếu tố hỗ trợ.
- yếu tố cần lưu ý.
- rủi ro cần theo dõi.
- trigger xem xét lại.
- thời điểm review.
- bằng chứng tham chiếu.

### 6.5. Post-Recommendation Monitoring & Outcome Review

Monitoring theo dõi:

- ML score/rank thay đổi.
- ticker rơi khỏi Top-K.
- chỉ báo kỹ thuật đảo chiều.
- tin mới trái chiều hoặc rủi ro.
- drawdown vượt ngưỡng.
- kết quả sau holding period.

Outcome review ghi:

- return thực tế.
- benchmark return.
- decision đúng/sai.
- yếu tố nào trong thesis đúng/sai.
- bài học rút ra.

---

## 7. Thiết kế thực nghiệm

### 7.1. Đánh giá ML Signal Engine

Chỉ số phân loại:

- Balanced Accuracy.
- AUC-ROC.
- F1-macro.
- Precision/Recall.

Chỉ số đầu tư:

- cumulative return.
- mean period return.
- Sharpe ratio.
- max drawdown.
- hit rate.
- transaction cost.
- Top-K portfolio performance.

Baseline:

- majority class.
- naive momentum.
- buy-and-hold equal.
- equal-weight rebalanced.
- VNINDEX nếu có dữ liệu phù hợp.

### 7.2. Đánh giá News Evidence Layer

- Độ phủ tin theo ticker/kỳ.
- Tỷ lệ tin có nguồn/ngày/title hợp lệ.
- Tỷ lệ evidence trước decision date.
- Tỷ lệ matching đúng ticker trên mẫu thủ công.
- Tỷ lệ evidence liên quan/không liên quan/không rõ.

### 7.3. Đánh giá LLM Decision Card

Rubric 1–5 điểm:

1. Faithfulness: bám sát evidence.
2. Hallucination control: không thêm dữ kiện ngoài input.
3. ML explanation: giải thích tín hiệu định lượng rõ.
4. Risk awareness: nêu rủi ro phù hợp.
5. Monitoring usefulness: trigger theo dõi cụ thể.
6. Clarity/usefulness: dễ hiểu và hữu ích cho người đọc.

So sánh:

- Rule-based template.
- LLM với ML-only evidence.
- LLM với full evidence pack.

### 7.4. Đánh giá Monitoring

Dùng case study 5–10 khuyến nghị lịch sử:

- Case thành công.
- Case thất bại.
- Case thiếu tin tức.
- Case tín hiệu đảo chiều.
- Case tin mới trái chiều.

Mục tiêu không phải chứng minh monitoring cải thiện return ở quy mô lớn, mà chứng minh cơ chế có thể phát hiện và giải thích thay đổi bối cảnh.

### 7.5. Đánh giá Outcome Review

Sau holding period:

- tính realized return.
- so sánh benchmark.
- kiểm tra thesis ban đầu.
- phân loại nguyên nhân: ML signal, kỹ thuật, news, market regime, thiếu dữ liệu.

---

## 8. Quy trình chống rò rỉ dữ liệu

### 8.1. Backtest mode

Chỉ dùng dữ liệu đã có tại thời điểm quyết định:

- dữ liệu giá/kỹ thuật đến kỳ q hoặc ngày t.
- tin tức có `published_at <= decision_date`.
- không dùng return/label/outcome của kỳ q+1 trong decision card.
- scaler/imputer/feature selection chỉ fit trên train.
- Top-K được chọn bằng score tại thời điểm đó.

### 8.2. LLM mode

Prompt tạo thesis ban đầu không được chứa:

- realized return tương lai.
- nhãn q+1.
- outcome review.
- bài viết sau decision date.

Outcome review là bước riêng sau holding period, lúc đó mới được dùng kết quả thực tế.

### 8.3. Live advisory mode

Nếu minh họa dữ liệu mới nhất, chỉ dùng để demo hệ thống; không dùng để đánh giá hiệu quả lịch sử.

---

## 9. Kết quả kỳ vọng

1. Một ML Signal Engine có khả năng tạo tín hiệu và xếp hạng cổ phiếu tốt hơn baseline.
2. Một backtest long-only cho thấy hiệu quả đầu tư trong phạm vi giả định mô phỏng.
3. Một evidence pack schema đảm bảo point-in-time và chống rò rỉ dữ liệu.
4. Một LLM decision card schema và prompt template có kiểm soát hallucination.
5. Một rubric đánh giá decision card.
6. Một bộ sample decision cards và monitoring/outcome review cases.
7. Một bản luận văn thể hiện được đóng góp: từ dự báo sang hỗ trợ quản trị quyết định đầu tư.

---

## 10. Giới hạn nghiên cứu

1. Prototype không thay thế nhà đầu tư.
2. LLM không dự báo giá và không tạo khuyến nghị đầu tư độc lập.
3. Tin tức công khai có thể thiếu hoặc không đều theo ticker/kỳ.
4. Đánh giá LLM có yếu tố định tính và chủ quan.
5. Backtest theo kỳ không mô phỏng đầy đủ khớp lệnh từng phiên, slippage và tác động thị trường.
6. Kết quả phụ thuộc dữ liệu 2022–2026 và universe được chọn.
7. Hệ thống cần kiểm soát nghiêm ngặt rò rỉ dữ liệu theo thời gian.

---

## 11. Định vị cuối cùng

Đề tài tập trung vào hệ thống hỗ trợ quyết định đầu tư dựa trên ML. Mô hình học máy cung cấp tín hiệu định lượng. Tin tức cung cấp bối cảnh và bằng chứng. LLM giúp chuyển evidence thành luận điểm đầu tư có cấu trúc, hỗ trợ theo dõi và hậu kiểm quyết định.

Luận văn không chứng minh LLM dự báo giá tốt hơn mô hình ML. Đóng góp chính là thiết kế và đánh giá một quy trình decision-support có kiểm soát, minh bạch và có khả năng hậu kiểm.
