# LLM Decision Cards — llm_ml_only

> Generated with anthropic-python model `claude-opus` from prompt-safe `ml_only` evidence packs. Outcome fields removed.


---

## 2025Q1_SCR_01

## 1. Tóm tắt tín hiệu

- Mã: **SCR**.
- Ngày quyết định: **2025-03-31**.
- Mô hình: **technical_Config_A_from_existing_pipeline**.
- Phân loại: **Buy Candidate**; xác suất nhãn tăng **0.999444**; xếp hạng **1** trong kỳ. [ml_signal.pred_label, ml_signal.pred_proba_up, ml_signal.rank_in_period, ml_signal.signal_class]
- Tín hiệu kỹ thuật chính: RSI cuối kỳ **61.84**, MACD histogram trung bình **0.0070**, giá cao hơn SMA20 **2.53%**, khối lượng thay đổi **69.54%**. [technical_snapshot.rsi_end_q, technical_snapshot.macd_hist_mean_q, technical_snapshot.price_vs_sma20, technical_snapshot.volume_change_q]
- Đây là card **ml-only**; tin tức bị loại khỏi evidence pack. [card_input_variant, data_quality_flags.news_evidence_removed_for_ablation, guardrails.news_evidence_excluded]

## 2. Luận điểm đầu tư chính

- Mô hình định lượng xếp SCR vào nhóm **Buy Candidate**, với xác suất mô hình cao và xếp hạng 1 trong kỳ. [ml_signal]
- Nhiều driver kỹ thuật cùng hỗ trợ tín hiệu: RSI, MACD histogram, vị trí giá so với SMA20 và thay đổi khối lượng. [top_drivers, technical_snapshot]
- Luận điểm chỉ dựa trên tín hiệu kỹ thuật và mô hình; **evidence tin tức chưa đủ mạnh**. [data_quality_flags.news_evidence_removed_for_ablation]

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ **61.8393**, được mô hình xác định là driver kỹ thuật quan trọng nhất và hỗ trợ tín hiệu đi lên. [top_drivers.feature=rsi_end_q, technical_snapshot.rsi_end_q]
- MACD histogram trung bình **0.007025**, phản ánh động lượng xu hướng hỗ trợ tín hiệu. [top_drivers.feature=macd_hist_mean_q, technical_snapshot.macd_hist_mean_q]
- Giá cao hơn SMA20 khoảng **2.53%**, hỗ trợ trạng thái kỹ thuật tích cực trong kỳ. [top_drivers.feature=price_vs_sma20, technical_snapshot.price_vs_sma20]
- Thay đổi khối lượng **69.54%**, được mô hình xem là yếu tố hỗ trợ mức độ quan tâm thị trường. [top_drivers.feature=volume_change_q, technical_snapshot.volume_change_q]
- Mô hình ghi nhận tín hiệu đi lên với xác suất **0.999444** và xếp hạng **1**. [ml_signal.pred_proba_up, ml_signal.rank_in_period]

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ là **31.38%**, cho thấy biến động cần theo dõi. [top_drivers.feature=price_range_q, technical_snapshot.price_range_q]
- Tín hiệu phụ thuộc vào một mô hình kỹ thuật; evidence pack không có kiểm chứng định tính từ tin tức. [ml_signal.model_name, card_input_variant, data_quality_flags.news_evidence_removed_for_ablation]
- Một driver bị mô hình gắn nhãn **weak_or_negative**; evidence pack không đủ cơ sở để diễn giải thêm ngoài trường dữ liệu này. [top_drivers.direction=weak_or_negative]
- Xác suất mô hình không phải cam kết kết quả. Evidence pack không cung cấp ngưỡng quản trị rủi ro hoặc điều kiện vô hiệu tín hiệu. [ml_signal.pred_proba_up, guardrails.not_investment_advice]
- **Evidence tin tức chưa đủ mạnh**; không có `article_summary`, `key_facts`, `risk_flags` hoặc `event_type` trong pack. [data_quality_flags.news_evidence_removed_for_ablation]

## 5. Trigger theo dõi

- Cập nhật lại phân loại, xác suất mô hình và xếp hạng kỳ mới. [ml_signal]
- Theo dõi RSI cuối kỳ, MACD histogram, vị trí giá so với SMA20. [technical_snapshot.rsi_end_q, technical_snapshot.macd_hist_mean_q, technical_snapshot.price_vs_sma20]
- Theo dõi thay đổi khối lượng và biên độ giá. [technical_snapshot.volume_change_q, technical_snapshot.price_range_q]
- Kiểm tra bổ sung evidence tin tức nếu xuất hiện `article_summary`, `key_facts`, `risk_flags`, `event_type`. Hiện chưa có ngưỡng trigger định lượng trong evidence pack. [data_quality_flags.missing_fields, data_quality_flags.news_evidence_removed_for_ablation]

## 6. Thời điểm review

- Review tại kỳ tín hiệu kế tiếp sau **2025-03-31**, phù hợp với `holding_horizon`: **next_quarter_or_period_return_in_signals**. [decision_date, holding_horizon]
- Review sớm hơn nếu mô hình, RSI, MACD histogram, vị trí giá so với SMA20 hoặc biến động thay đổi đáng kể. [ml_signal, technical_snapshot]

## 7. Kết luận hỗ trợ quyết định

- SCR có tín hiệu định lượng mạnh và được xếp **Buy Candidate** trong kỳ **2025Q1**. [ml_signal, period_id]
- Tín hiệu hỗ trợ chủ yếu đến từ kỹ thuật và mô hình; chưa có evidence tin tức đủ mạnh để củng cố luận điểm. [top_drivers, data_quality_flags.news_evidence_removed_for_ablation]
- Có thể dùng card như đầu vào sàng lọc và theo dõi. Không đủ cơ sở để biến thành khuyến nghị đầu tư chắc chắn. [guardrails.not_investment_advice]

## 8. Disclaimer

- Nội dung chỉ hỗ trợ phân tích học thuật và quyết định; không phải khuyến nghị đầu tư. [guardrails.not_investment_advice]
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Card dùng evidence có sẵn tại **2025-03-31**; tin tức đã bị loại khỏi pack. [decision_date, data_quality_flags.news_evidence_removed_for_ablation]
- Không sử dụng dữ liệu sau thời điểm quyết định. [guardrails.no_post_decision_data]

---

## 2025Q1_VHM_02

## 1. Tóm tắt tín hiệu

- VHM có tín hiệu ML nghiêng tăng: `pred_label = 1`, `pred_proba_up = 0.9990863674924828`, xếp hạng `2`, phân loại `Buy Candidate` (`ml_signal`).
- Động lượng quý tích cực: `return_q = 0.2825`, `macd_hist_mean_q = 0.1856`, giá cao hơn SMA20 khoảng `7.68%` (`technical_snapshot`).
- Trạng thái quá mua và thanh khoản yếu: `rsi_end_q = 86.14`, `volume_change_q = -37.10%` (`technical_snapshot`).
- Evidence tin tức chưa đủ mạnh: tin tức bị loại khỏi pack (`data_quality_flags.news_evidence_removed_for_ablation = true`; `guardrails.news_evidence_excluded = true`).

## 2. Luận điểm đầu tư chính

Tín hiệu ML và động lượng kỹ thuật đang ủng hộ việc đưa VHM vào danh sách theo dõi tích cực. Tuy nhiên, RSI ở vùng quá mua, biên độ giá cao và khối lượng giảm làm suy yếu độ chắc của tín hiệu (`ml_signal`; `technical_snapshot.rsi_end_q`; `technical_snapshot.price_range_q`; `technical_snapshot.volume_change_q`).

## 3. Yếu tố hỗ trợ

- Tín hiệu mô hình nghiêng tăng, xác suất mô hình gán cho chiều tăng ở mức `0.9990863674924828`; xếp hạng 2 trong kỳ (`ml_signal.pred_proba_up`; `ml_signal.rank_in_period`).
- Lợi suất quý hiện tại tích cực ở mức `0.2825` (`technical_snapshot.return_q`).
- MACD histogram trung bình dương, hỗ trợ động lượng xu hướng (`technical_snapshot.macd_hist_mean_q`).
- Giá cuối kỳ cao hơn SMA20 khoảng `7.68%`; SMA20 cuối kỳ là `47.64` (`technical_snapshot.price_vs_sma20`; `technical_snapshot.sma20_end`).
- Lợi suất trễ hai kỳ và lợi suất trung bình ngày đều dương (`technical_snapshot.return_2q_ago`; `technical_snapshot.return_mean_daily`).

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `86.14`, cho thấy trạng thái quá mua; đây là driver kỹ thuật quan trọng nhất của mô hình nhưng đồng thời tạo rủi ro điều chỉnh (`top_drivers[0]`; `technical_snapshot.rsi_end_q`).
- Khối lượng giảm `37.10%`, phản ánh mức độ quan tâm thị trường yếu hơn (`technical_snapshot.volume_change_q`; `top_drivers[6]`).
- Biên độ giá trong kỳ ở mức `0.3511`, cho thấy biến động cao (`technical_snapshot.price_range_q`; `top_drivers[8]`).
- Lợi suất quý trước âm `-7.94%`, tạo tín hiệu động lượng không đồng nhất (`technical_snapshot.return_prev_q`; `top_drivers[5]`).
- Giá nằm cao hơn SMA20; khoảng cách dương lớn có thể làm tăng rủi ro đảo chiều về đường trung bình (`technical_snapshot.price_vs_sma20`; `technical_snapshot.sma20_end`).
- Evidence tin tức bị loại khỏi phân tích; không có cơ sở định tính từ `article_summary`, `key_facts`, `risk_flags` hoặc `event_type` (`data_quality_flags.news_evidence_removed_for_ablation`; `guardrails.news_evidence_excluded`).

## 5. Trigger theo dõi

- RSI giảm từ mức `86.14`: theo dõi khả năng suy yếu trạng thái quá mua (`technical_snapshot.rsi_end_q`).
- MACD histogram suy giảm hoặc chuyển âm: theo dõi đảo chiều động lượng (`technical_snapshot.macd_hist_mean_q`).
- `price_vs_sma20` thu hẹp về 0 hoặc chuyển âm: theo dõi mất hỗ trợ xu hướng ngắn hạn (`technical_snapshot.price_vs_sma20`).
- `volume_change_q` tiếp tục âm: theo dõi xác nhận thanh khoản yếu (`technical_snapshot.volume_change_q`).
- `price_range_q` tăng thêm: theo dõi rủi ro biến động cao hơn (`technical_snapshot.price_range_q`).
- Cập nhật thêm evidence tin tức có `article_summary`, `key_facts`, `risk_flags`, `event_type` trước review định tính (`data_quality_flags.news_evidence_removed_for_ablation`).

## 6. Thời điểm review

Cuối quý hoặc kỳ tín hiệu kế tiếp, phù hợp với `holding_horizon = next_quarter_or_period_return_in_signals`. Review sớm hơn nếu trigger kỹ thuật xuất hiện.

## 7. Kết luận hỗ trợ quyết định

VHM có tín hiệu kỹ thuật và ML tích cực, phù hợp để tiếp tục theo dõi hoặc đưa vào bước đánh giá tiếp theo. Chưa đủ cơ sở cho quyết định độc lập vì RSI quá mua, khối lượng giảm, biến động cao và evidence tin tức bị loại khỏi pack (`ml_signal`; `technical_snapshot`; `data_quality_flags`; `guardrails`).

## 8. Disclaimer

Decision card chỉ dùng evidence trong pack, tại ngày quyết định `2025-03-31`. Không phải khuyến nghị đầu tư chắc chắn. Không dự báo giá tuyệt đối. Tín hiệu mô hình không bảo đảm kết quả.

---

## 2025Q1_VIC_03

## 1. Tóm tắt tín hiệu

- VIC, kỳ `2025Q1`, ngày quyết định `2025-03-31` (`ticker`, `period_id`, `decision_date`).
- Mô hình `technical_Config_A_from_existing_pipeline` gắn nhãn `Buy Candidate`; `pred_label = 1`, `pred_proba_up = 0.9981`, xếp hạng 3 trong kỳ (`ml_signal`).
- Động lượng kỹ thuật hỗ trợ hướng tăng: `macd_hist_mean_q = 0.1247`, `price_vs_sma20 = 0.1354`, `volume_change_q = 0.8265` (`technical_snapshot`).
- Rủi ro quá mua và biến động cao: `rsi_end_q = 91.10`, `price_range_q = 0.4419` (`technical_snapshot`, `top_drivers`).
- Tin tức bị loại khỏi pack (`data_quality_flags.news_evidence_removed_for_ablation = true`); evidence tin tức chưa đủ mạnh.

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình nghiêng tích cực, dựa trên nhãn `Buy Candidate` và output xác suất hướng tăng cao (`ml_signal`).
- Động lượng, vị trí giá so với SMA20 và khối lượng cùng hỗ trợ tín hiệu (`macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q`).
- Conviction bị hạn chế bởi RSI cuối kỳ ở mức rất cao và biên độ giá lớn (`rsi_end_q`, `price_range_q`).
- Kết luận phù hợp: xem xét theo dõi có điều kiện, không xem là khuyến nghị mua chắc chắn.

## 3. Yếu tố hỗ trợ

- MACD histogram trung bình dương, phản ánh động lượng xu hướng hỗ trợ tín hiệu tăng (`macd_hist_mean_q = 0.1247`; `top_drivers`).
- Feature giá so với SMA20 dương, phản ánh giá nằm trên mặt bằng SMA20 cuối kỳ (`price_vs_sma20 = 0.1354`; `sma20_end = 25.5415`).
- Thay đổi khối lượng dương, cho thấy mức độ quan tâm thị trường tăng theo feature mô hình (`volume_change_q = 0.8265`; `top_drivers`).
- Mô hình xếp hạng VIC ở vị trí 3 trong kỳ (`ml_signal.rank_in_period = 3`).

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `91.10` là driver quan trọng nhất và được gắn cờ `positive_but_overbought_risk`; trạng thái quá mua có thể làm tín hiệu dễ đảo chiều (`rsi_end_q`; `top_drivers`).
- Biên độ giá trong kỳ `0.4419` phản ánh biến động/rủi ro cao (`price_range_q`; `top_drivers`).
- SMA20 cuối kỳ chỉ là mặt bằng kỹ thuật tại thời điểm quyết định, không phải mức giá mục tiêu (`sma20_end`).
- Mô hình thuộc biến thể `ml_only`; tin tức bị loại khỏi phân tích (`card_input_variant`, `news_evidence_removed_for_ablation`, `news_evidence_excluded`).
- Evidence tin tức chưa đủ mạnh để đánh giá thêm catalyst hoặc rủi ro định tính (`data_quality_flags`, `guardrails`).

## 5. Trigger theo dõi

- RSI cuối kỳ: theo dõi việc tiếp tục duy trì ở mức `91.10` hoặc hạ nhiệt (`rsi_end_q`).
- MACD histogram: theo dõi xu hướng duy trì hay suy yếu so với `0.1247` (`macd_hist_mean_q`).
- Giá so với SMA20: theo dõi việc duy trì feature dương `0.1354` (`price_vs_sma20`, `sma20_end`).
- Khối lượng: theo dõi thay đổi so với `0.8265` (`volume_change_q`).
- Biên độ giá: theo dõi biến động so với `0.4419` (`price_range_q`).
- Cập nhật khi mô hình phát sinh period signal mới (`holding_horizon`, `ml_signal`).

## 6. Thời điểm review

- Review cuối quý kế tiếp theo horizon `next_quarter_or_period_return_in_signals` (`holding_horizon`).
- Review sớm hơn khi có period signal mới hoặc thay đổi rõ ở RSI, MACD, giá so với SMA20 và khối lượng (`holding_horizon`, `technical_snapshot`).

## 7. Kết luận hỗ trợ quyết định

- VIC có tín hiệu kỹ thuật và ML nghiêng tích cực (`ml_signal`, `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q`).
- Tín hiệu chưa đồng nhất do RSI quá mua, biến động cao và thiếu evidence tin tức (`rsi_end_q`, `price_range_q`, `news_evidence_removed_for_ablation`).
- Có thể đưa VIC vào diện theo dõi có điều kiện; cần review theo trigger trước khi đưa ra quyết định riêng.

## 8. Disclaimer

- Card chỉ hỗ trợ phân tích, không phải khuyến nghị đầu tư (`guardrails.not_investment_advice = true`).
- Output mô hình không bảo đảm kết quả tương lai (`ml_signal`).
- Card không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Phân tích dùng biến thể `ml_only`; evidence tin tức đã bị loại (`card_input_variant`, `data_quality_flags.news_evidence_removed_for_ablation = true`).

---

## 2025Q1_SHB_04

## 1. Tóm tắt tín hiệu

- SHB nhận tín hiệu **“Buy Candidate”** từ mô hình kỹ thuật; `pred_label: 1`, `pred_proba_up: 0.9971`, xếp hạng `4` trong kỳ. `[ml_signal]`
- Tín hiệu có động lượng kỹ thuật tích cực, nhưng đi kèm trạng thái quá mua và biến động cao. `[top_drivers]`, `[technical_snapshot]`
- Tin tức bị loại khỏi evidence pack; **evidence tin tức chưa đủ mạnh**. `[data_quality_flags.news_evidence_removed_for_ablation]`, `[guardrails.news_evidence_excluded]`

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình nghiêng về nhóm ứng viên tích cực dựa trên MACD dương, giá cao hơn SMA20, thay đổi khối lượng tích cực và động lượng kỳ hiện tại. `[ml_signal]`, `[technical_snapshot.macd_hist_mean_q]`, `[technical_snapshot.price_vs_sma20]`, `[technical_snapshot.volume_change_q]`
- Tín hiệu không đồng nghĩa với quyết định mua chắc chắn, vì RSI cuối kỳ ở mức cao và biên độ giá trong kỳ lớn. `[technical_snapshot.rsi_end_q]`, `[technical_snapshot.price_range_q]`
- Cần xem SHB như trường hợp cần theo dõi tín hiệu kỹ thuật, không như kết luận đầu tư độc lập. `[guardrails.not_investment_advice]`

## 3. Yếu tố hỗ trợ

- MACD histogram trung bình dương `0.0363`, hỗ trợ diễn giải động lượng tăng. `[technical_snapshot.macd_hist_mean_q]`
- Giá cao hơn SMA20 khoảng `11.38%`, cho thấy vị trí trên đường trung bình ngắn hạn. `[technical_snapshot.price_vs_sma20]`
- Thay đổi khối lượng trong kỳ `1.3341`, hỗ trợ tín hiệu về mức độ quan tâm thị trường. `[technical_snapshot.volume_change_q]`
- Lợi suất trung bình ngày `0.00528` và lợi suất kỳ hiện tại `0.34794` là các biến được mô hình dùng để phản ánh xu hướng gần nhất. `[technical_snapshot.return_mean_daily]`, `[technical_snapshot.return_q]`
- Mô hình xếp SHB hạng `4` trong kỳ và gắn nhãn `Buy Candidate`. `[ml_signal]`

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `80.33`; driver được mô tả là tích cực nhưng có rủi ro quá mua. `[technical_snapshot.rsi_end_q]`, `[top_drivers.feature=rsi_end_q]`
- Biên độ giá trong kỳ `0.37162`, phản ánh rủi ro biến động cao. `[technical_snapshot.price_range_q]`, `[top_drivers.feature=price_range_q]`
- Lợi suất kỳ trước `-0.07288` và lợi suất trễ hai kỳ `-0.00951` cho thấy động lượng lịch sử không đồng nhất. `[technical_snapshot.return_prev_q]`, `[technical_snapshot.return_2q_ago]`
- Dữ liệu tin tức không có trong biến thể này; không đủ cơ sở định tính để xác nhận hoặc phản biện tín hiệu kỹ thuật. `[data_quality_flags.news_evidence_removed_for_ablation]`
- Xác suất mô hình cao không loại bỏ rủi ro sai tín hiệu hoặc đảo chiều kỹ thuật. `[ml_signal.pred_proba_up]`, `[technical_snapshot.rsi_end_q]`, `[technical_snapshot.price_range_q]`

## 5. Trigger theo dõi

- Theo dõi RSI; mức cao hiện tại cần được đánh giá lại khi dữ liệu kỳ mới cập nhật. `[technical_snapshot.rsi_end_q]`
- Theo dõi MACD histogram; suy yếu so với mức trung bình hiện tại làm giảm hỗ trợ động lượng. `[technical_snapshot.macd_hist_mean_q]`
- Theo dõi vị trí giá so với SMA20; thu hẹp mức chênh lệch hiện tại là tín hiệu cần xem xét lại. `[technical_snapshot.price_vs_sma20]`, `[technical_snapshot.sma20_end]`
- Theo dõi khối lượng; đảo chiều so với mức thay đổi hiện tại làm yếu luận điểm về sự quan tâm thị trường. `[technical_snapshot.volume_change_q]`
- Theo dõi biên độ giá; biến động tiếp tục cao làm tăng yêu cầu kiểm soát rủi ro. `[technical_snapshot.price_range_q]`
- Evidence pack không cung cấp ngưỡng trigger định lượng cụ thể. `[data_quality_flags.missing_fields]`

## 6. Thời điểm review

- Review vào **quý hoặc kỳ kế tiếp**, phù hợp với `holding_horizon: next_quarter_or_period_return_in_signals`. `[holding_horizon]`
- Review sớm khi RSI, MACD, vị trí giá so với SMA20, khối lượng hoặc biên độ giá thay đổi đáng kể. `[technical_snapshot]`
- Ngày lập decision card: `2025-03-31`. `[decision_date]`

## 7. Kết luận hỗ trợ quyết định

- SHB có tín hiệu kỹ thuật tích cực và được mô hình xếp vào nhóm **“Buy Candidate”**. `[ml_signal]`
- Tín hiệu bị giảm độ tin cậy thực hành bởi RSI quá mua, biến động cao và động lượng lịch sử không đồng nhất. `[technical_snapshot]`, `[top_drivers]`
- Có thể đưa SHB vào danh sách theo dõi hoặc quy trình đánh giá tiếp theo; chưa đủ cơ sở để xem đây là khuyến nghị mua chắc chắn. `[guardrails.not_investment_advice]`
- Cần cập nhật các trigger kỹ thuật trước kỳ review kế tiếp. `[technical_snapshot]`

## 8. Disclaimer

- Nội dung chỉ hỗ trợ phân tích học thuật và quyết định; không phải khuyến nghị đầu tư. `[guardrails.not_investment_advice]`
- Chỉ sử dụng evidence pack được cung cấp.
- Tin tức bị loại khỏi evidence pack; **evidence tin tức chưa đủ mạnh**. `[data_quality_flags.news_evidence_removed_for_ablation]`
- Không có dự báo giá tuyệt đối, cam kết lợi nhuận hoặc kết luận chắc chắn.

---

## 2025Q1_BSI_05

## 1. Tóm tắt tín hiệu

- BSI được mô hình xếp loại **“Buy Candidate”**, xác suất dự báo tăng `0.9968577136500381`, xếp hạng 5 trong kỳ 2025Q1 (`ml_signal`).
- Tín hiệu kỹ thuật nghiêng tích cực: lợi suất kỳ hiện tại `0.1902488062327218`, giá cao hơn SMA20 `0.019843448862473752`, MACD histogram dương `0.07900520028589898` (`technical_snapshot`).
- Tín hiệu chưa đồng nhất: lợi suất kỳ trước âm `-0.06537924616100502`; biên độ giá trong kỳ `0.3517516948514966` (`technical_snapshot`).
- Evidence tin tức chưa đủ mạnh: dữ liệu tin tức bị loại khỏi pack (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình nghiêng về nhóm ứng viên mua dựa trên động lượng kỹ thuật và vị trí giá trên SMA20 (`ml_signal`, `top_drivers`).
- Cơ sở chính: RSI cuối kỳ `59.74769517805113`, MACD histogram dương, lợi suất kỳ hiện tại dương, khối lượng tăng (`rsi_end_q`, `macd_hist_mean_q`, `return_q`, `volume_change_q`).
- Đây là tín hiệu hỗ trợ quyết định, không phải khuyến nghị chắc chắn; `pred_proba_up` là đầu ra mô hình, không phải bảo đảm kết quả.

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ `59.74769517805113` là driver kỹ thuật quan trọng nhất trong mô hình (`top_drivers.feature = rsi_end_q`).
- MACD histogram trung bình dương `0.07900520028589898`, hỗ trợ diễn giải động lượng xu hướng (`macd_hist_mean_q`).
- Giá cao hơn SMA20 `1.9843%`, phản ánh trạng thái kỹ thuật tích cực hơn so với đường trung bình ngắn hạn (`price_vs_sma20`, `sma20_end`).
- Lợi suất kỳ hiện tại đạt `0.1902488062327218`; lợi suất trễ hai kỳ đạt `0.0514461223445098` (`return_q`, `return_2q_ago`).
- Khối lượng tăng `0.17060288468724058`, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ (`volume_change_q`).
- Lợi suất trung bình ngày dương `0.003054851268298556` (`return_mean_daily`).

## 4. Yếu tố cần lưu ý / rủi ro

- Lợi suất kỳ trước âm `-0.06537924616100502`, cho thấy động lượng giữa các kỳ chưa đồng nhất (`return_prev_q`).
- Biên độ giá trong kỳ cao `0.3517516948514966`, phản ánh biến động đáng lưu ý (`price_range_q`, `top_drivers.direction = risk_high_volatility`).
- Tín hiệu phụ thuộc mô hình kỹ thuật `technical_Config_A_from_existing_pipeline`; pack không cung cấp bằng chứng định tính hoặc tin tức bổ sung (`ml_signal.model_name`, `news_evidence_removed_for_ablation`).
- Xếp hạng 5 chỉ phản ánh vị trí trong nhóm tín hiệu của kỳ, không xác nhận chất lượng tuyệt đối (`ml_signal.rank_in_period`, `universe`).
- Không có dữ liệu hậu quyết định trong pack (`guardrails.no_post_decision_data`).

## 5. Trigger theo dõi

- Theo dõi thay đổi nhãn mô hình, `pred_proba_up` và xếp hạng trong kỳ kế tiếp (`ml_signal`).
- Theo dõi RSI cuối kỳ, MACD histogram và vị trí giá so với SMA20; tín hiệu suy yếu khi các driver này giảm so với trạng thái hiện tại (`rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`).
- Theo dõi lợi suất kỳ, lợi suất kỳ trước và lợi suất trễ hai kỳ để kiểm tra động lượng có nhất quán hơn không (`return_q`, `return_prev_q`, `return_2q_ago`).
- Theo dõi biên độ giá và thay đổi khối lượng để đánh giá biến động cùng mức độ quan tâm thị trường (`price_range_q`, `volume_change_q`).
- Cập nhật evidence tin tức nếu có; hiện chưa đủ dữ liệu từ `article_summary`, `key_facts`, `risk_flags`, `event_type` (`news_evidence_removed_for_ablation`).

## 6. Thời điểm review

- Review vào cuối kỳ kế tiếp hoặc theo kỳ lợi suất kế tiếp trong tín hiệu (`holding_horizon = next_quarter_or_period_return_in_signals`).
- Ngày lập card: `2025-03-31` (`decision_date`).
- Không dùng dữ liệu sau ngày quyết định trong đánh giá ban đầu (`guardrails.no_post_decision_data`).

## 7. Kết luận hỗ trợ quyết định

- BSI có tín hiệu kỹ thuật nghiêng tích cực và được mô hình xếp nhóm **“Buy Candidate”** (`ml_signal`, `top_drivers`).
- Động lượng hiện tại, vị trí trên SMA20 và khối lượng hỗ trợ tín hiệu (`return_q`, `price_vs_sma20`, `volume_change_q`).
- Biến động cao, lợi suất kỳ trước âm và thiếu evidence tin tức làm giảm độ đầy đủ của luận điểm (`price_range_q`, `return_prev_q`, `news_evidence_removed_for_ablation`).
- Có thể đưa vào danh sách theo dõi hoặc quy trình đánh giá tiếp; chưa đủ cơ sở để kết luận đầu tư chắc chắn.

## 8. Disclaimer

- Card chỉ hỗ trợ nghiên cứu và quyết định; không phải khuyến nghị đầu tư (`guardrails.not_investment_advice`).
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- `pred_proba_up` là đầu ra mô hình, không bảo đảm kết quả thực tế (`ml_signal.pred_proba_up`).
- Evidence tin tức bị loại khỏi pack; evidence tin tức chưa đủ mạnh (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).
- Card không sử dụng outcome tương lai hoặc dữ liệu hậu quyết định (`guardrails.no_post_decision_data`).

---

## 2025Q2_STB_01

## 1. Tóm tắt tín hiệu

- STB có tín hiệu mô hình **“Buy Candidate”**, nhãn dự báo `1`, xác suất mô hình cho hướng tăng `0.9987508337159348`, xếp hạng `1` trong kỳ 2025Q2. [ml_signal.pred_label; ml_signal.pred_proba_up; ml_signal.signal_class; ml_signal.rank_in_period]
- Nền tảng tín hiệu chủ yếu từ dữ liệu kỹ thuật. [card_input_variant; model_name]
- Biên độ giá trong kỳ là yếu tố rủi ro biến động. [top_drivers.price_range_q; top_drivers.direction = risk_high_volatility]
- Evidence tin tức chưa đủ mạnh: news evidence bị loại khỏi pack. [data_quality_flags.news_evidence_removed_for_ablation; guardrails.news_evidence_excluded]

## 2. Luận điểm đầu tư chính

- Tín hiệu kỹ thuật nghiêng tích cực, dựa trên nhãn mô hình, xác suất mô hình cao và xếp hạng đầu kỳ. [ml_signal.signal_class; ml_signal.pred_proba_up; ml_signal.rank_in_period]
- Động lượng được mô hình hỗ trợ qua RSI cuối kỳ, MACD histogram, vị trí giá so với SMA20 và khối lượng. [technical_snapshot.rsi_end_q; technical_snapshot.macd_hist_mean_q; technical_snapshot.price_vs_sma20; technical_snapshot.volume_change_q]
- STB phù hợp đưa vào danh sách theo dõi hoặc đánh giá thêm; chưa đủ cơ sở cho khuyến nghị chắc chắn do evidence chỉ gồm tín hiệu ML/kỹ thuật. [card_input_variant; data_quality_flags.news_evidence_removed_for_ablation]

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ `69.69503512517338` là driver kỹ thuật quan trọng nhất, theo hướng hỗ trợ tín hiệu tăng. [top_drivers.feature = rsi_end_q; top_drivers.direction = supports_up_signal]
- MACD histogram trung bình kỳ `0.09134528643173032` hỗ trợ đánh giá động lượng xu hướng. [technical_snapshot.macd_hist_mean_q; top_drivers.feature = macd_hist_mean_q]
- Giá nằm cao hơn SMA20 khoảng `0.043167476405874566`, hỗ trợ trạng thái xu hướng ngắn hạn. [technical_snapshot.price_vs_sma20; top_drivers.feature = price_vs_sma20]
- Khối lượng thay đổi `0.7803498501283113`, là yếu tố được mô hình dùng để phản ánh mức độ quan tâm thị trường. [technical_snapshot.volume_change_q; top_drivers.feature = volume_change_q]
- Tín hiệu tổng hợp đạt xếp hạng `1` trong kỳ. [ml_signal.rank_in_period]

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ `0.3745912752213095` được mô hình gắn với rủi ro biến động cao. [technical_snapshot.price_range_q; top_drivers.direction = risk_high_volatility]
- Tín hiệu phụ thuộc mô hình kỹ thuật `technical_Config_A_from_existing_pipeline`, không có evidence định tính từ tin tức trong card. [ml_signal.model_name; card_input_variant; data_quality_flags.news_evidence_removed_for_ablation]
- Xác suất mô hình không phải bảo đảm kết quả thực tế. [ml_signal.pred_proba_up; guardrails.not_investment_advice]
- Evidence tin tức chưa đủ mạnh để xác nhận hoặc phản biện luận điểm kỹ thuật. [data_quality_flags.news_evidence_removed_for_ablation; guardrails.news_evidence_excluded]

## 5. Trigger theo dõi

- Tín hiệu mô hình đổi khỏi `Buy Candidate` hoặc nhãn `pred_label` thay đổi. [ml_signal.signal_class; ml_signal.pred_label]
- Xác suất mô hình thay đổi đáng kể so với `0.9987508337159348`. [ml_signal.pred_proba_up]
- RSI, MACD histogram hoặc vị trí giá so với SMA20 suy yếu so với các mức kỳ hiện tại. [technical_snapshot.rsi_end_q; technical_snapshot.macd_hist_mean_q; technical_snapshot.price_vs_sma20]
- Biên độ giá tăng, vì đây là driver rủi ro biến động. [technical_snapshot.price_range_q; top_drivers.direction = risk_high_volatility]
- Cập nhật thêm evidence tin tức có `article_summary`, `key_facts`, `risk_flags`, `event_type`. [data_quality_flags.news_evidence_removed_for_ablation; yêu cầu ưu tiên trường tin tức]

## 6. Thời điểm review

- Review vào cuối quý kế tiếp hoặc kỳ tín hiệu kế tiếp, theo `holding_horizon`. [holding_horizon]
- Review sớm khi trigger mô hình, động lượng hoặc biến động thay đổi. [ml_signal.signal_class; technical_snapshot; top_drivers]

## 7. Kết luận hỗ trợ quyết định

- STB hiện có tín hiệu kỹ thuật tích cực và đứng đầu nhóm trong kỳ theo mô hình. [ml_signal.signal_class; ml_signal.pred_proba_up; ml_signal.rank_in_period]
- Có thể xem STB là ứng viên cần theo dõi hoặc phân tích bổ sung.
- Chưa nên kết luận chắc chắn về quyết định đầu tư vì evidence tin tức bị loại và rủi ro biến động vẫn hiện hữu. [data_quality_flags.news_evidence_removed_for_ablation; top_drivers.price_range_q]
- Quyết định tiếp theo nên phụ thuộc review tín hiệu mô hình, động lượng, SMA20, khối lượng và evidence tin tức bổ sung. [technical_snapshot; ml_signal; data_quality_flags]

## 8. Disclaimer

- Card phục vụ hỗ trợ quyết định trong nghiên cứu học thuật, không phải tư vấn đầu tư. [guardrails.not_investment_advice]
- Tín hiệu mô hình không bảo đảm kết quả.
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Card không sử dụng dữ liệu sau ngày quyết định `2025-06-30`. [decision_date; guardrails.no_post_decision_data]

---

## 2025Q2_DXG_02

## 1. Tóm tắt tín hiệu

- DXG được mô hình gắn nhãn **“Buy Candidate”**, xác suất tín hiệu tăng `0.9984698500767306`, xếp hạng `2` trong kỳ 2025Q2. `[ml_signal.pred_label, ml_signal.pred_proba_up, ml_signal.signal_class, ml_signal.rank_in_period]`
- Động lượng kỹ thuật nghiêng tích cực: lợi suất kỳ hiện tại `0.24747`, kỳ trước `0.04960`, MACD histogram trung bình `0.01884`, giá cao hơn SMA20 `4.59%`. `[technical_snapshot.return_q, return_prev_q, macd_hist_mean_q, price_vs_sma20]`
- RSI cuối kỳ `75.33`, cho thấy tín hiệu tăng đi kèm trạng thái quá mua theo driver mô hình. `[top_drivers: rsi_end_q]`
- Biên độ giá trong kỳ `0.47297`, phản ánh rủi ro biến động cao. `[technical_snapshot.price_range_q]`
- Evidence tin tức chưa đủ mạnh: dữ liệu tin tức bị loại khỏi pack. `[data_quality_flags.news_evidence_removed_for_ablation, guardrails.news_evidence_excluded]`

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình nghiêng tích cực nhờ động lượng giá, MACD, vị trí giá trên SMA20 và thay đổi khối lượng. `[ml_signal, top_drivers, technical_snapshot]`
- Tín hiệu cần đánh giá thận trọng vì RSI cao và biên độ giá lớn. `[top_drivers.rsi_end_q, top_drivers.price_range_q]`
- DXG phù hợp vai trò **ứng viên cần theo dõi**, không đủ cơ sở để xem là khuyến nghị chắc chắn. Evidence định tính từ tin tức chưa đủ mạnh. `[ml_signal.signal_class, data_quality_flags.news_evidence_removed_for_ablation]`

## 3. Yếu tố hỗ trợ

- Lợi suất trong kỳ đạt `0.24747`, hỗ trợ tín hiệu động lượng gần nhất. `[technical_snapshot.return_q]`
- Lợi suất kỳ trước đạt `0.04960`, bổ sung tín hiệu động lượng. `[technical_snapshot.return_prev_q]`
- MACD histogram trung bình dương `0.01884`, hỗ trợ xu hướng tăng trong mô hình. `[technical_snapshot.macd_hist_mean_q]`
- Giá cuối kỳ cao hơn SMA20 `4.59%`, phản ánh trạng thái trên đường trung bình ngắn hạn. `[technical_snapshot.price_vs_sma20, technical_snapshot.sma20_end]`
- Khối lượng tăng `49.00%`, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ. `[technical_snapshot.volume_change_q]`
- Lợi suất trung bình ngày `0.00401`, hỗ trợ xu hướng ngắn trong kỳ. `[technical_snapshot.return_mean_daily]`

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `75.33`; driver mô hình đánh dấu **positive_but_overbought_risk**, nên tín hiệu tăng đi kèm rủi ro quá mua. `[top_drivers.rsi_end_q, technical_snapshot.rsi_end_q]`
- Biên độ giá trong kỳ `0.47297`; driver mô hình đánh dấu **risk_high_volatility**. `[top_drivers.price_range_q, technical_snapshot.price_range_q]`
- Lợi suất trễ hai kỳ âm `-0.06578`, là driver yếu hoặc tiêu cực trong mô hình. `[top_drivers.return_2q_ago, technical_snapshot.return_2q_ago]`
- Evidence tin tức chưa đủ mạnh để kiểm chứng luận điểm kỹ thuật bằng thông tin định tính. `[data_quality_flags.news_evidence_removed_for_ablation, guardrails.news_evidence_excluded]`
- Xác suất mô hình cao không loại bỏ rủi ro quá mua, biến động hoặc sai số mô hình. `[ml_signal.pred_proba_up, top_drivers]`

## 5. Trigger theo dõi

- RSI: theo dõi việc duy trì hoặc suy giảm từ mức `75.33`; evidence chưa cung cấp ngưỡng hành động riêng. `[technical_snapshot.rsi_end_q]`
- MACD histogram: theo dõi dấu hiệu duy trì hoặc suy yếu từ mức trung bình `0.01884`. `[technical_snapshot.macd_hist_mean_q]`
- Giá so với SMA20: theo dõi việc duy trì trên hoặc chuyển xuống dưới SMA20; mức hiện tại cao hơn `4.59%`. `[technical_snapshot.price_vs_sma20, technical_snapshot.sma20_end]`
- Khối lượng: theo dõi việc duy trì hoặc đảo chiều sau mức tăng `49.00%`. `[technical_snapshot.volume_change_q]`
- Biên độ giá: theo dõi biến động sau mức `0.47297`. `[technical_snapshot.price_range_q]`
- Tin tức: cần bổ sung evidence định tính trước khi nâng mức độ tin cậy. `[data_quality_flags.news_evidence_removed_for_ablation]`

## 6. Thời điểm review

- Review vào **next quarter or period return in signals**, theo holding horizon của evidence pack. `[holding_horizon]`
- Decision date: `2025-06-30`. `[decision_date]`
- Evidence không cung cấp ngày review cụ thể hơn. `[holding_horizon, decision_date]`

## 7. Kết luận hỗ trợ quyết định

- DXG có tín hiệu mô hình tích cực và thuộc nhóm **Buy Candidate**, được hỗ trợ bởi động lượng, giá trên SMA20 và khối lượng tăng. `[ml_signal, technical_snapshot, top_drivers]`
- RSI quá cao, biến động lớn và lợi suất trễ hai kỳ âm làm tăng nhu cầu kiểm chứng. `[technical_snapshot.rsi_end_q, price_range_q, return_2q_ago]`
- Cách dùng thận trọng: xem DXG là **ứng viên cần theo dõi và review lại**, không xem tín hiệu này là khuyến nghị mua chắc chắn. Evidence tin tức chưa đủ mạnh. `[ml_signal.signal_class, data_quality_flags.news_evidence_removed_for_ablation]`

## 8. Disclaimer

- Decision card chỉ dùng thông tin trong evidence pack, phục vụ hỗ trợ quyết định học thuật.
- Không phải tư vấn đầu tư.
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Tín hiệu mô hình không loại bỏ rủi ro quá mua, biến động, dữ liệu thiếu hoặc sai số mô hình.

---

## 2025Q2_VBB_03

## 1. Tóm tắt tín hiệu

- VBB nhận nhãn **“Buy Candidate”** từ mô hình kỹ thuật. `ml_signal.signal_class`
- Xác suất tăng do mô hình gán: **0.9982**; xếp hạng **3** trong kỳ. `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`
- Tín hiệu dựa trên dữ liệu kỹ thuật; tin tức bị loại khỏi pack. `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`
- **Evidence tin tức chưa đủ mạnh.**

## 2. Luận điểm đầu tư chính

- Động lượng kỹ thuật đang hỗ trợ tín hiệu tăng: RSI cuối kỳ, MACD histogram, vị trí giá so với SMA20 và các mức lợi suất đều được mô hình đánh dấu hỗ trợ. `top_drivers`
- Mô hình xếp VBB vào nhóm ứng viên cần xem xét, không phải khuyến nghị chắc chắn. `ml_signal.signal_class`, `ml_signal.pred_label`
- Tín hiệu cần đánh giá cùng rủi ro biến động giá trong kỳ. `top_drivers[price_range_q]`

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ **65.4593**, driver kỹ thuật quan trọng nhất của mô hình. `technical_snapshot.rsi_end_q`, `top_drivers[rsi_end_q]`
- MACD histogram trung bình **0.00514**, phản ánh động lượng xu hướng theo mô hình. `technical_snapshot.macd_hist_mean_q`, `top_drivers[macd_hist_mean_q]`
- Giá nằm cao hơn SMA20 khoảng **5.12%**. `technical_snapshot.price_vs_sma20`, `top_drivers[price_vs_sma20]`
- Lợi suất trong kỳ **18.49%**, kỳ trước **8.76%**, và hai kỳ trước **12.82%**; các biến này hỗ trợ tín hiệu động lượng. `technical_snapshot.return_q`, `technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`
- Thay đổi khối lượng **1.2072**, được mô hình xem là yếu tố hỗ trợ. `technical_snapshot.volume_change_q`, `top_drivers[volume_change_q]`
- Lợi suất trung bình ngày **0.3309%**, hỗ trợ xu hướng ngắn trong kỳ. `technical_snapshot.return_mean_daily`, `top_drivers[return_mean_daily]`

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ **0.3689**, được mô hình gắn với rủi ro biến động cao. `technical_snapshot.price_range_q`, `top_drivers[price_range_q]`
- Tín hiệu phụ thuộc pipeline kỹ thuật `technical_Config_A_from_existing_pipeline`; không có bằng chứng tin tức đi kèm. `ml_signal.model_name`, `data_quality_flags.news_evidence_removed_for_ablation`
- Xác suất mô hình không đồng nghĩa kết quả thực tế. Pack không cung cấp kiểm định độ tin cậy hoặc điều kiện thất bại của tín hiệu. `ml_signal.pred_proba_up`, `data_quality_flags`
- Không có dữ liệu ngoài các biến kỹ thuật trong pack để đánh giá yếu tố định tính. `guardrails.news_evidence_excluded`

## 5. Trigger theo dõi

- Theo dõi thay đổi nhãn và xác suất mô hình. `ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.signal_class`
- Theo dõi RSI cuối kỳ và MACD histogram. `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`
- Theo dõi vị trí giá so với SMA20 và SMA20 cuối kỳ. `technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`
- Theo dõi lợi suất kỳ hiện tại, kỳ trước, hai kỳ trước và lợi suất trung bình ngày. `technical_snapshot.return_q`, `technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`, `technical_snapshot.return_mean_daily`
- Theo dõi thay đổi khối lượng và biên độ giá. `technical_snapshot.volume_change_q`, `technical_snapshot.price_range_q`
- Pack không cung cấp ngưỡng trigger cụ thể; không tự đặt ngưỡng.

## 6. Thời điểm review

- Review vào **quý tiếp theo hoặc kỳ có period return trong signals**, theo cấu hình `holding_horizon`.
- Mốc quyết định hiện tại: **2025-06-30**. `decision_date`
- Dùng dữ liệu cập nhật cùng pipeline để kiểm tra lại tín hiệu. `ml_signal.model_name`

## 7. Kết luận hỗ trợ quyết định

- VBB có tín hiệu kỹ thuật mạnh và được xếp **“Buy Candidate”**. `ml_signal.signal_class`, `ml_signal.pred_proba_up`
- Có cơ sở theo dõi tiếp nhờ động lượng, vị trí trên SMA20 và khối lượng. `top_drivers`
- Biến động giá là rủi ro chính; thiếu evidence tin tức làm giảm độ đầy đủ của đánh giá. `top_drivers[price_range_q]`, `data_quality_flags.news_evidence_removed_for_ablation`
- Phù hợp làm đầu vào cho bước review tiếp theo, không đủ cơ sở để kết luận đầu tư chắc chắn.

## 8. Disclaimer

- Card chỉ dùng thông tin trong evidence pack, chủ yếu từ mô hình kỹ thuật.
- Không phải tư vấn đầu tư. Không bảo đảm lợi nhuận hay kết quả.
- Không sử dụng dữ liệu sau ngày quyết định. `guardrails.no_post_decision_data`
- Evidence tin tức bị loại khỏi pack; không giả định nội dung toàn văn từ metadata.

---

## 2025Q2_MSN_04

## 1. Tóm tắt tín hiệu

- MSN có tín hiệu mô hình **“Buy Candidate”**, `pred_label = 1`, `pred_proba_up = 0.9972110602207352`, xếp hạng 4 trong kỳ 2025Q2. `[ml_signal]`
- Động lượng hiện tại tích cực: lợi suất kỳ này `0.16012084592145007`, MACD histogram trung bình `0.1094344612958833`, giá cao hơn SMA20 `13.49%`. `[technical_snapshot]`
- Rủi ro quá mua cao: RSI cuối kỳ `84.99941401293337`. Biên độ giá kỳ `0.4292316880014541` cho thấy biến động đáng lưu ý. `[technical_snapshot.rsi_end_q]`, `[technical_snapshot.price_range_q]`
- Tin tức bị loại khỏi pack. **Evidence tin tức chưa đủ mạnh.** `[data_quality_flags.news_evidence_removed_for_ablation]`

## 2. Luận điểm đầu tư chính

- Tín hiệu định lượng nghiêng tích cực nhờ mô hình gắn nhãn “Buy Candidate”, lợi suất kỳ hiện tại dương, MACD dương, giá nằm trên SMA20 và khối lượng tăng. `[ml_signal]`, `[technical_snapshot.return_q]`, `[technical_snapshot.macd_hist_mean_q]`, `[technical_snapshot.price_vs_sma20]`, `[technical_snapshot.volume_change_q]`
- Luận điểm bị giảm độ chắc do RSI ở vùng quá mua, biến động giá cao và động lượng lịch sử không đồng nhất. `[technical_snapshot.rsi_end_q]`, `[technical_snapshot.price_range_q]`, `[technical_snapshot.return_prev_q]`, `[technical_snapshot.return_2q_ago]`
- Phù hợp xem như **tín hiệu cần theo dõi**, không phải khuyến nghị đầu tư chắc chắn.

## 3. Yếu tố hỗ trợ

- Lợi suất kỳ hiện tại đạt `0.16012084592145007`, hỗ trợ xu hướng gần nhất. `[technical_snapshot.return_q]`
- MACD histogram trung bình đạt `0.1094344612958833`, hỗ trợ động lượng tăng. `[technical_snapshot.macd_hist_mean_q]`
- Giá cao hơn SMA20 `13.49%`; SMA20 cuối kỳ là `67.67`. `[technical_snapshot.price_vs_sma20]`, `[technical_snapshot.sma20_end]`
- Khối lượng tăng `51.47%`, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ. `[technical_snapshot.volume_change_q]`
- Lợi suất trung bình ngày dương `0.002649441012009954`. `[technical_snapshot.return_mean_daily]`
- Mô hình xếp MSN hạng 4 trong kỳ và gắn nhãn “Buy Candidate”. `[ml_signal.rank_in_period]`, `[ml_signal.signal_class]`

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `84.99941401293337`; mô hình đánh dấu driver này là **“positive_but_overbought_risk”**. Rủi ro điều chỉnh kỹ thuật cần được theo dõi. `[top_drivers.feature = rsi_end_q]`, `[technical_snapshot.rsi_end_q]`
- Biên độ giá kỳ `0.4292316880014541`; mô hình đánh dấu rủi ro biến động cao. `[top_drivers.feature = price_range_q]`, `[technical_snapshot.price_range_q]`
- Lợi suất kỳ trước `-0.05649717514124294` và lợi suất hai kỳ trước `-0.08616187989556129`, cho thấy động lượng lịch sử không đồng nhất. `[technical_snapshot.return_prev_q]`, `[technical_snapshot.return_2q_ago]`
- Tín hiệu mô hình không đồng nghĩa kết quả thực tế; `pred_proba_up` chỉ là đầu ra mô hình. `[ml_signal.pred_proba_up]`
- Không có evidence định tính từ tin tức trong pack. **Evidence tin tức chưa đủ mạnh.** `[data_quality_flags.news_evidence_removed_for_ablation]`

## 5. Trigger theo dõi

- RSI giảm khỏi mức cuối kỳ `84.99941401293337` hoặc tiếp tục duy trì vùng cao. `[technical_snapshot.rsi_end_q]`
- MACD histogram duy trì hoặc suy yếu so với `0.1094344612958833`. `[technical_snapshot.macd_hist_mean_q]`
- Quan hệ giá với SMA20 thay đổi so với mức `+13.49%`; SMA20 tham chiếu `67.67`. `[technical_snapshot.price_vs_sma20]`, `[technical_snapshot.sma20_end]`
- Khối lượng thay đổi so với mức tăng `51.47%`. `[technical_snapshot.volume_change_q]`
- Biên độ giá tăng so với `0.4292316880014541`. `[technical_snapshot.price_range_q]`
- Theo dõi thay đổi của `signal_class`, `pred_label`, `pred_proba_up` và `rank_in_period` ở kỳ tín hiệu kế tiếp. `[ml_signal]`

## 6. Thời điểm review

- Ngày lập card: `2025-06-30`. `[decision_date]`
- Review vào **kỳ kế tiếp hoặc period return kế tiếp trong signals**, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. `[holding_horizon]`
- Review sớm nếu RSI, MACD, quan hệ giá/SMA20, khối lượng hoặc nhãn mô hình thay đổi đáng kể. `[technical_snapshot]`, `[ml_signal]`

## 7. Kết luận hỗ trợ quyết định

- MSN có tín hiệu định lượng tích cực, nhưng trạng thái quá mua và biến động cao làm tăng nhu cầu kiểm soát rủi ro. `[ml_signal]`, `[technical_snapshot.rsi_end_q]`, `[technical_snapshot.price_range_q]`
- Có thể đưa MSN vào danh sách theo dõi hoặc quy trình đánh giá tiếp theo; chưa đủ cơ sở để kết luận hành động đầu tư chắc chắn.
- Cần review tín hiệu kỹ thuật và đầu ra mô hình ở kỳ kế tiếp. `[holding_horizon]`, `[ml_signal]`

## 8. Disclaimer

- Card chỉ hỗ trợ quyết định nghiên cứu, không phải tư vấn đầu tư.
- Không có dự báo giá tuyệt đối, cam kết lợi nhuận hoặc kết luận chắc chắn về kết quả.
- Phân tích chỉ dùng evidence trong pack; evidence tin tức đã bị loại khỏi pack.

---

## 2025Q2_VND_05

## 1. Tóm tắt tín hiệu

- Mô hình kỹ thuật gắn VND nhãn `Buy Candidate`, `pred_label = 1`, `pred_proba_up = 0.9971`, xếp hạng 5 trong kỳ 2025Q2 (`ml_signal`).
- Tín hiệu dựa trên dữ liệu kỹ thuật; tin tức bị loại khỏi pack (`news_evidence_removed_for_ablation = true`, `news_evidence_excluded = true`).
- Tín hiệu tích cực nhưng chưa đồng nhất: RSI, giá trên SMA20, động lượng gần nhất và khối lượng hỗ trợ; MACD histogram và lợi suất trễ hai kỳ yếu hoặc âm (`top_drivers`).

## 2. Luận điểm đầu tư chính

VND là ứng viên cần theo dõi trong nhóm tín hiệu kỹ thuật, không phải khuyến nghị chắc chắn. Cơ sở chính:

- `rsi_end_q = 65.8972` là driver hỗ trợ tăng quan trọng nhất (`top_drivers`).
- `price_vs_sma20 = 0.0524`, cho thấy giá nằm trên SMA20 khoảng 5,24% (`price_vs_sma20`).
- Động lượng gần nhất tích cực qua `return_q = 0.1523`, `return_prev_q = 0.2148` và `return_mean_daily = 0.00285` (`technical_snapshot`).
- Tín hiệu bị giảm chất lượng bởi `macd_hist_mean_q = -0.01105` và `return_2q_ago = -0.1848` (`top_drivers`).

## 3. Yếu tố hỗ trợ

- Mô hình xếp VND vào nhóm `Buy Candidate`, hạng 5 trong kỳ (`ml_signal.rank_in_period`, `ml_signal.signal_class`).
- RSI cuối kỳ hỗ trợ tín hiệu theo mô hình: `rsi_end_q = 65.8972` (`top_drivers`, `technical_snapshot`).
- Giá cao hơn SMA20: `price_vs_sma20 = 0.0524`; SMA20 cuối kỳ là `15.888` (`price_vs_sma20`, `sma20_end`).
- Động lượng hai kỳ gần nhất dương: `return_q = 0.1523`, `return_prev_q = 0.2148` (`return_q`, `return_prev_q`).
- Khối lượng tăng trong kỳ: `volume_change_q = 0.3749` (`volume_change_q`).

## 4. Yếu tố cần lưu ý / rủi ro

- MACD histogram trung bình âm: `macd_hist_mean_q = -0.01105`; động lượng xu hướng chưa đồng thuận (`top_drivers`).
- Lợi suất trễ hai kỳ âm: `return_2q_ago = -0.1848`; quán tính lịch sử còn yếu (`top_drivers`).
- Biên độ giá trong kỳ ở mức `price_range_q = 0.3415`, cho thấy cần theo dõi biến động (`price_range_q`).
- Tín hiệu chỉ dựa trên mô hình kỹ thuật; tin tức bị loại khỏi evidence pack (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).
- Evidence tin tức chưa đủ mạnh: pack không cung cấp `article_summary`, `key_facts`, `risk_flags` hoặc `event_type`.

## 5. Trigger theo dõi

- Cập nhật `ml_signal.pred_proba_up` và `ml_signal.signal_class`; xem xét lại khi xác suất mô hình hoặc nhãn tín hiệu thay đổi.
- Theo dõi `macd_hist_mean_q`; MACD tiếp tục âm hoặc yếu hơn là tín hiệu cần thận trọng.
- Theo dõi `price_vs_sma20`; mức này giảm về gần hoặc dưới 0 làm suy yếu cấu trúc kỹ thuật.
- Theo dõi `volume_change_q`; khối lượng đảo chiều hoặc giảm mạnh làm giảm xác nhận từ dòng tiền.
- Theo dõi `rsi_end_q`, `return_q`, `return_prev_q` và `price_range_q` khi có kỳ dữ liệu mới.

## 6. Thời điểm review

- Review tại quý hoặc kỳ kế tiếp khi có tín hiệu mới, theo `holding_horizon = next_quarter_or_period_return_in_signals`.
- Mốc lập card: `decision_date = 2025-06-30`.
- Card không sử dụng dữ liệu sau ngày quyết định (`guardrails.no_post_decision_data = true`).

## 7. Kết luận hỗ trợ quyết định

VND có tín hiệu kỹ thuật nghiêng tích cực, được hỗ trợ bởi `pred_proba_up = 0.9971`, giá trên SMA20, động lượng gần nhất và khối lượng tăng (`ml_signal`, `price_vs_sma20`, `return_q`, `return_prev_q`, `volume_change_q`). Tuy vậy, MACD histogram âm, dữ liệu trễ hai kỳ âm và thiếu evidence tin tức làm cơ sở chưa đồng nhất (`macd_hist_mean_q`, `return_2q_ago`, `news_evidence_removed_for_ablation`).

Phù hợp đưa vào danh sách theo dõi hoặc nghiên cứu thêm. Cần review khi có tín hiệu kỹ thuật mới; chưa đủ cơ sở cho quyết định đầu tư chắc chắn.

## 8. Disclaimer

Card chỉ hỗ trợ phân tích học thuật, không phải tư vấn đầu tư (`guardrails.not_investment_advice = true`). Tín hiệu mô hình không bảo đảm kết quả. Không sử dụng dự báo giá tuyệt đối, dữ liệu sau ngày quyết định hoặc outcome tương lai.

---

## 2025Q3_LPB_01

## 1. Tóm tắt tín hiệu

- LPB, kỳ 2025Q3; ngày quyết định 2025-09-30.
- Mô hình `technical_Config_A_from_existing_pipeline`: `pred_label = 1`, `pred_proba_up = 0.9985`, xếp hạng 1, phân loại `Buy Candidate` (`ml_signal`).
- Tín hiệu nghiêng tăng, nhưng RSI cao và biên độ giá lớn tạo rủi ro quá mua, biến động (`top_drivers.rsi_end_q`, `top_drivers.price_range_q`).
- Tin tức không có trong pack; **evidence tin tức chưa đủ mạnh** (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).

## 2. Luận điểm đầu tư chính

- LPB có tín hiệu kỹ thuật tích cực và xác suất mô hình rất cao, được hỗ trợ bởi động lượng giá, MACD, vị trí giá trên SMA20 và thay đổi khối lượng (`ml_signal`, `technical_snapshot`, `top_drivers`).
- Tín hiệu cần được xem như ứng viên để theo dõi, không phải xác nhận chắc chắn; RSI cuối kỳ 73.8891 cho thấy rủi ro quá mua (`technical_snapshot.rsi_end_q`, `top_drivers.rsi_end_q`).

## 3. Yếu tố hỗ trợ

- Lợi suất kỳ hiện tại: `return_q = 0.5398` (`technical_snapshot.return_q`).
- Lợi suất kỳ trước và hai kỳ trước đều dương: `return_prev_q = 0.0367`, `return_2q_ago = 0.0640` (`technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`).
- MACD histogram trung bình dương: `macd_hist_mean_q = 0.1005` (`technical_snapshot.macd_hist_mean_q`, `top_drivers.macd_hist_mean_q`).
- Giá cao hơn SMA20: `price_vs_sma20 = 0.0875`; SMA20 cuối kỳ là `43.0160` (`technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`).
- Khối lượng thay đổi dương: `volume_change_q = 0.3155` (`technical_snapshot.volume_change_q`).
- Xếp hạng mô hình đứng đầu kỳ: `rank_in_period = 1` (`ml_signal.rank_in_period`).

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `73.8891`; driver được mô hình gắn nhãn `positive_but_overbought_risk` (`technical_snapshot.rsi_end_q`, `top_drivers.rsi_end_q`).
- Biên độ giá trong kỳ `price_range_q = 0.4440`, phản ánh biến động cao (`technical_snapshot.price_range_q`, `top_drivers.price_range_q`).
- Tín hiệu phụ thuộc mô hình kỹ thuật; pack không cung cấp bằng chứng định tính từ tin tức (`ml_signal.model_name`, `data_quality_flags.news_evidence_removed_for_ablation`).
- Không có article summary, key facts hoặc risk flags trong evidence pack; **evidence tin tức chưa đủ mạnh**.

## 5. Trigger theo dõi

- RSI cuối kỳ giảm hay tiếp tục ở vùng cao (`technical_snapshot.rsi_end_q`).
- MACD histogram trung bình duy trì hay suy yếu (`technical_snapshot.macd_hist_mean_q`).
- Giá duy trì hay mất vị trí trên SMA20 (`technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`).
- Khối lượng tiếp tục tăng hay đảo chiều (`technical_snapshot.volume_change_q`).
- Biên độ giá tiếp tục lớn hay thu hẹp (`technical_snapshot.price_range_q`).
- Mô hình còn giữ nhãn `Buy Candidate` và vị trí xếp hạng cao hay không (`ml_signal.signal_class`, `ml_signal.rank_in_period`).

## 6. Thời điểm review

- Review vào cuối quý hoặc kỳ tín hiệu kế tiếp, phù hợp với `holding_horizon = next_quarter_or_period_return_in_signals`.
- Review sớm nếu RSI, MACD, vị trí giá so với SMA20 hoặc biến động thay đổi rõ (`technical_snapshot`, `top_drivers`).

## 7. Kết luận hỗ trợ quyết định

- Dữ liệu hiện tại ủng hộ việc đưa LPB vào danh sách theo dõi ưu tiên nhờ tín hiệu mô hình mạnh, động lượng dương và xếp hạng 1 (`ml_signal`, `technical_snapshot`).
- Không nên xem tín hiệu này là quyết định mua chắc chắn vì RSI cao, biến động lớn và thiếu evidence tin tức (`technical_snapshot.rsi_end_q`, `technical_snapshot.price_range_q`, `data_quality_flags.news_evidence_removed_for_ablation`).
- Bước tiếp theo: theo dõi các trigger kỹ thuật trước kỳ review kế tiếp.

## 8. Disclaimer

- Decision card chỉ hỗ trợ phân tích học thuật từ evidence pack tại ngày 2025-09-30.
- Không phải khuyến nghị đầu tư, không cam kết lợi nhuận, không dự báo giá tuyệt đối.
- Không sử dụng dữ liệu sau ngày quyết định hoặc outcome tương lai.

---

## 2025Q3_VIC_02

## 1. Tóm tắt tín hiệu

- VIC, ngày quyết định `2025-09-30`.
- Mô hình `technical_Config_A_from_existing_pipeline` gán nhãn `Buy Candidate`, xác suất lớp tăng `0.9970068380521899`, xếp hạng `2` trong kỳ. [ml_signal]
- Tín hiệu kỹ thuật tích cực nhưng có rủi ro quá mua, thanh khoản suy yếu và biến động cao. [top_drivers], [technical_snapshot]
- Evidence tin tức chưa đủ mạnh: `news_evidence_removed_for_ablation=true`, `news_evidence_excluded=true`. [data_quality_flags], [guardrails]

## 2. Luận điểm đầu tư chính

- VIC có tín hiệu mô hình nghiêng tích cực, dựa trên MACD dương, giá cao hơn SMA20 và nhóm biến động lượng lịch sử. [ml_signal.pred_label], [ml_signal.pred_proba_up], [technical_snapshot.macd_hist_mean_q], [technical_snapshot.price_vs_sma20]
- Độ tin cậy tín hiệu cần giảm trừ vì RSI cuối kỳ ở mức cao, khối lượng giảm và biên độ giá lớn. [technical_snapshot.rsi_end_q], [technical_snapshot.volume_change_q], [technical_snapshot.price_range_q]
- Nhãn `Buy Candidate` chỉ phản ánh đầu ra mô hình, không đủ làm kết luận mua chắc chắn. [ml_signal.signal_class], [guardrails.not_investment_advice]

## 3. Yếu tố hỗ trợ

- MACD histogram trung bình kỳ dương `0.20040437309325893`, hỗ trợ tín hiệu động lượng. [technical_snapshot.macd_hist_mean_q]
- Giá cao hơn SMA20 với `price_vs_sma20 = 0.22107026913812958`; SMA20 cuối kỳ là `71.6175`. [technical_snapshot.price_vs_sma20], [technical_snapshot.sma20_end]
- Các biến động lượng trong mô hình mang dấu hỗ trợ: `return_2q_ago = 0.4306857424765664`, `return_prev_q = 0.6013400335008373`, `return_q = 0.829497907949791`, `return_mean_daily = 0.009933861383748185`. [technical_snapshot]
- Mô hình xếp VIC hạng `2` trong kỳ. [ml_signal.rank_in_period]

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `83.94257466926713`; driver được mô tả là tích cực nhưng có rủi ro quá mua. [technical_snapshot.rsi_end_q], [top_drivers[0]]
- Khối lượng thay đổi `-0.4838746133712379`, là driver yếu hoặc tiêu cực. [technical_snapshot.volume_change_q], [top_drivers[6]]
- Biên độ giá kỳ `0.748385784737404`, phản ánh biến động/rủi ro cao. [technical_snapshot.price_range_q], [top_drivers[8]]
- Evidence định tính từ tin tức bị loại khỏi pack; evidence tin tức chưa đủ mạnh để xác nhận hoặc phản biện tín hiệu kỹ thuật. [data_quality_flags.news_evidence_removed_for_ablation], [guardrails.news_evidence_excluded]
- Xác suất mô hình cao không loại bỏ rủi ro mô hình hoặc rủi ro thị trường. [ml_signal.pred_proba_up], [ml_signal.model_name]

## 5. Trigger theo dõi

- MACD histogram trung bình kỳ tiếp tục dương hoặc suy yếu. [technical_snapshot.macd_hist_mean_q]
- Giá duy trì trên hoặc giảm xuống dưới SMA20. [technical_snapshot.price_vs_sma20], [technical_snapshot.sma20_end]
- RSI duy trì quanh mức cao `83.94257466926713` hoặc hạ nhiệt. [technical_snapshot.rsi_end_q]
- `volume_change_q` tiếp tục âm hoặc cải thiện. [technical_snapshot.volume_change_q]
- Biên độ giá tiếp tục lớn. [technical_snapshot.price_range_q]
- Xuất hiện evidence tin tức có `article_summary`, `key_facts`, `risk_flags`, `event_type`; hiện chưa có trong pack. [data_quality_flags], [guardrails]

## 6. Thời điểm review

- Ngày tham chiếu: `2025-09-30`. [decision_date]
- Review theo horizon `next_quarter_or_period_return_in_signals`. [holding_horizon]
- Evidence pack không cung cấp ngày lịch cụ thể cho kỳ review tiếp theo.

## 7. Kết luận hỗ trợ quyết định

- VIC thuộc nhóm cần theo dõi tích cực theo tín hiệu mô hình: nhãn `Buy Candidate`, xác suất mô hình cao, hạng `2`. [ml_signal]
- Tín hiệu chưa đủ để đưa ra khuyến nghị mua chắc chắn vì RSI cao, khối lượng giảm, biến động lớn và thiếu evidence tin tức. [technical_snapshot], [data_quality_flags], [guardrails]
- Bước tiếp theo: review MACD, vị trí giá so với SMA20, RSI, khối lượng và evidence tin tức tại kỳ kế tiếp. [technical_snapshot], [holding_horizon]

## 8. Disclaimer

- Card chỉ hỗ trợ phân tích quyết định, không phải khuyến nghị đầu tư. [guardrails.not_investment_advice]
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Phân tích chỉ dùng evidence pack tại ngày `2025-09-30`; không sử dụng dữ liệu sau quyết định. [decision_date], [guardrails.no_post_decision_data]

---

## 2025Q3_VRE_03

## 1. Tóm tắt tín hiệu

- VRE, kỳ 2025Q3, ngày quyết định 2025-09-30.
- Mô hình dự báo `pred_label = 1`, xác suất lớp tăng `0.9940922707557027`, xếp hạng 3 trong kỳ, phân loại `Buy Candidate` (`ml_signal`).
- Tín hiệu kỹ thuật nghiêng tích cực: giá trên SMA20 `0.0666223625186909`; RSI cuối kỳ `66.8365675740471`; lợi suất kỳ hiện tại `0.29435483870967744` (`technical_snapshot`).
- Tín hiệu chưa đồng nhất: MACD histogram trung bình âm `-0.0024726934475260247`; thay đổi khối lượng `-0.5036560369902255` (`technical_snapshot`).
- Tin tức bị loại khỏi pack; evidence tin tức chưa đủ mạnh (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).

## 2. Luận điểm đầu tư chính

- VRE có tín hiệu định lượng nghiêng về lớp tăng trong mô hình, với `pred_label = 1`, `pred_proba_up = 0.9940922707557027`, `signal_class = Buy Candidate` (`ml_signal`).
- Luận điểm được hỗ trợ bởi trạng thái giá trên SMA20, RSI cuối kỳ và lợi suất gần đây (`technical_snapshot.price_vs_sma20`, `technical_snapshot.rsi_end_q`, `technical_snapshot.return_q`).
- Luận điểm còn điều kiện: MACD âm, khối lượng giảm và thiếu evidence tin tức độc lập (`technical_snapshot.macd_hist_mean_q`, `technical_snapshot.volume_change_q`, `data_quality_flags.news_evidence_removed_for_ablation`).

## 3. Yếu tố hỗ trợ

- Mô hình xếp VRE vào nhóm `Buy Candidate`, hạng 3 trong kỳ (`ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`).
- Giá cuối kỳ cao hơn SMA20 tương đối `0.0666223625186909` (`technical_snapshot.price_vs_sma20`).
- RSI cuối kỳ `66.8365675740471` là driver kỹ thuật hỗ trợ tín hiệu tăng (`top_drivers.feature = rsi_end_q`).
- Lợi suất kỳ hiện tại `0.29435483870967744`, kỳ trước `0.2325`, hai kỳ trước `0.10693641618497098` (`technical_snapshot.return_q`, `technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`).
- Lợi suất trung bình ngày dương `0.004363385464226554` (`technical_snapshot.return_mean_daily`).

## 4. Yếu tố cần lưu ý / rủi ro

- MACD histogram trung bình âm `-0.0024726934475260247`, cho thấy tín hiệu động lượng không đồng nhất với các driver tích cực (`technical_snapshot.macd_hist_mean_q`).
- Khối lượng giảm `-0.5036560369902255`, làm yếu mức xác nhận từ mức độ quan tâm thị trường (`technical_snapshot.volume_change_q`).
- Biên độ giá trong kỳ `0.26122448979591845`, phản ánh biến động cần theo dõi (`technical_snapshot.price_range_q`).
- Evidence tin tức bị loại khỏi phân tích; evidence tin tức chưa đủ mạnh để bổ sung hoặc kiểm chứng luận điểm (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).
- Tín hiệu mô hình không đồng nghĩa với bảo đảm kết quả; pack chỉ cung cấp tín hiệu và dữ liệu kỹ thuật (`ml_signal`, `technical_snapshot`).

## 5. Trigger theo dõi

- Theo dõi thay đổi `pred_label`, `pred_proba_up` hoặc `signal_class` của mô hình (`ml_signal`).
- Theo dõi giá còn trên hay chuyển xuống dưới SMA20 (`technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`).
- Theo dõi MACD histogram có tiếp tục âm hay cải thiện (`technical_snapshot.macd_hist_mean_q`).
- Theo dõi thay đổi khối lượng có tiếp tục âm hay phục hồi (`technical_snapshot.volume_change_q`).
- Theo dõi RSI cuối kỳ và biên độ giá trong kỳ (`technical_snapshot.rsi_end_q`, `technical_snapshot.price_range_q`).
- Evidence pack không cung cấp ngưỡng trigger định lượng mới; không tự đặt ngưỡng.

## 6. Thời điểm review

- Review theo kỳ tín hiệu kế tiếp, phù hợp với `holding_horizon = next_quarter_or_period_return_in_signals` (`holding_horizon`).
- Evidence pack không cung cấp ngày review cụ thể.
- Không sử dụng dữ liệu sau ngày quyết định 2025-09-30 (`decision_date`, `guardrails.no_post_decision_data`).

## 7. Kết luận hỗ trợ quyết định

- VRE có tín hiệu mô hình và một số chỉ báo kỹ thuật tích cực (`ml_signal`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.rsi_end_q`, `technical_snapshot.return_q`).
- MACD âm, khối lượng giảm, biến động giá và thiếu evidence tin tức làm giảm độ đầy đủ của luận điểm (`technical_snapshot.macd_hist_mean_q`, `technical_snapshot.volume_change_q`, `technical_snapshot.price_range_q`, `data_quality_flags.news_evidence_removed_for_ablation`).
- Có thể đưa VRE vào danh sách theo dõi hoặc đánh giá thêm; chưa đủ cơ sở cho khuyến nghị chắc chắn.

## 8. Disclaimer

- Decision card chỉ hỗ trợ quyết định, không phải tư vấn đầu tư (`guardrails.not_investment_advice`).
- Không phải dự báo giá tuyệt đối và không bảo đảm lợi nhuận.
- Nội dung chỉ dùng evidence pack cung cấp; không dùng dữ liệu sau quyết định (`guardrails.initial_prompt_safe`, `guardrails.no_post_decision_data`).
- Tin tức bị loại khỏi pack; evidence tin tức chưa đủ mạnh (`guardrails.news_evidence_excluded`, `data_quality_flags.news_evidence_removed_for_ablation`).

---

## 2025Q3_KDH_04

## 1. Tóm tắt tín hiệu

- KDH nhận tín hiệu `Buy Candidate`; `pred_label = 1`, `pred_proba_up = 0.9921`, xếp hạng 4 trong kỳ 2025Q3. [Evidence: `ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`]
- Tín hiệu đến từ mô hình kỹ thuật `technical_Config_A_from_existing_pipeline`. [Evidence: `ml_signal.model_name`]
- Dữ liệu cho tín hiệu tích cực gần nhất, nhưng trạng thái kỹ thuật còn pha trộn: RSI trung tính-yếu, giá dưới SMA20, biến động giá cao. [Evidence: `top_drivers`, `technical_snapshot`]
- Evidence tin tức chưa đủ mạnh. News evidence bị loại khỏi pack. [Evidence: `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`, `card_input_variant`]

## 2. Luận điểm đầu tư chính

- KDH là ứng viên cần theo dõi trong nhóm tín hiệu kỹ thuật, nhờ xác suất mô hình cao và xếp hạng 4 trong kỳ. [Evidence: `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`]
- Luận điểm được hỗ trợ bởi lợi suất kỳ hiện tại, MACD histogram, thay đổi khối lượng và lợi suất trung bình ngày. [Evidence: `technical_snapshot.return_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.volume_change_q`, `technical_snapshot.return_mean_daily`]
- Luận điểm chưa đồng thuận hoàn toàn vì RSI cuối kỳ ở mức 48.20, giá thấp hơn SMA20 khoảng 2.21%, lợi suất kỳ trước và lợi suất hai kỳ trước âm. [Evidence: `technical_snapshot.rsi_end_q`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`]
- Đây là tín hiệu mô hình, không phải khuyến nghị đầu tư chắc chắn. [Evidence: `guardrails.not_investment_advice`]

## 3. Yếu tố hỗ trợ

- Lợi suất kỳ hiện tại đạt `0.2626`, hỗ trợ động lượng gần nhất. [Evidence: `technical_snapshot.return_q`]
- MACD histogram trung bình dương `0.00954`, hỗ trợ tín hiệu xu hướng tăng trong mô hình. [Evidence: `technical_snapshot.macd_hist_mean_q`]
- Khối lượng thay đổi `1.0518`, phản ánh mức độ quan tâm thị trường trong kỳ. [Evidence: `technical_snapshot.volume_change_q`]
- Lợi suất trung bình ngày dương `0.00396`, hỗ trợ xu hướng ngắn trong kỳ. [Evidence: `technical_snapshot.return_mean_daily`]
- Mô hình ghi nhận tín hiệu `Buy Candidate`, với `pred_proba_up = 0.9921`. [Evidence: `ml_signal.signal_class`, `ml_signal.pred_proba_up`]

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `48.20` được mô hình xếp hướng yếu hoặc trung tính; động lượng chưa cho tín hiệu mạnh. [Evidence: `top_drivers[0]`, `technical_snapshot.rsi_end_q`]
- Giá cuối kỳ thấp hơn SMA20 `2.21%`, phản ánh trạng thái kỹ thuật yếu hơn đường trung bình ngắn hạn. [Evidence: `top_drivers[2]`, `technical_snapshot.price_vs_sma20`]
- Lợi suất kỳ trước `-0.0982` và hai kỳ trước `-0.0723`, cho thấy lịch sử động lượng còn bất lợi. [Evidence: `technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`]
- Biên độ giá trong kỳ `0.3685`, được gắn cờ rủi ro biến động cao. [Evidence: `top_drivers[8]`, `technical_snapshot.price_range_q`]
- Evidence định tính từ tin tức không có trong pack; không thể đánh giá thêm catalyst hoặc rủi ro tin tức. [Evidence: `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`]

## 5. Trigger theo dõi

- Cập nhật lại tín hiệu khi có kỳ mới hoặc period mới. [Evidence: `period_id`, `holding_horizon`, `ml_signal`]
- Theo dõi thay đổi của RSI, MACD histogram và giá so với SMA20 để kiểm tra độ bền tín hiệu. [Evidence: `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`]
- Theo dõi lợi suất kỳ, lợi suất kỳ trước, lợi suất hai kỳ trước và lợi suất trung bình ngày để nhận diện thay đổi động lượng. [Evidence: `technical_snapshot.return_q`, `technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`, `technical_snapshot.return_mean_daily`]
- Theo dõi khối lượng và biên độ giá để đánh giá mức độ xác nhận và rủi ro biến động. [Evidence: `technical_snapshot.volume_change_q`, `technical_snapshot.price_range_q`]
- Không đặt ngưỡng trigger mới vì evidence pack không cung cấp ngưỡng xác nhận hoặc hủy tín hiệu.

## 6. Thời điểm review

- Review tại kỳ kế tiếp hoặc period return tiếp theo trong hệ thống tín hiệu. [Evidence: `holding_horizon = next_quarter_or_period_return_in_signals`]
- Mốc lập card: `2025-09-30`; kỳ tín hiệu: `2025Q3`. [Evidence: `decision_date`, `period_id`]

## 7. Kết luận hỗ trợ quyết định

- KDH có tín hiệu kỹ thuật tích cực và được xếp `Buy Candidate`, phù hợp đưa vào danh sách theo dõi hoặc đánh giá thêm. [Evidence: `ml_signal.signal_class`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`]
- Tín hiệu chưa đủ đồng thuận do RSI trung tính-yếu, giá dưới SMA20, động lượng lịch sử âm và biến động cao. [Evidence: `technical_snapshot.rsi_end_q`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.return_prev_q`, `technical_snapshot.return_2q_ago`, `technical_snapshot.price_range_q`]
- Quyết định cần chờ cập nhật kỹ thuật kỳ kế tiếp và không nên dựa riêng trên tín hiệu mô hình này. [Evidence: `holding_horizon`, `guardrails.not_investment_advice`]

## 8. Disclaimer

- Card chỉ hỗ trợ phân tích học thuật và quyết định; không phải khuyến nghị đầu tư. [Evidence: `guardrails.not_investment_advice`]
- `pred_proba_up` là đầu ra mô hình, không bảo đảm kết quả. [Evidence: `ml_signal.pred_proba_up`, `ml_signal.model_name`]
- Không có dự báo giá tuyệt đối, cam kết lợi nhuận hoặc sử dụng outcome tương lai.
- Evidence tin tức bị loại khỏi pack; đánh giá định tính về tin tức chưa đủ mạnh. [Evidence: `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`]

---

## 2025Q3_SCR_05

## 1. Tóm tắt tín hiệu

- SCR nhận nhãn **“Buy Candidate”** từ mô hình kỹ thuật; xác suất hướng lên theo mô hình: **0,9904**; xếp hạng **5** trong kỳ 2025Q3. [ml_signal.pred_label, ml_signal.pred_proba_up, ml_signal.rank_in_period, ml_signal.signal_class]
- Tín hiệu tăng được hỗ trợ bởi vị trí giá trên SMA20, các feature động lượng dương và thay đổi khối lượng. [technical_snapshot.price_vs_sma20, technical_snapshot.return_q, technical_snapshot.return_prev_q, technical_snapshot.return_2q_ago, technical_snapshot.volume_change_q]
- MACD histogram trung bình âm và biên độ giá cao tạo tín hiệu đối trọng. [technical_snapshot.macd_hist_mean_q, technical_snapshot.price_range_q]
- Tin tức bị loại khỏi evidence pack; **evidence tin tức chưa đủ mạnh**. [data_quality_flags.news_evidence_removed_for_ablation, guardrails.news_evidence_excluded]

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình nghiêng về hướng tăng trong khung theo dõi kỳ kế tiếp, dựa trên nhãn “Buy Candidate” và xác suất mô hình 0,9904. [ml_signal.signal_class, ml_signal.pred_proba_up]
- Luận điểm chưa đồng thuận hoàn toàn: RSI, giá so với SMA20, động lượng kỳ và khối lượng hỗ trợ tín hiệu; MACD âm và biến động cao làm tăng rủi ro tín hiệu suy yếu. [top_drivers, technical_snapshot]
- Card chỉ hỗ trợ sàng lọc, không đủ cơ sở kết luận hành động đầu tư chắc chắn.

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ ở mức **52,8499**, là driver kỹ thuật quan trọng nhất và được mô hình đánh dấu hỗ trợ tín hiệu hướng lên. [top_drivers.feature=rsi_end_q, technical_snapshot.rsi_end_q]
- Giá nằm trên SMA20 theo feature `price_vs_sma20` ở mức **0,0226**. [top_drivers.feature=price_vs_sma20, technical_snapshot.price_vs_sma20]
- Các feature động lượng ghi nhận giá trị dương: `return_q` **0,3324**, `return_prev_q` **0,0590**, `return_2q_ago` **0,1866**, `return_mean_daily` **0,0049**. [technical_snapshot.return_q, technical_snapshot.return_prev_q, technical_snapshot.return_2q_ago, technical_snapshot.return_mean_daily]
- Thay đổi khối lượng ở mức **1,4162**, được mô hình xếp vào nhóm hỗ trợ tín hiệu hướng lên. [top_drivers.feature=volume_change_q, technical_snapshot.volume_change_q]
- Mô hình xếp SCR hạng **5** trong kỳ. [ml_signal.rank_in_period]

## 4. Yếu tố cần lưu ý / rủi ro

- MACD histogram trung bình âm ở mức **-0,0050**, phản ánh động lượng xu hướng yếu hoặc chưa xác nhận đầy đủ. [top_drivers.feature=macd_hist_mean_q, technical_snapshot.macd_hist_mean_q]
- Biên độ giá trong kỳ ở mức **0,3900**, được mô hình gắn nhãn rủi ro biến động cao. [top_drivers.feature=price_range_q, technical_snapshot.price_range_q]
- Xác suất **0,9904** là xác suất do mô hình tạo ra, không phải bảo đảm kết quả. [ml_signal.pred_proba_up, ml_signal.model_name]
- Không có bằng chứng tin tức để kiểm tra yếu tố sự kiện, rủi ro hoặc thông tin định tính. **Evidence tin tức chưa đủ mạnh.** [data_quality_flags.news_evidence_removed_for_ablation, guardrails.news_evidence_excluded]
- Tín hiệu phụ thuộc pipeline kỹ thuật hiện có. [ml_signal.model_name]

## 5. Trigger theo dõi

- Theo dõi RSI cuối kỳ và vị trí giá so với SMA20; tín hiệu hỗ trợ suy yếu nếu các feature này giảm so với mức hiện tại. [technical_snapshot.rsi_end_q, technical_snapshot.price_vs_sma20]
- Theo dõi MACD histogram; mức âm hiện tại cần được cải thiện để giảm mâu thuẫn động lượng. [technical_snapshot.macd_hist_mean_q]
- Theo dõi thay đổi khối lượng cùng các feature động lượng kỳ hiện tại và kỳ trước. [technical_snapshot.volume_change_q, technical_snapshot.return_q, technical_snapshot.return_prev_q]
- Theo dõi biên độ giá; biến động tăng thêm làm tăng rủi ro tín hiệu. [technical_snapshot.price_range_q]
- Bổ sung kiểm tra tin tức khi có evidence định tính phù hợp; hiện pack không cung cấp nội dung tin tức. [data_quality_flags.news_evidence_removed_for_ablation]

## 6. Thời điểm review

- Review tại **kỳ kế tiếp**, phù hợp với `holding_horizon: next_quarter_or_period_return_in_signals`. [holding_horizon]
- Ngày lập card: **2025-09-30**. [decision_date]
- Review sớm khi các trigger kỹ thuật trên thay đổi đáng kể.

## 7. Kết luận hỗ trợ quyết định

- SCR có tín hiệu mô hình tích cực, thuộc nhóm **“Buy Candidate”**, nhưng chưa phải tín hiệu đồng thuận hoàn toàn do MACD âm, biến động cao và thiếu evidence tin tức. [ml_signal.signal_class, technical_snapshot.macd_hist_mean_q, technical_snapshot.price_range_q, data_quality_flags.news_evidence_removed_for_ablation]
- Có thể đưa SCR vào danh sách theo dõi hoặc quy trình thẩm định tiếp theo, với trọng tâm là xác nhận động lượng, biến động và thông tin định tính ở kỳ review.
- Không đủ evidence để đưa ra khuyến nghị đầu tư chắc chắn.

## 8. Disclaimer

- Card chỉ sử dụng evidence pack tại ngày **2025-09-30**. [decision_date]
- Tín hiệu mô hình không bảo đảm kết quả.
- Không sử dụng dự báo giá tuyệt đối.
- Không bao gồm evidence tin tức; **evidence tin tức chưa đủ mạnh**. [data_quality_flags.news_evidence_removed_for_ablation]
- Nội dung nhằm hỗ trợ nghiên cứu và quyết định, không phải tư vấn đầu tư. [guardrails.not_investment_advice]

---

## 2025Q4_GAS_01

## 1. Tóm tắt tín hiệu

- GAS nhận nhãn **“Buy Candidate”** từ mô hình `technical_Config_A_from_existing_pipeline`, xác suất lớp tăng `0.9977169088235865`, xếp hạng `1` trong kỳ `2025Q4` (`ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`).
- Tín hiệu kỹ thuật nghiêng tích cực: RSI cuối kỳ `67.5243`, MACD histogram trung bình `0.1337`, giá cao hơn SMA20 với `price_vs_sma20 = 0.09597` (`technical_snapshot`, `top_drivers`).
- Tín hiệu chưa đồng nhất: lợi suất kỳ trước `-0.0336`, thay đổi khối lượng `-0.07064` (`technical_snapshot`, `top_drivers`).
- Tin tức bị loại khỏi evidence pack; **evidence tin tức chưa đủ mạnh** (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).

## 2. Luận điểm đầu tư chính

- Mô hình ghi nhận tín hiệu tăng mạnh cho GAS, dựa chủ yếu trên RSI, MACD histogram, vị trí giá so với SMA20 và động lượng trong kỳ (`ml_signal`, `top_drivers`).
- Tín hiệu phù hợp với trạng thái động lượng tích cực trong `2025Q4`, nhưng chưa đủ để kết luận chắc chắn về kết quả kỳ tới (`technical_snapshot.return_q`, `technical_snapshot.return_mean_daily`, `holding_horizon`).
- Có thể xem GAS là **ứng viên cần theo dõi**, không phải khuyến nghị mua chắc chắn (`ml_signal.signal_class`, `guardrails.not_investment_advice`).

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ `67.5243409235251` là driver kỹ thuật quan trọng nhất của mô hình (`top_drivers.feature = rsi_end_q`).
- MACD histogram trung bình kỳ `0.1337493322570629` hỗ trợ tín hiệu động lượng (`top_drivers.feature = macd_hist_mean_q`).
- Giá duy trì trên SMA20, với `price_vs_sma20 = 0.09597335755373908` và `sma20_end = 66.06` (`technical_snapshot`).
- Lợi suất trong kỳ `0.19471947194719477` và lợi suất trung bình ngày `0.0029299763581694463` hỗ trợ tín hiệu xu hướng gần nhất (`technical_snapshot`, `top_drivers`).
- Mô hình xếp GAS hạng `1` trong kỳ báo cáo (`ml_signal.rank_in_period`).

## 4. Yếu tố cần lưu ý / rủi ro

- Lợi suất kỳ trước âm `-0.033600000000000026`, cho thấy động lượng giữa các kỳ chưa nhất quán (`technical_snapshot.return_prev_q`, `top_drivers`).
- Khối lượng giảm `-0.07063736767311526`, làm yếu mức xác nhận từ mức độ quan tâm thị trường (`technical_snapshot.volume_change_q`, `top_drivers`).
- Biên độ giá trong kỳ `0.31615619102917686`, cần theo dõi rủi ro biến động (`technical_snapshot.price_range_q`, `top_drivers`).
- RSI ở mức `67.5243409235251`; cần theo dõi khả năng động lượng suy yếu khi chỉ báo thay đổi (`technical_snapshot.rsi_end_q`).
- Evidence định tính từ tin tức không có; không thể đánh giá thêm `article_summary`, `key_facts`, `risk_flags` hoặc `event_type` (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).
- Xác suất mô hình cao không loại bỏ rủi ro sai tín hiệu (`ml_signal.pred_proba_up`, `guardrails.not_investment_advice`).

## 5. Trigger theo dõi

- RSI suy yếu so với mức cuối kỳ `67.5243409235251` (`technical_snapshot.rsi_end_q`).
- MACD histogram giảm so với mức trung bình `0.1337493322570629` (`technical_snapshot.macd_hist_mean_q`).
- Giá thu hẹp vị trí trên SMA20 so với `price_vs_sma20 = 0.09597335755373908` (`technical_snapshot.price_vs_sma20`).
- Khối lượng tiếp tục giảm từ mức thay đổi `-0.07063736767311526` (`technical_snapshot.volume_change_q`).
- Lợi suất kỳ mới tiếp tục yếu hơn tín hiệu hiện tại `return_q = 0.19471947194719477` hoặc lặp lại trạng thái âm của kỳ trước `return_prev_q = -0.033600000000000026` (`technical_snapshot`).
- Xuất hiện evidence tin tức mới với các trường `article_summary`, `key_facts`, `risk_flags`, `event_type` (`data_quality_flags.news_evidence_removed_for_ablation`).

## 6. Thời điểm review

- Review vào **cuối quý kế tiếp hoặc khi xuất hiện kỳ tín hiệu mới**, phù hợp với `holding_horizon = next_quarter_or_period_return_in_signals` (`holding_horizon`).
- Review sớm hơn nếu các trigger kỹ thuật trên thay đổi rõ rệt (`technical_snapshot`, `top_drivers`).

## 7. Kết luận hỗ trợ quyết định

- GAS có tín hiệu mô hình và động lượng kỹ thuật tích cực trong `2025Q4`; phù hợp đưa vào danh sách theo dõi ưu tiên (`ml_signal`, `technical_snapshot`, `top_drivers`).
- Quyết định cần cân nhắc tín hiệu khối lượng giảm, lợi suất kỳ trước âm, biến động giá và thiếu evidence tin tức (`technical_snapshot`, `data_quality_flags`, `guardrails`).
- Chưa đủ cơ sở để đưa ra khuyến nghị đầu tư chắc chắn hoặc kết luận về kết quả kỳ tới (`holding_horizon`, `guardrails.not_investment_advice`).

## 8. Disclaimer

- Decision card chỉ hỗ trợ phân tích và ra quyết định; không phải tư vấn đầu tư (`guardrails.not_investment_advice`).
- Chỉ sử dụng evidence trong pack tại ngày quyết định `2025-12-31` (`decision_date`, `guardrails.no_post_decision_data`).
- Không sử dụng dữ liệu tin tức vì news evidence đã bị loại khỏi pack (`guardrails.news_evidence_excluded`).
- Tín hiệu mô hình không bảo đảm kết quả tương lai.

---

## 2025Q4_MCH_02

## 1. Tóm tắt tín hiệu

- MCH, kỳ 2025Q4: mô hình gắn nhãn **“Buy Candidate”**, `pred_label = 1`, `pred_proba_up = 0.9944`, xếp hạng 2 trong kỳ. [ml_signal]
- Tín hiệu dựa trên dữ liệu kỹ thuật và mô hình ML. [card_input_variant], [ml_signal], [technical_snapshot]
- Tin tức bị loại khỏi evidence pack; **evidence tin tức chưa đủ mạnh**. [data_quality_flags.news_evidence_removed_for_ablation], [guardrails.news_evidence_excluded]
- Không có trường thiếu được ghi nhận. [data_quality_flags.missing_fields]

## 2. Luận điểm đầu tư chính

- MCH là ứng viên cần theo dõi vì mô hình phát hiện tín hiệu tăng với xác suất mô hình cao và thứ hạng 2 trong kỳ. [ml_signal.pred_label], [ml_signal.pred_proba_up], [ml_signal.rank_in_period], [ml_signal.signal_class]
- Luận điểm hiện nghiêng về động lượng kỹ thuật: RSI cuối kỳ 66.06, MACD histogram trung bình 0.2268, giá cao hơn SMA20 khoảng 2.18%. [technical_snapshot.rsi_end_q], [technical_snapshot.macd_hist_mean_q], [technical_snapshot.price_vs_sma20]
- Đây là tín hiệu sàng lọc từ mô hình, không phải kết luận đầu tư chắc chắn. [card_input_variant], [guardrails.not_investment_advice]

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ 66.06 là driver kỹ thuật quan trọng nhất trong mô hình. [top_drivers.feature=rsi_end_q], [top_drivers.value=66.06094473916028]
- MACD histogram trung bình dương 0.2268, hỗ trợ tín hiệu động lượng. [top_drivers.feature=macd_hist_mean_q], [top_drivers.value=0.22683360964630253]
- Giá nằm trên SMA20 khoảng 2.18%, phản ánh trạng thái kỹ thuật tích cực hơn so với đường trung bình ngắn hạn. [technical_snapshot.price_vs_sma20]
- Thay đổi khối lượng trong kỳ là 25.23%, phù hợp với tín hiệu quan tâm thị trường cao hơn. [technical_snapshot.volume_change_q], [top_drivers.feature=volume_change_q]
- Mô hình xếp MCH hạng 2 trong kỳ. [ml_signal.rank_in_period]

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ là 56.57%, cho thấy biến động cao. [technical_snapshot.price_range_q], [top_drivers.feature=price_range_q]
- RSI 66.06 nằm gần vùng cao theo chỉ báo, nên cần theo dõi khả năng động lượng suy yếu; evidence pack không cung cấp ngưỡng cảnh báo cụ thể. [technical_snapshot.rsi_end_q]
- Tín hiệu phụ thuộc vào mô hình kỹ thuật; không có xác nhận định tính từ tin tức do tin tức bị loại. [ml_signal.model_name], [data_quality_flags.news_evidence_removed_for_ablation]
- Một driver lịch sử có hướng yếu hoặc âm: `return_2q_ago = -0.1077`. [top_drivers.feature=return_2q_ago], [top_drivers.direction=weak_or_negative]
- `pred_proba_up` là đầu ra mô hình, không bảo đảm kết quả thực tế. [ml_signal.pred_proba_up], [guardrails.not_investment_advice]

## 5. Trigger theo dõi

- Theo dõi thay đổi `pred_label`, `pred_proba_up`, `signal_class` và thứ hạng trong kỳ kế tiếp. [ml_signal]
- Theo dõi RSI, MACD histogram và vị trí giá so với SMA20; suy yếu đồng thời có thể làm giảm độ ủng hộ của tín hiệu kỹ thuật. [technical_snapshot.rsi_end_q], [technical_snapshot.macd_hist_mean_q], [technical_snapshot.price_vs_sma20]
- Theo dõi biến động giá và thay đổi khối lượng; biên độ tăng hoặc khối lượng đảo chiều cần đánh giá lại. [technical_snapshot.price_range_q], [technical_snapshot.volume_change_q]
- Evidence pack không cung cấp ngưỡng trigger định lượng.

## 6. Thời điểm review

- Review tại kỳ tiếp theo, phù hợp với `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Mốc quyết định ban đầu: 2025-12-31. [decision_date]
- Không có ngày review cụ thể hơn trong evidence pack.

## 7. Kết luận hỗ trợ quyết định

- MCH có tín hiệu kỹ thuật mạnh và thuộc nhóm ứng viên cần theo dõi ưu tiên. [ml_signal], [technical_snapshot]
- Biến động cao, thiếu xác nhận tin tức, và phụ thuộc mô hình làm tăng nhu cầu kiểm tra lại trước kỳ review. [technical_snapshot.price_range_q], [guardrails.news_evidence_excluded], [ml_signal.model_name]
- Evidence hiện hỗ trợ trạng thái **theo dõi và thẩm định thêm**, không đủ để đưa ra khuyến nghị đầu tư chắc chắn.

## 8. Disclaimer

- Nội dung chỉ dùng hỗ trợ nghiên cứu và quyết định, không phải tư vấn đầu tư. [guardrails.not_investment_advice]
- Không có bảo đảm về kết quả thực tế, lợi nhuận, hay diễn biến giá.
- Decision card chỉ dùng evidence pack tại ngày 2025-12-31; không sử dụng dữ liệu sau quyết định. [decision_date], [guardrails.no_post_decision_data]

---

## 2025Q4_ABB_03

## 1. Tóm tắt tín hiệu

- ABB nhận nhãn `Buy Candidate` từ mô hình kỹ thuật `technical_Config_A_from_existing_pipeline`. [ml_signal.model_name, ml_signal.signal_class]
- Xác suất mô hình cho nhãn tăng: `0.9925587966120623`; xếp hạng `3` trong kỳ. [ml_signal.pred_proba_up, ml_signal.rank_in_period]
- Tín hiệu tăng được hỗ trợ bởi RSI, MACD, vị trí giá trên SMA20 và các biến lợi suất trong dữ liệu. [top_drivers]
- Khối lượng giảm `-0.3838155395206998`, tạo tín hiệu yếu hoặc tiêu cực. [top_drivers.volume_change_q]
- Tin tức bị loại khỏi bộ evidence; evidence tin tức chưa đủ mạnh. [data_quality_flags.news_evidence_removed_for_ablation, guardrails.news_evidence_excluded]

## 2. Luận điểm đầu tư chính

ABB có tín hiệu kỹ thuật tích cực trong `2025Q4`, với xác suất mô hình cao và xếp hạng `3` trong kỳ. Động lượng được hỗ trợ bởi RSI cuối kỳ `66.26886472073552`, MACD histogram trung bình `0.0216105821083708`, giá cao hơn SMA20 `2.8815%`, cùng các biến lợi suất kỳ hiện tại, kỳ trước và trễ hai kỳ. [ml_signal, technical_snapshot, top_drivers]

Luận điểm chưa toàn diện vì khối lượng giảm `38.3816%` và không có evidence tin tức để kiểm chứng định tính. [technical_snapshot.volume_change_q, data_quality_flags.news_evidence_removed_for_ablation]

## 3. Yếu tố hỗ trợ

- Mô hình gán nhãn `Buy Candidate`, xác suất nhãn tăng `0.9925587966120623`. [ml_signal.signal_class, ml_signal.pred_proba_up]
- RSI cuối kỳ `66.26886472073552` là driver kỹ thuật quan trọng nhất, theo mô tả mô hình. [top_drivers.feature = rsi_end_q]
- MACD histogram trung bình `0.0216105821083708` hỗ trợ tín hiệu động lượng. [top_drivers.feature = macd_hist_mean_q]
- Giá cao hơn SMA20 `2.8815%`, phản ánh trạng thái trên đường trung bình. [technical_snapshot.price_vs_sma20]
- `return_q = 0.2983230361871139` và `return_prev_q = 0.46354166666666674` bổ sung tín hiệu động lượng gần nhất. [technical_snapshot]
- `return_2q_ago = 0.06371191135734072` và `return_mean_daily = 0.004301626176972389` hỗ trợ tín hiệu quán tính lịch sử và xu hướng ngắn trong kỳ. [technical_snapshot]

## 4. Yếu tố cần lưu ý / rủi ro

- Khối lượng giảm `-0.3838155395206998`; driver được mô hình phân loại `weak_or_negative`. [top_drivers.feature = volume_change_q]
- Biên độ giá trong kỳ `0.2842016094875053` phản ánh yếu tố biến động/rủi ro. [technical_snapshot.price_range_q, top_drivers.feature = price_range_q]
- Tín hiệu dựa trên mô hình kỹ thuật; evidence pack không cung cấp xác nhận cơ bản hoặc định tính khác. [ml_signal.model_name, data_quality_flags.news_evidence_removed_for_ablation]
- Tin tức bị loại khỏi phân tích; evidence tin tức chưa đủ mạnh để đánh giá `article_summary`, `key_facts`, `risk_flags` hoặc `event_type`. [data_quality_flags.news_evidence_removed_for_ablation, guardrails.news_evidence_excluded]
- Xác suất mô hình không đồng nghĩa với kết quả chắc chắn. [ml_signal.pred_proba_up, guardrails.not_investment_advice]

## 5. Trigger theo dõi

- Theo dõi diễn biến RSI cuối kỳ so với mức hiện tại `66.26886472073552`. [technical_snapshot.rsi_end_q]
- Theo dõi MACD histogram trung bình quanh mức `0.0216105821083708`. [technical_snapshot.macd_hist_mean_q]
- Theo dõi vị trí giá so với SMA20 `14.298` và mức chênh lệch hiện tại `0.028815218911735965`. [technical_snapshot.sma20_end, technical_snapshot.price_vs_sma20]
- Theo dõi khối lượng, đặc biệt thay đổi kỳ `-0.3838155395206998`. [technical_snapshot.volume_change_q]
- Kiểm tra lại nhãn mô hình, xác suất và xếp hạng trong kỳ review tiếp theo. [ml_signal, period_id]
- Bổ sung evidence tin tức nếu có; hiện evidence tin tức chưa đủ mạnh. [data_quality_flags.news_evidence_removed_for_ablation]

## 6. Thời điểm review

- Review tại kỳ kế tiếp theo `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm hơn nếu RSI, MACD, vị trí giá trên SMA20 hoặc khối lượng thay đổi đáng kể so với mức hiện tại. [technical_snapshot, top_drivers]

## 7. Kết luận hỗ trợ quyết định

Tín hiệu kỹ thuật của ABB nghiêng tích cực: mô hình gắn nhãn `Buy Candidate`, xác suất nhãn tăng cao và xếp hạng `3` trong kỳ. [ml_signal]

Khối lượng giảm và thiếu evidence tin tức làm yếu độ đầy đủ của luận điểm. Card phù hợp làm đầu vào hỗ trợ quyết định, không đủ để kết luận đầu tư chắc chắn. [technical_snapshot.volume_change_q, data_quality_flags.news_evidence_removed_for_ablation, guardrails.not_investment_advice]

## 8. Disclaimer

- Nội dung chỉ hỗ trợ nghiên cứu và quyết định; không phải khuyến nghị đầu tư. [guardrails.not_investment_advice]
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Phân tích chỉ dùng evidence trong pack, chủ yếu từ mô hình và dữ liệu kỹ thuật. [card_input_variant, ml_signal, technical_snapshot]
- Tin tức bị loại khỏi bộ evidence; evidence tin tức chưa đủ mạnh. [data_quality_flags.news_evidence_removed_for_ablation]
- Không sử dụng dữ liệu sau ngày quyết định `2025-12-31`. [decision_date, guardrails.no_post_decision_data]

---

## 2025Q4_ELC_04

## 1. Tóm tắt tín hiệu

- ELC thuộc nhóm `Buy Candidate`; `pred_label = 1`, `pred_proba_up = 0.9852`, xếp hạng 4 trong kỳ `2025Q4` (`ml_signal`).
- Động lượng kỹ thuật hỗ trợ: `return_q = 0.1431`, `return_prev_q = 0.0244`, `macd_hist_mean_q = 0.0334`, `price_vs_sma20 = 0.0494` (`technical_snapshot`).
- Tín hiệu có điểm cảnh báo: `rsi_end_q = 71.35` và `volume_change_q = -0.4554` (`technical_snapshot`, `top_drivers`).
- Evidence tin tức chưa đủ mạnh: dữ liệu tin tức bị loại khỏi pack (`data_quality_flags.news_evidence_removed_for_ablation = true`, `guardrails.news_evidence_excluded = true`).

## 2. Luận điểm đầu tư chính

- Mô hình ghi nhận tín hiệu hướng lên tương đối mạnh, dựa trên `pred_proba_up = 0.9852` và `signal_class = "Buy Candidate"` (`ml_signal`).
- Động lượng gần đây hỗ trợ tín hiệu: lợi suất quý hiện tại dương, lợi suất quý trước dương, MACD histogram dương, giá nằm trên SMA20 (`return_q`, `return_prev_q`, `macd_hist_mean_q`, `price_vs_sma20`).
- Tín hiệu không đồng nhất hoàn toàn: RSI cuối kỳ ở mức 71.35 và khối lượng giảm mạnh (`rsi_end_q`, `volume_change_q`). Đây là cơ sở để theo dõi thay vì xem tín hiệu mô hình như quyết định chắc chắn.

## 3. Yếu tố hỗ trợ

- Xu hướng quý gần nhất tích cực: `return_q = 0.1431` (`technical_snapshot.return_q`).
- Động lượng kỳ trước vẫn dương: `return_prev_q = 0.0244` (`technical_snapshot.return_prev_q`).
- MACD histogram trung bình dương: `macd_hist_mean_q = 0.0334` (`technical_snapshot.macd_hist_mean_q`).
- Giá cao hơn SMA20: `price_vs_sma20 = 0.0494`; SMA20 cuối kỳ là `23.4425` (`technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`).
- Lợi suất trung bình ngày dương: `return_mean_daily = 0.00194` (`technical_snapshot.return_mean_daily`).
- Mô hình xếp ELC ở hạng 4 trong kỳ (`ml_signal.rank_in_period`).

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `71.35`; driver được mô tả là `positive_but_overbought_risk`, cho thấy rủi ro trạng thái quá mua (`top_drivers[0]`, `technical_snapshot.rsi_end_q`).
- Khối lượng giảm `45.54%`: `volume_change_q = -0.4554`; driver được phân loại `weak_or_negative` (`top_drivers[6]`, `technical_snapshot.volume_change_q`).
- Lợi suất trễ hai kỳ âm: `return_2q_ago = -0.0581`; động lượng lịch sử không đồng nhất (`top_drivers[3]`, `technical_snapshot.return_2q_ago`).
- Biên độ giá trong kỳ là `0.2230`, cần theo dõi biến động (`technical_snapshot.price_range_q`).
- Evidence định tính từ tin tức không có trong pack; evidence tin tức chưa đủ mạnh (`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).
- Xác suất mô hình không đồng nghĩa kết quả chắc chắn; pack chỉ cung cấp tín hiệu mô hình và dữ liệu kỹ thuật (`ml_signal`, `technical_snapshot`).

## 5. Trigger theo dõi

- RSI tiếp tục duy trì cao hoặc tăng thêm: theo dõi `rsi_end_q` (`technical_snapshot.rsi_end_q`).
- Giá giữ hoặc mất trạng thái trên SMA20: theo dõi `price_vs_sma20` và `sma20_end` (`technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`).
- MACD histogram suy yếu hoặc chuyển âm: theo dõi `macd_hist_mean_q` (`technical_snapshot.macd_hist_mean_q`).
- Động lượng quý và quý trước đảo chiều: theo dõi `return_q`, `return_prev_q` (`technical_snapshot.return_q`, `technical_snapshot.return_prev_q`).
- Khối lượng tiếp tục giảm: theo dõi `volume_change_q` (`technical_snapshot.volume_change_q`).
- Cập nhật evidence tin tức có `article_summary`, `key_facts`, `risk_flags`, `event_type`; hiện chưa có các trường này trong pack (`data_quality_flags.news_evidence_removed_for_ablation`).

## 6. Thời điểm review

- Review vào cuối quý tiếp theo hoặc theo kỳ tín hiệu kế tiếp, phù hợp `holding_horizon = "next_quarter_or_period_return_in_signals"` (`holding_horizon`).
- Mốc khởi tạo card: `2025-12-31` (`decision_date`).
- Review sớm nếu các trigger về RSI, SMA20, MACD hoặc khối lượng thay đổi rõ (`technical_snapshot`, `top_drivers`).

## 7. Kết luận hỗ trợ quyết định

- ELC có tín hiệu mô hình và động lượng kỹ thuật nghiêng tích cực (`ml_signal`, `return_q`, `return_prev_q`, `macd_hist_mean_q`).
- RSI cao, khối lượng giảm và lợi suất trễ hai kỳ âm làm tăng nhu cầu kiểm tra rủi ro (`rsi_end_q`, `volume_change_q`, `return_2q_ago`).
- Có thể dùng card làm đầu vào sàng lọc và theo dõi; chưa đủ cơ sở để xem đây là khuyến nghị đầu tư chắc chắn. Evidence tin tức chưa đủ mạnh (`data_quality_flags.news_evidence_removed_for_ablation`).

## 8. Disclaimer

- Card chỉ hỗ trợ phân tích học thuật và quyết định; không phải khuyến nghị đầu tư.
- Chỉ dùng evidence trong pack tại `decision_date = 2025-12-31`.
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Tín hiệu mô hình không bảo đảm kết quả.

---

## 2025Q4_VBB_05

## 1. Tóm tắt tín hiệu

- Mã `VBB`, kỳ `2025Q4`, ngày quyết định `2025-12-31`.
- Mô hình gán nhãn `Buy Candidate`, `pred_label=1`, `pred_proba_up=0.9821647646675534`, xếp hạng `5` trong kỳ [`ml_signal`].
- Tín hiệu mô hình tích cực; dữ liệu kỹ thuật đối nghịch: giá trên SMA20 và động lượng lịch sử hỗ trợ, nhưng lợi suất kỳ hiện tại, MACD, RSI và khối lượng yếu [`technical_snapshot`, `top_drivers`].
- Evidence tin tức chưa đủ mạnh: dữ liệu tin tức bị loại khỏi pack [`data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`].

## 2. Luận điểm đầu tư chính

- VBB là ứng viên được mô hình ưu tiên theo tín hiệu tăng, nhưng đây là tín hiệu mô hình, không phải kết luận hành động [`ml_signal`].
- Một số yếu tố kỹ thuật hỗ trợ: giá cao hơn SMA20 (`price_vs_sma20=0.0090763481`), lợi suất hai kỳ trước `0.1849405548`, lợi suất kỳ trước `0.1295454545` [`technical_snapshot`, `top_drivers`].
- Độ tin cậy quyết định bị giảm bởi lợi suất kỳ hiện tại âm, MACD âm, RSI yếu/trung tính và khối lượng giảm mạnh [`return_q`, `macd_hist_mean_q`, `rsi_end_q`, `volume_change_q`].

## 3. Yếu tố hỗ trợ

- Nhãn mô hình là `Buy Candidate`; `pred_proba_up=0.9821647646675534` [`ml_signal`].
- Giá cuối kỳ nằm trên SMA20: `price_vs_sma20=0.009076348104644855` [`technical_snapshot`, `top_drivers`].
- Lợi suất hai kỳ trước dương: `return_2q_ago=0.1849405548216645` [`technical_snapshot`, `top_drivers`].
- Lợi suất kỳ trước dương: `return_prev_q=0.1295454545454544` [`technical_snapshot`, `top_drivers`].
- Xếp hạng mô hình ở vị trí `5` trong kỳ [`ml_signal.rank_in_period`].

## 4. Yếu tố cần lưu ý / rủi ro

- Lợi suất kỳ hiện tại âm: `return_q=-0.07443682664054863` [`technical_snapshot`, `top_drivers`].
- Động lượng MACD yếu/âm: `macd_hist_mean_q=-0.005514007222263613` [`technical_snapshot`, `top_drivers`].
- RSI cuối kỳ yếu/trung tính: `rsi_end_q=47.868748788272086` [`technical_snapshot`, `top_drivers`].
- Khối lượng giảm mạnh: `volume_change_q=-0.5824407137470619` [`technical_snapshot`, `top_drivers`].
- Lợi suất trung bình ngày âm: `return_mean_daily=-0.0006765024421901496` [`technical_snapshot`, `top_drivers`].
- Biên độ giá trong kỳ ở mức `price_range_q=0.26662178084497556`, phản ánh yếu tố biến động cần theo dõi [`technical_snapshot`, `top_drivers`].
- Evidence tin tức chưa đủ mạnh; không có cơ sở từ `article_summary`, `key_facts`, `risk_flags` hoặc `event_type` trong pack [`data_quality_flags`, `guardrails`].

## 5. Trigger theo dõi

- Cập nhật `pred_label`, `pred_proba_up`, `signal_class` và `rank_in_period` khi có kỳ tín hiệu mới [`ml_signal`].
- Theo dõi giá duy trì trên hay rơi xuống dưới SMA20 qua `price_vs_sma20` [`technical_snapshot`].
- Theo dõi cải thiện hoặc suy yếu của MACD qua `macd_hist_mean_q` [`technical_snapshot`].
- Theo dõi RSI qua `rsi_end_q` [`technical_snapshot`].
- Theo dõi `return_q`, `return_mean_daily` và `return_prev_q` để đánh giá động lượng gần nhất [`technical_snapshot`].
- Theo dõi khả năng phục hồi của khối lượng qua `volume_change_q` [`technical_snapshot`].
- Chưa có trigger tin tức đáng tin cậy do evidence tin tức bị loại [`data_quality_flags.news_evidence_removed_for_ablation`].

## 6. Thời điểm review

- Review tại kỳ kế tiếp theo `holding_horizon=next_quarter_or_period_return_in_signals` [`holding_horizon`].
- Dùng snapshot kỹ thuật và tín hiệu mô hình mới; card hiện tại không dùng dữ liệu sau ngày quyết định [`decision_date`, `guardrails.no_post_decision_data`].

## 7. Kết luận hỗ trợ quyết định

- VBB có tín hiệu mô hình tích cực và được xếp nhóm `Buy Candidate` [`ml_signal`].
- Bằng chứng kỹ thuật chưa đồng thuận: yếu tố giá và động lượng lịch sử hỗ trợ, trong khi động lượng hiện tại và thanh khoản yếu [`technical_snapshot`, `top_drivers`].
- Phù hợp để đưa vào danh sách theo dõi có điều kiện, không đủ evidence để kết luận hành động chắc chắn.
- Cần review lại ở kỳ kế tiếp, tập trung vào MACD, RSI, giá so với SMA20, lợi suất gần nhất và khối lượng [`technical_snapshot`, `holding_horizon`].

## 8. Disclaimer

- Nội dung phục vụ hỗ trợ quyết định trong nghiên cứu học thuật, không phải khuyến nghị đầu tư [`guardrails.not_investment_advice`].
- Tín hiệu mô hình không bảo đảm kết quả, không phải dự báo giá tuyệt đối.
- Evidence tin tức đã bị loại; kết luận chỉ dựa trên tín hiệu ML và dữ liệu kỹ thuật có trong pack [`data_quality_flags`, `guardrails.news_evidence_excluded`].

---

## 2026Q1_GMD_01

## 1. Tóm tắt tín hiệu

- GMD nhận nhãn `Buy Candidate`; `pred_label=1`, xác suất mô hình cho hướng tăng `0.991833`, xếp hạng `1` trong kỳ `2026Q1` [ml_signal].
- Tín hiệu dựa trên mô hình kỹ thuật, không có evidence tin tức trong pack [card_input_variant; data_quality_flags.news_evidence_removed_for_ablation].
- Tín hiệu tích cực nhưng có biến động giá cao và lợi suất kỳ trước âm [top_drivers; price_range_q; return_prev_q].

## 2. Luận điểm đầu tư chính

- Mô hình kỹ thuật nghiêng tích cực cho GMD trong kỳ đánh giá, nhờ RSI, MACD histogram, vị trí giá so với SMA20, lợi suất kỳ hiện tại và thay đổi khối lượng [ml_signal; top_drivers].
- Động lượng hiện tại mạnh hơn kỳ trước: `return_q=0.311938`, trong khi `return_prev_q=-0.082637` [technical_snapshot.return_q; technical_snapshot.return_prev_q].
- Đây là tín hiệu hỗ trợ quyết định theo dõi, không phải khuyến nghị mua chắc chắn [ml_signal.signal_class; guardrails.not_investment_advice].

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ `57.560560`, được mô hình xác định là driver kỹ thuật quan trọng nhất [top_drivers.feature=rsi_end_q; technical_snapshot.rsi_end_q].
- MACD histogram trung bình `0.134793`, hỗ trợ tín hiệu động lượng [top_drivers.feature=macd_hist_mean_q; technical_snapshot.macd_hist_mean_q].
- Giá cao hơn SMA20 khoảng `4.053872%`, phản ánh vị trí trên đường trung bình ngắn hạn [top_drivers.feature=price_vs_sma20; technical_snapshot.price_vs_sma20].
- Lợi suất kỳ hiện tại `31.193751%` và lợi suất trễ hai kỳ `22.022929%`, cùng được mô hình gắn hướng hỗ trợ tín hiệu tăng [top_drivers; technical_snapshot.return_q; technical_snapshot.return_2q_ago].
- Thay đổi khối lượng `38.574437%`, được dùng như chỉ báo mức độ quan tâm thị trường [top_drivers.feature=volume_change_q; technical_snapshot.volume_change_q].
- Lợi suất trung bình ngày `0.511013%`, hỗ trợ xu hướng ngắn trong kỳ [top_drivers.feature=return_mean_daily; technical_snapshot.return_mean_daily].

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ `40.646087%`; mô hình gắn cờ rủi ro biến động cao [top_drivers.feature=price_range_q; technical_snapshot.price_range_q].
- Lợi suất kỳ trước âm `-8.263695%`, được mô hình phân loại là yếu hoặc tiêu cực [top_drivers.feature=return_prev_q; technical_snapshot.return_prev_q].
- Tín hiệu phụ thuộc mô hình kỹ thuật `technical_Config_A_from_existing_pipeline`; pack không cung cấp phân tích cơ bản [ml_signal.model_name; card_input_variant].
- Evidence tin tức chưa đủ mạnh: dữ liệu tin tức bị loại khỏi pack cho ablation [data_quality_flags.news_evidence_removed_for_ablation; guardrails.news_evidence_excluded].
- Không có nội dung toàn văn để bổ sung diễn giải; chỉ có metadata audit nếu được cung cấp [evidence pack rule].

## 5. Trigger theo dõi

- Theo dõi cập nhật `pred_label`, `pred_proba_up`, `signal_class` và `rank_in_period` ở kỳ tín hiệu kế tiếp [ml_signal].
- Theo dõi RSI, MACD histogram, `price_vs_sma20` và SMA20 [technical_snapshot; top_drivers].
- Theo dõi lợi suất kỳ, lợi suất kỳ trước, lợi suất trung bình ngày và thay đổi khối lượng [technical_snapshot].
- Đánh giá lại mức rủi ro khi `price_range_q` tăng hoặc tín hiệu động lượng suy yếu [technical_snapshot.price_range_q; top_drivers].
- Bổ sung evidence định tính trước review nếu có; hiện evidence tin tức chưa đủ mạnh [data_quality_flags.news_evidence_removed_for_ablation].

## 6. Thời điểm review

- Review vào kỳ kế tiếp hoặc cuối quý kế tiếp, phù hợp `holding_horizon=next_quarter_or_period_return_in_signals` [holding_horizon].
- Ngày lập decision card: `2026-03-31` [decision_date].

## 7. Kết luận hỗ trợ quyết định

- GMD có tín hiệu kỹ thuật tích cực, xác suất mô hình cao và xếp hạng đầu kỳ `2026Q1` [ml_signal].
- Động lượng hiện tại và vị trí giá trên SMA20 hỗ trợ tín hiệu; biến động cao và lợi suất kỳ trước âm cần theo dõi [technical_snapshot; top_drivers].
- Có thể dùng card làm cơ sở theo dõi và review lại ở kỳ kế tiếp. Evidence tin tức chưa đủ mạnh; chưa đủ cơ sở cho kết luận chắc chắn.

## 8. Disclaimer

- Nội dung chỉ hỗ trợ phân tích học thuật và quyết định.
- Không phải khuyến nghị đầu tư.
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Kết luận chỉ dùng evidence trong pack tại ngày `2026-03-31`; không sử dụng dữ liệu sau quyết định [guardrails.no_post_decision_data].

---

## 2026Q1_EVF_02

## 1. Tóm tắt tín hiệu

- EVF nhận nhãn **“Buy Candidate”**, xác suất tín hiệu tăng từ mô hình **0,99164**, xếp hạng **2 trong kỳ 2026Q1**. Evidence: `ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.signal_class`, `ml_signal.rank_in_period`.
- Động lượng kỹ thuật hiện nghiêng tích cực: lợi suất kỳ hiện tại **0,32093**, MACD histogram trung bình **0,04729**, giá cao hơn SMA20 **2,47%**. Evidence: `technical_snapshot.return_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`.
- Biến động kỳ ở mức đáng lưu ý: `price_range_q = 0,36992`. Evidence: `technical_snapshot.price_range_q`.
- Evidence tin tức chưa đủ mạnh vì news evidence bị loại khỏi pack. Evidence: `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`.

## 2. Luận điểm đầu tư chính

- EVF có tín hiệu kỹ thuật tích cực theo mô hình, dựa trên RSI cuối kỳ **56,98**, MACD histogram dương, giá trên SMA20 và lợi suất kỳ hiện tại dương. Evidence: `top_drivers`, `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.return_q`.
- Tín hiệu có hỗ trợ từ quán tính lịch sử và thanh khoản: lợi suất hai kỳ trước **0,27273**, thay đổi khối lượng **0,76001**. Evidence: `technical_snapshot.return_2q_ago`, `technical_snapshot.volume_change_q`.
- Luận điểm chỉ dựa trên mô hình và dữ liệu kỹ thuật; chưa có đủ evidence định tính từ tin tức. Evidence: `card_input_variant`, `data_quality_flags.news_evidence_removed_for_ablation`.

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ **56,98** là driver kỹ thuật quan trọng nhất trong mô hình. Evidence: `top_drivers[0]`, `technical_snapshot.rsi_end_q`.
- MACD histogram trung bình dương **0,04729**, hỗ trợ tín hiệu động lượng. Evidence: `top_drivers[1]`, `technical_snapshot.macd_hist_mean_q`.
- Giá cao hơn SMA20 **2,47%**, phản ánh trạng thái kỹ thuật trên đường trung bình. Evidence: `top_drivers[2]`, `technical_snapshot.price_vs_sma20`.
- Lợi suất kỳ hiện tại **32,09%** và lợi suất hai kỳ trước **27,27%**, hỗ trợ tín hiệu quán tính. Evidence: `top_drivers[4]`, `top_drivers[3]`, `technical_snapshot.return_q`, `technical_snapshot.return_2q_ago`.
- Khối lượng thay đổi **76,00%**, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ. Evidence: `top_drivers[6]`, `technical_snapshot.volume_change_q`.

## 4. Yếu tố cần lưu ý / rủi ro

- Lợi suất kỳ trước âm **-22,18%**, tạo tín hiệu động lượng không đồng nhất giữa các kỳ. Evidence: `top_drivers[5]`, `technical_snapshot.return_prev_q`.
- Biên độ giá kỳ **36,99%**, cho thấy biến động đáng kể. Evidence: `top_drivers[8]`, `technical_snapshot.price_range_q`.
- Tín hiệu tăng phụ thuộc mô hình kỹ thuật; evidence định tính từ tin tức bị loại khỏi pack. Evidence: `ml_signal.model_name`, `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`.
- Mô hình xếp EVF hạng **2**, không phải hạng 1 trong kỳ. Evidence: `ml_signal.rank_in_period`.
- Chưa có cơ sở từ pack để đánh giá yếu tố cơ bản, sự kiện doanh nghiệp hoặc rủi ro tin tức. Evidence: `data_quality_flags.missing_fields`, `data_quality_flags.news_evidence_removed_for_ablation`.

## 5. Trigger theo dõi

- Theo dõi RSI cuối kỳ so với mức nền **56,98**. Evidence: `technical_snapshot.rsi_end_q`.
- Theo dõi MACD histogram trung bình so với mức **0,04729**. Evidence: `technical_snapshot.macd_hist_mean_q`.
- Theo dõi vị trí giá so với SMA20 và mức nền `price_vs_sma20 = 0,02472`; SMA20 cuối kỳ là **13,8575**. Evidence: `technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`.
- Theo dõi thay đổi lợi suất giữa kỳ hiện tại **32,09%** và kỳ trước **-22,18%**. Evidence: `technical_snapshot.return_q`, `technical_snapshot.return_prev_q`.
- Theo dõi khối lượng so với mức thay đổi **76,00%** và biên độ giá **36,99%**. Evidence: `technical_snapshot.volume_change_q`, `technical_snapshot.price_range_q`.
- Bổ sung tin tức có cấu trúc gồm `article_summary`, `key_facts`, `risk_flags`, `event_type` nếu có nguồn evidence mới. Hiện evidence tin tức chưa đủ mạnh. Evidence: `data_quality_flags.news_evidence_removed_for_ablation`.

## 6. Thời điểm review

- Ngày lập card: **2026-03-31**. Evidence: `decision_date`.
- Review theo **kỳ kế tiếp / horizon `next_quarter_or_period_return_in_signals`**. Evidence: `holding_horizon`.
- Review sớm khi các trigger kỹ thuật trên thay đổi đáng kể so với mức nền hiện tại. Mức “đáng kể” chưa được định nghĩa trong evidence pack.

## 7. Kết luận hỗ trợ quyết định

- EVF hiện là **ứng viên theo dõi tích cực** theo mô hình kỹ thuật, không phải kết luận mua chắc chắn. Evidence: `ml_signal.signal_class`, `ml_signal.pred_proba_up`.
- Tín hiệu được hỗ trợ bởi RSI, MACD, vị trí giá trên SMA20, lợi suất kỳ hiện tại và thay đổi khối lượng. Evidence: `top_drivers`, `technical_snapshot`.
- Cần cân nhắc rủi ro biến động, tín hiệu lợi suất kỳ trước âm và thiếu evidence tin tức. Evidence: `technical_snapshot.price_range_q`, `technical_snapshot.return_prev_q`, `guardrails.news_evidence_excluded`.
- Bước tiếp theo: theo dõi trigger kỹ thuật, cập nhật evidence tin tức nếu xuất hiện, rồi review tại kỳ kế tiếp.

## 8. Disclaimer

- Card chỉ hỗ trợ phân tích học thuật và quyết định; không phải khuyến nghị đầu tư.
- Mô hình không bảo đảm kết quả.
- Card không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Phân tích không sử dụng dữ liệu sau ngày quyết định. Evidence: `guardrails.no_post_decision_data`.

---

## 2026Q1_DPM_03

## 1. Tóm tắt tín hiệu

- DPM được mô hình phân loại **“Buy Candidate”**, `pred_label = 1`, `pred_proba_up = 0.9718740266791716`, xếp hạng `3` trong kỳ. [Ref: `ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.signal_class`, `ml_signal.rank_in_period`]
- Tín hiệu kỹ thuật nghiêng tích cực qua RSI, MACD histogram, khối lượng. Giá dưới SMA20 và biên độ giá cao tạo tín hiệu trái chiều. [Ref: `top_drivers`, `technical_snapshot`]
- Evidence tin tức chưa đủ mạnh: pack ghi nhận news evidence bị loại khỏi phân tích. [Ref: `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`]

## 2. Luận điểm đầu tư chính

- DPM là ứng viên cần theo dõi thêm vì mô hình kỹ thuật gắn nhãn **“Buy Candidate”** với xác suất lớp tăng cao. Đây là tín hiệu mô hình, không phải kết luận chắc chắn. [Ref: `ml_signal.signal_class`, `ml_signal.pred_proba_up`]
- Luận điểm dựa chủ yếu trên động lượng kỹ thuật: RSI cuối kỳ, MACD histogram trung bình và thay đổi khối lượng cùng hỗ trợ tín hiệu. [Ref: `top_drivers.feature`, `top_drivers.direction`]
- Tín hiệu chưa đồng nhất vì giá vẫn ở dưới SMA20 và biên độ giá trong kỳ cao. [Ref: `technical_snapshot.price_vs_sma20`, `technical_snapshot.price_range_q`]

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ `52.11230805457214` là driver kỹ thuật quan trọng nhất và được mô hình đánh dấu hỗ trợ tín hiệu tăng. [Ref: `top_drivers.rsi_end_q`, `technical_snapshot.rsi_end_q`]
- MACD histogram trung bình kỳ `0.0901514938262197` phản ánh động lượng được mô hình xem là hỗ trợ. [Ref: `top_drivers.macd_hist_mean_q`, `technical_snapshot.macd_hist_mean_q`]
- Thay đổi khối lượng kỳ `1.8162517054285672` được mô hình xem là yếu tố hỗ trợ, phản ánh mức độ quan tâm thị trường. [Ref: `top_drivers.volume_change_q`, `technical_snapshot.volume_change_q`]
- Xếp hạng tín hiệu ở vị trí `3` trong kỳ cho thấy DPM nằm trong nhóm tín hiệu nổi bật của universe. [Ref: `ml_signal.rank_in_period`, `universe`]

## 4. Yếu tố cần lưu ý / rủi ro

- `price_vs_sma20 = -0.024509803921568513`, cho thấy vị trí giá dưới SMA20; đây là driver yếu hoặc tiêu cực. [Ref: `top_drivers.price_vs_sma20`, `technical_snapshot.price_vs_sma20`]
- `price_range_q = 0.5050327372227108` được mô hình gắn cờ rủi ro biến động cao. [Ref: `top_drivers.price_range_q`, `technical_snapshot.price_range_q`]
- Tín hiệu mô hình không đồng nghĩa với kết quả chắc chắn; xác suất mô hình chỉ phản ánh đầu ra của `technical_Config_A_from_existing_pipeline`. [Ref: `ml_signal.model_name`, `ml_signal.pred_proba_up`]
- Evidence định tính từ tin tức không có trong pack; evidence tin tức chưa đủ mạnh để bổ trợ luận điểm. [Ref: `data_quality_flags.news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`]

## 5. Trigger theo dõi

- Kiểm tra lại RSI cuối kỳ và MACD histogram trung bình để phát hiện suy yếu động lượng. [Ref: `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`]
- Theo dõi `price_vs_sma20`; giá trị âm tiếp diễn giữ nguyên điểm yếu kỹ thuật hiện tại. [Ref: `technical_snapshot.price_vs_sma20`]
- Theo dõi thay đổi khối lượng; mức hỗ trợ có thể yếu đi nếu chỉ báo này giảm trong lần cập nhật sau. [Ref: `technical_snapshot.volume_change_q`]
- Theo dõi `price_range_q` để đánh giá biến động và mức rủi ro kỹ thuật. [Ref: `technical_snapshot.price_range_q`]
- Cập nhật lại nhãn, xác suất mô hình và thứ hạng tín hiệu khi có kỳ dữ liệu mới. [Ref: `ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`]

## 6. Thời điểm review

- Ngày lập card: `2026-03-31`. [Ref: `decision_date`]
- Review tại kỳ cập nhật kế tiếp theo khung `next_quarter_or_period_return_in_signals`. [Ref: `holding_horizon`]
- Review sớm nếu các trigger kỹ thuật trên thay đổi đáng kể.

## 7. Kết luận hỗ trợ quyết định

- DPM có tín hiệu mô hình tích cực và đáng đưa vào danh sách theo dõi hoặc đánh giá thêm. [Ref: `ml_signal.signal_class`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`]
- Chưa đủ cơ sở để kết luận hành động đầu tư chắc chắn vì giá dưới SMA20, biến động cao và thiếu evidence tin tức định tính. [Ref: `technical_snapshot.price_vs_sma20`, `technical_snapshot.price_range_q`, `data_quality_flags.news_evidence_removed_for_ablation`]

## 8. Disclaimer

- Decision card chỉ tổng hợp evidence trong pack, phục vụ hỗ trợ quyết định học thuật.
- Không phải khuyến nghị đầu tư.
- Tín hiệu mô hình không bảo đảm kết quả.
- Không dùng card này như kết luận độc lập khi evidence mới hoặc chất lượng evidence thay đổi.

---

## 2026Q1_DCM_04

## 1. Tóm tắt tín hiệu

- DCM được mô hình gắn nhãn **“Buy Candidate”**; xác suất lớp tăng `0.9584405436818748`, xếp hạng `4` trong kỳ `2026Q1`. Tham chiếu: `ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`.
- Tín hiệu chủ yếu dựa trên dữ liệu kỹ thuật và mô hình ML. Tham chiếu: `card_input_variant`, `data_quality_flags.news_evidence_removed_for_ablation`.
- Động lượng kỳ hiện tại tích cực, nhưng kỳ trước âm và biên độ giá cao. Tham chiếu: `technical_snapshot.return_q`, `technical_snapshot.return_prev_q`, `technical_snapshot.price_range_q`.

## 2. Luận điểm đầu tư chính

- Tín hiệu ML nghiêng về chiều tăng, với xác suất mô hình cao và thứ hạng `4`. Tham chiếu: `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`.
- Nền tảng kỹ thuật hỗ trợ tín hiệu gồm RSI cuối kỳ, MACD histogram, vị trí giá so với SMA20, lợi suất kỳ hiện tại và thay đổi khối lượng. Tham chiếu: `top_drivers`, `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.return_q`, `technical_snapshot.volume_change_q`.
- Luận điểm chưa đủ mạnh để xem là tín hiệu chắc chắn do lợi suất kỳ trước âm, biến động giá cao và thiếu evidence tin tức định tính. Tham chiếu: `technical_snapshot.return_prev_q`, `technical_snapshot.price_range_q`, `data_quality_flags.news_evidence_removed_for_ablation`.

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ `58.62978197421903`, là driver kỹ thuật quan trọng nhất của mô hình. Tham chiếu: `top_drivers.feature=rsi_end_q`, `technical_snapshot.rsi_end_q`.
- MACD histogram trung bình `0.14499223318401344`, hỗ trợ động lượng xu hướng. Tham chiếu: `top_drivers.feature=macd_hist_mean_q`, `technical_snapshot.macd_hist_mean_q`.
- Giá cao hơn SMA20 khoảng `0.03128002562186391`, phản ánh trạng thái kỹ thuật tích cực hơn đường trung bình. Tham chiếu: `top_drivers.feature=price_vs_sma20`, `technical_snapshot.price_vs_sma20`.
- Lợi suất kỳ hiện tại `0.44827586206896536` và lợi suất trễ hai kỳ `0.1106128550074737` hỗ trợ động lượng lịch sử. Tham chiếu: `technical_snapshot.return_q`, `technical_snapshot.return_2q_ago`.
- Thay đổi khối lượng `1.7649475854447902`, hỗ trợ tín hiệu về mức độ quan tâm thị trường. Tham chiếu: `top_drivers.feature=volume_change_q`, `technical_snapshot.volume_change_q`.
- Evidence tin tức chưa đủ mạnh vì news evidence bị loại khỏi bộ dữ liệu. Tham chiếu: `data_quality_flags.news_evidence_removed_for_ablation=true`, `guardrails.news_evidence_excluded=true`.

## 4. Yếu tố cần lưu ý / rủi ro

- Lợi suất kỳ trước âm `-0.10655737704918028`, tạo tín hiệu động lượng không đồng nhất. Tham chiếu: `top_drivers.feature=return_prev_q`, `technical_snapshot.return_prev_q`.
- Biên độ giá trong kỳ `0.4956415583302991`, cho thấy biến động cao. Tham chiếu: `top_drivers.feature=price_range_q`, `technical_snapshot.price_range_q`.
- Tín hiệu phụ thuộc dữ liệu kỹ thuật và mô hình ML; không có lớp xác nhận từ tin tức trong evidence pack. Tham chiếu: `card_input_variant=ml_only`, `data_quality_flags.news_evidence_removed_for_ablation=true`.
- Xác suất mô hình là đầu ra mô hình, không phải cam kết kết quả. Tham chiếu: `ml_signal.pred_proba_up`, `guardrails.not_investment_advice=true`.

## 5. Trigger theo dõi

- Theo dõi thay đổi nhãn và xác suất ML. Tham chiếu: `ml_signal.signal_class`, `ml_signal.pred_proba_up`.
- Theo dõi RSI, MACD histogram và vị trí giá so với SMA20. Tham chiếu: `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`.
- Theo dõi lợi suất kỳ mới, lợi suất kỳ trước và biên độ giá. Tham chiếu: `technical_snapshot.return_q`, `technical_snapshot.return_prev_q`, `technical_snapshot.price_range_q`.
- Theo dõi thay đổi khối lượng và thứ hạng tín hiệu trong universe. Tham chiếu: `technical_snapshot.volume_change_q`, `ml_signal.rank_in_period`, `universe`.
- Cập nhật khi xuất hiện evidence tin tức đủ trường `article_summary`, `key_facts`, `risk_flags`, `event_type`; hiện chưa có trong pack. Tham chiếu: `data_quality_flags.news_evidence_removed_for_ablation=true`.

## 6. Thời điểm review

- Review vào **cuối quý kế tiếp hoặc kỳ tín hiệu kế tiếp**, theo `holding_horizon=next_quarter_or_period_return_in_signals`.
- Tại review, đối chiếu lại tín hiệu ML, nhóm driver kỹ thuật, biến động và evidence mới. Tham chiếu: `holding_horizon`, `top_drivers`, `technical_snapshot`.

## 7. Kết luận hỗ trợ quyết định

- DCM có tín hiệu kỹ thuật-ML nghiêng tích cực tại ngày `2026-03-31`, với nhãn **“Buy Candidate”** và xác suất mô hình `0.9584405436818748`. Tham chiếu: `decision_date`, `ml_signal.signal_class`, `ml_signal.pred_proba_up`.
- Có thể đưa DCM vào danh sách theo dõi hoặc quy trình đánh giá tiếp theo, không xem đây là quyết định mua chắc chắn.
- Cần giữ điều kiện review vì lợi suất kỳ trước âm, biến động cao và evidence tin tức chưa đủ mạnh. Tham chiếu: `technical_snapshot.return_prev_q`, `technical_snapshot.price_range_q`, `data_quality_flags.news_evidence_removed_for_ablation`.

## 8. Disclaimer

- Decision card chỉ hỗ trợ nghiên cứu và ra quyết định; không phải tư vấn đầu tư. Tham chiếu: `guardrails.not_investment_advice=true`.
- Không có bảo đảm về kết quả hoặc lợi nhuận.
- Card dùng dữ liệu có trong evidence pack tại `decision_date=2026-03-31`; không sử dụng dữ liệu sau thời điểm quyết định. Tham chiếu: `guardrails.no_post_decision_data=true`.

---

## 2026Q1_REE_05

## 1. Tóm tắt tín hiệu

- REE nhận nhãn `Buy Candidate` từ mô hình `technical_Config_A_from_existing_pipeline`; `pred_label = 1`, `pred_proba_up = 0.9533`, xếp hạng 5 trong kỳ `2026Q1` (`ml_signal`, `rank_in_period`).
- Tín hiệu nghiêng tích cực, nhưng chỉ phản ánh mô hình kỹ thuật. Không phải xác nhận kết quả tương lai.

## 2. Luận điểm đầu tư chính

- Động lượng kỹ thuật hỗ trợ tín hiệu tăng: RSI cuối kỳ 59.09, MACD histogram trung bình dương 0.1528, giá cao hơn SMA20 khoảng 5.29% (`rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`).
- Mức thay đổi khối lượng 1.8714 hỗ trợ quan sát rằng mức độ quan tâm thị trường tăng trong kỳ (`volume_change_q`).
- Luận điểm còn phụ thuộc tín hiệu kỹ thuật; evidence pack không có evidence tin tức hoặc phân tích định tính đủ mạnh (`news_evidence_removed_for_ablation`, `guardrails.news_evidence_excluded`).

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ 59.09 hỗ trợ tín hiệu mô hình (`rsi_end_q`).
- MACD histogram trung bình dương 0.1528 phản ánh động lượng tích cực (`macd_hist_mean_q`).
- Giá cao hơn SMA20 5.29%, hỗ trợ trạng thái xu hướng ngắn hạn (`price_vs_sma20`).
- Khối lượng thay đổi 1.8714, hỗ trợ tín hiệu quan tâm thị trường (`volume_change_q`).
- Mô hình xếp REE ở hạng 5 trong kỳ (`rank_in_period`).

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ 26.34% cho thấy biến động đáng kể (`price_range_q`).
- Một số chỉ báo động lượng trễ yếu: `return_2q_ago = -2.96%` và `return_prev_q = -7.30%` (`return_2q_ago`, `return_prev_q`).
- Tín hiệu phụ thuộc mô hình kỹ thuật; pack không cung cấp luận cứ cơ bản hoặc tin tức để kiểm chứng (`model_name`, `news_evidence_removed_for_ablation`).
- Evidence tin tức chưa đủ mạnh; không có `article_summary`, `key_facts`, `risk_flags` hoặc `event_type` để đánh giá thêm (`data_quality_flags`, `guardrails.news_evidence_excluded`).
- `pred_proba_up = 0.9533` là xác suất mô hình, không phải bảo đảm kết quả (`pred_proba_up`).

## 5. Trigger theo dõi

- Theo dõi RSI cuối kỳ, MACD histogram và vị trí giá so với SMA20 (`rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`).
- Xem xét lại khi các chỉ báo không còn hỗ trợ hướng tăng hoặc giá không còn duy trì trên SMA20 (`macd_hist_mean_q`, `price_vs_sma20`).
- Theo dõi thay đổi khối lượng và biên độ giá; biến động mở rộng cùng tín hiệu động lượng yếu là cảnh báo cần đánh giá lại (`volume_change_q`, `price_range_q`).
- Cập nhật nếu xuất hiện evidence tin tức có `article_summary`, `key_facts`, `risk_flags` hoặc `event_type`; hiện pack chưa có (`news_evidence_removed_for_ablation`).

## 6. Thời điểm review

- Review vào cuối quý kế tiếp hoặc kỳ tín hiệu kế tiếp, theo `holding_horizon`.
- Review sớm khi trigger kỹ thuật suy yếu hoặc biến động tăng (`holding_horizon`, `price_range_q`, `macd_hist_mean_q`, `price_vs_sma20`).

## 7. Kết luận hỗ trợ quyết định

- REE có tín hiệu kỹ thuật tích cực và được mô hình xếp vào nhóm `Buy Candidate` (`signal_class`, `pred_label`, `rank_in_period`).
- Có thể đưa vào danh sách theo dõi để đánh giá tiếp.
- Chưa đủ cơ sở cho kết luận đầu tư chắc chắn do biến động giá cao, động lượng trễ còn yếu và thiếu evidence tin tức định tính.

## 8. Disclaimer

- Decision card chỉ dùng evidence trong pack, phục vụ hỗ trợ quyết định nghiên cứu.
- Không phải khuyến nghị đầu tư.
- Không dự báo giá tuyệt đối, không bảo đảm kết quả, không sử dụng dữ liệu sau ngày quyết định `2026-03-31`.
