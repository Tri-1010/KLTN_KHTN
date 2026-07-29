"""Property-based tests for the B3 Segment_Mapper (Req 10.1, 10.2).

Feature: text-feature-experiments, Property 11: ánh xạ phân khúc phủ toàn bộ và
duy nhất — for any configured ticker universe, :func:`assign_segments` maps each
ticker to exactly one sector and exactly one cap_group in ``{large_cap,
mid_cap}``, so that the union of segments covers the whole ticker set and no
ticker lands in two cap_groups.

The property is exercised with Hypothesis by generating random non-empty subsets
of the known HOSE-80 tickers, writing them to a temporary YAML config file, and
calling :func:`assign_segments` against that config. The suite-wide ``default``
Hypothesis profile (see ``tests/conftest.py``) guarantees at least 100 iterations
per property.
"""

from __future__ import annotations

import os
import tempfile

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from experiments.common import segments
from experiments.common.segments import (
    LARGE_CAP_TICKERS,
    SECTOR_MAP,
    SegmentInfo,
    assign_segments,
)

# Valid sector enum set from the design (names written without spaces).
VALID_SECTORS = {
    "Banking",
    "Securities",
    "RealEstate",
    "Industrial",
    "Energy",
    "Consumer",
    "Technology",
    "Transport",
}

VALID_CAP_GROUPS = {"large_cap", "mid_cap"}

# Deterministic pool of all known tickers to sample configuration subsets from.
TICKER_POOL = sorted(SECTOR_MAP.keys())


def _write_temp_config(tickers: list[str]) -> str:
    """Write a ``{"tickers": [...]}`` YAML config to a temp file, return path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    )
    try:
        yaml.safe_dump({"tickers": tickers}, tmp, allow_unicode=True)
    finally:
        tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Property 11: coverage-complete and unique segment mapping.
# ---------------------------------------------------------------------------
# Feature: text-feature-experiments, Property 11: assign_segments assigns each
# configured ticker exactly one sector and one cap_group in {large_cap, mid_cap};
# the union of segments covers the whole ticker set and no ticker is in two
# cap_groups.


@settings(max_examples=100)
@given(
    st.lists(
        st.sampled_from(TICKER_POOL),
        min_size=1,
        max_size=len(TICKER_POOL),
        unique=True,
    )
)
def test_segments_cover_all_tickers_uniquely(configured_tickers):
    """Property 11: segment mapping is coverage-complete and unique.

    For a randomly configured ticker universe, ``assign_segments`` returns a
    mapping whose keys equal exactly the configured tickers, where each ticker
    maps to exactly one valid sector and exactly one cap_group in
    ``{large_cap, mid_cap}`` (never both), consistent with LARGE_CAP_TICKERS.

    **Validates: Requirements 10.1, 10.2**
    """
    config_path = _write_temp_config(configured_tickers)
    try:
        result = assign_segments(config_path=config_path)
    finally:
        os.unlink(config_path)

    configured_set = set(configured_tickers)

    # 1. Coverage: keys equal exactly the configured tickers (no extras/missing).
    assert set(result.keys()) == configured_set

    for ticker in configured_tickers:
        info = result[ticker]
        # 2. Each ticker maps to exactly one SegmentInfo tied to that ticker.
        assert isinstance(info, SegmentInfo)
        assert info.ticker == ticker

        # 3. Sector is one of the valid enum values.
        assert info.sector in VALID_SECTORS
        assert info.sector == SECTOR_MAP[ticker]

        # 4. cap_group is exactly one value in {large_cap, mid_cap}, never both.
        assert info.cap_group in VALID_CAP_GROUPS
        expected_cap = "large_cap" if ticker in LARGE_CAP_TICKERS else "mid_cap"
        assert info.cap_group == expected_cap

    # 5. No ticker in two cap_groups: the large_cap and mid_cap key sets are
    #    disjoint and their union covers the whole configured universe.
    large = {t for t, i in result.items() if i.cap_group == "large_cap"}
    mid = {t for t, i in result.items() if i.cap_group == "mid_cap"}
    assert large.isdisjoint(mid)
    assert large | mid == configured_set


def test_default_config_has_80_tickers_with_expected_cap_distribution():
    """The default config yields all 80 HOSE-80 tickers with 30/50 cap split.

    **Validates: Requirements 10.1, 10.2**
    """
    result = assign_segments()

    assert len(result) == 80

    large = [t for t, i in result.items() if i.cap_group == "large_cap"]
    mid = [t for t, i in result.items() if i.cap_group == "mid_cap"]
    assert len(large) == 30
    assert len(mid) == 50

    # Every ticker has a valid sector and a single valid cap_group.
    for info in result.values():
        assert info.sector in VALID_SECTORS
        assert info.cap_group in VALID_CAP_GROUPS
