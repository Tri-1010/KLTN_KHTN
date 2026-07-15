# LUẬN VĂN HOÀN THIỆN

## Hệ thống hỗ trợ phân tích cổ phiếu Việt Nam dựa trên học máy, biểu diễn ngữ nghĩa tin tức và LLM có bằng chứng

**Tên tiếng Anh:** *An ML-Led Decision Support System for Vietnamese Stocks with Semantic News Materiality and Evidence-Grounded LLM Decision Cards*

**Học viên:** Ngô Minh Trí  
**Mã số học viên:** 24C01024  
**Ngành:** Khoa học Dữ liệu  
**Mã số ngành:** 8460108  
**Đơn vị:** Trường Đại học Khoa học Tự nhiên, Đại học Quốc gia Thành phố Hồ Chí Minh  
**Thời điểm dữ liệu và artifact:** đến ngày 15/07/2026  
**Trạng thái:** Bản Markdown canonical theo artifact hiện có. Cần dàn trang, kiểm tra trích dẫn và đối chiếu quy định đơn vị đào tạo trước khi nộp.

> **Quy ước tái lập.** Mỗi kết quả trong bản này chỉ áp dụng cho đúng artifact, thời gian, universe, target và protocol nêu tại bảng hoặc chú thích nguồn. Các track cũ dùng split/horizon khác không được gộp với track purged out-of-sample (OOS) semantic hiện hành.

> **Phạm vi diễn giải.** Đây là công trình nghiên cứu học thuật và prototype hỗ trợ phân tích. Không nội dung nào trong luận văn là lời khuyên đầu tư, cam kết lợi nhuận, bằng chứng về hiệu quả triển khai, hay bằng chứng về quan hệ nhân quả.

---

## LỜI CAM ĐOAN

Tôi cam đoan bản luận văn này trình bày đúng phạm vi dữ liệu, phương pháp và artifact thực nghiệm đã lưu trong repository của đề tài. Các nhãn ngữ nghĩa do mô hình tạo và hợp nhất được gọi là **pseudo-label**, không gọi là nhãn chuẩn của con người. Các kết quả event-window được diễn giải là liên hệ quan sát được, không diễn giải thành tác động nhân quả. Các kết quả backtest và Top-K được xem là mô phỏng thăm dò trong điều kiện giả định, không phải bảo đảm kết quả tương lai.

Tôi chịu trách nhiệm kiểm tra lại nguồn, phiên bản, hash, giả định và giới hạn của các bảng số liệu trước khi sử dụng bản thảo cho mục đích chính thức.

## LỜI CẢM ƠN

Tôi cảm ơn giảng viên hướng dẫn, các thầy cô và những người đã góp ý cho thiết kế dữ liệu, kiểm soát rò rỉ thông tin, đánh giá mô hình và cách diễn giải kết quả âm. Tôi cũng cảm ơn các công cụ nguồn mở và các nhà cung cấp mô hình đã hỗ trợ việc xây dựng prototype. Mọi lỗi còn lại trong bản thảo thuộc trách nhiệm của tác giả.

---

## TÓM TẮT

Luận văn xây dựng một framework hỗ trợ phân tích cổ phiếu Việt Nam theo hướng kết hợp tín hiệu học máy, dữ liệu giá, tin tức công khai, biểu diễn ngữ nghĩa của tin tức và mô hình ngôn ngữ lớn (Large Language Model — LLM). Trọng tâm không phải tạo tín hiệu giao dịch tự động, mà là tạo một **decision record** có thể truy vết qua chuỗi `select → explain → monitor → update → review`.

Phần thực nghiệm gồm hai lớp. Lớp thứ nhất là ML và ranking với kiểm định theo thời gian. Artifact canonical hiện có 685.704 dự đoán, ba expanding walk-forward folds, purge 20 phiên giao dịch và bốn cấu hình: `A_technical`, `B_technical_keyword`, `C_technical_semantic`, `D_all`. Trong đánh giá purged out-of-sample mới nhất, Balanced Accuracy trung bình của `D_all`–Random Forest là 0,5105 và AUC là 0,5116; các mức này gần ngẫu nhiên. Vì vậy, luận văn không dùng artifact này để tuyên bố mô hình tạo lợi thế giao dịch ổn định. Các mô phỏng Top-K có kết quả khác nhau theo cấu hình, K, chi phí và null ngẫu nhiên; chúng chỉ là kết quả exploratory.

Lớp thứ hai là semantic news materiality. Ba lần annotation offline tạo 150 hàng, 122 hàng đủ điều kiện phân tích, 106 hàng majority vote, 40 hàng unanimous và 4 hàng disagreement. Tỷ lệ thiếu evidence span là 8,67%. So với pseudo-label ngữ nghĩa, rule baseline đạt accuracy 0,3770 cho direction, 0,1475 cho event type, 0,2213 cho materiality và 0,6885 cho ticker relevance. Kết quả cho thấy đếm từ khóa thiếu ngữ cảnh và không đại diện đầy đủ cho relevance, materiality, event type hoặc direction. Tuy nhiên, pseudo-label vẫn không phải ground truth.

Event-window gồm tám kiểm định trên lợi suất đã điều chỉnh VNINDEX tại T+1, T+5, T+20 và T+60. Sau Benjamini–Hochberg, chỉ một kiểm định có khoảng tin cậy dương nghiêm ngặt và đạt gate `p_value_bh <= 0,05 AND diff_ci_low > 0`: nhóm materiality cao/trung bình so với thấp tại T+5, chênh lệch trung bình 0,0223, p-value BH 0,0457, Cliff’s delta 0,3085 và khoảng tin cậy chênh lệch [0,0091; 0,0366]. Đây là bằng chứng exploratory cho liên hệ dương trong một cửa sổ, không phải bằng chứng tổng quát hay nhân quả.

Phần decision-support tạo 25 evidence packs, 25 rule-based cards, 25 LLM ML-only cards và 25 LLM full-evidence cards. Gemini `gemini-2.5-pro` tạo và tự chấm 75 card: full-evidence overall 5,00, rule baseline 4,32, ML-only 1,16. Run local-router độc lập tạo 75 card và 75 rubric scores: full-evidence 3,96, rule baseline 3,00, ML-only 2,32; response model là `gpt-5.6-luna` thuộc OpenAI-vendor, không phải Claude native. Common local judge chấm chéo 75 Gemini cards cho overall lần lượt 3,44, 2,96 và 2,32 đối với full-evidence, rule baseline và ML-only. Vì judge và điều kiện run khác nhau, thesis chỉ dùng so sánh **trong cùng run**; không xếp hạng tuyệt đối provider. Điểm rubric đo chất lượng card, không đo lợi nhuận.

Đóng góp chính là một pipeline có provenance và guardrail: dữ liệu ban đầu được cắt point-in-time, outcome tương lai bị loại khỏi initial prompt, mỗi luận điểm cần evidence reference, monitoring tách khỏi outcome review, và mọi kết luận được gắn mức độ hỗ trợ. Hạn chế lớn gồm pseudo-label, sample size, model error tương quan, matching ticker, possible content contamination, event confounding, giả định backtest, automated self-judge và thiếu bộ nhãn chuyên gia độc lập.

**Từ khóa:** học máy; cổ phiếu Việt Nam; hỗ trợ quyết định; semantic news materiality; evidence pack; LLM; decision card; monitoring; outcome review.

---

## ABSTRACT

This thesis develops an academic stock-analysis and decision-support framework for Vietnamese stocks by combining machine-learning signals, price data, public financial news, semantic news-materiality labels, and Large Language Models (LLMs). The objective is not to produce an autonomous trading signal, but to create an auditable decision record following `select → explain → monitor → update → review`.

The first experimental layer evaluates ML and ranking under temporal validation. The current canonical artifact contains 685,704 predictions, three expanding walk-forward folds, a 20-trading-day purge, and four configurations: `A_technical`, `B_technical_keyword`, `C_technical_semantic`, and `D_all`. Under the latest purged out-of-sample evaluation, `D_all` with Random Forest has mean Balanced Accuracy 0.5105 and mean AUC 0.5116, both close to random performance. The thesis therefore does not claim stable trading advantage. Top-K simulations vary by configuration, K, transaction cost, and random null; they are exploratory only.

The semantic-news layer contains 150 annotated rows, 122 analysis-eligible rows, 106 majority-vote rows, 40 unanimous rows, and four disagreement rows across three offline annotation runs. Missing evidence-span rate is 8.67%. Against semantic pseudo-labels, the rule baseline obtains accuracy 0.3770 for direction, 0.1475 for event type, 0.2213 for materiality, and 0.6885 for ticker relevance. These results show limitations of keyword counting, but pseudo-labels are not human ground truth.

Eight event-window tests compare VNINDEX-adjusted returns at T+1, T+5, T+20, and T+60. After Benjamini–Hochberg correction, one test passes the strict positive gate. This is exploratory association, not a causal result. For decision cards, 25 evidence packs, 25 rule-based cards, 25 ML-only LLM cards, and 25 full-evidence LLM cards were generated. Gemini `gemini-2.5-pro` scored 75 cards with overall means of 5.00, 4.32, and 1.16 for full-evidence, rule-based, and ML-only cards. A separate local-router run produced 3.96, 3.00, and 2.32. A subsequent common local-judge cross-score of the Gemini cards produced 3.44, 2.96, and 2.32 for full-evidence, ML-only, and rule-based cards, respectively. Because judge and run conditions differ, only within-run ordering is reported.

The main contribution is a provenance-aware and guarded pipeline: point-in-time inputs, recursive removal of future outcomes from initial prompts, evidence references for major claims, separate monitoring and outcome-review records, and explicit claim-strength labels. Limitations include pseudo-labels, sample size, correlated model errors, ticker matching, possible content contamination, event confounding, backtest assumptions, automated self-judging, and the absence of independent expert labels.

**Keywords:** machine learning; Vietnamese stocks; decision support; semantic news materiality; evidence pack; LLM; decision card; monitoring; outcome review.

---

## DANH MỤC VIẾT TẮT

| Viết tắt | Diễn giải |
|---|---|
| AUC | Area Under the ROC Curve |
| BA | Balanced Accuracy |
| BH-FDR | Benjamini–Hochberg False Discovery Rate |
| LLM | Large Language Model |
| ML | Machine Learning |
| OOS | Out-of-sample |
| OHLCV | Open, High, Low, Close, Volume |
| RQ | Research Question |
| SHAP | SHapley Additive exPlanations |
| T+1/T+5/T+20/T+60 | Cửa sổ sau sự kiện theo số phiên giao dịch |
| Top-K | K cổ phiếu xếp hạng cao nhất |
| VNINDEX | Chỉ số thị trường Việt Nam dùng để điều chỉnh lợi suất |

## DANH MỤC BẢNG

1. Claim–evidence matrix.
2. Quy mô các artifact canonical.
3. Kết quả annotation agreement.
4. So sánh rule baseline và semantic pseudo-label.
5. Kết quả event-window.
6. Kết quả purged walk-forward.
7. Kết quả Top-K và null.
8. Kết quả rubric Gemini.
9. Kết quả rubric local router.
10. Ma trận provider/model/provenance.

## DANH MỤC HÌNH

1. Kiến trúc pipeline tổng thể.
2. Tách initial evidence pack và outcome audit pack.
3. Vòng đời decision record.
4. Dòng provenance từ nguồn dữ liệu đến card và review.

---

# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh

Thị trường chứng khoán Việt Nam tạo ra đồng thời dữ liệu giao dịch có cấu trúc và lượng lớn tin tức tiếng Việt. Giá, khối lượng, lợi suất và chỉ báo kỹ thuật thuận tiện cho mô hình bảng. Tin tức chứa thông tin về kết quả kinh doanh, nợ, vốn, quản trị, pháp lý, dự án và diễn biến ngành, nhưng thường không có schema nhất quán. Một hệ thống hỗ trợ quyết định phải xử lý cả hai loại dữ liệu mà không biến bất kỳ nguồn nào thành bằng chứng chắc chắn vượt quá dữ liệu.

Nhiều pipeline dừng ở xác suất tăng, nhãn nhị phân hoặc thứ hạng. Đầu ra đó chưa trả lời được các câu hỏi vận hành: mô hình dựa vào driver nào, evidence nào ủng hộ hoặc phản biện, rủi ro nào cần theo dõi, khi nào phải review, và sau kỳ nắm giữ thì luận điểm ban đầu được hỗ trợ đến mức nào. Luận văn chuyển trọng tâm từ một dự đoán đơn lẻ sang quản trị một **decision record**.

## 1.2. Vấn đề nghiên cứu

Biểu diễn tin tức bằng số lượng bài, từ khóa hoặc sentiment thường bỏ qua:

- ticker có thực sự là chủ thể của tin hay chỉ được nhắc qua;
- materiality của sự kiện đối với doanh nghiệp;
- event type và thời hạn tác động;
- direction có thể là mixed hoặc neutral;
- evidence span cụ thể để kiểm tra lại.

Ngược lại, semantic extraction bằng LLM có thể tạo schema giàu hơn nhưng phát sinh pseudo-label, phụ thuộc provider, prompt sensitivity và hallucination. Vì thiếu bộ nhãn chuyên gia đủ lớn, semantic layer phải được dùng như lớp mô tả và audit, không dùng như nhãn chuẩn tuyệt đối.

Vấn đề của luận văn gồm bảy phần: kiểm tra tín hiệu ML purged OOS; báo cáo kết quả âm của keyword features; đo sai lệch rule representation; khảo sát semantic schema/agreement; kiểm định event-window; đánh giá quality của evidence-grounded LLM card; và thiết kế traceability cho monitoring/outcome review/UI.

## 1.3. Mục tiêu

### Mục tiêu tổng quát

Xây dựng và đánh giá prototype hỗ trợ phân tích cổ phiếu Việt Nam, trong đó ML tạo tín hiệu định lượng cần kiểm tra, semantic news tạo lớp evidence có cấu trúc, LLM tạo decision card có guardrail, và monitoring/outcome review tạo audit trail.

### Mục tiêu cụ thể

1. Xây dựng temporal ML benchmark với feature kỹ thuật, keyword và semantic.
2. Kiểm soát leakage bằng point-in-time cutoff, expanding folds, purge và physical data zones.
3. Định lượng giới hạn của keyword/news-count representation và rule baseline.
4. Thiết kế semantic schema gồm relevance, materiality, direction, event type, time horizon và evidence span; ghi rõ provenance pseudo-label.
5. Đánh giá event-window bằng adjustment VNINDEX, BH-FDR và bootstrap CI.
6. Xây dựng initial evidence pack tách về vật lý và logic khỏi audit/review outcome.
7. So sánh rule baseline, LLM ML-only và LLM full-evidence bằng rubric card-quality theo từng judge condition.
8. Đánh giá monitoring, provenance, outcome review và EvidenceTrace UI ở mức traceability, không ở mức hiệu quả đầu tư.

## 1.4. Câu hỏi nghiên cứu

**RQ1.** Tín hiệu ML trong thiết lập temporal và purged OOS hiện tại có ổn định đủ để làm lõi định lượng cần kiểm tra không?

**RQ2.** Keyword/news-count representation có cải thiện dự báo so với technical-only trong setting đã chạy không?

**RQ3.** Semantic schema có giúp mô tả relevance, materiality, event type, direction và lỗi của rule baseline rõ hơn không?

**RQ4.** Các nhãn semantic có liên hệ quan sát được với lợi suất trong event-window nào không, và mức bằng chứng mạnh đến đâu sau hiệu chỉnh đa kiểm định?

**RQ5.** Top-K non-overlap có cho kết quả nhất quán qua cấu hình, cost và deterministic random null không?

**RQ6.** Evidence-grounded full-evidence LLM card có chất lượng rubric tốt hơn ML-only card và rule baseline trong từng automated judge condition không?

**RQ7.** Decision record và EvidenceTrace có tách được dữ liệu ban đầu, monitoring mới và outcome review để audit/tái lập không?

## 1.5. Phạm vi và không-claim

Phạm vi dữ liệu gồm giá, tin tức đã xử lý, annotation artifact, ML predictions, evidence packs, decision cards, monitoring events và outcome reviews được lưu trong repository. Universe, giai đoạn và coverage thay đổi theo artifact; do đó mỗi bảng phải ghi nguồn và không được gộp các kết quả khác setting thành một con số duy nhất.

Luận văn **không**:

- chứng minh mô hình có lợi thế giao dịch ổn định;
- chứng minh LLM tạo alpha hoặc cải thiện return;
- chứng minh event semantic gây ra biến động giá;
- xem pseudo-label là ground truth;
- xem rubric tự động là human expert evaluation;
- dùng decision card làm khuyến nghị đầu tư;
- đưa realized return tương lai vào initial prompt.

## 1.6. Đóng góp

1. Hợp nhất ML, semantic news và LLM trong một pipeline có provenance.
2. Báo cáo negative finding của keyword representation thay vì che giấu kết quả không đạt.
3. Dùng semantic schema để tạo error taxonomy và evidence layer, không overclaim predictive gain.
4. Thiết kế initial/outcome separation và recursive outcome stripping.
5. So sánh hai điều kiện LLM trên cùng decision records: ML-only và full-evidence.
6. Gắn mọi kết luận với artifact, mức claim và limitation.

## 1.7. Cấu trúc luận văn

Chương 1 giới thiệu vấn đề và câu hỏi nghiên cứu. Chương 2 trình bày cơ sở lý thuyết. Chương 3 mô tả dữ liệu, schema và phương pháp. Chương 4 báo cáo kết quả. Chương 5 thảo luận claim và threats to validity. Chương 6 kết luận và đề xuất hướng phát triển. Các phụ lục cung cấp schema, prompt, provenance, validation và disclaimer.

---

# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG TRÌNH LIÊN QUAN

## 2.1. ML trên dữ liệu chuỗi thời gian tài chính

Bài toán có thể là hồi quy lợi suất, phân loại tăng/không tăng hoặc xếp hạng. Với dữ liệu chuỗi thời gian, random split làm trộn quá khứ và tương lai. Temporal split, expanding walk-forward và purge giảm nguy cơ sử dụng thông tin thuộc horizon đang dự báo; chúng không tự loại survivorship, matching sai, drift hoặc content contamination (White, 2000).

Các mô hình bảng trong đề tài gồm Logistic Regression và Random Forest trong artifact purged OOS; XGBoost và LightGBM xuất hiện trong các thí nghiệm H1 theo quý. Majority và baseline đơn giản làm mức tham chiếu. BA được ưu tiên khi tỷ lệ lớp thay đổi; AUC đo khả năng xếp hạng xác suất, không đồng nghĩa return. Random Forest, XGBoost và LightGBM được dùng theo đặc tính mô hình bảng, không phải bằng chứng rằng một thuật toán tự tạo lợi thế thị trường (Breiman, 2001; Chen & Guestrin, 2016; Ke et al., 2017).

## 2.2. Technical indicators và explainability

Lợi suất trễ, động lượng, volatility, volume, SMA/EMA, RSI, MACD và Bollinger position là các biến mô tả hành vi giá đã quan sát. SHAP hoặc permutation importance hỗ trợ trả lời mô hình dựa vào biến nào (Lundberg & Lee, 2017). Cần phân biệt giải thích tương quan nội bộ của mô hình với diễn giải kinh tế nhân quả. Một feature có importance cao không chứng minh nó gây ra kết quả.

## 2.3. Financial news và keyword representation

Keyword counts và TF-IDF dễ tái lập nhưng thiếu ngữ cảnh. Cụm “lợi nhuận không tăng” có thể bị đếm như positive nếu chỉ tìm substring “tăng”. Tin market-wide có thể bị gán direct cho ticker. Một bài có nhiều từ khóa không nhất thiết material hơn bài ngắn có một thông tin pháp lý quan trọng. Các lỗi này tạo động lực cho semantic fields và evidence span; chúng phù hợp giới hạn chung đã được ghi nhận trong literature text-mining tài chính (Schumaker & Chen, 2009; Nassirtoussi et al., 2014).

Trong H1, pipeline đã thêm cụm phủ định, từ đồng nghĩa và longest-first masking. 540 test pass sau cải tiến. Tuy nhiên, kết quả full-text và nhiều lần mở rộng nguồn vẫn không cho thấy keyword feature cải thiện ổn định. Negative finding này không chứng minh mọi cách dùng news đều vô ích; nó giới hạn claim trong representation, corpus và task đang kiểm tra.

## 2.4. Semantic relevance và materiality

Semantic schema tách:

- `ticker_relevance`: direct, market-wide, irrelevant hoặc dạng tương đương;
- `materiality`: low, medium, high;
- `direction`: support, risk, neutral hoặc mixed;
- `event_type`: earnings, debt, governance, legal, capital, market và các loại khác;
- `time_horizon`: short, medium, long hoặc unclear;
- numeric scores về impact, uncertainty, novelty;
- `evidence_span` và reasoning confidence.

Ba annotation runs dùng hai model family: DeepSeek native cho runs A/B và OpenAI-vendor `gpt-5.4-mini` qua gateway/proxy cho run C. Provenance hiện là `legacy_reconstructed`; đây là limitation cần ghi rõ.

## 2.5. Weak supervision và pseudo-label

Consensus giữa nhiều output mô hình giúp tạo tập tham chiếu có cấu trúc. Tuy nhiên, agreement cao chỉ phản ánh các hệ thống có thể đồng thuận trên prompt và schema; không biến nhãn thành sự thật độc lập. Vì vậy, tất cả bảng semantic dùng cụm **semantic pseudo-label**. Manual sanity check 24 rows chỉ là pilot QC; không có reviewer provenance và không phải human gold set.

## 2.6. Event study exploratory

Event-window so sánh lợi suất điều chỉnh VNINDEX giữa nhóm semantic. Mann–Whitney tie-corrected, Benjamini–Hochberg false-discovery-rate (BH-FDR) và bootstrap CI được dùng để giảm diễn giải dựa trên p-value đơn lẻ (Benjamini & Hochberg, 1995; Efron & Tibshirani, 1993). Những thủ tục này chỉ kiểm soát một phần nguy cơ đa kiểm định và không thay thế thiết kế nhân quả hay pre-registration. Gate hỗ trợ positive exploratory claim là:

```text
p_value_bh <= 0.05 AND diff_ci_low > 0
```

Gate này không giải quyết confounding, event clustering, selection bias hoặc causal identification. Kết quả đạt gate chỉ được gọi là exploratory association.

## 2.7. LLM evidence grounding

LLM phù hợp cho extraction, summarization và tạo văn bản có cấu trúc, nhưng có các rủi ro hallucination, prompt sensitivity, provider/model drift, evidence contamination và self-judge bias. Vì vậy artifact rubric của luận văn được coi là automated internal evaluation, không phải expert gold-standard. Thiết kế evidence-grounded card dùng:

1. schema cố định;
2. evidence reference;
3. initial prompt không có outcome;
4. recursive stripping;
5. statement thiếu evidence phải ghi rõ;
6. disclaimer không phải investment advice;
7. tách card ban đầu khỏi outcome review.

## 2.8. Decision support và traceability

Decision-support system không thay thế người ra quyết định. Giá trị cần đo gồm khả năng tổ chức evidence, giải thích signal, nêu risk, đặt trigger, lưu lineage và review sau holding period. Một card đẹp nhưng không có reference hoặc chứa future contamination vẫn là artifact không đạt.

## 2.9. Khoảng trống nghiên cứu

Khoảng trống của đề tài không chỉ là “thử thêm model”. Cần nối ba vấn đề thường tách rời: (i) ML signal với temporal validation; (ii) semantic materiality với error taxonomy; (iii) LLM card với evidence lineage và outcome separation. Đề tài đóng góp một prototype nối các lớp này, đồng thời giữ negative findings và uncertainty trong narrative.

---

# CHƯƠNG 3. DỮ LIỆU VÀ PHƯƠNG PHÁP

## 3.1. Kiến trúc tổng thể

```text
OHLCV ──> Technical Features ──> Purged ML ──> Signal / Rank
                                      │
News ──> Dedup / Entity Match ──> Semantic Layer
                                      │
                                      ▼
                         Point-in-time Evidence Pack
                                      │
                         Rule Card / LLM Card Ablation
                                      │
                         Monitoring ──> Outcome Review
```

Năm lớp chính:

1. **Data layer:** giá, tin, metadata và hash.
2. **Signal layer:** technical, keyword, semantic configurations.
3. **Evidence layer:** schema, cutoff và quality flags.
4. **Generation layer:** rule baseline, ML-only, full-evidence.
5. **Governance layer:** monitoring, outcome review, claim matrix.

## 3.2. Dữ liệu giá và tin tức

Các artifact nguồn mô tả OHLCV và tin tức Việt Nam trong giai đoạn nghiên cứu. H1 report ghi 35.160 dòng giá và 10.050 bài đã gắn mã, 7.492 bài sau preprocessing ở một setting cũ. Sau các lần mở rộng, corpus đạt 28.062 bài unique từ sáu nguồn: Kinh Tế Chứng Khoán 8.513, CafeF 8.020, Vietstock 5.008, VietnamBiz 3.598, VnExpress 1.762 và TNCK 1.161. Các con số này chỉ mô tả corpus của H1 và không được gán trực tiếp cho mọi artifact semantic.

Semantic study có 150 rows annotation, 93.824 semantic daily rows, 456 event windows, 685.704 ML predictions, 2.592 Top-K rows và 114 outcome reviews. Decision-support generation dùng 25 decision packs trong các kỳ 2025Q1–2026Q1.

## 3.3. Preprocessing và entity matching

Pipeline thực hiện chuẩn hóa ngày, ticker, source, title, summary và nội dung; deduplicate URL/title; matching ticker; enrich full text khi có thể; tạo summary/key facts và quality flags. Các lỗi cần giữ lại để audit gồm ticker mismatch, boilerplate, chỉ có title, thiếu evidence span và coverage thấp. Không được xóa lỗi chỉ để tăng score.

## 3.4. Đơn vị quan sát, target và phạm vi tái lập

Track semantic canonical dùng quan sát point-in-time theo ngày/mã trong artifact dự báo OOS và `(ticker, period)` trong Top-K. Bốn cấu hình feature, cùng hai mô hình Logistic Regression và Random Forest, được đánh giá trong ba fold expanding. Target, universe chi tiết và cột feature được cố định trong artifact `outperform_ml_predictions_v2`; luận văn không suy rộng kết quả sang H1 quarterly legacy vì unit quan sát, horizon, feature schema và split khác nhau.

Decision-support dùng 25 record lịch sử Top-5 cho năm kỳ `2025Q1`–`2026Q1`. Mỗi record có `decision_id`, `decision_date`, `holding_horizon`, technical snapshot, driver và evidence trước cutoff. Review/outcome là record hậu kiểm riêng; không phải nhãn để huấn luyện, chọn record hoặc chấm card ban đầu.

## 3.5. Feature configurations

| Cấu hình | Thành phần | Vai trò |
|---|---|---|
| `A_technical` | Technical features | Baseline định lượng |
| `B_technical_keyword` | Technical + keyword | Kiểm tra incremental keyword |
| `C_technical_semantic` | Technical + semantic fields | Exploratory semantic feature |
| `D_all` | Tập feature kết hợp | Kiểm tra tổng hợp |

H1 report còn có Config B keyword-only và Config C technical + keyword trong split theo quý. Hai naming systems được giữ nguyên theo artifact; không gộp số liệu khác schema thành một bảng mới.

## 3.6. Temporal validation và leakage

Purged expanding walk-forward có ba folds:

| Fold | Train | Test | Purge |
|---:|---|---|---:|
| 1 | 2021-10-14 đến 2022-01-06 | 2022-02-11 đến 2023-07-14 | 20 phiên |
| 2 | 2021-10-14 đến 2023-06-16 | 2023-07-17 đến 2024-12-16 | 20 phiên |
| 3 | 2021-10-14 đến 2024-11-18 | 2024-12-17 đến 2026-06-01 | 20 phiên |

Imputer/scaler nếu dùng chỉ fit trên train. Feature không được chứa `return` tương lai, `next_quarter_id`, `next_avg_close`, `label_basic`, `label_threshold` hoặc outcome fields. Với news, điều kiện là `published_at <= decision_date`. Initial evidence pack phải loại recursive mọi trường `outcome_for_review_only`, realized return và future label.

## 3.7. H1 keyword experiment

H1 kiểm tra Config A kỹ thuật, Config B keyword và Config C kết hợp ở nhiều granularity. Sau full-text enrichment 99,96% URL unique có full text, kết quả production split theo quý:

| Mô hình | A kỹ thuật | B keyword | C kết hợp | C − A |
|---|---:|---:|---:|---:|
| LightGBM | 0,7599 | 0,4510 | 0,7357 | −0,0242 |
| Logistic Regression | 0,7269 | 0,4999 | 0,7132 | −0,0138 |
| Random Forest | 0,7351 | 0,5053 | 0,6679 | −0,0672 |
| XGBoost | 0,7293 | 0,4792 | 0,7238 | −0,0055 |

Các thử nghiệm theo tuần, hai tuần, tháng, hai tháng và quý cho delta trung bình C−A lần lượt −0,0068, −0,0071, −0,0032, −0,0112 và +0,0094 trong artifact full-text. Dấu dương ở quý nhỏ và không nhất quán theo model. Kiểm định H2 có 0/71 keyword qua BH-FDR trong report ML/LLM decision support. Kết luận phù hợp: H1 không được ủng hộ trong representation hiện tại.

## 3.8. Semantic annotation và consensus

Mỗi row được gửi qua ba annotation runs. Output JSON được validate theo schema. Consensus dùng majority vote và ghi disagreement, quality flags, evidence span, analysis eligibility. Không đưa realized return, outcome review hoặc future label vào prompt annotation.

Manual sanity check có 24 rows: relevance OK 23/24, materiality OK 21/24, direction OK 23/24, event type OK 24/24 và evidence span OK 23/24. Reviewer-backed rows là 0; do đó đây là pilot QC.

## 3.9. Event-window

Lợi suất được điều chỉnh theo VNINDEX. So sánh direction support/risk và materiality high+medium/low ở bốn horizon. Dùng Mann–Whitney tie-corrected, BH-FDR và deterministic bootstrap CI. Chỉ gọi kết quả positive khi qua gate nghiêm ngặt tại Mục 2.6.

## 3.10. Purged ML outperform

Artifact `ml_outperform_experiment_report.md` chứa 685.704 predictions. Metrics gồm BA, AUC, F1, precision@10 theo ngày và daily rank IC. Kết quả được tổng hợp theo fold và model; paired daily deltas và bootstrap deltas dùng như robustness readers. Không dùng realized portfolio outcome từ audit pack để sửa initial ML prompt.

## 3.11. Top-K và chi phí

Top-K simulation dùng 54 entry periods, K=5/10, holding 20 ngày, equal weight, non-overlap và round-trip cost 0,5%. Có model_topk, equal_weight_universe và random_topk_deterministic. Null gồm 200 deterministic draws cho từng config/model/K. Vì null là empirical hash draw chứ không phải các market realization độc lập, p-value chỉ có ý nghĩa mô tả trong simulation.

Với mỗi entry period, tỷ trọng bằng nhau trong nhóm Top-K. Turnover được dùng để scale chi phí round-trip, vì vậy lợi suất ròng là lợi suất gộp trừ `0,005 × turnover` trong setting chính. Benchmark `equal_weight_universe` và baseline `random_topk_deterministic` cùng dùng 54 period OOS không chồng lấn. Annualized Sharpe dùng factor 3,5496 theo tần suất 20 ngày của artifact. Công thức mô phỏng không bao gồm spread biến thiên, market impact, thanh khoản, thuế hoặc timing khớp lệnh.

## 3.12. Evidence pack

Initial pack gồm `decision_id`, ticker, decision date, ML signal, technical snapshot, top drivers, news evidence trước cutoff, data quality flags và guardrails. Audit pack giữ outcome để phục vụ hậu kiểm; initial pack không giữ outcome. ML-only pack loại news evidence để làm ablation.

News evidence chỉ dùng summary, key facts, risk flags, excerpt ngắn và metadata ref/hash; không bơm toàn văn mặc định. Mỗi claim định tính cần `evidence_id`. Nếu evidence thiếu, card phải ghi “evidence tin tức chưa đủ mạnh”.

## 3.13. Decision-card variants

1. **Rule-based baseline:** template cố định, không generation tự do.
2. **LLM ML-only:** ML signal và technical drivers, không có news evidence.
3. **LLM full-evidence:** ML, technical, news, risk và data quality flags.

Rubric gồm faithfulness, hallucination control, ML explanation, risk awareness, monitoring usefulness và clarity/usefulness, mỗi tiêu chí 1–5. Rubric không chấm return.

## 3.14. Monitoring và outcome review

Monitoring được artifact hóa theo post-decision news và có thể gắn trạng thái rule-derived `Watch` hoặc `Review Required`; các trạng thái này là prompt để analyst kiểm tra, không phải factual verdict. UI/bundle hiện không dùng alert để thay đổi thesis ban đầu hoặc tái huấn luyện mô hình. Outcome review được tạo sau holding horizon, giữ realized return, benchmark khi có, direction alignment, salience và attribution status. Outcome review không được quay lại initial prompt.

---

# CHƯƠNG 4. KẾT QUẢ

## 4.1. Quy mô và provenance artifact

| Artifact | Số lượng | Nguồn |
|---|---:|---|
| Annotation sample | 150 | `semantic_news_materiality_study_report.md` |
| Consensus labels | 150 | `annotation_agreement_report.md` |
| Analysis-eligible consensus | 122 | `claim_vs_evidence_table.md` |
| Semantic daily | 93.824 | `semantic_news_materiality_study_report.md` |
| Event windows | 456 | `semantic_news_materiality_study_report.md` |
| Event tests | 8 | `event_window_stat_tests_report.md` |
| ML predictions | 685.704 | `ml_outperform_experiment_report.md` |
| Top-K rows | 2.592 | `topk_backtest_with_cost_report.md` |
| Outcome reviews | 114 | `outcome_review_report.md` |
| Decision packs | 25 | `generated_summary.md` |
| Monitoring news events | 3.838 | `generated_summary.md` |

Semantic annotation provenance gồm DeepSeek `deepseek-chat` trả về `deepseek-v4-flash` cho runs A/B và OpenAI-vendor `gpt-5.4-mini` qua gateway/proxy cho run C. Status artifact là `legacy_reconstructed`; không gọi đây là ba hệ thống độc lập hoàn toàn.

## 4.2. Kết quả keyword/news-as-predictor

Kết quả full-text production split cho thấy Config B gần ngẫu nhiên, Config C không vượt Config A ở cả bốn model. Sau cải tiến phủ định, đồng nghĩa và longest-first masking, delta một số horizon dịch lên nhưng không nhất quán; RF, XGBoost và LightGBM vẫn không hưởng lợi ổn định. H1 không được ủng hộ.

**Mức claim:** `supported negative finding` trong corpus, feature schema và temporal settings hiện tại. Không được mở rộng thành “mọi news representation đều vô dụng”.

## 4.3. Rule baseline so với semantic pseudo-label

| Field | Accuracy | Macro-F1 | n |
|---|---:|---:|---:|
| Direction | 0,3770 | 0,2282 | 122 |
| Event type | 0,1475 | 0,0865 | 122 |
| Materiality | 0,2213 | 0,1595 | 122 |
| Ticker relevance | 0,6885 | 0,2090 | 122 |

Error taxonomy gồm keyword thiếu ngữ cảnh, keyword không đo materiality, ticker relevance sai, market-wide bị đếm như direct, boilerplate/full-text noise, mixed direction và event-type overlap. Đây là kết quả hỗ trợ cho semantic audit; reference vẫn là pseudo-label consensus.

## 4.4. Annotation agreement

| Field | a–b agreement / kappa | a–c agreement / kappa | b–c agreement / kappa |
|---|---:|---:|---:|
| Ticker relevance | 0,9867 / 0,9408 | 0,9000 / 0,6325 | 0,8867 / 0,5917 |
| Materiality | 0,9467 / 0,9183 | 0,7267 / 0,5772 | 0,7200 / 0,5669 |
| Direction | 0,9667 / 0,9518 | 0,7800 / 0,6811 | 0,7600 / 0,6532 |
| Event type | 0,9733 / 0,9695 | 0,8467 / 0,8252 | 0,8400 / 0,8176 |
| Time horizon | 0,9267 / 0,8868 | 0,6867 / 0,5332 | 0,6533 / 0,4845 |

Agreement a–b cao hơn c ở nhiều field. Điều này phù hợp với khả năng hai run DeepSeek có tương quan model family. Không được diễn giải kappa là độ đúng tuyệt đối.

## 4.5. Event-window statistical tests

| Window | Comparison | diff mean | p raw | p BH | Cliff’s delta | CI diff | Robust positive |
|---|---|---:|---:|---:|---:|---|---|
| T+1 | direction support vs risk | 0,0080 | 0,1918 | 0,3069 | 0,2256 | [−0,0013; 0,0175] | Không |
| T+1 | materiality high+medium vs low | 0,0020 | 0,5494 | 0,6278 | −0,0654 | [−0,0046; 0,0089] | Không |
| T+5 | direction support vs risk | 0,0081 | 0,1766 | 0,3069 | 0,2344 | [−0,0245; 0,0338] | Không |
| **T+5** | **materiality high+medium vs low** | **0,0223** | **0,0057** | **0,0457** | **0,3085** | **[0,0091; 0,0366]** | **Có** |
| T+20 | direction support vs risk | 0,0249 | 0,2979 | 0,3972 | 0,1840 | [−0,0318; 0,0783] | Không |
| T+20 | materiality high+medium vs low | 0,0397 | 0,0325 | 0,1301 | 0,2482 | [0,0065; 0,0735] | Không |
| T+60 | direction support vs risk | 0,0205 | 0,9722 | 0,9722 | −0,0087 | [−0,0533; 0,1023] | Không |
| T+60 | materiality high+medium vs low | 0,0399 | 0,0865 | 0,2306 | 0,2147 | [−0,0117; 0,0914] | Không |

Có 1/8 test qua joint positive gate. Kết quả T+5 materiality là **supported exploratory association**. Nó không chứng minh materiality gây ra return, không chứng minh có thể giao dịch, và không chứng minh hiệu ứng tồn tại ngoài sample.

## 4.6. Purged OOS ML

| Config | Model | BA mean | BA std | AUC mean | AUC std | F1 mean | Rank IC mean |
|---|---|---:|---:|---:|---:|---:|---:|
| A_technical | LogisticRegression | 0,4898 | 0,0139 | 0,4871 | 0,0164 | 0,3977 | −0,0285 |
| A_technical | RandomForest | 0,4991 | 0,0195 | 0,5018 | 0,0207 | 0,4599 | 0,0090 |
| C_technical_semantic | LogisticRegression | 0,4905 | 0,0076 | 0,4957 | 0,0074 | 0,4193 | −0,0107 |
| C_technical_semantic | RandomForest | 0,5063 | 0,0135 | 0,5088 | 0,0156 | 0,4742 | 0,0193 |
| D_all | LogisticRegression | 0,4967 | 0,0087 | 0,5072 | 0,0158 | 0,4691 | 0,0228 |
| **D_all** | **RandomForest** | **0,5105** | **0,0069** | **0,5116** | **0,0091** | **0,4965** | **0,0246** |

Các kết quả gần 0,5 cho BA/AUC trong setting purged OOS. Đây là lý do luận văn đặt ML ở vị trí **quantitative core về kiến trúc**, không tuyên bố signal đã được xác nhận về hiệu quả giao dịch. Artifact cũ theo split quý có BA technical cao hơn; sự khác biệt setting cho thấy cần báo cáo version và validation protocol, không chọn con số đẹp nhất.

## 4.7. Top-K simulation và null

Ở cost 0,5%, một số dòng model_topk có cumulative net return dương, ví dụ `D_all`–LogisticRegression–K=10 là 0,7613 và `B_technical_keyword`–LogisticRegression–K=10 là 0,5847. Tuy nhiên, random-null summary cho `D_all`–LogisticRegression–K=10 có one-sided null p-value 0,01 và percentile 0,995; `B_technical_keyword`–LogisticRegression–K=10 cũng p-value 0,01. Đây là dấu hiệu cần kiểm tra thêm, không phải bằng chứng triển khai, vì simulation có 54 periods, hash-based null và nhiều cấu hình được thử.

Cost sensitivity cho `D_all`–LogisticRegression–K=10 giảm cumulative net return từ 0,8984 ở cost 0 xuống 0,7613 ở cost 0,005 và 0,6337 ở cost 0,01. Điều này cho thấy kết quả nhạy với giả định chi phí. Report cũng nêu chưa mô phỏng market impact, spread variation, liquidity, taxes và execution timing.

**Mức claim:** `weak/exploratory`; không gọi là alpha, không gọi là bằng chứng lợi nhuận bền vững.

## 4.8. Evidence pack và lifecycle artifacts

`generated_summary.md` ghi 25 evidence packs, 25 rule-based cards, 3.838 monitoring events và outcome reviews. `evidence_packs_initial.json` là prompt-safe; `evidence_packs_audit.json` có `outcome_for_review_only` và chỉ dùng hậu kiểm. Unit tests và validation report xác nhận initial prompt không chứa outcome tương lai trong run được kiểm tra.

Outcome review report có 114 rows: direction alignment unavailable 61, aligned 29, opposed 24; salience salient 54, not salient 53, unavailable 7; attribution status unassessed 114. Đây là structured external-consistency audit, không phải ground truth hoặc đo chất lượng card.

## 4.9. Rubric Gemini

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `llm_full_evidence` | 25 | 5,00 | 5,00 | 5,00 | 4,96 | 5,00 | 5,00 | **5,00** | 0 | 0 |
| `llm_ml_only` | 25 | 1,28 | 1,00 | 4,72 | 2,04 | 4,56 | 2,12 | **1,16** | 43 | 114 |
| `rule_based_baseline` | 25 | 4,56 | 4,88 | 4,60 | 4,56 | 5,00 | 4,12 | **4,32** | 2 | 15 |

Run: Gemini `gemini-2.5-pro`, official `google-genai`, 50 generated cards và 75 scores. Gemini vừa sinh vừa chấm; điểm có khả năng self-preference. ML-only bị đánh trên full evidence pack nên missing references một phần là hệ quả có chủ ý của ablation.

## 4.10. Rubric local router

| Card type | n | Faithfulness | Hallucination | ML explanation | Risk | Monitoring | Clarity | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `llm_full_evidence` | 25 | 4,64 | 4,84 | 4,08 | 4,80 | 2,52 | 4,36 | **3,96** | 0 | 71 |
| `llm_ml_only` | 25 | 2,32 | 1,28 | 3,96 | 2,64 | 2,12 | 3,24 | **2,32** | 90 | 148 |
| `rule_based_baseline` | 25 | 3,12 | 2,88 | 3,76 | 3,04 | 2,80 | 3,72 | **3,00** | 69 | 127 |

Run này có request provider config Anthropic-compatible nhưng response model ghi `gpt-5.6-luna`. Vì vậy provenance phải ghi **OpenAI-vendor model qua local router**, không gọi là Claude native. Artifact run-scoped được dùng là `router_claude2_llm_rubric_scores.csv` và `router_claude2_llm_rubric_summary.md`; không dùng manifest chung nếu manifest đã bị overwrite.

Hai run local judge đều cho pattern full-evidence > ML-only trong cùng run. Common local judge chấm chéo các card Gemini với overall 3,44 cho full-evidence, 2,96 cho rule baseline và 2,32 cho ML-only. Không so sánh 5,00 của Gemini self-judge với 3,44 của common local judge để xếp hạng provider, vì judge và điều kiện run khác nhau.

## 4.11. Case studies

Case study chỉ minh họa traceability, không dùng để suy rộng:

| Case | Decision ID | Cách dùng |
|---|---|---|
| News và ML cùng hỗ trợ | `2025Q2_STB_01` | Minh họa cách evidence trước decision date được nối với signal. |
| Tín hiệu yếu cần review | `2026Q1_DPM_03` | Minh họa risk flags, technical weakness và monitoring. |
| Return không thay thế evidence | `2025Q3_KDH_04` | Minh họa outcome hậu kiểm không được đưa vào initial card. |
| Evidence trái chiều | `2025Q2_VND_05` | Minh họa card phải nêu debt/capital risk dù signal khác chiều. |
| Cần review sau horizon | `2025Q4_VBB_05` | Minh họa separation giữa initial card và outcome review. |

## 4.12. EvidenceTrace research prototype

EvidenceTrace là Streamlit analyst workspace đọc **validated bundle** thay vì đọc CSV/JSONL/Markdown nguồn trực tiếp. Bundle builder viết vật lý riêng các zone `select`, `initial`, `monitor`, `update`, `review`, `semantic`, `evaluation` và `provenance`; outcome không thể chỉ bị ẩn bằng điều kiện giao diện. Initial payload bị quét recursive các marker `outcome`, `realized`, `review_only`, `benchmark_return`, `excess_return`, `future_return` và `future_label`; evidence ban đầu phải thỏa `published_at <= decision_date`.

Luồng demo là `Select → Explain → Monitor → Update → Review`. `Monitor` và `Update` bắt buộc historical `as_of`; event sau cutoff không hiện. `Review` chỉ mở khi holding period complete, kèm nhãn post-hoc. `Evaluation` tách Gemini self-judge, local-router judge và common local-judge cross-score thành các run riêng, mỗi run 75 score records. UI chỉ dùng nhãn `Model candidate`, `Watch`, `Review Required` và `Requires human review`; không có CTA giao dịch hoặc dữ liệu thị trường live.

**Hình 5. EvidenceTrace architecture (placeholder khi dàn trang).** Nguồn artifact → catalog SHA-256 → bundle partitioned → Streamlit analyst workspace → confirmed live-LLM run directory. Hình phải ghi ngày capture, bundle version, `decision_id`, `snapshot_mode` và `as_of`.

**Hình 6. EvidenceTrace lifecycle screenshots (placeholder khi dàn trang).** Cần tối thiểu ba ảnh: normal evidence, low-quality/ambiguous evidence và `Review Required`. Mỗi ảnh phải che secret, ghi bundle version/cutoff và không hiển thị outcome ngoài workspace Review.

## 4.13. QA và validation

Kiểm chứng được ghi lại trong artifact validation: decision-support tests 20 passed; py_compile script liên quan pass; live Gemini generation 50/50 cards và scoring 75/75 scores. `tests/test_research_ui_policy.py`, `test_research_ui_catalog.py` và `test_research_ui_bundle.py` cover cutoff, outcome leakage, hash/catalog, physical partition và count 75 cho common judge. Các số pass trong bản cuối chỉ được giữ sau khi chạy lại suite ở Phụ lục G; không gọi provider API khi chỉ kiểm artifact. QA vẫn có rủi ro automated self-judge, missing references, ticker matching và possible content-level future contamination cần audit thêm.

---

# CHƯƠNG 5. THẢO LUẬN

## 5.1. Claim–evidence matrix

| RQ | Claim được phép | Evidence canonical | Schema/hash khi có | Mức và giới hạn |
|---|---|---|---|---|
| RQ1 | Purged OOS ML hiện tại gần random; chưa đủ xác nhận signal ổn định | `ml_outperform_experiment_report.md` | `outperform_ml_predictions_v2`; SHA-256 tại Phụ lục A | Descriptive/exploratory; không trading advantage |
| RQ2 | Keyword representation không cải thiện ổn định trong setting đã chạy | `H1_experiment_report.md` | Track quarterly legacy, không gộp OOS semantic | Supported negative trong representation/setting đã chạy |
| RQ3 | Rule baseline bỏ sót context của direction, event type và materiality | `rule_vs_semantic_labels_report.md` | Pseudo-label reference, n=122 | Supported exploratory; không human ground truth |
| RQ4 | Semantic materiality có một liên hệ dương ở T+5 sau gate | `event_window_stat_tests_report.md` | `event_window_tests_v3`; 1/8 joint gate | Supported exploratory association; không causal |
| RQ5 | Top-K có kết quả nhạy config, K, null và cost | `topk_backtest_with_cost_report.md` | `topk_nonoverlap_v2`; 54 periods | Weak exploratory; không alpha/suitability |
| RQ6 | Full-evidence card cao hơn ML-only trong từng automated judge | Gemini/local-router/common-judge rubric artifacts | 75 scores mỗi run; judge conditions khác nhau | Card-quality pattern; không provider ranking/return |
| RQ7 | Lineage, cutoff, initial/outcome separation và UI bundle boundary được artifact hóa | validation report, catalog, UI tests | `research-ui-catalog-v1` | Technical traceability; không xác nhận factual truth |

## 5.2. Trả lời RQ1

Current purged OOS result không cho phép nói technical ML đã tạo signal đáng tin cậy. BA và AUC gần 0,5, và các model/config khác nhau có biến động. Đây là kết quả quan trọng vì ngăn việc lấy một split legacy có score cao để đại diện cho toàn bộ pipeline semantic hiện hành.

## 5.3. Trả lời RQ2

Negative finding của H1 không đồng nghĩa news vô dụng. Nó cho thấy keyword/frequency/sentiment khi ép thành predictor theo kỳ không cung cấp incremental signal ổn định so với technical setup đã thử. Việc thêm full text, nguồn mới, cụm phủ định, synonym và longest-first masking không đảo được kết luận. Đây là lý do hợp lý để chuyển news từ predictor sang evidence/context layer.

## 5.4. Trả lời RQ3 và RQ4

Semantic schema phân biệt những khía cạnh rule baseline bỏ sót. Rule accuracy event type và materiality thấp, error taxonomy cho thấy các lỗi có cấu trúc. Agreement giữa model cao ở một số pair nhưng thấp hơn khi so với run khác model family; pseudo-label limitation vẫn chi phối.

Event T+5 materiality là một tín hiệu exploratory sau BH-FDR. Vì chỉ 1/8 test qua gate và event data có thể bị confounding, claim chỉ dừng ở “có liên hệ quan sát được trong một cửa sổ”. Không được suy ra tác động nhân quả, lợi thế giao dịch hoặc tính tổng quát.

## 5.5. Trả lời RQ5

Top-K simulation có một số dòng return cao hơn deterministic null, nhưng nhiều cấu hình và cost sensitivity làm tăng nguy cơ selection. Null hash là reproducible nhưng không độc lập với thị trường. Vì vậy, Top-K chỉ chứng minh pipeline có thể tính ranking, non-overlap và net-return equation; chưa chứng minh khả năng đầu tư.

## 5.6. Trả lời RQ6

Full-evidence card tốt hơn ML-only trong Gemini self-judge, local-router judge và common judge trên Gemini cards. Điều này phù hợp construct của rubric: card được chấm về evidence, risk, monitoring và references; ML-only bị tước news evidence có chủ ý. Pattern nói evidence đầy đủ làm card giàu context hơn trong điều kiện judge đã ghi, không nói LLM dự báo tốt hơn.

Gemini score 5,00 có thể bị self-preference vì cùng model family sinh/chấm. Local router score 3,96 và common local cross-score 3,44 dùng response model `gpt-5.6-luna`, dù request config Anthropic-compatible. Do condition judge khác nhau, không dùng các score để ranking provider.

## 5.7. Trả lời RQ7

Initial pack, audit pack, monitoring event và outcome review là các record riêng. Hash, schema version, source path, run manifest và bundle physical partition hỗ trợ tái lập. Cutoff `published_at <= decision_date` và recursive outcome stripping là guardrail quan trọng. Tuy nhiên, validation không biến dữ liệu nguồn thành đúng tuyệt đối; content crawler và entity matching vẫn cần audit.

## 5.8. Threats to validity

### Internal validity

- News có thể chứa nội dung cập nhật sau timestamp bài hoặc boilerplate từ sidebar/footer.
- Ticker matching có thể gắn sai chủ thể.
- Future contamination có thể nằm trong text dù trường metadata đã cắt.
- Outcome audit pack có thể bị dùng nhầm nếu script sai path.

### Statistical validity

- Chỉ tám event tests, nhiều subgroup và horizon.
- `(ticker, period)` không hoàn toàn độc lập.
- Null hash không phải independent market realization.
- Top-K có nhiều configuration choices.
- Pseudo-label agreement không thay thế human annotation.

### Construct validity

- BA/AUC không đo mức lãi hoặc suitability.
- Materiality do LLM tạo không phải nhãn chuyên gia.
- Rubric score đo card quality, không đo decision quality ngoài rubric.
- Outcome direction alignment không phải attribution.

### External validity

- Dữ liệu tập trung Việt Nam và các universe đã chọn.
- Source coverage không đều theo thời gian và ticker.
- Regime thị trường khác có thể cho kết quả khác.
- Một số provider artifact có status legacy reconstructed.

### Evaluation validity

- Gemini tự chấm output của mình.
- Hai rubric runs dùng judge khác nhau.
- Missing refs của ML-only một phần là do ablation design.
- Manual sanity check 24 rows không có reviewer provenance.

## 5.9. Ý nghĩa phương pháp

Luận văn cho thấy negative result có giá trị thiết kế. Khi keyword features không vượt technical baseline và purged OOS hiện tại gần random, hệ thống không nên “cứ thêm prompt” để tạo câu chuyện tích cực. Thay vào đó, tách rõ ba lớp: signal định lượng, evidence ngữ nghĩa và văn bản hỗ trợ quyết định. Cách tách này làm claim nhỏ hơn nhưng audit được tốt hơn.

---

# CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 6.1. Kết luận

1. Pipeline hiện có nối price/ML, semantic news, evidence pack, rule/LLM card, monitoring, outcome review và EvidenceTrace bundle.
2. Purged OOS ML trong artifact canonical có BA/AUC gần random; chưa đủ xác nhận signal ổn định hoặc lợi thế giao dịch.
3. Keyword/news-count representation không cải thiện ổn định trong H1 đa granularity, full text và mở rộng nguồn; kết luận này không phủ định mọi cách dùng news.
4. Semantic schema hữu ích cho error taxonomy và audit, nhưng labels là pseudo-label, provenance annotation legacy reconstructed và không thay thế human ground truth.
5. Một trong tám event tests qua positive gate tại T+5 materiality; đây là exploratory association, không causal.
6. Top-K có một số outcome cao hơn deterministic null, nhưng kết quả nhạy cấu hình, K, cost và chọn model; chỉ là weak exploratory simulation.
7. Full-evidence card có điểm cao hơn ML-only trong từng automated judge condition; không suy ra forecast quality, return hay provider superiority.
8. Provenance, cutoff, recursive stripping, review-only gate và physical bundle separation tạo nền tảng traceability, nhưng không loại bỏ mọi contamination hoặc lỗi nguồn.

## 6.2. Đóng góp

Đóng góp của đề tài nằm ở framework và kỷ luật diễn giải: lưu artifact theo schema, báo cáo negative findings, tách provider với model vendor, tách initial evidence khỏi outcome, và gắn claim với evidence cùng limitation. Đây là đóng góp phù hợp với prototype data-science decision support, không phải hệ thống giao dịch tự động.

## 6.3. Hướng phát triển

1. Xây bộ human-labeled Vietnamese financial news với reviewer provenance và adjudication.
2. Chạy lại semantic annotation bằng cùng prompt, cùng sample và independent expert judge.
3. Kiểm tra DeepSeek decision-card run sau khi provider có balance; không gọi run 402 `Insufficient Balance` là kết quả card.
4. Audit content-level leakage bằng timestamp scanner, boilerplate ratio và entity consistency.
5. Mở rộng event study với pre-registration, sector/source/time stratification và cluster-aware inference.
6. Calibrate probability và kiểm tra drift theo rolling window.
7. Chạy backtest daily có slippage, spread, liquidity, market impact, T+2 và giới hạn giao dịch.
8. Tách paper-trading evaluation khỏi historical backtest.
9. Chấm card bằng chuyên gia độc lập, blind provider và common rubric.
10. Mở rộng EvidenceTrace sau khi có ảnh lifecycle được kiểm chứng, accessibility/E2E report, multi-user governance và human-in-the-loop workflow ổn định.

## 6.4. Kết luận cuối

Kết quả hiện có không ủng hộ việc trình bày news/LLM như nguồn dự báo trực tiếp hoặc lợi thế giao dịch đã được xác nhận. Giá trị phù hợp hơn là một hệ thống hỗ trợ phân tích có cấu trúc: ML tạo tín hiệu cần kiểm tra, semantic layer tổ chức evidence và lỗi, LLM diễn giải trong guardrail, monitoring ghi thay đổi, outcome review ghi hậu kiểm. Mọi kết luận phải giữ đúng giới hạn đó.

---

# TÀI LIỆU THAM KHẢO

Các nguồn dưới đây đã xuất hiện trong tài liệu và artifact của repository; cần chuẩn hóa kiểu trích dẫn theo quy định của trường trước khi nộp.

1. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.
2. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of KDD*.
3. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems*.
4. Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*.
5. Ding, X., Zhang, Y., Liu, T., & Duan, J. (2015). Deep learning for event-driven stock prediction. *Proceedings of IJCAI*.
6. Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *The Journal of Finance*, 25(2), 383–417.
7. Schumaker, R. P., & Chen, H. (2009). Textual analysis of stock market prediction using breaking financial news. *ACM Transactions on Information Systems*, 27(2).
8. Nassirtoussi, A. K., Aghabozorgi, S., Wah, T. Y., & Ngo, D. C. L. (2014). Text mining for market prediction: A systematic review. *Expert Systems with Applications*, 41(16), 7653–7670.
9. Nguyen, D. Q., & Nguyen, A. T. (2020). PhoBERT: Pre-trained language models for Vietnamese. *Findings of EMNLP*.
10. White, H. (2000). A reality check for data snooping. *Econometrica*.
11. Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. *arXiv preprint arXiv:1908.10063*.
12. Benjamini, Y., & Hochberg, Y. (1995). Controlling false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.
13. Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall.
14. Các báo cáo, artifact và manifest nội bộ của đề tài được liệt kê tại Phụ lục A. Chúng là nguồn tái lập thực nghiệm, không thay thế tài liệu học thuật phản biện.

---

# PHỤ LỤC A. CLAIM–EVIDENCE–LIMITATION VÀ ARTIFACT LEDGER

| Claim | Artifact | Schema/version hoặc SHA-256 | Diễn giải được phép | Limitation |
|---|---|---|---|---|
| Keyword thiếu ngữ cảnh | `rule_vs_semantic_labels_report.md` | Reference pseudo-label, n=122 | Rule sai nhiều ở direction/event/materiality | Không phải human ground truth |
| Consensus semantic | `annotation_agreement_report.md` | `pseudo_label_consensus_v2`; `658e6b8b827f7bc5b76f6cf72f5c100abd77dba0be95be563bec94d1b31715ba` | 150 rows, eligible 122 | Không phải human ground truth; provenance legacy reconstructed |
| Event association | `event_window_stat_tests_report.md` | `event_window_tests_v3`; `0ef12ace27fec1c809b24a2b93f077258c51840f5bab656e23752d7975721c7f` | 1/8 qua positive gate | Không causal, sample nhỏ |
| Purged ML | `ml_outperform_experiment_report.md` | `outperform_ml_predictions_v2`; `8ac3ddf5fcb328e9713b2311321e8d810a97f0c03f06d90923b90257aff03da9` | BA/AUC gần random trong current OOS | Không claim trading advantage |
| Top-K | `topk_backtest_with_cost_report.md` | `topk_nonoverlap_v2`; `f9c9becda04e72dff11f89ae7da777e0842ba21ea1c45a34a27d3ffd93d6f280` | Simulation non-overlap/cost/null | Nhạy config, cost, null |
| Decision card | Catalog-completed Gemini/local-router/common-judge artifacts | `research-ui-catalog-v1`; 75 score records cho mỗi run | Full evidence cao hơn ML-only trong từng judge | Automated judge, không đo return; không rank provider |
| Outcome review | `outcome_review_report.md` | 114 review-only rows | Structured post-hoc audit | Attribution unassessed |

# PHỤ LỤC B. SEMANTIC ANNOTATION SCHEMA

```json
{
  "news_id": "string",
  "ticker": "string",
  "article_date": "YYYY-MM-DD",
  "ticker_relevance": "direct|market_wide|irrelevant|unclear",
  "materiality": "low|medium|high|unclear",
  "direction": "support|risk|neutral|mixed|unclear",
  "event_type": "earnings|debt|governance|legal|capital|market|other|unclear",
  "time_horizon": "short_term|medium_term|long_term|unclear",
  "materiality_score": 1,
  "expected_impact_score": 1,
  "uncertainty_score": 1,
  "novelty_score": 1,
  "reasoning_confidence": 1,
  "evidence_span": "exact quote or null",
  "quality_flags": [],
  "future_information_blocked": true
}
```

`pseudo_label_consensus_v2` lưu thêm consensus method, agreement level, disagreement fields, eligibility và review flags. Numeric score outlier không tự động biến row thành invalid; row phải giữ quality flag.

# PHỤ LỤC C. EVIDENCE PACK VÀ DECISION CARD

## C.1. Initial evidence pack tối thiểu

```json
{
  "decision_id": "2025Q1_SCR_01",
  "ticker": "SCR",
  "decision_date": "2025-03-31",
  "ml_signal": {
    "model_name": "string",
    "pred_proba_up": 0.0,
    "pred_label": 0,
    "rank_in_period": 0
  },
  "technical_snapshot": {},
  "top_drivers": [],
  "news_evidence": [],
  "data_quality_flags": {},
  "guardrails": {
    "no_future_return_included": true,
    "news_cutoff": "2025-03-31",
    "llm_must_cite_evidence": true,
    "not_investment_advice": true
  }
}
```

## C.2. Decision card

1. Tóm tắt signal.
2. Thesis chính và evidence refs.
3. Yếu tố hỗ trợ.
4. Rủi ro và data-quality flags.
5. Trigger probability/rank/technical/news/drawdown.
6. Review date/horizon.
7. Kết luận hỗ trợ quyết định, không dùng ngôn ngữ chắc chắn.
8. Disclaimer.

## C.3. Outcome review riêng

Outcome review có thể chứa realized return sau holding period, benchmark return, direction alignment, salience, monitoring events và lessons. Record này không được merge ngược vào initial card.

# PHỤ LỤC D. PROMPT GUARDRAILS

```text
Chỉ sử dụng thông tin trong evidence pack.
Không thêm dữ kiện ngoài input.
Không dự báo giá tuyệt đối.
Không cam kết lợi nhuận.
Không đưa ra khuyến nghị đầu tư chắc chắn.
Mỗi luận điểm chính phải dẫn evidence_id hoặc trường dữ liệu liên quan.
Nếu evidence thiếu, yếu hoặc mâu thuẫn, phải ghi rõ.
Không sử dụng realized return, outcome review hoặc future label trong initial card.
Full_text_ref và content_hash chỉ là metadata audit; không suy diễn nội dung không có trong prompt.
```

# PHỤ LỤC E. PROVENANCE VÀ MODEL STATUS

| Artifact/run | API provider | Requested model | Response model | Vendor | Route | Trạng thái |
|---|---|---|---|---|---|---|
| Semantic A | DeepSeek | `deepseek-chat` | `deepseek-v4-flash` | DeepSeek | Native | Legacy reconstructed |
| Semantic B | DeepSeek | `deepseek-chat` | `deepseek-v4-flash` | DeepSeek | Native | Legacy reconstructed |
| Semantic C | Gateway | `cx/gpt-5.4-mini` | `gpt-5.4-mini` | OpenAI-vendor | Gateway/proxy | Legacy reconstructed |
| Decision cards | Gemini | `gemini-2.5-pro` | `gemini-2.5-pro` | Google | Official SDK | Completed 50 cards |
| Router rubric | Anthropic-compatible request | `claude-opus` config | `gpt-5.6-luna` | OpenAI-vendor | Local router | Completed 75 scores |
| DeepSeek card trial | DeepSeek | — | — | DeepSeek | Native | Failed: API `402 Insufficient Balance`, no cards |

Không gọi response `gpt-5.6-luna` là Claude native. Không gọi DeepSeek card provider vì trial thất bại và không có 50 cards.

# PHỤ LỤC F. RUBRIC VÀ CẢNH BÁO

| Tiêu chí | Câu hỏi |
|---|---|
| Faithfulness | Card bám evidence pack không? |
| Hallucination control | Card có thêm fact ngoài input không? |
| ML explanation | Card giải thích signal và drivers không? |
| Risk awareness | Card nêu risk cụ thể không? |
| Monitoring usefulness | Trigger có đo được không? |
| Clarity/usefulness | Card rõ, có thể hậu kiểm không? |

Rubric 1–5 là automated internal evaluation. Gemini self-generated/self-scored output có thể có self-preference. Common local judge đã chấm chéo 75 Gemini cards; đây vẫn chưa phải human expert ground truth. Local-router judge và Gemini self-judge khác nhau nên không dùng score để xếp hạng provider.

# PHỤ LỤC G. VALIDATION CHECKLIST

- [x] Initial prompt dùng `evidence_packs_initial.json`.
- [x] ML-only pack loại news evidence có chủ ý.
- [x] Outcome fields bị strip recursive khỏi initial packs.
- [x] News cutoff `published_at <= decision_date`.
- [x] Outcome review tách khỏi initial card.
- [x] Purged OOS folds có purge 20 phiên.
- [x] Event gate dùng BH-FDR và CI dương.
- [x] Top-K kiểm tra non-overlap, turnover cost và net equation.
- [x] Provider và response model được ghi tách.
- [x] DeepSeek card trial được ghi là thất bại, không có cards.
- [x] Automated rubric không được gọi là human ground truth.
- [ ] Human expert annotation đầy đủ.
- [x] Common local-judge cross-score 75 Gemini cards.
- [x] EvidenceTrace Streamlit research prototype: validated bundle tách Initial/Monitor/Update/Review/Evaluation; analyst-mode lifecycle và live-LLM confirmation workflow.
- [x] Chạy lại UI suite ngày 15/07/2026: `python -m pytest tests/test_research_ui_*.py -q` — 24 passed, 9.55s.
- [x] Chạy lại decision-support ngày 15/07/2026: `python -m pytest tests/test_decision_support.py -q` — 20 passed, 0.34s.
- [x] Chạy lại multi-LLM regression ngày 15/07/2026: `test_multi_llm_annotation_consensus.py`, `test_multi_llm_event_statistics.py`, `test_multi_llm_temporal_pipeline.py`, `test_multi_llm_robustness_outputs.py`, `test_multi_llm_backtest_reports.py`, `test_experiment_llm_semantic_features.py`, `test_a6_llm_sentiment.py`, `test_llm_sentiment_pbt.py`, `test_a7_llm_scorecard.py`, `test_outcome_manual_review.py` — 74 passed, 12.07s.
- [x] Compile UI modules ngày 15/07/2026: `python -m py_compile scripts/build_research_ui_bundle.py research_ui/app.py research_ui/policy.py research_ui/repository.py research_ui/live_jobs.py`.
- [x] Kiểm catalog path/hash qua UI suite `test_research_ui_catalog.py` và bundle build.
- [ ] Chạy Markdown/PDF render audit: heading, bảng, tiếng Việt, figure placeholder, reference và page break.
- [ ] Content-level future/ticker contamination audit hoàn chỉnh.
- [ ] Paper-trading validation.

# PHỤ LỤC H. EVIDENCETRACE RESEARCH PROTOTYPE

## H.1. Mục đích và phạm vi

EvidenceTrace là prototype Streamlit dùng để demo lifecycle `select → explain → monitor → update → review` trên artifact lịch sử đã kiểm chứng. Hệ thống tổ chức thông tin cho analyst; không có live market data, lệnh giao dịch, target price, phân bổ danh mục hay khuyến nghị đầu tư.

## H.2. Tách trust zone

| Workspace | Dữ liệu được phép | Dữ liệu bị cấm |
|---|---|---|
| Select / Explain | Prompt-safe initial evidence, signal kỹ thuật, tin đến `decision_date` | Outcome, realized return, review và monitoring post-decision |
| Monitor | Snapshot ban đầu và event `<= as_of` | Event sau `as_of`, outcome review |
| Update | Snapshot ban đầu và monitoring đã lọc `as_of` | Outcome/review, tự động ghi đè thesis |
| Review | Snapshot đóng băng, monitoring history, post-hoc outcome | Feed ngược vào initial/update/card prompt |
| Evaluation | Card, prompt-safe evidence và rubric | So sánh score với realized return |

Bundle builder tạo file vật lý riêng cho mỗi zone. Mọi initial payload được quét recursive để loại `outcome`, `realized`, `review_only`, `benchmark_return`, `excess_return`, `future_return` và `future_label`; mọi tin initial phải thỏa `published_at <= decision_date`.

## H.3. UI và evidence inspection

Trang Select hiển thị `Model candidate` thay cho CTA mua. Trang Explain cho xem model metadata, technical drivers, evidence ID, ngày, source, key facts, risk flags, match confidence, content hash và data-quality flags. Semantic consensus luôn kèm cảnh báo “model-derived pseudo-label; not human ground truth”.

Trang Monitor và Update bắt buộc historical `as_of`; event sau cutoff không hiển thị. Trang Review chỉ hiển thị realized return sau holding-period gate và gắn nhãn post-hoc. Trang Evaluation tách ba run rubric: Gemini self-judge, local-router judge và common local-judge cross-score; rubric chỉ đo card quality.

## H.4. Live LLM có xác nhận

Analyst chọn provider/model và variant `ml_only` hoặc `full_evidence`, xem pack/prompt hash cùng leakage check, rồi xác nhận external API call. Mỗi live run ghi vào `reports/decision_support/generated/runs/<run_id>/`, không ghi đè artifact canonical. Provider failure tạo manifest lỗi hoặc offline state, không tạo card/score giả. API key chỉ đọc từ environment/server-side; không xuất hiện trong UI hoặc artifact provenance.

## H.5. Xác minh prototype

Catalog `research-ui-catalog-v1` pin 25 initial full-evidence records, 25 ML-only records, 25 review records, 150 semantic-consensus records và ba rubric runs, mỗi run yêu cầu đúng 75 score records. `tests/test_research_ui_policy.py` kiểm initial cutoff, recursive outcome leakage, historical `as_of`, review boundary và no-trade-CTA label. `tests/test_research_ui_catalog.py` kiểm hash/path catalog. `tests/test_research_ui_bundle.py` kiểm physical partition, absence của outcome trong initial payload và ba evaluation-run count. Kết quả pass/fail của lần chạy cuối phải được ghi tại checklist Phụ lục G; không suy diễn thành browser E2E, accessibility hoặc screenshot verification nếu chưa có report riêng.

## H.6. Giới hạn

EvidenceTrace là local research prototype, một analyst mode, không auth/RBAC, không DB, không live price feed và không paper-trading. Monitoring hiện tập trung post-decision news; không chứng minh alert cải thiện return. Live LLM workflow có guardrail nhưng vẫn chịu chi phí, provider failure, model drift và automated-rubric limitation.

# PHỤ LỤC I. DISCLAIMER NGHIÊN CỨU

Luận văn phục vụ nghiên cứu và minh họa kỹ thuật dữ liệu. Decision card, ranking, event association, backtest, monitoring event và outcome review không phải lời khuyên đầu tư. Kết quả lịch sử không bảo đảm kết quả tương lai. Người đọc không được dùng số liệu trong luận văn làm căn cứ duy nhất cho giao dịch. Mọi quyết định thực tế cần đánh giá độc lập về rủi ro, thanh khoản, pháp lý, chi phí, dữ liệu và hoàn cảnh cá nhân.

---

## DANH SÁCH ARTIFACT CHÍNH

- `multi_llm_evidence_extraction/reports/semantic_news_materiality_study_report.md`
- `multi_llm_evidence_extraction/reports/claim_vs_evidence_table.md`
- `multi_llm_evidence_extraction/reports/annotation_agreement_report.md`
- `multi_llm_evidence_extraction/reports/event_window_stat_tests_report.md`
- `multi_llm_evidence_extraction/reports/ml_outperform_experiment_report.md`
- `multi_llm_evidence_extraction/reports/topk_backtest_with_cost_report.md`
- `multi_llm_evidence_extraction/reports/outcome_review_report.md`
- `multi_llm_evidence_extraction/reports/manual_sanity_check_report.md`
- `reports/H1_experiment_report.md`
- `reports/decision_support/validation_consistency_check.md`
- `reports/decision_support/generated/generated_summary.md`
- `reports/decision_support/generated/router_claude2_llm_rubric_summary.md`
- `reports/decision_support/generated/router_claude2_llm_rubric_scores.csv`
- `reports/decision_support/generated/evidence_packs_initial.json`
- `reports/decision_support/generated/evidence_packs_ml_only.json`
- `reports/decision_support/generated/llm_cards_ml_only.jsonl`
- `reports/decision_support/generated/llm_cards_full_evidence.jsonl`
- `reports/decision_support/generated/llm_rubric_scores.csv`
