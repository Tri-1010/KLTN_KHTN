# Khuyến nghị dùng LLM để tăng chất lượng luận văn

> **Mục đích tài liệu:** Ghi lại các hướng nên dùng LLM để nâng chất lượng pipeline dự báo xu hướng cổ phiếu VN30, đặc biệt ở tầng biểu diễn tin tức, kiểm soát chất lượng dữ liệu, và giải thích kết quả.
>
> **Ngày tạo:** 2026-07-07
> **Nguyên tắc chính:** LLM nên dùng như **công cụ annotation / feature extraction / explanation**, không dùng trực tiếp như mô hình dự báo giá.

---

## 1. Tóm tắt khuyến nghị

| Ưu tiên | Hướng | Vai trò LLM | Giá trị chính | Rủi ro |
|---|---|---|---|---|
| 1 | LLM structured event annotation | Gán nhãn sự kiện từ bài báo | Novelty cao, feature giàu hơn keyword | Trung bình-Cao |
| 2 | LLM sentiment theo ngữ cảnh | Gán polarity positive / negative / neutral | Vá điểm yếu keyword-count | Trung bình |
| 3 | LLM explanation sau dự báo ML | Giải thích prediction bằng tin liên quan | Tăng chất lượng hệ hỗ trợ quyết định | Thấp |
| 4 | LLM data quality / entity matching | Kiểm lỗi dữ liệu, chuẩn hóa ticker | Giảm nhiễu pipeline | Thấp-Trung bình |
| 5 | RAG hỏi đáp theo mã cổ phiếu | Trả lời câu hỏi từ news + feature + prediction | Demo hệ thống tốt, dễ trình bày | Trung bình |
| 6 | LLM judge kiểm explanation | Kiểm hallucination và groundedness | Tăng độ tin cậy | Trung bình |

**Khuyến nghị ngắn:** làm theo thứ tự **2 → 1 → 3 → 4** nếu mục tiêu là luận văn chắc và có novelty. Nếu cần ít rủi ro nhất, làm **3 trước** vì không phá pipeline ML hiện tại.

---

## 2. Nguyên tắc bất biến khi dùng LLM

1. **LLM không dự báo giá trực tiếp.**  
   Không hỏi: “Cổ phiếu này sẽ tăng hay giảm?”.

2. **LLM chỉ xử lý nội dung tin tức tại thời điểm bài viết.**  
   Input chỉ gồm `title`, `description`, `full_text` / `article_summary`, `key_facts_json`, `ticker`, `published_at` nếu cần.

3. **Không đưa nhãn tương lai vào prompt.**  
   Không đưa return, label quý, kết quả model, giá sau ngày đăng.

4. **Output LLM phải lưu cố định.**  
   Sau khi annotate xong, lưu thành artifact như:
   - `data/news/annotated/llm_annotations.csv`
   - `data/news/annotated/llm_annotations_raw.jsonl`
   - metadata model, prompt version, timestamp, temperature / seed nếu có.

5. **Pipeline ML sau đó phải thuần deterministic.**  
   LLM output trở thành feature tĩnh. ML train/test vẫn giữ time-series split.

6. **So sánh công bằng với baseline.**  
   LLM features phải đi qua cùng pipeline với keyword features để so sánh Config_A vs Config_C.

---

## 3. Hướng 1 — LLM structured event annotation

### 3.1. Mục tiêu

Biến bài báo thành annotation có cấu trúc, giàu ý nghĩa kinh tế hơn keyword frequency.

Thay vì chỉ đếm từ như `lợi nhuận`, `nợ xấu`, `cổ tức`, LLM trích xuất:

```json
{
  "ticker": "VCB",
  "event_type": "earnings",
  "polarity": "positive",
  "magnitude": "high",
  "certainty": "confirmed",
  "relevance_to_ticker": "direct",
  "confidence": 0.86
}
```

### 3.2. Schema đề xuất

```json
{
  "ticker": "string",
  "event_type": "earnings | dividend | capital | mna | legal_risk | operation | management | macro | other",
  "polarity": "positive | negative | neutral",
  "magnitude": "high | medium | low",
  "certainty": "confirmed | planned | rumored",
  "relevance_to_ticker": "direct | indirect | irrelevant",
  "confidence": "number from 0 to 1",
  "rationale": "short Vietnamese explanation grounded in article text"
}
```

### 3.3. Feature aggregate theo quý

Từ annotation bài viết, tạo feature theo `(ticker, quarter)`:

- `llm_positive_ratio`
- `llm_negative_ratio`
- `llm_neutral_ratio`
- `llm_high_magnitude_event_count`
- `llm_earnings_positive_count`
- `llm_legal_risk_negative_count`
- `llm_confirmed_event_ratio`
- `llm_direct_relevance_ratio`
- `llm_weighted_sentiment_score`

Công thức gợi ý:

```text
weighted_sentiment = sum(polarity_score * magnitude_weight * confidence) / total_news

polarity_score:
  positive = +1
  neutral  = 0
  negative = -1

magnitude_weight:
  high   = 1.0
  medium = 0.6
  low    = 0.3
```

### 3.4. Giá trị cho luận văn

- Tăng novelty: dùng LLM như công cụ gán nhãn tài chính tiếng Việt.
- Tăng interpretability: SHAP trên event features dễ giải thích hơn keyword counts.
- Vá phản biện: “keyword frequency quá thô”.
- Nếu kết quả vẫn âm: robust null result mạnh hơn.
- Nếu kết quả dương: chứng minh cách biểu diễn text quan trọng hơn việc có/không có tin tức.

### 3.5. Rủi ro

- Reproducibility yếu nếu không lưu artifact.
- Chi phí và thời gian cao nếu annotate toàn bộ corpus.
- Có thể hallucinate nếu prompt không ép groundedness.
- Cần validation thủ công 100-200 mẫu.

### 3.6. Cách triển khai an toàn

1. Pilot 50-100 bài.
2. Kiểm schema, lỗi JSON, agreement thủ công.
3. Chốt prompt version.
4. Chạy full corpus.
5. Lưu raw input/output + parsed CSV.
6. Aggregate features.
7. Chạy lại pipeline ML.
8. So sánh với keyword baseline.

---

## 4. Hướng 2 — LLM sentiment theo ngữ cảnh

### 4.1. Mục tiêu

Thay keyword polarity thô bằng sentiment hiểu ngữ cảnh tài chính.

Ví dụ keyword-count dễ sai:

| Câu | Keyword thô | Ý nghĩa thật |
|---|---|---|
| “Nợ xấu giảm mạnh” | negative vì có `nợ xấu` | positive |
| “Lợi nhuận giảm 30%” | positive vì có `lợi nhuận` | negative |
| “Doanh nghiệp thoát lỗ” | negative vì có `lỗ` | positive |
| “Cổ phiếu bị cảnh báo” | có thể miss nếu keyword thiếu | negative |

LLM giải quyết bằng cách đọc toàn câu / đoạn.

### 4.2. Output đề xuất

```json
{
  "ticker": "FPT",
  "sentiment": "positive | negative | neutral",
  "sentiment_score": -1.0,
  "confidence": 0.78,
  "main_reason": "Lợi nhuận quý giảm so với cùng kỳ và triển vọng đơn hàng yếu hơn."
}
```

`sentiment_score` có thể dùng thang:

```text
positive = +1
neutral  = 0
negative = -1
```

Hoặc thang liên tục:

```text
very_positive = +1.0
positive      = +0.5
neutral       = 0
negative      = -0.5
very_negative = -1.0
```

### 4.3. Feature aggregate

- `llm_sentiment_mean`
- `llm_sentiment_std`
- `llm_positive_news_count`
- `llm_negative_news_count`
- `llm_high_confidence_sentiment_mean`
- `llm_sentiment_change_vs_prev_quarter`

### 4.4. Vì sao nên ưu tiên

- Dễ hơn structured event annotation.
- Trực tiếp thay thế keyword sentiment hiện tại.
- Dễ trình bày trong luận văn.
- Ít thay đổi pipeline.
- Có thể chạy pilot nhanh.

### 4.5. Vị trí trong luận văn

Có thể đặt trong Chương 4 như tầng biểu diễn text mới:

| Tầng | Phương pháp |
|---|---|
| 1 | Keyword frequency |
| 2 | Negation-aware keyword |
| 3 | LLM sentiment |
| 4 | LLM event annotation |

---

## 5. Hướng 3 — LLM explanation sau dự báo ML

### 5.1. Mục tiêu

Dùng LLM để giải thích prediction của mô hình ML bằng ngôn ngữ tự nhiên, dựa trên feature và tin tức liên quan.

ML vẫn là mô hình dự báo. LLM chỉ giải thích.

### 5.2. Kiến trúc

```text
Technical features + keyword/LLM features
        │
        ▼
ML model dự báo nhãn tăng/giảm
        │
        ├── SHAP / feature importance
        ├── top related news trong quý
        ▼
LLM sinh explanation có căn cứ
```

### 5.3. Input cho LLM

- Ticker.
- Quý dự báo.
- Prediction label và probability.
- Top SHAP features.
- 3-5 tin tức liên quan nhất.
- Feature values chính.

Không cần đưa toàn bộ dataset.

### 5.4. Output mẫu

```text
Mô hình dự báo VCB có xu hướng tăng trong 2024Q3 với xác suất 0.68.
Các yếu tố đóng góp chính gồm RSI cải thiện, MA trend tích cực, và tỷ lệ tin tức tích cực cao hơn quý trước.
Tin tức liên quan chủ yếu nói về tăng trưởng lợi nhuận và kiểm soát nợ xấu.
Tuy nhiên, độ tin cậy chỉ ở mức trung bình vì một số tín hiệu kỹ thuật vẫn chưa đồng thuận.
```

### 5.5. Giá trị

- Tăng tính “decision support” của hệ thống.
- Dễ demo.
- Dễ viết vào luận văn.
- Ít rủi ro vì không ảnh hưởng kết quả ML.
- Phù hợp với tên tài liệu hiện có `luan_van_ml_llm_decision_support.md`.

### 5.6. Guardrail

Prompt phải ép LLM:

- Không tự thêm tin không có trong input.
- Không khẳng định chắc chắn tuyệt đối.
- Nói rõ “mô hình dự báo”, không nói “chắc chắn cổ phiếu sẽ tăng”.
- Nếu evidence yếu, phải nói evidence yếu.

---

## 6. Hướng 4 — LLM data quality và entity matching

### 6.1. Mục tiêu

Dùng LLM để giảm nhiễu dữ liệu tin tức trước khi tạo feature.

Các lỗi có thể kiểm:

- Bài không liên quan ticker nhưng bị match sai.
- Bài chỉ nhắc tên công ty phụ, không phải subject chính.
- Bài duplicate gần giống.
- Bài PR / quảng cáo / tin chung không có thông tin tài chính.
- Tên doanh nghiệp viết nhiều dạng khác nhau.

### 6.2. Entity normalization

LLM nhận biết các alias:

| Alias | Ticker |
|---|---|
| Vietcombank | VCB |
| Ngân hàng Ngoại thương | VCB |
| Vinhomes | VHM |
| CTCP Vinhomes | VHM |
| FPT Corp | FPT |

### 6.3. Output đề xuất

```json
{
  "ticker": "VCB",
  "is_relevant": true,
  "relevance_level": "primary | secondary | irrelevant",
  "reason": "Bài viết tập trung vào kết quả kinh doanh của Vietcombank.",
  "normalized_entity": "Ngân hàng TMCP Ngoại thương Việt Nam",
  "confidence": 0.91
}
```

### 6.4. Feature / pipeline impact

- Lọc chỉ bài `primary` hoặc `direct` relevance.
- Giảm false positive trong `all_news_matched.csv`.
- Tăng chất lượng aggregate theo ticker-quarter.
- Có thể so sánh trước/sau lọc để chứng minh robustness.

### 6.5. Rủi ro

- Nếu lọc quá mạnh, mất dữ liệu.
- Cần audit mẫu thủ công.
- Nên dùng như lớp kiểm tra, không thay toàn bộ rule matching ngay lập tức.

---

## 7. Hướng 5 — RAG hỏi đáp theo mã cổ phiếu

### 7.1. Mục tiêu

Cho người dùng hỏi hệ thống bằng ngôn ngữ tự nhiên:

```text
Tại sao FPT quý này được dự đoán tăng?
```

Hệ thống lấy prediction, feature, SHAP, tin liên quan rồi LLM trả lời.

### 7.2. Kiến trúc

```text
User question
   │
   ├── Retrieve ticker + quarter
   ├── Load prediction + probability
   ├── Load top features / SHAP
   ├── Retrieve top related news
   ▼
LLM answer with citations / evidence
```

### 7.3. Giá trị

- Biến mô hình dự báo thành hệ hỗ trợ quyết định có giao diện tốt hơn.
- Tốt cho demo bảo vệ.
- Tạo điểm khác biệt ML + LLM.

### 7.4. Rủi ro

- Cần kiểm hallucination.
- Cần citation hoặc link bài báo.
- Cần giới hạn scope câu trả lời.

### 7.5. Prompt guardrail

LLM phải:

- Chỉ trả lời từ context được retrieve.
- Nếu không đủ dữ liệu, nói không đủ dữ liệu.
- Trích nguồn bài báo hoặc ít nhất title/date/source.
- Phân biệt prediction của model với khuyến nghị đầu tư.

---

## 8. Hướng 6 — LLM judge kiểm explanation

### 8.1. Mục tiêu

Dùng LLM thứ hai hoặc cùng LLM ở vai trò judge để kiểm explanation có bám dữ liệu không.

### 8.2. Judge checklist

LLM judge chấm:

```json
{
  "groundedness": 0.92,
  "uses_only_provided_evidence": true,
  "overclaims_prediction": false,
  "missing_important_risk": true,
  "final_verdict": "pass | revise | fail"
}
```

### 8.3. Giá trị

- Giảm hallucination.
- Tăng độ tin cậy phần decision-support.
- Có thể báo cáo trong phụ lục như quality control.

### 8.4. Khi nào cần

Nên dùng nếu làm Hướng 3 hoặc Hướng 5. Không cần nếu chỉ làm feature extraction offline.

---

## 9. Prompt mẫu cho LLM annotation

### 9.1. System prompt

```text
Bạn là công cụ gán nhãn tin tức tài chính tiếng Việt.
Nhiệm vụ của bạn là phân loại nội dung bài báo được cung cấp thành JSON có cấu trúc.
Chỉ sử dụng thông tin có trong bài báo. Không dùng kiến thức ngoài, không suy đoán diễn biến giá cổ phiếu, không đưa khuyến nghị đầu tư.
Nếu bài viết không liên quan trực tiếp đến ticker, đánh dấu relevance_to_ticker = "irrelevant".
Trả về JSON hợp lệ, không thêm prose ngoài JSON.
```

### 9.2. User prompt

```text
Ticker: {ticker}
Ngày đăng: {date}
Tiêu đề: {title}
Mô tả: {description}
Nội dung: {text_excerpt}

Hãy trích xuất annotation theo schema:
{
  "event_type": "earnings | dividend | capital | mna | legal_risk | operation | management | macro | other",
  "polarity": "positive | negative | neutral",
  "magnitude": "high | medium | low",
  "certainty": "confirmed | planned | rumored",
  "relevance_to_ticker": "direct | indirect | irrelevant",
  "confidence": number,
  "rationale": string
}
```

---

## 10. Prompt mẫu cho explanation sau dự báo

```text
Bạn là trợ lý giải thích kết quả mô hình dự báo cổ phiếu.
Chỉ sử dụng dữ liệu được cung cấp. Không tự thêm thông tin ngoài context.
Không đưa khuyến nghị mua/bán. Không khẳng định chắc chắn giá sẽ tăng/giảm.
Giải thích phải phân biệt rõ:
1. Mô hình đã dự báo gì.
2. Feature nào đóng góp chính.
3. Tin tức nào hỗ trợ hoặc làm yếu dự báo.
4. Mức độ tin cậy và hạn chế.

Input:
Ticker: {ticker}
Quarter: {quarter}
Prediction: {prediction_label}
Probability: {probability}
Top SHAP features: {top_features}
Related news: {news_items}

Output bằng tiếng Việt, 1-2 đoạn ngắn.
```

---

## 11. Kế hoạch triển khai đề xuất

### Giai đoạn 1 — Ít rủi ro, hiệu quả nhanh

- [ ] Làm LLM explanation sau dự báo ML.
- [ ] Tạo prompt explanation.
- [ ] Chọn 5-10 case ticker-quarter để demo.
- [ ] Viết mục “ML + LLM decision support” trong luận văn.

**Lý do:** Không ảnh hưởng pipeline chính, dễ trình bày, rủi ro thấp.

### Giai đoạn 2 — Nâng chất lượng feature

- [ ] Pilot LLM sentiment 50-100 bài.
- [ ] Kiểm thủ công agreement.
- [ ] Chạy full sentiment nếu pilot ổn.
- [ ] Aggregate sentiment features theo quý.
- [ ] So sánh Config_A vs Config_C mới.

**Lý do:** Vá trực tiếp điểm yếu keyword-count.

### Giai đoạn 3 — Novelty cao

- [ ] Pilot structured event annotation.
- [ ] Chốt schema.
- [ ] Chạy annotation full corpus.
- [ ] Tạo event features.
- [ ] Chạy ML và SHAP.
- [ ] Viết kết quả theo 2 kịch bản: robust null hoặc positive signal.

**Lý do:** Đây là hướng có đóng góp phương pháp mạnh nhất.

### Giai đoạn 4 — Quality control

- [ ] LLM entity relevance check cho mẫu lỗi.
- [ ] LLM judge kiểm explanation.
- [ ] Báo cáo hallucination / groundedness trong phụ lục nếu có thời gian.

---

## 12. Cách viết vào luận văn

### 12.1. Nếu chỉ làm explanation

Định vị:

```text
LLM không được sử dụng để dự báo nhãn, mà đóng vai trò chuyển đổi kết quả mô hình học máy và tin tức liên quan thành giải thích ngôn ngữ tự nhiên phục vụ hệ hỗ trợ quyết định.
```

### 12.2. Nếu làm sentiment / event annotation

Định vị:

```text
LLM được sử dụng như công cụ gán nhãn dữ liệu văn bản nhằm tạo đặc trưng có cấu trúc. Các đặc trưng này sau đó được đưa vào cùng pipeline học máy với các đặc trưng kỹ thuật và từ khóa, đảm bảo so sánh công bằng với các cấu hình baseline.
```

### 12.3. Nếu kết quả LLM features vẫn không cải thiện

Kết luận:

```text
Ngay cả khi thay thế biểu diễn từ khóa thô bằng annotation ngữ nghĩa từ LLM, đặc trưng tin tức vẫn không cải thiện đáng kể hiệu quả dự báo ở cấp độ quý. Điều này củng cố kết luận rằng tín hiệu tin tức, nếu tồn tại, có thể đã được phản ánh nhanh vào giá hoặc bị làm mờ khi tổng hợp theo quý.
```

### 12.4. Nếu kết quả LLM features cải thiện

Kết luận:

```text
Kết quả cho thấy tín hiệu từ tin tức chỉ xuất hiện khi nội dung văn bản được biểu diễn ở mức ngữ nghĩa cao hơn, thông qua sentiment hoặc event annotation. Điều này gợi ý rằng hạn chế của keyword frequency không nằm ở bản thân dữ liệu tin tức, mà ở phương pháp biểu diễn văn bản quá thô.
```

---

## 13. File / artifact nên tạo nếu triển khai

```text
data/news/annotated/llm_annotations_raw.jsonl
  Lưu input + raw output từng bài.

data/news/annotated/llm_annotations.csv
  Bản parsed sạch dùng cho feature engineering.

data/features/llm_sentiment_features.csv
  Feature sentiment aggregate theo ticker-quarter.

data/features/llm_event_features.csv
  Feature event aggregate theo ticker-quarter.

reports/llm_annotation_validation.csv
  Kết quả kiểm thủ công / agreement.

reports/llm_feature_model_comparison.csv
  So sánh model với và không có LLM features.
```

---

## 14. Kết luận khuyến nghị

Nếu mục tiêu là **tăng chất lượng luận văn nhanh và an toàn**, chọn:

1. **LLM explanation sau dự báo ML** — rủi ro thấp, tăng chất lượng hệ hỗ trợ quyết định.
2. **LLM sentiment theo ngữ cảnh** — nâng feature text nhưng vẫn đơn giản.
3. **LLM structured event annotation** — novelty cao nhất, nên làm sau pilot.
4. **LLM data quality / entity matching** — dùng để kiểm soát nhiễu, không cần thay toàn bộ pipeline ngay.

Cách định vị tốt nhất:

> LLM là lớp **semantic feature extraction và explanation**, còn mô hình ML truyền thống vẫn là thành phần dự báo chính. Thiết kế này giữ được tính kiểm định học thuật, giảm rủi ro lookahead bias, và làm hệ thống dễ diễn giải hơn.
