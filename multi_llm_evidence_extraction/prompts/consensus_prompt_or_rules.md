# Consensus rules v1

Consensus is deterministic. LLM consensus is optional and not used by default.

## Categorical fields

Fields: `ticker_relevance`, `is_stock_relevant`, `event_type`, `direction`, `materiality`, `time_horizon`.

- 3 annotators: accept majority label if at least 2 agree.
- 3 annotators, no majority: set label to `disagreement` and add field to `disagreement_fields`.
- 2 annotators: accept only exact agreement.
- 2 annotators disagree: set label to `disagreement`, set `requires_human_review = true`.
- 1 annotator: carry label but mark `agreement_level = unclear` and `requires_human_review = true`.

## Numeric fields

Fields: `materiality_score`, `expected_impact_score`, `uncertainty_score`, `novelty_score`, `reasoning_confidence`.

- Use median rounded to nearest integer.
- If max-min >= 2, add field to `high_disagreement_fields`.
- If no valid numeric values, set null and require human review.

## Evidence span

- If annotators provide exact same non-empty span, keep it.
- If spans differ but categorical consensus is strong, choose shortest non-empty span appearing in article text.
- Otherwise set null and add `missing_evidence` / `conflicting_evidence`.

## Human review triggers

Set `requires_human_review = true` if any condition holds:

- no categorical majority.
- high materiality with reasoning confidence <= 2.
- direction is `mixed`, `unclear`, or `disagreement`.
- relevance is `unclear`, `irrelevant`, or `disagreement`.
- evidence span is null.
- flags include boilerplate, ticker mismatch, ambiguous entity, insufficient evidence.
