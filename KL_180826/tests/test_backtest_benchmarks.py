"""Unit tests for the long-only benchmark strategies (Req 4.1, 4.2).

Covers :func:`backtest.benchmarks.buy_and_hold_equal` and
:func:`backtest.benchmarks.equal_weight_rebalanced` on a tiny deterministic
dataset whose expected per-quarter returns and cumulative returns are computed
BY HAND from the documented semantics.

Dataset (columns ``ticker, quarter_id, period_return``):

    quarter_id  ticker  period_return
    2025Q1      AAA      0.10
    2025Q1      BBB     -0.05
    2025Q2      AAA      0.20
    2025Q2      BBB      0.00
    2025Q2      CCC      0.30   (CCC appears from Q2)
    2025Q3      AAA      0.05
    2025Q3      CCC      0.10   (BBB missing in Q3)

buy_and_hold_equal — hold the first-quarter set {AAA, BBB}, no rebalancing:
    Q1: mean(0.10, -0.05)      = 0.025
    Q2: mean(0.20, 0.00)       = 0.10    (CCC ignored — never held)
    Q3: mean(0.05)             = 0.05    (BBB missing → only AAA held/present)
    cumulative = 1.025 * 1.10 * 1.05 - 1 = 0.183875

equal_weight_rebalanced — equal-weight ALL present tickers each quarter:
    Q1: mean(0.10, -0.05)          = 0.025
    Q2: mean(0.20, 0.00, 0.30)     = 0.1666666...
    Q3: mean(0.05, 0.10)           = 0.075
    cumulative = 1.025 * 1.1666667 * 1.075 - 1 = 0.2855208...
"""

from __future__ import annotations

import pandas as pd
import pytest

from backtest.benchmarks import buy_and_hold_equal, equal_weight_rebalanced
from backtest.metrics import cumulative_return
from backtest.strategy import VN_MARKET_ASSUMPTIONS


# ---------------------------------------------------------------------------
# Fixture: tiny known-answer dataset
# ---------------------------------------------------------------------------

def _signals() -> pd.DataFrame:
    """Small deterministic SignalFrame-like DataFrame (see module docstring)."""
    rows = [
        ("AAA", "2025Q1", 0.10),
        ("BBB", "2025Q1", -0.05),
        ("AAA", "2025Q2", 0.20),
        ("BBB", "2025Q2", 0.00),
        ("CCC", "2025Q2", 0.30),
        ("AAA", "2025Q3", 0.05),
        ("CCC", "2025Q3", 0.10),
    ]
    return pd.DataFrame(rows, columns=["ticker", "quarter_id", "period_return"])


QUARTERS = ["2025Q1", "2025Q2", "2025Q3"]


# ---------------------------------------------------------------------------
# buy_and_hold_equal
# ---------------------------------------------------------------------------

def test_buy_and_hold_period_returns_match_hand_computed_means():
    """Each quarter return = mean over the initially-held tickers still present."""
    result = buy_and_hold_equal(_signals())

    expected = {"2025Q1": 0.025, "2025Q2": 0.10, "2025Q3": 0.05}
    for q, exp in expected.items():
        assert result.period_returns.loc[q] == pytest.approx(exp)


def test_buy_and_hold_cumulative_return():
    """cumulative_return = prod(1 + r) - 1 over the hand-computed per-quarter means."""
    result = buy_and_hold_equal(_signals())

    expected = 1.025 * 1.10 * 1.05 - 1.0  # 0.183875
    assert cumulative_return(result.period_returns) == pytest.approx(expected)


def test_buy_and_hold_holdings_use_fixed_first_quarter_set():
    """Held set is fixed from the FIRST quarter; CCC (new in Q2) is never held."""
    result = buy_and_hold_equal(_signals())

    # First-quarter set = {AAA, BBB}, equal weight 1/2 = 0.5.
    assert result.holdings_by_period["2025Q1"] == pytest.approx({"AAA": 0.5, "BBB": 0.5})
    # Q2: CCC present in data but NOT held (not in first quarter); weight stays 1/2.
    assert result.holdings_by_period["2025Q2"] == pytest.approx({"AAA": 0.5, "BBB": 0.5})
    assert "CCC" not in result.holdings_by_period["2025Q2"]
    # Q3: BBB missing → only AAA remains from the held set, weight still 1/2 (fixed N).
    assert result.holdings_by_period["2025Q3"] == pytest.approx({"AAA": 0.5})
    assert "CCC" not in result.holdings_by_period["2025Q3"]


def test_buy_and_hold_result_structure():
    """StrategyResult structure: series indexed by quarter_id, net==gross, cost 0."""
    result = buy_and_hold_equal(_signals())

    assert isinstance(result.period_returns, pd.Series)
    assert list(result.period_returns.index) == QUARTERS
    assert result.period_returns.index.name == "quarter_id"

    # Benchmark reports gross: net series equals gross series and total_cost == 0.
    pd.testing.assert_series_equal(
        result.period_returns_net, result.period_returns_gross
    )
    pd.testing.assert_series_equal(result.period_returns, result.period_returns_gross)
    assert result.total_cost == 0.0

    # Market assumptions metadata present.
    assert result.market_assumptions == VN_MARKET_ASSUMPTIONS


# ---------------------------------------------------------------------------
# equal_weight_rebalanced
# ---------------------------------------------------------------------------

def test_equal_weight_period_returns_match_hand_computed_means():
    """Each quarter return = mean of period_return over ALL tickers present."""
    result = equal_weight_rebalanced(_signals())

    expected = {
        "2025Q1": 0.025,
        "2025Q2": (0.20 + 0.00 + 0.30) / 3.0,  # 0.16666...
        "2025Q3": (0.05 + 0.10) / 2.0,  # 0.075
    }
    for q, exp in expected.items():
        assert result.period_returns.loc[q] == pytest.approx(exp)


def test_equal_weight_cumulative_return():
    """cumulative_return = prod(1 + r) - 1 over hand-computed per-quarter means."""
    result = equal_weight_rebalanced(_signals())

    q2 = (0.20 + 0.00 + 0.30) / 3.0
    q3 = (0.05 + 0.10) / 2.0
    expected = (1.0 + 0.025) * (1.0 + q2) * (1.0 + q3) - 1.0  # ~0.2855208
    assert cumulative_return(result.period_returns) == pytest.approx(expected)


def test_equal_weight_rebalances_on_present_tickers_only():
    """Rebalancing each quarter uses ONLY the tickers present that quarter."""
    result = equal_weight_rebalanced(_signals())

    # Q1: only AAA, BBB present → 1/2 each (CCC absent).
    assert result.holdings_by_period["2025Q1"] == pytest.approx({"AAA": 0.5, "BBB": 0.5})
    # Q2: AAA, BBB, CCC present → 1/3 each.
    third = 1.0 / 3.0
    assert result.holdings_by_period["2025Q2"] == pytest.approx(
        {"AAA": third, "BBB": third, "CCC": third}
    )
    # Q3: BBB missing → equal-weight only AAA, CCC → 1/2 each.
    assert result.holdings_by_period["2025Q3"] == pytest.approx({"AAA": 0.5, "CCC": 0.5})


def test_equal_weight_result_structure():
    """StrategyResult structure: series indexed by quarter_id, net==gross, cost 0."""
    result = equal_weight_rebalanced(_signals())

    assert isinstance(result.period_returns, pd.Series)
    assert list(result.period_returns.index) == QUARTERS
    assert result.period_returns.index.name == "quarter_id"

    pd.testing.assert_series_equal(
        result.period_returns_net, result.period_returns_gross
    )
    pd.testing.assert_series_equal(result.period_returns, result.period_returns_gross)
    assert result.total_cost == 0.0

    assert result.market_assumptions == VN_MARKET_ASSUMPTIONS
