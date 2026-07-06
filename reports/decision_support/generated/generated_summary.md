# Generated Decision-Support Artifact Summary

## 1. Generation run

- Script: `scripts/generate_decision_support_artifacts.py`
- Output directory: `reports/decision_support/generated/`
- Source files:
  - `C:\Users\User\KLTN_KHTN\reports\signals.csv`
  - `C:\Users\User\KLTN_KHTN\data\features\technical_features.csv`
  - `C:\Users\User\KLTN_KHTN\data\news\enriched\all_news_enriched.csv`
- Top-K per period: 5
- Periods covered: 2025Q1, 2025Q2, 2025Q3, 2025Q4, 2026Q1
- Number of evidence packs: 25
- Positive realized return: 19
- Negative or neutral realized return: 6
- Monitoring news events generated: 3,838

## 2. Output files

| File | Purpose |
|---|---|
| `evidence_packs_audit.json` | Full audit packs; includes `outcome_for_review_only` for post-hoc review only. |
| `evidence_packs_initial.json` | Prompt-safe full-evidence packs for initial LLM decision cards. |
| `evidence_packs_ml_only.json` | Prompt-safe ML/technical-only ablation packs. |
| `evidence_packs.json` | Backward-compatible audit copy. |
| `evidence_packs_initial.jsonl` | JSONL convenience copy for prompt-safe full-evidence packs. |
| `evidence_packs_ml_only.jsonl` | JSONL convenience copy for ML-only packs. |
| `decision_cards.md` | 25 rule-based baseline cards generated from real evidence packs. |
| `outcome_reviews.md` | Outcome reviews that use realized return only after holding period. |
| `monitoring_cases_summary.csv` | Decisions, ranks, probabilities, news counts and outcomes. |
| `monitoring_events.csv` | 3,838 post-decision monitoring news events. |
| `monitoring_timeline.json` | Monitoring events grouped by decision ID. |
| `news_fulltext_coverage.csv` | Full-text extraction and summary/key-fact coverage by source. |
| `llm_rubric_scoring_template.csv` | Scoring sheet for rule-based and LLM card variants. |
| `llm_prompt_packs_ml_only.jsonl` | 25 offline prompts for LLM ML-only card generation. |
| `llm_prompt_packs_full_evidence.jsonl` | 25 offline prompts for LLM full-evidence card generation. |
| `llm_rubric_prompt_packs.jsonl` | 25 offline prompts for rubric scoring of cards currently available. |
| `llm_rubric_scores.csv` | Header-only because live scoring has not run; no fake scores. |
| `llm_rubric_summary.md` | Rubric summary with `scoring_pending_offline` status. |
| `llm_generation_manifest.json` | LLM generation status and model metadata. |
| `manifest.json` | Artifact run metadata and source hashes. |

## 3. LLM generation status

- Provider: `anthropic` via official `anthropic-python` SDK.
- Requested model: `claude-opus-4-8`.
- Thinking: `{"type":"adaptive"}`.
- Effort: `high`.
- Temperature: `not_sent`.
- Variants prepared: `ml_only`, `full_evidence`.
- Prompt packs prepared: 25 per variant.
- Live smoke run status: blocked by environment credential/provider state: `No active credentials for provider: anthropic`.
- `ant auth status` could not run because `ant` CLI is not installed or not on PATH in this shell.
- No live LLM cards were generated in this run.
- Existing legacy `llm_decision_cards.md` is a prior 3-card Claude Code CLI/sonnet artifact and is not used as current result.

## 4. Rubric scoring status

- Rubric scorer uses `evidence_packs_initial.json`, not audit packs with outcomes.
- Offline scoring prompt pack was written to `llm_rubric_prompt_packs.jsonl`.
- `llm_rubric_scores.csv` is header-only because live scoring has not run.
- `llm_rubric_summary.md` records `scoring_pending_offline`.
- Rubric measures decision-card quality, not investment return and not LLM alpha.

## 5. Leakage guardrails

- Initial prompt packs are stripped recursively before LLM generation.
- Outcome reviews explicitly use realized return only after holding period.
- News evidence in each initial pack is filtered with `published_at <= decision_date`.
- Full text is not injected wholesale into prompts; prompts use summaries/key facts/risk flags and short excerpts.
- Rule-based cards and LLM cards are decision-support artifacts, not investment recommendations.
