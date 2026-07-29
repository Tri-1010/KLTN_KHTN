# PROMPT CHI TIẾT TỪNG TASK THỰC HIỆN LUẬN VĂN

## Tổng quan pipeline

```
TASK 1: Thu thập dữ liệu giá cổ phiếu VN30
    ↓
TASK 2: Scrape metadata tin tức từ CafeF, Vietstock, TNCK và các nguồn mở rộng
    ↓
TASK 3: Gắn tin tức với mã cổ phiếu (entity matching)
    ↓
TASK 2B: Làm giàu bài báo bằng toàn văn, summary, key facts
    ↓
TASK 4: Tiền xử lý văn bản tiếng Việt từ full text đã enrich
    ↓
TASK 5: Tổng hợp dữ liệu theo cổ phiếu - quý
    ↓
TASK 6: Xây dựng nhãn tăng/giảm
    ↓
TASK 7: Trích xuất đặc trưng kỹ thuật
    ↓
TASK 8: Xây dựng danh sách từ khóa tài chính
    ↓
TASK 9: Trích xuất đặc trưng tần suất từ khóa
    ↓
TASK 10: Huấn luyện và đánh giá mô hình
    ↓
TASK 11: Phân tích SHAP / Feature Importance
    ↓
TASK 12: Đóng gói pipeline bán tự động
```

---

## TASK 1 — Thu thập dữ liệu giá cổ phiếu VN30

```
Bạn là một kỹ sư dữ liệu tài chính. Hãy viết script Python hoàn chỉnh để thu thập
dữ liệu giá cổ phiếu cho toàn bộ 30 mã thuộc chỉ số VN30 trên sàn HOSE.

Yêu cầu:
- Sử dụng thư viện vnstock (phiên bản mới nhất) để lấy dữ liệu OHLCV theo ngày
- Danh sách 30 mã VN30 hiện tại: ACB, BCM, BID, BVH, CTG, FPT, GAS, GVR, HDB,
  HPG, MBB, MSN, MWG, PLX, POW, SAB, SHB, SSB, SSI, STB, TCB, TPB, VCB, VHM,
  VIB, VIC, VJC, VNM, VPB, VRE
- Khoảng thời gian: từ 01/01/2022 đến ngày hiện tại
- Dữ liệu cần lấy: date, open, high, low, close, volume cho mỗi mã
- Xử lý lỗi: nếu một mã lấy thất bại thì ghi log và tiếp tục các mã còn lại
- Lưu kết quả: một file CSV cho mỗi mã (ví dụ: data/prices/ACB.csv),
  đồng thời lưu một file tổng hợp data/prices/all_vn30_prices.csv với cột 'ticker'
- In ra tóm tắt: số ngày dữ liệu mỗi mã, ngày đầu và ngày cuối có dữ liệu
- Kiểm tra: phát hiện và báo cáo các mã có dữ liệu thiếu quá 5% số ngày giao dịch

Môi trường: Python 3.10+, thư viện vnstock đã được cài đặt.
Hãy thêm docstring và comment rõ ràng cho từng bước.
```

---

## TASK 2 — Scrape tin tức tài chính

### TASK 2A — Scrape CafeF

```
Bạn là một kỹ sư thu thập dữ liệu web. Hãy viết script Python để scrape tin tức
tài chính từ CafeF (cafef.vn) cho 30 mã cổ phiếu VN30.

Yêu cầu:
- CafeF có trang riêng cho từng mã theo pattern: https://cafef.vn/thi-truong-chung-khoan/{ticker}-ctck.chn
  Ví dụ: https://cafef.vn/thi-truong-chung-khoan/ACB-ctck.chn
- Thu thập tất cả bài viết từ 01/01/2022 đến nay
- Với mỗi bài viết cần lấy: tiêu đề, mô tả ngắn (nếu có), ngày đăng, URL bài viết, mã cổ phiếu
- Bước scrape metadata chỉ bắt buộc lấy tiêu đề + mô tả + ngày + URL; toàn văn được lấy sau TASK 3 bằng TASK 2B full-text enrichment để tránh fetch các bài không liên quan
- Xử lý phân trang: tự động lấy hết các trang kết quả
- Rate limiting: sleep 1-2 giây giữa các request để tránh bị chặn
- Lưu kết quả: data/news/cafef/{ticker}_cafef.csv
- Kiểm tra trùng lặp: loại bỏ bài viết có URL giống nhau
- Xử lý lỗi kết nối: retry tối đa 3 lần với exponential backoff
- In báo cáo: số bài thu thập được mỗi mã, khoảng thời gian bao phủ

Lưu ý quan trọng:
- Sử dụng headers giả lập browser (User-Agent) để tránh bị block
- Nếu cấu trúc HTML thay đổi ở trang nào đó, ghi log URL đó và bỏ qua thay vì crash

Môi trường: Python 3.10+, requests, BeautifulSoup4 đã cài đặt.
```

### TASK 2.2 — Scrape Vietstock

```
Bạn là một kỹ sư thu thập dữ liệu web. Hãy viết script Python để scrape tin tức
từ Vietstock (vietstock.vn) cho các mã cổ phiếu VN30.

Yêu cầu:
- Trang tìm kiếm tin tức theo mã: https://vietstock.vn/{ticker} hoặc tìm qua search
- Thu thập từ 01/01/2022 đến nay
- Với mỗi bài viết: tiêu đề, mô tả ngắn, ngày đăng, URL, mã cổ phiếu liên quan
- Lưu: data/news/vietstock/{ticker}_vietstock.csv
- Áp dụng rate limiting: sleep 1.5 giây giữa các request
- Xử lý lỗi và retry như TASK 2A
- Ghi rõ trong comment những chỗ có thể cần điều chỉnh nếu cấu trúc trang thay đổi

Lưu ý: nếu Vietstock yêu cầu login để xem đầy đủ nội dung, chỉ lấy phần
tiêu đề và tóm tắt hiển thị công khai. Ghi chú vào log nếu có bài bị chặn.

Môi trường: Python 3.10+, requests, BeautifulSoup4.
```

### TASK 2.3 — Scrape Tinnhanhchungkhoan

```
Bạn là một kỹ sư thu thập dữ liệu web. Hãy viết script Python để scrape tin tức
từ Tinnhanhchungkhoan (tinnhanhchungkhoan.vn) cho các mã VN30.

Yêu cầu:
- Tìm kiếm tin tức theo tên công ty hoặc mã cổ phiếu qua thanh tìm kiếm hoặc chuyên mục
- Thu thập từ 01/01/2022 đến nay
- Với mỗi bài: tiêu đề, mô tả, ngày đăng, URL
- Lưu: data/news/tnck/tnck_raw.csv (không phân theo mã vì cần entity matching ở bước sau)
- Rate limiting và xử lý lỗi tương tự TASK 2A/2B
- Tổng hợp và lưu thêm báo cáo: số bài theo tháng để kiểm tra độ phủ

Môi trường: Python 3.10+, requests, BeautifulSoup4.
```

---

## TASK 2B — Làm giàu bài báo bằng toàn văn (Full-text Enrichment)

```
Bạn là một kỹ sư dữ liệu/NLP. Hãy viết module Python để lấy toàn văn bài báo sau khi đã gắn mã cổ phiếu.

Đầu vào:
- data/news/matched/all_news_matched.csv

Yêu cầu:
1. Với mỗi URL bài báo đã match, fetch trang chi tiết và trích xuất:
   - full_text: toàn văn bài báo nếu có
   - lead: đoạn sapo/og:description nếu có
   - author, published_at_detail, canonical_url
   - extraction_status: ok/partial/failed/fetch_failed/restricted
   - full_text_available, full_text_chars, content_hash

2. Tạo bằng chứng rút gọn cho downstream:
   - article_summary: tóm tắt rule-based ngắn từ description/full_text
   - key_facts_json: danh sách fact có evidence_quote, fact_type, direction, confidence
   - event_type_enriched, risk_flags_json, relevance_hint

3. Tối ưu vận hành:
   - Fetch một lần theo URL nhưng bảo toàn nhiều dòng ticker nếu một bài match nhiều mã
   - Cache kết quả cũ theo URL; chỉ retry failed/partial/restricted khi cấu hình yêu cầu
   - Rate-limit theo domain, dùng retry/backoff, checkpoint định kỳ
   - Không nhúng toàn bộ full_text vào prompt LLM mặc định; dùng summary/key facts/hash để audit

4. Đầu ra:
   - data/news/enriched/all_news_enriched.csv

5. TASK 4 phải ưu tiên đọc file enriched này nếu tồn tại; nếu không có thì fallback về data/news/matched/all_news_matched.csv.

Môi trường: Python 3.10+, requests, BeautifulSoup4, pandas.
```

---

## TASK 3 — Gắn tin tức với mã cổ phiếu (Entity Matching)

```
Bạn là một kỹ sư xử lý dữ liệu. Hãy viết script Python để gắn mỗi bài tin tức
với một hoặc nhiều mã cổ phiếu VN30 tương ứng.

Đầu vào:
- data/news/cafef/: các file CSV từ TASK 2A (đã có cột ticker, nhưng cần xác nhận lại)
- data/news/vietstock/: các file CSV từ TASK 2.2
- data/news/tnck/tnck_raw.csv: file từ TASK 2.3 (chưa có ticker)

Yêu cầu:
1. Xây dựng dictionary mapping mã → danh sách tên nhận diện:
   Ví dụ:
   "VNM": ["Vinamilk", "VNM", "Công ty Cổ phần Sữa Việt Nam", "Vietnam Dairy"],
   "VCB": ["Vietcombank", "VCB", "Ngân hàng Ngoại thương"],
   "VIC": ["Vingroup", "VIC", "Tập đoàn Vingroup"],
   "VHM": ["Vinhomes", "VHM"],
   "VRE": ["Vincom Retail", "VRE"],
   ... (liệt kê đầy đủ 30 mã VN30)

   LƯU Ý QUAN TRỌNG cho nhóm Vin*:
   - VIC (Vingroup) vs VHM (Vinhomes) vs VRE (Vincom Retail) rất dễ nhầm
   - Quy tắc ưu tiên: nếu tiêu đề có "Vinhomes" → VHM (không gắn VIC)
   - Nếu có "Vincom Retail" hoặc "trung tâm thương mại Vincom" → VRE
   - Chỉ gắn VIC khi có từ "Vingroup" hoặc "tập đoàn Vingroup" rõ ràng

2. Matching logic:
   - Tìm kiếm case-insensitive trong cột tiêu đề + mô tả
   - Một bài có thể được gắn với nhiều mã (ví dụ bài so sánh ngân hàng)
   - Nếu không match được mã nào → gán ticker = "UNKNOWN", ghi vào log riêng
   - Nếu match nhiều mã → tạo nhiều dòng (một dòng per ticker)

3. Đầu ra: data/news/matched/all_news_matched.csv với các cột:
   date, title, description, url, source, ticker, match_confidence (exact/partial)

4. Báo cáo sau matching:
   - Tổng số bài trước và sau matching
   - Tỷ lệ UNKNOWN
   - Số bài per mã per nguồn
   - Cảnh báo nếu mã nào có < 20 bài/năm (có thể thiếu dữ liệu nghiêm trọng)

Môi trường: Python 3.10+, pandas, re.
```

---

## TASK 4 — Tiền xử lý văn bản tiếng Việt

```
Bạn là một kỹ sư NLP. Hãy viết module Python để tiền xử lý văn bản tiếng Việt
cho dữ liệu tin tức tài chính.

Đầu vào: ưu tiên data/news/enriched/all_news_enriched.csv; fallback data/news/matched/all_news_matched.csv nếu chưa enrich

Yêu cầu:

1. Làm sạch văn bản (hàm clean_text):
   - Chuyển về chữ thường
   - Loại bỏ HTML tags, ký tự đặc biệt, URL
   - Chuẩn hóa dấu câu tiếng Việt
   - Giữ lại số (vì "tăng 20%", "lợi nhuận 500 tỷ" có ý nghĩa tài chính)
   - Kết hợp tiêu đề + full_text/lead/article_summary/key_facts_json thành một trường text duy nhất; fallback về mô tả nếu chưa có full text

2. Tách từ (hàm tokenize_vi):
   - Sử dụng underthesea: word_tokenize(text, format="text")
   - Xử lý batch để tăng tốc (dùng multiprocessing nếu > 10.000 bài)

3. Loại từ dừng (hàm remove_stopwords):
   - Load danh sách từ dừng tiếng Việt cơ bản
   - BỔ SUNG từ dừng tài chính tùy chỉnh (những từ xuất hiện nhiều nhưng
     không có giá trị phân biệt):
     ["công ty", "doanh nghiệp", "cho biết", "theo đó", "được biết",
      "chia sẻ", "theo ông", "theo bà", "tại đây", "trong đó",
      "hiện nay", "thời gian", "năm nay", "năm ngoái", "quý này",
      "tháng này", "ngày hôm nay", "vừa qua", "mới đây",
      "theo thông tin", "được biết thêm", "cụ thể", "đáng chú ý"]
   - Lưu danh sách từ dừng đầy đủ ra file config/stopwords_finance.txt
     để dễ chỉnh sửa sau

4. Phát hiện bài trùng lặp (hàm deduplicate):
   - Bài có URL giống nhau → loại bỏ
   - Bài có tiêu đề giống nhau > 90% (fuzzy matching) → giữ lại bản sớm nhất

5. Đầu ra: data/news/processed/all_news_processed.csv
   Thêm cột: text_clean (text đã làm sạch), text_tokenized (đã tách từ)

6. Báo cáo:
   - Số bài trước và sau dedup
   - Độ dài trung bình (số từ) per bài
   - Top 50 từ phổ biến nhất sau khi loại từ dừng (để kiểm tra chất lượng)
   - Cảnh báo nếu bài nào có < 5 từ sau xử lý

Môi trường: Python 3.10+, underthesea, pandas, fuzzywuzzy hoặc rapidfuzz.
```

---

## TASK 5 — Tổng hợp dữ liệu theo cổ phiếu - quý

```
Bạn là một kỹ sư dữ liệu. Hãy viết script Python để tổng hợp dữ liệu tin tức
và giá cổ phiếu theo đơn vị (ticker, quarter).

Đầu vào:
- data/prices/all_vn30_prices.csv
- data/news/processed/all_news_processed.csv

Yêu cầu:

1. Định nghĩa quý:
   - Q1: tháng 1-3, Q2: tháng 4-6, Q3: tháng 7-9, Q4: tháng 10-12
   - Thêm cột quarter_id dạng "2022Q1", "2022Q2", ... vào cả hai dataset

2. Tổng hợp tin tức theo (ticker, quarter_id):
   - Đếm số bài: news_count
   - Ghép nối toàn bộ text_tokenized thành một văn bản duy nhất: combined_text
   - Lưu: data/aggregated/news_by_quarter.csv

3. Tổng hợp giá theo (ticker, quarter_id):
   - avg_close: trung bình giá đóng cửa trong quý
   - avg_volume: trung bình khối lượng giao dịch trong quý
   - return_intra: lợi suất nội quý = (close_last - close_first) / close_first
   - trading_days: số ngày giao dịch thực tế trong quý
   - Lưu: data/aggregated/prices_by_quarter.csv

4. Tạo bảng master: merge tin tức và giá theo (ticker, quarter_id)
   - Chỉ giữ các cặp có đủ cả dữ liệu giá lẫn tin tức
   - Thêm cột next_quarter_id: quý liền sau (để build nhãn ở TASK 6)
   - Merge thêm avg_close của quý kế tiếp (next_avg_close) vào cùng dòng
   - Lưu: data/aggregated/master_dataset.csv

5. Kiểm tra chất lượng:
   - Báo cáo số cặp (ticker, quarter) theo từng năm
   - Cảnh báo các cặp có news_count < 5 (có thể thiếu đặc trưng từ khóa)
   - Cảnh báo nếu tổng số mẫu < 300 (không đủ để train ML)
   - Vẽ heatmap: ticker (rows) × quarter (cols) với màu = news_count
     để trực quan hóa độ phủ tin tức, lưu vào reports/coverage_heatmap.png

Môi trường: Python 3.10+, pandas, matplotlib, seaborn.
```

---

## TASK 6 — Xây dựng nhãn tăng/giảm

```
Bạn là một kỹ sư dữ liệu tài chính. Hãy viết script Python để xây dựng biến
mục tiêu (nhãn) cho bài toán phân loại.

Đầu vào: data/aggregated/master_dataset.csv

Yêu cầu:

1. Xây dựng nhãn cơ bản (label_basic):
   - Nếu next_avg_close > avg_close → label = 1 (tăng)
   - Nếu next_avg_close <= avg_close → label = 0 (giảm/không tăng)

2. Xây dựng nhãn có ngưỡng (label_threshold):
   - Tính return = (next_avg_close - avg_close) / avg_close
   - Nếu return > +2% → label = 1
   - Nếu return < -2% → label = 0
   - Nếu |return| <= 2% → label = NaN (loại khỏi mẫu để giảm nhiễu)
   - Lưu cả hai phiên bản nhãn, sẽ quyết định dùng phiên bản nào khi train

3. Phân tích phân phối nhãn:
   - Tỷ lệ label=1 và label=0 tổng thể và theo từng năm
   - Tỷ lệ nhãn theo ngành (banking, real estate, industrial, consumer, energy, tech)
     Mapping ngành sơ bộ cho VN30:
     Banking: ACB, BID, CTG, HDB, MBB, SHB, SSB, STB, TCB, TPB, VCB, VIB, VPB
     Real Estate: BCM, VHM, VIC, VRE
     Energy/Resources: GAS, GVR, PLX, POW
     Consumer/Food: MWG, SAB, VNM
     Industrial: HPG
     Finance/Insurance: BVH, SSI
     Tech/Telecom: FPT
   - Cảnh báo nếu tỷ lệ lớp thiểu số < 35% (mất cân bằng đáng kể)
   - Lưu vào data/aggregated/master_with_labels.csv

4. Xuất báo cáo: reports/label_distribution.png
   Biểu đồ bar chart phân phối nhãn theo năm × quý

Môi trường: Python 3.10+, pandas, matplotlib.
```

---

## TASK 7 — Trích xuất đặc trưng kỹ thuật

```
Bạn là một kỹ sư đặc trưng tài chính. Hãy viết module Python để tính toán
các đặc trưng kỹ thuật từ dữ liệu giá OHLCV theo ngày, sau đó tổng hợp
theo quý cho từng mã cổ phiếu.

Đầu vào: data/prices/all_vn30_prices.csv

Yêu cầu:

1. Tính chỉ báo kỹ thuật theo ngày (dùng pandas-ta hoặc ta-lib):
   - RSI(14): Relative Strength Index 14 ngày
   - MACD: đường MACD, signal, histogram (12,26,9)
   - BB_upper, BB_middle, BB_lower: Bollinger Bands(20, 2)
   - SMA_20, SMA_50: đường trung bình đơn giản
   - EMA_20: đường trung bình hàm mũ

2. Tổng hợp theo quý — với mỗi (ticker, quarter_id) tính:

   Nhóm lợi suất:
   - return_q: lợi suất tích lũy trong quý
   - return_mean_daily: lợi suất trung bình ngày trong quý
   - return_std_daily: độ lệch chuẩn lợi suất ngày (đo biến động)

   Nhóm biến động:
   - volatility_q: return_std_daily * sqrt(trading_days)
   - price_range_q: (high_max - low_min) / avg_close trong quý

   Nhóm thanh khoản:
   - volume_mean_q: khối lượng giao dịch trung bình ngày
   - volume_change_q: thay đổi khối lượng so với quý trước

   Nhóm xu hướng (lấy giá trị cuối quý):
   - sma20_end, ema20_end: giá trị SMA20, EMA20 cuối quý
   - price_vs_sma20: (close_last - sma20_end) / sma20_end

   Nhóm chỉ báo (lấy trung bình trong quý):
   - rsi_mean_q: RSI trung bình trong quý
   - rsi_end_q: RSI cuối quý
   - macd_hist_mean_q: MACD histogram trung bình trong quý
   - bb_position_q: vị trí giá trong Bollinger Bands = (close - BB_lower) / (BB_upper - BB_lower)

   Nhóm động lượng:
   - return_prev_q: lợi suất quý trước (lag 1)
   - return_2q_ago: lợi suất 2 quý trước (lag 2)

3. Xử lý NaN:
   - Các đặc trưng lag quý đầu tiên sẽ bị NaN → ghi rõ và xử lý khi merge
   - Không impute tự động, để nguyên NaN và xử lý ở bước train

4. Đầu ra: data/features/technical_features.csv
   Với các cột: ticker, quarter_id + tất cả đặc trưng kỹ thuật

5. Kiểm tra: in correlation matrix giữa các đặc trưng, cảnh báo nếu
   có cặp đặc trưng có |correlation| > 0.95 (gần như trùng thông tin)

Môi trường: Python 3.10+, pandas, pandas-ta hoặc ta-lib, numpy, seaborn.
```

---

## TASK 8 — Xây dựng danh sách từ khóa tài chính

```
Bạn là một chuyên gia tài chính và NLP. Hãy xây dựng danh sách từ khóa/cụm từ
khóa tài chính tiếng Việt để trích xuất đặc trưng từ tin tức cổ phiếu.

Đầu vào: data/news/processed/all_news_processed.csv

Yêu cầu:

1. Phân tích corpus để tìm từ khóa ứng viên:
   - Dùng CountVectorizer lấy top 500 unigram phổ biến nhất
   - Dùng CountVectorizer lấy top 300 bigram phổ biến nhất
   - Loại bỏ từ dừng đã xác định ở TASK 4
   - Lưu danh sách ứng viên ra config/keyword_candidates.csv để xem xét thủ công

2. Tạo danh sách từ khóa có phân nhóm theo chiều tác động.
   Cấu trúc: mỗi từ khóa có thuộc tính direction = "positive" / "negative" / "neutral"

   NHÓM A — Kết quả kinh doanh (positive):
   positive: ["lợi nhuận tăng", "doanh thu tăng", "tăng trưởng mạnh",
              "vượt kế hoạch", "kỷ lục", "tăng trưởng", "lãi ròng",
              "lợi nhuận sau thuế tăng", "kết quả tích cực"]
   negative: ["lợi nhuận giảm", "doanh thu giảm", "lợi nhuận âm",
              "thua lỗ", "lỗ ròng", "dưới kế hoạch", "sụt giảm",
              "kết quả tiêu cực", "lợi nhuận thấp hơn"]

   NHÓM B — Chính sách cổ đông:
   positive: ["chia cổ tức", "cổ tức cao", "mua lại cổ phiếu", "phát hành thưởng",
              "tăng vốn điều lệ", "cổ tức tiền mặt"]
   negative: ["không chia cổ tức", "hủy cổ tức", "giảm cổ tức",
              "phát hành pha loãng", "chào bán giá thấp"]

   NHÓM C — Tài chính doanh nghiệp:
   positive: ["giảm nợ", "trả nợ", "cải thiện tài chính", "hệ số an toàn vốn",
              "dòng tiền dương", "tiền mặt dồi dào"]
   negative: ["nợ xấu", "nợ vay tăng", "áp lực tài chính", "nợ quá hạn",
              "hệ số nợ cao", "thiếu thanh khoản", "dòng tiền âm"]

   NHÓM D — Hoạt động kinh doanh:
   positive: ["ký kết hợp đồng", "mở rộng thị trường", "dự án mới",
              "đầu tư mới", "hợp tác chiến lược", "thắng thầu", "xuất khẩu tăng"]
   negative: ["hủy hợp đồng", "dự án trì hoãn", "thu hẹp hoạt động",
              "đóng cửa", "dừng dự án"]

   NHÓM E — Rủi ro và pháp lý:
   negative: ["bị phạt", "vi phạm", "bị thanh tra", "bị kiểm toán từ chối",
              "cảnh báo", "đình chỉ", "khởi tố", "điều tra", "tranh chấp pháp lý",
              "bị kiện"]

   NHÓM F — Trung tính / Sự kiện doanh nghiệp:
   neutral: ["đại hội cổ đông", "họp HĐQT", "thay đổi lãnh đạo",
             "thay CEO", "sáp nhập", "mua lại", "phát hành cổ phiếu mới",
             "niêm yết thêm", "thoái vốn"]

3. Lưu cấu trúc từ khóa vào: config/keywords_finance.json
   Format:
   {
     "positive": ["từ khóa 1", "từ khóa 2", ...],
     "negative": ["từ khóa 1", "từ khóa 2", ...],
     "neutral": ["từ khóa 1", "từ khóa 2", ...]
   }

4. Lưu thêm file config/keywords_by_group.json phân theo nhóm A-F để
   phục vụ phân tích sau

5. In báo cáo: tần suất xuất hiện của từng từ khóa trong corpus, giúp
   xác nhận danh sách có phù hợp không

Lưu ý: danh sách trên là gợi ý khởi đầu. Sau khi chạy TASK 9 và 11
(feature importance), sẽ tinh chỉnh lại danh sách này.

Môi trường: Python 3.10+, pandas, sklearn, json.
```

---

## TASK 9 — Trích xuất đặc trưng tần suất từ khóa

```
Bạn là một kỹ sư đặc trưng NLP. Hãy viết module Python để trích xuất đặc trưng
tần suất từ khóa tài chính từ dữ liệu tin tức đã tổng hợp theo quý.

Đầu vào:
- data/aggregated/news_by_quarter.csv (cột combined_text: toàn bộ text/quý/mã)
- config/keywords_finance.json (từ TASK 8)

Yêu cầu:

1. Với mỗi cặp (ticker, quarter_id), tính các đặc trưng sau:

   a) Tần suất thô (raw count):
      - Với mỗi từ khóa k: count_k = số lần từ khóa k xuất hiện trong combined_text
      - Tên cột: kw_{k} (ví dụ: kw_loi_nhuan_tang)

   b) Tần suất chuẩn hóa:
      - norm_count_k = count_k / news_count (chia cho số bài trong quý)
      - Tên cột: kw_norm_{k}

   c) Đặc trưng tổng hợp theo direction:
      - pos_score = tổng norm_count của tất cả từ khóa positive
      - neg_score = tổng norm_count của tất cả từ khóa negative
      - sentiment_ratio = (pos_score - neg_score) / (pos_score + neg_score + 1e-6)

   d) TF-IDF theo corpus (ticker, quarter):
      - Dùng TfidfVectorizer(vocabulary=keyword_list, min_df=2)
      - Fit trên toàn bộ corpus (all ticker-quarter)
      - Transform để lấy TF-IDF cho từng cặp
      - Tên cột: tfidf_{k}

   e) Đặc trưng phủ tin tức:
      - news_count: số bài trong quý (đã có từ TASK 5)
      - news_count_log: log(news_count + 1)
      - has_min_news: 1 nếu news_count >= 5, else 0

2. Xử lý sparse features:
   - Nhiều từ khóa sẽ có count = 0 → đây là bình thường, giữ nguyên
   - Tính sparsity rate: % cặp (ticker, quarter, keyword) có giá trị = 0
   - Nếu sparsity > 95%: cân nhắc loại từ khóa đó (ghi vào log)

3. Đầu ra: data/features/keyword_features.csv
   Các cột: ticker, quarter_id + tất cả đặc trưng từ khóa

4. Báo cáo:
   - Số lượng đặc trưng từ khóa được tạo ra
   - Top 20 từ khóa có tần suất cao nhất
   - Sparsity rate tổng thể
   - Phân phối pos_score và neg_score

Môi trường: Python 3.10+, pandas, sklearn, numpy.
```

---

## TASK 10 — Huấn luyện và đánh giá mô hình

```
Bạn là một kỹ sư Machine Learning. Hãy viết script Python hoàn chỉnh để huấn
luyện và đánh giá các mô hình dự báo xu hướng giá cổ phiếu theo quý.

Đầu vào:
- data/features/technical_features.csv (TASK 7)
- data/features/keyword_features.csv (TASK 9)
- data/aggregated/master_with_labels.csv (TASK 6)

Yêu cầu:

1. Merge và chuẩn bị dữ liệu:
   - Join 3 dataset theo (ticker, quarter_id)
   - Sử dụng label_basic làm nhãn chính
   - Loại bỏ cột quarter_id, ticker khỏi features trước khi train
   - Xử lý NaN: dùng median imputation cho từng cột
   - Ghi rõ số mẫu sau khi merge

2. Time-series split cho panel data:
   - KHÔNG dùng random split
   - Sắp xếp theo quarter_id tăng dần
   - Train: tất cả quý trước Q1/2025
   - Test: Q1/2025 trở đi (hoặc 20% cuối nếu ít hơn 4 quý)
   - Áp dụng nhất quán cho toàn bộ ticker

3. Ba cấu hình thực nghiệm:
   - Config A: chỉ technical_features
   - Config B: chỉ keyword_features
   - Config C: technical_features + keyword_features

4. Baseline models (cho cả 3 config):
   - Majority class baseline
   - Naive momentum: dự báo = nhãn quý hiện tại

5. Mô hình ML (train trên cả 3 config):
   - Logistic Regression (C=1.0, class_weight='balanced')
   - Random Forest (n_estimators=100, class_weight='balanced')
   - XGBoost (scale_pos_weight=neg/pos ratio)
   - LightGBM (is_unbalance=True)

6. Chỉ số đánh giá cho mỗi model × config:
   - Accuracy, Precision, Recall, F1 (macro), AUC-ROC, Balanced Accuracy
   - In confusion matrix

7. Tổng hợp kết quả vào bảng so sánh:
   rows = model × config (ví dụ "XGBoost - Config C")
   cols = các chỉ số đánh giá
   Lưu vào: reports/model_comparison.csv

8. Highlight:
   - Model tốt nhất theo Balanced Accuracy
   - Chênh lệch giữa Config A và Config C (để trả lời câu hỏi nghiên cứu chính)
   - Nếu Config C không cải thiện so với Config A → ghi nhận và phân tích lý do

Môi trường: Python 3.10+, pandas, sklearn, xgboost, lightgbm, numpy.
```

---

## TASK 11 — Phân tích SHAP và Feature Importance

```
Bạn là một kỹ sư Machine Learning. Hãy viết script Python để phân tích mức độ
quan trọng của các đặc trưng, đặc biệt tập trung vào nhóm đặc trưng từ khóa.

Đầu vào: model tốt nhất từ TASK 10 (Config C), tập test

Yêu cầu:

1. Feature Importance từ mô hình tree (XGBoost hoặc LightGBM tốt nhất):
   - Lấy feature_importances_ (gain-based)
   - Plot top 30 đặc trưng quan trọng nhất
   - Đánh dấu màu khác nhau cho đặc trưng kỹ thuật vs từ khóa
   - Lưu: reports/feature_importance.png

2. Permutation Importance (model-agnostic):
   - Dùng sklearn.inspection.permutation_importance trên tập test
   - Lấy top 30 và vẽ biểu đồ tương tự
   - Lưu: reports/permutation_importance.png

3. SHAP Analysis:
   - Dùng shap.TreeExplainer cho XGBoost/LightGBM
   - Vẽ SHAP summary plot (beeswarm): lưu reports/shap_summary.png
   - Vẽ SHAP bar plot (mean |SHAP|): lưu reports/shap_bar.png
   - Lọc riêng SHAP values cho nhóm từ khóa: top 20 từ khóa quan trọng nhất

4. Phân tích từ khóa quan trọng:
   - Tổng hợp top 20 từ khóa (kết hợp từ SHAP + permutation importance)
   - Với mỗi từ khóa: direction (positive/negative/neutral), mean SHAP value,
     chiều tác động thực tế (SHAP > 0 hay < 0 khi từ khóa cao)
   - Kiểm tra: từ khóa "positive" có SHAP dương không? (kỳ vọng: có)
   - Lưu: reports/top_keywords_analysis.csv

5. So sánh đóng góp nhóm:
   - Tổng mean |SHAP| của nhóm kỹ thuật vs nhóm từ khóa
   - Tỷ lệ phần trăm đóng góp
   - Đây là bằng chứng thực nghiệm cho câu hỏi nghiên cứu H1

6. Phân tích case study (tùy chọn nhưng có giá trị):
   - Chọn 2-3 cặp (ticker, quarter) có kết quả dự báo đúng nhờ từ khóa
   - SHAP waterfall plot cho từng case
   - Lưu: reports/shap_case_study_{ticker}_{quarter}.png

Môi trường: Python 3.10+, shap, sklearn, matplotlib, pandas.
```

---

## TASK 12 — Đóng gói Pipeline bán tự động

```
Bạn là một kỹ sư phần mềm. Hãy đóng gói toàn bộ quy trình thành một pipeline
bán tự động có thể chạy lại hoàn toàn từ đầu hoặc chạy từng bước riêng lẻ.

Yêu cầu:

1. Tạo file pipeline/run_pipeline.py với argparse:
   python run_pipeline.py --step all          # chạy toàn bộ
   python run_pipeline.py --step data         # chỉ thu thập dữ liệu (TASK 1+2+3)
   python run_pipeline.py --step features     # chỉ trích xuất đặc trưng (TASK 7+9)
   python run_pipeline.py --step train        # chỉ huấn luyện (TASK 10+11)
   python run_pipeline.py --step update_news  # scrape tin tức mới nhất và cập nhật

2. Tạo file config/pipeline_config.yaml:
   tickers: [ACB, BCM, ..., VRE]   # danh sách VN30
   start_date: "2022-01-01"
   end_date: "auto"                 # tự động lấy đến ngày hiện tại
   quarter_unit: "quarter"          # có thể đổi thành "month" nếu cần
   min_news_per_period: 5
   train_cutoff: "2024-Q4"         # tất cả trước đây là train
   label_threshold: 0.02            # ngưỡng ±2% cho label_threshold

3. Cấu trúc thư mục chuẩn:
   project/
   ├── config/
   │   ├── pipeline_config.yaml
   │   ├── keywords_finance.json
   │   └── stopwords_finance.txt
   ├── data/
   │   ├── prices/
   │   ├── news/
   │   │   ├── cafef/
   │   │   ├── vietstock/
   │   │   ├── tnck/
   │   │   ├── matched/
   │   │   └── processed/
   │   ├── aggregated/
   │   └── features/
   ├── models/
   │   └── best_model.pkl
   ├── reports/
   ├── pipeline/
   │   ├── run_pipeline.py
   │   ├── task1_prices.py
   │   ├── task2_scrape.py
   │   ├── task3_matching.py
   │   ├── task4_preprocess.py
   │   ├── task5_aggregate.py
   │   ├── task6_labels.py
   │   ├── task7_tech_features.py
   │   ├── task8_keywords.py
   │   ├── task9_kw_features.py
   │   ├── task10_train.py
   │   └── task11_shap.py
   └── notebooks/
       └── exploration.ipynb

4. Logging:
   - Mỗi task ghi log vào logs/{task_name}_{date}.log
   - Log cần có: timestamp, số dòng đầu vào/đầu ra, cảnh báo, lỗi

5. Checkpoint:
   - Sau mỗi task lưu checkpoint để không phải chạy lại từ đầu nếu bị lỗi giữa chừng
   - Kiểm tra checkpoint trước khi chạy: nếu output đã tồn tại thì skip (trừ khi có flag --force)

Môi trường: Python 3.10+, argparse, pyyaml, logging.
```

---

## GHI CHÚ THỰC HIỆN

### Thứ tự ưu tiên

| Tuần | Task | Ghi chú |
|------|------|---------|
| 1 | TASK 1 | Chạy thử ngay để kiểm tra vnstock hoạt động |
| 1-2 | TASK 2A | Scrape CafeF trước (ưu tiên vì có URL theo mã) |
| 2 | TASK 3 | Chạy thử entity matching trên 5 mã trước |
| 2-3 | TASK 2.2, 2.3 | Scrape Vietstock và TNCK song song |
| 3 | TASK 4, 5, 6 | Có thể chạy liên tiếp |
| 4 | TASK 8 | Review thủ công danh sách từ khóa — quan trọng |
| 4 | TASK 7, 9 | Chạy song song |
| 5 | TASK 10, 11 | Train và phân tích |
| 6 | TASK 12 | Đóng gói sau khi các bước đã ổn định |

### Kiểm tra nhanh trước khi làm thực sự

Trước khi chạy toàn bộ pipeline, nên làm **smoke test** với 3 mã (VNM, VCB, FPT)
và 4 quý (2022Q1–2022Q4) để:
- Xác nhận vnstock lấy được dữ liệu
- Xác nhận scrape được ≥ 10 bài/mã/quý từ CafeF
- Xác nhận pipeline chạy end-to-end không lỗi
- Ước lượng thời gian chạy toàn bộ

### Lưu ý quan trọng khi dùng prompt

Với mỗi task, khi dùng prompt với Claude hoặc công cụ AI:
- Cung cấp thêm mẫu dữ liệu thực tế (5-10 dòng CSV) để AI hiểu đúng cấu trúc
- Nếu cấu trúc HTML của trang web thay đổi, mô tả lại cấu trúc thực tế
- Chạy thử với 1 mã trước, sửa lỗi, rồi mới chạy toàn bộ 30 mã
