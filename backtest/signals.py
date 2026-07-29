"""Prediction_Signal (`backtest/signals.py`) — tín hiệu từ mô hình kỹ thuật (Req 1).

Module này huấn luyện Technical_Model trên ``Config_A`` (chỉ đặc trưng kỹ thuật)
bằng cách **tái sử dụng** các helper của ``pipeline/task10_train.py`` (không sửa
hành vi production), rồi xuất cho mỗi ``(ticker, quarter_id)`` của tập test một
tín hiệu gồm nhãn thật, nhãn dự đoán và xác suất lớp "tăng". Tín hiệu được gắn
``period_return`` lấy từ cột ``return`` của ``master_with_labels.csv`` để làm đầu
vào cho Strategy_Simulator.

Nguyên tắc chống rò rỉ thời gian (Req 8.4):

- dùng đúng ``time_series_split`` của pipeline (không xáo trộn, split theo
  ``quarter_id``);
- fit imputer CHỈ trên tập train rồi transform tập test.

``pred_proba_up = model.predict_proba(X_test)[:, 1]`` là xác suất lớp "tăng"
(lớp 1), cần cho biến thể top-N (Req 2.6) và cho xếp hạng.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from pipeline.logging_config import setup_logger
from pipeline.task10_train import (
    KW_FEATURES_PATH,
    LABELS_PATH,
    TECH_FEATURES_PATH,
    build_ml_models,
    fit_imputer,
    get_feature_configs,
    identify_feature_columns,
    load_and_merge_data,
    prepare_features,
    time_series_split,
)

logger = setup_logger("BACKTEST_SIGNALS")

# SignalFrame là một pd.DataFrame với các cột cố định (xem docstring
# generate_signals). Alias giúp type hint đọc rõ ý đồ thiết kế.
SignalFrame = pd.DataFrame

# Các cột của SignalFrame trả về (Req 1.2, 1.3).
SIGNAL_COLUMNS: List[str] = [
    "ticker",
    "quarter_id",
    "y_true",
    "pred_label",
    "pred_proba_up",
    "period_return",
]

# Bốn thuật toán ML hiện có trong pipeline (Req 1.4). Dùng đúng các khóa mà
# ``build_ml_models`` trả về.
AVAILABLE_MODELS: Tuple[str, ...] = (
    "Logistic_Regression",
    "Random_Forest",
    "XGBoost",
    "LightGBM",
)

# Sentinel cho "tự động chọn mô hình có balanced accuracy cao nhất" (Req 1.4).
AUTO_MODEL = "auto"


def _prepare_train_test_matrices(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: List[str],
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Tạo ma trận đặc trưng train/test theo đúng quy trình chống rò rỉ.

    Fit imputer trên train, transform test; căn hai tập về cùng tập cột số
    (Req 8.4). Trả về ``(X_train, y_train, X_test, y_test)``.
    """
    available_cols = [c for c in feature_cols if c in train_df.columns]

    train_imputer, _ = fit_imputer(train_df, available_cols)
    X_train, y_train = prepare_features(train_df, available_cols, imputer=train_imputer)
    X_test, y_test = prepare_features(test_df, available_cols, imputer=train_imputer)

    common_cols = [c for c in X_train.columns if c in X_test.columns]
    X_train = X_train[common_cols]
    X_test = X_test[common_cols]

    return X_train, y_train, X_test, y_test


def _fit_predict(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray]:
    """Fit *model* trên train, trả ``(pred_label, pred_proba_up)`` trên test.

    ``pred_proba_up`` là xác suất lớp "tăng" (cột 1 của ``predict_proba``).
    """
    model.fit(X_train, y_train)
    pred_label = np.asarray(model.predict(X_test))
    pred_proba_up = np.asarray(model.predict_proba(X_test)[:, 1])
    return pred_label, pred_proba_up


def _select_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: Optional[str],
) -> Tuple[str, np.ndarray, np.ndarray]:
    """Chọn/huấn luyện mô hình và trả ``(name, pred_label, pred_proba_up)``.

    - Khi *model_name* là một thuật toán tường minh → huấn luyện đúng thuật toán
      đó (mặc định ``"LightGBM"`` theo kết quả baseline).
    - Khi *model_name* là ``None`` hoặc :data:`AUTO_MODEL` → huấn luyện cả bốn
      thuật toán và chọn mô hình có balanced accuracy cao nhất trên tập test
      (Req 1.4).
    """
    models = build_ml_models(y_train)

    # Chế độ tường minh: huấn luyện đúng một thuật toán.
    if model_name is not None and model_name != AUTO_MODEL:
        if model_name not in models:
            raise KeyError(
                f"Unknown model_name {model_name!r}; available: {sorted(models)}"
            )
        pred_label, pred_proba_up = _fit_predict(
            models[model_name], X_train, y_train, X_test
        )
        return model_name, pred_label, pred_proba_up

    # Chế độ tự động: chọn mô hình có balanced accuracy cao nhất.
    best_name: Optional[str] = None
    best_ba = -np.inf
    best_pred_label: Optional[np.ndarray] = None
    best_pred_proba: Optional[np.ndarray] = None

    for name in AVAILABLE_MODELS:
        if name not in models:
            continue
        pred_label, pred_proba_up = _fit_predict(
            models[name], X_train, y_train, X_test
        )
        ba = balanced_accuracy_score(y_test, pred_label)
        logger.info("Auto-select — %s balanced accuracy = %.4f", name, ba)
        if ba > best_ba:
            best_ba = ba
            best_name = name
            best_pred_label = pred_label
            best_pred_proba = pred_proba_up

    if best_name is None:
        raise RuntimeError("No ML model could be trained for auto-selection.")

    logger.info(
        "Auto-selected best model: %s (balanced accuracy = %.4f)",
        best_name,
        best_ba,
    )
    return best_name, best_pred_label, best_pred_proba


def _attach_period_return(
    signals: pd.DataFrame,
    labels_path: str,
) -> Tuple[pd.DataFrame, int]:
    """Gắn ``period_return`` từ cột ``return`` của ``master_with_labels.csv``.

    Căn theo ``(ticker, quarter_id)`` (Req 1.3). Loại các hàng thiếu
    ``period_return`` và đếm số hàng bị loại (Req 1.5).

    Returns:
        ``(signals_with_return, n_dropped)``.
    """
    master = pd.read_csv(labels_path)

    missing = {c for c in ("ticker", "quarter_id", "return") if c not in master.columns}
    if missing:
        raise KeyError(
            f"master_with_labels.csv thiếu cột bắt buộc: {sorted(missing)}"
        )

    returns = master[["ticker", "quarter_id", "return"]].rename(
        columns={"return": "period_return"}
    )

    merged = signals.merge(returns, on=["ticker", "quarter_id"], how="left")

    n_before = len(merged)
    merged = merged.dropna(subset=["period_return"])
    n_dropped = n_before - len(merged)

    if n_dropped:
        logger.warning(
            "Loại %d/%d hàng thiếu Period_Return (return) khi gắn tín hiệu.",
            n_dropped,
            n_before,
        )

    return merged.reset_index(drop=True), n_dropped


def generate_signals(
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
    cutoff: str = "2025Q1",
    model_name: Optional[str] = "LightGBM",
    config: str = "Config_A",
) -> SignalFrame:
    """Sinh tín hiệu dự đoán từ Technical_Model cho tập test (Req 1).

    Huấn luyện Technical_Model trên *config* (mặc định ``Config_A`` — chỉ đặc
    trưng kỹ thuật) qua cùng split/imputer của pipeline, rồi trả về nhãn thật,
    nhãn dự đoán và xác suất lớp "tăng" cho từng ``(ticker, quarter_id)`` của tập
    test, đã gắn ``period_return`` (Req 1.2, 1.3).

    Args:
        tech_path: Đường dẫn tệp đặc trưng kỹ thuật.
        kw_path: Đường dẫn tệp đặc trưng từ khóa. Dù ``Config_A`` chỉ dùng đặc
            trưng kỹ thuật, ``load_and_merge_data`` vẫn inner-join với tệp này để
            giữ đúng tập mẫu như baseline luận văn.
        labels_path: Đường dẫn ``master_with_labels.csv`` (nguồn nhãn +
            ``Period_Return``).
        cutoff: Train_Cutoff — ranh giới chia train/test theo thời gian
            (mặc định ``"2025Q1"``).
        model_name: Thuật toán huấn luyện. Mặc định ``"LightGBM"``. Truyền
            ``None`` hoặc ``"auto"`` để tự chọn mô hình có balanced accuracy cao
            nhất trong bốn thuật toán (Req 1.4).
        config: Cấu hình đặc trưng, mặc định ``"Config_A"`` (chỉ kỹ thuật).

    Returns:
        SignalFrame (``pd.DataFrame``) với các cột: ``ticker``, ``quarter_id``,
        ``y_true``, ``pred_label``, ``pred_proba_up``, ``period_return``.

    Raises:
        KeyError: nếu *config* không tồn tại hoặc *model_name* không hợp lệ.
        ValueError: nếu dữ liệu merge rỗng hoặc chỉ có một lớp nhãn (không thể
            huấn luyện).
    """
    # 1. Load & merge (giữ đúng tập mẫu như baseline).
    merged = load_and_merge_data(tech_path, kw_path, labels_path)
    if merged.empty:
        raise ValueError(
            "No samples after merging technical/keyword/label data; "
            "cannot generate signals."
        )
    if merged["label_basic"].nunique() < 2:
        raise ValueError(
            "Training data has only one label class; at least two are required "
            "to train a Technical_Model."
        )

    # 2. Identify columns + configs (Config_A = technical only).
    tech_cols, kw_cols = identify_feature_columns(merged)
    configs = get_feature_configs(tech_cols, kw_cols)
    if config not in configs:
        raise KeyError(
            f"Unknown config {config!r}; available: {sorted(configs)}"
        )
    feature_cols = configs[config]

    # 3. Time-series split (không xáo trộn, split theo quarter_id).
    train_df, test_df = time_series_split(merged, cutoff=cutoff)

    # Khóa (ticker, quarter_id) của tập test theo đúng thứ tự hàng.
    test_index = test_df[["ticker", "quarter_id"]].reset_index(drop=True).copy()

    # 4. Fit imputer trên train, transform test; căn cột chung (Req 8.4).
    X_train, y_train, X_test, y_test = _prepare_train_test_matrices(
        train_df, test_df, feature_cols
    )

    # 5. Huấn luyện + dự đoán (chọn theo BA khi không chỉ định tường minh).
    chosen_name, pred_label, pred_proba_up = _select_model(
        X_train, y_train, X_test, y_test, model_name
    )
    logger.info(
        "Generated signals with model=%s, config=%s, cutoff=%s, %d test rows.",
        chosen_name,
        config,
        cutoff,
        len(test_index),
    )

    # 6. Lắp SignalFrame (nhãn + xác suất) căn theo cùng thứ tự hàng test.
    signals = pd.DataFrame(
        {
            "ticker": test_index["ticker"].to_numpy(),
            "quarter_id": test_index["quarter_id"].to_numpy(),
            "y_true": np.asarray(y_test).astype(int),
            "pred_label": np.asarray(pred_label).astype(int),
            "pred_proba_up": np.asarray(pred_proba_up, dtype=float),
        }
    )

    # 7. Gắn Period_Return; loại hàng thiếu return và đếm lại (Req 1.3, 1.5).
    signals, _ = _attach_period_return(signals, labels_path)

    return signals[SIGNAL_COLUMNS]
