# LUẬN VĂN THẠC SĨ

---

**ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH**  
**TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN**

---

**Họ và tên học viên:** Ngô Minh Trí  
**Mã số học viên:** 24C01024  
**Ngành:** Khoa học Dữ liệu  
**Mã số ngành:** 8460108

---

## ỨNG DỤNG MACHINE LEARNING TRONG DỰ BÁO XU HƯỚNG GIÁ CỔ PHIẾU DỰA TRÊN ĐẶC TRƯNG KỸ THUẬT VÀ TẦN SUẤT TỪ KHÓA TRONG TIN TỨC TÀI CHÍNH TIẾNG VIỆT

---

**LUẬN VĂN THẠC SĨ KHOA HỌC DỮ LIỆU**

---

**TP. Hồ Chí Minh, năm 2026**

---

## MỤC LỤC

- [Chương 1: Giới thiệu](#chương-1-giới-thiệu)
- [Chương 2: Cơ sở lý thuyết](#chương-2-cơ-sở-lý-thuyết)
- [Chương 3: Dữ liệu và Phương pháp](#chương-3-dữ-liệu-và-phương-pháp)
- [Chương 4: Kết quả và Thảo luận](#chương-4-kết-quả-và-thảo-luận)
- [Chương 5: Kết luận](#chương-5-kết-luận)
- [Tài liệu tham khảo](#tài-liệu-tham-khảo)

---

## TÓM TẮT

Luận văn này nghiên cứu việc kết hợp đặc trưng kỹ thuật từ dữ liệu giao dịch và đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt trong bài toán dự báo xu hướng giá cổ phiếu. Nghiên cứu được thực hiện trên tập dữ liệu gồm 80 cổ phiếu niêm yết trên Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE) trong giai đoạn 2022–2026, với corpus tin tức từ 6 nguồn và full-text enrichment gần đầy đủ (45.949/45.968 unique URLs có `full_text`, 99,96%).

Ba giả thuyết nghiên cứu (H1, H2, H3) được kiểm định thông qua bốn thuật toán Machine Learning (Logistic Regression, Random Forest, XGBoost, LightGBM), ba cấu hình đặc trưng (chỉ kỹ thuật, chỉ từ khóa, kết hợp), và năm đơn vị thời gian (quý, 2 tháng, tháng, 2 tuần, 1 tuần). Phương pháp kiểm định thống kê bao gồm chi-square/Fisher exact test, Mann-Whitney U test, McNemar, và hiệu chỉnh đa kiểm định Benjamini-Hochberg (BH-FDR). Phân tích giải thích mô hình sử dụng SHAP values và permutation importance.

Kết quả chính: **H1 không được ủng hộ** — mô hình kết hợp (Config_C) không cải thiện balanced accuracy so với mô hình chỉ dùng đặc trưng kỹ thuật (Config_A) một cách nhất quán. **H2 không được ủng hộ** sau hiệu chỉnh BH-FDR trên cả ba cấu hình dataset, mặc dù các từ khóa "chia cổ tức" và "nợ xấu" liên tục cho tín hiệu thô tiềm năng. **H3 được ủng hộ một phần** — các từ khóa chiếm khoảng 32% đóng góp SHAP trong Config_C, với các từ khóa hàng đầu có ý nghĩa tài chính rõ ràng.

Nghiên cứu đóng góp bằng chứng thực nghiệm về giới hạn của đặc trưng tần suất từ khóa tài chính trong bối cảnh thị trường chứng khoán Việt Nam, đồng thời chỉ ra hướng nghiên cứu tương lai với tiềm năng cao hơn.

**Từ khóa:** dự báo xu hướng giá cổ phiếu, machine learning, tần suất từ khóa, tin tức tài chính tiếng Việt, HOSE, phân tích kỹ thuật, SHAP.

---

## ABSTRACT

This thesis investigates the combination of technical features from trading data and keyword frequency features from Vietnamese financial news for stock price trend prediction. The study covers 80 stocks listed on the Ho Chi Minh Stock Exchange (HOSE) from 2022 to 2026, using a six-source news corpus with near-complete full-text enrichment (45,949/45,968 unique URLs with `full_text`, 99.96%).

Three research hypotheses (H1, H2, H3) were tested using four machine learning algorithms (Logistic Regression, Random Forest, XGBoost, LightGBM), three feature configurations (technical-only, keyword-only, combined), and five time units (quarter, 2-month, month, 2-week, 1-week). Statistical testing methods include chi-square/Fisher exact test, Mann-Whitney U test, McNemar test, and Benjamini-Hochberg false discovery rate (BH-FDR) correction. Model interpretation uses SHAP values and permutation importance.

Main results: **H1 is not supported** — the combined model (Config_C) does not consistently improve balanced accuracy over the technical-only model (Config_A). **H2 is not supported** after BH-FDR correction across all three dataset configurations, although keywords "chia cổ tức" (dividend) and "nợ xấu" (non-performing loans) consistently show potential raw signals. **H3 is partially supported** — keywords account for approximately 32% of SHAP contribution in Config_C, with top keywords having clear financial relevance.

**Keywords:** stock price trend prediction, machine learning, keyword frequency, Vietnamese financial news, HOSE, technical analysis, SHAP.

---

---

# CHƯƠNG 1: GIỚI THIỆU

## 1.1. Bối cảnh nghiên cứu

Thị trường chứng khoán Việt Nam trong những năm gần đây đã có bước phát triển đáng kể cả về chiều rộng lẫn chiều sâu. Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE) hiện niêm yết hơn 400 mã cổ phiếu với tổng vốn hóa thị trường đạt hàng triệu tỷ đồng, trong khi số lượng tài khoản nhà đầu tư cá nhân đã vượt mốc 8 triệu vào cuối năm 2023. Chỉ số VN-Index — thước đo tổng hợp của HOSE — đã trải qua nhiều giai đoạn biến động mạnh, từ đỉnh lịch sử gần 1.500 điểm vào đầu năm 2022, lao dốc xuống dưới 900 điểm cuối năm 2022, rồi phục hồi và duy trì trong vùng 1.200–1.300 điểm trong giai đoạn 2023–2026. Chỉ số VN30 — đại diện cho 30 cổ phiếu vốn hóa lớn và thanh khoản cao nhất trên HOSE — là thước đo được giới đầu tư tổ chức và cá nhân theo dõi sát nhất.

Trong bối cảnh đó, bài toán dự báo xu hướng giá cổ phiếu thu hút sự quan tâm của cả cộng đồng học thuật lẫn thực hành đầu tư. Về mặt kỹ thuật, giá cổ phiếu chịu tác động đồng thời từ nhiều nguồn thông tin: kết quả kinh doanh định kỳ, diễn biến vĩ mô, tâm lý đám đông, dòng tiền nước ngoài, và đặc biệt là các thông tin được công bố qua kênh truyền thông tài chính. Sự bùng nổ của các nền tảng báo điện tử tài chính như CafeF, Vietstock, VietnamBiz, VnExpress Finance đã tạo ra một nguồn dữ liệu văn bản phong phú, cập nhật theo thời gian thực về mọi diễn biến liên quan đến các doanh nghiệp niêm yết.

Đặc điểm nổi bật của tin tức tài chính tiếng Việt là mật độ cao về các cụm từ chuyên biệt: "chia cổ tức", "lợi nhuận tăng trưởng", "nợ xấu", "phát hành thêm cổ phiếu", "ký kết hợp đồng", "vi phạm quy định", v.v. Những cụm từ này xuất hiện lặp lại trong nhiều bài viết về cùng một mã cổ phiếu trong cùng một kỳ, tạo thành tín hiệu tần suất có thể lượng hóa được. Câu hỏi nghiên cứu cốt lõi của luận văn này là: *liệu tần suất xuất hiện của các từ khóa tài chính trong tin tức có mang thêm thông tin dự báo so với các đặc trưng kỹ thuật thông thường hay không?*

Câu hỏi này có ý nghĩa thực tiễn rõ ràng, nhưng cũng đặt ra thách thức phương pháp nghiêm túc. Thị trường hiệu quả — theo định nghĩa của Fama (1970) — ngụ ý rằng giá cổ phiếu đã phản ánh toàn bộ thông tin công khai có sẵn. Nếu điều này đúng, tần suất từ khóa trong tin tức — vốn là thông tin công khai — sẽ không cung cấp lợi thế dự báo nào thêm sau khi giá đã phản ánh thông tin đó. Tuy nhiên, mức độ hiệu quả của thị trường Việt Nam vẫn còn là vấn đề đang được nghiên cứu, và khả năng phản ánh thông tin không hoàn toàn — nhất là đối với thông tin văn bản phức tạp — tạo ra cơ sở lý thuyết cho việc kiểm định.

Nghiên cứu này tiếp cận bài toán theo hướng định lượng khoa học: xây dựng giả thuyết cụ thể, thu thập dữ liệu thực tế, áp dụng các phương pháp kiểm định thống kê nghiêm ngặt, và trình bày kết quả trung thực — kể cả khi kết quả là âm (không ủng hộ giả thuyết). Lập trường này phân biệt nghiên cứu hiện tại với nhiều nghiên cứu ứng dụng khác thường có xu hướng báo cáo thiên lệch về kết quả dương.

## 1.2. Tổng quan nghiên cứu trong và ngoài nước

### 1.2.1. Nghiên cứu quốc tế

Việc khai thác dữ liệu văn bản cho dự báo thị trường tài chính là một lĩnh vực nghiên cứu sôi động từ những năm 2000. Tetlock (2007) là một trong những nghiên cứu tiên phong chỉ ra rằng tâm lý tiêu cực trong tin tức trên Wall Street Journal có khả năng dự báo tạm thời cho lợi suất chứng khoán, đặc biệt là hiệu ứng đảo chiều giá sau các thông tin tiêu cực. Nghiên cứu này mở ra một hướng phân tích cảm xúc (sentiment analysis) trong tài chính và được trích dẫn rộng rãi.

Bollen và cộng sự (2011) mở rộng hướng này sang mạng xã hội, chứng minh rằng tâm lý trên Twitter — đo bằng công cụ POMS — có khả năng dự báo chỉ số Dow Jones Industrial Average với độ chính xác đáng kể. Tuy nhiên, các nghiên cứu tái lặp về sau gặp nhiều khó khăn trong việc xác nhận kết quả này một cách nhất quán, đặt ra câu hỏi về tính bền vững của tín hiệu.

Li và cộng sự (2014) nghiên cứu tác động của tin tức đến lợi suất cổ phiếu thông qua phân tích cảm xúc và chứng minh mối liên hệ giữa sắc thái tin tức và biến động giá ngắn hạn. Ding và cộng sự (2015) đề xuất mô hình học sâu kết hợp trích xuất sự kiện từ tin tức với mạng nơ-ron để dự báo chỉ số chứng khoán, đạt kết quả vượt trội so với các phương pháp baseline.

Nassirtoussi và cộng sự (2014) tổng hợp một cách hệ thống các nghiên cứu khai thác văn bản cho dự báo thị trường, rút ra kết luận rằng kết hợp dữ liệu văn bản với dữ liệu thị trường thường cải thiện hiệu quả dự báo, nhưng mức độ cải thiện phụ thuộc mạnh vào chất lượng corpus, thị trường mục tiêu và phương pháp đặc trưng hóa.

Về phương pháp Machine Learning cho tài chính, các nghiên cứu của Chen và Guestrin (2016) về XGBoost và Ke và cộng sự (2017) về LightGBM đã thiết lập hai thuật toán gradient boosting này như là công cụ tiêu chuẩn cho dữ liệu dạng bảng có cấu trúc hỗn hợp, bao gồm cả ứng dụng tài chính.

Sự xuất hiện của các mô hình ngôn ngữ tiền huấn luyện, đặc biệt là BERT (Devlin và cộng sự, 2019) và các biến thể chuyên biệt cho tài chính như FinBERT (Yang và cộng sự, 2020), đã mở ra hướng mới trong biểu diễn văn bản tài chính. Tuy nhiên, các nghiên cứu meta-phân tích gần đây (López de Prado, 2018) cảnh báo về nguy cơ overfitting và rò rỉ dữ liệu trong nhiều nghiên cứu tài chính dùng học máy, đòi hỏi thiết kế thực nghiệm cẩn trọng hơn.

Lundberg và Lee (2017) giới thiệu framework SHAP (SHapley Additive exPlanations) cho phép giải thích nhất quán đóng góp của từng đặc trưng trong mô hình học máy phức tạp, giúp tăng tính minh bạch và diễn giải trong các ứng dụng tài chính.

### 1.2.2. Nghiên cứu trong nước

Tại Việt Nam, nghiên cứu về dự báo giá cổ phiếu bằng học máy đang phát triển nhanh chóng nhưng vẫn còn tương đối thưa thớt so với văn học quốc tế. Phần lớn các nghiên cứu hiện tại tập trung vào dữ liệu giá và khối lượng giao dịch với các mô hình LSTM, mạng nơ-ron hồi quy, hoặc các thuật toán học máy cổ điển.

Nguyen và Nguyen (2020) phát triển PhoBERT — mô hình ngôn ngữ tiền huấn luyện đầu tiên cho tiếng Việt dựa trên kiến trúc RoBERTa — tạo nền tảng quan trọng cho các ứng dụng NLP tiếng Việt bao gồm phân tích cảm xúc tài chính. Việc có một mô hình ngôn ngữ tiền huấn luyện chất lượng cho tiếng Việt là bước tiến quan trọng, nhưng cũng đặt ra câu hỏi liệu phương pháp đơn giản hơn như tần suất từ khóa có đủ để nắm bắt tín hiệu hay không.

Trong lĩnh vực phân tích kỹ thuật, nhiều nhà phân tích Việt Nam đã áp dụng thành công các chỉ báo như RSI, MACD, Bollinger Bands cho thị trường HOSE và HNX. Tuy nhiên, các nghiên cứu học thuật kết hợp phân tích kỹ thuật với dữ liệu văn bản còn hạn chế về số lượng và chất lượng phương pháp.

Murphy (1999) là tài liệu nền tảng về phân tích kỹ thuật được sử dụng rộng rãi tại Việt Nam, trong khi nhiều tài liệu học thuật trong nước còn thiếu thiết kế thực nghiệm nghiêm ngặt về mặt kiểm định giả thuyết và tránh data leakage.

## 1.3. Khoảng trống nghiên cứu

Từ tổng quan trên, có thể xác định một số khoảng trống nghiên cứu mà luận văn này nhằm lấp đầy:

Thứ nhất, các nghiên cứu về dự báo giá cổ phiếu tại Việt Nam chủ yếu sử dụng dữ liệu giá và khối lượng, trong khi dữ liệu tin tức tài chính tiếng Việt — vốn ngày càng phong phú và đa dạng — chưa được khai thác đầy đủ trong framework học máy có cấu trúc.

Thứ hai, các nghiên cứu về văn bản tài chính thường tập trung vào phân tích cảm xúc ở cấp độ bài viết, trong khi hướng tiếp cận tần suất từ khóa như một đặc trưng định lượng độc lập — ổn định hơn về mặt kỹ thuật và không phụ thuộc vào mô hình ngôn ngữ phức tạp — chưa được nghiên cứu hệ thống.

Thứ ba, thiếu vắng các nghiên cứu sử dụng phương pháp kiểm định giả thuyết thống kê nghiêm ngặt (với hiệu chỉnh đa kiểm định) để đánh giá từng từ khóa riêng lẻ, thay vì chỉ đánh giá hiệu quả tổng thể của mô hình.

Thứ tư, chưa có nghiên cứu nào tại Việt Nam kết hợp SHAP analysis với đặc trưng từ khóa tài chính để xác định cụ thể từ khóa nào đóng góp đáng kể trong mô hình dự báo.

## 1.4. Mục tiêu và câu hỏi nghiên cứu

Mục tiêu tổng quát của luận văn là xây dựng và đánh giá mô hình Machine Learning dự báo xu hướng giá cổ phiếu kết hợp đặc trưng kỹ thuật và đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt, đồng thời kiểm định một cách nghiêm ngặt xem nhóm đặc trưng văn bản có tạo ra giá trị dự báo bổ sung hay không.

Các mục tiêu cụ thể bao gồm:

1. Xây dựng bộ dữ liệu thực nghiệm kết hợp dữ liệu giao dịch và dữ liệu tin tức tài chính tiếng Việt cho 80 cổ phiếu HOSE trong giai đoạn 2022–2026.
2. Thiết kế và triển khai phương pháp trích xuất đặc trưng tần suất từ khóa với 106 từ khóa tài chính thuộc 6 nhóm chủ đề.
3. Huấn luyện và so sánh bốn thuật toán ML trên ba cấu hình đặc trưng theo thiết kế time-series split nghiêm ngặt.
4. Kiểm định từng từ khóa bằng phương pháp thống kê (chi-square, Mann-Whitney, logistic đơn biến) với hiệu chỉnh BH-FDR.
5. Phân tích đóng góp của nhóm từ khóa qua SHAP values và permutation importance.

Các câu hỏi nghiên cứu tương ứng:

- **CQ1:** Đặc trưng kỹ thuật có khả năng dự báo xu hướng giá cổ phiếu ở mức nào, và kết quả có nhất quán qua các đơn vị thời gian khác nhau không?
- **CQ2:** Mô hình kết hợp kỹ thuật + từ khóa (Config_C) có cải thiện balanced accuracy so với mô hình chỉ kỹ thuật (Config_A) không?
- **CQ3:** Từng từ khóa tài chính có mối liên hệ thống kê có ý nghĩa với xu hướng tăng/giảm giá sau hiệu chỉnh đa kiểm định không?
- **CQ4:** Nhóm đặc trưng từ khóa chiếm tỷ lệ đóng góp như thế nào trong mô hình tổng thể (theo SHAP)?

## 1.5. Giả thuyết nghiên cứu

Dựa trên mục tiêu và câu hỏi nghiên cứu, luận văn đề xuất ba giả thuyết:

**Giả thuyết H1:** Đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt có thể cung cấp thông tin bổ sung cho mô hình dự báo xu hướng giá cổ phiếu so với mô hình chỉ sử dụng đặc trưng kỹ thuật, thể hiện qua balanced accuracy cao hơn của Config_C so với Config_A.

**Giả thuyết H2:** Một số từ khóa/cụm từ khóa tài chính có mối liên hệ thống kê có ý nghĩa với xu hướng tăng/giảm của giá cổ phiếu trong kỳ dự báo tiếp theo, sau khi hiệu chỉnh cho đa kiểm định (BH-FDR).

**Giả thuyết H3:** Các phương pháp giải thích mô hình (SHAP, permutation importance) có thể hỗ trợ xác định nhóm từ khóa/cụm từ khóa có đóng góp đáng kể trong mô hình dự báo Config_C.

Các giả thuyết được đặt ra với tinh thần kiểm định khoa học trung lập: kết quả âm (không ủng hộ) cũng là đóng góp khoa học hợp lệ vì cung cấp bằng chứng thực nghiệm về giới hạn của phương pháp trong bối cảnh cụ thể.

## 1.6. Phạm vi và giới hạn nghiên cứu

**Phạm vi nghiên cứu:**

| Tiêu chí | Phạm vi |
|---|---|
| Thị trường | HOSE (Sở Giao dịch Chứng khoán TP.HCM) |
| Cổ phiếu | 80 mã (VN30 + 50 mã mở rộng HOSE-80) |
| Giai đoạn | 2022-01-01 đến 2026-06-30 |
| Đơn vị dự báo chính | Quý (có sensitivity test với 2 tháng, tháng, 2 tuần, 1 tuần) |
| Bài toán | Phân loại nhị phân: tăng / không tăng |
| Nguồn tin tức | 6 nguồn: CafeF, Vietstock, TNCK, VietnamBiz, VnExpress, Kinh Tế Chứng Khoán; full-text enrichment 99,96% unique URLs |

**Giới hạn:**

Nghiên cứu không dự báo giá tuyệt đối, không xây dựng hệ thống giao dịch tự động, không sử dụng dữ liệu giao dịch trong ngày (intraday), không xem xét các biến vĩ mô (lãi suất, tỷ giá, GDP) như biến đầu vào độc lập. Nghiên cứu cũng không áp dụng mô hình ngôn ngữ học sâu (deep NLP) mà chỉ sử dụng đặc trưng tần suất từ khóa đã định nghĩa trước. Có thể tồn tại survivorship bias do chỉ chọn cổ phiếu có dữ liệu liên tục trong toàn bộ giai đoạn nghiên cứu.

---

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

## 2.1. Lý thuyết thị trường hiệu quả và dự báo giá cổ phiếu

Lý thuyết thị trường hiệu quả (Efficient Market Hypothesis — EMH) do Fama (1970) đề xuất là nền tảng lý thuyết quan trọng nhất để đặt vấn đề nghiên cứu của luận văn này. EMH phát biểu rằng giá cổ phiếu tại mọi thời điểm phản ánh đầy đủ tất cả thông tin có sẵn. Tùy theo mức độ phản ánh thông tin, EMH phân chia thành ba dạng:

- **Dạng yếu (Weak-form efficiency):** Giá đã phản ánh đầy đủ tất cả thông tin lịch sử về giá và khối lượng giao dịch. Điều này ngụ ý rằng phân tích kỹ thuật không thể tạo ra lợi suất vượt trội bền vững.
- **Dạng trung bình (Semi-strong form efficiency):** Giá phản ánh toàn bộ thông tin công khai, bao gồm báo cáo tài chính, thông tin về ngành, tin tức kinh tế. Điều này ngụ ý rằng phân tích cơ bản và khai thác tin tức công khai không thể tạo ra lợi suất vượt trội bền vững.
- **Dạng mạnh (Strong-form efficiency):** Giá phản ánh cả thông tin nội gián, ngụ ý rằng không ai có thể kiếm lợi vượt trội liên tục.

Đối với thị trường chứng khoán Việt Nam, bằng chứng thực nghiệm về mức độ hiệu quả còn khá phân tán. Một số nghiên cứu tìm thấy bằng chứng về tính không hiệu quả ở dạng yếu trong giai đoạn đầu phát triển của HOSE, nhưng mức độ này giảm dần theo thời gian khi thị trường trưởng thành hơn. Điều quan trọng cần lưu ý là EMH không phủ nhận khả năng dự báo ngắn hạn trong từng trường hợp cụ thể, mà chỉ phát biểu rằng không tồn tại chiến lược có thể tạo ra lợi suất vượt trội *bền vững* sau khi điều chỉnh rủi ro.

Trong bối cảnh của luận văn, nếu thị trường hiệu quả ở dạng trung bình, thì tần suất từ khóa trong tin tức công khai — vốn đã được thị trường tiêu hóa trong kỳ quan sát — sẽ không có giá trị dự báo cho kỳ tiếp theo. Đây chính là một trong những lý thuyết nền mà nghiên cứu này kiểm định thực nghiệm trên dữ liệu thị trường Việt Nam.

## 2.2. Phân tích kỹ thuật và các đặc trưng kỹ thuật

Phân tích kỹ thuật (Technical Analysis) là phương pháp phân tích chứng khoán dựa trên nghiên cứu dữ liệu giao dịch lịch sử, đặc biệt là giá và khối lượng, nhằm dự báo diễn biến giá tương lai. Murphy (1999) là tài liệu hệ thống hóa toàn diện nhất về phân tích kỹ thuật, đặt nền móng cho nhiều ứng dụng hiện đại.

Các chỉ báo kỹ thuật được sử dụng trong luận văn này bao gồm:

**Chỉ báo xu hướng:** Đường trung bình động đơn giản (SMA) và đường trung bình động lũy thừa (EMA) được tính trên chuỗi giá đóng cửa trong kỳ, phản ánh xu hướng trung hạn. Khoảng cách tương đối giữa giá và đường trung bình động là đặc trưng quan trọng trong phân tích kỹ thuật.

**Chỉ số sức mạnh tương đối (RSI):** Được Wilder (1978) phát triển, RSI đo tốc độ và sự thay đổi của biến động giá theo thang đo 0–100. Vùng RSI > 70 thường được coi là quá mua (overbought), RSI < 30 là quá bán (oversold).

**MACD (Moving Average Convergence Divergence):** Chỉ báo động lượng tính bằng hiệu giữa EMA ngắn hạn và dài hạn, cùng với đường tín hiệu. Giao cắt giữa MACD và đường tín hiệu là cơ sở cho nhiều chiến lược giao dịch.

**Bollinger Bands:** Được Bollinger (1992) phát triển, gồm một dải trên và dải dưới cách đường trung bình động một số lần độ lệch chuẩn. Các đặc trưng từ Bollinger Bands phản ánh độ biến động tương đối của giá.

**Chỉ báo khối lượng:** Biến động khối lượng giao dịch so với trung bình kỳ trước là tín hiệu quan trọng về mức độ quan tâm của thị trường.

Mặc dù phân tích kỹ thuật có nhiều tranh luận về cơ sở khoa học, các nghiên cứu thực nghiệm trên nhiều thị trường cho thấy một số chỉ báo kỹ thuật — đặc biệt khi kết hợp với học máy — có khả năng nắm bắt các pattern lặp lại trong dữ liệu giá tốt hơn là mô hình ngẫu nhiên thuần túy.

## 2.3. Đặc trưng văn bản trong tài chính: Tần suất từ khóa so với Phân tích cảm xúc

Có hai hướng tiếp cận chính để trích xuất thông tin từ văn bản tài chính:

**Phân tích cảm xúc (Sentiment Analysis):** Phân loại bài viết thành tích cực, tiêu cực hoặc trung tính dựa trên ngữ nghĩa tổng thể. Ưu điểm: nắm bắt được sắc thái phức tạp của ngôn ngữ. Nhược điểm: phụ thuộc nhiều vào chất lượng mô hình ngôn ngữ, khó tổng quát hóa qua các ngữ cảnh, và nhạy cảm với cách viết mỉa mai hay phủ định trong tiếng Việt.

**Tần suất từ khóa (Keyword Frequency):** Đếm số lần xuất hiện của các từ khóa được định nghĩa trước trong corpus tin tức. Ưu điểm: đơn giản, tái lặp được, minh bạch, không phụ thuộc vào mô hình ngôn ngữ, và có thể áp dụng trực tiếp cho tiếng Việt mà không cần mô hình ngôn ngữ phức tạp. Nhược điểm: bỏ qua ngữ cảnh, không xử lý được phủ định tốt, phụ thuộc vào chất lượng danh sách từ khóa.

Luận văn này chọn hướng tần suất từ khóa vì:

1. **Tính minh bạch và khả năng diễn giải:** Mỗi đặc trưng tương ứng trực tiếp với một từ khóa cụ thể, giúp phân tích SHAP có ý nghĩa rõ ràng.
2. **Tính ổn định kỹ thuật:** Không phụ thuộc vào mô hình ngôn ngữ tiếng Việt có thể không ổn định trên ngữ liệu tài chính chuyên biệt.
3. **Khả năng kiểm định:** Có thể kiểm định từng từ khóa riêng lẻ bằng phương pháp thống kê truyền thống.

Để tránh vấn đề double-counting khi một từ khóa dài chứa từ khóa ngắn hơn (ví dụ "lợi nhuận tăng trưởng mạnh" chứa cả "tăng trưởng" và "lợi nhuận"), luận văn áp dụng kỹ thuật **longest-first masking**: ưu tiên khớp cụm từ dài nhất trước, sau đó che (mask) vùng text đó để tránh đếm lại.

## 2.4. Machine Learning cho dự báo xu hướng giá

Bốn thuật toán được sử dụng trong luận văn này:

**Logistic Regression:** Mô hình tuyến tính đơn giản nhất cho bài toán phân loại nhị phân. Đóng vai trò baseline để đánh giá xem các mô hình phức tạp hơn có thực sự học được pattern phi tuyến hay không. Hệ số của Logistic Regression cũng có thể diễn giải trực tiếp.

**Random Forest:** Thuật toán ensemble dựa trên bagging của nhiều cây quyết định. Ưu điểm: xử lý tốt đặc trưng hỗn hợp, ít nhạy cảm với outlier, cung cấp feature importance tự nhiên. Được chọn làm mô hình chính cho phân tích SHAP (H3) vì TreeExplainer của SHAP chạy hiệu quả và chính xác trên Random Forest.

**XGBoost:** Gradient boosting tree với regularization. Chen và Guestrin (2016) chứng minh XGBoost vượt trội trong nhiều bài toán dữ liệu dạng bảng. Khả năng xử lý dữ liệu thưa (sparse) phù hợp với đặc trưng từ khóa có nhiều giá trị bằng 0.

**LightGBM:** Phiên bản gradient boosting tối ưu hóa tốc độ (Ke và cộng sự, 2017). Phù hợp với dataset lớn hơn và cho kết quả so sánh tốt với XGBoost trong nhiều benchmark.

**Thiết kế Time Series Split:** Do dữ liệu có cấu trúc thời gian (panel data: nhiều cổ phiếu × nhiều kỳ), việc chia tập huấn luyện/kiểm định phải tôn trọng thứ tự thời gian. Luận văn sử dụng Time_Series_Split với mốc cutoff 2025Q1: tất cả dữ liệu trước 2025Q1 dùng để huấn luyện, từ 2025Q1 trở đi dùng để kiểm định. Tuyệt đối không shuffle dữ liệu, không dùng cross-validation ngẫu nhiên để tránh look-ahead bias.

## 2.5. Giải thích mô hình: SHAP và Permutation Importance

Khi mô hình học máy đạt hiệu quả dự báo nhất định, câu hỏi tiếp theo là: *đặc trưng nào đóng góp nhiều nhất?* Luận văn sử dụng hai phương pháp:

**SHAP (SHapley Additive exPlanations):** Dựa trên lý thuyết giá trị Shapley trong lý thuyết trò chơi hợp tác. Mỗi đặc trưng nhận được giá trị SHAP phản ánh đóng góp biên của nó trong việc thay đổi dự báo so với giá trị dự báo trung bình. Thuộc tính quan trọng: tổng SHAP values của tất cả đặc trưng bằng đúng chênh lệch giữa dự báo cho mẫu đó và dự báo trung bình. Lundberg và Lee (2017) chứng minh SHAP là phương pháp duy nhất thỏa mãn đồng thời ba tính chất cơ bản: tính nhất quán (Consistency), tính cục bộ (Local accuracy), và tính thiếu vắng (Missingness).

**Permutation Importance:** Đánh giá tầm quan trọng của đặc trưng bằng cách đo sự suy giảm hiệu suất khi hoán vị ngẫu nhiên giá trị của đặc trưng đó trong tập kiểm định. Phương pháp này model-agnostic và đặc biệt phù hợp để xác nhận kết quả SHAP.

Trong luận văn này, SHAP được áp dụng trên Random Forest Config_C để trả lời câu hỏi H3: nhóm đặc trưng từ khóa chiếm tỷ lệ đóng góp như thế nào trong tổng đóng góp của mô hình? Và từ khóa nào là quan trọng nhất?

---

# CHƯƠNG 3: DỮ LIỆU VÀ PHƯƠNG PHÁP

## 3.1. Tổng quan thiết kế nghiên cứu

Nghiên cứu được thiết kế theo quy trình pipeline bán tự động gồm các bước tuần tự: (1) thu thập và làm sạch dữ liệu giá, (2) thu thập và xử lý tin tức, (3) matching tin tức với cổ phiếu, (4) xây dựng nhãn và đặc trưng, (5) huấn luyện và đánh giá mô hình, (6) kiểm định thống kê, (7) phân tích giải thích mô hình. Pipeline được cấu hình trong file `config/pipeline_config.yaml` và có thể tái chạy hoàn toàn từ đầu để đảm bảo tính tái lặp.

Điểm then chốt trong thiết kế là **ngăn chặn tuyệt đối data leakage theo thời gian**: mọi thông tin từ kỳ q+1 đều không được sử dụng khi xây dựng đặc trưng cho kỳ q. Cutoff huấn luyện/kiểm định được đặt tại 2025Q1: toàn bộ dữ liệu trước 2025Q1 dùng để huấn luyện mô hình, từ 2025Q1 trở về sau là tập kiểm định out-of-sample.

## 3.2. Dữ liệu giá cổ phiếu

### 3.2.1. Danh sách cổ phiếu — HOSE-80

Nghiên cứu sử dụng 80 cổ phiếu niêm yết trên HOSE, gồm hai nhóm:

**VN30 (30 mã gốc):** Đây là 30 cổ phiếu tạo thành chỉ số VN30 — nhóm cổ phiếu có vốn hóa lớn nhất và thanh khoản cao nhất trên HOSE, bao gồm các tên tuổi lớn như VCB (Vietcombank), TCB (Techcombank), FPT (Tập đoàn FPT), VHM (Vinhomes), ACB (Ngân hàng Á Châu), HPG (Hòa Phát), MBB (MB Bank), v.v.

**HOSE-80 mở rộng (50 mã thêm):** Được bổ sung vào tháng 6/2026 nhằm tăng statistical power cho kiểm định H2. Tiêu chí lựa chọn gồm 5 điều kiện bắt buộc:

1. **Sàn niêm yết:** Chỉ HOSE, loại trừ HNX và UPCoM (mức độ phủ tin tức trên các báo tài chính lớn thấp hơn đáng kể).
2. **Giá trị giao dịch bình quân ngày:** ≥ 50 tỷ VND/ngày (tính trung bình 6 tháng gần nhất). Ngưỡng này tương đương khoảng P25(VN30)/4, đảm bảo cổ phiếu có đủ thanh khoản để giá phản ánh thông tin hiệu quả.
3. **Vốn hóa thị trường:** ≥ 2.000 tỷ VND, tương đương P25 nhóm mid-cap HOSE. Ngưỡng này đảm bảo cổ phiếu xuất hiện thường xuyên trên các báo tài chính lớn.
4. **Tính liên tục niêm yết:** Niêm yết liên tục từ trước ngày 01/01/2022, đảm bảo chuỗi dữ liệu đầy đủ cho toàn bộ giai đoạn nghiên cứu.
5. **Loại trừ:** Chứng quyền có bảo đảm (CW), chứng chỉ quỹ ETF, cổ phiếu bị kiểm soát/cảnh báo.

50 mã mở rộng bao gồm đại diện từ 8 ngành: ngân hàng tầm trung (11 mã: EIB, LPB, MSB, NAB, OCB, PGB, BVB, ABB, KLB, BAB, VBB), chứng khoán (5 mã: VCI, HCM, VND, MBS, BSI), bất động sản (9 mã: KDH, NVL, DXG, PDR, NLG, DIG, HDG, VCG, SCR), công nghiệp và sản xuất (8 mã: HSG, NKG, VGC, PHR, CSV, DPM, DCM, BMP), năng lượng và tiện ích (5 mã: REE, NT2, PPC, GEX, EVF), tiêu dùng và bán lẻ (6 mã: PNJ, DGW, FRT, MCH, VHC, ANV), công nghệ (2 mã: CMG, ELC), và vận tải & logistics (4 mã: GMD, VSC, PVT, HAH).

### 3.2.2. Thu thập và xử lý dữ liệu giá

Dữ liệu giá ngày (OHLCV: Open, High, Low, Close, Volume) được thu thập qua thư viện vnstock cho 80 tickers trong giai đoạn từ 01/01/2022 đến 30/06/2026. Dữ liệu được lưu theo từng ticker riêng lẻ trong thư mục `data/prices/`, ví dụ `data/prices/VCB.csv`, `data/prices/ACB.csv`.

Từ dữ liệu giá ngày, dữ liệu được tổng hợp theo đơn vị quý (quarter) là đơn vị chính. Mỗi quan sát trong dataset cuối cùng tương ứng với một cặp (ticker, quý). Giai đoạn từ 2022 đến đầu 2026 bao gồm khoảng 17 quý, do đó dataset VN30 có khoảng 510 rows và dataset HOSE-80 có 1.348 rows sau khi loại các quý có dữ liệu không đủ.

### 3.2.3. Xây dựng biến mục tiêu

Biến mục tiêu `label_basic` được xây dựng dựa trên so sánh giá đóng cửa trung bình giữa hai kỳ liên tiếp:

- Ký hiệu `AvgPrice(i, q)` là giá đóng cửa trung bình của cổ phiếu *i* trong quý *q*.
- Nếu `AvgPrice(i, q+1) > AvgPrice(i, q)`: gán nhãn **1 (tăng)**.
- Nếu `AvgPrice(i, q+1) ≤ AvgPrice(i, q)`: gán nhãn **0 (không tăng/giảm)**.

Cách định nghĩa nhãn theo giá trung bình cả kỳ (thay vì so sánh điểm cuối kỳ) có ưu điểm giảm nhiễu từ các biến động giá bất thường vào cuối kỳ. Phân phối nhãn trong dataset HOSE-80 gần cân bằng với tỷ lệ lớp 1 (tăng) khoảng 52,5%.

## 3.3. Dữ liệu tin tức tài chính

### 3.3.1. Nguồn và quy mô corpus

Tin tức tài chính tiếng Việt được thu thập từ 6 nguồn:

- **CafeF** (cafef.vn): trang tài chính lớn, crawl theo ticker và detail page.
- **Vietstock** (vietstock.vn): tin tức, phân tích và dữ liệu thị trường; có deep paging/API paging.
- **Tinnhanh Chứng khoán** (TNCK): nguồn báo tài chính/chứng khoán bổ sung.
- **VietnamBiz**: nguồn tin doanh nghiệp và thị trường.
- **VnExpress Kinh doanh/Tài chính**: nguồn báo phổ thông có chuyên mục kinh doanh.
- **Kinh Tế Chứng Khoán**: nguồn được khai thác qua sitemap theo ngày.

Corpus sau matching/enrichment gồm 52.790 dòng bài-ticker và 45.968 unique URLs; sau bước repair có 45.949 unique URLs có `full_text` (99,96%). Các bài tin tức được gắn với mã cổ phiếu liên quan dựa trên mã ticker xuất hiện trong URL hoặc tiêu đề, tên doanh nghiệp, và các quy tắc entity matching đã được chuẩn hóa.

### 3.3.2. Matching và tiền xử lý

Quy trình matching bài tin tức với cổ phiếu:

1. **Crawl metadata theo nguồn:** Thu thập tiêu đề, mô tả, ngày đăng, URL và nguồn.
2. **Entity matching:** Gắn bài với mã cổ phiếu bằng ticker, tên doanh nghiệp, alias và quy tắc matching case-insensitive.
3. **Full-text enrichment (TASK 2B):** Fetch detail page sau matching để trích xuất `full_text`, `lead`, `article_summary`, `key_facts_json`, `content_hash` và trạng thái extraction.
4. **Lọc trùng lặp:** Loại bỏ bài viết trùng URL/tiêu đề gần giống trong cùng ticker và kỳ.
5. **Phân loại theo kỳ:** Gán mỗi bài viết vào kỳ tương ứng dựa trên ngày đăng bài.
6. **Tiền xử lý văn bản:** TASK 4 ưu tiên `full_text`, bổ sung `lead`, `article_summary`, `key_facts_json`, fallback `description`, rồi chuẩn hóa/tokenize tiếng Việt.

File sau matching lưu tại `data/news/matched/all_news_matched.csv`; file enriched downstream lưu tại `data/news/enriched/all_news_enriched.csv`.

## 3.4. Đặc trưng kỹ thuật

Từ dữ liệu giá ngày, 16 đặc trưng kỹ thuật được trích xuất và tổng hợp theo từng kỳ:

| STT | Đặc trưng | Mô tả |
|---|---|---|
| 1 | `avg_return` | Lợi suất trung bình ngày trong kỳ |
| 2 | `cum_return` | Lợi suất tích lũy trong kỳ |
| 3 | `volatility` | Độ lệch chuẩn lợi suất ngày |
| 4 | `price_range_ratio` | Biên độ giá (High–Low)/Close trung bình |
| 5 | `avg_volume` | Khối lượng giao dịch trung bình |
| 6 | `volume_change` | Thay đổi khối lượng so với kỳ trước |
| 7 | `sma_ratio` | Tỷ lệ giá đóng cửa so với SMA trong kỳ |
| 8 | `ema_ratio` | Tỷ lệ giá đóng cửa so với EMA trong kỳ |
| 9 | `rsi_avg` | RSI trung bình trong kỳ |
| 10 | `macd_avg` | MACD trung bình trong kỳ |
| 11 | `macd_signal_avg` | Đường tín hiệu MACD trung bình |
| 12 | `bb_upper_ratio` | Tỷ lệ giá so với dải trên Bollinger Bands |
| 13 | `bb_lower_ratio` | Tỷ lệ giá so với dải dưới Bollinger Bands |
| 14 | `momentum_1` | Lợi suất kỳ trước (momentum 1 kỳ) |
| 15 | `price_trend` | Xu hướng giá trong kỳ (hệ số hồi quy tuyến tính) |
| 16 | `high_low_range` | Khoảng dao động giá cao/thấp tổng thể trong kỳ |

Tất cả đặc trưng kỹ thuật được chuẩn hóa (z-score normalization) dựa trên tham số tính từ tập huấn luyện để tránh data leakage.

## 3.5. Đặc trưng từ khóa tài chính

### 3.5.1. Danh sách từ khóa

Danh sách từ khóa gồm **106 từ khóa/cụm từ khóa** tài chính, được tổ chức thành **6 nhóm chủ đề**:

| Nhóm | Số từ khóa | Ví dụ |
|---|---|---|
| Kết quả kinh doanh (tích cực) | ~20 | lợi nhuận tăng, doanh thu tăng, tăng trưởng mạnh, vượt kế hoạch, kỷ lục, báo lãi |
| Kết quả kinh doanh (tiêu cực) | ~20 | lợi nhuận giảm, thua lỗ, báo lỗ, lỗ ròng, sụt giảm, giảm mạnh |
| Chính sách cổ đông | ~8 | chia cổ tức, cổ tức tiền mặt, mua lại cổ phiếu, tăng vốn điều lệ, không chia cổ tức |
| Tài chính doanh nghiệp | ~10 | nợ xấu, nợ vay tăng, giảm nợ, trả nợ, hệ số an toàn vốn |
| Hoạt động kinh doanh | ~12 | ký kết hợp đồng, hợp tác chiến lược, mở rộng thị trường, thắng thầu, dự án mới |
| Rủi ro & pháp lý | ~12 | vi phạm, bị phạt, bị thanh tra, cảnh báo, khởi tố, đình chỉ |
| Sự kiện doanh nghiệp | ~12 | đại hội cổ đông, họp HĐQT, thay CEO, sáp nhập, mua lại, thoái vốn |
| Xu hướng thị trường | ~12 | hoàn thành kế hoạch, phục hồi, bứt phá, lập đỉnh, tăng vọt |

Trong thực tế sau khi kiểm tra corpus, 35 từ khóa bị loại do zero occurrences trong toàn bộ dataset HOSE-80, chủ yếu là các cụm từ tiêu cực phức tạp (ví dụ: "âm vốn chủ sở hữu", "dòng tiền âm", "phát hành pha loãng"). Điều này phản ánh xu hướng của báo tài chính Việt Nam: đưa tin về các sự kiện tiêu cực phức tạp theo cách gián tiếp hoặc dùng ngôn ngữ ít trực tiếp hơn.

### 3.5.2. Kỹ thuật Longest-First Masking

Để tránh double-counting khi một từ khóa dài chứa từ khóa ngắn hơn, nghiên cứu áp dụng kỹ thuật **longest-first masking**:

1. Sắp xếp tất cả từ khóa theo độ dài giảm dần.
2. Duyệt qua văn bản, khớp từ khóa dài nhất trước.
3. Khi tìm thấy match, ghi nhận và thay thế vùng text đó bằng placeholder.
4. Tiếp tục với các từ khóa ngắn hơn trên phần text còn lại.

Ví dụ: nếu văn bản chứa "lợi nhuận tăng trưởng mạnh", kỹ thuật này sẽ ghi nhận "tăng trưởng mạnh" (dài hơn) thay vì đồng thời ghi nhận cả "tăng trưởng" và "tăng trưởng mạnh".

### 3.5.3. Tính toán tần suất và chuẩn hóa

Với mỗi cặp (ticker, quý) *i*, đặc trưng từ khóa *k* được tính theo hai cách:

- **Raw count:** Tổng số lần từ khóa *k* xuất hiện trong tất cả bài viết của ticker *i* trong quý *q*.
- **Normalized frequency:** Raw count chia cho tổng số bài viết của ticker *i* trong quý *q* (để loại bỏ ảnh hưởng của mật độ tin tức tổng thể).

Nghiên cứu sử dụng normalized frequency làm đặc trưng chính trong các mô hình Machine Learning.

## 3.6. Thiết kế thực nghiệm

### 3.6.1. Ba cấu hình đặc trưng

| Cấu hình | Đặc trưng | Mục đích |
|---|---|---|
| **Config_A** | 16 đặc trưng kỹ thuật | Baseline — chỉ dữ liệu giá |
| **Config_B** | 106 đặc trưng từ khóa (sau lọc: 71 đặc trưng) | Chỉ dữ liệu tin tức |
| **Config_C** | Config_A + Config_B (kết hợp) | Mô hình đầy đủ |

### 3.6.2. Bốn thuật toán Machine Learning

Bốn thuật toán phân loại nhị phân được áp dụng đồng đều trên ba cấu hình:

1. **Logistic Regression** (LR): Regularization L2, class_weight='balanced'.
2. **Random Forest** (RF): 200 cây, max_depth=10, class_weight='balanced'.
3. **XGBoost** (XGB): scale_pos_weight điều chỉnh theo tỷ lệ nhãn, learning_rate=0.05.
4. **LightGBM** (LGBM): is_unbalance=True, num_leaves=31, learning_rate=0.05.

Tất cả mô hình sử dụng tham số mặc định hợp lý với điều chỉnh cân bằng lớp nhãn do dữ liệu có mất cân bằng nhẹ.

### 3.6.3. Time Series Split — Không shuffle

Nguyên tắc cốt lõi: **không shuffle, không cross-validation ngẫu nhiên**. Cấu trúc thời gian được tôn trọng tuyệt đối:

- **Tập huấn luyện:** Tất cả quan sát (ticker, quý) với quý < 2025Q1.
- **Tập kiểm định:** Tất cả quan sát với quý ≥ 2025Q1.
- Kích thước tập kiểm định: ~150 rows (VN30 baseline) và ~400 rows (HOSE-80 baseline).

### 3.6.4. Thực nghiệm đa đơn vị thời gian

Để kiểm tra tính bền vững của kết quả, toàn bộ thực nghiệm được lặp lại với năm đơn vị thời gian:

| Đơn vị | Tổng rows (HOSE-80) | Số kỳ |
|---|---:|---:|
| Quý (quarter) | 1.348 | 17 |
| Tháng (month) | 3.815 | 53 |
| 2 tháng (2month) | 2.042 | 26 |
| 2 tuần (2week) | 7.090 | 117 |
| 1 tuần (1week) | 10.788 | 232 |

## 3.7. Phương pháp kiểm định H2

Để kiểm định H2 (mối liên hệ thống kê giữa từng từ khóa và xu hướng giá), ba phương pháp kiểm định độc lập được áp dụng song song:

### 3.7.1. Chi-square / Fisher Exact Test

Kiểm tra tính độc lập giữa sự xuất hiện từ khóa (biến nhị phân: có/không) và nhãn xu hướng (tăng/không tăng). Khi ô kỳ vọng < 5 (thường gặp với các từ khóa hiếm gặp), sử dụng Fisher Exact Test thay vì Chi-square để đảm bảo tính chính xác.

### 3.7.2. Mann-Whitney U Test

So sánh phân phối tần suất từ khóa chuẩn hóa (biến liên tục) giữa nhóm "tăng" (nhãn = 1) và nhóm "không tăng" (nhãn = 0). Không giả định phân phối chuẩn, phù hợp với đặc trưng từ khóa thường có phân phối lệch phải mạnh.

### 3.7.3. Logistic Regression Đơn biến

Ước lượng hệ số hồi quy logistic với từng từ khóa là biến độc lập duy nhất. Cung cấp ước lượng khoảng tin cậy 95% cho hệ số và p-value từ likelihood ratio test.

### 3.7.4. Hiệu chỉnh Đa kiểm định — BH-FDR

Với 71 từ khóa được kiểm định đồng thời, xác suất xuất hiện ít nhất một false positive ở ngưỡng α = 0.05 (family-wise error rate) là 1 - (0.95)^71 ≈ 97.7%. Do đó, hiệu chỉnh đa kiểm định là bắt buộc.

Phương pháp **Benjamini-Hochberg (BH-FDR)** được chọn (thay vì Bonferroni) vì:
- Phù hợp hơn cho nghiên cứu khám phá (exploratory) với nhiều kiểm định đồng thời.
- Kiểm soát False Discovery Rate (tỷ lệ dương tính giả trong số các kết quả có ý nghĩa), ít bảo thủ hơn Bonferroni.
- Tuy nhiên, với 71 kiểm định và α = 0.05, ngưỡng p-value raw hiệu quả vẫn khá thấp (khoảng 0.001 cho từ khóa có hạng cao).

Hiệu chỉnh BH-FDR được áp dụng riêng biệt cho từng loại kiểm định (chi-square, Mann-Whitney, logistic).

## 3.8. Các chỉ số đánh giá mô hình

Do nhãn không hoàn toàn cân bằng, luận văn ưu tiên các chỉ số sau:

- **Balanced Accuracy:** Trung bình của recall từng lớp. Không bị ảnh hưởng bởi mất cân bằng nhãn, là chỉ số chính để so sánh.
- **AUC-ROC:** Khả năng phân biệt tổng thể của mô hình, không phụ thuộc ngưỡng.
- **Precision/Recall theo từng lớp:** Để phân tích trade-off giữa hai lớp khi bổ sung đặc trưng từ khóa (liên quan đến Góc 2).
- **F1-Macro:** Trung bình F1 của hai lớp, cân bằng precision và recall.

Baseline tham chiếu gồm: Majority Class Classifier (luôn dự báo lớp phổ biến, balanced_accuracy = 0.500) và Naive Momentum Classifier (dự báo xu hướng kỳ sau bằng xu hướng kỳ hiện tại, balanced_accuracy ≈ 0.486).


---

## Chương 4: Kết quả và Thảo luận

Chương này trình bày toàn bộ kết quả thực nghiệm theo trình tự ba giả thuyết nghiên cứu (H1, H2, H3), tiếp theo là phân tích từ các góc nhìn bổ sung (Góc 2 và Góc 3) và thảo luận tổng hợp.

---

## 4.1. Kết quả tổng quan — Kiểm định H1

### 4.1.1. So sánh Config_A và Config_C trên HOSE-80

**Giả thuyết H1:** Mô hình kết hợp đặc trưng kỹ thuật và đặc trưng tần suất từ khóa (Config_C) đạt balanced accuracy cao hơn mô hình chỉ dùng đặc trưng kỹ thuật (Config_A).

Bảng 4.1 tổng hợp kết quả balanced accuracy của bốn thuật toán trên tập kiểm định HOSE-80 (kỳ kiểm định: Q1/2025, n ≈ 400 quan sát):

**Bảng 4.1. Balanced Accuracy — Config_A vs. Config_C vs. Config_B (HOSE-80)**

| Thuật toán | Config_A (Kỹ thuật) | Config_C (Kết hợp) | Δ (C − A) | Config_B (Từ khóa) |
|---|---|---|---|---|
| LightGBM | **0.7599** | 0.7368 | −0.0231 | 0.5219 |
| Random Forest | 0.7351 | 0.7164 | −0.0187 | 0.5236 |
| XGBoost | 0.7293 | 0.7261 | −0.0032 | 0.5239 |
| Logistic Regression | 0.7269 | 0.6966 | −0.0303 | 0.5015 |
| **Baseline: Majority Class** | — | — | — | 0.500 |
| **Baseline: Naive Momentum** | — | — | — | 0.486 |

*Nguồn: tính toán từ `reports/model_comparison.csv`*

**Nhận xét:**

- Cả bốn thuật toán đều cho thấy Config_C (kết hợp) **không vượt trội** hơn Config_A (chỉ kỹ thuật); ngược lại, balanced accuracy giảm ở tất cả các trường hợp, từ −0.003 (XGBoost) đến −0.030 (Logistic Regression).
- Config_B (chỉ từ khóa) chỉ đạt xấp xỉ 0.52, gần mức ngẫu nhiên (0.50), xác nhận rằng đặc trưng tần suất từ khóa đơn lẻ không có khả năng dự báo.
- LightGBM với Config_A đạt hiệu suất tốt nhất (balanced_accuracy = 0.7599), vượt xa cả hai baseline.
- Kết quả nhất quán theo hướng: bổ sung đặc trưng từ khóa không cải thiện, thậm chí gây nhiễu cho mô hình kỹ thuật.

### 4.1.2. Phân tích theo đơn vị thời gian

Để kiểm tra tính bền vững của H1, thực nghiệm được lặp lại trên năm đơn vị thời gian (quarter, 2month, month, 2week, 1week). Bảng 4.2 trình bày delta (Config_C − Config_A) của balanced accuracy:

**Bảng 4.2. Δ Balanced Accuracy (Config_C − Config_A) theo đơn vị thời gian**

| Đơn vị thời gian | N mẫu | LightGBM | Random Forest | XGBoost | Logistic Regression |
|---|---:|---:|---:|---:|---:|
| Quarter | 1.348 | +0.0178 | −0.0187 | +0.0231 | +0.0154 |
| Month | 3.815 | +0.0000 | −0.0202 | −0.0065 | +0.0138 |
| 2 tháng | 2.042 | −0.0337 | −0.0024 | −0.0397 | +0.0311 |
| 2 tuần | 7.090 | −0.0108 | −0.0258 | +0.0095 | −0.0010 |
| 1 tuần | 10.788 | −0.0061 | −0.0077 | −0.0168 | +0.0031 |

*Nguồn: `reports/period_experiment.csv`*

**Nhận xét:**

- Delta không cho thấy mô hình cải thiện nhất quán ở bất kỳ granularity nào.
- Quarter là đơn vị duy nhất có mean delta dương nhẹ, nhưng dấu dương này không đồng nhất tuyệt đối giữa các thuật toán và không đảo được kết luận ở production split theo quý.
- Ở 4 đơn vị còn lại, mean delta đều âm; đặc biệt 1 tuần và 2 tuần cho thấy thêm nhiều dữ liệu thời gian ngắn hơn cũng không giúp Config_C thắng ổn định.
- Logistic Regression đôi khi cho delta dương nhỏ, nhưng LightGBM/Random Forest/XGBoost không lặp lại cùng xu hướng một cách bền vững.

### 4.1.3. Kết luận H1

> **H1: KHÔNG ĐƯỢC ỦNG HỘ.**

Bằng chứng từ năm đơn vị thời gian và bốn thuật toán cho thấy việc bổ sung đặc trưng tần suất từ khóa vào mô hình kỹ thuật không mang lại cải thiện ổn định về balanced accuracy. Ở production split theo quý, Config_C kém Config_A ở cả bốn thuật toán; trên các thí nghiệm granularity, delta dao động theo thuật toán nhưng không tạo được mẫu hình cải thiện nhất quán. Điều này gợi ý đặc trưng từ khóa đưa vào nhiễu thống kê nhiều hơn là tín hiệu dự báo bền vững.

---

## 4.2. Kiểm định H2 — Mối liên hệ thống kê giữa từng từ khóa và xu hướng giá

### 4.2.1. Kết quả trên tập đầy đủ HOSE-80

**Giả thuyết H2:** Tồn tại ít nhất một từ khóa tài chính có mối liên hệ thống kê có ý nghĩa (sau hiệu chỉnh đa kiểm định) với xu hướng giá cổ phiếu trong kỳ tiếp theo.

Kiểm định được thực hiện trên 71 từ khóa (sau khi loại trừ các từ khóa có n_occurrences = 0) bằng ba phương pháp độc lập: Chi-square/Fisher exact test, Mann-Whitney U test, và Logistic Regression đơn biến. Hiệu chỉnh đa kiểm định Benjamini-Hochberg (BH-FDR) được áp dụng với ngưỡng α = 0.05.

**Kết quả chính:**

- **0/71 từ khóa** đạt ý nghĩa thống kê sau hiệu chỉnh BH-FDR ở bất kỳ phương pháp nào.
- Tất cả p-value điều chỉnh (chi_p_adj, mw_p_adj) đều lớn hơn 0.05, nhiều trường hợp tiệm cận 1.0.

**Bảng 4.3. Top 5 từ khóa có p-value thô thấp nhất (trước hiệu chỉnh) — HOSE-80**

| Từ khóa | Hướng | Chi p-raw | MW p-raw | Kết luận sau BH-FDR |
|---|---|---|---|---|
| chia cổ tức | positive | 0.0089 | 0.0076 | Không có ý nghĩa |
| giảm mạnh | negative | 0.0094 | 0.0056 | Không có ý nghĩa |
| nợ xấu | negative | 0.0448 | 0.0337 | Không có ý nghĩa |
| đại hội cổ đông | neutral | 0.0486 | 0.0339 | Không có ý nghĩa |
| không chia cổ tức | negative | 0.0670 | 0.0551 | Không có ý nghĩa |

*Nguồn: `reports/keyword_significance.csv`*

Đáng chú ý, từ khóa **"chia cổ tức"** (119 lần xuất hiện) và **"giảm mạnh"** (36 lần xuất hiện) có p-value thô thấp nhất, cho thấy có tín hiệu tiềm năng, nhưng không vượt được ngưỡng sau hiệu chỉnh BH-FDR (chi_p_adj = 0.333 và 0.333 tương ứng).

### 4.2.2. Kết quả trên nhóm con "tin dày" (news_count ≥ 15)

Nhóm con được xây dựng để kiểm tra liệu tín hiệu từ khóa có mạnh hơn trong môi trường thông tin dày đặc, nơi corpus từ khóa đầy đủ hơn (n = 636 quan sát, 66 từ khóa có đủ dữ liệu).

**Kết quả:**

- **0/66 từ khóa** đạt ý nghĩa thống kê sau BH-FDR.
- Tuy nhiên, so với tập đầy đủ, một số từ khóa cho p-value thô thấp hơn:

**Bảng 4.4. Top từ khóa p-value thô thấp — Nhóm "tin dày" (news_count ≥ 15, n=636)**

| Từ khóa | Hướng | Chi p-raw | MW p-raw | Chi p-adj (BH) | Kết luận |
|---|---|---|---|---|---|
| hoàn thành kế hoạch | positive | 0.0151 | 0.0085 | 0.404 | Không có ý nghĩa |
| chia cổ tức | positive | 0.0156 | 0.0124 | 0.404 | Không có ý nghĩa |
| nợ xấu | negative | 0.0184 | 0.0121 | 0.404 | Không có ý nghĩa |
| đại hội cổ đông | neutral | 0.0250 | 0.0149 | 0.412 | Không có ý nghĩa |
| hợp tác chiến lược | positive | 0.0382 | 0.0191 | 0.504 | Không có ý nghĩa |

*Nguồn: `reports/keyword_significance_highnews.csv`*

**Nhận xét:** Tín hiệu của **"chia cổ tức"** và **"nợ xấu"** xuất hiện ổn định trong cả hai tập (đầy đủ và tin dày), cho thấy đây là những từ khóa có khả năng tương quan thực tế nhất, dù chưa đủ mạnh để vượt ngưỡng sau hiệu chỉnh.

### 4.2.3. So sánh kết quả monthly vs. quarterly

Phân tích bổ sung cho thấy tín hiệu từ khóa ở cấp độ **tháng** nhìn chung yếu hơn ở cấp độ **quý**, phù hợp với lý thuyết rằng thông tin cần thời gian dài hơn để được hấp thụ hoàn toàn vào giá. Tuy nhiên, không có đơn vị thời gian nào cho kết quả đáp ứng ngưỡng BH-FDR.

### 4.2.4. Kết luận H2

> **H2: KHÔNG ĐƯỢC ỦNG HỘ** sau hiệu chỉnh đa kiểm định BH-FDR trên tất cả các cấu hình dataset.

Mặc dù vậy, tín hiệu ổn định của "chia cổ tức" và "nợ xấu" qua nhiều cấu hình là một phát hiện thực nghiệm có giá trị, gợi ý hướng nghiên cứu sâu hơn với corpus và phương pháp cải tiến.

---

## 4.3. Góc 2 — Phân tích Trade-off Recall/Precision theo lớp

Ngoài balanced accuracy tổng thể, phân tích sâu hơn về precision và recall theo từng lớp (class 0: không tăng, class 1: tăng) giúp hiểu rõ bản chất tác động của đặc trưng từ khóa.

**Bảng 4.5. Thay đổi Recall và Precision lớp 1 khi bổ sung từ khóa (Config_C − Config_A)**

| Thuật toán | Δ Recall lớp 1 | Δ Precision lớp 1 | Δ Balanced Accuracy |
|---|---|---|---|
| Random Forest | +0.076 | −0.059 | −0.011 |
| XGBoost | +0.051 | −0.044 | −0.009 |
| LightGBM | +0.026 | −0.037 | −0.015 |
| Logistic Regression | +0.013 | −0.044 | −0.022 |

*Nguồn: `reports/metrics_breakdown.csv`, kỳ kiểm định 2025Q1*

**Nhận xét:**

- Tất cả bốn thuật toán đều thể hiện một **mẫu hình nhất quán**: bổ sung từ khóa **làm tăng recall lớp 1** (mô hình dự báo "tăng" nhiều hơn) nhưng **làm giảm precision lớp 1** (nhiều dự báo "tăng" hơn là sai).
- Random Forest cho delta mạnh nhất: +7.6% recall lớp 1, nhưng mất 5.9% precision lớp 1.
- Logistic Regression cho delta recall nhỏ nhất (+1.3%), nhưng mất nhiều precision nhất (−4.4%).
- Mẫu hình này cho thấy đặc trưng từ khóa có **giá trị có điều kiện**: trong các chiến lược ưu tiên recall cao (ví dụ: không muốn bỏ lỡ tín hiệu tăng), việc bổ sung từ khóa có thể mang lại lợi ích mặc dù precision giảm.

**Thảo luận:** Tác động này có thể được giải thích bởi các từ khóa tích cực ("chia cổ tức", "tăng trưởng", "báo lãi") thường xuất hiện trong các kỳ có xu hướng giá tăng, do đó kéo mô hình về phía dự báo lớp 1 nhiều hơn. Đây là một tác động có hệ thống nhưng không đủ chính xác để cải thiện balanced accuracy tổng thể.

---

## 4.4. Góc 3 — Phân tích theo Mật độ Tin tức

Phân tích này kiểm tra liệu tác động của đặc trưng từ khóa có thay đổi theo mức độ phủ sóng tin tức của từng cổ phiếu-kỳ.

**Định nghĩa nhóm:**
- **Nhóm "dày"** (dense): news_count ≥ 15 bài/kỳ — n = 148 quan sát.
- **Nhóm "thưa"** (sparse): news_count < 15 bài/kỳ — n = 2 quan sát (không đủ đại diện).

**Bảng 4.6. Kết quả Nhóm "Tin Dày" (n=148)**

| Thuật toán | Config_A (BA) | Config_C (BA) | Δ (C−A) | Δ Recall lớp 1 | Δ Precision lớp 1 |
|---|---|---|---|---|---|
| Logistic Regression | 0.7201 | 0.6985 | −0.022 | +0.013 | −0.044 |
| Random Forest | 0.7661 | 0.7558 | −0.010 | +0.078 | −0.059 |
| XGBoost | 0.7266 | 0.7174 | −0.009 | +0.052 | −0.044 |
| LightGBM | 0.7255 | 0.7104 | −0.015 | +0.026 | −0.037 |

*Nguồn: `reports/news_density_analysis.csv`*

**Nhận xét:**

- Nhóm "tin dày" tái hiện **đúng mẫu hình Góc 2**: recall lớp 1 tăng, precision lớp 1 giảm, balanced accuracy giảm hoặc không đổi khi bổ sung từ khóa.
- Điều này cho thấy mẫu hình trade-off recall/precision **không phải do thiếu thông tin** (corpus thưa), mà là đặc tính cơ bản của đặc trưng tần suất từ khóa.
- Nhóm "thưa" (n=2) hoàn toàn không đủ mẫu để đưa ra bất kỳ kết luận thống kê nào.

---

## 4.5. Kiểm định H3 — Phân tích SHAP

### 4.5.1. Đóng góp tương đối của nhóm đặc trưng

**Giả thuyết H3:** Trong mô hình Config_C, các đặc trưng từ khóa đóng góp có ý nghĩa vào quyết định của mô hình (theo SHAP values), cho thấy mô hình thực sự "học" từ tín hiệu từ khóa.

Phân tích SHAP được thực hiện như một kiểm định chẩn đoán trên mô hình Config_C, nhằm xem mô hình có sử dụng nhóm từ khóa hay bỏ qua hoàn toàn nhóm này. Kết quả chẩn đoán Config_C cho thấy:

- **Nhóm kỹ thuật** (16 đặc trưng): đóng góp trung bình khoảng 68% tổng SHAP absolute value.
- **Nhóm từ khóa**: đóng góp trung bình khoảng 32% tổng SHAP absolute value trong mô hình Config_C chẩn đoán.

Mặc dù nhóm từ khóa có đóng góp trong Config_C, đóng góp này không chuyển thành cải thiện out-of-sample balanced accuracy. Sau full-text enrichment, mô hình tốt nhất ở production split là LightGBM Config_A; vì vậy news/keyword phù hợp hơn với vai trò evidence layer thay vì predictor chính.

### 4.5.2. Top từ khóa theo SHAP

**Bảng 4.7. Top từ khóa có giá trị SHAP trung bình cao nhất (LightGBM Config_C)**

| Từ khóa | Hướng kỳ vọng | SHAP trung bình (abs) | Nhất quán hướng |
|---|---|---:|---|
| tăng trưởng | positive | 0,00685 | Có |
| nợ xấu | negative | 0,00659 | Không |
| tăng trưởng | positive | 0,00637 | Có |
| nợ xấu | negative | 0,00580 | Không |
| báo lãi | positive | 0,00359 | Có |
| chia cổ tức | positive | 0,00357 | Có |
| nợ xấu | negative | 0,00332 | Có |

**Kiểm tra tính nhất quán hướng:** Trong số 318 đặc trưng/tín hiệu từ khóa được xếp hạng, **80/318 trường hợp (25,2%)** có SHAP value nhất quán với hướng kỳ vọng kinh tế của từ khóa. Tỷ lệ này thấp, nên không đủ để kết luận mô hình học được quan hệ kinh tế ổn định giữa từ khóa và xu hướng giá.

### 4.5.3. Kết luận H3

> **H3: ĐƯỢC ỦNG HỘ MỘT PHẦN.**

- Trong mô hình Config_C chẩn đoán, từ khóa có đóng góp SHAP đáng kể (~32%), tức mô hình không bỏ qua hoàn toàn nhóm đặc trưng này.
- Top từ khóa có SHAP cao nhất (như tăng trưởng, nợ xấu, báo lãi, chia cổ tức) đều có ý nghĩa tài chính rõ ràng.
- Tuy nhiên, tỷ lệ nhất quán hướng chỉ đạt 25,2%, thấp hơn kỳ vọng nếu mô hình học được quan hệ kinh tế ổn định giữa từ khóa và xu hướng giá.
- Kết luận: H3 được ủng hộ một phần theo nghĩa từ khóa có ảnh hưởng đến quyết định của Config_C, nhưng ảnh hưởng này nhiễu/không ổn định và không đủ để cải thiện hiệu suất dự báo tổng thể.

---

## 4.6. Thảo luận Tổng hợp

### 4.6.1. Tại sao H1 và H2 không được ủng hộ?

Có ba giải thích chính cho việc đặc trưng tần suất từ khóa không cải thiện hiệu suất dự báo:

**1. Giả thuyết thị trường hiệu quả dạng bán mạnh (Semi-strong EMH):**
Thông tin từ tin tức tài chính công khai có thể đã được phản ánh vào giá ngay trong kỳ xuất hiện tin, hoặc thậm chí trước đó (anticipation effect). Do đó, tần suất từ khóa trong một kỳ quan sát không có khả năng dự báo xu hướng kỳ sau. Kết quả này nhất quán với phần lớn nghiên cứu quốc tế về hiệu quả thông tin trên các thị trường có tính thanh khoản khá (Fama, 1970; Malkiel, 2003).

**2. Hấp thụ thông tin trong kỳ (Within-period absorption):**
Với đơn vị thời gian từ 2 tuần đến 1 quý, thông tin từ tin tức có đủ thời gian để được thị trường định giá lại trước khi kỳ quan sát kết thúc. Tần suất từ khóa đo lường khối lượng thông tin, không đo lường mức độ phản ứng giá còn lại.

**3. Giới hạn của corpus:**
Đặc trưng tần suất từ khóa là phép đo thô: không phân biệt context (ví dụ: "nợ xấu tăng" vs. "nợ xấu giảm"), không nắm bắt được cường độ cảm xúc, và không tính đến novelty của thông tin. Các nghiên cứu sử dụng NLP tinh vi hơn (sentiment scoring, topic modeling, LLM embeddings) có thể cho kết quả khác.

### 4.6.2. Giá trị của kết quả âm

Kết quả âm (null results) trong nghiên cứu khoa học không kém giá trị hơn kết quả dương. Nghiên cứu này cung cấp:

- **Bằng chứng thực nghiệm đáng tin cậy** về giới hạn của đặc trưng tần suất từ khóa thô trên thị trường Việt Nam, với phương pháp kiểm định chặt chẽ (time series split, BH-FDR).
- **Benchmarks định lượng** cho các nghiên cứu tiếp theo: bất kỳ phương pháp xử lý ngôn ngữ tự nhiên nào mới cần vượt qua ngưỡng balanced accuracy của Config_A (~0.73–0.76 với LightGBM) để chứng minh giá trị gia tăng thực sự.
- **Xác nhận tính mạnh mẽ** của đặc trưng kỹ thuật: Config_A với balanced accuracy 0.76 vượt xa cả hai baseline (0.50 và 0.49), khẳng định giá trị thực tiễn của phân tích kỹ thuật trong bối cảnh Việt Nam.

### 4.6.3. Những điểm nổi bật

Mặc dù H1 và H2 không được ủng hộ ở cấp độ tổng thể, nghiên cứu phát hiện một số tín hiệu đáng chú ý:

- **Mẫu hình trade-off recall/precision** (Góc 2) là phát hiện nhất quán và có ý nghĩa ứng dụng: nhà đầu tư ưu tiên recall cao có thể hưởng lợi từ việc bổ sung từ khóa.
- **Tín hiệu ổn định của "chia cổ tức" và "nợ xấu"**: hai từ khóa này liên tục cho p-value thô thấp trong nhiều cấu hình, gợi ý rằng chúng mang thông tin có liên quan đến xu hướng giá, dù chưa đủ mạnh sau hiệu chỉnh BH-FDR.
- **H3 được ủng hộ một phần**: ~32% đóng góp SHAP từ nhóm từ khóa cho thấy mô hình thực sự học được một phần từ tín hiệu ngôn ngữ.

---

## Chương 5: Kết luận

Chương này tổng kết các kết quả nghiên cứu, đóng góp khoa học, hạn chế, và hướng nghiên cứu tương lai.

---

## 5.1. Tổng kết ba giả thuyết

**Bảng 5.1. Tóm tắt kết quả kiểm định ba giả thuyết**

| Giả thuyết | Nội dung | Kết luận | Bằng chứng chính |
|---|---|---|---|
| **H1** | Config_C (kết hợp) > Config_A (kỹ thuật) về balanced accuracy | **Không được ủng hộ** | Δ(C−A) âm ở 3/4 thuật toán trên tất cả đơn vị thời gian |
| **H2** | Ít nhất một từ khóa có mối liên hệ thống kê có ý nghĩa (sau BH-FDR) với xu hướng giá | **Không được ủng hộ** | 0/71 từ khóa có ý nghĩa sau BH-FDR; tín hiệu "chia cổ tức" và "nợ xấu" nhất quán nhưng chưa đủ mạnh |
| **H3** | Từ khóa đóng góp có ý nghĩa vào quyết định mô hình (SHAP) | **Được ủng hộ một phần** | ~32% đóng góp SHAP; top từ khóa có ý nghĩa tài chính; 25.2% nhất quán hướng |

Sự kết hợp của H1 không được ủng hộ (hiệu suất tổng thể không cải thiện) và H3 được ủng hộ một phần (mô hình có học từ từ khóa nhưng không hiệu quả) phản ánh một thực tế quan trọng: mô hình học được tín hiệu từ khóa nhưng tín hiệu đó không đủ ổn định và đáng tin cậy để cải thiện khả năng dự báo ngoài mẫu.

---

## 5.2. Đóng góp khoa học

Nghiên cứu này đóng góp bốn giá trị chính cho cộng đồng nghiên cứu:

**1. Bằng chứng thực nghiệm về giới hạn của đặc trưng tần suất từ khóa trong bối cảnh Việt Nam.**
Đây là một trong số ít nghiên cứu kiểm định một cách hệ thống và nghiêm ngặt (time series split, BH-FDR, đa đơn vị thời gian) về khả năng dự báo của tần suất từ khóa tài chính tiếng Việt. Kết quả âm được báo cáo đầy đủ, cung cấp benchmark tham chiếu cho các nghiên cứu tiếp theo.

**2. Phương pháp luận kiểm định đa cấp độ.**
Nghiên cứu kết hợp ba phương pháp kiểm định thống kê độc lập (Chi-square/Fisher, Mann-Whitney U, Logistic đơn biến) với hiệu chỉnh BH-FDR, cùng phân tích SHAP, tạo ra một framework đánh giá toàn diện có thể tái sử dụng cho các thị trường mới nổi khác.

**3. Phân tích trade-off recall/precision (Góc 2).**
Phát hiện rằng đặc trưng từ khóa có tác động không đối xứng — tăng recall lớp 1 nhưng giảm precision lớp 1 — là đóng góp thực tiễn có giá trị, đặc biệt trong thiết kế hệ thống giao dịch với tiêu chí tối ưu khác nhau.

**4. Corpus dữ liệu và pipeline xử lý tiếng Việt.**
Việc xây dựng và công bố pipeline thu thập, xử lý, làm giàu toàn văn, và ghép tin tức tài chính tiếng Việt từ 6 nguồn (52.790 dòng bài-ticker, 45.968 unique URLs; 99,96% unique URLs có `full_text` sau repair) với dữ liệu giá 80 cổ phiếu HOSE trong giai đoạn 2022–2026 là đóng góp hạ tầng dữ liệu có ý nghĩa cho cộng đồng nghiên cứu trong nước.

---

## 5.3. Hạn chế của nghiên cứu

**1. Đặc trưng tần suất thô:**
Tần suất từ khóa không nắm bắt được ngữ cảnh, cường độ, hay sắc thái ngữ nghĩa. Một bài báo viết "nợ xấu giảm mạnh" và một bài viết "nợ xấu tăng cao" đều được tính là có từ khóa "nợ xấu", dẫn đến nhiễu thống kê đáng kể.

**2. Giới hạn về phạm vi nguồn tin và loại văn bản:**
Dữ liệu đã mở rộng lên 6 nguồn báo điện tử tài chính, nhưng vẫn chưa bao gồm báo cáo phân tích của công ty chứng khoán, thông cáo doanh nghiệp chính thức, dữ liệu mạng xã hội, diễn đàn nhà đầu tư hoặc dữ liệu giao dịch nội bộ. Vì vậy, kết luận chỉ áp dụng cho tin tức công khai dạng báo điện tử trong phạm vi corpus đã thu thập.

**3. Vấn đề thời điểm tin tức:**
Nghiên cứu ghép tin tức theo kỳ thời gian (quý/tháng) mà không xem xét chính xác thời điểm xuất hiện tin trong kỳ. Tin xuất hiện đầu kỳ và cuối kỳ có khả năng ảnh hưởng đến giá khác nhau về cơ bản.

**4. Thiếu phân tích nhân quả:**
Phân tích tương quan thống kê không thể xác định nhân quả. Tần suất từ khóa cao có thể là kết quả của biến động giá (reverse causality) hơn là nguyên nhân.

**5. Tập kiểm định nhỏ và một điểm thời gian:**
Tập kiểm định chỉ bao gồm một kỳ duy nhất (Q1/2025 hoặc tương đương), làm hạn chế khả năng tổng quát hóa kết quả. Hiệu suất có thể thay đổi đáng kể trong các điều kiện thị trường khác nhau (bull market, bear market, giai đoạn biến động cao).

**6. Giới hạn về SHAP và diễn giải:**
Phân tích SHAP cung cấp giải thích cục bộ và tổng quát, nhưng không trực tiếp xác nhận rằng mô hình học được mối quan hệ nhân quả đúng đắn. SHAP value cao của một từ khóa có thể phản ánh sự tương quan thống kê chứ không nhất thiết là quan hệ kinh tế thực sự.

**7. Phạm vi địa lý và thị trường:**
Kết quả chỉ áp dụng cho thị trường HOSE trong giai đoạn 2022–2026. Khả năng tổng quát hóa sang các thị trường khác (HNX, UPCOM) hoặc giai đoạn thời gian khác cần được kiểm định thêm.

---

## 5.4. Hướng nghiên cứu tương lai

**1. Phân tích cảm xúc ngôn ngữ tinh vi hơn:**
Thay vì tần suất từ khóa, sử dụng các mô hình phân tích cảm xúc chuyên biệt cho tiếng Việt tài chính (như PhoBERT fine-tuned trên corpus tài chính) để tạo ra đặc trưng sentiment score thay vì bag-of-words. Nghiên cứu sinh kỳ vọng phương pháp này có thể vượt qua giới hạn của đặc trưng tần suất thô.

**2. Kết hợp thông tin thời điểm tin tức:**
Phân tích ảnh hưởng của tin tức theo timestamp cụ thể (giờ/ngày), phân biệt tin xuất hiện trước và sau giờ đóng cửa, để xây dựng đặc trưng time-weighted news impact.

**3. Mở rộng corpus và nguồn dữ liệu:**
Tích hợp thêm các nguồn như báo cáo tài chính doanh nghiệp, thông cáo niêm yết chính thức (HNX, HOSE disclosure system), và dữ liệu mạng xã hội tài chính (Facebook groups, Reddit-equivalent) để tăng độ phủ thông tin.

**4. Mô hình xử lý chuỗi thời gian nâng cao:**
Áp dụng các kiến trúc học sâu như LSTM, Transformer, hay temporal fusion transformer để nắm bắt phụ thuộc dài hạn giữa chuỗi tin tức và chuỗi giá — thứ mà các mô hình ML truyền thống với window cố định không thể làm được.

**5. Kiểm định ngoài mẫu trên nhiều giai đoạn:**
Mở rộng tập kiểm định sang nhiều kỳ không liên tiếp (ví dụ: 2022Q3, 2023Q2, 2024Q1, 2025Q1) để đánh giá tính ổn định của kết quả theo điều kiện thị trường khác nhau và giảm thiểu rủi ro kết quả phụ thuộc vào một giai đoạn cụ thể.

**6. Phân tích theo ngành và quy mô vốn hóa:**
Kiểm định liệu tác động của từ khóa tài chính có khác nhau đáng kể giữa các nhóm ngành (ngân hàng, bất động sản, sản xuất) hay nhóm quy mô (large-cap, mid-cap, small-cap). Kết quả của nghiên cứu này gợi ý rằng từ khóa "nợ xấu" có thể đặc biệt liên quan đến ngành ngân hàng.

---

## Tài liệu Tham khảo

1. **Bollen, J., Mao, H., & Zeng, X.** (2011). Twitter mood predicts the stock market. *Journal of Computational Science*, 2(1), 1–8. https://doi.org/10.1016/j.jocs.2010.12.007

2. **Chen, T., & Guestrin, C.** (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794. https://doi.org/10.1145/2939672.2939785

3. **Fama, E. F.** (1970). Efficient capital markets: A review of theory and empirical evidence. *Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486

4. **Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y.** (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 3146–3154.

5. **Loughran, T., & McDonald, B.** (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x

6. **Lundberg, S. M., & Lee, S.-I.** (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4765–4774.

7. **Malkiel, B. G.** (2003). The efficient market hypothesis and its critics. *Journal of Economic Perspectives*, 17(1), 59–82. https://doi.org/10.1257/089533003321164958

8. **Nguyen, T. H., Shirai, K., & Velcin, J.** (2015). Sentiment analysis on social media for stock movement prediction. *Expert Systems with Applications*, 42(24), 9603–9611. https://doi.org/10.1016/j.eswa.2015.07.052

9. **Pang, B., & Lee, L.** (2008). Opinion mining and sentiment analysis. *Foundations and Trends in Information Retrieval*, 2(1–2), 1–135. https://doi.org/10.1561/1500000011

10. **Schumaker, R. P., & Chen, H.** (2009). Textual analysis of stock market prediction using breaking financial news: The AZFin text system. *ACM Transactions on Information Systems*, 27(2), 1–19. https://doi.org/10.1145/1462198.1462204

11. **Shiller, R. J.** (2000). *Irrational Exuberance*. Princeton University Press.

12. **Tetlock, P. C.** (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139–1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x

13. **Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S.** (2008). More than words: Quantifying language to measure firms' fundamentals. *Journal of Finance*, 63(3), 1437–1467. https://doi.org/10.1111/j.1540-6261.2008.01362.x

14. **Benjamini, Y., & Hochberg, Y.** (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological)*, 57(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x

15. **Breiman, L.** (2001). Random forests. *Machine Learning*, 45(1), 5–32. https://doi.org/10.1023/A:1010933404324

---

*Luận văn hoàn thành tại TP. Hồ Chí Minh, năm 2026.*
