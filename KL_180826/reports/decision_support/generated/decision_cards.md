# Generated Decision Cards (Rule-based Baseline)

> Các card này được sinh từ evidence pack thật, nhưng chưa phải output LLM. Dùng làm baseline và input cho chấm LLM sau này.

---

## Decision Card: 2025Q1_SCR_01

### 1. Tóm tắt tín hiệu

- Ticker: **SCR**
- Decision date: 2025-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9994
- Rank trong kỳ: 1
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã SCR được chọn vào Top-5 của kỳ 2025Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9994 và rank 1 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 61.8393, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0070, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0253, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: SCR: Nghị quyết HĐQT về việc nhận chuyển nhượng tài sản (cafef, 2025-03-07). Tóm tắt: Công ty Cổ phần Địa ốc Sài Gòn Thương Tín công bố Nghị quyết HĐQT về việc nhận chuyển nhượng tài sản SCR: Nghị quyết HĐQT về việc nhận chuyển nhượng tài sản Công ty Cổ phần Địa ốc Sài Gòn Thương Tín công bố Nghị quyết HĐQT về việc nhận chuyển nhượng tài sản — Evidence: N001.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `return_2q_ago` = -0.2058, hướng `weak_or_negative`.
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q1_VHM_02

### 1. Tóm tắt tín hiệu

- Ticker: **VHM**
- Decision date: 2025-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9991
- Rank trong kỳ: 2
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã VHM được chọn vào Top-5 của kỳ 2025Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9991 và rank 2 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 86.1444, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1856, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0768, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: Vinhomes lãi 35.000 tỷ đồng, Ban điều hành được trả thù lao bao nhiêu? (cafef, 2025-03-31). Tóm tắt: Thu nhập do Vinhomes chi trả cho Ban điều hành năm 2024 giảm 40% so với 2023. Theo Hà My | 31-03-2025 - 15:25 PM | Thị trường chứng khoán Thu nhập do Vinhomes chi trả cho Ban điều hành năm 2024 giảm 40% so với 2023. Công ty cổ phần Vinhomes vừa công bố báo cáo tài chính hợp nhất kiểm toán năm 2024. — Evidence: N001.
   - Key fact F01: Vinhomes lãi 35.000 tỷ đồng, Ban điều hành được trả thù lao bao nhiêu?
   - Key fact F02: Thu nhập do Vinhomes chi trả cho Ban điều hành năm 2024 giảm 40% so với 2023.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 86.1444, hướng `positive_but_overbought_risk`.
- News/event cần kiểm tra thủ công: `earnings,legal_risk,governance,market` — Vinhomes lãi 35.000 tỷ đồng, Ban điều hành được trả thù lao bao nhiêu? (2025-03-31).
- News/event cần kiểm tra thủ công: `debt_risk,governance,market` — chi dao moi truoc them khoi cong sieu du an cua vinhomes tai ven vinh cam ranh 1362095.html (2025-03-19).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q1_VIC_03

### 1. Tóm tắt tín hiệu

- Ticker: **VIC**
- Decision date: 2025-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9981
- Rank trong kỳ: 3
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã VIC được chọn vào Top-5 của kỳ 2025Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9981 và rank 3 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 91.1043, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1247, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.1354, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: VIC: Giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước (cafef, 2025-03-31). Tóm tắt: Tập đoàn Vingroup - Công ty Cổ phần giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước VIC: Giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước Tập đoàn Vingroup - Công ty Cổ phần giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước — Evidence: N001.
   - Key fact F01: VIC: Giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước Tập đoàn Vingroup - Công ty Cổ phần giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước VIC: Giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước Tập đoàn Vingroup - Công ty Cổ phần giải 

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 91.1043, hướng `positive_but_overbought_risk`.
- News/event cần kiểm tra thủ công: `legal_risk` — VIC: Giải trình chênh lệch BCTC kiểm toán năm 2024 so với cùng kỳ năm trước (2025-03-31).
- News/event cần kiểm tra thủ công: `capital,legal_risk,governance` — Chủ tịch Vingroup nhận thù lao 0 đồng (2025-03-31).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q1_SHB_04

### 1. Tóm tắt tín hiệu

- Ticker: **SHB**
- Decision date: 2025-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9971
- Rank trong kỳ: 4
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã SHB được chọn vào Top-5 của kỳ 2025Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9971 và rank 4 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 80.3284, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0363, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.1138, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: Top 10 cổ phiếu tăng/giảm mạnh nhất tuần: Cổ phiếu VIC và SHB tiếp tục tiến bước (tnck, 2025-03-28). Tóm tắt: Kết thúc tuần giao dịch, chỉ số VN-Index giảm nhẹ 4,42 điểm (-0,33%), xuống 1.317,46 điểm. Thanh khoản bình quân giảm tuần thứ hai liên tiếp và hầu hết các phiên đều dưới ngưỡng bình quân 20 phiên, với khối lượng khớp lệnh trung bình đạt 788 triệu cổ phiếu, giảm hơn 8% và giá trị bình quân 18.751 tỷ đồng/phiên, giảm 6,5%. Trên sàn HOSE, hai bluechip SHB và VIC dù chỉ có mức tăng 8-9% nhưng đã cho thấy sự bền bỉ và tiếp tục xuất hiện trong top những mã tăng tốt nhất. — Evidence: N001.
   - Key fact F01: Top 10 cổ phiếu tăng/giảm mạnh nhất tuần: Cổ phiếu VIC và SHB tiếp tục tiến bước nan Kết thúc tuần giao dịch, chỉ số VN-Index giảm nhẹ 4,42 điểm (-0,33%), xuống 1.317,46 điểm.
   - Key fact F02: Thanh khoản bình quân giảm tuần thứ hai liên tiếp và hầu hết các phiên đều dưới ngưỡng bình quân 20 phiên, với khối lượng khớp lệnh trung bình đạt 788 triệu cổ phiếu, giảm hơn 8% và giá trị bình quân 18.751 tỷ đồng/phiên, giảm 6,5%.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 80.3284, hướng `positive_but_overbought_risk`.
- Driver cần theo dõi: `return_2q_ago` = -0.0095, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `market` — Top 10 cổ phiếu tăng/giảm mạnh nhất tuần: Cổ phiếu VIC và SHB tiếp tục tiến bước (2025-03-28).
- News/event cần kiểm tra thủ công: `earnings,debt_risk,governance,market` — chung khoan 27 3 fpt shb toa sang giua sac do nganh ngan hang 1364376.html (2025-03-27).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q1_BSI_05

### 1. Tóm tắt tín hiệu

- Ticker: **BSI**
- Decision date: 2025-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9969
- Rank trong kỳ: 5
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã BSI được chọn vào Top-5 của kỳ 2025Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9969 và rank 5 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 59.7477, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0790, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0198, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: chung khoan bidv bsc dat muc tieu lai 560 ty dong tang von len gan 2 500 ty trong nam 2025 1364874.html (kinhtechungkhoan, 2025-03-31). Tóm tắt: Chứng khoán BIDV (BSC) sẽ trình cổ đông kế hoạch lợi nhuận trước thuế năm 2025 đạt 560 tỷ đồng, tăng 8,5%. Đồng thời, công ty dự kiến phát hành hơn 22 triệu cổ phiếu trả cổ tức tỷ lệ 10%, nâng vốn điều lệ lên gần 2.500 tỷ đồng. Công ty CP Chứng khoán BIDV (BSC, HOSE: BSI) vừa công bố tài liệu họp Đại hội đồng cổ đông thường niên 2025, dự kiến tổ chức vào sáng 18/4/2025 tại Hà Nội. — Evidence: N001.
   - Key fact F01: chung khoan bidv bsc dat muc tieu lai 560 ty dong tang von len gan 2 500 ty trong nam 2025 1364874.html nan Chứng khoán BIDV (BSC) sẽ trình cổ đông kế hoạch lợi nhuận trước thuế năm 2025 đạt 560 tỷ đồng, tăng 8,5%.
   - Key fact F02: Đồng thời, công ty dự kiến phát hành hơn 22 triệu cổ phiếu trả cổ tức tỷ lệ 10%, nâng vốn điều lệ lên gần 2.500 tỷ đồng.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,governance,market` — chung khoan bidv bsc dat muc tieu lai 560 ty dong tang von len gan 2 500 ty trong nam 2025 1364874.html (2025-03-31).
- News/event cần kiểm tra thủ công: `legal_risk` — BSI: Báo cáo tỷ lệ an toàn tài chính đã được kiểm toán tại ngày 31/12/2024 (2025-03-26).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q2_STB_01

### 1. Tóm tắt tín hiệu

- Ticker: **STB**
- Decision date: 2025-06-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9988
- Rank trong kỳ: 1
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã STB được chọn vào Top-5 của kỳ 2025Q2 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9988 và rank 1 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 69.6950, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0913, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0432, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: Sacombank khởi động mùa hè rực rỡ với hàng loạt chương trình khuyến mại hấp dẫn (vietstock, 2025-06-28). Tóm tắt: Sacombank khởi động mùa hè rực rỡ với hàng loạt chương trình khuyến mại hấp dẫn Nhằm chào đón một mùa hè sôi động và tiếp thêm năng lượng tích cực cho khách hàng trong hành trình tài chính, Sacombank triển khai chuỗi chương trình khuyến mại "Rực rỡ Hè Xanh - Quà sang bất tận", diễn ra từ nay đến hết tháng 9/2025. Chuỗi 4 chương trình gồm: Bốc thăm trúng ngay, Quay số trúng thưởng cuối kỳ, Ưu đãi giao dịch qua thẻ và Sacombank Pay - tất cả đều được thiết kế nhằm tri ân khách hàng cá nhân, mang lại những giá trị thiết thực và trải nghiệm mùa hè trọn vẹn hơn. Nhận quà liền tay, trúng thưởng bất ngờ Sacombank khởi động chuỗi ưu đãi hè với chương trình ‘Bốc thăm trúng ngay’, dành cho khách hàng gửi tiết kiệm - mỗi giao dịch không chỉ sinh lời mà còn có cơ hội nhận quà liền tay. — Evidence: N001.
   - Key fact F01: Sacombank khởi động mùa hè rực rỡ với hàng loạt chương trình khuyến mại hấp dẫn nan Sacombank khởi động mùa hè rực rỡ với hàng loạt chương trình khuyến mại hấp dẫn Nhằm chào đón một mùa hè sôi động và tiếp thêm năng lượng tích cực cho khách hàng trong hành trình tài chính, Sacombank triển khai chuỗi
   - Key fact F02: Chuỗi 4 chương trình gồm: Bốc thăm trúng ngay, Quay số trúng thưởng cuối kỳ, Ưu đãi giao dịch qua thẻ và Sacombank Pay - tất cả đều được thiết kế nhằm tri ân khách hàng cá nhân, mang lại những giá trị thiết thực và trải nghiệm mùa hè trọn vẹn hơn.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `earnings,market` — SSI dự báo lợi nhuận 40 doanh nghiệp: Đột biến đến từ FPT Retail, Hải An, NT2, Sacombank (2025-06-24).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,governance,market` — Dấu ấn ‘nữ tướng’ Nguyễn Đức Thạch Diễm tại Sacombank: Hành trình 23 năm và di sản để lại (2025-06-23).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q2_DXG_02

### 1. Tóm tắt tín hiệu

- Ticker: **DXG**
- Decision date: 2025-06-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9985
- Rank trong kỳ: 2
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã DXG được chọn vào Top-5 của kỳ 2025Q2 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9985 và rank 2 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 75.3329, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0188, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0459, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: DXG: Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 (cafef, 2025-06-26). Tóm tắt: Công ty Cổ phần Tập đoàn Đất Xanh thông báo Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 DXG: Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 Công ty Cổ phần Tập đoàn Đất Xanh thông báo Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 — Evidence: N001.
   - Key fact F01: DXG: Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 Công ty Cổ phần Tập đoàn Đất Xanh thông báo Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 DXG: Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 Công ty Cổ phần Tập đoàn Đất Xanh thông báo Nghị quyết HĐ

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 75.3329, hướng `positive_but_overbought_risk`.
- Driver cần theo dõi: `return_2q_ago` = -0.0658, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `legal_risk` — DXG: Nghị quyết HĐQT về việc lựa chọn đơn vị kiểm toán cho năm 2025 (2025-06-26).
- News/event cần kiểm tra thủ công: `earnings,debt_risk,governance,market` — chon co dat nao cho 6 thang cuoi nam vhm nlg dxg hdc 1386029.html (2025-06-20).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q2_VBB_03

### 1. Tóm tắt tín hiệu

- Ticker: **VBB**
- Decision date: 2025-06-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9982
- Rank trong kỳ: 3
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã VBB được chọn vào Top-5 của kỳ 2025Q2 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9982 và rank 3 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 65.4593, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0051, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0512, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: VBB: Quyết định của NHNN về việc bổ sung nội dung hoạt động vào Giấy phép thành lập và hoạt động của Vietbank (cafef, 2025-06-30). Tóm tắt: Quyết định của NHNN về việc bổ sung nội dung hoạt động vào Giấy phép thành lập và hoạt động của Vietbank VBB: Quyết định của NHNN về việc bổ sung nội dung hoạt động vào Giấy phép thành lập và hoạt động của Vietbank Quyết định của NHNN về việc bổ sung nội dung hoạt động vào Giấy phép thành lập và hoạt động của Vietbank — Evidence: N001.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — VBB: Miễn nhiệm chức danh Phó Tổng giám đốc đối với Bà Phạm Thị Mỹ Chi (2025-06-30).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — VBB: Quyết định của NHNN về việc bổ sung nội dung hoạt động vào Giấy phép thành lập và hoạt động của Vietbank (2025-06-30).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q2_MSN_04

### 1. Tóm tắt tín hiệu

- Ticker: **MSN**
- Decision date: 2025-06-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9972
- Rank trong kỳ: 4
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã MSN được chọn vào Top-5 của kỳ 2025Q2 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9972 và rank 4 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 84.9994, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1094, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.1349, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: tien ngoai tro lai ung ho thi truong msn nlg cung dbc la tam diem 1388017.html (kinhtechungkhoan, 2025-06-30). Tóm tắt: Khối ngoại mua ròng hơn 500 tỷ đồng phiên 30/6, tập trung gom MSN, NLG và DBC. Trong khi đó, HPG, PVS và MCH bị rút vốn mạnh. Thị trường chứng khoán Việt Nam khởi đầu tuần giao dịch cuối cùng của tháng 6 với sắc xanh lan tỏa. — Evidence: N001.
   - Key fact F01: tien ngoai tro lai ung ho thi truong msn nlg cung dbc la tam diem 1388017.html nan Khối ngoại mua ròng hơn 500 tỷ đồng phiên 30/6, tập trung gom MSN, NLG và DBC.
   - Key fact F02: Thị trường chứng khoán Việt Nam khởi đầu tuần giao dịch cuối cùng của tháng 6 với sắc xanh lan tỏa.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 84.9994, hướng `positive_but_overbought_risk`.
- Driver cần theo dõi: `return_2q_ago` = -0.0862, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `debt_risk,governance,market` — tien ngoai tro lai ung ho thi truong msn nlg cung dbc la tam diem 1388017.html (2025-06-30).
- News/event cần kiểm tra thủ công: `dividend,earnings,market` — Top 10 cổ phiếu tăng/giảm mạnh nhất tuần: MSN và cặp đôi VIC-VHM đẩy VN-Index bay cao (2025-06-27).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q2_VND_05

### 1. Tóm tắt tín hiệu

- Ticker: **VND**
- Decision date: 2025-06-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9971
- Rank trong kỳ: 5
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã VND được chọn vào Top-5 của kỳ 2025Q2 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9971 và rank 5 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 65.8972, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = -0.0110, hướng `weak_or_negative` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0524, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: VND: Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng (cafef, 2025-06-27). Tóm tắt: Công ty Cổ phần Chứng khoán VNDIRECT thông báo Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng VND: Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng Công ty Cổ phần Chứng khoán VNDIRECT thông báo Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng — Evidence: N001.
   - Key fact F01: VND: Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng Công ty Cổ phần Chứng khoán VNDIRECT thông báo Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng VND: Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `macd_hist_mean_q` = -0.0110, hướng `weak_or_negative`.
- Driver cần theo dõi: `return_2q_ago` = -0.1848, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `debt_risk` — VND: Quyết định của HĐQT về việc thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng (2025-06-27).
- News/event cần kiểm tra thủ công: `debt_risk,capital` — VND: Nghị quyết HĐQT về việc phát hành trái phiếu ra công chúng năm 2025 (2025-06-26).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q3_LPB_01

### 1. Tóm tắt tín hiệu

- Ticker: **LPB**
- Decision date: 2025-09-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9985
- Rank trong kỳ: 1
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã LPB được chọn vào Top-5 của kỳ 2025Q3 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9985 và rank 1 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 73.8891, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1005, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0875, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: LPB: Nghị quyết HĐQT về việc thay đổi địa điểm trụ sở chi nhánh Hải Phòng, PGD Trường Chinh, PGD Mỹ Đình (vietstock, 2025-09-30). Tóm tắt: LPB: Nghị quyết HĐQT về việc thay đổi địa điểm trụ sở chi nhánh Hải Phòng, PGD Trường Chinh, PGD Mỹ Đình Ngân hàng Thương mại Cổ phần Lộc Phát Việt Nam công bố Nghị quyết HĐQT về việc thay đổi địa điểm trụ sở chi nhánh Hải Phòng, PGD Trường Chinh, PGD Mỹ Đình như sau: Ngân hàng Thương mại Cổ phần Lộc Phát Việt Nam công bố Nghị quyết HĐQT về việc thay đổi địa điểm trụ sở chi nhánh Hải Phòng, PGD Trường Chinh, PGD Mỹ Đình như sau: LPB: Nghị quyết HĐQT về việc thay đổi địa điểm trụ sở chi nhánh Hải Phòng, PGD Trường Chinh, PGD Mỹ Đình — Evidence: N001.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 73.8891, hướng `positive_but_overbought_risk`.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — CBTT về việc đăng ký giao dịch trái phiếu LPB12503 của Ngân hàng Thương mại Cổ phần Lộc Phát Việt Nam (tên cũ: Ngân hàng Thương mại cổ phần Bưu Điện Liên Việt) (2025-09-23).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — CBTT về việc đăng ký giao dịch trái phiếu LPB12504 của Ngân hàng Thương mại Cổ phần Lộc Phát Việt Nam (tên cũ: Ngân hàng Thương mại cổ phần Bưu Điện Liên Việt) (2025-09-23).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q3_VIC_02

### 1. Tóm tắt tín hiệu

- Ticker: **VIC**
- Decision date: 2025-09-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9970
- Rank trong kỳ: 2
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã VIC được chọn vào Top-5 của kỳ 2025Q3 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9970 và rank 2 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 83.9426, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.2004, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.2211, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: VIC: CBTT phát hành trái phiếu riêng lẻ 3.500 tỷ (cafef, 2025-09-30). Tóm tắt: Tập đoàn Vingroup - Công ty Cổ phần thông báo phát hành trái phiếu riêng lẻ 3.500 tỷ VIC: CBTT phát hành trái phiếu riêng lẻ 3.500 tỷ Tập đoàn Vingroup - Công ty Cổ phần thông báo phát hành trái phiếu riêng lẻ 3.500 tỷ — Evidence: N001.
   - Key fact F01: VIC: CBTT phát hành trái phiếu riêng lẻ 3.500 tỷ Tập đoàn Vingroup - Công ty Cổ phần thông báo phát hành trái phiếu riêng lẻ 3.500 tỷ VIC: CBTT phát hành trái phiếu riêng lẻ 3.500 tỷ Tập đoàn Vingroup - Công ty Cổ phần thông báo phát hành trái phiếu riêng lẻ 3.500 tỷ

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 83.9426, hướng `positive_but_overbought_risk`.
- News/event cần kiểm tra thủ công: `debt_risk,capital` — VIC: CBTT phát hành trái phiếu riêng lẻ 3.500 tỷ (2025-09-30).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,governance,market` — co phieu ho vingroup lai thang hoa ty phu pham nhat vuong lap ky luc chua tung co 1405072.html (2025-09-30).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q3_VRE_03

### 1. Tóm tắt tín hiệu

- Ticker: **VRE**
- Decision date: 2025-09-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9941
- Rank trong kỳ: 3
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã VRE được chọn vào Top-5 của kỳ 2025Q3 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9941 và rank 3 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 66.8366, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = -0.0025, hướng `weak_or_negative` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0666, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: VRE: Nghị quyết HĐQT về việc thực hiện chi trả lợi nhuận trong công ty của VRE (cafef, 2025-09-29). Tóm tắt: Công ty Cổ phần Vincom Retail công bố Nghị quyết HĐQT về việc thực hiện chi trả lợi nhuận trong công ty của VRE VRE: Nghị quyết HĐQT về việc thực hiện chi trả lợi nhuận trong công ty của VRE Công ty Cổ phần Vincom Retail công bố Nghị quyết HĐQT về việc thực hiện chi trả lợi nhuận trong công ty của VRE — Evidence: N001.
   - Key fact F01: VRE: Nghị quyết HĐQT về việc thực hiện chi trả lợi nhuận trong công ty của VRE Công ty Cổ phần Vincom Retail công bố Nghị quyết HĐQT về việc thực hiện chi trả lợi nhuận trong công ty của VRE VRE: Nghị quyết HĐQT về việc thực hiện chi trả lợi nhuận trong công ty của VRE Công ty Cổ phần Vincom Retail 

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `macd_hist_mean_q` = -0.0025, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `earnings,debt_risk,governance,market` — vincom retail vre sap mo ban shophouse vinhomes va mo them 3 vincom mega mall trong nam nay 1398746.html (2025-08-28).
- News/event cần kiểm tra thủ công: `earnings,debt_risk,governance` — Vincom Retail đã đặt cọc 1.8 ngàn tỷ để nhận chuyển nhượng một phần dự án Cần Giờ (2025-08-12).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q3_KDH_04

### 1. Tóm tắt tín hiệu

- Ticker: **KDH**
- Decision date: 2025-09-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9921
- Rank trong kỳ: 4
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã KDH được chọn vào Top-5 của kỳ 2025Q3 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9921 và rank 4 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 48.1968, hướng `weak_or_neutral` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0095, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = -0.0221, hướng `weak_or_negative` — Evidence: `top_drivers`.
5. Tin gần decision date: khoi ngoai lai giao dich kem tich cuc tam diem kdh cung hpg 1405056.html (kinhtechungkhoan, 2025-09-30). Tóm tắt: Khối ngoại bán ròng 1.268 tỷ đồng phiên cuối tháng 9, KDH và HPG bị xả mạnh, trong khi CII và SHB là điểm sáng được gom mạnh. Phiên giao dịch cuối cùng tháng 9/2025 khép lại trong trạng thái giằng co, VN-Index giảm nhẹ gần 5 điểm, dừng tại 1.661,7 điểm. Thanh khoản vẫn duy trì ở mức cao với giá trị khớp lệnh trên HoSE đạt 29.155 tỷ đồng, tăng so với khoảng 23.380 tỷ đồng của phiên 29/9, cho thấy dòng tiền trong nước vẫn khá sôi động dù chỉ số suy yếu. — Evidence: N001.
   - Key fact F01: khoi ngoai lai giao dich kem tich cuc tam diem kdh cung hpg 1405056.html nan Khối ngoại bán ròng 1.268 tỷ đồng phiên cuối tháng 9, KDH và HPG bị xả mạnh, trong khi CII và SHB là điểm sáng được gom mạnh.
   - Key fact F02: Phiên giao dịch cuối cùng tháng 9/2025 khép lại trong trạng thái giằng co, VN-Index giảm nhẹ gần 5 điểm, dừng tại 1.661,7 điểm.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 48.1968, hướng `weak_or_neutral`.
- Driver cần theo dõi: `price_vs_sma20` = -0.0221, hướng `weak_or_negative`.
- Driver cần theo dõi: `return_2q_ago` = -0.0723, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `debt_risk,governance,market` — khoi ngoai lai giao dich kem tich cuc tam diem kdh cung hpg 1405056.html (2025-09-30).
- News/event cần kiểm tra thủ công: `governance,market` — Lãnh đạo mua bán cổ phiếu: Hai quỹ lớn muốn thoái vốn tại KDH và OPC (2025-09-26).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q3_SCR_05

### 1. Tóm tắt tín hiệu

- Ticker: **SCR**
- Decision date: 2025-09-30
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9904
- Rank trong kỳ: 5
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã SCR được chọn vào Top-5 của kỳ 2025Q3 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9904 và rank 5 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 52.8499, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = -0.0050, hướng `weak_or_negative` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0226, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: SCR: Công văn công bố BCTC bán niên soát xét 2025 kèm giải trình (cafef, 2025-09-03). Tóm tắt: Công ty Cổ phần Địa ốc Sài Gòn Thương Tín thông báo công văn công bố BCTC bán niên soát xét 2025 kèm giải trình SCR: Công văn công bố BCTC bán niên soát xét 2025 kèm giải trình Công ty Cổ phần Địa ốc Sài Gòn Thương Tín thông báo công văn công bố BCTC bán niên soát xét 2025 kèm giải trình — Evidence: N001.
   - Key fact F01: SCR: Công văn công bố BCTC bán niên soát xét 2025 kèm giải trình Công ty Cổ phần Địa ốc Sài Gòn Thương Tín thông báo công văn công bố BCTC bán niên soát xét 2025 kèm giải trình SCR: Công văn công bố BCTC bán niên soát xét 2025 kèm giải trình Công ty Cổ phần Địa ốc Sài Gòn Thương Tín thông báo công v

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `macd_hist_mean_q` = -0.0050, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `legal_risk` — SCR: Công văn công bố BCTC bán niên soát xét 2025 kèm giải trình (2025-09-03).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — SCR: Giấy chứng nhận đăng ký địa điểm kinh doanh Cơ sở 1 Tây Ninh (2025-09-03).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q4_GAS_01

### 1. Tóm tắt tín hiệu

- Ticker: **GAS**
- Decision date: 2025-12-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9977
- Rank trong kỳ: 1
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã GAS được chọn vào Top-5 của kỳ 2025Q4 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9977 và rank 1 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 67.5243, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1337, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0960, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: GAS: Nghị quyết HĐQT số 102 ngày 31/12/2025 (vietstock, 2025-12-31). Tóm tắt: Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái sinh Chứng quyền Ý kiến chuyên gia Câu chuyện đầu tư Chính sách Trái phiếu DOANH NGHIỆP Hoạt động kinh doanh Cổ tức Tăng vốn - M&A IPO - Cổ phần hóa Nhân vật Trái phiếu doanh nghiệp BẤT ĐỘNG SẢN Thị trường nhà đất Quy hoạch - Hạ tầng Dự án Bảo hiểm và thuế nhà đất TÀI CHÍNH Ngân hàng Bảo hiểm Thuế và Ngân sách Tài sản số HÀNG HÓA Vàng và kim loại quý Nhiên liệu Kim loại Nông sản thực phẩm KINH TẾ Vĩ mô Kinh tế - Đầu tư THẾ GIỚI Chứng khoán thế giới Tiền kỹ thuật số Tài chính quốc tế Kinh tế - Đầu tư TÀI CHÍNH CÁ NHÂN Làm chủ đồng tiền Đầu tư – Kinh doanh nhỏ Doanh nhân và khởi nghiệp Chơi sang Xe - Công nghệ Tiêu dùng và lối sống Vì cộng đồng PHÂN TÍCH Nhận định thị trường Phân tích cơ bản Phân tích kỹ thuật ĐÔNG DƯƠNG Vĩ mô Tài chính - Ngân hàng Thị trường chứng khoán Kinh tế - Đầu tư CHỦ ĐỀ NÓNG Quan hệ Nhà đầu tư (IR) ĐHĐCĐ thường niên 2026 Nâng hạng thị trường Trump 2.0 Trung tâm tài chính Các kênh đầu tư DỮ LIỆU NGÀNH Tổng quan ngành Ngành chi tiết DỮ LIỆU DOANH NGHIỆP Doanh nghiệp A-Z Lịch sự kiện Cập nhật lãi lỗ Giao dịch nội bộ Tài liệu cổ đông Niên gi — Evidence: N001.
   - Key fact F01: GAS: Nghị quyết HĐQT số 102 ngày 31/12/2025 nan Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái sinh Chứng quyền Ý kiến chuyên gia Câu chuyện đầu tư Chính sách Trái phiếu DOANH NGHIỆP Hoạt động kinh doanh Cổ tức Tăng vốn - M
   - Key fact F02: Ngày 30/06/2026, CTCP Nhiệt điện Quảng Ninh (UPCoM: QTP) đã tổ chức ĐHĐCĐ bất thường năm 2026 nhằm thông qua việc điều chỉnh dự án nâng cấp, cải tạo hệ thống xử lý...

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — GAS: Nghị quyết HĐQT số 102 ngày 31/12/2025 (2025-12-31).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — GAS: CBTT đáp ứng điều kiện công ty đại chúng (2025-12-26).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q4_MCH_02

### 1. Tóm tắt tín hiệu

- Ticker: **MCH**
- Decision date: 2025-12-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9944
- Rank trong kỳ: 2
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã MCH được chọn vào Top-5 của kỳ 2025Q4 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9944 và rank 2 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 66.0609, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.2268, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0218, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: MCH: 9.1.2026, ngày GDKHQ sử dụng cổ phiếu quỹ để chia cho cổ đông hiện hữu (tỷ lệ 10.000:103), thưởng cp (tỷ lệ 10.000:2.147), tạm ứng cổ tức đợt 2 năm 2025 bằng tiền (2.500 đ/cp), lấy ý kiến cổ đông bằng văn bản (cafef, 2025-12-30). Tóm tắt: Sở Giao dịch Chứng khoán TP.HCM thông báo về ngày đăng ký cuối cùng sử dụng cổ phiếu quỹ để chia cho cổ đông hiện hữu, phát hành cổ phiếu để tăng vốn cổ phần từ nguồn vốn chủ sở hữu, tạm ứng cổ tức đợt 2 năm 2025 bằng tiền, lấy ý kiến cổ đông bằng văn bản của Công ty Cổ phần Hàng tiêu dùng Masan MCH: 9.1.2026, ngày GDKHQ sử dụng cổ phiếu quỹ để chia cho cổ đông hiện hữu (tỷ lệ 10.000:103), thưởng cp (tỷ lệ 10.000:2.147), tạm ứng cổ tức đợt 2 năm 2025 bằng tiền (2.500 đ/cp), lấy ý kiến cổ đông bằng văn bản Sở Giao dịch Chứng khoán TP.HCM thông báo về ngày đăng ký cuối cùng sử dụng cổ phiếu quỹ để chia cho cổ đông hiện hữu, phát hành cổ phiếu để tăng vốn cổ phần từ nguồn vốn chủ sở hữu, tạm ứng cổ tức đợt 2 năm 2025 bằng tiền, lấy ý kiến cổ đông bằng văn bản của Công ty Cổ phần Hàng tiêu dùng Masan — Evidence: N001.
   - Key fact F01: MCH: 9.1.2026, ngày GDKHQ sử dụng cổ phiếu quỹ để chia cho cổ đông hiện hữu (tỷ lệ 10.000:103), thưởng cp (tỷ lệ 10.000:2.147), tạm ứng cổ tức đợt 2 năm 2025 bằng tiền (2.500 đ/cp), lấy ý kiến cổ đông bằng văn bản Sở Giao dịch Chứng khoán TP.HCM thông báo về ngày đăng ký cuối cùng sử dụng cổ phiếu q

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `return_2q_ago` = -0.1077, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `dividend,capital` — MCH: 9.1.2026, ngày GDKHQ sử dụng cổ phiếu quỹ để chia cho cổ đông hiện hữu (tỷ lệ 10.000:103), thưởng cp (tỷ lệ 10.000:2.147), tạm ứng cổ tức đợt 2 năm 2025 bằng tiền (2.500 đ/cp), lấy ý kiến cổ đông bằng văn bản (2025-12-30).
- News/event cần kiểm tra thủ công: `dividend,capital,legal_risk,market` — Vừa lên HOSE, MCH đã chốt quyền "phát quà" kép cho cổ đông (2025-12-30).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q4_ABB_03

### 1. Tóm tắt tín hiệu

- Ticker: **ABB**
- Decision date: 2025-12-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9926
- Rank trong kỳ: 3
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã ABB được chọn vào Top-5 của kỳ 2025Q4 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9926 và rank 3 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 66.2689, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0216, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0288, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: ABBank chốt quyền chào bán cổ phiếu ra công chúng, tăng vốn lên 13,455 tỷ (vietstock, 2025-12-29). Tóm tắt: ABBank chốt quyền chào bán cổ phiếu ra công chúng, tăng vốn lên 13,455 tỷ Ngày 31/12/2025, Ngân hàng TMCP An Bình (ABBank, UPCoM: ABB ) nhận được giấy chứng nhận đăng ký chào bán thêm cổ phiếu ra công chúng, theo đó tăng vốn điều lệ thêm hơn 3,105 tỷ đồng. Cụ thể, ABBank dự kiến chào bán hơn 310.5 triệu cp với giá 10,000 đồng/cp cho cổ đông hiện hữu. Tỷ lệ thực hiện quyền: 100:30 (cổ đông sở hữu 100 cp tại ngày chốt danh sách được mua thêm 30 cp mới). — Evidence: N001.
   - Key fact F01: ABBank chốt quyền chào bán cổ phiếu ra công chúng, tăng vốn lên 13,455 tỷ nan ABBank chốt quyền chào bán cổ phiếu ra công chúng, tăng vốn lên 13,455 tỷ Ngày 31/12/2025, Ngân hàng TMCP An Bình (ABBank, UPCoM: ABB ) nhận được giấy chứng nhận đăng ký chào bán thêm cổ phiếu ra công chúng, theo đó tăng v
   - Key fact F02: Cụ thể, ABBank dự kiến chào bán hơn 310.5 triệu cp với giá 10,000 đồng/cp cho cổ đông hiện hữu.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `capital,market` — ABBank chốt quyền chào bán cổ phiếu ra công chúng, tăng vốn lên 13,455 tỷ (2025-12-29).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — CBTT về việc đăng ký giao dịch trái phiếu ABB12517 của Ngân hàng TMCP An Bình (ABBANK) (2025-12-29).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q4_ELC_04

### 1. Tóm tắt tín hiệu

- Ticker: **ELC**
- Decision date: 2025-12-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9852
- Rank trong kỳ: 4
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã ELC được chọn vào Top-5 của kỳ 2025Q4 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9852 và rank 4 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 71.3503, hướng `positive_but_overbought_risk` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0334, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0494, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: ELC: Thông báo mua lại cổ phiếu của CBNV nghỉ việc theo quy chế ESOP (cafef, 2025-12-05). Tóm tắt: Công ty Cổ phần Công nghệ - Viễn thông ELCOM thông báo mua lại cổ phiếu của CBNV nghỉ việc theo quy chế ESOP ELC: Thông báo mua lại cổ phiếu của CBNV nghỉ việc theo quy chế ESOP Công ty Cổ phần Công nghệ - Viễn thông ELCOM thông báo mua lại cổ phiếu của CBNV nghỉ việc theo quy chế ESOP — Evidence: N001.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 71.3503, hướng `positive_but_overbought_risk`.
- Driver cần theo dõi: `return_2q_ago` = -0.0581, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — ELC: Thông báo thay đổi nhân sự và Nghị quyết HĐQT (2025-12-05).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — ELC: Thông báo mua lại cổ phiếu của CBNV nghỉ việc theo quy chế ESOP (2025-12-02).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2025Q4_VBB_05

### 1. Tóm tắt tín hiệu

- Ticker: **VBB**
- Decision date: 2025-12-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9822
- Rank trong kỳ: 5
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã VBB được chọn vào Top-5 của kỳ 2025Q4 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9822 và rank 5 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 47.8687, hướng `weak_or_neutral` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = -0.0055, hướng `weak_or_negative` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0091, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: VBB: Bổ nhiệm Bà Đoàn Thị Thanh Hương phụ trách điều hành chi nhánh Bình Định thay cho Ông Nguyễn Văn Phú - Bổ nhiệm Ông Nguyễn Hồng Hải giữ chức Giám đốc chi nhánh BR - VT (vietstock, 2025-12-29). Tóm tắt: Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái sinh Chứng quyền Ý kiến chuyên gia Câu chuyện đầu tư Chính sách Trái phiếu DOANH NGHIỆP Hoạt động kinh doanh Cổ tức Tăng vốn - M&A IPO - Cổ phần hóa Nhân vật Trái phiếu doanh nghiệp BẤT ĐỘNG SẢN Thị trường nhà đất Quy hoạch - Hạ tầng Dự án Bảo hiểm và thuế nhà đất TÀI CHÍNH Ngân hàng Bảo hiểm Thuế và Ngân sách Tài sản số HÀNG HÓA Vàng và kim loại quý Nhiên liệu Kim loại Nông sản thực phẩm KINH TẾ Vĩ mô Kinh tế - Đầu tư THẾ GIỚI Chứng khoán thế giới Tiền kỹ thuật số Tài chính quốc tế Kinh tế - Đầu tư TÀI CHÍNH CÁ NHÂN Làm chủ đồng tiền Đầu tư – Kinh doanh nhỏ Doanh nhân và khởi nghiệp Chơi sang Xe - Công nghệ Tiêu dùng và lối sống Vì cộng đồng PHÂN TÍCH Nhận định thị trường Phân tích cơ bản Phân tích kỹ thuật ĐÔNG DƯƠNG Vĩ mô Tài chính - Ngân hàng Thị trường chứng khoán Kinh tế - Đầu tư CHỦ ĐỀ NÓNG Quan hệ Nhà đầu tư (IR) ĐHĐCĐ thường niên 2026 Nâng hạng thị trường Trump 2.0 Trung tâm tài chính Các kênh đầu tư DỮ LIỆU NGÀNH Tổng quan ngành Ngành chi tiết DỮ LIỆU DOANH NGHIỆP Doanh nghiệp A-Z Lịch sự kiện Cập nhật lãi lỗ Giao dịch nội bộ Tài liệu cổ đông Niên gi — Evidence: N001.
   - Key fact F01: VBB: Bổ nhiệm Bà Đoàn Thị Thanh Hương phụ trách điều hành chi nhánh Bình Định thay cho Ông Nguyễn Văn Phú - Bổ nhiệm Ông Nguyễn Hồng Hải giữ chức Giám đốc chi nhánh BR - VT nan Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái
   - Key fact F02: Đến nay cơ quan điều tra đã khởi tố 31 bị can liên quan đến vụ án tại Tổng công ty Cảng hàng không Việt Nam ACV về nhiều tội danh.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `rsi_end_q` = 47.8687, hướng `weak_or_neutral`.
- Driver cần theo dõi: `macd_hist_mean_q` = -0.0055, hướng `weak_or_negative`.
- Driver cần theo dõi: `return_q` = -0.0744, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — VBB: Bổ nhiệm Bà Đoàn Thị Thanh Hương phụ trách điều hành chi nhánh Bình Định thay cho Ông Nguyễn Văn Phú - Bổ nhiệm Ông Nguyễn Hồng Hải giữ chức Giám đốc chi nhánh BR - VT (2025-12-29).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — VBB: Ông Phạm Danh – Phó Tổng Giám đốc đã thực hiện 19,828 quyền mua cổ phần trong đợt chào bán cổ phiếu cho cổ đông hiện hữu (2025-12-26).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2026Q1_GMD_01

### 1. Tóm tắt tín hiệu

- Ticker: **GMD**
- Decision date: 2026-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9918
- Rank trong kỳ: 1
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã GMD được chọn vào Top-5 của kỳ 2026Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9918 và rank 1 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 57.5606, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1348, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0405, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: GMD: Gemadept và CJ Logistics tối ưu hóa Chiến lược hợp tác giữa hai doanh nghiệp (cafef, 2026-03-31). Tóm tắt: Công ty Cổ phần GEMADEPT công bố về việc Gemadept và CJ Logistics tối ưu hóa Chiến lược hợp tác giữa hai doanh nghiệp GMD: Gemadept và CJ Logistics tối ưu hóa Chiến lược hợp tác giữa hai doanh nghiệp Công ty Cổ phần GEMADEPT công bố về việc Gemadept và CJ Logistics tối ưu hóa Chiến lược hợp tác giữa hai doanh nghiệp — Evidence: N001.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — GMD: CBTT nội dung Nghị quyết HĐQT số 057 về việc chuyển nhượng cổ phần (2026-03-31).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — GMD: Gemadept và CJ Logistics tối ưu hóa Chiến lược hợp tác giữa hai doanh nghiệp (2026-03-31).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2026Q1_EVF_02

### 1. Tóm tắt tín hiệu

- Ticker: **EVF**
- Decision date: 2026-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9916
- Rank trong kỳ: 2
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã EVF được chọn vào Top-5 của kỳ 2026Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9916 và rank 2 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 56.9772, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0473, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0247, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: EVF: CBTT bổ nhiệm lại KTT (vietstock, 2026-03-23). Tóm tắt: Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái sinh Chứng quyền Ý kiến chuyên gia Câu chuyện đầu tư Chính sách Trái phiếu DOANH NGHIỆP Hoạt động kinh doanh Cổ tức Tăng vốn - M&A IPO - Cổ phần hóa Nhân vật Trái phiếu doanh nghiệp BẤT ĐỘNG SẢN Thị trường nhà đất Quy hoạch - Hạ tầng Dự án Bảo hiểm và thuế nhà đất TÀI CHÍNH Ngân hàng Bảo hiểm Thuế và Ngân sách Tài sản số HÀNG HÓA Vàng và kim loại quý Nhiên liệu Kim loại Nông sản thực phẩm KINH TẾ Vĩ mô Kinh tế - Đầu tư THẾ GIỚI Chứng khoán thế giới Tiền kỹ thuật số Tài chính quốc tế Kinh tế - Đầu tư TÀI CHÍNH CÁ NHÂN Làm chủ đồng tiền Đầu tư – Kinh doanh nhỏ Doanh nhân và khởi nghiệp Chơi sang Xe - Công nghệ Tiêu dùng và lối sống Vì cộng đồng PHÂN TÍCH Nhận định thị trường Phân tích cơ bản Phân tích kỹ thuật ĐÔNG DƯƠNG Vĩ mô Tài chính - Ngân hàng Thị trường chứng khoán Kinh tế - Đầu tư CHỦ ĐỀ NÓNG Quan hệ Nhà đầu tư (IR) ĐHĐCĐ thường niên 2026 Nâng hạng thị trường Trump 2.0 Trung tâm tài chính Các kênh đầu tư DỮ LIỆU NGÀNH Tổng quan ngành Ngành chi tiết DỮ LIỆU DOANH NGHIỆP Doanh nghiệp A-Z Lịch sự kiện Cập nhật lãi lỗ Giao dịch nội bộ Tài liệu cổ đông Niên gi — Evidence: N001.
   - Key fact F01: EVF: CBTT bổ nhiệm lại KTT nan Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái sinh Chứng quyền Ý kiến chuyên gia Câu chuyện đầu tư Chính sách Trái phiếu DOANH NGHIỆP Hoạt động kinh doanh Cổ tức Tăng vốn - M&A IPO - Cổ phần 
   - Key fact F02: Đến nay cơ quan điều tra đã khởi tố 31 bị can liên quan đến vụ án tại Tổng công ty Cảng hàng không Việt Nam ACV về nhiều tội danh.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — EVF: CBTT bổ nhiệm lại KTT (2026-03-23).
- News/event cần kiểm tra thủ công: `debt_risk,capital` — EVF: Nghị quyết HĐQT phê duyệt phương án phát hành Trái phiếu tăng vốn cấp 2 theo hình thức riêng lẻ năm 2026 (2026-03-11).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2026Q1_DPM_03

### 1. Tóm tắt tín hiệu

- Ticker: **DPM**
- Decision date: 2026-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9719
- Rank trong kỳ: 3
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã DPM được chọn vào Top-5 của kỳ 2026Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9719 và rank 3 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 52.1123, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.0902, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = -0.0245, hướng `weak_or_negative` — Evidence: `top_drivers`.
5. Tin gần decision date: DPM: Thông báo mời họp ĐHĐCĐ thường niên năm 2026 (cafef, 2026-03-26). Tóm tắt: Tổng Công ty Phân bón và Hóa chất Dầu khí - Công ty Cổ phần thông báo mời họp ĐHĐCĐ thường niên năm 2026 DPM: Thông báo mời họp ĐHĐCĐ thường niên năm 2026 Tổng Công ty Phân bón và Hóa chất Dầu khí - Công ty Cổ phần thông báo mời họp ĐHĐCĐ thường niên năm 2026 — Evidence: N001.
   - Key fact F01: DPM: Thông báo mời họp ĐHĐCĐ thường niên năm 2026 Tổng Công ty Phân bón và Hóa chất Dầu khí - Công ty Cổ phần thông báo mời họp ĐHĐCĐ thường niên năm 2026 DPM: Thông báo mời họp ĐHĐCĐ thường niên năm 2026 Tổng Công ty Phân bón và Hóa chất Dầu khí - Công ty Cổ phần thông báo mời họp ĐHĐCĐ thường niên

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `price_vs_sma20` = -0.0245, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `earnings,legal_risk` — DPM: Giải trình biến động KQKD năm 2025 sau kiểm toán so với cùng kỳ năm trước (2026-03-26).
- News/event cần kiểm tra thủ công: `legal_risk` — DPM: Công bố thông tin BCTC Hợp nhất và Riêng năm 2025 đã kiểm toán (2026-03-26).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2026Q1_DCM_04

### 1. Tóm tắt tín hiệu

- Ticker: **DCM**
- Decision date: 2026-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9584
- Rank trong kỳ: 4
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã DCM được chọn vào Top-5 của kỳ 2026Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9584 và rank 4 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 58.6298, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1450, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0313, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: DCM: Quyết định của HĐQT về việc thành lập Chi nhánh - Thương mại & Dịch vụ (vietstock, 2026-03-27). Tóm tắt: Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái sinh Chứng quyền Ý kiến chuyên gia Câu chuyện đầu tư Chính sách Trái phiếu DOANH NGHIỆP Hoạt động kinh doanh Cổ tức Tăng vốn - M&A IPO - Cổ phần hóa Nhân vật Trái phiếu doanh nghiệp BẤT ĐỘNG SẢN Thị trường nhà đất Quy hoạch - Hạ tầng Dự án Bảo hiểm và thuế nhà đất TÀI CHÍNH Ngân hàng Bảo hiểm Thuế và Ngân sách Tài sản số HÀNG HÓA Vàng và kim loại quý Nhiên liệu Kim loại Nông sản thực phẩm KINH TẾ Vĩ mô Kinh tế - Đầu tư THẾ GIỚI Chứng khoán thế giới Tiền kỹ thuật số Tài chính quốc tế Kinh tế - Đầu tư TÀI CHÍNH CÁ NHÂN Làm chủ đồng tiền Đầu tư – Kinh doanh nhỏ Doanh nhân và khởi nghiệp Chơi sang Xe - Công nghệ Tiêu dùng và lối sống Vì cộng đồng PHÂN TÍCH Nhận định thị trường Phân tích cơ bản Phân tích kỹ thuật ĐÔNG DƯƠNG Vĩ mô Tài chính - Ngân hàng Thị trường chứng khoán Kinh tế - Đầu tư CHỦ ĐỀ NÓNG Quan hệ Nhà đầu tư (IR) ĐHĐCĐ thường niên 2026 Nâng hạng thị trường Trump 2.0 Trung tâm tài chính Các kênh đầu tư DỮ LIỆU NGÀNH Tổng quan ngành Ngành chi tiết DỮ LIỆU DOANH NGHIỆP Doanh nghiệp A-Z Lịch sự kiện Cập nhật lãi lỗ Giao dịch nội bộ Tài liệu cổ đông Niên gi — Evidence: N001.
   - Key fact F01: DCM: Quyết định của HĐQT về việc thành lập Chi nhánh - Thương mại & Dịch vụ nan Vietstock - Trang thông tin điện tử tổng hợp CHỨNG KHOÁN Cổ phiếu Giao dịch nội bộ Niêm yết ETF và các quỹ Chứng khoán phái sinh Chứng quyền Ý kiến chuyên gia Câu chuyện đầu tư Chính sách Trái phiếu DOANH NGHIỆP Hoạt độn
   - Key fact F02: Ngày 30/06/2026, CTCP Nhiệt điện Quảng Ninh (UPCoM: QTP) đã tổ chức ĐHĐCĐ bất thường năm 2026 nhằm thông qua việc điều chỉnh dự án nâng cấp, cải tạo hệ thống xử lý...

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — DCM: Quyết định của HĐQT về việc thành lập Chi nhánh - Thương mại & Dịch vụ (2026-03-27).
- News/event cần kiểm tra thủ công: `dividend,earnings,capital,market` — Đạm Cà Mau lên kế hoạch lợi nhuận 2026 giảm mạnh, cổ tức dự kiến còn một nửa (2026-03-25).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.

---

## Decision Card: 2026Q1_REE_05

### 1. Tóm tắt tín hiệu

- Ticker: **REE**
- Decision date: 2026-03-31
- Trạng thái: **Buy Candidate**
- Xác suất tăng theo ML: 0.9533
- Rank trong kỳ: 5
- Số news evidence trước decision date: 5

### 2. Luận điểm đầu tư chính

Mã REE được chọn vào Top-5 của kỳ 2026Q1 dựa trên tín hiệu kỹ thuật từ mô hình ML. Luận điểm ban đầu nên được xem là luận điểm định lượng, cần được xác nhận thêm bằng bối cảnh tin tức và các trigger theo dõi.

### 3. Yếu tố hỗ trợ

1. Tín hiệu ML có xác suất tăng 0.9533 và rank 5 trong kỳ — Evidence: `ml_signal`.
2. `rsi_end_q` = 59.0921, hướng `supports_up_signal` — Evidence: `top_drivers`.
3. `macd_hist_mean_q` = 0.1528, hướng `supports_up_signal` — Evidence: `top_drivers`.
4. `price_vs_sma20` = 0.0529, hướng `supports_up_signal` — Evidence: `top_drivers`.
5. Tin gần decision date: SGR: Báo cáo kết quả giao dịch cổ phiếu của tổ chức có liên quan đến người nội bộ Công ty TNHH BĐS REE (vietstock, 2026-03-31). Tóm tắt: SGR: Báo cáo kết quả giao dịch cổ phiếu của tổ chức có liên quan đến người nội bộ Công ty TNHH BĐS REE Công ty TNHH BĐS REE báo cáo kết quả giao dịch cổ phiếu của tổ chức có liên quan đến người nội bộ Công ty Cổ phần Tổng Công ty Cổ phần Địa ốc Sài Gòn như sau: Công ty TNHH BĐS REE báo cáo kết quả giao dịch cổ phiếu của tổ chức có liên quan đến người nội bộ Công ty Cổ phần Tổng Công ty Cổ phần Địa ốc Sài Gòn như sau: SGR: Báo cáo kết quả giao dịch cổ phiếu của tổ chức có liên quan đến người nội bộ Công ty TNHH BĐS REE — Evidence: N001.

### 4. Rủi ro và điểm cần theo dõi

- Tín hiệu ML dựa trên dữ liệu lịch sử, không đảm bảo hiệu quả tương lai.
- Nếu rank/probability giảm trong kỳ cập nhật sau, cần chuyển trạng thái Review Required.
- Nếu tin mới trái chiều hoặc drawdown vượt 8–10%, cần review sớm.
- Driver cần theo dõi: `return_2q_ago` = -0.0296, hướng `weak_or_negative`.
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — REE: Thông báo giao dịch cổ phiếu của tổ chức có liên quan đến người nội bộ PLATINUM VICTORY PTE.LTD (2026-03-31).
- News/event cần kiểm tra thủ công: `dividend,earnings,debt_risk,capital,legal_risk,governance,market` — REE: Báo cáo kết quả giao dịch cổ phiếu của tổ chức có liên quan đến người nội bộ PLATINUM VICTORY PTE.LTD (2026-03-31).
- Ticker matching confidence ở mức mixed; cần kiểm tra thủ công các tin dùng cho thesis định tính.

### 5. Trigger theo dõi

- `pred_proba_up < 0.55` hoặc giảm hơn 0.15 so với lúc decision.
- Rank rơi khỏi Top-K hoặc `pred_label` chuyển sang 0.
- MACD histogram chuyển âm, `price_vs_sma20 < 0`, hoặc RSI suy yếu mạnh.
- Drawdown vượt 8–10% từ decision price.
- Xuất hiện tin mới thuộc nhóm rủi ro hoặc trái với thesis.

### 6. Disclaimer

Card này phục vụ nghiên cứu và hỗ trợ phân tích, không phải khuyến nghị đầu tư.
