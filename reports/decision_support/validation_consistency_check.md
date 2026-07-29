# Validation consistency check — ML + LLM decision support thesis

## 1. Scope

Checked thesis/docs after generating decision-support spec, prompt-safe evidence packs, rule-based decision cards, monitoring events and full 25-case Gemini Pro LLM evaluation.

Main files checked:

- `docs/luan_van_ml_llm_decision_support.md`
- `docs/phu_luc_ml_llm_decision_support.md`
- `.kiro/specs/decision-support/requirements.md`
- `.kiro/specs/decision-support/design.md`
- `.kiro/specs/decision-support/tasks.md`
- `reports/decision_support/generated/evidence_packs_audit.json`
- `reports/decision_support/generated/evidence_packs_initial.json`
- `reports/decision_support/generated/evidence_packs_ml_only.json`
- `reports/decision_support/generated/decision_cards.md`
- `reports/decision_support/generated/outcome_reviews.md`
- `reports/decision_support/generated/monitoring_events.csv`
- `reports/decision_support/generated/monitoring_timeline.json`
- `reports/decision_support/generated/llm_cards_ml_only.jsonl`
- `reports/decision_support/generated/llm_cards_full_evidence.jsonl`
- `reports/decision_support/generated/llm_rubric_scores.csv`
- `reports/decision_support/generated/llm_rubric_summary.md`
- `reports/decision_support/generated/llm_generation_manifest.json`
- `reports/decision_support/generated/generated_summary.md`

## 2. Metrics consistency

Key metrics in thesis match `reports/source_evidence/tong_hop_bang_chung_tu_KLTN_MASTER.md`:

| Metric | Thesis/report value | Source evidence status |
|---|---:|---|
| Model net cumulative return | about 60.3% / 0.602964 | consistent |
| Buy-hold/equal-weight return | about 25.4% / 0.253502 | consistent |
| Net Sharpe | about 1.05 / 1.05171 | consistent |
| Walk-forward benchmark wins | 3/3 cutoffs | consistent |
| Robustness BA | 0.7607 | consistent |
| Robustness AUC | 0.8307 | consistent |
| VNINDEX outperformance | about 15.3 percentage points | consistent |
| Leakage audit | PASS, 0 future features | consistent |

Generated artifact metrics:

| Metric | Value |
|---|---:|
| Evidence packs | 25 |
| Prompt-safe full-evidence packs | 25 |
| ML-only packs | 25 |
| Periods | 2025Q1–2026Q1 |
| Top-K per period | 5 |
| Positive realized returns | 19 |
| Negative/neutral realized returns | 6 |
| Monitoring news events | 3,838 |
| Live Gemini LLM cards | 50 |
| Live Gemini rubric scores | 75 |

## 3. Leakage and point-in-time consistency

Status: pass for generated baseline artifacts, prompt packs and full 25-case LLM cards.

Checks:

- `evidence_packs_initial.json` strips `outcome_for_review_only`, realized return, review-only keys and future labels recursively.
- `evidence_packs_ml_only.json` also strips outcome/future fields and excludes `news_evidence` for ablation.
- Outcome reviews contain realized return and are clearly post-holding-period records.
- News evidence is filtered by `published_at <= decision_date` in the generator.
- Unit tests enforce no initial leakage and cutoff behavior.
- LLM generation manifest records `outcome_removed_from_prompt: true`.
- LLM prompts used prompt-safe packs, not audit packs.

Remaining caution:

- `evidence_packs_audit.json` and backward-compatible `evidence_packs.json` include `outcome_for_review_only`; do not use them for initial LLM prompting.
- Existing legacy `llm_decision_cards.md` is a prior 3-card Claude Code CLI/sonnet artifact. Current reported live result uses `llm_cards_*` Gemini artifacts.

## 4. LLM/API status

Status: full 25-case LLM generation completed.

Live full command:

```powershell
python .\scripts\generate_llm_decision_cards.py --provider gemini --model gemini-2.5-pro --variant both --max-packs 25 --score
```

Run metadata:

- Provider: `gemini`
- SDK: `google-genai`
- Requested model: `gemini-2.5-pro`
- Thinking: `not_sent`
- Effort: `not_sent`
- Temperature: `not_sent`
- Variants: `ml_only`, `full_evidence`
- Decision count: 25
- Generated cards: 50
- Generated rubric scores: 75
- Failures: 0

Outputs:

- `llm_cards_ml_only.md`
- `llm_cards_ml_only.jsonl`
- `llm_cards_full_evidence.md`
- `llm_cards_full_evidence.jsonl`
- `llm_rubric_scores.csv`
- `llm_rubric_summary.md`
- `llm_generation_manifest.json`

## 5. Rubric status

Status: full 25-case rubric scoring completed.

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `llm_full_evidence` | 25 | 5.00 | 5.00 | 5.00 | 4.96 | 5.00 | 5.00 | 5.00 | 0 | 0 |
| `llm_ml_only` | 25 | 1.28 | 1.00 | 4.72 | 2.04 | 4.56 | 2.12 | 1.16 | 43 | 114 |
| `rule_based_baseline` | 25 | 4.56 | 4.88 | 4.60 | 4.56 | 5.00 | 4.12 | 4.32 | 2 | 15 |

Interpretation:

- Full-evidence LLM cards score best across all 25 decision records because they can use ML/technical data, point-in-time news evidence, risk flags and data quality flags.
- ML-only LLM cards explain quantitative signals well, but score poorly on evidence/risk dimensions because the rubric evaluates card quality against full prompt-safe evidence packs.
- Rule-based baseline is useful and safe, especially for monitoring triggers, but less complete and less clear than full-evidence LLM cards.
- This is a decision-card quality result, not proof of improved return or LLM alpha.

## 6. Overclaim check

Status: pass.

The thesis and appendices avoid these claims:

- LLM creates alpha.
- LLM improves investment return.
- News layer improves forecast performance.
- Decision cards are real investment recommendations.
- Monitoring improves portfolio return without a separate backtest.

Safe framing used:

- ML technical signal is the quantitative core.
- News is an evidence/context layer.
- LLM is a controlled explanation and decision-support layer.
- Generated full-evidence LLM cards are best on the decision-card quality rubric, not on return.
- Rubric measures decision-card quality, not realized return.

## 7. Verification commands run

```powershell
python -m py_compile .\scripts\llm_provider.py .\scripts\generate_llm_decision_cards.py .\scripts\score_decision_cards.py
python -m pytest .\tests\test_decision_support.py -q
python .\scripts\generate_llm_decision_cards.py --provider gemini --model gemini-2.5-pro --variant both --max-packs 25 --score
```

Results:

- Decision-support tests: 20 passed.
- Verification on 2026-07-11 reused completed live artifacts; no provider API was called.
- Gemini 2.5 Pro generated and scored the cards, so rubric scores may contain self-preference and are not independent human ground truth.
- Live Gemini full card generation: completed, 50/50 cards.
- Live Gemini full scoring: completed, 75/75 scores.

## 8. Final status

Consistency status: pass for current thesis draft, Kiro spec, generated rule-based baseline artifacts, monitoring artifacts, provider-neutral Gemini support and full 25-case LLM evaluation.
