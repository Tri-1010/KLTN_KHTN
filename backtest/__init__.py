"""``backtest`` package — tầng đánh giá đầu tư chồng lên pipeline dự báo kỹ thuật.

Gói này biến kết quả *độ chính xác dự báo* của Technical_Model (huấn luyện qua
``pipeline/task10_train.py``) thành kết quả *giá trị đầu tư thực tế* (lợi nhuận,
Sharpe, drawdown), theo đúng đặc thù thị trường cơ sở Việt Nam (long-only, phí
giao dịch VN). Gói tách biệt hoàn toàn với ``pipeline/`` (production) và
``experiments/`` (thí nghiệm văn bản) — chỉ tái sử dụng pipeline như một thư
viện, không sửa hành vi mặc định (Req 10.1, 10.2).
"""
