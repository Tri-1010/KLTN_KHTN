# LLM Decision Card Rubric Summary

Status: `completed`

Provider: `anthropic`

Rubric đo chất lượng hỗ trợ quyết định của card, không đo lợi nhuận và không chứng minh LLM tạo alpha.

## Mean scores by card type

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| llm_full_evidence | 25 | 4.64 | 4.84 | 4.08 | 4.80 | 2.52 | 4.36 | 3.96 | 0 | 71 |
| llm_ml_only | 25 | 2.32 | 1.28 | 3.96 | 2.64 | 2.12 | 3.24 | 2.32 | 90 | 148 |
| rule_based_baseline | 25 | 3.12 | 2.88 | 3.76 | 3.04 | 2.80 | 3.72 | 3.00 | 69 | 127 |

## Guardrails

- Scoring dùng `evidence_packs_initial.json`, không dùng audit pack có outcome.
- Initial decision cards không được chấm dựa trên realized return tương lai.
- So sánh `llm_full_evidence` với `llm_ml_only` chỉ phản ánh chất lượng giải thích/risk/monitoring trong rubric.
