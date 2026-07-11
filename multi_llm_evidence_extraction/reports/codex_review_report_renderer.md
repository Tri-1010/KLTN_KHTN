Review limited to requested files. No files modified.

**Findings**
- Medium — `multi_llm_evidence_extraction/scripts/write_final_reports.py:57`: artifact handling assumes every `snapshot["artifacts"]` key exists in hardcoded `summaries`; added/missing artifact key causes `KeyError` before “unavailable” fallback can render.
- Medium — `multi_llm_evidence_extraction/scripts/write_final_reports.py:62`: artifact metadata uses required dict keys; missing `sha256`, `modified_utc`, `latest_upstream_utc`, or `freshness` crashes report generation instead of reporting missing data.
- Medium — `multi_llm_evidence_extraction/scripts/write_final_reports.py:133`: artifact table omits canonical artifact path; report only shows artifact names/hashes. Generated report also lacks paths at `multi_llm_evidence_extraction/reports/ket_qua_luan_van_semantic_news_materiality.md:97`.
- Low — `multi_llm_evidence_extraction/scripts/write_final_reports.py:109`: raw Python formatting leaks into report (`0.8400000000000001`, dict reprs), visible at `multi_llm_evidence_extraction/reports/ket_qua_luan_van_semantic_news_materiality.md:46`.
- Low — `multi_llm_evidence_extraction/scripts/write_final_reports.py:11`: `OUTPUT_DIR` and `ROOT` imported but unused; likely intended for canonical path reporting, now dead imports.