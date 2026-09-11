"""Factory for the intentionally small, aggregate-only locked V6 release fixture."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from research_ui_v2.contracts import PUBLIC_RELEASE_SCHEMA_VERSION


# H2's locked primary comparison is intentionally represented as unsupported.  The
# values are load-bearing public aggregate facts, not a claim of confirmation.
LOCKED_H2_RESULT = {
    "result_id": "C-A RF BA",
    "contrast": "C-A",
    "model": "Random Forest",
    "metric": "balanced_accuracy",
    "estimate": -0.0042486,
    "ci_lower": -0.0112006,
    "ci_upper": 0.0018953,
    "bh_adjusted_p_value": 0.229977,
}


def public_release_fixture() -> dict[str, Any]:
    """Return a fresh strict release fixture containing aggregate results only."""

    payload: dict[str, Any] = {
        "schema_version": PUBLIC_RELEASE_SCHEMA_VERSION,
        "artifact_id": "v6-study-results-public-release",
        "release_id": "v6-locked-study-results-fixture",
        "generated_at_utc": "2026-09-05T00:00:00Z",
        "aggregate_only": True,
        "research_only": True,
        "record_count": 7,
        "claims": [
            {
                "claim_id": "H1-keyword-comparison",
                "analysis_state": "primary",
                "status": "inconclusive",
                "title": {
                    "vi": "H1 — Biểu diễn từ khóa so với kỹ thuật",
                    "en": "H1 — Keyword representation versus technical baseline",
                },
                "statement": {
                    "vi": "Phát biểu chính được giữ trong phạm vi kết quả tổng hợp đã khóa; không được diễn giải thành quan hệ nhân quả hoặc hiệu quả đầu tư.",
                    "en": "The primary statement remains limited to the locked aggregate result and is not interpreted as causality or investment performance.",
                },
                "source_id": "locked-primary-comparisons",
                "gate_id": None,
                "result": None,
                "locked": True,
            },
            {
                "claim_id": "H2-semantic-comparison",
                "analysis_state": "confirmation",
                "status": "unsupported",
                "title": {
                    "vi": "H2 — Biểu diễn ngữ nghĩa so với kỹ thuật",
                    "en": "H2 — Semantic representation versus technical baseline",
                },
                "statement": {
                    "vi": "So sánh C-A RF BA đã khóa không được ủng hộ: ước lượng âm, khoảng tin cậy bao gồm 0 và giá trị p đã hiệu chỉnh BH không đạt cổng xác nhận.",
                    "en": "The locked C-A RF BA comparison is unsupported: the estimate is negative, the confidence interval includes 0, and the BH-adjusted p-value does not meet the confirmation gate.",
                },
                "source_id": "locked-primary-comparisons",
                "gate_id": "H2-locked-confirmation-gate",
                "result": LOCKED_H2_RESULT,
                "locked": True,
            },
        ],
        "gates": [
            {
                "gate_id": "H2-locked-confirmation-gate",
                "claim_id": "H2-semantic-comparison",
                "analysis_state": "confirmation",
                "status": "not_met",
                "label": {
                    "vi": "Cổng xác nhận H2 đã khóa trước",
                    "en": "Pre-specified locked H2 confirmation gate",
                },
                "rationale": {
                    "vi": "Không đạt: khoảng tin cậy bao gồm 0 và BH = 0.229977; kết quả không được gọi là đã xác nhận.",
                    "en": "Not met: the confidence interval includes 0 and BH = 0.229977; the result is not called confirmed.",
                },
                "source_id": "locked-primary-comparisons",
            }
        ],
        "source_statuses": [
            {
                "source_id": "locked-primary-comparisons",
                "status": "locked",
                "scope": "aggregate_public",
                "label": {"vi": "Bảng so sánh chính đã khóa", "en": "Locked primary comparison table"},
                "note": {
                    "vi": "Chỉ tổng hợp chỉ số, khoảng tin cậy và p đã hiệu chỉnh trong phạm vi phát hành công khai.",
                    "en": "Contains only aggregate metrics, confidence intervals, and adjusted p-values within the public-release scope.",
                },
                "contains_raw_records": False,
                "contains_credentials": False,
                "contains_prompts": False,
                "contains_full_local_paths": False,
            }
        ],
        "subgroup_results": [
            {
                "subgroup_id": "coverage-subgroup-summary",
                "analysis_state": "exploratory",
                "status": "descriptive",
                "label": {"vi": "Nhóm theo độ phủ tin tức", "en": "News-coverage subgroup"},
                "note": {
                    "vi": "Chỉ mô tả theo nhóm; không thay thế mẫu chính, không xác nhận giả thuyết và không suy luận nhân quả.",
                    "en": "Descriptive subgroup context only; it does not replace the primary sample, confirm a hypothesis, or support causal inference.",
                },
                "source_id": "locked-primary-comparisons",
                "result": None,
            }
        ],
        "approved_presets": [
            {
                "preset_id": "locked-h2-review",
                "label": {"vi": "Rà soát H2 đã khóa", "en": "Locked H2 review"},
                "description": {
                    "vi": "Chỉ xem phát biểu H2 và cổng xác nhận đã khóa. Không chạy mã, mô hình hoặc tác vụ dữ liệu.",
                    "en": "Views only the locked H2 statement and confirmation gate. It does not run code, models, or data tasks.",
                },
                "view": "confirmation",
                "claim_ids": ["H2-semantic-comparison"],
                "execution": "non_executing",
                "fixed": True,
            },
            {
                "preset_id": "primary-scope-review",
                "label": {"vi": "Phạm vi kết quả chính", "en": "Primary-result scope"},
                "description": {
                    "vi": "Xem phát biểu chính đã công bố và giới hạn diễn giải; không có điều khiển thực thi.",
                    "en": "Views the published primary statement and interpretation limits; there are no execution controls.",
                },
                "view": "primary",
                "claim_ids": ["H1-keyword-comparison"],
                "execution": "non_executing",
                "fixed": True,
            },
        ],
        "limitations": [
            {
                "vi": "Release này chỉ là fixture tổng hợp nhỏ phục vụ xem xét Dashboard V2; không phải dữ liệu thay thế cho báo cáo nghiên cứu đầy đủ.",
                "en": "This release is a small aggregate fixture for Dashboard V2 review; it is not a substitute for the full research report.",
            },
            {
                "vi": "Không suy luận alpha, quan hệ nhân quả, khuyến nghị đầu tư hoặc hiệu quả triển khai từ các kết quả này.",
                "en": "Do not infer alpha, causality, investment advice, or deployable performance from these results.",
            },
        ],
    }
    return deepcopy(payload)
