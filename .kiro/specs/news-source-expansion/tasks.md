# Plan: Mở rộng nguồn tin tức để tăng mật độ dữ liệu và sức mạnh thống kê

## Bối cảnh & mục tiêu

Hiện corpus tin tức mất cân đối nghiêm trọng: CafeF 83%, TNCK 12%, Vietstock chỉ 5%
(~534 bài). Kiểm định McNemar ở đơn vị tháng chưa đạt ý nghĩa thống kê (p=0.121) vì
số ca bất đồng quá ít — gốc rễ là mật độ tin mỏng ở nhiều (mã, kỳ).

**Mục tiêu:** tăng mật độ và độ đa dạng tin tức để (1) làm dày các (mã, kỳ) đang thưa,
(2) tăng số mẫu hữu ích, (3) tăng sức mạnh kiểm định H1.

**Ràng buộc:**
- Không phá vỡ pipeline hiện có; tái dùng hạ tầng `fetch_with_retry`, `RateLimiter`,
  dedup theo URL + fuzzy-title, `safe_write_csv`.
- TASK 3 (entity matching) tự gắn mã theo tên công ty → nguồn mới không cần gán mã thủ công.
- Commit sau mỗi phần để có điểm roll back.
- Chạy scraping ở chế độ nền, lịch sự với server (rate-limit riêng từng domain).

## Tasks

- [ ] 1. Khảo sát khả thi các nguồn (trước khi viết code)
  - [x] 1.1 Dò endpoint Vietstock lấy tin sâu hơn (API JSON hoặc phân trang) thay cho ~20 bài hiện tại
  - [x] 1.2 Khảo sát cấu trúc VnEconomy (vneconomy.vn) — trang tìm kiếm/chuyên mục chứng khoán
  - [x] 1.3 Khảo sát cấu trúc VietnamBiz (vietnambiz.vn) — trang theo mã/tìm kiếm
  - [x] 1.4 Ghi lại nguồn nào khả thi, nguồn nào bỏ; cập nhật plan theo thực tế

### Kết quả khảo sát (đo thực tế)

| Nguồn | Khả thi | Ghi chú |
|---|---|---|
| **VietnamBiz** | ✅ Cao | Chuyên mục `chung-khoan.htm` server-render, `li.item` (~24/trang); phân trang `/chung-khoan/trang-N.htm` chạy sâu (trang 2/10/30 khác nhau); trang chi tiết có `meta[property=article:published_time]` (ISO). **Làm trước.** |
| **VnEconomy** | ⚠️ Trung bình | Chuyên mục server-render (~75 link) nhưng `?trang=2` trả lại trang 1 → cần tìm cơ chế phân trang khác. |
| **Vietstock (đào sâu)** | ❌ Thấp | Chỉ trang "tin mới nhất" ~20-42 bài, nặng JS, không có API phân trang công khai. **Bỏ.** |

**Điều chỉnh plan:** bỏ Task 2 (Vietstock); nguồn #1 = VietnamBiz; nguồn #2 = VnEconomy (nếu giải được phân trang).

- [ ] ~~2. Cải thiện Vietstock~~ — **BỎ** (bất khả thi, xem khảo sát 1.1)

- [x] 3. Thêm nguồn mới #1 — VietnamBiz (chuyên mục chứng khoán + phân trang, TASK 3 lọc về VN30)
  - [x] 3.1 Viết `scrape_vietnambiz()` tái dùng hạ tầng chung; duyệt chuyên mục + phân trang tới khi vượt start_date; trích date từ meta bài chi tiết
  - [x] 3.2 Nối vào TASK 2 và lưu `data/news/vietnambiz/vietnambiz_raw.csv`
  - [x] 3.3 Test vài trang, kiểm tra parse đúng (title/date/url/description) — 129 bài/cửa sổ ~2 tuần, date đầy đủ
  - [x] 3.4 Viết unit test cơ bản (parse fixture, dedup) — 139 test pass
  - [x] 3.5 Commit
  - **Ghi chú:** phát hiện & sửa lỗi Brotli — VietnamBiz nén `br`, requests không giải mã được nếu thiếu gói `brotli` → dùng header chỉ `gzip, deflate` cho domain này.

- [x] 4. Thêm nguồn mới #2 — VnEconomy (nếu giải được phân trang)
  - [x] 4.1 Tìm cơ chế phân trang VnEconomy; nếu không có → ghi nhận và bỏ qua
  - [ ] ~~4.2 Viết `scrape_vneconomy()`~~ — **BỎ**
  - [ ] ~~4.3 Commit~~
  - **Kết luận: BỎ VnEconomy.** Mọi biến thể phân trang (`/trang-2.htm`, `?page=2`, `?trang=2`, `-p2.htm`) đều trả về cùng nội dung trang 1 (overlap >70%) → không có phân trang server-side; nội dung sâu nạp bằng JS. Trang chi tiết cũng thiếu `meta article:published_time` → khó trích ngày. Chi phí dò endpoint ẩn cao, khả năng thành công thấp. Dừng lại ở 1 nguồn mới (VietnamBiz).

- [ ] 5. Cập nhật entity matching nếu cần
  - [ ] 5.1 Kiểm tra alias trong `config/entity_aliases.json` có đủ bắt tin từ nguồn mới không
  - [ ] 5.2 Bổ sung alias còn thiếu nếu phát hiện UNKNOWN rate cao
  - [ ] 5.3 Commit

- [ ] 6. Chạy lại pipeline đầy đủ với nguồn mở rộng
  - [ ] 6.1 Scrape tin tất cả nguồn cho 30 mã (chạy nền, UTF-8)
  - [ ] 6.2 Chạy entity matching + preprocess + aggregate
  - [ ] 6.3 So sánh corpus trước/sau: tổng bài, phân bố nguồn, coverage heatmap, số (mã, kỳ) có news_count>=5

- [ ] 7. Đánh giá lại tác động lên H1
  - [ ] 7.1 Chạy lại features + train (đơn vị quý) và experiment_period (tháng)
  - [ ] 7.2 Chạy lại McNemar ở đơn vị tháng, so sánh p-value và số ca bất đồng trước/sau
  - [ ] 7.3 Cập nhật `reports/H1_experiment_report.md` với kết quả nguồn mở rộng
  - [ ] 7.4 Commit cuối

## Lưu ý rủi ro

- Scraping phụ thuộc cấu trúc web thật; một số nguồn có thể không khả thi (chặn bot,
  nặng JavaScript, không có API). Nếu một nguồn bất khả thi, ghi rõ lý do và chuyển nguồn khác.
- Mục tiêu là **chất lượng + mật độ**, không nhân bản tin trùng. Đo lại tỷ lệ trùng sau khi thêm.
- Nếu sau khi mở rộng mà H1 vẫn không significant, đó vẫn là kết luận nghiên cứu hợp lệ.
