# Phụ lục hỗ trợ — ML signal + LLM decision support

> **Trạng thái tài liệu.** Tài liệu này là phụ lục lịch sử/supplementary. Thesis canonical là `docs/luan_van_hoan_thien_ml_llm.md`. Khi số liệu, RQ, trạng thái LLM/UI hoặc framing khác nhau, bản canonical và artifact ledger tại Phụ lục A của bản canonical được ưu tiên.
>
> **Không gộp track.** Các metric ML/backtest legacy dùng universe, split, horizon và cost khác không được dùng để kết luận cho track semantic purged OOS. Rubric luôn đo chất lượng decision card, không đo return/alpha; semantic consensus luôn là pseudo-label, không phải human ground truth.

## Phụ lục A. Nguồn bằng chứng tái sử dụng (legacy)

Nguồn canonical hiện hành: `multi_llm_evidence_extraction/reports/claim_vs_evidence_table.md`, các report semantic cùng thư mục, `reports/decision_support/validation_consistency_check.md` và `config/research_ui_catalog.yaml`.

Tham chiếu legacy `reports/source_evidence/tong_hop_bang_chung_tu_KLTN_MASTER.md` không còn là nguồn runtime/canonical; không dùng khi kiểm thesis final.

Các nhóm bằng chứng đã trích:

1. **ML technical signal**
   - Backtest HOSE-80: model net cumulative return khoảng 0.6030, benchmark buy-hold/equal-weight khoảng 0.2535.
   - Sharpe net khoảng 1.0517.
   - Walk-forward vượt benchmark ở 3/3 cutoff.
   - Robustness 125 mã HOSE+HNX: Balanced Accuracy 0.7607, AUC 0.8307.

2. **Leakage audit**
   - Kết luận PASS.
   - Không có future feature.
   - Không có label/return tương lai trong feature set.
   - Không có tương quan feature-label đáng ngờ vượt ngưỡng 0.95.

3. **News/text negative evidence**
   - Keyword/news features không cải thiện forecast ổn định.
   - H2 không có keyword significant sau BH-FDR.
   - LLM sentiment không cải thiện forecast trong thiết kế cũ.
   - Distant supervision có tín hiệu yếu cấp bài nhưng không tạo cải thiện rõ ở cấp quý.

Kết luận dùng trong luận văn: ML kỹ thuật làm lõi định lượng; news chuyển sang evidence layer; LLM không forecast mà tạo decision card có kiểm soát.

## Phụ lục B. Evidence pack schema

Schema chi tiết: `reports/decision_support/evidence_pack_schema.md`.

Trường chính:

| Nhóm | Nội dung |
|---|---|
| Metadata | `decision_id`, `ticker`, `decision_date`, `period_id`, `holding_horizon` |
| ML signal | `model_name`, `pred_proba_up`, `pred_label`, `rank_in_period`, `signal_class` |
| Technical snapshot | RSI, MACD, price-vs-SMA20, return, volume, volatility |
| Top drivers | Feature, value, direction, explanation |
| News evidence | Evidence ID, date, source, title, summary, `article_summary`, `key_facts`, `risk_flags`, event type, match confidence, full-text ref/hash |
| Data quality | News coverage, recent news flag, ticker matching confidence, full-text/summary/key-fact coverage, missing fields |
| Outcome review only | Realized return, outcome label; không dùng trong initial card |
| Guardrails | News cutoff, no investment advice, no future outcome in initial card |

Nguyên tắc chống leakage:

- `news_evidence.published_at <= decision_date`.
- Initial card không được dùng realized return.
- Outcome review tách riêng sau holding period.
- LLM chỉ dùng evidence pack được cung cấp.

## Phụ lục C. Decision card và outcome review schema

Schema chi tiết: `reports/decision_support/decision_card_schema.md`.

Decision card gồm:

1. Tóm tắt tín hiệu.
2. Luận điểm đầu tư chính.
3. Yếu tố hỗ trợ.
4. Yếu tố cần lưu ý/rủi ro.
5. Trigger theo dõi.
6. Thời điểm review.
7. Kết luận hỗ trợ quyết định.
8. Disclaimer.

Outcome review gồm:

1. Decision ban đầu.
2. Kết quả sau holding period.
3. Monitoring events.
4. Thesis assessment.
5. Bài học.

Điểm quan trọng: decision card ban đầu là point-in-time record; outcome review là post-hoc record. Hai phần không được trộn dữ liệu.

## Phụ lục D. Prompt templates

Prompt chi tiết: `reports/decision_support/llm_prompt_template.md`.

Các prompt chính:

| Prompt | Mục đích |
|---|---|
| System prompt chung | Ràng buộc LLM chỉ dùng evidence pack, không forecast, không hallucinate. |
| Initial decision card | Tạo card ban đầu từ evidence pack. |
| Thesis update | Cập nhật trạng thái khi có evidence mới sau decision date. |
| Outcome review | Hậu kiểm sau holding period, lúc này được dùng realized return. |
| Rubric scoring | Chấm chất lượng card theo tiêu chí 1–5. |

Ràng buộc bắt buộc:

- Không thêm dữ kiện ngoài evidence pack.
- Không cam kết lợi nhuận.
- Không dùng outcome tương lai trong initial card.
- Mỗi luận điểm chính phải dẫn evidence reference.
- Nếu evidence thiếu hoặc mixed, phải nói rõ.

## Phụ lục E. Rubric đánh giá LLM decision card

Rubric chi tiết: `reports/decision_support/llm_evaluation_rubric.md`.

Tiêu chí 1–5 điểm:

| Tiêu chí | Ý nghĩa |
|---|---|
| Faithfulness | Bám sát evidence pack. |
| Hallucination control | Không thêm dữ kiện ngoài input. |
| ML explanation | Giải thích probability, rank và technical drivers. |
| Risk awareness | Nêu rủi ro cụ thể, bám evidence/data quality. |
| Monitoring usefulness | Trigger rõ, đo được, có ngưỡng. |
| Clarity/usefulness | Rõ ràng, dễ đọc, dễ hậu kiểm. |

So sánh:

1. Rule-based template baseline.
2. LLM ML-only.
3. LLM full evidence.

Không được diễn giải điểm rubric thành lợi nhuận đầu tư. Muốn kết luận về return cần backtest riêng.

## Phụ lục F. Generated artifacts thực tế

Artifacts đã sinh bằng `scripts/generate_decision_support_artifacts.py`, `scripts/monitor_news_events.py`, completed Gemini/local-router runs và EvidenceTrace bundle workflow. Danh sách bên dưới là inventory lịch sử; run/provenance runtime phải lấy từ `config/research_ui_catalog.yaml`:

| File | Vai trò |
|---|---|
| `reports/decision_support/generated/evidence_packs_audit.json` | 25 audit evidence pack; có `outcome_for_review_only` cho hậu kiểm. |
| `reports/decision_support/generated/evidence_packs_initial.json` | 25 prompt-safe full-evidence packs; outcome/future fields đã strip. |
| `reports/decision_support/generated/evidence_packs_ml_only.json` | 25 ML/technical-only ablation packs. |
| `reports/decision_support/generated/evidence_packs.json` | Backward-compatible audit copy. |
| `reports/decision_support/generated/decision_cards.md` | 25 rule-based baseline decision card. |
| `reports/decision_support/generated/outcome_reviews.md` | 25 outcome review sau holding period. |
| `reports/decision_support/generated/monitoring_cases_summary.csv` | Bảng tổng hợp decision/outcome. |
| `reports/decision_support/generated/monitoring_events.csv` | 3,838 monitoring news events sau decision date. |
| `reports/decision_support/generated/monitoring_timeline.json` | Timeline event theo decision ID. |
| `reports/decision_support/generated/llm_prompt_packs_ml_only.jsonl` | Prompt packs offline cho LLM ML-only. |
| `reports/decision_support/generated/llm_prompt_packs_full_evidence.jsonl` | Prompt packs offline cho LLM full-evidence. |
| `reports/decision_support/generated/llm_cards_ml_only.md` / `.jsonl` | 25 live Gemini Pro cards dùng ML/technical-only packs. |
| `reports/decision_support/generated/llm_cards_full_evidence.md` / `.jsonl` | 25 live Gemini Pro cards dùng full-evidence prompt-safe packs. |
| `reports/decision_support/generated/llm_rubric_scores.csv` | 75 live Gemini Pro rubric scores: rule-based, ML-only, full-evidence. |
| `reports/decision_support/generated/llm_rubric_summary.md` | Full rubric summary, status `completed`. |
| `reports/decision_support/generated/llm_generation_manifest.json` | Metadata live generation/model/rubric status. |
| `reports/decision_support/generated/generated_summary.md` | Tóm tắt run, guardrails và full rubric. |
| `reports/decision_support/generated/manifest.json` | Metadata artifact run và source hashes. |

Runtime/provenance completed theo `config/research_ui_catalog.yaml`:

- Số evidence pack: 25; giai đoạn `2025Q1` đến `2026Q1`; Top-K mỗi kỳ: 5.
- Monitoring news events: 3.838; review-only decision records: 25 trong UI bundle; semantic outcome-review labels: 114 ở semantic track. Không dùng các outcome này cho initial card.
- Gemini run `gemini-full-2026-07`: Google `gemini-2.5-pro`, 25 `ml_only` cards, 25 `full_evidence` cards, 75 self-judge scores. Full rubric overall: `llm_full_evidence` 5,00, `rule_based_baseline` 4,32, `llm_ml_only` 1,16.
- Local-router run `local-router-claude2-2026-07`: request Anthropic-compatible `claude-opus`, response `gpt-5.6-luna`, OpenAI-vendor; 25 cards/variant và 75 rubric scores. Không gọi response này là Claude native.
- Common-judge run `common-local-judge-gemini-cards-2026-07`: chấm chéo 75 Gemini cards bằng local-router response `gpt-5.6-luna`.
- Mỗi rubric chỉ đo card quality. So sánh tuyệt đối score giữa judge/run khác nhau bị cấm; không claim LLM tạo alpha hoặc cải thiện return.

## Phụ lục G. Monitoring case studies

Chi tiết: `reports/decision_support/monitoring_review_cases.md`.

Case đại diện:

| Case | Decision record | Mục đích minh họa |
|---|---|---|
| A | `2025Q2_STB_01` | ML đúng, thesis được hỗ trợ. |
| B | `2026Q1_DPM_03` | ML sai, monitoring có warning. |
| C | `2025Q3_KDH_04` | Outcome dương nhưng evidence cần thận trọng. |
| D | `2025Q2_VND_05` | News/event trái chiều với ML signal. |
| E | `2025Q4_VBB_05` | Tín hiệu yếu cần review sau khuyến nghị. |

Các case này chỉ minh họa vòng đời quyết định. Không dùng 5 case để claim monitoring cải thiện return toàn danh mục.

## Phụ lục H. Checklist trước bản nộp cuối

- [x] Chuẩn bị prompt packs cho LLM ML-only và LLM full-evidence.
- [x] Chuẩn bị prompt packs chấm rubric cho card hiện có.
- [x] Ghi model/provider, version, temperature, ngày chạy trong manifest.
- [x] Kiểm tra initial prompt packs không chứa realized return/outcome/future fields.
- [x] Kiểm tra news cutoff đúng `published_at <= decision_date` bằng unit tests.
- [x] Kiểm tra full-text coverage, summary/key-fact coverage và bảo đảm initial prompt không nhúng toàn bộ `full_text` mặc định.
- [x] Kiểm tra mọi số liệu ML/backtest khớp source evidence ở validation report.
- [x] Ghi disclaimer: nghiên cứu học thuật, không phải khuyến nghị đầu tư.
- [x] Không claim LLM tạo alpha hoặc cải thiện return nếu chưa có backtest riêng.
- [x] Chạy LLM live full 25-case bằng Gemini Pro.
- [x] Chấm rubric live rule-based vs LLM ML-only vs LLM full-evidence cho full 25-case.
