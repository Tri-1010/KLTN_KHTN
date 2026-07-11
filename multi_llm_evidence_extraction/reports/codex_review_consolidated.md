# Codex review consolidation

## Runs

- Snapshot logic: `codex_review_snapshot_logic.md`
- Report renderer: `codex_review_report_renderer.md`
- Focused tests: `codex_review_focused_tests.md`
- Route: 9router model `cx/gpt-5.5`

## Findings applied

- Agreement keys now use `(news_id, ticker)` and ignore blank categorical labels.
- Degenerate single-class Cohen kappa now returns unavailable (`None`) instead of 1.0.
- Rule comparison requires `analysis_eligible`; missing eligibility makes comparison unavailable.
- Manual sanity summary reports partial schemas and missing columns.
- Renderer tolerates unknown/missing artifact metadata, includes artifact paths, and formats mean agreement to four decimals.
- Tests now cover split event gates, Top-K overlap/cost/net failures, multi-ticker agreement, blank labels, degenerate kappa, manual materiality normalization, partial manual schema, and missing eligibility.

## Findings verified but not changed

- Hardcoded annotators `a/b/c`: current study contract and artifacts explicitly define these three annotators.
- Duplicate `news_id` risk: current artifacts contain no duplicate `news_id` or `(news_id, ticker)` rows; composite-key protection still added.
- Agreement/manual/rule summaries absent from claim table: canonical final report renders them; claim table remains concise by design.

## Re-review after fixes

Sources:

- `codex_rereview_snapshot_logic.md`
- `codex_rereview_report_renderer.md`
- `codex_rereview_focused_tests.md`

Additional findings applied:

- Purge verification now checks declared `purge_trading_days` against business-day gap and rejects blank fold IDs.
- Top-K verification now rejects reversed holding periods and negative turnover/cost inputs.
- Tests now cover insufficient purge, missing fold IDs, reversed Top-K windows, and negative costs.
- Renderer overclaim about purged OOS was resolved by strengthening source verification; current real artifact still passes with three folds and 20-day purge.

Remaining review notes:

- Renderer integration test still uses sparse event/ML/Top-K fixtures and no annotation manifest fixture. Core dynamic summaries and current real artifact regeneration are exercised separately; these are coverage improvements, not confirmed runtime defects.
- Business-day purge uses weekday calendar, not exchange holiday calendar. It is stricter than calendar-day comparison but cannot prove HOSE-specific session counts without a trading-calendar artifact.

## Verification

```text
12 passed in 0.38s
real ML folds: 3
purge trading days: [20]
purged OOS verified: True
status: verified_from_fold_metadata
```

Final report regeneration succeeded. Canonical, negative-findings, and advisor-pitch reports are idempotent across repeated runs. Canonical report retains outcome-review count 114 and guarded exploratory wording.
