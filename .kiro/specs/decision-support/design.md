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

## EvidenceTrace analyst workspace

### Runtime architecture

```text
validated source artifact catalog
        |
        v
scripts/build_research_ui_bundle.py
  - hash/schema/count validation
  - recursive leakage scans
  - initial/monitor/review physical partition
  - semantic and rubric normalization
        |
        v
ui_artifacts/ (immutable generated bundle)
        |
        v
research_ui/ Streamlit analyst workspace
  Select -> Explain -> Monitor(as_of) -> Update(as_of) -> Review
        |
        +--> confirmed live LLM job only
               |
               v
reports/decision_support/generated/runs/<run_id>/
```

Streamlit reads only validated bundles. Pages never read audit packs, source CSV, raw secrets or provider responses directly.

### Trust zones

| Zone | Input | Required boundary |
|---|---|---|
| Initial | `evidence_packs_initial.json`, `evidence_packs_ml_only.json` | No outcome/review/post-decision data; news date <= decision date |
| Monitor | Initial reference plus monitoring timeline | Filter `event_date <= as_of`; no review outcome |
| Update | Initial reference plus filtered monitor events | Read-only delta; no outcome or auto-written thesis |
| Review | Review-only structured data and frozen history | Holding-period gate; never feeds Initial/Update |
| Evaluation | Cards + prompt-safe evidence + rubric | Quality only; never joins realized return |

### UI navigation

- **Select:** period/ticker/rank/data-quality filters. Source labels render as `Model candidate`, never a trade CTA.
- **Explain:** technical signal, top drivers, evidence inspector, data quality, card variants and provenance.
- **Monitor:** historical replay with mandatory `as_of`, `Watch`/`Review Required` rule reasons and semantic-quality indicators.
- **Update:** deterministic read-only comparison of initial evidence and valid new evidence.
- **Review:** post-hoc view only, outcome data after holding-period gate.
- **Evaluation:** separate Gemini self-judge, local-router judge and common local-judge cross-score provenance; no cross-judge provider ranking.
- **Provenance:** source catalog, SHA-256, model/vendor/run details and legacy/reconstructed warnings.

### Live LLM jobs

Live generation is manually initiated from a dedicated form. Analyst selects a catalog-allowed provider/model, decision ID and variant; UI previews prompt/pack hash and leakage validation, then requires explicit confirmation for external API use. A service reuses `scripts/llm_provider.py` and callable generation logic from `scripts/generate_llm_decision_cards.py`; it must not build shell commands from UI input.

Each job writes only to `reports/decision_support/generated/runs/<run_id>/` and persists a run manifest. Jobs are single-concurrency and bounded by configured card limit. API credentials stay environment-only. Failures create a clear failed/offline state, never a synthetic card.

### UI-safe contracts and non-claim policy

Bundle builder and UI use Pydantic DTOs for dataset manifest, candidate, initial decision, news evidence, monitoring event, update detail, review detail, semantic consensus, card record, evaluation record and live job state. `decision_id` is primary identity. News joins prefer `content_hash`, then deterministic `news_id`; title-only joins are rejected.

Every screen includes `Research prototype`, `No live market data`, and `Not investment advice`. UI text forbids Buy/Sell, target price, allocation and order placement. Rubric labels state card-quality only. Semantic labels state model-derived pseudo-label, not human ground truth. Status uses text/icon/color together and has keyboard/table alternatives.

### External market context

Overview uses one narrow fixed FireAnt Markets exception. `research_ui/components/fireant_vnindex.py` keeps exact no-argument `https://www.fireant.vn/Widgets/Markets` contract and exact native VNINDEX fallback.

Monitor additionally uses FireAnt's purpose-built Quote widget verified on 2026-07-28: `https://www.fireant.vn/Widgets/Quote?symbols={TICKER}`. `research_ui/components/external_market_context.py` normalizes a server-derived ticker, requires membership in validated candidate allowlist, builds exact Quote/native URL shapes and rejects extra query, fragment, credentials, port, path traversal, Unicode and unknown ticker input. `research_ui/components/fireant_selected_ticker.py` owns one browser-only iframe plus permanent top-level `https://fireant.vn/ma-chung-khoan/{TICKER}` fallback. Native ticker page is not iframe-embedded; current frame headers and login/cookie behavior are not treated as a stable integration contract. `Widgets/Markets` remains fixed VNINDEX macro context and is separated in its own Monitor expander.

Browser connects directly to FireAnt. Components are display-only and make no server request, proxy, scrape, response parse, callback, parent-message handler, session-state write, provider-content log, ingestion or artifact mutation. Provider content remains outside validated historical bundle, historical `as_of`, evidence packs, ML features, monitoring events, LLM/card/scorer prompts, review and evaluation. Failure leaves historical workspace usable and preserves native fallback.

Monitor has one identity source: global validated `decision_id` derives ticker for selected-record panel, Quote widget, historical technical panel and LLM workflows. No second ticker state exists. Technical panel projects full initial `technical_snapshot`, rule-based `top_drivers` and provenance with cutoff fixed at `decision_date`; monitoring retains separate `as_of`; FireAnt is current browser display; fresh RSS has `retrieved_at_utc`. Current/partial-quarter indicators are not computed at runtime because price artifact validation and comparable model semantics are not yet established.

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
