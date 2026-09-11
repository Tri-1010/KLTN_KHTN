"""Unit tests for TASK 3: Baseline_Snapshotter.

Tests cover ``experiments.common.snapshot.create_baseline_snapshot`` — the module
that freezes the six legacy result files into ``reports/baseline_v0/`` so every
experiment has an immutable comparison baseline (Baseline_v0).

Coverage (Req 1.2, 1.3, 1.4):
- Full copy: all six SNAPSHOT_FILES are copied and the manifest lists them.
- Missing source file: a missing file is warned about and skipped, remaining
  files are still copied, and the run does not raise (Req 1.2).
- No overwrite: when a baseline already exists and ``force=False``, existing
  content is preserved and nothing is rewritten (Req 1.3).
- Manifest: ``.snapshot_meta.json`` records the creation date plus the copied and
  missing file lists (Req 1.4).

Every test uses pytest's ``tmp_path`` so the real ``reports/`` directory is never
touched.
"""

import json

import pytest

from experiments.common.snapshot import (
    MANIFEST_NAME,
    SNAPSHOT_FILES,
    SnapshotResult,
    create_baseline_snapshot,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _write_reports(reports_dir, names, *, prefix="content"):
    """Create ``names`` under ``reports_dir`` with identifiable content.

    Returns a dict mapping each file name to the text written, so tests can
    assert on content preservation after copy.
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    contents = {}
    for name in names:
        text = f"{prefix}:{name}"
        (reports_dir / name).write_text(text, encoding="utf-8")
        contents[name] = text
    return contents


@pytest.fixture
def reports_dir(tmp_path):
    """A temporary ``reports/`` source directory."""
    return tmp_path / "reports"


@pytest.fixture
def baseline_dir(tmp_path):
    """A temporary ``reports/baseline_v0/`` destination directory."""
    return tmp_path / "reports" / "baseline_v0"


# ---------------------------------------------------------------------------
# Full copy (Req 1.1, 1.4)
# ---------------------------------------------------------------------------


class TestFullCopy:
    """All six snapshot files present → all copied, manifest complete."""

    def test_copies_all_snapshot_files(self, reports_dir, baseline_dir):
        contents = _write_reports(reports_dir, SNAPSHOT_FILES)

        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert isinstance(result, SnapshotResult)
        assert sorted(result.copied) == sorted(SNAPSHOT_FILES)
        assert result.missing == []
        assert result.already_existed is False
        for name, text in contents.items():
            copied = baseline_dir / name
            assert copied.exists()
            assert copied.read_text(encoding="utf-8") == text

    def test_creates_baseline_dir_when_absent(self, reports_dir, baseline_dir):
        _write_reports(reports_dir, SNAPSHOT_FILES)
        assert not baseline_dir.exists()

        create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert baseline_dir.is_dir()

    def test_created_at_is_populated(self, reports_dir, baseline_dir):
        _write_reports(reports_dir, SNAPSHOT_FILES)

        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert result.created_at  # non-empty ISO timestamp


# ---------------------------------------------------------------------------
# Missing source file (Req 1.2)
# ---------------------------------------------------------------------------


class TestMissingSourceFile:
    """A missing source file is skipped with a warning; run continues."""

    def test_missing_file_is_skipped_and_others_copied(
        self, reports_dir, baseline_dir
    ):
        present = SNAPSHOT_FILES[1:]  # omit the first file
        missing_name = SNAPSHOT_FILES[0]
        _write_reports(reports_dir, present)

        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert missing_name in result.missing
        assert sorted(result.copied) == sorted(present)
        # Present files were copied; missing file was not created.
        for name in present:
            assert (baseline_dir / name).exists()
        assert not (baseline_dir / missing_name).exists()

    def test_does_not_raise_when_source_missing(self, reports_dir, baseline_dir):
        # Only a subset present; must not raise.
        _write_reports(reports_dir, SNAPSHOT_FILES[:2])

        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert sorted(result.missing) == sorted(SNAPSHOT_FILES[2:])

    def test_logs_warning_naming_missing_file(
        self, reports_dir, baseline_dir, caplog
    ):
        missing_name = SNAPSHOT_FILES[0]
        _write_reports(reports_dir, SNAPSHOT_FILES[1:])

        with caplog.at_level("WARNING"):
            create_baseline_snapshot(
                reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
            )

        assert any(
            missing_name in rec.getMessage() for rec in caplog.records
        )

    def test_all_sources_missing_copies_nothing(self, reports_dir, baseline_dir):
        reports_dir.mkdir(parents=True, exist_ok=True)  # empty reports dir

        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert result.copied == []
        assert sorted(result.missing) == sorted(SNAPSHOT_FILES)
        # Manifest is still written even when nothing was copied.
        assert (baseline_dir / MANIFEST_NAME).exists()


# ---------------------------------------------------------------------------
# No overwrite when baseline exists (Req 1.3)
# ---------------------------------------------------------------------------


class TestNoOverwrite:
    """Existing baseline is preserved when force=False."""

    def test_existing_baseline_is_not_overwritten(self, reports_dir, baseline_dir):
        # First snapshot with original content.
        _write_reports(reports_dir, SNAPSHOT_FILES, prefix="original")
        create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        # Source content changes, then a second snapshot without force.
        _write_reports(reports_dir, SNAPSHOT_FILES, prefix="changed")
        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert result.already_existed is True
        assert result.copied == []
        # Baseline still holds the ORIGINAL content, not the changed one.
        for name in SNAPSHOT_FILES:
            assert (baseline_dir / name).read_text(encoding="utf-8") == f"original:{name}"

    def test_existing_manifest_marks_already_existed(self, reports_dir, baseline_dir):
        # A baseline dir containing only the manifest counts as snapshotted.
        baseline_dir.mkdir(parents=True, exist_ok=True)
        (baseline_dir / MANIFEST_NAME).write_text("{}", encoding="utf-8")
        _write_reports(reports_dir, SNAPSHOT_FILES)

        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        assert result.already_existed is True
        assert result.copied == []

    def test_force_true_overwrites_existing_baseline(self, reports_dir, baseline_dir):
        _write_reports(reports_dir, SNAPSHOT_FILES, prefix="original")
        create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        _write_reports(reports_dir, SNAPSHOT_FILES, prefix="changed")
        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir), force=True
        )

        assert result.already_existed is False
        assert sorted(result.copied) == sorted(SNAPSHOT_FILES)
        for name in SNAPSHOT_FILES:
            assert (baseline_dir / name).read_text(encoding="utf-8") == f"changed:{name}"


# ---------------------------------------------------------------------------
# Manifest (Req 1.4)
# ---------------------------------------------------------------------------


class TestManifest:
    """The manifest records creation date and copied/missing file lists."""

    def test_manifest_written_with_expected_fields(self, reports_dir, baseline_dir):
        _write_reports(reports_dir, SNAPSHOT_FILES)

        result = create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        manifest_path = baseline_dir / MANIFEST_NAME
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert set(manifest.keys()) == {"created_at", "copied", "missing"}
        assert sorted(manifest["copied"]) == sorted(SNAPSHOT_FILES)
        assert manifest["missing"] == []
        assert manifest["created_at"] == result.created_at

    def test_manifest_records_missing_files(self, reports_dir, baseline_dir):
        present = SNAPSHOT_FILES[2:]
        missing = SNAPSHOT_FILES[:2]
        _write_reports(reports_dir, present)

        create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        manifest = json.loads(
            (baseline_dir / MANIFEST_NAME).read_text(encoding="utf-8")
        )
        assert sorted(manifest["copied"]) == sorted(present)
        assert sorted(manifest["missing"]) == sorted(missing)

    def test_manifest_created_at_is_iso_parseable(self, reports_dir, baseline_dir):
        from datetime import datetime

        _write_reports(reports_dir, SNAPSHOT_FILES)
        create_baseline_snapshot(
            reports_dir=str(reports_dir), baseline_dir=str(baseline_dir)
        )

        manifest = json.loads(
            (baseline_dir / MANIFEST_NAME).read_text(encoding="utf-8")
        )
        # Should not raise — confirms an ISO-8601 timestamp was written.
        datetime.fromisoformat(manifest["created_at"])
