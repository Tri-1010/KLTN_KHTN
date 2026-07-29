# Evidence Pack Schema

## 1. Mục đích

Evidence pack là gói dữ liệu point-in-time dùng làm input duy nhất cho LLM khi tạo decision card. Mục tiêu là khóa dữ liệu đầu vào, giảm hallucination và tránh rò rỉ thông tin tương lai.

LLM chỉ được diễn giải những gì có trong evidence pack. Nếu evidence thiếu, LLM phải ghi rõ thiếu dữ liệu thay vì suy đoán.

## 2. Nguyên tắc dữ liệu

1. Chỉ dùng dữ liệu có tại hoặc trước `decision_date`.
2. Không chứa realized return tương lai.
3. Không chứa nhãn `label_basic` hoặc outcome của kỳ sau.
4. Không chứa bài báo sau `decision_date`.
5. Mỗi luận điểm định tính phải tham chiếu `evidence_id`.
6. Evidence pack cần lưu nguyên bản để phục vụ audit và tái lập.

## 3. Schema đề xuất

```json
{
  "decision_id": "2025Q1_FPT_001",
  "ticker": "FPT",
  "decision_date": "2025-03-31",
  "period_id": "2025Q1",
  "holding_horizon": "next_quarter",
  "universe": "HOSE-80",
  "ml_signal": {
    "model_name": "LightGBM_Config_A",
    "train_cutoff": "2025Q1",
    "pred_proba_up": 0.73,
    "pred_label": 1,
    "rank_in_period": 3,
    "signal_class": "Buy Candidate"
  },
  "technical_snapshot": {
    "rsi_end_q": 64.2,
    "macd_hist_mean_q": 0.18,
    "price_vs_sma20": 0.045,
    "return_q": 0.082,
    "return_prev_q": 0.031,
    "volatility_q": 0.21,
    "volume_change_q": 0.12
  },
  "top_drivers": [
    {
      "feature": "rsi_end_q",
      "importance_type": "SHAP_or_feature_importance",
      "direction": "supports_up_signal",
      "explanation": "RSI cuối kỳ nằm vùng tích cực nhưng chưa quá mua."
    },
    {
      "feature": "macd_hist_mean_q",
      "importance_type": "SHAP_or_feature_importance",
      "direction": "supports_up_signal",
      "explanation": "MACD histogram trung bình dương, phản ánh động lượng cải thiện."
    }
  ],
  "news_evidence": [
    {
      "evidence_id": "N001",
      "published_at": "2025-03-18",
      "source": "CafeF",
      "title": "FPT công bố kết quả kinh doanh tăng trưởng",
      "summary": "Tin liên quan đến kết quả kinh doanh và triển vọng doanh nghiệp.",
      "article_summary": "Tóm tắt ngắn từ nội dung bài viết đã crawl.",
      "key_facts": [
        {
          "fact_id": "N001-F01",
          "fact": "Doanh thu tăng 18% so với cùng kỳ.",
          "evidence_quote": "Doanh thu tăng 18% so với cùng kỳ.",
          "fact_type": "earnings",
          "direction": "support_or_context",
          "confidence": "medium"
        }
      ],
      "risk_flags": [],
      "event_type": "earnings",
      "match_confidence": "exact",
      "full_text_available": true,
      "full_text_chars": 3456,
      "full_text_ref": "sha256-content-hash-or-url",
      "full_text_excerpt": "Trích đoạn ngắn phục vụ audit, không phải toàn văn.",
      "content_hash": "sha256...",
      "extraction_status": "ok",
      "relevance_hint": "ticker_mentioned"
    }
  ],
  "data_quality_flags": {
    "news_coverage": "medium",
    "ticker_matching_confidence": "high",
    "has_recent_news": true,
    "missing_fields": []
  },
  "guardrails": {
    "no_future_return_included": true,
    "news_cutoff": "2025-03-31",
    "llm_must_cite_evidence": true,
    "not_investment_advice": true
  }
}
```

## 4. Signal class

| Class | Điều kiện gợi ý | Ý nghĩa |
|---|---|---|
| Buy Candidate | `pred_label = 1` và rank trong Top-K | Ứng viên xem xét mua |
| Watchlist | `pred_label = 1` nhưng rank ngoài Top-K hoặc evidence yếu | Theo dõi thêm |
| Avoid | `pred_label = 0` hoặc tín hiệu suy yếu | Không ưu tiên |
| Review Required | Sau decision, trigger monitoring bị kích hoạt | Cần xem xét lại |

## 5. Data quality flags

| Flag | Ý nghĩa |
|---|---|
| `news_coverage` | `none`, `low`, `medium`, `high` theo số tin gần decision date |
| `ticker_matching_confidence` | `low`, `medium`, `high` |
| `has_recent_news` | Có tin trong lookback window hay không |
| `full_text_coverage` | Số tin có full text đã crawl trong pack |
| `summary_coverage` | Số tin có `article_summary` |
| `key_fact_coverage` | Số tin có `key_facts` |
| `num_title_only_articles` | Số tin chỉ còn title/description do crawl thất bại hoặc bị giới hạn |
| `missing_fields` | Các trường thiếu như source, date, summary |

## 6. Lưu ý chống leakage

- `decision_date` phải là ranh giới cắt dữ liệu.
- `news_evidence.published_at` phải nhỏ hơn hoặc bằng `decision_date`.
- `technical_snapshot` chỉ tính từ dữ liệu đến kỳ hiện tại.
- `outcome_review` không nằm trong evidence pack ban đầu; nếu cần, lưu ở file riêng sau holding period.
- `full_text` toàn văn không đưa vào prompt LLM mặc định; chỉ dùng `article_summary`, `key_facts`, `risk_flags`, `full_text_excerpt` ngắn và `full_text_ref`/`content_hash` để audit.
- Nếu cần phân tích sâu một tin quan trọng, có thể mở full text theo `full_text_ref` và truncate riêng ngoài initial prompt mặc định.

## 7. Mapping từ kết quả hiện có

| Thành phần evidence pack | Nguồn hiện có |
|---|---|
| `pred_proba_up`, `pred_label`, `period_return` | `reports/signals.csv` hoặc `backtest/signals.py` |
| Technical features | `data/features/technical_features.csv` |
| Feature importance/SHAP | `reports/technical_ml_backtest_report.md`, `pipeline/task11_shap.py` outputs |
| News evidence | Ưu tiên `data/news/enriched/all_news_enriched.csv`, fallback `data/news/processed/all_news_processed.csv`, rồi `data/news/matched/all_news_matched.csv` |
| Full-text coverage report | `reports/decision_support/generated/news_fulltext_coverage.csv` |
| Monitoring events | `reports/decision_support/generated/monitoring_events.csv`, `monitoring_timeline.json` |
| Leakage guardrails | `reports/leakage_audit.md` |
| Market assumptions | `backtest/strategy.py` |
