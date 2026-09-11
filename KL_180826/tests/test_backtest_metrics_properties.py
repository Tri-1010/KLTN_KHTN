"""Property-based tests for Performance_Evaluator — P6, P7, P8, P10 (Req 5).

Hosts the mandatory Hypothesis properties for the pure metric functions in
:mod:`backtest.metrics`:

- **Property 6** (:func:`backtest.metrics.cumulative_return`): equals
  ``∏(1 + r_t) − 1`` and is 0 for an all-zeros sequence (Req 5.1).
- **Property 7** (:func:`backtest.metrics.max_drawdown`): lies in ``[−1, 0]``,
  equals 0 when all returns are non-negative, and is invariant to appending
  zero-return periods at the end (Req 5.4).
- **Property 8** (:func:`backtest.metrics.sharpe_ratio`): equals
  ``mean(r − rf) / std(r)`` when std > 0, and returns a well-defined value
  (0.0, per the module convention) without raising when std = 0 (Req 5.3).
- **Property 10** (:func:`backtest.metrics.hit_rate`): lies in ``[0, 1]`` and
  equals the fraction of positive-return periods (Req 5.5).

Every property is exercised with Hypothesis. The suite-wide ``default`` profile
(see ``tests/conftest.py``) guarantees at least 100 iterations.
"""

from __future__ import annotations

import math

import numpy as np
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from backtest.metrics import (
    cumulative_return,
    hit_rate,
    max_drawdown,
    mean_std_period,
    sharpe_ratio,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Period returns bounded to keep products/equity curves free of overflow and
# precision blow-ups. Kept >= -0.9 (> -1) for economic validity: a period can
# lose at most ~90% but never wipe out more than the invested capital.
_RETURN = st.floats(
    min_value=-0.9,
    max_value=5.0,
    allow_nan=False,
    allow_infinity=False,
)

# A sequence of period returns. Length bounded (max_size 40) so compounded
# products over the series stay numerically well-behaved.
_RETURNS = st.lists(_RETURN, min_size=0, max_size=40)

# Non-negative period returns (for the "MDD == 0" branch of Property 7).
_NON_NEG_RETURN = st.floats(
    min_value=0.0,
    max_value=5.0,
    allow_nan=False,
    allow_infinity=False,
)
_NON_NEG_RETURNS = st.lists(_NON_NEG_RETURN, min_size=0, max_size=40)


def _independent_cumulative_return(returns: list[float]) -> float:
    """Reference ``∏(1 + r) − 1`` computed independently of the implementation."""
    product = 1.0
    for r in returns:
        product *= 1.0 + r
    return product - 1.0


# ---------------------------------------------------------------------------
# Property 6: cumulative return is the product of per-period gross returns.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(_RETURNS)
def test_cumulative_return_equals_product_of_gross_returns(returns):
    """P6: ``cumulative_return`` equals ``∏(1 + r_t) − 1`` for any sequence.

    **Validates: Requirements 5.1**
    """
    expected = _independent_cumulative_return(returns)
    actual = cumulative_return(returns)

    assert math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12), (
        f"cumulative_return={actual} != product-based {expected} for {returns}"
    )


@settings(max_examples=100)
@given(st.integers(min_value=0, max_value=40))
def test_cumulative_return_zero_for_all_zeros(length):
    """P6: an all-zeros sequence (any length, incl. empty) yields exactly 0.0.

    A zero return each period means the invested capital never grows, so the
    compounded product is 1 and the cumulative return is 0.

    **Validates: Requirements 5.1**
    """
    returns = [0.0] * length
    assert cumulative_return(returns) == 0.0


# ---------------------------------------------------------------------------
# Property 7: bounds and invariants of Max_Drawdown.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(_RETURNS)
def test_max_drawdown_within_bounds(returns):
    """P7: ``max_drawdown`` always lies within ``[−1, 0]``.

    A drawdown cannot exceed a total loss of capital (−1) and, since the equity
    curve starts at its own first peak, can never be positive.

    **Validates: Requirements 5.4**
    """
    mdd = max_drawdown(returns)
    # Tiny slack for floating-point arithmetic on the equity/peak ratio.
    assert -1.0 - 1e-9 <= mdd <= 0.0 + 1e-9, f"MDD {mdd} outside [-1, 0] for {returns}"


@settings(max_examples=100)
@given(_NON_NEG_RETURNS)
def test_max_drawdown_zero_when_all_non_negative(returns):
    """P7: ``max_drawdown`` is exactly 0 when every return is >= 0.

    With no negative period the equity curve never dips below its running peak,
    so there is no drawdown.

    **Validates: Requirements 5.4**
    """
    assert max_drawdown(returns) == 0.0


@settings(max_examples=100)
@given(_RETURNS, st.integers(min_value=0, max_value=20))
def test_max_drawdown_invariant_to_trailing_zeros(returns, k):
    """P7: appending ``k`` zero-return periods at the end does not change MDD.

    Zero returns after the series leave the equity curve flat, so neither the
    running peak nor the deepest trough moves.

    **Validates: Requirements 5.4**
    """
    base = max_drawdown(returns)
    extended = max_drawdown(list(returns) + [0.0] * k)

    assert math.isclose(base, extended, rel_tol=1e-9, abs_tol=1e-12), (
        f"MDD changed after appending {k} zeros: {base} -> {extended} for {returns}"
    )


# ---------------------------------------------------------------------------
# Property 8: Sharpe is well-defined and never raises when std = 0.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(
    st.lists(_RETURN, min_size=2, max_size=40),
    st.floats(min_value=-0.5, max_value=0.5, allow_nan=False, allow_infinity=False),
)
def test_sharpe_ratio_equals_mean_over_std_when_positive_std(returns, rf):
    """P8: with positive std, ``sharpe_ratio`` == ``mean(r − rf) / std(r)``.

    **Validates: Requirements 5.3**
    """
    _, std = mean_std_period(returns)
    # Only the positive-std case is covered here; the std=0 case is a separate
    # property below.
    assume(std > 0.0)

    expected = float(np.mean(np.asarray(returns, dtype=float) - rf) / std)
    actual = sharpe_ratio(returns, rf)

    assert math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12), (
        f"sharpe_ratio={actual} != mean/std {expected} for {returns}, rf={rf}"
    )


@settings(max_examples=100)
@given(
    _RETURN,
    st.integers(min_value=1, max_value=40),
    st.floats(min_value=-0.5, max_value=0.5, allow_nan=False, allow_infinity=False),
)
def test_sharpe_ratio_zero_and_safe_when_std_zero(value, length, rf):
    """P8: a constant series (std = 0) yields a well-defined 0.0 without raising.

    When all period returns are equal the sample std is 0. The module documents
    a controlled 0.0 return (no division by zero, no exception).

    **Validates: Requirements 5.3**
    """
    returns = [value] * length
    # Confirm the generated series genuinely has zero std.
    _, std = mean_std_period(returns)
    assert std == 0.0

    result = sharpe_ratio(returns, rf)
    assert result == 0.0, f"expected 0.0 Sharpe for constant series, got {result}"


def test_sharpe_ratio_empty_series_is_zero():
    """P8: an empty series returns 0.0 (documented edge-case convention).

    **Validates: Requirements 5.3**
    """
    assert sharpe_ratio([]) == 0.0


# ---------------------------------------------------------------------------
# Property 10: hit rate is a valid ratio equal to the positive-period fraction.
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(_RETURNS)
def test_hit_rate_is_valid_positive_fraction(returns):
    """P10: ``hit_rate`` lies in ``[0, 1]`` and equals the fraction of r > 0.

    **Validates: Requirements 5.5**
    """
    actual = hit_rate(returns)
    assert 0.0 <= actual <= 1.0, f"hit_rate {actual} outside [0, 1] for {returns}"

    if len(returns) == 0:
        assert actual == 0.0
    else:
        positives = sum(1 for r in returns if r > 0.0)
        expected = positives / len(returns)
        assert math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12), (
            f"hit_rate={actual} != positive fraction {expected} for {returns}"
        )


def test_hit_rate_empty_series_is_zero():
    """P10: an empty series returns 0.0 (no positive periods).

    **Validates: Requirements 5.5**
    """
    assert hit_rate([]) == 0.0
