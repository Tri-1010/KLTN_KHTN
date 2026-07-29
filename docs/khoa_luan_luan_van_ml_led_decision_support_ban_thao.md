# BẢN THẢO KHÓA LUẬN / LUẬN VĂN

## Hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam dựa trên tín hiệu học máy và LLM tạo luận điểm từ bằng chứng tin tức

**Tên tiếng Anh:**  
**An ML-Led Investment Decision Support System for Vietnamese Stocks with LLM-Generated Evidence-Grounded Decision Cards**

> Bản thảo này dùng narrative cuối sau phản biện: **ML-led decision support**, không claim LLM/news tạo alpha ổn định.

---

## TÓM TẮT

Luận văn đề xuất một hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam kết hợp mô hình học máy, dữ liệu tin tức công khai và mô hình ngôn ngữ lớn (Large Language Model — LLM). Khác với cách tiếp cận chỉ tập trung dự báo giá hoặc dự báo xu hướng tăng/giảm, luận văn đặt trọng tâm vào việc chuyển đầu ra của mô hình học máy thành một **decision record** có thể giải thích, theo dõi và hậu kiểm.

Kết quả thực nghiệm hiện có cho thấy mô hình học máy dựa trên đặc trưng kỹ thuật là nguồn tín hiệu định lượng ổn định nhất. Trên dữ liệu cổ phiếu Việt Nam giai đoạn 2022–2026, mô hình kỹ thuật đạt Balanced Accuracy khoảng 0,76 và AUC khoảng 0,83. Backtest long-only cho thấy chiến lược mô hình đạt lợi nhuận tích lũy net khoảng 60,3% so với benchmark buy-and-hold/equal-weight khoảng 25,4%, Sharpe ratio khoảng 1,05, và walk-forward vượt benchmark ở 3/3 cutoff. Robustness test trên 125 mã HOSE+HNX đạt Balanced Accuracy 0,7607 và AUC 0,8307.

Ngược lại, các đặc trưng tin tức dạng keyword/frequency/sentiment/distant supervision không cải thiện dự báo xu hướng một cách ổn định khi được dùng trực tiếp như predictor. Các thí nghiệm LLM semantic features có tín hiệu cục bộ trong một số cấu hình, nhưng hiệu ứng không đủ robust để làm claim chính về alpha. Vì vậy, luận văn tái định vị tin tức như **lớp bằng chứng định tính** thay vì nguồn alpha trực tiếp.

Hệ thống được thiết kế theo vòng đời `select → explain → monitor → update → review`. ML Signal Engine chọn và xếp hạng cổ phiếu. Evidence Pack Builder đóng gói tín hiệu ML, technical drivers, tin tức point-in-time và data quality flags. LLM tạo decision card có cấu trúc từ evidence pack, bị ràng buộc không thêm thông tin ngoài input. Monitoring theo dõi thay đổi tín hiệu, technical state, tin mới và drawdown; outcome review hậu kiểm sau kỳ nắm giữ.

Artifact hiện có gồm 25 evidence packs, 25 rule-based decision cards, 25 LLM ML-only cards, 25 LLM full-evidence cards, 75 rubric scores, 3.838 monitoring news events và 25 outcome reviews. Kết quả rubric cho thấy LLM full-evidence cards đạt điểm overall 5,00, cao hơn rule-based baseline 4,32 và ML-only cards 1,16. Kết quả này đo **chất lượng decision card**, không đo lợi nhuận và không chứng minh LLM tạo alpha.

Đóng góp chính của luận văn là một framework khoa học dữ liệu ứng dụng cho hỗ trợ quyết định đầu tư: ML làm lõi định lượng, tin tức làm evidence layer, LLM làm lớp diễn giải có kiểm soát, monitoring và outcome review giúp quản trị vòng đời quyết định. Hệ thống là prototype nghiên cứu, không phải khuyến nghị đầu tư hay robo-advisor.

**Từ khóa:** học máy, cổ phiếu Việt Nam, hỗ trợ quyết định đầu tư, LLM, decision card, evidence pack, SHAP, backtest, monitoring, outcome review.

---

## ABSTRACT

This thesis proposes an investment decision support system for Vietnamese stocks by combining machine learning signals, public financial news, and Large Language Models (LLMs). Instead of focusing solely on price forecasting or binary up/down prediction, the thesis emphasizes the transformation of machine learning outputs into auditable decision records that can be explained, monitored, and reviewed after the holding period.

Existing results show that the technical-feature-based machine learning model provides the most stable quantitative signal. On Vietnamese stock data from 2022 to 2026, the technical model achieves a Balanced Accuracy of approximately 0.76 and an AUC of approximately 0.83. A long-only backtest reports about 60.3% net cumulative return compared with approximately 25.4% for the buy-and-hold/equal-weight benchmark, with a Sharpe ratio of approximately 1.05. Walk-forward evaluation outperforms the benchmark in 3 out of 3 cutoffs. A robustness test on 125 HOSE+HNX stocks reports a Balanced Accuracy of 0.7607 and an AUC of 0.8307.

In contrast, keyword/frequency/sentiment/distant-supervision news features do not consistently improve trend prediction when used directly as predictors. LLM semantic features show localized positive signals under some configurations, but the effect is not sufficiently robust to support a general alpha claim. Therefore, this thesis repositions news as a qualitative evidence layer rather than a primary alpha source.

The proposed system follows the lifecycle `select → explain → monitor → update → review`. The ML Signal Engine selects and ranks candidate stocks. The Evidence Pack Builder packages ML signals, technical drivers, point-in-time news evidence, and data-quality flags. The LLM generates structured decision cards from the evidence pack under strict grounding constraints. The monitoring module tracks signal changes, technical-state changes, new risk-related news, and drawdowns; the outcome review module evaluates the initial thesis after the holding period.

The current artifacts include 25 evidence packs, 25 rule-based decision cards, 25 LLM ML-only cards, 25 LLM full-evidence cards, 75 rubric scores, 3,838 monitoring news events, and 25 outcome reviews. Rubric results show that full-evidence LLM cards achieve an overall score of 5.00, compared with 4.32 for the rule-based baseline and 1.16 for ML-only cards. This result measures decision-card quality, not return improvement or LLM-generated alpha.

The main contribution is an applied data-science framework for investment decision support: machine learning as the quantitative core, news as the evidence layer, LLMs as controlled explanation generators, and monitoring/outcome review as decision-lifecycle governance. The system is a research prototype, not investment advice or an autonomous trading advisor.

---

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh nghiên cứu

Thị trường chứng khoán Việt Nam trong những năm gần đây phát triển nhanh về quy mô, thanh khoản và mức độ tham gia của nhà đầu tư cá nhân. Cùng với dữ liệu giao dịch như giá, khối lượng và lợi suất, nhà đầu tư còn phải xử lý lượng lớn tin tức tài chính tiếng Việt từ nhiều nguồn: báo điện tử, trang tin tài chính, công bố doanh nghiệp và các nền tảng phân tích.

Trong nghiên cứu khoa học dữ liệu tài chính, bài toán thường được thiết kế dưới dạng dự báo giá, dự báo lợi suất hoặc phân loại xu hướng tăng/giảm trong kỳ tiếp theo. Các mô hình học máy có thể khai thác dữ liệu kỹ thuật như RSI, MACD, SMA, Bollinger Bands, động lượng, biến động và thanh khoản để tạo tín hiệu định lượng.

Tuy nhiên, trong thực tế đầu tư, một tín hiệu như “xác suất tăng cao” chưa đủ để trở thành quyết định có thể sử dụng. Nhà đầu tư cần biết:

- vì sao mã được chọn;
- mô hình dựa vào đặc trưng nào;
- tin tức nào ủng hộ hoặc phản biện luận điểm;
- rủi ro nào cần theo dõi;
- khi nào cần xem xét lại;
- sau kỳ nắm giữ, quyết định đúng hay sai vì lý do gì.

Do đó, vấn đề nghiên cứu không chỉ là “dự báo đúng hơn”, mà là “tổ chức một quy trình hỗ trợ quyết định có thể giải thích, theo dõi và hậu kiểm”.

## 1.2. Vấn đề nghiên cứu

Các hệ thống dự báo tài chính truyền thống thường dừng ở đầu ra như probability, label, Buy/Sell/Hold hoặc ranking. Những đầu ra này hữu ích nhưng chưa đủ cho một quy trình đầu tư có kiểm soát. Chúng thiếu:

1. giải thích định lượng và định tính;
2. bằng chứng tin tức đi kèm;
3. cảnh báo rủi ro;
4. trigger theo dõi;
5. outcome review để học lại từ quyết định.

Dữ liệu tin tức tài chính có vẻ là nguồn thông tin bổ sung tự nhiên. Tuy nhiên, kết quả thực nghiệm trong dự án cho thấy khi tin tức được biểu diễn bằng keyword/frequency/sentiment đơn giản, chúng không cải thiện dự báo xu hướng ổn định so với technical-only baseline. Điều này đặt ra câu hỏi: nếu tin tức không tạo alpha ổn định khi dùng làm predictor, liệu tin tức có thể đóng vai trò khác trong hệ thống đầu tư không?

Luận văn trả lời bằng cách tái định vị tin tức như **evidence layer**. Tin tức được dùng để giải thích bối cảnh, nêu rủi ro, tạo trigger theo dõi và hỗ trợ hậu kiểm; không được dùng như nguồn dự báo chính.

LLM được đưa vào để biến evidence pack thành decision card có cấu trúc. Tuy nhiên, LLM không được dùng để dự báo giá trực tiếp và không được thêm dữ kiện ngoài evidence pack. Cách tiếp cận này giảm rủi ro hallucination và tránh overclaim về khả năng dự báo của LLM.

## 1.3. Mục tiêu nghiên cứu

### 1.3.1. Mục tiêu tổng quát

Xây dựng và đánh giá một prototype hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam kết hợp ML signal, tin tức công khai và LLM-generated decision cards theo vòng đời:

**select → explain → monitor → update → review**

### 1.3.2. Mục tiêu cụ thể

1. Đóng gói mô hình học máy kỹ thuật thành ML Signal Engine để tạo probability, label và rank.
2. Đánh giá ML signal bằng classification metrics, backtest, walk-forward và robustness.
3. Tổng hợp kết quả thử nghiệm news-as-predictor để xác định giới hạn của keyword/frequency/sentiment features.
4. Thiết kế evidence pack point-in-time chứa ML signal, technical drivers, news evidence và data quality flags.
5. Dùng LLM tạo decision cards có cấu trúc, bám evidence và hạn chế hallucination.
6. Thiết kế monitoring events và outcome reviews để quản trị vòng đời quyết định.
7. Đánh giá decision cards bằng rubric chất lượng hỗ trợ quyết định.

## 1.4. Câu hỏi nghiên cứu

**RQ1.** Mô hình học máy dựa trên đặc trưng kỹ thuật có tạo tín hiệu hữu ích cho việc lựa chọn cổ phiếu Việt Nam không?

**RQ2.** Chiến lược Top-K long-only dựa trên ML signal có vượt benchmark theo return, Sharpe và drawdown không?

**RQ3.** Các đặc trưng tin tức dạng keyword/frequency/sentiment/semantic có cải thiện forecast so với technical-only baseline không?

**RQ4.** Nếu news không tạo alpha ổn định, news có thể được dùng như evidence layer để giải thích, theo dõi và hậu kiểm quyết định không?

**RQ5.** LLM full-evidence decision card có chất lượng hỗ trợ quyết định tốt hơn rule-based baseline và ML-only card theo rubric không?

## 1.5. Phạm vi nghiên cứu

Luận văn tập trung vào cổ phiếu Việt Nam, trọng tâm là HOSE-80 và robustness trên 125 mã HOSE+HNX. Dữ liệu gồm OHLCV, technical features, tin tức công khai đã gắn ticker, ML signals, evidence packs, decision cards, monitoring events và outcome reviews trong giai đoạn 2022–2026.

Luận văn không xây dựng hệ thống giao dịch tự động, không dự báo giá tuyệt đối, không dùng LLM để dự báo giá trực tiếp và không đưa ra khuyến nghị đầu tư thực tế. Kết quả backtest là historical simulation trong phạm vi giả định, không bảo đảm hiệu quả tương lai.

## 1.6. Đóng góp của luận văn

1. Đề xuất framing mới: từ dự báo xu hướng sang hỗ trợ quản trị quyết định đầu tư.
2. Chứng minh technical ML signal là lõi định lượng mạnh hơn news-as-predictor trong dữ liệu hiện có.
3. Ghi nhận kết quả âm có giá trị: keyword/frequency/sentiment không cải thiện forecast ổn định.
4. Thiết kế evidence pack point-in-time để ràng buộc LLM.
5. Tạo decision cards bằng rule-based baseline và LLM full-evidence, đánh giá bằng rubric.
6. Thiết kế monitoring và outcome review để hậu kiểm quyết định.

---

# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ NGHIÊN CỨU LIÊN QUAN

## 2.1. Machine Learning trong dự báo cổ phiếu

Machine Learning trong tài chính thường được dùng cho ba nhóm bài toán: hồi quy lợi suất, phân loại xu hướng và xếp hạng cổ phiếu. Trong luận văn này, bài toán lõi là phân loại xu hướng tăng/không tăng trong kỳ tiếp theo và xếp hạng cổ phiếu theo xác suất tăng.

Các mô hình dạng bảng như Logistic Regression, Random Forest, XGBoost và LightGBM phù hợp với dữ liệu kỹ thuật có nhiều đặc trưng phi tuyến và số lượng mẫu vừa phải. Với dữ liệu tài chính theo thời gian, đánh giá phải dùng temporal split hoặc walk-forward, không shuffle ngẫu nhiên, để tránh look-ahead bias.

## 2.2. Đặc trưng kỹ thuật

Đặc trưng kỹ thuật phản ánh hành vi giá và thanh khoản đã quan sát. Các nhóm đặc trưng gồm:

- lợi suất và động lượng;
- biến động;
- thanh khoản;
- xu hướng so với đường trung bình;
- RSI, MACD, Bollinger Bands;
- lagged returns.

Trong hệ thống đề xuất, đặc trưng kỹ thuật không tự tạo quyết định đầu tư. Chúng tạo **tín hiệu định lượng** để chọn ứng viên, sau đó decision-support layer bổ sung giải thích và bằng chứng.

## 2.3. Tin tức tài chính và text features

Tin tức tài chính có thể chứa thông tin về kết quả kinh doanh, cổ tức, rủi ro nợ, pháp lý, quản trị, dự án và điều kiện ngành. Các nghiên cứu trước thường biến tin tức thành:

- Bag-of-Words;
- TF-IDF;
- keyword counts;
- sentiment score;
- event labels;
- embeddings.

Tuy nhiên, keyword/frequency thường thiếu ngữ cảnh. Ví dụ, từ “nợ xấu” có thể là rủi ro mới, cũng có thể là thông tin đã xử lý; “chia cổ tức” có thể tích cực hoặc trung tính tùy kỳ vọng thị trường. Vì vậy, semantic/event extraction có cơ sở học thuật tốt hơn keyword counts.

Ding et al. (2015) cho thấy event-driven features từ financial news có thể vượt bag-of-words trong dự báo stock movement. FinBERT (Araci, 2019) cũng cho thấy financial language cần domain adaptation.

## 2.4. LLM trong tài chính

LLM có khả năng tổng hợp thông tin, trích xuất luận điểm và viết giải thích bằng ngôn ngữ tự nhiên. Trong tài chính, LLM có thể hỗ trợ:

- tóm tắt tin tức;
- phân loại sentiment/materiality;
- giải thích tín hiệu;
- tạo investment memo;
- tạo risk checklist;
- hỗ trợ analyst workflow.

Tuy nhiên, LLM có rủi ro:

- hallucination;
- diễn giải quá mức;
- prompt sensitivity;
- provider/model drift;
- contamination nếu evidence input bẩn;
- self-evaluation bias nếu LLM vừa sinh vừa chấm.

Vì vậy, luận văn dùng LLM theo hướng evidence-grounded generation: LLM chỉ được dùng evidence pack, output theo schema, phải cite evidence, không dự báo giá trực tiếp.

## 2.5. Explainable AI và SHAP

SHAP giúp giải thích đóng góp của từng đặc trưng vào dự báo của mô hình. Trong hệ thống này, SHAP/feature importance đóng vai trò cầu nối giữa mô hình định lượng và LLM decision card. Thay vì chỉ nói “mã được chọn vì probability cao”, decision card có thể nói rõ những driver như RSI, MACD, price_vs_sma20 hoặc return momentum.

## 2.6. Decision support system

Hệ thống hỗ trợ quyết định không thay thế người ra quyết định. Trong bối cảnh đầu tư, hệ thống có nhiệm vụ:

- tổ chức thông tin;
- giải thích tín hiệu;
- nêu rủi ro;
- đặt trigger theo dõi;
- tạo audit trail;
- hậu kiểm sau quyết định.

Luận văn tổ chức quy trình theo năm bước:

1. **Select** — ML chọn ứng viên.
2. **Explain** — evidence pack và LLM tạo luận điểm.
3. **Monitor** — theo dõi tín hiệu và bối cảnh.
4. **Update** — cập nhật luận điểm nếu có thông tin mới.
5. **Review** — hậu kiểm sau holding period.

## 2.7. Rủi ro phương pháp trong nghiên cứu tài chính

Các rủi ro chính:

- look-ahead leakage;
- content-level leakage từ news crawler;
- survivorship bias;
- multiple testing;
- backtest overfitting;
- non-independent observations;
- slippage/liquidity/market impact;
- overclaim từ p-value đơn lẻ.

Luận văn cần thừa nhận và kiểm soát các rủi ro này trong phần phương pháp và limitations.

---

# CHƯƠNG 3. DỮ LIỆU VÀ PHƯƠNG PHÁP

## 3.1. Tổng quan hệ thống

Hệ thống gồm năm lớp:

1. ML Signal Engine.
2. News Evidence Layer.
3. Evidence Pack Builder.
4. LLM Decision Card Generator.
5. Monitoring & Outcome Review.

Sơ đồ:

```text
OHLCV ──> Technical Features ──> ML Signal Engine ──> Top-K Candidates
                                                        │
News ──> Matching/Enrichment ──> News Evidence ─────────┤
                                                        ▼
                                                Evidence Pack
                                                        ▼
                                    Rule-based / LLM Decision Card
                                                        ▼
                                         Monitoring + Outcome Review
```

## 3.2. Dữ liệu giá và universe cổ phiếu

Dữ liệu giá gồm OHLCV ngày của cổ phiếu Việt Nam. Universe chính là HOSE-80; robustness dùng 125 mã HOSE+HNX. Mỗi mẫu cuối cùng tương ứng với cặp `(ticker, period)`. Label phản ánh xu hướng tăng/không tăng của kỳ tiếp theo.

## 3.3. Technical feature engineering

Từ OHLCV, hệ thống tạo các nhóm đặc trưng:

| Nhóm | Ví dụ |
|---|---|
| Return/momentum | return_q, return_prev_q, return_2q_ago |
| Volatility | return_std_daily, volatility_q, price_range_q |
| Liquidity | volume_mean_q, volume_change_q |
| Trend | sma20_end, ema20_end, price_vs_sma20 |
| Indicators | rsi_mean_q, rsi_end_q, macd_hist_mean_q, bb_position_q |

Feature tại kỳ hiện tại được dùng dự báo kỳ tiếp theo. Imputer/scaler chỉ fit trên train.

## 3.4. ML Signal Engine

ML Signal Engine huấn luyện các mô hình:

- Logistic Regression;
- Random Forest;
- XGBoost;
- LightGBM.

Đầu ra gồm:

- `pred_proba_up`;
- `pred_label`;
- rank;
- Top-K candidates;
- feature importance/SHAP drivers.

Metrics:

- Balanced Accuracy;
- AUC-ROC;
- F1 Macro;
- Precision/Recall.

## 3.5. Backtest long-only

Backtest mô phỏng chiến lược long-only:

- chọn Top-K hoặc mã có `pred_label=1`;
- phân bổ đều;
- có transaction cost;
- so sánh buy-hold/equal-weight/VNINDEX.

Chỉ số:

- cumulative return;
- mean period return;
- Sharpe ratio;
- max drawdown;
- hit rate.

Giới hạn: chưa mô phỏng đầy đủ daily execution, slippage, liquidity, T+2, market impact.

## 3.6. News-as-predictor experiments

Các cấu hình:

- Config_A: technical-only.
- Config_B: news/keyword-only.
- Config_C: technical + news/keyword.

Mục tiêu là kiểm tra liệu tin tức khi biến thành feature trực tiếp có cải thiện forecast không. Kết quả này dùng để quyết định vai trò của news trong hệ thống.

## 3.7. LLM semantic features exploratory

LLM semantic features gồm event/materiality/relevance/sentiment. Tuy nhiên, vì chưa có gold human labels đầy đủ và kết quả sweep mixed, phần này chỉ được trình bày như exploratory evidence. Không dùng làm claim chính.

## 3.8. Evidence Pack Builder

Evidence pack là input point-in-time cho decision card. Mỗi pack gồm:

- decision_id;
- ticker;
- decision_date;
- period_id;
- holding horizon;
- ML signal;
- technical snapshot;
- top drivers;
- news evidence;
- data quality flags;
- guardrails.

Evidence pack ban đầu không chứa outcome/realized return. Outcome chỉ dùng trong outcome review sau holding period.

## 3.9. LLM Decision Card Generator

Decision card gồm:

1. signal summary;
2. investment thesis;
3. supporting factors;
4. risks/caveats;
5. monitoring triggers;
6. review date;
7. conclusion;
8. disclaimer.

Prompt yêu cầu:

- chỉ dùng evidence pack;
- không thêm dữ kiện ngoài input;
- cite evidence IDs;
- không dự báo giá tuyệt đối;
- không dùng ngôn ngữ khuyến nghị chắc chắn;
- nếu evidence thiếu phải nêu rõ.

## 3.10. Monitoring và Outcome Review

Monitoring triggers gồm:

- probability giảm;
- rank rơi khỏi Top-K;
- label đổi;
- RSI/MACD/price_vs_sma20 yếu đi;
- drawdown vượt ngưỡng;
- tin mới tiêu cực hoặc trái thesis;
- hết holding period.

Outcome review sau holding period ghi:

- realized return;
- benchmark return;
- excess return;
- thesis đúng/sai;
- monitoring events;
- bài học.

## 3.11. Đánh giá decision cards

Rubric 1–5 điểm:

| Tiêu chí | Ý nghĩa |
|---|---|
| Faithfulness | Bám sát evidence pack |
| Hallucination control | Không thêm dữ kiện ngoài input |
| ML explanation | Giải thích ML signal/drivers |
| Risk awareness | Nêu rủi ro cụ thể |
| Monitoring usefulness | Trigger rõ và đo được |
| Clarity/usefulness | Rõ ràng, dễ hậu kiểm |

So sánh:

1. rule-based baseline;
2. LLM ML-only;
3. LLM full-evidence.

---

# CHƯƠNG 4. KẾT QUẢ VÀ THẢO LUẬN

## 4.1. Kết quả ML technical baseline

Kết quả cho thấy technical ML là lõi định lượng mạnh nhất. Trên robustness 125 mã HOSE+HNX:

| Mô hình | Balanced Acc | AUC-ROC | F1 Macro | n_train | n_test |
|---|---:|---:|---:|---:|---:|
| Baseline Majority | 0.5000 | 0.5000 | 0.2973 | 1,653 | 735 |
| Baseline Stratified | 0.5223 | 0.5223 | 0.5186 | 1,653 | 735 |
| Logistic Regression | 0.6488 | 0.7036 | 0.6438 | 1,653 | 735 |
| Random Forest | **0.7607** | **0.8307** | **0.7573** | 1,653 | 735 |
| XGBoost | 0.7531 | 0.8265 | 0.7502 | 1,653 | 735 |
| LightGBM | 0.7530 | 0.8198 | 0.7509 | 1,653 | 735 |

Kết quả này cho thấy mô hình kỹ thuật vượt rõ baseline đa số/ngẫu nhiên và duy trì hiệu quả khi mở rộng universe.

## 4.2. Backtest và walk-forward

Backtest long-only theo kỳ:

| strategy | cost_scenario | cumulative_return | mean_period_return | sharpe_ratio | max_drawdown | hit_rate |
|---|---|---:|---:|---:|---:|---:|
| model | net | **0.602964** | **0.102254** | **1.05171** | -0.001035 | 0.8 |
| buy_hold_equal | net | 0.253502 | 0.050748 | 0.446062 | -0.020034 | 0.6 |

Walk-forward:

| cutoff | n_test | Balanced Accuracy | AUC-ROC | Model net return | Buy-hold return |
|---|---:|---:|---:|---:|---:|
| 2024Q3 | 556 | 0.722948 | 0.796966 | 0.656316 | 0.281762 |
| 2025Q1 | 400 | 0.759900 | 0.823509 | 0.602964 | 0.253502 |
| 2025Q3 | 240 | 0.639988 | 0.709755 | 0.118227 | 0.007196 |

Mô hình vượt benchmark 3/3 cutoff. Tuy nhiên, kết quả này chỉ chứng minh tín hiệu có giá trị trong historical simulation, chưa chứng minh chiến lược triển khai thật.

## 4.3. Leakage audit

Leakage audit kết luận PASS. Các cột nhãn và return tương lai như `return`, `next_quarter_id`, `next_avg_close`, `label_basic`, `label_threshold` không xuất hiện trong feature set. Scaler/imputer fit trên train. Decision card ban đầu không chứa realized return hay outcome review.

Cần lưu ý thêm: row-level leakage đã được kiểm soát, nhưng content-level leakage trong news vẫn cần audit kỹ nếu dùng card làm case study.

## 4.4. Negative result của news-as-predictor

Sau khi mở rộng full-text coverage, Config_C technical + keyword vẫn không vượt Config_A technical-only.

| Mô hình | Config_A kỹ thuật | Config_B từ khóa | Config_C kết hợp | C - A |
|---|---:|---:|---:|---:|
| LightGBM | 0.7599 | 0.4510 | 0.7357 | -0.0242 |
| Logistic Regression | 0.7269 | 0.4999 | 0.7132 | -0.0138 |
| Random Forest | 0.7351 | 0.5053 | 0.6679 | -0.0672 |
| XGBoost | 0.7293 | 0.4792 | 0.7238 | -0.0055 |

H2 keyword significance cũng không được ủng hộ: 0 keyword significant sau BH-FDR. LLM sentiment A6 có mean Δ(C−A) khoảng -0.0061, p khoảng 0.6177. Distant supervision B1 có Δ khoảng +0.0027, p khoảng 0.5601.

Kết quả này là negative finding quan trọng: news dạng keyword/frequency/sentiment không cải thiện forecast ổn định trong setting hiện tại. Vì vậy, news được chuyển sang evidence layer.

## 4.5. LLM semantic features: exploratory evidence

Các báo cáo LLM semantic cho thấy một số cấu hình material-event có delta dương khoảng +0.02 đến +0.04 BA và p-value nhỏ. Tuy nhiên, kết quả không ổn định qua horizon, universe, event filter và model. Một số sweep có mean effect gần 0 hoặc có cả negative significant results.

Do đó, luận văn không claim LLM semantic features tạo alpha phổ quát. Kết luận an toàn là:

> LLM semantic features có thể chứa tín hiệu bổ sung trong một số cấu hình được kiểm soát, nhưng hiện tại phù hợp hơn như hướng mở rộng/evidence enrichment hơn là main predictive source.

## 4.6. Evidence packs và generated artifacts

Hệ thống đã sinh:

| Artifact | Số lượng |
|---|---:|
| Evidence packs | 25 |
| Prompt-safe full-evidence packs | 25 |
| ML-only packs | 25 |
| Periods | 2025Q1–2026Q1 |
| Top-K per period | 5 |
| Positive realized returns | 19 |
| Negative/neutral realized returns | 6 |
| Monitoring news events | 3,838 |
| Live Gemini LLM cards | 50 |
| Live Gemini rubric scores | 75 |

Các prompt-safe packs đã strip outcome/realized return. Audit packs có outcome chỉ được dùng cho outcome review.

## 4.7. LLM decision-card rubric results

Rubric scoring hoàn tất cho 75 cards:

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LLM full-evidence | 25 | 5.00 | 5.00 | 5.00 | 4.96 | 5.00 | 5.00 | 5.00 | 0 | 0 |
| LLM ML-only | 25 | 1.28 | 1.00 | 4.72 | 2.04 | 4.56 | 2.12 | 1.16 | 43 | 114 |
| Rule-based baseline | 25 | 4.56 | 4.88 | 4.60 | 4.56 | 5.00 | 4.12 | 4.32 | 2 | 15 |

Diễn giải:

- Full-evidence LLM cards đạt điểm cao nhất vì có đủ ML/technical/news/risk/data-quality evidence.
- ML-only cards vẫn giải thích ML khá tốt, nhưng thiếu news/risk evidence nên bị chấm thấp ở faithfulness/risk/reference.
- Rule-based baseline an toàn và hữu ích, nhưng kém rõ và kém hoàn chỉnh hơn full-evidence LLM cards.
- Kết quả này đo **decision-card quality**, không đo return, không chứng minh LLM tạo alpha.

## 4.8. Monitoring và outcome review

Monitoring events giúp hệ thống không dừng ở thời điểm tạo card. Trigger gồm probability/rank/label change, technical deterioration, drawdown, news risk và end-of-horizon. Outcome review ghi realized return và phân tích thesis sau holding period.

Case studies nên chọn thủ công từ 25 records, ưu tiên card sạch, evidence rõ, tránh card có ticker mismatch hoặc boilerplate. Gợi ý:

1. ML đúng và evidence hỗ trợ.
2. ML sai nhưng monitoring cảnh báo.
3. ML đúng nhưng news trái chiều.
4. Evidence yếu và data quality warning.
5. Full-evidence LLM card tốt hơn ML-only card.

## 4.9. Thảo luận tổng hợp

Kết quả tổng hợp ủng hộ hướng **ML-led decision support**:

- ML kỹ thuật tạo signal định lượng tốt.
- News-as-predictor không cải thiện forecast ổn định.
- LLM semantic predictive features chỉ nên xem là exploratory.
- News phù hợp hơn như evidence/risk/monitoring layer.
- LLM có giá trị khi tạo decision card có kiểm soát từ evidence pack.

Điểm quan trọng là không overclaim. Luận văn không nói LLM dự báo cổ phiếu tốt hơn. Luận văn nói LLM giúp chuyển evidence thành decision record có thể đọc, theo dõi và hậu kiểm.

---

# CHƯƠNG 5. KẾT LUẬN, HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

## 5.1. Trả lời câu hỏi nghiên cứu

**RQ1.** Technical ML có tạo tín hiệu hữu ích không?  
Có, trong phạm vi dữ liệu và mô phỏng. Mô hình đạt BA khoảng 0.76, AUC khoảng 0.83 và vượt baseline.

**RQ2.** Top-K long-only có vượt benchmark không?  
Có trong backtest hiện tại: net cumulative return khoảng 60.3% so với benchmark 25.4%, walk-forward thắng 3/3 cutoff. Tuy nhiên, không claim triển khai thật vì backtest còn đơn giản.

**RQ3.** News features có cải thiện forecast không?  
Keyword/frequency/sentiment không cải thiện ổn định. LLM semantic có tín hiệu cục bộ nhưng mixed, chưa đủ làm main predictive claim.

**RQ4.** News có thể làm evidence layer không?  
Có. News hữu ích để giải thích bối cảnh, nêu rủi ro, tạo monitoring triggers và outcome review, nếu kiểm soát point-in-time và data quality.

**RQ5.** LLM full-evidence card có tốt hơn baseline không?  
Có theo rubric decision-card quality: full-evidence LLM đạt overall 5.00, rule-based baseline 4.32, ML-only 1.16. Kết quả này không đo return.

## 5.2. Đóng góp chính

1. Đề xuất hệ thống hỗ trợ quyết định đầu tư theo vòng đời `select → explain → monitor → update → review`.
2. Chứng minh technical ML là lõi định lượng phù hợp trong dữ liệu nghiên cứu.
3. Báo cáo negative finding robust: keyword/news features không cải thiện forecast ổn định.
4. Tái định vị news thành evidence layer.
5. Thiết kế evidence pack point-in-time và decision card có guardrails.
6. Đánh giá LLM full-evidence cards bằng rubric chất lượng hỗ trợ quyết định.
7. Tạo monitoring events và outcome reviews để hậu kiểm.

## 5.3. Hạn chế

1. Hệ thống là prototype, chưa phải production investment system.
2. Backtest theo kỳ, chưa daily mark-to-market đầy đủ.
3. Chưa mô phỏng đầy đủ slippage, liquidity, market impact, T+2, limit up/down.
4. Up/down label không phản ánh magnitude/risk đầy đủ.
5. LLM semantic labels chưa có human gold set đủ lớn.
6. Rubric scoring có thể chịu bias nếu dùng LLM judge.
7. News matching/extraction có thể chứa boilerplate, ticker mismatch hoặc content-level leakage.
8. Kết quả phụ thuộc giai đoạn 2022–2026 và universe chọn lọc.

## 5.4. Threats to Validity

### Internal validity

- Look-ahead leakage trong ML features.
- Outcome leakage trong LLM prompts.
- Content-level leakage từ news crawler.
- Crawler lấy sidebar/footer hoặc nội dung cập nhật sau decision date.

### Statistical validity

- Multiple testing trong LLM semantic sweeps.
- p-value đơn lẻ dễ false positive.
- Segment nhỏ thiếu power.
- `(ticker, period)` observations không hoàn toàn độc lập.
- Backtest overfitting.

### Construct validity

- Up/down label chưa đại diện đầy đủ cho quyết định đầu tư.
- Rubric score đo card quality, không đo lợi nhuận.
- Sentiment/materiality LLM không phải ground truth nếu thiếu human labels.

### External validity

- Giai đoạn 2022–2026 có thể không đại diện tương lai.
- Universe HOSE-80/125 mã có selection bias.
- Thị trường Việt Nam có ràng buộc thanh khoản, T+2, biên độ giá.
- News coverage không đều theo mã và nguồn.

## 5.5. Hướng phát triển

1. Tạo human-labeled Vietnamese financial news benchmark 100–300 bài cho event/materiality/relevance/sentiment.
2. So sánh LLM với TF-IDF, PhoBERT, XLM-R, FinBERT/multilingual financial sentiment baseline.
3. Kiểm tra prompt/provider stability trên cùng tập bài.
4. Xây event-time evidence graph thay vì gộp news theo quý.
5. Audit content-level leakage bằng scanner ngày tương lai, entity mismatch và boilerplate ratio.
6. Thêm random Top-K, momentum, RSI/MACD rule benchmark.
7. Chạy daily mark-to-market backtest có slippage/liquidity/T+2.
8. Thử paper-trading dashboard với human-in-the-loop.
9. Chấm decision cards bằng human evaluators độc lập.

## 5.6. Kết luận cuối

Luận văn cho thấy hướng dự báo cổ phiếu bằng news/LLM không nên được overclaim trong bối cảnh dữ liệu hiện có. Technical ML mới là lõi định lượng mạnh nhất; news features dạng thô không cải thiện forecast ổn định; LLM semantic features có tiềm năng nhưng chưa robust đủ để làm claim alpha.

Giá trị chính của luận văn nằm ở thiết kế hệ thống hỗ trợ quyết định đầu tư có kiểm soát: ML tạo tín hiệu, tin tức cung cấp bằng chứng, LLM tạo decision card có guardrails, monitoring theo dõi thay đổi và outcome review giúp hậu kiểm. Đây là hướng có ý nghĩa học thuật và thực tiễn, đồng thời có khả năng bảo vệ cao vì trung thực với kết quả thực nghiệm và tránh overclaim.

---

# TÀI LIỆU THAM KHẢO GỢI Ý

1. Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical evidence. *Journal of Finance*.
2. Breiman, L. (2001). Random Forests. *Machine Learning*.
3. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *KDD*.
4. Ke, G. et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. *NeurIPS*.
5. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *NeurIPS*.
6. Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*.
7. Schumaker, R. P., & Chen, H. (2009). Textual analysis of stock market prediction using breaking financial news. *ACM TOIS*.
8. Ding, X., Zhang, Y., Liu, T., & Duan, J. (2015). Deep Learning for Event-Driven Stock Prediction. *IJCAI*. https://www.ijcai.org/Abstract/15/329
9. Xu, Y., & Cohen, S. B. (2018). Stock Movement Prediction from Tweets and Historical Prices. *ACL*. https://aclanthology.org/P18-1183/
10. Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. https://arxiv.org/abs/1908.10063
11. Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT Forecast Stock Price Movements? https://arxiv.org/abs/2304.07619
12. Yang, H. et al. (2023). FinGPT: Open-Source Financial Large Language Models. https://arxiv.org/abs/2306.06031
13. Le Hong Hanh et al. (2022). Stock Market Prediction: The Application of Text-Mining in Vietnam. *VNU Journal of Economics and Business*. https://js.vnu.edu.vn/EAB/article/view/4715
14. White, H. (2000). A Reality Check for Data Snooping. *Econometrica*.
15. Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2014). The Probability of Backtest Overfitting.

---

# PHỤ LỤC GỢI Ý

## Phụ lục A. Danh sách artifact

- `reports/decision_support/generated/evidence_packs_initial.json`
- `reports/decision_support/generated/evidence_packs_ml_only.json`
- `reports/decision_support/generated/decision_cards.md`
- `reports/decision_support/generated/llm_cards_ml_only.md`
- `reports/decision_support/generated/llm_cards_full_evidence.md`
- `reports/decision_support/generated/llm_rubric_scores.csv`
- `reports/decision_support/generated/llm_rubric_summary.md`
- `reports/decision_support/generated/outcome_reviews.md`
- `reports/decision_support/generated/monitoring_events.csv`

## Phụ lục B. Claim / Evidence / Limitation

| Claim | Evidence | Limitation |
|---|---|---|
| Technical ML có signal | BA ~0.76, AUC ~0.83, backtest tốt | Backtest đơn giản, cần liquidity/slippage |
| Keyword/news thô không cải thiện forecast | Config_C không vượt Config_A, 0 keyword BH-FDR | Không chứng minh mọi news method đều vô dụng |
| LLM semantic có tiềm năng | Vài config material-event dương | Mixed, multiple testing, thiếu gold labels |
| Full-evidence LLM card tốt hơn baseline | Rubric 75 cards | Card quality, không phải return |
| Monitoring/outcome review hữu ích | 3,838 monitoring events, 25 reviews | Chưa chứng minh cải thiện portfolio |

## Phụ lục C. Non-claim checklist

- Không claim LLM tạo alpha.
- Không claim news cải thiện forecast ổn định.
- Không claim decision card là khuyến nghị đầu tư.
- Không claim backtest bảo đảm lợi nhuận tương lai.
- Không claim rubric score đo hiệu quả đầu tư.
