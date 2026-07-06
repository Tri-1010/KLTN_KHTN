# LLM Decision Card Rubric Summary

Status: `scoring_pending_offline`

Rubric đo chất lượng hỗ trợ quyết định của card, không đo lợi nhuận và không chứng minh LLM tạo alpha.

## Mean scores by card type

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| none | 0 | NA | NA | NA | NA | NA | NA | NA | NA | NA |

## Guardrails

- Scoring dùng `evidence_packs_initial.json`, không dùng audit pack có outcome.
- Initial decision cards không được chấm dựa trên realized return tương lai.
- So sánh `llm_full_evidence` với `llm_ml_only` chỉ phản ánh chất lượng giải thích/risk/monitoring trong rubric.
