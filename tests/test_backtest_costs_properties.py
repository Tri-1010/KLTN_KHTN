"""Property-based tests for Transaction_Cost — Property P3 (Req 3.2, 3.3, 3.4).

Hosts **Property 3**: for any two portfolio weight configurations,
:func:`backtest.costs.period_cost` is non-negative; equals 0 when the two
portfolios are identical (no turnover); and increases monotonically with the
amount of portfolio change.

The property is exercised with Hypothesis. The suite-wide ``default`` profile
(see ``tests/conftest.py``) guarantees at least 100 iterations.
"""

from __future__ import annotations

import math

from hypothesis import given, settings
from hypothesis import strategies as st

from backtest.costs import CostConfig, period_cost, turnover


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# A small fixed universe of tickers so that prev/new portfolios overlap often
# (overlap exercises both the buy and sell legs of the turnover computation).
_TICKERS = ["AAA", "BBB", "CCC", "DDD", "EEE"]

_WEIGHT = st.floats(
    min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
)


@st.composite
def _portfolio(draw) -> dict[str, float]:
    """Draw a portfolio: ticker -> weight, weights >= 0, normalized to sum 1.

    An empty portfolio (all cash) is a valid configuration, so the possibility
    of selecting no tickers is deliberately allowed.
    """
    tickers = draw(
        st.lists(st.sampled_from(_TICKERS), min_size=0, max_size=len(_TICKERS), unique=True)
    )
    weights = {t: draw(_WEIGHT) for t in tickers}
    total = sum(weights.values())
    if total > 0.0:
        weights = {t: w / total for t, w in weights.items()}
    return weights


@st.composite
def _cost_config(draw) -> CostConfig:
    """Draw a non-negative cost configuration within realistic VN bounds."""
    brokerage = draw(
        st.floats(min_value=0.0, max_value=0.005, allow_nan=False, allow_infinity=False)
    )
    sell_tax = draw(
        st.floats(min_value=0.0, max_value=0.005, allow_nan=False, allow_infinity=False)
    )
    return CostConfig(brokerage=brokerage, sell_tax=sell_tax)


def _scaled_portfolio(
    prev_w: dict[str, float], new_w: dict[str, float], alpha: float
) -> dict[str, float]:
    """Interpolate ``prev_w`` toward ``new_w`` by fraction ``alpha`` in [0, 1].

    Returns ``prev_w + alpha * (new_w - prev_w)`` per ticker. At ``alpha == 0``
    the result equals ``prev_w`` (no change); at ``alpha == 1`` it equals
    ``new_w``. Both buy and sell volumes scale linearly with ``alpha``, so the
    period cost is a linear (hence non-decreasing) function of ``alpha``.
    """
    scaled: dict[str, float] = {}
    for ticker in prev_w.keys() | new_w.keys():
        p = prev_w.get(ticker, 0.0)
        n = new_w.get(ticker, 0.0)
        scaled[ticker] = p + alpha * (n - p)
    return scaled


# ---------------------------------------------------------------------------
# Property 3: cost non-negative, zero when unchanged, monotone in turnover.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(_portfolio(), _portfolio(), _cost_config())
def test_period_cost_is_non_negative(prev_w, new_w, cfg):
    """P3a: period_cost is always non-negative for any two portfolios.

    **Validates: Requirements 3.2, 3.3, 3.4**
    """
    cost = period_cost(prev_w, new_w, cfg)
    assert cost >= 0.0, f"period_cost returned negative value {cost}"


@settings(max_examples=100)
@given(_portfolio(), _cost_config())
def test_period_cost_zero_when_portfolio_unchanged(weights, cfg):
    """P3b: period_cost is exactly 0 when the portfolio does not change.

    Identical prev/new portfolios imply zero turnover (buy = sell = 0), hence
    zero cost regardless of the fee configuration.

    **Validates: Requirements 3.2, 3.3, 3.4**
    """
    buy_v, sell_v = turnover(weights, weights)
    assert buy_v == 0.0 and sell_v == 0.0

    cost = period_cost(weights, dict(weights), cfg)
    assert cost == 0.0, f"expected zero cost for unchanged portfolio, got {cost}"


@settings(max_examples=100)
@given(
    _portfolio(),
    _portfolio(),
    _cost_config(),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_period_cost_monotonic_in_turnover(prev_w, new_w, cfg, alpha1, alpha2):
    """P3c: period_cost is non-decreasing as portfolio change grows.

    Interpolate ``prev_w`` toward ``new_w`` by two fractions ``alpha1 <=
    alpha2``. Since both buy and sell volumes scale linearly with the fraction,
    a larger fraction (more portfolio change) can never cost less.

    **Validates: Requirements 3.2, 3.3, 3.4**
    """
    lo, hi = sorted((alpha1, alpha2))

    port_lo = _scaled_portfolio(prev_w, new_w, lo)
    port_hi = _scaled_portfolio(prev_w, new_w, hi)

    cost_lo = period_cost(prev_w, port_lo, cfg)
    cost_hi = period_cost(prev_w, port_hi, cfg)

    # Allow tiny floating-point slack from the interpolation arithmetic.
    assert cost_hi + 1e-12 >= cost_lo, (
        f"cost not monotonic in turnover: alpha_lo={lo} -> {cost_lo}, "
        f"alpha_hi={hi} -> {cost_hi}"
    )
    # Sanity: the zero-change endpoint must itself be costless.
    if math.isclose(lo, 0.0):
        assert cost_lo == 0.0


# ---------------------------------------------------------------------------
# Property 4: sell leg costs more than a buy leg of the same value.
# ---------------------------------------------------------------------------

# Strictly positive transaction value (a portfolio weight change on NAV = 1).
_POS_VALUE = st.floats(
    min_value=1e-6, max_value=1.0, allow_nan=False, allow_infinity=False
)


@st.composite
def _cost_config_positive_sell_tax(draw) -> CostConfig:
    """Draw a cost config with non-negative brokerage and a *strictly positive*
    sell_tax, so the sell-vs-buy fee asymmetry is a strict inequality."""
    brokerage = draw(
        st.floats(min_value=0.0, max_value=0.005, allow_nan=False, allow_infinity=False)
    )
    sell_tax = draw(
        st.floats(min_value=1e-6, max_value=0.005, allow_nan=False, allow_infinity=False)
    )
    return CostConfig(brokerage=brokerage, sell_tax=sell_tax)


@settings(max_examples=100)
@given(_POS_VALUE, _cost_config_positive_sell_tax())
def test_sell_fee_higher_than_buy_fee_same_value(value, cfg):
    """P4: for any positive transaction value, the sell-leg fee exceeds the
    buy-leg fee of the same value (the 0.1% sell tax applies only to sells).

    The two legs are exercised through the real ``period_cost`` API:

    - **Pure buy leg**: ``prev`` empty, ``new = {ticker: value}`` → the whole
      ``value`` is bought, so cost == ``value * brokerage``.
    - **Pure sell leg**: ``prev = {ticker: value}``, ``new`` empty → the whole
      ``value`` is sold, so cost == ``value * (brokerage + sell_tax)``.

    With ``value > 0`` and ``sell_tax > 0`` the sell leg is strictly costlier.

    **Validates: Requirements 3.1, 3.3**
    """
    buy_leg_cost = period_cost({}, {"AAA": value}, cfg)
    sell_leg_cost = period_cost({"AAA": value}, {}, cfg)

    assert sell_leg_cost > buy_leg_cost, (
        f"sell fee {sell_leg_cost} not greater than buy fee {buy_leg_cost} "
        f"for value={value}, cfg={cfg}"
    )
    # The gap must equal exactly the sell tax applied to the transacted value.
    assert math.isclose(
        sell_leg_cost - buy_leg_cost, value * cfg.sell_tax, rel_tol=1e-9, abs_tol=1e-15
    )
