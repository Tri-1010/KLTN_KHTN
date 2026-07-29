"""Baseline_Snapshotter — đóng băng kết quả cũ (v0) vào ``reports/baseline_v0/``.

Module này tạo một bản sao bất biến (immutable snapshot) của toàn bộ kết quả cũ
trong luận văn, dùng làm mốc so sánh cố định cho mọi thí nghiệm mở rộng đặc trưng
văn bản (Baseline_v0). Sau khi đóng băng, các tệp trong ``reports/baseline_v0/``
được coi là bất biến và không bị ghi đè bởi các lần chạy thí nghiệm sau.

Đáp ứng Requirement 1:
- Req 1.1: Copy 6 tệp kết quả cũ từ ``reports/`` sang ``reports/baseline_v0/``.
- Req 1.2: Tệp nguồn thiếu → ghi cảnh báo nêu tên tệp và tiếp tục (không ném exception).
- Req 1.3: Baseline đã tồn tại và ``force=False`` → giữ nguyên, log "đã tồn tại".
- Req 1.4: Ghi manifest ``.snapshot_meta.json`` gồm ngày tạo + danh sách tệp đã copy.
- Req 1.5: Sau khi đóng băng hoàn tất, baseline được coi là bất biến.

Các hàm được viết ở dạng thuần (pure-ish) và nhận ``reports_dir``/``baseline_dir``
làm tham số để có thể kiểm thử bằng thư mục tạm.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

__all__ = [
    "BASELINE_DIR",
    "SNAPSHOT_FILES",
    "MANIFEST_NAME",
    "SnapshotResult",
    "create_baseline_snapshot",
]

logger = logging.getLogger(__name__)

BASELINE_DIR = "reports/baseline_v0"

# Sáu tệp kết quả cũ cần đóng băng làm Baseline_v0 (Req 1.1).
SNAPSHOT_FILES = [
    "model_comparison.csv",
    "keyword_significance.csv",
    "period_experiment.csv",
    "metrics_breakdown.csv",
    "news_density_analysis.csv",
    "shap_configc_keyword_ranking.csv",
]

# Tên tệp manifest ghi metadata của snapshot (Req 1.4).
MANIFEST_NAME = ".snapshot_meta.json"


@dataclass
class SnapshotResult:
    """Kết quả của một lần chạy :func:`create_baseline_snapshot`.

    Attributes:
        copied: Danh sách tên tệp đã được sao chép thành công vào baseline.
        missing: Danh sách tên tệp nguồn không tồn tại trong ``reports/`` (Req 1.2).
        already_existed: ``True`` nếu baseline đã tồn tại và giữ nguyên (Req 1.3).
        created_at: Dấu thời gian ISO của lần tạo/kiểm tra snapshot.
    """

    copied: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    already_existed: bool = False
    created_at: str = ""


def _baseline_already_snapshotted(baseline_path: Path) -> bool:
    """Xác định baseline đã được đóng băng hay chưa (Req 1.3).

    Coi là đã đóng băng nếu thư mục tồn tại và chứa manifest hoặc ít nhất một
    trong các tệp thuộc :data:`SNAPSHOT_FILES`.
    """
    if not baseline_path.is_dir():
        return False
    if (baseline_path / MANIFEST_NAME).exists():
        return True
    return any((baseline_path / name).exists() for name in SNAPSHOT_FILES)


def create_baseline_snapshot(
    reports_dir: str = "reports",
    baseline_dir: str = BASELINE_DIR,
    force: bool = False,
) -> SnapshotResult:
    """Đóng băng 6 tệp kết quả cũ từ ``reports/`` vào ``reports/baseline_v0/``.

    Với mỗi tên trong :data:`SNAPSHOT_FILES`, sao chép tệp tương ứng từ
    ``reports_dir`` sang ``baseline_dir`` (giữ metadata bằng ``shutil.copy2``).

    - Nếu ``baseline_dir`` đã có snapshot và ``force=False`` → giữ nguyên nội dung,
      log "đã tồn tại" và trả về ``SnapshotResult(already_existed=True)`` (Req 1.3).
    - Tệp nguồn thiếu → ghi cảnh báo nêu tên tệp và tiếp tục với các tệp còn lại,
      không ném exception (Req 1.2).
    - Sau khi copy, ghi manifest ``.snapshot_meta.json`` gồm ngày tạo và danh sách
      tệp đã copy (kèm danh sách tệp thiếu để truy vết) (Req 1.4).

    Args:
        reports_dir: Thư mục nguồn chứa các tệp kết quả cũ.
        baseline_dir: Thư mục đích lưu snapshot bất biến.
        force: Nếu ``True``, ghi đè snapshot dù đã tồn tại.

    Returns:
        :class:`SnapshotResult` mô tả kết quả đóng băng.

    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5
    """
    reports_path = Path(reports_dir)
    baseline_path = Path(baseline_dir)
    created_at = datetime.now().isoformat()

    # Req 1.3: baseline đã tồn tại và không ép ghi đè → giữ nguyên.
    if not force and _baseline_already_snapshotted(baseline_path):
        logger.info(
            "Baseline snapshot đã tồn tại tại '%s' — giữ nguyên nội dung, không ghi đè.",
            baseline_path,
        )
        return SnapshotResult(already_existed=True, created_at=created_at)

    # Tạo thư mục đích nếu chưa có.
    baseline_path.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    missing: list[str] = []

    # Req 1.1 + 1.2: copy từng tệp, bỏ qua (cảnh báo) tệp thiếu.
    for name in SNAPSHOT_FILES:
        src = reports_path / name
        if not src.exists():
            logger.warning(
                "Tệp nguồn baseline bị thiếu, bỏ qua: '%s'. Tiếp tục với các tệp còn lại.",
                src,
            )
            missing.append(name)
            continue
        shutil.copy2(src, baseline_path / name)
        copied.append(name)

    logger.info(
        "Đã đóng băng %d/%d tệp baseline vào '%s' (thiếu %d).",
        len(copied),
        len(SNAPSHOT_FILES),
        baseline_path,
        len(missing),
    )

    # Req 1.4: ghi manifest metadata.
    manifest = {
        "created_at": created_at,
        "copied": copied,
        "missing": missing,
    }
    manifest_path = baseline_path / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return SnapshotResult(
        copied=copied,
        missing=missing,
        already_existed=False,
        created_at=created_at,
    )
