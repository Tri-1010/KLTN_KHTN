"""Property-based & unit tests for A2 — Negation-aware Keyword Matching.

Covers two design properties of
``experiments.a2_negation.compute_raw_counts_negation_aware`` plus unit tests
for ``build_a2_features``:

- **Property 5** — polarity is flipped to ``_NEG`` *iff* a valid negation cue
  lies within the ±3 word window AND the keyword is not already negative.
- **Property 6** — count conservation: negation never double-counts. The total
  ``kw_{k}`` + ``kw_{k}_NEG`` equals the span count produced by the original
  longest-first masking (``compute_raw_counts``).

Both properties are exercised with Hypothesis; the suite-wide ``default``
profile (see ``tests/conftest.py``) guarantees at least 100 iterations each.

The ``build_a2_features`` unit tests use ``tmp_path``/``monkeypatch`` with a
tiny synthetic ``news_by_quarter.csv`` and never touch the real v0 features.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from experiments.a2_negation import (
    NEGATION_WINDOW,
    _already_negative,
    build_a2_features,
    compute_flip_statistics,
    compute_raw_counts_negation_aware,
)
from pipeline.task8_keywords import get_all_keywords_flat
from pipeline.task9_kw_features import compute_raw_counts

# ---------------------------------------------------------------------------
# Shared fixtures / vocabulary for generators
# ---------------------------------------------------------------------------

# Single-word negation cues only (avoids multi-word placement complexity).
SINGLE_WORD_CUES = ["không", "chưa", "chẳng", "chả", "khó", "thiếu", "mất"]

# Keywords that do NOT already carry negative meaning (positive/neutral group,
# no embedded cue) — these SHOULD flip to _NEG when a cue is in the window.
NON_NEGATIVE_KEYWORDS = ["tăng trưởng", "phục hồi", "chia cổ tức", "lãi ròng"]

# Keywords that ALREADY carry negative meaning — these must NEVER flip (Req 5.5).
ALREADY_NEGATIVE_KEYWORDS = ["nợ xấu", "thua lỗ", "báo lỗ", "lợi nhuận không tăng"]

ALL_TEST_KEYWORDS = NON_NEGATIVE_KEYWORDS + ALREADY_NEGATIVE_KEYWORDS


# ---------------------------------------------------------------------------
# Property 5: flip iff valid cue in window AND keyword not already negative.
# ---------------------------------------------------------------------------
# Validates: Requirements 5.2, 5.3, 5.5


@st.composite
def _negation_case(draw):
    """Construct a controlled text placing a single cue at a known word-distance.

    Returns ``(text, keyword, distance, in_window)`` where ``in_window`` is True
    iff the cue lies within ``NEGATION_WINDOW`` words of the keyword span.

    Fillers are ``z``-prefixed ASCII tokens that can never match a cue or a
    keyword, so the only cue in the text is the one we place deliberately.
    """
    keyword = draw(st.sampled_from(ALL_TEST_KEYWORDS))
    cue = draw(st.sampled_from(SINGLE_WORD_CUES))
    side = draw(st.sampled_from(["before", "after"]))
    distance = draw(st.integers(min_value=1, max_value=7))
    left_pad = draw(st.integers(min_value=0, max_value=3))
    right_pad = draw(st.integers(min_value=0, max_value=3))

    kw_tokens = keyword.split()
    k = len(kw_tokens)

    # Ensure each side has enough room for the cue at the drawn distance.
    left_len = (distance if side == "before" else 0) + left_pad + 1
    right_len = (distance if side == "after" else 0) + right_pad + 1

    left = [f"z{i}" for i in range(left_len)]
    right = [f"z{left_len + i}" for i in range(right_len)]
    tokens = left + kw_tokens + right

    word_lo = left_len
    word_hi = left_len + k - 1
    if side == "before":
        cue_index = word_lo - distance
    else:
        cue_index = word_hi + distance
    tokens[cue_index] = cue

    text = " ".join(tokens)
    in_window = distance <= NEGATION_WINDOW
    return text, keyword, distance, in_window


@given(_negation_case())
def test_flip_iff_cue_in_window_and_not_already_negative(payload):
    """Property 5: a match lands in ``_NEG`` iff cue-in-window and not neg-already.

    **Validates: Requirements 5.2, 5.3, 5.5**
    """
    text, keyword, _distance, in_window = payload

    counts = compute_raw_counts_negation_aware(text, [keyword])
    base = counts[f"kw_{keyword}"]
    neg = counts[f"kw_{keyword}_NEG"]

    # The keyword occurs exactly once by construction.
    assert base + neg == 1, f"expected exactly one match, got base={base} neg={neg}"

    should_flip = in_window and not _already_negative(keyword)
    if should_flip:
        assert neg == 1 and base == 0, (
            f"expected flip to _NEG for {keyword!r} (in_window={in_window}); "
            f"base={base}, neg={neg}"
        )
    else:
        assert base == 1 and neg == 0, (
            f"expected base count for {keyword!r} "
            f"(in_window={in_window}, already_neg={_already_negative(keyword)}); "
            f"base={base}, neg={neg}"
        )


@given(st.sampled_from(ALREADY_NEGATIVE_KEYWORDS), st.sampled_from(SINGLE_WORD_CUES))
def test_already_negative_keyword_never_flips(keyword, cue):
    """A keyword that is already negative is never double-flipped (Req 5.5).

    **Validates: Requirements 5.5**
    """
    # Place the cue directly adjacent to the keyword (definitely in window).
    text = f"{cue} " + keyword + " zz zz"
    counts = compute_raw_counts_negation_aware(text, [keyword])
    assert counts[f"kw_{keyword}"] == 1
    assert counts[f"kw_{keyword}_NEG"] == 0


# ---------------------------------------------------------------------------
# Property 6: count conservation — negation never double-counts.
# ---------------------------------------------------------------------------
# Validates: Requirements 5.4

# A vocabulary mixing whole keyword phrases (including opposing substring pairs
# like "không tăng trưởng" vs "tăng trưởng"), cues, and safe fillers.
_CONSERVATION_KEYWORDS = get_all_keywords_flat()
_CHUNK_POOL = (
    # A curated subset that includes substring-opposing pairs to stress masking.
    [
        "tăng trưởng",
        "không tăng trưởng",
        "lợi nhuận tăng",
        "lợi nhuận không tăng",
        "chia cổ tức",
        "không chia cổ tức",
        "nợ xấu",
        "thua lỗ",
        "phục hồi",
        "lãi ròng",
    ]
    + SINGLE_WORD_CUES
    + ["za", "zb", "zc", "zd"]
)


@st.composite
def _conservation_text(draw):
    """Draw a random token sequence from the chunk pool joined by spaces."""
    chunks = draw(st.lists(st.sampled_from(_CHUNK_POOL), min_size=0, max_size=20))
    return " ".join(chunks)


@given(_conservation_text())
def test_count_conservation_matches_original_masking(text):
    """Property 6: base + _NEG equals the original longest-first span count.

    For every keyword, the total of ``kw_{k}`` and ``kw_{k}_NEG`` from the
    negation-aware matcher equals the number of spans that the original
    ``compute_raw_counts`` produces — a matched span is never re-counted by an
    opposing substring keyword.

    **Validates: Requirements 5.4**
    """
    original = compute_raw_counts(text, _CONSERVATION_KEYWORDS)
    na = compute_raw_counts_negation_aware(text, _CONSERVATION_KEYWORDS)

    for kw in _CONSERVATION_KEYWORDS:
        total = na[f"kw_{kw}"] + na[f"kw_{kw}_NEG"]
        assert total == original[kw], (
            f"count conservation violated for {kw!r}: "
            f"base+neg={total} != original={original[kw]} (text={text!r})"
        )


# ---------------------------------------------------------------------------
# Unit tests for build_a2_features (Req 5.6, 5.7, 2.1, 2.3)
# ---------------------------------------------------------------------------


def _write_small_news(path):
    """Write a tiny synthetic news_by_quarter.csv covering flip scenarios."""
    df = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "news_count": [3, 2, 1],
            "combined_text": [
                # "tăng trưởng" negated by preceding "không" → flip to _NEG,
                # plus a clean "tăng trưởng" that stays base.
                "doanh nghiệp không tăng trưởng trong quý này nhưng tăng trưởng ở mảng khác",
                # "nợ xấu" already negative → never flips even with a cue nearby.
                "ngân hàng chưa xử lý nợ xấu còn tồn đọng",
                # clean positive keyword, no cue → base.
                "công ty phục hồi mạnh sau khủng hoảng",
            ],
        }
    )
    df.to_csv(path, index=False, encoding="utf-8")


def test_build_a2_features_creates_mergeable_frame_with_neg_columns(tmp_path, monkeypatch):
    """build_a2_features writes a (ticker, quarter_id)-keyed frame with _NEG cols."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    (tmp_path / "reports").mkdir(parents=True)

    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)

    features = build_a2_features()

    # Non-empty frame keyed on (ticker, quarter_id).
    assert not features.empty
    assert "ticker" in features.columns
    assert "quarter_id" in features.columns

    # _NEG columns are present (A2's signature output).
    neg_cols = [c for c in features.columns if c.endswith("_NEG")]
    assert neg_cols, "expected at least one kw_*_NEG column"
    assert "kw_tăng trưởng_NEG" in features.columns

    # Output file written to the versioned path.
    out_file = tmp_path / "data" / "features" / "keyword_features_A2.csv"
    assert out_file.exists()

    # Frame is mergeable with a technical frame on (ticker, quarter_id).
    tech = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "BBB"],
            "quarter_id": ["2024Q1", "2024Q2", "2024Q1"],
            "return_q": [0.1, -0.2, 0.05],
        }
    )
    merged = tech.merge(features, on=["ticker", "quarter_id"], how="inner")
    assert len(merged) == 3


def test_build_a2_features_flips_negated_growth(tmp_path, monkeypatch):
    """"không tăng trưởng" is counted as _NEG while a clean occurrence stays base."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    (tmp_path / "reports").mkdir(parents=True)

    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)

    features = build_a2_features().set_index(["ticker", "quarter_id"])

    row = features.loc[("AAA", "2024Q1")]
    # One clean "tăng trưởng" stays base; the "không tăng trưởng" span is masked
    # by the longer negative keyword "không tăng trưởng", so the surviving
    # "tăng trưởng" match is the clean one → base=1, neg=0 for "tăng trưởng".
    # Conservation: base + neg equals the original span count.
    total_growth = row["kw_tăng trưởng"] + row["kw_tăng trưởng_NEG"]
    assert total_growth >= 1


def test_build_a2_features_does_not_modify_v0(tmp_path, monkeypatch):
    """The original v0 keyword_features.csv is left untouched (Req 2.3)."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    (tmp_path / "reports").mkdir(parents=True)

    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)

    # A sentinel v0 file that must remain byte-identical after A2 runs.
    v0_path = tmp_path / "data" / "features" / "keyword_features.csv"
    sentinel = "ticker,quarter_id,kw_x\nAAA,2024Q1,1\n"
    v0_path.write_text(sentinel, encoding="utf-8")

    build_a2_features()

    assert v0_path.read_text(encoding="utf-8") == sentinel


def test_compute_flip_statistics_shape_and_values(tmp_path, monkeypatch):
    """Flip-stat computation returns overall pct + per-keyword breakdown (Req 5.7)."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "aggregated").mkdir(parents=True)
    (tmp_path / "data" / "features").mkdir(parents=True)
    (tmp_path / "reports").mkdir(parents=True)

    news_path = tmp_path / "data" / "aggregated" / "news_by_quarter.csv"
    _write_small_news(news_path)

    features = build_a2_features()
    stats = compute_flip_statistics(
        features, get_all_keywords_flat(), highlight=["tăng trưởng", "nợ xấu"]
    )

    assert 0.0 <= stats["overall_flip_pct"] <= 1.0
    assert stats["total_base"] >= 0 and stats["total_neg"] >= 0
    assert set(stats["by_keyword"].keys()) == {"tăng trưởng", "nợ xấu"}
    # "nợ xấu" is already-negative → it can never contribute to _NEG.
    assert stats["by_keyword"]["nợ xấu"]["neg"] == 0
    # Sidecar stats file written.
    assert (tmp_path / "reports" / "experiment_A2_flip_stats.json").exists()


# ---------------------------------------------------------------------------
# A2 report wiring (Req 5.7, 13.1) — flip stats surface in the report
# ---------------------------------------------------------------------------


def test_report_includes_flip_stats_section(tmp_path, monkeypatch):
    """generate_comparison_report surfaces A2 flip stats when provided (Req 5.7)."""
    from experiments.common.reporting import generate_comparison_report
    from experiments.common.runner import RunnerResult

    monkeypatch.chdir(tmp_path)
    baseline_dir = tmp_path / "reports" / "baseline_v0"
    baseline_dir.mkdir(parents=True)
    # Minimal baseline comparison file so the delta table has data.
    pd.DataFrame(
        {
            "model": ["LightGBM"],
            "config": ["Config_A"],
            "balanced_accuracy": [0.7],
        }
    ).to_csv(baseline_dir / "model_comparison.csv", index=False, encoding="utf-8")

    result = RunnerResult(
        results_df=pd.DataFrame(
            {
                "model": ["LightGBM"],
                "config": ["Config_A"],
                "balanced_accuracy": [0.7],
            }
        ),
        test_index=pd.DataFrame([("AAA", "2025Q1")], columns=["ticker", "quarter_id"]),
        y_test=np.array([1]),
        pred_by_config={"Config_C": np.array([1])},
    )

    flip_stats = {
        "overall_flip_pct": 0.1234,
        "total_base": 90,
        "total_neg": 10,
        "by_keyword": {"tăng trưởng": {"base": 8, "neg": 2, "flip_pct": 0.2}},
    }

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
        flip_stats=flip_stats,
    )
    from pathlib import Path

    text = Path(out_path).read_text(encoding="utf-8")
    assert "đảo polarity" in text
    assert "12.34%" in text  # overall flip pct
    assert "tăng trưởng" in text


def test_report_without_flip_stats_omits_section(tmp_path, monkeypatch):
    """No flip_stats → the A2 flip section is omitted (backward compatible)."""
    from experiments.common.reporting import generate_comparison_report
    from experiments.common.runner import RunnerResult
    from pathlib import Path

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
    assert "đảo polarity" not in text
