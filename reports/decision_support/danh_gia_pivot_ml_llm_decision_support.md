# Đánh giá pivot đề tài: ML signal + LLM decision support

## 1. Kết luận ngắn

Hướng mới **ổn và nên làm**, nhưng phải khóa phạm vi: đây là **hệ thống hỗ trợ quyết định đầu tư**, không phải hệ thống giao dịch tự động và không phải đề tài chứng minh LLM dự báo giá cổ phiếu.

Narrative nên dùng:

> Mô hình học máy tạo tín hiệu định lượng và danh sách cổ phiếu ứng viên. Tin tức công khai được dùng như lớp bằng chứng định tính. LLM được dùng để tạo luận điểm đầu tư, nêu rủi ro, theo dõi thay đổi bối cảnh và hỗ trợ hậu kiểm quyết định.

Cách này tận dụng tốt các kết quả đã được trích sang `reports/source_evidence/`: phần ML kỹ thuật, backtest, SHAP, robustness và leakage audit đều mạnh. Phần tin tức/từ khóa có kết quả âm nhưng vẫn có giá trị: nó cho thấy không nên ép tin tức thành biến dự báo trực tiếp; tin tức phù hợp hơn với vai trò evidence layer cho LLM.

## 2. Vì sao hướng mới tốt hơn hướng cũ

Hướng cũ tập trung vào câu hỏi: đặc trưng tin tức/từ khóa có cải thiện dự báo xu hướng giá không. Kết quả thực nghiệm cho thấy câu trả lời phần lớn là không. Đây là kết quả khoa học hợp lệ, nhưng nếu luận văn chỉ xoay quanh kết quả âm thì narrative bảo vệ sẽ khó thuyết phục hơn.

Hướng mới giữ phần mạnh nhất của hướng cũ:

- ML kỹ thuật tạo tín hiệu có hiệu quả định lượng.
- Backtest cho thấy chiến lược mô hình vượt benchmark.
- Leakage audit đã kiểm soát rò rỉ dữ liệu.
- SHAP giúp giải thích tín hiệu.

Đồng thời chuyển phần tin tức/LLM sang vai trò hợp lý hơn:

- Tin tức không phải predictor chính.
- Tin tức là bằng chứng định tính để giải thích và giám sát.
- LLM không ra quyết định độc lập.
- LLM chỉ diễn giải evidence pack và tạo decision card có cấu trúc.

## 3. Phạm vi nên giữ

Nên giữ bốn module chính:

1. **ML Signal Engine**
   - Huấn luyện mô hình ML bằng đặc trưng kỹ thuật.
   - Sinh xác suất tăng, nhãn dự báo, rank và Top-K candidate.
   - Đánh giá bằng Balanced Accuracy, AUC, backtest return, Sharpe, max drawdown, walk-forward.

2. **News Evidence Layer**
   - Dùng tin tức đã gắn ticker, ngày, nguồn, tiêu đề, nhóm sự kiện.
   - Chỉ lấy tin có thời điểm công bố trước thời điểm decision.
   - Đánh giá bằng coverage, độ đúng ticker matching, độ liên quan của tin.

3. **LLM Decision Card Generator**
   - Nhận evidence pack gồm ML score, rank, SHAP/feature importance, technical summary và news evidence.
   - Sinh luận điểm đầu tư, yếu tố hỗ trợ, rủi ro, trigger theo dõi và review date.
   - Bị ràng buộc không thêm dữ kiện ngoài evidence.

4. **Monitoring & Outcome Review**
   - Theo dõi tín hiệu sau khuyến nghị: rank/probability giảm, ticker rơi khỏi Top-K, chỉ báo kỹ thuật đảo chiều, drawdown vượt ngưỡng, tin mới trái chiều.
   - Hậu kiểm sau kỳ nắm giữ: return thực tế, so với benchmark, thesis đúng/sai ở điểm nào.

## 4. Phạm vi nên cắt

Không nên làm trong luận văn hiện tại:

- Không xây hệ thống giao dịch tự động.
- Không làm multi-agent trading.
- Không xây UI/dashboard lớn.
- Không claim LLM tạo alpha.
- Không claim news layer cải thiện return nếu không có kiểm định định lượng đủ mạnh.
- Không mở rộng universe quá nhiều nếu chưa kiểm soát coverage/news/liquidity.

## 5. Tận dụng kết quả cũ

### 5.1. Kết quả ML/backtest nên dùng làm lõi

| File | Giá trị tái sử dụng |
|---|---|
| `reports/technical_ml_backtest_report.md` | Kết quả backtest chính: model net return 0.6030, Sharpe 1.0517, vượt buy-and-hold 0.2535; walk-forward thắng benchmark 3/3 cutoff. |
| `reports/robustness_extended_tickers_report.md` | Robustness 125 mã HOSE+HNX: BA 0.7607, AUC 0.8307, model vượt VNINDEX 15.3 điểm %. |
| `reports/leakage_audit.md` | Leakage audit PASS: 0 future feature, không label/return tương lai trong feature set, không corr đáng ngờ > 0.95. |
| `backtest/strategy.py` | Logic long-only, Top-N, equal-weight, chi phí giao dịch, giả định thị trường Việt Nam. |
| `backtest/run_backtest.py` | CLI chạy signals, strategy, metrics, walk-forward, interpret, audit, report. |
| `pipeline/task10_train.py` | Merge dữ liệu, train/test split, train models, fit imputer trên train. |
| `pipeline/task11_shap.py` | SHAP, permutation importance, group contribution. |

### 5.2. Kết quả news/text nên dùng để biện minh pivot

| File | Cách dùng mới |
|---|---|
| `reports/H1_experiment_report.md` | Chứng minh keyword/news features không cải thiện forecast ổn định; vì vậy news chuyển sang evidence layer. |
| `reports/H2_H3_validation_report.md` | Dùng các từ khóa có tín hiệu thô như `chia cổ tức`, `nợ xấu`, `tăng trưởng`, `báo lãi` làm evidence tags, không overclaim significance. |
| `reports/phan_tich_ket_qua_va_dinh_huong.md` | Dùng phân tích “text không tạo alpha ổn định” và cảnh báo không diễn giải H3 quá lạc quan. |
| `reports/experiment_A6_report.md` | LLM sentiment không cải thiện forecast; LLM nên dùng để giải thích/thesis, không forecast. |
| `reports/distant_supervision_report.md` | Article-level signal yếu có thể dùng làm gợi ý monitoring, không làm bằng chứng alpha chính. |
| `docs/huong_phat_trien_mo_rong.md` | Dùng ý tưởng LLM như annotation/evidence tool. |

## 6. Thiết kế đánh giá đề xuất

### 6.1. Đánh giá ML Signal Engine

- Balanced Accuracy.
- AUC-ROC.
- Top-K portfolio return.
- Sharpe ratio.
- Max drawdown.
- Hit rate.
- Walk-forward theo nhiều cutoff.
- So sánh với buy-and-hold, equal-weight và VNINDEX.

### 6.2. Đánh giá News Evidence Layer

- Tỷ lệ tin gắn đúng ticker.
- Độ phủ tin theo ticker/kỳ.
- Tỷ lệ tin có ngày/nguồn/title hợp lệ.
- Tỷ lệ evidence có trước decision date.
- Mẫu chấm thủ công: relevant / irrelevant / ambiguous.

### 6.3. Đánh giá LLM Decision Card

Rubric 1–5 điểm:

1. Bám sát evidence.
2. Không hallucinate.
3. Giải thích tín hiệu ML rõ.
4. Nêu rủi ro hợp lý.
5. Có trigger theo dõi cụ thể.
6. Có ích cho người đọc.

Baseline so sánh:

- Rule-based template không LLM.
- LLM chỉ có ML score + technical summary.
- LLM có full evidence pack.

### 6.4. Đánh giá Monitoring/Outcome Review

- Chọn 5–10 case Top-K lịch sử.
- Với mỗi case, ghi decision card ban đầu.
- Sau holding period, ghi return và benchmark.
- Xác định alert có xuất hiện trước outcome xấu/tốt không.
- Phân tích thesis ban đầu đúng/sai ở điểm nào.

## 7. Rủi ro chính và cách khóa

| Rủi ro | Cách khóa |
|---|---|
| Scope quá rộng | Giới hạn prototype, không UI lớn, không auto-trading. |
| Data leakage | Evidence chỉ dùng dữ liệu trước decision; prompt ban đầu không chứa outcome/return tương lai. |
| LLM hallucination | Prompt bắt buộc chỉ dùng evidence, từng luận điểm phải có evidence id. |
| LLM evaluation chủ quan | Dùng rubric cố định, chấm mẫu, ghi rõ giới hạn. |
| News coverage không đều | Báo cáo coverage và chọn case có đủ tin. |
| ML result quá tốt bị nghi overfit | Trình bày leakage audit, walk-forward, robustness 125 mã. |

## 8. Kết luận

Pivot này có cơ sở tốt hơn việc bỏ hẳn luận văn cũ. Phần ML/backtest hiện tại đủ làm lõi định lượng. Phần news/text/LLM hiện tại đủ làm bằng chứng phương pháp luận: tin tức không tạo alpha ổn định khi ép thành feature dự báo, nhưng vẫn hữu ích trong giải thích, theo dõi và hậu kiểm quyết định.

Đề tài nên được viết lại theo câu chuyện:

> Từ dự báo xu hướng giá sang hệ thống hỗ trợ quản trị quyết định đầu tư: ML chọn ứng viên, evidence giải thích bối cảnh, LLM tạo luận điểm có kiểm soát, monitoring và outcome review đóng vòng phản hồi.
