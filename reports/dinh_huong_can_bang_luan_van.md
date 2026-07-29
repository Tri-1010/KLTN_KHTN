# Định hướng cân bằng lại luận văn: ML kỹ thuật (trọng tâm) + Văn bản (khám phá)

> Tài liệu tư vấn chiến lược về cấu trúc luận văn, dựa trên kết quả thực nghiệm thực tế.
> Trả lời câu hỏi: luận văn đã đủ chưa, và có nên nhấn mạnh phần ML kỹ thuật lên không.

---

## 1. Hiện trạng hai phần của luận văn

**Phần 1 — ML với đặc trưng kỹ thuật (dự báo xu hướng giá).**
Kết quả **dương và vững**:

| Mô hình (Config A) | Balanced Accuracy | AUC |
|---|---|---|
| LightGBM | 0.760 | 0.824 |
| Random Forest | 0.735 | 0.810 |
| XGBoost | 0.730 | 0.807 |
| Logistic Regression | 0.727 | 0.779 |
| Baseline đa số lớp | 0.500 | 0.500 |
| Baseline momentum | 0.486 | 0.486 |

Dữ liệu: 80 mã HOSE, 1.348 mẫu, test 400 mẫu cân bằng. Kết quả vượt xa baseline → phần này
là **đóng góp chắc chắn, đủ chất lượng**.

**Phần 2 — Đặc trưng văn bản (từ khóa + ML).**
Kết quả **âm, được kiểm chứng cực kỳ nghiêm ngặt**: Config B (chỉ từ khóa) ~0.47–0.55
(gần ngẫu nhiên); Config C (kết hợp) không cải thiện Config A. Đã kiểm qua 5 lần mở rộng
corpus (9.7k→28k bài, 6 nguồn), nhiều đơn vị thời gian, xử lý phủ định, LLM, distant
supervision, phân khúc. Kết luận H1/H2 không được ủng hộ; H3 ủng hộ một phần.

## 2. Đánh giá: đã đủ chưa?

**Về mặt học thuật: ĐỦ để bảo vệ.** Bạn có một phần dương vững + một phần âm được kiểm
chứng chặt. Đây là cấu trúc luận văn tốt, trung thực, và khó phản biện về mặt phương pháp.

**Về mặt "đóng góp mới": cần củng cố nếu muốn phần ML làm trọng tâm.** Dự báo xu hướng giá
bằng ML trên đặc trưng kỹ thuật là chủ đề phổ biến. Balanced accuracy 0.76 là tốt nhưng
bản thân nó chưa đủ khác biệt. Có hai khoảng trống cần lấp:

1. **Khoảng trống ứng dụng đầu tư:** Đề tài nêu mục tiêu "tăng đầu tư", nhưng hiện mới đo
   *accuracy dự báo*, chưa đo *lợi nhuận thực tế*. Một mô hình accuracy cao chưa chắc sinh
   lời sau phí giao dịch.
2. **Khoảng trống phân tích chiều sâu:** Chưa có phân tích ổn định theo thời gian, theo
   ngành, hay diễn giải mô hình (feature importance) riêng cho phần kỹ thuật.

## 3. Khuyến nghị: NÊN nhấn mạnh phần ML kỹ thuật — theo cách này

### 3.1 Tái cấu trúc tường thuật (narrative)

Đặt lại trọng tâm luận văn theo hai trụ:

- **Trụ chính (đóng góp dương):** "Xây dựng và đánh giá hệ thống ML dự báo xu hướng giá
  HOSE-80 dựa trên đặc trưng kỹ thuật, hướng tới hỗ trợ quyết định đầu tư."
- **Trụ phụ (đóng góp khám phá):** "Kiểm định nghiêm ngặt liệu đặc trưng tin tức tiếng Việt
  có bổ sung giá trị dự báo — kết quả âm được xác thực đa chiều."

Cách này giữ toàn bộ công sức phần văn bản (không lãng phí) nhưng đưa phần dương lên làm
điểm tựa, giảm rủi ro "luận văn toàn kết quả âm".

### 3.2 Việc nên bổ sung để phần ML đủ "nặng" (xếp theo ưu tiên)

**Ưu tiên 1 — Backtest chiến lược đầu tư (quan trọng nhất, khớp mục tiêu "tăng đầu tư").**
✅ **ĐÃ HOÀN THÀNH.** Lợi nhuận tích lũy mô hình 60.3% vs buy-and-hold 25.4%, Sharpe 1.05.

**Ưu tiên 2 — Phân tích độ ổn định theo thời gian.**
✅ **ĐÃ HOÀN THÀNH.** Walk-forward qua 3 cutoff: mô hình vượt buy-and-hold ở 3/3.

**Ưu tiên 3 — Diễn giải mô hình kỹ thuật.**
✅ **ĐÃ HOÀN THÀNH.** SHAP + permutation importance: RSI cuối quý là đặc trưng quan trọng nhất.

**Ưu tiên 4 — Kiểm tra tính vững trên tập mã mở rộng (Robustness Test).**
✅ **ĐÃ HOÀN THÀNH.** Mở rộng lên 125 mã HOSE+HNX: BA 0.761 (gần như không đổi so với 80
mã gốc), AUC 0.831. Chiến lược vượt VNINDEX 15.3%. Xác nhận mô hình tổng quát hóa tốt.

### 3.3 Điều CẦN kiểm tra trước khi nhấn mạnh (tránh rủi ro)

- **Xác minh không rò rỉ dữ liệu trong đặc trưng kỹ thuật.** Balanced accuracy 0.76 khá cao
  cho dự báo giá; cần chắc chắn các chỉ báo kỹ thuật (return, volatility…) của kỳ q không vô
  tình dùng thông tin kỳ q+1. Nhãn là "giá trung bình kỳ kế tiếp tăng/giảm" — cần đảm bảo
  đặc trưng chỉ tính từ dữ liệu ≤ q. (Pipeline đã tuyên bố time-split đúng, nhưng đây là câu
  hội đồng chắc chắn hỏi khi thấy accuracy cao.)
- **Định nghĩa nhãn rõ ràng.** "Tăng/không tăng" dựa trên ngưỡng nào; nhãn cân bằng 53/47 là
  hợp lý, nên nêu rõ.

## 4. Rủi ro của việc KHÔNG nhấn mạnh phần ML

Nếu để luận văn nghiêng hẳn về phần văn bản (kết quả âm), rủi ro:
- Hội đồng có thể hỏi "vậy đóng góp dương của luận văn là gì?"
- Kết quả âm dù nghiêm ngặt vẫn khó gây ấn tượng bằng một hệ thống hoạt động được.

Nhấn mạnh phần ML kỹ thuật giải quyết cả hai: có đóng góp dương rõ ràng, phần âm trở thành
bổ trợ làm tăng độ tin cậy/trung thực.

## 5. Tóm tắt khuyến nghị

1. **Đủ để bảo vệ** — không cần đổi đề tài.
2. **Nên nhấn mạnh phần ML kỹ thuật** làm trọng tâm (đóng góp dương), giữ phần văn bản làm
   khám phá bổ trợ (đóng góp âm được kiểm chứng).
3. **Bổ sung backtest lợi nhuận đầu tư** — việc quan trọng nhất, khớp đúng mục tiêu đề tài
   và lấp khoảng trống lớn nhất.
4. **Xác minh chống rò rỉ dữ liệu** cho đặc trưng kỹ thuật trước khi trình bày accuracy cao.
5. Xác nhận định hướng cân bằng hai phần này với GVHD trước khi viết lại cấu trúc.

---

## Nguồn số liệu
- `reports/model_comparison.csv`, `reports/baseline_v0/model_comparison.csv`
- `reports/metrics_breakdown.csv`
- `reports/H1_experiment_report.md`, `reports/H2_H3_validation_report.md`
