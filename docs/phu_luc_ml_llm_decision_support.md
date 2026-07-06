# Phụ lục luận văn: ML signal + LLM decision support

## Phụ lục A. Nguồn bằng chứng tái sử dụng

Nguồn tổng hợp chính: `reports/source_evidence/tong_hop_bang_chung_tu_KLTN_MASTER.md`.

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

So sánh đề xuất:

1. Rule-based template baseline.
2. LLM ML-only.
3. LLM full evidence.

Không được diễn giải điểm rubric thành lợi nhuận đầu tư. Muốn kết luận về return cần backtest riêng.

## Phụ lục F. Generated artifacts thực tế

Artifacts đã sinh bằng `scripts/generate_decision_support_artifacts.py`, `scripts/monitor_news_events.py`, `scripts/generate_llm_decision_cards.py --offline` và `scripts/score_decision_cards.py --offline`:

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
| `reports/decision_support/generated/llm_prompt_packs_ml_only.jsonl` | 25 prompt packs offline cho LLM ML-only. |
| `reports/decision_support/generated/llm_prompt_packs_full_evidence.jsonl` | 25 prompt packs offline cho LLM full-evidence. |
| `reports/decision_support/generated/llm_rubric_prompt_packs.jsonl` | 25 prompt packs offline để chấm rubric rule-based baseline hiện có. |
| `reports/decision_support/generated/llm_rubric_scores.csv` | Header-only vì live scorer chưa chạy; không có điểm giả. |
| `reports/decision_support/generated/llm_rubric_summary.md` | Summary ghi trạng thái `scoring_pending_offline`. |
| `reports/decision_support/generated/llm_generation_manifest.json` | Metadata LLM generation status/model/prompt packs. |
| `reports/decision_support/generated/generated_summary.md` | Tóm tắt run và guardrails. |
| `reports/decision_support/generated/manifest.json` | Metadata artifact run và source hashes. |

Run hiện tại:

- Số evidence pack: 25.
- Giai đoạn: `2025Q1` đến `2026Q1`.
- Top-K mỗi kỳ: 5.
- Positive realized return: 19.
- Negative/neutral realized return: 6.
- Monitoring news events: 3,838.
- LLM requested model: `claude-opus-4-8`.
- LLM settings: `thinking={"type":"adaptive"}`, `effort=high`, `temperature=not_sent`.
- Card hiện tại: rule-based baseline; live LLM output thật pending vì môi trường trả `No active credentials for provider: anthropic`.
- Không có LLM card/rubric score giả; prompt packs offline đã sẵn sàng để chạy lại khi credentials sẵn sàng.

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
- [ ] Chạy LLM live cho subset hoặc full 25 packs sau khi có active Anthropic provider credentials.
- [ ] Chấm rubric live rule-based vs LLM ML-only vs LLM full-evidence sau khi có output LLM thật.
