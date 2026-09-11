---
geometry: "top=2.5cm, bottom=2.5cm, left=3cm, right=2cm"
fontsize: 12pt
mainfont: "Times New Roman"
header-includes:
  - \usepackage{titlesec}
  - \usepackage{longtable}
  - \usepackage{array}
  - \usepackage{booktabs}
  - \usepackage{caption}
  - \usepackage{ragged2e}
  - \usepackage{setspace}
  - \usepackage{etoolbox}
  - \setstretch{1.2}
  - \setlength{\parindent}{1cm}
  - \setlength{\parskip}{0.25em}
  - \AtBeginEnvironment{longtable}{\small}
  - \titleformat{\section}{\normalfont\Large\bfseries}{\thesection.}{0.5em}{}
  - \titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection.}{0.5em}{}
  - \titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{\thesubsubsection.}{0.5em}{}
---


\begin{titlepage}
\begin{center}

\textbf{ĐẠI HỌC QUỐC GIA TP.HCM}\\
\textbf{TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN}

\vspace{2cm}

Họ tên HVCH: Ngô Minh Trí\\
Mã số học viên: 24C01024

\vspace{1.5cm}

{\LARGE \textbf{ĐỀ CƯƠNG NGHIÊN CỨU ĐỀ TÀI\\LUẬN VĂN THẠC SĨ}}

\vspace{2cm}

\end{center}

\noindent \underline{Tên đề tài:} \parbox[t]{0.78\textwidth}{\justifying Hệ thống hỗ trợ quyết định cổ phiếu dựa trên tín hiệu học máy và bằng chứng tin tức ngữ nghĩa có truy vết}

\vspace{0.5cm}

\noindent \underline{Tên tiếng Anh:} \parbox[t]{0.72\textwidth}{\justifying Evidence-Grounded Stock Decision Support Using Machine Learning Signals and Semantic News Materiality}

\vspace{0.8cm}

\noindent \underline{Ngành:} Khoa học Dữ liệu

\vspace{0.5cm}

\noindent \underline{Mã số ngành:} 8460108

\vspace{2.5cm}

\begin{center}
\underline{Xác nhận của giảng viên hướng dẫn}\\
\textit{(Ký tên và ghi rõ họ tên)}

\vspace{2.5cm}

\underline{Họ tên:} .......................................

\vspace{\fill}

TP. HCM, tháng 08 năm 2026

\end{center}
\end{titlepage}

\begin{center}
{\large \textbf{NỘI DUNG CHÍNH CỦA NGHIÊN CỨU}}
\end{center}

\vspace{0.5cm}

# 1. Giới thiệu tổng quan

## 1.1. Bối cảnh nghiên cứu

Thị trường chứng khoán Việt Nam ngày càng tạo ra lượng lớn dữ liệu giao dịch và tin tức tài chính. Dữ liệu giá và khối lượng cho phép xây dựng đặc trưng kỹ thuật phục vụ học máy. Tin tức tiếng Việt phản ánh các sự kiện doanh nghiệp như kết quả kinh doanh, cổ tức, phát hành, nợ vay, dự án, quản trị và rủi ro pháp lý. Hai nguồn thông tin này bổ sung cho nhau nhưng thường được khai thác tách rời.

Trong thực tiễn phân tích, việc chỉ biết xác suất tăng hoặc thứ hạng của một mã cổ phiếu thường chưa đủ. Người dùng còn cần hiểu vì sao mã đó được chọn, bằng chứng tin tức nào hỗ trợ hoặc làm suy yếu luận điểm, rủi ro nào cần theo dõi, và sau kỳ nắm giữ thì luận điểm ban đầu đúng hay sai vì lý do gì. Khoảng cách giữa tín hiệu mô hình và hồ sơ quyết định có thể giải thích, theo dõi, hậu kiểm là vấn đề trung tâm của đề tài.

Đề tài không dùng mô hình ngôn ngữ lớn (LLM) như mô hình dự báo giá độc lập. Định hướng nghiên cứu theo chuỗi:

```text
Tín hiệu học máy từ đặc trưng kỹ thuật
→ kiểm định vai trò tin tức như đặc trưng bổ sung
→ trích xuất bằng chứng tin tức ngữ nghĩa có cấu trúc
→ gói bằng chứng có truy vết
→ thẻ quyết định có kiểm soát
→ bảng điều khiển theo dõi và hậu kiểm
```

Tin tức được xét ở hai vai trò. Vai trò thứ nhất là đặc trưng bổ sung cho mô hình học máy, cần kiểm định trung thực. Vai trò thứ hai là lớp bằng chứng phục vụ giải thích và hỗ trợ quyết định. Đề tài không giả định trước rằng đưa tin tức vào mô hình sẽ mặc định làm tăng hiệu quả dự báo. Nếu một số cách biểu diễn tin tức không tạo giá trị dự báo gia tăng ổn định, kết quả đó vẫn có ý nghĩa khoa học và là cơ sở để chuyển trọng tâm sang lớp bằng chứng cùng hệ hỗ trợ quyết định có truy vết.

## 1.2. Tổng quan nghiên cứu trong và ngoài nước

### 1.2.1. Nghiên cứu quốc tế

Dự báo xu hướng giá cổ phiếu bằng học máy dựa trên dữ liệu giá, khối lượng và chỉ báo kỹ thuật là hướng nghiên cứu đã phát triển lâu. Song song đó, nhiều công trình khai thác văn bản tài chính qua phân tích cảm xúc, biểu diễn từ khóa hoặc TF-IDF, mô hình ngôn ngữ tiền huấn luyện và trích xuất sự kiện. Hướng event-driven cho thấy tin tức có thể hữu ích hơn khi được biểu diễn ở mức sự kiện và ngữ cảnh, thay vì chỉ đếm từ.

Gần đây, LLM được thử nghiệm trong phân tích tài chính, đồng thời bộc lộ rủi ro ảo giác, thiếu trung thực với bằng chứng đầu vào và khó kiểm soát khi dùng trực tiếp cho dự báo giá. Xu hướng phù hợp hơn là dùng LLM cho tác vụ có cấu trúc và ràng buộc bằng chứng, rồi đặt kết quả trong hệ hỗ trợ quyết định có giám sát và hậu kiểm.

### 1.2.2. Nghiên cứu trong nước

Tại Việt Nam, nhiều nghiên cứu học máy tập trung vào dữ liệu giá và khối lượng. Một số công trình khai thác tin tức hoặc cảm xúc văn bản tiếng Việt, nhưng vẫn còn hạn chế ở ba điểm: biểu diễn tin tức thường dừng ở từ khóa hoặc cảm xúc tổng hợp; việc so sánh các cách biểu diễn chưa luôn bảo đảm cùng mẫu, cùng mục tiêu và kiểm soát thời gian; ít công trình đi tiếp từ tín hiệu mô hình tới hồ sơ quyết định có truy vết, theo dõi và hậu kiểm.

## 1.3. Khoảng trống nghiên cứu

- Nhiều nghiên cứu dừng ở dự báo tăng hoặc giảm, chưa tổ chức đủ vòng đời quyết định gồm chọn tín hiệu, giải thích bằng chứng, theo dõi và hậu kiểm.
- Đặc trưng tần suất từ khóa dễ tái lập nhưng thiếu độ liên quan theo mã, mức độ trọng yếu, loại sự kiện, chiều tác động và đoạn bằng chứng nguyên văn.
- Việc kết luận tin tức “có ích” hoặc “vô ích” dễ lệch nếu không tách vai trò tin tức như biến dự báo và như bằng chứng hỗ trợ quyết định.
- So sánh keyword, sentiment và semantic dễ thiếu kỷ luật cùng mẫu quan sát và kiểm soát rò rỉ thời gian.
- Các bảng điều khiển phân tích cổ phiếu thường nghiêng hiển thị thông tin, chưa gắn với đánh giá mức bám bằng chứng và truy vết nguồn.

---

# 2. Mục đích và ý nghĩa nghiên cứu

## 2.1. Tính cấp thiết

Nhà phân tích phải xử lý đồng thời tín hiệu kỹ thuật và thông tin sự kiện. Chỉ tối ưu độ chính xác phân loại mà thiếu bằng chứng và truy vết sẽ hạn chế tính sử dụng. Chỉ tóm tắt tin tức bằng LLM mà thiếu tín hiệu định lượng và kiểm soát bằng chứng lại dễ dẫn tới diễn giải không kiểm chứng. Do đó, cần một nghiên cứu ứng dụng kết hợp đánh giá tín hiệu học máy, kiểm định trung thực vai trò tin tức, và hiện thực hệ hỗ trợ quyết định có thẻ quyết định cùng bảng điều khiển truy vết.

Đơn vị tổng hợp dữ liệu và cửa sổ đánh giá tín hiệu sẽ được chốt trong giai đoạn thực nghiệm dựa trên độ dày tin tức, đặc điểm biến động giá và yêu cầu kiểm soát thời gian. Đề tài không khóa cứng một kỳ duy nhất ngay từ đề cương.

## 2.2. Ý nghĩa lý luận

- Làm rõ sự khác nhau giữa tin tức như đặc trưng dự báo và tin tức như bằng chứng có cấu trúc.
- Bổ sung bằng chứng thực nghiệm về giới hạn của biểu diễn tần suất từ khóa trên thị trường Việt Nam.
- Đề xuất khung đánh giá biểu diễn sự kiện trọng yếu có ngữ nghĩa cho tin tức tài chính tiếng Việt.
- Kết nối học máy có khả năng giải thích, kiểm soát tính trung thực của LLM và thiết kế hệ hỗ trợ quyết định có giám sát vòng đời.

## 2.3. Ý nghĩa thực tiễn

- Xây dựng pipeline nghiên cứu căn chỉnh point-in-time giữa giá, tin tức, tín hiệu và bằng chứng.
- Hỗ trợ kiểm định giá trị dự báo gia tăng của từng cách biểu diễn tin tức so với mô hình kỹ thuật.
- Cung cấp gói bằng chứng và thẻ quyết định có kiểm soát để trình bày luận điểm, rủi ro và điều kiện theo dõi.
- Xây dựng prototype bảng điều khiển phục vụ theo dõi, cập nhật bối cảnh và hậu kiểm sau kỳ nắm giữ.

---

# 3. Mục tiêu nghiên cứu

## 3.1. Mục tiêu tổng quát

Xây dựng và đánh giá hệ thống hỗ trợ quyết định cổ phiếu theo hướng dẫn dắt bởi tín hiệu học máy, sử dụng tin tức tài chính tiếng Việt như lớp bằng chứng ngữ nghĩa có truy vết, kết hợp thẻ quyết định có kiểm soát và bảng điều khiển theo dõi/hậu kiểm. Đề tài kiểm định trung thực vai trò của tin tức, không giả định trước rằng tin tức mặc định làm tăng hiệu quả dự báo.

## 3.2. Mục tiêu cụ thể

1. Xây dựng bộ dữ liệu giá và tin tức được căn chỉnh theo nguyên tắc point-in-time.
2. Xây dựng và đánh giá tín hiệu học máy từ đặc trưng kỹ thuật để tạo xác suất, xếp hạng và danh sách ứng viên phân tích.
3. Xây dựng baseline tần suất từ khóa và kiểm định giá trị dự báo gia tăng so với mô hình kỹ thuật.
4. Xây dựng schema và quy trình trích xuất sự kiện trọng yếu có ngữ nghĩa gồm độ liên quan, mức độ trọng yếu, loại sự kiện, chiều tác động và đoạn bằng chứng.
5. So sánh các cấu hình đặc trưng kỹ thuật và tin tức theo hợp đồng thực nghiệm đã khóa trước đánh giá chính.
6. Xây dựng gói bằng chứng, thẻ quyết định có kiểm soát và prototype bảng điều khiển theo dõi/hậu kiểm.
7. Xác định phạm vi diễn giải và giới hạn claim phù hợp với bằng chứng thu được.

---

# 4. Câu hỏi nghiên cứu và giả thuyết nghiên cứu

## 4.1. Câu hỏi nghiên cứu

1. Tín hiệu học máy dựa trên đặc trưng kỹ thuật có tạo được lớp chọn ứng viên hữu ích cho hệ hỗ trợ quyết định hay không?
2. Đặc trưng tần suất từ khóa có tạo giá trị dự báo gia tăng ổn định ngoài đặc trưng kỹ thuật hay không?
3. Biểu diễn sự kiện trọng yếu có ngữ nghĩa có phù hợp hơn baseline từ khóa hoặc rule cho việc cấu trúc hóa bằng chứng tin tức hay không?
4. Khi so sánh các cấu hình kỹ thuật và tin tức trên cùng giao thức đánh giá đã khóa trước, vai trò của tin tức như biến dự báo thể hiện như thế nào?
5. Gói bằng chứng, thẻ quyết định có kiểm soát và bảng điều khiển truy vết có cải thiện khả năng trình bày bằng chứng, rủi ro và truy vết so với baseline chỉ dùng tín hiệu học máy hoặc mẫu rule hay không?

Câu hỏi 4 mang tính kiểm định trung tính. Đề tài không đặt giả thuyết chiều dương bắt buộc rằng cấu hình có tin tức sẽ vượt cấu hình kỹ thuật. Nếu có phân tích liên hệ giữa đặc tính sự kiện và biến động giá sau sự kiện, phân tích này chỉ mang tính khám phá hỗ trợ diễn giải, không phải giả thuyết chính và không được suy thành quan hệ nhân quả.

## 4.2. Giả thuyết nghiên cứu

- **H1:** Trong các thiết lập thực nghiệm của đề tài, đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt không tạo ra giá trị dự báo gia tăng ổn định so với mô hình chỉ dùng đặc trưng kỹ thuật.
- **H2:** Biểu diễn tin tức theo hướng sự kiện trọng yếu có ngữ nghĩa phù hợp hơn baseline từ khóa hoặc rule cho mục tiêu cấu trúc hóa bằng chứng phục vụ phân tích và hỗ trợ quyết định.
- **H3:** Hệ thống hỗ trợ quyết định gồm gói bằng chứng, thẻ quyết định có kiểm soát và bảng điều khiển truy vết giúp trình bày bằng chứng, rủi ro và truy vết tốt hơn so với baseline chỉ dựa trên tín hiệu học máy hoặc mẫu rule.

Các giả thuyết mang tính kiểm định thực nghiệm. Kết quả không cải thiện dự báo khi bổ sung tin tức vẫn là kết quả hợp lệ. H2 được đánh giá trên tiêu chí biểu diễn và chất lượng bằng chứng, không đồng nhất với cải thiện chỉ số dự báo. H3 được đánh giá trên mức bám bằng chứng, kiểm soát nội dung phát sinh ngoài bằng chứng, khả năng nêu rủi ro và truy vết; không suy thành gia tăng lợi nhuận hoặc chất lượng quyết định của con người.

---

# 5. Đối tượng và phạm vi nghiên cứu

## 5.1. Đối tượng nghiên cứu

- Dữ liệu giao dịch của nhóm cổ phiếu niêm yết trên Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE).
- Tin tức tài chính tiếng Việt liên quan đến các cổ phiếu được chọn.
- Tín hiệu học máy từ đặc trưng kỹ thuật và các cách biểu diễn tin tức.
- Gói bằng chứng, thẻ quyết định và bảng điều khiển hỗ trợ theo dõi, cập nhật và hậu kiểm.

## 5.2. Phạm vi nghiên cứu

| Tiêu chí | Phạm vi |
|---|---|
| Thị trường | HOSE |
| Giai đoạn dữ liệu | Khoảng vài năm gần đây có đủ biến động thị trường; mốc cụ thể phụ thuộc tính khả dụng của dữ liệu |
| Universe cổ phiếu | Nhóm mã thanh khoản, có dữ liệu liên tục và phủ tin tức đủ dùng; danh sách cuối cùng chốt khi triển khai |
| Dữ liệu giá | OHLCV theo ngày, tổng hợp theo kỳ phân tích phù hợp |
| Tầm đánh giá tín hiệu | Cửa sổ ngắn đến trung hạn được chốt trước thực nghiệm chính |
| Dữ liệu văn bản | Tin tức tài chính tiếng Việt từ nguồn báo hoặc chuyên trang phù hợp |
| Vai trò học máy | Tạo xác suất, xếp hạng và giải thích kỹ thuật |
| Vai trò tin tức | Kiểm định như đặc trưng bổ sung và khai thác như bằng chứng có cấu trúc |
| Vai trò LLM | Trích xuất cấu trúc và sinh thẻ quyết định có ràng buộc bằng chứng |
| Sản phẩm ứng dụng | Prototype bảng điều khiển nghiên cứu phục vụ truy vết, theo dõi và hậu kiểm |
| Hình thức quyết định | Hỗ trợ phân tích; người dùng là người ra quyết định cuối |

## 5.3. Giới hạn của đề tài

- Không xây dựng hệ thống giao dịch tự động và không đưa ra khuyến nghị đầu tư thực tế.
- Không cam kết lợi nhuận hoặc hiệu quả triển khai production.
- Không kết luận quan hệ nhân quả từ phân tích liên hệ sự kiện và biến động giá.
- Nhãn ngữ nghĩa sinh từ mô hình được xem là pseudo-label, không phải nhãn chuẩn của chuyên gia.
- Rubric tự động đo chất lượng trình bày và mức bám bằng chứng, không đo chất lượng quyết định của con người.
- Bảng điều khiển là prototype nghiên cứu, chưa phải hệ thống vận hành đầy đủ.
- Đề tài không giả định mọi cách đưa tin tức vào mô hình sẽ làm tăng hiệu quả dự báo.
- Có thể tồn tại survivorship bias do ưu tiên cổ phiếu có dữ liệu liên tục; hạn chế này sẽ được ghi nhận khi phân tích kết quả.

---

# 6. Phương pháp nghiên cứu

## 6.1. Thiết kế tổng quát

1. Lựa chọn nhóm cổ phiếu và thu thập dữ liệu giá, tin tức.
2. Căn chỉnh point-in-time và xây biến mục tiêu.
3. Trích xuất đặc trưng kỹ thuật, baseline từ khóa và đặc trưng sự kiện trọng yếu có ngữ nghĩa.
4. Huấn luyện, đánh giá tín hiệu học máy và so sánh cấu hình theo hợp đồng đã khóa trước.
5. Xây gói bằng chứng, thẻ quyết định có kiểm soát và đánh giá theo rubric.
6. Hiện thực prototype bảng điều khiển theo dõi, truy vết và hậu kiểm.
7. Tổng hợp kết quả và giới hạn diễn giải.

## 6.2. Lựa chọn cổ phiếu nghiên cứu

Nhóm cổ phiếu được chọn từ cổ phiếu phổ thông trên HOSE theo các nguyên tắc: vốn hóa và thanh khoản ổn định; dữ liệu giao dịch đủ liên tục; mức độ phủ tin tức đủ cho phân tích; loại trừ chứng quyền, ETF và công cụ phái sinh nếu không phục vụ trực tiếp câu hỏi nghiên cứu. Danh sách cuối cùng được chốt sau khi kiểm tra tính đầy đủ của dữ liệu.

## 6.3. Biến mục tiêu và nguyên tắc thời gian

Đề tài đánh giá tín hiệu theo cửa sổ ngắn đến trung hạn được chốt trước thực nghiệm chính. Biến mục tiêu có thể là nhãn phân loại hoặc tiêu chí xếp hạng phù hợp với việc chọn ứng viên phân tích. Định nghĩa nhãn, quy tắc loại bản ghi thiếu dữ liệu và cách xử lý quan sát biên sẽ được khóa trước đánh giá chính.

Nguyên tắc thời gian áp dụng thống nhất: chỉ dùng dữ liệu đã khả dụng tại thời điểm quyết định; không dùng thông tin tương lai để tạo đặc trưng hoặc viết thẻ quyết định ban đầu; phần theo dõi chỉ ghi nhận sự kiện sau thời điểm quyết định; phần hậu kiểm chỉ mở sau khi kết thúc cửa sổ đánh giá. Nếu đơn vị tổng hợp hoặc cửa sổ đánh giá cần điều chỉnh, mọi thay đổi liên quan đến đánh giá chính phải được ghi nhận trước khi chạy lại.

## 6.4. Dữ liệu giao dịch và đặc trưng kỹ thuật

Dữ liệu giao dịch theo ngày gồm giá mở, đóng, cao, thấp và khối lượng, thu thập từ nguồn công khai phù hợp với thị trường Việt Nam. Các nhóm đặc trưng kỹ thuật dự kiến gồm lợi suất, biến động, thanh khoản, xu hướng, động lượng và chỉ báo phổ biến như RSI, MACD, SMA, EMA, Bollinger Bands. Danh sách cụ thể có thể điều chỉnh trong thực nghiệm.

## 6.5. Dữ liệu tin tức và baseline từ khóa

Tin tức tài chính tiếng Việt được thu thập từ nguồn có chuyên mục tài chính hoặc chứng khoán. Mỗi bài dự kiến gồm tiêu đề, nội dung hoặc mô tả ngắn, thời điểm đăng, nguồn và mã cổ phiếu liên quan. Các bước xử lý gồm làm sạch văn bản, loại trùng, gắn mã và căn chỉnh thời điểm khả dụng theo point-in-time.

Baseline từ khóa phản ánh tần suất xuất hiện của từ khóa hoặc cụm từ khóa tài chính. Các biến dự kiến gồm tần suất, tần suất chuẩn hóa, trọng số dạng TF-IDF hoặc tương đương, và mức độ phủ tin tức. Lớp này dùng để kiểm định H1, không phải biểu diễn cuối cùng của đề tài.

## 6.6. Trích xuất sự kiện trọng yếu có ngữ nghĩa

Đơn vị đầu vào là bài báo hoặc đơn vị tin đã gắn mã. Đầu ra cấu trúc tập trung vào các trường: mức độ liên quan tới mã, mức độ trọng yếu, loại sự kiện, chiều tác động, mức bất định hoặc tính mới, đoạn bằng chứng nguyên văn và thông tin nguồn. Nhãn được xử lý như pseudo-label. Đề tài đánh giá độ ổn định giữa các lần gán nhãn, tính hợp lệ của đoạn bằng chứng, mức đầy đủ provenance và mức phù hợp hơn so với baseline rule hoặc keyword. Mẫu kiểm tra chất lượng bởi người, nếu có, chỉ là cầu nối kiểm soát chứ không thay cho bộ nhãn chuẩn đầy đủ.

## 6.7. Mô hình học máy và so sánh cấu hình

Các thuật toán dự kiến gồm Logistic Regression, Random Forest, XGBoost hoặc LightGBM. Cấu hình so sánh dự kiến:

| Cấu hình | Thành phần chính |
|---|---|
| Technical-only | Đặc trưng kỹ thuật |
| Technical + Keyword | Thêm đặc trưng tần suất từ khóa |
| Technical + Semantic | Thêm đặc trưng sự kiện trọng yếu có ngữ nghĩa |

Mô hình và cấu hình đánh giá chính được khóa trước khi chạy. Đề tài có thể dùng thêm baseline đơn giản như majority class hoặc naive momentum để tham chiếu. So sánh cấu hình nhằm trả lời các câu hỏi về tín hiệu kỹ thuật, giá trị gia tăng của từ khóa và vai trò tin tức như biến dự báo; không đặt giả thuyết bắt buộc rằng cấu hình có tin tức sẽ vượt cấu hình kỹ thuật.

## 6.8. Đánh giá tín hiệu và kiểm định thống kê

Việc chia tập tuân thủ nguyên tắc thời gian để tránh rò rỉ thông tin tương lai. Chỉ số đánh giá dự kiến gồm Balanced Accuracy, AUC-ROC, Precision, Recall, F1-score và các chỉ số xếp hạng phù hợp. Các so sánh chính ưu tiên đối chiếu theo cặp ngoài mẫu trên cùng tập quan sát hợp lệ, kèm khoảng tin cậy dạng bootstrap hoặc tương đương, kiểm định hoán vị hoặc dấu khi phù hợp, và hiệu chỉnh đa kiểm định theo họ giả thuyết đã khai báo. Kết quả không vượt ngưỡng hoặc không ước lượng được vẫn được báo cáo đầy đủ. Các phương pháp giải thích mô hình như feature importance, permutation importance hoặc SHAP được dùng như công cụ diễn giải, không phải giả thuyết độc lập.

## 6.9. Gói bằng chứng, thẻ quyết định và bảng điều khiển

Gói bằng chứng tổng hợp tín hiệu học máy, giải thích kỹ thuật, bằng chứng tin tức, mã nguồn và cảnh báo thiếu thông tin. Thẻ quyết định được sinh theo mẫu có kiểm soát với các thành phần dự kiến: luận điểm, bằng chứng hỗ trợ, rủi ro, khoảng trống thông tin, điều kiện theo dõi và giới hạn diễn giải.

Ba nhóm đối chứng dự kiến gồm mẫu rule-based, thẻ chỉ dựa trên tín hiệu học máy, và thẻ dùng đầy đủ gói bằng chứng. Rubric tập trung vào mức bám bằng chứng, kiểm soát nội dung phát sinh ngoài bằng chứng, khả năng nêu rủi ro, chất lượng gợi ý theo dõi và tính rõ ràng.

Prototype bảng điều khiển phục vụ H3 với các vùng chức năng dự kiến: tổng quan tín hiệu, giải thích kỹ thuật, bằng chứng tin tức, thẻ quyết định, timeline theo dõi, hậu kiểm sau kỳ đánh giá và panel provenance. Bảng điều khiển được đánh giá theo tính đầy đủ, khả năng truy vết và an toàn thời gian trên một số tình huống điển hình; không định vị như hệ thống giao dịch tự động.

## 6.10. Kiểm soát rò rỉ dữ liệu và kỷ luật diễn giải

- Chỉ dùng dữ liệu đã có tại thời điểm quyết định.
- Không đưa kết quả sau cửa sổ đánh giá vào gói bằng chứng hoặc thẻ quyết định ban đầu.
- Chuẩn hóa, chọn đặc trưng và huấn luyện chỉ thực hiện trên phần dữ liệu được phép tại từng fold.
- Tách rõ vùng quyết định ban đầu, vùng theo dõi và vùng hậu kiểm.
- Pseudo-label, phân tích liên hệ sự kiện--biến động giá và mô phỏng xếp hạng được diễn giải đúng lớp claim tương ứng.

---

# 7. Công cụ và thư viện dự kiến

| Nhóm | Công cụ / Thư viện | Mục đích |
|---|---|---|
| Ngôn ngữ lập trình | Python | Ngôn ngữ chính |
| Xử lý dữ liệu | Pandas, NumPy | Làm sạch, căn chỉnh, tổng hợp |
| Dữ liệu thị trường | vnstock hoặc nguồn tương đương | Thu thập dữ liệu giá |
| Thu thập tin tức | BeautifulSoup, Scrapy hoặc công cụ tương đương | Thu thập bài viết |
| Xử lý tiếng Việt | underthesea, VnCoreNLP hoặc công cụ phù hợp | Tách từ, chuẩn hóa |
| Học máy | scikit-learn, XGBoost, LightGBM | Tín hiệu và so sánh cấu hình |
| Giải thích mô hình | SHAP, permutation importance | Diễn giải đặc trưng kỹ thuật |
| LLM / API | Nhà cung cấp mô hình phù hợp qua API | Trích xuất ngữ nghĩa và sinh thẻ quyết định |
| Đánh giá thống kê | SciPy hoặc công cụ tương đương | So sánh ngoài mẫu và kiểm soát đa kiểm định |
| Bảng điều khiển | Streamlit, Dash, FastAPI hoặc stack tương đương | Prototype truy vết và theo dõi |
| Trực quan hóa | Matplotlib, Seaborn, Plotly | Biểu đồ và báo cáo |

Danh sách công cụ có thể được điều chỉnh trong quá trình triển khai.

---

# 8. Kết quả dự kiến

1. Bộ dữ liệu và pipeline căn chỉnh point-in-time giữa giá, tin tức, tín hiệu và bằng chứng.
2. Kết quả đánh giá tín hiệu học máy từ đặc trưng kỹ thuật.
3. Kết luận kiểm định về giá trị dự báo gia tăng của đặc trưng tần suất từ khóa.
4. Schema sự kiện trọng yếu có ngữ nghĩa kèm kiểm tra chất lượng biểu diễn và provenance.
5. Kết quả so sánh các cấu hình kỹ thuật và tin tức theo hợp đồng đã khóa trước, gồm cả trường hợp không cải thiện hoặc không ước lượng được.
6. Tập gói bằng chứng, thẻ quyết định và kết quả đánh giá rubric.
7. Prototype bảng điều khiển theo dõi, truy vết và hậu kiểm trên các tình huống điển hình.
8. Ma trận claim--evidence--limitation phục vụ diễn giải trung thực kết quả luận văn.

---

# 9. Đóng góp dự kiến của đề tài

- Cung cấp bằng chứng thực nghiệm có kiểm soát về giới hạn của biểu diễn tần suất từ khóa trong phân tích cổ phiếu Việt Nam.
- Đề xuất và đánh giá schema bằng chứng tin tức theo hướng sự kiện trọng yếu có ngữ nghĩa.
- Thiết kế giao thức so sánh các cách dùng tin tức theo hướng trung thực với dữ liệu, chấp nhận kết quả không cải thiện dự báo như kết quả khoa học hợp lệ.
- Hiện thực kiến trúc hỗ trợ quyết định dẫn dắt bởi học máy, dùng LLM có ràng buộc bằng chứng và bảng điều khiển truy vết vòng đời quyết định.
- Tách rõ các lớp claim giữa dự báo, chất lượng biểu diễn, chất lượng thẻ quyết định và khả năng truy vết.

---

# 10. Nơi thực hiện đề tài

Trường Đại học Khoa học Tự nhiên - Đại học Quốc gia Thành phố Hồ Chí Minh.

---

# 11. Tài liệu tham khảo dự kiến

1. Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. *arXiv preprint* arXiv:1908.10063. https://arxiv.org/abs/1908.10063
2. Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. *Journal of Computational Science*, 2(1), 1--8. https://doi.org/10.1016/j.jocs.2010.12.007
3. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785--794). https://doi.org/10.1145/2939672.2939785
4. Ding, X., Zhang, Y., Liu, T., & Duan, J. (2015). Deep learning for event-driven stock prediction. In *Proceedings of the 24th International Joint Conference on Artificial Intelligence* (pp. 2327--2333).
5. Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys*, 55(12), Article 248. https://doi.org/10.1145/3571730
6. Li, X., Xie, H., Chen, L., Wang, J., & Deng, X. (2014). News impact on stock price return via sentiment analysis. *Knowledge-Based Systems*, 69, 14--23. https://doi.org/10.1016/j.knosys.2014.04.022
7. Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. *SSRN Working Paper* No. 4412788. https://doi.org/10.2139/ssrn.4412788
8. Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. In *Advances in Neural Information Processing Systems* (Vol. 30, pp. 4765--4774).
9. Murphy, J. J. (1999). *Technical analysis of the financial markets*. New York Institute of Finance.
10. Nassirtoussi, A. K., Aghabozorgi, S., Wah, T. Y., & Ngo, D. C. L. (2014). Text mining for market prediction: A systematic review. *Expert Systems with Applications*, 41(16), 7653--7670. https://doi.org/10.1016/j.eswa.2014.06.009
11. Nguyen, D. Q., & Nguyen, A. T. (2020). PhoBERT: Pre-trained language models for Vietnamese. In *Findings of the Association for Computational Linguistics: EMNLP 2020* (pp. 1037--1042). https://doi.org/10.18653/v1/2020.findings-emnlp.92
12. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825--2830.
13. Schumaker, R. P., & Chen, H. (2009). Textual analysis of stock market prediction using breaking financial news. *ACM Transactions on Information Systems*, 27(2), Article 12. https://doi.org/10.1145/1462198.1462204
14. Vu, L. T., Pham, T. T. T., Kieu, D. T., & Pham, H. T. (2023). Sentiments extracted from news and stock market reactions in Vietnam. *International Journal of Financial Studies*, 11(3), 101. https://doi.org/10.3390/ijfs11030101
15. Xu, Y., & Cohen, S. B. (2018). Stock movement prediction from tweets and historical prices. In *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics* (pp. 1970--1979). https://doi.org/10.18653/v1/P18-1183
