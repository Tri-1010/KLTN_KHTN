"""ExperimentRunner — cầu nối mỏng tới ``pipeline/task10_train.py`` (Req 14).

Module này cho phép mỗi thí nghiệm đi qua **đúng cùng một pipeline huấn luyện**
của baseline v0, chỉ thay tập đặc trưng từ khóa (``kw_features_path``) và nơi
ghi bảng so sánh (``comparison_path``). Nhờ đó, mọi khác biệt kết quả chỉ phản
ánh khác biệt về tập đặc trưng, thỏa mãn Req 14 (so sánh công bằng).

Bên cạnh việc chạy ``run_model_training`` để ghi ``model_comparison_{id}.csv``,
runner còn thu thập predictions của Config_A/Config_C trên cùng tập test qua
``run_configs_return_predictions`` — cần cho McNemar (Req 13.4).

Các hàm dựng đường dẫn artifact (``feature_path``, ``comparison_path``,
``report_path``) bảo đảm cùng một ``experiment_id`` được nhúng nhất quán vào
mọi tệp đầu ra của thí nghiệm (Req 2.1, 2.2, 2.4, Property 15).

_Requirements: 2.1, 2.2, 2.4, 14.1_
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from pipeline.task10_train import (
    run_configs_return_predictions,
    run_model_training,
)

__all__ = [
    "ExperimentConfig",
    "RunnerResult",
    "feature_path",
    "comparison_path",
    "report_path",
    "build_experiment_config",
    "run_experiment_training",
]


# ---------------------------------------------------------------------------
# Artifact path builders — nhúng experiment_id nhất quán (Req 2.1, 2.2, 2.4)
# ---------------------------------------------------------------------------


def feature_path(experiment_id: str) -> str:
    """Đường dẫn tệp đặc trưng từ khóa version hóa của thí nghiệm (Req 2.1).

    Ví dụ: ``feature_path("A2") -> "data/features/keyword_features_A2.csv"``.
    """
    return f"data/features/keyword_features_{experiment_id}.csv"


def comparison_path(experiment_id: str) -> str:
    """Đường dẫn tệp bảng so sánh mô hình của thí nghiệm (Req 2.2).

    Ví dụ: ``comparison_path("A2") -> "reports/model_comparison_A2.csv"``.
    """
    return f"reports/model_comparison_{experiment_id}.csv"


def report_path(experiment_id: str) -> str:
    """Đường dẫn tệp báo cáo so sánh Markdown của thí nghiệm (Req 2.4).

    Ví dụ: ``report_path("A2") -> "reports/experiment_A2_report.md"``.
    """
    return f"reports/experiment_{experiment_id}_report.md"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class ExperimentConfig:
    """Cấu hình một lần chạy thí nghiệm qua pipeline huấn luyện chung.

    Attributes:
        experiment_id: Mã thí nghiệm (``"A2"``, ``"A1a"``, ``"B1"``, ...).
        kw_features_path: Đường dẫn tệp ``keyword_features_{id}.csv``.
        comparison_path: Đường dẫn ghi ``model_comparison_{id}.csv``.
        cutoff: Train_Cutoff theo thời gian (mặc định ``"2025Q1"``).
    """

    experiment_id: str
    kw_features_path: str
    comparison_path: str
    cutoff: str = "2025Q1"


@dataclass
class RunnerResult:
    """Kết quả của một lần chạy thí nghiệm.

    Attributes:
        results_df: Bảng so sánh mô hình (như ``run_model_training`` trả về).
        test_index: Các khóa ``(ticker, quarter_id)`` của tập test, cùng thứ tự
            với ``y_test`` và các mảng trong ``pred_by_config`` — dùng để căn
            predictions giữa các tập đặc trưng theo khóa (McNemar).
        y_test: Nhãn thật của tập test.
        pred_by_config: Ánh xạ ``config_name -> np.ndarray`` nhãn dự đoán, căn
            theo cùng các hàng test.
    """

    results_df: pd.DataFrame
    test_index: pd.DataFrame
    y_test: np.ndarray
    pred_by_config: dict[str, np.ndarray] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Config builder
# ---------------------------------------------------------------------------


def build_experiment_config(
    experiment_id: str,
    cutoff: str = "2025Q1",
) -> ExperimentConfig:
    """Dựng ``ExperimentConfig`` từ ``experiment_id`` dùng các path helper.

    Bảo đảm cùng một ``experiment_id`` được nhúng nhất quán vào tệp đặc trưng
    và tệp bảng so sánh (Req 2.4, Property 15).
    """
    return ExperimentConfig(
        experiment_id=experiment_id,
        kw_features_path=feature_path(experiment_id),
        comparison_path=comparison_path(experiment_id),
        cutoff=cutoff,
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_experiment_training(cfg: ExperimentConfig) -> RunnerResult:
    """Chạy pipeline huấn luyện chung cho một thí nghiệm.

    Gọi ``run_model_training`` với ``kw_path``/``comparison_path`` tùy biến để
    ghi ``model_comparison_{id}.csv`` (Req 14.1), sau đó thu predictions
    Config_A/Config_C trên cùng tập test cho McNemar (Req 13.4). Gộp lại thành
    một :class:`RunnerResult`.

    Args:
        cfg: Cấu hình thí nghiệm.

    Returns:
        :class:`RunnerResult` gồm bảng so sánh và predictions đã căn theo test.
    """
    results_df = run_model_training(
        kw_path=cfg.kw_features_path,
        comparison_path=cfg.comparison_path,
        cutoff=cfg.cutoff,
    )

    predictions = run_configs_return_predictions(
        kw_path=cfg.kw_features_path,
        cutoff=cfg.cutoff,
    )

    return RunnerResult(
        results_df=results_df,
        test_index=predictions["test_index"],
        y_test=predictions["y_test"],
        pred_by_config=predictions["pred_by_config"],
    )
