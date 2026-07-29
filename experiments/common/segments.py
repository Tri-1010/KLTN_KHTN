"""Segment_Mapper — B3: phân khúc ticker theo Ngành & Vốn hóa (Req 10.1, 10.2).

Thí nghiệm B3 kiểm tra liệu tín hiệu văn bản có giá trị dự báo *khác nhau* giữa
các phân khúc thị trường không (từng ngành, và large-cap vs mid-cap). Muốn vậy,
mỗi ticker trong vũ trụ cấu hình phải được gán **đúng một ngành (sector)** và
**đúng một nhóm vốn hóa (cap_group)**.

Hai ánh xạ này được khai báo **tường minh** ở cấp module (Req 10.1):

- :data:`SECTOR_MAP` — ticker → sector, phủ toàn bộ 80 ticker của HOSE-80. Bộ
  ngành khớp đúng enum của thiết kế: ``Banking``, ``Securities``, ``RealEstate``,
  ``Industrial``, ``Energy``, ``Consumer``, ``Technology``, ``Transport`` (tên
  ngành viết liền, không dấu cách, để đồng bộ enum).
- :data:`LARGE_CAP_TICKERS` — tập 30 mã VN30 gốc (``large_cap``). Mọi ticker
  còn lại của HOSE-80 thuộc phần mở rộng 50 mã (``mid_cap``) (Req 10.2).

Nguồn danh sách ticker là ``config/pipeline_config.yaml`` (đọc lúc runtime), nên
:func:`assign_segments` luôn phủ **đúng** vũ trụ đang cấu hình. Nếu một ticker
cấu hình thiếu trong :data:`SECTOR_MAP`, hàm ném :class:`ValueError` để bảo đảm
ánh xạ luôn total/coverage-complete (nền tảng cho Property 11 ở task 15.2).

_Requirements: 10.1, 10.2_
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List

import yaml

logger = logging.getLogger(__name__)

__all__ = [
    "SegmentInfo",
    "SECTOR_MAP",
    "LARGE_CAP_TICKERS",
    "CONFIG_PATH",
    "load_configured_tickers",
    "assign_segments",
]

#: Đường dẫn cấu hình pipeline mặc định (nguồn vũ trụ ticker).
CONFIG_PATH = "config/pipeline_config.yaml"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SegmentInfo:
    """Thông tin phân khúc của một ticker (Req 10.1, 10.2).

    Attributes:
        ticker: Mã cổ phiếu (ví dụ ``"VCB"``).
        sector: Ngành — một trong ``{Banking, Securities, RealEstate,
            Industrial, Energy, Consumer, Technology, Transport}`` (viết liền,
            không dấu cách; đồng bộ enum thiết kế).
        cap_group: Nhóm vốn hóa — ``"large_cap"`` (30 mã VN30 gốc) hoặc
            ``"mid_cap"`` (50 mã HOSE-80 mở rộng).
    """

    ticker: str
    sector: str
    cap_group: str


# ---------------------------------------------------------------------------
# Ánh xạ tường minh (Req 10.1) — nguồn chân lý cho sector và cap_group
# ---------------------------------------------------------------------------

#: Tập 30 mã VN30 gốc → ``large_cap``; mọi mã HOSE-80 khác → ``mid_cap`` (Req 10.2).
LARGE_CAP_TICKERS: frozenset[str] = frozenset(
    {
        "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
        "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
        "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
    }
)

#: Ánh xạ tường minh ticker → sector, phủ toàn bộ 80 mã HOSE-80 (Req 10.1).
#: Tên ngành viết liền, không dấu cách, khớp enum thiết kế.
SECTOR_MAP: Dict[str, str] = {
    # === VN30 (large_cap) ===
    # Banking & Finance (kể cả BVH — bảo hiểm/tài chính, gộp nhóm Banking)
    "ACB": "Banking",
    "BID": "Banking",
    "BVH": "Banking",
    "CTG": "Banking",
    "HDB": "Banking",
    "MBB": "Banking",
    "SHB": "Banking",
    "SSB": "Banking",
    "STB": "Banking",
    "TCB": "Banking",
    "TPB": "Banking",
    "VCB": "Banking",
    "VIB": "Banking",
    "VPB": "Banking",
    # Securities
    "SSI": "Securities",
    # Real Estate
    "BCM": "RealEstate",
    "VHM": "RealEstate",
    "VIC": "RealEstate",
    "VRE": "RealEstate",
    # Industrial / Manufacturing
    "GVR": "Industrial",
    "HPG": "Industrial",
    # Energy & Utilities
    "GAS": "Energy",
    "PLX": "Energy",
    "POW": "Energy",
    # Consumer / Retail
    "MSN": "Consumer",
    "MWG": "Consumer",
    "SAB": "Consumer",
    "VNM": "Consumer",
    # Technology / Telecom
    "FPT": "Technology",
    # Transport / Logistics
    "VJC": "Transport",
    # === HOSE-80 expansion (mid_cap) ===
    # Banking & Finance (11)
    "EIB": "Banking",
    "LPB": "Banking",
    "MSB": "Banking",
    "NAB": "Banking",
    "OCB": "Banking",
    "PGB": "Banking",
    "VBB": "Banking",
    "BVB": "Banking",
    "ABB": "Banking",
    "KLB": "Banking",
    "BAB": "Banking",
    # Securities (5)
    "VCI": "Securities",
    "HCM": "Securities",
    "VND": "Securities",
    "MBS": "Securities",
    "BSI": "Securities",
    # Real Estate (9)
    "KDH": "RealEstate",
    "NVL": "RealEstate",
    "DXG": "RealEstate",
    "PDR": "RealEstate",
    "NLG": "RealEstate",
    "DIG": "RealEstate",
    "HDG": "RealEstate",
    "VCG": "RealEstate",
    "SCR": "RealEstate",
    # Industrial / Manufacturing (8)
    "HSG": "Industrial",
    "NKG": "Industrial",
    "VGC": "Industrial",
    "PHR": "Industrial",
    "CSV": "Industrial",
    "DPM": "Industrial",
    "DCM": "Industrial",
    "BMP": "Industrial",
    # Energy & Utilities (5)
    "REE": "Energy",
    "NT2": "Energy",
    "PPC": "Energy",
    "GEX": "Energy",
    "EVF": "Energy",
    # Consumer / Retail (6)
    "PNJ": "Consumer",
    "DGW": "Consumer",
    "FRT": "Consumer",
    "MCH": "Consumer",
    "VHC": "Consumer",
    "ANV": "Consumer",
    # Technology / Telecom (2)
    "CMG": "Technology",
    "ELC": "Technology",
    # Transport / Logistics (4)
    "GMD": "Transport",
    "VSC": "Transport",
    "PVT": "Transport",
    "HAH": "Transport",
}


# ---------------------------------------------------------------------------
# Nạp vũ trụ ticker từ cấu hình
# ---------------------------------------------------------------------------


def load_configured_tickers(config_path: str = CONFIG_PATH) -> List[str]:
    """Đọc danh sách ticker cấu hình từ ``pipeline_config.yaml``.

    Tuân theo quy ước nạp cấu hình của pipeline (``yaml.safe_load``) như trong
    ``pipeline/task1_prices.py`` và ``pipeline/run_pipeline.py``.

    Args:
        config_path: Đường dẫn tệp cấu hình pipeline.

    Returns:
        Danh sách mã ticker theo đúng thứ tự khai báo trong cấu hình.

    Raises:
        ValueError: Nếu cấu hình thiếu khóa ``tickers`` hoặc danh sách rỗng.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tickers = (config or {}).get("tickers")
    if not tickers:
        raise ValueError(
            f"Cấu hình {config_path!r} thiếu khóa 'tickers' hoặc danh sách rỗng."
        )
    return list(tickers)


# ---------------------------------------------------------------------------
# Gán phân khúc (Req 10.1, 10.2)
# ---------------------------------------------------------------------------


def assign_segments(config_path: str = CONFIG_PATH) -> Dict[str, SegmentInfo]:
    """Gán mỗi ticker cấu hình đúng một sector và một cap_group (Req 10.1, 10.2).

    Với từng ticker trong vũ trụ cấu hình:

    - ``cap_group`` = ``"large_cap"`` nếu ticker thuộc :data:`LARGE_CAP_TICKERS`
      (30 mã VN30 gốc), ngược lại ``"mid_cap"`` (Req 10.2).
    - ``sector`` = tra cứu từ :data:`SECTOR_MAP` (ánh xạ tường minh) (Req 10.1).

    Ánh xạ được thiết kế để **total**: mọi ticker cấu hình phải có mặt trong
    :data:`SECTOR_MAP`. Nếu thiếu, hàm ném :class:`ValueError` thay vì gán mặc
    định, để bảo đảm coverage đầy đủ (nền tảng cho Property 11).

    Args:
        config_path: Đường dẫn ``pipeline_config.yaml`` chứa danh sách ticker.

    Returns:
        Dict ``ticker -> SegmentInfo`` phủ đúng vũ trụ cấu hình.

    Raises:
        ValueError: Nếu có ticker cấu hình không nằm trong :data:`SECTOR_MAP`.
    """
    tickers = load_configured_tickers(config_path)

    missing = [t for t in tickers if t not in SECTOR_MAP]
    if missing:
        raise ValueError(
            "Các ticker cấu hình thiếu ánh xạ sector trong SECTOR_MAP: "
            f"{sorted(missing)}. Cập nhật SECTOR_MAP để phủ toàn bộ vũ trụ."
        )

    segments: Dict[str, SegmentInfo] = {}
    for ticker in tickers:
        cap_group = "large_cap" if ticker in LARGE_CAP_TICKERS else "mid_cap"
        segments[ticker] = SegmentInfo(
            ticker=ticker,
            sector=SECTOR_MAP[ticker],
            cap_group=cap_group,
        )

    logger.info(
        "Đã gán phân khúc cho %d ticker (%d large_cap, %d mid_cap).",
        len(segments),
        sum(1 for s in segments.values() if s.cap_group == "large_cap"),
        sum(1 for s in segments.values() if s.cap_group == "mid_cap"),
    )
    return segments


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    _segs = assign_segments()
    for _t, _info in _segs.items():
        print(_t, _info.sector, _info.cap_group)
