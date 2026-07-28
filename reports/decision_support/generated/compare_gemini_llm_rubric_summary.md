# LLM Decision Card Rubric Summary

Status: `completed`

Provider: `anthropic`

Rubric đo chất lượng hỗ trợ quyết định của card, không đo lợi nhuận và không chứng minh LLM tạo alpha.

## Mean scores by card type

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| llm_full_evidence | 25 | 3.88 | 3.52 | 3.96 | 3.84 | 2.44 | 4.04 | 3.44 | 42 | 93 |
| llm_ml_only | 25 | 2.36 | 1.36 | 3.92 | 2.48 | 2.52 | 3.60 | 2.32 | 88 | 112 |
| rule_based_baseline | 25 | 3.08 | 2.76 | 3.84 | 3.04 | 2.88 | 3.72 | 2.96 | 71 | 122 |

## Guardrails

- Scoring dùng `evidence_packs_initial.json`, không dùng audit pack có outcome.
- Initial decision cards không được chấm dựa trên realized return tương lai.
- So sánh `llm_full_evidence` với `llm_ml_only` chỉ phản ánh chất lượng giải thích/risk/monitoring trong rubric.
