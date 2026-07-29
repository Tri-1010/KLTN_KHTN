# Robustness Test: Extended Ticker Universe (HOSE + HNX)

> Ngày chạy: 2026-07-04 11:15

## 1. Tóm tắt

- **Tổng số mã kiểm tra:** 125 (HOSE: 107, HNX: 18)
- **Train cutoff:** 2025Q1
- **Tiêu chí lọc:** volume TB >= 100,000 cổ/phiên, >= 500 phiên từ 2022
- **Mô hình tốt nhất:** Random_Forest (Balanced Accuracy = 0.7607)

## 2. Kết quả phân loại (Config A — chỉ đặc trưng kỹ thuật)

| Mô hình | Balanced Acc | AUC-ROC | F1 Macro | n_train | n_test |
|---|---|---|---|---|---|
| Baseline_Majority | 0.5000 | 0.5000 | 0.2973 | 1653 | 735 |
| Baseline_Stratified | 0.5223 | 0.5223 | 0.5186 | 1653 | 735 |
| Logistic_Regression | 0.6488 | 0.7036 | 0.6438 | 1653 | 735 |
| Random_Forest | 0.7607 | 0.8307 | 0.7573 | 1653 | 735 |
| XGBoost | 0.7531 | 0.8265 | 0.7502 | 1653 | 735 |
| LightGBM | 0.7530 | 0.8198 | 0.7509 | 1653 | 735 |

## 3. So sánh với kết quả gốc (80 mã HOSE)

| Chỉ số | 80 mã HOSE (gốc) | 125 mã HOSE+HNX (mở rộng) | Nhận xét |
|---|---|---|---|
| Best Balanced Accuracy | 0.760 (LightGBM) | 0.7607 (Random_Forest) | ↑ 0.0007 |
| Best AUC-ROC | 0.824 | 0.8307 | ↑ 0.0067 |
| Số mã | 80 | 125 | x1.6 |
| Cỡ mẫu train | 1,348 | 1,653 | |
| Cỡ mẫu test | 400 | 735 | |

## 4. Benchmark VNINDEX

| Chiến lược | Lợi nhuận tích lũy | Return TB/quý | Sharpe | Hit Rate |
|---|---|---|---|---|
| **Mô hình (Random_Forest)** | 0.5746 (57.5%) | 0.0816 | 1.00 | 83.3% |
| VNINDEX (buy & hold) | 0.4212 (42.1%) | 0.0634 | — | — |

**Lợi nhuận vượt trội (excess return) so với VNINDEX:** 0.1534 (15.3%)

## 5. Kết luận Robustness Test

Mô hình ML dự báo xu hướng giá bằng đặc trưng kỹ thuật **duy trì hiệu quả** khi mở rộng từ 80 mã HOSE gốc lên 125 mã HOSE+HNX (Balanced Accuracy = 0.761). Kết quả cho thấy khả năng tổng quát hóa (generalization) tốt — mô hình không overfit vào tập 80 mã ban đầu.

Chiến lược mô hình **vượt VNINDEX** 15.3% trên cùng khoảng test — xác nhận giá trị đầu tư thực.

## 6. Giới hạn

- Backtest đơn giản (equal-weight, không tính phí giao dịch cho phiên bản mở rộng này).
- Một số mã HNX có thanh khoản thấp hơn ngưỡng HOSE-80 gốc.
- Kết quả quá khứ không đảm bảo hiệu quả tương lai.
- Test này chỉ kiểm tra đặc trưng kỹ thuật (không bao gồm đặc trưng từ khóa).

---

*Script: `scripts/robustness_extended_tickers.py`*