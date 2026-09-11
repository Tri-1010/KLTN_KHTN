# Rule vs semantic labels report

Semantic labels are controlled pseudo-label references, not human ground truth.
- Eligible consensus rows: 122 (122 unique news-ticker keys)
- Compared rows (analysis eligible): 122 (122 unique keys)
- Unique-key merge coverage over eligible consensus: 1.0000
- rule_direction vs consensus_direction: accuracy=0.3770, macro_f1=0.2282, n=122, unclear/disagreement rate=0.0000
- rule_event_type vs consensus_event_type: accuracy=0.1475, macro_f1=0.0865, n=122, unclear/disagreement rate=0.0000
- rule_materiality vs consensus_materiality: accuracy=0.2213, macro_f1=0.1595, n=122, unclear/disagreement rate=0.0000
- rule_relevance vs consensus_ticker_relevance: accuracy=0.6885, macro_f1=0.2090, n=122, unclear/disagreement rate=0.0000

## Error taxonomy

- keyword thiếu ngữ cảnh
- keyword không đo materiality
- ticker relevance sai
- market-wide bị đếm như direct
- boilerplate/full-text noise
- mixed direction
- event type overlap
