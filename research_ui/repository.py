"""Read-only repository adapter for a validated EvidenceTrace bundle."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .contracts import DatasetManifest
from .policy import filter_monitor_events, parse_iso_date
from .summary import (
    derive_demo_presets,
    derive_workflow_state,
    filter_candidates_historically,
    summarize_candidates,
    summarize_full_evidence_quality_by_period,
    summarize_workflow_by_period,
)


class BundleRepositoryError(ValueError):
    """Raised when a UI bundle is missing or violates expected shape."""


class BundleRepository:
    """Load only UI-safe bundle artifacts; never source audit packs directly."""

    def __init__(self, bundle_dir: Path):
        self.bundle_dir = bundle_dir.resolve()
        try:
            raw_manifest = self._read_json_unverified("manifest.json")
            self._manifest_contract = DatasetManifest.model_validate(raw_manifest)
        except (ValidationError, TypeError) as exc:
            raise BundleRepositoryError("Bundle manifest violates validated contract") from exc
        self.manifest = self._manifest_contract.model_dump(mode="json")
        if self._manifest_contract.leakage_validation_passed is not True:
            raise BundleRepositoryError("Bundle leakage validation has not passed")
        self._runtime_hashes = {member.path: member.sha256 for member in self._manifest_contract.runtime_members}

    def candidates(self) -> list[dict[str, Any]]:
        return self._read_json("select.json")

    def overview(self) -> dict[str, Any]:
        """Summarize select and monitor zones without accessing review payloads."""
        candidates = self.candidates()
        states_by_id = {
            str(candidate["decision_id"]): derive_workflow_state(self.monitor(str(candidate["decision_id"])))
            for candidate in candidates
        }
        return summarize_candidates(candidates, states_by_id)

    def demo_presets(self) -> list[dict[str, str]]:
        """Return deterministic presets selected from safe select and monitor zones."""
        candidates = self.candidates()
        states_by_id = {
            str(candidate["decision_id"]): derive_workflow_state(self.monitor(str(candidate["decision_id"])))
            for candidate in candidates
        }
        return derive_demo_presets(candidates, states_by_id)

    def dashboard_scope(self, as_of: date | str, periods: list[str] | None = None) -> dict[str, Any]:
        """Return chart-ready data sourced only from select, initial, and monitor zones."""
        candidates = filter_candidates_historically(self.candidates(), as_of, periods)
        events_by_id = {str(candidate["decision_id"]): self.monitor(str(candidate["decision_id"]), as_of) for candidate in candidates}
        details = [self.initial(str(candidate["decision_id"])) for candidate in candidates]
        return {
            "candidates": candidates,
            "events_by_id": events_by_id,
            "workflow_by_period": summarize_workflow_by_period(candidates, events_by_id),
            "evidence_quality_by_period": summarize_full_evidence_quality_by_period(details),
        }

    def monitor_date_bounds(self, decision_id: str) -> tuple[date, date]:
        """Return decision cutoff and validated monitoring horizon."""
        lower = parse_iso_date(self.initial(decision_id)["decision_date"])
        return lower, max(lower, self.latest_monitor_date(decision_id))

    def periods(self) -> list[str]:
        return sorted({str(row["period_id"]) for row in self.candidates()})

    def initial(self, decision_id: str, snapshot_mode: str = "full_evidence") -> dict[str, Any]:
        directory = "initial" if snapshot_mode == "full_evidence" else "initial_ml_only"
        return self._read_json(f"{directory}/{decision_id}.json")

    def monitor(self, decision_id: str, as_of: date | str | None = None) -> list[dict[str, Any]]:
        events = self._read_json(f"monitor/{decision_id}.json")
        if as_of is None:
            return events
        return filter_monitor_events(events, as_of)

    def update(self, decision_id: str, as_of: date | str | None = None) -> dict[str, Any]:
        """Derive a read-only update state from monitoring evidence through `as_of`."""
        baseline = self._read_json(f"update/{decision_id}.json")
        if as_of is None:
            return baseline
        cutoff = parse_iso_date(as_of)
        events = self.monitor(decision_id, cutoff)
        state = "Review Required" if any(event["action"] == "Review Required" for event in events) else "Watch" if events else "Initial"
        baseline["as_of"] = cutoff.isoformat()
        baseline["monitoring_events"] = events
        baseline["workflow_state"] = state
        return baseline

    def review(self, decision_id: str) -> dict[str, Any]:
        return self._read_json(f"review/{decision_id}.json")

    def semantic(self, news_id: str) -> dict[str, Any]:
        return self._read_json(f"semantic/{news_id}.json")

    def evaluations(self) -> list[dict[str, Any]]:
        return self._read_json("evaluation.json")

    def provenance(self) -> dict[str, Any]:
        return self._read_json("provenance.json")

    def validation(self) -> dict[str, Any]:
        return self._read_json("bundle_validation.json")

    def latest_monitor_date(self, decision_id: str) -> date:
        del decision_id
        return self._manifest_contract.monitor_as_of_date

    def _artifact_path(self, relative_path: str) -> Path:
        normalized = relative_path.replace("\\", "/")
        path = (self.bundle_dir / normalized).resolve()
        try:
            path.relative_to(self.bundle_dir)
        except ValueError as exc:
            raise BundleRepositoryError("Bundle path escapes configured root") from exc
        return path

    def _read_json_unverified(self, relative_path: str) -> Any:
        path = self._artifact_path(relative_path)
        if not path.is_file():
            raise BundleRepositoryError(f"Missing validated bundle artifact: {relative_path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BundleRepositoryError(f"Invalid validated bundle artifact: {relative_path}") from exc

    def _read_json(self, relative_path: str) -> Any:
        normalized = relative_path.replace("\\", "/")
        expected_hash = self._runtime_hashes.get(normalized)
        if expected_hash is None:
            raise BundleRepositoryError(f"Runtime artifact is not integrity-declared: {normalized}")
        path = self._artifact_path(normalized)
        if not path.is_file():
            raise BundleRepositoryError(f"Missing validated bundle artifact: {normalized}")
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise BundleRepositoryError(f"Cannot read validated bundle artifact: {normalized}") from exc
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != expected_hash:
            raise BundleRepositoryError(f"Runtime artifact integrity mismatch: {normalized}")
        try:
            return json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BundleRepositoryError(f"Invalid validated bundle artifact: {normalized}") from exc


def _manifest_identity(bundle_dir: Path) -> tuple[int, int, str]:
    manifest_path = bundle_dir / "manifest.json"
    try:
        stat = manifest_path.stat()
        digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise BundleRepositoryError(f"Cannot identify bundle manifest: {manifest_path}") from exc
    return stat.st_mtime_ns, stat.st_size, digest


@lru_cache(maxsize=8)
def _open_bundle_cached(
    resolved_bundle_dir: str,
    manifest_mtime_ns: int,
    manifest_size: int,
    manifest_sha256: str,
) -> BundleRepository:
    del manifest_mtime_ns, manifest_size, manifest_sha256
    return BundleRepository(Path(resolved_bundle_dir))


def open_bundle(bundle_dir: str) -> BundleRepository:
    resolved = Path(bundle_dir).resolve()
    identity = _manifest_identity(resolved)
    return _open_bundle_cached(str(resolved), *identity)


open_bundle.cache_clear = _open_bundle_cached.cache_clear  # type: ignore[attr-defined]
open_bundle.cache_info = _open_bundle_cached.cache_info  # type: ignore[attr-defined]
