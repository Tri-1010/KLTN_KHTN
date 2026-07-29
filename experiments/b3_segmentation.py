"""Segmentation_Analyzer — B3: phân tích theo phân khúc ngành & vốn hóa (Req 10).

Thí nghiệm B3 kiểm tra liệu tín hiệu văn bản (Config_C so với Config_A) có giá
trị dự báo *khác nhau* giữa các phân khúc thị trường không — từng ngành, và
large-cap so với mid-cap. Với mỗi phân khúc, module này:

- Lọc dữ liệu merged theo các ticker thuộc phân khúc, rồi **huấn luyện lại**
  Config_A/Config_B/Config_C với **cùng Train_Cutoff và cùng quy trình chia
  thời gian** (không rò rỉ), tính ``Delta_CA = BA(Config_C) − BA(Config_A)`` cho
  cả 4 thuật toán (LightGBM, Random_Forest, XGBoost, Logistic_Regression)
  (Req 10.3).
- **Kiểm định ý nghĩa từ khóa** (chi-square/Fisher, Mann-Whitney, logistic đơn
  biến) trên riêng dữ liệu của phân khúc (in-sample), rồi áp dụng hiệu chỉnh
  BH-FDR **trong phạm vi phân khúc đó** (Req 10.4).
- **Báo cáo số mẫu** (``n_samples``) và số ticker mỗi phân khúc (Req 10.5).
- Ghi kết quả ra ``reports/segmentation_analysis.csv`` và
  ``reports/segmentation_keyword_sig.csv`` (Req 10.6).

Toàn bộ tính toán tái dùng các thành phần đã kiểm thử:
:func:`experiments.common.segments.assign_segments` (ánh xạ ticker→phân khúc),
:func:`pipeline.task10_train.run_configs_return_predictions` (retrain theo cùng
pipeline, hỗ trợ lọc theo ticker), và các hàm kiểm định thống kê + BH-FDR trong
``pipeline.experiment_keyword_significance``.

Xử lý lỗi (Req 10.5, mục "Segmentation" của thiết kế): một phân khúc có quá ít
mẫu (một lớp nhãn, hoặc dưới ngưỡng tối thiểu ``min_samples``) sẽ **không** được
huấn luyện, nhưng vẫn được báo cáo ``n_samples``/``n_tickers`` cùng ghi chú
``"insufficient power"`` và ``ba``/``delta`` = NaN.

_Requirements: 10.3, 10.4, 10.5, 10.6_
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from experiments.common.segments import SegmentInfo, assign_segments
from pipeline.experiment_keyword_significance import (
    apply_bh_correction,
    build_keyword_label_dataset,
    chi_square_or_fisher,
    logistic_univariate,
    mann_whitney_test,
)
from pipeline.task8_keywords import get_curated_keywords
from pipeline.task10_train import (
    KW_FEATURES_PATH,
    LABELS_PATH,
    TECH_FEATURES_PATH,
    load_and_merge_data,
    run_configs_return_predictions,
)

logger = logging.getLogger(__name__)

__all__ = [
    "SEGMENTATION_ANALYSIS_PATH",
    "SEGMENTATION_KEYWORD_SIG_PATH",
    "REPORT_MODELS",
    "DEFAULT_CUTOFF",
    "build_segment_list",
    "compute_segment_deltas",
    "compute_segment_keyword_significance",
    "run_segmentation_analysis",
    "build_b3_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn artifact & hằng số (Req 10.6)
# ---------------------------------------------------------------------------

SEGMENTATION_ANALYSIS_PATH = "reports/segmentation_analysis.csv"
SEGMENTATION_KEYWORD_SIG_PATH = "reports/segmentation_keyword_sig.csv"

#: Bốn thuật toán báo cáo — trùng bộ thuật toán của Comparison_Reporter.
REPORT_MODELS: Tuple[str, ...] = (
    "LightGBM",
    "Random_Forest",
    "XGBoost",
    "Logistic_Regression",
)

#: Train_Cutoff mặc định theo thời gian (Req 4.1). Trùng mặc định của pipeline.
DEFAULT_CUTOFF = "2025Q1"

#: Ngưỡng số mẫu tối thiểu để huấn luyện một phân khúc. Mặc định 0 → không áp
#: ngưỡng cứng; hành vi bỏ-qua được điều khiển bởi guard ValueError của
#: ``run_configs_return_predictions`` (phân khúc rỗng/một-lớp-nhãn). Người dùng
#: có thể đặt >0 để chủ động bỏ qua các phân khúc quá nhỏ.
DEFAULT_MIN_SAMPLES = 0


# ---------------------------------------------------------------------------
# Liệt kê phân khúc (Req 10.3)
# ---------------------------------------------------------------------------


def build_segment_list(
    segments: Dict[str, SegmentInfo],
) -> List[Tuple[str, str, List[str]]]:
    """Dựng danh sách phân khúc cần phân tích từ ánh xạ ticker→SegmentInfo.

    Sinh ra:

    - một phân khúc cho mỗi ngành riêng biệt: ``("sector", <sector>, tickers)``;
    - hai phân khúc vốn hóa: ``("cap_group", "large_cap", tickers)`` và
      ``("cap_group", "mid_cap", tickers)``.

    Các ticker trong mỗi phân khúc được sắp xếp ổn định để đầu ra tất định.

    Args:
        segments: Dict ``ticker -> SegmentInfo`` (từ :func:`assign_segments`).

    Returns:
        Danh sách bộ ``(segment_type, segment_name, tickers)``, sắp theo
        ``segment_type`` rồi ``segment_name`` để tất định.
    """
    sector_map: Dict[str, List[str]] = {}
    cap_map: Dict[str, List[str]] = {}

    for ticker, info in segments.items():
        sector_map.setdefault(info.sector, []).append(ticker)
        cap_map.setdefault(info.cap_group, []).append(ticker)

    segment_list: List[Tuple[str, str, List[str]]] = []

    for sector in sorted(sector_map):
        segment_list.append(("sector", sector, sorted(sector_map[sector])))

    for cap_group in sorted(cap_map):
        segment_list.append(("cap_group", cap_group, sorted(cap_map[cap_group])))

    return segment_list


# ---------------------------------------------------------------------------
# Delta_CA theo phân khúc (Req 10.3)
# ---------------------------------------------------------------------------


def compute_segment_deltas(
    segment_type: str,
    segment_name: str,
    segment_tickers: List[str],
    n_samples: int,
    n_tickers: int,
    cutoff: str,
    tech_path: str,
    kw_path: str,
    labels_path: str,
    models: Tuple[str, ...] = REPORT_MODELS,
) -> List[Dict[str, object]]:
    """Tính ``Delta_CA`` cho từng thuật toán trên một phân khúc (Req 10.3).

    Với mỗi thuật toán trong ``models``, huấn luyện lại Config_A/Config_B/
    Config_C **chỉ trên các ticker của phân khúc** qua
    :func:`run_configs_return_predictions` (cùng Train_Cutoff, cùng chia thời
    gian, cùng pipeline), rồi tính balanced accuracy của Config_A và Config_C
    trên cùng tập test, với ``delta_ca = ba_config_c − ba_config_a``.

    Xử lý lỗi (Req 10.5): nếu retrain ném :class:`ValueError` (phân khúc quá ít
    mẫu hoặc chỉ một lớp nhãn), trả về một dòng/thuật toán với ba/delta = NaN và
    ghi chú ``"insufficient power"``.

    Args:
        segment_type: ``"sector"`` hoặc ``"cap_group"``.
        segment_name: Tên phân khúc (ví dụ ``"Banking"``, ``"large_cap"``).
        segment_tickers: Danh sách ticker của phân khúc.
        n_samples: Số mẫu (ticker×quarter) của phân khúc.
        n_tickers: Số ticker của phân khúc.
        cutoff: Train_Cutoff theo thời gian.
        tech_path: Đường dẫn đặc trưng kỹ thuật.
        kw_path: Đường dẫn đặc trưng từ khóa.
        labels_path: Đường dẫn nhãn.
        models: Bộ thuật toán cần báo cáo (mặc định :data:`REPORT_MODELS`).

    Returns:
        Danh sách dict (mỗi thuật toán một dòng) khớp schema
        ``segmentation_analysis.csv`` (Req 10.6).
    """
    rows: List[Dict[str, object]] = []

    for model_name in models:
        base_row: Dict[str, object] = {
            "segment_type": segment_type,
            "segment_name": segment_name,
            "n_samples": n_samples,
            "n_tickers": n_tickers,
            "model": model_name,
        }
        try:
            preds = run_configs_return_predictions(
                tech_path=tech_path,
                kw_path=kw_path,
                labels_path=labels_path,
                cutoff=cutoff,
                configs_to_run=("Config_A", "Config_B", "Config_C"),
                model_name=model_name,
                tickers=segment_tickers,
            )
            y_test = preds["y_test"]
            pred_by_config = preds["pred_by_config"]

            ba_config_a = float(
                balanced_accuracy_score(y_test, pred_by_config["Config_A"])
            )
            ba_config_b = float(
                balanced_accuracy_score(y_test, pred_by_config["Config_B"])
            )
            ba_config_c = float(
                balanced_accuracy_score(y_test, pred_by_config["Config_C"])
            )
            base_row.update(
                {
                    "ba_config_a": ba_config_a,
                    "ba_config_b": ba_config_b,
                    "ba_config_c": ba_config_c,
                    "delta_ca": ba_config_c - ba_config_a,
                    "note": "",
                }
            )
        except ValueError as exc:
            logger.warning(
                "Bỏ qua huấn luyện phân khúc %s='%s' cho %s (insufficient "
                "power): %s",
                segment_type,
                segment_name,
                model_name,
                exc,
            )
            base_row.update(
                {
                    "ba_config_a": np.nan,
                    "ba_config_b": np.nan,
                    "ba_config_c": np.nan,
                    "delta_ca": np.nan,
                    "note": "insufficient power",
                }
            )
        rows.append(base_row)

    return rows


# ---------------------------------------------------------------------------
# Kiểm định ý nghĩa từ khóa trong phân khúc + BH-FDR (Req 10.4)
# ---------------------------------------------------------------------------


def compute_segment_keyword_significance(
    seg_merged: pd.DataFrame,
    keywords: List[str],
    direction_map: Dict[str, str],
    segment_type: str,
    segment_name: str,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Kiểm định ý nghĩa từ khóa + BH-FDR trong một phân khúc (Req 10.4).

    Phản chiếu :func:`pipeline.experiment_keyword_significance.run_keyword_significance`
    nhưng giới hạn trong ``seg_merged`` (in-sample) và áp dụng BH-FDR **riêng cho
    phân khúc này**. Schema đầu ra trùng ``keyword_significance.csv`` cộng thêm
    ``segment_type``, ``segment_name`` và ``n_samples`` (Req 10.4, 10.6).

    Nếu phân khúc thoái hóa (chỉ một lớp nhãn), các dòng từ khóa được ghi với
    p-value = NaN và ``significant_any=False`` (kiểm định không chạy được).

    Args:
        seg_merged: Tập merged đã lọc theo ticker của phân khúc.
        keywords: Danh sách phẳng toàn bộ từ khóa curated.
        direction_map: Ánh xạ keyword → hướng (positive/negative/neutral).
        segment_type: ``"sector"`` hoặc ``"cap_group"``.
        segment_name: Tên phân khúc.
        alpha: Mức ý nghĩa cho BH-FDR (mặc định 0.05).

    Returns:
        DataFrame kết quả kiểm định từ khóa của phân khúc.
    """
    n_samples = len(seg_merged)
    dataset_df, excluded_kws = build_keyword_label_dataset(seg_merged, keywords)

    included_keywords = [
        kw
        for kw in keywords
        if kw not in excluded_kws and f"occurrence_{kw}" in dataset_df.columns
    ]

    labels = dataset_df["label_basic"].to_numpy().astype(int)
    degenerate = len(np.unique(labels)) < 2
    if degenerate:
        logger.warning(
            "Phân khúc %s='%s' chỉ có một lớp nhãn — ghi p-value NaN cho các "
            "kiểm định từ khóa.",
            segment_type,
            segment_name,
        )

    rows: List[Dict[str, object]] = []

    for kw in included_keywords:
        occ_col = f"occurrence_{kw}"
        norm_col = f"kw_norm_{kw}"

        occurrence = dataset_df[occ_col].to_numpy().astype(int)
        n_occ = int(occurrence.sum())

        if norm_col in dataset_df.columns:
            norm_freq = dataset_df[norm_col].to_numpy().astype(float)
        else:
            norm_freq = np.zeros(len(occurrence), dtype=float)

        if degenerate:
            chi_stat = chi_p_raw = np.nan
            chi_test_used = "degenerate"
            mw_stat = mw_p_raw = np.nan
            logit_coef = logit_ci_lower = logit_ci_upper = logit_p_raw = np.nan
        else:
            norm_up = norm_freq[labels == 1]
            norm_not_up = norm_freq[labels == 0]

            chi_stat, chi_p_raw, chi_test_used = chi_square_or_fisher(
                occurrence, labels
            )
            mw_stat, mw_p_raw = mann_whitney_test(norm_up, norm_not_up)
            (
                logit_coef,
                logit_ci_lower,
                logit_ci_upper,
                logit_p_raw,
            ) = logistic_univariate(occurrence, labels)

        rows.append(
            {
                "segment_type": segment_type,
                "segment_name": segment_name,
                "n_samples": n_samples,
                "keyword": kw,
                "direction": direction_map.get(kw, "unknown"),
                "n_occurrences": n_occ,
                "n_excluded": 0,
                "chi_statistic": chi_stat,
                "chi_p_raw": chi_p_raw,
                "chi_p_adj": np.nan,
                "chi_test_used": chi_test_used,
                "mw_statistic": mw_stat,
                "mw_p_raw": mw_p_raw,
                "mw_p_adj": np.nan,
                "logit_coef": logit_coef,
                "logit_ci_lower": logit_ci_lower,
                "logit_ci_upper": logit_ci_upper,
                "logit_p_raw": logit_p_raw,
                "logit_p_adj": np.nan,
                "significant_chi": False,
                "significant_mw": False,
                "significant_logit": False,
                "significant_any": False,
            }
        )

    # Các từ khóa bị loại (zero occurrences) — dòng thông tin.
    for ek in excluded_kws:
        rows.append(
            {
                "segment_type": segment_type,
                "segment_name": segment_name,
                "n_samples": n_samples,
                "keyword": ek,
                "direction": direction_map.get(ek, "unknown"),
                "n_occurrences": 0,
                "n_excluded": 1,
                "chi_statistic": np.nan,
                "chi_p_raw": np.nan,
                "chi_p_adj": np.nan,
                "chi_test_used": "excluded",
                "mw_statistic": np.nan,
                "mw_p_raw": np.nan,
                "mw_p_adj": np.nan,
                "logit_coef": np.nan,
                "logit_ci_lower": np.nan,
                "logit_ci_upper": np.nan,
                "logit_p_raw": np.nan,
                "logit_p_adj": np.nan,
                "significant_chi": False,
                "significant_mw": False,
                "significant_logit": False,
                "significant_any": False,
            }
        )

    seg_sig_df = pd.DataFrame(rows)
    if seg_sig_df.empty:
        return seg_sig_df

    # BH-FDR riêng cho phân khúc, áp dụng từng loại kiểm định (Req 10.4).
    included_mask = seg_sig_df["n_excluded"] == 0
    if included_mask.any():
        for raw_col, adj_col in [
            ("chi_p_raw", "chi_p_adj"),
            ("mw_p_raw", "mw_p_adj"),
            ("logit_p_raw", "logit_p_adj"),
        ]:
            p_raw = seg_sig_df.loc[included_mask, raw_col].to_numpy()
            seg_sig_df.loc[included_mask, adj_col] = apply_bh_correction(
                p_raw, alpha=alpha
            )

    seg_sig_df["significant_chi"] = seg_sig_df["chi_p_adj"] < alpha
    seg_sig_df["significant_mw"] = seg_sig_df["mw_p_adj"] < alpha
    seg_sig_df["significant_logit"] = seg_sig_df["logit_p_adj"] < alpha
    seg_sig_df["significant_any"] = (
        seg_sig_df["significant_chi"]
        | seg_sig_df["significant_mw"]
        | seg_sig_df["significant_logit"]
    )

    return seg_sig_df


# ---------------------------------------------------------------------------
# Runner chính (Req 10.3–10.6)
# ---------------------------------------------------------------------------


def run_segmentation_analysis(
    cutoff: str = DEFAULT_CUTOFF,
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
    min_samples: int = DEFAULT_MIN_SAMPLES,
    alpha: float = 0.05,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Chạy toàn bộ phân tích B3 theo phân khúc và ghi hai báo cáo (Req 10.3–10.6).

    Với mỗi phân khúc (từng ngành, và large-cap/mid-cap):

    1. Xác định các ticker và tập merged con của phân khúc; báo cáo ``n_samples``
       và ``n_tickers`` (Req 10.5).
    2. Huấn luyện lại Config_A/B/C cho 4 thuật toán, tính Delta_CA (Req 10.3),
       với xử lý lỗi cho phân khúc quá nhỏ (Req 10.5).
    3. Kiểm định ý nghĩa từ khóa + BH-FDR trong phân khúc (Req 10.4).

    Ghi ``segmentation_analysis.csv`` và ``segmentation_keyword_sig.csv`` (Req
    10.6) rồi trả về ``(analysis_df, keyword_sig_df)``.

    Args:
        cutoff: Train_Cutoff theo thời gian (mặc định ``"2025Q1"``).
        tech_path: Đường dẫn đặc trưng kỹ thuật.
        kw_path: Đường dẫn đặc trưng từ khóa.
        labels_path: Đường dẫn nhãn.
        min_samples: Ngưỡng số mẫu tối thiểu để huấn luyện phân khúc. Mặc định
            0 → không áp ngưỡng cứng (hành vi điều khiển bởi guard ValueError).
        alpha: Mức ý nghĩa cho BH-FDR (mặc định 0.05).

    Returns:
        Bộ ``(analysis_df, keyword_sig_df)`` tương ứng hai báo cáo đã ghi.
    """
    logger.info("=== B3: bắt đầu phân tích theo phân khúc (cutoff=%s) ===", cutoff)

    # 1. Ánh xạ phân khúc + danh sách phân khúc cần phân tích.
    segments = assign_segments()
    segment_list = build_segment_list(segments)
    logger.info("Sẽ phân tích %d phân khúc.", len(segment_list))

    # 2. Nạp merged đầy đủ một lần (cho phần kiểm định từ khóa in-sample và để
    #    đếm n_samples/n_tickers mỗi phân khúc).
    merged = load_and_merge_data(tech_path, kw_path, labels_path)

    # Từ khóa curated + ánh xạ hướng.
    kw_by_dir = get_curated_keywords()
    all_keywords = (
        kw_by_dir.get("positive", [])
        + kw_by_dir.get("negative", [])
        + kw_by_dir.get("neutral", [])
    )
    direction_map: Dict[str, str] = {}
    for kw in kw_by_dir.get("positive", []):
        direction_map[kw] = "positive"
    for kw in kw_by_dir.get("negative", []):
        direction_map[kw] = "negative"
    for kw in kw_by_dir.get("neutral", []):
        direction_map[kw] = "neutral"

    analysis_rows: List[Dict[str, object]] = []
    keyword_sig_frames: List[pd.DataFrame] = []

    for segment_type, segment_name, segment_tickers in segment_list:
        ticker_set = set(segment_tickers)
        seg_merged = merged[merged["ticker"].isin(ticker_set)]
        n_samples = len(seg_merged)
        n_tickers = int(seg_merged["ticker"].nunique())

        logger.info(
            "Phân khúc %s='%s': %d mẫu, %d ticker.",
            segment_type,
            segment_name,
            n_samples,
            n_tickers,
        )

        # 3. Delta_CA theo thuật toán (Req 10.3). Nếu dưới ngưỡng min_samples,
        #    bỏ qua huấn luyện nhưng vẫn báo cáo n (Req 10.5).
        if n_samples < min_samples:
            logger.warning(
                "Phân khúc %s='%s' có %d mẫu < min_samples=%d — bỏ qua huấn "
                "luyện (insufficient power).",
                segment_type,
                segment_name,
                n_samples,
                min_samples,
            )
            for model_name in REPORT_MODELS:
                analysis_rows.append(
                    {
                        "segment_type": segment_type,
                        "segment_name": segment_name,
                        "n_samples": n_samples,
                        "n_tickers": n_tickers,
                        "model": model_name,
                        "ba_config_a": np.nan,
                        "ba_config_b": np.nan,
                        "ba_config_c": np.nan,
                        "delta_ca": np.nan,
                        "note": "insufficient power",
                    }
                )
        else:
            analysis_rows.extend(
                compute_segment_deltas(
                    segment_type=segment_type,
                    segment_name=segment_name,
                    segment_tickers=segment_tickers,
                    n_samples=n_samples,
                    n_tickers=n_tickers,
                    cutoff=cutoff,
                    tech_path=tech_path,
                    kw_path=kw_path,
                    labels_path=labels_path,
                )
            )

        # 4. Kiểm định ý nghĩa từ khóa + BH-FDR trong phân khúc (Req 10.4).
        seg_sig_df = compute_segment_keyword_significance(
            seg_merged=seg_merged,
            keywords=all_keywords,
            direction_map=direction_map,
            segment_type=segment_type,
            segment_name=segment_name,
            alpha=alpha,
        )
        if not seg_sig_df.empty:
            keyword_sig_frames.append(seg_sig_df)

    # 5. Dựng DataFrame kết quả và ghi báo cáo (Req 10.6).
    analysis_df = pd.DataFrame(analysis_rows)
    keyword_sig_df = (
        pd.concat(keyword_sig_frames, ignore_index=True)
        if keyword_sig_frames
        else pd.DataFrame()
    )

    os.makedirs(os.path.dirname(SEGMENTATION_ANALYSIS_PATH), exist_ok=True)
    analysis_df.to_csv(SEGMENTATION_ANALYSIS_PATH, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi %s (%d dòng).", SEGMENTATION_ANALYSIS_PATH, len(analysis_df)
    )

    os.makedirs(os.path.dirname(SEGMENTATION_KEYWORD_SIG_PATH), exist_ok=True)
    keyword_sig_df.to_csv(
        SEGMENTATION_KEYWORD_SIG_PATH, index=False, encoding="utf-8"
    )
    logger.info(
        "Đã ghi %s (%d dòng).",
        SEGMENTATION_KEYWORD_SIG_PATH,
        len(keyword_sig_df),
    )

    logger.info("=== B3: hoàn tất phân tích theo phân khúc ===")
    return analysis_df, keyword_sig_df


# ---------------------------------------------------------------------------
# Entrypoint cho CLI registry (import mềm trong run_experiment.py)
# ---------------------------------------------------------------------------


def build_b3_features() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Entrypoint tương thích CLI registry cho B3.

    B3 là một phân tích *báo cáo theo phân khúc*, KHÔNG sinh tệp đặc trưng
    version hóa (``keyword_features_B3.csv``). Hàm này gọi
    :func:`run_segmentation_analysis` để sinh hai báo cáo
    ``segmentation_analysis.csv`` và ``segmentation_keyword_sig.csv``, rồi gọi
    :func:`experiments.common.reporting.generate_b3_report` để sinh báo cáo so
    sánh ``reports/experiment_B3_report.md`` cạnh Baseline_v0 (Req 13.1–13.7).

    Việc sinh báo cáo được guard mềm: nếu bước báo cáo lỗi (ví dụ thiếu baseline),
    phân tích phân khúc vẫn được coi là hoàn tất và các frame vẫn được trả về.

    Returns:
        Bộ ``(analysis_df, keyword_sig_df)`` từ :func:`run_segmentation_analysis`.
    """
    analysis_df, keyword_sig_df = run_segmentation_analysis()
    try:
        from experiments.common.reporting import generate_b3_report

        generate_b3_report(
            analysis_path=SEGMENTATION_ANALYSIS_PATH,
            keyword_sig_path=SEGMENTATION_KEYWORD_SIG_PATH,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Không sinh được báo cáo B3: %s.", exc)
    return analysis_df, keyword_sig_df


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    run_segmentation_analysis()
