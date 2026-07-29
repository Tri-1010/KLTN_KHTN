"""Property-based & unit tests for A1 — Signed Group Sentiment Score.

Covers design **Property 7** for
``experiments.a1_group_sentiment.compute_group_sentiment`` plus unit tests for
the ``build_a1a_features`` / ``build_a1b_features`` builders.

- **Property 7** — ``sent_{G}`` equals the signed formula (Σ kw_norm of positive
  group keywords − Σ kw_norm of negative group keywords) and is monotonically
  increasing in the positive contribution when the negative contribution is held
  constant.

The property is exercised with Hypothesis; the suite-wide ``default`` profile
(see ``tests/conftest.py``) guarantees at least 100 iterations.

The builder unit tests use ``tmp_path``/``monkeypatch`` with a tiny synthetic
``news_by_quarter.csv`` and never touch the real v0 features.
"""

from __future__ import annotations

import math

import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from experiments.a1_group_sentiment import (
    GROUP_NAMES,
    build_a1a_features,
    build_a1b_features,
    compute_group_sentiment,
)
from pipeline.task8_keywords import (
    KEYWORD_GROUPS,
    get_all_keywords_flat,
    get_curated_keywords,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALL_KEYWORDS = get_all_keywords_flat()
_KW_NORM_COLS = [f"kw_norm_{kw}" for kw in _ALL_KEYWORDS]


def _expected_group_sentiment(row: pd.Series, group: str) -> float:
    """Reference formula for sent_{G} from a row of kw_norm_* values."""
    group_data = KEYWORD_GROUPS[group]
    pos = sum(
        float(row.get(f"kw_norm_{kw}", 0.0))
        for kw in group_data.get("positive", [])
    )
    neg = sum(
        float(row.get(f"kw_norm_{kw}", 0.0))
        for kw in group_data.get("negative", [])
    )
    return pos - neg


# ---------------------------------------------------------------------------
# Property 7: signed group sentiment formula + monotonicity.
# ---------------------------------------------------------------------------
# Validates: Requirements 6.1, 6.2


@st.composite
def _kw_norm_frame(draw):
    """Draw a single-row DataFrame with random kw_norm_* values in [0, 5]."""
    values = draw(
        st.lists(
            st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False),
            min_size=len(_KW_NORM_COLS),
            max_size=len(_KW_NORM_COLS),
        )
    )
    data = {col: [val] for col, val in zip(_KW_NORM_COLS, values)}
    data["ticker"] = ["AAA"]
    data["quarter_id"] = ["2024Q1"]
    data["news_count"] = [3]
    return pd.DataFrame(data)


@given(_kw_norm_frame())
def test_group_sentiment_matches_signed_formula(df):
    """Property 7: sent_{G} equals Σ pos kw_norm − Σ neg kw_norm.

    **Validates: Requirements 6.1, 6.2**
    """
    out = compute_group_sentiment(df)
    row = out.iloc[0]
    for group in GROUP_NAMES:
        expected = _expected_group_sentiment(row, group)
        actual = float(out.iloc[0][f"sent_{group}"])
        assert math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9), (
            f"sent_{group}: expected {expected}, got {actual}"
        )


@given(
    _kw_norm_frame(),
    st.floats(min_value=0.01, max_value=5.0, allow_nan=False, allow_infinity=False),
)
def test_group_sentiment_monotonic_in_positive_contribution(df, bump):
    """Property 7: increasing positive kw_norm (neg fixed) never decreases sent.

    For every group that has at least one positive keyword, bumping one of its
    positive kw_norm columns while holding negatives constant strictly increases
    ``sent_{G}``.

    **Validates: Requirements 6.1, 6.2**
    """
    base = compute_group_sentiment(df)

    for group in GROUP_NAMES:
        positives = KEYWORD_GROUPS[group].get("positive", [])
        if not positives:
            # Neutral-only group (e.g. F): sent stays 0, skip monotonicity.
            continue
        bumped = df.copy()
        col = f"kw_norm_{positives[0]}"
        bumped[col] = bumped[col] + bump
        bumped_out = compute_group_sentiment(bumped)

        before = float(base.iloc[0][f"sent_{group}"])
        after = float(bumped_out.iloc[0][f"sent_{group}"])
        assert after > before, (
            f"sent_{group} should increase when positive contribution grows: "
            f"before={before}, after={after}"
        )


def test_neutral_only_group_is_zero():
    """A group without positive/negative keywords emits sent_ == 0 (schema)."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "quarter_id": ["2024Q1"],
            "news_count": [3],
            **{col: [1.0] for col in _KW_NORM_COLS},
        }
    )
    out = compute_group_sentiment(df)
    # Find any neutral-only group (has neither positive nor negative).
    neutral_only = [
        g
        for g in GROUP_NAMES
        if not KEYWORD_GROUPS[g].get("positive")
        and not KEYWORD_GROUPS[g].get("negative")
    ]
    assert neutral_only, "expected at least one neutral-only group (e.g. F)"
    for g in neutral_only:
        assert f"sent_{g}" in out.columns
        assert float(out.iloc[0][f"sent_{g}"]) == 0.0


# ---------------------------------------------------------------------------
# Unit tests for build_a1a_features / build_a1b_features (Req 6.3, 6.4, 2.1, 2.3)
# ---------------------------------------------------------------------------


def _write_small_news(path):
    """Write a tiny synthetic news_by_quarter.csv."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "news_count": [3, 2, 1],
            "combined_text": [
                "lợi nhuận tăng doanh thu tăng tăng trưởng mạnh chia cổ tức",
                "nợ xấu tăng thua lỗ áp lực tài chính",
                "đại hội cổ đông họp hđqt phục hồi",
            ],
        }
    )
    df.to_csv(path, index=False, encoding="utf-8")


def _setup_workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    (tmp_path / "reports").mkdir(parents=True)
    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)
    return news_path


def test_build_a1a_has_only_sent_coverage_and_keys(tmp_path, monkeypatch):
    """A1a contains only sent_*, coverage, and (ticker, quarter_id) keys (Req 6.3)."""
    _setup_workspace(tmp_path, monkeypatch)

    features = build_a1a_features()

    assert not features.empty
    expected_cols = (
        {"ticker", "quarter_id"}
        | {"news_count", "news_count_log", "has_min_news"}
        | {f"sent_{g}" for g in GROUP_NAMES}
    )
    assert set(features.columns) == expected_cols

    # No raw keyword / tfidf columns leaked into A1a.
    assert not [c for c in features.columns if c.startswith("kw_")]
    assert not [c for c in features.columns if c.startswith("tfidf_")]

    # Output file written to the versioned path.
    assert (tmp_path / "data" / "features" / "keyword_features_A1a.csv").exists()


def test_build_a1b_contains_v0_columns_plus_sent(tmp_path, monkeypatch):
    """A1b = v0 frequency columns + sent_A..F (Req 6.4)."""
    _setup_workspace(tmp_path, monkeypatch)

    features = build_a1b_features()

    assert not features.empty
    # sent_* present.
    for g in GROUP_NAMES:
        assert f"sent_{g}" in features.columns
    # v0 frequency columns present.
    assert [c for c in features.columns if c.startswith("kw_")]
    assert [c for c in features.columns if c.startswith("kw_norm_")]
    assert [c for c in features.columns if c.startswith("tfidf_")]
    assert {"pos_score", "neg_score", "sentiment_ratio"}.issubset(features.columns)
    # combined_text dropped.
    assert "combined_text" not in features.columns

    assert (tmp_path / "data" / "features" / "keyword_features_A1b.csv").exists()


def test_a1a_and_a1b_are_mergeable_on_keys(tmp_path, monkeypatch):
    """Both A1a and A1b merge cleanly with a technical frame on the keys (Req 2.1)."""
    _setup_workspace(tmp_path, monkeypatch)

    a1a = build_a1a_features()
    a1b = build_a1b_features()

    tech = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "return_q": [0.1, -0.2, 0.05],
        }
    )
    merged_a = tech.merge(a1a, on=["ticker", "quarter_id"], how="inner")
    merged_b = tech.merge(a1b, on=["ticker", "quarter_id"], how="inner")
    assert len(merged_a) == 3
    assert len(merged_b) == 3


def test_build_a1_does_not_modify_v0(tmp_path, monkeypatch):
    """The original v0 keyword_features.csv is left untouched (Req 2.3)."""
    _setup_workspace(tmp_path, monkeypatch)

    v0_path = tmp_path / "data" / "features" / "keyword_features.csv"
    sentinel = "ticker,quarter_id,kw_x\nAAA,2024Q1,1\n"
    v0_path.write_text(sentinel, encoding="utf-8")

    build_a1a_features()
    build_a1b_features()

    assert v0_path.read_text(encoding="utf-8") == sentinel


def test_a1b_sent_matches_v0_signed_formula(tmp_path, monkeypatch):
    """sent_{G} in A1b matches the signed kw_norm formula on real curated data."""
    _setup_workspace(tmp_path, monkeypatch)

    a1b = build_a1b_features().set_index(["ticker", "quarter_id"])
    row = a1b.loc[("AAA", "2024Q1")]
    for group in GROUP_NAMES:
        expected = _expected_group_sentiment(row, group)
        assert math.isclose(
            float(row[f"sent_{group}"]), expected, rel_tol=1e-9, abs_tol=1e-9
        )


# ---------------------------------------------------------------------------
# A1 report wiring (Req 6.5) — feature counts surface in the report
# ---------------------------------------------------------------------------


def test_report_includes_feature_counts_section(tmp_path, monkeypatch):
    """generate_comparison_report surfaces A1 feature counts when provided (Req 6.5)."""
    import numpy as np
    from pathlib import Path

    from experiments.common.reporting import generate_comparison_report
    from experiments.common.runner import RunnerResult

    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    pd.DataFrame(
        {"model": ["LightGBM"], "config": ["Config_A"], "balanced_accuracy": [0.7]}
    ).to_csv(baseline_dir / "model_comparison.csv", index=False, encoding="utf-8")

    result = RunnerResult(
        results_df=pd.DataFrame(
            {"model": ["LightGBM"], "config": ["Config_A"], "balanced_accuracy": [0.7]}
        ),
        test_index=pd.DataFrame([("AAA", "2025Q1")], columns=["ticker", "quarter_id"]),
        y_test=np.array([1]),
        pred_by_config={"Config_C": np.array([1])},
    )

    out_path = generate_comparison_report(
        experiment_id="A1a",
        new_results=result,
        baseline_dir=str(baseline_dir),
        baseline_config_c={
            "test_index": pd.DataFrame(
                [("AAA", "2025Q1")], columns=["ticker", "quarter_id"]
            ),
            "y_test": np.array([1]),
            "pred_by_config": {"Config_C": np.array([1])},
        },
        feature_counts={"exp_feature_count": 9, "v0_feature_count": 213},
    )

    text = Path(out_path).read_text(encoding="utf-8")
    assert "Số lượng đặc trưng" in text
    assert "9" in text
    assert "213" in text


def test_report_without_feature_counts_omits_section(tmp_path, monkeypatch):
    """No feature_counts → the A1 feature-count section is omitted (backward compat)."""
    import numpy as np
    from pathlib import Path

    from experiments.common.reporting import generate_comparison_report
    from experiments.common.runner import RunnerResult

    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    pd.DataFrame(
        {"model": ["LightGBM"], "config": ["Config_A"], "balanced_accuracy": [0.7]}
    ).to_csv(baseline_dir / "model_comparison.csv", index=False, encoding="utf-8")

    result = RunnerResult(
        results_df=pd.DataFrame(
            {"model": ["LightGBM"], "config": ["Config_A"], "balanced_accuracy": [0.7]}
        ),
        test_index=pd.DataFrame([("AAA", "2025Q1")], columns=["ticker", "quarter_id"]),
        y_test=np.array([1]),
        pred_by_config={"Config_C": np.array([1])},
    )
    out_path = generate_comparison_report(
        experiment_id="A3",
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
    text = Path(out_path).read_text(encoding="utf-8")
    assert "Số lượng đặc trưng" not in text
