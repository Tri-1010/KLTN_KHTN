# Hướng phát triển mở rộng luận văn — Nâng cấp đặc trưng văn bản

> **Mục đích tài liệu:** Ghi lại toàn bộ phân tích và kế hoạch mở rộng luận văn sau khi
> kết quả hiện tại cho thấy H1 và H2 không được ủng hộ. Tài liệu này là kim chỉ nam để
> triển khai các hướng cải tiến đặc trưng văn bản (text features) nhằm nâng chất lượng
> luận văn.
>
> **Ngày tạo:** 2026-07-01
> **Trạng thái kế hoạch:** Ưu tiên Hướng A → B (tuần tự), Hướng C cân nhắc làm song song.

---

## 0. Bối cảnh và vấn đề cốt lõi

### 0.1. Tóm tắt kết quả hiện tại

| Giả thuyết | Nội dung | Kết luận hiện tại |
|---|---|---|
| **H1** | Config_C (kỹ thuật + từ khóa) > Config_A (chỉ kỹ thuật) về balanced accuracy | **Không được ủng hộ** — Δ(C−A) âm ở 3/4 thuật toán, mọi đơn vị thời gian |
| **H2** | Ít nhất một từ khóa có liên hệ thống kê có ý nghĩa (sau BH-FDR) với xu hướng giá | **Không được ủng hộ** — 0/71 từ khóa đạt ý nghĩa sau hiệu chỉnh |
| **H3** | Từ khóa đóng góp có ý nghĩa vào quyết định mô hình (SHAP) | **Được ủng hộ một phần** — ~32% đóng góp SHAP |

- Config_A (chỉ kỹ thuật) với LightGBM đạt **balanced accuracy ~0.76** — mạnh, vượt xa baseline.
- Đặc trưng từ khóa hiện tại là **tần suất thô (raw keyword frequency)** — phương pháp biểu diễn text đơn giản nhất.

### 0.2. Đặc điểm dữ liệu thực tế (quan trọng cho mọi quyết định)

- **Corpus tin tức:** ~34.966 bài đã processed, ~52.790 bài matched (gồm cả UNKNOWN ticker).
- **Nguồn:** cafef (13.275), vietstock (7.754), kinhtechungkhoan (7.358), vietnambiz (3.505), vnexpress (1.755), tnck (1.319).
- **Full-text enrichment đã hoàn tất sau kế hoạch ban đầu:** `45.949/45.968` unique URLs có `full_text` (**99,96% coverage**).
- **Độ dài văn bản sau full text:** `text_clean`/token trung bình tăng mạnh (average token/article khoảng **714,8**), không còn là title + mô tả ngắn.
- **Cột dữ liệu có sẵn:** `date`, `title`, `description`, `url`, `source`, `ticker`, `match_confidence`, `full_text`, `lead`, `article_summary`, `key_facts_json`, `text_clean`, `text_tokenized`.

> ⚠️ **Trần thông tin sau full text:** Lỗ hổng "corpus quá ngắn" đã được vá phần lớn. Kết quả âm sau full text cho thấy giới hạn chính nằm ở cách biểu diễn tin tức bằng tần suất từ khóa và thiết kế dự báo theo kỳ, không phải chỉ do thiếu nội dung bài báo.

### 0.3. Điểm yếu chí mạng cần vá — "Lỗ hổng phòng thủ"

Kết quả âm hiện tại có một lỗ hổng mà hội đồng gần như chắc chắn sẽ hỏi:

> *"Bạn kết luận news không có tín hiệu. Nhưng bạn chỉ dùng đếm tần suất từ khóa — phương
> pháp thô nhất. Làm sao biết kết quả âm là do thị trường hiệu quả (EMH), chứ không phải
> do phương pháp đo lường quá yếu?"*

**Luận văn hiện đã trả lời một phần lớn câu hỏi này:** đã mở rộng nguồn tin và bổ sung full-text enrichment 99,96%; các thí nghiệm đã chạy vẫn cho kết quả âm. Một số hướng biểu diễn nâng cao trong tài liệu này vẫn là kế hoạch/tuỳ chọn, không phải toàn bộ đã hoàn tất.

### 0.4. Ba trục tác động của các hướng mở rộng

| Trục | Ý nghĩa |
|---|---|
| **Defensibility** (khả năng phòng thủ) | Trả lời được câu hỏi phản biện khó |
| **Depth** (độ sâu phân tích) | Từ kết luận nhị phân → nuanced finding có điều kiện |
| **Novelty** (tính mới) | Đóng góp phương pháp mới, tiềm năng publication |

---

## 1. TỔNG QUAN BA HƯỚNG CHIẾN LƯỢC

| Hướng | Bản chất | Trục nâng chính | Rủi ro | Thay đổi thesis |
|---|---|---|---|---|
| **A** | Confirm & strengthen kết quả âm | Defensibility (rất nhiều), Rigor | Thấp | Không |
| **B** | Tìm điều kiện có tín hiệu | Depth (rất nhiều), Novelty | Trung bình | Mở rộng |
| **C** | Đổi framework: LLM event extraction | Novelty (rất nhiều), Depth | Cao | Lớn |

**Điểm mấu chốt:** Cả A và B đều KHÔNG cần thay đổi H1/H2/H3 hay viết lại cấu trúc luận
văn. Chỉ thêm mục mới vào Chương 4. Cấu trúc hiện tại vẫn intact.

---

## 2. HƯỚNG A — Confirm & Strengthen kết quả âm

### 2.1. Mục tiêu

Vá lỗ hổng phòng thủ (mục 0.3). Bước đã hoàn tất là loại trừ phản biện thiếu nội dung bằng full-text enrichment. Các bước còn lại, nếu cần, là thử thêm nhiều cấp độ biểu diễn text tinh vi hơn tần suất thô để chứng minh sâu hơn rằng kết quả âm không phải do phương pháp đo lường yếu.

### 2.2. Thay đổi về chất

- **Trước:** "Tần suất từ khóa không cải thiện dự báo" → phản biện: *có thể do phương pháp yếu.*
- **Sau full-text:** "Chúng tôi đã loại trừ phản biện thiếu nội dung bài báo; tần suất từ khóa trên gần như toàn văn corpus vẫn không cải thiện dự báo."
- Các hướng A1/A3/A5/A6 trong tài liệu này là các tầng biểu diễn có thể dùng tiếp nếu cần củng cố thêm luận điểm "không phải do phương pháp đo lường yếu".
- Kết luận hiện tại chuyển từ phát hiện hẹp ("keyword frequency trên title/description yếu") → phát hiện mạnh hơn ("keyword frequency trên full text vẫn yếu") → củng cố interpretation Semi-strong EMH/news-as-evidence.

### 2.3. Các kỹ thuật thành phần

#### A1. Signed Sentiment Score theo nhóm chủ đề
- Thay 71 raw counts → 6 điểm tổng hợp (earnings+, earnings−, dividend, risk, operations, event).
- Công thức: `sentiment_score(ticker, q) = (freq_positive_kw − freq_negative_kw) / total_news`.
- **Cần:** Không cần gì thêm (đã có keyword list với positive/negative).
- **Thời gian:** 2-3 ngày.
- **Potential:** Thấp-Trung bình.

#### A2. Negation-aware Keyword Matching
- Vấn đề hiện tại: "nợ xấu giảm" và "nợ xấu tăng" đều count là 1 hit "nợ xấu".
- Giải pháp: nếu có từ phủ định trong cửa sổ ±3 từ → đảo dấu (flip polarity).
- **Cần:** Viết thêm logic matching.
- **Thời gian:** 3-5 ngày.
- **Potential:** Trung bình (giải quyết đúng một điểm yếu thực sự của thiết kế hiện tại).

#### A3. News Velocity & Novelty Features
- Thêm: tốc độ tăng/giảm news so với kỳ trước, novelty (lần đầu xuất hiện của keyword),
  entropy phân phối keywords.
- Giả thuyết: thông tin mới quan trọng hơn thông tin lặp lại.
- **Cần:** Không cần gì thêm.
- **Thời gian:** 3-5 ngày.
- **Potential:** Trung bình.

#### A4. TF-IDF Weighted Keyword Score (cross-ticker)
- Thay normalize theo số bài → TF-IDF cross-ticker: keyword xuất hiện ở nhiều cổ phiếu
  cùng kỳ → IDF thấp → ít meaningful; keyword đặc trưng riêng → IDF cao → quan trọng hơn.
- **Cần:** Không cần gì thêm.
- **Thời gian:** 2-3 ngày.
- **Potential:** Thấp-Trung bình.

#### A5. PhoBERT Zero-shot Sentence Similarity (tùy chọn, nếu có GPU/thời gian)
- Encode bài viết + anchor phrases (positive/negative), tính cosine similarity → sentiment score.
- **Cần:** PyTorch, transformers, ~4GB RAM (CPU chạy được nhưng chậm).
- **Thời gian:** 1 tuần.
- **Potential:** Trung bình (corpus ngắn là bottleneck).

#### A6. LLM Zero-shot Sentiment (Gemini Flash — gần như free)
- Gửi từng bài lên API hỏi sentiment (positive/negative/neutral) đối với cổ phiếu liên quan.
- **Cần:** API key (Gemini Flash có free tier; GPT-4o-mini ~$0.60 cho toàn corpus).
- **Chi phí ước tính:** ~34.000 bài × ~200 tokens ≈ 7M tokens.
- **Thời gian:** 3-5 ngày implementation + 1-2 ngày chạy.
- **Potential:** Cao (LLM hiểu ngữ cảnh, phủ định, ẩn dụ tài chính tiếng Việt).
- **Lưu ý reproducibility:** fix temperature=0, ghi rõ model version. Nên lưu output cố định.

### 2.4. Kết quả kỳ vọng cho luận văn

Bảng so sánh mới trong Chương 4:

| Tầng | Phương pháp | Kỳ vọng |
|---|---|---|
| 1 | Keyword frequency (đã có) | Δ(C−A) ≈ 0 hoặc âm |
| 2 | Signed sentiment (A1) | So sánh |
| 3 | Negation-aware (A2) | So sánh |
| 4 | LLM sentiment (A6) | So sánh |

→ Nếu tất cả đều âm: **robust null result** — khó phản biện hơn nhiều.

### 2.5. Trục được nâng
Defensibility (rất nhiều), Rigor (nhiều), Depth (vừa). **Không tăng novelty ý tưởng gốc.**

### 2.6. Rủi ro
Thấp nhất. Ngay cả khi mọi thứ đều âm, luận văn vẫn tốt hơn hẳn.

---

## 3. HƯỚNG B — Tìm điều kiện mà text features CÓ tín hiệu

### 3.1. Mục tiêu

Thay đổi câu hỏi từ *"có tín hiệu không"* → *"khi nào thì có tín hiệu"*. Biến null finding
đơn giản thành nuanced finding có điều kiện.

### 3.2. Thay đổi về chất

- **Trước:** Kết luận nhị phân trên toàn bộ mẫu.
- **Sau:** "Tín hiệu news không tồn tại ở mức aggregate quý, **nhưng** ở granularity bài
  viết / nhóm mid-cap / khi có news spike / với announcement-type news, ta quan sát được [X]."

### 3.3. Các kỹ thuật thành phần

#### B1. Distant Supervision — Short-term Price Return Labeling ⭐ (hướng mạnh nhất)
- Dùng return 1-5 ngày sau ngày đăng bài làm **noisy label** cho sentiment bài viết đó:
  - Bài đăng → giá tăng ≥2% trong 3 ngày → "positive signal"
  - Bài đăng → giá giảm ≥2% trong 3 ngày → "negative signal"
  - Còn lại → neutral / bỏ qua
- Train classifier đơn giản (logistic/TF-IDF) trên text với noisy label này.
- Dùng predicted probability làm feature aggregate (ticker, quarter).
- **Ưu điểm:** methodology well-established trong văn liệu tài chính, KHÔNG cần expert label,
  reproducible 100%, chưa ai làm trên dữ liệu tiếng Việt theo setup này.
- **Cho phép kiểm định ở cấp độ TỪNG BÀI thay vì aggregate quý** → granularity cao có thể
  phát hiện pattern mà quarterly aggregation làm mờ.
- **Cần:** Join news date với price data theo ngày (đã có cả hai).
- **Thời gian:** 1-2 tuần.
- **Potential:** Cao (học thuật mạnh).
- **⚠️ Cảnh báo:** Cần tránh data leakage cực kỳ cẩn thận (label dùng future return chỉ để
  huấn luyện sentiment classifier ở tầng bài viết, KHÔNG được rò rỉ vào tập test của bài
  toán dự báo quý).

#### B2. Event-driven Price Reaction Labeling
- Chỉ lấy bài "announcement" (corporate disclosure feed của CafeF/Vietstock), map với price
  reaction ngay sau. Cleaner signal hơn B1 vì tránh contamination từ market-wide movement.
- **Cần:** Filter bài theo category/source pattern.
- **Thời gian:** 2-3 tuần.
- **Potential:** Cao.

#### B3. Phân tích theo Ngành và Vốn hóa (Segmentation)
- Kiểm định liệu tác động text có khác giữa nhóm ngành (ngân hàng, BĐS, sản xuất) hay
  nhóm vốn hóa (large-cap VN30 vs mid-cap HOSE-80).
- Giả thuyết: mid-cap ít analyst coverage → market phản ứng chậm hơn → text có tín hiệu hơn.
  Từ khóa "nợ xấu" có thể đặc biệt liên quan ngành ngân hàng.
- **Cần:** Sector labels (đã có trong config), tái chạy phân tích theo nhóm.
- **Thời gian:** 3-5 ngày.
- **Potential:** Trung bình-Cao.

#### B4. Cross-sector News Spillover
- Tin tức một cổ phiếu cùng ngành ảnh hưởng cổ phiếu khác. Build industry_sentiment score.
- **Cần:** Sector labels, industry-level news aggregation.
- **Thời gian:** 1 tuần.
- **Potential:** Trung bình-Cao (spillover ít được khai thác).

#### B5. Anomaly Detection trên News Volume
- Phát hiện spike bất thường số lượng tin (bất kể content). Spike = event bất thường.
- Feature binary: "kỳ này có news spike không?"
- **Cần:** Không cần gì mới.
- **Thời gian:** 2-3 ngày.
- **Potential:** Thấp-Trung bình.

### 3.4. Trục được nâng
Depth (rất nhiều), Novelty (nhiều), Rigor (vừa).

### 3.5. Rủi ro
Trung bình. Kết quả conditional có thể cũng âm; cần cẩn thận data leakage hơn.

---

## 4. HƯỚNG C — LLM as Annotation Tool (Structured Event Extraction)

> **Positioning đã chốt:** LLM dùng như **annotation tool** (công cụ gán nhãn), KHÔNG phải
> forecaster. Đây là lựa chọn an toàn nhất về mặt phương pháp luận.

### 4.1. Nguyên tắc cốt lõi — RANH GIỚI BẤT KHẢ XÂM PHẠM

**LLM chỉ chạm tầng biểu diễn text (feature extraction), TUYỆT ĐỐI không chạm tầng dự báo.**

- LLM đọc bài viết → sinh structured annotation.
- Annotation trở thành features tĩnh.
- Mô hình ML (LightGBM, RF...) mới là thứ dự báo.
- **LLM KHÔNG BAO GIỜ được hỏi "giá sẽ tăng hay giảm".**

Ba lớp phòng thủ có được:
1. Không circularity ở tầng dự báo (LLM không predict).
2. Annotation lưu cố định → phần ML reproducible 100%.
3. So sánh trực tiếp được với keyword frequency vì cùng đi qua một pipeline ML.

### 4.2. Kiến trúc dữ liệu (mấu chốt reproducibility)

```
Bài viết (text)
    │
    ├──[LLM annotate 1 LẦN]──► annotation JSON (LƯU CỐ ĐỊNH)
    │                          + model version, timestamp, temperature, prompt version
    │
    ▼
data/news/annotated/llm_annotations.csv   ◄── artifact đóng băng, commit vào repo
    │
    ▼
[Aggregate theo (ticker, quarter)]  ◄── code thuần, reproducible
    │
    ▼
Features mới ──► pipeline ML hiện tại (không đổi)
```

→ Sau khi có `llm_annotations.csv`, mọi bước sau KHÔNG cần gọi LLM. Bất kỳ ai có file này
đều tái lập được kết quả ML. Phòng thủ: *"Annotation là dữ liệu đầu vào cố định, tương tự
nhãn do chuyên gia gán, được đóng gói kèm luận văn."*

### 4.3. Annotation schema đề xuất

```json
{
  "event_type": "earnings | dividend | capital | mna | legal_risk | operation | management | other",
  "polarity": "positive | negative | neutral",
  "magnitude": "high | medium | low",
  "certainty": "confirmed | planned | rumored",
  "relevance_to_ticker": "direct | indirect"
}
```

Aggregate lên (ticker, quarter) thành features:
- Tỷ lệ bài positive/negative/neutral theo từng event_type.
- Điểm sentiment có trọng số magnitude.
- Tỷ lệ tin "confirmed" vs "planned/rumored" (novelty/certainty signal).
- Lọc chỉ giữ bài "direct" relevance.

→ Giàu hơn hẳn 71 keyword counts; mỗi feature có diễn giải kinh tế rõ ràng cho SHAP (H3).

### 4.4. Chống lookahead bias trong prompt

- Prompt chỉ đưa nội dung point-in-time được phép dùng (`title`, `description`, `article_summary`, `key_facts` hoặc excerpt từ `full_text` đã cắt ngắn), yêu cầu đánh giá **thuần túy dựa trên nội dung văn bản được cung cấp**.
- Cấm rõ ràng: *"Không suy đoán về diễn biến giá cổ phiếu, chỉ phân loại nội dung bài viết."*
- `polarity` ở đây là polarity của **nội dung tin** (sự kiện tốt/xấu), KHÔNG phải dự báo giá.

### 4.5. Đóng góp cho luận văn — 4 tầng biểu diễn text

| Tầng | Phương pháp | Độ tinh vi |
|---|---|---|
| 1 | Keyword frequency (đã có) | Thô nhất |
| 2 | Signed sentiment theo nhóm (A1) | Trung bình |
| 3 | (tùy chọn) PhoBERT embeddings (A5) | Cao |
| 4 | **LLM structured annotation (C)** | Cao nhất |

**Thắng ở cả hai kịch bản:**
- **Nếu tầng 4 vẫn âm:** "Ngay cả annotation bằng LLM state-of-the-art với
  event/magnitude/certainty cũng không cải thiện dự báo → bằng chứng rất mạnh cho
  semi-strong EMH ở tầng dự báo quý tại VN." → robust null result đúng nghĩa.
- **Nếu tầng 4 có tín hiệu:** "Tín hiệu text chỉ xuất hiện khi biểu diễn đủ tinh vi
  (structured events) → đóng góp phương pháp: *cách biểu diễn text quan trọng hơn bản thân
  sự hiện diện của text.*" → positive finding có giá trị.

### 4.6. Nhược điểm — Phân tích 2 nhóm

#### Nhóm 1: Model mạnh (Gemini Pro / GPT-5.5) CÓ giúp
| Nhược điểm | Model mạnh cứu? |
|---|---|
| Chất lượng extraction event | ✅ Có |
| Tuân thủ JSON schema | ✅ Phần lớn |
| Khai thác full text dài hơn | ✅ Có, nhưng vẫn cần chống nhiễu/boilerplate |

#### Nhóm 2: Model mạnh KHÔNG giải quyết (vấn đề phương pháp luận)
| Nhược điểm | Mức nghiêm trọng | Model mạnh cứu? |
|---|---|---|
| **Reproducibility** (closed API, deprecate, non-deterministic) | Rất cao | ❌ Không — còn TỆ HƠN (model mới bị đổi/tắt nhanh hơn) |
| **Lookahead/circularity** (model đã "biết" tương lai từ training data) | Rất cao | ❌ Không — còn TỆ HƠN (model mạnh nhiều kiến thức hơn) |
| Không chứng minh nhân quả (reverse causality) | Cao | ❌ Không |
| Nhiễu/boilerplate trong full text và quan hệ nhân quả yếu | Cao | ❌ Không |
| Thời gian/scope/chi phí | Cao | ❌ Không (model mạnh còn đắt hơn) |

> **Kết luận cốt lõi:** Model mạnh cải thiện chất lượng đầu ra, nhưng 2 nhược điểm chí mạng
> nhất — **reproducibility** và **lookahead bias** — thì model mạnh làm TỆ HƠN.
> **Positioning "annotation tool" (đã chọn) trung hòa được lookahead** vì LLM không predict giá.

### 4.7. Ba biện pháp bắt buộc để phòng thủ Hướng C

1. **Chống lookahead:** prompt cấm dùng kiến thức ngoài text; chỉ đưa nội dung bài báo/summary/key facts đã có tại `published_at`; cân nhắc ẩn tên công ty/ngày tháng; test trên sự kiện sau training cutoff để chứng minh không hindsight; ghi rõ trong Chương phương pháp.
2. **Chống irreproducibility:** dùng LLM như labeler chạy MỘT LẦN, lưu toàn bộ raw output
   (input + output + model version + timestamp + temperature + prompt version) thành dataset
   cố định, đóng gói kèm luận văn. Phần "science" nằm ở classifier/pipeline local reproducible.
3. **Đa model (khuyến khích):** chạy song song thêm 1 model open-source (Qwen, Llama, PhoGPT)
   để chứng minh kết quả không phụ thuộc một model đóng cụ thể → tăng độ tin cậy.

### 4.8. Validation annotation (chuẩn mực học thuật)
- Tự tay kiểm tra ~100-200 annotation, báo cáo "agreement rate" giữa người và LLM.
- Đây là chuẩn trong các paper dùng LLM annotation.

### 4.9. Rủi ro còn lại (chấp nhận)
- Chi phí/thời gian: 34k bài × model. Cần batch, xử lý rate limit, validate schema. ~2-4 tuần.
- Vẫn là correlational, không nhân quả (áp dụng cho toàn luận văn).

### 4.10. Câu hỏi cần chốt trước khi build Hướng C
1. **Model nào truy cập được** — Gemini Pro API hay ChatGPT? (ảnh hưởng client & chi phí)
2. **Đơn vị annotation** — mỗi bài riêng (34k lần gọi) hay gộp nhiều bài cùng ticker-quarter?
3. **Bắt đầu từ đâu** — thiết kế prompt+schema, hay pilot 50-100 bài trước khi chạy full.

→ **Khuyến nghị:** bắt đầu bằng **pilot 50-100 bài** để kiểm tra chất lượng annotation
thực tế trước khi commit chạy toàn bộ.

---

## 5. BẢNG TỔNG HỢP TẤT CẢ KỸ THUẬT

| Mã | Kỹ thuật | Hướng | Cần label | Thời gian | Potential | Corpus ngắn OK |
|---|---|---|---|---|---|---|
| A1 | Signed sentiment theo nhóm | A | ✅ Không | 2-3 ngày | Thấp-TB | ✅ |
| A2 | Negation-aware matching | A | ✅ Không | 3-5 ngày | Trung bình | ✅ |
| A3 | News velocity & novelty | A | ✅ Không | 3-5 ngày | Trung bình | ✅ |
| A4 | TF-IDF cross-ticker | A | ✅ Không | 2-3 ngày | Thấp-TB | ✅ |
| A5 | PhoBERT zero-shot similarity | A | ✅ Không | 1 tuần | Trung bình | ⚠️ |
| A6 | LLM zero-shot sentiment | A | ✅ Không | 3-5 ngày | Cao | ✅ |
| B1 | Distant supervision (price return) ⭐ | B | ✅ Không | 1-2 tuần | Cao | ✅ |
| B2 | Event-driven price reaction | B | ✅ Không | 2-3 tuần | Cao | ✅ |
| B3 | Segmentation ngành/vốn hóa | B | ✅ Không | 3-5 ngày | TB-Cao | ✅ |
| B4 | Cross-sector spillover | B | ✅ Không | 1 tuần | TB-Cao | ✅ |
| B5 | Anomaly detection news volume | B | ✅ Không | 2-3 ngày | Thấp-TB | ✅ |
| C | LLM structured event annotation | C | ✅ Không* | 2-4 tuần | Cao | ✅ |

*Hướng C dùng LLM như annotation tool, không cần expert label.

---

## 6. KẾ HOẠCH TRIỂN KHAI (đã chốt: A → B trước, C song song)

Timeline tham chiếu: hiện tại ~Tháng 7, bảo vệ ~Tháng 9-10 → còn ~8-10 tuần.

### Giai đoạn 1 — Hướng A (Tuần 1-3)
**Mục tiêu:** Vá lỗ hổng phòng thủ. Ưu tiên các kỹ thuật rẻ, chắc chắn có giá trị.
- [ ] A2 — Negation-aware matching (giải quyết điểm yếu thực sự nhất).
- [ ] A1 — Signed sentiment theo nhóm.
- [ ] A3 — News velocity & novelty (nếu còn thời gian).
- [ ] A6 — LLM zero-shot sentiment (Gemini Flash) — novelty point rõ ràng.
- [ ] Tạo **Bảng so sánh 4 tầng biểu diễn text** trong Chương 4.

**Đầu ra Chương 4:** Mục mới *"Phân tích mở rộng: So sánh các phương pháp biểu diễn text"*.

### Giai đoạn 2 — Hướng B (Tuần 3-5)
**Mục tiêu:** Từ null finding → nuanced finding có điều kiện.
- [ ] B1 — Distant supervision (ưu tiên cao nhất, học thuật mạnh).
- [ ] B3 — Segmentation ngành/vốn hóa (rẻ, dễ có kết quả thú vị).
- [ ] B4 — Cross-sector spillover (nếu còn thời gian).

**Đầu ra Chương 4:** Mục mới *"Kiểm định điều kiện có tín hiệu"*.

### Giai đoạn 3 — Hướng C song song (khi có băng thông)
**Mục tiêu:** Novelty mạnh nhất; annotation tool an toàn.
- [ ] Chốt 3 câu hỏi mục 4.10.
- [ ] Pilot 50-100 bài, đánh giá chất lượng annotation.
- [ ] Nếu pilot tốt → chạy full corpus, lưu `llm_annotations.csv` cố định.
- [ ] Validation agreement rate (~100-200 bài).
- [ ] Aggregate → tầng 4 trong bảng so sánh biểu diễn text.

### Giai đoạn 4 — Viết & hoàn thiện (Tuần 5+)
- [ ] Cập nhật Chương 4 với các phân tích mở rộng.
- [ ] Cập nhật Chương 5: robust null result / nuanced finding / positive finding tùy kết quả.
- [ ] Cập nhật mục "Hướng nghiên cứu tương lai" (đã đề cập nhiều ý ở đây).

---

## 7. NGUYÊN TẮC BẤT BIẾN (áp dụng cho MỌI hướng)

1. **Không data leakage thời gian:** mọi thông tin từ kỳ q+1 không được dùng khi xây feature
   cho kỳ q. Cutoff train/test 2025Q1 giữ nguyên. Chuẩn hóa/chọn feature chỉ fit trên train.
2. **Time-series split, không shuffle, không random CV.**
3. **Cấu trúc H1/H2/H3 giữ nguyên** với A và B — chỉ thêm mục vào Chương 4.
4. **Kết quả âm vẫn là đóng góp khoa học hợp lệ** — tinh thần kiểm định trung lập.
5. **Reproducibility:** artifact LLM (nếu dùng) phải đóng băng và commit; ghi model version.
6. **So sánh công bằng:** mọi tầng biểu diễn text đều đi qua CÙNG pipeline ML để so sánh
   Config_A vs Config_C nhất quán.

---

## 8. GHI CHÚ NHANH VỀ VỊ TRÍ FILE & DỮ LIỆU

- Config pipeline: `config/pipeline_config.yaml`
- Keyword groups: `config/keywords_by_group.json` (đã có positive/negative — nền cho A1/A2)
- News processed: `data/news/processed/all_news_processed.csv` (cột `text_clean`, `description`)
- News matched: `data/news/matched/all_news_matched.csv`
- Giá: `data/prices/<TICKER>.csv` (nền cho B1/B2 distant supervision)
- Luận văn: `docs/luan_van.md`
- Reports hiện có: `reports/model_comparison.csv`, `reports/period_experiment.csv`,
  `reports/keyword_significance.csv`, v.v.
- **Dự kiến thêm:** `data/news/annotated/llm_annotations.csv` (Hướng C)
