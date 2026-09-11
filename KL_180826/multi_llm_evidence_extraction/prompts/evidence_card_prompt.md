# Evidence card prompt v1

Bạn tạo evidence card phục vụ phân tích, không phải khuyến nghị đầu tư.

Chỉ dùng các trường được cung cấp trong evidence payload. Không dùng outcome/future return/realized return trong card ban đầu.

Card cần có:

1. `ticker`, `article_date`, `news_id`.
2. Tóm tắt evidence.
3. Bảng claim:
   - claim_id
   - claim_text
   - relevance/materiality/direction
   - evidence_span
   - confidence
4. Data quality flags.
5. What would make this evidence weaker.
6. Limitations/disclaimer: research support only, not buy/sell recommendation.

Không viết câu kiểu chắc chắn tăng/giảm giá. Không dự báo giá mục tiêu.

Input payload:

```json
{{EVIDENCE_PAYLOAD}}
```
