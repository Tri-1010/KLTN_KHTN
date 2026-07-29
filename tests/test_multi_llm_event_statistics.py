from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


audit = _load("run_semantic_signal_audit")
stats = _load("run_event_window_stat_tests")


def test_market_adjusted_forward_metrics():
    dates = pd.bdate_range("2024-01-02", periods=6)
    stock = pd.DataFrame({"ticker": ["AAA"] * 6, "date": dates, "close": [100, 105, 110, 115, 120, 125], "volume": [100] * 6})
    market = pd.DataFrame({"date": dates, "close": [100, 102, 104, 106, 108, 110]})
    result = audit.forward_metrics(stock, market, "AAA", dates[1], 2)
    assert result["raw_return"] == 115 / 105 - 1
    assert result["benchmark_return"] == 106 / 102 - 1
    assert result["market_adjusted_return"] == result["raw_return"] - result["benchmark_return"]


def test_bh_and_bootstrap_are_deterministic():
    assert stats.benjamini_hochberg([0.01, 0.04, 0.03]) == stats.benjamini_hochberg([0.01, 0.04, 0.03])
    first = stats.bootstrap_ci([1, 2, 3], [0, 0, 1], samples=100, seed=7)
    second = stats.bootstrap_ci([1, 2, 3], [0, 0, 1], samples=100, seed=7)
    assert first == second


def test_mann_whitney_handles_ties():
    u, p, z, variance = stats.mann_whitney_u([1, 1, 2], [1, 2, 2])
    assert variance > 0
    assert 0 <= p <= 1
    assert all(value == value for value in [u, z])


def test_non_overlapping_events_excludes_boundary_overlap():
    frame = pd.DataFrame({
        "ticker": ["AAA", "AAA", "AAA"],
        "effective_date": ["2024-01-02", "2024-01-05", "2024-01-08"],
        "window_end_date": ["2024-01-05", "2024-01-10", "2024-01-12"],
    })
    selected = stats.non_overlapping_events(frame, 5)
    assert list(selected["effective_date"]) == ["2024-01-02", "2024-01-08"]


def test_bh_rejection_is_separate_from_effect_direction():
    adjusted = stats.benjamini_hochberg([0.001, 0.8])
    reject = [value <= 0.05 for value in adjusted]
    ci = [(-0.4, -0.1), (-0.2, 0.3)]
    robust_negative = [flag and high < 0 for flag, (_, high) in zip(reject, ci)]
    assert reject == [True, False]
    assert robust_negative == [True, False]
