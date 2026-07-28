# Requirements Document

## Introduction

Tính năng `decision-support` gom toàn bộ hướng đề tài trong `de_cuong_ml_llm_decision_support.md`: hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam dựa trên tín hiệu ML, news evidence, LLM decision card, monitoring và outcome review. Tính năng này không thay thế các spec huấn luyện/backtest/news cũ; nó dùng các artifact đã có làm đầu vào cho lớp hỗ trợ quyết định có kiểm soát.

Mục tiêu chính: biến tín hiệu dự báo thành decision record có thể giải thích, theo dõi và hậu kiểm, đồng thời đánh giá chất lượng LLM decision card bằng rubric thay vì claim LLM tạo alpha hoặc cải thiện return.

## Glossary

- **Decision_Support_System**: Tầng select → explain → monitor → update → review của luận văn.
- **ML_Signal_Engine**: Thành phần tái sử dụng `reports/signals.csv` và mô hình kỹ thuật Config_A để tạo xác suất, nhãn, rank và Top-K.
- **News_Evidence_Layer**: Thành phần dùng tin tức point-in-time làm bằng chứng định tính, không làm predictor chính.
- **Evidence_Pack**: Gói bằng chứng cho một decision gồm ML score, technical drivers, news evidence và data quality flags.
- **Audit_Pack**: Evidence pack đầy đủ cho hậu kiểm, được phép chứa `outcome_for_review_only`.
- **Initial_Prompt_Pack**: Evidence pack đã strip mọi trường outcome/future, dùng cho prompt tạo decision card ban đầu.
- **Decision_Card**: Luận điểm đầu tư có cấu trúc, có evidence references, không phải khuyến nghị đầu tư thực tế.
- **Card_Type**: Một trong `rule_based_baseline`, `llm_ml_only`, `llm_full_evidence`.
- **Monitoring_Event**: Sự kiện sau decision kích hoạt Keep / Watch / Review Required.
- **Outcome_Review**: Hậu kiểm sau holding period, lúc này mới được dùng realized return và benchmark/outcome.
- **Rubric_Scorer**: Thành phần chấm decision card theo 6 tiêu chí chất lượng hỗ trợ quyết định.

## Requirements

### Requirement 1: Gom scope decision-support thành spec riêng

**User Story:** Là nghiên cứu sinh, tôi muốn có một spec `decision-support` riêng, để mọi task liên quan tới hướng ML + LLM decision support nằm cùng một nơi.

#### Acceptance Criteria

1. WHEN spec được tạo, THE repository SHALL contain `.kiro/specs/decision-support/requirements.md`, `design.md`, and `tasks.md`.
2. THE spec SHALL reference thesis direction from `de_cuong_ml_llm_decision_support.md` without duplicating old ML/backtest/text-feature specs.
3. THE spec SHALL distinguish completed upstream work from remaining decision-support work.
4. THE spec SHALL frame LLM as explanation/decision-support layer, not a price forecaster.

### Requirement 2: Tái sử dụng ML signal làm lõi định lượng

**User Story:** Là người làm luận văn, tôi muốn decision-support layer dùng lại tín hiệu ML/backtest đã kiểm chứng, để không huấn luyện lại sai lệch và giữ kết quả nhất quán.

#### Acceptance Criteria

1. WHEN Evidence_Pack_Builder runs, THE system SHALL read ML signals from `reports/signals.csv`.
2. THE system SHALL include `pred_proba_up`, `pred_label`, `rank_in_period`, and `signal_class` for every decision.
3. THE system SHALL include technical snapshot and top drivers from `data/features/technical_features.csv`.
4. THE system SHALL not retrain or change ML model behavior inside decision-support generation.
5. THE generated artifacts SHALL record source files and source hashes for reproducibility.

### Requirement 3: Dùng full-text enriched news làm evidence layer

**User Story:** Là người đánh giá luận văn, tôi muốn decision card dùng evidence từ bài báo đầy đủ đã crawl bổ sung, để đánh giá chính xác hơn metadata-only title/description.

#### Acceptance Criteria

1. WHEN enriched news exists at `data/news/enriched/all_news_enriched.csv`, THE system SHALL prefer it over processed/matched legacy news.
2. THE News_Evidence_Layer SHALL include `article_summary`, `key_facts_json`, `risk_flags_json`, `event_type_enriched`, `lead`, `full_text_available`, `full_text_chars`, `content_hash`, and a capped `full_text_excerpt` when available.
3. THE system SHALL keep full article bodies out of default LLM prompts except capped excerpts to control token cost.
4. THE system SHALL calculate coverage flags for full text, summary, key facts, and ticker matching confidence.
5. THE system SHALL include only news with `published_at <= decision_date` in initial decision packs.

### Requirement 4: Tách audit pack và prompt-safe pack để chống rò rỉ dữ liệu

**User Story:** Là hội đồng phản biện, tôi muốn chắc chắn LLM không thấy outcome tương lai khi tạo decision card ban đầu.

#### Acceptance Criteria

1. THE system SHALL write an audit pack that may contain `outcome_for_review_only`.
2. THE system SHALL write an initial prompt pack that recursively removes `outcome_for_review_only` and future/outcome fields.
3. THE initial prompt pack SHALL not contain serialized tokens such as `realized`, `outcome_for_review_only`, or future labels.
4. THE initial decision-card prompt SHALL use only the initial prompt pack.
5. THE outcome review prompt SHALL be the only prompt allowed to use realized return/outcome fields.
6. Tests SHALL fail if initial prompt packs contain future/outcome leakage.

### Requirement 5: Sinh decision card theo ba nhóm so sánh

**User Story:** Là người làm thực nghiệm, tôi muốn so sánh rule-based baseline, LLM chỉ dùng ML, và LLM dùng full evidence, để đánh giá đóng góp của news evidence và LLM.

#### Acceptance Criteria

1. THE system SHALL preserve or regenerate `rule_based_baseline` cards from evidence packs.
2. THE system SHALL generate `llm_ml_only` cards from packs excluding `news_evidence`.
3. THE system SHALL generate `llm_full_evidence` cards from prompt-safe packs including news evidence.
4. THE LLM generator SHALL use the official Anthropic Python SDK for API calls, not OpenAI-compatible shims.
5. THE default API model SHALL be `claude-opus-4-8` unless overridden by CLI argument.
6. THE system SHALL record provider, requested model, response model, request id, max tokens, thinking/effort, prompt hash, pack hash, and generation timestamp.
7. IF API credentials are unavailable, THE system SHALL write offline prompt packs and mark LLM run pending rather than fabricating cards.

### Requirement 6: Chấm rubric decision card

**User Story:** Là người làm luận văn, tôi muốn chấm các decision card bằng rubric cố định, để báo cáo chất lượng hỗ trợ quyết định có thể so sánh.

#### Acceptance Criteria

1. THE Rubric_Scorer SHALL score every available card by `decision_id` and `card_type`.
2. THE score SHALL include faithfulness, hallucination_control, ml_explanation, risk_awareness, monitoring_usefulness, clarity_usefulness, and overall.
3. THE scorer SHALL flag major hallucinations and missing evidence references.
4. THE scorer SHALL use prompt-safe initial packs when scoring initial decision cards.
5. THE system SHALL output `llm_rubric_scores.csv` and `llm_rubric_summary.md`.
6. THE summary SHALL report mean score by criterion and card type.
7. THE summary SHALL state that rubric score measures card quality, not investment return improvement.

### Requirement 7: Monitoring và outcome review dùng đúng thời điểm

**User Story:** Là người dùng prototype, tôi muốn hệ thống phát hiện thay đổi sau decision và hậu kiểm sau holding period, để decision có vòng đời quản trị.

#### Acceptance Criteria

1. THE monitoring script SHALL read audit packs and enriched news to emit post-decision events.
2. THE monitoring logic SHALL classify actions as Keep / Watch / Review Required based on risk flags, event types, weak matching, or technical/ML triggers when available.
3. THE outcome review SHALL use realized return only after holding period.
4. THE generated reports SHALL distinguish initial evidence, monitoring events, and outcome review.

### Requirement 8: Cập nhật tài liệu luận văn và validation report

**User Story:** Là người nộp luận văn, tôi muốn docs phản ánh đúng trạng thái đã chạy LLM/rubric, để không còn placeholder hoặc claim sai.

#### Acceptance Criteria

1. AFTER successful LLM generation/scoring, THE docs SHALL remove outdated “LLM-run pending” statements.
2. THE docs SHALL include model/provider/version/temperature metadata from manifest.
3. THE docs SHALL include rubric summary table and limitations.
4. THE docs SHALL retain overclaim guardrails: no claim that LLM improves return or creates alpha.
5. IF LLM run is blocked by auth/rate limit, THE docs SHALL explicitly say pending and point to generated prompt packs.

### Requirement 9: Cung cấp analyst workspace có khả năng truy vết

**User Story:** Là analyst/nghiên cứu sinh, tôi muốn duyệt artifact lịch sử qua giao diện `select → explain → monitor → update → review`, để kiểm tra evidence, provenance, cảnh báo và outcome mà không trộn dữ liệu tương lai.

#### Acceptance Criteria

1. THE system SHALL provide a Vietnamese-first Streamlit research prototype in analyst mode, without trading, portfolio execution, target-price, allocation, or investment-advice actions.
2. THE Select and Explain screens SHALL use only prompt-safe initial evidence packs and SHALL label a source `Buy Candidate` signal as a model candidate, not a call to buy.
3. THE Monitor and Update screens SHALL require an explicit historical `as_of` timestamp and SHALL exclude monitoring events after that timestamp.
4. THE Review screen SHALL physically read a review-only bundle and SHALL expose realized return/outcome only after a holding-period-complete gate.
5. THE system SHALL display source artifact hash, schema/version, source path, provider/model/run provenance, data-quality flags, and pseudo-label warnings where applicable.
6. THE system SHALL show semantic consensus, evidence span, disagreement, and human-review flags without calling them human ground truth.
7. THE system SHALL present rubric scores as card-quality evaluation only, never return, alpha, causal impact, or investment performance.
8. THE system SHALL validate all UI runtime artifacts through a catalog pinned to completed source artifacts; legacy/pending manifests SHALL not override completed runs.
9. THE Overview screen MAY use one narrow fixed FireAnt Markets exception: a browser-only, display-only nested iframe whose exact source is `https://www.fireant.vn/Widgets/Markets`, with no ticker, URL, raw HTML, callback, or other runtime input. THE Monitor screen MAY additionally render the selected validated ticker through exact FireAnt Quote contract `https://www.fireant.vn/Widgets/Quote?symbols={TICKER}`, where `{TICKER}` is derived server-side from selected `decision_id`, normalized and checked against validated-bundle ticker allowlist. THE selected Quote SHALL always provide exact top-level fallback `https://fireant.vn/ma-chung-khoan/{TICKER}`. THE system SHALL NOT iframe the native ticker page or accept free-form ticker/provider URL. Both widgets SHALL be labeled current external display outside validated historical bundle, historical `as_of`, evidence, model, monitoring, review, evaluation and prompts. THE server SHALL NOT fetch, proxy, scrape, parse, callback, handle provider messages, write state, log provider content, or ingest provider content. Monitor technical analysis SHALL use only frozen initial `technical_snapshot`/`top_drivers` at `decision_date`; runtime current/partial-quarter recomputation is forbidden until price artifacts receive separate validation and provenance.

### Requirement 10: Chạy LLM live qua workflow xác nhận rõ

**User Story:** Là analyst, tôi muốn chọn provider/model và tạo card LLM trực tiếp từ evidence pack, để demo workflow thực tế nhưng vẫn giữ kiểm soát chi phí, leakage và provenance.

#### Acceptance Criteria

1. THE system SHALL require a manual provider/model selection from a configured allowlist, a prompt/pack preview, and explicit confirmation before every external API call.
2. THE system SHALL use the existing provider abstraction and official provider SDK path; API keys SHALL remain environment/server-side only and SHALL never appear in UI state, artifacts, logs, or browser output.
3. THE system SHALL submit one bounded live job at a time and SHALL record decision ID, variant, provider, requested/response model, vendor, request ID, pack hash, prompt hash, timestamps, usage if supplied, and failures.
4. THE system SHALL write each live run only under an isolated run directory and SHALL never overwrite canonical completed artifacts.
5. IF generation or scoring fails, THE system SHALL show an honest failure/offline-prompt state and SHALL not fabricate a card or score.
6. THE local-router route SHALL display request route separately from response-model vendor and SHALL not call `gpt-5.6-luna` a native Claude response.
7. THE initial LLM job SHALL be blocked if recursive leakage validation or news cutoff validation fails.

### Requirement 11: Xây validated UI bundle và kiểm thử boundary

**User Story:** Là người phản biện, tôi muốn UI chỉ nhận artifact đã validate và tách trust zone vật lý, để kiểm chứng không có outcome leakage hoặc provenance mismatch.

#### Acceptance Criteria

1. THE bundle builder SHALL emit separate initial, monitor, review, semantic, evaluation, and provenance payloads; UI SHALL not hide a shared audit payload client-side.
2. THE builder SHALL fail on initial/update fields or serialized tokens containing outcome/future values, invalid initial news cutoff, hash mismatch, malformed required record, or duplicate card-score identity.
3. THE builder SHALL require exactly 75 common-judge cross-score rows and complete producer/judge/run provenance before publishing an evaluation bundle.
4. THE builder SHALL use content hash then deterministic news ID for monitoring-to-consensus joins; title-only matching SHALL be forbidden.
5. Tests SHALL cover zone isolation, cutoff equality, as-of filtering, hash mismatch, score completeness, legacy manifest handling, provider allowlist, live-job failure state, and no-trading UI copy.
