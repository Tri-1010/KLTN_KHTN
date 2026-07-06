# Implementation Tasks — decision-support

## Task List

- [x] 1. Tạo spec `decision-support`
  - [x] 1.1 Tạo `.kiro/specs/decision-support/requirements.md`
  - [x] 1.2 Tạo `.kiro/specs/decision-support/design.md`
  - [x] 1.3 Tạo `.kiro/specs/decision-support/tasks.md`
  - [x] 1.4 Ghi rõ phạm vi: ML signal core, news evidence layer, LLM decision card, monitoring, outcome review
  - [x] 1.5 Ghi rõ guardrails: no alpha claim, no future leakage, rubric đo chất lượng card chứ không đo return

- [x] 2. Refactor `scripts/generate_decision_support_artifacts.py`
  - [x] 2.1 Thêm CLI args: `--top-k`, `--max-news-per-pack`, `--output-dir`, `--write-prompt-packs`
  - [x] 2.2 Tách output thành `evidence_packs_audit.json` và `evidence_packs_initial.json`
  - [x] 2.3 Giữ `evidence_packs.json` cho backward compatibility và ghi rõ trong manifest
  - [x] 2.4 Implement `strip_initial_prompt_fields()` để xóa recursive mọi field outcome/future
  - [x] 2.5 Implement `build_ml_only_pack()` và ghi `evidence_packs_ml_only.json`
  - [x] 2.6 Bổ sung source file SHA-256 vào manifest
  - [x] 2.7 Đảm bảo prompt-safe packs không chứa `outcome_for_review_only`, `realized_*`, `*_review_only`
  - [x] 2.8 Dùng enriched news fields đầy đủ: `article_summary`, `key_facts_json`, `risk_flags_json`, `event_type_enriched`, `lead`, `full_text_*`, `content_hash`
  - [x] 2.9 Giữ `published_at <= decision_date` cho initial evidence
  - [x] 2.10 Cập nhật `generated_summary.md` và `manifest.json`

- [x] 3. Nâng cấp `scripts/generate_llm_decision_cards.py` sang Anthropic SDK
  - [x] 3.1 Bỏ đường gọi `claude -p` qua `subprocess`
  - [x] 3.2 Dùng `anthropic.Anthropic()` zero-arg client
  - [x] 3.3 Default model = `claude-opus-4-8`, adaptive thinking, effort=high, không gửi temperature
  - [x] 3.4 Thêm CLI args: `--model`, `--max-packs`, `--decision-id`, `--variant`, `--offline`, `--score`, `--output-prefix`
  - [x] 3.5 Hỗ trợ generate `llm_ml_only`
  - [x] 3.6 Hỗ trợ generate `llm_full_evidence`
  - [x] 3.7 Ghi markdown + JSONL cho từng variant khi API auth chạy được
  - [x] 3.8 Ghi `llm_generation_manifest.json` với provider/model/request-id/prompt-hash/pack-hash/time
  - [x] 3.9 Nếu auth fail, ghi prompt packs offline và manifest `llm_run_pending_auth/offline`, không tạo fake card

- [x] 4. Tạo rubric scorer cho card types có artifact thật
  - [x] 4.1 Tạo `scripts/score_decision_cards.py`
  - [x] 4.2 Hỗ trợ score `rule_based_baseline`
  - [x] 4.3 Hỗ trợ score `llm_ml_only` nếu JSONL LLM tồn tại
  - [x] 4.4 Hỗ trợ score `llm_full_evidence` nếu JSONL LLM tồn tại
  - [x] 4.5 Dùng structured output JSON schema cho score 1–5 từng tiêu chí
  - [x] 4.6 Ghi `llm_rubric_scores.csv`
  - [x] 4.7 Ghi `llm_rubric_summary.md`
  - [x] 4.8 Ghi rõ major hallucination count và missing evidence ref count
  - [x] 4.9 Chỉ dùng `evidence_packs_initial.json` khi chấm initial cards

- [x] 5. Cập nhật `scripts/monitor_news_events.py`
  - [x] 5.1 Ưu tiên đọc `evidence_packs_audit.json`
  - [x] 5.2 Fallback sang `evidence_packs.json` nếu artifact cũ còn được dùng
  - [x] 5.3 Giữ logic enriched news/risk flags hiện có

- [x] 6. Thêm test `tests/test_decision_support.py`
  - [x] 6.1 `test_strip_initial_prompt_fields_removes_outcome`
  - [x] 6.2 `test_initial_pack_has_no_realized_or_future_tokens`
  - [x] 6.3 `test_news_evidence_cutoff_published_at_le_decision_date`
  - [x] 6.4 `test_ml_only_variant_excludes_news_evidence`
  - [x] 6.5 `test_full_evidence_uses_enriched_fields`
  - [x] 6.6 `test_manifest_records_model_metadata_and_hashes`
  - [x] 6.7 `test_offline_mode_writes_prompt_packs_not_fake_cards`
  - [x] 6.8 Không gọi API thật trong unit tests

- [x] 7. Validate code locally
  - [x] 7.1 Chạy `python -m py_compile .\scripts\generate_decision_support_artifacts.py .\scripts\generate_llm_decision_cards.py .\scripts\monitor_news_events.py .\scripts\score_decision_cards.py`
  - [x] 7.2 Chạy `python -m pytest .\tests\test_decision_support.py -q` — 7 passed
  - [x] 7.3 Chạy test regression liên quan: `tests/test_task4_preprocess.py`, `tests/test_run_pipeline.py` — 98 passed

- [x] 8. Regenerate decision-support artifacts
  - [x] 8.1 Chạy `python .\scripts\generate_decision_support_artifacts.py --write-prompt-packs`
  - [x] 8.2 Chạy `python .\scripts\monitor_news_events.py` — 3,838 monitoring events
  - [x] 8.3 Smoke test LLM run: API route trả `No active credentials for provider: anthropic`
  - [x] 8.4 Full run chưa chạy live vì auth/provider credential chưa sẵn sàng
  - [x] 8.5 Offline mode đã ghi 25 `ml_only` prompt packs và 25 `full_evidence` prompt packs; scorer offline ghi 25 rule-based scoring prompt packs

- [x] 9. Cập nhật docs/reports theo trạng thái thật
  - [x] 9.1 Update `docs/luan_van_ml_llm_decision_support.md`
  - [x] 9.2 Update `docs/phu_luc_ml_llm_decision_support.md`
  - [x] 9.3 Update `reports/decision_support/validation_consistency_check.md`
  - [x] 9.4 Update `reports/decision_support/generated/generated_summary.md`
  - [x] 9.5 Ghi rõ model/provider/version/temperature metadata
  - [x] 9.6 Ghi rõ initial prompts dùng stripped packs, không dùng outcome
  - [x] 9.7 Giữ guardrail chống overclaim

- [x] 10. Kiểm tra cuối
  - [x] 10.1 Xác nhận artifact tồn tại: spec files, audit/initial/ml-only packs, prompt packs, rubric prompt packs, manifest
  - [x] 10.2 Xác nhận no-leakage: initial pack không chứa outcome/future, news cutoff đúng qua unit tests
  - [x] 10.3 Xác nhận báo cáo nói đúng trạng thái thực tế: live LLM pending do auth/provider credential; offline prompt packs ready
