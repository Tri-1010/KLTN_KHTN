"""Artifact catalog loading and integrity validation for EvidenceTrace."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class CatalogValidationError(ValueError):
    """Raised when a runtime artifact catalog is invalid or stale."""


@dataclass(frozen=True)
class CatalogIssue:
    level: str
    subject: str
    message: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or (repo_root() / "config" / "research_ui_catalog.yaml")
    with catalog_path.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)
    if not isinstance(catalog, dict) or not isinstance(catalog.get("artifacts"), list):
        raise CatalogValidationError("Catalog must define an artifacts list")
    return catalog


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record_count(path: Path) -> int:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    if suffix == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return sum(1 for _ in csv.DictReader(handle))
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return len(data) if isinstance(data, (list, dict)) else 1
    return 0


def validate_catalog(catalog: dict[str, Any], root: Path | None = None) -> list[CatalogIssue]:
    """Validate required source paths, pinned hashes, expected counts and run score totals."""
    resolved_root = root or repo_root()
    issues: list[CatalogIssue] = []
    for artifact in catalog.get("artifacts", []):
        _validate_reference(artifact, resolved_root, issues)

    for run in catalog.get("runs", []):
        run_id = str(run.get("run_id", "unknown-run"))
        for variant, card in (run.get("cards") or {}).items():
            _validate_reference(card, resolved_root, issues, f"{run_id}:{variant}")
        rubric = run.get("rubric")
        if isinstance(rubric, dict):
            _validate_reference(rubric, resolved_root, issues, f"{run_id}:rubric")
            expected = rubric.get("expected_records")
            relative_path = rubric.get("path")
            path = resolved_root / relative_path if isinstance(relative_path, str) and relative_path else None
            if expected is not None and path is not None and path.is_file():
                actual = record_count(path)
                if actual != expected:
                    issues.append(CatalogIssue("error", f"{run_id}:rubric", f"expected {expected} score rows, found {actual}"))
    return issues


def assert_catalog_valid(catalog: dict[str, Any], root: Path | None = None) -> None:
    issues = validate_catalog(catalog, root)
    errors = [issue for issue in issues if issue.level == "error"]
    if errors:
        text = "; ".join(f"{issue.subject}: {issue.message}" for issue in errors)
        raise CatalogValidationError(text)


def _validate_reference(reference: dict[str, Any], root: Path, issues: list[CatalogIssue], subject: str | None = None) -> None:
    name = subject or str(reference.get("name", reference.get("path", "artifact")))
    relative = reference.get("path")
    if not isinstance(relative, str) or not relative:
        issues.append(CatalogIssue("error", name, "missing path"))
        return
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        issues.append(CatalogIssue("error", name, "path escapes repository root"))
        return
    if not path.is_file():
        issues.append(CatalogIssue("error", name, f"missing artifact {relative}"))
        return
    expected_hash = reference.get("sha256")
    if expected_hash:
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            issues.append(CatalogIssue("error", name, "SHA-256 mismatch"))
    expected_count = reference.get("expected_records")
    if expected_count is not None:
        actual_count = record_count(path)
        if actual_count != expected_count:
            issues.append(CatalogIssue("error", name, f"expected {expected_count} records, found {actual_count}"))
    expected_columns = reference.get("expected_columns")
    if expected_columns is not None:
        if path.suffix.lower() != ".csv":
            issues.append(CatalogIssue("error", name, "expected_columns requires a CSV artifact"))
        elif not isinstance(expected_columns, list) or not all(isinstance(column, str) for column in expected_columns):
            issues.append(CatalogIssue("error", name, "expected_columns must be a list of column names"))
        else:
            with path.open(encoding="utf-8-sig", newline="") as handle:
                actual_columns = csv.DictReader(handle).fieldnames or []
            if actual_columns != expected_columns:
                issues.append(CatalogIssue("error", name, f"expected columns {expected_columns}, found {actual_columns}"))
