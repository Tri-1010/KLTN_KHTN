# Consensus family sensitivity report

## Method

- Annotators are grouped only when manifests provide a known `model_vendor`.
- Votes within each vendor family use canonical categorical voting semantics.
- Each family contributes at most one resolved vote per news item and field.
- Tied family votes produce `disagreement`; fewer than two resolved family votes produce `insufficient`.
- Missing, invalid, mixed, or unknown vendor metadata is excluded rather than treated as one family.
- News IDs, fields, vendors, and annotators use deterministic sorted ordering.
- Canonical consensus artifacts are read for comparison and never modified.

## Annotator family metadata

| annotator | model_vendor | manifest_status |
| --- | --- | --- |
| a | deepseek | ok |
| b | deepseek | ok |
| c | openai | ok |

## Canonical comparison

| field | total_rows | available_family_consensus | family_disagreement | family_insufficient | canonical_comparable | canonical_matches | canonical_mismatches | canonical_match_rate | canonical_available | canonical_status | artifact_schema_version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ticker_relevance | 150 | 133 | 15 | 2 | 133 | 133 | 0 | 1.0 | True | available | consensus_family_sensitivity_summary_v1 |
| materiality | 150 | 105 | 37 | 8 | 105 | 105 | 0 | 1.0 | True | available | consensus_family_sensitivity_summary_v1 |
| direction | 150 | 114 | 31 | 5 | 114 | 114 | 0 | 1.0 | True | available | consensus_family_sensitivity_summary_v1 |
| event_type | 150 | 125 | 21 | 4 | 125 | 125 | 0 | 1.0 | True | available | consensus_family_sensitivity_summary_v1 |
| time_horizon | 150 | 96 | 43 | 11 | 96 | 96 | 0 | 1.0 | True | available | consensus_family_sensitivity_summary_v1 |

## Artifacts

- Detail CSV: `C:\Users\User\KLTN_KHTN\multi_llm_evidence_extraction\outputs\consensus_family_sensitivity_detail.csv`
- Summary CSV: `C:\Users\User\KLTN_KHTN\multi_llm_evidence_extraction\outputs\consensus_family_sensitivity_summary.csv`
