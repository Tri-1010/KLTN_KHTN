# Design Document

## Overview

`decision-support` là tầng prototype nghiên cứu nằm sau pipeline ML/news hiện có. Tầng này không thay đổi cách huấn luyện mô hình; nó đọc artifact đã có, tạo evidence pack point-in-time, sinh decision card có kiểm soát, theo dõi post-decision events, và hậu kiểm outcome.

Nguyên tắc thiết kế:

1. **ML là lõi định lượng.** Lấy score/rank/label từ `reports/signals.csv`.
2. **News là evidence layer.** Dùng full-text enriched news để giải thích/risk/monitoring, không claim news cải thiện forecast.
3. **LLM chỉ diễn giải evidence.** Prompt cấm dùng thông tin ngoài input và yêu cầu evidence references.
4. **Audit pack ≠ prompt pack.** Audit pack được phép chứa outcome; initial prompt pack tuyệt đối không chứa outcome/future fields.
5. **Đánh giá bằng rubric.** So sánh chất lượng card, không so sánh return do LLM.

## Architecture

```text
reports/signals.csv
      +
data/features/technical_features.csv
      +
data/news/enriched/all_news_enriched.csv
      |
      v
EvidencePackBuilder
      |
      +--> evidence_packs_audit.json
      |      includes outcome_for_review_only for review only
      |
      +--> evidence_packs_initial.json
      |      strips outcome/future fields recursively
      |
      +--> evidence_packs_ml_only.json
             strips news_evidence for ML-only ablation

Card Generation
      |
      +--> rule_based_baseline cards
      +--> llm_ml_only cards
      +--> llm_full_evidence cards

Rubric Scoring
      |
      +--> llm_rubric_scores.csv
      +--> llm_rubric_summary.md

Monitoring + Outcome Review
      |
      +--> monitoring_events.csv
      +--> monitoring_timeline.json
      +--> outcome_reviews.md
```

## Components

### EvidencePackBuilder

Implementation file:

- `scripts/generate_decision_support_artifacts.py`

Inputs:

- `reports/signals.csv`
- `data/features/technical_features.csv`
- `data/news/enriched/all_news_enriched.csv`
- fallback legacy news only if enriched news missing

Responsibilities:

- Group signals by period and select Top-K by `pred_proba_up`.
- Construct decision id: `{quarter_id}_{ticker}_{rank:02d}`.
- Attach ML signal: model name, probability, label, rank, signal class.
- Attach technical snapshot and top drivers.
- Select news where `date <= decision_date`.
- Prefer enriched fields for news evidence:
  - `article_summary`
  - `key_facts_json`
  - `risk_flags_json`
  - `event_type_enriched`
  - `lead`
  - `full_text_available`
  - `full_text_chars`
  - `content_hash`
  - capped `full_text_excerpt`
- Add data quality flags.
- Emit source file hash metadata.

Key functions to keep/reuse:

- `read_csv()`
- `parse_json_list()`
- `safe_float()`
- `short_text()`
- `signal_class()`
- `technical_direction()`

New helper functions:

- `sha256_file(path)`
- `strip_initial_prompt_fields(obj)`
- `build_ml_only_pack(pack)`
- `assert_no_initial_leakage(pack)`

### Pack variants

#### Audit pack

Output:

- `reports/decision_support/generated/evidence_packs_audit.json`

Contains:

- all evidence fields
- `outcome_for_review_only`
- guardrails metadata

Use cases:

- outcome review
- monitoring timeline
- research audit

#### Initial prompt pack

Output:

- `reports/decision_support/generated/evidence_packs_initial.json`

Contains:

- same decision evidence minus outcome/future fields

Forbidden recursively:

- `outcome_for_review_only`
- `realized_*`
- `*_review_only`
- future label/return fields

Use cases:

- initial LLM full-evidence card
- scoring initial cards

#### ML-only pack

Output:

- `reports/decision_support/generated/evidence_packs_ml_only.json`

Contains:

- decision identity
- ML signal
- technical snapshot
- top drivers
- non-news data quality flags
- guardrails

Excluded:

- `news_evidence`
- news-specific risk claims
- outcome/future fields

Use cases:

- LLM ML-only ablation.

### LLM Card Generator

Implementation file:

- `scripts/generate_llm_decision_cards.py`

SDK:

- official `anthropic` Python SDK
- `anthropic.Anthropic()` zero-arg client

Default request:

```python
client.messages.create(
    model="claude-opus-4-8",
    max_tokens=12000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[...],
)
```

No `temperature` is sent for Opus 4.8. Manifest records `temperature: not_sent`.

CLI:

```powershell
python .\scripts\generate_llm_decision_cards.py --variant both --max-packs 25 --score
```

Arguments:

- `--model`
- `--max-packs`
- `--decision-id`
- `--variant ml_only|full_evidence|both`
- `--offline`
- `--score`
- `--output-prefix`

Outputs:

- `llm_cards_ml_only.md`
- `llm_cards_full_evidence.md`
- `llm_cards_ml_only.jsonl`
- `llm_cards_full_evidence.jsonl`
- `llm_generation_manifest.json`
- optional `llm_raw_responses.jsonl`

Manifest fields:

- provider
- SDK surface
- requested model
- response model
- request id
- max tokens
- thinking
- effort
- temperature status
- prompt template hash
- evidence pack hash
- generated timestamp UTC
- card type
- decision ids
- success/failure state
- `outcome_removed_from_prompt`

Offline mode:

If API auth is unavailable, generator writes prompt packs:

- `llm_prompt_packs_ml_only.jsonl`
- `llm_prompt_packs_full_evidence.jsonl`

and manifest:

- `status: llm_run_pending_auth`

It must not create fake LLM outputs.

### Rubric Scorer

Preferred implementation:

- `scripts/score_decision_cards.py`

May also be invoked via:

```powershell
python .\scripts\generate_llm_decision_cards.py --score
```

Inputs:

- `evidence_packs_initial.json`
- `decision_cards.md` for rule-based baseline
- `llm_cards_ml_only.jsonl`
- `llm_cards_full_evidence.jsonl`
- `reports/decision_support/llm_evaluation_rubric.md`
- `reports/decision_support/llm_prompt_template.md`

Scoring criteria:

1. Faithfulness
2. Hallucination control
3. ML explanation
4. Risk awareness
5. Monitoring usefulness
6. Clarity/usefulness

Output:

- `llm_rubric_scores.csv`
- `llm_rubric_summary.md`

Structured output schema should constrain returned scores to integers 1–5 and require justification/issue fields. The scorer must use prompt-safe initial packs only.

### Monitoring

Implementation file:

- `scripts/monitor_news_events.py`

Current behavior already uses enriched news fields. Update pack input preference:

1. `evidence_packs_audit.json`
2. `evidence_packs.json`

Outputs:

- `monitoring_events.csv`
- `monitoring_timeline.json`

### Reports and thesis docs

Files updated after real run:

- `docs/luan_van_ml_llm_decision_support.md`
- `docs/phu_luc_ml_llm_decision_support.md`
- `reports/decision_support/validation_consistency_check.md`
- `reports/decision_support/generated/generated_summary.md`

Content rules:

- Only mark LLM run complete after actual API success.
- Record exact model/provider/temperature metadata.
- Include rubric summary.
- Do not claim LLM improves return.
- Do not claim news improves forecast.

## Data leakage controls

Initial generation prompt may use:

- `decision_id`
- `ticker`
- `decision_date`
- `period_id`
- `ml_signal`
- `technical_snapshot`
- `top_drivers`
- `news_evidence` filtered by `published_at <= decision_date`
- `data_quality_flags`
- `guardrails`

Initial generation prompt must not use:

- `outcome_for_review_only`
- `realized_period_return`
- q+1 label
- benchmark return after decision
- future articles after decision date
- outcome review text

Outcome review prompt may use outcome only after holding period and must label it as post-hoc.

## Error handling

Anthropic SDK calls should catch typed exceptions where practical:

- `anthropic.AuthenticationError`
- `anthropic.PermissionDeniedError`
- `anthropic.RateLimitError`
- `anthropic.APIStatusError`
- `anthropic.APIConnectionError`

Auth failure behavior:

- print actionable message: run `ant auth login` or set `ANTHROPIC_API_KEY`
- write prompt packs
- mark manifest pending

## Verification strategy

Unit tests focus on deterministic local logic, not API calls:

- pack stripping
- no leakage tokens
- news cutoff
- ML-only variant exclusion
- enriched fields present
- manifest metadata
- offline mode

Runtime verification:

```powershell
python -m py_compile .\scripts\generate_decision_support_artifacts.py .\scripts\generate_llm_decision_cards.py .\scripts\monitor_news_events.py
python -m pytest .\tests\test_decision_support.py -q
python .\scripts\generate_decision_support_artifacts.py --write-prompt-packs
python .\scripts\generate_llm_decision_cards.py --variant both --max-packs 3 --score
python .\scripts\generate_llm_decision_cards.py --variant both --max-packs 25 --score
```
