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

Thị trường chứng khoán Việt Nam trong những năm gần đây có sự phát triển mạnh về quy mô vốn hóa, số lượng doanh nghiệp niêm yết và mức độ tham gia của nhà đầu tư cá nhân cũng như tổ chức. Giá cổ phiếu chịu tác động đồng thời bởi nhiều yếu tố như kết quả kinh doanh của doanh nghiệp, diễn biến ngành, tình hình kinh tế vĩ mô, thanh khoản thị trường, tâm lý nhà đầu tư và thông tin từ truyền thông tài chính.

Trong các nghiên cứu và ứng dụng phân tích cổ phiếu, dữ liệu giao dịch như giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch thường được sử dụng để xây dựng các đặc trưng kỹ thuật. Các đặc trưng này phản ánh hành vi giá trong quá khứ và thuận tiện cho mô hình học máy. Tuy nhiên, bên cạnh dữ liệu giá và khối lượng, tin tức tài chính tiếng Việt cũng là nguồn thông tin quan trọng, phản ánh các sự kiện liên quan đến doanh nghiệp, ngành nghề và thị trường như lợi nhuận, doanh thu, cổ tức, phát hành cổ phiếu, nợ vay, dự án đầu tư, quản trị và rủi ro pháp lý.

Trong thực tiễn phân tích, việc chỉ biết xác suất tăng hoặc xếp hạng của một mã cổ phiếu thường chưa đủ. Người dùng còn cần hiểu vì sao mã đó được chọn, bằng chứng tin tức nào hỗ trợ hoặc làm suy yếu luận điểm, rủi ro nào cần theo dõi, và sau kỳ nắm giữ thì luận điểm ban đầu đúng hay sai vì lý do gì. Khoảng cách giữa tín hiệu mô hình và hồ sơ quyết định có thể giải thích, theo dõi, hậu kiểm là vấn đề trung tâm của đề tài.

Đề tài không đặt Large Language Model (LLM) ở vị trí mô hình dự báo giá độc lập. Định hướng nghiên cứu theo chuỗi:

```text
Tín hiệu học máy từ đặc trưng kỹ thuật
→ kiểm định vai trò tin tức như đặc trưng bổ sung
→ trích xuất bằng chứng tin tức ngữ nghĩa có cấu trúc
→ gói bằng chứng có truy vết
→ decision card có kiểm soát
→ dashboard theo dõi và hậu kiểm
```

Theo đó, tin tức được xem xét ở hai vai trò khác nhau. Vai trò thứ nhất là nhóm đặc trưng bổ sung cho mô hình học máy, cần được kiểm định một cách trung thực. Vai trò thứ hai là lớp bằng chứng phục vụ giải thích và hỗ trợ quyết định. Đề tài không giả định trước rằng việc đưa tin tức vào mô hình sẽ mặc định làm tăng hiệu quả dự báo. Nếu kết quả thực nghiệm cho thấy một số cách biểu diễn tin tức không tạo giá trị dự báo gia tăng ổn định, kết quả đó vẫn có ý nghĩa khoa học và là cơ sở để chuyển trọng tâm sang lớp bằng chứng cùng hệ hỗ trợ quyết định có truy vết.

## 1.2. Tổng quan nghiên cứu trong và ngoài nước

### 1.2.1. Nghiên cứu quốc tế

Trên thế giới, dự báo xu hướng giá cổ phiếu bằng Machine Learning là hướng nghiên cứu đã được quan tâm trong nhiều năm. Các nghiên cứu thường sử dụng dữ liệu giá, khối lượng giao dịch và các chỉ báo kỹ thuật như đường trung bình động, RSI, MACD, Bollinger Bands và độ biến động để xây dựng mô hình dự báo hoặc xếp hạng.

Bên cạnh dữ liệu thị trường, nhiều nghiên cứu quốc tế khai thác dữ liệu văn bản như tin tức tài chính, thông cáo báo chí, báo cáo doanh nghiệp hoặc dữ liệu mạng xã hội. Các hướng tiếp cận phổ biến bao gồm phân tích cảm xúc, biểu diễn từ khóa hoặc TF-IDF, word embedding, mô hình ngôn ngữ tiền huấn luyện và trích xuất sự kiện. Một số công trình theo hướng event-driven cho thấy tin tức có thể chứa thông tin hữu ích khi được biểu diễn ở mức sự kiện và ngữ cảnh, thay vì chỉ đếm từ đơn thuần.

Gần đây, các mô hình ngôn ngữ lớn được thử nghiệm trong phân tích tài chính, nhưng đồng thời cũng bộc lộ rủi ro ảo giác, thiếu trung thực với bằng chứng đầu vào và khó kiểm soát khi dùng trực tiếp cho dự báo giá. Vì vậy, xu hướng phù hợp hơn là dùng LLM cho các tác vụ có cấu trúc và có ràng buộc bằng chứng, rồi đặt kết quả trong một hệ hỗ trợ quyết định có kiểm soát, giám sát và hậu kiểm.

### 1.2.2. Nghiên cứu trong nước

Tại Việt Nam, các nghiên cứu về dự báo giá cổ phiếu bằng Machine Learning đã bắt đầu phát triển, trong đó nhiều nghiên cứu tập trung vào dữ liệu giá và khối lượng giao dịch. Một số nghiên cứu khác khai thác dữ liệu văn bản tiếng Việt, đặc biệt trong các bài toán phân tích cảm xúc tài chính hoặc đánh giá phản ứng thị trường trước tin tức.

Tuy nhiên, các nghiên cứu kết hợp đồng thời đặc trưng kỹ thuật, kiểm định giới hạn của biểu diễn từ khóa, xây dựng lớp bằng chứng ngữ nghĩa có truy vết và hiện thực hóa hệ hỗ trợ quyết định kèm dashboard vẫn còn hạn chế. Đặc biệt, ít công trình tách rõ hai lớp claim khác nhau: tin tức như biến dự báo và tin tức như bằng chứng phục vụ giải thích, theo dõi và hậu kiểm.

## 1.3. Khoảng trống nghiên cứu

Từ tổng quan trên, có thể xác định một số khoảng trống nghiên cứu như sau:

- Nhiều nghiên cứu và ứng dụng dừng ở dự báo tăng hoặc giảm, chưa tổ chức đủ vòng đời quyết định theo hướng chọn tín hiệu, giải thích bằng chứng, theo dõi và hậu kiểm.
- Đặc trưng tần suất từ khóa dễ tái lập nhưng thường thiếu độ liên quan theo mã cổ phiếu, mức độ trọng yếu, loại sự kiện, chiều tác động và đoạn bằng chứng nguyên văn.
- Việc kết luận tin tức “có ích” hoặc “vô ích” dễ bị lệch nếu không tách rõ vai trò tin tức như biến dự báo và vai trò tin tức như bằng chứng hỗ trợ quyết định.
- Các so sánh giữa keyword, sentiment và semantic dễ thiếu kỷ luật cùng mẫu quan sát, cùng mục tiêu và kiểm soát rò rỉ thời gian.
- Các dashboard phân tích cổ phiếu tại Việt Nam thường nghiêng về hiển thị thông tin, chưa gắn chặt với protocol đánh giá mức bám bằng chứng, kiểm soát nội dung phát sinh ngoài bằng chứng và truy vết nguồn.

---

# 2. Mục đích và ý nghĩa nghiên cứu

## 2.1. Tính cấp thiết

Trong bối cảnh lượng thông tin tài chính tiếng Việt ngày càng lớn, nhà đầu tư và nhà phân tích phải xử lý đồng thời tín hiệu kỹ thuật và thông tin sự kiện. Nếu chỉ tối ưu độ chính xác phân loại mà thiếu lớp bằng chứng và truy vết, kết quả mô hình khó sử dụng trong thực tiễn. Ngược lại, nếu chỉ tóm tắt tin tức bằng LLM mà thiếu tín hiệu định lượng và kiểm soát bằng chứng, hệ thống dễ rơi vào diễn giải không kiểm chứng.

Do đó, cần một nghiên cứu ứng dụng kết hợp ba việc: đánh giá tín hiệu học máy từ dữ liệu kỹ thuật; kiểm định trung thực các cách đưa tin tức vào phân tích, kể cả trường hợp không làm tăng hiệu quả dự báo; và hiện thực hóa phần ứng dụng dưới dạng hệ hỗ trợ quyết định có decision card cùng dashboard truy vết.

Đơn vị thời gian tổng hợp dữ liệu và cửa sổ đánh giá tín hiệu sẽ được xác định trong giai đoạn thực nghiệm dựa trên độ dày tin tức, đặc điểm biến động giá và yêu cầu kiểm soát rò rỉ thời gian. Đề tài không khóa cứng một kỳ duy nhất ngay từ đề cương, nhằm bảo đảm tính linh hoạt hợp lý trong quá trình triển khai.

## 2.2. Ý nghĩa lý luận

Đề tài có ý nghĩa lý luận ở các khía cạnh sau:

- Góp phần làm rõ sự khác nhau giữa tin tức như đặc trưng dự báo và tin tức như bằng chứng có cấu trúc trong bài toán phân tích cổ phiếu.
- Cung cấp bằng chứng thực nghiệm về giới hạn của biểu diễn tần suất từ khóa trong bối cảnh thị trường chứng khoán Việt Nam.
- Đề xuất khung đánh giá biểu diễn semantic material-event cho tin tức tài chính tiếng Việt, gắn với provenance và đoạn bằng chứng.
- Kết nối học máy có khả năng giải thích, kiểm soát tính trung thực của LLM và thiết kế hệ hỗ trợ quyết định có giám sát vòng đời.

## 2.3. Ý nghĩa thực tiễn

Đề tài có ý nghĩa thực tiễn ở các khía cạnh sau:

- Xây dựng bộ dữ liệu và pipeline nghiên cứu kết hợp dữ liệu giá cổ phiếu với tin tức tài chính tiếng Việt theo nguyên tắc point-in-time.
- Hỗ trợ đánh giá xem việc bổ sung tin tức theo từng cách biểu diễn có tạo giá trị dự báo gia tăng so với mô hình kỹ thuật hay không.
- Cung cấp evidence pack và decision card có kiểm soát để trình bày luận điểm, bằng chứng, rủi ro và điều kiện theo dõi.
- Xây dựng prototype dashboard phục vụ theo dõi tín hiệu, cập nhật bối cảnh và hậu kiểm sau kỳ nắm giữ.
- Tạo nền tảng cho các bước mở rộng về nhãn người, đánh giá chất lượng quyết định và quản trị mô hình về sau.

---

# 3. Mục tiêu nghiên cứu

## 3.1. Mục tiêu tổng quát

Mục tiêu tổng quát của đề tài là xây dựng và đánh giá một hệ thống hỗ trợ quyết định cổ phiếu theo hướng dẫn dắt bởi tín hiệu học máy, sử dụng tin tức tài chính tiếng Việt như lớp bằng chứng ngữ nghĩa có truy vết, kết hợp decision card có kiểm soát và dashboard theo dõi/hậu kiểm. Đề tài kiểm định trung thực vai trò của tin tức trong dự báo và trong hỗ trợ quyết định, không giả định trước rằng tin tức mặc định làm tăng hiệu quả dự báo.

## 3.2. Mục tiêu cụ thể

Đề tài hướng đến các mục tiêu cụ thể sau:

1. Xây dựng bộ dữ liệu thực nghiệm gồm dữ liệu giao dịch cổ phiếu và dữ liệu tin tức tài chính tiếng Việt, được căn chỉnh theo nguyên tắc point-in-time.
2. Xây dựng và đánh giá tín hiệu học máy dựa trên đặc trưng kỹ thuật để tạo xác suất, xếp hạng và danh sách ứng viên phân tích.
3. Xây dựng baseline đặc trưng tần suất từ khóa từ tin tức và kiểm định giá trị dự báo gia tăng của nhóm đặc trưng này so với mô hình kỹ thuật.
4. Xây dựng schema và quy trình trích xuất semantic material-event gồm độ liên quan, mức độ trọng yếu, loại sự kiện, chiều tác động, độ bất định, tính mới và đoạn bằng chứng.
5. So sánh các cấu hình đặc trưng kỹ thuật và tin tức theo hợp đồng thực nghiệm đã khóa trước khi chạy đánh giá chính; ghi nhận đầy đủ kết quả cải thiện, không cải thiện hoặc không ước lượng được.
6. Xây dựng evidence pack và decision card có kiểm soát từ tín hiệu học máy cùng bằng chứng tin tức, rồi so sánh với các baseline phù hợp.
7. Xây dựng prototype dashboard hỗ trợ theo dõi tín hiệu, bằng chứng, rủi ro, sự kiện cập nhật và hậu kiểm kết quả sau kỳ nắm giữ.
8. Xác định phạm vi diễn giải, giới hạn claim và điều kiện cần cho kiểm chứng bổ sung trước khi xem xét triển khai thực tế.

---

# 4. Câu hỏi nghiên cứu và giả thuyết nghiên cứu

## 4.1. Câu hỏi nghiên cứu

Đề tài tập trung trả lời các câu hỏi nghiên cứu sau:

1. **RQ0.** Tín hiệu học máy dựa trên đặc trưng kỹ thuật có tạo được lớp chọn ứng viên hữu ích cho hệ hỗ trợ quyết định trong phạm vi nghiên cứu hay không?
2. **RQ1.** Đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt có tạo giá trị dự báo gia tăng ổn định ngoài đặc trưng kỹ thuật hay không?
3. **RQ2.** Biểu diễn semantic material-event có phù hợp hơn baseline từ khóa hoặc rule cho việc cấu trúc hóa bằng chứng tin tức hay không?
4. **RQ3.** Khi so sánh các cấu hình kỹ thuật và tin tức trên cùng giao thức đánh giá đã khóa trước, vai trò của tin tức như biến dự báo thể hiện như thế nào?
5. **RQ4.** Evidence pack, decision card có kiểm soát và dashboard truy vết có cải thiện khả năng trình bày bằng chứng, rủi ro và lineage so với baseline chỉ dùng tín hiệu học máy hoặc mẫu rule hay không?

RQ3 mang tính kiểm định trung tính. Đề tài không đặt giả thuyết chiều dương bắt buộc rằng cấu hình có tin tức sẽ vượt cấu hình kỹ thuật. Nếu có phân tích liên hệ giữa đặc tính sự kiện và biến động giá sau sự kiện, phân tích này chỉ đóng vai trò khám phá hỗ trợ diễn giải, không phải giả thuyết chính và không được suy thành quan hệ nhân quả.

## 4.2. Giả thuyết nghiên cứu

Đề tài đề xuất các giả thuyết nghiên cứu sau:

- **H1:** Trong các thiết lập thực nghiệm của đề tài, đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt không tạo ra giá trị dự báo gia tăng ổn định so với mô hình chỉ dùng đặc trưng kỹ thuật.
- **H2:** Biểu diễn tin tức theo hướng sự kiện trọng yếu có ngữ nghĩa (relevance, materiality, event type, direction, evidence span) phù hợp hơn baseline từ khóa hoặc rule cho mục tiêu cấu trúc hóa bằng chứng phục vụ phân tích và hỗ trợ quyết định.
- **H3:** Hệ thống hỗ trợ quyết định gồm evidence pack, decision card có kiểm soát và dashboard truy vết giúp trình bày bằng chứng, rủi ro và lineage tốt hơn so với baseline chỉ dựa trên tín hiệu học máy hoặc mẫu rule.

Các giả thuyết trên mang tính kiểm định thực nghiệm. Đề tài không giả định trước rằng mọi cách đưa tin tức vào mô hình sẽ làm tăng hiệu quả dự báo. Trong trường hợp cấu hình có tin tức không vượt cấu hình kỹ thuật, kết quả này vẫn có ý nghĩa nghiên cứu vì giúp xác định giới hạn của từng lớp biểu diễn trước khi chuyển trọng tâm sang hỗ trợ quyết định có truy vết. H2 được đánh giá trên các tiêu chí biểu diễn và chất lượng bằng chứng, không đồng nhất với việc cải thiện chỉ số dự báo. H3 được đánh giá trên mức bám bằng chứng, kiểm soát nội dung phát sinh ngoài bằng chứng, khả năng nêu rủi ro và truy vết; không suy thành gia tăng lợi nhuận hoặc chất lượng quyết định của con người.

---

# 5. Đối tượng và phạm vi nghiên cứu

## 5.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu của đề tài bao gồm:

- Dữ liệu giao dịch của một nhóm cổ phiếu niêm yết trên Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE), bao gồm giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch.
- Dữ liệu tin tức tài chính tiếng Việt liên quan đến các cổ phiếu được chọn, thu thập từ các nguồn báo hoặc chuyên trang tài chính phù hợp.
- Tín hiệu học máy từ đặc trưng kỹ thuật và các cách biểu diễn tin tức phục vụ kiểm định dự báo hoặc tạo bằng chứng.
- Evidence pack, decision card và dashboard hỗ trợ theo dõi, cập nhật và hậu kiểm quyết định phân tích.

## 5.2. Phạm vi nghiên cứu

Đề tài được giới hạn trong phạm vi sau:

| Tiêu chí | Phạm vi |
|---|---|
| Thị trường | Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE) |
| Giai đoạn dữ liệu | Khoảng vài năm gần đây, bao gồm các giai đoạn thị trường đa dạng; phạm vi cụ thể được xác định dựa trên tính khả dụng và độ đầy đủ của dữ liệu thực tế |
| Đối tượng cổ phiếu | Nhóm cổ phiếu phổ thông được lựa chọn theo tiêu chí vốn hóa, thanh khoản, tính liên tục niêm yết và mức độ xuất hiện trên tin tức tài chính; tiêu chí cụ thể được xác định trong giai đoạn triển khai |
| Tần suất dữ liệu | Dữ liệu giá theo ngày, tổng hợp theo kỳ phân tích phù hợp |
| Tầm đánh giá tín hiệu | Cửa sổ ngắn đến trung hạn được chốt trước thực nghiệm chính; có thể điều chỉnh nếu phân tích dữ liệu thực tế cho thấy tín hiệu tin tức suy giảm nhanh hơn hoặc chậm hơn dự kiến |
| Loại bài toán tín hiệu | Phân loại hoặc xếp hạng ứng viên theo mục tiêu đã khai báo trước thực nghiệm chính |
| Dữ liệu văn bản | Tin tức tài chính tiếng Việt từ các nguồn báo có chuyên mục tài chính, chứng khoán hoặc doanh nghiệp |
| Vai trò học máy | Tạo xác suất, xếp hạng và giải thích kỹ thuật cho ứng viên phân tích |
| Vai trò tin tức | Kiểm định như đặc trưng bổ sung và khai thác như bằng chứng có cấu trúc |
| Vai trò LLM | Trích xuất cấu trúc và sinh decision card có ràng buộc bằng chứng; không dự báo giá độc lập |
| Sản phẩm ứng dụng | Prototype dashboard nghiên cứu phục vụ truy vết, theo dõi và hậu kiểm |
| Hình thức quyết định | Hỗ trợ phân tích; người dùng là người ra quyết định cuối |

Danh sách cổ phiếu cụ thể sẽ được xác định trong giai đoạn triển khai thực nghiệm dựa trên tính đầy đủ của dữ liệu giao dịch, mức độ phủ tin tức và các tiêu chí kỹ thuật khác.

## 5.3. Giới hạn của đề tài

Đề tài có các giới hạn sau:

- Không dự báo mức giá cụ thể của cổ phiếu và không xây dựng hệ thống giao dịch tự động.
- Không đưa ra khuyến nghị đầu tư thực tế và không cam kết lợi nhuận hoặc alpha ổn định.
- Không kết luận quan hệ nhân quả từ các phân tích liên hệ sự kiện và biến động giá.
- Không xây dựng mô hình ngôn ngữ mới từ đầu.
- Không sử dụng dữ liệu giao dịch trong ngày làm trọng tâm.
- Không xem xét các biến vĩ mô như lãi suất, tỷ giá, GDP hoặc lạm phát như biến đầu vào độc lập bắt buộc.
- Nhãn semantic sinh từ mô hình hoặc hợp nhất đa mô hình được xem là pseudo-label, không phải nhãn chuẩn của chuyên gia.
- Rubric tự động cho decision card đo chất lượng trình bày và mức bám bằng chứng, không đo chất lượng quyết định của con người.
- Dashboard là prototype nghiên cứu, chưa phải hệ thống vận hành có phân quyền và hạ tầng production đầy đủ.
- Đề tài có thể chịu ảnh hưởng nhẹ từ survivorship bias do ưu tiên cổ phiếu có dữ liệu liên tục; hạn chế này sẽ được ghi nhận khi phân tích kết quả.
- Đề tài không giả định rằng mọi cách đưa tin tức vào mô hình sẽ làm tăng hiệu quả dự báo.

---

# 6. Phương pháp nghiên cứu

## 6.1. Thiết kế tổng quát

Quy trình nghiên cứu được thiết kế theo các bước chính sau:

1. Lựa chọn nhóm cổ phiếu nghiên cứu theo tiêu chí đã xác định.
2. Thu thập dữ liệu giá và khối lượng giao dịch theo ngày.
3. Thu thập tin tức tài chính tiếng Việt từ các nguồn được lựa chọn.
4. Gắn bài viết với cổ phiếu tương ứng dựa trên mã cổ phiếu, tên doanh nghiệp và các quy tắc lọc phù hợp.
5. Căn chỉnh dữ liệu theo nguyên tắc point-in-time và xây dựng biến mục tiêu.
6. Trích xuất đặc trưng kỹ thuật từ dữ liệu giao dịch.
7. Trích xuất đặc trưng tần suất từ khóa từ dữ liệu tin tức.
8. Trích xuất semantic material-event có provenance và đoạn bằng chứng.
9. Huấn luyện, đánh giá tín hiệu học máy và so sánh các cấu hình đặc trưng theo hợp đồng đã khóa trước.
10. Xây dựng evidence pack, decision card có kiểm soát và đánh giá theo rubric.
11. Hiện thực prototype dashboard phục vụ theo dõi, truy vết và hậu kiểm.
12. Tổng hợp kết quả, giới hạn claim và điều kiện phát triển tiếp theo.

## 6.2. Lựa chọn cổ phiếu nghiên cứu

Nhóm cổ phiếu nghiên cứu được lựa chọn từ các cổ phiếu phổ thông niêm yết trên HOSE theo các nguyên tắc sau:

- **Vốn hóa và thanh khoản:** Ưu tiên các cổ phiếu có vốn hóa lớn và thanh khoản ổn định, nhằm bảo đảm dữ liệu giao dịch đầy đủ và các đặc trưng kỹ thuật có ý nghĩa.
- **Tính liên tục dữ liệu:** Cổ phiếu cần có dữ liệu giao dịch đủ liên tục trong giai đoạn nghiên cứu và không thuộc diện cảnh báo hoặc kiểm soát kéo dài nếu điều đó làm mất tính khả dụng của chuỗi giá.
- **Mức độ phủ tin tức:** Cổ phiếu cần có lượng tin tức tài chính đủ lớn để việc xây đặc trưng từ khóa và bằng chứng ngữ nghĩa có ý nghĩa phân tích. Ngưỡng cụ thể sẽ được xác định sau khi thu thập dữ liệu thực tế.
- **Loại cổ phiếu:** Chỉ bao gồm cổ phiếu phổ thông; loại trừ chứng quyền có bảo đảm, chứng chỉ quỹ ETF và các công cụ phái sinh nếu không phục vụ trực tiếp câu hỏi nghiên cứu.

Danh sách cổ phiếu cuối cùng sẽ được xác định trong giai đoạn triển khai thực nghiệm sau khi kiểm tra tính đầy đủ của dữ liệu.

## 6.3. Xác định biến mục tiêu và nguyên tắc thời gian

Đề tài đánh giá tín hiệu theo một cửa sổ ngắn đến trung hạn được chốt trước thực nghiệm chính. Biến mục tiêu có thể là nhãn phân loại hoặc tiêu chí xếp hạng phù hợp với mục tiêu hỗ trợ chọn ứng viên phân tích. Định nghĩa cụ thể của nhãn, cách xử lý các quan sát biên và tiêu chí loại bản ghi thiếu dữ liệu sẽ được khóa trước khi chạy đánh giá chính.

Các nguyên tắc thời gian được áp dụng thống nhất:

- Chỉ sử dụng dữ liệu giá và tin tức đã khả dụng tại thời điểm quyết định.
- Không dùng thông tin phát sinh sau thời điểm quyết định để tạo đặc trưng hoặc viết decision card ban đầu.
- Phần theo dõi chỉ ghi nhận sự kiện xuất hiện sau thời điểm quyết định.
- Phần hậu kiểm chỉ mở sau khi kết thúc cửa sổ đánh giá tương ứng.

Đơn vị tổng hợp tin tức và cửa sổ đánh giá có thể được điều chỉnh trong quá trình thực nghiệm nếu phân tích dữ liệu cho thấy tín hiệu suy giảm nhanh hơn hoặc chậm hơn so với giả định ban đầu. Mọi điều chỉnh liên quan đến đánh giá chính phải được ghi nhận trước khi chạy lại theo hợp đồng mới.

## 6.4. Thu thập và xử lý dữ liệu giao dịch

Dữ liệu giao dịch theo ngày bao gồm: giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch. Dữ liệu được thu thập thông qua các thư viện và API công khai phù hợp với thị trường Việt Nam, ví dụ vnstock hoặc các nguồn tương đương.

Từ dữ liệu này, đề tài sẽ tính toán các đặc trưng kỹ thuật phục vụ tín hiệu học máy. Các nhóm đặc trưng dự kiến bao gồm:

| Nhóm đặc trưng | Đặc trưng cụ thể |
|---|---|
| Lợi suất | Lợi suất gần nhất, lợi suất tích lũy trên các cửa sổ phù hợp |
| Biến động | Độ lệch chuẩn lợi suất, biên độ dao động giá |
| Thanh khoản | Khối lượng giao dịch trung bình, thay đổi khối lượng |
| Xu hướng | SMA, EMA, khoảng cách giá so với đường trung bình |
| Chỉ báo kỹ thuật | RSI, MACD, Bollinger Bands |
| Động lượng | Tỷ suất sinh lợi trong các khoảng thời gian gần nhất |

Danh sách đặc trưng cụ thể có thể được điều chỉnh trong giai đoạn thực nghiệm.

## 6.5. Thu thập và xử lý dữ liệu tin tức

Dữ liệu tin tức tài chính tiếng Việt sẽ được thu thập từ các nguồn báo có chuyên mục tài chính, chứng khoán hoặc doanh nghiệp, có tần suất xuất bản ổn định và lịch sử bài viết đủ sâu để bao phủ giai đoạn nghiên cứu. Nguồn dữ liệu cụ thể sẽ được xác định và kiểm tra tính khả dụng trong giai đoạn triển khai.

Thông tin thu thập từ mỗi bài viết dự kiến bao gồm: tiêu đề, nội dung hoặc mô tả ngắn, thời điểm đăng bài, nguồn và mã cổ phiếu liên quan.

Các bước tiền xử lý văn bản bao gồm:

1. Làm sạch và chuẩn hóa văn bản.
2. Tách từ tiếng Việt bằng công cụ xử lý ngôn ngữ tự nhiên phù hợp khi cần cho baseline từ khóa.
3. Loại bỏ bài viết trùng lặp và các trường hợp gắn mã không đủ tin cậy.
4. Gắn bài viết với mã cổ phiếu tương ứng dựa trên tên doanh nghiệp và các quy tắc nhận diện phù hợp.
5. Căn chỉnh thời điểm khả dụng của tin theo nguyên tắc point-in-time trước khi đưa vào đặc trưng hoặc evidence pack.

## 6.6. Đặc trưng tần suất từ khóa từ tin tức tài chính

Đặc trưng từ khóa trong đề tài phản ánh sự xuất hiện và tần suất lặp lại của các từ khóa hoặc cụm từ khóa tài chính trong tin tức. Lớp này đóng vai trò baseline dễ tái lập để kiểm định H1, không phải hướng biểu diễn cuối cùng của đề tài.

Danh sách từ khóa ban đầu được xây dựng dựa trên kiến thức tài chính và kết hợp phân tích thống kê từ corpus tin tức thực tế. Các nhóm từ khóa dự kiến bao gồm chủ đề về kết quả kinh doanh, chính sách cổ đông, tài chính doanh nghiệp, hoạt động kinh doanh, rủi ro và thị trường ngành.

Các nhóm đặc trưng từ khóa dự kiến bao gồm:

| Nhóm đặc trưng | Mô tả |
|---|---|
| Tần suất từ khóa | Số lần xuất hiện của từng từ khóa hoặc cụm từ khóa trong tin liên quan đến một cổ phiếu trong cửa sổ được xét |
| Tần suất chuẩn hóa | Tần suất từ khóa chia cho tổng số bài viết hoặc tổng số từ trong cửa sổ tương ứng |
| TF-IDF hoặc biến trọng số tương đương | Mức độ đặc trưng của từ khóa theo cổ phiếu và cửa sổ phân tích |
| Mức độ phủ tin tức | Số lượng bài viết liên quan đến cổ phiếu trong cửa sổ được xét |

Nếu đặc trưng từ khóa không tạo giá trị dự báo gia tăng ổn định, đề tài vẫn giữ kết quả này như một kết luận thực nghiệm hợp lệ và dùng nó làm tiền đề cho lớp semantic material-event cùng hệ hỗ trợ quyết định.

## 6.7. Semantic material-event extraction

Đơn vị đầu vào của lớp semantic là bài báo hoặc đơn vị tin đã gắn mã. Đầu ra cấu trúc tập trung vào các trường:

| Trường | Vai trò |
|---|---|
| Ticker relevance | Mức độ liên quan trực tiếp hoặc gián tiếp tới mã cổ phiếu |
| Materiality | Mức độ trọng yếu của thông tin |
| Event type | Loại sự kiện như kết quả kinh doanh, vốn, nợ, quản trị, pháp lý và các nhóm liên quan |
| Direction | Chiều hỗ trợ, rủi ro hoặc trung tính đối với luận điểm phân tích |
| Uncertainty / novelty | Mức bất định và tính mới của thông tin |
| Evidence span | Đoạn bằng chứng nguyên văn hỗ trợ nhãn |
| Provenance | Nguồn, thời điểm và mã định danh liên quan |

Lớp này phục vụ H2 và cung cấp đầu vào cho evidence pack. Nhãn được xử lý như pseudo-label. Đề tài đánh giá độ ổn định giữa các lần gán nhãn, mức đầy đủ provenance, tính hợp lệ của evidence span và mức phù hợp hơn so với baseline rule hoặc keyword trên các chiều biểu diễn. Một mẫu kiểm tra chất lượng bởi người có thể được dùng như cầu nối kiểm soát, nhưng không được đồng nhất với bộ nhãn chuẩn đầy đủ.

## 6.8. Xây dựng mô hình học máy và so sánh cấu hình

Đề tài xây dựng các mô hình phân loại hoặc xếp hạng dựa trên tín hiệu kỹ thuật và các cấu hình có tin tức. Các thuật toán dự kiến bao gồm Logistic Regression, Random Forest, XGBoost hoặc LightGBM. Lựa chọn mô hình và cấu hình thực nghiệm cuối cùng có thể điều chỉnh dựa trên đặc điểm dữ liệu thực tế, nhưng phải được khóa trước đánh giá chính.

Các cấu hình đặc trưng dự kiến để phục vụ so sánh:

| Cấu hình | Đặc trưng sử dụng |
|---|---|
| Technical-only | Chỉ sử dụng đặc trưng kỹ thuật |
| Technical + Keyword | Kết hợp đặc trưng kỹ thuật và đặc trưng tần suất từ khóa |
| Technical + Semantic | Kết hợp đặc trưng kỹ thuật và đặc trưng semantic material-event |

Ngoài ra, đề tài có thể sử dụng các baseline đơn giản để tham chiếu, ví dụ majority class baseline hoặc naive momentum baseline. Việc so sánh nhằm trả lời RQ0, RQ1 và RQ3. Đề tài không đặt giả thuyết bắt buộc rằng cấu hình có tin tức sẽ vượt cấu hình kỹ thuật.

## 6.9. Đánh giá tín hiệu và kiểm định thống kê

Do dữ liệu có tính thời gian và cấu trúc dạng panel, việc chia tập huấn luyện và kiểm định áp dụng nguyên tắc thời gian: các quan sát dùng để huấn luyện phải nằm trước phần kiểm định theo cách không làm rò rỉ thông tin tương lai. Cách chia cụ thể, số fold và quy tắc loại bản ghi không hợp lệ sẽ được xác định dựa trên quy mô dữ liệu thực tế và khóa trước đánh giá chính.

Các chỉ số đánh giá dự kiến gồm Balanced Accuracy, AUC-ROC, Precision, Recall, F1-score và các chỉ số xếp hạng phù hợp. Khi mất cân bằng nhãn xảy ra, đề tài sẽ xem xét điều chỉnh trọng số lớp hoặc ngưỡng phân loại trong phạm vi hợp đồng đã khai báo.

Đối với các so sánh chính, đề tài ưu tiên so sánh theo cặp ngoài mẫu trên cùng tập quan sát hợp lệ, kèm khoảng tin cậy dạng bootstrap hoặc tương đương, kiểm định hoán vị hoặc dấu khi phù hợp, và hiệu chỉnh đa kiểm định theo họ giả thuyết đã khai báo. Kết quả không vượt ngưỡng hoặc không ước lượng được vẫn được báo cáo đầy đủ.

Bên cạnh đó, đề tài sử dụng các phương pháp giải thích mô hình như hệ số hồi quy, feature importance, permutation importance hoặc SHAP để hỗ trợ diễn giải tín hiệu kỹ thuật. Các phương pháp này là công cụ phân tích, không phải giả thuyết nghiên cứu độc lập.

## 6.10. Evidence pack, decision card và đánh giá hỗ trợ quyết định

Evidence pack tổng hợp xác suất hoặc xếp hạng học máy, giải thích kỹ thuật, bằng chứng tin tức, mã nguồn bằng chứng và các cảnh báo thiếu thông tin. Decision card được sinh theo mẫu có kiểm soát với các thành phần dự kiến: luận điểm, bằng chứng hỗ trợ, rủi ro, khoảng trống thông tin, điều kiện theo dõi và giới hạn diễn giải.

Ba nhóm đối chứng dự kiến:

1. Mẫu rule-based.
2. Card chỉ dựa trên tín hiệu học máy hoặc đặc trưng kỹ thuật.
3. Card dùng đầy đủ evidence pack.

Rubric đánh giá tập trung vào mức bám bằng chứng, kiểm soát nội dung phát sinh ngoài bằng chứng, khả năng nêu rủi ro, chất lượng gợi ý theo dõi và tính rõ ràng. Nếu điều kiện cho phép, đề tài tách mô hình sinh và mô hình chấm điểm, đồng thời bổ sung đánh giá người trên mẫu nhỏ. Rubric không được dùng để suy ra lợi nhuận hoặc chất lượng quyết định đầu tư của con người.

## 6.11. Dashboard truy vết, theo dõi và hậu kiểm

Prototype dashboard là thành phần ứng dụng của đề tài, phục vụ trực tiếp H3 và mục tiêu hỗ trợ quyết định. Các vùng chức năng dự kiến bao gồm:

1. Tổng quan tín hiệu và trạng thái ứng viên.
2. Giải thích kỹ thuật.
3. Bằng chứng tin tức ngữ nghĩa.
4. Decision card.
5. Timeline theo dõi sau thời điểm quyết định.
6. Hậu kiểm kết quả sau kỳ đánh giá.
7. Panel provenance gồm mã nguồn, phiên bản schema và dấu vết dữ liệu liên quan.

Dashboard được đánh giá theo tính đầy đủ, khả năng truy vết và an toàn thời gian trên một số tình huống điển hình. Đề tài không dùng chất lượng giao diện để thay cho bằng chứng nghiên cứu và không định vị dashboard như hệ thống giao dịch tự động.

## 6.12. Kiểm soát rò rỉ dữ liệu và kỷ luật claim

Để tránh rò rỉ dữ liệu và diễn giải vượt bằng chứng, đề tài áp dụng các nguyên tắc sau:

- Chỉ sử dụng dữ liệu tin tức và dữ liệu giá đã có tại thời điểm quyết định.
- Không sử dụng kết quả sau cửa sổ đánh giá trong evidence pack hoặc decision card ban đầu.
- Các bước chuẩn hóa, chọn đặc trưng và huấn luyện mô hình phải được thực hiện trong phạm vi dữ liệu được phép tại từng phần huấn luyện trước khi áp dụng lên phần kiểm định.
- Tách rõ vùng quyết định ban đầu, vùng theo dõi và vùng hậu kiểm.
- Pseudo-label, phân tích liên hệ sự kiện--biến động giá và mô phỏng xếp hạng được diễn giải đúng lớp claim tương ứng.
- Mọi kết luận chính phải gắn được với protocol, chỉ số và điều kiện hợp lệ đã khai báo trước.

---

# 7. Công cụ và thư viện dự kiến

| Nhóm | Công cụ / Thư viện | Mục đích |
|---|---|---|
| Ngôn ngữ lập trình | Python | Ngôn ngữ lập trình chính |
| Xử lý dữ liệu | Pandas, NumPy | Xử lý, căn chỉnh và tổng hợp dữ liệu |
| Dữ liệu thị trường | vnstock hoặc nguồn dữ liệu tương đương | Thu thập dữ liệu giá cổ phiếu |
| Thu thập tin tức | BeautifulSoup, Scrapy hoặc công cụ tương đương | Thu thập dữ liệu bài viết |
| Xử lý tiếng Việt | underthesea, VnCoreNLP hoặc công cụ phù hợp | Tách từ, chuẩn hóa văn bản |
| Đặc trưng văn bản | scikit-learn hoặc công cụ tương đương | Trích xuất đặc trưng từ khóa |
| Machine Learning | scikit-learn, XGBoost, LightGBM | Xây dựng và đánh giá tín hiệu |
| Giải thích mô hình | SHAP, permutation importance | Phân tích vai trò của đặc trưng kỹ thuật |
| LLM / API | Nhà cung cấp mô hình phù hợp qua API | Trích xuất semantic và sinh decision card |
| Đánh giá thống kê | SciPy hoặc công cụ tương đương | So sánh ngoài mẫu và kiểm soát đa kiểm định |
| Dashboard | Streamlit, Dash, FastAPI hoặc stack tương đương | Prototype truy vết và theo dõi |
| Trực quan hóa | Matplotlib, Seaborn, Plotly | Trực quan hóa kết quả |

Danh sách công cụ có thể được điều chỉnh trong quá trình triển khai tùy theo đặc điểm dữ liệu thực tế.

---

# 8. Kết quả dự kiến

Đề tài dự kiến đạt được các kết quả sau:

1. Bộ dữ liệu thực nghiệm kết hợp dữ liệu giao dịch cổ phiếu và dữ liệu tin tức tài chính tiếng Việt, được căn chỉnh theo nguyên tắc point-in-time.
2. Kết quả đánh giá tín hiệu học máy từ đặc trưng kỹ thuật trong vai trò lớp chọn ứng viên cho hệ hỗ trợ quyết định.
3. Kết luận kiểm định về giá trị dự báo gia tăng của đặc trưng tần suất từ khóa so với mô hình kỹ thuật.
4. Schema semantic material-event kèm quy trình gán nhãn, kiểm tra chất lượng biểu diễn và provenance.
5. Kết quả so sánh các cấu hình kỹ thuật và tin tức theo hợp đồng đánh giá đã khóa trước, bao gồm cả trường hợp không cải thiện hoặc không ước lượng được.
6. Tập evidence pack, decision card và kết quả đánh giá rubric so với các baseline phù hợp.
7. Prototype dashboard hỗ trợ theo dõi, truy vết và hậu kiểm trên các tình huống điển hình.
8. Ma trận claim--evidence--limitation làm cơ sở diễn giải kết quả luận văn một cách trung thực.

---

# 9. Đóng góp dự kiến của đề tài

Đề tài dự kiến có các đóng góp chính sau:

- Cung cấp bằng chứng thực nghiệm có kiểm soát về giới hạn của biểu diễn tần suất từ khóa trong bài toán phân tích cổ phiếu Việt Nam.
- Đề xuất và đánh giá schema bằng chứng tin tức theo hướng sự kiện trọng yếu có ngữ nghĩa, thay vì dừng ở cảm xúc hoặc đếm từ.
- Thiết kế giao thức so sánh các cách dùng tin tức theo hướng trung thực với dữ liệu, chấp nhận kết quả không cải thiện dự báo như kết quả khoa học hợp lệ.
- Hiện thực hóa kiến trúc hỗ trợ quyết định dẫn dắt bởi học máy, dùng LLM có ràng buộc bằng chứng và dashboard truy vết vòng đời quyết định.
- Tách rõ các lớp claim giữa dự báo, chất lượng biểu diễn, chất lượng card và khả năng truy vết, giảm rủi ro diễn giải vượt bằng chứng.

---

# 10. Thời gian thực hiện dự kiến

| Giai đoạn | Nội dung công việc | Thời gian dự kiến |
|---|---|---|
| 1 | Nghiên cứu tổng quan, hoàn thiện đề cương, xác định phạm vi cổ phiếu và nguồn dữ liệu | Tháng 1 |
| 2 | Thu thập dữ liệu giá cổ phiếu và dữ liệu tin tức tài chính tiếng Việt | Tháng 1--2 |
| 3 | Tiền xử lý dữ liệu, căn chỉnh point-in-time, xây đặc trưng kỹ thuật và baseline từ khóa | Tháng 2--3 |
| 4 | Kiểm định H1 và đánh giá tín hiệu kỹ thuật | Tháng 3--4 |
| 5 | Xây semantic schema, gán nhãn, kiểm tra chất lượng biểu diễn và so sánh cấu hình đặc trưng | Tháng 4--5 |
| 6 | Xây evidence pack, decision card, rubric và prototype dashboard | Tháng 5--6 |
| 7 | Tổng hợp kết quả, viết luận văn và hoàn thiện hồ sơ | Tháng 6--7 |
| 8 | Rà soát, chỉnh sửa và chuẩn bị bảo vệ | Tháng 7--8 |

Các mốc thời gian mang tính kế hoạch và có thể điều chỉnh theo tiến độ dữ liệu, phản hồi của giảng viên hướng dẫn và lịch học vụ.

---

# 11. Nơi thực hiện đề tài

Trường Đại học Khoa học Tự nhiên - Đại học Quốc gia Thành phố Hồ Chí Minh.

---

# 12. Tài liệu tham khảo dự kiến

1. Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. arXiv preprint.
2. Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. *Journal of Computational Science*, 2(1), 1--8.
3. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785--794.
4. Ding, X., Zhang, Y., Liu, T., & Duan, J. (2015). Deep learning for event-driven stock prediction. *Proceedings of the 24th International Joint Conference on Artificial Intelligence*, 2327--2333.
5. Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys*, 55(12), 1--38.
6. Li, X., Xie, H., Chen, L., Wang, J., & Deng, X. (2014). News impact on stock price return via sentiment analysis. *Knowledge-Based Systems*, 69, 14--23.
7. Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. Working paper.
8. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30, 4765--4774.
9. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. New York Institute of Finance.
10. Nassirtoussi, A. K., Aghabozorgi, S., Wah, T. Y., & Ngo, D. C. L. (2014). Text mining for market prediction: A systematic review. *Expert Systems with Applications*, 41(16), 7653--7670.
11. Nguyen, D. Q., & Nguyen, A. T. (2020). PhoBERT: Pre-trained language models for Vietnamese. *Findings of the Association for Computational Linguistics: EMNLP 2020*, 1037--1042.
12. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825--2830.
13. Schumaker, R. P., & Chen, H. (2009). Textual analysis of stock market prediction using breaking financial news. *ACM Transactions on Information Systems*, 27(2), 1--19.
14. Vu, L., Pham, T., Kieu, D., & Pham, H. (2023). Sentiments extracted from news and stock market reactions in Vietnam. *International Journal of Financial Studies*, 11(3), 101.
15. Xu, Y., & Cohen, S. B. (2018). Stock movement prediction from tweets and historical prices. *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics*, 1970--1979.
