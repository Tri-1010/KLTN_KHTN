"""Property-based tests for the Feature Registry and Feature_Column_Classifier.

Covers two design properties of ``identify_feature_columns()`` (in
``pipeline/task10_train.py``), extended by ``experiments/feature_registry.py``:

- **Property 1** — new text-feature columns are always classified as keyword.
- **Property 2** — the fixed 16-feature Config_A technical set is invariant no
  matter which keyword columns are added alongside it.

Both properties are exercised with Hypothesis. The suite-wide ``default``
Hypothesis profile (see ``tests/conftest.py``) guarantees at least 100
iterations per property.
"""

from __future__ import annotations

import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from experiments.feature_registry import (
    NEG_SUFFIX,
    NEW_KW_EXACT,
    NEW_KW_PREFIXES,
)
from pipeline.task10_train import identify_feature_columns


# ---------------------------------------------------------------------------
# Shared constants / strategies
# ---------------------------------------------------------------------------

META_COLS = ["ticker", "quarter_id", "label_basic"]

# The 16 fixed technical features of Config_A, read from the real project header
# ``data/features/technical_features.csv``. These must always remain technical.
CONFIG_A_TECH_FEATURES = [
    "return_q",
    "return_mean_daily",
    "return_std_daily",
    "volatility_q",
    "price_range_q",
    "volume_mean_q",
    "volume_change_q",
    "sma20_end",
    "ema20_end",
    "price_vs_sma20",
    "rsi_mean_q",
    "rsi_end_q",
    "macd_hist_mean_q",
    "bb_position_q",
    "return_prev_q",
    "return_2q_ago",
]

# Existing keyword rules already baked into identify_feature_columns; used to
# avoid accidentally generating a "technical" name that matches a keyword rule.
_EXISTING_KW_PREFIXES = ("kw_", "kw_norm_", "tfidf_")
_EXISTING_KW_EXACT = {
    "pos_score",
    "neg_score",
    "sentiment_ratio",
    "news_count",
    "news_count_log",
    "has_min_news",
    "combined_text",
}
_ALL_KW_PREFIXES = _EXISTING_KW_PREFIXES + tuple(NEW_KW_PREFIXES)


def _looks_like_keyword(col: str) -> bool:
    """True if *col* would match ANY keyword rule (existing or new)."""
    if col in _EXISTING_KW_EXACT or col in NEW_KW_EXACT:
        return True
    if any(col.startswith(p) for p in _ALL_KW_PREFIXES):
        return True
    if col.endswith(NEG_SUFFIX):
        return True
    return False


# Base tokens for building "safe" technical (non-keyword) column names.
_TECH_TOKENS = [
    "return", "volatility", "rsi", "macd", "bb", "sma", "ema", "price",
    "volume", "momentum", "beta", "alpha", "spread", "range", "trend",
]

# A safe technical column name: alnum/underscore, does not match any kw rule.
_safe_tech_names = (
    st.lists(st.sampled_from(_TECH_TOKENS), min_size=1, max_size=3)
    .map(lambda parts: "_".join(parts))
    .filter(lambda name: not _looks_like_keyword(name))
)

# Suffixes to build distinct new-text-feature column names per group.
_kw_base_tokens = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=1,
    max_size=6,
)


def _new_prefix_columns(draw) -> list[str]:
    """Draw a few columns using the registered new keyword prefixes."""
    cols = []
    for prefix in draw(
        st.lists(st.sampled_from(NEW_KW_PREFIXES), min_size=0, max_size=len(NEW_KW_PREFIXES), unique=True)
    ):
        suffix = draw(_kw_base_tokens)
        cols.append(f"{prefix}{suffix}")
    return cols


# ---------------------------------------------------------------------------
# Property 1: New text feature columns are always classified as keyword.
# ---------------------------------------------------------------------------
# Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.7


@st.composite
def _mixed_dataframe(draw):
    """Generate a DataFrame mixing meta, technical, and new-text-feature cols.

    Returns ``(df, new_text_cols)`` where ``new_text_cols`` is the set of
    generated columns that must land in the keyword group.
    """
    new_text_cols: list[str] = []

    # A2 negation columns: kw_{base}_NEG
    for base in draw(st.lists(_kw_base_tokens, min_size=0, max_size=3, unique=True)):
        new_text_cols.append(f"kw_{base}{NEG_SUFFIX}")

    # Prefix-based new columns (sent_, llm_, ds_, sector_, emb_, tfidfx_)
    new_text_cols.extend(_new_prefix_columns(draw))

    # Exact-name new columns (A3/B5)
    new_text_cols.extend(
        draw(st.lists(st.sampled_from(sorted(NEW_KW_EXACT)), min_size=0, max_size=len(NEW_KW_EXACT), unique=True))
    )

    # Technical (non-keyword) columns.
    tech_cols = draw(st.lists(_safe_tech_names, min_size=0, max_size=4, unique=True))

    # Ensure at least one new-text-feature column exists so the property is
    # non-vacuous for most examples (Hypothesis still explores the empty case).
    if not new_text_cols:
        new_text_cols.append("news_velocity")

    # De-duplicate while keeping a set for membership checks; make column names
    # unique across the whole frame to build a valid DataFrame.
    all_cols = list(dict.fromkeys(META_COLS + tech_cols + new_text_cols))
    data = {col: [0.0] for col in all_cols}
    df = pd.DataFrame(data)
    return df, set(new_text_cols)


@given(_mixed_dataframe())
def test_new_text_features_are_classified_as_keyword(payload):
    """Property 1: every new text-feature column lands in ``kw_cols``.

    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.7**
    """
    df, new_text_cols = payload
    _tech_cols, kw_cols = identify_feature_columns(df)
    kw_set = set(kw_cols)

    for col in new_text_cols:
        assert col in kw_set, (
            f"New text-feature column {col!r} was not classified as keyword; "
            f"kw_cols={sorted(kw_set)}"
        )


# ---------------------------------------------------------------------------
# Property 2: Config_A technical feature set is invariant.
# ---------------------------------------------------------------------------
# Validates: Requirements 3.6, 14.2, 14.3


@st.composite
def _keyword_columns(draw):
    """Draw an arbitrary, possibly empty, set of keyword column names."""
    cols: list[str] = []

    # Existing keyword-prefix columns.
    for prefix in draw(st.lists(st.sampled_from(_EXISTING_KW_PREFIXES), min_size=0, max_size=3, unique=True)):
        cols.append(f"{prefix}{draw(_kw_base_tokens)}")

    # Existing exact keyword columns.
    cols.extend(
        draw(st.lists(st.sampled_from(sorted(_EXISTING_KW_EXACT)), min_size=0, max_size=4, unique=True))
    )

    # New-registry columns: A2 negation, prefixes, and exact names.
    for base in draw(st.lists(_kw_base_tokens, min_size=0, max_size=2, unique=True)):
        cols.append(f"kw_{base}{NEG_SUFFIX}")
    cols.extend(_new_prefix_columns(draw))
    cols.extend(
        draw(st.lists(st.sampled_from(sorted(NEW_KW_EXACT)), min_size=0, max_size=len(NEW_KW_EXACT), unique=True))
    )

    return cols


@given(_keyword_columns())
def test_config_a_technical_set_is_invariant(keyword_cols):
    """Property 2: tech_cols equals exactly the 16 fixed technical features.

    No matter which keyword columns are added alongside the 16 fixed technical
    columns (plus meta columns), ``identify_feature_columns`` returns exactly
    those 16 technical columns in ``tech_cols`` — Config_A never drifts.

    **Validates: Requirements 3.6, 14.2, 14.3**
    """
    # Build a frame: meta + 16 fixed technical + arbitrary keyword columns.
    # Column order is shuffled implicitly by dict de-duplication order but the
    # returned set must be exactly the 16 technical features.
    all_cols = list(dict.fromkeys(META_COLS + CONFIG_A_TECH_FEATURES + keyword_cols))
    df = pd.DataFrame({col: [0.0] for col in all_cols})

    tech_cols, _kw_cols = identify_feature_columns(df)

    assert set(tech_cols) == set(CONFIG_A_TECH_FEATURES), (
        "Config_A technical set drifted: "
        f"expected {sorted(CONFIG_A_TECH_FEATURES)}, got {sorted(tech_cols)}"
    )
    assert len(tech_cols) == 16, f"Expected 16 technical features, got {len(tech_cols)}"
