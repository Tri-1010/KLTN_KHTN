"""Property-based tests for the long-only strategy simulator — Property P1.

Hosts **Property 1**: for any finite set of returns of the selected tickers in
a period, :func:`backtest.strategy.portfolio_period_return` equals the
arithmetic mean of those returns; and equals 0 when no ticker is selected
(empty portfolio → all cash).

The property is exercised with Hypothesis. The suite-wide ``default`` profile
(see ``tests/conftest.py``) guarantees at least 100 iterations.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from backtest.costs import CostConfig
from backtest.strategy import (
    StrategyConfig,
    _equal_weights,
    portfolio_period_return,
    select_portfolio,
    simulate_strategy,
)


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Per-ticker period returns within sane bounds: a total loss (-1.0 = -100%)
# up to a +500% gain. Bounded and finite to avoid float precision blow-ups
# (NaN/inf) that would obscure the arithmetic-mean property under test.
_RETURN = st.floats(
    min_value=-1.0, max_value=5.0, allow_nan=False, allow_infinity=False
)

# Non-empty list of selected-ticker returns for the "mean" leg of the property.
_NON_EMPTY_RETURNS = st.lists(_RETURN, min_size=1, max_size=50)


# ---------------------------------------------------------------------------
# Property 1: portfolio period return is the mean of selected-ticker returns.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(_NON_EMPTY_RETURNS)
def test_portfolio_return_equals_mean_of_selected(returns):
    """P1a: portfolio_period_return equals the arithmetic mean of the returns.

    Equal capital allocation means the one-period portfolio return is exactly
    the arithmetic mean of the selected tickers' period returns.

    **Validates: Requirements 2.3, 2.4**
    """
    result = portfolio_period_return(returns)
    expected = math.fsum(returns) / len(returns)

    assert result == expected or math.isclose(
        result, expected, rel_tol=1e-9, abs_tol=1e-12
    ), f"portfolio return {result} != mean {expected} for returns={returns}"


@settings(max_examples=100)
@given(st.just([]))
def test_portfolio_return_zero_when_empty(returns):
    """P1b: portfolio_period_return is exactly 0 for an empty portfolio.

    Selecting no ticker means holding cash for the period, so the reported
    period return is 0 regardless of the market.

    **Validates: Requirements 2.3, 2.4**
    """
    assert portfolio_period_return(returns) == 0.0


# ---------------------------------------------------------------------------
# Property 2: portfolio selection is correct wrt predictions and top-N.
# ---------------------------------------------------------------------------

# Ticker symbols: short upper-case identifiers. Uniqueness within a period is
# enforced by the composite strategy via ``unique_by`` on the ticker column.
_TICKER = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=5
)

# Binary model label: 0 = predicted "down" (never bought), 1 = predicted "up".
_PRED_LABEL = st.integers(min_value=0, max_value=1)

# Predicted up-probability in the closed unit interval [0, 1].
_PRED_PROBA = st.floats(
    min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
)


@st.composite
def _signal_frames(draw):
    """Build a random single-period SignalFrame with unique tickers.

    Columns: ``ticker`` (unique within the period), ``pred_label`` in {0, 1},
    ``pred_proba_up`` in [0, 1]. ``pred_proba_up`` values are drawn uniquely so
    that the "k highest probabilities" ordering is unambiguous (no ties), which
    keeps the top-N equality check robust and non-flaky.
    """
    n = draw(st.integers(min_value=0, max_value=12))

    tickers = draw(
        st.lists(_TICKER, min_size=n, max_size=n, unique=True)
    )
    labels = draw(st.lists(_PRED_LABEL, min_size=n, max_size=n))
    # Unique probabilities to avoid ties in the top-N ordering.
    probas = draw(st.lists(_PRED_PROBA, min_size=n, max_size=n, unique=True))

    return pd.DataFrame(
        {
            "ticker": tickers,
            "pred_label": labels,
            "pred_proba_up": probas,
        }
    )


@settings(max_examples=100)
@given(_signal_frames())
def test_select_portfolio_all_predicted_up_when_top_n_none(frame):
    """P2a: with ``top_n=None`` the selection equals the predicted-up set.

    When no top-N cap is applied, the selected portfolio is exactly the set of
    tickers with ``pred_label == 1`` — never a ``pred_label == 0`` ticker
    (long-only) — and the equal weights are all non-negative.

    **Validates: Requirements 2.1, 2.2, 2.6**
    """
    selected = select_portfolio(frame, top_n=None)

    predicted_up = set(frame.loc[frame["pred_label"] == 1, "ticker"])
    predicted_down = set(frame.loc[frame["pred_label"] == 0, "ticker"])

    # Exactly the predicted-up set (Req 2.1).
    assert set(selected) == predicted_up
    # No duplicates in the returned list.
    assert len(selected) == len(set(selected))
    # Long-only: never a predicted-down ticker (Req 2.2).
    assert not (set(selected) & predicted_down)

    # Equal weights are all non-negative (Req 2.3 long-only weights).
    weights = _equal_weights(selected)
    assert all(w >= 0 for w in weights.values())


@settings(max_examples=100)
@given(_signal_frames(), st.integers(min_value=1, max_value=15))
def test_select_portfolio_top_n_highest_proba_predicted_up(frame, k):
    """P2b: with ``top_n=k`` the selection is the k highest-proba predicted-up.

    The selection is a subset of the predicted-up tickers of size
    ``min(k, num_predicted_up)``, contains no ``pred_label == 0`` ticker
    (long-only), and separates cleanly by probability: the minimum
    ``pred_proba_up`` among the selected is >= the maximum ``pred_proba_up``
    among the non-selected predicted-up tickers. Weights stay non-negative.

    **Validates: Requirements 2.1, 2.2, 2.6**
    """
    selected = select_portfolio(frame, top_n=k)
    selected_set = set(selected)

    up = frame[frame["pred_label"] == 1]
    predicted_up = set(up["ticker"])
    predicted_down = set(frame.loc[frame["pred_label"] == 0, "ticker"])
    num_up = len(predicted_up)

    # Subset of predicted-up, capped at k (Req 2.6).
    assert selected_set <= predicted_up
    assert len(selected) == min(k, num_up)
    assert len(selected) == len(selected_set)  # no duplicates

    # Long-only: never a predicted-down ticker (Req 2.2).
    assert not (selected_set & predicted_down)

    # Probability separation: selected are the highest-proba predicted-up.
    proba_by_ticker = dict(zip(up["ticker"], up["pred_proba_up"]))
    not_selected_up = predicted_up - selected_set
    if selected_set and not_selected_up:
        min_selected = min(proba_by_ticker[t] for t in selected_set)
        max_rest = max(proba_by_ticker[t] for t in not_selected_up)
        assert min_selected >= max_rest

    # Equal weights are all non-negative (Req 2.3 long-only weights).
    weights = _equal_weights(selected)
    assert all(w >= 0 for w in weights.values())


# ---------------------------------------------------------------------------
# Property 11: portfolio-wide long-only constraint across periods.
# ---------------------------------------------------------------------------

# Quarter identifiers for multi-period frames. A small, unique pool keeps the
# generated frames multi-period while bounding the search space.
_QUARTER_ID = st.integers(min_value=1, max_value=40)

# Per-ticker period returns for the multi-period simulation. Bounded/finite to
# avoid NaN/inf; wide enough to exercise gains and total losses.
_PERIOD_RETURN = st.floats(
    min_value=-1.0, max_value=5.0, allow_nan=False, allow_infinity=False
)

# Small, non-negative transaction fees for the net (cost) scenario.
_FEE = st.floats(
    min_value=0.0, max_value=0.05, allow_nan=False, allow_infinity=False
)


@st.composite
def _multi_period_signal_frames(draw):
    """Build a random multi-period SignalFrame with unique (ticker, quarter_id).

    Columns match everything :func:`simulate_strategy` reads: ``ticker``,
    ``quarter_id``, ``pred_label`` in {0, 1}, ``pred_proba_up`` in [0, 1], and
    ``period_return``. Multiple quarters are generated and the (ticker,
    quarter_id) pair is unique across the frame.
    """
    # Draw a set of unique (ticker, quarter_id) keys spanning multiple quarters.
    n = draw(st.integers(min_value=0, max_value=30))
    keys = draw(
        st.lists(
            st.tuples(_TICKER, _QUARTER_ID),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )

    rows = []
    for ticker, quarter_id in keys:
        rows.append(
            {
                "ticker": ticker,
                "quarter_id": quarter_id,
                "pred_label": draw(_PRED_LABEL),
                "pred_proba_up": draw(_PRED_PROBA),
                "period_return": draw(_PERIOD_RETURN),
            }
        )

    columns = ["ticker", "quarter_id", "pred_label", "pred_proba_up", "period_return"]
    return pd.DataFrame(rows, columns=columns)


@st.composite
def _strategy_configs(draw):
    """Draw a varied :class:`StrategyConfig` covering the top-N and cost axes.

    ``top_n`` is either ``None`` (select all predicted-up) or ``k > 0``; ``cost``
    is either ``None`` (gross) or a :class:`CostConfig` with small non-negative
    fees (net).
    """
    top_n = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10)))
    cost = draw(
        st.one_of(
            st.none(),
            st.builds(CostConfig, brokerage=_FEE, sell_tax=_FEE),
        )
    )
    return StrategyConfig(top_n=top_n, cost=cost)


@settings(max_examples=100)
@given(_multi_period_signal_frames(), _strategy_configs())
def test_holdings_are_long_only_every_period(frame, cfg):
    """P11: every period's holdings respect the portfolio-wide long-only bound.

    For any multi-period SignalFrame and any StrategyConfig, each period in
    ``result.holdings_by_period`` has total weight in [0, 1] (the remainder is
    cash), all component weights are non-negative, and no period contains a
    negative-weight position — the one-directional (long-only) constraint of the
    VN base market.

    **Validates: Requirements 2.2, 2.3**
    """
    result = simulate_strategy(frame, cfg)

    # Tiny slack for float summation of equal weights (1/N repeated N times).
    slack = 1e-9

    for quarter_id, weights in result.holdings_by_period.items():
        total = math.fsum(weights.values())

        # Total portfolio weight lies in [0, 1]; remainder is cash (Req 2.3).
        assert -slack <= total <= 1.0 + slack, (
            f"period {quarter_id}: total weight {total} outside [0, 1]"
        )

        # Every component weight is non-negative — no short position (Req 2.2).
        for ticker, w in weights.items():
            assert w >= 0.0, (
                f"period {quarter_id}: negative weight {w} for {ticker}"
            )


# ---------------------------------------------------------------------------
# Property 5: net cumulative return never exceeds gross cumulative return.
# ---------------------------------------------------------------------------


def _cumulative_return(series):
    """Cumulative return computed inline as ``prod(1 + r) - 1`` over the series.

    Computed locally (not imported from ``backtest.metrics``) to avoid a
    cross-task dependency: the metrics module is implemented in a later task.
    An empty series yields 0.0.

    **Validates: Requirements 5.1**
    """
    values = series.values
    if len(values) == 0:
        return 0.0
    return float(np.prod(1.0 + values) - 1.0)


@st.composite
def _cost_strategy_configs(draw):
    """Draw a StrategyConfig that always carries a non-negative CostConfig.

    ``top_n`` is either ``None`` (select all predicted-up) or ``k > 0``; ``cost``
    is always a :class:`CostConfig` whose ``brokerage`` and ``sell_tax`` are
    non-negative, so the net scenario always applies fees (never below gross by
    construction).
    """
    top_n = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10)))
    cost = draw(st.builds(CostConfig, brokerage=_FEE, sell_tax=_FEE))
    return StrategyConfig(top_n=top_n, cost=cost)


@settings(max_examples=100)
@given(_multi_period_signal_frames(), _cost_strategy_configs())
def test_net_cumulative_return_never_exceeds_gross(frame, cfg):
    """P5: cumulative net return is <= cumulative gross return.

    For any sequence of portfolio decisions with non-negative costs, the
    cumulative return of the net scenario (with fees) is less than or equal to
    the cumulative return of the gross scenario (no fees). Per-period costs are
    non-negative, so per-period ``(1 + net) <= (1 + gross)``; period returns are
    bounded at ``>= -1`` (a portfolio cannot lose more than 100%), keeping every
    ``(1 + r)`` factor non-negative so the running product stays monotonic.

    **Validates: Requirements 3.5, 5.1**
    """
    result = simulate_strategy(frame, cfg)

    gross_cum = _cumulative_return(result.period_returns_gross)
    net_cum = _cumulative_return(result.period_returns_net)

    # Small float slack for accumulated rounding in the running product.
    slack = 1e-9
    assert net_cum <= gross_cum + slack, (
        f"net cumulative {net_cum} exceeds gross cumulative {gross_cum} "
        f"for cfg={cfg}"
    )
