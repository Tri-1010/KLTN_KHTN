# Implementation Plan: technical-ml-investment-backtest

## Overview

Kế hoạch xây dựng gói `backtest/` chồng lên pipeline hiện có, biến kết quả accuracy thành kết
quả đầu tư long-only sát đặc thù thị trường cơ sở VN. Thứ tự: (1) nền tảng (khung test,
Prediction_Signal, chi phí), (2) mô phỏng chiến lược + benchmark, (3) chỉ số hiệu quả,
(4) walk-forward, (5) diễn giải mô hình + kiểm toán rò rỉ, (6) báo cáo tổng hợp + CLI.

Mọi huấn luyện tái dùng `pipeline/task10_train.py` (không sửa production). Chiến lược thuần
**long-only** — không có vế short. Property tests P1–P11 (định nghĩa trong design) là **bắt
buộc**, chạy tối thiểu 100 iterations bằng Hypothesis. Mọi task chỉ gồm viết/sửa/kiểm thử code.

Ngôn ngữ: **Python** (bám pipeline hiện có), property-based testing bằng **Hypothesis**.

## Tasks

- [x] 1. Thiết lập gói `backtest/` và khung kiểm thử
  - Tạo `backtest/__init__.py`
  - Xác nhận `pytest` chạy được suite hiện có (baseline test count cho Req 10.4)
  - Xác nhận Hypothesis profile `max_examples=100` trong `tests/conftest.py` áp dụng cho test mới
  - _Requirements: 10.2, 10.4_

- [x] 2. Transaction_Cost (`backtest/costs.py`) — phí giao dịch VN
  - [x] 2.1 Hiện thực `CostConfig` và các hàm `turnover`, `period_cost`
    - `CostConfig(brokerage=0.0015, sell_tax=0.0010)` cấu hình được
    - `turnover(prev_w, new_w)` → (buy_value, sell_value) chuẩn hóa theo NAV=1, chỉ phần thay đổi
    - `period_cost` = buy_v·brokerage + sell_v·(brokerage + sell_tax); kỳ đầu tính brokerage trên toàn vốn vào
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [x] 2.2 Viết property test P3 — chi phí không âm, bằng 0 khi danh mục không đổi
    - **Property 3: Chi phí giao dịch không âm và bằng 0 khi danh mục không đổi**
    - **Validates: Requirements 3.2, 3.3, 3.4**
    - Sinh cặp trọng số danh mục ngẫu nhiên; kiểm cost ≥ 0, = 0 khi hai danh mục giống nhau, tăng đơn điệu theo turnover; tối thiểu 100 iterations
  - [x] 2.3 Viết property test P4 — phí bán cao hơn phí mua cùng giá trị
    - **Property 4: Phí bán cao hơn phí mua cùng giá trị**
    - **Validates: Requirements 3.1, 3.3**
    - Sinh giá trị giao dịch dương; kiểm phí bán (brokerage+sell_tax) > phí mua (brokerage); tối thiểu 100 iterations

- [x] 3. Prediction_Signal (`backtest/signals.py`) — tín hiệu từ mô hình kỹ thuật
  - [x] 3.1 Hiện thực `generate_signals()` trả về `SignalFrame`
    - Tái dùng `load_and_merge_data`, `identify_feature_columns`, `get_feature_configs`, `time_series_split`, `fit_imputer`, `prepare_features`, `build_ml_models` từ `pipeline/task10_train.py`
    - Huấn luyện `model_name` (mặc định LightGBM) trên `Config_A` (chỉ kỹ thuật); fit imputer trên train, transform test
    - Trả DataFrame cột `ticker, quarter_id, y_true, pred_label, pred_proba_up, period_return`
    - Gắn `period_return` từ cột `return` của `master_with_labels.csv` theo `(ticker, quarter_id)`; loại hàng thiếu return và đếm lại
    - Hỗ trợ chọn mô hình có BA cao nhất khi không chỉ định tường minh
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.4_
  - [x] 3.2 Viết integration test cho `generate_signals`
    - Chạy trên dữ liệu thật cutoff mặc định; xác nhận đủ cột, số hàng khớp tập test, proba ∈ [0,1]
    - _Requirements: 1.2, 1.3_

- [x] 4. Strategy_Simulator (`backtest/strategy.py`) — mô phỏng long-only
  - [x] 4.1 Hiện thực `portfolio_period_return` và hàm chọn danh mục
    - `portfolio_period_return(selected_returns)` = mean nếu có mã, 0 nếu rỗng
    - Hàm chọn danh mục: mã `pred_label==1`; biến thể top-N theo `pred_proba_up`; KHÔNG bao giờ chọn `pred_label==0` (long-only)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [x] 4.2 Hiện thực `simulate_strategy(signals, cfg)` và `StrategyResult`
    - Sort theo quarter_id; mỗi kỳ chọn danh mục, phân bổ đều, tính lợi nhuận kỳ
    - Áp Transaction_Cost trên phần danh mục thay đổi; tính cả gross và net
    - Kỳ rỗng → giữ tiền mặt, return = 0; chỉ dùng thông tin ≤ q
    - Ghi giả định thị trường VN vào metadata kết quả
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.7, 2.8, 3.5_
  - [x] 4.3 Viết property test P1 — lợi nhuận danh mục là trung bình mã được chọn
    - **Property 1: Lợi nhuận danh mục là trung bình lợi nhuận các mã được chọn**
    - **Validates: Requirements 2.3, 2.4**
    - Sinh tập lợi nhuận mã ngẫu nhiên; kiểm bằng mean, = 0 khi rỗng; tối thiểu 100 iterations
  - [x] 4.4 Viết property test P2 — chọn danh mục đúng theo dự đoán và top-N (long-only)
    - **Property 2: Chọn danh mục đúng theo dự đoán và top-N (long-only)**
    - **Validates: Requirements 2.1, 2.2, 2.6**
    - Sinh SignalFrame ngẫu nhiên; kiểm danh mục = tập pred_label==1 (hoặc top-N proba), không chứa pred_label==0, trọng số ≥ 0; tối thiểu 100 iterations
  - [x] 4.5 Viết property test P11 — ràng buộc long-only trên toàn danh mục qua các kỳ
    - **Property 11: Ràng buộc long-only trên toàn danh mục qua các kỳ**
    - **Validates: Requirements 2.2, 2.3**
    - Sinh SignalFrame nhiều kỳ; kiểm tổng trọng số ∈ [0,1], mọi trọng số ≥ 0, không kỳ nào có vị thế âm; tối thiểu 100 iterations
  - [x] 4.6 Viết property test P5 — lợi nhuận net không vượt gross
    - **Property 5: Lợi nhuận net không vượt lợi nhuận gross**
    - **Validates: Requirements 3.5, 5.1**
    - Sinh chuỗi quyết định danh mục với phí ≥ 0; kiểm cumulative net ≤ gross; tối thiểu 100 iterations

- [x] 5. Performance_Evaluator (`backtest/metrics.py`) — chỉ số hiệu quả
  - [x] 5.1 Hiện thực các pure function chỉ số
    - `cumulative_return` = ∏(1+r)−1; `mean_std_period`; `sharpe_ratio(rf=0)`; `max_drawdown`; `hit_rate`
    - Xử lý std=0 an toàn (trả 0 hoặc NaN có kiểm soát, không chia 0)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - [x] 5.2 Hiện thực `evaluate_all(strategies)` → `reports/backtest_performance.csv`
    - Bảng chỉ số mọi chiến lược, hai kịch bản gross/net, kèm total_cost
    - _Requirements: 5.6, 3.5_
  - [x] 5.3 Viết property test P6 — cumulative return là tích gross-return
    - **Property 6: Lợi nhuận tích lũy là tích các gross-return theo kỳ**
    - **Validates: Requirements 5.1**
    - Sinh chuỗi lợi nhuận kỳ; kiểm = ∏(1+r)−1, = 0 khi toàn 0; tối thiểu 100 iterations
  - [x] 5.4 Viết property test P7 — cận của Max_Drawdown
    - **Property 7: Cận của Max_Drawdown**
    - **Validates: Requirements 5.4**
    - Kiểm MDD ∈ [−1,0], = 0 khi mọi return ≥ 0, bất biến khi thêm kỳ 0 ở cuối sau đỉnh; tối thiểu 100 iterations
  - [x] 5.5 Viết property test P8 — Sharpe xác định, không lỗi khi std=0
    - **Property 8: Sharpe bằng 0/không đổi theo biến đổi hợp lệ**
    - **Validates: Requirements 5.3**
    - Kiểm Sharpe = mean(r−rf)/std(r) khi std>0; trả giá trị xác định (0/NaN) khi std=0 không ném lỗi; tối thiểu 100 iterations
  - [x] 5.6 Viết property test P10 — hit rate là tỷ lệ hợp lệ
    - **Property 10: Hit rate là tỷ lệ hợp lệ**
    - **Validates: Requirements 5.5**
    - Sinh chuỗi lợi nhuận kỳ; kiểm hit_rate ∈ [0,1] và bằng tỷ lệ kỳ dương; tối thiểu 100 iterations

- [x] 6. Benchmark_Strategy (`backtest/benchmarks.py`) — tham chiếu long-only
  - [x] 6.1 Hiện thực `buy_and_hold_equal` và `equal_weight_rebalanced`
    - Buy-and-hold: phân bổ đều toàn bộ ticker, giữ suốt kỳ test
    - Equal-weight: tái cân bằng đều mỗi kỳ trên ticker có dữ liệu kỳ đó
    - Cả hai long-only, đo bằng cùng Performance_Evaluator trên cùng khoảng test
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 6.2 Viết unit test cho benchmark
    - Dữ liệu nhỏ đã biết đáp án; kiểm cumulative return và cấu trúc kết quả
    - _Requirements: 4.1, 4.2_

- [x] 7. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Walk_Forward_Evaluator (`backtest/walk_forward.py`) — độ ổn định thời gian
  - [x] 8.1 Hiện thực `run_walk_forward(cutoffs, model_name)`
    - Với mỗi cutoff: `generate_signals(cutoff=...)` → BA, AUC; `simulate_strategy` → cumulative return (net); benchmark buy-hold để đối chiếu
    - Chỉ train trên kỳ < cutoff; cutoff cho test rỗng/một-lớp → cảnh báo, bỏ qua
    - Ghi `reports/walk_forward_results.csv`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 8.2 Viết property test P9 — không rò rỉ thời gian trong walk-forward
    - **Property 9: Không rò rỉ thời gian trong walk-forward**
    - **Validates: Requirements 6.1, 6.5, 8.4**
    - Sinh dữ liệu nhiều kỳ; kiểm tập train của mỗi cutoff chỉ gồm quarter_id < cutoff; thay đổi dữ liệu kỳ ≥ cutoff không đổi mô hình; tối thiểu 100 iterations

- [x] 9. Model_Interpreter (`backtest/interpret.py`) — diễn giải mô hình kỹ thuật
  - [x] 9.1 Hiện thực `interpret_technical_model(model, X_test, feature_names)`
    - SHAP (TreeExplainer cho mô hình cây; fallback permutation cho LogReg/không hỗ trợ) xếp hạng 16 đặc trưng theo mean|SHAP|
    - permutation_importance theo balanced accuracy trên tập test
    - Ghi `reports/technical_feature_importance.csv` + biểu đồ PNG
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [x] 9.2 Viết unit test cho interpreter
    - Mô hình nhỏ đã fit; kiểm bảng xếp hạng đủ 16 đặc trưng, có cột mean_abs_shap và permutation_importance
    - _Requirements: 7.1, 7.3_

- [x] 10. Leakage_Auditor (`backtest/leakage_audit.py`) — kiểm toán rò rỉ thời gian
  - [x] 10.1 Hiện thực `audit_leakage(tech_path, labels_path, cutoff, corr_threshold)`
    - (a) Phân loại cửa sổ thời gian mỗi đặc trưng kỹ thuật (in-period/past); xác nhận không dùng dữ liệu > q
    - (b) Xác nhận cột nhãn/return tương lai không nằm trong feature set
    - (c) Tính |corr| đặc trưng–nhãn; > ngưỡng → cờ đỏ rà soát thủ công
    - Ghi `reports/leakage_audit.md`
    - _Requirements: 8.1, 8.2, 8.3, 8.5_
  - [x] 10.2 Viết unit test cho auditor
    - Dựng đặc trưng giả có rò rỉ rõ ràng (bản sao nhãn tương lai) → kiểm auditor gắn cờ; đặc trưng sạch → pass
    - _Requirements: 8.2, 8.3_

- [x] 11. Backtest_Reporter (`backtest/reporting.py`) — báo cáo tổng hợp
  - Hiện thực `generate_backtest_report()`
  - Gộp `backtest_performance.csv`, `walk_forward_results.csv`, `technical_feature_importance.csv`, `leakage_audit.md`
  - Viết nhận xét mô hình có/không tạo giá trị vượt benchmark kèm giả định thị trường VN (long-only, T+2, ±7%, lô 100) và giới hạn
  - Ghi `reports/technical_ml_backtest_report.md`
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 2.8_

- [x] 12. CLI orchestrator (`backtest/run_backtest.py`)
  - Hiện thực CLI: `--all`, `--signals --model {name}`, `--walk-forward`, `--interpret`, `--audit`, `--report`
  - Thứ tự `--all`: signals → strategy+benchmarks → metrics → walk-forward → interpret → audit → report
  - _Requirements: 10.1, 10.5_

- [x] 13. Checkpoint cuối — chạy toàn bộ test suite
  - Chạy `pytest` toàn bộ suite (property tests P1–P11 ≥100 iterations + test hiện có)
  - Xác nhận số test pass không giảm so với baseline task 1 (Req 10.4)
  - Chạy `python -m backtest.run_backtest --all` xác nhận sinh đủ artifact/báo cáo
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Chiến lược **thuần long-only** — không có vế short (đặc thù thị trường cơ sở VN). Đây là ràng
  buộc cứng, không có biến thể long-short.
- **Property tests P1–P11 là bắt buộc**, chạy tối thiểu 100 iterations bằng Hypothesis.
- Tái dùng `pipeline/task10_train.py` làm thư viện, KHÔNG sửa hành vi mặc định (Req 10.1).
- Phí giao dịch VN: brokerage 0,15%/lượt + sell_tax 0,1% (chỉ bán), round-trip ~0,40%.
- Period_Return dùng cột `return` của `master_with_labels.csv` (suất sinh lời kỳ kế tiếp) —
  khớp định nghĩa nhãn, không rò rỉ vì dự đoán chỉ dùng đặc trưng ≤ q.
- Leakage_Auditor quan trọng để bảo vệ con số BA ~0,76 trước hội đồng.
- Mọi giả định thị trường (long-only, T+2, ±7%, lô 100, bỏ qua slippage/lô lẻ) ghi rõ trong
  báo cáo cuối.
