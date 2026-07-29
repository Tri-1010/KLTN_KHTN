# Nội dung deck cập nhật hướng nghiên cứu gửi GVHD

## Mục tiêu deck

Trình bày ngắn gọn quá trình chuyển hướng nghiên cứu:

- Keyword-based đã được thử như baseline nhưng không ổn định.
- Trọng tâm mới: kết hợp tín hiệu kỹ thuật, LLM đọc ngữ cảnh tin tức và bằng chứng có thể kiểm tra.
- Đầu ra hướng tới hệ hỗ trợ quyết định cho nhà đầu tư, không phải hệ khuyến nghị mua/bán.

## Nguyên tắc diễn giải

- LLM consensus là pseudo-label, không phải human ground truth.
- Kết quả event-window và ML hiện là exploratory.
- Không claim quan hệ nhân quả.
- Không claim alpha dài hạn.
- Không đưa khuyến nghị đầu tư.
- Tách dữ liệu/bằng chứng sẵn có tại thời điểm quyết định khỏi outcome review để hạn chế hindsight bias.

---

# Slide 1 — Từ keyword-based đến LLM hỗ trợ quyết định

## Tiêu đề

**Từ keyword-based đến LLM hỗ trợ quyết định**

## Thông điệp chính

Mục tiêu mới: kết hợp tín hiệu kỹ thuật, hiểu ngữ cảnh tin tức và bằng chứng có thể kiểm tra.

## Luồng nội dung

1. **Keyword đếm từ**
   - Đã thử nhiều cách.
   - Kết quả không ổn định.

2. **LLM đọc ngữ cảnh**
   - Trích ticker relevance.
   - Trích materiality.
   - Trích direction.
   - Trích evidence span.

3. **Decision support**
   - Evidence card.
   - Dashboard.
   - Hỗ trợ nhà đầu tư hiểu tin nào liên quan, vì sao trọng yếu và bằng chứng nằm ở đâu.

## Gợi ý lời nói

Hướng keyword không bị bỏ hoàn toàn. Keyword được giữ lại thành baseline minh bạch và phần phản biện nghiên cứu. Hướng mới tập trung vào bằng chứng semantic có thể kiểm tra, không hứa hẹn tín hiệu mua/bán.

---

# Slide 2 — Các hạng mục đã hoàn thành

## Tiêu đề

**Các hạng mục đã hoàn thành**

## Số liệu headline

| Chỉ số | Giá trị |
|---|---:|
| Bài tin unique | 28.062 |
| Nguồn tin | 6 |
| Dự báo ML out-of-sample | 685.704 |
| Purged folds | 3 |
| LLM consensus rows | 150 |
| Eligible rows | 122 |
| Evidence packs và decision cards | 25 |

## Dữ liệu và mô hình

- Crawl và chuẩn hóa tin tức; ghép với giá và mã VN30.
- Xây dựng đặc trưng kỹ thuật.
- Kiểm định walk-forward với purge 20 phiên.
- Xây dựng schema LLM gồm relevance, materiality, direction, event type và evidence span.

## LLM và sản phẩm hỗ trợ

- Sinh consensus pseudo-label, kiểm tra agreement và QC thủ công.
- Tạo evidence pack, decision card, monitoring timeline và dashboard prototype.
- Theo dõi outcome tách biệt dữ liệu sẵn có tại thời điểm ra quyết định.

## Gợi ý lời nói

Hạ tầng nghiên cứu đã hoàn thành xuyên suốt từ dữ liệu, ML, LLM đến prototype. Các số lượng này không chứng minh hiệu quả đầu tư.

---

# Slide 3 — Keyword: kết quả phản biện, không phải tín hiệu chính

## Tiêu đề

**Keyword: kết quả phản biện, không phải tín hiệu chính**

## Thông điệp chính

Keyword hữu ích để tạo baseline minh bạch. Rule-based không nắm được ngữ cảnh và materiality.

## Bảng rule so với semantic labels, n = 122

| Đại diện rule | Accuracy | Macro-F1 |
|---|---:|---:|
| Direction | 37,7% | 22,8% |
| Event type | 14,8% | 8,7% |
| Materiality | 22,1% | 15,9% |
| Ticker relevance | 68,9% | 20,9% |

## Nguyên nhân chính

- Thiếu context và materiality.
- Ticker mismatch.
- Tin thị trường chung.
- Boilerplate.
- Mixed direction.

## Kết luận

Giữ keyword như baseline phản biện; không dùng keyword làm hướng đóng góp chính.

## Biểu đồ dùng

`multi_llm_evidence_extraction/reports/charts/rule_vs_semantic_confusion.png`

## Gợi ý lời nói

Negative finding vẫn là kết quả có giá trị. Kết quả không chứng minh tin tức vô ích; chỉ cho thấy biểu diễn bằng đếm từ thiếu ngữ cảnh và chưa phù hợp mục tiêu nghiên cứu.

---

# Slide 4 — LLM nâng cấp biểu diễn tin tức thành bằng chứng

## Tiêu đề

**LLM nâng cấp biểu diễn tin tức thành bằng chứng**

## Thông điệp chính

Thay vì đếm từ, LLM trích xuất cấu trúc và câu bằng chứng có thể truy vết.

## Schema semantic evidence extraction

| Trường | Câu hỏi |
|---|---|
| Ticker relevance | Tin có liên quan trực tiếp đến mã? |
| Materiality | Mức độ trọng yếu của thông tin? |
| Direction | Tác động support / risk / neutral? |
| Event type | Sự kiện nào đang diễn ra? |
| Evidence span | Câu nào chứng minh nhãn? |

## Số liệu

| Chỉ số | Giá trị |
|---|---:|
| Consensus rows | 150 |
| Eligible rows | 122 |
| Mean agreement | 0,84 |

## Lưu ý bắt buộc

Consensus là pseudo-label, không phải human ground truth.

## Biểu đồ dùng

`multi_llm_evidence_extraction/reports/charts/agreement_heatmap.png`

## Gợi ý lời nói

LLM phục vụ trích xuất có cấu trúc và evidence span. Agreement 0,84 biểu thị độ nhất quán giữa annotators trong quy trình này; không phải độ chính xác với toàn bộ quần thể.

---

# Slide 5 — Kết quả thực nghiệm: có tín hiệu ban đầu, claim có kiểm soát

## Tiêu đề

**Kết quả thực nghiệm: có tín hiệu ban đầu, claim có kiểm soát**

## Event-window exploratory

- Có **1 / 8** test robust-positive sau điều chỉnh BH-FDR.
- So sánh materiality cao/trung bình với thấp tại T+5: **+2,23% adjusted return**.
- Đây là bằng chứng exploratory, không phải claim nhân quả.

## Technical + semantic ML

- **685.704** dự báo out-of-sample.
- **3** purged folds.
- Purge: **20 phiên**.
- AUC và balanced accuracy gần 0,5.
- Chưa có bằng chứng lọc cổ phiếu hữu ích ổn định.

## Kỷ luật diễn giải

Không claim nhân quả, alpha dài hạn hay khuyến nghị đầu tư.

## Giá trị hiện tại

Bằng chứng exploratory cùng quy trình kiểm định có thể audit.

## Biểu đồ dùng

`multi_llm_evidence_extraction/reports/charts/event_window_adjusted_returns.png`

## Gợi ý lời nói

Điểm mạnh hiện tại là báo cáo minh bạch cả tín hiệu yếu/null. Có correction cho multiple testing, confidence interval, purged OOS và phân tách rõ nội dung exploratory khỏi investment claim.

---

# Slide 6 — Prototype hỗ trợ nhà đầu tư và bước tiếp theo

## Tiêu đề

**Prototype hỗ trợ nhà đầu tư và bước tiếp theo**

## Giá trị của hướng mới

- Không chỉ trả về score: cho thấy tin nào, vì sao trọng yếu và câu bằng chứng.
- Tách point-in-time evidence khỏi outcome review để hạn chế hindsight bias.
- Keyword giữ vai trò baseline minh bạch và phần phản biện học thuật.

## Dashboard / prototype

- Tín hiệu kỹ thuật.
- Evidence semantic.
- Monitoring timeline.
- Outcome review.
- Evidence card và decision card.

## Bước tiếp theo

1. Mở rộng human annotation và kiểm tra liên-chủ thể.
2. Audit contamination, ticker matching và dữ liệu point-in-time.
3. Paper-trading trước bất kỳ claim nào về tính hữu ích đầu tư.

## Hình minh họa dùng

`streamlit_dashboard.png`

## Gợi ý lời nói

Đề tài chuyển từ tối ưu keyword sang hệ hỗ trợ quyết định có bằng chứng. Ba bước tiếp theo là điều kiện cần trước khi mở rộng bất kỳ kết luận nào về tính hữu ích đầu tư.

---

# Nguồn số liệu và hình

- `multi_llm_evidence_extraction/reports/advisor_pitch_one_page.md`
- `multi_llm_evidence_extraction/reports/ket_qua_luan_van_semantic_news_materiality.md`
- `multi_llm_evidence_extraction/reports/event_window_stat_tests_report.md`
- `multi_llm_evidence_extraction/reports/charts/rule_vs_semantic_confusion.png`
- `multi_llm_evidence_extraction/reports/charts/agreement_heatmap.png`
- `multi_llm_evidence_extraction/reports/charts/event_window_adjusted_returns.png`
- `streamlit_dashboard.png`
