# Annotation sample selection summary

- Input: `C:\Users\User\KLTN_KHTN\data\news\enriched\all_news_enriched.csv`
- Input SHA256: `c521184ebcd87cd95591779432304036e3047bea520d050a8fe2187b690559fe`
- Rows before dedup: 52790
- Rows after URL dedup: 45968
- Rows after content hash dedup: 44462
- Rows after title dedup: 43198
- Output rows: 150
- Output: `C:\Users\User\KLTN_KHTN\multi_llm_evidence_extraction\data\sample_news_for_annotation.csv`

## Bucket counts

| sample_bucket | value |
| --- | --- |
| debt_legal_governance_risk | 25 |
| earnings_business_result | 25 |
| market_sector_macro | 25 |
| dividend_capital | 20 |
| generic_company_announcement | 20 |
| project_business_expansion | 20 |
| noisy_low_confidence | 15 |

## Source counts

| source | value |
| --- | --- |
| cafef | 60 |
| vietstock | 44 |
| kinhtechungkhoan | 23 |
| vietnambiz | 15 |
| vnexpress | 4 |
| tnck | 4 |

## Match confidence counts

| match_confidence | value |
| --- | --- |
| exact | 82 |
| partial | 53 |
| none | 15 |

## Missing field counts in sample

| index | value |
| --- | --- |
| ticker | 0 |
| date | 0 |
| source | 0 |
| title | 0 |
| description | 0 |
| full_text | 0 |
| url | 0 |
| match_confidence | 0 |
