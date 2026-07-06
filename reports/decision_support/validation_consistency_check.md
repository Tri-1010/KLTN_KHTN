# Validation consistency check — ML + LLM decision support thesis

## 1. Scope

Checked thesis/docs after generating decision-support spec, prompt-safe evidence packs, rule-based decision cards, monitoring events, offline LLM prompt packs and offline rubric prompt packs.

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
- `reports/decision_support/generated/llm_generation_manifest.json`
- `reports/decision_support/generated/llm_rubric_summary.md`
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
| ML-only prompt packs | 25 |
| Periods | 2025Q1–2026Q1 |
| Top-K per period | 5 |
| Positive realized returns | 19 |
| Negative/neutral realized returns | 6 |
| Monitoring news events | 3,838 |
| Offline LLM card prompts | 50 |
| Offline rubric scoring prompts | 25 |

These values are recorded in `reports/decision_support/generated/manifest.json`, `llm_generation_manifest.json` and `generated_summary.md`.

## 3. Leakage and point-in-time consistency

Status: pass for generated baseline artifacts and prompt packs.

Checks:

- `evidence_packs_initial.json` strips `outcome_for_review_only`, realized return, review-only keys and future labels recursively.
- `evidence_packs_ml_only.json` also strips outcome/future fields and excludes `news_evidence` for ablation.
- Outcome reviews contain realized return and are clearly post-holding-period records.
- News evidence is filtered by `published_at <= decision_date` in the generator.
- Unit tests enforce no initial leakage and cutoff behavior.
- LLM generation manifest records `outcome_removed_from_prompt: true`.

Remaining caution:

- `evidence_packs_audit.json` and backward-compatible `evidence_packs.json` include `outcome_for_review_only`; do not use them for initial LLM prompting.
- Existing legacy `llm_decision_cards.md` is a prior 3-card Claude Code CLI/sonnet artifact. Current run does not treat it as full LLM result.

## 4. LLM/API status

Status: live LLM generation pending due to credentials/provider state.

Observed smoke run:

- Command: `python .\scripts\generate_llm_decision_cards.py --variant both --max-packs 3 --output-prefix smoke`
- Requested provider: `anthropic`
- SDK: `anthropic-python`
- Requested model: `claude-opus-4-8`
- Thinking: `{"type":"adaptive"}`
- Effort: `high`
- Temperature: `not_sent`
- Result: no cards generated.
- Error: `No active credentials for provider: anthropic`.

Offline fallback completed:

- `llm_prompt_packs_ml_only.jsonl`: 25 prompts.
- `llm_prompt_packs_full_evidence.jsonl`: 25 prompts.
- `llm_generation_manifest.json`: status `llm_run_pending_offline`.

`ant auth status` was attempted but `ant` CLI is not installed or not on PATH in this shell. To run live generation later, configure active Anthropic credentials/provider, then rerun:

```powershell
python .\scripts\generate_llm_decision_cards.py --variant both --max-packs 25 --score
```

## 5. Rubric status

Status: rubric scoring prompt packs ready; live scoring pending.

- `scripts/score_decision_cards.py --offline` wrote `llm_rubric_prompt_packs.jsonl`.
- `llm_rubric_scores.csv` is header-only; no fake scores.
- `llm_rubric_summary.md` records `scoring_pending_offline`.
- Scoring uses `evidence_packs_initial.json`, not audit packs with outcome.
- Rubric measures decision-card quality, not realized return, LLM alpha or portfolio improvement.

## 6. Overclaim check

Status: pass.

The thesis and appendices avoid these claims:

- LLM creates alpha.
- LLM improves investment return.
- News layer improves forecast performance.
- Decision cards are real investment recommendations.
- Monitoring improves portfolio return without a separate backtest.
- Pending LLM prompt packs are live LLM results.

Safe framing used:

- ML technical signal is the quantitative core.
- News is an evidence/context layer.
- LLM is a controlled explanation and decision-support layer.
- Generated cards are rule-based baseline unless live LLM output exists.
- Rubric measures decision-card quality, not return.

## 7. Verification commands run

```powershell
python -m py_compile .\scripts\generate_decision_support_artifacts.py .\scripts\generate_llm_decision_cards.py .\scripts\monitor_news_events.py .\scripts\score_decision_cards.py
python -m pytest .\tests\test_decision_support.py -q
python -m pytest .\tests\test_task4_preprocess.py .\tests\test_run_pipeline.py -q
python .\scripts\generate_decision_support_artifacts.py --write-prompt-packs
python .\scripts\monitor_news_events.py
python .\scripts\generate_llm_decision_cards.py --variant both --max-packs 25 --offline
python .\scripts\score_decision_cards.py --offline
```

Results:

- Decision-support tests: 7 passed.
- Regression tests: 98 passed.
- Evidence artifacts: regenerated successfully.
- Monitoring events: regenerated successfully.
- Offline LLM prompt packs: generated successfully.
- Offline rubric prompt packs: generated successfully.

## 8. Final status

Consistency status: pass for current thesis draft, Kiro spec, generated rule-based baseline artifacts, monitoring artifacts and offline prompt packs.

Before final submission, still needed if thesis requires live LLM results:

1. Install/configure active Anthropic credentials/provider in this environment.
2. Run actual LLM decision-card generation on selected or all evidence packs.
3. Score rule-based, LLM ML-only and LLM full-evidence cards with rubric.
4. Replace pending/offline wording with completed live-run metadata only after real outputs exist.
