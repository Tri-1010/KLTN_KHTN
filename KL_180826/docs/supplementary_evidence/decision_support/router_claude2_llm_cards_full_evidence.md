# LLM Decision Cards — llm_full_evidence

> Generated with anthropic-python model `claude-opus` from prompt-safe `full_evidence` evidence packs. Outcome fields removed.


---

## 2025Q1_SCR_01

## 1. Tóm tắt tín hiệu

- SCR có tín hiệu định lượng tích cực: `pred_label = 1`, `pred_proba_up = 0.999444145459264`, xếp hạng 1 trong kỳ, phân loại `Buy Candidate`. [ml_signal]
- Động lượng kỹ thuật hỗ trợ: RSI cuối kỳ 61.8393, MACD histogram trung bình 0.0070, giá cao hơn SMA20 2.525%, khối lượng tăng 69.54%. [rsi_end_q], [macd_hist_mean_q], [price_vs_sma20], [volume_change_q]
- Tin tức gần đây tập trung vào nhận chuyển nhượng tài sản, ĐHCĐ thường niên, thay đổi người liên quan người nội bộ và từ nhiệm thành viên HĐQT. [N001–N005]
- Tin tức có độ khớp ticker `partial`, trích xuất `partial`; nhiều bài thiếu `key_facts`. Evidence tin tức chưa đủ mạnh. [data_quality_flags], [N001–N005]

## 2. Luận điểm đầu tư chính

- Tín hiệu kỹ thuật nghiêng về hướng tích cực, nhờ RSI, MACD, vị trí giá trên SMA20 và khối lượng tăng. [ml_signal], [rsi_end_q], [macd_hist_mean_q], [price_vs_sma20], [volume_change_q]
- SCR phù hợp đưa vào danh sách theo dõi hoặc đánh giá tiếp trong kỳ kế tiếp; chưa đủ cơ sở kết luận mua chắc chắn. [ml_signal], [guardrails.initial_prompt_safe]
- Luận điểm định tính còn yếu. Các tin hiện có chủ yếu là công bố sự kiện, chưa cung cấp đủ chi tiết về tác động tài chính hoặc vận hành. [N001–N005], [data_quality_flags]

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ 61.8393 được mô hình xác định là driver quan trọng, hỗ trợ tín hiệu tăng. [rsi_end_q], [top_drivers]
- MACD histogram trung bình dương ở mức 0.007025, phản ánh động lượng tích cực trong mô hình. [macd_hist_mean_q], [top_drivers]
- Giá cao hơn SMA20 2.525%, hỗ trợ trạng thái xu hướng ngắn hạn. [price_vs_sma20], [sma20_end]
- Khối lượng trong kỳ tăng 69.54%, cho thấy mức độ quan tâm thị trường cao hơn theo logic mô hình. [volume_change_q], [top_drivers]
- Mô hình xếp SCR hạng 1 trong kỳ với nhãn `Buy Candidate`. [ml_signal]

## 4. Yếu tố cần lưu ý / rủi ro

- Động lượng trễ hai kỳ là yếu hoặc âm theo mô hình, tạo tín hiệu đối trọng với động lượng hiện tại. [return_2q_ago], [top_drivers]
- Biên độ giá trong kỳ ở mức 0.3138401, cho thấy biến động cần được theo dõi. [price_range_q]
- N005 ghi nhận HĐQT tiếp nhận đơn từ nhiệm của thành viên HĐQT; evidence pack không nêu tác động tiếp theo. [N005]
- N001 ghi nhận nghị quyết về nhận chuyển nhượng tài sản; pack không có giá trị, điều khoản hoặc tác động tài chính. [N001]
- N004 ghi nhận thay đổi người có liên quan của người nội bộ; pack không cung cấp chi tiết để đánh giá hướng tác động. [N004]
- N002 và N003 chỉ ghi nhận thông tin ngày ĐKCC/ngày GDKHQ dự ĐHCĐ thường niên 2025; key fact có độ tin cậy thấp và hướng trung tính. [N002], [N003]
- Chất lượng khớp ticker ở mức `mixed`; từng bài có `match_confidence = partial`, extraction `partial`. [data_quality_flags], [N001–N005]

## 5. Trigger theo dõi

- Mô hình đổi `pred_label`, giảm xác suất mô hình, hoặc mất vị trí xếp hạng cao. [ml_signal]
- RSI giảm đáng kể so với 61.8393, MACD histogram mất trạng thái dương, hoặc giá không còn cao hơn SMA20. [rsi_end_q], [macd_hist_mean_q], [price_vs_sma20]
- Khối lượng đảo chiều so với mức tăng 69.54%. [volume_change_q]
- Công bố thêm chi tiết về nhận chuyển nhượng tài sản. [N001]
- Công bố kết quả hoặc nội dung liên quan ĐHCĐ thường niên 2025. [N002], [N003]
- Công bố cập nhật về đơn từ nhiệm thành viên HĐQT hoặc thay đổi người liên quan người nội bộ. [N004], [N005]

## 6. Thời điểm review

- Review vào cuối quý kế tiếp, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm khi xuất hiện trigger kỹ thuật hoặc công bố doanh nghiệp nêu trên. [ml_signal], [N001–N005]
- Mốc thông tin hiện tại: 2025-03-31; cutoff tin tức: 2025-03-31. [decision_date], [guardrails.news_cutoff]

## 7. Kết luận hỗ trợ quyết định

- SCR có tín hiệu định lượng mạnh và đứng hạng 1 trong kỳ. [ml_signal]
- Tín hiệu này phù hợp với hành động theo dõi, kiểm chứng thêm, không phải khuyến nghị mua chắc chắn. [ml_signal], [guardrails.not_investment_advice]
- Evidence tin tức chưa đủ mạnh để xác nhận luận điểm định lượng; cần chờ chi tiết về tài sản, quản trị và ĐHCĐ. [N001–N005], [data_quality_flags]
- Không đưa ra dự báo giá tuyệt đối hoặc cam kết lợi nhuận.

## 8. Disclaimer

- Decision card chỉ hỗ trợ phân tích học thuật từ evidence pack tại ngày 2025-03-31. [decision_date]
- Không phải tư vấn đầu tư. [guardrails.not_investment_advice]
- Không sử dụng dữ liệu sau ngày quyết định. [guardrails.no_post_decision_data]
- Xác suất mô hình không bảo đảm kết quả thực tế. [ml_signal]

---

## 2025Q1_VHM_02

## 1. Tóm tắt tín hiệu

- VHM được mô hình phân loại **“Buy Candidate”**, xác suất tín hiệu tăng `0.9990863674924828`, xếp hạng 2 trong kỳ. Đây là tín hiệu mô hình, không phải khuyến nghị chắc chắn. [`ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`]
- Động lượng kỹ thuật hỗ trợ: MACD histogram dương `0.1856`; giá cao hơn SMA20 `7.68%`. [`macd_hist_mean_q`, `price_vs_sma20`]
- Rủi ro kỹ thuật nổi bật: RSI cuối kỳ `86.14`, trạng thái quá mua; khối lượng giảm `37.10%`; biên độ giá kỳ `35.11%`. [`rsi_end_q`, `volume_change_q`, `price_range_q`]
- Tin tức ghi nhận tiến triển dự án Cam Ranh và doanh thu quý 4/2024 tăng theo bài tổng hợp VNDirect. Tuy nhiên, tin tức có độ tin cậy không đồng đều; **evidence tin tức chưa đủ mạnh** để kết luận độc lập. [N002, N003; `data_quality_flags.ticker_matching_confidence`; N004, N005]

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình và động lượng kỹ thuật đang nghiêng tích cực. [`ml_signal`, `macd_hist_mean_q`, `price_vs_sma20`]
- Tín hiệu bị giảm chất lượng bởi RSI quá mua, khối lượng suy giảm và biến động giá cao. [`rsi_end_q`, `volume_change_q`, `price_range_q`]
- Dữ liệu doanh nghiệp cho thấy nền tảng bàn giao và dự án mới là yếu tố trọng tâm, nhưng bằng chứng tin tức hiện cần xác nhận thêm. [N002 F01–F05, N003 F02–F05]

## 3. Yếu tố hỗ trợ

- Mô hình ghi nhận tín hiệu **“Buy Candidate”** với xác suất mô hình `0.9990863674924828`. [`ml_signal.pred_proba_up`, `ml_signal.signal_class`]
- MACD histogram trung bình dương, giá nằm trên SMA20. [`macd_hist_mean_q`, `price_vs_sma20`]
- N002 ghi nhận VHM cùng Công ty CP Đầu tư Cam Ranh và VinES là các đơn vị duy nhất đáp ứng yêu cầu sơ bộ về năng lực, kinh nghiệm tại dự án. [N002 F01]
- N002 ghi nhận địa phương chỉ đạo đẩy nhanh giải phóng mặt bằng, hướng tới tiến độ khởi công tháng 4/2025. Đây là thông tin kế hoạch, chưa phải xác nhận hoàn tất. [N002 F02]
- N003 ghi nhận doanh thu thuần quý 4/2024 đạt `32.874 tỷ đồng`, tăng `21,6%` so với cùng kỳ; tăng trưởng gắn với bàn giao tại các dự án lớn. [N003 F03–F05]

## 4. Yếu tố cần lưu ý / rủi ro

- RSI `86.14` cho thấy trạng thái quá mua, làm tăng rủi ro điều chỉnh kỹ thuật. [`rsi_end_q`]
- Khối lượng giảm `37.10%`, trong khi biên độ giá kỳ ở mức `35.11%`; tín hiệu động lượng cần được xác nhận thêm. [`volume_change_q`, `price_range_q`]
- N003 nêu sự gián đoạn trong chu kỳ bàn giao dự án; doanh thu và lợi nhuận phụ thuộc đáng kể vào tiến độ các đại đô thị lớn. [N003 F02, N003 F05]
- N001 gắn các cờ `audit_issue`, `governance`, `legal_risk`; dữ liệu bài viết chỉ nêu báo cáo tài chính hợp nhất kiểm toán và thù lao Hội đồng quản trị `17,1 tỷ đồng`, chưa cung cấp chi tiết đủ để kết luận có sai phạm. [N001, N001 F04–F05]
- N002 cũng gắn cờ `debt_risk`, `governance`, `audit_issue`, nhưng các key facts không cung cấp số liệu nợ hoặc chi tiết kiểm toán. Không suy diễn vượt dữ liệu. [N002, N002 F01–F05]
- N004 và N005 có trạng thái trích xuất `partial`, key facts độ tin cậy thấp; chỉ xác nhận thông tin ngày đăng ký quyền tham dự ĐHĐCĐ 2025. [N004, N005]
- `ticker_matching_confidence` ở mức `mixed`; cần kiểm tra thủ công các tin tức có độ liên quan thấp hoặc cờ rủi ro không khớp nội dung. [`data_quality_flags.ticker_matching_confidence`, N001, N002, N003]

## 5. Trigger theo dõi

- Cập nhật lại `signal_class`, `pred_proba_up`, RSI, MACD, vị trí giá so với SMA20 và khối lượng trong kỳ tín hiệu tiếp theo. [`ml_signal`, `rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q`]
- Kiểm tra xác nhận giải phóng mặt bằng và thông tin khởi công dự án Cam Ranh. [N002 F02]
- Theo dõi công bố tiếp theo liên quan ĐHĐCĐ thường niên 2025; N004 và N005 hiện mới ghi nhận ngày đăng ký quyền. [N004, N005]
- Theo dõi cập nhật doanh thu, bàn giao và tiến độ các đại đô thị được nêu trong N003. [N003 F02–F05]
- Kiểm tra công bố giải trình nếu xuất hiện thông tin cụ thể liên quan audit, governance hoặc legal risk. [N001, N002]

## 6. Thời điểm review

- Review cơ bản: **cuối quý kế tiếp hoặc theo kỳ tín hiệu trong pack**. [`holding_horizon`]
- Review sớm khi xuất hiện trigger về dự án, ĐHĐCĐ, báo cáo tài chính hoặc thay đổi mạnh ở RSI, MACD, SMA20, khối lượng. [N002, N004, N005, `technical_snapshot`]

## 7. Kết luận hỗ trợ quyết định

- VHM là ứng viên có tín hiệu mô hình tích cực, nhưng chưa đủ cơ sở cho kết luận mua chắc chắn.
- Trạng thái phù hợp với evidence hiện có: **theo dõi và chờ xác nhận** từ kỹ thuật, tiến độ dự án và công bố doanh nghiệp.
- RSI quá mua, khối lượng giảm, biến động cao và chất lượng tin tức không đồng đều cần được đặt ngang với tín hiệu mô hình. [`rsi_end_q`, `volume_change_q`, `price_range_q`, `data_quality_flags`, N001–N005]

## 8. Disclaimer

- Decision card chỉ hỗ trợ phân tích, không phải khuyến nghị đầu tư cá nhân.
- Tín hiệu mô hình không bảo đảm kết quả.
- Card chỉ dùng dữ liệu trong evidence pack, với thời điểm quyết định `2025-03-31` và news cutoff `2025-03-31`.
- Không đưa dự báo giá tuyệt đối, không cam kết lợi nhuận.

---

## 2025Q1_VIC_03

## 1. Tóm tắt tín hiệu

- VIC, ngày quyết định 31/03/2025. Mô hình gắn nhãn **“Buy Candidate”**, `pred_label = 1`, `pred_proba_up = 0.9981398250260798`, xếp hạng 3 trong kỳ. [ml_signal]
- Động lượng kỹ thuật tích cực: MACD histogram trung bình `0.1246856309080669`, giá trên SMA20 `0.1354070825910773`, khối lượng thay đổi `0.8264844950295648`. [technical_snapshot.macd_hist_mean_q; technical_snapshot.price_vs_sma20; technical_snapshot.volume_change_q]
- Rủi ro quá mua và biến động cao: RSI cuối kỳ `91.10431541618765`, biên độ giá trong kỳ `0.44185210651331414`. [technical_snapshot.rsi_end_q; technical_snapshot.price_range_q]
- Tin tức có tín hiệu hỗ trợ thị trường, nhưng ghi nhận rủi ro kiểm toán, pháp lý, quản trị và nợ. [N001; N002; N003; N004; N005]
- `ticker_matching_confidence = mixed`; một bài yêu cầu kiểm tra thủ công. [data_quality_flags.ticker_matching_confidence; N004.relevance_hint]

## 2. Luận điểm đầu tư chính

- Tín hiệu định lượng nghiêng tích cực, nhờ mô hình xếp VIC vào nhóm “Buy Candidate” và các chỉ báo MACD, vị trí giá trên SMA20, khối lượng cùng hỗ trợ tín hiệu. [ml_signal; technical_snapshot.macd_hist_mean_q; technical_snapshot.price_vs_sma20; technical_snapshot.volume_change_q]
- Tín hiệu chưa đồng thuận hoàn toàn. RSI ở mức `91.10431541618765` cảnh báo trạng thái quá mua; biên độ giá `0.44185210651331414` cho thấy rủi ro biến động. [top_drivers; technical_snapshot.rsi_end_q; technical_snapshot.price_range_q]
- Tin tức chưa đủ để xác nhận luận điểm cơ bản: có thông tin về hỗ trợ VinFast và nhà ở xã hội, nhưng đồng thời có cờ rủi ro kiểm toán, pháp lý, quản trị và nợ. [N001.risk_flags; N003.risk_flags; N004.risk_flags]
- **evidence tin tức chưa đủ mạnh** để thay thế đánh giá độc lập về chất lượng tài chính, dòng tiền hoặc tác động lợi nhuận.

## 3. Yếu tố hỗ trợ

- Mô hình định lượng ghi nhận tín hiệu hướng lên, với `pred_proba_up = 0.9981398250260798`. [ml_signal.pred_proba_up]
- MACD histogram trung bình dương `0.1246856309080669`, hỗ trợ luận điểm động lượng. [technical_snapshot.macd_hist_mean_q]
- Giá cuối kỳ cao hơn SMA20 theo trường `price_vs_sma20 = 0.1354070825910773`. [technical_snapshot.price_vs_sma20]
- Khối lượng thay đổi `0.8264844950295648`, cho thấy mức độ quan tâm thị trường cao hơn theo tín hiệu kỹ thuật. [technical_snapshot.volume_change_q]
- Tin ngày 25/03 ghi nhận nhóm VIC, VHM, VRE hỗ trợ VN-Index và thuộc nhóm dẫn đầu mức tăng trong VN30. Đây là tín hiệu thị trường, không phải xác nhận nền tảng doanh nghiệp. [N005.article_summary; N005.key_facts.F01–F03; N005.event_type]
- Vingroup công bố giá bán nhà ở xã hội đầu tiên tại Thanh Hóa; dự án gồm 280 căn, dự kiến bàn giao tháng 11/2025. Thông tin này chỉ xác nhận sự kiện dự án. [N004.article_summary; N004.key_facts.F01–F04]

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `91.10431541618765` ở vùng cao, tạo rủi ro quá mua và điều chỉnh kỹ thuật. [technical_snapshot.rsi_end_q; top_drivers]
- Biên độ giá trong kỳ `0.44185210651331414` cho thấy biến động cao. [technical_snapshot.price_range_q; top_drivers]
- VIC có tin giải trình chênh lệch BCTC kiểm toán năm 2024; bài có `extraction_status = partial`, độ tin cậy fact trung bình, cùng cờ `audit_issue` và `legal_risk`. [N001.article_summary; N001.key_facts.F01; N001.extraction_status; N001.risk_flags]
- Tin về quản trị ghi nhận tổng thù lao HĐQT hơn 12 tỷ đồng, tăng 4,45% so với 2023; bộ fact có độ tin cậy thấp đến trung bình và cờ `governance`, `legal_risk`. [N002.key_facts.F01–F05; N002.risk_flags]
- Chủ tịch tiếp tục tài trợ VinFast thêm 8.277 tỷ đồng, tổng hơn 27.000 tỷ đồng trong hai năm; bài không có `key_facts`, đồng thời gắn cờ `debt_risk`, `legal_risk`, `governance`. [N003.article_summary; N003.risk_flags; N003.key_facts]
- Dự án nhà ở xã hội Thanh Hóa có `relevance_hint = needs_manual_check`; các fact có độ tin cậy thấp và bài gắn cờ `debt_risk`, `governance`. [N004.relevance_hint; N004.key_facts; N004.risk_flags]
- Tín hiệu tin tức thị trường ngày 25/03 phản ánh diễn biến nhóm cổ phiếu, không cung cấp xác nhận về kết quả kinh doanh VIC. [N005.article_summary; N005.event_type]

## 5. Trigger theo dõi

- Kiểm tra văn bản giải trình chênh lệch BCTC kiểm toán năm 2024 và cập nhật cờ `audit_issue`, `legal_risk`. [N001]
- Theo dõi công bố quản trị, thù lao HĐQT và các thông tin pháp lý liên quan. [N002]
- Theo dõi các công bố liên quan tài trợ VinFast và rủi ro nợ. [N003]
- Kiểm tra tiến độ dự án nhà ở xã hội Thanh Hóa so với thông tin dự kiến bàn giao tháng 11/2025. [N004.key_facts.F02]
- Theo dõi RSI, MACD histogram, vị trí giá so với SMA20 và khối lượng. [technical_snapshot.rsi_end_q; technical_snapshot.macd_hist_mean_q; technical_snapshot.price_vs_sma20; technical_snapshot.volume_change_q]
- Kiểm tra lại mức độ liên quan của tin N004 trước khi dùng làm luận cứ. [N004.relevance_hint; data_quality_flags.ticker_matching_confidence]

## 6. Thời điểm review

- Review định kỳ: **quý kế tiếp**, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm khi xuất hiện cập nhật về BCTC kiểm toán, pháp lý, quản trị, tài trợ VinFast hoặc tiến độ dự án Thanh Hóa. [N001; N002; N003; N004]
- Ngày dữ liệu hiện tại: `2025-03-31`; news cutoff: `2025-03-31`. [decision_date; guardrails.news_cutoff]

## 7. Kết luận hỗ trợ quyết định

- VIC có tín hiệu định lượng tích cực và được mô hình xếp vào nhóm “Buy Candidate”. [ml_signal; technical_snapshot]
- RSI quá cao, biến động lớn và các cờ rủi ro tin tức làm giảm độ chắc chắn của tín hiệu. [technical_snapshot.rsi_end_q; technical_snapshot.price_range_q; N001; N002; N003; N004]
- Card phù hợp cho **theo dõi có điều kiện và review theo trigger**, không đủ cơ sở cho quyết định độc lập chỉ dựa trên tín hiệu này. [ml_signal; data_quality_flags; N001–N005]

## 8. Disclaimer

- Nội dung chỉ hỗ trợ nghiên cứu và quyết định; không phải khuyến nghị đầu tư. [guardrails.not_investment_advice]
- `pred_proba_up` là đầu ra mô hình, không bảo đảm diễn biến giá hoặc lợi nhuận. [ml_signal]
- Card không dự báo giá tuyệt đối, không cam kết lợi nhuận, không sử dụng dữ liệu sau ngày quyết định. [guardrails.initial_prompt_safe; guardrails.no_post_decision_data; guardrails.news_cutoff]

---

## 2025Q1_SHB_04

## 1. Tóm tắt tín hiệu

- SHB thuộc nhóm **“Buy Candidate”** theo mô hình `technical_Config_A_from_existing_pipeline`; `pred_label = 1`, `pred_proba_up = 0.9971`, xếp hạng 4 trong kỳ (`ml_signal`).
- Động lượng kỹ thuật tích cực: `return_q = 0.3479`, `macd_hist_mean_q = 0.0363`, `price_vs_sma20 = 0.1138`, `volume_change_q = 1.3341`.
- Tín hiệu có rủi ro quá mua: `rsi_end_q = 80.3284`; biến động kỳ ở mức cao theo `price_range_q = 0.3716`.
- Tin tức ghi nhận SHB hút dòng tiền, tăng liên tiếp trong ba tuần và xuất hiện trong nhóm cổ phiếu tăng tốt (`N001`, F03–F04; độ tin cậy thấp).
- Bối cảnh thị trường chưa rõ xu hướng, thanh khoản giảm (`N001`, F02, F05).
- `ticker_matching_confidence = mixed`; `N002` có trạng thái trích xuất `partial`, không có `key_facts`.

## 2. Luận điểm đầu tư chính

- Tín hiệu kỹ thuật và mô hình nghiêng tích cực trong kỳ: `signal_class = Buy Candidate`, `return_q = 0.3479`, `macd_hist_mean_q = 0.0363`, `price_vs_sma20 = 0.1138` (`ml_signal`, `top_drivers`).
- Dòng tiền và động lượng SHB nổi bật hơn mặt bằng tin tức gần đây: thanh khoản hơn 84 triệu đơn vị trong phiên 24/3; SHB tăng hơn 21% trong 7 phiên (`N004`, F01–F04).
- Luận điểm bị giảm độ tin cậy bởi trạng thái quá mua, biến động cao và thiếu xác nhận nền tảng cơ bản. **Evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản dài hơn (`rsi_end_q`, `price_range_q`, `N003`, `N004`).

## 3. Yếu tố hỗ trợ

- Mô hình ghi nhận tín hiệu tăng với xác suất mô hình `pred_proba_up = 0.9971`; đây là đầu ra mô hình, không phải bảo đảm kết quả (`ml_signal`).
- Động lượng kỳ hiện tại tích cực: `return_q = 0.3479`, `return_mean_daily = 0.0053` (`technical_snapshot`).
- MACD histogram trung bình và vị trí giá so với SMA20 cùng hỗ trợ tín hiệu tăng: `macd_hist_mean_q = 0.0363`, `price_vs_sma20 = 0.1138` (`top_drivers`).
- Khối lượng kỳ tăng theo `volume_change_q = 1.3341` (`technical_snapshot`).
- SHB tăng ba tuần liên tiếp, lần lượt 7%, 10% và 8% trong tuần gần nhất; tin có độ tin cậy thấp (`N001`, F04).
- SHB khớp lệnh hơn 84 triệu đơn vị, đứng đầu toàn ba sàn trong phiên được nêu (`N004`, F04).

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ ở mức 80.3284; chính mô hình gắn driver này với hướng `positive_but_overbought_risk` (`rsi_end_q`, `top_drivers`).
- Biên độ giá kỳ ở mức 0.3716; mô hình gắn với `risk_high_volatility` (`price_range_q`, `top_drivers`).
- Động lượng lịch sử không đồng nhất: `return_prev_q = -0.0729`, `return_2q_ago = -0.0095` (`technical_snapshot`, `top_drivers`).
- VN-Index giảm nhẹ, thanh khoản bình quân giảm tuần thứ hai liên tiếp; thị trường được mô tả chưa rõ xu hướng (`N001`, F01–F05).
- Một bài viết gắn các cờ `audit_issue`, `debt_risk`, `governance` cho SHB, nhưng `key_facts` không nêu chi tiết nguyên nhân hoặc mức độ (`N003`, `risk_flags`).
- Một bài viết khác cũng gắn `audit_issue`, `debt_risk`, `governance`, trong khi nội dung trích dẫn chủ yếu mô tả diễn biến giá và thanh khoản (`N004`, `risk_flags`).
- Thông tin điều chỉnh số lượng cổ phiếu đăng ký chỉ mang tính thông báo; bài có `extraction_status = partial`, không có `key_facts` (`N002`).
- Một số dữ kiện tin tức có độ tin cậy thấp; cần tránh xem diễn biến ngắn hạn như xác nhận nền tảng doanh nghiệp (`N001`, `N004`).

## 5. Trigger theo dõi

- Theo dõi RSI: `rsi_end_q = 80.3284`; rà soát nếu trạng thái quá mua tiếp diễn hoặc suy yếu (`technical_snapshot`, `top_drivers`).
- Theo dõi `macd_hist_mean_q = 0.0363` và `price_vs_sma20 = 0.1138`; rà soát khi hai driver này đảo chiều (`top_drivers`).
- Theo dõi thanh khoản SHB và `volume_change_q = 1.3341`; kiểm tra liệu dòng tiền còn duy trì sau phiên hơn 84 triệu đơn vị (`technical_snapshot`, `N004`, F04).
- Theo dõi thanh khoản thị trường chung, hiện giảm tuần thứ hai liên tiếp (`N001`, F02).
- Kiểm tra thêm thông tin liên quan các cờ `audit_issue`, `debt_risk`, `governance`; evidence hiện chưa có chi tiết đủ để đánh giá (`N003`, `N004`).
- Rà soát độ tin cậy dữ liệu tin tức khi xuất hiện bài mới có `key_facts` rõ hơn; hiện `ticker_matching_confidence = mixed`, `N002` trích xuất một phần (`data_quality_flags`, `N002`).

## 6. Thời điểm review

- Mốc quyết định: **2025-03-31**; dữ liệu tin tức cắt tại **2025-03-31** (`decision_date`, `guardrails.news_cutoff`).
- Review tại **quý kế tiếp** theo `holding_horizon = next_quarter_or_period_return_in_signals`.
- Review sớm khi xuất hiện trigger về RSI, MACD, SMA20, thanh khoản hoặc các cờ kiểm toán, nợ và quản trị (`technical_snapshot`, `top_drivers`, `N003`, `N004`).

## 7. Kết luận hỗ trợ quyết định

- SHB có tín hiệu mô hình và kỹ thuật tích cực trong kỳ, cùng bằng chứng tin tức về dòng tiền và đà tăng gần đây (`ml_signal`, `technical_snapshot`, `N001`, `N004`).
- Rủi ro quá mua, biến động cao, thị trường thiếu xu hướng rõ và các cờ `audit_issue`, `debt_risk`, `governance` làm tăng nhu cầu kiểm chứng (`top_drivers`, `N001`, `N003`, `N004`).
- Có thể xếp SHB vào **danh sách ứng viên cần theo dõi và thẩm định thêm**, không đủ căn cứ từ evidence pack để kết luận mua chắc chắn.
- **Evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản; cần ưu tiên xác minh các cờ rủi ro và khả năng duy trì thanh khoản.

## 8. Disclaimer

Decision card chỉ hỗ trợ phân tích học thuật và quyết định. Không phải khuyến nghị đầu tư. Không bảo đảm lợi nhuận. Mọi đánh giá chỉ dựa trên evidence pack tại thời điểm **2025-03-31**; dữ liệu mô hình không bảo đảm kết quả thực tế.

---

## 2025Q1_BSI_05

## 1. Tóm tắt tín hiệu

- BSI thuộc nhóm **“Buy Candidate”**; xác suất tăng do mô hình gán: **0,9969**; xếp hạng kỳ: **5**. [ml_signal]
- Tín hiệu kỹ thuật nghiêng tích cực: RSI cuối kỳ **59,75**, MACD histogram trung bình **0,0790**, giá cao hơn SMA20 **1,98%**, khối lượng tăng **17,06%**. [technical_snapshot], [top_drivers]
- Tin tức có kế hoạch lợi nhuận và tăng vốn, nhưng phần lớn mới ở trạng thái trình cổ đông. [N001/F01], [N001/F02], [N001/F03]
- **evidence tin tức chưa đủ mạnh** để xác nhận thực thi kế hoạch hoặc đánh giá đầy đủ rủi ro pháp lý, kiểm toán, tín dụng.

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình và động lượng kỹ thuật đang ủng hộ BSI trong khung theo dõi quý kế tiếp. [ml_signal], [technical_snapshot], [top_drivers]
- Kế hoạch lợi nhuận trước thuế năm 2025 đạt **560 tỷ đồng**, tăng **8,5%**, tạo yếu tố hỗ trợ định tính. [N001/F01], [N001/F04]
- Kế hoạch phát hành hơn **22 triệu cổ phiếu** trả cổ tức **10%**, nâng vốn điều lệ gần **2.500 tỷ đồng**, tạo thay đổi về vốn cần kiểm chứng sau ĐHĐCĐ. [N001/F02], [N001/F05]

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ **59,75**; mô hình xác định RSI là driver hỗ trợ tín hiệu tăng. [technical_snapshot.rsi_end_q], [top_drivers]
- MACD histogram trung bình **0,0790**, phản ánh động lượng xu hướng tích cực theo mô hình. [technical_snapshot.macd_hist_mean_q], [top_drivers]
- Giá cao hơn SMA20 **1,98%**; vị trí này hỗ trợ trạng thái kỹ thuật hiện tại. [technical_snapshot.price_vs_sma20], [top_drivers]
- Khối lượng tăng **17,06%**, cho thấy mức độ quan tâm thị trường tăng trong kỳ. [technical_snapshot.volume_change_q], [top_drivers]
- Kế hoạch lợi nhuận năm 2025 tăng **8,5%** so với kế hoạch/kết quả tham chiếu trong bài viết. Đây vẫn là kế hoạch, chưa phải kết quả thực hiện. [N001/F01], [N001/F04]
- Cổ tức cổ phiếu **10%** và kế hoạch nâng vốn gần **2.500 tỷ đồng** là yếu tố hỗ trợ về mặt thông tin vốn. [N001/F02], [N001/F05]

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ **35,18%**, phản ánh biến động cao. [technical_snapshot.price_range_q], [top_drivers]
- N001 gắn cờ **audit_issue, debt_risk, governance**; bài viết không cung cấp đủ chi tiết để định lượng hoặc kết luận mức độ rủi ro. [N001.risk_flags], [N001/article_summary]
- N003 đề cập báo cáo tỷ lệ an toàn tài chính đã được kiểm toán, đồng thời gắn cờ **audit_issue, legal_risk**; evidence không có số liệu tỷ lệ hoặc kết luận kiểm toán chi tiết. [N003/article_summary], [N003.risk_flags], [N003/F01]
- Kế hoạch cổ tức và tăng vốn còn chờ trình cổ đông tại ĐHĐCĐ ngày **18/4/2025**. [N001/F02], [N001/F03], [N001/F05]
- N004 chỉ cho biết HĐQT phê duyệt hạn mức tín dụng tại VIB; không có key facts, nên chưa đánh giá được tác động tín dụng. [N004/article_summary], [N004/key_facts]
- Độ tin cậy khớp ticker toàn pack ở mức **mixed**; N002, N003, N004 có match confidence **partial**; N005 cần kiểm tra thủ công. [data_quality_flags.ticker_matching_confidence], [N002.match_confidence], [N003.match_confidence], [N004.match_confidence], [N005.relevance_hint]
- N005 chủ yếu nói về dòng ETF ở các mã khác; không dùng làm bằng chứng hỗ trợ trực tiếp cho BSI. [N005/article_summary], [N005/relevance_hint]

## 5. Trigger theo dõi

- Kết quả ĐHĐCĐ ngày **18/4/2025**: thông qua hay điều chỉnh kế hoạch lợi nhuận, cổ tức cổ phiếu và tăng vốn. [N001/F03], [N001/F04], [N001/F05]
- Công bố tiếp theo về tỷ lệ an toàn tài chính, kiểm toán và vấn đề pháp lý liên quan. [N003/article_summary], [N003/risk_flags]
- Cập nhật về hạn mức tín dụng tại VIB và tác động liên quan. [N004/article_summary]
- Diễn biến RSI, MACD histogram, vị trí giá so với SMA20 và khối lượng. [technical_snapshot], [top_drivers]
- Biến động giá tiếp tục ở mức cao hoặc thay đổi mạnh so với biên độ kỳ hiện tại. [technical_snapshot.price_range_q]

## 6. Thời điểm review

- **Review lần 1:** sau ĐHĐCĐ dự kiến ngày **18/4/2025**. [N001/F03]
- **Review lần 2:** cuối quý kế tiếp, phù hợp holding horizon **“next quarter”**. [holding_horizon]
- Review sớm nếu xuất hiện cập nhật mới về audit, legal risk, debt risk, governance hoặc tín hiệu kỹ thuật đảo chiều. [N001.risk_flags], [N003.risk_flags], [technical_snapshot], [top_drivers]

## 7. Kết luận hỗ trợ quyết định

- BSI có tín hiệu mô hình mạnh và nền kỹ thuật hiện tại tương đối tích cực. [ml_signal], [technical_snapshot]
- Kế hoạch lợi nhuận, cổ tức và tăng vốn tạo thêm yếu tố hỗ trợ, nhưng chưa được xác nhận bằng kết quả thực hiện hoặc nghị quyết sau ĐHĐCĐ. [N001/F01], [N001/F02], [N001/F03]
- Có thể xếp BSI vào **danh sách theo dõi tích cực / ứng viên nghiên cứu thêm**.
- Chưa đủ evidence để đưa ra kết luận đầu tư chắc chắn. Ưu tiên kiểm chứng các trigger tại mục 5.

## 8. Disclaimer

Decision card chỉ hỗ trợ phân tích học thuật và quyết định. Không phải tư vấn đầu tư. Không bảo đảm lợi nhuận. Evidence có giới hạn, gồm cờ rủi ro audit, debt, governance, legal và độ khớp ticker mixed.

---

## 2025Q2_STB_01

## 1. Tóm tắt tín hiệu

- STB có tín hiệu định lượng tích cực: `pred_label = 1`, `pred_proba_up = 0.9987508337`, xếp hạng 1 kỳ, lớp `Buy Candidate` từ mô hình `technical_Config_A_from_existing_pipeline` [ml_signal].
- Động lượng kỹ thuật hỗ trợ tín hiệu: `rsi_end_q = 69.6950`, `macd_hist_mean_q = 0.0913`, giá cao hơn SMA20 `4.3167%`, khối lượng tăng `78.03%` [technical_snapshot].
- Biên độ giá kỳ cao `37.4591%`, tạo rủi ro biến động [technical_snapshot.price_range_q].
- Tin tức có độ phủ cao nhưng ticker matching ở mức `mixed`, nhiều bài có `match_confidence = partial`, cần kiểm tra thủ công [data_quality_flags; N001–N005]. Evidence tin tức chưa đủ mạnh để xác nhận độc lập tín hiệu kỹ thuật.

## 2. Luận điểm đầu tư chính

- STB phù hợp đưa vào nhóm cần xem xét tiếp, nhờ tín hiệu kỹ thuật đứng đầu kỳ và động lượng tích cực [ml_signal; technical_snapshot].
- Kỳ vọng lợi nhuận từ VCBS tạo hỗ trợ định tính, nhưng vẫn là ước tính, chưa phải kết quả đã xác nhận [N005, F01, F03, F05].
- Luận điểm phụ thuộc vào việc động lượng kỹ thuật duy trì, chất lượng lợi nhuận được xác nhận, và rủi ro quản trị được làm rõ [technical_snapshot; N004; N005].

## 3. Yếu tố hỗ trợ

- Mô hình ghi nhận `Buy Candidate`, xác suất dự đoán tăng `0.9987508337`, xếp hạng 1 kỳ [ml_signal].
- RSI, MACD histogram và vị trí giá so với SMA20 đều là driver hỗ trợ tín hiệu tăng [top_drivers; `rsi_end_q`; `macd_hist_mean_q`; `price_vs_sma20`].
- Khối lượng tăng `78.03%`, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ [technical_snapshot.volume_change_q].
- VCBS dự báo lợi nhuận quý II của Sacombank tăng `25%`; động lực được nêu gồm tín dụng và phục hồi khách hàng cá nhân [N005, F01–F03].
- Sacombank được nêu trong nhóm doanh nghiệp có triển vọng lợi nhuận tích cực theo SSI Research; chi tiết riêng cho STB còn hạn chế [N003, F01].
- Sacombank được vinh danh VIE 10 và ESG 10; bài viết nêu tiếp cận đổi mới, số hóa và phát triển bền vững [N002, F01–F05]. Độ tin cậy các key fact ở mức thấp.

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá kỳ `37.4591%` cho thấy biến động cao; tín hiệu có thể nhạy với đảo chiều kỹ thuật [technical_snapshot.price_range_q; top_drivers].
- RSI cuối kỳ `69.6950` là driver quan trọng nhất; cần tránh xem xác suất mô hình như bảo đảm kết quả [top_drivers; technical_snapshot.rsi_end_q].
- N004 ghi nhận thay đổi lãnh đạo cấp cao và gắn cờ `governance`, `debt_risk`; key facts của bài này không có dữ liệu trích xuất [N004].
- N005 gắn cờ `debt_risk`; kỳ vọng lợi nhuận dựa một phần vào tín dụng, bất động sản và phục hồi khách hàng cá nhân [N005, F02; risk_flags].
- N003 gắn cờ `earnings_warning`; bài viết nói về nhiều doanh nghiệp, không cung cấp đầy đủ bằng chứng riêng cho STB [N003, risk_flags; N003.match_confidence].
- N001 và N002 chủ yếu là tin khuyến mại, giải thưởng, định hướng ESG; các key fact có confidence thấp, chưa đủ chứng minh tác động tài chính [N001–N002, F01–F05].
- Chất lượng ghép mã ở mức `mixed`; các bài đều cần kiểm tra thủ công [data_quality_flags; N001–N005].

## 5. Trigger theo dõi

- Cập nhật `rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q`; ghi nhận khi động lượng suy yếu hoặc giá mất trạng thái hỗ trợ [technical_snapshot; top_drivers].
- Theo dõi `price_range_q`; biến động tăng thêm làm giảm độ tin cậy tín hiệu kỹ thuật [technical_snapshot.price_range_q].
- Kiểm tra công bố kết quả kinh doanh quý II và đối chiếu với ước tính VCBS, SSI; không xem ước tính là kết quả thực tế [N005; N003].
- Theo dõi thay đổi nhân sự điều hành, HĐQT và các cập nhật liên quan quản trị, nợ [N004; N005].
- Xác minh ticker matching và nội dung gốc trước khi dùng N001–N005 làm luận cứ chính [data_quality_flags; `relevance_hint = needs_manual_check`].

## 6. Thời điểm review

- Ngày chốt card: `2025-06-30`; cutoff tin tức: `2025-06-30` [decision_date; guardrails.news_cutoff].
- Review chính: kỳ kế tiếp, theo `holding_horizon` [holding_horizon].
- Review sớm khi xuất hiện trigger kỹ thuật, công bố kết quả kinh doanh quý II, hoặc cập nhật quản trị [technical_snapshot; N003–N005].
- Không bổ sung dữ liệu sau ngày quyết định vào card ban đầu [guardrails.no_post_decision_data].

## 7. Kết luận hỗ trợ quyết định

- STB có tín hiệu định lượng mạnh và đứng đầu kỳ, nhưng mức biến động cao và bằng chứng tin tức còn hạn chế [ml_signal; technical_snapshot; data_quality_flags].
- Có thể xếp STB vào nhóm cần thẩm định tiếp, không xem đây là kết luận mua hoặc bảo đảm lợi nhuận.
- Ưu tiên xác minh ba điểm: độ bền động lượng, kết quả kinh doanh so với ước tính, và rủi ro quản trị/nợ [technical_snapshot; N003–N005].

## 8. Disclaimer

- Decision card phục vụ nghiên cứu và hỗ trợ quyết định, không phải khuyến nghị đầu tư chắc chắn [guardrails.not_investment_advice].
- Xác suất mô hình, tin tức và ước tính phân tích không bảo đảm kết quả.
- Card không dự báo giá tuyệt đối, không cam kết lợi nhuận, không sử dụng dữ liệu sau `2025-06-30` [guardrails].

---

## 2025Q2_DXG_02

## 1. Tóm tắt tín hiệu

- DXG có tín hiệu mô hình tích cực: `pred_label = 1`, `pred_proba_up = 0.9985`, xếp hạng 2, phân loại `Buy Candidate` [ `ml_signal` ].
- Động lượng kỹ thuật hỗ trợ: MACD histogram dương `0.0188`, giá cao hơn SMA20 `4.59%`, khối lượng tăng `49.0%` [ `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q` ].
- Rủi ro kỹ thuật hiện hữu: RSI cuối kỳ `75.33`, có cờ `positive_but_overbought_risk`; biên độ giá kỳ `0.4730`, có cờ biến động cao [ `rsi_end_q`, `price_range_q` ].
- Tin tức cho tín hiệu hỗn hợp: audit/pháp lý [N001], trái phiếu [N003], quản trị [N004], vốn [N005]. Bối cảnh ngành có dấu hiệu hồi phục, DXG được nêu trong nhóm đáng chú ý [N002].
- Ticker matching ở mức `mixed`; nhiều bài có `extraction_status = partial`. Evidence tin tức chưa đủ mạnh cho kết luận riêng về nền tảng tài chính DXG [ `ticker_matching_confidence`, N001, N003, N004, N005 ].

## 2. Luận điểm đầu tư chính

- DXG là ứng viên theo dõi tích cực nhờ tín hiệu mô hình và động lượng kỹ thuật mạnh [ `ml_signal`, `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q` ].
- Luận điểm bị giảm độ tin cậy bởi RSI cao, biến động giá lớn và các tin tức liên quan audit, trái phiếu, quản trị [ `rsi_end_q`, `price_range_q`, N001, N003, N004 ].
- Chưa đủ cơ sở để chuyển tín hiệu mô hình thành khuyến nghị mua chắc chắn [ `ml_signal`, `data_quality_flags`, N001–N004 ].

## 3. Yếu tố hỗ trợ

- Mô hình xếp DXG hạng 2 trong kỳ, nhãn `Buy Candidate`, xác suất mô hình đi lên `0.9985` [ `ml_signal` ].
- MACD histogram trung bình dương, hỗ trợ động lượng xu hướng [ `macd_hist_mean_q` ].
- Giá nằm trên SMA20, hỗ trợ trạng thái kỹ thuật ngắn hạn [ `price_vs_sma20` ].
- Khối lượng tăng `49.0%`, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ [ `volume_change_q` ].
- Bài viết ghi nhận thị trường địa ốc dần hồi phục và liệt kê DXG trong nhóm đáng chú ý quý 2 và năm 2025; độ tin cậy fact thấp, chỉ nên xem là bối cảnh ngành [N002, F01, F03].
- DXG có nghị quyết thông qua kết quả phát hành cổ phiếu tăng vốn từ vốn chủ sở hữu; bằng chứng chỉ cho thấy sự kiện vốn, chưa cho thấy tác động tài chính cụ thể [N005, F01].

## 4. Yếu tố cần lưu ý / rủi ro

- RSI `75.33` cho thấy trạng thái quá mua; mô hình cũng gắn cờ `positive_but_overbought_risk` [ `rsi_end_q`, `top_drivers` ].
- Biên độ giá kỳ `0.4730` cho thấy rủi ro biến động cao [ `price_range_q`, `top_drivers` ].
- Nghị quyết lựa chọn đơn vị kiểm toán năm 2025 đi kèm `audit_issue` và `legal_risk`; nội dung trích xuất ngắn, mức tin cậy trung bình [N001, F01, `risk_flags`].
- Nghị quyết thông qua phương án mua lại trước hạn toàn bộ dư nợ trái phiếu; bằng chứng chưa nêu nguồn tiền, tiến độ hoặc kết quả thực hiện [N003, F01, `risk_flags`].
- Tái bổ nhiệm Tổng giám đốc là sự kiện quản trị cần theo dõi; bằng chứng không kết luận tác động tích cực hay tiêu cực [N004, F01, `risk_flags`].
- N002 gắn cờ `audit_issue`, `debt_risk`, `governance`, nhưng các key fact chính chủ yếu mô tả ngành hoặc doanh nghiệp khác; không nên suy diễn thành kết luận riêng cho DXG [N002, F01–F05].
- Chất lượng ghép ticker ở mức `mixed`; bốn bài N001, N003, N004, N005 có `match_confidence = partial` [ `data_quality_flags`, N001, N003, N004, N005 ].

## 5. Trigger theo dõi

- Tín hiệu mô hình đổi nhãn khỏi `Buy Candidate` hoặc xác suất mô hình giảm đáng kể [ `ml_signal` ].
- MACD histogram suy yếu hoặc chuyển âm [ `macd_hist_mean_q` ].
- Giá không còn duy trì trên SMA20 [ `price_vs_sma20`, `sma20_end` ].
- RSI tiếp tục ở vùng cao cùng biên độ giá lớn [ `rsi_end_q`, `price_range_q` ].
- Cập nhật kết quả thực hiện phương án mua lại trái phiếu [N003].
- Cập nhật về kiểm toán năm 2025 và các vấn đề pháp lý liên quan [N001].
- Cập nhật tác động của thay đổi quản trị và phát hành vốn [N004, N005].

## 6. Thời điểm review

- Review tại cuối quý kế tiếp hoặc khi có kỳ tín hiệu mới, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals` [ `holding_horizon` ].
- Dữ liệu hiện tại chốt ngày `2025-06-30`; không dùng dữ liệu sau ngày quyết định trong card ban đầu [ `decision_date`, `guardrails.news_cutoff`, `guardrails.no_post_decision_data` ].

## 7. Kết luận hỗ trợ quyết định

- Trạng thái: **theo dõi tích cực, cần đánh giá thêm**.
- Tín hiệu kỹ thuật và mô hình mạnh, nhưng RSI quá cao, biến động lớn và tin tức doanh nghiệp còn rủi ro [ `ml_signal`, `rsi_end_q`, `price_range_q`, N001, N003, N004 ].
- Evidence tin tức chưa đủ mạnh để xác nhận luận điểm cơ bản riêng cho DXG [N002, `data_quality_flags`].
- Không kết luận mua chắc chắn. Ưu tiên kiểm tra trigger về kiểm toán, trái phiếu, quản trị và diễn biến kỹ thuật trước review tiếp theo [N001, N003, N004, `technical_snapshot`].

## 8. Disclaimer

- Card phục vụ hỗ trợ quyết định và nghiên cứu học thuật, không phải tư vấn đầu tư [ `guardrails.not_investment_advice` ].
- Xác suất mô hình không bảo đảm kết quả thực tế [ `ml_signal` ].
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận.
- Phân tích chỉ dùng evidence có cutoff `2025-06-30`; một số bằng chứng tin tức có trích xuất từng phần và độ khớp ticker chưa đầy đủ [ `guardrails.news_cutoff`, `data_quality_flags` ].

---

## 2025Q2_VBB_03

## 1. Tóm tắt tín hiệu

- VBB thuộc nhóm **“Buy Candidate”** trong mô hình; `pred_label = 1`, `pred_proba_up = 0.9981673135834384`, xếp hạng 3 trong kỳ. [ml_signal]
- Động lượng kỹ thuật tích cực: RSI cuối kỳ 65.4593; MACD histogram trung bình dương 0.0051395; `price_vs_sma20` dương 0.0512; khối lượng thay đổi 1.2072. [technical_snapshot]
- Tin tức có đề cập quyết định NHNN, thay đổi nhân sự và thay đổi chi nhánh VBB. Chi tiết tác động chưa rõ. [N001, N002, N004, N005]
- **Evidence tin tức chưa đủ mạnh** cho kết luận cơ bản: N001 và N005 trích xuất từng phần; N002–N004 có key facts lẫn nội dung không liên quan trực tiếp VBB. [N001, N002, N003, N004, N005]

## 2. Luận điểm đầu tư chính

- Tín hiệu kỹ thuật và mô hình đang nghiêng tích cực trong kỳ 2025Q2. [ml_signal, technical_snapshot]
- Tín hiệu này phù hợp trạng thái **ứng viên cần theo dõi**, không đủ làm cơ sở cho khuyến nghị mua chắc chắn. [ml_signal, guardrails.not_investment_advice]
- Luận điểm cơ bản chưa xác nhận vì pack không cung cấp đủ thông tin chi tiết về tác động kinh doanh từ các tin NHNN, nhân sự và chi nhánh. [N001, N002, N004, N005]

## 3. Yếu tố hỗ trợ

- Xác suất hướng lên do mô hình ghi nhận ở mức 0.9981673; tín hiệu được xếp loại “Buy Candidate”. Đây là output mô hình, không phải bảo đảm kết quả. [ml_signal]
- RSI 65.4593, MACD histogram dương và vị trí giá so với SMA20 dương hỗ trợ luận điểm động lượng. [technical_snapshot.rsi_end_q, technical_snapshot.macd_hist_mean_q, technical_snapshot.price_vs_sma20]
- Khối lượng thay đổi 1.2072, được mô hình xem là yếu tố hỗ trợ tín hiệu. [technical_snapshot.volume_change_q, top_drivers]
- Quyết định NHNN về bổ sung nội dung hoạt động vào giấy phép Vietbank là tin liên quan trực tiếp VBB; tác động tích cực chưa thể xác nhận do nội dung trích xuất hạn chế. [N001, N003]

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ ở mức 0.3688826, cho thấy biến động cần được kiểm soát khi đánh giá tín hiệu. [technical_snapshot.price_range_q, top_drivers]
- RSI cao và giá nằm trên SMA20 có thể khiến tín hiệu phụ thuộc nhiều vào động lượng; pack không xác nhận độ bền xu hướng. [technical_snapshot.rsi_end_q, technical_snapshot.price_vs_sma20]
- Có thay đổi chức danh Phó Tổng giám đốc, Kế toán trưởng và thay đổi địa điểm, tên gọi chi nhánh; tác động quản trị và vận hành chưa rõ. [N002, N004, N005]
- N002–N004 gắn các cờ `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `legal_risk`, `governance`, nhưng key facts gồm nhiều nội dung về ACV, PVT, CC1, VIX và thị trường; không đủ cơ sở quy kết các rủi ro này cho VBB. [N002, N003, N004]
- Dữ liệu tin tức có mâu thuẫn thời điểm và phạm vi: `published_at` của N002 là 2025-06-30 nhưng URL chứa `/2025/07`; N003 có facts ngày 03/07, sau `news_cutoff` 2025-06-30. [N002, N003, guardrails.news_cutoff, data_quality_flags]
- Độ tin cậy matching ticker toàn pack là `mixed`, dù từng tin ghi nhận `match_confidence = exact`. [data_quality_flags.ticker_matching_confidence, N001–N005]

## 5. Trigger theo dõi

- Kiểm tra mô hình kỳ kế tiếp: `signal_class`, `pred_label`, `pred_proba_up`, `rank_in_period`. [ml_signal]
- Theo dõi RSI, MACD histogram, `price_vs_sma20`, `volume_change_q` và `price_range_q`. [technical_snapshot]
- Xác minh nội dung đầy đủ và tác động thực tế của quyết định NHNN. [N001, N003]
- Xác minh thay đổi nhân sự, kế toán trưởng và chi nhánh; tách facts không liên quan VBB khỏi news pack. [N002, N004, N005]
- Rà soát lại các cờ rủi ro audit, pha loãng vốn, nợ, lợi nhuận, pháp lý và quản trị trước review. [N002, N003, N004]

## 6. Thời điểm review

- Review vào **kỳ kế tiếp**, theo `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm hơn nếu xuất hiện tin chính thức mới về giấy phép, nhân sự, quản trị hoặc các cờ rủi ro nêu trên. [N001–N005]

## 7. Kết luận hỗ trợ quyết định

- VBB có tín hiệu mô hình và kỹ thuật tích cực trong kỳ 2025Q2. [ml_signal, technical_snapshot]
- Tin tức liên quan VBB tồn tại, nhưng **evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản hoặc tác động kinh doanh. [N001–N005, data_quality_flags]
- Trạng thái phù hợp: **đưa vào danh sách theo dõi có điều kiện, chờ xác minh news và review kỳ kế tiếp**. Không xem đây là khuyến nghị mua chắc chắn. [ml_signal, guardrails.initial_prompt_safe]

## 8. Disclaimer

- Decision card chỉ dùng hỗ trợ nghiên cứu và quyết định; không phải tư vấn đầu tư. [guardrails.not_investment_advice]
- Output mô hình không bảo đảm kết quả hay lợi nhuận. [ml_signal]
- Card chỉ dùng evidence có trong pack, cutoff 2025-06-30; dữ liệu tin tức có điểm thiếu, lẫn nội dung và mâu thuẫn thời điểm. [guardrails.news_cutoff, data_quality_flags, N001–N005]

---

## 2025Q2_MSN_04

## 1. Tóm tắt tín hiệu

- MSN thuộc nhóm **“Buy Candidate”** theo mô hình; `pred_label = 1`, `pred_proba_up = 0.9972`, xếp hạng 4 trong kỳ. Đây là điểm số mô hình, không phải bảo đảm kết quả. [ml_signal]
- Động lượng kỹ thuật hỗ trợ: `macd_hist_mean_q = 0.1094`, `price_vs_sma20 = 0.1349`, `volume_change_q = 0.5147`. [technical_snapshot]
- RSI cuối kỳ ở `84.9994`, đi kèm nhãn **positive_but_overbought_risk**. [top_drivers: rsi_end_q]
- Tin tức ghi nhận khối ngoại mua MSN, nhưng bối cảnh thị trường có rung lắc, thanh khoản thấp và vùng cản 1.370 điểm. [N001 F01/F05; N003 F01/F04; N005 F01/F02]
- Chất lượng dữ liệu tin tức cao, nhưng độ tin cậy ghép mã ở mức **mixed**; evidence tin tức chưa đủ mạnh cho luận điểm cơ bản doanh nghiệp. [data_quality_flags]

## 2. Luận điểm đầu tư chính

- MSN là ứng viên cần theo dõi theo tín hiệu mô hình, nhờ xác suất mô hình và thứ hạng kỳ hiện tại. [ml_signal]
- Động lượng hiện tại nghiêng tích cực: MACD histogram dương, giá nằm trên SMA20, khối lượng tăng trong kỳ. [technical_snapshot; top_drivers]
- Tín hiệu tăng bị giảm chất lượng bởi trạng thái quá mua và thị trường thiếu xác nhận thanh khoản. [rsi_end_q; N003 F04; N005 F02]
- Luận điểm phù hợp với cách tiếp cận **theo dõi có điều kiện**, không đủ cơ sở cho khuyến nghị chắc chắn. [ml_signal; data_quality_flags; guardrails]

## 3. Yếu tố hỗ trợ

- Mô hình xếp MSN vào nhóm **“Buy Candidate”**, `pred_proba_up = 0.9972`. [ml_signal]
- MACD histogram trung bình dương, phản ánh động lượng xu hướng hỗ trợ tín hiệu. [macd_hist_mean_q; top_drivers]
- Giá nằm trên SMA20 với `price_vs_sma20 = 0.1349`. [price_vs_sma20; sma20_end]
- Khối lượng trong kỳ tăng `51.47%`, cho thấy mức độ quan tâm thị trường cao hơn. [volume_change_q; top_drivers]
- Khối ngoại mua ròng MSN `127,2 tỷ đồng` ngày 27/6. [N004 F04]
- Khối ngoại tiếp tục tập trung mua MSN trong phiên 30/6; tổng mua ròng HOSE gần `600 tỷ đồng`. [N001 F01/F05]

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `84.9994`, mô hình gắn nhãn rủi ro quá mua; dư địa vận động ngắn hạn có thể kém ổn định. [rsi_end_q; top_drivers]
- Biên độ giá trong kỳ cao, `price_range_q = 0.4292`, phản ánh biến động đáng lưu ý. [price_range_q; top_drivers]
- Thị trường xuất hiện rung lắc, điều chỉnh nhẹ và thanh khoản dưới trung bình 20 phiên. [N005 F01/F02]
- Thanh khoản chưa bứt phá, thiếu nhóm dẫn dắt đủ mạnh; nhịp tăng được đánh giá là thiếu thuyết phục. [N003 F04]
- Dòng tiền khối ngoại không đồng nhất theo phiên: MSN được mua ròng ngày 27/6, nhưng toàn HOSE bán ròng `11,4 tỷ đồng` trong cùng phiên. [N004 F03/F04]
- Tin N001 có `risk_flags`: `audit_issue`, `debt_risk`, `governance`; pack không cung cấp đủ key facts định tính để xác minh chi tiết các rủi ro này. [N001 risk_flags; N001 key_facts]
- Độ tin cậy ghép ticker ở mức **mixed**; N005 chỉ có `match_confidence = partial`. [data_quality_flags; N005]
- **Evidence tin tức chưa đủ mạnh** cho đánh giá nền tảng doanh nghiệp; phần lớn key facts tập trung vào diễn biến thị trường. [news_evidence; data_quality_flags]

## 5. Trigger theo dõi

- RSI hạ nhiệt khỏi mức `84.9994` hoặc tiếp tục duy trì vùng quá mua. [rsi_end_q]
- `macd_hist_mean_q` duy trì dương; theo dõi dấu hiệu suy yếu động lượng. [macd_hist_mean_q; top_drivers]
- `price_vs_sma20` duy trì dương; ghi nhận nếu giá mất trạng thái trên SMA20. [price_vs_sma20; sma20_end]
- Khối lượng MSN duy trì mức tăng `51.47%` hoặc suy giảm trở lại. [volume_change_q]
- Khối ngoại tiếp tục mua ròng MSN hay đảo chiều bán ròng. [N001 F01/F05; N004 F04]
- Thanh khoản thị trường cải thiện hay tiếp tục dưới trung bình 20 phiên. [N003 F04; N005 F02]
- Cập nhật xác minh các cờ `audit_issue`, `debt_risk`, `governance`. [N001 risk_flags]

## 6. Thời điểm review

- Review vào **kỳ kế tiếp**, theo holding horizon `next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm khi RSI, MACD, vị trí so với SMA20, khối lượng hoặc dòng tiền khối ngoại đảo chiều. [technical_snapshot; N001; N004]
- Ngày quyết định: `2025-06-30`; news cutoff: `2025-06-30`. [decision_date; guardrails]

## 7. Kết luận hỗ trợ quyết định

- MSN có tín hiệu mô hình tích cực và nhiều yếu tố kỹ thuật hỗ trợ. [ml_signal; technical_snapshot]
- Tín hiệu chưa đủ độc lập để xem là quyết định mua chắc chắn do RSI quá mua, biến động cao, thanh khoản thiếu xác nhận và risk flags tin tức chưa được làm rõ. [rsi_end_q; price_range_q; N001; N003; N005]
- Cách xử lý thận trọng: đưa MSN vào danh sách theo dõi có điều kiện, chờ review theo trigger và bổ sung evidence định tính. [data_quality_flags; holding_horizon]

## 8. Disclaimer

- Decision card chỉ hỗ trợ nghiên cứu và ra quyết định; không phải khuyến nghị đầu tư. [guardrails: not_investment_advice]
- Điểm `pred_proba_up` là đầu ra mô hình, không phải cam kết lợi nhuận hay dự báo giá tuyệt đối. [ml_signal]
- Chỉ sử dụng dữ liệu đến `2025-06-30`; không bao gồm dữ liệu sau thời điểm quyết định. [guardrails: news_cutoff; no_post_decision_data]

---

## 2025Q2_VND_05

## 1. Tóm tắt tín hiệu

- Mô hình xếp VND vào nhóm **“Buy Candidate”**, với `pred_label = 1`, `pred_proba_up = 0.9970933137405896`, hạng 5 trong kỳ. Đây là tín hiệu mô hình, không phải kết luận chắc chắn. `[ml_signal]`
- Kỹ thuật nghiêng tích cực: RSI cuối kỳ 65.8972, giá cao hơn SMA20 5.2367%, khối lượng tăng 37.4850%. `[technical_snapshot.rsi_end_q; technical_snapshot.price_vs_sma20; technical_snapshot.volume_change_q]`
- Tín hiệu chưa đồng thuận hoàn toàn: MACD histogram trung bình âm -0.01105; biên độ giá trong kỳ 0.3415. `[technical_snapshot.macd_hist_mean_q; technical_snapshot.price_range_q]`
- Tin tức ghi nhận phát hành trái phiếu ra công chúng, tạo yếu tố cần giám sát về nợ và vốn. `[N001; N002]`

## 2. Luận điểm đầu tư chính

- VND có tín hiệu mô hình và kỹ thuật nghiêng tích cực trong kỳ, nhưng cần đặt cạnh MACD âm và rủi ro liên quan phát hành trái phiếu. `[ml_signal; technical_snapshot.rsi_end_q; technical_snapshot.price_vs_sma20; technical_snapshot.macd_hist_mean_q; N001; N002]`
- Phù hợp hơn với trạng thái **theo dõi và phân tích tiếp**, chưa đủ cơ sở cho khuyến nghị mua hoặc bán chắc chắn. `[ml_signal; data_quality_flags.ticker_matching_confidence; N001; N002]`
- **Evidence tin tức chưa đủ mạnh** cho kết luận định tính rộng: N001, N002, N004 có `extraction_status = partial`; dữ liệu ghép mã ở mức `mixed`. `[N001; N002; N004; data_quality_flags.ticker_matching_confidence]`

## 3. Yếu tố hỗ trợ

- RSI cuối kỳ 65.8972 được mô hình xác định là driver kỹ thuật quan trọng, hỗ trợ tín hiệu tăng. `[technical_snapshot.rsi_end_q; top_drivers[0]]`
- Giá cao hơn SMA20 5.2367%, hỗ trợ trạng thái xu hướng ngắn hạn. `[technical_snapshot.price_vs_sma20; technical_snapshot.sma20_end; top_drivers[2]]`
- Khối lượng trong kỳ tăng 37.4850%, phản ánh mức độ quan tâm thị trường cao hơn trong dữ liệu kỹ thuật. `[technical_snapshot.volume_change_q; top_drivers[6]]`
- VND có thông báo trả cổ tức tiền mặt năm 2024 ở mức 500 đồng/cổ phiếu; đây là yếu tố hỗ trợ hoặc bối cảnh, không phải bảo đảm lợi nhuận. `[N004; N004.key_facts[0]]`

## 4. Yếu tố cần lưu ý / rủi ro

- MACD histogram trung bình âm -0.01105, cho thấy động lượng xu hướng chưa đồng thuận với RSI và vị trí giá trên SMA20. `[technical_snapshot.macd_hist_mean_q; top_drivers[1]]`
- Công ty thông qua hồ sơ đăng ký chào bán trái phiếu ra công chúng. Tin được gắn `debt_risk`, nhưng mức tin cậy chỉ `medium` và trích xuất một phần. `[N001; N001.key_facts[0]; N001.extraction_status]`
- Công ty công bố nghị quyết phát hành trái phiếu ra công chúng năm 2025. Tin được gắn `debt_risk,capital`, với mức tin cậy `medium` và trích xuất một phần. `[N002; N002.key_facts[0]; N002.extraction_status]`
- Tin vĩ mô ghi nhận USD/VND tăng trong nửa đầu năm 2025, tỷ giá trung tâm đạt 25.031 VND/USD ngày 20/6; tác động riêng lên cổ phiếu VND chưa được chứng minh trong pack. `[N003.key_facts.F01; N005.key_facts.F01]`
- N003 và N005 có `risk_flags = audit_issue`; N003 có một số key fact độ tin cậy thấp. `[N003.risk_flags; N003.key_facts; N005.risk_flags]`
- Biên độ giá trong kỳ ở mức 0.3415, cần lưu ý biến động. `[technical_snapshot.price_range_q; top_drivers[8]]`

## 5. Trigger theo dõi

- Cập nhật công bố mới về hồ sơ, nghị quyết và tiến độ phát hành trái phiếu. `[N001; N002]`
- Kiểm tra diễn biến MACD histogram, RSI, vị trí giá so với SMA20 và khối lượng trong kỳ tín hiệu mới. `[technical_snapshot.macd_hist_mean_q; technical_snapshot.rsi_end_q; technical_snapshot.price_vs_sma20; technical_snapshot.volume_change_q]`
- Theo dõi USD/VND và swap rate VND/USD, vì pack ghi nhận áp lực tỷ giá và swap rate quanh 0% ở nhiều kỳ hạn. `[N003.key_facts.F01; N003.key_facts.F05; N005.key_facts.F01]`
- Xác minh mức độ liên quan trực tiếp của tin vĩ mô với VND, do độ tin cậy ghép mã tổng thể ở mức `mixed`. `[data_quality_flags.ticker_matching_confidence; N003.match_confidence; N005.match_confidence]`

## 6. Thời điểm review

- Review vào **cuối quý hoặc kỳ tín hiệu kế tiếp**, phù hợp với `holding_horizon = next_quarter_or_period_return_in_signals`. `[holding_horizon; decision_date]`
- Review sớm hơn nếu xuất hiện công bố mới về phát hành trái phiếu hoặc dữ liệu kỹ thuật thay đổi rõ rệt. `[N001; N002; technical_snapshot]`

## 7. Kết luận hỗ trợ quyết định

- VND là **ứng viên cần theo dõi**: mô hình và một số chỉ báo kỹ thuật ủng hộ, nhưng MACD âm, biên độ giá và rủi ro nợ làm giảm độ chắc của tín hiệu. `[ml_signal; technical_snapshot; N001; N002]`
- Chưa đủ evidence để đưa ra khuyến nghị đầu tư chắc chắn. Cần chờ cập nhật kỹ thuật và xác minh thêm thông tin phát hành trái phiếu. `[data_quality_flags; N001; N002; technical_snapshot.macd_hist_mean_q]`

## 8. Disclaimer

- Card chỉ dùng evidence pack tại ngày 2025-06-30. `[decision_date; guardrails.news_cutoff]`
- Đây không phải tư vấn đầu tư. Tín hiệu mô hình không bảo đảm kết quả.
- Không sử dụng nội dung toàn văn ngoài phần được cung cấp; N001, N002 và N004 có trích xuất một phần. `[N001.extraction_status; N002.extraction_status; N004.extraction_status]`
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận, không kết luận outcome tương lai.

---

## 2025Q3_LPB_01

## 1. Tóm tắt tín hiệu

- LPB thuộc nhóm **“Buy Candidate”** theo mô hình kỹ thuật; xác suất nhãn tăng: **0,998529**; xếp hạng **1** trong kỳ 2025Q3. [ml_signal]
- Động lượng kỹ thuật hỗ trợ: MACD histogram trung bình **0,100522**; giá cao hơn SMA20 **8,75%**; khối lượng tăng **31,55%**. [technical_snapshot]
- RSI cuối kỳ **73,889**, cho thấy rủi ro quá mua; biên độ giá kỳ **0,444032**, cho thấy biến động đáng lưu ý. [technical_snapshot; top_drivers]
- Tin tức chủ yếu liên quan thay đổi địa điểm chi nhánh/PGD. **Evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản cho LPB. [N001; N002; N003; N004; N005; data_quality_flags]

## 2. Luận điểm đầu tư chính

- Tín hiệu kỹ thuật hiện nghiêng tích cực: mô hình gắn nhãn **“Buy Candidate”**, động lượng MACD dương, giá nằm trên SMA20, khối lượng tăng. [ml_signal; technical_snapshot]
- Tín hiệu không đồng nhất hoàn toàn: RSI cao và biên độ giá lớn làm tăng rủi ro điều chỉnh hoặc biến động. [technical_snapshot.rsi_end_q; technical_snapshot.price_range_q]
- Tin tức chưa bổ sung xác nhận định tính đủ mạnh. N001 chỉ nêu thay đổi địa điểm; N002 và N003 có key fact độ tin cậy thấp; N004 và N005 có dữ kiện trích xuất liên quan nhiều doanh nghiệp khác. [N001; N002/F01; N003/F01; N004/F02–F05; N005/F02–F05]

## 3. Yếu tố hỗ trợ

- Mô hình kỹ thuật phát tín hiệu **“Buy Candidate”**, xác suất nhãn tăng **0,998529**. [ml_signal.pred_label; ml_signal.pred_proba_up; ml_signal.signal_class]
- MACD histogram trung bình dương **0,100522**, hỗ trợ động lượng. [technical_snapshot.macd_hist_mean_q]
- Giá cuối kỳ cao hơn SMA20 **8,75%**, phản ánh trạng thái kỹ thuật trên đường trung bình. [technical_snapshot.price_vs_sma20]
- Khối lượng tăng **31,55%**, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ. [technical_snapshot.volume_change_q]
- LPB công bố thay đổi địa điểm chi nhánh Hải Phòng, PGD Trường Chinh, PGD Mỹ Đình; đồng thời nhận chấp thuận thay đổi địa điểm PGD Dĩ An. Đây là thông tin hoạt động, chưa phải catalyst tài chính rõ ràng. [N001; N002/F01; N003/F01]

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ **73,889**, được mô hình đánh dấu **positive_but_overbought_risk**; trạng thái quá mua có thể làm tín hiệu dễ biến động. [technical_snapshot.rsi_end_q; top_drivers]
- Biên độ giá kỳ **0,444032**, được mô hình đánh dấu **risk_high_volatility**. [technical_snapshot.price_range_q; top_drivers]
- Độ tin cậy ghép ticker toàn pack là **mixed**. Cần kiểm tra lại trước khi dùng tin tức làm luận cứ LPB. [data_quality_flags.ticker_matching_confidence]
- N002 và N003 có key fact độ tin cậy **low**, hướng **neutral**; tác động thông tin chưa rõ. [N002/F01; N003/F01]
- N004 và N005 có headline về trái phiếu LPB12503/LPB12504, nhưng F02–F05 nêu trái phiếu của Starbay Hà Nội, Thăng Long, Bcons PS và PC1. Không đủ cơ sở gán các rủi ro này cho LPB. [N004/F01–F05; N005/F01–F05]
- N004 và N005 chứa risk flags như `debt_risk`, `legal_risk`, `governance`, nhưng dữ kiện chi tiết không xác nhận trực tiếp rủi ro thuộc LPB. [N004.risk_flags; N005.risk_flags]
- **Evidence tin tức chưa đủ mạnh** cho đánh giá cơ bản hoặc tác động tài chính. [data_quality_flags.key_fact_coverage; N001; N002; N003; N004; N005]

## 5. Trigger theo dõi

- Kiểm tra tín hiệu mô hình ở kỳ báo cáo kế tiếp: `pred_label`, `pred_proba_up`, `signal_class`. [ml_signal]
- Theo dõi RSI, MACD histogram và `price_vs_sma20`; xem xét lại khi động lượng không còn hỗ trợ hoặc RSI vẫn ở vùng quá mua. [technical_snapshot; top_drivers]
- Theo dõi biên độ giá và khối lượng để đánh giá biến động tiếp diễn. [technical_snapshot.price_range_q; technical_snapshot.volume_change_q]
- Xác minh riêng nội dung LPB12503/LPB12504 bằng key facts trực tiếp về LPB; không dùng F02–F05 làm dữ kiện LPB. [N004; N005]
- Không có ngưỡng trigger định lượng bổ sung trong evidence pack. Không tự đặt ngưỡng mới.

## 6. Thời điểm review

- Review tại cuối quý kế tiếp hoặc khi xuất hiện trigger kỹ thuật/tin tức nêu trên. [holding_horizon; decision_date]
- Ngày lập card: **2025-09-30**. Cắt dữ liệu tin tức: **2025-09-30**. [decision_date; guardrails.news_cutoff]
- Không dùng dữ liệu sau ngày quyết định trong card ban đầu. [guardrails.no_post_decision_data]

## 7. Kết luận hỗ trợ quyết định

- LPB có tín hiệu kỹ thuật tích cực và được mô hình xếp **“Buy Candidate”**. [ml_signal]
- Tín hiệu này nên được xem là **tín hiệu theo dõi tích cực có điều kiện**, không phải khuyến nghị mua chắc chắn. RSI cao, biến động lớn và chất lượng evidence tin tức hạn chế làm giảm độ chắc của kết luận. [technical_snapshot; data_quality_flags; N001–N005]
- Ưu tiên xác minh tín hiệu mô hình, diễn biến MACD/RSI/SMA20, khối lượng và dữ kiện trái phiếu trực tiếp của LPB trước review tiếp theo. [ml_signal; technical_snapshot; N004; N005]

## 8. Disclaimer

- Card phục vụ hỗ trợ quyết định trong nghiên cứu học thuật. Không phải tư vấn đầu tư. [guardrails.not_investment_advice]
- Chỉ sử dụng evidence pack, dữ liệu đến **2025-09-30**. [decision_date; guardrails.news_cutoff]
- Xác suất mô hình không bảo đảm kết quả. Card không dự báo giá tuyệt đối, không cam kết lợi nhuận, không sử dụng outcome tương lai.

---

## 2025Q3_VIC_02

## 1. Tóm tắt tín hiệu

- Mô hình phát tín hiệu tăng: `pred_label=1`, `pred_proba_up=0.9970068380521899`, hạng 2 trong kỳ, lớp `Buy Candidate` [ml_signal].
- Động lượng kỹ thuật tích cực: `macd_hist_mean_q=0.20040437309325893`; giá nằm trên SMA20, `price_vs_sma20=0.22107026913812958` [technical_snapshot].
- RSI cuối kỳ `83.94257466926713`: tín hiệu tích cực nhưng có rủi ro quá mua [technical_snapshot; top_drivers].
- Khối lượng suy yếu: `volume_change_q=-0.4838746133712379` [technical_snapshot].
- Tin tức hỗn hợp: VIC, VHM tăng 1–2% ngày 30/9; thị trường chung chịu áp lực bán [N002, N003].
- Phát hành trái phiếu riêng lẻ 3.500 tỷ đồng tạo cờ rủi ro nợ [N001].

## 2. Luận điểm đầu tư chính

- VIC thuộc nhóm ứng viên cần theo dõi, nhờ tín hiệu mô hình và động lượng kỹ thuật tích cực [ml_signal; technical_snapshot].
- Luận điểm bị giảm độ tin cậy bởi RSI quá mua, khối lượng giảm, biến động cao và thông tin phát hành trái phiếu [technical_snapshot; N001].
- News hỗ trợ chưa đủ mạnh để xác nhận luận điểm dài hạn: một số key fact confidence thấp/trung bình; N004 và N005 có `relevance_hint=needs_manual_check` [N004; N005; data_quality_flags].

## 3. Yếu tố hỗ trợ

- Mô hình xếp VIC hạng 2 trong kỳ và gắn nhãn `Buy Candidate` [ml_signal].
- MACD histogram dương, giá nằm trên SMA20, phản ánh động lượng kỹ thuật đang hỗ trợ tín hiệu [technical_snapshot; top_drivers].
- VIC và VHM cùng tăng 1–2% trong phiên 30/9, cho thấy sức hút ngắn hạn của nhóm Vingroup [N002, F03].
- VinEnergo ký biên bản hợp tác chuyển giao dữ liệu đo gió ngoài khơi; bài viết nêu kế hoạch năng lượng tái tạo 30 tỷ USD và mục tiêu 80GW đến 2035. Đây là thông tin định hướng, chưa phải bằng chứng kết quả kinh doanh [N004, F02–F03].

## 4. Yếu tố cần lưu ý / rủi ro

- RSI `83.94257466926713` nằm trong vùng driver được đánh dấu `positive_but_overbought_risk`; rủi ro điều chỉnh kỹ thuật tăng [technical_snapshot; top_drivers].
- Khối lượng kỳ giảm `-0.4838746133712379`; tín hiệu giá thiếu xác nhận đầy đủ từ dòng tiền [technical_snapshot; top_drivers].
- Biên độ giá kỳ `0.748385784737404`, phản ánh biến động cao [technical_snapshot; top_drivers].
- VIC công bố phát hành trái phiếu riêng lẻ 3.500 tỷ đồng; bài viết có `event_type=debt_risk,capital`, `risk_flags=debt_risk`, confidence trung bình và extraction partial [N001].
- Thị trường chung yếu: VN-Index giảm 0,67%; HOSE có 273 mã giảm và 45 mã tăng trong phiên sáng 30/9 [N003, F01–F04].
- N002 và N003 mang các cờ `audit_issue`, `debt_risk`, `governance`; pack không cung cấp đủ chi tiết để định lượng tác động [N002; N003].
- N005 nói về đối tác và công ty liên quan, không phải bằng chứng trực tiếp về VIC; cần kiểm tra liên hệ và mức ảnh hưởng [N005; data_quality_flags].

## 5. Trigger theo dõi

- RSI giảm khỏi vùng quá mua hoặc tiếp tục duy trì cao [technical_snapshot; top_drivers].
- Giá duy trì trên hoặc suy yếu so với SMA20 [technical_snapshot; top_drivers].
- Khối lượng có xác nhận lại cho động lượng giá [technical_snapshot; top_drivers].
- Công bố chi tiết, mục đích sử dụng vốn và nghĩa vụ liên quan đến trái phiếu 3.500 tỷ đồng [N001].
- Sức mạnh VIC so với diễn biến thị trường chung và độ rộng HOSE [N002; N003].
- Xác minh thêm thông tin VinEnergo và các quan hệ đối tác do N004, N005 có độ tin cậy hoặc mức liên quan chưa đầy đủ [N004; N005].

## 6. Thời điểm review

- Review tại đầu kỳ kế tiếp, phù hợp `holding_horizon=next_quarter_or_period_return_in_signals` [holding_horizon].
- Review sớm khi xuất hiện cập nhật về trái phiếu, RSI, khối lượng hoặc diễn biến thị trường chung [N001; technical_snapshot; N003].

## 7. Kết luận hỗ trợ quyết định

- Trạng thái phù hợp: **theo dõi tích cực, chờ xác nhận**.
- Tín hiệu mô hình và kỹ thuật nghiêng tích cực [ml_signal; technical_snapshot].
- Rủi ro quá mua, khối lượng giảm, biến động cao và phát hành nợ làm giảm mức độ chắc chắn [technical_snapshot; N001].
- **Evidence tin tức chưa đủ mạnh** để xác nhận luận điểm dài hạn; cần ưu tiên kiểm tra công bố chính thức và thông tin liên quan trực tiếp đến VIC [N001; N004; N005].

## 8. Disclaimer

- Decision card phục vụ hỗ trợ quyết định và nghiên cứu học thuật, không phải khuyến nghị đầu tư.
- Chỉ dùng evidence pack, với ngày quyết định và news cutoff `2025-09-30` [decision_date; guardrails].
- Tín hiệu mô hình không bảo đảm diễn biến thực tế hoặc lợi nhuận.
- Không dự báo giá tuyệt đối.

---

## 2025Q3_VRE_03

## 1. Tóm tắt tín hiệu

- VRE có tín hiệu mô hình `Buy Candidate`; xác suất lớp tăng 0.9941, xếp hạng 3 trong kỳ (`ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`).
- Kỹ thuật nghiêng tích cực: RSI cuối kỳ 66.84; giá cao hơn SMA20 6.66% (`technical_snapshot.rsi_end_q`, `technical_snapshot.price_vs_sma20`).
- Động lượng chưa đồng nhất: MACD histogram trung bình âm; khối lượng giảm 50.37% (`technical_snapshot.macd_hist_mean_q`, `technical_snapshot.volume_change_q`).
- Tin tức có kế hoạch mở rộng và cải thiện vận hành, nhưng chất lượng bằng chứng không đồng đều. `evidence tin tức chưa đủ mạnh` để xác nhận chắc chắn luận điểm định tính (`data_quality_flags`, `N002`, `N004`).

## 2. Luận điểm đầu tư chính

- Có thể xem VRE là mã cần theo dõi với tín hiệu mô hình và kỹ thuật hiện nghiêng tích cực (`ml_signal`, `technical_snapshot.rsi_end_q`, `technical_snapshot.price_vs_sma20`).
- Luận điểm hỗ trợ gồm tỷ lệ lấp đầy và biên lợi nhuận gộp được nêu là cải thiện, cùng kế hoạch mở thêm trung tâm thương mại (`N002.F03`, `N002.F04`, `N002.F05`).
- Luận điểm bị hạn chế bởi MACD âm, thanh khoản giảm, kế hoạch huy động thêm nợ và khoản đặt cọc 1,8 nghìn tỷ đồng (`technical_snapshot.macd_hist_mean_q`, `technical_snapshot.volume_change_q`, `N004.F01`).
- Kết luận chỉ mang tính hỗ trợ sàng lọc, không phải khuyến nghị mua bán chắc chắn.

## 3. Yếu tố hỗ trợ

- Mô hình ghi nhận `Buy Candidate`, xác suất lớp tăng 0.9941 và xếp hạng 3 trong kỳ (`ml_signal.pred_label`, `ml_signal.pred_proba_up`, `ml_signal.rank_in_period`).
- RSI 66.84 và giá cao hơn SMA20 6.66% hỗ trợ trạng thái kỹ thuật hiện tại (`technical_snapshot.rsi_end_q`, `technical_snapshot.price_vs_sma20`).
- Tỷ lệ lấp đầy trung bình được nêu tăng từ 82,8% quý I/2024 lên 86,3% quý II/2025 (`N002.F03`).
- Biên lợi nhuận gộp được nêu tăng từ 53,9% lên 55,5% (`N002.F04`).
- Công ty có kế hoạch khai trương 3 trung tâm thương mại trong năm 2025 (`N002.F05`).
- Bài viết nêu kế hoạch mở bán gần 1.300 shophouse tại dự án của Vinhomes (`N002.F02`).
- Hai dự án được nêu có tỷ lệ lấp đầy cam kết trước 95% và 96%; độ tin cậy fact ở mức thấp (`N004.F05`).

## 4. Yếu tố cần lưu ý / rủi ro

- MACD histogram trung bình âm, cho thấy động lượng xu hướng chưa hỗ trợ đầy đủ (`technical_snapshot.macd_hist_mean_q`).
- Khối lượng trong kỳ giảm 50,37%, làm yếu mức xác nhận của tín hiệu kỹ thuật (`technical_snapshot.volume_change_q`).
- VRE được nêu đã đặt cọc 1,8 nghìn tỷ đồng cho dự án Cần Giờ và có kế hoạch huy động thêm nợ vay (`N004.F01`, `N004.F03`).
- Kế hoạch dài hạn gồm 4 trung tâm thương mại và 1 cụm nhà phố thương mại, tạo yêu cầu theo dõi tiến độ và nguồn vốn (`N004.F02`).
- N002 có `risk_flags`: `audit_issue`, `debt_risk`, `governance`; excerpt không cung cấp chi tiết đủ để diễn giải thêm (`N002.risk_flags`, `N002.full_text_excerpt`).
- N001, N003 và N005 có `extraction_status: partial`; N003 không có key fact; N005 chỉ có fact độ tin cậy thấp (`N001.extraction_status`, `N003.key_facts`, `N005.key_facts`).
- Độ tin cậy ghép mã tổng thể ở mức `mixed`; các kế hoạch và số liệu tin tức không đồng nhất về độ tin cậy (`data_quality_flags.ticker_matching_confidence`, `N002`, `N004`).
- Các kế hoạch mở bán, khai trương và lấp đầy chưa phải bằng chứng xác nhận hoàn tất trong evidence pack (`N002.F02`, `N002.F05`, `N004.F04`, `N004.F05`).

## 5. Trigger theo dõi

- Cập nhật mô hình và các biến kỹ thuật: RSI, MACD histogram, vị trí giá so với SMA20, khối lượng (`ml_signal`, `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.volume_change_q`).
- Theo dõi thông tin chính thức về 3 trung tâm thương mại dự kiến khai trương (`N002.F05`).
- Theo dõi tiến độ 1.300 shophouse và các dự án liên quan (`N002.F02`).
- Theo dõi tỷ lệ lấp đầy và biên lợi nhuận gộp trong cập nhật kế tiếp (`N002.F03`, `N002.F04`).
- Theo dõi khoản đặt cọc Cần Giờ, kế hoạch huy động nợ và cấu trúc nguồn vốn (`N004.F01`, `N004.F02`, `N004.F03`).
- Theo dõi giải thích chi tiết cho các cờ `audit_issue`, `debt_risk`, `governance` (`N002.risk_flags`).

## 6. Thời điểm review

- Review tại quý kế tiếp, phù hợp với `holding_horizon: next_quarter_or_period_return_in_signals` (`holding_horizon`).
- Review sớm khi xuất hiện cập nhật về nợ, Cần Giờ, khai trương trung tâm thương mại, lấp đầy, biên lợi nhuận hoặc thay đổi tín hiệu mô hình (`N002`, `N004`, `ml_signal`, `technical_snapshot`).
- Ngày lập card: 2025-09-30; chỉ dùng dữ liệu đến cutoff này (`decision_date`, `guardrails.news_cutoff`).

## 7. Kết luận hỗ trợ quyết định

- Tín hiệu hiện nghiêng tích cực ở mô hình và một số chỉ báo kỹ thuật (`ml_signal`, `technical_snapshot.rsi_end_q`, `technical_snapshot.price_vs_sma20`).
- Tín hiệu chưa đồng thuận vì MACD âm, khối lượng giảm và rủi ro nợ còn hiện diện (`technical_snapshot.macd_hist_mean_q`, `technical_snapshot.volume_change_q`, `N004.F01`).
- Tin tức có yếu tố hỗ trợ, nhưng `evidence tin tức chưa đủ mạnh` do nhiều trường partial hoặc độ tin cậy thấp (`data_quality_flags`, `N001`, `N003`, `N005`, `N002`, `N004`).
- VRE phù hợp đưa vào danh sách theo dõi và đánh giá bổ sung; không đủ cơ sở để kết luận hành động đầu tư chắc chắn.

## 8. Disclaimer

- Decision card chỉ hỗ trợ phân tích học thuật và sàng lọc tín hiệu.
- Không phải tư vấn đầu tư.
- Không dự báo giá tuyệt đối.
- Không cam kết lợi nhuận.
- Không sử dụng dữ liệu sau ngày quyết định 2025-09-30 (`guardrails.no_post_decision_data`).

---

## 2025Q3_KDH_04

## 1. Tóm tắt tín hiệu

- **Tín hiệu mô hình:** `Buy Candidate`; `pred_label = 1`; xác suất tăng mô hình `0.9921`; xếp hạng `4` trong kỳ (`ml_signal`).
- **Kỹ thuật:** MACD histogram trung bình dương `0.00954`; khối lượng thay đổi `1.0518`, hỗ trợ tín hiệu (`macd_hist_mean_q`, `volume_change_q`).
- **Tín hiệu yếu:** RSI cuối kỳ `48.20`; giá thấp hơn SMA20 `2.21%` (`rsi_end_q`, `price_vs_sma20`).
- **Tin tức:** Khối ngoại bán ròng `1.268 nghìn tỷ đồng`; KDH thuộc nhóm bị bán mạnh (`N001`, `F01`, `F04`).
- **Chất lượng định tính:** `ticker_matching_confidence = mixed`; N002 và N005 không có `key_facts`; N003 và N004 có một số dữ kiện độ tin cậy thấp. **evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản (`data_quality_flags`, `N002`, `N003`, `N004`, `N005`).

## 2. Luận điểm đầu tư chính

- Mô hình kỹ thuật xếp KDH vào nhóm **Buy Candidate**, với xác suất mô hình cao và thứ hạng 4 trong kỳ (`ml_signal.pred_proba_up`, `ml_signal.rank_in_period`, `ml_signal.signal_class`).
- Luận điểm tích cực bị cân bằng bởi giá dưới SMA20, RSI trung tính-yếu, khối ngoại bán ròng và đăng ký bán lớn từ quỹ liên quan VinaCapital (`price_vs_sma20`, `rsi_end_q`, `N001`, `N004`).
- Decision stance: **theo dõi tích cực có điều kiện**, chưa đủ cơ sở cho khuyến nghị chắc chắn.

## 3. Yếu tố hỗ trợ

- MACD histogram trung bình dương, phản ánh động lượng hỗ trợ tín hiệu tăng của mô hình (`macd_hist_mean_q = 0.0095445`).
- Khối lượng thay đổi trong kỳ ở mức `1.0518`, cho thấy mức độ quan tâm thị trường hỗ trợ tín hiệu (`volume_change_q = 1.0518421`).
- Mô hình ghi nhận tín hiệu `Buy Candidate`, xác suất `0.9921091`, xếp hạng `4` (`ml_signal`).

## 4. Yếu tố cần lưu ý / rủi ro

- Khối ngoại bán ròng toàn thị trường `1.268 nghìn tỷ đồng`; KDH bị bán mạnh (`N001`, `F01`, `F04`).
- Vietnam Investment Limited đăng ký bán gần `9,3 triệu cổ phiếu KDH` trong thời gian `30/09–29/10`; giao dịch có thể làm tỷ lệ sở hữu giảm từ `1,189%` xuống `0,361%` (`N004`, `F01`, `F02`).
- N001 gắn cờ `audit_issue`, `debt_risk`, `governance`; đây là cờ rủi ro, không đủ dữ kiện để kết luận chi tiết về từng vấn đề (`N001.risk_flags`).
- RSI cuối kỳ `48,20`, được mô hình đánh dấu `weak_or_neutral` (`rsi_end_q`, `top_drivers`).
- Giá thấp hơn SMA20 `2,21%`, được mô hình đánh dấu `weak_or_negative` (`price_vs_sma20`, `top_drivers`).
- Biên độ giá trong kỳ `36,85%`, được mô hình đánh dấu `risk_high_volatility` (`price_range_q`, `top_drivers`).
- N003 nêu động thái muốn thoái vốn của quỹ lớn, nhưng một số `key_facts` có độ tin cậy thấp (`N003`, `N003.F02`).
- N002 và N005 chỉ cung cấp thông báo giao dịch, không có `key_facts`; nội dung định tính hạn chế (`N002`, `N005`).

## 5. Trigger theo dõi

- Cập nhật kết quả thực tế giao dịch đăng ký bán trong cửa sổ `30/09–29/10` (`N004`, `F01`, `F02`).
- Theo dõi giao dịch khối ngoại đối với KDH sau phiên bán ròng được nêu trong N001 (`N001`, `F01`, `F04`, `F05`).
- Theo dõi quan hệ giá với SMA20, RSI, MACD histogram và thay đổi khối lượng trong snapshot kế tiếp (`price_vs_sma20`, `rsi_end_q`, `macd_hist_mean_q`, `volume_change_q`).
- Kiểm tra tin mới liên quan `audit_issue`, `debt_risk`, `governance`; chỉ nâng độ tin cậy khi có `key_facts` rõ hơn (`N001.risk_flags`, `N003.risk_flags`).
- Đối chiếu thông tin N002 và N005 với công bố giao dịch chi tiết, vì hai bài không có `key_facts` (`N002`, `N005`).

## 6. Thời điểm review

- Review sau khi kết thúc cửa sổ giao dịch `30/09–29/10` của Vietnam Investment Limited (`N004`).
- Review định kỳ cuối quý kế tiếp, theo `holding_horizon = next_quarter_or_period_return_in_signals` và `decision_date = 2025-09-30` (`guardrails`, `holding_horizon`).
- Review sớm hơn khi xuất hiện thay đổi rõ trong các trigger tại mục 5.

## 7. Kết luận hỗ trợ quyết định

- KDH có tín hiệu mô hình tích cực mạnh, nhưng tín hiệu kỹ thuật chưa đồng nhất và tin tức có áp lực bán, rủi ro quản trị/nợ/kiểm toán (`ml_signal`, `rsi_end_q`, `price_vs_sma20`, `N001`, `N004`).
- Trạng thái phù hợp: **Buy Candidate để theo dõi và kiểm chứng**, không phải khuyến nghị mua chắc chắn.
- Ưu tiên xác minh giao dịch bán của quỹ, dòng vốn ngoại và diễn biến MACD–RSI–SMA20 trước review tiếp theo (`N004`, `N001`, `macd_hist_mean_q`, `rsi_end_q`, `price_vs_sma20`).

## 8. Disclaimer

- Card chỉ dùng dữ liệu trong evidence pack, chốt tại `2025-09-30`; không dùng dữ liệu sau thời điểm quyết định (`decision_date`, `news_cutoff`, `no_post_decision_data`).
- Tín hiệu mô hình không bảo đảm kết quả.
- Không dự báo giá tuyệt đối. Không cam kết lợi nhuận.
- Nội dung không phải khuyến nghị đầu tư (`guardrails.not_investment_advice = true`).

---

## 2025Q3_SCR_05

## 1. Tóm tắt tín hiệu

- SCR, kỳ `2025Q3`, ngày quyết định `2025-09-30`.
- Mô hình gắn nhãn `Buy Candidate`, xác suất tín hiệu hướng lên `0.9904412570629436`, xếp hạng 5 trong kỳ. [`ml_signal`]
- Kỹ thuật nghiêng tích cực: RSI cuối kỳ `52.84985985423489`; `price_vs_sma20 = 0.022617643906099102`; `volume_change_q = 1.4161851765018045`. [`technical_snapshot`, `top_drivers`]
- Kỹ thuật còn điểm yếu: MACD histogram trung bình `-0.004962472087480404`; biên độ giá kỳ `0.3900177376582778`. [`technical_snapshot`, `top_drivers`]
- Tin tức có cờ `audit_issue`, `legal_risk`; độ khớp ticker tổng thể `mixed`. N002 có `published_at` 2025-09-03 nhưng URL chứa `/2025/10`; N003 có key facts phần lớn nói về mã khác. [`N001`, `N002`, `N003`, `data_quality_flags`]
- **Evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản riêng cho SCR. [`N001`, `N002`, `N003`, `N004`, `N005`]

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình và một số chỉ báo kỹ thuật hỗ trợ SCR vào nhóm cần theo dõi. [`ml_signal`, `technical_snapshot`, `top_drivers`]
- MACD âm, biến động giá cao, cùng cờ audit/legal làm giảm độ tin cậy của tín hiệu kỹ thuật. [`technical_snapshot`, `N001`, `N002`, `N003`, `N005`]
- Kết luận phù hợp: **theo dõi và xác minh thêm**, chưa đủ cơ sở cho khuyến nghị mua chắc chắn. [`guardrails.not_investment_advice`, `data_quality_flags.ticker_matching_confidence`]

## 3. Yếu tố hỗ trợ

- Mô hình ghi nhận `Buy Candidate`, `pred_proba_up = 0.9904412570629436`, xếp hạng 5. [`ml_signal`]
- RSI cuối kỳ `52.84985985423489` là driver hỗ trợ tín hiệu hướng lên. [`top_drivers`, `technical_snapshot.rsi_end_q`]
- `price_vs_sma20 = 0.022617643906099102`, phản ánh vị trí giá trên SMA20 theo driver mô hình. [`top_drivers`, `technical_snapshot.price_vs_sma20`]
- `volume_change_q = 1.4161851765018045`, được mô hình xếp vào nhóm hỗ trợ tín hiệu. [`top_drivers`, `technical_snapshot.volume_change_q`]
- Có công bố liên quan BCTC bán niên soát xét 2025 kèm giải trình. Đây là cơ sở để tiếp tục kiểm tra thông tin doanh nghiệp, không phải bằng chứng tích cực độc lập. [`N001`, `N003`]

## 4. Yếu tố cần lưu ý / rủi ro

- MACD histogram trung bình âm `-0.004962472087480404`, phản ánh động lượng yếu hoặc tiêu cực trong mô hình. [`top_drivers`, `technical_snapshot.macd_hist_mean_q`]
- Biên độ giá kỳ `0.3900177376582778`, cho thấy biến động cao trong bộ tín hiệu. [`top_drivers`, `technical_snapshot.price_range_q`]
- N001 gắn `audit_issue` và `legal_risk`; bài có trạng thái trích xuất `partial`, key fact độ tin cậy `medium`. [`N001.extraction_status`, `N001.key_facts`, `N001.risk_flags`]
- N002, N003 và N005 gắn các cờ `debt_risk`, `capital_dilution`, `earnings_warning`, `governance`, `legal_risk`, `audit_issue`; evidence pack chưa cung cấp đủ nội dung trực tiếp để xác nhận từng cờ cho SCR. [`N002.risk_flags`, `N003.risk_flags`, `N005.risk_flags`]
- N002 có key facts về thị trường chung; N003 có key facts liên quan QTP, GMD, PNJ, với confidence `low`. Không dùng các facts này làm bằng chứng riêng cho SCR. [`N002.key_facts`, `N003.key_facts`]
- N004 chỉ nêu nâng cấp website, không có key facts và không có risk flags. Giá trị phân tích thấp. [`N004`]

## 5. Trigger theo dõi

- Xác minh BCTC bán niên soát xét 2025 và phần giải trình của SCR; kiểm tra riêng nội dung audit/legal. [`N001`, `N003`]
- Kiểm tra lại độ khớp ticker và loại bỏ key facts không thuộc SCR, nhất là N002 và N003. [`data_quality_flags.ticker_matching_confidence`, `N002.key_facts`, `N003.key_facts`]
- Theo dõi MACD histogram: trạng thái âm hiện tại, cùng thay đổi của `price_vs_sma20`, RSI và khối lượng. [`technical_snapshot`, `top_drivers`]
- Theo dõi biến động giá khi `price_range_q` duy trì ở mức cao hoặc thay đổi mạnh. [`technical_snapshot.price_range_q`, `top_drivers`]
- Theo dõi công bố mới liên quan audit, pháp lý, công bố thông tin, nợ, pha loãng và quản trị. [`N001.risk_flags`, `N002.risk_flags`, `N003.risk_flags`, `N005.risk_flags`]

## 6. Thời điểm review

- Review vào **quý kế tiếp hoặc kỳ tín hiệu kế tiếp**, theo `holding_horizon`. [`holding_horizon`]
- Review sớm hơn nếu xuất hiện trigger về BCTC soát xét, audit/legal hoặc thay đổi rõ trong MACD, RSI, SMA20 và biến động. [`N001`, `N003`, `technical_snapshot`]

## 7. Kết luận hỗ trợ quyết định

- SCR có tín hiệu kỹ thuật và mô hình nghiêng tích cực. [`ml_signal`, `technical_snapshot`, `top_drivers`]
- Tín hiệu bị đối trọng bởi MACD âm, biến động cao và rủi ro audit/legal. [`technical_snapshot`, `N001`, `N002`, `N003`, `N005`]
- Tin tức có độ phủ cao nhưng độ khớp và chất lượng định tính không đồng đều. **Evidence tin tức chưa đủ mạnh.** [`data_quality_flags`, `N001`–`N005`]
- Phân loại hỗ trợ quyết định: **đưa vào danh sách theo dõi, chờ xác minh thêm; không xem là khuyến nghị đầu tư chắc chắn**. [`guardrails.not_investment_advice`]

## 8. Disclaimer

- Card chỉ phục vụ nghiên cứu và hỗ trợ quyết định, không phải tư vấn đầu tư. [`guardrails.not_investment_advice`]
- Dữ liệu giới hạn đến `2025-09-30`; không dùng dữ liệu sau ngày quyết định. [`decision_date`, `guardrails.news_cutoff`, `guardrails.no_post_decision_data`]
- Xác suất mô hình là đầu ra kỹ thuật, không bảo đảm kết quả. Không dự báo giá tuyệt đối, không cam kết lợi nhuận. [`ml_signal`, `guardrails`]

---

## 2025Q4_GAS_01

## 1. Tóm tắt tín hiệu

- GAS có tín hiệu mô hình **“Buy Candidate”**, xác suất nhãn tăng `0.9977169088235865`, xếp hạng **1** trong kỳ `2025Q4` (`ml_signal`).
- Động lượng kỹ thuật tích cực: lợi suất kỳ `19.47%`, giá cao hơn SMA20 `9.60%`, RSI cuối kỳ `67.52`, MACD histogram trung bình `0.1337` (`technical_snapshot`).
- Tín hiệu chưa đồng nhất: lợi suất kỳ trước `-3.36%`, khối lượng giảm `7.06%`, biên độ giá kỳ `31.62%` (`technical_snapshot`).
- Năm 2025 có doanh thu ước tính khoảng `134.000 tỷ đồng`, tăng `27%`; lợi nhuận trước thuế ước tính `14.500 tỷ đồng`, tăng `10%`. Tuy vậy, lợi nhuận trước thuế quý IV giảm hơn `26%` so với cùng kỳ (N005-F01, N005-F03, N005-F04).
- **Evidence tin tức chưa đủ mạnh để xác nhận tác động đầu tư**: nhiều key fact có độ tin cậy thấp hoặc trung bình; N003–N005 có `match_confidence: partial`; ticker matching toàn pack là `mixed` (`data_quality_flags`, N003, N004, N005).

## 2. Luận điểm đầu tư chính

- Tín hiệu định lượng đang nghiêng tích cực, dẫn đầu nhóm trong kỳ; động lượng giá, vị trí trên SMA20 và MACD cùng hỗ trợ tín hiệu (`ml_signal`, `top_drivers`, `technical_snapshot`).
- Nền tảng hoạt động năm 2025 có dấu hiệu cải thiện qua doanh thu và lợi nhuận trước thuế ước tính tăng; kết quả vượt kế hoạch doanh thu và lợi nhuận (`N005-F02`, `N005-F03`, `N005-F04`, `N005-F05`).
- Câu chuyện ngành có yếu tố hỗ trợ từ nhu cầu hạ tầng khí, LNG và chính sách năng lượng giai đoạn 2026–2030; tác động thực tế chưa được xác nhận trong evidence pack (`N004-F02` đến `N004-F05`).
- Luận điểm bị cân bằng bởi áp lực chi phí quý IV và tín hiệu thanh khoản giảm (`N005-F01`, `technical_snapshot.volume_change_q`).

## 3. Yếu tố hỗ trợ

- Mô hình xếp GAS hạng 1 trong kỳ, nhãn `Buy Candidate`, xác suất mô hình `0.9977169088235865` (`ml_signal`).
- Giá cuối kỳ cao hơn SMA20 `9.60%`; RSI `67.52` và MACD histogram trung bình `0.1337` hỗ trợ động lượng (`technical_snapshot.price_vs_sma20`, `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`).
- Lợi suất trong kỳ đạt `19.47%`; lợi suất trung bình ngày đạt `0.293%` (`technical_snapshot.return_q`, `technical_snapshot.return_mean_daily`).
- Doanh thu năm 2025 ước đạt `134.000 tỷ đồng`, tăng `27%`; lợi nhuận trước thuế ước đạt `14.500 tỷ đồng`, tăng `10%` (`N005-F03`, `N005-F04`).
- Doanh nghiệp ước hoàn thành `181%` kế hoạch doanh thu và vượt `218%` kế hoạch lợi nhuận trước thuế năm 2025 (`N005-F05`).
- PV GAS được mô tả là đơn vị nòng cốt ngành khí, chủ động bảo đảm nguồn cung khí năm 2026 (`N003-F01`, `N003-F02`).
- Chính sách năng lượng giai đoạn 2026–2030 được mô tả là tháo gỡ một số vướng mắc triển khai dự án dầu khí; nhiều dự án LNG, kho cảng LNG và nguồn khí mới được lên kế hoạch (`N004-F03`, `N004-F04`, `N004-F05`).

## 4. Yếu tố cần lưu ý / rủi ro

- Lợi nhuận trước thuế quý IV giảm hơn `26%` so với cùng kỳ dù doanh thu quý IV tăng; áp lực chi phí cần kiểm tra thêm (`N005-F01`, `N005-F02`).
- Khối lượng giao dịch giảm `7.06%` trong kỳ, làm suy yếu mức xác nhận của động lượng giá (`technical_snapshot.volume_change_q`, `top_drivers`).
- Lợi suất kỳ trước âm `3.36%`; biên độ giá kỳ `31.62%`, cho thấy tín hiệu có biến động và thiếu nhất quán (`technical_snapshot.return_prev_q`, `technical_snapshot.price_range_q`).
- Các bài N001 và N002 gắn nhiều `risk_flags` gồm `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk`; key facts không cung cấp đủ chi tiết để xác định mức độ hoặc tác động cụ thể (`N001.risk_flags`, `N002.risk_flags`).
- N002 nêu việc UBCKNN xử phạt nhiều doanh nghiệp vì lỗi công bố thông tin, nhưng evidence không xác nhận riêng GAS bị xử phạt (`N002-F02`).
- Các luận điểm về dự án khí và chính sách có `confidence: low`, không đủ cơ sở kết luận hiệu quả kinh doanh hoặc định giá (`N004-F01` đến `N004-F05`).
- Một số tin có `match_confidence: partial` hoặc nội dung trích xuất nhiễu; cần tránh dùng làm bằng chứng độc lập mạnh (`N003`, `N004`, `N005`, `data_quality_flags.ticker_matching_confidence`).

## 5. Trigger theo dõi

- Giá duy trì hoặc mất trạng thái trên SMA20; mốc tham chiếu SMA20 cuối kỳ là `66.06` (`technical_snapshot.price_vs_sma20`, `technical_snapshot.sma20_end`).
- MACD histogram suy yếu hoặc RSI thay đổi đáng kể so với cuối kỳ `67.52` (`technical_snapshot.macd_hist_mean_q`, `technical_snapshot.rsi_end_q`).
- Khối lượng cải thiện hoặc tiếp tục giảm so với mức thay đổi `-7.06%` (`technical_snapshot.volume_change_q`).
- Kết quả chính thức quý IV/năm 2025 so với số ước tính: doanh thu `134.000 tỷ đồng`, lợi nhuận trước thuế `14.500 tỷ đồng`; tập trung vào chênh lệch lợi nhuận quý IV giảm hơn `26%` (`N005-F01`, `N005-F03`, `N005-F04`).
- Cập nhật triển khai dự án LNG, kho cảng LNG, nguồn khí mới và cơ chế chính sách năng lượng (`N004-F03` đến `N004-F05`).
- Công bố thông tin liên quan cổ tức, điều kiện công ty đại chúng, quản trị, nợ, pháp lý và pha loãng vốn (`N001.event_type`, `N001.risk_flags`, `N002.event_type`, `N002.risk_flags`).

## 6. Thời điểm review

- Cuối quý tiếp theo hoặc kỳ tín hiệu kế tiếp, phù hợp `holding_horizon: next_quarter_or_period_return_in_signals`.
- Review sớm khi một trigger kỹ thuật, kết quả kinh doanh hoặc công bố thông tin trọng yếu xuất hiện.
- Mốc dữ liệu hiện tại: `decision_date: 2025-12-31`; cutoff tin tức: `2025-12-31` (`guardrails`).

## 7. Kết luận hỗ trợ quyết định

- GAS có tín hiệu định lượng tích cực và đang đứng đầu nhóm trong kỳ (`ml_signal`).
- Kết quả kinh doanh năm 2025 ước tính tăng, nhưng lợi nhuận quý IV giảm mạnh theo cùng kỳ; rủi ro tín hiệu kỹ thuật gồm khối lượng giảm, lợi suất kỳ trước âm và biên độ giá cao (`N005-F01`, `N005-F03`, `N005-F04`, `technical_snapshot`).
- Có thể xếp GAS vào **danh sách theo dõi tích cực**, không xem đây là khuyến nghị mua chắc chắn.
- Cần xác nhận bằng kết quả kinh doanh chính thức, diễn biến trên SMA20, khối lượng và thông tin dự án/quản trị trước kỳ review kế tiếp.

## 8. Disclaimer

- Decision card chỉ hỗ trợ phân tích, không phải tư vấn đầu tư (`guardrails.not_investment_advice`).
- Xác suất mô hình không bảo đảm kết quả thực tế hoặc lợi nhuận (`ml_signal`, `guardrails`).
- Không sử dụng dữ liệu sau `2025-12-31`; không dự báo giá tuyệt đối và không cam kết lợi nhuận (`guardrails.news_cutoff`, `guardrails.no_post_decision_data`).

---

## 2025Q4_MCH_02

## 1. Tóm tắt tín hiệu

- MCH nhận tín hiệu **“Buy Candidate”**; `pred_label = 1`, `pred_proba_up = 0.9944298168290505`, xếp hạng `2` trong kỳ. [ml_signal]
- Động lượng kỹ thuật hỗ trợ tín hiệu: `rsi_end_q = 66.06094473916028`, `macd_hist_mean_q = 0.22683360964630253`, `price_vs_sma20 = 0.021768580503021603`, `volume_change_q = 0.25228163165401385`. [technical_snapshot; top_drivers]
- Biến động kỳ cao: `price_range_q = 0.5656884037914879`. [technical_snapshot; top_drivers]
- Tin tức xác nhận sự kiện cổ tức, cổ phiếu quỹ và tăng vốn. [N001; N002; N004]
- Evidence tin tức chưa đủ mạnh để đánh giá tác động đến hoạt động kinh doanh hoặc định giá; N001, N003 có `extraction_status = partial`, N003 có độ tin cậy thấp. [N001; N003; data_quality_flags]

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình nghiêng về chiều tăng trong kỳ đánh giá, dựa trên xác suất mô hình cao và xếp hạng 2. Đây là tín hiệu mô hình, không phải dự báo giá tuyệt đối. [ml_signal]
- Động lượng gần đây hỗ trợ tín hiệu: `return_q = 0.7236641221374045`, `return_prev_q = 0.05161548464539358`, giá nằm trên SMA20 với `price_vs_sma20 = 0.021768580503021603`. [technical_snapshot]
- Sự kiện phân phối cho cổ đông tạo thêm bối cảnh hỗ trợ: cổ tức tiền mặt `2.500 đ/cp`, chia cổ phiếu quỹ tỷ lệ `10.000:103`, thưởng cổ phiếu tỷ lệ `10.000:2.147`. [N001; F01; N004]
- Luận điểm còn phụ thuộc xác minh rủi ro `audit_issue`, `capital_dilution`, `legal_risk` và thông tin nghị quyết đính chính. [N002; N003]

## 3. Yếu tố hỗ trợ

- Mô hình xếp MCH vào nhóm **“Buy Candidate”**, `pred_proba_up = 0.9944298168290505`. [ml_signal]
- RSI cuối kỳ, MACD histogram và vị trí giá trên SMA20 đều được mô hình đánh dấu `supports_up_signal`. [top_drivers]
- Lợi suất kỳ hiện tại và kỳ trước cùng được mô hình đánh dấu `supports_up_signal`: `return_q = 0.7236641221374045`; `return_prev_q = 0.05161548464539358`. [top_drivers]
- Khối lượng tăng `25.2281631654013%` trong kỳ, được mô hình đánh dấu `supports_up_signal`. [technical_snapshot; top_drivers]
- MCH có lịch tạm ứng cổ tức đợt 2 năm 2025 bằng tiền, chia cổ phiếu quỹ và phát hành cổ phiếu tăng vốn. [N001; N002; N004]

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ ở mức `0.5656884037914879`; mô hình gắn cờ `risk_high_volatility`. [technical_snapshot; top_drivers]
- Lợi suất trễ hai kỳ âm `-0.10768823373642865`; mô hình đánh dấu `weak_or_negative`. [technical_snapshot; top_drivers]
- N002 có các cờ `audit_issue`, `capital_dilution`, `legal_risk`. Evidence pack không cung cấp chi tiết đủ để định lượng hoặc kết luận tác động. [N002]
- N003 là thông báo đính chính nghị quyết HĐQT; `extraction_status = partial`, độ tin cậy key fact `low`, `relevance_hint = needs_manual_check`. [N003]
- N005 liên quan chốt danh sách cổ đông lấy ý kiến bằng văn bản nhưng không có `key_facts`; cần kiểm tra thêm. [N005]
- Độ tin cậy ghép mã tổng thể ở mức `mixed`. [data_quality_flags]
- Sự kiện cổ tức và phát hành cổ phiếu xác nhận quyền lợi, không tự chứng minh cải thiện lợi nhuận hoặc định giá. [N001; N002; N004]

## 5. Trigger theo dõi

- Cập nhật khi `pred_label`, `pred_proba_up` hoặc `signal_class` thay đổi. [ml_signal]
- Kiểm tra diễn biến `rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q` và `price_range_q`. [technical_snapshot]
- Theo dõi ngày giao dịch không hưởng quyền `09/01/2026` và ngày đăng ký cuối cùng `12/01/2026`. [N002]
- Xác minh thực hiện cổ phiếu quỹ tỷ lệ `10.000:103`, thưởng cổ phiếu tỷ lệ `10.000:2.147`, cổ tức tiền mặt `2.500 đ/cp`. [N001; F01; N002]
- Kiểm tra nội dung nghị quyết đính chính số 38 ngày 24/12/2025. [N003]
- Kiểm tra nội dung lấy ý kiến cổ đông bằng văn bản. [N005]
- Làm rõ các cờ `audit_issue`, `capital_dilution`, `legal_risk` trước khi nâng mức tin cậy. [N002]

## 6. Thời điểm review

- Review cuối quý hoặc kỳ tiếp theo, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm quanh các mốc `09/01/2026` và `12/01/2026` để kiểm tra sự kiện quyền cổ đông. [N002]
- Evidence pack không cung cấp ngày cụ thể cho kỳ review kế tiếp ngoài các mốc trên. [holding_horizon; N002]

## 7. Kết luận hỗ trợ quyết định

- MCH có tín hiệu mô hình và động lượng kỹ thuật tích cực; có thêm sự kiện cổ tức, cổ phiếu quỹ và tăng vốn. [ml_signal; technical_snapshot; N001; N002]
- Biến động cao, động lượng lịch sử không đồng nhất, ticker matching ở mức `mixed`; tin tức còn cờ cần xác minh. [technical_snapshot; data_quality_flags; N002; N003; N005]
- Có thể xếp MCH vào nhóm **ứng viên cần theo dõi ưu tiên**, chưa đủ evidence để kết luận đầu tư chắc chắn. [ml_signal; data_quality_flags; N002]

## 8. Disclaimer

Decision card phục vụ hỗ trợ nghiên cứu, không phải khuyến nghị đầu tư. Không dự báo giá tuyệt đối, không cam kết lợi nhuận. Phân tích chỉ dùng evidence pack với ngày quyết định `2025-12-31` và news cutoff `2025-12-31`; không sử dụng outcome tương lai.

---

## 2025Q4_ABB_03

## 1. Tóm tắt tín hiệu

- ABB, kỳ `2025Q4`, ngày quyết định `2025-12-31`.
- Mô hình gắn nhãn `Buy Candidate`, xác suất tín hiệu tăng `0.9925587966120623`, xếp hạng `3` trong kỳ. [ml_signal]
- Động lượng kỹ thuật tích cực: `rsi_end_q = 66.26886472073552`, `macd_hist_mean_q = 0.0216105821083708`, `price_vs_sma20 = 0.028815218911735965`. [technical_snapshot]
- Khối lượng giảm `-0.3838155395206998`, tạo tín hiệu yếu hoặc tiêu cực. [technical_snapshot; top_drivers]
- Tin nổi bật: kế hoạch chào bán hơn 310,5 triệu cổ phiếu, giá 10.000 đồng/cp, tỷ lệ quyền `100:30`; vốn điều lệ dự kiến tăng từ 10.350 tỷ lên 13.455 tỷ đồng. [N001; F01–F04]
- Chất lượng tin: độ phủ cao nhưng `ticker_matching_confidence = mixed`; N003 có trạng thái `partial`. [data_quality_flags; N003]

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình nghiêng mạnh về chiều tăng trong kỳ theo dõi kế tiếp, dựa trên nhãn `Buy Candidate`, xác suất mô hình cao, RSI, MACD và vị trí giá trên SMA20. [ml_signal; technical_snapshot]
- Kế hoạch tăng vốn tạo bối cảnh hỗ trợ hoặc trung tính, nhưng chưa đủ dữ liệu để đánh giá hiệu quả sử dụng vốn. [N001; F01–F04]
- Tín hiệu kỹ thuật chưa được xác nhận đầy đủ bởi thanh khoản và evidence định tính. **evidence tin tức chưa đủ mạnh** để hình thành kết luận cơ bản độc lập. [technical_snapshot; data_quality_flags; N003–N005]

## 3. Yếu tố hỗ trợ

- Mô hình xếp ABB vào nhóm `Buy Candidate`, xác suất tín hiệu tăng `0.9925587966120623`. [ml_signal]
- RSI cuối kỳ `66.26886472073552`, MACD histogram trung bình dương `0.0216105821083708`, giá nằm trên SMA20 với `price_vs_sma20 = 0.028815218911735965`. [technical_snapshot; top_drivers]
- ABB có kế hoạch chào bán hơn 310,5 triệu cổ phiếu cho cổ đông hiện hữu, giá 10.000 đồng/cp, tỷ lệ quyền `100:30`. [N001; F02–F03]
- Vốn điều lệ dự kiến tăng từ 10.350 tỷ lên 13.455 tỷ đồng. Đây là yếu tố hỗ trợ hoặc bối cảnh, không phải bằng chứng về hiệu quả kinh doanh. [N001; F01; F04]
- N001 có `match_confidence = exact`, `extraction_status = ok`, và tin liên quan trực tiếp đến ABB. [N001]

## 4. Yếu tố cần lưu ý / rủi ro

- Chào bán thêm có cờ `capital_dilution`; tác động pha loãng cần được theo dõi cùng kết quả thực hiện quyền. [N001; risk_flags; F01–F03]
- Khối lượng giảm `-0.3838155395206998`, cho thấy mức độ quan tâm thị trường yếu hơn trong kỳ. [technical_snapshot; top_drivers]
- Biên độ giá kỳ `price_range_q = 0.2842016094875053`, là bối cảnh biến động cần lưu ý. [technical_snapshot; top_drivers]
- Evidence tin tức có độ khớp ticker `mixed`; N003 chỉ có 72 ký tự toàn văn và trạng thái `partial`. [data_quality_flags; N003]
- N002, N004 và N005 chứa các key fact về doanh nghiệp hoặc sự kiện khác; không đủ căn cứ gán trực tiếp các rủi ro nợ, pháp lý, kiểm toán hoặc lợi nhuận cho ABB. [N002; N004; N005]
- Pack chưa nêu mục đích sử dụng vốn, mức độ hoàn tất chào bán hoặc hiệu quả vốn sau phát hành. [N001; F01–F05]

## 5. Trigger theo dõi

- Ngày đăng ký cuối cùng chốt danh sách cổ đông: `15/01`; kiểm tra thông báo và tiến độ thực hiện quyền. [N001; F05]
- Cập nhật số cổ phiếu phát hành và vốn điều lệ sau chào bán; đối chiếu với mức dự kiến 13.455 tỷ đồng. [N001; F01; F04]
- Theo dõi RSI, MACD, vị trí giá so SMA20 và thay đổi khối lượng trong kỳ mới. [technical_snapshot; top_drivers]
- Theo dõi tài liệu và diễn biến Đại hội đồng cổ đông ABB. [N003; N005]
- Kiểm tra tin mới có `match_confidence` rõ ràng và key facts trực tiếp về ABB trước khi nâng mức tin cậy định tính. [data_quality_flags; N001; N003–N005]

## 6. Thời điểm review

- Review cuối quý kế tiếp, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm hơn khi có cập nhật về chốt quyền, hoàn tất chào bán, vốn điều lệ hoặc tài liệu Đại hội đồng cổ đông. [N001; N003; N005]

## 7. Kết luận hỗ trợ quyết định

- ABB có tín hiệu kỹ thuật mạnh và có thể nằm trong danh sách theo dõi hoặc thẩm định tiếp. [ml_signal; technical_snapshot]
- Kế hoạch tăng vốn là yếu tố hỗ trợ hoặc bối cảnh, đồng thời tạo rủi ro pha loãng. [N001; risk_flags]
- Khối lượng giảm và chất lượng một phần evidence tin tức còn hạn chế. **evidence tin tức chưa đủ mạnh** cho kết luận đầu tư độc lập dựa trên nền tảng cơ bản. [technical_snapshot; data_quality_flags; N003–N005]
- Không kết luận mua hoặc bán chỉ từ card này.

## 8. Disclaimer

- Card chỉ dùng evidence pack đến ngày `2025-12-31`. [decision_date; guardrails]
- Nhãn mô hình và `pred_proba_up` là tín hiệu mô hình, không phải dự báo giá tuyệt đối, không bảo đảm kết quả. [ml_signal; guardrails]
- Không phải tư vấn đầu tư. Cần thẩm định thêm trước quyết định. [guardrails]
- `full_text_ref`, `content_hash`, `full_text_chars` chỉ dùng audit; card không giả định nội dung toàn văn ngoài phần đã cung cấp. [N001–N005]

---

## 2025Q4_ELC_04

## 1. Tóm tắt tín hiệu

- ELC có tín hiệu mô hình `Buy Candidate`; `pred_label=1`, `pred_proba_up=0.985207419352861`, xếp hạng 4 trong kỳ. `[ml_signal]`
- Kỹ thuật hỗ trợ: `macd_hist_mean_q=0.033366134298060984`; `price_vs_sma20=0.04937613309160707`. `[technical_snapshot]`
- Rủi ro kỹ thuật: `rsi_end_q=71.35028331481989`, bị mô hình gắn cờ `positive_but_overbought_risk`; `volume_change_q=-0.45543372706426505`. `[top_drivers]`
- Tin tức có độ phủ cao nhưng độ khớp mã chỉ `mixed`. N001 và N003 trích xuất một phần, không có `key_facts`; N002, N004, N005 chứa nhiều dữ kiện không liên quan ELC. Evidence tin tức chưa đủ mạnh. `[data_quality_flags] [N001] [N002] [N003] [N004] [N005]`

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình và một số chỉ báo kỹ thuật nghiêng tích cực. `[ml_signal] [macd_hist_mean_q] [price_vs_sma20]`
- Độ tin cậy bị giảm bởi RSI cao, khối lượng giảm và chất lượng evidence tin tức không đồng nhất. `[rsi_end_q] [volume_change_q] [data_quality_flags]`
- Thông tin ELC cụ thể chủ yếu liên quan mua lại hoặc thu hồi cổ phiếu ESOP của CBNV nghỉ việc; pack chưa có `key_facts` đủ rõ về hoạt động kinh doanh hoặc kết quả lợi nhuận. `[N001] [N003] [N004] [N005]`

## 3. Yếu tố hỗ trợ

- Mô hình phân loại ELC là `Buy Candidate`, xác suất hướng lên của mô hình ở mức `0.985207419352861`. Đây là tín hiệu mô hình, không phải xác nhận kết quả. `[ml_signal]`
- MACD histogram trung bình dương, hỗ trợ động lượng xu hướng. `[macd_hist_mean_q] [top_drivers]`
- `price_vs_sma20` dương, cho thấy vị trí giá nằm trên SMA20 theo biến dữ liệu. `[price_vs_sma20] [sma20_end]`
- N001, N003, N004, N005 ghi nhận thông báo hoặc nghị quyết về mua lại/thu hồi cổ phiếu ESOP của CBNV nghỉ việc. Thông tin này tạo bối cảnh doanh nghiệp, chưa đủ làm luận điểm cơ bản mạnh. `[N001] [N003] [N004] [N005]`

## 4. Yếu tố cần lưu ý / rủi ro

- RSI cuối kỳ `71.35028331481989`; mô hình ghi nhận rủi ro quá mua. `[rsi_end_q] [top_drivers]`
- Khối lượng thay đổi `-0.45543372706426505`, phản ánh mức quan tâm thị trường yếu hơn trong kỳ theo dữ liệu mô hình. `[volume_change_q] [top_drivers]`
- Biên độ giá trong kỳ `0.22303045504901645`, cần lưu ý biến động. `[price_range_q]`
- N002, N004, N005 có `risk_flags`: `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk`. Các cờ này thiếu `key_facts` ELC tương ứng; không nên xem là kết luận đã xác thực. `[N002] [N004] [N005]`
- Ticker matching ở mức `mixed`; nhiều `key_facts` trong N002, N004, N005 nói về QTP, GMD, UNI, PC1, LSG, SP2, Brand Finance hoặc PNJ. `[data_quality_flags] [N002] [N004] [N005]`
- N001 và N003 có `extraction_status=partial`, `key_facts=[]`; nội dung định tính còn mỏng. `[N001] [N003]`

## 5. Trigger theo dõi

- Theo dõi RSI, MACD histogram và vị trí giá so với SMA20; đánh giá lại nếu động lượng suy yếu hoặc giá không còn duy trì vị trí trên SMA20. `[rsi_end_q] [macd_hist_mean_q] [price_vs_sma20]`
- Theo dõi diễn biến `volume_change_q`; khối lượng tiếp tục suy giảm là tín hiệu cần thận trọng. `[volume_change_q]`
- Xác nhận thông tin thực hiện phương án mua lại hoặc thu hồi ESOP, thay vì chỉ dựa trên tiêu đề và thông báo hiện có. `[N001] [N003] [N004]`
- Làm rõ từng `risk_flag` bằng evidence ELC khớp mã và `key_facts` cụ thể. `[N002] [N004] [N005] [data_quality_flags]`
- Rà soát lại các bài có dữ kiện lẫn mã khác trước khi nâng trọng số tin tức. `[N002] [N004] [N005]`

## 6. Thời điểm review

- Review vào cuối quý kế tiếp theo `holding_horizon`; review sớm khi trigger kỹ thuật hoặc chất lượng tin tức thay đổi. `[holding_horizon]`
- Mốc quyết định hiện tại: `2025-12-31`; news cutoff: `2025-12-31`. `[decision_date] [guardrails]`

## 7. Kết luận hỗ trợ quyết định

- Tín hiệu mô hình nghiêng tích cực, nhưng card chỉ phù hợp hỗ trợ theo dõi có điều kiện. `[ml_signal]`
- Kỹ thuật có điểm hỗ trợ, song RSI cao, khối lượng giảm và evidence tin tức yếu làm giảm độ chắc của luận điểm. `[technical_snapshot] [data_quality_flags]`
- Chưa đủ evidence để kết luận hành động đầu tư chắc chắn. Ưu tiên xác minh tin ELC khớp mã và theo dõi động lượng trước review tiếp theo. `[N001] [N002] [N003] [N004] [N005]`

## 8. Disclaimer

- Card dùng dữ liệu đến `2025-12-31`, không dùng dữ liệu sau thời điểm quyết định. `[guardrails]`
- Đây không phải khuyến nghị đầu tư. `[guardrails.not_investment_advice]`
- Xác suất mô hình không bảo đảm kết quả. Card không dự báo giá tuyệt đối, không cam kết lợi nhuận. `[ml_signal]`

---

## 2025Q4_VBB_05

## 1. Tóm tắt tín hiệu

- VBB thuộc nhóm **“Buy Candidate”**; `pred_label = 1`, `pred_proba_up = 0.9822`, xếp hạng 5 trong kỳ (`ml_signal`).
- Kỹ thuật phân hóa: giá cuối kỳ trên SMA20 khoảng 0,91%; MACD histogram âm; RSI 47,87; khối lượng giảm 58,24% (`technical_snapshot`, `top_drivers`).
- Tin tức có độ phủ cao nhưng `ticker_matching_confidence = mixed`; một số bài có dữ kiện lẫn doanh nghiệp khác (`data_quality_flags`, N001, N004, N005).
- **Evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản hoặc rủi ro pháp lý riêng cho VBB.

## 2. Luận điểm đầu tư chính

- VBB có tín hiệu định lượng mạnh từ mô hình, phù hợp đưa vào nhóm cần theo dõi hoặc sàng lọc thêm (`ml_signal`).
- Tín hiệu chưa đồng thuận: giá trên SMA20 hỗ trợ, nhưng MACD âm và khối lượng giảm cho thấy động lượng và mức độ quan tâm thị trường còn yếu (`price_vs_sma20`, `macd_hist_mean_q`, `volume_change_q`).
- Sự kiện phát hành cổ phiếu và quyền mua của lãnh đạo là dữ kiện vốn cần theo dõi, chưa đủ để kết luận về chất lượng tăng trưởng hoặc định giá (N002, N004, N005).

## 3. Yếu tố hỗ trợ

- Xác suất dự báo tăng của mô hình ở mức 0,9822; tín hiệu được xếp “Buy Candidate” (`pred_proba_up`, `signal_class` trong `ml_signal`).
- Giá cuối kỳ cao hơn SMA20, cho thấy trạng thái kỹ thuật ngắn hạn còn điểm hỗ trợ (`price_vs_sma20 = 0.009076`, `sma20_end = 9.365`).
- Hai Phó Tổng Giám đốc đã thực hiện quyền mua cổ phần trong đợt chào bán cho cổ đông hiện hữu; dữ kiện có độ tin cậy trung bình, chỉ nên xem là bối cảnh hỗ trợ (`N004`, `N005`, `key_facts.direction = support_or_context`).
- VBB đã báo cáo phát hành 270.940.550 cổ phiếu ra công chúng, xác nhận sự kiện huy động vốn đã hoàn tất theo dữ liệu cung cấp (`N002`, `event_type = capital`).

## 4. Yếu tố cần lưu ý / rủi ro

- MACD histogram trung bình âm, phản ánh động lượng xu hướng yếu hoặc tiêu cực (`macd_hist_mean_q = -0.005514`, `top_drivers`).
- RSI cuối kỳ 47,87, chưa cho thấy động lượng mạnh (`rsi_end_q`, `top_drivers`).
- Khối lượng giao dịch giảm 58,24%, làm yếu mức xác nhận của tín hiệu (`volume_change_q = -0.582441`, `top_drivers`).
- Đợt phát hành 270.940.550 cổ phiếu tạo rủi ro pha loãng cần đánh giá thêm (`N002`, `risk_flags = capital_dilution`).
- Số cổ phiếu có quyền biểu quyết đang lưu hành được thông báo là 1.076.897.384 cổ phiếu; cần đối soát với dữ liệu sau phát hành (`N003`).
- N001 có `risk_flags` gồm `audit_issue`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk`, nhưng `key_facts` chứa nhiều thông tin về ACV, PVT, CC1 và VIX; không nên xem toàn bộ là rủi ro riêng của VBB (`N001`).
- N004 và N005 có tiêu đề, lead liên quan VBB nhưng phần `key_facts` cũng lẫn dữ kiện doanh nghiệp khác; chất lượng bằng chứng định tính bị hạn chế (`N004`, `N005`).

## 5. Trigger theo dõi

- Cập nhật `macd_hist_mean_q`, `rsi_end_q`, `price_vs_sma20`; tín hiệu cần xem xét lại khi các chỉ báo không còn hỗ trợ (`technical_snapshot`).
- Theo dõi `volume_change_q` để đánh giá mức xác nhận của biến động kỹ thuật (`technical_snapshot`).
- Đối soát số cổ phiếu lưu hành sau đợt phát hành và các công bố liên quan pha loãng (`N002`, `N003`).
- Theo dõi công bố tiếp theo về quyền mua của lãnh đạo và thay đổi nhân sự liên quan VBB (`N001`, `N004`, `N005`).
- Làm sạch, xác minh lại dữ kiện tin tức trước khi dùng cho luận điểm cơ bản hoặc pháp lý (`data_quality_flags`, N001, N004, N005).

## 6. Thời điểm review

- Review vào **cuối quý kế tiếp, 2026Q1**, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals` và `decision_date = 2025-12-31`.
- Review sớm khi trigger kỹ thuật, phát hành vốn hoặc chất lượng dữ liệu tin tức thay đổi.

## 7. Kết luận hỗ trợ quyết định

- VBB có tín hiệu mô hình mạnh nhưng nền kỹ thuật chưa đồng thuận.
- Có bối cảnh phát hành vốn và quyền mua nội bộ; đồng thời tồn tại rủi ro pha loãng và hạn chế chất lượng tin tức.
- Có thể xếp VBB vào nhóm **ứng viên cần theo dõi và xác minh thêm**, chưa đủ evidence để kết luận hành động đầu tư chắc chắn (`ml_signal`, `technical_snapshot`, N002–N005).

## 8. Disclaimer

- Decision card chỉ hỗ trợ phân tích, không phải khuyến nghị đầu tư (`guardrails.not_investment_advice = true`).
- Nội dung chỉ dùng evidence pack đến ngày 2025-12-31.
- Không dự báo giá tuyệt đối, không cam kết lợi nhuận, không kết luận chắc chắn về kết quả tương lai.

---

## 2026Q1_GMD_01

## 1. Tóm tắt tín hiệu

- GMD được mô hình `technical_Config_A_from_existing_pipeline` xếp loại **“Buy Candidate”**, xác suất mô hình cho chiều tăng `0.9918332061384683`, hạng `1` trong kỳ 2026Q1. Đây là tín hiệu mô hình, không phải bảo đảm kết quả. [ml_signal]
- Driver kỹ thuật chính cùng chiều: `rsi_end_q = 57.56055987287681`, `macd_hist_mean_q = 0.13479312514556438`, `price_vs_sma20 = 0.040538720538720804`, `volume_change_q = 0.3857443663750644`. [top_drivers; technical_snapshot]
- Tin tức nêu hợp tác Gemadept–CJ Logistics về Logistics và Shipping, gồm GMD tập trung 100% Shipping và nắm 49% MKL. [N004; N004/F03–F05]
- **Evidence tin tức chưa đủ mạnh** để xác nhận tác động tài chính hoặc lợi nhuận. Nhiều bài có `match_confidence` partial, trích xuất nhiễu, hoặc thiếu số liệu. [data_quality_flags; N001; N003; N005]

## 2. Luận điểm đầu tư chính

- GMD là **ứng viên cần theo dõi thêm** nhờ tín hiệu mô hình rất tích cực và nhiều driver kỹ thuật hỗ trợ. [ml_signal; top_drivers]
- Hợp tác chiến lược với CJ Logistics tạo bối cảnh hỗ trợ cho hoạt động Logistics và Shipping, nhưng evidence chưa chứng minh tác động cụ thể lên doanh thu, lợi nhuận, nợ hoặc định giá. [N004/F01–F05]
- Luận điểm hiện nghiêng về **tín hiệu kỹ thuật**, chưa đủ cơ sở để kết luận theo hướng cơ bản. [technical_snapshot; N004; N005]

## 3. Yếu tố hỗ trợ

- Mô hình xếp GMD hạng `1`, nhãn **“Buy Candidate”**, xác suất mô hình `0.9918332061384683`. [ml_signal]
- RSI cuối kỳ, MACD histogram trung bình và vị trí giá so với SMA20 đều được mô hình đánh dấu `supports_up_signal`. [top_drivers; technical_snapshot]
- Khối lượng thay đổi trong kỳ `0.3857443663750644`, cũng được mô hình đánh dấu `supports_up_signal`. [top_drivers; technical_snapshot]
- GMD và CJ Logistics thống nhất tối ưu hóa chiến lược Logistics và Shipping. [N004; N004/F01]
- GMD được nêu là đầu tư và quản lý 100% hoạt động Shipping, đồng thời nắm 49% cổ phần MKL. [N004/F03]
- Quan hệ hợp tác giữa hai bên được mô tả kéo dài hơn 8 năm. [N004/F02]

## 4. Yếu tố cần lưu ý / rủi ro

- Biên độ giá trong kỳ `price_range_q = 0.40646086897736294`; mô hình gắn nhãn `risk_high_volatility`. [top_drivers; technical_snapshot]
- Tín hiệu mô hình không thay thế kiểm chứng cơ bản; evidence pack không cung cấp số liệu tài chính cụ thể từ BCTC 2025. [N005; N005/key_facts]
- `risk_flags` của N002 và N005 gồm `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk`. Đây là cờ cảnh báo dữ liệu, chưa đủ chi tiết để khẳng định từng rủi ro đang xảy ra. [N002/risk_flags; N005/risk_flags]
- Tin N003 có `match_confidence = partial`; một số key facts mang ngày 30/06–02/07, sau `decision_date = 2026-03-31` và `news_cutoff = 2026-03-31`. Không dùng các facts này làm evidence quyết định. [N003; N003/F02–F05; guardrails]
- N002 và N005 cũng chứa key facts ngày 30/06–02/07, mâu thuẫn thời điểm với cutoff. Không dùng các facts đó. [N002/F02–F05; N005/F02–F05; guardrails]
- Độ tin cậy ghép mã ở mức `mixed`; N001 và N003 có trích xuất hoặc ghép mã chưa hoàn toàn chắc chắn. [data_quality_flags; N001; N003]

## 5. Trigger theo dõi

- Kiểm tra công bố chính thức về việc triển khai hợp tác GMD–CJ Logistics, đặc biệt phạm vi Shipping, 49% MKL và hoạt động 3PL. [N004/F03–F05]
- Kiểm tra chi tiết Nghị quyết HĐQT số 057 về chuyển nhượng cổ phần. [N002/title; N002/lead]
- Làm rõ các `risk_flags` liên quan kiểm toán, pha loãng, nợ, lợi nhuận, quản trị và pháp lý. [N002/risk_flags; N005/risk_flags]
- Theo dõi lại `rsi_end_q`, `macd_hist_mean_q`, `price_vs_sma20`, `volume_change_q` và `price_range_q` trong kỳ mới. [technical_snapshot; top_drivers]
- Rà soát lại nguồn tin khi `match_confidence`, `extraction_status` hoặc thời điểm bài viết tiếp tục mâu thuẫn. [data_quality_flags; N001; N002; N003; N005]

## 6. Thời điểm review

- Review trong **kỳ kế tiếp**, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. [holding_horizon]
- Review sớm hơn nếu xuất hiện công bố chính thức mới, risk flag được xác nhận, hoặc các driver kỹ thuật mất trạng thái hỗ trợ. [N002; N004; N005; top_drivers]

## 7. Kết luận hỗ trợ quyết định

- GMD có tín hiệu mô hình và kỹ thuật tích cực, phù hợp đưa vào **danh sách ứng viên cần nghiên cứu tiếp**. [ml_signal; top_drivers]
- Hợp tác GMD–CJ Logistics là yếu tố hỗ trợ định tính, nhưng chưa đủ evidence để xác nhận cải thiện tài chính. [N004; N004/F01–F05]
- Biến động cao, risk flags chưa được giải thích đầy đủ và chất lượng tin tức không đồng nhất. [technical_snapshot; N002/risk_flags; N005/risk_flags; data_quality_flags]
- Không nên dùng card này như khuyến nghị mua bán độc lập.

## 8. Disclaimer

- Thông tin chỉ dựa trên evidence pack, cutoff `2026-03-31`. [guardrails]
- Kết quả mô hình không bảo đảm kết quả đầu tư. [ml_signal]
- Đây không phải tư vấn hoặc khuyến nghị đầu tư chắc chắn. [guardrails/not_investment_advice]
- Evidence tin tức có mâu thuẫn thời điểm và chất lượng trích xuất; cần xác minh trước khi ra quyết định. [data_quality_flags; N001–N005]

---

## 2026Q1_EVF_02

## 1. Tóm tắt tín hiệu

- Tín hiệu mô hình nghiêng tích cực: `signal_class = Buy Candidate`, `pred_label = 1`, `pred_proba_up = 0.9916400447480391`, xếp hạng `2` trong kỳ. [ml_signal]
- Kỹ thuật hỗ trợ tín hiệu: RSI cuối kỳ `56.9772`, MACD histogram trung bình `0.0473`, giá cao hơn SMA20 `2.47%`, khối lượng tăng `76.00%`. [technical_snapshot.rsi_end_q; `macd_hist_mean_q`; `price_vs_sma20`; `volume_change_q`]
- Tin doanh nghiệp cho thấy kết quả 2025 vượt kế hoạch; EVF không chia cổ tức và đặt mục tiêu lợi nhuận trước thuế 2026 là `1,325 tỷ đồng`. [N005/F01–F04]
- EVF có nghị quyết phê duyệt phát hành trái phiếu tăng vốn cấp 2 riêng lẻ năm 2026. [N002/F01; N004/F01]
- Tín hiệu tổng thể tích cực nhưng chưa sạch. Biên độ giá trong kỳ ở mức `0.3699`; tin tức có nội dung nhiễu tại N001 và N002 có trạng thái trích xuất `partial`. [technical_snapshot.price_range_q; N001; N002; `data_quality_flags`]
- Evidence tin tức chưa đủ mạnh để xác nhận rủi ro pháp lý, quản trị hoặc chất lượng tín dụng của riêng EVF.

## 2. Luận điểm đầu tư chính

- EVF phù hợp nhóm **theo dõi theo tín hiệu kỹ thuật**, vì mô hình và nhiều biến kỹ thuật cùng nghiêng tích cực. [ml_signal; `technical_snapshot`; `top_drivers`]
- Luận điểm bị cân bằng bởi việc không chia cổ tức, kế hoạch phát hành trái phiếu tăng vốn cấp 2 và biến động giá cao. [N005/F01; N002/F01; N004/F01; `technical_snapshot.price_range_q`]
- Mục tiêu lợi nhuận 2026 là mục tiêu trong tài liệu doanh nghiệp, không phải dự báo độc lập. [N005/F04]

## 3. Yếu tố hỗ trợ

- Mô hình xếp EVF vào nhóm `Buy Candidate`, với `pred_proba_up = 0.9916400447480391`. Đây là đầu ra mô hình, không phải bảo đảm kết quả. [`ml_signal`]
- RSI cuối kỳ `56.9772` và MACD histogram trung bình `0.0473` là các driver hỗ trợ tín hiệu tăng trong mô hình. [`technical_snapshot.rsi_end_q`; `technical_snapshot.macd_hist_mean_q`; `top_drivers`]
- Giá nằm trên SMA20 `2.47%`, cho thấy trạng thái kỹ thuật ngắn hạn hỗ trợ tín hiệu. [`technical_snapshot.price_vs_sma20`; `top_drivers`]
- Khối lượng tăng `76.00%`, phản ánh mức độ quan tâm thị trường cao hơn trong kỳ. [`technical_snapshot.volume_change_q`; `top_drivers`]
- EVF được mô tả là vượt kế hoạch lợi nhuận 2025; tài liệu công ty đặt mục tiêu lợi nhuận trước thuế 2026 ở `1,325 tỷ đồng`. [N005/F02; N005/F04]
- Có thông báo khôi phục giao dịch với trái phiếu EVF12201. Đây là thông tin bối cảnh, chưa đủ để kết luận chất lượng tín dụng. [N003/F01]

## 4. Yếu tố cần lưu ý / rủi ro

- EVF không chia cổ tức dù được mô tả là vượt kế hoạch lợi nhuận 2025; điều này làm giảm luận điểm thu nhập tiền mặt. [N005/F01]
- EVF đề xuất trích thưởng cho HĐQT, BKS và Ban điều hành. Cần theo dõi quyết nghị chính thức và mức phân bổ. [N005/F02]
- Phương án phát hành trái phiếu tăng vốn cấp 2 riêng lẻ năm 2026 tạo nhu cầu kiểm tra thêm về điều khoản, quy mô và tiến độ; pack chưa cung cấp các chi tiết này. [N002/F01; N004/F01]
- Biên độ giá trong kỳ `0.3699232379623168`, cho thấy biến động đáng lưu ý. [`technical_snapshot.price_range_q`; `top_drivers`]
- N001 có tiêu đề liên quan EVF nhưng `key_facts` chứa nội dung về ACV, PVT, CC1 và VIX. Không dùng các nội dung này làm rủi ro trực tiếp của EVF. [N001/F02–F05]
- `ticker_matching_confidence = mixed`; N002 có `extraction_status = partial`. Độ tin cậy định tính cần kiểm tra lại. [`data_quality_flags`; N002]
- Các `risk_flags` tại N001 và N003 gồm `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk`, nhưng pack không cung cấp đủ key facts EVF để xác nhận từng rủi ro. [N001/risk_flags; N003/risk_flags]

## 5. Trigger theo dõi

- Tài liệu và nghị quyết sau ĐHĐCĐ thường niên dự kiến ngày `03/04/2026`: tập trung vào cổ tức, thưởng và mục tiêu 2026. [N005/F03; N005/F01–F04]
- Công bố tiếp theo về phát hành trái phiếu tăng vốn cấp 2: điều khoản, quy mô, hoàn tất phát hành. [N002/F01; N004/F01]
- Cập nhật tình trạng giao dịch và công bố liên quan trái phiếu EVF12201. [N003/F01]
- Kiểm tra lại RSI, MACD histogram, vị trí giá so với SMA20, khối lượng và biên độ giá tại kỳ cập nhật tiếp theo. [`technical_snapshot`; `top_drivers`]
- Xác minh lại nội dung N001 bằng công bố chính thức của EVF trước khi dùng cho đánh giá quản trị hoặc pháp lý. [N001; `data_quality_flags`]

## 6. Thời điểm review

- Review chính: cuối quý kế tiếp, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. [`holding_horizon`]
- Review sớm sau các công bố liên quan ĐHĐCĐ ngày `03/04/2026` hoặc phương án trái phiếu cấp 2. [N005/F03; N002/F01; N004/F01]
- Ngày lập card: `2026-03-31`; dữ liệu sau ngày quyết định không được sử dụng. [`decision_date`; `guardrails.no_post_decision_data`]

## 7. Kết luận hỗ trợ quyết định

- EVF có tín hiệu mô hình và kỹ thuật nghiêng tích cực. [ml_signal; `technical_snapshot`; `top_drivers`]
- Tin doanh nghiệp có điểm hỗ trợ từ kết quả 2025 và mục tiêu 2026, nhưng không chia cổ tức và có hoạt động phát hành trái phiếu tăng vốn cấp 2. [N005/F01–F04; N002/F01; N004/F01]
- Trạng thái phù hợp: **theo dõi có điều kiện, cần xác nhận thêm**, không đủ cơ sở cho khuyến nghị đầu tư chắc chắn.
- Evidence tin tức chưa đủ mạnh cho kết luận độc lập về pháp lý, quản trị, pha loãng hoặc rủi ro tín dụng EVF. [N001; N002; N003; `data_quality_flags`]

## 8. Disclaimer

- Card chỉ sử dụng evidence pack tại ngày `2026-03-31`. [`decision_date`; `guardrails.news_cutoff`]
- Đầu ra mô hình không bảo đảm biến động giá hoặc lợi nhuận. [`ml_signal`; `guardrails.not_investment_advice`]
- Không đưa ra dự báo giá tuyệt đối, cam kết lợi nhuận hoặc khuyến nghị mua bán chắc chắn.
- Nội dung phục vụ hỗ trợ quyết định và nghiên cứu học thuật, không phải tư vấn đầu tư. [`guardrails.not_investment_advice`]

---

## 2026Q1_DPM_03

## 1. Tóm tắt tín hiệu

- DPM có nhãn mô hình **“Buy Candidate”**, xác suất nhãn tăng `0.9718740266791716`, xếp hạng 3 trong kỳ. Đây là output mô hình, không phải bảo đảm kết quả. `[ml_signal]`
- Kỹ thuật nghiêng tích cực: RSI cuối kỳ `52.1123`, MACD histogram trung bình `0.09015`, khối lượng thay đổi `1.81625`. Giá vẫn dưới SMA20 `2.45%`; biên độ giá kỳ `0.50503` cho thấy biến động cao. `[technical_snapshot]`
- Tin tức có yếu tố hỗ trợ từ KQKD 2025 và cổ tức dự kiến, nhưng có cờ `audit_issue`, `legal_risk` và dữ liệu trích xuất lẫn nội dung không liên quan. `[N002, N003, N004, N005]`
- **Evidence tin tức chưa đủ mạnh để xác nhận xu hướng bền vững.**

## 2. Luận điểm đầu tư chính

- Tín hiệu mô hình mạnh, động lượng kỹ thuật và thông tin KQKD 2025 hỗ trợ trạng thái **ứng viên cần theo dõi**. `[ml_signal, technical_snapshot, N004/F05]`
- Giá dưới SMA20, biến động cao, cùng cờ kiểm toán/pháp lý làm giảm độ chắc của luận điểm. `[technical_snapshot.price_vs_sma20, technical_snapshot.price_range_q, N002, N003, N005]`
- Trạng thái phù hợp: **đánh giá có điều kiện, chưa đủ cơ sở cho khuyến nghị chắc chắn**.

## 3. Yếu tố hỗ trợ

- KQKD 2025 được nêu với doanh thu hợp nhất `16,564.4 tỷ đồng`, hoàn thành `133%` kế hoạch; lợi nhuận sau thuế hợp nhất `1,095 tỷ đồng`, vượt `342%` mục tiêu. `[N004/F05]`
- Doanh nghiệp dự kiến trình cổ đông cổ tức tiền mặt `1,500 đồng/cổ phiếu`, cao hơn mức `1,200 đồng/cổ phiếu` đã được phê duyệt trước đó. Đây vẫn là phương án dự kiến. `[N004/F01, N004/F02]`
- RSI `52.1123` và MACD histogram `0.09015` được mô hình xác định là driver hỗ trợ tín hiệu tăng. `[top_drivers, technical_snapshot]`
- Khối lượng thay đổi `1.81625`, được mô hình xếp vào nhóm hỗ trợ tín hiệu. `[top_drivers.volume_change_q, technical_snapshot.volume_change_q]`

## 4. Yếu tố cần lưu ý / rủi ro

- Giá cuối kỳ dưới SMA20 `2.45%`, trong khi biên độ giá kỳ ở mức `0.50503`; trạng thái kỹ thuật chưa đồng thuận và biến động cao. `[technical_snapshot.price_vs_sma20, technical_snapshot.price_range_q]`
- Tin về giải trình KQKD sau kiểm toán mang cờ `audit_issue` và `legal_risk`; nội dung chi tiết trong evidence chỉ ở trạng thái `partial`. `[N002]`
- Công bố BCTC 2025 đã kiểm toán cũng mang cờ `audit_issue`, `legal_risk`, cùng các cờ `debt_risk`, `capital_dilution`, `earnings_warning`, `governance`; evidence không cung cấp đủ chi tiết để xác nhận mức độ từng rủi ro. `[N003, N005]`
- Cổ tức `1,500 đồng/cổ phiếu` mới là dự kiến trình ĐHĐCĐ, chưa có evidence xác nhận được thông qua. `[N001, N004]`
- N005 có facts về QTP, GMD và PNJ không liên quan trực tiếp DPM; `ticker_matching_confidence` ở mức `mixed`. Cần giảm trọng số diễn giải N005. `[N005, data_quality_flags]`

## 5. Trigger theo dõi

- Kết quả ĐHĐCĐ thường niên dự kiến ngày `23/04/2026`, đặc biệt việc thông qua phương án cổ tức. `[N001, N004]`
- Công bố bổ sung về BCTC 2025, giải trình kiểm toán và các cờ pháp lý. `[N002, N003]`
- Cập nhật các trường `price_vs_sma20`, `rsi_end_q`, `macd_hist_mean_q`, `volume_change_q`; theo dõi khả năng cải thiện hoặc suy yếu của tín hiệu kỹ thuật. `[technical_snapshot, top_drivers]`
- Kiểm tra lại độ khớp ticker và nội dung N005 trước khi dùng làm evidence chính. `[N005, data_quality_flags.ticker_matching_confidence]`

## 6. Thời điểm review

- Review lần đầu sau sự kiện ĐHĐCĐ dự kiến ngày `23/04/2026`, nếu có công bố mới. `[N004]`
- Review định kỳ cuối quý kế tiếp theo horizon `next_quarter_or_period_return_in_signals`. `[holding_horizon]`
- Review sớm hơn nếu xuất hiện cập nhật về kiểm toán, pháp lý, BCTC hoặc thay đổi rõ trong các trường kỹ thuật nêu trên. `[N002, N003, technical_snapshot]`

## 7. Kết luận hỗ trợ quyết định

- DPM có tín hiệu mô hình mạnh và một số yếu tố cơ bản hỗ trợ. `[ml_signal, N004/F05]`
- Tín hiệu chưa đủ sạch do giá dưới SMA20, biến động cao, cờ kiểm toán/pháp lý và chất lượng không đồng nhất ở N005. `[technical_snapshot, N002, N003, N005]`
- Kết luận: **đưa vào diện theo dõi có điều kiện; ưu tiên xác nhận thông tin ĐHĐCĐ, BCTC và rủi ro kiểm toán trước quyết định tiếp theo. Không xem đây là khuyến nghị mua chắc chắn.**

## 8. Disclaimer

- Card phục vụ hỗ trợ quyết định và nghiên cứu học thuật; không phải tư vấn đầu tư. `[guardrails.not_investment_advice]`
- Xác suất mô hình không bảo đảm kết quả. Không có dự báo giá tuyệt đối. `[ml_signal, guardrails]`
- Cổ tức là phương án dự kiến, chưa được evidence xác nhận thông qua. `[N004]`
- Evidence tin tức có bài trích xuất `partial` và dữ liệu lẫn nội dung không liên quan; cần kiểm tra công bố chính thức trước khi sử dụng. `[N001, N002, N003, N005, data_quality_flags]`

---

## 2026Q1_DCM_04

## 1. Tóm tắt tín hiệu

- DCM có tín hiệu mô hình tích cực: `pred_label = 1`, `pred_proba_up = 0.9584`, xếp hạng 4, lớp `Buy Candidate` (`ml_signal`).
- Động lượng kỹ thuật hỗ trợ tín hiệu: RSI cuối kỳ `58.63`, MACD histogram trung bình `0.145`, giá cao hơn SMA20 `3.13%`, `volume_change_q = 1.765` (`top_drivers`, `technical_snapshot`).
- Nền tảng 2025 tích cực: doanh thu gần `17,033 tỷ đồng`, tăng `21%`; lợi nhuận sau thuế `1,962 tỷ đồng`, tăng `37%` (N002-F02).
- Kế hoạch 2026 trái chiều: doanh thu mục tiêu `17,615 tỷ đồng`, tăng khoảng `3%`, nhưng lợi nhuận trước thuế và sau thuế cùng giảm khoảng `40%` (N002-F04, N002-F05).
- Tín hiệu tổng thể: kỹ thuật tích cực; triển vọng lợi nhuận và cổ tức 2026 yếu hơn. Tín hiệu mô hình không phải bảo đảm kết quả.

## 2. Luận điểm đầu tư chính

- Tín hiệu theo dõi DCM được hỗ trợ bởi mô hình kỹ thuật và động lượng hiện tại (`ml_signal`, `top_drivers`).
- Luận điểm bị cân bằng bởi kế hoạch lợi nhuận 2026 giảm mạnh và cổ tức dự kiến giảm một nửa (N002-F01, N002-F05).
- Card phù hợp với trạng thái **theo dõi có điều kiện**, chưa đủ cơ sở cho khuyến nghị đầu tư chắc chắn.
- Evidence tin tức chưa đủ mạnh cho đánh giá tác động từ thành lập chi nhánh, quản trị, pháp lý, nợ hoặc pha loãng; N001 và N005 có dữ liệu lẫn nội dung không liên quan.

## 3. Yếu tố hỗ trợ

- Mô hình ghi nhận xác suất tín hiệu tăng `0.9584` và xếp hạng 4 trong kỳ (`ml_signal`).
- RSI, MACD histogram, vị trí giá so với SMA20 và khối lượng đều được mô hình gắn hướng `supports_up_signal` (`top_drivers`).
- Kết quả 2025 vượt kế hoạch; doanh thu tăng `21%`, lợi nhuận sau thuế tăng `37%` (N002-F02).
- DCM duy trì cổ tức tiền mặt `20%`, tương đương `2,000 đồng/cp`, trong 4 năm liên tiếp từ 2022 (N002-F03).
- Doanh thu mục tiêu 2026 vẫn tăng khoảng `3%` so với thực hiện 2025 (N002-F04).

## 4. Yếu tố cần lưu ý / rủi ro

- Lợi nhuận trước thuế 2026 dự kiến `1,320 tỷ đồng`, lợi nhuận sau thuế `1,182 tỷ đồng`, cùng giảm khoảng `40%` (N002-F05).
- Cổ tức 2026 dự kiến còn một nửa, làm yếu luận điểm thu nhập so với mức cổ tức tiền mặt `20%` năm 2025 (N002-F01, N002-F03).
- Biên độ giá trong kỳ ở mức `0.4956`, được mô hình gắn nhãn `risk_high_volatility` (`top_drivers`, `technical_snapshot.price_range_q`).
- N001 và N005 gắn các `risk_flags`: `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk`; pack không cung cấp bằng chứng chi tiết đủ xác nhận từng rủi ro (N001, N005).
- N001 và N005 có `key_facts` lẫn nội dung QTP, GMD, PNJ; độ tin cậy diễn giải bị hạn chế (N001, N005).
- N003 và N004 chỉ có nội dung thông báo họp và tài liệu họp, `extraction_status = partial`; bằng chứng định tính hạn chế (N003, N004).
- `ticker_matching_confidence = mixed`; cần kiểm tra lại liên kết tin tức với DCM (`data_quality_flags`).

## 5. Trigger theo dõi

- ĐHĐCĐ thường niên dự kiến ngày `22/04/2026`: kiểm tra mục tiêu lợi nhuận, cổ tức và các nghị quyết liên quan (N002, N003, N004).
- Cập nhật thực hiện so với mục tiêu doanh thu `17,615 tỷ đồng`, lợi nhuận trước thuế `1,320 tỷ đồng` và lợi nhuận sau thuế `1,182 tỷ đồng` (N002-F04, N002-F05).
- Theo dõi lại RSI, MACD histogram, giá so với SMA20 và khối lượng trong kỳ kế tiếp (`technical_snapshot`, `top_drivers`).
- Xác minh riêng các nhãn `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk` bằng công bố cụ thể (N001, N005).
- Kiểm tra độ khớp ticker và chất lượng trích xuất của N001, N003, N004, N005 (`match_confidence`, `extraction_status`, `data_quality_flags`).

## 6. Thời điểm review

- Review lần đầu sau ĐHĐCĐ dự kiến ngày `22/04/2026` (N002, N003).
- Review tiếp theo vào cuối quý kế tiếp, theo `holding_horizon = next_quarter_or_period_return_in_signals`.
- Không sử dụng dữ liệu sau ngày quyết định `31/03/2026` trong đánh giá hiện tại (`decision_date`, `guardrails.news_cutoff`, `guardrails.no_post_decision_data`).

## 7. Kết luận hỗ trợ quyết định

- DCM có tín hiệu kỹ thuật và mô hình tích cực (`ml_signal`, `top_drivers`).
- Kế hoạch 2026 cho thấy rủi ro suy giảm lợi nhuận và cổ tức (N002-F01, N002-F05).
- Phân loại hỗ trợ quyết định: **theo dõi có điều kiện; cần xác nhận sau ĐHĐCĐ và cập nhật kết quả thực hiện**.
- Không đủ cơ sở từ pack để kết luận mua, cam kết lợi nhuận hoặc dự báo giá tuyệt đối.

## 8. Disclaimer

- Decision card phục vụ hỗ trợ phân tích học thuật, không phải tư vấn đầu tư (`guardrails.not_investment_advice`).
- Xác suất mô hình là đầu ra mô hình, không phải bảo đảm kết quả (`ml_signal`).
- Dữ liệu có thời điểm quyết định `31/03/2026`; không gồm dữ liệu sau quyết định (`decision_date`, `guardrails.no_post_decision_data`).

---

## 2026Q1_REE_05

## 1. Tóm tắt tín hiệu

- REE nhận nhãn **“Buy Candidate”**; `pred_label = 1`, xác suất mô hình cho nhãn tăng `0.9533451285937101`, xếp hạng 5 trong kỳ. Đây là tín hiệu mô hình, không phải bảo đảm kết quả. (`ml_signal`)
- Tín hiệu kỹ thuật nghiêng tích cực: RSI cuối kỳ `59.0921`, MACD histogram trung bình `0.1528`, giá so với SMA20 `+0.05285`, thay đổi khối lượng `1.87135`. (`technical_snapshot`, `top_drivers`)
- Tin tức có cả bối cảnh hỗ trợ và cờ rủi ro. Chất lượng khớp mã ở mức `mixed`; một số bài có dữ kiện thấp hoặc trích xuất một phần. (`data_quality_flags.ticker_matching_confidence`, `N002`, `N003`, `N005`)
- **Evidence tin tức chưa đủ mạnh** để xác nhận luận điểm cơ bản độc lập.

## 2. Luận điểm đầu tư chính

- Tín hiệu ngắn hạn nghiêng tích cực nhờ mô hình và nhóm chỉ báo kỹ thuật: RSI, MACD, vị trí giá trên SMA20, khối lượng. (`ml_signal`, `technical_snapshot.rsi_end_q`, `technical_snapshot.macd_hist_mean_q`, `technical_snapshot.price_vs_sma20`, `technical_snapshot.volume_change_q`)
- N004 ghi nhận thành viên HĐQT độc lập mô tả lợi thế cạnh tranh của REE và kế hoạch nâng công suất năng lượng từ khoảng `1,200 MW` lên `3,000 MW`. Dữ kiện này chỉ nên xem là bối cảnh kế hoạch, vì độ tin cậy fact ở mức thấp. (`N004`, `N004.F04`)
- Rủi ro nợ, pha loãng, quản trị, pháp lý và cảnh báo kết quả xuất hiện trong `risk_flags`, nhưng nội dung chi tiết chưa đủ để định lượng tác động. (`N002.risk_flags`, `N003.risk_flags`, `N005`)

## 3. Yếu tố hỗ trợ

- Mô hình xếp REE vào nhóm **“Buy Candidate”**, xác suất nhãn tăng `0.9533451285937101`. (`ml_signal`)
- RSI cuối kỳ `59.092130761390706` là driver hỗ trợ tín hiệu tăng trong mô hình. (`top_drivers[0]`, `technical_snapshot.rsi_end_q`)
- MACD histogram trung bình `0.15282420064366853` hỗ trợ động lượng xu hướng trong mô hình. (`top_drivers[1]`, `technical_snapshot.macd_hist_mean_q`)
- Giá nằm cao hơn SMA20 theo biến `price_vs_sma20 = 0.05285483258070484`. (`top_drivers[2]`, `technical_snapshot.price_vs_sma20`)
- Khối lượng thay đổi `1.871350845986579`, được mô hình xếp là driver hỗ trợ. (`top_drivers[6]`, `technical_snapshot.volume_change_q`)
- N004 nêu REE có danh mục dự án và mục tiêu công suất năng lượng `3,000 MW` so với khoảng `1,200 MW` hiện tại. Fact có độ tin cậy thấp; chưa đủ xác nhận thực thi. (`N004.F04`, `N004.key_facts[3].confidence`)

## 4. Yếu tố cần lưu ý / rủi ro

- N005 là công bố định kỳ của tổ chức phát hành trái phiếu REE, gắn `debt_risk`; trích xuất chỉ dài `143` ký tự, nên chưa đủ dữ kiện đánh giá quy mô hoặc mức độ rủi ro. (`N005`, `N005.extraction_status`, `N005.full_text_chars`, `N005.risk_flags`)
- N002 và N003 gắn các cờ `audit_issue`, `capital_dilution`, `debt_risk`, `earnings_warning`, `governance`, `legal_risk`; dữ kiện chính chủ yếu là tiêu đề hoặc nội dung lẫn tin khác, nhiều fact có độ tin cậy thấp. Không xem đây là rủi ro đã được xác nhận đầy đủ. (`N002.risk_flags`, `N003.risk_flags`, `N002.key_facts`, `N003.key_facts`)
- N002 và N003 liên quan giao dịch của tổ chức có liên quan đến người nội bộ, nhưng pack không cung cấp rõ khối lượng, giá, tỷ lệ sở hữu hoặc kết quả giao dịch. (`N002.article_summary`, `N003.article_summary`, `N002.key_facts`, `N003.key_facts`)
- N001 nói về SGR, không phải REE. Cần loại khỏi luận điểm REE do độ tin cậy khớp mã toàn pack chỉ ở mức `mixed`. (`N001`, `data_quality_flags.ticker_matching_confidence`)
- Biên độ giá trong kỳ là `0.26337361043982593`, cho thấy cần theo dõi biến động của tín hiệu kỹ thuật. (`technical_snapshot.price_range_q`, `top_drivers[8]`)
- N004 có `risk_flags = ["audit_issue"]`; bài viết cũng dùng nhận định của thành viên HĐQT độc lập với độ tin cậy fact thấp. (`N004.risk_flags`, `N004.key_facts`)

## 5. Trigger theo dõi

- Xác minh chi tiết công bố trái phiếu REE: nghĩa vụ, lịch thanh toán, điều kiện liên quan nếu được công bố. (`N005`)
- Cập nhật giao dịch của PLATINUM VICTORY PTE.LTD và tổ chức liên quan người nội bộ; tập trung khối lượng, tỷ lệ sở hữu, giá và trạng thái hoàn tất. (`N002`, `N003`)
- Theo dõi công bố mới về kế hoạch công suất năng lượng `3,000 MW` và tiến độ dự án. (`N004.F04`)
- Theo dõi hướng thay đổi của RSI, MACD histogram, vị trí giá so với SMA20 và khối lượng. (`technical_snapshot`, `top_drivers`)
- Kiểm tra lại các cờ audit, pha loãng, nợ, kết quả kinh doanh, quản trị và pháp lý khi có dữ kiện chi tiết hơn. (`N002.risk_flags`, `N003.risk_flags`, `N004.risk_flags`, `N005.risk_flags`)

## 6. Thời điểm review

- Review vào cuối quý tiếp theo, phù hợp `holding_horizon = next_quarter_or_period_return_in_signals`. (`holding_horizon`, `period_id`)
- Review sớm khi xuất hiện công bố mới về trái phiếu, giao dịch nội bộ, kế hoạch năng lượng hoặc thay đổi rõ trong nhóm chỉ báo kỹ thuật. (`N002`, `N003`, `N004`, `N005`, `technical_snapshot`)

## 7. Kết luận hỗ trợ quyết định

- REE có tín hiệu mô hình và kỹ thuật nghiêng tích cực.
- Evidence định tính còn không đồng nhất; rủi ro nợ và các cờ quản trị, pháp lý, pha loãng chưa được làm rõ.
- Có thể xếp REE vào **danh sách theo dõi / ứng viên cần thẩm định thêm**, không xem là khuyến nghị mua chắc chắn.
- Bước tiếp theo: xác minh N002, N003, N005 và theo dõi các trigger kỹ thuật trước review kế tiếp.

## 8. Disclaimer

- Decision card chỉ dùng evidence pack, ngày quyết định `2026-03-31`, news cutoff `2026-03-31`.
- Không dự báo giá tuyệt đối.
- Không bảo đảm lợi nhuận hoặc kết quả.
- Không thay thế thẩm định độc lập và không phải khuyến nghị đầu tư chắc chắn.
