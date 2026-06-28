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

\noindent \underline{Tên đề tài:} \parbox[t]{0.78\textwidth}{\justifying Ứng dụng Machine Learning trong dự báo xu hướng giá cổ phiếu dựa trên đặc trưng kỹ thuật và tần suất từ khóa trong tin tức tài chính tiếng Việt}

\vspace{0.8cm}

\noindent \underline{Ngành:} Khoa học Dữ liệu

\vspace{0.5cm}

\noindent \underline{Mã số ngành:} 8460108

\vspace{3cm}

\begin{center}
\underline{Xác nhận của giảng viên hướng dẫn}\\
\textit{(Ký tên và ghi rõ họ tên)}

\vspace{2.5cm}

\underline{Họ tên:} .......................................

\vspace{\fill}

TP. HCM, tháng 05 năm 2026

\end{center}
\end{titlepage}

\begin{center}
{\large \textbf{NỘI DUNG CHÍNH CỦA NGHIÊN CỨU}}
\end{center}

\vspace{0.5cm}

# 1. Giới thiệu tổng quan

## 1.1. Bối cảnh nghiên cứu

Thị trường chứng khoán Việt Nam trong những năm gần đây có sự phát triển mạnh mẽ về quy mô vốn hóa, số lượng doanh nghiệp niêm yết và mức độ tham gia của nhà đầu tư cá nhân cũng như tổ chức. Giá cổ phiếu chịu tác động đồng thời bởi nhiều yếu tố như kết quả kinh doanh của doanh nghiệp, diễn biến ngành, tình hình kinh tế vĩ mô, thanh khoản thị trường, tâm lý nhà đầu tư và thông tin từ truyền thông tài chính.

Trong các nghiên cứu và ứng dụng dự báo giá cổ phiếu, dữ liệu giao dịch như giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch thường được sử dụng để xây dựng các đặc trưng kỹ thuật. Các đặc trưng này phản ánh hành vi giá trong quá khứ và được sử dụng phổ biến trong phân tích kỹ thuật. Tuy nhiên, bên cạnh dữ liệu giá và khối lượng, tin tức tài chính cũng là một nguồn dữ liệu quan trọng, phản ánh các sự kiện liên quan đến doanh nghiệp, ngành nghề và thị trường.

Đối với thị trường chứng khoán Việt Nam, tin tức tài chính tiếng Việt ngày càng phong phú, bao gồm các thông tin về kết quả kinh doanh, lợi nhuận, doanh thu, cổ tức, phát hành cổ phiếu, đầu tư dự án, nợ vay, rủi ro pháp lý và các sự kiện doanh nghiệp khác. Sự xuất hiện lặp lại của một số từ khóa hoặc cụm từ khóa trong tin tức có thể phản ánh mức độ quan tâm của thị trường đối với một doanh nghiệp hoặc một vấn đề cụ thể. Do đó, việc lượng hóa tần suất xuất hiện của các từ khóa tài chính trong tin tức có thể bổ sung thêm một nhóm đặc trưng hữu ích cho bài toán dự báo xu hướng giá cổ phiếu.

Khác với hướng tiếp cận phân tích cảm xúc, đề tài này không tập trung vào việc xác định sắc thái tích cực, tiêu cực hay trung tính của bài viết. Thay vào đó, đề tài xem xét sự xuất hiện và tần suất lặp lại của các từ khóa/cụm từ khóa tài chính như một dạng đặc trưng văn bản định lượng. Các đặc trưng này sẽ được kết hợp với đặc trưng kỹ thuật để xây dựng mô hình Machine Learning dự báo xu hướng giá cổ phiếu trong kỳ tiếp theo.

## 1.2. Tổng quan nghiên cứu trong và ngoài nước

### 1.2.1. Nghiên cứu quốc tế

Trên thế giới, dự báo xu hướng giá cổ phiếu bằng Machine Learning là một hướng nghiên cứu đã được quan tâm trong nhiều năm. Các nghiên cứu thường sử dụng dữ liệu giá, khối lượng giao dịch và các chỉ báo kỹ thuật như đường trung bình động, RSI, MACD, Bollinger Bands và độ biến động để xây dựng mô hình dự báo.

Bên cạnh dữ liệu thị trường, nhiều nghiên cứu quốc tế cũng khai thác dữ liệu văn bản như tin tức tài chính, thông cáo báo chí, báo cáo doanh nghiệp hoặc dữ liệu mạng xã hội để hỗ trợ dự báo thị trường. Các hướng tiếp cận phổ biến bao gồm phân tích cảm xúc, trích xuất sự kiện, biểu diễn văn bản bằng TF-IDF, word embedding hoặc mô hình ngôn ngữ tiền huấn luyện.

Một số nghiên cứu cho thấy dữ liệu văn bản có thể bổ sung thông tin cho dữ liệu giá, đặc biệt trong các trường hợp tin tức phản ánh những thay đổi về hoạt động kinh doanh, kỳ vọng của thị trường hoặc sự kiện bất thường liên quan đến doanh nghiệp. Tuy nhiên, việc khai thác dữ liệu văn bản trong tài chính vẫn cần được thiết kế cẩn trọng để tránh rò rỉ dữ liệu, nhiễu thông tin và overfitting.

### 1.2.2. Nghiên cứu trong nước

Tại Việt Nam, các nghiên cứu về dự báo giá cổ phiếu bằng Machine Learning đã bắt đầu phát triển, trong đó nhiều nghiên cứu tập trung vào dữ liệu giá và khối lượng giao dịch. Một số nghiên cứu khác khai thác dữ liệu văn bản tiếng Việt, đặc biệt trong các bài toán phân tích cảm xúc tài chính hoặc đánh giá tác động của tin tức đến phản ứng thị trường.

Tuy nhiên, các nghiên cứu kết hợp đồng thời đặc trưng kỹ thuật và đặc trưng văn bản từ tin tức tài chính tiếng Việt cho bài toán dự báo xu hướng giá cổ phiếu vẫn còn hạn chế. Đặc biệt, hướng tiếp cận dựa trên tần suất từ khóa tài chính như một đặc trưng định lượng độc lập — thay vì chỉ dựa vào phân tích cảm xúc — vẫn là một hướng có tiềm năng khai thác tại thị trường Việt Nam.

## 1.3. Khoảng trống nghiên cứu

Từ tổng quan trên, có thể xác định một số khoảng trống nghiên cứu như sau:

- Nhiều nghiên cứu dự báo giá cổ phiếu tại Việt Nam chủ yếu sử dụng dữ liệu giá và khối lượng, trong khi dữ liệu tin tức tài chính tiếng Việt chưa được khai thác đầy đủ trong mô hình dự báo.
- Các nghiên cứu về văn bản tài chính thường tập trung vào phân tích cảm xúc, trong khi tần suất xuất hiện của các từ khóa/cụm từ khóa tài chính như một dạng đặc trưng định lượng chưa được nghiên cứu sâu.
- Chưa có nhiều nghiên cứu đánh giá rõ ràng mức độ đóng góp của từng từ khóa/cụm từ khóa tài chính đối với dự báo xu hướng giá cổ phiếu tại Việt Nam.
- Việc kết hợp đặc trưng kỹ thuật, đặc trưng tần suất từ khóa và các phương pháp giải thích mô hình như SHAP hoặc permutation importance có thể giúp làm rõ hơn vai trò của dữ liệu văn bản trong bài toán dự báo tài chính, nhưng hướng này còn chưa được khai thác tại thị trường Việt Nam.

---

# 2. Mục đích và ý nghĩa nghiên cứu

## 2.1. Tính cấp thiết

Trong bối cảnh lượng thông tin tài chính tiếng Việt ngày càng lớn, nhà đầu tư và nhà phân tích phải xử lý nhiều nguồn tin liên quan đến doanh nghiệp và thị trường. Các tin tức này thường chứa nhiều từ khóa tài chính quan trọng như lợi nhuận, doanh thu, cổ tức, nợ vay, phát hành cổ phiếu, dự án, rủi ro hoặc xử phạt. Việc lượng hóa sự xuất hiện của các từ khóa này và kiểm định mối liên hệ của chúng với xu hướng giá cổ phiếu có ý nghĩa thực tiễn trong việc hỗ trợ phân tích thị trường.

Đồng thời, việc dự báo xu hướng giá cổ phiếu trong một khoảng thời gian đủ dài thay vì theo ngày giúp giảm nhiễu ngắn hạn và phù hợp hơn với chu kỳ công bố thông tin tài chính, báo cáo kết quả kinh doanh và các sự kiện doanh nghiệp. Đơn vị thời gian cụ thể sẽ được xác định trong giai đoạn thực nghiệm, với quý là lựa chọn ban đầu do tính phù hợp với chu kỳ tài chính doanh nghiệp. Do đó, nghiên cứu kết hợp đặc trưng kỹ thuật với đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt là cần thiết và có tính ứng dụng trong bối cảnh thị trường chứng khoán Việt Nam hiện nay.

## 2.2. Ý nghĩa lý luận

Đề tài có ý nghĩa lý luận ở các khía cạnh sau:

- Góp phần mở rộng hướng nghiên cứu dự báo xu hướng giá cổ phiếu tại Việt Nam bằng cách kết hợp dữ liệu có cấu trúc và dữ liệu văn bản.
- Đề xuất cách tiếp cận lượng hóa đặc trưng văn bản dựa trên tần suất từ khóa/cụm từ khóa tài chính, khác biệt với hướng phân tích cảm xúc truyền thống.
- Cung cấp bằng chứng thực nghiệm về việc liệu nhóm đặc trưng tần suất từ khóa có tạo ra giá trị dự báo bổ sung trong bối cảnh thị trường chứng khoán Việt Nam hay không.
- Sử dụng các phương pháp giải thích mô hình để xác định những từ khóa/cụm từ khóa có đóng góp đáng kể trong bài toán dự báo, từ đó tăng tính diễn giải của mô hình.

## 2.3. Ý nghĩa thực tiễn

Đề tài có ý nghĩa thực tiễn ở các khía cạnh sau:

- Xây dựng bộ dữ liệu kết hợp giữa dữ liệu giá cổ phiếu và dữ liệu tin tức tài chính tiếng Việt theo từng cổ phiếu và từng kỳ dự báo.
- Cung cấp phương pháp lượng hóa tần suất từ khóa tài chính trong tin tức để phục vụ phân tích định lượng.
- Hỗ trợ đánh giá xem việc bổ sung đặc trưng từ khóa từ tin tức có giúp cải thiện hiệu quả dự báo so với mô hình chỉ dùng đặc trưng kỹ thuật hay không.
- Tạo nền tảng cho việc xây dựng pipeline bán tự động nhằm thu thập dữ liệu, trích xuất đặc trưng, huấn luyện mô hình và cập nhật danh sách từ khóa quan trọng.

---

# 3. Mục tiêu nghiên cứu

## 3.1. Mục tiêu tổng quát

Mục tiêu tổng quát của đề tài là xây dựng và đánh giá mô hình Machine Learning dự báo xu hướng giá cổ phiếu trong một khoảng thời gian tới bằng cách kết hợp đặc trưng kỹ thuật từ dữ liệu giao dịch và đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt, đồng thời kiểm định xem nhóm đặc trưng văn bản có tạo ra giá trị dự báo bổ sung so với chỉ sử dụng đặc trưng kỹ thuật hay không. Đơn vị thời gian dự báo dự kiến là quý, có thể được điều chỉnh trong quá trình thực nghiệm.

## 3.2. Mục tiêu cụ thể

Đề tài hướng đến các mục tiêu cụ thể sau:

1. Xây dựng bộ dữ liệu thực nghiệm gồm dữ liệu giao dịch cổ phiếu và dữ liệu tin tức tài chính tiếng Việt được tổng hợp theo từng cổ phiếu và từng khoảng thời gian dự báo.
2. Thiết kế phương pháp xác định xu hướng tăng/giảm của cổ phiếu dựa trên sự thay đổi giá trung bình giữa các kỳ dự báo liên tiếp.
3. Trích xuất các đặc trưng kỹ thuật từ dữ liệu giá và khối lượng giao dịch.
4. Xây dựng danh sách từ khóa/cụm từ khóa tài chính và lượng hóa tần suất xuất hiện của các từ khóa này trong tin tức liên quan đến từng cổ phiếu theo từng kỳ dự báo.
5. Sử dụng các mô hình Machine Learning để dự báo xu hướng tăng/giảm của cổ phiếu trong kỳ kế tiếp.
6. So sánh hiệu quả dự báo giữa mô hình chỉ sử dụng đặc trưng kỹ thuật, mô hình chỉ sử dụng đặc trưng từ khóa và mô hình kết hợp cả hai nhóm đặc trưng.
7. Phân tích mức độ quan trọng của các từ khóa/cụm từ khóa bằng các phương pháp giải thích mô hình để xác định những tín hiệu văn bản có đóng góp lớn đối với kết quả dự báo.
8. Đề xuất pipeline bán tự động cho việc cập nhật dữ liệu, trích xuất đặc trưng, huấn luyện mô hình và đánh giá kết quả, có thể tái sử dụng khi điều chỉnh phạm vi nghiên cứu.

---

# 4. Câu hỏi nghiên cứu và giả thuyết nghiên cứu

## 4.1. Câu hỏi nghiên cứu

Đề tài tập trung trả lời các câu hỏi nghiên cứu sau:

1. Các đặc trưng kỹ thuật từ dữ liệu giá và khối lượng có khả năng dự báo xu hướng giá cổ phiếu trong kỳ tiếp theo ở mức độ nào?
2. Các đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt có cung cấp thông tin bổ sung cho bài toán dự báo xu hướng giá cổ phiếu hay không?
3. Mô hình kết hợp đặc trưng kỹ thuật và đặc trưng từ khóa có cải thiện hiệu quả dự báo so với mô hình chỉ sử dụng đặc trưng kỹ thuật hay không?
4. Những từ khóa/cụm từ khóa tài chính nào có mức đóng góp đáng kể trong việc dự báo xu hướng tăng/giảm của giá cổ phiếu?
5. Có thể xây dựng một pipeline bán tự động để cập nhật dữ liệu, trích xuất đặc trưng và đánh giá mô hình cho bài toán này hay không?

## 4.2. Giả thuyết nghiên cứu

Đề tài đề xuất các giả thuyết nghiên cứu sau:

- **H1:** Đặc trưng tần suất từ khóa từ tin tức tài chính tiếng Việt có thể cung cấp thông tin bổ sung cho mô hình dự báo xu hướng giá cổ phiếu so với mô hình chỉ sử dụng đặc trưng kỹ thuật.
- **H2:** Một số từ khóa/cụm từ khóa tài chính có thể có mối liên hệ thống kê với xu hướng tăng/giảm của giá cổ phiếu trong kỳ dự báo tiếp theo.
- **H3:** Các phương pháp giải thích mô hình có thể hỗ trợ xác định nhóm từ khóa/cụm từ khóa có mức đóng góp đáng kể trong mô hình dự báo.

Các giả thuyết trên mang tính kiểm định thực nghiệm. Đề tài không giả định trước rằng đặc trưng từ khóa chắc chắn giúp cải thiện hiệu quả dự báo. Trong trường hợp mô hình kết hợp không đạt kết quả tốt hơn mô hình chỉ sử dụng đặc trưng kỹ thuật, kết quả này vẫn có ý nghĩa nghiên cứu vì cho thấy trong phạm vi dữ liệu, phương pháp và giai đoạn khảo sát, tín hiệu từ khóa chưa tạo ra giá trị dự báo bổ sung đáng kể.

---

# 5. Đối tượng và phạm vi nghiên cứu

## 5.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu của đề tài bao gồm:

- Dữ liệu giao dịch của một nhóm cổ phiếu niêm yết trên Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE), bao gồm giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch.
- Dữ liệu tin tức tài chính tiếng Việt liên quan đến các cổ phiếu được chọn, thu thập từ các nguồn báo tài chính phù hợp.
- Mối liên hệ giữa đặc trưng kỹ thuật, đặc trưng tần suất từ khóa trong tin tức và xu hướng tăng/giảm của giá cổ phiếu trong kỳ dự báo tiếp theo.

## 5.2. Phạm vi nghiên cứu

Đề tài được giới hạn trong phạm vi sau:

| Tiêu chí | Phạm vi |
|---|---|
| Thị trường | Sở Giao dịch Chứng khoán TP. Hồ Chí Minh (HOSE) |
| Giai đoạn dữ liệu | Khoảng 3–5 năm gần đây, bao gồm các giai đoạn thị trường đa dạng; phạm vi cụ thể được xác định dựa trên tính khả dụng và độ đầy đủ của dữ liệu thực tế |
| Đối tượng cổ phiếu | Nhóm cổ phiếu phổ thông được lựa chọn theo tiêu chí vốn hóa, thanh khoản, tính liên tục niêm yết và mức độ xuất hiện trên tin tức tài chính (tiêu chí cụ thể được xác định trong giai đoạn triển khai) |
| Tần suất dữ liệu | Dữ liệu giá theo ngày, tổng hợp theo kỳ dự báo được chọn |
| Tầm dự báo | Xu hướng giá của quý kế tiếp (q+1). Quý được chọn làm đơn vị dự báo chính vì phù hợp với chu kỳ công bố báo cáo tài chính doanh nghiệp và giúp giảm nhiễu ngắn hạn. Trong quá trình thực nghiệm, đơn vị thời gian có thể được điều chỉnh nếu phân tích dữ liệu thực tế cho thấy tín hiệu tin tức suy giảm nhanh hơn hoặc chậm hơn so với chu kỳ quý. |
| Loại bài toán | Phân loại nhị phân: xu hướng tăng hoặc giảm/không tăng |
| Dữ liệu văn bản | Tin tức tài chính tiếng Việt từ các nguồn báo có chuyên mục tài chính, chứng khoán hoặc doanh nghiệp |
| Đặc trưng văn bản | Tần suất xuất hiện của từ khóa/cụm từ khóa tài chính, tần suất chuẩn hóa, TF-IDF và các biến liên quan |

Danh sách cổ phiếu cụ thể sẽ được xác định trong giai đoạn triển khai thực nghiệm dựa trên tính đầy đủ của dữ liệu giao dịch, mức độ phủ tin tức và các tiêu chí kỹ thuật khác.

## 5.3. Giới hạn của đề tài

Đề tài có các giới hạn sau:

- Không dự báo giá trị cụ thể của giá cổ phiếu, chỉ dự báo xu hướng tăng/giảm trong kỳ tiếp theo.
- Không xây dựng hệ thống khuyến nghị đầu tư hoặc hệ thống giao dịch tự động.
- Không tập trung vào phân tích cảm xúc tích cực/tiêu cực của tin tức.
- Không xây dựng mô hình ngôn ngữ mới từ đầu.
- Không sử dụng dữ liệu giao dịch trong ngày.
- Không xem xét các biến vĩ mô như lãi suất, tỷ giá, GDP hoặc lạm phát như biến đầu vào độc lập.
- Đề tài có thể chịu ảnh hưởng nhẹ từ survivorship bias do chỉ lựa chọn cổ phiếu có dữ liệu liên tục trong giai đoạn nghiên cứu. Hạn chế này sẽ được ghi nhận khi phân tích kết quả.
- Pipeline đề xuất trong đề tài là công cụ hỗ trợ nghiên cứu, không phải hệ thống production hoàn chỉnh.
- Đề tài không đặt mục tiêu chứng minh chắc chắn rằng tần suất từ khóa luôn có khả năng dự báo xu hướng giá cổ phiếu. Thay vào đó, đề tài tập trung kiểm định xem nhóm đặc trưng này có tạo ra giá trị bổ sung so với đặc trưng kỹ thuật hay không trong phạm vi dữ liệu và giai đoạn nghiên cứu.

---

# 6. Phương pháp nghiên cứu

## 6.1. Thiết kế tổng quát

Quy trình nghiên cứu được thiết kế theo các bước chính sau:

1. Lựa chọn nhóm cổ phiếu nghiên cứu theo tiêu chí đã xác định.
2. Thu thập dữ liệu giá và khối lượng giao dịch theo ngày.
3. Thu thập tin tức tài chính tiếng Việt từ các nguồn báo được lựa chọn.
4. Gắn bài viết với cổ phiếu tương ứng dựa trên mã cổ phiếu, tên doanh nghiệp và các quy tắc lọc phù hợp.
5. Tổng hợp dữ liệu theo từng cổ phiếu và từng kỳ dự báo.
6. Xây dựng nhãn tăng/giảm dựa trên giá trung bình kỳ sau so với kỳ hiện tại.
7. Trích xuất đặc trưng kỹ thuật từ dữ liệu giao dịch.
8. Trích xuất đặc trưng tần suất từ khóa từ dữ liệu tin tức.
9. Huấn luyện và đánh giá các mô hình Machine Learning.
10. Phân tích feature importance để xác định các đặc trưng và từ khóa quan trọng.
11. Đề xuất pipeline bán tự động phục vụ cập nhật và tái huấn luyện mô hình.

## 6.2. Lựa chọn cổ phiếu nghiên cứu

Nhóm cổ phiếu nghiên cứu được lựa chọn từ các cổ phiếu phổ thông niêm yết trên HOSE theo các nguyên tắc sau:

- **Vốn hóa và thanh khoản:** Ưu tiên các cổ phiếu có vốn hóa lớn và thanh khoản ổn định, nhằm đảm bảo dữ liệu giao dịch đầy đủ và các đặc trưng kỹ thuật có ý nghĩa.
- **Tính liên tục niêm yết:** Cổ phiếu cần có dữ liệu giao dịch liên tục trong toàn bộ giai đoạn nghiên cứu và không thuộc diện cảnh báo hoặc kiểm soát kéo dài.
- **Mức độ phủ tin tức:** Cổ phiếu cần có lượng tin tức tài chính đủ lớn để trích xuất đặc trưng từ khóa có ý nghĩa thống kê. Tiêu chí cụ thể về ngưỡng số bài tối thiểu sẽ được xác định sau khi thu thập dữ liệu thực tế.
- **Loại cổ phiếu:** Chỉ bao gồm cổ phiếu phổ thông, loại trừ chứng quyền có bảo đảm, chứng chỉ quỹ ETF và các công cụ phái sinh.

Danh sách cổ phiếu cuối cùng sẽ được xác định trong giai đoạn triển khai thực nghiệm sau khi kiểm tra tính đầy đủ của dữ liệu.

## 6.3. Xác định biến mục tiêu

Đề tài dự báo xu hướng giá cổ phiếu trong một kỳ dự báo xác định, dự kiến là quý. Với mỗi cổ phiếu i tại kỳ q, giá đại diện được tính bằng trung bình giá đóng cửa trong kỳ đó.

Ký hiệu:
- AvgPrice(i, q): giá đóng cửa trung bình của cổ phiếu i trong kỳ q.
- AvgPrice(i, q+1): giá đóng cửa trung bình của cổ phiếu i trong kỳ kế tiếp.

Nhãn dự báo được xác định như sau:
- Nếu AvgPrice(i, q+1) > AvgPrice(i, q): gán nhãn **tăng**.
- Nếu AvgPrice(i, q+1) ≤ AvgPrice(i, q): gán nhãn **giảm/không tăng**.

Trong quá trình triển khai, đề tài có thể xem xét thêm ngưỡng biến động tối thiểu để lọc các trường hợp biến động gần bằng không. Đồng thời, đơn vị kỳ dự báo (quý, tháng hoặc cửa sổ thời gian cố định) có thể được điều chỉnh dựa trên phân tích dữ liệu thực tế. Các phương án cụ thể sẽ được quyết định trong giai đoạn thực nghiệm.

## 6.4. Thu thập và xử lý dữ liệu giao dịch

Dữ liệu giao dịch theo ngày bao gồm: giá mở cửa, giá đóng cửa, giá cao nhất, giá thấp nhất và khối lượng giao dịch. Dữ liệu được thu thập thông qua các thư viện và API công khai phù hợp với thị trường Việt Nam (ví dụ: vnstock hoặc các nguồn tương đương).

Từ dữ liệu này, đề tài sẽ tính toán và tổng hợp các đặc trưng kỹ thuật theo từng kỳ dự báo. Các nhóm đặc trưng dự kiến bao gồm:

| Nhóm đặc trưng | Đặc trưng cụ thể |
|---|---|
| Lợi suất | Lợi suất trung bình, lợi suất tích lũy trong kỳ |
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

1. Làm sạch và chuẩn hóa văn bản (chữ hoa/thường, ký tự đặc biệt).
2. Tách từ tiếng Việt bằng công cụ xử lý ngôn ngữ tự nhiên phù hợp.
3. Loại bỏ từ dừng và bài viết trùng lặp.
4. Gắn bài viết với mã cổ phiếu tương ứng dựa trên tên doanh nghiệp và các quy tắc nhận diện thực thể.
5. Tổng hợp văn bản theo từng cổ phiếu và từng kỳ dự báo.

## 6.6. Đặc trưng tần suất từ khóa từ tin tức tài chính

Đặc trưng văn bản trong đề tài phản ánh sự xuất hiện và tần suất lặp lại của các từ khóa/cụm từ khóa tài chính trong tin tức, không tập trung vào sắc thái cảm xúc của bài viết.

Danh sách từ khóa ban đầu được xây dựng dựa trên kiến thức tài chính và kết hợp phân tích thống kê từ corpus tin tức thực tế (ví dụ: trích xuất các token phổ biến có ý nghĩa tài chính rõ ràng). Các nhóm từ khóa dự kiến bao gồm chủ đề về kết quả kinh doanh, chính sách cổ đông, tài chính doanh nghiệp, hoạt động kinh doanh, rủi ro và thị trường ngành.

Các nhóm đặc trưng từ khóa dự kiến bao gồm:

| Nhóm đặc trưng | Mô tả |
|---|---|
| Tần suất từ khóa | Số lần xuất hiện của từng từ khóa/cụm từ khóa trong tin tức của một cổ phiếu trong một kỳ dự báo |
| Tần suất chuẩn hóa | Tần suất từ khóa chia cho tổng số bài viết hoặc tổng số từ trong kỳ |
| TF-IDF | Trọng số từ khóa phản ánh mức độ đặc trưng trong từng cổ phiếu - kỳ dự báo |
| N-gram | Cụm 2–3 từ có ý nghĩa tài chính như "lợi nhuận tăng", "phát hành cổ phiếu", "nợ vay" |
| Mức độ phủ tin tức | Số lượng bài viết liên quan đến cổ phiếu trong kỳ |

Sau khi huấn luyện mô hình, đề tài sẽ sử dụng các phương pháp giải thích mô hình để đánh giá và sàng lọc từ khóa dựa trên mức đóng góp thực nghiệm.

## 6.7. Xây dựng mô hình Machine Learning

Đề tài xây dựng các mô hình phân loại nhị phân xu hướng giá cổ phiếu trong kỳ tiếp theo. Các thuật toán dự kiến bao gồm Logistic Regression, Random Forest, XGBoost/LightGBM và Support Vector Machine. Lựa chọn mô hình và cấu hình thực nghiệm cuối cùng có thể điều chỉnh dựa trên đặc điểm dữ liệu thực tế.

Các mô hình được huấn luyện trên ba cấu hình đặc trưng để phục vụ so sánh:

| Cấu hình | Đặc trưng sử dụng |
|---|---|
| A | Chỉ sử dụng đặc trưng kỹ thuật |
| B | Chỉ sử dụng đặc trưng tần suất từ khóa |
| C | Kết hợp đặc trưng kỹ thuật và đặc trưng tần suất từ khóa |

Ngoài ra, đề tài sử dụng các baseline đơn giản để tham chiếu, bao gồm: majority class baseline (luôn dự báo lớp phổ biến nhất) và naive momentum baseline (dự báo xu hướng kỳ sau dựa trên xu hướng kỳ hiện tại).

## 6.8. Đánh giá mô hình

Do dữ liệu có tính thời gian và cấu trúc dạng panel (nhiều cổ phiếu × nhiều kỳ dự báo), việc chia tập huấn luyện và kiểm định áp dụng nguyên tắc: toàn bộ quan sát trước một mốc thời gian T được dùng để huấn luyện, các quan sát từ T trở đi được dùng để kiểm định — áp dụng nhất quán cho toàn bộ cổ phiếu trong mẫu. Cách chia cụ thể sẽ được xác định dựa trên quy mô dữ liệu thực tế.

Trọng tâm của phần đánh giá là so sánh chênh lệch hiệu quả giữa ba cấu hình đặc trưng A, B và C nhằm kiểm định giá trị bổ sung của đặc trưng từ khóa.

Các chỉ số đánh giá dự kiến: Accuracy, Precision, Recall, F1-score, AUC-ROC và Balanced Accuracy (trong trường hợp dữ liệu mất cân bằng nhãn). Khi mất cân bằng nhãn xảy ra, đề tài sẽ áp dụng các kỹ thuật xử lý phù hợp như điều chỉnh trọng số lớp hoặc hiệu chỉnh ngưỡng phân loại.

Bên cạnh đó, đề tài phân tích khả năng diễn giải mô hình thông qua: hệ số Logistic Regression, feature importance của mô hình cây, permutation importance và SHAP. Nếu đặc trưng từ khóa không cải thiện hiệu quả dự báo, đề tài sẽ phân tích các nguyên nhân có thể như dữ liệu tin tức không đủ dày, từ khóa chưa có tính phân biệt, hoặc biến động giá chịu ảnh hưởng mạnh bởi các yếu tố ngoài phạm vi nghiên cứu.

## 6.9. Kiểm soát rò rỉ dữ liệu

Để tránh rò rỉ dữ liệu, đề tài áp dụng các nguyên tắc sau:

- Chỉ sử dụng dữ liệu tin tức và dữ liệu giá đã có tại thời điểm dự báo.
- Dữ liệu của kỳ q được sử dụng để dự báo xu hướng của kỳ q+1; không sử dụng bất kỳ thông tin nào từ kỳ q+1 khi xây dựng đặc trưng cho kỳ q. Nguyên tắc này được áp dụng nhất quán bất kể đơn vị kỳ dự báo là quý, tháng hay cửa sổ thời gian cố định.
- Các bước chuẩn hóa, chọn đặc trưng và huấn luyện mô hình phải được thực hiện hoàn toàn trong phạm vi tập huấn luyện trước khi áp dụng lên tập kiểm định.

## 6.10. Pipeline bán tự động đề xuất

Đề tài hướng đến việc xây dựng pipeline bán tự động phục vụ nghiên cứu, bao gồm các bước: cập nhật dữ liệu giá, thu thập và gắn tin tức với cổ phiếu, tiền xử lý văn bản, trích xuất đặc trưng, huấn luyện và đánh giá mô hình, xuất kết quả và danh sách từ khóa quan trọng.

Pipeline này không nhằm xây dựng một hệ thống giao dịch tự động, mà nhằm hỗ trợ quá trình nghiên cứu, tái lập thực nghiệm và mở rộng phân tích trong tương lai.

---

# 7. Công cụ và thư viện dự kiến

| Nhóm | Công cụ / Thư viện | Mục đích |
|---|---|---|
| Ngôn ngữ lập trình | Python | Ngôn ngữ lập trình chính |
| Xử lý dữ liệu | Pandas, NumPy | Xử lý và tổng hợp dữ liệu |
| Dữ liệu thị trường | vnstock hoặc nguồn dữ liệu tương đương | Thu thập dữ liệu giá cổ phiếu |
| Thu thập tin tức | BeautifulSoup, Scrapy hoặc công cụ tương đương | Thu thập dữ liệu bài viết |
| Xử lý tiếng Việt | underthesea, VnCoreNLP hoặc công cụ phù hợp | Tách từ, chuẩn hóa văn bản |
| Đặc trưng văn bản | scikit-learn (TF-IDF, CountVectorizer) | Trích xuất đặc trưng từ khóa |
| Machine Learning | scikit-learn, XGBoost, LightGBM | Xây dựng và đánh giá mô hình |
| Giải thích mô hình | SHAP, permutation importance | Phân tích vai trò của đặc trưng |
| Trực quan hóa | Matplotlib, Seaborn, Plotly | Trực quan hóa kết quả |

Danh sách công cụ có thể được điều chỉnh trong quá trình triển khai tùy theo đặc điểm dữ liệu thực tế.

---

# 8. Kết quả dự kiến

Đề tài dự kiến đạt được các kết quả sau:

1. Bộ dữ liệu thực nghiệm kết hợp dữ liệu giao dịch cổ phiếu và dữ liệu tin tức tài chính tiếng Việt, được tổng hợp theo từng cổ phiếu và từng kỳ dự báo.
2. Phương pháp xác định nhãn tăng/giảm dựa trên sự thay đổi giá trung bình giữa hai kỳ liên tiếp.
3. Bộ đặc trưng kỹ thuật và bộ đặc trưng tần suất từ khóa phục vụ mô hình dự báo.
4. Kết quả so sánh hiệu quả giữa các mô hình Machine Learning và các cấu hình đặc trưng A, B, C.
5. Danh sách các từ khóa/cụm từ khóa có mức đóng góp cao trong dự báo xu hướng giá cổ phiếu theo phân tích feature importance.
6. Phân tích thực nghiệm về việc đặc trưng từ khóa có giúp cải thiện mô hình dự báo so với chỉ sử dụng đặc trưng kỹ thuật hay không. Trong trường hợp đặc trưng từ khóa không cải thiện kết quả, đề tài vẫn ghi nhận đây là kết quả nghiên cứu hợp lệ và phân tích các nguyên nhân có thể.
7. Pipeline bán tự động phục vụ thu thập dữ liệu, trích xuất đặc trưng, huấn luyện mô hình và đánh giá kết quả.

---

# 9. Đóng góp dự kiến của đề tài

Đề tài dự kiến có các đóng góp chính sau:

- Đề xuất cách tiếp cận dự báo xu hướng giá cổ phiếu bằng cách kết hợp dữ liệu giá và dữ liệu tin tức tài chính tiếng Việt, áp dụng cho thị trường chứng khoán Việt Nam.
- Xây dựng phương pháp lượng hóa đặc trưng văn bản dựa trên tần suất từ khóa/cụm từ khóa tài chính thay vì tập trung vào phân tích cảm xúc.
- Cung cấp bằng chứng thực nghiệm nhằm kiểm định liệu dữ liệu tin tức, dưới dạng đặc trưng tần suất từ khóa, có mang lại giá trị bổ sung trong bài toán dự báo xu hướng giá cổ phiếu tại Việt Nam hay không.
- Sử dụng các phương pháp giải thích mô hình để xác định từ khóa/cụm từ khóa có liên hệ đáng kể với xu hướng giá cổ phiếu, tăng tính diễn giải của mô hình.
- Xây dựng pipeline bán tự động có thể tái sử dụng cho các nghiên cứu mở rộng.

---

# 10. Thời gian thực hiện dự kiến

| Giai đoạn | Nội dung công việc | Thời gian dự kiến |
|---|---|---|
| 1 | Nghiên cứu tổng quan, hoàn thiện đề cương, xác định phạm vi cổ phiếu và nguồn dữ liệu | Tháng 4 |
| 2 | Thu thập dữ liệu giá cổ phiếu và dữ liệu tin tức tài chính tiếng Việt | Tháng 4 - 5 |
| 3 | Tiền xử lý dữ liệu, gắn tin tức với cổ phiếu, tổng hợp dữ liệu theo kỳ dự báo | Tháng 5 - 6 |
| 4 | Trích xuất đặc trưng kỹ thuật và đặc trưng tần suất từ khóa | Tháng 6 |
| 5 | Xây dựng, huấn luyện và đánh giá mô hình Machine Learning | Tháng 6 - 7 |
| 6 | Phân tích feature importance, xác định từ khóa quan trọng, đánh giá kết quả | Tháng 7 - 8 |
| 7 | Viết luận văn, chỉnh sửa và hoàn thiện | Tháng 8 - 9 |
| 8 | Chuẩn bị bảo vệ luận văn | Tháng 9 - 10 |

---

# 11. Nơi thực hiện đề tài

Trường Đại học Khoa học Tự nhiên - Đại học Quốc gia Thành phố Hồ Chí Minh.

---

# 12. Tài liệu tham khảo dự kiến

1. Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. *Journal of Computational Science*, 2(1), 1–8.
2. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794.
3. Ding, X., Zhang, Y., Liu, T., & Duan, J. (2015). Deep learning for event-driven stock prediction. *Proceedings of the 24th International Joint Conference on Artificial Intelligence*, 2327–2333.
4. Li, X., Xie, H., Chen, L., Wang, J., & Deng, X. (2014). News impact on stock price return via sentiment analysis. *Knowledge-Based Systems*, 69, 14–23.
5. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30, 4765–4774.
6. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. New York Institute of Finance.
7. Nassirtoussi, A. K., Aghabozorgi, S., Wah, T. Y., & Ngo, D. C. L. (2014). Text mining for market prediction: A systematic review. *Expert Systems with Applications*, 41(16), 7653–7670.
8. Nguyen, D. Q., & Nguyen, A. T. (2020). PhoBERT: Pre-trained language models for Vietnamese. *Findings of the Association for Computational Linguistics: EMNLP 2020*, 1037–1042.
9. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
10. Schumaker, R. P., & Chen, H. (2009). Textual analysis of stock market prediction using breaking financial news. *ACM Transactions on Information Systems*, 27(2), 1–19.
11. Vu, L., Pham, T., Kieu, D., & Pham, H. (2023). Sentiments extracted from news and stock market reactions in Vietnam. *International Journal of Financial Studies*, 11(3), 101.
12. Xu, Y., & Cohen, S. B. (2018). Stock movement prediction from tweets and historical prices. *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics*, 1970–1979.
