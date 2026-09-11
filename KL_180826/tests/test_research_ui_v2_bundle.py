from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

KLTN_ROOT = Path(__file__).resolve().parents[1]
if str(KLTN_ROOT) not in sys.path:
    sys.path.insert(0, str(KLTN_ROOT))

from research_ui_v2.repository import PublicReleaseRepository, PublicReleaseRepositoryError, open_public_release
from scripts.build_research_ui_v2_bundle import PublicReleaseBuildError, build_bundle

FIXTURE = KLTN_ROOT / "ui_artifacts" / "v2" / "fixtures" / "public_release" / "v6_public_release.json"
TEST_OUTPUT = KLTN_ROOT / "ui_artifacts" / "v2" / "test-output"


def _build() -> Path:
    if TEST_OUTPUT.exists():
        shutil.rmtree(TEST_OUTPUT)
    build_bundle(FIXTURE, TEST_OUTPUT)
    return TEST_OUTPUT


def test_v2_builder_produces_only_aggregate_public_release_and_manifest():
    output = _build()
    names = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    assert names == {"manifest.json", "public_release.json"}
    repository = PublicReleaseRepository(output)
    release = repository.release_artifact()
    assert release["aggregate_only"] is True
    assert release["research_only"] is True
    assert repository.manifest["root_policy"] == "portable-root-contained-json-only"
    assert repository.manifest["member_count"] == 1
    assert {claim["analysis_state"] for claim in repository.claims()} == {"primary", "confirmation"}
    h2 = repository.claims("confirmation")[0]
    assert h2["status"] == "unsupported"
    assert h2["result"]["estimate"] == -0.0042486


def test_v2_repository_rejects_tampered_runtime_member():
    output = _build()
    release_path = output / "public_release.json"
    release_path.write_text(release_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(PublicReleaseRepositoryError, match="integrity mismatch"):
        PublicReleaseRepository(output)


def test_v2_repository_rejects_manifest_path_traversal_absolute_unc_and_non_json():
    output = _build()
    manifest_path = output / "manifest.json"
    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    for unsafe_path in ("../public_release.json", "C:/public_release.json", "//server/share/a.json", "public_release.csv"):
        manifest = json.loads(json.dumps(original))
        manifest["release_member_path"] = unsafe_path
        manifest["runtime_members"][0]["path"] = unsafe_path
        manifest["artifacts"][0]["path"] = unsafe_path
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(PublicReleaseRepositoryError, match="manifest violates"):
            PublicReleaseRepository(output)


def test_v2_repository_rejects_manifest_hash_count_and_schema_mismatch():
    output = _build()
    manifest_path = output / "manifest.json"
    original = json.loads(manifest_path.read_text(encoding="utf-8"))
    for field, value in (("sha256", "0" * 64), ("record_count", 999), ("schema_version", "wrong-v1")):
        manifest = json.loads(json.dumps(original))
        manifest["runtime_members"][0][field] = value
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        expected = "integrity mismatch|manifest violates" if field == "sha256" else "manifest violates"
        with pytest.raises(PublicReleaseRepositoryError, match=expected):
            PublicReleaseRepository(output)


def test_v2_build_failure_preserves_previously_published_output(tmp_path: Path):
    output = KLTN_ROOT / "ui_artifacts" / "v2" / "atomic-preserve-test"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    sentinel = output / "published-sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    invalid_source = tmp_path / "invalid-public-release.json"
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["claims"][0]["raw_predictions"] = []
    invalid_source.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(PublicReleaseBuildError):
        build_bundle(invalid_source, output)
    assert sentinel.read_text(encoding="utf-8") == "preserve"
    assert not (output / "manifest.json").exists()


def test_v2_builder_rejects_root_current_and_outside_v2_paths(tmp_path: Path):
    with pytest.raises(PublicReleaseBuildError, match="named child"):
        build_bundle(FIXTURE, KLTN_ROOT / "ui_artifacts" / "v2")
    with pytest.raises(PublicReleaseBuildError, match="current"):
        build_bundle(FIXTURE, KLTN_ROOT / "ui_artifacts" / "v2" / "current")
    with pytest.raises(PublicReleaseBuildError, match="V2 output"):
        build_bundle(FIXTURE, tmp_path / "outside-v2")


def test_open_public_release_rejects_root_current_and_outside_paths(tmp_path: Path):
    with pytest.raises(PublicReleaseRepositoryError, match="non-legacy child"):
        open_public_release(KLTN_ROOT / "ui_artifacts" / "v2")
    with pytest.raises(PublicReleaseRepositoryError, match="non-legacy child"):
        open_public_release(KLTN_ROOT / "ui_artifacts" / "v2" / "current")
    with pytest.raises(PublicReleaseRepositoryError, match="remain below"):
        open_public_release(tmp_path / "outside")


def test_open_public_release_cache_invalidates_after_atomic_manifest_replacement():
    output = _build()
    open_public_release.cache_clear()
    first = open_public_release(output)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["built_at_utc"] = "2026-09-05T12:00:00Z"
    replacement = output / ".replacement.json"
    replacement.write_text(json.dumps(manifest), encoding="utf-8")
    replacement.replace(manifest_path)
    second = open_public_release(output)
    assert second is not first
    assert second.manifest["built_at_utc"] == "2026-09-05T12:00:00Z"


def test_open_public_release_cache_invalidates_when_only_runtime_member_changes():
    output = _build()
    open_public_release.cache_clear()
    first = open_public_release(output)
    release_path = output / "public_release.json"
    release_path.write_text(release_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(PublicReleaseRepositoryError, match="integrity mismatch"):
        open_public_release(output)
    assert first.release_artifact()["release_id"] == "v6-locked-study-results-fixture"


def test_default_v2_output_rejects_altered_locked_h2(tmp_path: Path):
    source = tmp_path / "altered-public-release.json"
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for claim in payload["claims"]:
        if claim["claim_id"] == "H2-semantic-comparison":
            claim["status"] = "supported"
            claim["locked"] = False
            claim["result"]["estimate"] = 0.01
    source.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(PublicReleaseBuildError, match="approved locked"):
        build_bundle(source, KLTN_ROOT / "ui_artifacts" / "v2" / "default")
