# THESIS SUBMISSION — CANONICAL BUNDLE

## Đề tài

**Hệ thống hỗ trợ quyết định cổ phiếu dựa trên tín hiệu học máy và bằng chứng tin tức ngữ nghĩa có truy vết**

**English:** *Evidence-Grounded Stock Decision Support Using Machine Learning Signals and Semantic News Materiality*

## Trạng thái

Bundle này là đầu mối nộp và tái lập. Hai tài liệu chính:

- `proposal/de_cuong.md`
- `thesis/luan_van.md`

Kết quả so sánh keyword–semantic chỉ được đưa vào bản final sau canonical run `canonical_150_v7`. Run dùng cùng article spine, observation rows, target T+20, folds, model và backtest. Số thiếu hoặc không ước lượng được phải giữ trạng thái `Không khả dụng`, `not_estimable` hoặc `blocked`; không thay bằng số legacy.

## Nguồn canonical

1. Protocol: `../multi_llm_evidence_extraction/config/harmonized_comparison_v5.json`
2. Run artifacts: `../multi_llm_evidence_extraction/outputs/harmonized/canonical_150_v7/`
3. Run report: `../multi_llm_evidence_extraction/reports/harmonized/canonical_150_v7/`
4. Claim matrix: `governance/claim_evidence_matrix.md`
5. Reproduction: `reproduction/README.md`

## Phạm vi diễn giải

- Pseudo-label không phải human ground truth.
- Event association không phải causal effect.
- Top-K/backtest không chứng minh alpha.
- LLM card rubric không đo lợi nhuận hoặc chất lượng quyết định của con người.
- Hệ thống không phải công cụ giao dịch tự động hoặc khuyến nghị đầu tư.

## Legacy separation

Kết quả quarterly keyword, daily semantic, period-material sweep, B1 và technical-only backtest cũ dùng protocol khác. Chúng chỉ xuất hiện như bằng chứng lịch sử hoặc phụ lục, không được so trực tiếp với canonical same-sample run.
