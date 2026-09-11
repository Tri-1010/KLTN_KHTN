"""Locale catalog and safe display helpers for Dashboard V2."""

from __future__ import annotations

from typing import Literal

from .contracts import BilingualText


Locale = Literal["vi", "en"]
SUPPORTED_LOCALES: tuple[Locale, ...] = ("vi", "en")

LOCALE_CATALOG: dict[str, dict[Locale, str]] = {
    "app_title": {"vi": "Bảng điều khiển kết quả nghiên cứu V6", "en": "V6 Study Results Dashboard"},
    "app_subtitle": {
        "vi": "Bản công bố tổng hợp công khai; chỉ phục vụ nghiên cứu.",
        "en": "Aggregate public release; for research use only.",
    },
    "locale_label": {"vi": "Ngôn ngữ / Language", "en": "Language / Ngôn ngữ"},
    "release_status": {"vi": "Trạng thái công bố", "en": "Release status"},
    "aggregate_only": {"vi": "Chỉ dữ liệu tổng hợp công khai", "en": "Aggregate public data only"},
    "locked": {"vi": "Đã khóa", "en": "Locked"},
    "primary": {"vi": "Kết quả chính", "en": "Primary results"},
    "exploratory": {"vi": "Kết quả thăm dò", "en": "Exploratory results"},
    "confirmation": {"vi": "Xác nhận", "en": "Confirmation"},
    "claims": {"vi": "Các phát biểu nghiên cứu", "en": "Study claims"},
    "gates": {"vi": "Cổng xác nhận", "en": "Confirmation gates"},
    "subgroups": {"vi": "Phân tích theo nhóm", "en": "Subgroup analyses"},
    "source_status": {"vi": "Nguồn, trạng thái và phạm vi", "en": "Sources, status, and scope"},
    "limitations": {"vi": "Giới hạn diễn giải", "en": "Interpretation limitations"},
    "provenance": {"vi": "Truy xuất và toàn vẹn", "en": "Provenance and integrity"},
    "operate_preview": {"vi": "Operate Preview", "en": "Operate Preview"},
    "non_executing": {
        "vi": "Chế độ này không thực thi: chỉ chuyển giữa các preset đã được phê duyệt.",
        "en": "This mode is non-executing: it only switches among approved fixed presets.",
    },
    "preset_label": {"vi": "Preset đã phê duyệt", "en": "Approved preset"},
    "metric_estimate": {"vi": "Chênh lệch BA", "en": "BA difference"},
    "ci_95": {"vi": "Khoảng tin cậy", "en": "Confidence interval"},
    "bh_p": {"vi": "p đã hiệu chỉnh BH", "en": "BH-adjusted p-value"},
    "analysis_state": {"vi": "Trạng thái phân tích", "en": "Analysis state"},
    "claim_status": {"vi": "Trạng thái phát biểu", "en": "Claim status"},
    "table_equivalent": {"vi": "Bảng dữ liệu tương đương", "en": "Equivalent data table"},
    "not_investment_advice": {
        "vi": "Không phải khuyến nghị đầu tư; không suy luận alpha, quan hệ nhân quả hoặc hiệu quả đầu tư.",
        "en": "Not investment advice; no inference about alpha, causality, or investment performance.",
    },
    "unsupported": {"vi": "Không được ủng hộ", "en": "Unsupported"},
    "not_confirmed": {"vi": "Chưa được xác nhận", "en": "Not confirmed"},
    "descriptive": {"vi": "Mô tả", "en": "Descriptive"},
    "not_estimable": {"vi": "Không ước lượng được", "en": "Not estimable"},
    "inconclusive": {"vi": "Chưa kết luận", "en": "Inconclusive"},
    "supported": {"vi": "Được hỗ trợ", "en": "Supported"},
    "met": {"vi": "Đạt", "en": "Met"},
    "not_met": {"vi": "Không đạt", "en": "Not met"},
    "not_assessed": {"vi": "Chưa đánh giá", "en": "Not assessed"},
    "available": {"vi": "Sẵn có", "en": "Available"},
    "limited": {"vi": "Có giới hạn", "en": "Limited"},
    "runtime_integrity": {"vi": "Kiểm tra toàn vẹn runtime", "en": "Runtime integrity check"},
    "passed": {"vi": "Đã đạt", "en": "Passed"},
    "release_id": {"vi": "Mã công bố", "en": "Release ID"},
    "bundle_id": {"vi": "Mã bundle", "en": "Bundle ID"},
    "member_count": {"vi": "Số thành viên runtime", "en": "Runtime member count"},
    "schema_version": {"vi": "Phiên bản schema", "en": "Schema version"},
    "footer": {
        "vi": "Dashboard V2 hiển thị duy nhất public release tổng hợp đã kiểm tra hash.",
        "en": "Dashboard V2 renders only the hash-checked aggregate public release.",
    },
}


def validate_locale_catalog(catalog: dict[str, dict[str, str]] = LOCALE_CATALOG) -> list[str]:
    """Return deterministic completeness errors for every global UI message."""

    errors: list[str] = []
    for key in sorted(catalog):
        entry = catalog[key]
        if set(entry) != set(SUPPORTED_LOCALES):
            errors.append(f"{key}: expected locales {SUPPORTED_LOCALES}, found {tuple(sorted(entry))}")
            continue
        for locale in SUPPORTED_LOCALES:
            if not isinstance(entry[locale], str) or not entry[locale].strip():
                errors.append(f"{key}.{locale}: missing translated text")
    return errors


def tr(key: str, locale: Locale) -> str:
    """Look up a known global UI label and fail closed for an incomplete catalog."""

    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")
    try:
        value = LOCALE_CATALOG[key][locale]
    except KeyError as exc:
        raise KeyError(f"Missing V2 locale key: {key}") from exc
    if not value.strip():
        raise ValueError(f"Blank V2 locale key: {key}.{locale}")
    return value


def bilingual_text(value: BilingualText | dict[str, str], locale: Locale) -> str:
    """Select locale text from a strict release-provided bilingual pair."""

    if isinstance(value, BilingualText):
        return getattr(value, locale)
    return BilingualText.model_validate(value).model_dump()[locale]


def status_label(status: str, locale: Locale) -> str:
    """Translate declared state/status tokens without inferring a conclusion."""

    return tr(status, locale) if status in LOCALE_CATALOG else status
