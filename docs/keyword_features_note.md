# Ghi chú keyword features đang dùng trong mô hình

## Mục đích file

File này ghi lại danh sách keyword đang dùng để tạo `keyword_features.csv`, các nhóm keyword, cách sinh feature và các điểm yếu cần nêu trong luận văn.

Nguồn chính:

- `config/keywords_finance.json`
- `config/keywords_by_group.json`
- `data/features/keyword_features.csv`
- `pipeline/task8_keywords.py`
- `pipeline/task9_kw_features.py`

Lưu ý: `config/keyword_candidates.csv` chỉ là danh sách candidate theo tần suất corpus để tham khảo/manual review, không phải danh sách curated chính đưa vào mô hình.

---

## 1. Tổng quan keyword set

Danh sách curated hiện có **106 keyword/cụm từ**, chia thành:

| Nhóm sentiment | Số lượng | Vai trò |
|---|---:|---|
| Positive | 43 | Tín hiệu tích cực về kết quả kinh doanh, cổ tức, tài chính, hoạt động |
| Negative | 54 | Tín hiệu tiêu cực về kết quả kinh doanh, nợ, thanh khoản, pháp lý, hoạt động |
| Neutral | 9 | Sự kiện doanh nghiệp trung tính hoặc chưa rõ chiều tác động |

Các keyword được gom theo 6 nhóm chủ đề:

| Mã nhóm | Tên nhóm | Ý nghĩa |
|---|---|---|
| A | Kết quả kinh doanh | Lợi nhuận, doanh thu, tăng trưởng, lãi/lỗ |
| B | Chính sách cổ đông | Cổ tức, phát hành, mua lại cổ phiếu |
| C | Tài chính doanh nghiệp | Nợ, thanh khoản, dòng tiền, an toàn vốn |
| D | Hoạt động kinh doanh | Hợp đồng, dự án, mở rộng, thu hẹp hoạt động |
| E | Rủi ro và pháp lý | Phạt, thanh tra, kiện tụng, điều tra, cảnh báo |
| F | Sự kiện doanh nghiệp trung tính | ĐHĐCĐ, HĐQT, lãnh đạo, sáp nhập, niêm yết |

---

## 2. Danh sách keyword positive

### A. Kết quả kinh doanh

- lợi nhuận tăng
- doanh thu tăng
- tăng trưởng mạnh
- vượt kế hoạch
- kỷ lục
- tăng trưởng
- lãi ròng
- lợi nhuận sau thuế tăng
- kết quả tích cực
- lãi khủng
- lãi lớn
- lãi đậm
- báo lãi
- lợi nhuận kỷ lục
- doanh thu kỷ lục
- lãi kỷ lục
- bứt phá
- tăng vọt
- tăng mạnh
- khởi sắc
- phục hồi
- lập đỉnh
- hoàn thành kế hoạch
- lợi nhuận cải thiện

### B. Chính sách cổ đông

- chia cổ tức
- cổ tức cao
- mua lại cổ phiếu
- phát hành thưởng
- tăng vốn điều lệ
- cổ tức tiền mặt

### C. Tài chính doanh nghiệp

- giảm nợ
- trả nợ
- cải thiện tài chính
- hệ số an toàn vốn
- dòng tiền dương
- tiền mặt dồi dào

### D. Hoạt động kinh doanh

- ký kết hợp đồng
- mở rộng thị trường
- dự án mới
- đầu tư mới
- hợp tác chiến lược
- thắng thầu
- xuất khẩu tăng

---

## 3. Danh sách keyword negative

### A. Kết quả kinh doanh

- lợi nhuận giảm
- doanh thu giảm
- lợi nhuận âm
- thua lỗ
- lỗ ròng
- dưới kế hoạch
- sụt giảm
- kết quả tiêu cực
- lợi nhuận thấp hơn
- báo lỗ
- lỗ nặng
- lỗ lớn
- lỗ kỷ lục
- lỗ lũy kế
- lao dốc
- giảm sâu
- giảm mạnh
- tụt dốc
- kinh doanh sa sút
- âm vốn chủ sở hữu
- lợi nhuận không tăng
- doanh thu không tăng
- không tăng trưởng
- tăng trưởng chậm lại
- không hoàn thành kế hoạch
- không đạt kế hoạch
- chưa có lãi

### B. Chính sách cổ đông

- không chia cổ tức
- hủy cổ tức
- giảm cổ tức
- phát hành pha loãng
- chào bán giá thấp

### C. Tài chính doanh nghiệp

- nợ xấu
- nợ vay tăng
- áp lực tài chính
- nợ quá hạn
- hệ số nợ cao
- thiếu thanh khoản
- dòng tiền âm

### D. Hoạt động kinh doanh

- hủy hợp đồng
- dự án trì hoãn
- thu hẹp hoạt động
- đóng cửa
- dừng dự án

### E. Rủi ro và pháp lý

- bị phạt
- vi phạm
- bị thanh tra
- bị kiểm toán từ chối
- cảnh báo
- đình chỉ
- khởi tố
- điều tra
- tranh chấp pháp lý
- bị kiện

---

## 4. Danh sách keyword neutral

### F. Sự kiện doanh nghiệp trung tính

- đại hội cổ đông
- họp HĐQT
- thay đổi lãnh đạo
- thay CEO
- sáp nhập
- mua lại
- phát hành cổ phiếu mới
- niêm yết thêm
- thoái vốn

---

## 5. Feature được sinh từ keyword

Trong `data/features/keyword_features.csv`, mỗi keyword sinh 3 nhóm feature:

### 5.1. Raw count

Dạng cột:

- `kw_lợi nhuận tăng`
- `kw_doanh thu tăng`
- `kw_nợ xấu`
- `kw_bị kiện`

Ý nghĩa: số lần keyword xuất hiện trong tin tức của một `ticker` và `quarter_id`.

### 5.2. Normalized count

Dạng cột:

- `kw_norm_lợi nhuận tăng`
- `kw_norm_nợ xấu`

Ý nghĩa: raw count chuẩn hóa theo `news_count`, giúp giảm bias do mã có nhiều tin hơn.

### 5.3. TF-IDF-like feature

Dạng cột:

- `tfidf_lợi nhuận tăng`
- `tfidf_nợ xấu`

Ý nghĩa: trọng số keyword theo mức xuất hiện và độ hiếm tương đối.

### 5.4. Feature tổng hợp

- `news_count`
- `pos_score`
- `neg_score`
- `sentiment_ratio`
- `news_count_log`
- `has_min_news`

---

## 6. Điểm yếu của keyword features

### 6.1. Keyword thiếu ngữ cảnh

Keyword count không hiểu bối cảnh câu. Ví dụ:

- `nợ xấu` có thể là rủi ro mới, cũng có thể là tin đã xử lý nợ xấu.
- `chia cổ tức` thường tích cực, nhưng nếu cổ tức thấp hơn kỳ vọng thì có thể tiêu cực.
- `tăng vốn điều lệ` có thể tích cực nếu phục vụ mở rộng, nhưng cũng có thể gây pha loãng.
- `mua lại` có thể là mua lại cổ phiếu, mua lại doanh nghiệp, hoặc chỉ là cụm từ trong ngữ cảnh khác.

### 6.2. Không phân biệt phủ định và đảo chiều nghĩa đầy đủ

Dù list có vài cụm phủ định như:

- `không tăng trưởng`
- `không đạt kế hoạch`
- `không chia cổ tức`
- `lợi nhuận không tăng`

Keyword count vẫn khó xử lý các cấu trúc phức tạp như:

- “không còn nợ xấu đáng kể”
- “giảm áp lực tài chính”
- “không bị ảnh hưởng bởi tranh chấp pháp lý”
- “lỗ giảm mạnh so với cùng kỳ”

### 6.3. Không đo materiality

Keyword xuất hiện không đồng nghĩa tin đó quan trọng với giá cổ phiếu.

Ví dụ:

- `đại hội cổ đông` có thể là sự kiện thường niên không có tác động.
- `thay đổi lãnh đạo` có thể quan trọng hoặc chỉ là bổ nhiệm cấp thấp.
- `dự án mới` có thể nhỏ, chưa đủ material.
- `vi phạm` có thể là vi phạm nhỏ, không ảnh hưởng tài chính.

### 6.4. Không đo relevance với ticker

Tin có thể nhắc ticker nhưng không thật sự liên quan chính. Keyword count có thể bị nhiễu bởi:

- bài tổng hợp nhiều mã;
- bài thị trường chung;
- sidebar/footer/menu;
- tin ngành có nhiều ticker;
- nội dung liên quan công ty con/công ty cùng tên;
- ticker matching confidence thấp hoặc `mixed`.

### 6.5. Không phân biệt thời điểm và decay

Feature hiện được tổng hợp theo kỳ. Điều này làm mất timing:

- tin đầu quý và cuối quý được tính gần như nhau;
- tin vừa xảy ra có thể quan trọng hơn tin cũ;
- legal risk có tác động dài hơn earnings surprise;
- một tin rất material có thể bị pha loãng bởi nhiều tin nhỏ.

### 6.6. Không phân biệt direction theo điều kiện doanh nghiệp

Cùng một keyword có thể tác động khác nhau tùy doanh nghiệp/ngành/trạng thái thị trường.

Ví dụ:

- `nợ vay tăng` có thể tiêu cực với doanh nghiệp yếu, nhưng trung tính/tích cực nếu vay để mở rộng dự án sinh lời.
- `tăng vốn điều lệ` có thể tích cực với ngân hàng cần CAR, nhưng tiêu cực nếu pha loãng cổ đông.
- `giảm cổ tức` có thể tiêu cực, nhưng cũng có thể hợp lý nếu công ty giữ tiền cho dự án sinh lời cao.

### 6.7. Keyword list nhỏ và thủ công

Danh sách 106 keyword phù hợp làm baseline, nhưng chưa bao phủ đủ ngôn ngữ tài chính Việt Nam.

Thiếu nhiều nhóm semantic/event như:

- earnings surprise;
- guidance revision;
- analyst recommendation;
- insider trading context;
- audit opinion;
- bond maturity/default risk;
- credit rating;
- regulatory approval;
- macro shock;
- commodity price exposure;
- FX/interest-rate exposure;
- sector-specific events.

### 6.8. Một số keyword quá chung

Các keyword có thể gây false positive:

- `cảnh báo`
- `vi phạm`
- `mua lại`
- `đóng cửa`
- `đình chỉ`
- `điều tra`
- `dự án mới`
- `đầu tư mới`
- `kỷ lục`
- `phục hồi`

Các từ này cần context window hoặc LLM/human validation để xác định đúng nghĩa.

### 6.9. Dễ bị nhiễu bởi boilerplate/full-text extraction

Nếu full-text crawler lấy thêm menu/sidebar/footer, keyword count có thể đếm nhầm từ không thuộc nội dung bài chính.

Đây là rủi ro content-level leakage/noise, đặc biệt với các trang có nhiều block điều hướng, tin liên quan, lịch sự kiện hoặc quảng cáo.

### 6.10. Không thay thế được semantic extraction

Keyword features chỉ trả lời “từ/cụm có xuất hiện không”. Chúng không trả lời:

- sự kiện là gì;
- ai tác động đến ai;
- mức độ quan trọng;
- hướng tác động;
- có bằng chứng quote nào;
- tác động ngắn hạn hay dài hạn;
- có mâu thuẫn với tin khác không.

---

## 7. Liên hệ với kết quả thực nghiệm

Kết quả keyword/news-as-predictor hiện không mạnh:

- Config_C technical + keyword không vượt Config_A technical-only ổn định.
- Config_B keyword-only gần random hoặc yếu.
- H2 keyword significance: 0 keyword qua BH-FDR.
- SHAP có thể cho thấy keyword đóng góp trong model, nhưng không đồng nghĩa cải thiện predictive performance.
- LLM sentiment/distant supervision cũ cũng không cải thiện rõ sau aggregation.

Diễn giải nên dùng trong luận văn:

> Keyword features là baseline cần thiết để kiểm định vai trò của tin tức. Kết quả âm cho thấy cách biểu diễn keyword/frequency không đủ để khai thác thông tin tin tức trong bối cảnh dữ liệu hiện có. Điều này biện minh cho việc chuyển news từ predictor trực tiếp sang evidence layer và/hoặc nghiên cứu semantic extraction bằng LLM có kiểm soát.

---

## 8. Cách viết trong luận văn

### Nên viết

> Danh sách keyword curated gồm 106 cụm từ tài chính được chia thành positive, negative và neutral. Các keyword này được dùng để tạo raw count, normalized count và TF-IDF-like features theo từng cặp `(ticker, quarter)`. Kết quả thực nghiệm cho thấy các feature keyword không cải thiện dự báo ổn định so với technical-only baseline. Điều này cho thấy biểu diễn keyword/frequency còn thiếu ngữ cảnh, materiality và relevance, nên phù hợp hơn làm baseline so sánh thay vì feature chính.

### Không nên viết

> Keyword features đại diện đầy đủ cho thông tin tin tức.

> Keyword sentiment đo được tác động của tin tức lên giá cổ phiếu.

> Keyword nào có SHAP cao là keyword có ý nghĩa thống kê hoặc causal impact.

> News không có giá trị vì keyword features thất bại.

### Nên kết luận

> Tin tức vẫn có giá trị, nhưng cần được xử lý như evidence có ngữ cảnh thay vì đếm từ đơn giản. Đây là cơ sở cho hướng evidence pack, decision card và LLM semantic extraction có kiểm soát.

---

## 9. Hướng cải thiện keyword/news features

### 9.1. Cải thiện ngắn hạn

- Lọc boilerplate/menu/footer trước khi đếm keyword.
- Đếm keyword trong title + article body chính, không đếm toàn trang.
- Thêm context window quanh keyword.
- Loại tin ticker matching confidence thấp.
- Gắn source quality score.
- Dùng recency weighting theo ngày trong kỳ.
- Tách event-specific features thay vì chỉ pos/neg score.

### 9.2. Cải thiện trung hạn

- Tạo human-labeled set 100–300 bài để đánh relevance/materiality/sentiment.
- So sánh keyword với TF-IDF + Logistic Regression.
- So sánh keyword với PhoBERT/XLM-R classifier.
- So sánh keyword với LLM zero-shot/few-shot extraction.
- Dùng event-time panel thay vì quarter aggregation.

### 9.3. Cải thiện dài hạn

- Xây Vietnamese financial event ontology.
- Xây evidence graph gồm company–event–source–date–materiality.
- Dùng RAG/evidence-span citation cho decision card.
- Dùng human-in-the-loop để verify LLM labels.

---

## 10. Ghi chú bảo vệ

Nếu hội đồng hỏi “vì sao keyword không hiệu quả?”, trả lời:

> Keyword count là baseline thô, thiếu ngữ cảnh, materiality, relevance và timing. Kết quả âm không chứng minh tin tức vô dụng; nó chứng minh cách biểu diễn keyword/frequency chưa đủ. Vì vậy luận văn dùng kết quả này để biện minh cho việc chuyển tin tức sang evidence layer và dùng LLM để tạo decision card có kiểm soát.

Nếu hội đồng hỏi “có nên bỏ keyword không?”, trả lời:

> Không nên bỏ. Keyword baseline cần giữ vì nó là đối chứng đơn giản, dễ giải thích. Kết quả âm của baseline này là bằng chứng quan trọng cho luận điểm rằng cần cách xử lý tin tức giàu ngữ nghĩa hơn.
