# Data Dictionary — Canonical Harmonized Study

## Keys

| Field | Meaning |
|---|---|
| `news_id` | ID ổn định của bài báo |
| `ticker` | Mã cổ phiếu chuẩn hóa uppercase |
| `article_date` | Ngày bài báo từ source artifact |
| `effective_date` / `date` | Phiên signal được phép dùng bài theo mapping policy |
| `target_exit_date` | Phiên benchmark thứ 20 sau entry |
| `fold_id` | Expanding OOS fold ID |
| `run_id` | ID artifact run; canonical là `canonical_150_v7` |

## Target

| Field | Meaning |
|---|---|
| `stock_return_T20` | Return cổ phiếu trên exact entry/exit sessions |
| `VNINDEX_return_T20` | Return benchmark trên cùng sessions |
| `excess_return_T20` | Stock return trừ VNINDEX return |
| `label_outperform_T20` | 1 nếu excess return > 0, ngược lại 0 |
| `target_status` | `ok` hoặc lý do không thể tính target |

## Feature families

| Prefix | Family |
|---|---|
| `tech_lag1q__` | Technical features lagged một quý |
| `common_` | Shared news coverage controls |
| `keyword_` | Context-aware curated keyword counts/ratios |
| `semantic_` | Consensus relevance/materiality/direction/event/score features |

## Configurations

| Config | Families |
|---|---|
| `A_technical` | technical |
| `E_technical_coverage` | technical + coverage |
| `B_technical_coverage_keyword` | technical + coverage + keyword |
| `C_technical_coverage_semantic` | technical + coverage + semantic |
| `D_technical_coverage_keyword_semantic` | technical + coverage + keyword + semantic |

## Backtest và inference

| Field | Meaning |
|---|---|
| `config = C_minus_B` | Paired Top-K delta: semantic trừ keyword; `stock_return_T20`, label và prediction fields không áp dụng nên là structural null |
| `status = paired_delta` | Row chênh lệch paired, không phải portfolio config độc lập |
| `candidate_count` | Số ticker trong candidate universe chung trước chọn Top-K |
| `test_end` | Cuối OOS fold; baseline prediction rows không tham gia Top-K nên có thể structural null |
| `n_paired_dates` | Số ngày/period có delta hợp lệ dùng cho estimate |
| `n_folds` | Số OOS folds có observation hợp lệ; canonical estimability yêu cầu đủ 3 |

## Denominator chain

- 150 sampled articles; 150 joined; 122 consensus-eligible; 114 mapped analytic articles.
- 5.656 panel-eligible rows là universe modeling trước temporal OOS filtering.
- 4.986 OOS observation keys trên 807 OOS dates là B/C aligned predictions mỗi model.
- 410 paired dates là denominator của primary inference sau metric validity checks.

## Status conventions

- `ok`: artifact/estimate satisfies structural prerequisites.
- `undefined`: metric mathematically undefined, thường do một lớp.
- `not_estimable` / `not_estimable_in_<mode>`: không đủ paired dates, folds hoặc Top-K periods.
- `not_estimable_degenerate_bootstrap`: bootstrap distribution không có variation; CI và p-value phải null.
- `paired_delta`: row chênh lệch C trừ B, không phải estimate status.
- `blocked`: thiếu input, hash mismatch hoặc integrity failure.
- Structural null: field không áp dụng cho loại row; không diễn giải là zero hoặc missing-data imputation.
- Không thay các trạng thái trên bằng 0.
