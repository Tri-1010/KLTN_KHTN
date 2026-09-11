"""Read-only loader for a root-contained V6 aggregate public release bundle."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .contracts import (
    PublicReleaseContractError,
    PublicV6ReleaseArtifact,
    RuntimeBundle,
    assert_public_release_payload_safe,
    normalize_portable_json_path,
)


class PublicReleaseRepositoryError(ValueError):
    """Raised when a V2 public release bundle cannot be safely opened."""


def v2_artifact_root() -> Path:
    return (Path(__file__).resolve().parents[1] / "ui_artifacts" / "v2").resolve()


def validate_v2_bundle_directory(value: str | Path) -> Path:
    """Require a non-root V2 child and reject the legacy current bundle."""
    bundle = Path(value).resolve()
    root = v2_artifact_root()
    try:
        relative = bundle.relative_to(root)
    except ValueError as exc:
        raise PublicReleaseRepositoryError("V2 bundle must remain below KL_180826/ui_artifacts/v2") from exc
    if not relative.parts or "current" in relative.parts:
        raise PublicReleaseRepositoryError("V2 bundle must be a non-legacy child of ui_artifacts/v2")
    return bundle


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class PublicReleaseRepository:
    """Load precisely one verified aggregate release member from a portable bundle."""

    def __init__(self, bundle_dir: Path | str):
        self.bundle_dir = validate_v2_bundle_directory(bundle_dir)
        if not self.bundle_dir.is_dir():
            raise PublicReleaseRepositoryError("Public V6 runtime bundle directory is missing")
        try:
            manifest_payload = self._read_json_unverified("manifest.json")
            self.runtime_bundle = RuntimeBundle.model_validate(manifest_payload)
        except (ValidationError, TypeError, ValueError) as exc:
            raise PublicReleaseRepositoryError("Public V6 runtime manifest violates its strict contract") from exc

        self._members = {member.path: member for member in self.runtime_bundle.runtime_members}
        try:
            release_payload = self._read_verified_json(self.runtime_bundle.release_member_path)
            release = assert_public_release_payload_safe(release_payload)
        except PublicReleaseRepositoryError:
            raise
        except (PublicReleaseContractError, ValidationError, TypeError, ValueError) as exc:
            raise PublicReleaseRepositoryError("Aggregate public release violates its strict contract") from exc

        member = self._members[self.runtime_bundle.release_member_path]
        if release.release_id != self.runtime_bundle.release_id:
            raise PublicReleaseRepositoryError("Runtime bundle release_id does not match aggregate public release")
        if release.record_count != member.record_count:
            raise PublicReleaseRepositoryError("Aggregate public release record_count does not match manifest")
        for member_path in self._members:
            self._read_verified_json(member_path)
        self._release_contract = release
        self.release = release.model_dump(mode="json")
        self.manifest = self.runtime_bundle.model_dump(mode="json")

    def release_artifact(self) -> dict[str, Any]:
        return self._release_contract.model_dump(mode="json")

    def claims(self, analysis_state: str | None = None) -> list[dict[str, Any]]:
        claims = [claim.model_dump(mode="json") for claim in self._release_contract.claims]
        return claims if analysis_state is None else [claim for claim in claims if claim["analysis_state"] == analysis_state]

    def gates(self) -> list[dict[str, Any]]:
        return [gate.model_dump(mode="json") for gate in self._release_contract.gates]

    def source_statuses(self) -> list[dict[str, Any]]:
        return [status.model_dump(mode="json") for status in self._release_contract.source_statuses]

    def subgroup_results(self) -> list[dict[str, Any]]:
        return [result.model_dump(mode="json") for result in self._release_contract.subgroup_results]

    def approved_presets(self) -> list[dict[str, Any]]:
        return [preset.model_dump(mode="json") for preset in self._release_contract.approved_presets]

    def _artifact_path(self, relative_path: str) -> Path:
        try:
            normalized = normalize_portable_json_path(relative_path)
        except ValueError as exc:
            raise PublicReleaseRepositoryError("Runtime artifact path is unsafe") from exc
        candidate = (self.bundle_dir / normalized).resolve()
        try:
            candidate.relative_to(self.bundle_dir)
        except ValueError as exc:
            raise PublicReleaseRepositoryError("Runtime artifact path escapes the configured bundle root") from exc
        return candidate

    def _read_json_unverified(self, relative_path: str) -> Any:
        path = self._artifact_path(relative_path)
        if not path.is_file():
            raise PublicReleaseRepositoryError(f"Missing V2 runtime artifact: {relative_path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PublicReleaseRepositoryError(f"Invalid V2 runtime artifact: {relative_path}") from exc

    def _read_verified_json(self, relative_path: str) -> Any:
        try:
            normalized = normalize_portable_json_path(relative_path)
        except ValueError as exc:
            raise PublicReleaseRepositoryError("Runtime member path is unsafe") from exc
        member = self._members.get(normalized)
        if member is None:
            raise PublicReleaseRepositoryError(f"Runtime artifact is not integrity-declared: {normalized}")
        path = self._artifact_path(normalized)
        if not path.is_file():
            raise PublicReleaseRepositoryError(f"Missing V2 runtime artifact: {normalized}")
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise PublicReleaseRepositoryError(f"Cannot read V2 runtime artifact: {normalized}") from exc
        if _sha256_bytes(content) != member.sha256:
            raise PublicReleaseRepositoryError(f"Runtime artifact integrity mismatch: {normalized}")
        try:
            return json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PublicReleaseRepositoryError(f"Invalid V2 runtime artifact: {normalized}") from exc


def _bundle_identity(bundle_dir: Path) -> tuple[tuple[str, int, int, str], ...]:
    try:
        members = sorted(
            (path for path in bundle_dir.rglob("*") if path.is_file()),
            key=lambda path: path.relative_to(bundle_dir).as_posix(),
        )
    except OSError as exc:
        raise PublicReleaseRepositoryError("Cannot identify V2 runtime bundle members") from exc
    if not members:
        raise PublicReleaseRepositoryError("V2 runtime bundle has no members")
    identity: list[tuple[str, int, int, str]] = []
    for path in members:
        try:
            content = path.read_bytes()
            stat = path.stat()
        except OSError as exc:
            raise PublicReleaseRepositoryError(f"Cannot identify V2 runtime member: {path.name}") from exc
        identity.append((path.relative_to(bundle_dir).as_posix(), stat.st_mtime_ns, stat.st_size, _sha256_bytes(content)))
    return tuple(identity)


@lru_cache(maxsize=8)
def _open_public_release_cached(
    resolved_bundle_dir: str,
    member_identity: tuple[tuple[str, int, int, str], ...],
) -> PublicReleaseRepository:
    del member_identity
    return PublicReleaseRepository(resolved_bundle_dir)


def open_public_release(bundle_dir: str | Path) -> PublicReleaseRepository:
    resolved = validate_v2_bundle_directory(bundle_dir)
    identity = _bundle_identity(resolved)
    return _open_public_release_cached(str(resolved), identity)


open_public_release.cache_clear = _open_public_release_cached.cache_clear  # type: ignore[attr-defined]
open_public_release.cache_info = _open_public_release_cached.cache_info  # type: ignore[attr-defined]
