"""Model_Interpreter (`backtest/interpret.py`) — diễn giải mô hình kỹ thuật (Req 7).

Module này xếp hạng 16 đặc trưng kỹ thuật của Technical_Model (Config_A) theo hai
thước đo bổ trợ nhau:

- **SHAP** (Req 7.1): dùng ``shap.TreeExplainer`` cho mô hình cây (LightGBM,
  XGBoost, RandomForest) và xếp hạng theo ``mean(|SHAP|)``. Với mô hình không hỗ
  trợ TreeExplainer (ví dụ ``LogisticRegression``) hoặc khi SHAP import/explain
  thất bại, module **fallback về permutation importance** cho cột xếp hạng SHAP
  (ghi chú rõ trong log) — một lỗi SHAP KHÔNG làm sập toàn bộ tiến trình.
- **Permutation importance** (Req 7.2): mức giảm balanced accuracy khi hoán vị
  từng đặc trưng trên tập test (``sklearn.inspection.permutation_importance`` với
  ``scoring="balanced_accuracy"``, ``random_state=42``).

Kết quả được ghi ra ``reports/technical_feature_importance.csv`` (Req 7.3) và một
biểu đồ bar tóm tắt PNG (Req 7.4), đồng thời trả về dưới dạng ``pd.DataFrame``.

Xử lý shape của SHAP (an toàn với nhiều phiên bản API):

- ``shap`` mới trả về ``shap.Explanation`` (có ``.values``); bản cũ trả ndarray.
- Với phân loại nhị phân, giá trị SHAP có thể là ``list [class0, class1]`` hoặc
  mảng 3D ``(n_samples, n_features, 2)`` → lấy lát lớp "tăng" (lớp 1) rồi tính
  ``mean(|SHAP|)`` theo từng đặc trưng.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

import matplotlib

matplotlib.use("Agg")  # Backend headless — phải set trước khi import pyplot.
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402

from pipeline.logging_config import setup_logger  # noqa: E402

logger = setup_logger("BACKTEST_INTERPRET")

# Đường dẫn báo cáo mặc định (Req 7.3, 7.4).
DEFAULT_OUTPUT_DIR = "reports"
CSV_FILENAME = "technical_feature_importance.csv"
PNG_FILENAME = "technical_feature_importance.png"

# Thứ tự cột chuẩn của reports/technical_feature_importance.csv
# (theo design.md Data Models).
IMPORTANCE_COLUMNS = [
    "feature",
    "mean_abs_shap",
    "permutation_importance",
    "rank",
]


def _extract_positive_class_shap(shap_output: Any, n_features: int) -> np.ndarray:
    """Trích mảng SHAP 2D ``(n_samples, n_features)`` cho lớp "tăng" (lớp 1).

    Chuẩn hóa nhiều dạng đầu ra của thư viện ``shap`` về một mảng 2D:

    - ``shap.Explanation`` (có thuộc tính ``.values``) → dùng ``.values``.
    - ``list [class0, class1]`` (API cũ cho phân loại) → lấy phần tử lớp 1.
    - ndarray 3D ``(n_samples, n_features, n_classes)`` → lấy lát lớp 1.
    - ndarray 2D → dùng trực tiếp.

    Args:
        shap_output: Kết quả trả về từ explainer của ``shap``.
        n_features: Số đặc trưng kỳ vọng (để chọn đúng trục khi mơ hồ).

    Returns:
        Mảng ``numpy`` 2D ``(n_samples, n_features)`` kiểu float.
    """
    # 1) shap.Explanation → lấy .values (có thể là 2D hoặc 3D).
    if hasattr(shap_output, "values"):
        shap_output = shap_output.values

    # 2) list [class0, class1] (API cũ) → chọn lớp "tăng" (lớp 1) nếu có.
    if isinstance(shap_output, list):
        shap_output = shap_output[1] if len(shap_output) > 1 else shap_output[0]

    arr = np.asarray(shap_output, dtype=float)

    # 3) 3D (n_samples, n_features, n_classes) → lát lớp cuối (lớp "tăng").
    if arr.ndim == 3:
        # Trục lớp thường là trục cuối; lấy lớp 1 nếu có, ngược lại lớp 0.
        cls = 1 if arr.shape[-1] > 1 else 0
        arr = arr[:, :, cls]

    return arr


def _compute_permutation_importance(
    model: Any,
    X_test: pd.DataFrame,
    y_test: Sequence[int],
    feature_names: List[str],
    n_repeats: int = 10,
    random_state: int = 42,
) -> np.ndarray:
    """Tính permutation importance theo balanced accuracy trên tập test (Req 7.2).

    Args:
        model: Mô hình đã fit.
        X_test: Ma trận đặc trưng test.
        y_test: Nhãn thật của tập test (bắt buộc để chấm balanced accuracy).
        feature_names: Danh sách tên đặc trưng (để căn thứ tự đầu ra).
        n_repeats: Số lần hoán vị mỗi đặc trưng (mặc định 10).
        random_state: Seed cố định để tái lập (mặc định 42).

    Returns:
        Mảng importance trung bình theo đúng thứ tự *feature_names*.
    """
    result = permutation_importance(
        model,
        X_test,
        y_test,
        scoring="balanced_accuracy",
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=-1,
    )
    return np.asarray(result.importances_mean, dtype=float)


def _compute_shap_ranking(
    model: Any,
    X_test: pd.DataFrame,
    feature_names: List[str],
) -> Optional[np.ndarray]:
    """Tính ``mean(|SHAP|)`` theo từng đặc trưng bằng TreeExplainer (Req 7.1).

    Bọc toàn bộ thao tác SHAP trong try/except để một lỗi SHAP (import thất bại,
    mô hình không hỗ trợ, v.v.) KHÔNG làm sập tiến trình — khi đó trả về ``None``
    để tầng gọi fallback sang permutation importance (Error Handling design).

    Chỉ dùng ``TreeExplainer`` cho mô hình cây (nhận diện qua thuộc tính
    ``feature_importances_``). Mô hình khác (ví dụ ``LogisticRegression``) trả
    ``None`` để fallback.

    Args:
        model: Mô hình đã fit.
        X_test: Ma trận đặc trưng test.
        feature_names: Danh sách tên đặc trưng (để căn độ dài kết quả).

    Returns:
        Mảng ``mean(|SHAP|)`` theo thứ tự *feature_names*, hoặc ``None`` nếu SHAP
        không khả dụng/không hỗ trợ.
    """
    # Chỉ mô hình cây mới hỗ trợ TreeExplainer.
    if not hasattr(model, "feature_importances_"):
        logger.info(
            "Mô hình %s không phải mô hình cây — bỏ qua SHAP, fallback về "
            "permutation importance cho cột xếp hạng.",
            type(model).__name__,
        )
        return None

    try:
        import shap  # import trong hàm để lỗi thiếu shap không sập cả module.

        explainer = shap.TreeExplainer(model)
        shap_output = explainer.shap_values(X_test)
        shap_arr = _extract_positive_class_shap(shap_output, len(feature_names))
        mean_abs = np.abs(shap_arr).mean(axis=0)

        # Căn độ dài với feature_names (phòng shape bất thường).
        if mean_abs.shape[0] != len(feature_names):
            logger.warning(
                "SHAP trả %d giá trị nhưng có %d đặc trưng — fallback permutation.",
                mean_abs.shape[0],
                len(feature_names),
            )
            return None

        logger.info(
            "Tính SHAP (TreeExplainer) thành công cho %s: %d đặc trưng.",
            type(model).__name__,
            len(feature_names),
        )
        return np.asarray(mean_abs, dtype=float)
    except Exception as exc:  # noqa: BLE001 — SHAP không được làm sập tiến trình.
        logger.warning(
            "SHAP thất bại cho %s (%s); fallback về permutation importance "
            "cho cột mean_abs_shap.",
            type(model).__name__,
            exc,
        )
        return None


def _plot_importance(
    df: pd.DataFrame,
    save_path: Union[str, os.PathLike],
    used_shap: bool,
) -> None:
    """Vẽ biểu đồ bar tóm tắt tầm quan trọng đặc trưng và lưu PNG (Req 7.4).

    Xếp các đặc trưng theo ``mean_abs_shap`` giảm dần (đã có cột ``rank``) và vẽ
    thanh ngang. Tiêu đề nêu rõ nguồn xếp hạng (SHAP hay permutation fallback).

    Args:
        df: DataFrame kết quả đã xếp hạng (cột theo :data:`IMPORTANCE_COLUMNS`).
        save_path: Đường dẫn PNG đầu ra.
        used_shap: True nếu cột ``mean_abs_shap`` là SHAP thật; False nếu là
            giá trị permutation fallback (dùng cho nhãn biểu đồ).
    """
    # Sắp xếp tăng dần để barh vẽ đặc trưng quan trọng nhất trên cùng.
    plot_df = df.sort_values("mean_abs_shap", ascending=True)

    metric_label = (
        "mean(|SHAP|)" if used_shap else "Permutation importance (SHAP fallback)"
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(plot_df["feature"], plot_df["mean_abs_shap"], color="#2070C0")
    ax.set_xlabel(metric_label)
    ax.set_title(f"Technical Feature Importance — {metric_label}")
    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info("Đã lưu biểu đồ tầm quan trọng đặc trưng → %s", save_path)


def interpret_technical_model(
    model: Any,
    X_test: pd.DataFrame,
    feature_names: Sequence[str],
    y_test: Optional[Sequence[int]] = None,
    output_dir: Union[str, os.PathLike] = DEFAULT_OUTPUT_DIR,
    n_repeats: int = 10,
    random_state: int = 42,
) -> pd.DataFrame:
    """Diễn giải Technical_Model: SHAP + permutation importance (Req 7).

    Xếp hạng các đặc trưng kỹ thuật theo ``mean(|SHAP|)`` (Req 7.1, dùng
    ``TreeExplainer`` cho mô hình cây; fallback permutation cho mô hình không hỗ
    trợ hoặc khi SHAP lỗi) và tính permutation importance theo balanced accuracy
    trên tập test (Req 7.2). Ghi ``reports/technical_feature_importance.csv``
    (Req 7.3) và một biểu đồ PNG (Req 7.4), rồi trả về ``pd.DataFrame``.

    Hành vi fallback (được ghi rõ trong log): nếu SHAP không khả dụng/không hỗ
    trợ mô hình, cột ``mean_abs_shap`` sẽ **tái sử dụng giá trị permutation
    importance** làm thước đo xếp hạng thay thế (thay vì để trống), để bảng vẫn
    có thứ hạng đầy đủ và có ý nghĩa.

    Args:
        model: Technical_Model đã fit (LightGBM / XGBoost / RandomForest /
            LogisticRegression).
        X_test: Ma trận đặc trưng test (``pd.DataFrame`` cột là đặc trưng).
        feature_names: Tên các đặc trưng (thường 16 đặc trưng kỹ thuật của
            Config_A).
        y_test: Nhãn thật của tập test. **Bắt buộc** để tính permutation
            importance theo balanced accuracy; nếu ``None`` → ném ``ValueError``.
        output_dir: Thư mục ghi CSV + PNG (mặc định ``"reports"``). Tự tạo nếu
            thiếu.
        n_repeats: Số lần hoán vị mỗi đặc trưng cho permutation importance.
        random_state: Seed cố định để tái lập (mặc định 42).

    Returns:
        ``pd.DataFrame`` với các cột: ``feature``, ``mean_abs_shap``,
        ``permutation_importance``, ``rank`` (rank bắt đầu từ 1, theo
        ``mean_abs_shap`` giảm dần).

    Raises:
        ValueError: nếu *y_test* là ``None`` (không thể tính permutation
            importance theo balanced accuracy), hoặc số cột/độ dài không khớp.
    """
    feature_names = list(feature_names)

    if y_test is None:
        raise ValueError(
            "y_test là bắt buộc để tính permutation importance theo balanced "
            "accuracy (Req 7.2). Vui lòng truyền nhãn thật của tập test."
        )

    if X_test.shape[1] != len(feature_names):
        raise ValueError(
            f"Số cột X_test ({X_test.shape[1]}) không khớp số feature_names "
            f"({len(feature_names)})."
        )

    # 1) Permutation importance theo balanced accuracy (Req 7.2).
    perm_imp = _compute_permutation_importance(
        model, X_test, y_test, feature_names, n_repeats=n_repeats,
        random_state=random_state,
    )

    # 2) SHAP ranking (Req 7.1); None → fallback permutation cho cột SHAP.
    shap_ranking = _compute_shap_ranking(model, X_test, feature_names)
    used_shap = shap_ranking is not None
    if used_shap:
        mean_abs_shap = shap_ranking
    else:
        # Fallback được ghi chú: tái dùng permutation importance làm thước đo
        # xếp hạng thay thế cho cột mean_abs_shap (Error Handling design).
        logger.info(
            "Fallback: dùng permutation importance làm giá trị mean_abs_shap "
            "(SHAP không khả dụng cho mô hình này)."
        )
        mean_abs_shap = perm_imp

    # 3) Lắp bảng, xếp hạng theo mean_abs_shap giảm dần (rank bắt đầu từ 1).
    df = pd.DataFrame(
        {
            "feature": feature_names,
            "mean_abs_shap": np.asarray(mean_abs_shap, dtype=float),
            "permutation_importance": perm_imp,
        }
    )
    df = df.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    df["rank"] = np.arange(1, len(df) + 1)
    df = df[IMPORTANCE_COLUMNS]

    # 4) Ghi CSV + PNG (Req 7.3, 7.4); tạo output_dir nếu thiếu.
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / CSV_FILENAME
    png_path = out_dir / PNG_FILENAME

    df.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi bảng tầm quan trọng đặc trưng (%d đặc trưng, SHAP=%s) → %s",
        len(df),
        used_shap,
        csv_path,
    )

    _plot_importance(df, png_path, used_shap)

    return df
