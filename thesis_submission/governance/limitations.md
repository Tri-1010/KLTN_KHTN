# Limitations and Non-Claims

## Dữ liệu

- Canonical sample gồm 150 bài stratified; không phải full corpus.
- 122 bài đủ điều kiện consensus trước temporal mapping; số analytic cuối phụ thuộc mapping và target availability.
- Source pages có thể chứa boilerplate hoặc effective-date ambiguity.
- Technical features theo quý làm giảm độ chi tiết so với daily signal.
- Point-in-time exchange membership, delisting và survivorship chưa được xác nhận hoàn chỉnh. File nguồn mang tên `all_vn30_prices.csv`, nhưng canonical predictions có 52 tickers; tên file không chứng minh universe là thành phần VN30 point-in-time.
- Quyền tái phân phối full text/URL từ sáu nguồn báo, chính sách lưu giữ, PII và việc truyền dữ liệu cho LLM provider chưa có register governance hoàn chỉnh; bundle chỉ dành cho nghiên cứu nội bộ cho đến khi quyền sử dụng được xác minh.

## Semantic labels

- Nhãn là pseudo-label consensus, không phải human expert gold labels.
- Ba runs chỉ thuộc hai model families; errors có thể tương quan.
- Annotation provenance có phần legacy reconstructed.
- Agreement không chứng minh correctness.

## ML và inference

- Primary result chỉ áp dụng cho Random Forest, Balanced Accuracy, T+20 và common spine đã khóa.
- Sample nhỏ có thể làm inference thiếu power.
- BH-FDR chỉ kiểm soát family đã khai báo; không loại hết researcher degrees of freedom.
- Protocol và runner harmonized không xuất hiện trong commit được manifest ghi nhận; vì vậy `preregistered` ở đây nghĩa là contract cố định trong config trước canonical rerun, không phải bằng chứng VCS/timestamp độc lập. Replication sau phải commit/tag protocol trước khi chạy.
- Kết quả âm hoặc không đạt gate vẫn là kết quả hợp lệ.

## Backtest

- Top-K là exploratory simulation.
- Cost model chưa bao phủ đầy đủ spread, liquidity, taxes, market impact và execution delay.
- Không gọi kết quả là alpha hoặc bằng chứng deployable.

## Event study

- Association không phải causal effect.
- Confounding, clustered events, market regimes và selection bias vẫn tồn tại.

## Decision cards và UI

- Automated rubric có self-judge/provider bias.
- Rubric không đo return hoặc human decision quality.
- EvidenceTrace là prototype; chưa có auth/RBAC, production DB, live pricing validation hoặc complete browser accessibility audit.

## Research-use disclaimer

Tài liệu phục vụ nghiên cứu học thuật. Không phải khuyến nghị đầu tư, công cụ giao dịch tự động, cam kết lợi nhuận hoặc tư vấn tài chính.
