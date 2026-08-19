# STRUCTURE KLTN

## 1. Định hướng chốt

### Tên hướng nghiên cứu đề xuất

**Hệ thống hỗ trợ quyết định cổ phiếu dựa trên tín hiệu học máy và bằng chứng tin tức ngữ nghĩa có truy vết**

Tên tiếng Anh đề xuất:

**Evidence-Grounded Stock Decision Support Using Machine Learning Signals and Semantic News Materiality**

### Luận điểm trung tâm

Nghiên cứu không xem LLM là mô hình dự báo giá độc lập. Kiến trúc được chốt theo hướng:

```text
Technical ML signal
+ LLM semantic material-event extraction
+ evidence pack có truy vết
+ constrained LLM decision card
+ monitoring dashboard
+ outcome review
```

Technical ML tạo tín hiệu định lượng và xếp hạng cổ phiếu. Semantic material-event chuyển tin tức thành bằng chứng có cấu trúc. LLM decision card tổng hợp tín hiệu và bằng chứng thành nội dung hỗ trợ quyết định. Dashboard quản lý monitoring, thay đổi bối cảnh và hậu kiểm.

### Phạm vi claim

Nghiên cứu được phép kết luận:

1. Keyword-frequency features không tạo giá trị dự báo gia tăng ổn định ngoài technical features trong các thiết lập đã kiểm tra.
2. LLM-extracted semantic material-event features có thể bổ sung thông tin cho technical indicators trong một số horizon, event filter và model configuration cụ thể.
3. Full-evidence LLM decision cards bám evidence và trình bày rủi ro tốt hơn ML-only cards theo automated rubric hiện có.
4. EvidenceTrace dashboard tăng khả năng truy vết signal, evidence, risk, monitoring trigger và outcome review.

Nghiên cứu không được kết luận:

- LLM luôn cải thiện dự báo cổ phiếu.
- Semantic features tạo alpha ổn định trên toàn thị trường.
- LLM card làm tăng lợi nhuận đầu tư.
- Pseudo-label là human ground truth.
- Event association là causal effect.
- Hệ thống là công cụ giao dịch tự động hoặc khuyến nghị đầu tư.

---

## 2. Cơ sở thực nghiệm để chọn hướng

### 2.1. Technical ML là lõi định lượng

Technical-only models là nhóm ổn định nhất trong các thí nghiệm cũ:

- Balanced Accuracy tốt nhất khoảng `0.76`.
- AUC khoảng `0.82–0.83`.
- Robustness trên 125 mã: Random Forest BA `0.7607`, AUC `0.8307`.
- Leakage audit: pass.
- Walk-forward và backtest cũ cho kết quả tích cực, nhưng vẫn phải trình bày giới hạn về slippage, liquidity, execution và target definition.

Vai trò trong đề tài mới:

- sinh probability;
- sinh rank;
- chọn Top-K candidate;
- cung cấp technical explanation;
- không dùng news để thay thế lõi technical.

### 2.2. Keyword-frequency là negative empirical finding

Đã thử:

- 6 nguồn, corpus khoảng 28 nghìn bài;
- full-text coverage 99.96%;
- tuần, 2 tuần, tháng, 2 tháng và quý;
- nhiều cutoff thời gian;
- phủ định, đồng nghĩa, longest-first masking;
- nhiều model;
- phân tích ngành và vốn hóa;
- kiểm định keyword với BH-FDR.

Kết quả:

- Keyword-only gần random.
- Technical + keyword không thắng technical-only ổn định.
- Không keyword nào đạt ý nghĩa sau BH-FDR trong các bộ 62–71 keyword được kiểm định.
- Full text và mở rộng nguồn không đảo kết luận.

Cách diễn giải:

> Trong setting đã kiểm tra, keyword-frequency representation không cung cấp incremental predictive value ổn định ngoài technical features. Kết quả này không chứng minh tin tức vô ích; nó cho thấy keyword count không biểu diễn đủ relevance, materiality, event context và timing.

### 2.3. LLM polarity sentiment đơn giản không đủ

A6 chỉ gán positive/negative/neutral rồi aggregate theo quý:

- Mean delta Hybrid−Technical: `−0.0061`.
- McNemar `p=0.6177`.

A7 semantic scorecard aggregate theo quý cũng không cải thiện ổn định:

- Pilot500: mean delta `−0.0046`, `p=0.1770`.
- DeepSeek pilot: mean delta `−0.0081`, `p=0.6989`.

Kết luận:

> Polarity sentiment hoặc scorecard aggregate theo kỳ không đủ để làm main predictive contribution.

### 2.4. Semantic material-event có bằng chứng hỗ trợ có điều kiện

Semantic extraction gồm:

- ticker relevance;
- materiality;
- event type;
- direction;
- uncertainty;
- novelty;
- evidence span;
- publication/effective date.

Các kết quả pooled đáng chú ý:

| Semantic configuration | Horizon | Model | Technical BA | Hybrid BA | Delta | CI | p |
|---|---:|---|---:|---:|---:|---:|---:|
| material events | T+20 | Random Forest | 0.5025 | 0.5343 | +0.0318 | [0.0094, 0.0555] | 0.0109 |
| direct material | T+10 | Random Forest | 0.4905 | 0.5216 | +0.0310 | [0.0020, 0.0579] | 0.0211 |
| material events | T+10 | Random Forest | 0.4905 | 0.5159 | +0.0254 | [0.0008, 0.0523] | 0.0488 |

Trên HOSE100, strict material filters mạnh nhất ở 1–2 tuần. Khi thêm macro/market context, một số cấu hình 1–2 tháng cải thiện. Tuy nhiên toàn sweep có cả kết quả dương và âm; mean delta gần zero và tồn tại multiple-comparisons risk.

Kết luận được phép:

> LLM semantic material-event features cung cấp complementary information cho technical indicators trong selected, interpretable configurations. Hiệu ứng có điều kiện, không phổ quát.

### 2.5. Event study hỗ trợ materiality ở T+5

Kết quả qua đủ BH-FDR và positive bootstrap CI:

- materiality high/medium so với low tại T+5;
- adjusted-return difference `+2.23%`;
- BH-adjusted `p=0.0457`;
- bootstrap CI `[0.91%, 3.66%]`.

Đây là exploratory association, không phải causal effect hoặc alpha.

### 2.6. Decision-support có giá trị ứng dụng

Artifacts đã có:

- 25 evidence packs;
- 25 ML-only packs;
- 25 rule-based cards;
- 25 ML-only LLM cards;
- 25 full-evidence LLM cards;
- 75 rubric scores;
- khoảng 3,838 monitoring events;
- 25 outcome reviews.

Common automated judge cho kết quả:

| Card type | Overall | Faithfulness | Hallucination | Risk | Monitoring |
|---|---:|---:|---:|---:|---:|
| Full evidence | 3.96 | 4.64 | 4.84 | 4.80 | 2.52 |
| ML only | 2.32 | 2.32 | 1.28 | 2.64 | 2.12 |
| Rule baseline | 3.00 | 3.12 | 2.88 | 3.04 | 2.80 |

Kết luận:

> Full-evidence cards tốt hơn ML-only và rule baseline về faithfulness, hallucination control và risk articulation theo automated rubric. Monitoring vẫn là điểm yếu cần cải thiện. Rubric không đo lợi nhuận hoặc human decision quality.

---

## 3. Kiến trúc hệ thống nghiên cứu

```text
┌───────────────────────────────────────────────────────────────┐
│ 1. Technical ML Signal Engine                                │
│ OHLCV → technical features → probability/rank/Top-K          │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. Semantic News Materiality Extractor                       │
│ News → relevance/materiality/event/direction/evidence span    │
└──────────────────────────────┬────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌────────────────────────────┐   ┌──────────────────────────────┐
│ 3A. Hybrid ML Evaluation   │   │ 3B. Evidence Pack Builder    │
│ technical + semantic       │   │ ML + technical + semantic    │
│ versus technical-only      │   │ + provenance/source IDs      │
└────────────────────────────┘   └──────────────┬───────────────┘
                                               ▼
                                ┌──────────────────────────────┐
                                │ 4. LLM Decision Card         │
                                │ thesis/evidence/risk/trigger │
                                └──────────────┬───────────────┘
                                               ▼
                                ┌──────────────────────────────┐
                                │ 5. EvidenceTrace Dashboard   │
                                │ monitor/update/review        │
                                └──────────────────────────────┘
```

---

## 4. Phân biệt semantic extractor và LLM decision card

### 4.1. Semantic extractor

Đơn vị đầu vào: một bài báo.

Đầu ra cấu trúc ví dụ:

```json
{
  "ticker_relevance": "direct",
  "materiality": "high",
  "event_type": "earnings",
  "direction": "support",
  "uncertainty_score": 2,
  "novelty_score": 4,
  "evidence_span": "..."
}
```

Vai trò:

- tạo semantic labels/features;
- lọc material events;
- hỗ trợ event study;
- làm input cho Hybrid ML;
- xây evidence pack.

### 4.2. LLM decision-card generator

Đầu vào:

- ML probability và rank;
- technical explanation;
- semantic evidence;
- source/evidence IDs;
- uncertainty và monitoring context.

Đầu ra:

- decision thesis;
- supporting evidence;
- risk factors;
- evidence gaps;
- monitoring triggers;
- review date;
- uncertainty/limitations.

Vai trò:

- tổng hợp và trình bày evidence;
- không tạo semantic label gốc;
- không trực tiếp dự báo return;
- không phát sinh dữ kiện ngoài evidence pack;
- không thay người dùng ra quyết định.

Semantic extraction và decision card có thể dùng cùng model hoặc khác model, nhưng là hai task và hai lớp đánh giá riêng.

---

## 5. Mục tiêu nghiên cứu

### Mục tiêu tổng quát

Xây dựng và đánh giá hệ thống hỗ trợ quyết định cổ phiếu kết hợp tín hiệu học máy từ dữ liệu kỹ thuật với bằng chứng tin tức semantic materiality có truy vết, dùng LLM để tạo decision card và hỗ trợ monitoring/hậu kiểm.

### Mục tiêu cụ thể

1. Đánh giá giới hạn của keyword-frequency features so với technical-only baseline.
2. Xây semantic material-event extraction schema cho tin tức tài chính tiếng Việt.
3. Đánh giá incremental value của semantic features khi kết hợp technical ML.
4. Xây point-in-time evidence packs có provenance và leakage guardrails.
5. So sánh rule-based, ML-only LLM và full-evidence LLM decision cards.
6. Xây dashboard thể hiện signal, evidence, risk, monitoring và outcome review.
7. Xác định giới hạn claim và điều kiện cần cho human validation/deployment.

---

## 6. Câu hỏi nghiên cứu

### RQ1 — Keyword representation

Keyword-frequency features có tạo incremental predictive value ngoài technical indicators không?

Kỳ vọng theo bằng chứng hiện có: không ổn định.

### RQ2 — Semantic representation

Semantic material-event features có biểu diễn relevance, materiality và event context tốt hơn keyword/rule baseline không?

Đánh giá bằng agreement, manual QC, rule comparison, provenance và error taxonomy.

### RQ3 — Hybrid predictive value

Technical + semantic material-event có cải thiện Technical-only trong primary horizon/configuration đã preregister không?

Đánh giá bằng paired OOS metrics, bootstrap CI, permutation test và BH-FDR.

### RQ4 — Event association

Materiality/direction có liên hệ với VNINDEX-adjusted returns tại T+1/T+5/T+10/T+20 không?

Chỉ kết luận association, không causal effect.

### RQ5 — LLM decision-card quality

Full-evidence LLM cards có tốt hơn ML-only cards và rule-based templates về faithfulness, hallucination control, risk articulation, monitoring và clarity không?

Automated rubric là evidence ban đầu; human evaluation là bước xác nhận mạnh hơn.

### RQ6 — Traceability

EvidenceTrace dashboard có duy trì được point-in-time lineage từ signal và news evidence tới card, monitoring event và outcome review không?

Đánh giá bằng schema validation, artifact hashes, source IDs, temporal boundaries và case audit.

---

## 7. Giả thuyết nghiên cứu

### H1 — Keyword incremental value

`Technical + Keyword` không cải thiện ổn định so với `Technical-only`.

Đây là negative empirical hypothesis được đánh giá bằng kết quả đã có.

### H2 — Semantic representation quality

Semantic material-event extraction cải thiện khả năng biểu diễn relevance/materiality/event context so với keyword/rule baseline.

Không đánh đồng agreement hoặc manual QC nhỏ với human ground truth.

### H3 — Conditional hybrid improvement

Trong primary preregistered configuration, `Technical + Semantic` cải thiện OOS performance so với `Technical-only`.

H3 chỉ pass khi đồng thời:

```text
same rows/folds/targets
AND status == ok
AND BH-adjusted p <= 0.05
AND bootstrap CI lower bound > 0
AND coverage/fold/provenance audits pass
```

### H4 — Decision-card evidence value

Full-evidence LLM decision cards đạt rubric score cao hơn ML-only và rule-based cards về faithfulness, hallucination control và risk articulation.

Không suy diễn H4 thành tăng return hoặc tăng human decision accuracy.

### H5 — Traceability

Hệ thống duy trì được liên kết có kiểm chứng từ input data tới ML signal, semantic evidence, decision card, monitoring event và outcome review mà không dùng future outcome trong initial decision artifacts.

---

## 8. Thiết kế thực nghiệm chính

### 8.1. Experiment A — Keyword negative baseline

So sánh:

- Technical-only;
- Keyword-only;
- Technical + Keyword.

Dùng kết quả đã có làm baseline và negative finding. Không cần mở rộng thêm keyword sweep nếu không phục vụ robustness cụ thể.

### 8.2. Experiment B — Semantic extraction quality

Đánh giá:

- annotation coverage;
- inter-run agreement;
- human sanity sample;
- rule-vs-semantic metrics;
- evidence-span validity;
- provenance completeness;
- family sensitivity.

Labels được gọi là pseudo-labels.

### 8.3. Experiment C — Primary Hybrid ML

Cần preregister một cấu hình chính trước khi chạy canonical:

**Đề xuất primary:**

```text
Universe: VN30 hoặc common validated universe
Event filter: core material
Relevance: direct
Horizon: T+10 hoặc 2 tuần
Model: Logistic Regression hoặc Random Forest cố định trước run
Baseline: Technical-only
Comparison: Technical + Semantic
```

**Đề xuất secondary:**

```text
Event filter: core material hoặc plus_macro_market
Horizon: T+20 hoặc 1 tháng
Model: fixed secondary model
```

Mọi configuration khác là sensitivity analysis, không đổi primary sau khi xem kết quả.

Metrics:

- Balanced Accuracy;
- AUC;
- F1;
- Brier score;
- log loss;
- Precision@K;
- rank IC;
- calibration/ECE.

Inference:

- paired OOS predictions;
- target-exit-aware folds;
- fold-local block bootstrap;
- block sign-flip/permutation;
- BH-FDR theo preregistered family;
- same-row claim gate.

### 8.4. Experiment D — Event study

So sánh:

- high/medium materiality vs low;
- support vs risk;
- direct vs indirect/market-wide khi đủ mẫu.

Horizons:

- T+1;
- T+5;
- T+10;
- T+20.

Dùng VNINDEX-adjusted return, non-overlap sample, BH-FDR và bootstrap CI.

### 8.5. Experiment E — LLM decision cards

Ba nhóm:

1. Rule-based template.
2. LLM với ML/technical evidence only.
3. LLM với full evidence pack: ML + technical + semantic news.

Rubric:

- faithfulness;
- hallucination control;
- ML explanation;
- risk articulation;
- monitoring quality;
- clarity/usefulness;
- evidence-reference completeness.

Cần tách generator và judge model nếu có thể. Human blinded review là bước ưu tiên.

### 8.6. Experiment F — Dashboard traceability

Audit theo selected cases:

- decision date;
- dữ liệu có trước decision date;
- ML signal provenance;
- semantic evidence IDs;
- card claim-to-evidence links;
- monitoring trigger;
- review-only outcome zone;
- artifact hashes và schema validation.

Dashboard evaluation tập trung vào traceability, completeness và temporal safety; không dùng visual quality để thay cho research evidence.

---

## 9. Cấu trúc dữ liệu và leakage guardrails

### Initial decision zone

Được phép chứa:

- dữ liệu giá/technical trước hoặc tại decision date;
- ML probability/rank;
- news published trước hoặc tại decision date;
- semantic labels/evidence spans;
- card thesis/risk/monitoring plan.

Cấm chứa:

- realized return;
- future label;
- benchmark return sau decision;
- outcome review;
- future monitoring event.

### Monitoring zone

Chỉ thêm event xuất hiện sau decision date và ghi rõ event timestamp, source, match confidence và trigger reason.

### Review zone

Chỉ dùng sau target exit date, chứa realized return, benchmark/excess return và outcome assessment. Không được feed ngược vào initial card của cùng decision.

---

## 10. Vai trò EvidenceTrace dashboard

Dashboard gồm các vùng:

1. **Signal overview** — ticker, decision date, probability, rank, Top-K status.
2. **Technical explanation** — chỉ báo chính và feature contribution.
3. **Semantic evidence** — relevance, materiality, event type, direction, evidence span, source.
4. **Decision card** — thesis, support, risks, gaps, monitoring triggers.
5. **Monitoring timeline** — signal deterioration, technical reversal, adverse/supporting news.
6. **Outcome review** — chỉ mở sau exit date; return, benchmark, thesis assessment.
7. **Provenance panel** — data hashes, schema versions, provider/model route, evidence IDs.

Dashboard là research prototype hỗ trợ audit và lifecycle management, không phải production trading terminal.

---

## 11. Đóng góp dự kiến của luận văn

### Đóng góp thực nghiệm

Chứng minh có hệ thống rằng keyword-frequency representation không tạo incremental predictive value ổn định trong setting đã kiểm tra.

### Đóng góp semantic

Xây schema và pipeline semantic material-event cho tin tức tài chính tiếng Việt, gồm relevance, materiality, event, direction và evidence span.

### Đóng góp predictive có điều kiện

Cung cấp bằng chứng rằng semantic material-event có thể bổ sung technical indicators trong selected short/medium horizons khi event/relevance filters được kiểm soát.

### Đóng góp decision support

Đề xuất và hiện thực kiến trúc ML-led, evidence-grounded decision support thay vì autonomous LLM forecasting.

### Đóng góp auditability

Tạo lineage từ dữ liệu → signal → evidence → card → monitoring → outcome review, với point-in-time guardrails và explicit claim gates.

---

## 12. Cấu trúc chương luận văn

### Chương 1 — Giới thiệu

- Bối cảnh dự báo và hỗ trợ quyết định cổ phiếu.
- Vấn đề của keyword-based news features.
- Động lực chuyển sang semantic materiality và decision support.
- Mục tiêu, RQ, giả thuyết, đóng góp và phạm vi.

### Chương 2 — Cơ sở lý thuyết và nghiên cứu liên quan

- Technical analysis và ML forecasting.
- Market efficiency và tốc độ phản ánh tin tức.
- Keyword/sentiment/text representation.
- Semantic event extraction và materiality.
- Explainable AI, evidence grounding và LLM hallucination.
- Decision-support systems, monitoring và outcome review.

### Chương 3 — Dữ liệu và phương pháp

- Price/news datasets và universe.
- Temporal alignment, targets và leakage controls.
- Technical feature pipeline.
- Keyword baseline.
- Semantic annotation schema và consensus.
- Hybrid ML design.
- Event-study methods.
- Evidence packs và LLM decision cards.
- Dashboard architecture.
- Statistical tests và claim gates.

### Chương 4 — Kết quả thực nghiệm

1. Technical ML baseline.
2. Keyword negative findings và robustness.
3. Semantic annotation quality.
4. Semantic event association.
5. Hybrid Technical + Semantic results.
6. Sensitivity theo horizon/event/relevance/model.
7. LLM decision-card rubric results.
8. Dashboard traceability case audit.
9. Null findings, failed gates và limitations.

### Chương 5 — Thảo luận

- Vì sao keyword count thất bại.
- Vì sao material-event filters hiệu quả hơn sentiment đơn giản.
- Conditionality và multiple-comparisons risk.
- Vai trò hợp lý của LLM trong tài chính.
- Giá trị của evidence-grounded decision support.
- External validity và human-validation gap.

### Chương 6 — Kết luận và hướng phát triển

- Trả lời từng RQ/H.
- Tóm tắt đóng góp.
- Giới hạn.
- Human labels và blinded card evaluation.
- Larger independent holdout.
- Daily execution/liquidity/slippage evaluation.
- Production governance và model monitoring.

---

## 13. Kết quả hiện tại theo từng claim

| Claim | Trạng thái hiện tại |
|---|---|
| Technical ML có signal định lượng | Supported trong bài toán theo quý cũ; cần phân biệt với target T+10/T+20 mới |
| Keyword tăng forecast | Not supported, robust negative finding |
| LLM polarity sentiment tăng forecast | Not supported ở aggregate theo quý |
| Semantic material-event có incremental value | Conditionally supported trong selected configurations |
| Semantic materiality liên hệ outcome T+5 | Một exploratory association qua BH-FDR |
| Semantic luôn tốt hơn technical | Not supported |
| Full-evidence card tốt hơn ML-only | Supported theo automated rubric |
| LLM card tăng return/human decision quality | Chưa được kiểm chứng |
| Dashboard cung cấp traceability | Supported ở mức technical validation/case audit |
| Hệ thống tạo alpha ổn định | Không được claim |

---

## 14. Việc cần hoàn thành trước khi chốt kết quả luận văn

### Bắt buộc

1. Chọn và preregister primary Hybrid configuration.
2. Chạy canonical harmonized comparison với 10,000 bootstrap/permutation draws.
3. Giữ cùng article universe, target, rows, folds và coverage giữa baseline/comparison.
4. Áp dụng BH-FDR và same-row claim gate.
5. Regenerate structured claim/report artifacts bằng explicit canonical run directory.
6. Chọn 3–5 dashboard case studies sạch, audit point-in-time evidence.
7. Báo rõ null/negative findings cùng positive findings.

### Ưu tiên cao

1. Mở rộng semantic annotation sample từ 150 lên 500 bằng run-scoped provenance.
2. Human-review semantic labels trên một tập blinded.
3. Human-review decision cards: rule vs ML-only vs full-evidence.
4. Cải thiện monitoring triggers vì automated rubric hiện cho điểm thấp.

### Không cần ưu tiên

- Mở rộng thêm keyword list không có giả thuyết mới.
- Chạy thêm hàng loạt configuration sau khi xem kết quả.
- Xây auto-trading hoặc multi-agent trading.
- Claim PhoBERT result nếu chưa có canonical report.

---

## 15. Câu kết luận đề xuất cho luận văn

> Canonical same-sample run so sánh keyword và semantic trên cùng article spine, T+20 target, rows, folds, Random Forest và matched Top-K. Primary semantic-minus-keyword Balanced Accuracy delta gần 0 và không đạt statistical gate; vì vậy chưa có đủ bằng chứng semantic cải thiện keyword trong primary preregistered setting. Kết quả này không phủ định giá trị semantic cho representation quality, evidence grounding, risk articulation và traceability. Trên cơ sở đó, luận văn đề xuất hệ thống hỗ trợ quyết định theo hướng ML-led và evidence-grounded: ML tạo tín hiệu cần kiểm tra, semantic extraction cấu trúc hóa bằng chứng tin tức, LLM decision card tổng hợp luận điểm và rủi ro có truy vết, còn dashboard hỗ trợ monitoring và outcome review. Hệ thống không được diễn giải như mô hình giao dịch tự động, bằng chứng causal hoặc nguồn alpha ổn định.

Bản nộp canonical: `thesis_submission/README.md`, `thesis_submission/proposal/de_cuong.md`, `thesis_submission/thesis/luan_van.md`. Mọi số same-sample phải đọc từ `canonical_150_v7` artifacts và bundle checksums; các track cũ giữ vai trò legacy evidence dưới protocol khác.

---

## 16. Tài liệu kết quả chính

- `reports/technical_ml_backtest_report.md`
- `reports/H1_experiment_report.md`
- `reports/H2_H3_validation_report.md`
- `reports/experiment_A6_report.md`
- `reports/distant_supervision_report.md`
- `reports/experiment_B1_report.md`
- `reports/experiment_B3_report.md`
- `reports/experiment_A7_pilot500_report.md`
- `reports/experiment_A7_pilot500_deepseek_report.md`
- `reports/llm_semantic_material_validation_summary.md`
- `reports/llm_semantic_vn30_material_expansion_summary.md`
- `reports/llm_semantic_hose100_findings_and_next_steps.md`
- `multi_llm_evidence_extraction/reports/event_window_stat_tests_report.md`
- `multi_llm_evidence_extraction/reports/ket_qua_luan_van_semantic_news_materiality.md`
- `reports/decision_support/danh_gia_pivot_ml_llm_decision_support.md`
- `reports/decision_support/generated/generated_summary.md`
- `reports/decision_support/generated/router_claude2_llm_rubric_summary.md`
