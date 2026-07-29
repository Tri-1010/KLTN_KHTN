"""Unit tests for Comparison_Reporter (`experiments/common/reporting.py`).

Covers Req 13.1 (bảng Δ(C−A) 4 thuật toán cạnh baseline), Req 13.2/13.3 (con số
``0/71`` và ``32%`` tham chiếu), Req 13.4 (McNemar align theo ``(ticker,
quarter_id)`` với predictions baseline được inject — KHÔNG huấn luyện thật), và
Req 13.8 (bảng tổng hợp tầng biểu diễn, xử lý tệp thiếu).

Mọi test dùng ``RunnerResult`` tổng hợp nhỏ và ``tmp_path`` với các tệp
``model_comparison.csv`` giả — không đọc dữ liệu thật và không gọi model training.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from experiments.common.reporting import (
    BASELINE_KEYWORD_SIG,
    BASELINE_SHAP_PCT_TEXT,
    TEXT_REPRESENTATION_TABLE_PATH,
    generate_comparison_report,
    generate_text_representation_table,
    write_text_representation_table,
)
from experiments.common.runner import RunnerResult

_COMPARISON_COLUMNS = [
    "model",
    "config",
    "accuracy",
    "precision",
    "recall",
    "f1_macro",
    "auc_roc",
    "balanced_accuracy",
]


def _make_comparison_df(ba_by_model_config: dict[tuple[str, str], float]) -> pd.DataFrame:
    """Dựng model_comparison DataFrame với balanced_accuracy cho trước."""
    rows = []
    for (model, config), ba in ba_by_model_config.items():
        rows.append(
            {
                "model": model,
                "config": config,
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_macro": 0.0,
                "auc_roc": 0.0,
                "balanced_accuracy": ba,
            }
        )
    return pd.DataFrame(rows, columns=_COMPARISON_COLUMNS)


def _full_comparison_df(base: float) -> pd.DataFrame:
    """Bảng so sánh có đủ 4 thuật toán × (Config_A, Config_C)."""
    models = ["LightGBM", "Random_Forest", "XGBoost", "Logistic_Regression"]
    mapping: dict[tuple[str, str], float] = {}
    for i, m in enumerate(models):
        mapping[(m, "Config_A")] = base + 0.01 * i
        mapping[(m, "Config_C")] = base + 0.01 * i + 0.005  # delta = +0.005
    return _make_comparison_df(mapping)


def _make_runner_result(
    tickers_quarters: list[tuple[str, str]],
    y_test: list[int],
    pred_c: list[int],
    results_df: pd.DataFrame | None = None,
) -> RunnerResult:
    test_index = pd.DataFrame(tickers_quarters, columns=["ticker", "quarter_id"])
    return RunnerResult(
        results_df=results_df if results_df is not None else _full_comparison_df(0.70),
        test_index=test_index,
        y_test=np.array(y_test),
        pred_by_config={"Config_C": np.array(pred_c)},
    )


# ---------------------------------------------------------------------------
# Req 13.1 / 13.2 / 13.3 — delta table + baseline references
# ---------------------------------------------------------------------------


def test_report_contains_all_algorithms_and_baseline_references(tmp_path, monkeypatch):
    """Bảng Δ(C−A) chứa 4 thuật toán + tham chiếu 0/71 và 32% (Req 13.1–13.3)."""
    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )

    result = _make_runner_result(
        [("AAA", "2025Q1"), ("BBB", "2025Q1")],
        y_test=[1, 0],
        pred_c=[1, 0],
    )

    out_path = generate_comparison_report(
        experiment_id="A2",
        new_results=result,
        baseline_dir=str(baseline_dir),
        baseline_config_c={
            "test_index": pd.DataFrame(
                [("AAA", "2025Q1"), ("BBB", "2025Q1")],
                columns=["ticker", "quarter_id"],
            ),
            "y_test": np.array([1, 0]),
            "pred_by_config": {"Config_C": np.array([0, 0])},
        },
    )

    content = Path(out_path).read_text(encoding="utf-8")
    for display in ["LightGBM", "Random Forest", "XGBoost", "Logistic Regression"]:
        assert display in content
    assert BASELINE_KEYWORD_SIG in content  # 0/71
    assert BASELINE_SHAP_PCT_TEXT in content  # 32%
    # Δ(C−A) exp = +0.0050 cho mọi thuật toán trong fixture.
    assert "+0.0050" in content


def test_delta_table_computes_exact_signed_values(tmp_path, monkeypatch):
    """Δ(C−A) trong bảng bằng đúng ba_config_c − ba_config_a (kể cả âm) (Req 13.1)."""
    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)

    # Baseline: mỗi thuật toán có một Δ khác nhau, gồm cả giá trị âm.
    baseline_mapping: dict[tuple[str, str], float] = {
        ("LightGBM", "Config_A"): 0.700,
        ("LightGBM", "Config_C"): 0.720,  # Δ = +0.0200
        ("Random_Forest", "Config_A"): 0.650,
        ("Random_Forest", "Config_C"): 0.630,  # Δ = -0.0200
        ("XGBoost", "Config_A"): 0.600,
        ("XGBoost", "Config_C"): 0.600,  # Δ = +0.0000
        ("Logistic_Regression", "Config_A"): 0.550,
        ("Logistic_Regression", "Config_C"): 0.5625,  # Δ = +0.0125
    }
    _make_comparison_df(baseline_mapping).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )

    # Thí nghiệm: Δ khác baseline để phân biệt hai cột.
    exp_mapping: dict[tuple[str, str], float] = {
        ("LightGBM", "Config_A"): 0.700,
        ("LightGBM", "Config_C"): 0.710,  # Δ = +0.0100
        ("Random_Forest", "Config_A"): 0.650,
        ("Random_Forest", "Config_C"): 0.700,  # Δ = +0.0500
        ("XGBoost", "Config_A"): 0.600,
        ("XGBoost", "Config_C"): 0.570,  # Δ = -0.0300
        ("Logistic_Regression", "Config_A"): 0.550,
        ("Logistic_Regression", "Config_C"): 0.550,  # Δ = +0.0000
    }
    result = _make_runner_result(
        [("AAA", "2025Q1")],
        y_test=[1],
        pred_c=[1],
        results_df=_make_comparison_df(exp_mapping),
    )

    out_path = generate_comparison_report(
        experiment_id="A2",
        new_results=result,
        baseline_dir=str(baseline_dir),
        baseline_config_c={
            "test_index": pd.DataFrame(
                [("AAA", "2025Q1")], columns=["ticker", "quarter_id"]
            ),
            "y_test": np.array([1]),
            "pred_by_config": {"Config_C": np.array([1])},
        },
    )
    content = Path(out_path).read_text(encoding="utf-8")

    # Δ(C−A) exp cho từng thuật toán (định dạng +.4f).
    assert "+0.0100" in content  # LightGBM exp
    assert "+0.0500" in content  # Random Forest exp
    assert "-0.0300" in content  # XGBoost exp (âm)
    # Δ(C−A) baseline_v0 cho từng thuật toán.
    assert "+0.0200" in content  # LightGBM v0
    assert "-0.0200" in content  # Random Forest v0 (âm)
    assert "+0.0125" in content  # Logistic Regression v0
    # Δ = 0 hiển thị đúng dấu (+0.0000).
    assert "+0.0000" in content


def test_report_keyword_sig_and_shap_reported(tmp_path, monkeypatch):
    """Đếm significant_any và định dạng % SHAP (Req 13.2, 13.3)."""
    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )

    kw_sig = tmp_path / "keyword_significance_A2.csv"
    pd.DataFrame(
        {
            "keyword": ["a", "b", "c"],
            "significant_any": [True, False, True],
        }
    ).to_csv(kw_sig, index=False, encoding="utf-8")

    result = _make_runner_result(
        [("AAA", "2025Q1")], y_test=[1], pred_c=[1]
    )

    out_path = generate_comparison_report(
        experiment_id="A2",
        new_results=result,
        baseline_dir=str(baseline_dir),
        keyword_sig_path=str(kw_sig),
        shap_contrib_pct=0.25,
        baseline_config_c={
            "test_index": pd.DataFrame(
                [("AAA", "2025Q1")], columns=["ticker", "quarter_id"]
            ),
            "y_test": np.array([1]),
            "pred_by_config": {"Config_C": np.array([1])},
        },
    )
    content = Path(out_path).read_text(encoding="utf-8")
    assert "2/3" in content  # 2 significant out of 3
    assert "25%" in content


def test_report_missing_baseline_shows_na(tmp_path, monkeypatch):
    """Baseline thiếu → bảng Δ(C−A) đánh N/A cho cột baseline, không crash."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "reports").mkdir()
    result = _make_runner_result([("AAA", "2025Q1")], y_test=[1], pred_c=[1])

    out_path = generate_comparison_report(
        experiment_id="A3",
        new_results=result,
        baseline_dir=str(tmp_path / "reports" / "baseline_v0"),
        baseline_config_c={
            "test_index": pd.DataFrame(
                [("AAA", "2025Q1")], columns=["ticker", "quarter_id"]
            ),
            "y_test": np.array([1]),
            "pred_by_config": {"Config_C": np.array([1])},
        },
    )
    content = Path(out_path).read_text(encoding="utf-8")
    assert "N/A" in content
    assert "not computed" in content  # SHAP + keyword sig not provided


# ---------------------------------------------------------------------------
# Req 13.4 — McNemar alignment by (ticker, quarter_id)
# ---------------------------------------------------------------------------


def test_mcnemar_aligns_by_ticker_quarter_injected_baseline(tmp_path, monkeypatch):
    """McNemar align theo (ticker, quarter_id) với baseline inject (không train)."""
    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )

    # Thí nghiệm: test rows theo thứ tự [X, Y, Z]. y = [1,1,1].
    new_result = _make_runner_result(
        [("X", "2025Q1"), ("Y", "2025Q1"), ("Z", "2025Q2")],
        y_test=[1, 1, 1],
        pred_c=[1, 1, 0],  # mới đúng X,Y sai Z
    )
    # Baseline: CÙNG các key nhưng THỨ TỰ KHÁC → phải align theo key, không theo hàng.
    baseline_c = {
        "test_index": pd.DataFrame(
            [("Z", "2025Q2"), ("X", "2025Q1"), ("Y", "2025Q1")],
            columns=["ticker", "quarter_id"],
        ),
        "y_test": np.array([1, 1, 1]),
        "pred_by_config": {"Config_C": np.array([1, 0, 1])},  # Z đúng, X sai, Y đúng
    }

    out_path = generate_comparison_report(
        experiment_id="A2",
        new_results=new_result,
        baseline_dir=str(baseline_dir),
        baseline_config_c=baseline_c,
    )
    content = Path(out_path).read_text(encoding="utf-8")
    assert "p-value" in content
    assert "3 mẫu test chung" in content
    # Không bao giờ được gọi tới đường dẫn "not available" khi có đủ overlap.
    assert "not available" not in content


def test_mcnemar_no_overlap_reports_not_available(tmp_path, monkeypatch):
    """Không có key chung → McNemar 'not available', không crash (Req 13.4 guard)."""
    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )

    new_result = _make_runner_result(
        [("X", "2025Q1")], y_test=[1], pred_c=[1]
    )
    baseline_c = {
        "test_index": pd.DataFrame(
            [("Q", "2099Q9")], columns=["ticker", "quarter_id"]
        ),
        "y_test": np.array([1]),
        "pred_by_config": {"Config_C": np.array([1])},
    }
    out_path = generate_comparison_report(
        experiment_id="A2",
        new_results=new_result,
        baseline_dir=str(baseline_dir),
        baseline_config_c=baseline_c,
    )
    content = Path(out_path).read_text(encoding="utf-8")
    assert "not available" in content


def test_mcnemar_uses_reconstruct_fn_without_training(tmp_path, monkeypatch):
    """reconstruct_fn được dùng để lấy baseline predictions (thay cho training)."""
    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )

    calls: dict[str, object] = {}

    def fake_reconstruct(kw_path: str, cutoff: str):
        calls["kw_path"] = kw_path
        calls["cutoff"] = cutoff
        return {
            "test_index": pd.DataFrame(
                [("X", "2025Q1")], columns=["ticker", "quarter_id"]
            ),
            "y_test": np.array([1]),
            "pred_by_config": {"Config_C": np.array([0])},
        }

    new_result = _make_runner_result([("X", "2025Q1")], y_test=[1], pred_c=[1])
    out_path = generate_comparison_report(
        experiment_id="A2",
        new_results=new_result,
        baseline_dir=str(baseline_dir),
        reconstruct_fn=fake_reconstruct,
    )
    content = Path(out_path).read_text(encoding="utf-8")
    assert calls["kw_path"] == "data/features/keyword_features.csv"
    assert "p-value" in content
    assert "1 mẫu test chung" in content


# ---------------------------------------------------------------------------
# Req 13.8 — text representation summary table
# ---------------------------------------------------------------------------


def test_text_representation_table_handles_missing_files(tmp_path, monkeypatch):
    """Bảng tổng hợp tạo được và tệp thiếu → cột N/A (Req 13.8)."""
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    baseline_dir = reports / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    # v0 có, A2 có, A1a & A6 thiếu.
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )
    _full_comparison_df(0.70).to_csv(
        reports / "model_comparison_A2.csv", index=False, encoding="utf-8"
    )

    table = generate_text_representation_table(["v0", "A2", "A1a", "A6"])

    # Header có đủ 4 tầng + 4 thuật toán.
    for tier in ["v0", "A2", "A1a", "A6"]:
        assert tier in table
    for display in ["LightGBM", "Random Forest", "XGBoost", "Logistic Regression"]:
        assert display in table
    # v0 và A2 có Δ = +0.0050; A1a & A6 thiếu → N/A.
    assert "+0.0050" in table
    assert "N/A" in table


def test_text_representation_table_v0_fallback(tmp_path, monkeypatch):
    """v0 fallback sang reports/model_comparison.csv khi baseline thiếu (Req 13.8)."""
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    reports.mkdir(parents=True)
    _full_comparison_df(0.68).to_csv(
        reports / "model_comparison.csv", index=False, encoding="utf-8"
    )

    table = generate_text_representation_table(["v0"])
    assert "+0.0050" in table


# ---------------------------------------------------------------------------
# Req 13.8 — persist text representation summary to a report file
# ---------------------------------------------------------------------------


def test_write_text_representation_table_persists_file(tmp_path, monkeypatch):
    """Bảng tổng hợp được persist ra reports/text_representation_summary.md (Req 13.8)."""
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    baseline_dir = reports / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    # v0 và A2 có dữ liệu.
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )
    _full_comparison_df(0.70).to_csv(
        reports / "model_comparison_A2.csv", index=False, encoding="utf-8"
    )

    out_path = write_text_representation_table(["v0", "A2"])

    # Trả về đúng đường dẫn tương đối mặc định và tệp tồn tại.
    assert out_path == TEXT_REPRESENTATION_TABLE_PATH
    assert out_path == "reports/text_representation_summary.md"
    written = tmp_path / out_path
    assert written.exists()

    content = written.read_text(encoding="utf-8")
    # Tiêu đề tài liệu.
    assert "# Bảng tổng hợp Δ(C−A) — 4 tầng biểu diễn văn bản (Hướng A)" in content
    # Legend cho từng tầng cung cấp.
    assert "v0" in content
    assert "A2" in content
    # Các hàng bảng gồm tên hiển thị của thuật toán.
    for display in ["LightGBM", "Random Forest", "XGBoost", "Logistic Regression"]:
        assert display in content
    # Δ(C−A) của fixture = +0.0050 cho mọi thuật toán.
    assert "+0.0050" in content


def test_write_text_representation_table_creates_reports_dir(tmp_path, monkeypatch):
    """Thư mục reports/ được tạo nếu còn thiếu; tệp thiếu → cột N/A (Req 13.8)."""
    monkeypatch.chdir(tmp_path)
    # Không tạo sẵn reports/ — hàm phải tự tạo.
    out_path = write_text_representation_table(["v0", "A2"])

    written = tmp_path / out_path
    assert written.exists()
    content = written.read_text(encoding="utf-8")
    # Không có tệp so sánh nào → mọi ô Δ(C−A) là N/A, không crash.
    assert "N/A" in content


# ---------------------------------------------------------------------------
# Req 13.1–13.7 — B3 segmentation report (generate_b3_report)
# ---------------------------------------------------------------------------


def _make_b3_analysis_df() -> pd.DataFrame:
    """Dựng segmentation_analysis.csv giả nhỏ: 1 sector + 1 cap_group.

    Sector "Banking" huấn luyện đủ 4 model; cap_group "large_cap" có một model
    ``insufficient power`` để kiểm tra hiển thị N/A.
    """
    models = ["LightGBM", "Random_Forest", "XGBoost", "Logistic_Regression"]
    rows = []
    for i, m in enumerate(models):
        rows.append(
            {
                "segment_type": "sector",
                "segment_name": "Banking",
                "n_samples": 120,
                "n_tickers": 8,
                "model": m,
                "ba_config_a": 0.60 + 0.01 * i,
                "ba_config_b": 0.60 + 0.01 * i,
                "ba_config_c": 0.62 + 0.01 * i,  # delta = +0.02
                "delta_ca": 0.02,
                "note": "",
            }
        )
    # large_cap: 3 model bình thường + 1 insufficient power.
    for i, m in enumerate(models):
        if m == "XGBoost":
            rows.append(
                {
                    "segment_type": "cap_group",
                    "segment_name": "large_cap",
                    "n_samples": 40,
                    "n_tickers": 3,
                    "model": m,
                    "ba_config_a": float("nan"),
                    "ba_config_b": float("nan"),
                    "ba_config_c": float("nan"),
                    "delta_ca": float("nan"),
                    "note": "insufficient power",
                }
            )
        else:
            rows.append(
                {
                    "segment_type": "cap_group",
                    "segment_name": "large_cap",
                    "n_samples": 40,
                    "n_tickers": 3,
                    "model": m,
                    "ba_config_a": 0.55,
                    "ba_config_b": 0.55,
                    "ba_config_c": 0.54,  # delta = -0.01
                    "delta_ca": -0.01,
                    "note": "",
                }
            )
    return pd.DataFrame(rows)


def _make_b3_keyword_sig_df() -> pd.DataFrame:
    """Dựng segmentation_keyword_sig.csv giả với significant_any (bool) + n_excluded."""
    rows = [
        # Banking: 3 tested (1 significant), plus 1 excluded.
        {"segment_type": "sector", "segment_name": "Banking", "keyword": "loi_nhuan",
         "n_excluded": 0, "significant_any": True},
        {"segment_type": "sector", "segment_name": "Banking", "keyword": "no_xau",
         "n_excluded": 0, "significant_any": False},
        {"segment_type": "sector", "segment_name": "Banking", "keyword": "tang_truong",
         "n_excluded": 0, "significant_any": False},
        {"segment_type": "sector", "segment_name": "Banking", "keyword": "hiem",
         "n_excluded": 1, "significant_any": False},
        # large_cap: 2 tested, 0 significant.
        {"segment_type": "cap_group", "segment_name": "large_cap", "keyword": "loi_nhuan",
         "n_excluded": 0, "significant_any": False},
        {"segment_type": "cap_group", "segment_name": "large_cap", "keyword": "no_xau",
         "n_excluded": 0, "significant_any": False},
    ]
    return pd.DataFrame(rows)


def test_generate_b3_report_contains_required_sections(tmp_path, monkeypatch):
    """Báo cáo B3 chứa bảng Δ(C−A), subheading n_samples, 0/71, 32%, H1/H2/H3."""
    from experiments.common.reporting import generate_b3_report

    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "reports"
    baseline_dir = reports / "baseline_v0"
    baseline_dir.mkdir(parents=True)

    # Baseline v0 global comparison (Δ = +0.005 mỗi model).
    _full_comparison_df(0.68).to_csv(
        baseline_dir / "model_comparison.csv", index=False, encoding="utf-8"
    )

    analysis_path = reports / "segmentation_analysis.csv"
    keyword_sig_path = reports / "segmentation_keyword_sig.csv"
    _make_b3_analysis_df().to_csv(analysis_path, index=False, encoding="utf-8")
    _make_b3_keyword_sig_df().to_csv(keyword_sig_path, index=False, encoding="utf-8")

    out_path = generate_b3_report(
        analysis_path=str(analysis_path),
        keyword_sig_path=str(keyword_sig_path),
        baseline_dir=str(baseline_dir),
    )

    assert out_path == "reports/experiment_B3_report.md"
    written = tmp_path / out_path
    assert written.exists()
    content = written.read_text(encoding="utf-8")

    # Δ(C−A) table headers.
    assert "Δ(C−A) seg" in content
    assert "Δ(C−A) v0" in content
    # Segment subheading nhấn mạnh statistical power (n_samples).
    assert "sector: Banking — n_samples=120, n_tickers=8" in content
    # Δ(C−A) v0 = +0.0050 từ fixture baseline.
    assert "+0.0050" in content
    # Δ(C−A) seg dương cho Banking.
    assert "+0.0200" in content
    # insufficient power được xử lý.
    assert "insufficient power" in content
    # Keyword significance: Banking 1/3, cạnh 0/71.
    assert "1/3" in content
    assert "0/71" in content
    # SHAP 32% baseline.
    assert "32%" in content
    assert "not computed per segment" in content
    # McNemar not applicable.
    assert "not applicable" in content
    # H1/H2/H3 section.
    assert "H1" in content and "H2" in content and "H3" in content
    # Có tín hiệu (Banking mean Δ=+0.02 > 0.01 và 1 keyword significant) → H3 ủng hộ.
    assert "ủng hộ H3" in content


def test_generate_b3_report_degrades_when_inputs_missing(tmp_path, monkeypatch):
    """Thiếu tệp đầu vào B3 → báo cáo vẫn sinh với 'not available', không crash."""
    from experiments.common.reporting import generate_b3_report

    monkeypatch.chdir(tmp_path)
    (tmp_path / "reports").mkdir()

    out_path = generate_b3_report(
        analysis_path=str(tmp_path / "reports" / "missing_analysis.csv"),
        keyword_sig_path=str(tmp_path / "reports" / "missing_sig.csv"),
        baseline_dir=str(tmp_path / "reports" / "baseline_v0"),
    )
    written = tmp_path / out_path
    assert written.exists()
    content = written.read_text(encoding="utf-8")
    assert "not available" in content
    # Không có tín hiệu → kết luận không ủng hộ mạnh H3.
    assert "H3" in content
