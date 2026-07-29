# Dự thảo Chương 5 — Kết luận, Hạn chế & Hướng phát triển

> Văn bản học thuật soạn sẵn để đưa vào luận văn (Chương 5). Đã bám sát bằng chứng thực
> nghiệm từ các thí nghiệm A6, B1, B3 và baseline v0. Có thể chỉnh giọng văn/thuật ngữ
> cho khớp phần còn lại của luận văn.

---

## 5.1 Kết luận chung

Luận văn đặt ra câu hỏi nghiên cứu trung tâm: *liệu đặc trưng trích xuất từ tin tức tài
chính tiếng Việt có cải thiện khả năng dự báo xu hướng giá cổ phiếu HOSE-80 khi kết hợp
với đặc trưng kỹ thuật hay không, và nếu không thì vì sao.* Qua toàn bộ hệ thống thí
nghiệm, câu trả lời nhất quán là: ở độ chi tiết theo quý, đặc trưng văn bản **không mang
lại cải thiện dự báo** vượt trên đặc trưng kỹ thuật.

Ngược lại, bản thân mô hình dự báo xu hướng giá bằng đặc trưng kỹ thuật đạt kết quả khả
quan và có giá trị thực tiễn. Trên tập 80 mã HOSE gốc, mô hình tốt nhất (LightGBM) đạt
balanced accuracy 0.760 và AUC 0.824, với Sharpe ratio 1.05 và lợi nhuận vượt benchmark
buy-and-hold 34.9 điểm phần trăm. Để kiểm chứng tính vững, nghiên cứu đã mở rộng kiểm tra
trên **125 mã HOSE+HNX** (gấp 1.56 lần tập gốc, bao gồm cả sàn HNX), với kết quả gần như
không thay đổi (balanced accuracy 0.761, AUC 0.831) và chiến lược mô hình vượt VNINDEX 15.3
điểm phần trăm — xác nhận khả năng tổng quát hóa tốt và loại trừ nghi vấn overfit vào tập
mã ban đầu.

Kết luận này được rút ra không phải từ một phép đo đơn lẻ, mà từ nhiều lớp kiểm chứng độc
lập. Sau full-text enrichment gần đầy đủ (45.949/45.968 unique URLs có `full_text`, 99,96%),
chênh lệch balanced accuracy giữa cấu hình kết hợp (Config C) và cấu hình chỉ dùng đặc trưng
kỹ thuật (Config A), ký hiệu Δ(C−A), vẫn dao động quanh 0 và có dấu âm ở phần lớn granularity
đã kiểm tra (1 tuần, 2 tuần, 1 tháng, 2 tháng, quý). Đặc biệt, ở cấp 1 tuần với 2.764 mẫu
test (cỡ mẫu lớn nhất), Δ(C−A) = −0,0068 — gần bằng 0 nhưng theo chiều bất lợi cho Config_C.
Kiểm định McNemar giữa mô hình có đặc trưng văn bản và mô hình nền không cho thấy khác biệt
có ý nghĩa thống kê theo chiều cải thiện; trường hợp Random Forest 1 tháng còn cho Config_C
kém Config_A có ý nghĩa thống kê (p = 0,0227). Đồng thời, không một từ khóa nào trong bộ đặc
trưng đạt ý nghĩa thống kê sau hiệu chỉnh đa kiểm định Benjamini–Hochberg, cả ở cấp toàn thị
trường lẫn ở từng phân khúc.

Điểm mấu chốt là kết quả âm này **không phải là hệ quả của hạn chế phương pháp**, mà phản
ánh một đặc tính thực chất của thị trường. Hai hướng thí nghiệm được thiết kế riêng để
loại trừ các lời giải thích thay thế đã cho phép khẳng định điều đó.

## 5.2 Kết luận theo từng hướng thí nghiệm

**Hướng A — Củng cố kết quả âm qua nội dung văn bản đầy đủ và các biến thể biểu diễn.**
Giả thuyết đối lập tự nhiên nhất với kết quả âm là "đặc trưng văn bản không có giá trị vì
phương pháp biểu diễn hoặc dữ liệu văn bản quá nghèo". Để kiểm chứng, luận văn mở rộng nguồn
tin, bổ sung full-text enrichment gần đầy đủ, và thử các biến thể biểu diễn văn bản đã có
như nhận biết phủ định, LLM sentiment và distant supervision. Kết quả vẫn không tạo cải thiện
ổn định cho Config_C. Việc full text không đảo ngược kết luận là bằng chứng mạnh rằng kết quả
âm không phải do chỉ dùng tiêu đề/mô tả quá ngắn.

**Hướng B — Tìm tín hiệu có điều kiện.** Giả thuyết đối lập thứ hai là "tín hiệu văn bản
tồn tại nhưng bị pha loãng khi gộp toàn thị trường hoặc gộp theo quý". Phân tích theo phân
khúc ngành và nhóm vốn hóa (B3) không tìm thấy phân khúc nào có tín hiệu văn bản vững:
các chênh lệch dương quan sát được chỉ xuất hiện ở những phân khúc có cỡ mẫu test nhỏ nhất
(Transport với 25 mẫu, Technology với 15 mẫu), không nhất quán giữa các thuật toán, và
không kèm theo bất kỳ từ khóa nào đạt ý nghĩa thống kê; do đó chúng phù hợp với dao động
do phương sai lấy mẫu hơn là tín hiệu thực. Ngược lại, hai phân khúc có cỡ mẫu lớn nhất
(large-cap và mid-cap) đều cho Δ(C−A) âm, nhất quán với kết quả toàn cục. Thí nghiệm
distant supervision ở cấp bài viết (B1) cho thấy có tín hiệu yếu tồn tại ở cấp độ từng bài
(AUC ≈ 0,68), nhưng tín hiệu này tan biến khi tổng hợp theo quý — một chỉ dấu cho cơ chế
hấp thụ trong kỳ.

## 5.3 Diễn giải lý thuyết

Kết quả nhất quán với ba cơ chế lý thuyết bổ trợ lẫn nhau:

Thứ nhất, **giả thuyết thị trường hiệu quả dạng vừa (semi-strong EMH)**: nếu thông tin
công khai từ tin tức được phản ánh nhanh vào giá, thì đặc trưng trích từ tin tức khó bổ
sung thêm thông tin dự báo vượt trên đặc trưng kỹ thuật, vốn đã hàm chứa dấu vết phản ứng
giá. Δ(C−A) ≈ 0 là hệ quả trực tiếp có thể dự đoán được từ giả thuyết này.

Thứ hai, **cơ chế hấp thụ trong kỳ (within-period absorption)**: ở độ chi tiết theo quý,
phản ứng giá đối với một tin tức thường xảy ra và kết thúc ngay trong cùng kỳ, nên việc
tổng hợp đặc trưng theo quý làm mờ các tín hiệu ngắn hạn. Kết quả B1 (tín hiệu cấp bài
viết tồn tại nhưng biến mất sau khi gộp quý) là bằng chứng thực nghiệm cho cơ chế này.

Thứ ba, **giới hạn của cách biểu diễn tần suất từ khóa**: full-text enrichment đã làm yếu đi
phản biện "corpus quá ngắn", nhưng tần suất từ khóa vẫn không phân biệt đầy đủ ngữ cảnh,
cường độ, novelty và thời điểm tác động của sự kiện. Điều này làm tăng nhiễu ước lượng và
kéo Δ(C−A) về 0.

## 5.4 Đóng góp của luận văn

Luận văn có các đóng góp sau. Về mặt thực chứng, đây là một trong số ít nghiên cứu trên
thị trường chứng khoán Việt Nam kiểm định một cách hệ thống và nghiêm ngặt giá trị dự báo
của đặc trưng tin tức tiếng Việt, và cung cấp một kết quả âm được kiểm chứng chặt chẽ —
loại kết quả thường ít được công bố nhưng có giá trị định hướng cao cho các nghiên cứu sau.
Về mặt phương pháp, luận văn xây dựng một quy trình thí nghiệm có tính tái lập cao: chống
rò rỉ dữ liệu theo thời gian bằng ranh giới chia train/test cố định, so sánh công bằng qua
cùng một pipeline huấn luyện, kiểm định thống kê có hiệu chỉnh đa kiểm định, và kiểm thử
tính đúng đắn của các hàm xử lý đặc trưng bằng property-based testing. Về mặt ứng dụng,
mô hình dự báo xu hướng giá bằng đặc trưng kỹ thuật đạt balanced accuracy 0.76 và tạo ra
giá trị đầu tư thực (Sharpe ratio > 1, vượt VNINDEX 15.3%), đồng thời khả năng tổng quát
hóa đã được xác nhận qua robustness test trên 125 mã HOSE+HNX — gấp 1.56 lần tập gốc —
với kết quả gần như không đổi. Về mặt lý thuyết, luận văn liên hệ kết quả thực nghiệm với
ba cơ chế giải thích và loại trừ được hai lời giải thích thay thế phổ biến (đo lường yếu và
pha loãng tín hiệu), qua đó tăng độ vững cho kết luận.

## 5.5 Hạn chế của nghiên cứu

Nghiên cứu có một số hạn chế cần nêu rõ. *Thứ nhất, về độ chi tiết thời gian*: toàn bộ đặc
trưng và nhãn đã được thí nghiệm ở nhiều độ chi tiết từ 1 tuần đến quý; kết quả cho thấy
đặc trưng từ khóa không cải thiện dự báo ở bất kỳ granularity nào đã kiểm tra, kể cả khi
corpus đủ dày ở cấp tuần (trung bình 3.19 bài/mã/tuần, độ phủ 56.7%). Kết luận âm do đó
áp dụng cho mọi khung thời gian từ 1 tuần trở lên với phương pháp biểu diễn tần suất từ
khóa. *Thứ hai, về cỡ mẫu phân khúc*: một số phân
khúc ngành có số mẫu test rất nhỏ (15–30 mẫu), khiến các ước lượng Δ(C−A) trên các phân
khúc này có phương sai cao và không đủ statistical power để kết luận chắc chắn. *Thứ ba,
về corpus*: dữ liệu tin tức được thu thập từ một số nguồn giới hạn và độ phủ theo mã/kỳ
không đồng đều. *Thứ tư, về nhãn distant supervision*: nhãn cấp bài viết được suy ra từ
suất sinh lời ngắn hạn nên mang bản chất nhiễu; AUC ≈ 0,68 phản ánh chất lượng nhãn ở mức
trung bình. *Thứ năm, về phạm vi mô hình*: nghiên cứu giới hạn ở bốn thuật toán học máy
dạng bảng và chưa khảo sát các kiến trúc chuỗi thời gian hoặc mô hình đa phương thức.

## 5.6 Hướng phát triển

Từ các hạn chế trên, luận văn đề xuất các hướng nghiên cứu tiếp theo. *Hướng ưu tiên nhất*
là thay đổi cách biểu diễn văn bản: thay vì tần suất từ khóa, sử dụng embedding ngữ nghĩa
hoặc mô hình ngôn ngữ lớn để biểu diễn bài tin ở cấp sự kiện (event-driven), kết hợp với
khung thời gian ngắn (tuần/ngày). Nghiên cứu hiện tại đã chứng minh rằng tần suất từ khóa
không hiệu quả ở mọi granularity kể cả khi corpus đủ dày (3.19 bài/mã/tuần), nên hướng đi
tiếp phải là **đổi phương pháp biểu diễn** chứ không chỉ đổi granularity. *Hướng thứ hai* là mở
rộng và làm giàu corpus tin tức (thêm nguồn, thêm giai đoạn, chuẩn hóa độ phủ) để giảm
nhiễu ước lượng. *Hướng thứ ba* là thử nghiệm các phương pháp biểu diễn và mô hình hiện đại
hơn như event study kết hợp học máy, mô hình chuỗi thời gian có yếu tố văn bản, hoặc mô
hình đa phương thức kết hợp giá và văn bản ở cấp sự kiện. *Hướng thứ tư* là cải thiện chất
lượng nhãn cấp bài viết bằng gán nhãn thủ công một tập con để hiệu chỉnh nhãn nhiễu. Các
hướng này đều nhắm tới việc kiểm chứng xem kết luận âm ở độ chi tiết quý có được bảo toàn
khi thay đổi độ chi tiết và phương pháp hay không.

---

## Ghi chú sử dụng

- Các con số nêu trong dự thảo (p-value McNemar, AUC, cỡ mẫu test) đã được lấy từ kết quả
  thực nghiệm; nên đối chiếu lần cuối với bảng số liệu trong Chương 4 trước khi nộp.
- Nếu hội đồng/GVHD yêu cầu, có thể bổ sung một bảng tóm tắt Δ(C−A) toàn cục và theo phân
  khúc ngay trong Chương 5 để tăng tính trực quan.
- Nguồn số liệu: `reports/experiment_A6_report.md`, `experiment_B1_report.md`,
  `experiment_B3_report.md`, `distant_supervision_report.md`, `segment_test_sizes.csv`.
