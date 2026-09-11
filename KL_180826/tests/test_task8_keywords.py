"""
Unit tests for TASK 8: Keyword_Builder module.

Tests cover:
- Keyword candidate extraction via CountVectorizer (Req 8.1)
- Curated keyword list structure and completeness (Req 8.2)
- Keyword JSON output structure (Req 8.3, 8.4)
- Corpus frequency computation (Req 8.5)
- Sentiment direction assignment
"""

import json
import os
import tempfile

import pandas as pd
import pytest

from pipeline.task8_keywords import (
    KEYWORD_GROUPS,
    build_keyword_list,
    compute_corpus_frequency,
    extract_candidates,
    get_all_keywords_flat,
    get_curated_keywords,
    save_keywords_by_group,
    save_keywords_finance,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_corpus():
    """Small Vietnamese financial news corpus for testing."""
    return [
        "lợi nhuận tăng mạnh doanh thu tăng trưởng kỷ lục quý này",
        "nợ xấu tăng áp lực tài chính lớn dòng tiền âm",
        "đại hội cổ đông thường niên thay đổi lãnh đạo mới",
        "chia cổ tức tiền mặt cổ tức cao hơn năm trước",
        "bị phạt vi phạm quy định bị thanh tra kiểm toán",
        "ký kết hợp đồng mở rộng thị trường xuất khẩu tăng",
        "lợi nhuận giảm sụt giảm doanh thu giảm mạnh",
        "giảm nợ trả nợ cải thiện tài chính dòng tiền dương",
        "sáp nhập mua lại thoái vốn phát hành cổ phiếu mới",
        "hủy hợp đồng dự án trì hoãn đóng cửa nhà máy",
    ]


@pytest.fixture
def tmp_dir():
    """Temporary directory for output files."""
    with tempfile.TemporaryDirectory() as d:
        yield d


# ---------------------------------------------------------------------------
# Curated keyword list tests (Req 8.2)
# ---------------------------------------------------------------------------


class TestCuratedKeywords:
    """Test the hardcoded curated keyword list."""

    def test_six_groups_exist(self):
        """KEYWORD_GROUPS should have exactly 6 groups A-F."""
        assert set(KEYWORD_GROUPS.keys()) == {"A", "B", "C", "D", "E", "F"}

    def test_each_group_has_name(self):
        """Each group should have a 'name' field."""
        for group_id, data in KEYWORD_GROUPS.items():
            assert "name" in data, f"Group {group_id} missing 'name'"
            assert isinstance(data["name"], str)

    def test_group_a_positive_count(self):
        """Group A positive list should be non-empty and contain core terms."""
        pos = KEYWORD_GROUPS["A"]["positive"]
        assert len(pos) >= 9
        assert "lợi nhuận tăng" in pos
        assert "tăng trưởng" in pos

    def test_group_a_negative_count(self):
        """Group A negative list should include negation phrases and core terms."""
        neg = KEYWORD_GROUPS["A"]["negative"]
        assert len(neg) >= 9
        assert "lợi nhuận giảm" in neg
        # Negation phrases added for the improved keyword method
        assert "lợi nhuận không tăng" in neg
        assert "không tăng trưởng" in neg

    def test_group_b_positive_count(self):
        """Group B should have 6 positive keywords."""
        assert len(KEYWORD_GROUPS["B"]["positive"]) == 6

    def test_group_b_negative_count(self):
        """Group B should have 5 negative keywords."""
        assert len(KEYWORD_GROUPS["B"]["negative"]) == 5

    def test_group_c_positive_count(self):
        """Group C should have 6 positive keywords."""
        assert len(KEYWORD_GROUPS["C"]["positive"]) == 6

    def test_group_c_negative_count(self):
        """Group C should have 7 negative keywords."""
        assert len(KEYWORD_GROUPS["C"]["negative"]) == 7

    def test_group_d_positive_count(self):
        """Group D should have 7 positive keywords."""
        assert len(KEYWORD_GROUPS["D"]["positive"]) == 7

    def test_group_d_negative_count(self):
        """Group D should have 5 negative keywords."""
        assert len(KEYWORD_GROUPS["D"]["negative"]) == 5

    def test_group_e_negative_only(self):
        """Group E should have only negative keywords (10)."""
        assert "positive" not in KEYWORD_GROUPS["E"]
        assert "neutral" not in KEYWORD_GROUPS["E"]
        assert len(KEYWORD_GROUPS["E"]["negative"]) == 10

    def test_group_f_neutral_only(self):
        """Group F should have only neutral keywords (9)."""
        assert "positive" not in KEYWORD_GROUPS["F"]
        assert "negative" not in KEYWORD_GROUPS["F"]
        assert len(KEYWORD_GROUPS["F"]["neutral"]) == 9

    def test_get_curated_keywords_structure(self):
        """get_curated_keywords should return dict with 3 direction keys."""
        kw = get_curated_keywords()
        assert set(kw.keys()) == {"positive", "negative", "neutral"}
        assert len(kw["positive"]) > 0
        assert len(kw["negative"]) > 0
        assert len(kw["neutral"]) > 0

    def test_no_duplicate_keywords(self):
        """All keywords should be unique across all groups and directions."""
        all_kw = get_all_keywords_flat()
        assert len(all_kw) == len(set(all_kw)), "Duplicate keywords found"

    def test_total_keyword_count(self):
        """Total keywords should equal the sum across all groups/directions."""
        kw = get_curated_keywords()
        total = len(kw["positive"]) + len(kw["negative"]) + len(kw["neutral"])
        # Recompute the expected total directly from KEYWORD_GROUPS so the
        # test stays correct as the curated lists are expanded.
        expected = sum(
            len(group.get(direction, []))
            for group in KEYWORD_GROUPS.values()
            for direction in ("positive", "negative", "neutral")
        )
        assert total == expected
        # Sanity floor: at least the original 73 curated keywords.
        assert total >= 73

    def test_specific_keywords_present(self):
        """Verify a few specific keywords from each group are present."""
        kw = get_curated_keywords()
        assert "lợi nhuận tăng" in kw["positive"]
        assert "nợ xấu" in kw["negative"]
        assert "đại hội cổ đông" in kw["neutral"]
        assert "bị phạt" in kw["negative"]
        assert "chia cổ tức" in kw["positive"]


# ---------------------------------------------------------------------------
# Candidate extraction tests (Req 8.1)
# ---------------------------------------------------------------------------


class TestExtractCandidates:
    """Test CountVectorizer-based candidate extraction."""

    def test_returns_dataframe(self, sample_corpus):
        """extract_candidates should return a DataFrame."""
        result = extract_candidates(sample_corpus, top_unigrams=50, top_bigrams=30)
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self, sample_corpus):
        """Output should have term, ngram, count columns."""
        result = extract_candidates(sample_corpus, top_unigrams=50, top_bigrams=30)
        assert "term" in result.columns
        assert "ngram" in result.columns
        assert "count" in result.columns

    def test_contains_unigrams_and_bigrams(self, sample_corpus):
        """Output should contain both unigrams and bigrams."""
        result = extract_candidates(sample_corpus, top_unigrams=50, top_bigrams=30)
        ngram_types = result["ngram"].unique()
        assert "unigram" in ngram_types
        assert "bigram" in ngram_types

    def test_sorted_by_count_descending(self, sample_corpus):
        """Candidates should be sorted by count descending."""
        result = extract_candidates(sample_corpus, top_unigrams=50, top_bigrams=30)
        counts = result["count"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_respects_max_features(self, sample_corpus):
        """Should not exceed the requested number of unigrams/bigrams."""
        result = extract_candidates(sample_corpus, top_unigrams=10, top_bigrams=5)
        uni_count = len(result[result["ngram"] == "unigram"])
        bi_count = len(result[result["ngram"] == "bigram"])
        assert uni_count <= 10
        assert bi_count <= 5

    def test_stopword_removal(self):
        """Stopwords should be excluded from candidates."""
        corpus = ["hello world hello world test test"]
        stopwords = {"hello"}
        result = extract_candidates(corpus, stopwords=stopwords, top_unigrams=10, top_bigrams=5)
        unigrams = result[result["ngram"] == "unigram"]["term"].tolist()
        assert "hello" not in unigrams


# ---------------------------------------------------------------------------
# Save / load tests (Req 8.3, 8.4)
# ---------------------------------------------------------------------------


class TestSaveKeywords:
    """Test keyword list serialization."""

    def test_save_keywords_finance_json(self, tmp_dir):
        """save_keywords_finance should create valid JSON with correct structure."""
        path = os.path.join(tmp_dir, "keywords_finance.json")
        kw = get_curated_keywords()
        save_keywords_finance(kw, path)

        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        assert set(loaded.keys()) == {"positive", "negative", "neutral"}
        assert loaded["positive"] == kw["positive"]
        assert loaded["negative"] == kw["negative"]
        assert loaded["neutral"] == kw["neutral"]

    def test_save_keywords_by_group_json(self, tmp_dir):
        """save_keywords_by_group should create valid JSON with groups A-F."""
        path = os.path.join(tmp_dir, "keywords_by_group.json")
        save_keywords_by_group(KEYWORD_GROUPS, path)

        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        assert set(loaded.keys()) == {"A", "B", "C", "D", "E", "F"}
        for group_id in loaded:
            assert "name" in loaded[group_id]

    def test_json_contains_vietnamese_characters(self, tmp_dir):
        """JSON files should preserve Vietnamese diacritics (ensure_ascii=False)."""
        path = os.path.join(tmp_dir, "keywords_finance.json")
        kw = get_curated_keywords()
        save_keywords_finance(kw, path)

        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        # Vietnamese characters should appear directly, not as \\uXXXX escapes
        assert "lợi nhuận tăng" in content
        assert "\\u" not in content


# ---------------------------------------------------------------------------
# Corpus frequency tests (Req 8.5)
# ---------------------------------------------------------------------------


class TestCorpusFrequency:
    """Test corpus frequency computation."""

    def test_counts_single_word_keyword(self):
        """Should count occurrences of single-word keywords."""
        corpus = ["tăng trưởng mạnh tăng trưởng", "tăng trưởng"]
        freq = compute_corpus_frequency(corpus, ["tăng trưởng"])
        assert freq["tăng trưởng"] == 3

    def test_counts_multi_word_keyword(self):
        """Should count occurrences of multi-word keywords."""
        corpus = ["lợi nhuận tăng mạnh lợi nhuận tăng"]
        freq = compute_corpus_frequency(corpus, ["lợi nhuận tăng"])
        assert freq["lợi nhuận tăng"] == 2

    def test_zero_count_for_absent_keyword(self):
        """Keywords not in corpus should have count 0."""
        corpus = ["some random text"]
        freq = compute_corpus_frequency(corpus, ["lợi nhuận tăng"])
        assert freq["lợi nhuận tăng"] == 0

    def test_case_insensitive(self):
        """Frequency counting should be case-insensitive."""
        corpus = ["Lợi Nhuận Tăng mạnh"]
        freq = compute_corpus_frequency(corpus, ["lợi nhuận tăng"])
        assert freq["lợi nhuận tăng"] == 1

    def test_all_keywords_have_entry(self, sample_corpus):
        """Every curated keyword should appear in the frequency dict."""
        all_kw = get_all_keywords_flat()
        freq = compute_corpus_frequency(sample_corpus, all_kw)
        assert set(freq.keys()) == set(all_kw)


# ---------------------------------------------------------------------------
# Integration test — build_keyword_list
# ---------------------------------------------------------------------------


class TestBuildKeywordList:
    """Test the main build_keyword_list function end-to-end."""

    def test_returns_correct_structure(self, sample_corpus, tmp_dir, monkeypatch):
        """build_keyword_list should return dict with positive/negative/neutral."""
        # Redirect output paths to tmp_dir
        monkeypatch.setattr(
            "pipeline.task8_keywords.CANDIDATES_PATH",
            os.path.join(tmp_dir, "keyword_candidates.csv"),
        )
        monkeypatch.setattr(
            "pipeline.task8_keywords.KEYWORDS_FINANCE_PATH",
            os.path.join(tmp_dir, "keywords_finance.json"),
        )
        monkeypatch.setattr(
            "pipeline.task8_keywords.KEYWORDS_BY_GROUP_PATH",
            os.path.join(tmp_dir, "keywords_by_group.json"),
        )

        result = build_keyword_list(sample_corpus)
        assert set(result.keys()) == {"positive", "negative", "neutral"}
        assert len(result["positive"]) > 0
        assert len(result["negative"]) > 0
        assert len(result["neutral"]) > 0

    def test_creates_output_files(self, sample_corpus, tmp_dir, monkeypatch):
        """build_keyword_list should create all 3 output files."""
        candidates_path = os.path.join(tmp_dir, "keyword_candidates.csv")
        finance_path = os.path.join(tmp_dir, "keywords_finance.json")
        group_path = os.path.join(tmp_dir, "keywords_by_group.json")

        monkeypatch.setattr("pipeline.task8_keywords.CANDIDATES_PATH", candidates_path)
        monkeypatch.setattr("pipeline.task8_keywords.KEYWORDS_FINANCE_PATH", finance_path)
        monkeypatch.setattr("pipeline.task8_keywords.KEYWORDS_BY_GROUP_PATH", group_path)

        build_keyword_list(sample_corpus)

        assert os.path.isfile(candidates_path)
        assert os.path.isfile(finance_path)
        assert os.path.isfile(group_path)

    def test_works_without_corpus(self, tmp_dir, monkeypatch):
        """build_keyword_list should work even without a corpus (saves curated lists)."""
        finance_path = os.path.join(tmp_dir, "keywords_finance.json")
        group_path = os.path.join(tmp_dir, "keywords_by_group.json")

        monkeypatch.setattr("pipeline.task8_keywords.KEYWORDS_FINANCE_PATH", finance_path)
        monkeypatch.setattr("pipeline.task8_keywords.KEYWORDS_BY_GROUP_PATH", group_path)

        result = build_keyword_list(None)
        assert set(result.keys()) == {"positive", "negative", "neutral"}
        assert os.path.isfile(finance_path)
        assert os.path.isfile(group_path)
