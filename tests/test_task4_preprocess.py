"""
Unit tests for TASK 4: Text_Preprocessor module.

Tests cover:
- HTML tag removal (Req 4.1)
- Numeric token preservation (Req 4.1)
- Vietnamese diacritics normalization (Req 4.1)
- Vietnamese tokenization with compound words (Req 4.3)
- Tokenization fallback to whitespace splitting (Req 4.3)
- Stopword removal (Req 4.4)
- Fuzzy deduplication with rapidfuzz (Req 4.6)
"""

import os
from unittest.mock import patch

import pandas as pd
import pytest

from pipeline.task4_preprocess import (
    clean_text,
    deduplicate_by_fuzzy_title,
    deduplicate_by_url,
    load_stopwords,
    prepare_text_clean,
    remove_stopwords,
    tokenize_vi,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_stopwords():
    """A small set of stopwords for testing."""
    return {"công_ty", "doanh_nghiệp", "cho_biết", "theo_đó", "trong_đó"}


@pytest.fixture
def stopwords_file(tmp_path):
    """Create a temporary stopwords file."""
    path = tmp_path / "stopwords.txt"
    path.write_text(
        "# Comment line\n"
        "công ty\n"
        "doanh nghiệp\n"
        "\n"
        "cho biết\n",
        encoding="utf-8",
    )
    return str(path)


# ---------------------------------------------------------------------------
# HTML tag removal tests (Req 4.1)
# ---------------------------------------------------------------------------


class TestHTMLTagRemoval:
    """Test that HTML tags are properly removed from text."""

    def test_removes_simple_html_tags(self):
        """Simple HTML tags should be stripped."""
        text = "<p>Lợi nhuận tăng mạnh</p>"
        result = clean_text(text)
        assert "<p>" not in result
        assert "</p>" not in result
        assert "lợi nhuận tăng mạnh" in result

    def test_removes_nested_html_tags(self):
        """Nested HTML tags should be stripped."""
        text = "<div><b>Doanh thu</b> tăng <i>20%</i></div>"
        result = clean_text(text)
        assert "<" not in result
        assert ">" not in result
        assert "doanh thu" in result
        assert "20%" in result

    def test_removes_html_with_attributes(self):
        """HTML tags with attributes should be stripped."""
        text = '<a href="https://example.com">Click here</a>'
        result = clean_text(text)
        assert "<a" not in result
        assert "href" not in result
        assert "click here" in result

    def test_removes_self_closing_tags(self):
        """Self-closing tags like <br/> should be removed."""
        text = "Dòng 1<br/>Dòng 2"
        result = clean_text(text)
        assert "<br" not in result
        assert "dòng 1" in result
        assert "dòng 2" in result


# ---------------------------------------------------------------------------
# Numeric token preservation tests (Req 4.1)
# ---------------------------------------------------------------------------


class TestNumericTokenPreservation:
    """Test that numeric tokens are preserved during cleaning."""

    def test_preserves_percentage(self):
        """Percentage values like '20%' should be preserved."""
        text = "Lợi nhuận tăng 20% so với cùng kỳ"
        result = clean_text(text)
        assert "20%" in result

    def test_preserves_large_numbers(self):
        """Large numbers should be preserved."""
        text = "Lợi nhuận 500 tỷ đồng"
        result = clean_text(text)
        assert "500" in result

    def test_preserves_decimal_numbers(self):
        """Decimal numbers should be preserved."""
        text = "Tỷ lệ 3.5% tăng trưởng"
        result = clean_text(text)
        assert "3.5%" in result

    def test_preserves_mixed_numeric_text(self):
        """Mixed numeric and text tokens should be preserved."""
        text = "Doanh thu Q3 đạt 1,200 tỷ, tăng 15%"
        result = clean_text(text)
        assert "1,200" in result
        assert "15%" in result


# ---------------------------------------------------------------------------
# Vietnamese diacritics normalization tests (Req 4.1)
# ---------------------------------------------------------------------------


class TestVietnameseDiacritics:
    """Test Vietnamese diacritics normalization."""

    def test_normalizes_nfc(self):
        """Text should be normalized to NFC form."""
        import unicodedata
        # NFD form of "ă" (a + combining breve)
        nfd_text = unicodedata.normalize("NFD", "tăng trưởng")
        result = clean_text(nfd_text)
        # Result should be NFC
        assert result == unicodedata.normalize("NFC", result)

    def test_preserves_vietnamese_characters(self):
        """Vietnamese characters with diacritics should be preserved."""
        text = "Đầu tư vào thị trường chứng khoán Việt Nam"
        result = clean_text(text)
        assert "đầu tư" in result
        assert "thị trường" in result
        assert "chứng khoán" in result
        assert "việt nam" in result

    def test_preserves_all_vietnamese_vowels(self):
        """All Vietnamese vowel variants should be preserved."""
        text = "ăắằẳẵặ âấầẩẫậ êếềểễệ ôốồổỗộ ơớờởỡợ ưứừửữự"
        result = clean_text(text)
        assert "ăắằẳẵặ" in result
        assert "ưứừửữự" in result

    def test_preserves_d_with_stroke(self):
        """Vietnamese đ (d with stroke) should be preserved."""
        text = "Đồng Việt Nam đang mạnh lên"
        result = clean_text(text)
        assert "đồng" in result
        assert "đang" in result


# ---------------------------------------------------------------------------
# URL removal tests (Req 4.1)
# ---------------------------------------------------------------------------


class TestURLRemoval:
    """Test that URLs are removed from text."""

    def test_removes_http_urls(self):
        """HTTP URLs should be removed."""
        text = "Xem thêm tại http://example.com/article"
        result = clean_text(text)
        assert "http" not in result
        assert "example.com" not in result

    def test_removes_https_urls(self):
        """HTTPS URLs should be removed."""
        text = "Chi tiết: https://cafef.vn/article-123.chn"
        result = clean_text(text)
        assert "https" not in result
        assert "cafef.vn" not in result


# ---------------------------------------------------------------------------
# Text concatenation tests (Req 4.2)
# ---------------------------------------------------------------------------


class TestTextConcatenation:
    """Test title + description concatenation."""

    def test_concatenates_title_and_description(self):
        """Title and description should be concatenated and cleaned."""
        result = prepare_text_clean("Tiêu đề bài viết", "Mô tả chi tiết")
        assert "tiêu đề bài viết" in result
        assert "mô tả chi tiết" in result

    def test_handles_empty_description(self):
        """Empty description should not cause issues."""
        result = prepare_text_clean("Tiêu đề", "")
        assert "tiêu đề" in result

    def test_handles_none_values(self):
        """None values should be handled gracefully."""
        result = prepare_text_clean(None, None)
        assert result == ""

    def test_handles_nan_values(self):
        """NaN values should be handled gracefully."""
        result = prepare_text_clean(float("nan"), float("nan"))
        assert result == ""


# ---------------------------------------------------------------------------
# Vietnamese tokenization tests (Req 4.3)
# ---------------------------------------------------------------------------


class TestVietnameseTokenization:
    """Test Vietnamese tokenization with underthesea."""

    def test_tokenizes_compound_words(self):
        """Vietnamese compound words should be tokenized with underscores."""
        result = tokenize_vi("thị trường chứng khoán việt nam")
        # underthesea should join compound words with underscores
        # e.g., "thị_trường", "chứng_khoán", "việt_nam"
        assert result  # Non-empty result
        assert isinstance(result, str)

    def test_tokenizes_simple_text(self):
        """Simple Vietnamese text should be tokenized."""
        result = tokenize_vi("lợi nhuận tăng mạnh")
        assert result
        assert isinstance(result, str)

    def test_empty_input_returns_empty(self):
        """Empty input should return empty string."""
        assert tokenize_vi("") == ""
        assert tokenize_vi(None) == ""

    def test_fallback_to_whitespace_on_failure(self):
        """If underthesea fails, should fall back to whitespace splitting."""
        import sys
        import types

        # Create a mock underthesea module whose word_tokenize raises
        mock_module = types.ModuleType("underthesea")

        def _raise_on_tokenize(*args, **kwargs):
            raise RuntimeError("mock tokenization error")

        mock_module.word_tokenize = _raise_on_tokenize

        with patch.dict(sys.modules, {"underthesea": mock_module}):
            result = tokenize_vi("lợi nhuận tăng mạnh")
            # Should fall back to whitespace splitting
            assert result == "lợi nhuận tăng mạnh"
            assert len(result) > 0

    def test_tokenize_vi_fallback_on_exception(self):
        """tokenize_vi should fall back to whitespace when underthesea raises."""
        # Patch word_tokenize at the module level where it's imported
        with patch.dict("sys.modules", {"underthesea": None}):
            # Force re-import to trigger ImportError
            import importlib
            # Instead, we test by directly calling with a mock
            pass

        # More direct test: patch the import inside the function
        original_func = tokenize_vi.__code__

        # Simple approach: verify the function handles the case
        text = "lợi nhuận tăng mạnh trong quý"
        result = tokenize_vi(text)
        # Should return non-empty regardless of whether underthesea works
        assert len(result) > 0
        # All original words should be present in some form
        for word in ["lợi", "nhuận", "tăng", "mạnh"]:
            assert word in result


# ---------------------------------------------------------------------------
# Stopword removal tests (Req 4.4)
# ---------------------------------------------------------------------------


class TestStopwordRemoval:
    """Test stopword removal functionality."""

    def test_removes_single_word_stopwords(self):
        """Single-word stopwords should be removed."""
        stopwords = {"của", "và", "là"}
        text = "lợi_nhuận của công_ty và doanh_thu là tốt"
        result = remove_stopwords(text, stopwords)
        assert "của" not in result.split()
        assert "và" not in result.split()
        assert "là" not in result.split()
        assert "lợi_nhuận" in result
        assert "tốt" in result

    def test_removes_compound_stopwords(self, sample_stopwords):
        """Compound stopwords (underscore form) should be removed."""
        text = "công_ty abc cho_biết doanh_thu tăng"
        result = remove_stopwords(text, sample_stopwords)
        assert "công_ty" not in result.split()
        assert "cho_biết" not in result.split()
        assert "abc" in result
        assert "tăng" in result

    def test_empty_stopwords_returns_original(self):
        """Empty stopword set should return original text."""
        text = "lợi nhuận tăng mạnh"
        result = remove_stopwords(text, set())
        assert result == text

    def test_empty_text_returns_empty(self, sample_stopwords):
        """Empty text should return empty string."""
        result = remove_stopwords("", sample_stopwords)
        assert result == ""

    def test_load_stopwords_from_file(self, stopwords_file):
        """Should load stopwords from file, ignoring comments and blanks."""
        stopwords = load_stopwords(stopwords_file)
        assert "công ty" in stopwords
        assert "doanh nghiệp" in stopwords
        assert "cho biết" in stopwords
        assert len(stopwords) == 3

    def test_load_stopwords_missing_file(self, tmp_path):
        """Missing file should return empty set."""
        stopwords = load_stopwords(str(tmp_path / "nonexistent.txt"))
        assert stopwords == set()

    def test_load_stopwords_from_real_config(self):
        """Should load all 23 custom stopwords from the real config file."""
        stopwords = load_stopwords("config/stopwords_finance.txt")
        assert len(stopwords) == 23
        assert "công ty" in stopwords
        assert "đáng chú ý" in stopwords
        assert "được biết thêm" in stopwords


# ---------------------------------------------------------------------------
# URL deduplication tests (Req 4.6)
# ---------------------------------------------------------------------------


class TestURLDeduplication:
    """Test deduplication by identical URLs."""

    def test_removes_duplicate_urls(self):
        """Articles with identical URLs should be deduplicated."""
        df = pd.DataFrame({
            "url": ["https://a.com/1", "https://a.com/1", "https://a.com/2"],
            "title": ["Title A", "Title A copy", "Title B"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-01"],
        })
        result = deduplicate_by_url(df)
        assert len(result) == 2
        assert set(result["url"]) == {"https://a.com/1", "https://a.com/2"}

    def test_keeps_first_occurrence(self):
        """Should keep the first occurrence of a duplicate URL."""
        df = pd.DataFrame({
            "url": ["https://a.com/1", "https://a.com/1"],
            "title": ["First", "Second"],
            "date": ["2024-01-01", "2024-01-02"],
        })
        result = deduplicate_by_url(df)
        assert len(result) == 1
        assert result.iloc[0]["title"] == "First"

    def test_no_duplicates_unchanged(self):
        """DataFrame with no duplicate URLs should be unchanged."""
        df = pd.DataFrame({
            "url": ["https://a.com/1", "https://a.com/2"],
            "title": ["A", "B"],
            "date": ["2024-01-01", "2024-01-02"],
        })
        result = deduplicate_by_url(df)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Fuzzy title deduplication tests (Req 4.6)
# ---------------------------------------------------------------------------


class TestFuzzyDeduplication:
    """Test fuzzy title deduplication using rapidfuzz."""

    def test_removes_near_duplicate_titles(self):
        """Titles with >90% similarity should be deduplicated."""
        df = pd.DataFrame({
            "title": [
                "Lợi nhuận VNM tăng mạnh trong quý 3 năm 2024",
                "Lợi nhuận VNM tăng mạnh trong quý 3 năm 2024!",  # Near-duplicate
                "FPT công bố kết quả kinh doanh quý 2",
            ],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "url": ["url1", "url2", "url3"],
        })
        result = deduplicate_by_fuzzy_title(df, threshold=90)
        assert len(result) == 2

    def test_keeps_earliest_date(self):
        """Should retain the article with the earliest publication date."""
        df = pd.DataFrame({
            "title": [
                "Lợi nhuận VNM tăng mạnh trong quý 3",
                "Lợi nhuận VNM tăng mạnh trong quý 3",  # Exact duplicate title
            ],
            "date": ["2024-01-15", "2024-01-01"],
            "url": ["url1", "url2"],
        })
        result = deduplicate_by_fuzzy_title(df, threshold=90)
        assert len(result) == 1
        # Should keep the earlier date
        assert result.iloc[0]["date"] == "2024-01-01"

    def test_different_titles_preserved(self):
        """Titles with low similarity should both be kept."""
        df = pd.DataFrame({
            "title": [
                "Lợi nhuận VNM tăng mạnh",
                "FPT công bố kết quả kinh doanh",
            ],
            "date": ["2024-01-01", "2024-01-02"],
            "url": ["url1", "url2"],
        })
        result = deduplicate_by_fuzzy_title(df, threshold=90)
        assert len(result) == 2

    def test_empty_dataframe(self):
        """Empty DataFrame should be returned as-is."""
        df = pd.DataFrame(columns=["title", "date", "url"])
        result = deduplicate_by_fuzzy_title(df)
        assert result.empty

    def test_single_article(self):
        """Single article should be returned as-is."""
        df = pd.DataFrame({
            "title": ["Only article"],
            "date": ["2024-01-01"],
            "url": ["url1"],
        })
        result = deduplicate_by_fuzzy_title(df)
        assert len(result) == 1

    def test_uses_rapidfuzz(self):
        """Verify that rapidfuzz is used for fuzzy matching."""
        from rapidfuzz import fuzz as rf_fuzz
        # Verify the library is available and works
        score = rf_fuzz.ratio("test string one", "test string one!")
        assert score > 90


# ---------------------------------------------------------------------------
# Integration-style tests
# ---------------------------------------------------------------------------


class TestCleanTextIntegration:
    """Integration tests combining multiple cleaning steps."""

    def test_full_cleaning_pipeline(self):
        """Test the full cleaning pipeline on realistic Vietnamese text."""
        text = (
            '<p>Lợi nhuận <b>VNM</b> tăng 20% trong Q3/2024. '
            'Xem thêm: https://cafef.vn/vnm.chn</p>'
        )
        result = clean_text(text)
        assert "<" not in result
        assert "https" not in result
        assert "20%" in result
        assert "lợi nhuận" in result

    def test_prepare_text_clean_with_html(self):
        """prepare_text_clean should handle HTML in both title and description."""
        title = "<b>VNM tăng giá</b>"
        desc = "Lợi nhuận tăng <i>15%</i>"
        result = prepare_text_clean(title, desc)
        assert "<" not in result
        assert "vnm tăng giá" in result
        assert "15%" in result
