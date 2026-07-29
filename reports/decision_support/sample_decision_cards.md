# Sample Decision Cards

> File này lưu các decision card rút gọn dùng minh họa trong luận văn. Bản đầy đủ 25 card nằm ở `reports/decision_support/generated/decision_cards.md`. Các card dưới đây được trích từ evidence pack thật, nhưng vẫn là rule-based baseline, chưa phải output LLM thật.

---

## Sample 1: `2025Q2_STB_01` — ML đúng, thesis được hỗ trợ

### 1. Tóm tắt tín hiệu

- Ticker: **STB**
- Decision date: 2025-06-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9988
- Rank trong kỳ: 1
- Outcome review: realized return 0.2763, positive

### 2. Evidence chính

- `rsi_end_q` = 69.6950, hướng `supports_up_signal`.
- `macd_hist_mean_q` = 0.0913, hướng `supports_up_signal`.
- `price_vs_sma20` = 0.0432, hướng `supports_up_signal`.
- News evidence gần decision date gồm tin Sacombank và earnings-related news trong pack.

### 3. Bài học dùng trong luận văn

Case này minh họa ML signal mạnh, rank cao và outcome dương. Có thể dùng làm case A: ML đúng, thesis được hỗ trợ.

---

## Sample 2: `2026Q1_DPM_03` — ML sai, monitoring có warning

### 1. Tóm tắt tín hiệu

- Ticker: **DPM**
- Decision date: 2026-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9719
- Rank trong kỳ: 3
- Outcome review: realized return -0.0276, negative/neutral

### 2. Evidence chính

- `rsi_end_q` = 52.1123, hướng `supports_up_signal`.
- `macd_hist_mean_q` = 0.0902, hướng `supports_up_signal`.
- `price_vs_sma20` = -0.0245, hướng `weak_or_negative`.
- News/event flags gồm nhiều mục `legal_risk` liên quan BCTC kiểm toán và giải trình biến động KQKD.

### 3. Bài học dùng trong luận văn

Case này minh họa probability cao không đủ để bỏ qua monitoring. Technical/news flags có thể kích hoạt trạng thái Watch hoặc Review Required.

---

## Sample 3: `2025Q3_KDH_04` — Outcome dương nhưng evidence cần thận trọng

### 1. Tóm tắt tín hiệu

- Ticker: **KDH**
- Decision date: 2025-09-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9921
- Rank trong kỳ: 4
- Outcome review: realized return 0.0461, positive

### 2. Evidence chính

- `rsi_end_q` = 48.1968, hướng `weak_or_neutral`.
- `macd_hist_mean_q` = 0.0095, hướng `supports_up_signal`.
- `price_vs_sma20` = -0.0221, hướng `weak_or_negative`.
- News evidence thiên về giao dịch/quỹ và governance hơn là thesis vận hành mạnh.

### 3. Bài học dùng trong luận văn

Outcome dương không đồng nghĩa evidence định tính mạnh. Card phải ghi rõ đây là technical candidate và tránh overclaim news layer.

---

## Sample 4: `2025Q2_VND_05` — News/event trái chiều với ML

### 1. Tóm tắt tín hiệu

- Ticker: **VND**
- Decision date: 2025-06-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9971
- Rank trong kỳ: 5
- Outcome review: realized return 0.4522, positive

### 2. Evidence chính

- `rsi_end_q` = 65.8972, hướng `supports_up_signal`.
- `macd_hist_mean_q` = -0.0110, hướng `weak_or_negative`.
- `price_vs_sma20` = 0.0524, hướng `supports_up_signal`.
- News/event flags gồm `debt_risk` và `debt_risk,capital` liên quan phát hành trái phiếu.

### 3. Bài học dùng trong luận văn

Dù outcome tốt, card vẫn cần nêu rủi ro trái chiều từ event layer. Evidence layer có vai trò cân bằng thesis, không chỉ tìm tin hỗ trợ.

---

## Sample 5: `2025Q4_VBB_05` — Tín hiệu cần Review Required

### 1. Tóm tắt tín hiệu

- Ticker: **VBB**
- Decision date: 2025-12-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9822
- Rank trong kỳ: 5
- Outcome review: realized return -0.0526, negative/neutral

### 2. Evidence chính

- `rsi_end_q` = 47.8687, hướng `weak_or_neutral`.
- `macd_hist_mean_q` = -0.0055, hướng `weak_or_negative`.
- `return_q` = -0.0744, hướng `weak_or_negative`.
- Ticker matching confidence mixed, cần kiểm tra thủ công news evidence.

### 3. Bài học dùng trong luận văn

Case này phù hợp minh họa trạng thái Review Required: probability vẫn cao nhưng nhiều technical flags yếu và outcome âm.

---

## Ghi chú sử dụng

- Dùng file này để trình bày case rút gọn trong Chương 4 hoặc phụ lục.
- Dùng `generated/decision_cards.md` và `generated/outcome_reviews.md` nếu cần bản đầy đủ.
- Không trình bày các card này như khuyến nghị đầu tư hoặc LLM output thật.
