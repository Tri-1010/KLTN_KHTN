"""
Unit tests for TASK 3: Entity_Matcher module.

Tests cover:
- Vinhomes → VHM priority matching (Req 3.1, 3.2)
- Vingroup family disambiguation (Req 3.2)
- UNKNOWN assignment for non-VN30 companies (Req 3.5)
- Multi-ticker article expansion (Req 3.4)
- Alias loading from config/entity_aliases.json (Req 3.1)
- Match confidence tagging (Req 3.6)
"""

import json
import os

import pandas as pd
import pytest

from pipeline.task3_matching import (
    _build_alias_index,
    _match_vingroup,
    load_aliases,
    match_entities,
    match_single_article,
    OUTPUT_COLUMNS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_aliases():
    """Minimal alias dictionary for testing."""
    return {
        "VHM": ["VHM", "Vinhomes", "CTCP Vinhomes"],
        "VRE": ["VRE", "Vincom Retail", "trung tâm thương mại Vincom"],
        "VIC": ["VIC", "Vingroup", "Tập đoàn Vingroup"],
        "VNM": ["VNM", "Vinamilk", "Công ty Cổ phần Sữa Việt Nam"],
        "VCB": ["VCB", "Vietcombank", "Ngân hàng Ngoại thương"],
        "FPT": ["FPT", "Tập đoàn FPT"],
        "HPG": ["HPG", "Hòa Phát", "Tập đoàn Hòa Phát"],
    }


@pytest.fixture
def alias_index(sample_aliases):
    """Pre-built alias index for testing."""
    return _build_alias_index(sample_aliases)


def _make_articles(rows):
    """Helper to create a DataFrame of articles from a list of dicts."""
    defaults = {
        "date": "2024-01-15",
        "title": "",
        "description": "",
        "url": "https://example.com/article",
        "source": "cafef",
    }
    records = []
    for i, row in enumerate(rows):
        rec = {**defaults, **row}
        if rec["url"] == defaults["url"]:
            rec["url"] = f"https://example.com/article-{i}"
        records.append(rec)
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Alias loading tests (Req 3.1)
# ---------------------------------------------------------------------------

class TestLoadAliases:
    """Test alias loading from config/entity_aliases.json."""

    def test_loads_from_default_path(self):
        """Should load aliases from the real config file."""
        aliases = load_aliases()
        assert isinstance(aliases, dict)
        assert len(aliases) == 30  # All 30 VN30 tickers

    def test_all_vn30_tickers_present(self):
        """All 30 VN30 tickers should be keys in the alias dict."""
        expected = [
            "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR",
            "HDB", "HPG", "MBB", "MSN", "MWG", "PLX", "POW", "SAB",
            "SHB", "SSB", "SSI", "STB", "TCB", "TPB", "VCB", "VHM",
            "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
        ]
        aliases = load_aliases()
        for ticker in expected:
            assert ticker in aliases, f"Ticker {ticker} missing from aliases"

    def test_each_ticker_has_aliases(self):
        """Each ticker should have at least 2 aliases."""
        aliases = load_aliases()
        for ticker, names in aliases.items():
            assert len(names) >= 2, f"{ticker} has fewer than 2 aliases"

    def test_vingroup_family_aliases_present(self):
        """Vingroup family should have specific aliases per spec."""
        aliases = load_aliases()
        # VHM must include "Vinhomes"
        assert any("vinhomes" in a.lower() for a in aliases["VHM"])
        # VRE must include "Vincom Retail"
        assert any("vincom retail" in a.lower() for a in aliases["VRE"])
        # VIC must include "Vingroup"
        assert any("vingroup" in a.lower() for a in aliases["VIC"])

    def test_loads_from_custom_path(self, tmp_path):
        """Should load aliases from a custom path."""
        custom = {"TEST": ["Test Corp", "TEST"]}
        path = str(tmp_path / "aliases.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(custom, f)

        aliases = load_aliases(path)
        assert aliases == custom

    def test_raises_on_missing_file(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_aliases("/nonexistent/path.json")


# ---------------------------------------------------------------------------
# Vingroup family disambiguation tests (Req 3.2)
# ---------------------------------------------------------------------------

class TestVingroupDisambiguation:
    """Test Vingroup family priority matching."""

    def test_vinhomes_maps_to_vhm(self):
        """'Vinhomes' should map to VHM, not VIC."""
        matches = _match_vingroup("vinhomes ra mắt dự án mới")
        tickers = [t for t, _ in matches]
        assert "VHM" in tickers
        assert "VIC" not in tickers

    def test_vincom_retail_maps_to_vre(self):
        """'Vincom Retail' should map to VRE."""
        matches = _match_vingroup("vincom retail mở trung tâm mới")
        tickers = [t for t, _ in matches]
        assert "VRE" in tickers
        assert "VIC" not in tickers

    def test_trung_tam_thuong_mai_vincom_maps_to_vre(self):
        """'trung tâm thương mại Vincom' should map to VRE."""
        matches = _match_vingroup("trung tâm thương mại vincom tại hà nội")
        tickers = [t for t, _ in matches]
        assert "VRE" in tickers

    def test_vingroup_maps_to_vic(self):
        """'Vingroup' alone should map to VIC."""
        matches = _match_vingroup("vingroup công bố kết quả kinh doanh")
        tickers = [t for t, _ in matches]
        assert "VIC" in tickers

    def test_tap_doan_vingroup_maps_to_vic(self):
        """'tập đoàn Vingroup' should map to VIC."""
        matches = _match_vingroup("tập đoàn vingroup đầu tư mới")
        tickers = [t for t, _ in matches]
        assert "VIC" in tickers

    def test_vinhomes_and_vingroup_both_match(self):
        """Article mentioning both Vinhomes and Vingroup should match VHM and VIC."""
        matches = _match_vingroup(
            "vinhomes thuộc tập đoàn vingroup ra mắt dự án"
        )
        tickers = [t for t, _ in matches]
        assert "VHM" in tickers
        assert "VIC" in tickers

    def test_all_three_vingroup_entities(self):
        """Article mentioning all three should match VHM, VRE, and VIC."""
        text = "vinhomes và vincom retail thuộc vingroup"
        matches = _match_vingroup(text)
        tickers = [t for t, _ in matches]
        assert set(tickers) == {"VHM", "VRE", "VIC"}

    def test_no_vingroup_mention(self):
        """Text without Vingroup family should return empty."""
        matches = _match_vingroup("vinamilk tăng doanh thu")
        assert matches == []

    def test_vinhomes_confidence_is_exact(self):
        """Vinhomes match should have 'exact' confidence."""
        matches = _match_vingroup("vinhomes dự án mới")
        assert matches[0] == ("VHM", "exact")


# ---------------------------------------------------------------------------
# General matching tests
# ---------------------------------------------------------------------------

class TestMatchSingleArticle:
    """Test single article matching against alias index."""

    def test_exact_ticker_match(self, alias_index):
        """Ticker code in text should produce an exact match."""
        matches = match_single_article("Cổ phiếu FPT tăng mạnh", alias_index)
        tickers = [t for t, _ in matches]
        assert "FPT" in tickers

    def test_company_name_match(self, alias_index):
        """Full company name should produce a partial match."""
        matches = match_single_article(
            "Tập đoàn Hòa Phát công bố lợi nhuận", alias_index
        )
        tickers = [t for t, _ in matches]
        assert "HPG" in tickers

    def test_case_insensitive(self, alias_index):
        """Matching should be case-insensitive."""
        matches = match_single_article("VINAMILK tăng giá", alias_index)
        tickers = [t for t, _ in matches]
        assert "VNM" in tickers

    def test_no_match_returns_empty(self, alias_index):
        """Text with no VN30 mentions should return empty list."""
        matches = match_single_article(
            "Thời tiết hôm nay đẹp", alias_index
        )
        assert matches == []

    def test_vingroup_priority_in_full_match(self, alias_index):
        """Vinhomes in text should match VHM, not VIC, even with general index."""
        matches = match_single_article(
            "Vinhomes ra mắt dự án mới tại Hà Nội", alias_index
        )
        tickers = [t for t, _ in matches]
        assert "VHM" in tickers
        assert "VIC" not in tickers


# ---------------------------------------------------------------------------
# Multi-ticker expansion tests (Req 3.4)
# ---------------------------------------------------------------------------

class TestMultiTickerExpansion:
    """Test that articles matching multiple tickers produce multiple rows."""

    def test_two_tickers_produce_two_rows(self, sample_aliases):
        """Article mentioning two tickers should create two output rows."""
        articles = _make_articles([
            {
                "title": "So sánh FPT và Vinamilk",
                "description": "Hai cổ phiếu công nghệ và tiêu dùng",
            }
        ])
        result = match_entities(articles, sample_aliases)
        assert len(result) == 2
        tickers = set(result["ticker"].tolist())
        assert tickers == {"FPT", "VNM"}

    def test_banking_comparison_multiple_rows(self, sample_aliases):
        """Banking comparison article should match each mentioned bank."""
        articles = _make_articles([
            {
                "title": "Vietcombank và FPT công bố kết quả",
                "description": "Hai doanh nghiệp lớn",
            }
        ])
        result = match_entities(articles, sample_aliases)
        tickers = set(result["ticker"].tolist())
        assert "VCB" in tickers
        assert "FPT" in tickers

    def test_same_url_different_tickers(self, sample_aliases):
        """Each expanded row should share the same URL."""
        articles = _make_articles([
            {
                "title": "FPT và Hòa Phát",
                "description": "",
                "url": "https://example.com/multi",
            }
        ])
        result = match_entities(articles, sample_aliases)
        assert len(result) == 2
        assert all(result["url"] == "https://example.com/multi")


# ---------------------------------------------------------------------------
# UNKNOWN assignment tests (Req 3.5)
# ---------------------------------------------------------------------------

class TestUnknownAssignment:
    """Test UNKNOWN ticker assignment for non-VN30 companies."""

    def test_non_vn30_gets_unknown(self, sample_aliases):
        """Article about a non-VN30 company should get ticker=UNKNOWN."""
        articles = _make_articles([
            {
                "title": "Công ty ABC phát triển mạnh",
                "description": "Không liên quan đến VN30",
            }
        ])
        result = match_entities(articles, sample_aliases)
        assert len(result) == 1
        assert result.iloc[0]["ticker"] == "UNKNOWN"

    def test_unknown_confidence_is_none(self, sample_aliases):
        """UNKNOWN articles should have match_confidence='none'."""
        articles = _make_articles([
            {
                "title": "Tin tức chung về thị trường",
                "description": "Không đề cập mã cụ thể",
            }
        ])
        result = match_entities(articles, sample_aliases)
        assert result.iloc[0]["match_confidence"] == "none"

    def test_empty_title_and_description(self, sample_aliases):
        """Article with empty title and description should be UNKNOWN."""
        articles = _make_articles([
            {"title": "", "description": ""}
        ])
        result = match_entities(articles, sample_aliases)
        assert result.iloc[0]["ticker"] == "UNKNOWN"


# ---------------------------------------------------------------------------
# Output format tests (Req 3.6)
# ---------------------------------------------------------------------------

class TestOutputFormat:
    """Test output DataFrame has correct columns and format."""

    def test_output_columns(self, sample_aliases):
        """Output should have all required columns."""
        articles = _make_articles([
            {"title": "FPT tăng giá", "description": "Cổ phiếu FPT"}
        ])
        result = match_entities(articles, sample_aliases)
        assert list(result.columns) == OUTPUT_COLUMNS

    def test_preserves_article_metadata(self, sample_aliases):
        """Output should preserve date, title, description, url, source."""
        articles = _make_articles([
            {
                "date": "2024-03-15",
                "title": "FPT công bố",
                "description": "Kết quả kinh doanh",
                "url": "https://cafef.vn/fpt.chn",
                "source": "cafef",
            }
        ])
        result = match_entities(articles, sample_aliases)
        row = result.iloc[0]
        assert row["date"] == "2024-03-15"
        assert row["title"] == "FPT công bố"
        assert row["description"] == "Kết quả kinh doanh"
        assert row["url"] == "https://cafef.vn/fpt.chn"
        assert row["source"] == "cafef"

    def test_empty_input_returns_empty_df(self, sample_aliases):
        """Empty input should return empty DataFrame with correct columns."""
        articles = pd.DataFrame(
            columns=["date", "title", "description", "url", "source"]
        )
        result = match_entities(articles, sample_aliases)
        assert result.empty
        assert list(result.columns) == OUTPUT_COLUMNS


# ---------------------------------------------------------------------------
# Match confidence tests (Req 3.6)
# ---------------------------------------------------------------------------

class TestMatchConfidence:
    """Test match_confidence column values."""

    def test_ticker_code_is_exact(self, alias_index):
        """Matching by ticker code should be 'exact'."""
        matches = match_single_article("Cổ phiếu VNM hôm nay", alias_index)
        confidences = {t: c for t, c in matches}
        assert confidences.get("VNM") == "exact"

    def test_company_name_is_partial(self, alias_index):
        """Matching by full company name should be 'partial'."""
        matches = match_single_article(
            "Ngân hàng Ngoại thương tăng lãi suất", alias_index
        )
        confidences = {t: c for t, c in matches}
        assert confidences.get("VCB") == "partial"
