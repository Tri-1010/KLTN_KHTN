"""Build a portable, aggregate-only V6 study-results Dashboard V2 bundle.

This script deliberately has no dependency on legacy dashboard code, raw datasets,
predictions, news, providers, credentials, prompts, or V6 processing pipelines.
It validates a strict aggregate release into a sibling staging directory and publishes
only below ``KL_180826/ui_artifacts/v2`` by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_ui_v2.contracts import (  # noqa: E402
    PUBLIC_RELEASE_SCHEMA_VERSION,
    RUNTIME_BUNDLE_SCHEMA_VERSION,
    PublicReleaseArtifactReference,
    PublicReleaseContractError,
    PublicV6ReleaseArtifact,
    RuntimeBundle,
    RuntimeMember,
    assert_public_release_payload_safe,
    normalize_portable_json_path,
)


DEFAULT_OUTPUT = ROOT / "ui_artifacts" / "v2" / "default"
DEFAULT_FIXTURE = ROOT / "ui_artifacts" / "v2" / "fixtures" / "public_release" / "v6_public_release.json"
APPROVED_OUTPUT_PARENT = (ROOT / "ui_artifacts" / "v2").resolve()
APPROVED_DEFAULT_RELEASE_ID = "v6-locked-study-results-fixture"
APPROVED_DEFAULT_SOURCE_SHA256 = "950a6c6e949f4cd3ab5c8d4cd2613442985a09ec78de730959698cc0ee0aed6e"


class PublicReleaseBuildError(ValueError):
    """Raised when a V2 bundle cannot be safely built or atomically published."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _assert_approved_output_path(output_dir: Path) -> Path:
    """Reject publishing outside V2 and reject the legacy ``ui_artifacts/current`` target."""

    output = output_dir.resolve()
    try:
        output.relative_to(APPROVED_OUTPUT_PARENT)
    except ValueError as exc:
        raise PublicReleaseBuildError("V2 output must be root-contained below KL_180826/ui_artifacts/v2") from exc
    if output == APPROVED_OUTPUT_PARENT:
        raise PublicReleaseBuildError("V2 output must be a named child below ui_artifacts/v2, not the V2 root")
    if output == APPROVED_OUTPUT_PARENT / "current" or "current" in output.parts:
        raise PublicReleaseBuildError("V2 build must never write legacy ui_artifacts/current")
    return output


def load_public_release(source_path: Path) -> PublicV6ReleaseArtifact:
    """Load one strict aggregate public release artifact without inspecting any raw data."""

    try:
        normalize_portable_json_path("public_release.json")
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicReleaseBuildError("Cannot read a valid aggregate public release JSON artifact") from exc
    try:
        return assert_public_release_payload_safe(payload)
    except PublicReleaseContractError as exc:
        raise PublicReleaseBuildError("Aggregate public release fails strict contract/safety validation") from exc


def _build_bundle_contents(source_path: Path, staging: Path) -> dict[str, Any]:
    release = load_public_release(source_path)
    member_path = "public_release.json"
    release_path = staging / member_path
    _write_json(release_path, release.model_dump(mode="json"))
    digest = sha256_file(release_path)
    member = RuntimeMember(
        artifact_id="v6-study-results-public-release",
        path=member_path,
        sha256=digest,
        record_count=release.record_count,
        schema_version=PUBLIC_RELEASE_SCHEMA_VERSION,
    )
    artifact = PublicReleaseArtifactReference(
        artifact_id="v6-study-results-public-release",
        path=member_path,
        sha256=digest,
        record_count=release.record_count,
        schema_version=PUBLIC_RELEASE_SCHEMA_VERSION,
        scope="aggregate_public",
    )
    manifest = RuntimeBundle(
        schema_version=RUNTIME_BUNDLE_SCHEMA_VERSION,
        bundle_id=f"{release.release_id}-runtime",
        release_id=release.release_id,
        built_at_utc=datetime.now(timezone.utc),
        root_policy="portable-root-contained-json-only",
        member_count=1,
        release_member_path=member_path,
        artifacts=[artifact],
        runtime_members=[member],
    )
    _write_json(staging / "manifest.json", manifest.model_dump(mode="json"))
    return {
        "bundle_id": manifest.bundle_id,
        "release_id": release.release_id,
        "member_count": manifest.member_count,
        "record_count": release.record_count,
        "output_scope": "KL_180826/ui_artifacts/v2 only",
    }


def build_bundle(source_path: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    """Stage and atomically publish a V2-only public bundle.

    Existing V2 output remains intact if loading, strict validation, serialization, or
    manifest creation fails.  The staging and replacement directory live under the
    approved V2 output parent; legacy ``ui_artifacts/current`` is never addressed.
    """

    source = (source_path or DEFAULT_FIXTURE).resolve()
    output = _assert_approved_output_path(output_dir or DEFAULT_OUTPUT)
    if output == DEFAULT_OUTPUT.resolve():
        if sha256_file(source) != APPROVED_DEFAULT_SOURCE_SHA256:
            raise PublicReleaseBuildError("default V2 output requires the approved locked public-release digest")
        release = load_public_release(source)
        if release.release_id != APPROVED_DEFAULT_RELEASE_ID:
            raise PublicReleaseBuildError("default V2 output requires the approved locked release_id")
        if any(not claim.locked for claim in release.claims):
            raise PublicReleaseBuildError("default V2 output requires locked claim artifacts")
        h2 = next((claim for claim in release.claims if claim.claim_id == "H2-semantic-comparison"), None)
        if h2 is None or h2.status != "unsupported" or h2.result is None or h2.result.estimate >= 0:
            raise PublicReleaseBuildError("default V2 output requires the locked unsupported H2 comparison")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent))
    backup = output.with_name(f".{output.name}.previous")
    try:
        result = _build_bundle_contents(source, staging)
        if backup.exists():
            shutil.rmtree(backup)
        if output.exists():
            output.replace(backup)
        try:
            staging.replace(output)
        except Exception:
            if backup.exists() and not output.exists():
                backup.replace(output)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return result
    except PublicReleaseBuildError:
        raise
    except Exception as exc:
        raise PublicReleaseBuildError("V2 public bundle build failed before publish") from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an aggregate-only public V6 Dashboard V2 bundle.")
    parser.add_argument("--source", type=Path, default=DEFAULT_FIXTURE, help="Strict aggregate public release JSON.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Must remain below KL_180826/ui_artifacts/v2.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_bundle(args.source, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
