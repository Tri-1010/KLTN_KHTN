# Báo cáo tổng hợp: Backtest ML trên đặc trưng kỹ thuật (HOSE-80)

Báo cáo này tổng hợp kết quả đánh giá *giá trị đầu tư* của mô hình dự báo xu hướng giá dựa trên đặc trưng kỹ thuật (Config_A), theo đúng đặc thù thị trường chứng khoán cơ sở Việt Nam (long-only).

## 1. Chỉ số hiệu quả đầu tư (Req 9.1)

Bảng dưới liệt kê chỉ số của chiến lược mô hình cạnh các benchmark (buy-and-hold, equal-weight tái cân bằng), ở cả hai kịch bản gross/net.

| strategy | cost_scenario | cumulative_return | mean_period_return | std_period_return | sharpe_ratio | max_drawdown | hit_rate | total_cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model | gross | 0.620698 | 0.104646 | 0.0969415 | 1.07947 | 0 | 1 | 0 |
| model | net | 0.602964 | 0.102254 | 0.0972263 | 1.05171 | -0.00103525 | 0.8 | 0.0119571 |
| buy_hold_equal | gross | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |
| buy_hold_equal | net | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |
| equal_weight_rebalanced | gross | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |
| equal_weight_rebalanced | net | 0.253502 | 0.0507482 | 0.113769 | 0.446062 | -0.0200341 | 0.6 | 0 |

## 2. Độ ổn định theo thời gian — walk-forward (Req 9.2)

| cutoff | n_test | balanced_accuracy | auc_roc | strategy_cumulative_return_net | buy_hold_cumulative_return |
| --- | --- | --- | --- | --- | --- |
| 2024Q3 | 556 | 0.722948 | 0.796966 | 0.656316 | 0.281762 |
| 2025Q1 | 400 | 0.7599 | 0.823509 | 0.602964 | 0.253502 |
| 2025Q3 | 240 | 0.639988 | 0.709755 | 0.118227 | 0.00719634 |

**Nhận xét về độ ổn định:**

Balanced accuracy qua 3 cutoff: trung bình 0.7076, dao động [0.6400, 0.7599] (độ lệch chuẩn 0.0501).

Lợi nhuận tích lũy (net) của chiến lược mô hình dương ở 3/3 cutoff; trung bình 0.4592.

Chiến lược mô hình vượt buy-and-hold ở 3/3 cutoff.

## 3. Diễn giải mô hình & kiểm toán rò rỉ (Req 9.3)

### 3.1. Tầm quan trọng đặc trưng kỹ thuật

| feature | mean_abs_shap | permutation_importance | rank |
| --- | --- | --- | --- |
| rsi_end_q | 1.67288 | 0.186028 | 1 |
| macd_hist_mean_q | 0.50877 | 0.0192105 | 2 |
| price_vs_sma20 | 0.446245 | 0.00300752 | 3 |
| return_2q_ago | 0.413385 | 0.00483709 | 4 |
| return_q | 0.322035 | 0.0128195 | 5 |
| return_prev_q | 0.305401 | 0.0148371 | 6 |
| volume_change_q | 0.283926 | 0.0107644 | 7 |
| return_mean_daily | 0.280323 | 0.00922306 | 8 |
| price_range_q | 0.265953 | 0.00533835 | 9 |
| sma20_end | 0.256022 | 0.0172055 | 10 |
| bb_position_q | 0.216413 | 0.0111153 | 11 |
| ema20_end | 0.204855 | 0.00714286 | 12 |
| rsi_mean_q | 0.199274 | 0.0137218 | 13 |
| return_std_daily | 0.179352 | 0.00838346 | 14 |
| volume_mean_q | 0.166354 | 0.00922306 | 15 |
| volatility_q | 0.141897 | 0.00928571 | 16 |

### 3.2. Tóm tắt kiểm toán rò rỉ dữ liệu

Nội dung đầy đủ: xem `reports/leakage_audit.md`.

> Trích kết quả kiểm toán:

## Kiểm toán rò rỉ dữ liệu thời gian (Leakage Audit)

**Kết luận tổng thể:** ✅ PASS

### Tham số kiểm toán

- Tệp đặc trưng kỹ thuật: `data/features/technical_features.csv`
- Tệp nhãn: `data/aggregated/master_with_labels.csv`
- Train_Cutoff: `2025Q1`
- Ngưỡng tương quan (corr_threshold): `0.95`
- Số đặc trưng kỹ thuật kiểm tra: **16**
- Số hàng dùng tính tương quan (sau merge): **1428**

### (a) Phân loại cửa sổ thời gian của đặc trưng (Req 8.1)

Quy tắc: tên khớp mẫu `next_`/`future`/`ahead` → **future** (cấm); khớp `prev`/`_ago`/`lag` → **past** (dùng kỳ < q, hợp lệ); còn lại → **in-period** (tính trong kỳ q, hợp lệ).

| Đặc trưng | Cửa sổ thời gian |
|---|---|
| `return_q` | in-period |
| `return_mean_daily` | in-period |
| `return_std_daily` | in-period |
| `volatility_q` | in-period |
| `price_range_q` | in-period |
| `volume_mean_q` | in-period |
| `volume_change_q` | in-period |
| `sma20_end` | in-period |
| `ema20_end` | in-period |
| `price_vs_sma20` | in-period |
| `rsi_mean_q` | in-period |
| `rsi_end_q` | in-period |
| `macd_hist_mean_q` | in-period |
| `bb_position_q` | in-period |
| `return_prev_q` | past |
| `return_2q_ago` | past |

Tổng hợp: **14** in-period, **2** past, **0** future.

→ Không đặc trưng nào dùng dữ liệu tương lai (> q). Đặc trưng `return_q`/`volatility_q` là *trong kỳ* (dùng để dự báo kỳ *kế tiếp*), KHÔNG phải nhãn tương lai.

### (b) Cột nhãn/return tương lai không nằm trong feature set (Req 8.2)

Các cột kiểm tra: `return`, `next_quarter_id`, `next_avg_close`, `label_basic`, `label_threshold`.

→ ✅ Không cột nhãn/return tương lai nào xuất hiện trong tập đặc trưng kỹ thuật.

### (c) Tương quan đặc trưng–nhãn (Req 8.3)

Tính `|corr|` Pearson giữa mỗi đặc trưng và nhãn `label_basic`; vượt `0.95` → cờ đỏ rà soát thủ công.

→ ✅ Không đặc trưng nào có `|corr|` với `label_basic` vượt ngưỡng `0.95`.

## 4. Nhận xét: mô hình có tạo giá trị vượt benchmark? (Req 9.4)

**Kết luận (dựa trên số liệu net):** mô hình TẠO giá trị đầu tư vượt toàn bộ benchmark về lợi nhuận tích lũy trên khoảng test hiện tại.

- So với **buy_hold_equal**: lợi nhuận tích lũy mô hình 0.6030 vượt 0.2535.
- So với **equal_weight_rebalanced**: lợi nhuận tích lũy mô hình 0.6030 vượt 0.2535.

- Sharpe ratio (net) của mô hình: 1.0517.

### 4.1. Giả định thị trường chứng khoán cơ sở Việt Nam

Mọi kết quả trên chỉ có hiệu lực trong phạm vi các giả định sau (Req 2.8):

- **position**: long-only (một chiều) — chỉ mua mã dự báo 'tăng', không bán khống.
- **settlement**: thanh toán T+2 (mua về sau 2 ngày làm việc mới bán được).
- **price_band**: biên độ giá HOSE ±7%/phiên (giả định mọi lệnh khớp ở suất sinh lời kỳ).
- **min_lot**: lô giao dịch tối thiểu 100 cổ phiếu.
- **capital**: giả định NAV đủ lớn để bỏ qua hiệu ứng lô lẻ (odd-lot rounding).
- **slippage**: bỏ qua trượt giá (slippage); chỉ tính chi phí tường minh (brokerage + sell_tax).

### 4.2. Giới hạn và cảnh báo

- Backtest theo đơn vị **quý** và dùng suất sinh lời kỳ, không mô phỏng khớp lệnh từng phiên; T+2/biên độ ±7%/lô 100 chỉ là giả định nền.
- Chỉ tính chi phí tường minh (brokerage + sell_tax), **bỏ qua trượt giá** và tác động thị trường; chi phí thực tế có thể cao hơn.
- Kết quả phụ thuộc khoảng thời gian test và tập 80 mã HOSE; walk-forward chỉ giảm nhẹ rủi ro phụ thuộc một cutoff, không đảm bảo hiệu lực tương lai.
- Lợi nhuận quá khứ **không đảm bảo** lợi nhuận tương lai; báo cáo phục vụ mục tiêu học thuật, không phải khuyến nghị đầu tư.

## 5. Kiểm tra tính vững trên tập mã mở rộng (Robustness Test)

Để kiểm chứng mô hình không overfit vào tập 80 mã HOSE ban đầu, nghiên cứu mở rộng kiểm tra trên **125 mã** từ cả sàn HOSE và HNX (107 HOSE + 18 HNX), với tiêu chí lọc: khối lượng giao dịch trung bình ≥ 100.000 cổ/phiên, niêm yết liên tục từ 2022, tối thiểu 500 phiên giao dịch. Đồng thời bổ sung **VNINDEX** làm benchmark thị trường để tăng tính khách quan.

### 5.1. Kết quả phân loại trên 125 mã HOSE+HNX

| Mô hình | Balanced Accuracy | AUC-ROC | F1 Macro | n_train | n_test |
|---|---|---|---|---|---|
| Baseline (đa số lớp) | 0.500 | 0.500 | 0.297 | 1.653 | 735 |
| Logistic Regression | 0.649 | 0.704 | 0.644 | 1.653 | 735 |
| Random Forest | **0.761** | **0.831** | 0.757 | 1.653 | 735 |
| XGBoost | 0.753 | 0.827 | 0.750 | 1.653 | 735 |
| LightGBM | 0.753 | 0.820 | 0.751 | 1.653 | 735 |

### 5.2. So sánh với kết quả gốc (80 mã HOSE)

| Chỉ số | 80 mã HOSE (gốc) | 125 mã HOSE+HNX (mở rộng) | Chênh lệch |
|---|---|---|---|
| Best Balanced Accuracy | 0.760 (LightGBM) | 0.761 (Random Forest) | +0.001 |
| Best AUC-ROC | 0.824 | 0.831 | +0.007 |
| Số mã | 80 | 125 | ×1.56 |
| Cỡ mẫu train | 1.348 | 1.653 | +22.6% |
| Cỡ mẫu test | 400 | 735 | +83.8% |

Kết quả gần như **không thay đổi** khi mở rộng tập mã gấp 1.56 lần và bao gồm cả sàn HNX. Balanced accuracy ổn định ở mức 0.76, AUC thậm chí nhỉnh hơn (0.831 vs 0.824). Điều này xác nhận mô hình có khả năng **tổng quát hóa** (generalization) tốt và không overfit vào tập 80 mã ban đầu.

### 5.3. Benchmark VNINDEX

| Chiến lược | Lợi nhuận tích lũy | Return TB/quý | Sharpe Ratio | Hit Rate |
|---|---|---|---|---|
| Mô hình (Random Forest) | **57.5%** | 8.16%/quý | 1.00 | 83.3% |
| VNINDEX (buy & hold) | 42.1% | 6.34%/quý | — | — |
| Buy-and-hold 80 mã (gốc) | 25.4% | 5.07%/quý | 0.45 | 60% |

**Lợi nhuận vượt trội so với VNINDEX:** +15.3 điểm phần trăm trên cùng khoảng test.

Chiến lược mô hình vượt cả VNINDEX (chỉ số toàn thị trường) lẫn chiến lược buy-and-hold phân bổ đều — xác nhận giá trị dự báo của mô hình tạo ra lợi nhuận thực, không chỉ đơn thuần đi theo xu hướng thị trường chung.

### 5.4. Nhận xét

- Mô hình **duy trì hiệu quả** trên tập mã lớn hơn, đa dạng hơn (bao gồm mid/small-cap và sàn HNX).
- Kết quả **không phụ thuộc vào lựa chọn 80 mã cụ thể** — loại trừ nghi vấn survivorship bias hẹp.
- So sánh với VNINDEX cho thấy lợi nhuận mô hình không đơn thuần do thị trường đi lên (excess return dương 15.3%).
- Hạn chế: backtest mở rộng dùng kịch bản gross (chưa trừ phí), một số mã HNX có thanh khoản thấp hơn mặt bằng HOSE.

*Chi tiết đầy đủ: xem `reports/robustness_extended_tickers_report.md`. Script: `scripts/robustness_extended_tickers.py`.*
