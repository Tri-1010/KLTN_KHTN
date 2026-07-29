"""Tests for period-granularity experiment helpers."""

from __future__ import annotations

import pandas as pd

from pipeline.experiment_period import make_period_funcs


def test_make_period_funcs_supports_one_week_buckets():
    assign_fn, next_fn = make_period_funcs("1week")

    first = assign_fn(pd.Timestamp("2022-01-03"))
    same_bucket = assign_fn(pd.Timestamp("2022-01-06"))
    next_bucket = assign_fn(pd.Timestamp("2022-01-07"))

    assert first == same_bucket
    assert next_bucket == next_fn(first)
    assert next_bucket > first


def test_make_period_funcs_supports_one_day_buckets():
    assign_fn, next_fn = make_period_funcs("1day")

    day1 = assign_fn(pd.Timestamp("2022-01-03"))
    day2 = assign_fn(pd.Timestamp("2022-01-04"))
    day3 = assign_fn(pd.Timestamp("2022-01-05"))

    assert day2 == next_fn(day1)
    assert day3 == next_fn(day2)
    assert [day1, day2, day3] == sorted([day3, day1, day2])
