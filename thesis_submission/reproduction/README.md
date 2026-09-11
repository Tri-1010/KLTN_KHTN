# Reproduction

Chạy từ root repository bằng PowerShell hoặc shell tương đương.

## 1. Tests tập trung

```text
python -m pytest tests/test_multi_llm_harmonized_comparison.py tests/test_multi_llm_backtest_reports.py -q -p no:cacheprovider
```

## 2. Canonical build

Các lệnh này tạo run mới một lần. Không chạy lại nếu `canonical_150_v7` đã tồn tại.

```text
python multi_llm_evidence_extraction/scripts/build_outperform_targets.py --mode harmonized --output multi_llm_evidence_extraction/outputs/harmonized/canonical_150_v7/harmonized_outperform_targets.csv
python multi_llm_evidence_extraction/scripts/build_harmonized_comparison.py --mode pilot --run-id canonical_150_v7 --validate-only
python multi_llm_evidence_extraction/scripts/build_harmonized_comparison.py --mode pilot --run-id canonical_150_v7
python multi_llm_evidence_extraction/scripts/run_harmonized_comparison.py --mode pilot --run-id canonical_150_v7
```

`canonical_150_v7` từ chối `--fast`. Target, build và completed comparison đều immutable. Muốn tái chạy sau protocol/code change phải tăng protocol version và dùng run ID mới; không xóa hoặc ghi đè run canonical.

## 3. Build submission

```text
python thesis_submission/reproduction/build_submission.py --run-id canonical_150_v7
python thesis_submission/reproduction/validate_submission.py --run-id canonical_150_v7
```

## 4. Full validation

```text
python -m pytest -q -p no:cacheprovider
python thesis_submission/reproduction/validate_submission.py --run-id canonical_150_v7
```

## Fail-closed policy

- Hash mismatch: dừng.
- Thiếu 3 folds: dừng.
- Primary record không duy nhất: dừng.
- Thiếu paired Top-K periods: ghi `not_estimable`.
- Metric một lớp: ghi `undefined`.
- Không dùng output smoke hoặc legacy thay canonical evidence.
