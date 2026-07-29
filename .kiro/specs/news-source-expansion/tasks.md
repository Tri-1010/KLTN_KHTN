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

- [ ] ~~2. Cải thiện Vietstock~~ — **HOÀN THÀNH (đào sâu lần 2)**
  - Lần khảo sát đầu kết luận "bất khả thi", nhưng đào sâu hơn đã tìm được endpoint phân trang nội bộ
    `/View/PagingNewsContent` (phát hiện từ JS của trang tin-moi-nhat). Endpoint trả fragment HTML nhẹ
    ~20 bài/trang, phân trang lùi nhiều năm về quá khứ.
  - Kết quả: Vietstock **534 → 5.008 bài** (gấp ~9 lần). CafeF từ 83% → 45% tổng corpus.
  - Đã viết `_scrape_vietstock_paging` + parser + 5 unit test; cập nhật `scrape_vietstock` dùng nó
    làm chiến lược chính (giữ latest-news + tag-search làm fallback).

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
- [x] 5. Cập nhật entity matching nếu cần
  - [x] 5.1 Kiểm tra alias trong `config/entity_aliases.json` có đủ bắt tin từ nguồn mới không — đủ; toàn bộ 3.598 bài VietnamBiz match được vào VN30
  - [x] 5.2 Bổ sung alias còn thiếu — không cần (đã đăng ký vietnambiz trong NEWS_SOURCES + _load_all_news của TASK 3)
  - [x] 5.3 Commit

- [x] 6. Chạy lại pipeline đầy đủ với nguồn mở rộng
  - [x] 6.1 Scrape tin VietnamBiz (3.598 bài, 2024-08 → 2026; trang web giới hạn phân trang sâu nên không về tới 2022)
  - [x] 6.2 Chạy entity matching + preprocess + aggregate
  - [x] 6.3 So sánh corpus: matched unique 9.715 → 13.313 (+37%); processed 7.492 → 11.087 (+48%)

- [x] 7. Đánh giá lại tác động lên H1
  - [x] 7.1 Chạy lại features + train + experiment_period
  - [x] 7.2 Chạy lại McNemar — số ca bất đồng 34 → 45, delta về −0.003, p-value = 1.000
  - [x] 7.3 Cập nhật `reports/H1_experiment_report.md` (thêm mục 5c)
  - [x] 7.4 Commit cuối

## Kết luận cuối của plan

Đã mở rộng từ 3 → **6 nguồn**: VietnamBiz (3.598), Vietstock deep (5.008), VnExpress (1.762),
Kinh Tế Chứng Khoán qua sitemap (8.513). Corpus unique **9.7k → 28k bài (gần gấp 3)**, CafeF từ
83% → **29%** (không nguồn nào quá 30%). Bất chấp dữ liệu gấp 3 và 6 nguồn cân bằng, đặc trưng từ
khóa **vẫn không cải thiện** dự báo (mọi delta quanh 0/âm, mọi McNemar không significant, p=0.12–1.0).
Kết luận **H1 không được ủng hộ** đã được kiểm chứng triệt để và khách quan.

Nguồn đã thêm (khả thi): VietnamBiz, Vietstock (deep paging), VnExpress, Kinh Tế Chứng Khoán (sitemap).
Nguồn đã loại (bất khả thi): VnEconomy, VietnamFinance, Stockbiz, 24hmoney, nguoiquansat
(phân trang JS / API ẩn / 404 / quá ít bài).
Kỹ thuật khám phá: API ẩn (Vietstock PagingNewsContent), sitemap theo ngày (KTCK), date từ URL ảnh
(VnExpress), date từ id bài (VietnamBiz), header Brotli fix.

## Full-text enrichment follow-up

- [x] TASK 2B full-text enrichment đã chạy trên corpus 6 nguồn sau matching.
- [x] Coverage sau repair: **45,949/45,968 unique URLs** có `full_text` (**99.96%**) theo `reports/decision_support/generated/ktck_missing_metadata_repair_summary.json`.
- [x] Các nguồn gần như đủ full text: CafeF 100%, Kinh Tế Chứng Khoán 100%, TNCK 100%, VietnamBiz 100%, Vietstock 99.84%, VnExpress 99.94%.
- [x] Downstream đã cập nhật: TASK 4 dùng `full_text/lead/article_summary/key_facts_json`; TASK 5-11 và báo cáo H1 đã rerun/cập nhật theo full-text corpus.

## Lưu ý rủi ro

- Scraping phụ thuộc cấu trúc web thật; một số nguồn có thể không khả thi (chặn bot,
  nặng JavaScript, không có API). Nếu một nguồn bất khả thi, ghi rõ lý do và chuyển nguồn khác.
- Mục tiêu là **chất lượng + mật độ**, không nhân bản tin trùng. Đo lại tỷ lệ trùng sau khi thêm.
- Nếu sau khi mở rộng mà H1 vẫn không significant, đó vẫn là kết luận nghiên cứu hợp lệ.
