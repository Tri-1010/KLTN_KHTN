# LLM Decision Card Rubric Summary

Status: `completed`

Provider: `gemini`

Rubric đo chất lượng hỗ trợ quyết định của card, không đo lợi nhuận và không chứng minh LLM tạo alpha.

## Mean scores by card type

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| llm_full_evidence | 25 | 5.00 | 5.00 | 5.00 | 4.96 | 5.00 | 5.00 | 5.00 | 0 | 0 |
| llm_ml_only | 25 | 1.28 | 1.00 | 4.72 | 2.04 | 4.56 | 2.12 | 1.16 | 43 | 114 |
| rule_based_baseline | 25 | 4.56 | 4.88 | 4.60 | 4.56 | 5.00 | 4.12 | 4.32 | 2 | 15 |

## Guardrails

- Scoring dùng `evidence_packs_initial.json`, không dùng audit pack có outcome.
- Initial decision cards không được chấm dựa trên realized return tương lai.
- So sánh `llm_full_evidence` với `llm_ml_only` chỉ phản ánh chất lượng giải thích/risk/monitoring trong rubric.
- Gemini 2.5 Pro vừa sinh card vừa chấm rubric; điểm 5.00 là kết quả automated model judge, có nguy cơ self-preference và không phải human ground truth.
- Scorer dùng full prompt-safe evidence cho mọi card type; điểm `llm_ml_only` vì vậy phản ánh cả lượng evidence bị loại trong ablation, không chỉ chất lượng diễn đạt.
