# Kiểm toán rò rỉ dữ liệu thời gian (Leakage Audit)

**Kết luận tổng thể:** ✅ PASS

## Tham số kiểm toán

- Tệp đặc trưng kỹ thuật: `data/features/technical_features.csv`
- Tệp nhãn: `data/aggregated/master_with_labels.csv`
- Train_Cutoff: `2025Q1`
- Ngưỡng tương quan (corr_threshold): `0.95`
- Số đặc trưng kỹ thuật kiểm tra: **16**
- Số hàng dùng tính tương quan (sau merge): **1428**

## (a) Phân loại cửa sổ thời gian của đặc trưng (Req 8.1)

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

## (b) Cột nhãn/return tương lai không nằm trong feature set (Req 8.2)

Các cột kiểm tra: `return`, `next_quarter_id`, `next_avg_close`, `label_basic`, `label_threshold`.

→ ✅ Không cột nhãn/return tương lai nào xuất hiện trong tập đặc trưng kỹ thuật.

## (c) Tương quan đặc trưng–nhãn (Req 8.3)

Tính `|corr|` Pearson giữa mỗi đặc trưng và nhãn `label_basic`; vượt `0.95` → cờ đỏ rà soát thủ công.

→ ✅ Không đặc trưng nào có `|corr|` với `label_basic` vượt ngưỡng `0.95`.
