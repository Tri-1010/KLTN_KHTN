# BẢN THẢO LUẬN VĂN THẠC SĨ (LEGACY — KHÔNG PHẢI BẢN CANONICAL)

> **Trạng thái:** Không dùng tài liệu này để nộp, trích số liệu headline hoặc kết luận. Bản canonical là `docs/luan_van_hoan_thien_ml_llm.md`; nó tách track ML legacy khỏi track semantic purged OOS, cập nhật provenance Gemini/local-router/common judge và mô tả EvidenceTrace theo implementation/test hiện hữu.
>
> **Lý do lưu giữ:** Bản này giữ nội dung phát triển lịch sử. Metric ML/backtest cao trong bản này thuộc protocol legacy, không được gộp với artifact semantic canonical. Phần LLM chỉ được diễn giải là chất lượng decision card, không phải alpha, return hoặc tư vấn đầu tư.

---

**ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH**  
**TRƯỜNG ĐẠI HỌC KHOA HỌC TỰ NHIÊN**

---

**Họ và tên học viên:** Ngô Minh Trí  
**Mã số học viên:** 24C01024  
**Ngành:** Khoa học Dữ liệu  
**Mã số ngành:** 8460108

---

## ỨNG DỤNG HỖ TRỢ QUYẾT ĐỊNH ĐẦU TƯ CỔ PHIẾU VIỆT NAM DỰA TRÊN TÍN HIỆU HỌC MÁY, LLM TẠO LUẬN ĐIỂM ĐẦU TƯ VÀ THEO DÕI SAU KHUYẾN NGHỊ

**Tên tiếng Anh:**  
**An ML-Led Investment Decision Support System for Vietnamese Stocks with LLM-Based Investment Thesis Generation and Post-Recommendation Monitoring**

---

**LUẬN VĂN THẠC SĨ KHOA HỌC DỮ LIỆU**

---

**TP. Hồ Chí Minh, năm 2026**

---

## MỤC LỤC

- [Tóm tắt](#tóm-tắt)
- [Abstract](#abstract)
- [Chương 1: Giới thiệu](#chương-1-giới-thiệu)
- [Chương 2: Cơ sở lý thuyết và tổng quan phương pháp](#chương-2-cơ-sở-lý-thuyết-và-tổng-quan-phương-pháp)
- [Chương 3: Dữ liệu và phương pháp nghiên cứu](#chương-3-dữ-liệu-và-phương-pháp-nghiên-cứu)
- [Chương 4: Kết quả thực nghiệm và thảo luận](#chương-4-kết-quả-thực-nghiệm-và-thảo-luận)
- [Chương 5: Kết luận, hạn chế và hướng phát triển](#chương-5-kết-luận-hạn-chế-và-hướng-phát-triển)
- [Tài liệu tham khảo](#tài-liệu-tham-khảo)
- [Phụ lục](#phụ-lục)

---

## TÓM TẮT

Luận văn này đề xuất một hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam theo hướng kết hợp mô hình học máy, tin tức công khai và mô hình ngôn ngữ lớn (Large Language Model — LLM). Khác với các nghiên cứu chỉ tập trung vào dự báo xu hướng tăng/giảm hoặc tạo khuyến nghị mua/bán tại một thời điểm, luận văn đặt trọng tâm vào quản trị vòng đời của một quyết định đầu tư: lựa chọn cổ phiếu ứng viên, giải thích tín hiệu, tạo luận điểm đầu tư, theo dõi sau khuyến nghị, cập nhật bối cảnh và hậu kiểm kết quả.

Mô hình học máy đóng vai trò lõi định lượng của hệ thống. Trên dữ liệu cổ phiếu Việt Nam giai đoạn 2022–2026, mô hình dựa trên đặc trưng kỹ thuật đạt hiệu quả tốt hơn các baseline đơn giản. Kết quả hiện có cho thấy mô hình kỹ thuật đạt Balanced Accuracy khoảng 0,76 và AUC khoảng 0,82–0,83. Backtest long-only cho thấy chiến lược mô hình đạt lợi nhuận tích lũy net khoảng 60,3% so với buy-and-hold equal khoảng 25,4%, Sharpe ratio khoảng 1,05, và walk-forward vượt benchmark ở 3/3 cutoff. Robustness test trên 125 mã HOSE+HNX cho Balanced Accuracy khoảng 0,761 và AUC khoảng 0,831, đồng thời vượt VNINDEX khoảng 15,3 điểm phần trăm trong cùng giai đoạn kiểm định.

Các thử nghiệm trước đó với đặc trưng tin tức/từ khóa, LLM sentiment và distant supervision cho thấy tin tức không cải thiện dự báo xu hướng giá một cách ổn định khi được ép thành biến dự báo trực tiếp. Vì vậy, luận văn định vị lại tin tức như một lớp bằng chứng định tính (evidence layer), không phải nguồn alpha chính. LLM được sử dụng để tạo decision card có cấu trúc từ evidence pack, trong đó evidence pack gồm tín hiệu ML, thứ hạng, technical drivers, SHAP/feature importance và tin tức point-in-time. LLM không được sử dụng để dự báo giá trực tiếp và không được thêm dữ kiện ngoài evidence pack.

Đóng góp chính của luận văn là chuyển trọng tâm từ bài toán dự báo cổ phiếu sang một quy trình hỗ trợ quản trị quyết định đầu tư theo vòng đời `select → explain → monitor → update → review`. Hệ thống được đánh giá bằng cả nhóm chỉ số định lượng của ML signal và nhóm tiêu chí định tính cho LLM decision card, monitoring và outcome review. Kết quả phục vụ mục tiêu học thuật và hỗ trợ phân tích, không phải khuyến nghị đầu tư thực tế.

**Từ khóa:** học máy, cổ phiếu Việt Nam, hỗ trợ quyết định đầu tư, LLM, investment thesis, SHAP, backtest, monitoring, hậu kiểm.

---

## ABSTRACT

This thesis proposes an investment decision support system for Vietnamese stocks by combining machine learning signals, public financial news, and Large Language Models (LLMs). Instead of focusing solely on one-shot price movement prediction or buy/sell recommendation generation, the thesis emphasizes the lifecycle management of an investment decision: selecting candidate stocks, explaining quantitative signals, generating an investment thesis, monitoring post-recommendation changes, updating the context, and reviewing outcomes after the holding period.

Machine learning serves as the quantitative core of the system. Using Vietnamese stock data from 2022 to 2026, the technical-feature-based model outperforms simple baselines. Existing results show a Balanced Accuracy of approximately 0.76 and an AUC of approximately 0.82–0.83. A long-only backtest indicates that the model strategy achieves about 60.3% net cumulative return compared with approximately 25.4% for an equal-weight buy-and-hold benchmark, with a Sharpe ratio of around 1.05. Walk-forward evaluation shows the model strategy outperforming the benchmark in 3 out of 3 cutoffs. A robustness test on 125 HOSE+HNX stocks reports a Balanced Accuracy of approximately 0.761 and an AUC of approximately 0.831, with the model outperforming VNINDEX by about 15.3 percentage points over the same test period.

Prior experiments with keyword-based news features, LLM sentiment, and distant supervision show that news does not consistently improve price trend prediction when forced into direct predictive features. Therefore, this thesis repositions news as a qualitative evidence layer rather than a primary alpha source. The LLM is used to generate structured decision cards from point-in-time evidence packs that include ML signals, rankings, technical drivers, SHAP/feature importance, and relevant public news. The LLM is not used to directly forecast prices and is constrained from adding information outside the evidence pack.

The main contribution of this thesis is a shift from stock trend prediction to lifecycle-based investment decision support: `select → explain → monitor → update → review`. The system is evaluated using both quantitative ML/investment metrics and qualitative criteria for LLM-generated decision cards, monitoring, and outcome review. The system is intended for academic research and analytical support, not as real-world investment advice.

**Keywords:** machine learning, Vietnamese stocks, investment decision support, LLM, investment thesis, SHAP, backtesting, monitoring, outcome review.

---

# CHƯƠNG 1: GIỚI THIỆU

## 1.1. Bối cảnh nghiên cứu

Thị trường chứng khoán Việt Nam trong những năm gần đây phát triển mạnh về quy mô vốn hóa, số lượng doanh nghiệp niêm yết, mức độ tham gia của nhà đầu tư cá nhân và độ phong phú của dữ liệu công khai. Bên cạnh dữ liệu giao dịch như giá, khối lượng, lợi suất và biến động, thị trường còn tạo ra một lượng lớn tin tức tài chính tiếng Việt từ các trang tin, báo điện tử, nền tảng phân tích và công bố doanh nghiệp.

Trong nghiên cứu dự báo cổ phiếu, các mô hình học máy thường được sử dụng để dự báo xu hướng tăng/giảm hoặc xác suất sinh lời trong một khoảng thời gian nhất định. Các mô hình này có thể khai thác tốt các đặc trưng kỹ thuật như lợi suất, động lượng, độ biến động, RSI, MACD, SMA, EMA, Bollinger Bands và biến động khối lượng. Tuy nhiên, trong thực tế đầu tư, một tín hiệu dự báo tích cực chưa đủ để tạo thành một quyết định đầu tư có thể sử dụng.

Nhà đầu tư cần nhiều hơn một xác suất dự báo. Họ cần hiểu vì sao cổ phiếu được chọn, luận điểm đầu tư ban đầu là gì, thông tin định lượng và định tính nào đang ủng hộ hoặc làm suy yếu luận điểm, khi nào cần xem xét lại quyết định, và sau kỳ nắm giữ thì quyết định đúng hay sai vì nguyên nhân nào. Nói cách khác, khoảng cách giữa **tín hiệu mô hình** và **quyết định đầu tư có thể quản trị** là một vấn đề quan trọng.

Luận văn này đề xuất một hệ thống hỗ trợ quyết định đầu tư theo vòng đời:

**select → explain → monitor → update → review**

Trong đó:

- **select:** mô hình học máy tạo tín hiệu định lượng và danh sách cổ phiếu ứng viên;
- **explain:** evidence pack và LLM tạo luận điểm đầu tư có cấu trúc;
- **monitor:** hệ thống theo dõi thay đổi tín hiệu, kỹ thuật và tin tức;
- **update:** luận điểm được cập nhật khi có bằng chứng mới;
- **review:** sau kỳ nắm giữ, hệ thống hậu kiểm kết quả và rút kinh nghiệm.

## 1.2. Vấn đề nghiên cứu

Nhiều hệ thống dự báo tài chính dừng ở đầu ra như xác suất tăng, nhãn Buy/Sell/Hold hoặc bảng xếp hạng cổ phiếu. Đầu ra này hữu ích nhưng chưa đủ để hỗ trợ quyết định đầu tư trong thực tế vì thiếu các thành phần sau:

1. Giải thích có cấu trúc về lý do lựa chọn.
2. Gắn kết giữa tín hiệu định lượng và bằng chứng định tính.
3. Danh sách rủi ro và điều kiện cần theo dõi.
4. Cơ chế cập nhật khi bối cảnh thay đổi.
5. Hậu kiểm để đánh giá chất lượng quyết định.

Dữ liệu tin tức công khai là một nguồn thông tin quan trọng, nhưng các kết quả thực nghiệm cũ trong dự án cho thấy tin tức tài chính tiếng Việt khi biểu diễn bằng tần suất từ khóa, sentiment hoặc distant supervision không cải thiện dự báo xu hướng giá một cách ổn định. Điều này đặt ra yêu cầu định vị lại vai trò của tin tức. Thay vì ép tin tức thành biến dự báo trực tiếp, luận văn sử dụng tin tức như **lớp bằng chứng** để hỗ trợ giải thích, theo dõi và hậu kiểm.

Sự xuất hiện của LLM mở ra khả năng chuyển dữ liệu cấu trúc và bán cấu trúc thành luận điểm đầu tư dễ đọc. Tuy nhiên, LLM cũng có rủi ro hallucination và diễn giải quá mức. Vì vậy, luận văn không dùng LLM để dự báo giá trực tiếp. LLM chỉ được dùng để tạo decision card từ evidence pack đã kiểm soát.

## 1.3. Mục tiêu nghiên cứu

### 1.3.1. Mục tiêu tổng quát

Xây dựng và đánh giá một prototype hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam kết hợp tín hiệu học máy, tin tức công khai và LLM nhằm tạo, theo dõi và hậu kiểm luận điểm đầu tư.

### 1.3.2. Mục tiêu cụ thể

1. Đóng gói mô hình học máy dựa trên đặc trưng kỹ thuật để tạo tín hiệu định lượng và xếp hạng cổ phiếu.
2. Đánh giá hiệu quả ML signal bằng chỉ số phân loại và backtest đầu tư long-only.
3. Thiết kế evidence pack point-in-time cho từng cổ phiếu ứng viên.
4. Thiết kế LLM decision card có cấu trúc, chỉ dựa trên evidence pack.
5. Thiết kế monitoring sau khuyến nghị và outcome review sau kỳ nắm giữ.
6. Đánh giá hệ thống bằng cả tiêu chí định lượng và rubric định tính.

## 1.4. Câu hỏi nghiên cứu

**RQ1.** Mô hình học máy dựa trên đặc trưng kỹ thuật có tạo tín hiệu hữu ích cho việc lựa chọn cổ phiếu Việt Nam hay không?

**RQ2.** Chiến lược đầu tư long-only dựa trên ML signal/Top-K ranking có vượt benchmark theo return, Sharpe ratio và drawdown hay không?

**RQ3.** LLM decision card được tạo từ evidence pack có bám sát dữ liệu đầu vào, hạn chế hallucination, giải thích rõ tín hiệu ML và nêu rủi ro hữu ích hay không?

**RQ4.** Monitoring và outcome review có giúp phát hiện các trường hợp tín hiệu suy yếu, bối cảnh thay đổi hoặc luận điểm cần xem xét lại hay không?

## 1.5. Phạm vi và giới hạn nghiên cứu

Luận văn tập trung vào cổ phiếu Việt Nam, trọng tâm là universe HOSE-80 đã được xây dựng trong giai đoạn nghiên cứu trước và robustness test trên 125 mã HOSE+HNX. Dữ liệu gồm giá/khối lượng lịch sử, đặc trưng kỹ thuật, tin tức công khai đã gắn ticker và kết quả mô hình ML.

Luận văn không xây dựng hệ thống giao dịch tự động, không dự báo giá tuyệt đối, không sử dụng LLM để dự báo giá trực tiếp và không đưa ra khuyến nghị đầu tư thực tế. Hệ thống là prototype nghiên cứu nhằm minh họa cách chuyển tín hiệu ML thành decision record có thể giải thích, theo dõi và hậu kiểm.

## 1.6. Đóng góp của luận văn

Luận văn có năm đóng góp chính:

1. Đề xuất framing mới: từ dự báo xu hướng giá sang hỗ trợ quản trị quyết định đầu tư.
2. Sử dụng ML signal đã kiểm chứng làm lõi định lượng.
3. Tái định vị tin tức từ feature dự báo sang evidence layer.
4. Thiết kế decision card có cấu trúc bằng LLM và kiểm soát hallucination bằng evidence pack.
5. Đề xuất monitoring và outcome review để hậu kiểm quyết định.

## 1.7. Cấu trúc luận văn

Luận văn gồm năm chương. Chương 1 trình bày bối cảnh, vấn đề, mục tiêu và câu hỏi nghiên cứu. Chương 2 trình bày cơ sở lý thuyết về ML trong dự báo cổ phiếu, đặc trưng kỹ thuật, tin tức tài chính, SHAP, LLM và decision support. Chương 3 mô tả dữ liệu, kiến trúc hệ thống và phương pháp đánh giá. Chương 4 trình bày kết quả thực nghiệm và thảo luận. Chương 5 tổng kết đóng góp, hạn chế và hướng phát triển.

---

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ TỔNG QUAN PHƯƠNG PHÁP

## 2.1. Machine Learning trong dự báo cổ phiếu

Machine Learning trong dự báo cổ phiếu thường khai thác dữ liệu dạng bảng gồm giá, khối lượng, chỉ báo kỹ thuật, đặc trưng văn bản hoặc biến vĩ mô. Bài toán có thể được thiết kế dưới dạng hồi quy lợi suất, phân loại tăng/giảm hoặc xếp hạng cổ phiếu. Trong luận văn này, bài toán lõi là phân loại xu hướng tăng/không tăng trong kỳ tiếp theo và xếp hạng cổ phiếu theo xác suất tăng.

Các thuật toán dạng bảng như Logistic Regression, Random Forest, XGBoost và LightGBM thường phù hợp với dữ liệu tài chính có số lượng mẫu vừa phải, nhiều đặc trưng kỹ thuật và quan hệ phi tuyến. Tuy nhiên, với dữ liệu tài chính theo thời gian, mô hình phải được đánh giá bằng chia train/test theo thời gian, không shuffle ngẫu nhiên, để tránh look-ahead bias.

Trong hệ thống đề xuất, ML không được xem là công cụ ra quyết định độc lập. Vai trò của ML là tạo tín hiệu định lượng gồm xác suất tăng, nhãn dự báo, thứ hạng và danh sách ứng viên đầu tư. Tín hiệu này là đầu vào cho các lớp giải thích và hỗ trợ quyết định phía sau.

## 2.2. Đặc trưng kỹ thuật

Đặc trưng kỹ thuật phản ánh hành vi giá và thanh khoản trong quá khứ. Các nhóm đặc trưng sử dụng gồm:

- Lợi suất và động lượng: `return_q`, `return_prev_q`, `return_2q_ago`, `return_mean_daily`.
- Biến động: `return_std_daily`, `volatility_q`, `price_range_q`.
- Thanh khoản: `volume_mean_q`, `volume_change_q`.
- Xu hướng: `sma20_end`, `ema20_end`, `price_vs_sma20`.
- Chỉ báo kỹ thuật: `rsi_mean_q`, `rsi_end_q`, `macd_hist_mean_q`, `bb_position_q`.

Các đặc trưng này không diễn giải doanh nghiệp theo nghĩa cơ bản, nhưng phản ánh hành vi thị trường đã quan sát. Trong bối cảnh hệ thống hỗ trợ quyết định, chúng giúp mô hình tạo danh sách ứng viên, còn LLM giúp giải thích các tín hiệu này bằng ngôn ngữ tự nhiên.

## 2.3. Tin tức tài chính và vai trò evidence layer

Tin tức tài chính chứa thông tin về kết quả kinh doanh, cổ tức, nợ xấu, dự án, thay đổi lãnh đạo, rủi ro pháp lý và diễn biến ngành. Trong các nghiên cứu dự báo, tin tức thường được chuyển thành feature như tần suất từ khóa, TF-IDF, sentiment hoặc embedding. Tuy nhiên, kết quả thực nghiệm trong dự án cho thấy các đặc trưng tin tức/từ khóa không cải thiện dự báo ổn định so với mô hình kỹ thuật.

Điều này không có nghĩa tin tức vô dụng. Tin tức vẫn rất hữu ích để giải thích bối cảnh, nêu rủi ro và hỗ trợ hậu kiểm. Do đó, luận văn dùng tin tức theo vai trò **evidence layer**. Tin tức không trực tiếp quyết định tín hiệu mua/bán mà cung cấp bằng chứng định tính cho LLM tạo luận điểm và monitoring phát hiện thay đổi bối cảnh.

## 2.4. Explainable AI và SHAP

SHAP (SHapley Additive exPlanations) là phương pháp giải thích mô hình dựa trên giá trị Shapley trong lý thuyết trò chơi. SHAP gán cho mỗi đặc trưng một mức đóng góp vào dự báo của mô hình, giúp diễn giải mô hình phức tạp như Random Forest, XGBoost hoặc LightGBM.

Trong hệ thống đề xuất, SHAP có hai vai trò:

1. Giải thích định lượng cho ML signal.
2. Cung cấp structured evidence cho LLM, giúp decision card không chỉ nói “mô hình dự báo tăng” mà còn chỉ ra tín hiệu đến từ đặc trưng nào.

## 2.5. LLM trong hỗ trợ quyết định tài chính

LLM có khả năng tổng hợp thông tin, diễn giải bằng ngôn ngữ tự nhiên và tạo cấu trúc lập luận. Trong tài chính, LLM có thể hỗ trợ đọc tin tức, tóm tắt báo cáo, giải thích tín hiệu và tạo luận điểm đầu tư. Tuy nhiên, LLM có rủi ro hallucination, suy diễn quá mức hoặc đưa ra phát biểu không có căn cứ nếu prompt không kiểm soát.

Vì vậy, luận văn áp dụng các nguyên tắc sau:

- LLM không dự báo giá trực tiếp.
- LLM không được đưa thông tin ngoài evidence pack.
- Mỗi luận điểm quan trọng phải tham chiếu evidence ID.
- Output phải theo schema cố định.
- Decision card ban đầu không được chứa outcome tương lai.
- Nếu evidence thiếu, LLM phải nêu rõ thay vì suy đoán.

## 2.6. Hệ thống hỗ trợ quyết định và vòng đời quyết định đầu tư

Hệ thống hỗ trợ quyết định không thay thế người ra quyết định. Trong bối cảnh đầu tư, hệ thống có nhiệm vụ tổ chức thông tin, giải thích tín hiệu, nêu rủi ro và hỗ trợ hậu kiểm. Luận văn tổ chức quy trình theo năm bước:

1. **Select:** chọn cổ phiếu ứng viên bằng ML signal.
2. **Explain:** tạo thesis dựa trên evidence.
3. **Monitor:** theo dõi thay đổi tín hiệu và bối cảnh.
4. **Update:** cập nhật luận điểm khi có thông tin mới.
5. **Review:** hậu kiểm sau kỳ nắm giữ.

Cấu trúc này giúp biến một dự báo đơn lẻ thành một decision record có thể kiểm tra lại.

## 2.7. Rò rỉ dữ liệu trong nghiên cứu tài chính

Rò rỉ dữ liệu là rủi ro lớn trong nghiên cứu tài chính dùng ML. Một mô hình có thể đạt độ chính xác cao nếu vô tình sử dụng thông tin tương lai, ví dụ nhãn kỳ sau, return tương lai, dữ liệu tin tức sau ngày quyết định hoặc tham số chuẩn hóa fit trên toàn bộ dữ liệu.

Luận văn kiểm soát rò rỉ theo hai lớp:

- Lớp ML: chia train/test theo thời gian, fit imputer/scaler trên train, không đưa cột nhãn/return tương lai vào feature set.
- Lớp LLM: evidence pack ban đầu chỉ chứa dữ liệu trước hoặc tại decision date, không chứa realized return hoặc outcome review.

---

# CHƯƠNG 3: DỮ LIỆU VÀ PHƯƠNG PHÁP NGHIÊN CỨU

## 3.1. Tổng quan thiết kế hệ thống

Hệ thống gồm năm lớp:

1. **ML Signal Engine:** tạo xác suất, nhãn dự báo, rank và Top-K candidate.
2. **News Evidence Layer:** lưu tin tức công khai đã gắn ticker, ngày, nguồn và event type.
3. **Evidence Pack Builder:** đóng gói dữ liệu point-in-time cho từng decision record.
4. **LLM Decision Card Generator:** tạo luận điểm đầu tư có cấu trúc từ evidence pack.
5. **Post-Recommendation Monitoring & Outcome Review:** theo dõi sau khuyến nghị và hậu kiểm.

Thiết kế tổng quát:

```text
Price/Volume Data ──> Technical Features ──> ML Signal Engine ──> Ranked Candidates
                                                               │
News Data ──> Ticker Matching/Event Tags ──> News Evidence ─────┤
                                                               ▼
                                                       Evidence Pack
                                                               ▼
                                                     LLM Decision Card
                                                               ▼
                                           Monitoring / Update / Outcome Review
```

## 3.2. Dữ liệu giá và universe cổ phiếu

Dữ liệu giá gồm OHLCV ngày của các cổ phiếu Việt Nam trong giai đoạn 2022–2026. Universe chính là HOSE-80, được chọn theo các tiêu chí thanh khoản, vốn hóa, niêm yết liên tục và độ phủ dữ liệu. Robustness test sử dụng tập mở rộng 125 mã HOSE+HNX.

Mỗi quan sát trong dataset cuối cùng tương ứng với một cặp `(ticker, period)`. Nhãn dự báo phản ánh xu hướng tăng/không tăng của kỳ tiếp theo.

## 3.3. Đặc trưng kỹ thuật

Từ dữ liệu OHLCV ngày, hệ thống tính các đặc trưng kỹ thuật theo kỳ:

| Nhóm | Đặc trưng ví dụ |
|---|---|
| Lợi suất | `return_q`, `return_mean_daily`, `return_prev_q`, `return_2q_ago` |
| Biến động | `return_std_daily`, `volatility_q`, `price_range_q` |
| Thanh khoản | `volume_mean_q`, `volume_change_q` |
| Xu hướng | `sma20_end`, `ema20_end`, `price_vs_sma20` |
| Chỉ báo | `rsi_mean_q`, `rsi_end_q`, `macd_hist_mean_q`, `bb_position_q` |

Các đặc trưng kỳ hiện tại được dùng để dự báo kỳ tiếp theo. Các bước chuẩn hóa và xử lý thiếu dữ liệu phải được fit trên tập train để tránh leakage.

## 3.4. ML Signal Engine

ML Signal Engine sử dụng Config_A, tức chỉ dùng đặc trưng kỹ thuật. Quy trình:

1. Merge dữ liệu đặc trưng kỹ thuật và nhãn.
2. Chia train/test theo thời gian, không shuffle.
3. Fit imputer/scaler trên train, transform test.
4. Huấn luyện Logistic Regression, Random Forest, XGBoost, LightGBM.
5. Đánh giá bằng Balanced Accuracy, AUC, F1, Precision/Recall.
6. Sinh `pred_proba_up`, `pred_label`, rank và period return cho backtest.

Đầu ra của ML Signal Engine là input chính cho evidence pack.

## 3.5. Backtest long-only

Chiến lược mô phỏng tuân thủ đặc thù thị trường cổ phiếu cơ sở Việt Nam:

- Chỉ mua mã có `pred_label = 1`.
- Có thể chọn tất cả mã dự báo tăng hoặc Top-K theo `pred_proba_up`.
- Phân bổ đều vốn cho các mã được chọn.
- Không bán khống.
- Tính chi phí giao dịch explicit cost.
- So sánh với buy-and-hold equal, equal-weight rebalanced và VNINDEX nếu có.

Các giả định giới hạn:

- Backtest theo kỳ, không mô phỏng khớp lệnh từng phiên.
- Bỏ qua slippage và tác động thị trường.
- T+2, biên độ giá và lô tối thiểu chỉ là giả định nền.
- Kết quả phục vụ học thuật, không phải khuyến nghị đầu tư.

## 3.6. News Evidence Layer

News Evidence Layer lưu tin tức công khai liên quan đến cổ phiếu. Mỗi tin gồm:

- `evidence_id`.
- `ticker`.
- `published_at`.
- `source`.
- `title`.
- `summary` hoặc nội dung xử lý.
- `article_summary` sinh từ full article nếu crawl được.
- `key_facts` gồm các fact ngắn có `fact_id`, `evidence_quote`, `fact_type`, `direction` và `confidence`.
- `risk_flags` như debt/legal/governance/capital dilution/audit issue nếu rule-based detector phát hiện.
- `event_type` nếu xác định được.
- `full_text_ref`/`content_hash` và `full_text_chars` để audit nội dung gốc.
- `relevance` nếu được chấm thủ công hoặc rule-based.

Pipeline hiện có lớp `TASK_2B` để crawl detail page và tạo `data/news/enriched/all_news_enriched.csv`. Full text được lưu cục bộ để audit nhưng không mặc định đưa toàn bộ vào prompt LLM. Evidence pack chỉ dùng summary/key facts/risk flags và excerpt ngắn nhằm giảm token, giảm nhiễu boilerplate và giữ kiểm soát trích dẫn.

Tin tức chỉ được đưa vào evidence pack nếu `published_at <= decision_date`.

## 3.7. Evidence Pack

Evidence pack là gói dữ liệu point-in-time cho một decision record. Schema gồm:

- `decision_id`.
- `ticker`.
- `decision_date` hoặc `quarter_id`.
- `holding_horizon`.
- `ml_signal`: probability, rank, label, signal class.
- `technical_snapshot`: RSI, MACD, price_vs_sma, return, volatility.
- `top_drivers`: SHAP/feature importance.
- `news_evidence`: danh sách tin trước decision date.
- `data_quality_flags`: thiếu tin, coverage thấp, matching không chắc chắn.
- `guardrails`: xác nhận không chứa dữ liệu tương lai.

Evidence pack là input duy nhất cho LLM khi tạo decision card ban đầu.

## 3.8. LLM Decision Card

Decision card gồm:

1. Tóm tắt tín hiệu.
2. Luận điểm đầu tư chính.
3. Yếu tố hỗ trợ.
4. Yếu tố cần lưu ý/rủi ro.
5. Trigger theo dõi.
6. Thời điểm review.
7. Kết luận hỗ trợ quyết định.
8. Disclaimer.

Prompt bắt buộc:

- chỉ dùng evidence pack;
- không thêm dữ kiện ngoài;
- không dự báo giá tuyệt đối;
- không dùng ngôn ngữ khuyến nghị chắc chắn;
- nếu thiếu dữ liệu thì phải ghi rõ;
- mỗi luận điểm chính phải có evidence reference.

## 3.9. Monitoring và Outcome Review

Monitoring sử dụng rule-based triggers:

- ML probability giảm dưới ngưỡng.
- Rank rơi khỏi Top-K.
- `pred_label` đổi từ 1 sang 0.
- RSI/MACD/price_vs_sma đảo chiều.
- Drawdown vượt ngưỡng.
- Tin mới có event type tiêu cực hoặc trái với thesis.
- Hết holding period.

Outcome review sau holding period ghi:

- realized return;
- benchmark return;
- excess return;
- decision outcome;
- thesis đúng/sai ở điểm nào;
- monitoring có phát hiện cảnh báo không;
- bài học rút ra.

Outcome review được tách khỏi decision card ban đầu để tránh rò rỉ dữ liệu.

## 3.10. Đánh giá hệ thống

Đánh giá gồm bốn nhóm:

1. **ML metrics:** Balanced Accuracy, AUC, F1, Precision/Recall.
2. **Investment metrics:** cumulative return, Sharpe, max drawdown, hit rate.
3. **LLM decision card rubric:** faithfulness, hallucination control, ML explanation, risk awareness, monitoring usefulness, clarity/usefulness.
4. **Monitoring/outcome case studies:** đánh giá khả năng phát hiện bối cảnh thay đổi và hậu kiểm thesis.

---

# CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ THẢO LUẬN

## 4.1. Kết quả ML Signal Engine

ML Signal Engine là phần lõi định lượng của hệ thống. Kết quả hiện có cho thấy mô hình dựa trên đặc trưng kỹ thuật tạo tín hiệu tốt hơn đáng kể so với baseline.

### 4.1.1. Hiệu quả phân loại

Trong cấu hình kỹ thuật Config_A, mô hình tốt nhất trên tập HOSE-80 đạt Balanced Accuracy xấp xỉ **0,76** và AUC khoảng **0,82–0,83**. Kết quả robustness trên universe mở rộng 125 mã HOSE+HNX cho thấy hiệu quả không suy giảm: Random Forest đạt Balanced Accuracy **0,7607**, AUC-ROC **0,8307**, F1 Macro **0,7573** trên 735 mẫu test. XGBoost và LightGBM cũng đạt Balanced Accuracy khoảng **0,753**.

Bảng kết quả robustness:

| Mô hình | Balanced Acc | AUC-ROC | F1 Macro | n_train | n_test |
|---|---:|---:|---:|---:|---:|
| Baseline Majority | 0,5000 | 0,5000 | 0,2973 | 1.653 | 735 |
| Baseline Stratified | 0,5223 | 0,5223 | 0,5186 | 1.653 | 735 |
| Logistic Regression | 0,6488 | 0,7036 | 0,6438 | 1.653 | 735 |
| Random Forest | **0,7607** | **0,8307** | **0,7573** | 1.653 | 735 |
| XGBoost | 0,7531 | 0,8265 | 0,7502 | 1.653 | 735 |
| LightGBM | 0,7530 | 0,8198 | 0,7509 | 1.653 | 735 |

Kết quả này cho thấy mô hình kỹ thuật không chỉ vượt baseline ngẫu nhiên/đa số lớp mà còn duy trì hiệu quả khi mở rộng tập mã. Vì vậy, Config_A phù hợp làm `ML Signal Engine` cho hệ thống decision-support mới.

### 4.1.2. Hiệu quả backtest đầu tư

Backtest long-only theo kỳ cho thấy chiến lược mô hình tạo giá trị đầu tư trong phạm vi giả định mô phỏng.

| strategy | cost_scenario | cumulative_return | mean_period_return | sharpe_ratio | max_drawdown | hit_rate |
|---|---|---:|---:|---:|---:|---:|
| model | gross | 0,620698 | 0,104646 | 1,07947 | 0 | 1 |
| model | net | **0,602964** | **0,102254** | **1,05171** | -0,001035 | 0,8 |
| buy_hold_equal | gross | 0,253502 | 0,050748 | 0,446062 | -0,020034 | 0,6 |
| buy_hold_equal | net | 0,253502 | 0,050748 | 0,446062 | -0,020034 | 0,6 |
| equal_weight_rebalanced | gross | 0,253502 | 0,050748 | 0,446062 | -0,020034 | 0,6 |
| equal_weight_rebalanced | net | 0,253502 | 0,050748 | 0,446062 | -0,020034 | 0,6 |

Chiến lược mô hình đạt lợi nhuận tích lũy net khoảng **60,3%**, cao hơn benchmark buy-and-hold/equal-weight khoảng **25,4%**. Sharpe ratio net khoảng **1,05**, cao hơn benchmark khoảng **0,45**.

Kết quả robustness với 125 mã HOSE+HNX cũng cho thấy chiến lược mô hình đạt lợi nhuận tích lũy khoảng **57,5%**, so với VNINDEX buy-and-hold khoảng **42,1%**, tức vượt khoảng **15,3 điểm phần trăm** trong cùng giai đoạn kiểm định.

### 4.1.3. Walk-forward stability

| cutoff | n_test | Balanced Accuracy | AUC-ROC | Model net return | Buy-hold return |
|---|---:|---:|---:|---:|---:|
| 2024Q3 | 556 | 0,722948 | 0,796966 | 0,656316 | 0,281762 |
| 2025Q1 | 400 | 0,759900 | 0,823509 | 0,602964 | 0,253502 |
| 2025Q3 | 240 | 0,639988 | 0,709755 | 0,118227 | 0,007196 |

Mô hình có lợi nhuận dương ở **3/3 cutoff** và vượt buy-and-hold ở **3/3 cutoff**. Balanced Accuracy trung bình khoảng **0,7076**. Điều này không chứng minh hiệu quả tương lai, nhưng cho thấy tín hiệu kỹ thuật tương đối ổn định trong nhiều lát cắt thời gian.

## 4.2. Giải thích tín hiệu ML bằng SHAP/feature importance

Hệ thống decision-support cần giải thích vì sao một cổ phiếu được chọn, không chỉ trả về xác suất. Kết quả SHAP/feature importance hiện có cho phép chuyển tín hiệu mô hình thành bằng chứng định lượng trong evidence pack.

Top driver kỹ thuật:

| rank | feature | mean_abs_shap | permutation_importance |
|---:|---|---:|---:|
| 1 | `rsi_end_q` | 1,67288 | 0,186028 |
| 2 | `macd_hist_mean_q` | 0,50877 | 0,0192105 |
| 3 | `price_vs_sma20` | 0,446245 | 0,00300752 |
| 4 | `return_2q_ago` | 0,413385 | 0,00483709 |
| 5 | `return_q` | 0,322035 | 0,0128195 |
| 6 | `return_prev_q` | 0,305401 | 0,0148371 |
| 7 | `volume_change_q` | 0,283926 | 0,0107644 |
| 8 | `return_mean_daily` | 0,280323 | 0,00922306 |
| 9 | `price_range_q` | 0,265953 | 0,00533835 |
| 10 | `sma20_end` | 0,256022 | 0,0172055 |

Trong hệ thống mới, các driver này được đưa vào `top_drivers` của evidence pack. LLM sau đó diễn giải các driver này thành ngôn ngữ tự nhiên, ví dụ: động lượng tích cực, giá nằm trên đường trung bình, hoặc RSI ở vùng hỗ trợ xu hướng. Cách làm này giúp decision card gắn với bằng chứng định lượng thay vì viết luận điểm chung chung.

## 4.3. Kiểm toán rò rỉ dữ liệu

Leakage audit cũ kết luận **PASS**. Có 16 đặc trưng kỹ thuật được kiểm tra, trong đó 14 đặc trưng thuộc nhóm in-period và 2 đặc trưng thuộc nhóm past; không có đặc trưng nào thuộc nhóm future.

Các cột nhãn và return tương lai như `return`, `next_quarter_id`, `next_avg_close`, `label_basic`, `label_threshold` không xuất hiện trong feature set. Ngoài ra, không có đặc trưng nào có tương quan tuyệt đối với `label_basic` vượt ngưỡng 0,95.

Kết quả này đặc biệt quan trọng vì hiệu quả mô hình kỹ thuật khá cao. Trong hệ thống mới, nguyên tắc chống leakage được mở rộng từ ML pipeline sang LLM pipeline:

- Decision card ban đầu chỉ dùng dữ liệu trước hoặc tại `decision_date`.
- News evidence phải có `published_at <= decision_date`.
- Prompt tạo thesis không chứa realized return, nhãn kỳ sau hoặc outcome review.
- Outcome review được tạo riêng sau holding period.

## 4.4. Vai trò mới của tin tức: từ predictor sang evidence layer

Các thử nghiệm sau full-text enrichment cho thấy tin tức/từ khóa không cải thiện dự báo ổn định khi được dùng như feature đầu vào của mô hình. Full text gần như đầy đủ (**45.949/45.968 unique URLs**, 99,96% coverage) đã được đưa vào TASK 4, nhưng Config_B chỉ dùng từ khóa vẫn gần mức ngẫu nhiên; Config_C kết hợp kỹ thuật + từ khóa không vượt Config_A.

Kết quả production split theo quý sau full text:

| Mô hình | Config_A kỹ thuật | Config_B từ khóa | Config_C kết hợp | C - A |
|---|---:|---:|---:|---:|
| LightGBM | 0,7599 | 0,4510 | 0,7357 | −0,0242 |
| Logistic Regression | 0,7269 | 0,4999 | 0,7132 | −0,0138 |
| Random Forest | 0,7351 | 0,5053 | 0,6679 | −0,0672 |
| XGBoost | 0,7293 | 0,4792 | 0,7238 | −0,0055 |

Kiểm định H2 cũng không tìm thấy từ khóa nào đạt ý nghĩa thống kê sau hiệu chỉnh BH-FDR: **0/71** từ khóa significant. Một số từ khóa như `chia cổ tức`, `giảm mạnh`, `nợ xấu`, `đại hội cổ đông` có raw p-value thấp, nhưng không vượt ngưỡng sau hiệu chỉnh đa kiểm định.

LLM sentiment A6 và distant supervision B1 cũng không làm thay đổi kết luận. LLM sentiment có mean Δ(C−A) khoảng **-0,0061**, McNemar p khoảng **0,6177**. Distant supervision có tín hiệu yếu ở cấp bài viết với AUC macro khoảng **0,6797**, nhưng khi tổng hợp theo kỳ thì Δ(C−A) chỉ khoảng **+0,0027**, McNemar p khoảng **0,5601**.

Vì vậy, luận văn mới không xem tin tức là predictor chính. Tin tức được định vị là evidence layer:

- giúp LLM giải thích bối cảnh doanh nghiệp;
- giúp nêu yếu tố hỗ trợ hoặc rủi ro;
- giúp monitoring phát hiện tin mới trái chiều;
- giúp outcome review phân tích thesis ban đầu đúng/sai ở đâu.

Đây là pivot quan trọng của luận văn: kết quả âm của news-as-feature không bị bỏ đi, mà trở thành cơ sở khoa học cho thiết kế news-as-evidence.

## 4.5. Evidence pack và decision card

Evidence pack là lớp trung gian giữa ML pipeline và LLM. Từ dữ liệu hiện có, script `scripts/generate_decision_support_artifacts.py` đã sinh 25 evidence pack cho Top-5 cổ phiếu mỗi kỳ trong 5 kỳ `2025Q1`–`2026Q1`. Mỗi pack chứa 5 tin tức trước hoặc tại `decision_date`, technical snapshot, top drivers và guardrail tách outcome khỏi decision card ban đầu.

Một evidence pack gồm:

- `decision_id`, `ticker`, `decision_date`, `period_id`, `holding_horizon`;
- `ml_signal`: model name, probability, label, rank, signal class;
- `technical_snapshot`: RSI, MACD, price_vs_sma20, return, volatility, volume;
- `top_drivers`: feature importance/driver kỹ thuật đã chuẩn hóa diễn giải;
- `news_evidence`: evidence ID, ngày đăng, nguồn, tiêu đề, `article_summary`, `key_facts`, `risk_flags`, event type, full-text reference/hash và excerpt ngắn;
- `data_quality_flags`: coverage, matching confidence, full-text/summary/key-fact coverage, missing fields;
- `outcome_for_review_only`: realized return chỉ dùng cho outcome review, không đưa vào initial decision card;
- `guardrails`: không chứa dữ liệu tương lai trong initial prompt, yêu cầu LLM cite evidence.

Các artifact baseline đã sinh nằm trong `reports/decision_support/generated/`, gồm `evidence_packs_audit.json`, `evidence_packs_initial.json`, `evidence_packs_ml_only.json`, `decision_cards.md`, `outcome_reviews.md`, `monitoring_cases_summary.csv`, `llm_rubric_scoring_template.csv` và `generated_summary.md`. Sau khi chạy lại generator/enrichment/monitoring, các file bổ sung như `news_fulltext_coverage.csv`, `monitoring_events.csv` và `monitoring_timeline.json` được dùng để kiểm tra coverage và trigger tin mới. Prompt packs offline cho LLM đã ghi tại `llm_prompt_packs_ml_only.jsonl` và `llm_prompt_packs_full_evidence.jsonl`; prompt packs chấm rubric đã ghi tại `llm_rubric_prompt_packs.jsonl`.

Decision card được thiết kế theo các mục:

1. Tóm tắt tín hiệu.
2. Luận điểm đầu tư chính.
3. Yếu tố hỗ trợ.
4. Yếu tố cần lưu ý/rủi ro.
5. Trigger theo dõi.
6. Thời điểm review.
7. Kết luận hỗ trợ quyết định.
8. Disclaimer.

Một decision card tốt phải cụ thể, bám evidence, phân biệt tín hiệu định lượng với bằng chứng định tính, nêu rủi ro thật và có trigger đo được. Card không được viết như lời khuyên đầu tư chắc chắn.

## 4.6. Đánh giá LLM decision card

Luận văn dùng rubric 1–5 điểm cho sáu tiêu chí:

| Tiêu chí | Ý nghĩa |
|---|---|
| Faithfulness | Card có bám sát evidence pack không |
| Hallucination control | Card có thêm dữ kiện ngoài evidence không |
| ML explanation | Card có giải thích probability/rank/driver không |
| Risk awareness | Card có nêu rủi ro cụ thể không |
| Monitoring usefulness | Trigger có đo được và hữu ích không |
| Clarity/usefulness | Card có rõ ràng, dễ dùng và dễ hậu kiểm không |

Nên so sánh ba baseline:

1. Rule-based template không LLM.
2. LLM chỉ có ML score + technical evidence.
3. LLM có full evidence pack gồm ML + technical + news + data quality flags.

Trong bản artifact hiện tại, baseline rule-based đã được sinh cho 25 decision records trong `reports/decision_support/generated/decision_cards.md`. Run live bằng Gemini Pro (`gemini-2.5-pro`, SDK `google-genai`, `temperature=not_sent`) đã tạo đủ 50 LLM decision cards cho toàn bộ 25 records: 25 card `llm_ml_only` và 25 card `llm_full_evidence`. Sau đó hệ thống chấm rubric 75 card gồm `rule_based_baseline`, `llm_ml_only` và `llm_full_evidence`.

Kết quả full 25-case cho thấy `llm_full_evidence` đạt điểm cao nhất trên rubric chất lượng decision card: overall trung bình 5.00, so với 4.32 của rule-based baseline và 1.16 của `llm_ml_only`. Điểm thấp của `llm_ml_only` không được diễn giải là mô hình LLM yếu, mà phản ánh việc card thiếu lớp bằng chứng tin tức/rủi ro khi rubric đánh giá trên evidence pack đầy đủ. Kết quả này chỉ là đánh giá chất lượng card, không phải bằng chứng LLM cải thiện lợi nhuận đầu tư.

Kết quả rubric chỉ đo chất lượng hỗ trợ quyết định, không được diễn giải thành “LLM cải thiện lợi nhuận đầu tư”.

## 4.7. Monitoring và outcome review

Monitoring giúp hệ thống không dừng ở thời điểm tạo decision card. Các trigger chính gồm:

| Nhóm trigger | Điều kiện ví dụ | Trạng thái |
|---|---|---|
| ML probability | `pred_proba_up < 0,55` hoặc giảm mạnh | Review Required |
| Rank | Rơi khỏi Top-K hoặc giảm nhiều bậc | Watch / Review Required |
| Label | `pred_label` chuyển từ 1 sang 0 | Review Required |
| Technical | MACD âm, price_vs_sma20 < 0, RSI suy yếu | Watch / Review Required |
| Drawdown | Giá giảm trên 8–10% từ decision price | Review Required |
| News | Tin mới tiêu cực hoặc trái thesis | Watch / Review Required |
| Data quality | Matching nghi ngờ hoặc coverage thấp | Watch |
| Time | Đến cuối holding period | Outcome Review |

Outcome review sau kỳ nắm giữ ghi realized return, benchmark return, excess return, các monitoring events, phần thesis đúng/sai và bài học rút ra. Điều quan trọng là outcome review được tách khỏi decision card ban đầu để tránh rò rỉ dữ liệu.

Trong luận văn, monitoring nên được trình bày bằng 3–5 case study tiêu biểu. Từ 25 decision records đã sinh, các case đại diện có thể dùng là:

| Case | Decision record | Lý do chọn |
|---|---|---|
| ML đúng và thesis được hỗ trợ | `2025Q2_STB_01` | Rank 1, probability cao, realized return 0.2763, có earnings-related news trước decision date. |
| ML sai nhưng monitoring cảnh báo được | `2026Q1_DPM_03` | Realized return -0.0276, `price_vs_sma20` âm và nhiều news tag `legal_risk`. |
| ML đúng nhưng evidence cần thận trọng | `2025Q3_KDH_04` | Return dương 0.0461 nhưng RSI weak/neutral, `price_vs_sma20` âm và news thiên về giao dịch/quỹ. |
| News trái chiều với ML | `2025Q2_VND_05` | Return dương nhưng có news tag `debt_risk`/`capital` và MACD âm; dùng để minh họa evidence layer nêu rủi ro. |
| Tín hiệu cần review sau khuyến nghị | `2025Q4_VBB_05` | Return -0.0526, RSI weak/neutral, MACD âm và current return âm. |

## 4.8. Thảo luận tổng hợp

Kết quả tổng hợp cho thấy hướng tiếp cận phù hợp là **ML-led decision support**. ML tạo tín hiệu có giá trị định lượng; news cung cấp bối cảnh; LLM giúp chuyển evidence thành luận điểm có cấu trúc; monitoring và outcome review giúp đóng vòng phản hồi.

Điểm cần nhấn mạnh là LLM không thay thế mô hình ML và không thay thế nhà đầu tư. LLM chỉ là lớp diễn giải và tổ chức thông tin. Điều này giúp giảm rủi ro hallucination và tránh overclaim về khả năng dự báo của LLM.

Hướng mới cũng giữ lại giá trị khoa học của kết quả âm cũ. Việc tin tức/từ khóa không cải thiện forecast không làm luận văn yếu đi; ngược lại, nó giúp xác định đúng vai trò của tin tức trong hệ thống: evidence để giải thích và theo dõi, không phải biến dự báo chính.

---

# CHƯƠNG 5: KẾT LUẬN, HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

## 5.1. Kết luận chính

Luận văn đề xuất một hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam dựa trên tín hiệu học máy, tin tức công khai và LLM. Hướng tiếp cận này chuyển trọng tâm từ dự báo đơn lẻ sang quản trị vòng đời quyết định đầu tư.

Kết quả hiện có cho thấy ML kỹ thuật có giá trị định lượng rõ ràng qua classification metrics, backtest, walk-forward và robustness test. Tin tức/từ khóa không cải thiện dự báo ổn định khi dùng làm feature, nhưng vẫn có giá trị như evidence layer. LLM phù hợp để tạo decision card, nêu rủi ro, hỗ trợ monitoring và hậu kiểm, với điều kiện được ràng buộc chặt bởi evidence pack.

Có thể trả lời các câu hỏi nghiên cứu như sau:

- **RQ1:** Có. Mô hình kỹ thuật tạo tín hiệu phân loại vượt baseline và duy trì hiệu quả trong robustness test.
- **RQ2:** Có trong phạm vi backtest hiện tại. Chiến lược mô hình vượt buy-and-hold/equal-weight và vượt VNINDEX trong robustness test, nhưng kết quả phụ thuộc giả định mô phỏng.
- **RQ3:** Có trong phạm vi đánh giá chất lượng decision card. Baseline rule-based đã được sinh từ 25 evidence pack thật; toàn bộ 25 records đã được chạy live bằng Gemini Pro cho hai biến thể `llm_ml_only` và `llm_full_evidence`, rồi chấm rubric cùng rule-based baseline. Kết quả cho thấy `llm_full_evidence` đạt điểm rubric cao nhất về faithfulness, risk awareness, monitoring usefulness và clarity. Kết quả này chỉ đo chất lượng decision card, không chứng minh cải thiện return hay alpha.
- **RQ4:** Có thể minh họa bằng case study monitoring/outcome review. Các case đại diện đã được chọn từ generated artifacts, nhưng monitoring không nên được claim cải thiện return nếu chưa có backtest quy mô lớn.

## 5.2. Đóng góp

1. Đề xuất framing mới: từ dự báo xu hướng giá sang hỗ trợ quản trị quyết định đầu tư.
2. Sử dụng ML signal đã kiểm chứng làm lõi định lượng.
3. Tái định vị tin tức từ feature dự báo sang evidence layer.
4. Thiết kế decision card có cấu trúc bằng LLM và kiểm soát hallucination bằng evidence pack.
5. Đề xuất monitoring và outcome review để hậu kiểm quyết định.

## 5.3. Hạn chế

1. Prototype chưa phải hệ thống production.
2. Backtest còn đơn giản, chưa mô phỏng đầy đủ slippage, khớp lệnh từng phiên và tác động thị trường.
3. Đánh giá LLM có yếu tố định tính và phụ thuộc rubric.
4. Tin tức công khai có coverage không đều theo mã/kỳ.
5. Kết quả phụ thuộc dữ liệu 2022–2026 và universe được chọn.
6. Hệ thống không đưa ra khuyến nghị đầu tư thực tế.
7. Monitoring hiện được thiết kế ở mức rule-based/case study, chưa chứng minh cải thiện hiệu quả danh mục ở quy mô lớn.

## 5.4. Hướng phát triển

1. Mở rộng evidence layer bằng báo cáo tài chính, công bố doanh nghiệp và dữ liệu vĩ mô.
2. Tăng độ chính xác ticker/news matching và event extraction.
3. Đánh giá LLM decision card với nhiều người chấm độc lập.
4. Thử nghiệm rolling live advisory trong môi trường paper trading.
5. Kết hợp monitoring định lượng với cảnh báo tin tức theo event-time.
6. Xây dựng giao diện dashboard sau khi prototype nghiên cứu ổn định.
7. Kiểm định chiến lược có monitoring bằng backtest riêng nếu muốn đánh giá tác động lên return/drawdown.

## 5.5. Định vị cuối cùng

Đề tài không chứng minh LLM dự báo cổ phiếu tốt hơn ML. Đề tài chứng minh một hướng thiết kế thực tế hơn: ML tạo tín hiệu định lượng, tin tức cung cấp bằng chứng, LLM tạo luận điểm có kiểm soát, monitoring theo dõi thay đổi và outcome review giúp học lại từ quyết định.

Đây là đóng góp phù hợp cho một luận văn khoa học dữ liệu ứng dụng: có mô hình định lượng, có kiểm soát rò rỉ dữ liệu, có đánh giá đầu tư, có lớp giải thích và có cơ chế hậu kiểm.

---

# TÀI LIỆU THAM KHẢO

1. Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical evidence. *Journal of Finance*, 25(2), 383–417.
2. Murphy, J. J. (1999). *Technical Analysis of the Financial Markets*. New York Institute of Finance.
3. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.
4. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of KDD*.
5. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. *NeurIPS*.
6. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *NeurIPS*.
7. Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. *Journal of Computational Science*, 2(1), 1–8.
8. Schumaker, R. P., & Chen, H. (2009). Textual analysis of stock market prediction using breaking financial news. *ACM Transactions on Information Systems*, 27(2), 1–19.
9. Nassirtoussi, A. K., Aghabozorgi, S., Wah, T. Y., & Ngo, D. C. L. (2014). Text mining for market prediction: A systematic review. *Expert Systems with Applications*, 41(16), 7653–7670.
10. Nguyen, D. Q., & Nguyen, A. T. (2020). PhoBERT: Pre-trained language models for Vietnamese. *Findings of EMNLP*.

---

# PHỤ LỤC

## Phụ lục A. Nguồn số liệu nội bộ đã trích

- `reports/source_evidence/tong_hop_bang_chung_tu_KLTN_MASTER.md` — bản tổng hợp số liệu và kết luận đã trích ra khỏi thư mục cũ.
- `reports/decision_support/danh_gia_pivot_ml_llm_decision_support.md` — đánh giá hướng pivot và phạm vi nên giữ/cắt.

## Phụ lục B. Schema hệ thống hỗ trợ quyết định

- `reports/decision_support/evidence_pack_schema.md` — schema evidence pack point-in-time.
- `reports/decision_support/decision_card_schema.md` — schema decision card và outcome review.

## Phụ lục C. Prompt và rubric LLM

- `reports/decision_support/llm_prompt_template.md` — prompt templates cho tạo card, update, review và chấm rubric.
- `reports/decision_support/llm_evaluation_rubric.md` — rubric đánh giá LLM decision card.

## Phụ lục D. Mẫu minh họa và case study

- `reports/decision_support/sample_decision_cards.md` — decision card mẫu ban đầu.
- `reports/decision_support/monitoring_review_cases.md` — thiết kế và case study monitoring/hậu kiểm đã cập nhật bằng decision records thật.
- `reports/decision_support/generated/evidence_packs.json` — 25 evidence pack thật sinh từ signals/features/news hiện có.
- `reports/decision_support/generated/decision_cards.md` — 25 decision card rule-based baseline.
- `reports/decision_support/generated/outcome_reviews.md` — 25 outcome review có realized return hậu kiểm.
- `reports/decision_support/generated/generated_summary.md` — tổng hợp run, outcome summary và case study đề xuất.
- `docs/phu_luc_ml_llm_decision_support.md` — phụ lục gom schema, prompt, rubric, artifacts, case study và checklist bản nộp.
- `reports/decision_support/validation_consistency_check.md` — kiểm tra nhất quán số liệu, leakage, overclaim và phụ thuộc dữ liệu.

## Phụ lục E. Disclaimer học thuật

Luận văn này phục vụ mục tiêu nghiên cứu và minh họa kỹ thuật khoa học dữ liệu. Nội dung không phải khuyến nghị đầu tư. Mọi kết quả backtest là kết quả lịch sử trong phạm vi giả định mô phỏng và không đảm bảo hiệu quả tương lai.
