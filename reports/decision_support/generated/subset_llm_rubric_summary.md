# LLM Decision Card Rubric Summary

Status: `completed`

Provider: `gemini`

Rubric đo chất lượng hỗ trợ quyết định của card, không đo lợi nhuận và không chứng minh LLM tạo alpha.

## Mean scores by card type

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| llm_full_evidence | 5 | 5.00 | 5.00 | 5.00 | 4.80 | 5.00 | 5.00 | 5.00 | 0 | 0 |
| llm_ml_only | 5 | 1.00 | 1.00 | 4.80 | 1.80 | 4.40 | 2.00 | 1.00 | 8 | 27 |
| rule_based_baseline | 5 | 3.60 | 4.80 | 4.20 | 4.40 | 5.00 | 3.20 | 3.40 | 0 | 7 |

## Guardrails

- Scoring dùng `evidence_packs_initial.json`, không dùng audit pack có outcome.
- Initial decision cards không được chấm dựa trên realized return tương lai.
- So sánh `llm_full_evidence` với `llm_ml_only` chỉ phản ánh chất lượng giải thích/risk/monitoring trong rubric.
