---
geometry: "top=3.5cm, bottom=3cm, left=3.5cm, right=2cm"
documentclass: extarticle
fontsize: 12pt
mainfont: "Times New Roman"
lang: vi-VN
header-includes:
  - \usepackage{titlesec}
  - \usepackage{longtable}
  - \usepackage{array}
  - \usepackage{booktabs}
  - \usepackage{caption}
  - \usepackage{ragged2e}
  - \usepackage{setspace}
  - \usepackage{etoolbox}
  - \usepackage{graphicx}
  - \setstretch{1.5}
  - \AtBeginDocument{\fontsize{13}{19.5}\selectfont}
  - \setlength{\parindent}{1cm}
  - \setlength{\parskip}{0.25em}
  - \AtBeginEnvironment{longtable}{\small}
  - \titleformat{\section}{\normalfont\Large\bfseries}{\thesection.}{0.5em}{}
  - \titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection.}{0.5em}{}
  - \titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{\thesubsubsection.}{0.5em}{}
---

\begin{titlepage}
\begin{center}

{\large ĐẠI HỌC QUỐC GIA TP. HCM}\\
{\large \textbf{TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN}}

\vspace{0.8cm}

{\large \textbf{NGÔ MINH TRÍ}}

\vspace{1.2cm}

{\fontsize{16}{20}\selectfont\textbf{HỆ THỐNG HỖ TRỢ QUYẾT ĐỊNH CỔ PHIẾU\\DỰA TRÊN TÍN HIỆU HỌC MÁY VÀ BẰNG CHỨNG\\TIN TỨC NGỮ NGHĨA CÓ TRUY VẾT}}

\vspace{0.9cm}

{\large \textbf{\underline{ĐỀ CƯƠNG ĐỒ ÁN TỐT NGHIỆP THẠC SĨ}}}\\
\textit{\underline{CẦN XÁC NHẬN: tên gọi bìa đề cương với GVHD/Phòng Đào tạo Sau đại học.}}

\end{center}

\vspace{0.5cm}

\noindent Ngành: Khoa học Dữ liệu\\
\noindent Mã số ngành: 8460108\\
\noindent Học viên cao học: Ngô Minh Trí\\
\noindent Mã số học viên: 24C01024

\vspace{0.8cm}

\begin{center}
\textbf{NGƯỜI HƯỚNG DẪN KHOA HỌC}\\
HDC: \underline{........................................................}

\vspace{1.2cm}
TP. Hồ Chí Minh -- Năm 2026
\end{center}
\end{titlepage}

\begin{center}
{\large \textbf{NỘI DUNG CHÍNH CỦA NGHIÊN CỨU}}
\end{center}

\vspace{0.5cm}

# 1. Giới thiệu tổng quan

## 1.1. Bối cảnh nghiên cứu

Thị trường chứng khoán Việt Nam tạo ra lượng lớn dữ liệu giao dịch và tin tức công khai. Dữ liệu giá và khối lượng cho phép xây dựng đặc trưng kỹ thuật phục vụ học máy [9]. Tin tức tiếng Việt phản ánh nhiều sự kiện doanh nghiệp như kết quả kinh doanh, cổ tức, phát hành, nợ vay, dự án, quản trị và rủi ro pháp lý. Hai nguồn thông tin này có thể bổ sung cho nhau, nhưng thường được khai thác riêng rẽ hoặc được kết hợp mà chưa kiểm soát đầy đủ thời điểm dữ liệu thực sự khả dụng [10].

Trong thực tiễn phân tích, xác suất tăng hoặc thứ hạng cổ phiếu chưa đủ để tạo thành hồ sơ quyết định có thể kiểm chứng. Người dùng còn cần biết tín hiệu được tạo từ dữ liệu nào, bằng chứng tin tức nào củng cố hoặc làm suy yếu luận điểm, rủi ro nào cần theo dõi, và sau thời hạn đánh giá thì luận điểm ban đầu phù hợp hay không. Vì vậy, thu hẹp khoảng cách giữa tín hiệu mô hình và một quy trình hỗ trợ quyết định có khả năng giải thích, truy vết, theo dõi và hậu kiểm là vấn đề trung tâm của đồ án.

Đồ án hướng đến xây dựng một **nguyên mẫu hệ thống hỗ trợ quyết định dựa trên bằng chứng** (*evidence-grounded decision support prototype*). Tín hiệu định lượng từ dữ liệu thị trường và bằng chứng từ tin tức công khai là hai nguồn thông tin bổ trợ. Mô hình kỹ thuật tạo xác suất và xếp hạng ban đầu cho toàn bộ cổ phiếu có dữ liệu giao dịch đủ điều kiện. Tin tức chỉ làm giàu phân tích cho các cổ phiếu ưu tiên khi có bài báo đã liên kết và khả dụng đúng thời điểm; việc không quan sát được tin không loại cổ phiếu khỏi xếp hạng.

Mô hình ngôn ngữ lớn (Large Language Model - LLM) **không được dùng như mô hình dự báo giá độc lập**. LLM chủ yếu hỗ trợ trích xuất, cấu trúc hóa và tổng hợp tin tức dựa trên bằng chứng đầu vào [5], [7]. Nhánh tín hiệu kỹ thuật và nhánh bằng chứng tin tức gặp nhau tại lớp hỗ trợ quyết định, nhưng chỉ lớp tín hiệu kỹ thuật quyết định thứ hạng ban đầu như Hình 1.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.84\textwidth]{assets/khung_nghien_cuu_tong_quat.png}
\caption{Khung nghiên cứu tổng quát: các đầu vào point-in-time được căn chỉnh tại từng thời điểm; Technical + Coverage là lớp đặc trưng dùng chung. Các cấu hình được so sánh ngoài mẫu theo cặp trên cùng protocol; tin tức đã liên kết được nối với bằng chứng ngữ nghĩa và EvidenceTrace. Ba vùng thời gian (quyết định ban đầu, theo dõi, hậu kiểm) kiểm soát rò rỉ và ngăn kết quả tác động ngược trở lại quyết định ban đầu..}
\label{fig:research-framework}
\end{figure}

Tin tức được xem xét với hai vai trò. Thứ nhất, tin tức là nguồn đặc trưng bổ sung cần được kiểm định riêng trên tập con có tin tức liên kết khả dụng theo quy tắc point-in-time. Thứ hai, tin tức là nguồn bằng chứng phục vụ giải thích và hỗ trợ phân tích cho các ứng viên được tín hiệu kỹ thuật ưu tiên. Cách thiết kế này cho phép đánh giá riêng ba vấn đề: chất lượng tín hiệu dự báo trên toàn bộ tập dữ liệu giao dịch đủ điều kiện, giá trị thông tin có điều kiện của nội dung tin tức và khả năng dùng hai nguồn thông tin để hỗ trợ quyết định có căn cứ, có thể truy vết. Tác động của việc bổ sung tin tức được xác định từ kết quả thực nghiệm, không giả định trước theo hướng cải thiện.

## 1.2. Tổng quan nghiên cứu trong và ngoài nước

### 1.2.1. Nghiên cứu quốc tế

Dự báo xu hướng giá cổ phiếu bằng học máy dựa trên dữ liệu giá, khối lượng và chỉ báo kỹ thuật là hướng nghiên cứu đã phát triển lâu [9]. Bên cạnh đó, tin tức và bài báo công khai được khai thác bằng nhiều phương pháp biểu diễn, từ từ khóa, TF-IDF và phân tích cảm xúc đến mô hình ngôn ngữ tiền huấn luyện và trích xuất sự kiện [1], [2], [4], [6], [10]. Các nghiên cứu theo hướng sự kiện cho thấy loại sự kiện và ngữ cảnh có thể chứa nhiều thông tin hơn so với việc chỉ đếm tần suất từ khóa [4].

Gần đây, LLM được thử nghiệm trong phân tích tài chính [7]. Tuy nhiên, việc dùng trực tiếp LLM để dự báo hoặc tạo khuyến nghị làm phát sinh rủi ro về nội dung thiếu căn cứ và khó kiểm soát [5]. Một hướng phù hợp hơn đối với hệ thống hỗ trợ quyết định là dùng LLM cho tác vụ có cấu trúc, ràng buộc đầu ra bằng bằng chứng, duy trì truy vết nguồn và tách rõ dữ liệu tại thời điểm quyết định với dữ liệu dùng cho theo dõi, hậu kiểm.

### 1.2.2. Nghiên cứu trong nước

Tại Việt Nam, nhiều nghiên cứu học máy tập trung vào dữ liệu giá và khối lượng. Một số công trình đã khai thác tin tức hoặc cảm xúc văn bản tiếng Việt, đồng thời xuất hiện các mô hình ngôn ngữ tiền huấn luyện cho tiếng Việt [11]. Tuy vậy, vẫn còn hạn chế ở ba điểm: biểu diễn tin tức thường dừng ở từ khóa hoặc điểm cảm xúc tổng hợp; so sánh giữa các cách biểu diễn không phải lúc nào cũng bảo đảm cùng mẫu quan sát, cùng biến mục tiêu và cùng nguyên tắc thời gian; phần giải thích kết quả mô hình cũng chưa thường xuyên gắn với bằng chứng nguyên văn và thông tin truy vết nguồn.

## 1.3. Khoảng trống nghiên cứu

- Nhiều nghiên cứu dừng ở dự báo tăng/giảm hoặc xếp hạng, chưa tổ chức đủ quy trình hỗ trợ quyết định gồm tín hiệu, bằng chứng, rủi ro, theo dõi và hậu kiểm.
- Biểu diễn tần suất từ khóa dễ tái lập nhưng chưa thể hiện đầy đủ mức liên quan theo mã, tính trọng yếu, loại sự kiện, chiều tác động và đoạn bằng chứng nguyên văn [4], [10].
- Việc kết luận tin tức “có ích” hoặc “không có ích” dễ thiếu chính xác nếu không tách vai trò tin tức như biến dự báo và như bằng chứng hỗ trợ quyết định.
- So sánh từ khóa, cảm xúc và ngữ nghĩa có thể bị sai lệch nếu không bảo đảm cùng mẫu quan sát, cùng biến mục tiêu, cùng cách chia tập và cùng kiểm soát rò rỉ thời gian [13].
- Nhãn giả do mô hình tạo cần được đánh giá về chất lượng, độ ổn định, tính hợp lệ của đoạn bằng chứng và khả năng truy vết nguồn, thay vì mặc định xem là nhãn chuẩn [14].
- Việc đánh giá thẻ quyết định do LLM tạo ra cần tách biệt với đánh giá khả năng dự báo; đồng thời phải kiểm tra mức bám sát bằng chứng, nội dung phát sinh ngoài bằng chứng và cách trình bày rủi ro [5].

---

# 2. Mục đích và ý nghĩa nghiên cứu

## 2.1. Tính cấp thiết

Nhà phân tích phải xử lý đồng thời tín hiệu kỹ thuật và thông tin sự kiện. Nếu chỉ tối ưu độ chính xác phân loại mà thiếu bằng chứng và khả năng truy vết, kết quả mô hình sẽ khó dùng trong thực tiễn. Ngược lại, nếu chỉ dùng LLM để tóm tắt tin tức mà thiếu tín hiệu định lượng và cơ chế kiểm soát bằng chứng, phần diễn giải có thể khó kiểm chứng. Do đó, cần một nghiên cứu ứng dụng vừa đánh giá tín hiệu học máy, vừa kiểm định khách quan vai trò của tin tức, đồng thời xây dựng hệ thống hỗ trợ quyết định có bằng chứng truy vết, thẻ quyết định được kiểm soát và cơ chế hậu kiểm.

Nghiên cứu áp dụng nguyên tắc **phương pháp cố định, phạm vi dữ liệu linh hoạt**. Các yếu tố quyết định tính hợp lệ của nghiên cứu — gồm nguyên tắc sử dụng dữ liệu theo đúng thời điểm khả dụng (*point-in-time*), tiêu chí lựa chọn dữ liệu, cách chia tập, mô hình cơ sở, nhóm so sánh và tiêu chí đánh giá — được xác định trước. Danh sách cổ phiếu và khoảng thời gian nghiên cứu có thể được xác lập sau khi kiểm tra mức độ sẵn có và chất lượng dữ liệu, nhưng không được lựa chọn dựa trên kết quả dự báo của mô hình trên tập giữ lại.

## 2.2. Ý nghĩa học thuật

- Làm rõ sự khác nhau giữa tin tức như đặc trưng dự báo và tin tức như bằng chứng có cấu trúc.
- Bổ sung bằng chứng thực nghiệm về hiệu quả và giới hạn của cách biểu diễn tần suất từ khóa trên dữ liệu cổ phiếu Việt Nam.
- Đề xuất khung biểu diễn tin tức theo các sự kiện trọng yếu có ngữ nghĩa và có khả năng truy vết nguồn.
- Đánh giá nhãn giả ngữ nghĩa theo nhiều tiêu chí, thay vì mặc định xem đầu ra của mô hình là nhãn chuẩn [14].
- Kết nối học máy, khả năng giải thích, cơ chế ràng buộc bằng chứng và thiết kế hệ thống hỗ trợ quyết định trong một quy trình thống nhất [8].

## 2.3. Ý nghĩa thực tiễn

- Xây dựng quy trình căn chỉnh dữ liệu giá, tin tức, tín hiệu và bằng chứng theo đúng thời điểm khả dụng.
- Thiết lập quy trình lựa chọn tập cổ phiếu và giai đoạn nghiên cứu có thể tái lập, qua đó hạn chế lựa chọn hậu nghiệm.
- Kiểm định giá trị dự báo gia tăng của các cách biểu diễn tin tức so với cấu hình kỹ thuật có kiểm soát độ phủ tin tức.
- Cung cấp gói bằng chứng và thẻ quyết định có kiểm soát để trình bày luận điểm, rủi ro, khoảng trống thông tin và điều kiện theo dõi.
- Xây dựng nguyên mẫu bảng điều khiển EvidenceTrace phục vụ truy vết, cập nhật bối cảnh và hậu kiểm sau thời hạn đánh giá.

---

# 3. Mục tiêu nghiên cứu

## 3.1. Mục tiêu tổng quát

Xây dựng và đánh giá nguyên mẫu hệ thống hỗ trợ quyết định cổ phiếu dựa trên tín hiệu học máy, trong đó tin tức tiếng Việt vừa là nguồn đặc trưng cần kiểm định, vừa là lớp bằng chứng ngữ nghĩa có thể truy vết. Nguyên mẫu kết hợp gói bằng chứng, thẻ quyết định có kiểm soát và bảng điều khiển EvidenceTrace phục vụ theo dõi, hậu kiểm. Nghiên cứu chú trọng tính hợp lệ ngoài mẫu, kiểm soát rò rỉ dữ liệu theo thời gian và giới hạn kết luận phù hợp với bằng chứng thu được.

## 3.2. Mục tiêu cụ thể

1. Khảo sát tính khả thi của dữ liệu, xác định phạm vi cổ phiếu và giai đoạn nghiên cứu, đồng thời xây dựng bộ dữ liệu giá và tin tức theo đúng thời điểm khả dụng.
2. Xây dựng và đánh giá tín hiệu học máy từ đặc trưng kỹ thuật kèm kiểm soát độ phủ tin tức để tạo xác suất, xếp hạng và danh sách cổ phiếu ứng viên phục vụ phân tích.
3. Khai thác tin tức như đặc trưng bổ sung theo hai lớp biểu diễn từ khóa và ngữ nghĩa; đánh giá giá trị dự báo tăng thêm theo các so sánh đã khóa trước.
4. Xây dựng gói bằng chứng và thẻ quyết định có kiểm soát, sử dụng thông tin tin tức có truy vết để giải thích tín hiệu và các rủi ro cần theo dõi.
5. Phát triển nguyên mẫu EvidenceTrace phục vụ theo dõi, truy vết và hậu kiểm; xác định phạm vi diễn giải và giới hạn kết luận của hệ thống dựa trên bằng chứng thu được.

---

# 4. Câu hỏi nghiên cứu và giả thuyết nghiên cứu

## 4.1. Câu hỏi nghiên cứu

Để phân biệt ảnh hưởng của **mức độ phủ tin tức** với ảnh hưởng của **cách biểu diễn nội dung tin tức**, nghiên cứu sử dụng một cấu hình tham chiếu gồm tín hiệu kỹ thuật và các biến phản ánh mức tin tức khả dụng. Trên nền tham chiếu này, nghiên cứu lần lượt bổ sung biểu diễn dựa trên từ khóa và biểu diễn dựa trên sự kiện trọng yếu có ngữ nghĩa. Ký hiệu E, B và C chỉ được dùng để truy vết cấu hình trong phần giả thuyết, phương pháp và báo cáo thực nghiệm. Hiệu quả tuyệt đối của cấu hình tham chiếu E được báo cáo mô tả trên cùng giao thức ngoài mẫu, không phải cổng giả thuyết.

1. **RQ1.** Việc bổ sung biểu diễn tin tức dựa trên **từ khóa** có làm thay đổi hiệu quả dự báo ngoài mẫu so với cấu hình tham chiếu chỉ gồm tín hiệu kỹ thuật và mức độ phủ tin tức hay không, theo **tiêu chí đánh giá ngoài mẫu chính đã khóa**?
2. **RQ2 — câu hỏi chính.** Biểu diễn tin tức theo **sự kiện trọng yếu có ngữ nghĩa** có làm thay đổi hiệu quả dự báo ngoài mẫu so với biểu diễn dựa trên từ khóa hay không, khi các thành phần kỹ thuật, mức độ phủ tin tức, biến mục tiêu, mẫu quan sát và cách chia tập được giữ giống nhau, theo **tiêu chí đánh giá ngoài mẫu chính đã khóa**?
3. **RQ3.** Pseudo-label ngữ nghĩa đạt mức nào về tính hợp lệ cấu trúc, tính hợp lệ đoạn bằng chứng, độ đầy đủ provenance, độ ổn định và phân loại lỗi khi so với baseline phù hợp? Liên hệ giữa materiality/direction và biến động sau sự kiện, nếu được thực hiện, chỉ là phân tích khám phá tách riêng.
4. **RQ4.** Gói bằng chứng, thẻ quyết định có kiểm soát và EvidenceTrace có duy trì liên kết nguồn, tính đầy đủ trường bắt buộc, tham chiếu bằng chứng và ranh giới thời gian giữa quyết định ban đầu, theo dõi và hậu kiểm hay không?

Các câu hỏi 1 và 2 được đặt theo hướng trung tính, không giả định trước rằng việc bổ sung tin tức sẽ cải thiện mô hình. Câu hỏi 4 chỉ phản ánh chất lượng kỹ thuật và khả năng truy vết của sản phẩm ứng dụng, không đo lường hiệu quả ra quyết định của người dùng hay lợi nhuận đầu tư.

## 4.2. Giả thuyết nghiên cứu

- **H1 — Thông tin dự báo gia tăng từ biểu diễn ngữ nghĩa:** Biểu diễn tin tức theo sự kiện trọng yếu có ngữ nghĩa có thể cung cấp thông tin dự báo gia tăng so với biểu diễn tin tức dựa trên từ khóa, khi tín hiệu kỹ thuật, mức độ phủ tin tức, biến mục tiêu và mẫu quan sát được giữ giống nhau, còn các so sánh đối sánh sử dụng tiêu chí đánh giá ngoài mẫu chính đã khóa trước khi xem holdout.

- **H2 — Bằng chứng ngữ nghĩa có truy vết:** Biểu diễn sự kiện trọng yếu có ngữ nghĩa có thể tạo ra bằng chứng tin tức có cấu trúc, gắn với đoạn trích và thông tin truy vết nguồn, đáp ứng các tiêu chí chất lượng kỹ thuật được xác định trước cho mục đích hỗ trợ phân tích.

H1 là giả thuyết nghiên cứu chính về giá trị thông tin dự báo. H2 đánh giá tính nhất quán, grounding và khả năng truy vết của lớp semantic evidence; H2 không đồng nhất với tính đúng ở mức chuyên gia, cải thiện lợi nhuận hoặc chất lượng quyết định của người dùng. Câu hỏi về keyword và EvidenceTrace vẫn được đánh giá như benchmark thứ cấp và kiểm tra kỹ thuật tương ứng.

Các giả thuyết thống kê vận hành, họ kiểm định và cổng kết luận được quy định tại Mục 6.8--6.9 sau khi hồ sơ cấu hình chính được khóa. Trường hợp kết quả không ủng hộ H1 hoặc không bác bỏ giả thuyết không chỉ được hiểu là chưa có đủ bằng chứng về khác biệt trong phạm vi và giao thức đã khảo sát; kết quả này không chứng minh các cấu hình tương đương hoặc semantic evidence vô ích.

---

# 5. Đối tượng và phạm vi nghiên cứu

## 5.1. Đối tượng nghiên cứu

- Dữ liệu giao dịch của các cổ phiếu phổ thông niêm yết trên thị trường chứng khoán Việt Nam, với tập mã thực nghiệm được lựa chọn theo tiêu chí dữ liệu đã xác định trước.
- Tin tức tiếng Việt có thể liên kết với các cổ phiếu thuộc phạm vi nghiên cứu.
- Tín hiệu học máy từ đặc trưng kỹ thuật và các cách biểu diễn tin tức.
- Nhãn giả ngữ nghĩa, đoạn bằng chứng và thông tin truy vết nguồn của tin tức.
- Gói bằng chứng, thẻ quyết định và bảng điều khiển EvidenceTrace hỗ trợ theo dõi, cập nhật và hậu kiểm.

## 5.2. Phạm vi nghiên cứu

| Tiêu chí | Phạm vi và nguyên tắc |
|---|---|
| Thị trường mục tiêu | Thị trường chứng khoán Việt Nam; tập mã thực nghiệm được chọn từ một hoặc một số sàn giao dịch có dữ liệu phù hợp. Không diễn giải tập mã cuối cùng là đại diện toàn thị trường hoặc thành viên một rổ chỉ số tại mọi thời điểm |
| Tập cổ phiếu ban đầu | Cổ phiếu phổ thông đáp ứng tiêu chí thanh khoản, thời gian niêm yết, dữ liệu giao dịch và khả năng liên kết tin tức |
| Tập cổ phiếu cuối cùng | Theo tiêu chí khả thi đã xác định trước; \underline{CẦN CHỐT TRƯỚC ĐÁNH GIÁ CHÍNH} |
| Giai đoạn dữ liệu | Theo độ bao phủ, thời điểm ghi nhận và chất lượng dữ liệu; \underline{CẦN CHỐT MỐC CỤ THỂ} |
| Dữ liệu giá | OHLCV theo ngày và các biến dẫn xuất kỹ thuật |
| Dữ liệu tin tức | Tin tức và bài báo công khai bằng tiếng Việt, có thời điểm đăng và thông tin nguồn phù hợp |
| Biến mục tiêu và thời hạn dự báo | \underline{CẦN CHỐT: nhãn, benchmark, cửa sổ chính} trong hồ sơ cấu hình trước đánh giá ngoài mẫu |
| Vai trò học máy | Tạo xác suất, xếp hạng và giải thích tín hiệu kỹ thuật |
| Vai trò tin tức | Được kiểm định như nguồn đặc trưng bổ sung và được khai thác như bằng chứng có cấu trúc |
| Vai trò LLM | Trích xuất thông tin ngữ nghĩa và tạo thẻ quyết định có ràng buộc bằng chứng; không trực tiếp dự báo lợi suất |
| Sản phẩm ứng dụng | Nguyên mẫu EvidenceTrace phục vụ truy vết, theo dõi và hậu kiểm kết quả |
| Hình thức quyết định | Hỗ trợ phân tích; người dùng là người ra quyết định cuối |

\noindent \textit{\underline{CẦN RÀ SOÁT TRƯỚC IN:} điền cụ thể tập cổ phiếu cuối cùng, giai đoạn dữ liệu, nhãn/benchmark/cửa sổ chính và thông tin GVHD theo Phiếu đăng ký đề tài luận văn/đồ án Thạc sĩ.}

## 5.3. Giới hạn của đồ án

- Không xây dựng hệ thống giao dịch tự động và không đưa ra khuyến nghị đầu tư thực tế.
- Không cam kết lợi nhuận hoặc hiệu quả khi triển khai trong môi trường thực tế.
- Nhãn ngữ nghĩa do mô hình tạo ra được xem là nhãn giả, không phải nhãn chuẩn của chuyên gia; chất lượng của chúng được đánh giá bằng các phép kiểm tra tự động và phân tích sai số phù hợp [14].
- EvidenceTrace chỉ là nguyên mẫu phục vụ nghiên cứu, chưa phải hệ thống vận hành thực tế.
- Nghiên cứu có thể chịu ảnh hưởng của sai lệch sống sót và sai lệch về độ bao phủ, do ưu tiên các mã cổ phiếu và giai đoạn có dữ liệu đủ chất lượng; hạn chế này phải được báo cáo rõ.
- Nghiên cứu không giả định mọi cách đưa tin tức vào mô hình sẽ làm tăng hiệu năng dự báo.
- Phân tích liên hệ sự kiện–biến động giá, nếu thực hiện, chỉ mang tính khám phá và không được suy thành quan hệ nhân quả.

## 5.4. Quyền dữ liệu và sử dụng mô hình bên ngoài

Đồ án chỉ sử dụng tin tức công khai theo điều khoản của nguồn dữ liệu và trong phạm vi phục vụ nghiên cứu. Toàn văn tin tức, URL hoặc corpus chưa được xác minh quyền tái phân phối sẽ không được công bố công khai như một phần dữ liệu mở. Khi cần gửi nội dung tới nhà cung cấp mô hình bên ngoài, nghiên cứu chỉ thực hiện theo cấu hình được phê duyệt, hạn chế dữ liệu không cần thiết, lưu dấu vết nguồn và không lưu trữ khóa truy cập trong mã nguồn. Các rủi ro về quyền sử dụng, lưu giữ dữ liệu và chuyển dữ liệu cho nhà cung cấp được ghi nhận trong phần giới hạn của báo cáo.

---

# 6. Phương pháp nghiên cứu

## 6.1. Thiết kế tổng quát

Nghiên cứu được triển khai qua hai giai đoạn nhằm bảo đảm tính khả thi của dữ liệu và hạn chế việc điều chỉnh phương pháp dựa trên kết quả đã quan sát [13].

**Giai đoạn A – Đánh giá tính khả thi của dữ liệu và hoàn thiện quy trình thực nghiệm**

1. Khảo sát nguồn dữ liệu giá và tin tức.
2. Kiểm tra thời điểm đăng, mức độ bao phủ, dữ liệu trùng lặp, dữ liệu thiếu và khả năng liên kết tin tức với từng mã cổ phiếu.
3. Áp dụng tiêu chí đã xác định trước để chọn tập cổ phiếu và khoảng thời gian khả dụng.
4. Xác định các phương án cho biến mục tiêu và thời hạn dự báo, sau đó đánh giá tính khả thi trên tập huấn luyện và tập xác thực.
5. Khóa hồ sơ cấu hình chính trước khi truy cập hoặc sử dụng kết quả trên tập kiểm tra cuối cùng để đưa ra quyết định thiết kế.

**Giai đoạn B – Đánh giá chính thức và xây dựng hệ thống hỗ trợ quyết định**

1. Đánh giá các cấu hình `E` và `B`.
2. Xây dựng quy trình trích xuất sự kiện trọng yếu có ngữ nghĩa và đánh giá chất lượng biểu diễn.
3. Đánh giá cấu hình `C` trên cùng mẫu dữ liệu, cùng cách chia tập và cùng biến mục tiêu với cấu hình cơ sở tương ứng.
4. Thực hiện các kiểm định thống kê và phân tích độ nhạy đã xác định trước.
5. Xây dựng gói bằng chứng và thẻ quyết định theo cấu trúc thống nhất.
6. Kiểm tra tính đầy đủ, tính hợp lệ của tham chiếu nguồn và khả năng truy vết của thẻ quyết định.
7. Xây dựng EvidenceTrace phục vụ truy vết, theo dõi và hậu kiểm kết quả.
8. Đối chiếu các kết luận với bằng chứng thu được và trình bày rõ những giới hạn của nghiên cứu.

## 6.2. Đánh giá tính khả thi của dữ liệu và quy tắc lựa chọn phạm vi

Việc lựa chọn cổ phiếu và giai đoạn nghiên cứu chỉ dựa trên các tiêu chí dữ liệu được xác định trước, như thanh khoản, thời gian niêm yết, mức độ đầy đủ của dữ liệu và khả năng liên kết tin tức. Nghiên cứu không lựa chọn mã cổ phiếu hoặc giai đoạn dựa trên kết quả dự báo của mô hình hay biến động giá xảy ra sau thời điểm lựa chọn. Các tiêu chí dự kiến gồm:

- cổ phiếu phổ thông niêm yết trên thị trường chứng khoán Việt Nam, thuộc một hoặc một số sàn giao dịch có dữ liệu phù hợp;
- có thời gian niêm yết đủ dài cho việc tạo đặc trưng và đánh giá theo thời gian;
- dữ liệu OHLCV có tính liên tục và tỷ lệ thiếu dữ liệu nằm trong ngưỡng chấp nhận;
- mức thanh khoản tối thiểu phù hợp để hạn chế các trường hợp dữ liệu quá thưa;
- tin tức có thời điểm đăng, nguồn rõ ràng và có thể liên kết với mã cổ phiếu ở mức phù hợp;
- khoảng thời gian giao nhau giữa dữ liệu giá và tin tức đủ dài để chia thành tập huấn luyện, tập xác thực và tập kiểm tra;
- các trường hợp bị loại phải được ghi nhận cùng lý do loại.

Sau bước đánh giá này, nghiên cứu tạo một **hồ sơ cấu hình chính** (*primary configuration snapshot*), trong đó ghi nhận tập cổ phiếu, giai đoạn nghiên cứu, nguồn dữ liệu, tiêu chí loại trừ, biến mục tiêu, thời hạn dự báo chính, nhóm đặc trưng, quy tắc chia tập, thước đo đánh giá và họ kiểm định. Hồ sơ này là mốc tham chiếu cho lần đánh giá chính thức. Mọi thay đổi sau thời điểm khóa phải được ghi lại cùng lý do và được phân loại là điều chỉnh quy trình hoặc phân tích độ nhạy. Hồ sơ cấu hình chính là mốc khóa quy trình nội bộ; đề tài không khẳng định đây là đăng ký độc lập có timestamp bên ngoài.

## 6.3. Biến mục tiêu, thời hạn dự báo và nguyên tắc thời gian

Bài toán chính là tạo tín hiệu và xếp hạng trên **nhãn nhị phân hiệu suất tương đối so với chỉ số thị trường tham chiếu**, đo trên một cửa sổ nắm giữ ngắn hoặc trung hạn theo phiên giao dịch; không dùng nhãn giá trung bình theo quý. Các cửa sổ ứng viên có thể được khảo sát trong Giai đoạn A, nhưng cửa sổ chính và chỉ số tham chiếu phải được khóa trong hồ sơ cấu hình chính từ tập huấn luyện/tập xác thực hoặc căn cứ phương pháp đã công bố, trước khi xem tập kiểm tra cuối cùng. Mọi cửa sổ khác chỉ là phân tích độ nhạy và không được dùng để thay cổng kết luận chính.

Nguyên tắc thời gian áp dụng thống nhất [13]:

- chỉ sử dụng dữ liệu đã khả dụng tại thời điểm ra quyết định;
- bài không có giờ đăng đáng tin chỉ được xem là khả dụng từ phiên giao dịch kế tiếp; bài liên kết mã lỗi được ghi vào nhật ký loại trừ, không biến thành đặc trưng bằng không;
- không dùng lợi suất tương lai hoặc thông tin được đăng sau thời điểm ra quyết định để tạo đặc trưng ban đầu;
- mọi bước chuẩn hóa, xử lý dữ liệu thiếu, lựa chọn đặc trưng và huấn luyện mô hình chỉ được thực hiện trên phần dữ liệu được phép trong từng tập;
- tin tức xuất hiện sau thời điểm ra quyết định chỉ được đưa vào vùng theo dõi;
- kết quả thực tế chỉ xuất hiện trong vùng hậu kiểm sau khi kết thúc thời hạn dự báo;
- các quan sát có thời hạn dự báo chồng lấn hoặc phụ thuộc theo thời gian được xử lý bằng fold mở rộng và purge yêu cầu `target_exit_date < test_start`, hoặc quy tắc tương đương được khóa trước.

## 6.4. Dữ liệu giao dịch và đặc trưng kỹ thuật

Dữ liệu giao dịch theo ngày gồm giá mở cửa, giá cao nhất, giá thấp nhất, giá đóng cửa, khối lượng giao dịch và các biến điều chỉnh nếu nguồn dữ liệu cung cấp đáng tin cậy. Các nhóm đặc trưng kỹ thuật dự kiến gồm lợi suất, biến động, thanh khoản, xu hướng, động lượng, SMA/EMA, RSI, MACD, Bollinger Bands và các đặc trưng thị trường hoặc chỉ số tham chiếu nếu bảo đảm đúng thời điểm khả dụng [9]. Đặc trưng kỹ thuật đưa vào mô hình chính được trễ theo kỳ đã khóa để bảo đảm point-in-time; danh sách trên là nhóm ứng viên, không hàm ý biến tức thời tại ngày đánh giá.

Danh sách chi tiết có thể được điều chỉnh trong Giai đoạn A dựa trên tập huấn luyện và tập xác thực. Sau khi quy trình chính được khóa, các nhóm đặc trưng của thí nghiệm chính không được thay đổi dựa trên kết quả của tập kiểm tra cuối cùng.

## 6.5. Dữ liệu tin tức và phương pháp cơ sở dựa trên từ khóa

Tin tức tiếng Việt được thu thập từ các nguồn cho phép xác định thời điểm đăng và truy vết nguồn gốc. Mỗi bản ghi dự kiến gồm tiêu đề, nội dung hoặc phần tóm tắt sẵn có, thời điểm đăng, nguồn, địa chỉ URL hoặc mã định danh nguồn và mã cổ phiếu liên quan.

Các bước xử lý gồm làm sạch, chuẩn hóa, loại bỏ bản tin trùng lặp, liên kết với mã cổ phiếu và xác định thời điểm khả dụng. Biểu diễn từ khóa của cấu hình chính là tần suất hoặc tỷ số trên danh mục đã khóa, chỉ dùng dữ liệu đã khả dụng tại thời điểm quyết định. Việc xây dựng danh mục có tham khảo nguyên tắc từ điển tài chính theo miền [17]. TF-IDF hoặc biến trọng số học được, nếu được dùng, chỉ được ước lượng trên tập huấn luyện tương ứng và thuộc phân tích độ nhạy; không được fit trên toàn bộ dữ liệu trước khi chia tập.

## 6.6. Trích xuất sự kiện trọng yếu có ngữ nghĩa

Đơn vị đầu vào là bài báo hoặc bản tin đã được liên kết với mã cổ phiếu. Cấu trúc biểu diễn sự kiện trọng yếu có ngữ nghĩa dự kiến gồm:

- `ticker_relevance`: mức độ liên quan đến mã cổ phiếu;
- `materiality`: mức độ trọng yếu của sự kiện;
- `event_type`: loại sự kiện;
- `direction`: chiều tác động hỗ trợ, bất lợi hoặc trung tính, hay cách mã hóa tương đương;
- `uncertainty` hoặc `novelty` khi phù hợp;
- `evidence_span`: đoạn bằng chứng nguyên văn;
- `source_id`, thời điểm đăng và các trường thông tin phục vụ truy vết nguồn.

Đầu ra từ LLM được gọi là **nhãn giả** (*pseudo-label*) và được sử dụng như các biến hoặc đặc trưng do mô hình tạo ra, không mặc định là nhãn chuẩn của chuyên gia [14]. Các lần gán nhãn có thể thuộc ít họ mô hình độc lập hơn số lần chạy; do đó mức thỏa thuận không chứng minh tính đúng so với chuyên gia. Chất lượng trích xuất ngữ nghĩa được đánh giá theo các tiêu chí sau:

1. mức độ bao phủ và tính hợp lệ của cấu trúc đầu ra;
2. độ ổn định giữa các lần chạy hoặc giữa các cấu hình mô hình khi phù hợp;
3. tính hợp lệ của đoạn bằng chứng (*evidence-span validity*);
4. mức độ đầy đủ của thông tin truy vết nguồn (*provenance completeness*);
5. so sánh với phương pháp cơ sở dựa trên từ khóa hoặc luật;
6. phân tích các dạng lỗi và trường hợp bất nhất.

Các phép kiểm tra trên được dùng để mô tả độ nhất quán, khả năng bám bằng chứng và giới hạn của đặc trưng ngữ nghĩa; chúng không xác lập semantic truth ở mức chuyên gia. Nếu có phân tích liên hệ giữa materiality/direction và biến động sau sự kiện, phân tích này chỉ mang tính khám phá và không thuộc họ giả thuyết chính.

## 6.7. Mô hình học máy và lựa chọn cấu hình chính

Mô hình chính dự kiến là **Random Forest** [16]; Logistic Regression được dùng để kiểm tra độ vững. XGBoost hoặc LightGBM, nếu được chạy, chỉ thuộc phân tích độ nhạy [3]. Việc điều chỉnh siêu tham số chỉ sử dụng tập huấn luyện và tập xác thực được chia theo thời gian. Không được đổi mô hình chính, thước đo chính hoặc cặp so sánh chính sau khi đã xem kết quả của tập kiểm tra cuối cùng.

Các cấu hình so sánh:

| Cấu hình | Thành phần chính | Vai trò |
|---|---|---|
| E | Technical + Coverage | Cấu hình tham chiếu chung |
| B | Technical + Coverage + Keyword | Benchmark thứ cấp (họ S1) |
| C | Technical + Coverage + Semantic | So sánh chính kiểm định H1 (họ P1) |
| Technical-only | Chỉ đặc trưng kỹ thuật | Benchmark mô tả |
| Keyword-only | Chỉ đặc trưng từ khóa | Baseline mô tả |

**Coverage** là nhóm biến kiểm soát mức độ phủ tin tức dùng chung cho E, B và C: số bài trên spine chung cùng các tổng hoặc cờ cửa sổ lăn theo phiên. Coverage không chứa tần suất từ khóa hoặc nhãn ngữ nghĩa. Dòng phân tích chính phải có nhãn mục tiêu tính được, đặc trưng kỹ thuật trễ khả dụng và Coverage của cửa sổ chính lớn hơn 0. Nhờ đó, B−E đo giá trị gia tăng của biểu diễn từ khóa ngoài độ phủ, còn C−B đo giá trị gia tăng của biểu diễn ngữ nghĩa ngoài từ khóa, trên cùng cường độ tin tức.

Trong mọi kết luận dựa trên so sánh trực tiếp, cấu hình cơ sở và cấu hình so sánh phải sử dụng cùng biến mục tiêu, cùng mẫu quan sát hợp lệ, cùng cách chia tập và cùng khoảng đánh giá. E, B và C dùng cùng technical/coverage; B và C chỉ khác lớp biểu diễn tin tức. Nếu mức độ bao phủ dữ liệu làm số lượng quan sát khác nhau, kết luận chỉ được đưa ra trên phần mẫu chung hoặc phải nêu rõ sự khác biệt về độ bao phủ.

## 6.8. Phân tích chính và phân tích độ nhạy

Trước lần đánh giá chính thức, nghiên cứu xây dựng một hồ sơ cấu hình chính, trong đó ghi nhận ít nhất các nội dung sau:

- tập cổ phiếu đã qua bước đánh giá tính khả thi của dữ liệu, ngưỡng chọn và nhật ký loại trừ;
- giai đoạn nghiên cứu và nguồn dữ liệu kèm phiên bản hoặc hash phù hợp;
- cách xác định biến mục tiêu nhị phân hiệu suất tương đối và chỉ số tham chiếu;
- thời hạn dự báo chính cùng các thời hạn ứng viên được phép khảo sát;
- mô hình chính, mô hình độ vững, candidate set và quy tắc tuning;
- các nhóm đặc trưng, định nghĩa Coverage, quy tắc missingness và khóa quan sát hợp lệ;
- bộ lọc sự kiện và mức độ liên quan của biểu diễn ngữ nghĩa;
- quy tắc chia tập mở rộng, purge, số fold tối thiểu và chính sách không fallback split;
- tiêu chí đánh giá ngoài mẫu chính đã khóa, danh sách chỉ số phụ và lý do chọn/đổi tiêu chí nếu có;
- quy tắc suy luận chính, đơn vị bắt cặp, block bootstrap, kiểm định hoán vị và alpha;
- các họ P1 (C−B, kết luận chính), S1 (B−E và C−E, thứ cấp/độ nhạy) và T1 (Top-K thăm dò, nếu đủ điều kiện) cùng quy tắc hiệu chỉnh đa kiểm định Benjamini–Hochberg;
- timestamp, phiên bản/hàm băm hồ sơ và nhật ký deviation sau thời điểm khóa.

Các thời hạn dự báo, mô hình, bộ lọc sự kiện hoặc biến thể đặc trưng khác được xếp vào **phân tích độ nhạy hoặc phân tích bổ sung**. Không được thay đổi cấu hình chính sau khi đã xem kết quả của tập kiểm tra cuối cùng chỉ vì một cấu hình khác cho kết quả tốt hơn.

Để kiểm định **H1**, cổng suy luận chính thuộc họ **P1** dùng chênh lệch giữa C và B. Giả thuyết không vận hành là $H_{01}: \Delta(C-B) \leq 0$; giả thuyết thay thế là $H_{11}: \Delta(C-B) > 0$, trong đó $\Delta$ là chênh lệch theo tiêu chí đánh giá ngoài mẫu chính đã khóa. So sánh B−E và C−E thuộc họ **S1**, được kiểm định hai phía như benchmark/thử độ nhạy; không thay cổng kết luận của H1. Các trạng thái thiếu điều kiện được báo cáo là `không ước lượng được` hoặc `blocked`, không gán chênh lệch bằng không.

## 6.9. Đánh giá tín hiệu và kiểm định thống kê

Tập tiêu chí đánh giá ứng viên gồm Balanced Accuracy, AUC-ROC, Precision, Recall, F1-score, Brier score, log loss, độ hiệu chỉnh xác suất/ECE khi phù hợp, cùng Precision@K hoặc rank IC khi biến mục tiêu và dạng tín hiệu cho phép.

**Balanced Accuracy là thước đo mặc định được đề xuất cho cấu hình chính.** Việc thay thước đo mặc định chỉ được quyết định trong Giai đoạn A, trên tập huấn luyện/tập xác thực hoặc căn cứ phương pháp đã công bố, khi thước đo mặc định không xác định được hoặc không phù hợp với biến mục tiêu/phân bố nhãn. Lý do thay đổi, tiêu chí thay thế và phiên bản hồ sơ cấu hình phải được ghi nhận trước khi xem kết quả trên tập giữ lại. Không được đổi thước đo chính, mô hình chính hoặc cặp so sánh chính sau khi đã xem tập kiểm tra. Các chỉ số phụ không thay cổng kết luận chính.

Các cấu hình mô hình được so sánh trên cùng tập quan sát ngoài mẫu để bảo đảm tính công bằng. Do dữ liệu chứng khoán có sự phụ thuộc theo thời gian, khoảng tin cậy và kiểm định thống kê được tính bằng phương pháp phù hợp với dữ liệu chuỗi thời gian, chẳng hạn lấy mẫu lại theo khối [15]. Khi thực hiện nhiều kiểm định, nghiên cứu áp dụng hiệu chỉnh Benjamini–Hochberg cho họ giả thuyết đã khóa trước [12].

Kết quả phân tích được trình bày theo các thước đo đã xác định, bao gồm cả trường hợp chênh lệch giữa các mô hình không có ý nghĩa thống kê. Precision@K là chỉ số xếp hạng; mô phỏng danh mục Top-K, nếu thực hiện, chỉ mang tính thăm dò kinh tế và không được dùng để claim alpha hoặc khả năng triển khai thực tế.

## 6.10. Gói bằng chứng và thẻ quyết định

Đối với mỗi trường hợp phân tích, hệ thống xây dựng một gói bằng chứng gồm:

- xác suất hoặc thứ hạng do mô hình học máy tạo ra;
- phần giải thích dựa trên đặc trưng kỹ thuật [8];
- thông tin liên quan được trích xuất từ tin tức, kèm mã định danh nguồn và thời điểm đăng;
- các rủi ro, mức độ bất định và khoảng trống thông tin cần lưu ý.

Từ gói bằng chứng, hệ thống tạo thẻ quyết định theo một cấu trúc thống nhất, gồm nhận định và tín hiệu chính, bằng chứng củng cố hoặc phản biện, yếu tố rủi ro, điều kiện cần theo dõi và thời điểm hậu kiểm. Thẻ quyết định được kiểm tra về tính đầy đủ của các trường thông tin, tính hợp lệ của tham chiếu nguồn và sự nhất quán giữa nội dung trình bày với bằng chứng được dẫn. Kết quả kiểm tra chỉ phản ánh chất lượng kỹ thuật và khả năng truy vết của thẻ.

## 6.11. EvidenceTrace, theo dõi và hậu kiểm kết quả

Nguyên mẫu EvidenceTrace được tổ chức theo ba vùng thời gian:

- **Vùng quyết định ban đầu**: hiển thị dữ liệu, tín hiệu và tin tức đã khả dụng tại thời điểm ra quyết định.
- **Vùng theo dõi**: cập nhật các tin tức và sự kiện xuất hiện sau thời điểm ra quyết định, kèm thời điểm đăng và nguồn tin.
- **Vùng hậu kiểm**: hiển thị kết quả thực tế sau khi kết thúc thời hạn dự báo và hỗ trợ đối chiếu với nhận định ban đầu.

EvidenceTrace được kiểm tra trên tối thiểu ba trường hợp được chọn trước theo các strata về mức độ phủ tin, trạng thái theo dõi và tính sẵn có của hậu kiểm. Mỗi case audit phải có source ID hoặc URL/mã định danh nguồn, timestamp, khóa quyết định, tham chiếu tín hiệu, evidence span hoặc lý do thiếu bằng chứng, và phân tách rõ initial/monitor/review. Audit không đạt nếu thiếu định danh nguồn bắt buộc, đoạn bằng chứng không truy được, dữ liệu hậu kiểm xuất hiện ở vùng initial, hoặc timestamp vi phạm ranh giới thời gian. Nếu có so sánh thẻ full-evidence với thẻ ML-only hoặc rule, việc so sánh chỉ được thực hiện trong cùng điều kiện sinh và chấm điểm đã khai báo; kết quả không được suy thành chất lượng quyết định của người dùng.

## 6.12. Kiểm soát rò rỉ dữ liệu và nguyên tắc diễn giải

- Không sử dụng dữ liệu xuất hiện sau thời điểm ra quyết định để tạo đặc trưng, bằng chứng hoặc thẻ quyết định ban đầu.
- Mọi bước tiền xử lý có học tham số chỉ được thực hiện trên tập huấn luyện tương ứng.
- Các cấu hình mô hình phải được so sánh trên cùng mẫu quan sát và cùng cách chia tập.
- Các lựa chọn chính về dữ liệu, biến mục tiêu, thời hạn dự báo, mô hình và thước đo đánh giá phải được xác định trước khi xem kết quả của tập kiểm tra cuối cùng; mọi thay đổi sau đó phải được ghi nhận riêng.

Các kết luận của đồ án chỉ phản ánh hiệu quả dự báo và chất lượng kỹ thuật trong phạm vi dữ liệu được khảo sát, không được suy rộng thành hiệu quả đầu tư hoặc chất lượng quyết định thực tế của người dùng.

---

# 7. Công cụ và thư viện dự kiến

| Nhóm | Công cụ / Thư viện | Mục đích |
|---|---|---|
| Ngôn ngữ lập trình | Python | Ngôn ngữ chính |
| Xử lý dữ liệu | Pandas, NumPy | Làm sạch, căn chỉnh, tổng hợp |
| Dữ liệu thị trường | vnstock hoặc nguồn tương đương | Thu thập dữ liệu giá |
| Thu thập tin tức | BeautifulSoup, Scrapy hoặc công cụ tương đương | Thu thập bài viết |
| Xử lý tiếng Việt | underthesea, VnCoreNLP, PhoBERT hoặc công cụ phù hợp | Chuẩn hóa và biểu diễn văn bản khi cần [11] |
| Học máy | scikit-learn, XGBoost, LightGBM | Xây dựng mô hình cơ sở và so sánh các cấu hình [3] |
| Giải thích mô hình | SHAP, permutation importance | Giải thích tín hiệu của mô hình [8] |
| LLM và API | Mô hình phù hợp được truy cập qua API | Trích xuất thông tin ngữ nghĩa và tạo thẻ quyết định |
| Đánh giá thống kê | SciPy, statsmodels hoặc công cụ tương đương | Ước lượng khoảng tin cậy, kiểm định và hiệu chỉnh đa kiểm định |
| Bảng điều khiển | Streamlit, Dash, FastAPI hoặc bộ công nghệ tương đương | Xây dựng nguyên mẫu EvidenceTrace |
| Trực quan hóa | Matplotlib, Plotly hoặc tương đương | Biểu đồ và báo cáo |
| Quản lý phiên bản | Git | Theo dõi mã nguồn, quy trình thực nghiệm và các sản phẩm trung gian |

Danh sách công cụ có thể được điều chỉnh trong quá trình triển khai, miễn là không làm thay đổi logic của quy trình nghiên cứu.

---

# 8. Kết quả dự kiến

1. Bộ tiêu chí đánh giá tính khả thi của dữ liệu, hồ sơ cấu hình chính và bộ dữ liệu đã căn chỉnh theo đúng thời điểm khả dụng.
2. Kết quả đánh giá ngoài mẫu của cấu hình tham chiếu, benchmark từ khóa và so sánh chính kiểm định H1; báo cáo đầy đủ kết quả ủng hộ, không ủng hộ, không bác bỏ giả thuyết không hoặc không ước lượng được.
3. Cấu trúc biểu diễn sự kiện trọng yếu có ngữ nghĩa và báo cáo chất lượng nhãn giả, gồm tính ổn định, tính hợp lệ của đoạn bằng chứng, khả năng truy vết nguồn và phân loại lỗi.
4. Các gói bằng chứng, thẻ quyết định và kết quả kiểm tra tính đầy đủ, tính hợp lệ của tham chiếu nguồn, khả năng truy vết.
5. Nguyên mẫu EvidenceTrace phục vụ theo dõi, truy vết và hậu kiểm trên một số trường hợp nghiên cứu đã được rà soát.
6. Ma trận liên kết giữa kết luận, bằng chứng và giới hạn, cùng nhật ký thay đổi quy trình nhằm bảo đảm diễn giải trung thực kết quả nghiên cứu.

---

# 9. Đóng góp dự kiến của đồ án

- Áp dụng nguyên tắc **phương pháp cố định, phạm vi dữ liệu linh hoạt**, phù hợp với bài toán dữ liệu tài chính và tin tức có mức độ bao phủ không đồng đều.
- Cung cấp bằng chứng thực nghiệm có kiểm soát về hiệu quả và giới hạn của cách biểu diễn tần suất từ khóa trên dữ liệu cổ phiếu Việt Nam trong phạm vi và giao thức đã khảo sát.
- Đề xuất và đánh giá cấu trúc bằng chứng tin tức dựa trên sự kiện trọng yếu có ngữ nghĩa, kèm đoạn bằng chứng và thông tin truy vết nguồn.
- Thiết kế quy trình so sánh các cấu hình `E`, `B` và `C` trên cùng mẫu quan sát, cùng cách chia tập và theo đúng thời điểm khả dụng của dữ liệu.
- Xây dựng quy trình đánh giá nhãn giả ngữ nghĩa và kiểm tra thẻ quyết định dựa trên độ ổn định, tính hợp lệ của bằng chứng và khả năng truy vết nguồn tin.
- Xây dựng kiến trúc hỗ trợ quyết định dựa trên tín hiệu học máy, trong đó LLM chỉ đóng vai trò trích xuất và tổng hợp thông tin có ràng buộc bằng chứng, thay vì trực tiếp dự báo giá.
- Phân biệt rõ các nhóm kết luận về khả năng dự báo, chất lượng biểu diễn, chất lượng nội dung được tạo từ bằng chứng, khả năng truy vết và kết quả hậu kiểm.

---

# 10. Nơi thực hiện đồ án

Trường Đại học Khoa học Tự nhiên – Đại học Quốc gia Thành phố Hồ Chí Minh.

---

# 11. Thời gian thực hiện

Đồ án được thực hiện theo các giai đoạn dự kiến dưới đây. Tiến độ cụ thể có thể điều chỉnh theo tình hình dữ liệu, phản hồi hướng dẫn và lịch học vụ, nhưng không được dùng để thay đổi cấu hình chính sau khi đã xem kết quả trên tập giữ lại.

\underline{CẦN CHỐT THỜI GIAN THEO PHIẾU ĐĂNG KÝ TRƯỚC KHI NỘP HỒ SƠ.}

| Giai đoạn dự kiến | Nội dung thực hiện | Mốc dự kiến |
|---|---|---|
| 1 | Khảo sát bài toán, tổng quan tài liệu và chuẩn bị nguồn dữ liệu | \underline{Tháng ... đến tháng ...} |
| 2 | Đánh giá tính khả thi của dữ liệu, hoàn thiện phạm vi và khóa hồ sơ cấu hình chính | \underline{Tháng ... đến tháng ...} |
| 3 | Xây dựng tín hiệu kỹ thuật, baseline từ khóa, semantic schema và thực hiện một lần đánh giá ngoài mẫu theo hồ sơ cấu hình đã khóa | \underline{Tháng ... đến tháng ...} |
| 4 | Kiểm định H1 qua cổng P1 (C−B), thực hiện benchmark/độ nhạy S1, đánh giá chất lượng nhãn giả và ghi nhận kết quả không ước lượng được nếu có | \underline{Tháng ... đến tháng ...} |
| 5 | Hoàn thiện gói bằng chứng, thẻ quyết định và nguyên mẫu EvidenceTrace | \underline{Tháng ... đến tháng ...} |
| 6 | Tổng hợp kết quả, hoàn thiện báo cáo đồ án và chuẩn bị bảo vệ | \underline{Tháng ... đến tháng ...} |

---

# 12. Tài liệu tham khảo dự kiến

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
12. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological)*, 57(1), 289--300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
13. Bergmeir, C., Hyndman, R. J., & Koo, B. (2018). A note on the validity of cross-validation for evaluating autoregressive time series prediction. *Computational Statistics & Data Analysis*, 120, 70--83. https://doi.org/10.1016/j.csda.2017.11.003
14. Ratner, A., Bach, S. H., Ehrenberg, H., Fries, J., Wu, S., & Ré, C. (2017). Snorkel: Rapid training data creation with weak supervision. *Proceedings of the VLDB Endowment*, 11(3), 269--282. https://doi.org/10.14778/3157794.3157797
15. Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303--1313. https://doi.org/10.1080/01621459.1994.10476870
16. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5--32. https://doi.org/10.1023/A:1010933404324
17. Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance*, 66(1), 35--65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
