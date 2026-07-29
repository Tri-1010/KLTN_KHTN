# Định hướng đề tài luận văn

## Tên đề tài dự kiến

**Ứng dụng hỗ trợ quyết định đầu tư cổ phiếu Việt Nam dựa trên tín hiệu học máy, LLM tạo luận điểm đầu tư và theo dõi sau khuyến nghị**

Tên tiếng Anh dự kiến:

**An ML-Led Investment Decision Support System for Vietnamese Stocks with LLM-Based Investment Thesis Generation and Post-Recommendation Monitoring**

---

# 1. Bối cảnh và vấn đề nghiên cứu

Trong các nghiên cứu và ứng dụng về dự báo cổ phiếu, mô hình học máy thường được sử dụng để dự báo xu hướng giá hoặc xác suất tăng/giảm của cổ phiếu trong một khoảng thời gian nhất định. Các mô hình này có thể khai thác tốt các đặc trưng kỹ thuật như xu hướng giá, động lượng, biến động, RSI, MACD, đường trung bình động và các tín hiệu thị trường khác. Tuy nhiên, trong thực tế đầu tư, một tín hiệu dự báo tích cực không đồng nghĩa ngay với một quyết định đầu tư hoàn chỉnh.

Nhà đầu tư không chỉ cần biết cổ phiếu nào có xác suất tăng cao, mà còn cần hiểu vì sao cổ phiếu đó được lựa chọn, luận điểm đầu tư ban đầu là gì, thông tin nào đang ủng hộ hoặc làm suy yếu luận điểm đó, khi nào cần xem xét lại quyết định và sau kỳ nắm giữ thì quyết định đó đúng hay sai vì nguyên nhân nào. Nói cách khác, khoảng cách giữa “tín hiệu mô hình” và “quyết định đầu tư có thể sử dụng” vẫn là một vấn đề quan trọng.

Gần đây, các hệ thống LLM và multi-agent trading đã được phát triển để phân tích kỹ thuật, tin tức, yếu tố cơ bản và đưa ra khuyến nghị mua/bán. Tuy nhiên, nhiều hệ thống tập trung vào việc tạo khuyến nghị tại một thời điểm, trong khi chưa nhấn mạnh đầy đủ đến việc quản trị vòng đời của một quyết định đầu tư: từ lúc tạo tín hiệu, hình thành luận điểm, theo dõi thay đổi sau khuyến nghị, cập nhật bối cảnh và hậu kiểm kết quả.

Do đó, luận văn đề xuất một hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam theo hướng không chỉ tạo tín hiệu mua/bán, mà còn quản trị toàn bộ vòng đời của khuyến nghị. Mô hình học máy đóng vai trò lõi định lượng để tạo danh sách cổ phiếu ứng viên. Tin tức công khai được thu thập và chuẩn hóa thành các bằng chứng định tính. LLM được sử dụng để tạo luận điểm đầu tư, giải thích lý do lựa chọn, nêu rủi ro cần theo dõi, cập nhật luận điểm khi có thông tin mới và hỗ trợ hậu kiểm kết quả sau kỳ nắm giữ.

---

# 2. Mục tiêu nghiên cứu

Mục tiêu tổng quát của luận văn là ứng dụng và đánh giá một hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam kết hợp tín hiệu học máy, tin tức công khai và LLM nhằm tạo, theo dõi và hậu kiểm luận điểm đầu tư.

Các mục tiêu cụ thể gồm:

1. Ứng dụng mô hình học máy sử dụng đặc trưng kỹ thuật để dự báo xu hướng hoặc xếp hạng cổ phiếu Việt Nam.

2. Sử dụng đầu ra của mô hình học máy để xây dựng danh sách cổ phiếu ứng viên đầu tư dựa trên thứ hạng hoặc mức độ hấp dẫn tương đối.

3. Ứng dụng lớp thu thập và xử lý tin tức công khai, trong đó tin tức được gắn mã cổ phiếu, ngày công bố, nguồn và loại sự kiện.

4. Thiết kế cơ chế tạo “investment thesis” bằng LLM dựa trên tín hiệu ML và thông tin tin tức liên quan.

5. Ứng dụng cơ chế theo dõi sau khuyến nghị nhằm phát hiện khi bối cảnh đầu tư thay đổi.

6. Thực hiện hậu kiểm kết quả sau kỳ nắm giữ để đánh giá hiệu quả và rút kinh nghiệm.

7. Đánh giá hệ thống trên cả hai khía cạnh: hiệu quả định lượng của mô hình ML và khả năng hỗ trợ quyết định của LLM.

---

# 3. Câu hỏi nghiên cứu

Luận văn tập trung vào một số câu hỏi nghiên cứu tổng quát sau:

**RQ1.** Mô hình học máy dựa trên đặc trưng kỹ thuật có thể cung cấp tín hiệu hữu ích cho việc lựa chọn cổ phiếu Việt Nam hay không?

**RQ2.** Việc bổ sung lớp thông tin tin tức vào pipeline lựa chọn cổ phiếu dựa trên tín hiệu học máy có giúp cải thiện hiệu quả danh mục đầu tư (đo bằng các chỉ số như return, Sharpe ratio, drawdown) so với chỉ sử dụng tín hiệu kỹ thuật hay không?

**RQ3.** Các luận điểm đầu tư được tạo bởi LLM dựa trên tín hiệu mô hình và dữ liệu tin tức có đạt mức độ nhất quán với dữ liệu đầu vào và có thể được đánh giá là hữu ích đối với người dùng theo các tiêu chí định tính hay không?

**RQ4.** Việc bổ sung cơ chế theo dõi và cập nhật sau khuyến nghị có giúp phát hiện sớm các trường hợp suy giảm tín hiệu và cải thiện hiệu quả danh mục so với chiến lược không theo dõi hay không?

---

# 4. Phạm vi nghiên cứu

Luận văn tập trung vào thị trường cổ phiếu Việt Nam, với phạm vi nghiên cứu linh hoạt về số lượng mã cổ phiếu tùy thuộc vào khả năng thu thập và xử lý dữ liệu. Universe có thể mở rộng từ nhóm cổ phiếu vốn hóa lớn đến các mã có thanh khoản và mức độ phủ tin tức phù hợp. Tần suất đánh giá không bị giới hạn cố định, có thể được thiết kế theo ngày, tuần, tháng hoặc quý nhằm phù hợp với mục tiêu nghiên cứu và đặc điểm của từng mô hình cũng như chiến lược backtest.

Dữ liệu sử dụng bao gồm:

1. Dữ liệu giá và khối lượng giao dịch lịch sử.
2. Các đặc trưng kỹ thuật như RSI, MACD, SMA, return lag, volatility, price trend và volume-related indicators.
3. Tin tức công khai liên quan đến doanh nghiệp, ngành và thị trường.
4. Kết quả dự báo/xếp hạng từ mô hình học máy.
5. SHAP hoặc feature importance để giải thích tín hiệu mô hình.

Luận văn không đặt mục tiêu ứng dụng hệ thống giao dịch tự động hoàn toàn. Hệ thống được định vị là công cụ hỗ trợ quyết định, trong đó nhà đầu tư vẫn là người ra quyết định cuối cùng.

Luận văn cũng không đặt mục tiêu chứng minh rằng LLM trực tiếp tạo alpha hoặc dự báo giá tốt hơn mô hình ML. Vai trò của LLM là hỗ trợ tạo luận điểm đầu tư, giải thích, theo dõi và hậu kiểm quyết định dựa trên dữ liệu được cung cấp.

---

# 5. Đóng góp dự kiến

Luận văn có các đóng góp chính sau:

## 5.1. Chuyển từ dự báo cổ phiếu sang quản trị quyết định đầu tư

Thay vì chỉ dừng ở dự báo tăng/giảm hoặc khuyến nghị Buy/Sell/Hold, luận văn đề xuất cách tiếp cận theo vòng đời quyết định đầu tư:

**select → explain → monitor → update → review**

Trong đó, mỗi khuyến nghị được lưu lại như một decision record có lý do, bằng chứng, rủi ro cần theo dõi và kết quả hậu kiểm.

## 5.2. Kết hợp ML signal với LLM thesis generation

Mô hình học máy tạo tín hiệu định lượng và danh sách cổ phiếu ứng viên. LLM không tự do đưa ra khuyến nghị, mà sử dụng tín hiệu ML và thông tin tin tức để tạo investment thesis có cấu trúc.

## 5.3. Sử dụng tin tức như evidence layer

Thay vì ép tin tức trở thành biến dự báo trực tiếp, luận văn sử dụng tin tức như lớp thông tin định tính để hỗ trợ LLM giải thích và cập nhật bối cảnh đầu tư.

## 5.4. Theo dõi sau khuyến nghị

Hệ thống không kết thúc tại thời điểm đưa ra khuyến nghị. Sau khi một mã được chọn, hệ thống tiếp tục theo dõi sự thay đổi của tín hiệu ML, đặc trưng kỹ thuật và tin tức mới để đánh giá xem luận điểm ban đầu còn phù hợp hay không.

## 5.5. Hậu kiểm và phân tích kết quả

Sau kỳ nắm giữ, hệ thống đánh giá kết quả khuyến nghị và phân tích nguyên nhân thành công hoặc thất bại ở mức tổng quát.

---

# 6. Kiến trúc hệ thống đề xuất

Hệ thống gồm 5 lớp chính.

## 6.1. ML Signal Engine

Lớp này sử dụng dữ liệu kỹ thuật để huấn luyện các mô hình học máy như LightGBM, XGBoost, Random Forest hoặc Logistic Regression.

Đầu ra gồm:

- xác suất dự báo;
- tín hiệu Buy Candidate / Watchlist / Avoid;
- xếp hạng cổ phiếu;
- danh sách ứng viên;
- các đặc trưng quan trọng thông qua SHAP hoặc feature importance.

## 6.2. News Evidence Layer

Lớp này thu thập và xử lý tin tức công khai liên quan đến các mã cổ phiếu.

Mỗi tin tức được lưu dưới dạng thông tin gồm:

- ticker;
- ngày công bố;
- nguồn;
- tiêu đề;
- tóm tắt;
- loại sự kiện.

## 6.3. Evidence Pack Builder

Với mỗi cổ phiếu ứng viên, hệ thống tạo một gói thông tin gồm:

- tín hiệu ML;
- xác suất dự báo;
- thứ hạng;
- các chỉ báo kỹ thuật chính;
- tin tức liên quan trong khoảng thời gian gần.

Gói thông tin này là đầu vào cho LLM.

## 6.4. LLM Investment Thesis Generator

LLM nhận thông tin đầu vào và tạo decision card gồm:

- mã cổ phiếu;
- ngày ra quyết định;
- trạng thái hỗ trợ quyết định;
- luận điểm đầu tư chính;
- các yếu tố hỗ trợ;
- các yếu tố cần lưu ý;
- rủi ro cần theo dõi;
- thời điểm xem xét lại.

## 6.5. Post-Recommendation Monitoring & Outcome Review

Sau khi decision card được tạo, hệ thống theo dõi:

- sự thay đổi của tín hiệu ML;
- biến động giá;
- tin tức mới;
- kết quả sau kỳ nắm giữ.

Sau đó thực hiện đánh giá lại kết quả và rút kinh nghiệm.

---

# 7. Thiết kế thực nghiệm

## 7.1. Đánh giá mô hình ML

Các mô hình được đánh giá bằng:

- Balanced Accuracy;
- AUC;
- backtest return;
- Sharpe ratio;
- max drawdown;
- Top-K portfolio performance.

So sánh với các baseline như buy-and-hold hoặc chiến lược đơn giản.

## 7.2. Đánh giá news layer

Đánh giá ở mức tổng quát:

- độ chính xác khi gắn tin với mã cổ phiếu;
- mức độ liên quan của tin;
- độ bao phủ dữ liệu.

## 7.3. Đánh giá LLM decision card

Đánh giá theo các tiêu chí:

- mức độ bám sát dữ liệu đầu vào;
- tính rõ ràng của giải thích;
- khả năng nêu rủi ro;
- tính hữu ích cho người dùng.

## 7.4. Đánh giá monitoring

Xem xét một số trường hợp tiêu biểu để đánh giá khả năng hệ thống cập nhật khi bối cảnh thay đổi.

## 7.5. Đánh giá hậu kiểm

Đánh giá kết quả đầu tư và phân tích nguyên nhân ở mức tổng quát.

---

# 8. Quy trình chống rò rỉ dữ liệu

## 8.1. Backtest mode

Chỉ sử dụng dữ liệu có sẵn tại thời điểm ra quyết định:

- dữ liệu giá và kỹ thuật đến thời điểm t;
- tin tức đã công bố trước t;
- không sử dụng thông tin tương lai.

## 8.2. Live advisory mode

Sử dụng dữ liệu mới nhất để minh họa hệ thống, không dùng để đánh giá hiệu quả lịch sử.

---

# 9. So sánh với các hướng hiện có

Các hệ thống hiện nay thường tập trung vào việc tạo khuyến nghị mua/bán tại một thời điểm.

Luận văn này tập trung vào việc hỗ trợ quản lý toàn bộ quá trình ra quyết định đầu tư.

Điểm khác biệt chính:

1. Sử dụng mô hình học máy làm nền tảng định lượng.
2. Kết hợp tin tức như nguồn thông tin bổ trợ.
3. LLM đóng vai trò giải thích và hỗ trợ quyết định.
4. Có cơ chế theo dõi và đánh giá lại sau khuyến nghị.

---

# 10. Kết quả kỳ vọng

1. Một mô hình ML có khả năng tạo tín hiệu và xếp hạng cổ phiếu tốt hơn baseline.

2. Một pipeline xử lý tin tức phục vụ phân tích.

3. Một cơ chế LLM tạo luận điểm đầu tư có cấu trúc.

4. Một module theo dõi sau khuyến nghị.

5. Một cơ chế đánh giá lại kết quả đầu tư.

6. Một prototype hệ thống hỗ trợ quyết định đầu tư.

---

# 11. Giới hạn nghiên cứu

1. Hệ thống không thay thế nhà đầu tư.

2. LLM không dùng để dự báo giá trực tiếp.

3. Tin tức công khai có thể chưa đầy đủ.

4. Kết quả phụ thuộc vào chất lượng dữ liệu.

5. Đánh giá LLM mang tính định tính.

6. Cần kiểm soát chặt chẽ rò rỉ dữ liệu.

7. Hệ thống chỉ ở mức prototype.

---

# 12. Định vị cuối cùng của đề tài

Đề tài tập trung vào việc kết hợp mô hình học máy, tin tức công khai và LLM để hỗ trợ quá trình ra quyết định đầu tư.

Mô hình học máy cung cấp tín hiệu định lượng. Tin tức cung cấp bối cảnh. LLM hỗ trợ giải thích và theo dõi quyết định, giúp nhà đầu tư hiểu và quản lý quyết định tốt hơn.
