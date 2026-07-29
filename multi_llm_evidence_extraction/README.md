# Semantic News Materiality Study

Thư mục này dành cho hướng nghiên cứu đã chỉnh lại:

> Đánh giá đặc trưng tin tức có xét độ liên quan và trọng yếu trong hỗ trợ phân tích cổ phiếu Việt Nam.

Trọng tâm:

- Tin tức chứng khoán Việt Nam.
- Relevance / materiality / event type / direction / evidence span.
- ML signal làm baseline, decision candidate và lớp kiểm tra exploratory.
- So sánh keyword/rule baseline với semantic pseudo-labels.
- Phân tích vì sao keyword/sentiment/news-as-feature chưa cải thiện dự báo ổn định.
- Semantic signal audit bằng outcome windows T+1/T+5/T+20.
- Evidence card / claim ledger / outcome review framework cho hỗ trợ phân tích minh bạch.

Vai trò AI/LLM:

- Chỉ là công cụ annotation/extraction tạm thời khi chưa có human labels.
- Dùng để tạo pseudo labels/weak reference labels.
- Không phải ground truth.
- Không phải nội dung chính của luận văn.
- Không dùng để claim alpha hoặc khuyến nghị mua/bán.

Phương pháp đã hiệu chỉnh:

- Consensus chỉ gọi `unanimous` khi mọi categorical field và stock relevance đạt 3/3; 2/3 là `majority_vote`.
- Predictive/event analyses chỉ dùng rows `analysis_eligible`; tin thiếu giờ map sang phiên giao dịch kế tiếp.
- Semantic features dùng daily/rolling past-only; technical/keyword quarterly features lag một quý.
- ML dùng expanding walk-forward 3 folds, purge 20 phiên; predictions chỉ OOS. Report validator kiểm tra fold ID, test-window boundaries và business-day purge gap từ metadata.
- Event study dùng VNINDEX-adjusted return, non-overlap primary sample, BH-FDR và cluster-bootstrap CI.
- Top-K dùng cửa sổ T+20 không overlap, cost `0,50% × turnover`, Sharpe annualize `sqrt(252/20)`.
- Mọi kết quả ML/event/Top-K là exploratory; không claim causal impact, alpha hoặc khuyến nghị đầu tư.

Regenerate artifact/report:

```text
python multi_llm_evidence_extraction/scripts/run_semantic_annotation.py --reconstruct-legacy-manifests
python multi_llm_evidence_extraction/scripts/build_consensus_labels.py
python multi_llm_evidence_extraction/scripts/analyze_annotation_agreement.py
python multi_llm_evidence_extraction/scripts/evaluate_rule_vs_semantic.py
python multi_llm_evidence_extraction/scripts/build_semantic_features.py
python multi_llm_evidence_extraction/scripts/run_semantic_signal_audit.py
python multi_llm_evidence_extraction/scripts/run_event_window_stat_tests.py
python multi_llm_evidence_extraction/scripts/build_outperform_targets.py
python multi_llm_evidence_extraction/scripts/run_ml_outperform_experiment.py --fast-models
python multi_llm_evidence_extraction/scripts/run_topk_simulation.py
python multi_llm_evidence_extraction/scripts/select_case_studies.py
python multi_llm_evidence_extraction/scripts/generate_evidence_cards.py
python multi_llm_evidence_extraction/scripts/run_outcome_review.py
python multi_llm_evidence_extraction/scripts/generate_result_charts.py
python multi_llm_evidence_extraction/scripts/build_lineage_manifest.py
python multi_llm_evidence_extraction/scripts/write_claim_evidence_table.py
python multi_llm_evidence_extraction/scripts/write_final_reports.py
```

File chính và vai trò:

- `de_cuong_chi_tiet_multi_llm_evidence_extraction.md` — framing học thuật, câu hỏi `RQ-SM*`, giả thuyết `H-SM*`, primary/secondary scope; không phải report kết quả.
- `reports/ket_qua_luan_van_semantic_news_materiality.md` — report kết quả thực nghiệm canonical, đọc số từ structured artifacts và giữ null findings.
- `reports/claim_vs_evidence_table.md` — RQ–hypothesis–evidence matrix, claim gates, provenance, robustness availability, hashes và freshness.
- `outputs/report_lineage_manifest.json` — manifest byte-level cho input report: path, availability, size, mtime UTC và SHA256; missing optional artifacts không làm pipeline fail.
- `reports/codex_review_consolidated.md` — nhật ký review kỹ thuật lịch sử; không thay report kết quả hoặc lineage manifest.

Optional robustness readers dùng `placebo_pre_event_stat_tests.csv`, `consensus_family_sensitivity_summary.csv`, `ml_paired_daily_metrics_outperform.csv`, `ml_bootstrap_delta_outperform.csv`, `topk_random_null_summary.csv` và `topk_cost_sensitivity_summary.csv` khi có. Thiếu file được ghi `unavailable`, không được suy diễn thành test đã pass.

Kiểm tra report pipeline:

```text
python -m pytest tests/test_multi_llm_backtest_reports.py -q -p no:cacheprovider
python multi_llm_evidence_extraction/scripts/write_final_reports.py
```

Giới hạn: business-day purge validation chưa thay thế trading-calendar chính thức của HOSE; kết quả ML/event/Top-K vẫn exploratory. Ba annotation runs chỉ thuộc hai model families, nên không được diễn giải như ba hệ độc lập hoặc ba bằng chứng độc lập.
