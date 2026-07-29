# Kế hoạch triển khai chi tiết — Hướng A & B

> **Mục đích:** Kế hoạch thực thi cụ thể, bám sát pipeline hiện có, để triển khai Hướng A
> (củng cố kết quả âm) và Hướng B (tìm tín hiệu có điều kiện). **Yêu cầu bắt buộc:** mỗi
> thí nghiệm khi xong PHẢI so sánh với kết quả cũ trong luận văn, có nhận xét và phân tích
> đầy đủ.
>
> **Ngày tạo:** 2026-07-01
> **Tài liệu nền:** `docs/huong_phat_trien_mo_rong.md`, `docs/luan_van.md`

---

## PHẦN 0: NGUYÊN TẮC NỀN TẢNG

### 0.1. Hiểu kiến trúc pipeline hiện có (đã khảo sát)

Pipeline tổ chức theo TASK tuần tự trong `pipeline/`:

| Task | File | Vai trò | Output chính |
|---|---|---|---|
| TASK 8 | `task8_keywords.py` | Định nghĩa keyword list (`KEYWORD_GROUPS`), matching | `config/keywords_by_group.json` |
| TASK 9 | `task9_kw_features.py` | Trích xuất keyword features | `data/features/keyword_features.csv` |
| TASK 10 | `task10_train.py` | Train 4 thuật toán × 3 config | `reports/model_comparison.csv` |
| TASK 11 | `task11_shap.py` | Phân tích SHAP | `reports/shap_*.png` |

**Điểm mấu chốt về code cần biết:**
- `task9_kw_features.py::compute_raw_counts()` — đã có **longest-first masking**. Đây là nơi
  can thiệp cho A2 (negation-aware).
- `task9_kw_features.py::compute_sentiment_scores()` — đã có `pos_score`, `neg_score`,
  `sentiment_ratio`. Đây là nơi mở rộng cho A1 (signed sentiment theo nhóm).
- `task10_train.py::identify_feature_columns()` — phân loại cột tech vs keyword bằng prefix
  (`kw_`, `kw_norm_`, `tfidf_`) và tập `kw_exact`. **Mọi feature mới phải được nhận diện đúng
  ở đây** để rơi vào đúng Config.
- `task10_train.py::get_feature_configs()` — định nghĩa Config_A/B/C.
- Split: `time_series_split(cutoff="2025Q1")`, không shuffle. Imputer fit trên train.

### 0.2. Đóng băng kết quả cũ làm baseline so sánh (LÀM TRƯỚC TIÊN)

Trước khi thay đổi bất cứ gì, phải **snapshot toàn bộ kết quả hiện tại** để so sánh về sau.

**Số liệu tham chiếu cũ (từ luận văn — để đối chiếu nhanh):**

*HOSE-80, cutoff 2025Q1 (Bảng 4.1 luận văn):*
| Thuật toán | Config_A | Config_C | Δ(C−A) | Config_B |
|---|---|---|---|---|
| LightGBM | 0.7599 | 0.7368 | −0.0231 | 0.5219 |
| Random Forest | 0.7351 | 0.7164 | −0.0187 | 0.5236 |
| XGBoost | 0.7293 | 0.7261 | −0.0032 | 0.5239 |
| Logistic Regression | 0.7269 | 0.6966 | −0.0303 | 0.5015 |

*Kiểm định H2:* 0/71 keyword đạt ý nghĩa sau BH-FDR. Top raw signal: "chia cổ tức"
(chi_p=0.0089), "giảm mạnh" (0.0094), "nợ xấu" (0.0448).

*SHAP (H3):* keyword ~32% đóng góp; nhất quán hướng 25.2%.

**Hành động cụ thể — tạo snapshot:**
```
reports/baseline_v0/
├── model_comparison.csv          (copy từ reports/model_comparison.csv)
├── keyword_significance.csv       (copy)
├── period_experiment.csv          (copy)
├── metrics_breakdown.csv          (copy)
├── news_density_analysis.csv      (copy)
└── shap_configc_keyword_ranking.csv (copy)
```
→ Đây là "kết quả cũ" bất biến. Mọi thí nghiệm mới so với snapshot này.

### 0.3. Quy ước đặt tên để so sánh nhất quán

Mỗi kỹ thuật tạo một biến thể feature set có version rõ ràng:
- `keyword_features.csv` → giữ nguyên (v0, baseline).
- `keyword_features_A1.csv`, `keyword_features_A2.csv`, ... cho từng biến thể.
- Kết quả train tương ứng: `reports/model_comparison_A1.csv`, v.v.

→ Cho phép chạy song song và so sánh trực tiếp mà không ghi đè baseline.

### 0.4. Nguyên tắc bất biến (áp dụng mọi thí nghiệm)
1. **Không data leakage thời gian:** cutoff 2025Q1 giữ nguyên; imputer/scaler fit chỉ trên train.
2. **Time-series split, không shuffle.**
3. **So sánh công bằng:** mọi biến thể đi qua CÙNG `task10_train.py` (cùng thuật toán,
   cùng hyperparameter, cùng split) → chỉ khác feature set.
4. **Giữ nguyên Config_A** (16 tech features) ở mọi thí nghiệm → Config_A là "hằng số đối chứng".
   Chỉ thay đổi phần keyword (Config_B) và do đó Config_C.

---

## PHẦN A: HƯỚNG A — CỦNG CỐ KẾT QUẢ ÂM

> **Mục tiêu tổng:** Chứng minh kết quả âm KHÔNG do phương pháp đo lường yếu, bằng cách thử
> nhiều tầng biểu diễn text tinh vi hơn. Tất cả đều đi qua cùng pipeline để so sánh với v0.

### A2 — Negation-aware Keyword Matching ⭐ (làm đầu tiên — vá điểm yếu thực nhất)

**Lý do làm đầu:** Đây là điểm yếu thực sự được luận văn tự thừa nhận (mục 5.3.1):
*"nợ xấu giảm" và "nợ xấu tăng" đều tính là 1 hit "nợ xấu"*.

**Vị trí can thiệp:** `task9_kw_features.py::compute_raw_counts()`.

**Thiết kế kỹ thuật:**
1. Định nghĩa danh sách từ phủ định tiếng Việt: `["không", "chưa", "chẳng", "không còn",
   "giảm", "hạ", "thu hẹp", ...]` (cần tách rõ: phủ định phủ nhận vs. từ chỉ hướng giảm).
2. Khi match một keyword, kiểm tra cửa sổ ±N từ (N=3) xung quanh vị trí match.
3. Nếu có từ phủ định trong cửa sổ → không count vào keyword gốc, mà count vào một feature
   "flipped" (đảo polarity). Ví dụ: "nợ xấu giảm" → không tính `kw_nợ xấu`, tính
   `kw_nợ xấu_NEG` (polarity đảo).
4. Tạo cột features mới với hậu tố rõ ràng để `identify_feature_columns` nhận diện.

**Điểm cần cẩn thận:**
- Longest-first masking hiện có phải được giữ; negation check chạy SAU khi xác định span.
- Tránh double-flip (một số keyword đã mang sẵn nghĩa phủ định như "không chia cổ tức").
- Cần cập nhật `identify_feature_columns()` trong `task10_train.py` để cột `*_NEG` rơi vào
  nhóm keyword.

**Output:** `data/features/keyword_features_A2.csv` → `reports/model_comparison_A2.csv`.

**So sánh & phân tích bắt buộc:**
- Bảng: Config_A / Config_B / Config_C × 4 thuật toán, đặt cạnh v0 (Bảng 4.1).
- Δ(C−A) mới vs. Δ(C−A) cũ → negation có làm giảm nhiễu không?
- Kiểm tra riêng: các keyword hay bị phủ định nhất (nợ xấu, lợi nhuận, tăng trưởng) — bao
  nhiêu % số hit bị flip? (thống kê mô tả).
- Nhận xét: nếu Δ vẫn âm → bằng chứng mạnh hơn rằng vấn đề không phải do negation.

**Thời gian:** 3-5 ngày.

---

### A1 — Signed Sentiment Score theo nhóm chủ đề

**Vị trí can thiệp:** `task9_kw_features.py::compute_sentiment_scores()` (mở rộng).

**Thiết kế kỹ thuật:**
- Hiện tại chỉ có `pos_score`, `neg_score` toàn cục. Mở rộng thành score theo TỪNG nhóm
  chủ đề (A-F trong `KEYWORD_GROUPS`):
  - `sent_A` (kết quả kinh doanh) = Σ(pos nhóm A) − Σ(neg nhóm A), normalized theo news_count.
  - Tương tự `sent_B` (cổ đông), `sent_C` (tài chính), `sent_D` (hoạt động), `sent_E` (rủi ro).
- Kết quả: thay 71 features rời rạc → ~6-10 features tổng hợp có ý nghĩa kinh tế.

**Hai biến thể để so sánh:**
- A1a: chỉ dùng ~6 group sentiment scores (thay thế hoàn toàn 71 raw features).
- A1b: giữ 71 raw + thêm 6 group scores (bổ sung).

**Output:** `keyword_features_A1a.csv`, `keyword_features_A1b.csv`.

**So sánh & phân tích bắt buộc:**
- Bảng đối chiếu với v0. Câu hỏi: gộp nhóm có giảm nhiễu (ít feature hơn → ít overfit) không?
- So sánh số lượng features: v0 (71) vs A1a (~6) → có cải thiện balanced accuracy do giảm chiều?
- Phân tích: nếu A1a tốt hơn v0 nhưng vẫn thua Config_A → xác nhận text yếu về bản chất.

**Thời gian:** 2-3 ngày.

---

### A3 — News Velocity & Novelty Features

**Vị trí can thiệp:** Task mới hoặc mở rộng `task9_kw_features.py` (thêm hàm sau
`add_coverage_features`).

**Thiết kế kỹ thuật (features mới, tính theo (ticker, quarter)):**
- `news_velocity` = (news_count[q] − news_count[q−1]) / (news_count[q−1] + 1).
- `kw_novelty` = số keyword lần đầu xuất hiện ở kỳ q (chưa từng có ở các kỳ trước của ticker đó).
- `kw_entropy` = entropy của phân phối keyword trong kỳ (đo độ đa dạng chủ đề).
- `pos_neg_shift` = thay đổi sentiment_ratio so với kỳ trước.

**⚠️ Data leakage:** velocity/novelty dùng kỳ q−1 (quá khứ) → HỢP LỆ. Tuyệt đối không dùng q+1.

**Output:** `keyword_features_A3.csv`.

**So sánh & phân tích bắt buộc:**
- So với v0: velocity/novelty có phải tín hiệu mạnh hơn tần suất tĩnh không?
- SHAP trên Config_C mới: các feature velocity/novelty xếp hạng ở đâu?
- Nhận xét gắn với lý thuyết: "thông tin mới" (novelty) có giá trị hơn "lặp lại" không?

**Thời gian:** 3-5 ngày.

---

### A6 — LLM Zero-shot Sentiment (Gemini Flash) — tầng biểu diễn cao nhất của Hướng A

**Vị trí:** Script độc lập `pipeline/experiment_llm_sentiment.py`, ghi ra file annotation cố định.

**Thiết kế kỹ thuật:**
1. Với mỗi bài trong `all_news_processed.csv`, đưa nội dung point-in-time đã xử lý (`title`, `description`, `article_summary`, `key_facts` hoặc excerpt ngắn từ `full_text`) vào Gemini Flash để hỏi sentiment {positive/negative/neutral} + confidence.
2. **Lưu output cố định:** `data/news/annotated/llm_sentiment.csv` (input hash, output,
   model version, timestamp, temperature=0). Chạy MỘT LẦN.
3. Aggregate theo (ticker, quarter): `llm_pos_ratio`, `llm_neg_ratio`, `llm_net_sentiment`.
4. Đưa vào pipeline như keyword features.

**⚠️ Reproducibility:** file annotation phải commit vào repo. Ghi rõ model version trong luận văn.
**⚠️ Anti-lookahead:** prompt chỉ đánh giá polarity NỘI DUNG, cấm dự đoán giá.

**Output:** `keyword_features_A6.csv`.

**So sánh & phân tích bắt buộc — ĐÂY LÀ BẢNG THEN CHỐT CỦA HƯỚNG A:**

**Bảng tổng hợp 4 tầng biểu diễn text (Δ balanced accuracy C−A):**
| Thuật toán | v0 (raw freq) | A2 (negation) | A1a (group sent) | A6 (LLM sent) |
|---|---|---|---|---|
| LightGBM | −0.0231 | ? | ? | ? |
| Random Forest | −0.0187 | ? | ? | ? |
| XGBoost | −0.0032 | ? | ? | ? |
| Logistic Regression | −0.0303 | ? | ? | ? |

- Nếu tất cả cột đều âm/gần 0 → **robust null result**: "ngay cả LLM sentiment cũng không
  cải thiện → củng cố mạnh interpretation Semi-strong EMH".
- Nếu A6 có cải thiện nhỏ → phát hiện: "chỉ biểu diễn text đủ tinh vi mới có tín hiệu".

**Chi phí:** ~34k bài × Gemini Flash ≈ gần free (free tier) hoặc <$1 (GPT-4o-mini).
**Thời gian:** 3-5 ngày (gồm chạy API).

---

### A4, A5 (tùy chọn, nếu còn thời gian)
- **A4 (TF-IDF cross-ticker):** đã có một phần TF-IDF trong task9; mở rộng thành cross-ticker IDF.
- **A5 (PhoBERT embeddings):** nặng, chỉ làm nếu có GPU và muốn tầng biểu diễn thứ 5.

---

## PHẦN B: HƯỚNG B — TÌM TÍN HIỆU CÓ ĐIỀU KIỆN

> **Mục tiêu tổng:** Chuyển từ "có/không tín hiệu" → "khi nào có tín hiệu". Biến null finding
> thành nuanced finding.

### B3 — Segmentation theo Ngành & Vốn hóa ⭐ (làm đầu — rẻ, dễ có kết quả)

**Lý do làm đầu:** Rẻ nhất, dùng lại toàn bộ pipeline, luận văn đã gợi ý (mục 5.4.6:
"nợ xấu" có thể đặc biệt liên quan ngân hàng).

**Vị trí:** Script mới `pipeline/experiment_segmentation.py` (mẫu theo
`experiment_news_density.py`).

**Thiết kế kỹ thuật:**
1. Gán sector cho mỗi ticker (đã có mapping trong `config/pipeline_config.yaml` comments +
   phần mô tả 8 ngành trong luận văn 3.2.1).
2. Gán nhóm vốn hóa: VN30 (large-cap) vs HOSE-80 mở rộng (mid-cap).
3. Chạy lại train + kiểm định H2 RIÊNG cho từng nhóm:
   - Nhóm ngân hàng (nhiều mã nhất).
   - Nhóm mid-cap vs large-cap.
4. So sánh Δ(C−A) và kết quả kiểm định keyword giữa các nhóm.

**Giả thuyết kiểm định:** mid-cap ít analyst coverage → market phản ứng chậm → text có tín
hiệu hơn. "nợ xấu" mạnh hơn ở nhóm ngân hàng.

**Output:** `reports/segmentation_analysis.csv`, `reports/segmentation_keyword_sig.csv`.

**So sánh & phân tích bắt buộc:**
- Bảng Δ(C−A) theo từng sector và nhóm vốn hóa, đặt cạnh kết quả tổng hợp v0.
- Kiểm định H2 riêng nhóm ngân hàng: "nợ xấu" có đạt ý nghĩa trong subset không?
- ⚠️ Lưu ý statistical power: chia nhỏ → n giảm → BH-FDR càng khó vượt. Phải báo cáo n mỗi nhóm.
- Nhận xét: nếu tín hiệu mạnh hơn ở mid-cap → nuanced finding có giá trị.

**Thời gian:** 3-5 ngày.

---

### B1 — Distant Supervision (Short-term Price Return Labeling) ⭐⭐ (học thuật mạnh nhất)

**Vị trí:** Task mới `pipeline/experiment_distant_supervision.py`.

**Thiết kế kỹ thuật:**
1. **Tạo noisy label ở cấp độ TỪNG BÀI:**
   - Với mỗi bài đăng ngày d về ticker t: tính return của t trong [d+1, d+3] ngày giao dịch.
   - return ≥ +2% → label "positive"; ≤ −2% → "negative"; giữa → "neutral".
   - Nguồn giá: `data/prices/<TICKER>.csv`.
2. **Train sentiment classifier nhẹ** (Logistic/TF-IDF trên text_clean) với noisy label này.
3. **Dùng predicted probability** của classifier làm feature aggregate (ticker, quarter):
   `ds_pos_prob_mean`, `ds_net_sentiment`.
4. Đưa vào pipeline dự báo quý như keyword features.

**⚠️⚠️ DATA LEAKAGE — CỰC KỲ QUAN TRỌNG:**
- Sentiment classifier (bước 2) chỉ được train trên bài viết thuộc **giai đoạn train**
  (trước 2025Q1). Không được train trên bài của kỳ test.
- Noisy label dùng short-term return [d+1,d+3] để HUẤN LUYỆN classifier ở tầng bài viết — điều
  này KHÁC với target dự báo quý (q+1). Phải đảm bảo return dùng cho noisy label nằm TRONG kỳ q,
  không lấn sang kỳ q+1 (nếu bài đăng cuối kỳ, cắt tại ranh giới kỳ).
- Khi tạo feature cho kỳ q, chỉ dùng bài đăng trong kỳ q → không leak.

**Output:** `data/features/keyword_features_B1.csv`, `reports/distant_supervision_report.md`.

**So sánh & phân tích bắt buộc:**
- So với v0: distant-supervised sentiment có mạnh hơn keyword frequency không?
- **Granularity analysis:** kiểm định ở cấp độ bài viết (n~34k) — classifier có học được gì
  không (AUC trên noisy label)? Đây là góc mà quarterly aggregation của luận văn cũ đã làm mờ.
- Nhận xét gắn lý thuyết: nếu cấp độ bài có tín hiệu nhưng aggregate quý mất → "thông tin bị
  hấp thụ trong kỳ" (within-period absorption, mục 4.6.1 luận văn).

**Thời gian:** 1-2 tuần.

---

### B4 — Cross-sector News Spillover (tùy chọn)

**Thiết kế:** industry_sentiment score = sentiment trung bình toàn ngành trong kỳ, gán ngược
lại cho từng ticker trong ngành. Feature: `sector_pos_score`, `sector_news_count`.

**⚠️ Leakage:** chỉ dùng tin cùng kỳ q. Cẩn thận không dùng chính ticker đó để tránh trùng.

**So sánh:** Δ(C−A) khi thêm sector features vs v0. Spillover có bổ sung tín hiệu không?

**Thời gian:** 1 tuần.

---

### B5 — Anomaly Detection News Volume (tùy chọn, rẻ)

**Thiết kế:** feature binary `news_spike` = 1 nếu news_count[q] > mean + 2·std (tính trên
train). Kiểm tra kỳ có spike có dự báo tốt hơn không.

**Thời gian:** 2-3 ngày.

---

## PHẦN C: QUY TRÌNH SO SÁNH, NHẬN XÉT, PHÂN TÍCH (BẮT BUỘC MỌI THÍ NGHIỆM)

> Đây là phần đáp ứng trực tiếp yêu cầu "so sánh với luận văn hiện có, kết quả cũ, nhận xét,
> phân tích đầy đủ". Mỗi thí nghiệm PHẢI hoàn thành đủ 5 bước dưới đây.

### Bước 1 — Bảng so sánh trực tiếp với v0
Mọi thí nghiệm xuất một bảng có cấu trúc:
| Metric | v0 (cũ) | Thí nghiệm mới | Δ | Ý nghĩa |
|---|---|---|---|---|
| BA Config_A | (giữ nguyên) | (kiểm chứng không đổi) | ~0 | đối chứng |
| BA Config_C | ... | ... | ... | trọng tâm |
| Δ(C−A) | ... | ... | ... | H1 |
| # keyword đạt BH-FDR | 0/71 | ? | ? | H2 |
| % SHAP keyword | 32% | ? | ? | H3 |

### Bước 2 — Kiểm định ý nghĩa thống kê của sự khác biệt
- Dùng **McNemar test** (đã có `experiment_mcnemar.py`) để kiểm tra: dự báo của model mới có
  KHÁC BIỆT có ý nghĩa so với model cũ không? Chỉ số cải thiện nhỏ có thể chỉ là nhiễu.
- Báo cáo p-value McNemar cho cặp (v0 Config_C vs new Config_C).

### Bước 3 — Nhận xét gắn với 3 giả thuyết
Mỗi thí nghiệm phải trả lời rõ:
- **H1:** biểu diễn text mới có đảo ngược kết luận H1 không? (Δ(C−A) chuyển dương?)
- **H2:** có keyword/feature nào đạt ý nghĩa sau BH-FDR trong setup mới không?
- **H3:** đóng góp SHAP của text thay đổi thế nào?

### Bước 4 — Phân tích nguyên nhân (gắn lý thuyết luận văn)
Liên hệ kết quả với 3 giải thích ở mục 4.6.1 luận văn:
- Semi-strong EMH.
- Within-period absorption.
- Giới hạn biểu diễn văn bản/tần suất từ khóa sau khi đã có full text.
→ Kết quả mới ủng hộ/bác bỏ giải thích nào?

### Bước 5 — Kết luận cho luận văn
- Kết quả này viết vào mục nào của Chương 4? (mục mở rộng mới)
- Có thay đổi kết luận Chương 5 không? Nếu không → củng cố thế nào?

---

## PHẦN D: TIMELINE TỔNG HỢP

| Tuần | Công việc | Đầu ra |
|---|---|---|
| **0** (0.5 ngày) | Snapshot `reports/baseline_v0/` | Baseline đóng băng |
| **1** | A2 (negation) + A1 (group sentiment) | 2 bảng so sánh vs v0 |
| **2** | A6 (LLM sentiment) + A3 (velocity/novelty) | **Bảng 4 tầng biểu diễn text** |
| **3** | B3 (segmentation) | Bảng Δ(C−A) theo ngành/vốn hóa |
| **4** | B1 (distant supervision) — phần 1 | Sentiment classifier + granularity analysis |
| **5** | B1 — phần 2 + B4/B5 (nếu kịp) | Bảng so sánh distant supervision |
| **6** | Tổng hợp, McNemar, viết Chương 4 mở rộng | Mục mới trong `docs/luan_van.md` |
| **7+** | Hoàn thiện, cập nhật Chương 5 | Luận văn bản cập nhật |

**Ưu tiên nếu thời gian gấp:** A2 → A6 → B3 → B1 (bỏ A3, A4, A5, B4, B5).

---

## PHẦN E: CHECKLIST OUTPUT CUỐI CÙNG CHO LUẬN VĂN

Sau khi hoàn thành, Chương 4 luận văn sẽ có thêm:

- [ ] **Mục 4.7 — "So sánh các phương pháp biểu diễn đặc trưng văn bản"**
  - Bảng 4 tầng: raw freq / negation / group sentiment / LLM sentiment.
  - Kết luận: tất cả cho kết quả nhất quán (củng cố H1 âm) HOẶC phát hiện tầng nào có tín hiệu.
- [ ] **Mục 4.8 — "Kiểm định tín hiệu có điều kiện"**
  - Segmentation theo ngành/vốn hóa.
  - Distant supervision + granularity analysis cấp độ bài viết.
- [ ] **Cập nhật mục 4.6 (Thảo luận)** — bổ sung bằng chứng mới về 3 giải thích.
- [ ] **Cập nhật Chương 5:**
  - Nếu vẫn âm: "robust null result — đã loại trừ giả thuyết phương pháp yếu".
  - Nếu có tín hiệu điều kiện: bổ sung nuanced finding.
- [ ] **Cập nhật mục 5.4 (Hướng tương lai):** đánh dấu những hướng đã thực hiện.
- [ ] **Bảng tổng kết H1/H2/H3 cập nhật** (Bảng 5.1) với bằng chứng mới.

---

## PHẦN F: RỦI RO & CÁCH XỬ LÝ

| Rủi ro | Xác suất | Cách xử lý |
|---|---|---|
| Kết quả mới vẫn âm hoàn toàn | Cao | Đã lường trước — đây chính là "robust null result", vẫn có giá trị |
| Segmentation làm n quá nhỏ → không power | Trung bình | Báo cáo n rõ ràng; dùng raw p-value làm exploratory signal |
| Data leakage trong B1 | Trung bình | Review kỹ ranh giới kỳ; unit test cho hàm gán label |
| LLM API rate limit / chi phí | Thấp | Batch nhỏ; Gemini Flash free tier; lưu cache annotation |
| Feature mới không được nhận diện đúng Config | Trung bình | Cập nhật + test `identify_feature_columns()` |
| Reproducibility LLM | Trung bình | Đóng băng file annotation, commit, ghi model version |

---

## PHẦN G: BƯỚC TIẾP THEO NGAY

1. Tạo snapshot `reports/baseline_v0/` (Phần 0.2).
2. Bắt đầu A2 (negation-aware) — can thiệp `task9_kw_features.py::compute_raw_counts()`.
3. Sau mỗi thí nghiệm, hoàn thành đủ 5 bước Phần C trước khi sang thí nghiệm tiếp theo.
