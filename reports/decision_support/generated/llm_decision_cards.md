# LLM Decision Cards

> Generated with Claude Code CLI model `sonnet` from stripped initial evidence packs. Outcome fields removed.


---

## 2025Q1_SCR_01

## Decision card — SCR — 2025Q1_SCR_01

### 1. Tóm tắt tín hiệu
- SCR = **Buy Candidate**, mô hình cho `pred_proba_up = 0.999444145459264`, `pred_label = 1`, `rank_in_period = 1`. Nguồn: `ml_signal`.
- Tín hiệu kỹ thuật hỗ trợ: `rsi_end_q = 61.8393`, `macd_hist_mean_q = 0.0070`, `price_vs_sma20 = 0.02525`. Nguồn: `technical_snapshot`, `top_drivers`.
- Động lượng gần tích cực: `return_q = 0.18662`, `return_prev_q = 0.02693`, `return_mean_daily = 0.0029998`. Nguồn: `technical_snapshot`.
- Khối lượng tăng: `volume_change_q = 0.69540`. Nguồn: `technical_snapshot`.
- Tin tức có nhưng yếu chi tiết: 5 bài, đều `event_type = general_news`, `match_confidence = partial`, không có `key_facts`, không có full text. Nguồn: `N001`–`N005`, `data_quality_flags`.

### 2. Luận điểm đầu tư chính
- Luận điểm chính: SCR là **ứng viên theo dõi/mua theo mô hình**, vì tín hiệu ML xếp hạng cao nhất kỳ và xác suất nhãn tăng rất cao. Nguồn: `ml_signal.rank_in_period = 1`, `ml_signal.pred_proba_up = 0.999444145459264`, `ml_signal.signal_class = Buy Candidate`.
- Luận điểm kỹ thuật: động lượng ngắn hạn nghiêng tích cực, vì RSI, MACD histogram, vị trí so với SMA20 đều là driver hỗ trợ tín hiệu tăng. Nguồn: `top_drivers.rsi_end_q`, `top_drivers.macd_hist_mean_q`, `top_drivers.price_vs_sma20`.
- Luận điểm dòng tiền: mức quan tâm thị trường có dấu hiệu tăng qua `volume_change_q = 0.6953967642429763`. Nguồn: `technical_snapshot.volume_change_q`, `top_drivers.volume_change_q`.

### 3. Yếu tố hỗ trợ
- RSI cuối kỳ `61.8393` là driver kỹ thuật quan trọng nhất trong mô hình. Nguồn: `top_drivers[0]`.
- MACD histogram trung bình `0.0070` hỗ trợ động lượng xu hướng. Nguồn: `top_drivers[1]`.
- Giá nằm trên SMA20 theo `price_vs_sma20 = 0.02525`, hỗ trợ trạng thái kỹ thuật ngắn hạn. Nguồn: `top_drivers[2]`.
- Lợi suất trong kỳ `return_q = 0.18662` và kỳ trước `return_prev_q = 0.02693` hỗ trợ động lượng gần. Nguồn: `technical_snapshot.return_q`, `technical_snapshot.return_prev_q`.
- Tin tức gần kỳ gồm: nhận chuyển nhượng tài sản (`N001`), quyền tham dự ĐHCĐ thường niên 2025 (`N002`, `N003`), thay đổi người liên quan người nội bộ (`N004`), tiếp nhận đơn từ nhiệm thành viên HĐQT (`N005`). Tất cả chỉ ở mức tóm tắt.

### 4. Yếu tố cần lưu ý / rủi ro
- Tin tức yếu về chiều sâu: `full_text_coverage = 0`, `key_fact_coverage = 0`, `num_title_only_articles = 5`. Nguồn: `data_quality_flags`.
- Ticker matching không đồng nhất: `ticker_matching_confidence = mixed`, từng bài `match_confidence = partial`. Nguồn: `data_quality_flags`, `N001`–`N005`.
- Động lượng lịch sử 2 kỳ trước âm: `return_2q_ago = -0.20579710144927535`, driver ghi `weak_or_negative`. Nguồn: `top_drivers.return_2q_ago`.
- Biến động trong kỳ cần theo dõi: `price_range_q = 0.31384009953991726`, driver ghi phản ánh biến động/rủi ro. Nguồn: `top_drivers.price_range_q`.
- Tin quản trị có thay đổi nhân sự HĐQT qua việc tiếp nhận đơn từ nhiệm thành viên HĐQT. Chi tiết thiếu do không có full text/key facts. Nguồn: `N005`, `data_quality_flags`.

### 5. Trigger theo dõi
- Cập nhật full text/key facts cho `N001`–`N005`, vì hiện `full_text_available = false`, `key_facts = []`.  
- Diễn biến tiếp theo liên quan nhận chuyển nhượng tài sản. Nguồn: `N001.article_summary`.
- Tài liệu/diễn biến ĐHCĐ thường niên 2025. Nguồn: `N002.article_summary`, `N003.article_summary`.
- Thay đổi tiếp theo về người nội bộ/người liên quan/HĐQT. Nguồn: `N004.article_summary`, `N005.article_summary`.
- Tín hiệu kỹ thuật đảo chiều: theo dõi `rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q`, `return_q`. Nguồn: `technical_snapshot`, `top_drivers`.

### 6. Thời điểm review
- Review tại cuối kỳ kế tiếp hoặc khi có dữ liệu mới trong horizon đã nêu. Nguồn: `decision_date = 2025-03-31`, `period_id = 2025Q1`, `holding_horizon = next_quarter_or_period_return_in_signals`.
- Review sớm nếu có cập nhật tin tức trọng yếu cho `N001`–`N005` hoặc chất lượng dữ liệu tin tức được cải thiện. Nguồn: `data_quality_flags`, `news_evidence`.

### 7. Kết luận hỗ trợ quyết định
- Kết luận: SCR đủ điều kiện thành **ứng viên ưu tiên theo dõi theo mô hình kỹ thuật**, nhờ ML rank 1, xác suất tín hiệu tăng cao, nhiều driver kỹ thuật hỗ trợ. Nguồn: `ml_signal`, `top_drivers`.
- Tuy vậy, mức tin cậy định tính từ tin tức còn hạn chế vì thiếu full text, thiếu key facts, ticker matching mixed/partial. Nguồn: `data_quality_flags`, `N001`–`N005`.
- Quyết định nên xem đây là tín hiệu mô hình + kỹ thuật, không phải kết luận cơ bản đầy đủ. Nguồn: `ml_signal`, `technical_snapshot`, `data_quality_flags`.

### 8. Disclaimer
- Không phải khuyến nghị đầu tư.
- Không cam kết lợi nhuận.
- Không dự báo giá tuyệt đối.
- Chỉ dùng evidence pack được cung cấp.
- Tin tức thiếu full text/key facts nên luận điểm định tính có độ bao phủ hạn chế. Nguồn: `data_quality_flags`.

---

## 2025Q1_VHM_02

## 1. Tóm tắt tín hiệu

- VHM = **Buy Candidate**, xác suất mô hình báo tăng **0.999086**, xếp hạng **2** trong kỳ. Nguồn: `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`.
- Động lượng kỹ thuật mạnh: `return_q` **+0.2825**, `return_mean_daily` **+0.004392**, `price_vs_sma20` **+0.076826**. Nguồn: `technical_snapshot`.
- Rủi ro quá mua cao: RSI cuối quý **86.14**. Nguồn: `technical_snapshot.rsi_end_q`, `top_drivers[0].direction=positive_but_overbought_risk`.
- Tin tức có nhưng yếu về chiều sâu: `full_text_coverage=0`, `key_fact_coverage=0`, `summary_coverage=3`, `ticker_matching_confidence=mixed`. Nguồn: `data_quality_flags`.

## 2. Luận điểm đầu tư chính

- Luận điểm chính: VHM có tín hiệu định lượng mạnh cho kỳ kế tiếp, do mô hình xếp VHM nhóm **Buy Candidate**, rank **2**, `pred_label=1`. Nguồn: `ml_signal`.
- Nền kỹ thuật ủng hộ: MACD histogram trung bình dương **0.185622**, giá cao hơn SMA20 **7.68%**, lợi suất quý hiện tại **+28.25%**. Nguồn: `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.return_q`.
- Nhưng tín hiệu không sạch: RSI **86.14** và `price_range_q` **0.35113** cho thấy quá mua + biến động cao. Nguồn: `technical_snapshot.rsi_end_q`, `technical_snapshot.price_range_q`, `top_drivers`.

## 3. Yếu tố hỗ trợ

- Mô hình định lượng rất mạnh: `pred_proba_up=0.9990863674924828`, `signal_class=Buy Candidate`. Nguồn: `ml_signal`.
- Động lượng gần nhất tốt: `return_q=0.2825`, `return_mean_daily=0.0043919767`. Nguồn: `technical_snapshot`.
- Xu hướng ngắn hạn tích cực: giá trên SMA20 **7.68%**, `sma20_end=47.64`. Nguồn: `technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`.
- MACD hỗ trợ tín hiệu tăng: `macd_hist_mean_q=0.1856220694`, driver `supports_up_signal`. Nguồn: `technical_snapshot.macd_hist_mean_q`, `top_drivers[1]`.
- Tin tức doanh nghiệp có hiện diện gần ngày quyết định: 5 tin trong tháng 3/2025, `has_recent_news=true`, `news_coverage=high`. Nguồn: `news_evidence`, `data_quality_flags`.
- Tin N001 ghi nhận thu nhập Ban điều hành năm 2024 giảm **40%** so với 2023. Nguồn: `N001.article_summary`.

## 4. Yếu tố cần lưu ý / rủi ro

- RSI **86.14** = vùng quá mua theo chính driver mô hình, rủi ro đảo chiều/nghỉ nhịp kỹ thuật. Nguồn: `technical_snapshot.rsi_end_q`, `top_drivers[0].direction`.
- Biến động quý cao: `price_range_q=0.3511295303`, driver gắn nhãn `risk_high_volatility`. Nguồn: `technical_snapshot.price_range_q`, `top_drivers[8]`.
- Khối lượng giảm mạnh: `volume_change_q=-0.3709552429`, driver `weak_or_negative`. Nguồn: `technical_snapshot.volume_change_q`, `top_drivers[6]`.
- Kỳ trước âm: `return_prev_q=-0.0794016110`, driver `weak_or_negative`. Nguồn: `technical_snapshot.return_prev_q`, `top_drivers[5]`.
- Tin tức thiếu chiều sâu: `full_text_coverage=0`, `key_fact_coverage=0`, `num_title_only_articles=5`; nhiều bài không có `article_summary`. Nguồn: `data_quality_flags`, `news_evidence`.
- Độ tin cậy gắn ticker không hoàn toàn đồng nhất: `ticker_matching_confidence=mixed`. Nguồn: `data_quality_flags`.
- N002, N003 chỉ có tiêu đề/URL, không có summary/key_facts/risk_flags; không nên dùng làm luận điểm mạnh. Nguồn: `N002`, `N003`.

## 5. Trigger theo dõi

- RSI hạ nhiệt khỏi trạng thái quá mua hiện tại hoặc tiếp tục duy trì rất cao. Mốc gốc: `rsi_end_q=86.1443783479`.
- MACD histogram còn dương hay suy yếu. Mốc gốc: `macd_hist_mean_q=0.1856220694`.
- Giá còn duy trì trên SMA20 hay mất lợi thế. Mốc gốc: `price_vs_sma20=0.0768261965`, `sma20_end=47.64`.
- Khối lượng có cải thiện từ mức giảm hiện tại hay không. Mốc gốc: `volume_change_q=-0.3709552429`.
- Tin AGM/ĐHĐCĐ có thêm thông tin thực chất sau các thông báo ngày đăng ký cuối cùng. Nguồn gốc: `N004.article_summary`, `N005.article_summary`.
- Cập nhật full text/key facts cho N001–N005, vì hiện `full_text_coverage=0`, `key_fact_coverage=0`.

## 6. Thời điểm review

- Review tại kỳ kế tiếp theo horizon: `holding_horizon=next_quarter_or_period_return_in_signals`.
- Review sớm nếu có tin mới sau `news_cutoff=2025-03-31` hoặc nếu dữ liệu tin được bổ sung full text/key facts. Nguồn: `guardrails.news_cutoff`, `data_quality_flags`.
- Review quanh thông tin ĐHĐCĐ thường niên 2025, vì N004/N005 chỉ mới nêu ngày đăng ký/quyền tham dự, chưa có nội dung nghị quyết. Nguồn: `N004.article_summary`, `N005.article_summary`.

## 7. Kết luận hỗ trợ quyết định

- VHM phù hợp đưa vào danh sách **theo dõi/mua ứng viên có điều kiện**, do mô hình rất mạnh và động lượng kỹ thuật ủng hộ. Nguồn: `ml_signal`, `technical_snapshot`.
- Không nên xem tín hiệu là quyết định mua tự động, vì RSI quá mua, biến động cao, khối lượng giảm, và evidence tin tức thiếu full text/key facts. Nguồn: `technical_snapshot.rsi_end_q`, `technical_snapshot.price_range_q`, `technical_snapshot.volume_change_q`, `data_quality_flags`.
- Decision stance: **ủng hộ xem xét tích cực nhưng cần kiểm soát rủi ro kỹ thuật và chờ xác nhận thêm từ dữ liệu tin tức/khối lượng**. Nguồn: `ml_signal.signal_class`, `top_drivers`, `data_quality_flags`.

## 8. Disclaimer

- Đây là decision card nghiên cứu học thuật, chỉ dùng evidence pack được cung cấp.
- Không phải khuyến nghị đầu tư.
- Không dự báo giá tuyệt đối.
- Không cam kết lợi nhuận.
- Không dùng dữ liệu outcome/realized return tương lai. Nguồn: `guardrails.initial_card_must_not_use_outcome=true`.

---

## 2025Q1_VIC_03

## 1. Tóm tắt tín hiệu

- VIC = **Buy Candidate**, rank **3** trong period, `pred_proba_up=0.9981398250260798`, `pred_label=1`. Nguồn: `ml_signal`.
- Động lượng kỹ thuật mạnh: `return_q=0.4306857424765664`, `return_mean_daily=0.006340964202580277`, `macd_hist_mean_q=0.1246856309080669`. Nguồn: `technical_snapshot`.
- Trạng thái quá nóng rõ: `rsi_end_q=91.10431541618765`, driver ghi `positive_but_overbought_risk`. Nguồn: `top_drivers.rsi_end_q`.
- Biến động cao: `price_range_q=0.44185210651331414`, driver ghi `risk_high_volatility`. Nguồn: `top_drivers.price_range_q`.
- Tin tức gần ngày quyết định có, nhưng chất lượng trích xuất yếu: `full_text_coverage=0`, `key_fact_coverage=0`, `num_title_only_articles=5`. Nguồn: `data_quality_flags`.

## 2. Luận điểm đầu tư chính

- Luận điểm chính: **động lượng kỹ thuật hỗ trợ đưa VIC vào danh sách ứng viên mua**, vì mô hình xếp VIC `Buy Candidate`, rank 3, xác suất tín hiệu tăng cao. Nguồn: `ml_signal`.
- Tín hiệu không độc lập cơ bản: news chủ yếu thiếu `article_summary`, `key_facts`, `risk_flags`; do đó luận điểm nghiêng về kỹ thuật, không phải xác nhận bằng nền tảng tin tức. Nguồn: `news_evidence`, `data_quality_flags.summary_coverage=1`, `key_fact_coverage=0`.
- Rủi ro chính: tín hiệu mạnh đi cùng quá mua và biến động cao, nên cần kiểm soát theo trigger thay vì xem là xác nhận chắc chắn. Nguồn: `top_drivers.rsi_end_q`, `top_drivers.price_range_q`.

## 3. Yếu tố hỗ trợ

- MACD histogram trung bình dương, hỗ trợ động lượng xu hướng: `macd_hist_mean_q=0.1246856309080669`, direction `supports_up_signal`. Nguồn: `top_drivers.macd_hist_mean_q`.
- Giá cao hơn SMA20: `price_vs_sma20=0.1354070825910773`, direction `supports_up_signal`. Nguồn: `top_drivers.price_vs_sma20`.
- Lợi suất kỳ hiện tại mạnh: `return_q=0.4306857424765664`, direction `supports_up_signal`. Nguồn: `top_drivers.return_q`.
- Khối lượng tăng: `volume_change_q=0.8264844950295648`, direction `supports_up_signal`. Nguồn: `top_drivers.volume_change_q`.
- Tin tức liên quan hiện diện gần decision date: N001 ngày 2025-03-31 về giải trình chênh lệch BCTC kiểm toán 2024; event_type `legal_risk`. Nguồn: `N001`.

## 4. Yếu tố cần lưu ý / rủi ro

- RSI rất cao: `rsi_end_q=91.10431541618765`; evidence pack tự gắn hướng `positive_but_overbought_risk`. Nguồn: `top_drivers.rsi_end_q`.
- Biên độ giá trong kỳ lớn: `price_range_q=0.44185210651331414`; evidence pack gắn `risk_high_volatility`. Nguồn: `top_drivers.price_range_q`.
- Kỳ trước âm: `return_prev_q=-0.04160756501182029`, direction `weak_or_negative`. Nguồn: `top_drivers.return_prev_q`.
- N001 có event_type `legal_risk`, nhưng không có key facts/risk flags để định lượng hay diễn giải sâu. Nguồn: `N001.key_facts=[]`, `N001.risk_flags=[]`.
- Tin N002–N005 phần lớn thiếu summary/key facts/risk flags; nhiều bài chỉ có title, full text không có trong prompt. Nguồn: `N002`–`N005`, `data_quality_flags.full_text_coverage=0`.
- `ticker_matching_confidence=mixed`; cần thận trọng khi dùng cụm tin tức tổng hợp. Nguồn: `data_quality_flags.ticker_matching_confidence`.

## 5. Trigger theo dõi

- RSI giảm khỏi vùng quá nóng hoặc tiếp tục duy trì cao: theo dõi lại `rsi_end_q`, vì đây là driver kỹ thuật quan trọng nhất và có overbought risk. Nguồn: `top_drivers.rsi_end_q`.
- MACD histogram đảo chiều hoặc suy yếu: theo dõi `macd_hist_mean_q`, vì đang là yếu tố hỗ trợ xu hướng. Nguồn: `top_drivers.macd_hist_mean_q`.
- Giá mất khoảng cách so với SMA20: theo dõi `price_vs_sma20` và `sma20_end=25.5415`. Nguồn: `technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`.
- Khối lượng thay đổi mạnh: theo dõi `volume_change_q=0.8264844950295648`, vì đang phản ánh mức quan tâm thị trường. Nguồn: `top_drivers.volume_change_q`.
- Có thêm dữ liệu chi tiết cho N001 hoặc BCTC kiểm toán: vì N001 là `legal_risk`, nhưng `key_facts=[]` và `full_text_available=false`. Nguồn: `N001`.
- Cải thiện chất lượng news evidence: đặc biệt `full_text_coverage`, `key_fact_coverage`, `summary_coverage`. Nguồn: `data_quality_flags`.

## 6. Thời điểm review

- Review chính: cuối kỳ kế tiếp hoặc kỳ return tiếp theo theo `holding_horizon=next_quarter_or_period_return_in_signals`. Nguồn: `holding_horizon`.
- Review sớm nếu trigger kỹ thuật đổi chiều: RSI, MACD, price_vs_sma20, volume_change_q. Nguồn: `top_drivers`.
- Review sớm nếu có thêm thông tin chi tiết cho N001 hoặc tin mới trước/sau `news_cutoff=2025-03-31`. Nguồn: `guardrails.news_cutoff`, `N001`.

## 7. Kết luận hỗ trợ quyết định

- VIC có **tín hiệu kỹ thuật mạnh**, phù hợp xếp vào nhóm **ứng viên theo dõi/mua theo mô hình**, dựa trên `Buy Candidate`, rank 3, `pred_proba_up=0.9981398250260798`. Nguồn: `ml_signal`.
- Quyết định cần điều kiện: không nên dựa riêng vào điểm mô hình vì RSI quá mua, biến động cao, news evidence thiếu full text/key facts. Nguồn: `top_drivers.rsi_end_q`, `top_drivers.price_range_q`, `data_quality_flags`.
- Kết luận ngắn: **hỗ trợ quyết định tích cực có kiểm soát rủi ro**, không phải xác nhận chắc chắn từ tin tức/cơ bản. Nguồn: `ml_signal`, `data_quality_flags`.

## 8. Disclaimer

- Nội dung chỉ dùng evidence pack được cung cấp.
- Không dùng dữ kiện ngoài evidence pack.
- Không dự báo giá tuyệt đối.
- Không cam kết lợi nhuận.
- Không phải khuyến nghị đầu tư.
- Không dùng realized return hoặc outcome tương lai.
