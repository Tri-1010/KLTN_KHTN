---
geometry: "paper=a4paper, top=3.5cm, bottom=3cm, left=3.5cm, right=2cm"
documentclass: extarticle
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
  - \AtBeginDocument{\fontsize{13}{13}\selectfont}
  - \setlength{\parindent}{1cm}
  - \setlength{\parskip}{0.2em}
  - \titleformat{\section}{\normalfont\fontsize{16}{19}\selectfont\bfseries}{\thesection.}{0.5em}{}
  - \titleformat{\subsection}{\normalfont\fontsize{15}{18}\selectfont\bfseries}{\thesubsection.}{0.5em}{}
  - \titleformat{\subsubsection}{\normalfont\fontsize{14}{17}\selectfont\bfseries}{\thesubsubsection.}{0.5em}{}
---

\begin{titlepage}
\fontsize{14}{19}\selectfont
\setstretch{1.25}
\begin{center}

\textbf{ĐẠI HỌC QUỐC GIA TP.HCM}\\
\textbf{TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN}

\vspace{1.2cm}

Họ tên HVCH: Ngô Minh Trí\\
Mã số học viên: 24C01024

\vspace{1.0cm}

{\fontsize{16}{19}\selectfont\textbf{ĐỀ CƯƠNG NGHIÊN CỨU ĐỀ TÀI\\ĐỒ ÁN THẠC SĨ}}

\vspace{1.0cm}

\end{center}

{\fontsize{13}{18}\selectfont\noindent\underline{Tên đề tài:}\par}
{\centering\fontsize{16}{19}\selectfont\parbox[t]{0.94\textwidth}{\centering Xây dựng và đánh giá hệ thống hỗ trợ phân tích cổ phiếu Việt Nam kết hợp tín hiệu học máy với các biểu diễn tin tức}\par}

\vspace{0.4cm}

{\fontsize{13}{18}\selectfont\noindent\underline{Tên đề tài (tiếng Anh):}\par}
{\centering\fontsize{16}{19}\selectfont\hyphenpenalty=10000\relax\exhyphenpenalty=10000\relax\parbox[t]{0.94\textwidth}{\centering Development and Evaluation of a Support System for Vietnamese \mbox{Stock Analysis} Combining Machine Learning Signals with News~Representations}\par}

\vspace{0.45cm}

\noindent \underline{Ngành:} Khoa học Dữ liệu

\vspace{0.3cm}

\noindent \underline{Mã số ngành:} 8460108

\vspace{0.6cm}

\begin{center}
\underline{Xác nhận của giảng viên hướng dẫn}\\
\textit{(Ký tên và ghi rõ họ tên)}

\vspace{0.8cm}

\begin{minipage}[t]{0.45\textwidth}
\centering
\vspace{2.4cm}
\underline{Họ tên:} Hồ Sĩ Tùng Lâm
\end{minipage}
\hfill
\begin{minipage}[t]{0.45\textwidth}
\centering
\vspace{2.4cm}
\underline{Họ tên:} Nguyễn Thanh Bình
\end{minipage}

\vspace{0.4cm}

TP. HCM, tháng 9 năm 2026

\end{center}
\end{titlepage}

\begin{center}
{\fontsize{16}{19}\selectfont\textbf{NỘI DUNG CHÍNH CỦA NGHIÊN CỨU}}
\end{center}

\vspace{0.35cm}

# 1. Giới thiệu tổng quan

## 1.1. Bối cảnh nghiên cứu

Thị trường chứng khoán Việt Nam tạo ra lượng lớn dữ liệu giao dịch và tin tức công khai. Dữ liệu giá, khối lượng và các chỉ báo dẫn xuất từ chúng cung cấp cơ sở để xây dựng đặc trưng kỹ thuật cho mô hình học máy [1]. Trong khi đó, tin tức tiếng Việt phản ánh những sự kiện có thể ảnh hưởng đến doanh nghiệp và nhà đầu tư, như kết quả kinh doanh, cổ tức, phát hành, nợ vay, dự án, thay đổi quản trị và rủi ro pháp lý. Việc kết hợp dữ liệu giao dịch với tin tức có thể bổ sung thông tin cho mô hình dự báo [2]. Tuy nhiên, mọi đặc trưng phải chỉ sử dụng thông tin đã khả dụng tại thời điểm ra quyết định.

Trong thực tiễn phân tích, xác suất tăng giá hoặc thứ hạng cổ phiếu chưa đủ để hình thành một hồ sơ quyết định có thể kiểm chứng. Người sử dụng cần biết tín hiệu được tạo từ dữ liệu nào, thông tin nào củng cố hoặc làm suy yếu nhận định, rủi ro nào cần được theo dõi, và kết quả thực tế sau thời hạn đánh giá có phù hợp với luận điểm ban đầu hay không. Vì vậy, vấn đề trung tâm của đồ án là thu hẹp khoảng cách giữa đầu ra dự báo của mô hình và một quy trình hỗ trợ quyết định có khả năng giải thích, truy vết, theo dõi và hậu kiểm.

Trên cơ sở đó, đồ án hướng đến xây dựng một nguyên mẫu hệ thống hỗ trợ quyết định dựa trên bằng chứng (*evidence-grounded decision support prototype*). Hệ thống kết hợp tín hiệu định lượng từ dữ liệu thị trường với tin tức công khai theo hai vai trò phân biệt. Thứ nhất, tin tức được biểu diễn thành đặc trưng để kiểm định liệu việc bổ sung thông tin văn bản có tạo ra giá trị dự báo gia tăng so với chỉ sử dụng đặc trưng kỹ thuật hay không. Thứ hai, các bài viết liên quan và các đoạn thông tin có nguồn gốc xác định được sử dụng làm bằng chứng nhằm giải thích tín hiệu, nhận diện rủi ro và hỗ trợ quá trình theo dõi nhận định.

Để bảo đảm tính khách quan của so sánh, mẫu đánh giá chính bao gồm mọi quan sát có dữ liệu giao dịch và biến mục tiêu hợp lệ, không phụ thuộc vào việc tại thời điểm đánh giá có tin tức liên quan hay không. Đối với các quan sát không có tin phù hợp, các đặc trưng tin tức được quy ước bằng không theo quy tắc xác định trước. Độ phủ tin tức, việc liên kết bài viết với mã cổ phiếu, thời điểm đăng tải và chất lượng trích xuất thông tin được theo dõi riêng trong kiểm tra chất lượng dữ liệu, phân tầng và phân tích độ nhạy; các yếu tố này không được dùng để lọc mẫu đánh giá chính hoặc làm biến dự báo.

Mô hình ngôn ngữ lớn (Large Language Model - LLM) không được sử dụng như một mô hình dự báo giá độc lập. Trong đồ án, mô hình chỉ hỗ trợ trích xuất, cấu trúc hóa và tổng hợp thông tin từ dữ liệu đầu vào có thể kiểm tra. Nghiên cứu đánh giá ba cấu hình dự báo: chỉ sử dụng đặc trưng kỹ thuật; kết hợp đặc trưng kỹ thuật với biểu diễn từ khóa; và kết hợp đặc trưng kỹ thuật với biểu diễn ngữ nghĩa. Hiệu quả của việc bổ sung tin tức được xác định từ kết quả thực nghiệm trên cùng mẫu quan sát. Nguyên mẫu đồng thời tách thông tin có tại thời điểm ra quyết định khỏi dữ liệu dùng cho theo dõi và hậu kiểm, qua đó hỗ trợ truy vết và hạn chế rò rỉ thông tin theo thời gian.

## 1.2. Tổng quan nghiên cứu trong và ngoài nước

### 1.2.1. Nghiên cứu quốc tế

Dự báo xu hướng giá cổ phiếu bằng học máy từ dữ liệu giá, khối lượng và chỉ báo kỹ thuật là hướng nghiên cứu đã được quan tâm từ lâu [1]. Tin tức và bài báo công khai cũng được khai thác bằng nhiều cách, từ từ khóa, TF-IDF và phân tích cảm xúc đến mô hình ngôn ngữ tiền huấn luyện và trích xuất sự kiện [2], [5], [6], [7], [8]. Do từ ngữ trong văn bản tài chính có thể mang nghĩa khác với ngữ cảnh thông thường, các cách biểu diễn dựa trên từ khóa cần được xây dựng và diễn giải thận trọng [13]. Nghiên cứu theo hướng sự kiện còn cho thấy loại sự kiện và ngữ cảnh có thể cung cấp thông tin mà việc đếm từ khóa khó phản ánh đầy đủ [7].

Gần đây, LLM đã được thử nghiệm trong phân tích tài chính [4]. Tuy nhiên, việc dùng trực tiếp LLM để dự báo hoặc tạo khuyến nghị có thể làm phát sinh nội dung thiếu căn cứ, rò rỉ thông tin từ tương lai và kết quả khó kiểm soát [3], [18]. Vì vậy, trong một hệ thống hỗ trợ quyết định, LLM phù hợp hơn với các tác vụ có cấu trúc, được ràng buộc bằng bằng chứng, có khả năng truy vết nguồn và tách biệt dữ liệu tại thời điểm ra quyết định khỏi dữ liệu theo dõi, hậu kiểm.

### 1.2.2. Nghiên cứu trong nước

Trong phạm vi tài liệu đã rà soát đến thời điểm lập đề cương, các nghiên cứu về thị trường chứng khoán Việt Nam đã áp dụng học máy để dự báo xu hướng giá từ dữ liệu và chỉ báo kỹ thuật, nhận diện trạng thái bong bóng thị trường, hoặc phân tích mối liên hệ giữa thông tin kế toán và lợi suất cổ phiếu [20], [21], [22].

Đối với dữ liệu văn bản, PhoBERT cung cấp một mô hình ngôn ngữ tiền huấn luyện cho tiếng Việt, tạo nền tảng để khai thác văn bản trong các bài toán chuyên biệt [9].

Trên cơ sở đó, chưa tìm thấy công trình nào đồng thời so sánh biểu diễn tin tức dựa trên từ khóa và biểu diễn ngữ nghĩa trên cùng mẫu theo nguyên tắc *point-in-time*, gắn đầu ra ngữ nghĩa với đoạn bằng chứng có thể truy vết về nguồn, và tách đánh giá khả năng dự báo khỏi đánh giá khả năng truy vết trong hệ thống hỗ trợ quyết định. Nhận định khoảng trống này chỉ có hiệu lực trong phạm vi tài liệu đã rà soát và sẽ tiếp tục được cập nhật trong quá trình thực hiện đồ án.

## 1.3. Khoảng trống nghiên cứu

- Nhiều nghiên cứu dừng ở dự báo tăng/giảm hoặc xếp hạng, chưa tổ chức đủ quy trình hỗ trợ quyết định gồm tín hiệu, bằng chứng, rủi ro, theo dõi và hậu kiểm.
- Biểu diễn dựa trên tần suất từ khóa dễ tái lập nhưng khó phản ánh đầy đủ mức liên quan với từng mã cổ phiếu, tính trọng yếu, loại sự kiện, chiều tác động và đoạn bằng chứng nguyên văn [2], [7]. Khác biệt về ngữ nghĩa của từ ngữ tài chính càng làm rõ giới hạn này [13].
- Việc kết luận tin tức “có ích” hoặc “không có ích” dễ thiếu chính xác nếu không tách vai trò tin tức như đặc trưng dự báo và như bằng chứng hỗ trợ quyết định.
- Khoảng trống trọng tâm không chỉ nằm ở việc bổ sung một mô hình mới, mà còn ở việc xây dựng một phép so sánh có thể tái lập. Các cách biểu diễn tin tức cần được đánh giá trên cùng mẫu quan sát, biến mục tiêu, mốc thời gian khả dụng, cách chia tập, mô hình và quy tắc đánh giá. Kết quả về khả năng dự báo, chất lượng biểu diễn, nội dung có bằng chứng và khả năng truy vết cũng cần được diễn giải riêng.
- Nhãn giả (*pseudo-label*) do mô hình tạo cần được kiểm tra về cấu trúc, độ ổn định, đoạn bằng chứng và khả năng truy vết, thay vì mặc định là nhãn chuẩn [11]. Mức độ đồng thuận giữa các lần trích xuất không tự xác lập độ đúng theo chuẩn chuyên gia [19].
- Việc đánh giá thẻ quyết định do LLM tạo ra cần tách biệt với đánh giá khả năng dự báo; đồng thời phải kiểm tra mức bám sát bằng chứng, nội dung phát sinh ngoài bằng chứng và cách trình bày rủi ro [3].


# 2. Mục đích và ý nghĩa nghiên cứu

## 2.1. Tính cấp thiết

Nhà phân tích phải xử lý đồng thời tín hiệu kỹ thuật và thông tin sự kiện. Nếu chỉ tối ưu độ chính xác phân loại mà thiếu bằng chứng và khả năng truy vết, kết quả mô hình sẽ khó dùng trong thực tiễn. Ngược lại, nếu chỉ dùng LLM để tóm tắt tin tức mà thiếu tín hiệu định lượng và cơ chế kiểm soát bằng chứng, phần diễn giải có thể khó kiểm chứng. Do đó, cần một nghiên cứu ứng dụng vừa đánh giá tín hiệu học máy, vừa kiểm định khách quan vai trò của tin tức, đồng thời xây dựng hệ thống hỗ trợ quyết định dựa trên bằng chứng có thể truy vết, thẻ quyết định được kiểm soát và cơ chế hậu kiểm.

Nghiên cứu áp dụng nguyên tắc phương pháp cố định, phạm vi dữ liệu linh hoạt. Các yếu tố quyết định tính hợp lệ của nghiên cứu — gồm nguyên tắc sử dụng dữ liệu theo đúng thời điểm khả dụng (*point-in-time*), tiêu chí lựa chọn dữ liệu, cách chia tập, mô hình cơ sở, nhóm so sánh và tiêu chí đánh giá — được xác định trước. Danh sách cổ phiếu và khoảng thời gian nghiên cứu có thể được xác lập sau khi kiểm tra mức độ sẵn có và chất lượng dữ liệu, nhưng không được lựa chọn dựa trên kết quả dự báo của mô hình trên tập giữ lại.

## 2.2. Ý nghĩa học thuật

- Làm rõ sự khác nhau giữa tin tức như đặc trưng dự báo và tin tức như bằng chứng có cấu trúc.
- Bổ sung bằng chứng thực nghiệm về hiệu quả và giới hạn của cách biểu diễn từ khóa và ngữ nghĩa trên dữ liệu cổ phiếu Việt Nam trong cùng một giao thức so sánh có thể tái lập.
- Đề xuất khung biểu diễn tin tức theo các sự kiện trọng yếu có ngữ nghĩa, gắn với đoạn bằng chứng và thông tin truy vết nguồn.
- Đánh giá quy trình tạo nhãn giả ngữ nghĩa về tính đầy đủ của cấu trúc, độ ổn định giữa các lần trích xuất, khả năng đối chiếu với đoạn bằng chứng, thông tin truy vết nguồn và các dạng lỗi thường gặp.
- Phân biệt kết luận về hiệu quả dự báo, chất lượng biểu diễn, chất lượng nội dung có bằng chứng và khả năng truy vết; kết nối các lớp này trong một quy trình hỗ trợ quyết định thống nhất.

## 2.3. Ý nghĩa thực tiễn

- Xây dựng quy trình căn chỉnh dữ liệu giá, tin tức, tín hiệu và bằng chứng theo đúng thời điểm khả dụng.
- Thiết lập quy trình lựa chọn tập cổ phiếu và giai đoạn nghiên cứu có thể tái lập, qua đó hạn chế lựa chọn hậu nghiệm.
- Kiểm định giá trị dự báo gia tăng của các cách biểu diễn tin tức so với cấu hình kỹ thuật trên cùng mẫu chính; độ phủ tin tức chỉ phục vụ kiểm tra chất lượng dữ liệu, phân tầng và phân tích độ nhạy.
- Cung cấp gói bằng chứng và thẻ quyết định có kiểm soát để trình bày luận điểm, rủi ro, khoảng trống thông tin và điều kiện theo dõi.
- Xây dựng nguyên mẫu bảng điều khiển EvidenceTrace phục vụ truy vết, cập nhật bối cảnh và hậu kiểm sau thời hạn đánh giá.


# 3. Mục tiêu nghiên cứu

## 3.1. Mục tiêu tổng quát

Mục tiêu tổng quát là xây dựng và đánh giá khung hỗ trợ phân tích cổ phiếu theo nghĩa đã nêu ở Mục 1.1: cung cấp tín hiệu, bằng chứng và điều kiện theo dõi để hỗ trợ quyết định có kiểm soát, chứ không thay thế người dùng. Khung này được hiện thực hóa bằng một nguyên mẫu kết hợp tín hiệu học máy với tin tức tiếng Việt. Trong khung đó, tin tức vừa được khai thác như một nguồn đặc trưng để kiểm định, vừa được tổ chức thành bằng chứng ngữ nghĩa có thể truy vết. Nguyên mẫu cung cấp gói bằng chứng, thẻ quyết định có kiểm soát và bảng điều khiển EvidenceTrace phục vụ theo dõi và hậu kiểm. Nghiên cứu chú trọng đánh giá ngoài mẫu, hạn chế rò rỉ dữ liệu theo thời gian và đưa ra các kết luận phù hợp với bằng chứng thu được.

## 3.2. Mục tiêu cụ thể

1. Khảo sát tính khả thi của dữ liệu, xác định phạm vi cổ phiếu và giai đoạn nghiên cứu, đồng thời xây dựng bộ dữ liệu giá và tin tức theo đúng thời điểm khả dụng.
2. Xây dựng và đánh giá tín hiệu học máy từ đặc trưng kỹ thuật để tạo xác suất, xếp hạng và danh sách cổ phiếu ứng viên phục vụ phân tích trên mẫu chính, bao gồm cả các quan sát không có tin.
3. Khai thác tin tức như đặc trưng bổ sung theo hai cách biểu diễn từ khóa và ngữ nghĩa; đánh giá hiệu quả dự báo của từng cách biểu diễn so với tín hiệu kỹ thuật, đồng thời so sánh trực tiếp hai cách biểu diễn theo các quy tắc đã khóa trước.
4. Xây dựng gói bằng chứng và thẻ quyết định có kiểm soát, sử dụng thông tin tin tức có truy vết để giải thích tín hiệu và các rủi ro cần theo dõi.
5. Phát triển nguyên mẫu EvidenceTrace phục vụ theo dõi, truy vết và hậu kiểm; xác định phạm vi diễn giải và giới hạn kết luận của hệ thống dựa trên bằng chứng thu được.


# 4. Câu hỏi nghiên cứu và giả thuyết nghiên cứu

## 4.1. Câu hỏi nghiên cứu

Nghiên cứu sử dụng một mẫu đánh giá chung gồm các quan sát có dữ liệu giao dịch, biến mục tiêu và đặc trưng kỹ thuật khả dụng đúng thời điểm. Ba cấu hình được đánh giá là cấu hình kỹ thuật, cấu hình từ khóa và cấu hình ngữ nghĩa. Các quan sát không có tin tức phù hợp vẫn thuộc mẫu chính theo quy tắc xử lý đặc trưng đã xác định trước. Thông tin về độ phủ tin tức chỉ được sử dụng để kiểm tra chất lượng dữ liệu, phân tích theo nhóm và đánh giá độ nhạy.

1. RQ1. Trên cùng mẫu quan sát và cùng giao thức đánh giá ngoài mẫu, việc bổ sung biểu diễn tin tức dựa trên từ khóa hoặc biểu diễn ngữ nghĩa vào đặc trưng kỹ thuật có làm thay đổi hiệu quả dự báo so với cấu hình kỹ thuật hay không?

2. RQ2. Quy trình trích xuất sự kiện trọng yếu từ tin tức có tạo được đầu ra có cấu trúc, có thể đối chiếu với đoạn bằng chứng và truy vết về nguồn theo các tiêu chí kỹ thuật đã xác định trước hay không?

RQ1 là câu hỏi thực nghiệm chính và được xem xét qua hai so sánh: cấu hình từ khóa với cấu hình kỹ thuật, và cấu hình ngữ nghĩa với cấu hình kỹ thuật. So sánh trực tiếp giữa cấu hình từ khóa và cấu hình ngữ nghĩa chỉ nhằm đối chiếu bổ sung hai cách biểu diễn tin tức trong cùng điều kiện thực nghiệm. RQ2 đánh giá tính vận hành, tính nhất quán và khả năng truy vết của quy trình trích xuất.

## 4.2. Giả thuyết nghiên cứu

- H1 — Giá trị dự báo của biểu diễn từ khóa: Trên mẫu đánh giá chung và theo tiêu chí đánh giá ngoài mẫu đã xác định trước, cấu hình từ khóa có hiệu quả dự báo khác với cấu hình kỹ thuật.

- H2 — Giá trị dự báo của biểu diễn ngữ nghĩa: Trên mẫu đánh giá chung và theo tiêu chí đánh giá ngoài mẫu đã xác định trước, cấu hình ngữ nghĩa có hiệu quả dự báo khác với cấu hình kỹ thuật.

H1 và H2 thuộc cùng một họ giả thuyết về giá trị dự báo của tin tức. Hai giả thuyết được kiểm định trên cùng biến mục tiêu, cùng mẫu quan sát, cùng cách chia tập, cùng mô hình chính và cùng tiêu chí đánh giá đã khóa trước. Khi đánh giá đồng thời hai biểu diễn tin tức, nghiên cứu áp dụng quy tắc hiệu chỉnh đa kiểm định đã xác định trước.


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
| Thị trường | Thị trường chứng khoán Việt Nam |
| Tập cổ phiếu thực nghiệm | Được lựa chọn từ một hoặc một số sàn giao dịch có dữ liệu phù hợp, theo các tiêu chí đã xác định trước về thanh khoản, thời gian niêm yết và mức độ đầy đủ của dữ liệu; tập cuối cùng được khóa trước lần đánh giá chính thức |
| Giai đoạn dữ liệu | Khoảng thời gian mà dữ liệu giá đáp ứng yêu cầu về độ đầy đủ, thời điểm ghi nhận và chất lượng; được khóa trước lần đánh giá chính thức. Độ phủ tin tức trong giai đoạn này được ghi nhận để kiểm tra chất lượng dữ liệu, phân tích theo nhóm và đánh giá độ nhạy |
| Dữ liệu giá | Dữ liệu OHLCV theo ngày và các biến dẫn xuất kỹ thuật |
| Dữ liệu tin tức | Tin tức và bài báo công khai bằng tiếng Việt, có thời điểm đăng hoặc ngày ghi nhận đủ để áp dụng quy tắc ánh xạ bảo thủ, kèm thông tin nguồn phù hợp |
| Biến mục tiêu và thời hạn dự báo | Một số thời hạn ngắn và trung hạn được xác định trước; một thời hạn chính, biến mục tiêu và chỉ số tham chiếu được khóa trước lần đánh giá cuối cùng |
| Vai trò học máy | Tạo xác suất, thứ hạng và danh sách cổ phiếu ứng viên phục vụ phân tích |
| Vai trò tin tức | Được kiểm định như nguồn đặc trưng bổ sung và được khai thác như bằng chứng có cấu trúc |
| Vai trò LLM | Trích xuất thông tin ngữ nghĩa và tạo thẻ quyết định có ràng buộc bằng chứng; không trực tiếp dự báo lợi suất |
| Sản phẩm ứng dụng | Nguyên mẫu bảng điều khiển EvidenceTrace phục vụ truy vết, theo dõi và hậu kiểm kết quả |
| Hình thức quyết định | Hỗ trợ phân tích; người dùng là người ra quyết định cuối cùng |

## 5.3. Giới hạn của đồ án

- Không xây dựng hệ thống giao dịch tự động và không đưa ra khuyến nghị đầu tư thực tế.
- Không cam kết lợi nhuận hoặc hiệu quả khi triển khai trong môi trường thực tế.
- Nhãn ngữ nghĩa do mô hình tạo ra được xem là nhãn giả, không phải nhãn chuẩn của chuyên gia; các kết quả liên quan chỉ được diễn giải trong phạm vi tính hợp lệ kỹ thuật và khả năng truy vết [11], [19].
- EvidenceTrace chỉ là nguyên mẫu phục vụ nghiên cứu, chưa phải hệ thống vận hành thực tế.
- Nghiên cứu có thể chịu ảnh hưởng của sai lệch sống sót và sai lệch về độ bao phủ, do ưu tiên các mã cổ phiếu và giai đoạn có dữ liệu đủ chất lượng; hạn chế này phải được báo cáo rõ.
- Nghiên cứu không giả định mọi cách đưa tin tức vào mô hình sẽ làm tăng hiệu năng dự báo.
- Phân tích liên hệ sự kiện–biến động giá, nếu thực hiện, chỉ mang tính khám phá và không được suy thành quan hệ nhân quả.


# 6. Phương pháp nghiên cứu

## 6.1. Thiết kế nghiên cứu, dữ liệu và nguyên tắc thời gian

Nghiên cứu được triển khai theo hai giai đoạn. Giai đoạn đầu đánh giá tính khả thi của dữ liệu giá và tin tức, xác định tập cổ phiếu, giai đoạn nghiên cứu, biến mục tiêu và thời hạn dự báo. Các lựa chọn này dựa trên thanh khoản, thời gian niêm yết, mức độ đầy đủ và tính liên tục của dữ liệu giao dịch; không dựa trên kết quả dự báo hoặc biến động giá xảy ra sau thời điểm lựa chọn.

Sau giai đoạn đánh giá tính khả thi, nghiên cứu khóa tập cổ phiếu, giai đoạn dữ liệu, biến mục tiêu, thời hạn dự báo, nhóm đặc trưng, quy tắc chia tập và tiêu chí đánh giá trước lần đánh giá chính thức. Các phương án còn lại chỉ được sử dụng cho phân tích bổ sung hoặc phân tích độ nhạy; mọi thay đổi sau thời điểm khóa phải được ghi nhận riêng.

Bài toán chính là tạo tín hiệu và xếp hạng cổ phiếu ứng viên trong một số thời hạn ngắn và trung hạn. Quy trình chỉ sử dụng thông tin đã khả dụng tại thời điểm ra quyết định [10], [18].

Với bài viết có thời điểm công bố đáng tin cậy, thời điểm khả dụng được xác định theo múi giờ của nguồn và lịch giao dịch. Bài được công bố sau giờ đóng cửa, vào cuối tuần hoặc ngày nghỉ chỉ được dùng từ phiên giao dịch hợp lệ kế tiếp. Nếu nguồn chỉ cung cấp ngày mà không có giờ công bố đáng tin cậy, bài viết được dùng từ phiên giao dịch đầu tiên sau ngày ghi nhận của nguồn và không ảnh hưởng đến đặc trưng hoặc bằng chứng của phiên cùng ngày.

Những bài không thể xác định phiên giao dịch tương ứng hoặc không xác định được mã cổ phiếu liên quan được ghi nhận trong báo cáo chất lượng dữ liệu và nhật ký sàng lọc mẫu; chúng không được dùng để xây dựng đặc trưng chính hoặc bằng chứng ban đầu. Mọi bước xử lý dữ liệu, lựa chọn đặc trưng và huấn luyện mô hình chỉ sử dụng phần dữ liệu tương ứng với từng tập. Tin tức xuất hiện sau thời điểm ra quyết định chỉ phục vụ theo dõi, còn kết quả thực tế chỉ được dùng cho hậu kiểm sau khi kết thúc thời hạn dự báo. Sự phụ thuộc theo thời gian giữa các quan sát được xử lý thông qua cách chia tập và phương pháp suy luận phù hợp.

## 6.2. Dữ liệu giao dịch và đặc trưng kỹ thuật

Dữ liệu giao dịch theo ngày gồm giá mở cửa (Open), giá cao nhất (High), giá thấp nhất (Low), giá đóng cửa (Close), khối lượng giao dịch (Volume) và các biến điều chỉnh nếu nguồn dữ liệu cung cấp đáng tin cậy. Các nhóm đặc trưng kỹ thuật dự kiến gồm:

- biến động lịch sử;
- thanh khoản và biến đổi khối lượng;
- xu hướng và động lượng;
- SMA/EMA;
- RSI;
- MACD;
- Bollinger Bands;
- các đặc trưng thị trường hoặc chỉ số tham chiếu, nếu bảo đảm đúng thời điểm khả dụng.

Các đặc trưng kỹ thuật được tính từ dữ liệu đã khả dụng trước thời điểm ra quyết định và được làm trễ theo quy tắc xác định trước. Danh sách chi tiết có thể được điều chỉnh trong giai đoạn đánh giá tính khả thi dựa trên tập huấn luyện và tập xác thực. Sau khi quy trình chính được khóa, các nhóm đặc trưng của thí nghiệm chính không được thay đổi dựa trên kết quả của tập kiểm tra cuối cùng.

## 6.3. Dữ liệu tin tức và các cách biểu diễn

Tin tức tiếng Việt được thu thập từ các nguồn cho phép xác định thời điểm đăng hoặc ngày ghi nhận theo quy tắc bảo thủ, đồng thời truy vết nguồn gốc. Mỗi bản ghi dự kiến gồm tiêu đề, nội dung hoặc phần tóm tắt sẵn có, thời điểm đăng hoặc ngày ghi nhận, nguồn, địa chỉ URL hoặc mã định danh nguồn và mã cổ phiếu liên quan.

Các bước xử lý gồm làm sạch, chuẩn hóa, loại bỏ bản tin trùng lặp, liên kết với mã cổ phiếu và xác định thời điểm khả dụng. Phương pháp cơ sở dựa trên từ khóa, trong đó tin tức được biểu diễn bằng tần suất xuất hiện của các từ hoặc cụm từ liên quan, dưới dạng số lần xuất hiện, tần suất chuẩn hóa hoặc TF-IDF. Nếu sử dụng TF-IDF, trọng số chỉ được ước lượng trên tập huấn luyện tương ứng. Độ phủ tin tức được ghi nhận để kiểm tra chất lượng dữ liệu và phân tích độ nhạy, không được đưa vào mô hình như một đặc trưng dự báo. Quy trình phân biệt các trạng thái: không có tin hợp lệ, thiếu thời điểm, không xác định được phiên giao dịch, lỗi liên kết mã và lỗi trích xuất.

Biểu diễn ngữ nghĩa ghi nhận mức độ liên quan đến mã cổ phiếu, mức độ trọng yếu, loại sự kiện, chiều tác động, đoạn bằng chứng và thông tin nguồn. Đầu ra của LLM được xem là nhãn giả (*pseudo-label*), không phải nhãn chuẩn của chuyên gia [11]. Quy trình được đánh giá qua tính đầy đủ của cấu trúc, độ ổn định giữa các lần trích xuất, khả năng đối chiếu với đoạn bằng chứng, thông tin truy vết nguồn và các dạng lỗi thường gặp.

## 6.4. Mô hình, cấu hình so sánh và đánh giá ngoài mẫu

Mô hình chính dự kiến là Random Forest [14]. Logistic Regression được sử dụng để kiểm tra độ vững; XGBoost [15] hoặc LightGBM [23], nếu được triển khai, chỉ thuộc phân tích độ nhạy. Việc lựa chọn đặc trưng và điều chỉnh siêu tham số chỉ sử dụng dữ liệu huấn luyện và xác thực theo thời gian, không sử dụng tập kiểm tra cuối cùng.

Nghiên cứu đánh giá ba cấu hình:

| Cấu hình | Thành phần | Vai trò |
|---|---|---|
| Kỹ thuật | Chỉ gồm các đặc trưng kỹ thuật | Cấu hình đối chứng của H1 và H2 |
| Kỹ thuật + từ khóa | Đặc trưng kỹ thuật kết hợp biểu diễn tin tức dựa trên từ khóa | Kiểm định H1 |
| Kỹ thuật + ngữ nghĩa | Đặc trưng kỹ thuật kết hợp biểu diễn sự kiện ngữ nghĩa | Kiểm định H2 |

Ba cấu hình sử dụng cùng biến mục tiêu, mẫu quan sát, cách chia tập theo thời gian, mô hình chính và nhóm đặc trưng kỹ thuật. Quan sát không có tin phù hợp vẫn được giữ trong mẫu chính; các đặc trưng tin tức được xử lý theo một quy tắc thống nhất, được xác định và khóa trước.

Độ phủ tin tức được lưu riêng để kiểm tra chất lượng dữ liệu, phân tích theo nhóm và phân tích độ nhạy; không được dùng làm đặc trưng dự báo, bộ lọc quan sát hoặc tiêu chí xác định mẫu chính. Trong mẫu chính, chỉ quan sát thực sự không có tin hợp lệ mới được xử lý theo quy tắc mã hóa đã xác định trước; các lỗi về thời điểm, ánh xạ phiên giao dịch, liên kết mã hoặc trích xuất được báo cáo riêng.

### 6.4.1. Kế hoạch phân tích

Trước khi đánh giá trên tập kiểm tra cuối cùng, nghiên cứu khóa hồ sơ phân tích chính, bao gồm:

- dữ liệu, mẫu nghiên cứu, biến mục tiêu và thời hạn dự báo;
- mô hình chính, ba cấu hình và quy tắc xây dựng đặc trưng;
- cách chia tập theo thời gian, xử lý dữ liệu thiếu và quan sát phụ thuộc;
- tiêu chí đánh giá chính, đơn vị bắt cặp, phương pháp kiểm định và quy tắc hiệu chỉnh đa kiểm định.

Mọi thay đổi sau thời điểm khóa phải được ghi nhận riêng và trình bày như phân tích bổ sung, không thay thế phân tích chính.

H1 được kiểm định bằng so sánh giữa cấu hình kỹ thuật + từ khóa và cấu hình kỹ thuật. H2 được kiểm định bằng so sánh giữa cấu hình kỹ thuật + ngữ nghĩa và cấu hình kỹ thuật. Hai giả thuyết sử dụng cùng tiêu chí chính, cùng đơn vị bắt cặp và cùng họ kiểm định; kết quả được hiệu chỉnh đa kiểm định theo quy tắc xác định trước.

So sánh giữa kỹ thuật + từ khóa và kỹ thuật + ngữ nghĩa chỉ là đối chiếu bổ sung giữa hai cấu hình không lồng nhau. Kết quả này không được diễn giải là giá trị của biểu diễn ngữ nghĩa tăng thêm ngoài biểu diễn từ khóa. Các thời hạn dự báo khác, mô hình khác, biến thể đặc trưng và phân tích theo độ phủ tin tức thuộc phân tích độ nhạy hoặc phân tích bổ sung.

### 6.4.2. Đánh giá và kiểm định thống kê

Balanced Accuracy được chọn làm tiêu chí đánh giá chính mặc định. Các chỉ số bổ sung có thể gồm AUC-ROC, Precision, Recall, F1-score, Brier score, log loss và chỉ số hiệu chỉnh xác suất. Precision@K hoặc rank IC chỉ được sử dụng khi phù hợp với dạng tín hiệu và biến mục tiêu.

Nếu Balanced Accuracy không phù hợp hoặc không xác định được, tiêu chí thay thế phải được lựa chọn trong giai đoạn huấn luyện–xác thực, có lý do phương pháp rõ ràng và được khóa trước khi xem kết quả của tập kiểm tra cuối cùng.

Chênh lệch giữa các cấu hình được tính trên cùng các quan sát ngoài mẫu và cùng đơn vị bắt cặp. Do dữ liệu có phụ thuộc theo thời gian, việc ước lượng khoảng tin cậy và thực hiện kiểm định sử dụng các phương pháp phù hợp với chuỗi thời gian, chẳng hạn lấy mẫu lại theo khối [16] hoặc kiểm định hoán vị theo quy tắc đã khóa. Hai kiểm định của H1 và H2 thuộc cùng một họ và được hiệu chỉnh bằng Benjamini–Hochberg [17].

Nghiên cứu báo cáo đầy đủ ước lượng chênh lệch, khoảng tin cậy, giá trị $p$ và kết quả sau hiệu chỉnh. Precision@K chỉ phản ánh chất lượng xếp hạng. Mô phỏng danh mục Top-K, nếu có, là phân tích kinh tế thăm dò và không được dùng để khẳng định alpha, lợi nhuận có thể triển khai hoặc hiệu quả đầu tư thực tế.

## 6.5. Gói bằng chứng, EvidenceTrace và hậu kiểm

Với mỗi trường hợp phân tích, hệ thống xây dựng một gói bằng chứng gồm:

- xác suất hoặc thứ hạng do mô hình tạo ra;
- phần giải thích dựa trên các đặc trưng kỹ thuật [12];
- sự kiện tin tức liên quan, đoạn bằng chứng, nguồn và thời điểm đăng;
- mức độ bất định, yếu tố rủi ro và khoảng trống thông tin.

Từ gói bằng chứng, hệ thống tạo thẻ quyết định theo cấu trúc thống nhất, gồm tín hiệu chính, bằng chứng ủng hộ và bằng chứng trái chiều, yếu tố rủi ro, điều kiện cần theo dõi và thời điểm hậu kiểm. Thẻ được đánh giá bằng các tiêu chí kỹ thuật: mức độ đầy đủ của trường thông tin, tính hợp lệ của tham chiếu nguồn, khả năng truy vết đến đoạn bằng chứng và sự nhất quán giữa nội dung trình bày với bằng chứng được dẫn. Các tiêu chí này không đo chất lượng quyết định của người dùng, hiệu quả đầu tư hoặc lợi nhuận.

### 6.5.1. EvidenceTrace và hậu kiểm kỹ thuật

EvidenceTrace được tổ chức thành ba vùng thời gian:

1. Vùng ban đầu: chỉ chứa dữ liệu, tín hiệu và tin tức đã khả dụng tại thời điểm lập thẻ;
2. Vùng theo dõi: ghi nhận các tin tức hoặc sự kiện xuất hiện sau thời điểm lập thẻ;
3. Vùng hậu kiểm: hiển thị biến mục tiêu hoặc kết quả quan sát được sau khi kết thúc thời hạn dự báo.

Nguyên mẫu được kiểm tra trên một tập trường hợp được xác định trước nhằm đánh giá:

- tính hợp lệ của mã định danh nguồn và thời điểm đăng;
- khả năng truy xuất đoạn bằng chứng;
- liên kết giữa thẻ, tín hiệu mô hình và dữ liệu nguồn;
- sự phân tách đúng giữa thông tin ban đầu, theo dõi và hậu kiểm;
- việc tuân thủ ranh giới thời gian.

Một trường hợp không đạt nếu thiếu định danh nguồn bắt buộc, bằng chứng không thể truy xuất, dữ liệu tương lai xuất hiện trong vùng ban đầu hoặc dữ liệu được sử dụng trước khi thực sự khả dụng. Việc lựa chọn và kiểm tra các trường hợp EvidenceTrace chỉ nhằm xác minh hoạt động kỹ thuật của nguyên mẫu, không dùng để ước lượng hiệu quả dự báo, chất lượng quyết định hoặc lợi nhuận.

## 6.6. Kiểm soát rò rỉ dữ liệu và giới hạn diễn giải

Nghiên cứu áp dụng các nguyên tắc sau:

- không sử dụng dữ liệu xuất hiện sau thời điểm lập tín hiệu để xây dựng đặc trưng, bằng chứng hoặc thẻ ban đầu;
- chỉ bài viết có thời điểm khả dụng được xác định theo quy tắc đã khóa trước mới đi vào đặc trưng chính hoặc vùng bằng chứng ban đầu; bài thiếu thời điểm, không thể ánh xạ phiên giao dịch hoặc lỗi liên kết mã được lưu và báo cáo riêng, không được mã hóa là không có tin;
- mọi bước tiền xử lý có học tham số chỉ được ước lượng trên tập huấn luyện tương ứng;
- ba cấu hình được đánh giá trên cùng mẫu, biến mục tiêu, cách chia tập, mô hình chính và nhóm đặc trưng kỹ thuật;
- độ phủ tin tức không được dùng làm đặc trưng dự báo, bộ lọc hoặc tiêu chí xác định mẫu chính;
- biến mục tiêu, thời hạn dự báo, mô hình, tiêu chí chính, cặp so sánh và giao thức kiểm định phải được khóa trước khi xem tập kiểm tra cuối cùng;
- dữ liệu theo dõi và hậu kiểm phải được tách khỏi thông tin khả dụng tại thời điểm lập tín hiệu;
- mọi thay đổi sau thời điểm khóa phải được ghi nhận và báo cáo riêng.

Kết luận của nghiên cứu chỉ phản ánh hiệu quả dự báo ngoài mẫu của ba cấu hình và chất lượng kỹ thuật của quy trình trích xuất bằng chứng, tạo thẻ và EvidenceTrace trong phạm vi dữ liệu khảo sát. Kết quả không được suy rộng thành quan hệ nhân quả, chất lượng quyết định thực tế của người dùng, khả năng tạo alpha hoặc lợi nhuận đầu tư.


# 7. Công cụ và thư viện dự kiến

| Nhóm | Công cụ / Thư viện | Mục đích |
|---|---|---|
| Ngôn ngữ lập trình | Python | Ngôn ngữ chính |
| Xử lý dữ liệu | Pandas, NumPy | Làm sạch, căn chỉnh, tổng hợp |
| Dữ liệu thị trường | vnstock hoặc nguồn tương đương | Thu thập dữ liệu giá |
| Thu thập tin tức | BeautifulSoup, Scrapy hoặc công cụ tương đương | Thu thập bài viết |
| Xử lý tiếng Việt | underthesea, VnCoreNLP, PhoBERT [9] hoặc công cụ phù hợp | Chuẩn hóa và biểu diễn văn bản khi cần |
| Học máy | scikit-learn, XGBoost, LightGBM | Xây dựng mô hình cơ sở và so sánh các cấu hình |
| Giải thích mô hình | SHAP [12], permutation importance | Giải thích tín hiệu của mô hình |
| LLM và API | Mô hình phù hợp được truy cập qua API | Trích xuất thông tin ngữ nghĩa và tạo thẻ quyết định |
| Đánh giá thống kê | SciPy, statsmodels hoặc công cụ tương đương | Ước lượng khoảng tin cậy, kiểm định và hiệu chỉnh đa kiểm định |
| Bảng điều khiển | Streamlit, Dash, FastAPI hoặc bộ công nghệ tương đương | Xây dựng nguyên mẫu EvidenceTrace |
| Trực quan hóa | Matplotlib, Plotly hoặc tương đương | Biểu đồ và báo cáo |
| Quản lý phiên bản | Git | Theo dõi mã nguồn, quy trình thực nghiệm và các sản phẩm trung gian |

Danh sách công cụ có thể được điều chỉnh trong quá trình triển khai, miễn là không làm thay đổi logic của quy trình nghiên cứu.


# 8. Kết quả dự kiến

1. Bộ tiêu chí đánh giá tính khả thi của dữ liệu, hồ sơ cấu hình chính và bộ dữ liệu đã căn chỉnh theo đúng thời điểm khả dụng.
2. Kết quả đánh giá ngoài mẫu của cấu hình kỹ thuật, cấu hình từ khóa và cấu hình ngữ nghĩa; báo cáo đầy đủ kết quả kiểm định H1, H2, kết quả đối chiếu trực tiếp giữa hai biểu diễn tin tức, cũng như các trường hợp không ước lượng được.
3. Cấu trúc biểu diễn sự kiện ngữ nghĩa và báo cáo đánh giá quy trình tạo nhãn giả về cấu trúc, độ ổn định, đoạn bằng chứng, khả năng truy vết nguồn và các dạng lỗi thường gặp.
4. Các gói bằng chứng, thẻ quyết định và kết quả kiểm tra về tính đầy đủ, tính hợp lệ của tham chiếu nguồn, khả năng truy vết và ranh giới thời gian.
5. Nguyên mẫu EvidenceTrace phục vụ theo dõi, truy vết và hậu kiểm trên một số trường hợp nghiên cứu đã được rà soát.
6. Ma trận liên kết giữa kết luận, bằng chứng và giới hạn, cùng nhật ký thay đổi quy trình nhằm bảo đảm diễn giải trung thực kết quả nghiên cứu.


# 9. Đóng góp dự kiến của đồ án

- Áp dụng nguyên tắc phương pháp cố định, phạm vi dữ liệu linh hoạt, phù hợp với bài toán dữ liệu tài chính và tin tức có mức độ bao phủ không đồng đều.
- Cung cấp một giao thức so sánh tái lập được giữa cấu hình kỹ thuật, cấu hình từ khóa và cấu hình ngữ nghĩa trên cùng mẫu quan sát, biến mục tiêu, cách chia tập và quy tắc *point-in-time* đã khóa trước.
- Bổ sung bằng chứng thực nghiệm có kiểm soát về hiệu quả và giới hạn của các biểu diễn tin tức trên dữ liệu cổ phiếu Việt Nam trong phạm vi và giao thức đã khảo sát.
- Đề xuất và đánh giá cấu trúc bằng chứng tin tức dựa trên sự kiện trọng yếu có ngữ nghĩa, kèm đoạn bằng chứng, thông tin truy vết nguồn và ranh giới thời gian rõ ràng.
- Xây dựng quy trình kiểm tra nhãn giả và thẻ quyết định dựa trên cấu trúc, độ ổn định, đoạn bằng chứng, thông tin truy vết nguồn và các dạng lỗi thường gặp.
- Tổ chức nguyên mẫu hỗ trợ phân tích dựa trên tín hiệu học máy, trong đó LLM chỉ đóng vai trò trích xuất và tổng hợp thông tin có ràng buộc bằng chứng, thay vì trực tiếp dự báo giá.
- Phân biệt rõ các nhóm kết luận về khả năng dự báo, chất lượng biểu diễn, chất lượng của nội dung được tạo trên cơ sở bằng chứng, khả năng truy vết và kết quả hậu kiểm.


# 10. Nơi thực hiện đồ án

Trường Đại học Khoa học Tự nhiên – Đại học Quốc gia Thành phố Hồ Chí Minh.


# 11. Thời gian thực hiện

Đồ án được thực hiện và hoàn thiện theo các giai đoạn dự kiến sau. Tiến độ có thể được điều chỉnh phù hợp với tình hình dữ liệu, kết quả thực nghiệm và kế hoạch đào tạo thực tế.

| Thời gian dự kiến | Nội dung thực hiện |
|---|---|
| 06–07/2026 | Khảo sát bài toán, tổng quan tài liệu, thử nghiệm ban đầu và chuẩn bị dữ liệu |
| 08–09/2026 | Cập nhật đề cương, hoàn thiện dữ liệu, phương pháp và các mô hình cơ sở |
| 09–10/2026 | Thực hiện các thí nghiệm chính, đánh giá tín hiệu học máy và các cách khai thác tin tức |
| 10–11/2026 | Hoàn thiện hệ thống hỗ trợ quyết định, đánh giá kết quả và xây dựng nguyên mẫu |
| 11–12/2026 | Tổng hợp kết quả, hoàn thiện báo cáo đồ án và chuẩn bị bảo vệ |


# 12. Tài liệu tham khảo

1. Murphy, J. J. (1999). *Technical analysis of the financial markets*. New York Institute of Finance.
2. Nassirtoussi, A. K., Aghabozorgi, S., Wah, T. Y., & Ngo, D. C. L. (2014). Text mining for market prediction: A systematic review. *Expert Systems with Applications*, 41(16), 7653--7670. https://doi.org/10.1016/j.eswa.2014.06.009
3. Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys*, 55(12), Article 248. https://doi.org/10.1145/3571730
4. Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. *SSRN Working Paper* No. 4412788. https://doi.org/10.2139/ssrn.4412788
5. Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. *arXiv preprint* arXiv:1908.10063. https://arxiv.org/abs/1908.10063
6. Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. *Journal of Computational Science*, 2(1), 1--8. https://doi.org/10.1016/j.jocs.2010.12.007
7. Ding, X., Zhang, Y., Liu, T., & Duan, J. (2015). Deep learning for event-driven stock prediction. In *Proceedings of the 24th International Joint Conference on Artificial Intelligence* (pp. 2327--2333).
8. Li, X., Xie, H., Chen, L., Wang, J., & Deng, X. (2014). News impact on stock price return via sentiment analysis. *Knowledge-Based Systems*, 69, 14--23. https://doi.org/10.1016/j.knosys.2014.04.022
9. Nguyen, D. Q., & Nguyen, A. T. (2020). PhoBERT: Pre-trained language models for Vietnamese. In *Findings of the Association for Computational Linguistics: EMNLP 2020* (pp. 1037--1042). https://doi.org/10.18653/v1/2020.findings-emnlp.92
10. Bergmeir, C., Hyndman, R. J., & Koo, B. (2018). A note on the validity of cross-validation for evaluating autoregressive time series prediction. *Computational Statistics & Data Analysis*, 120, 70--83. https://doi.org/10.1016/j.csda.2017.11.003
11. Ratner, A., Bach, S. H., Ehrenberg, H., Fries, J., Wu, S., & Ré, C. (2017). Snorkel: Rapid training data creation with weak supervision. *Proceedings of the VLDB Endowment*, 11(3), 269--282. https://doi.org/10.14778/3157794.3157797
12. Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. In *Advances in Neural Information Processing Systems* (Vol. 30, pp. 4765--4774).
13. Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance*, 66(1), 35--65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
14. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5--32. https://doi.org/10.1023/A:1010933404324
15. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785--794). https://doi.org/10.1145/2939672.2939785
16. Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303--1313. https://doi.org/10.1080/01621459.1994.10476870
17. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological)*, 57(1), 289--300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
18. Glasserman, P., & Lin, C. (2024). Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis. *The Journal of Financial Data Science*, 6(1), 25--42. https://doi.org/10.3905/jfds.2023.1.143
19. Artstein, R., & Poesio, M. (2008). Inter-Coder Agreement for Computational Linguistics. *Computational Linguistics*, 34(4), 555--596. https://doi.org/10.1162/coli.07-034-r2
20. Phuoc, T., Anh, P. T. K., Tam, P. H., & Nguyen, C. V. (2024). Applying machine learning algorithms to predict the stock price trend in the stock market -- The case of Vietnam. *Humanities and Social Sciences Communications*, 11, Article 498. https://doi.org/10.1057/s41599-024-02807-x
21. Tran, K. L., Le, H. A., Lieu, C. P., & Nguyen, D. T. (2023). Machine Learning to Forecast Financial Bubbles in Stock Markets: Evidence from Vietnam. *International Journal of Financial Studies*, 11(4), Article 133. https://doi.org/10.3390/ijfs11040133
22. Dang, N. H., Vu, T. T. V., & Dao, T. N. L. (2022). Accounting information and stock returns in Vietnam securities market: Machine learning approach. *Contabilidad y Negocios*, 17(33), 94--118. https://doi.org/10.18800/contabilidad.202201.004
23. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. In *Advances in Neural Information Processing Systems* (Vol. 30). https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html
