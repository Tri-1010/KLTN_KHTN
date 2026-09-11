#!/usr/bin/env python
"""Generate a SHA-256 inventory for the portable KL_180826 bundle."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "bundle_manifest.json"
EXCLUDE = {".git", ".venv", "__pycache__", ".pytest_cache", ".hypothesis"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def scope(relative: str) -> str:
    if relative.startswith("data/news/") or relative.startswith("restricted_internal_data/"):
        return "restricted"
    if relative.startswith("ui_artifacts/") or relative.startswith("research_ui/"):
        return "runtime"
    if relative.startswith("thesis_submission/") or relative.startswith("docs/supplementary_evidence/"):
        return "canonical" if relative.startswith("thesis_submission/") else "supplementary"
    if relative.startswith(("multi_llm_evidence_extraction/", "data/", "pipeline/", "scripts/", "config/", "tests/")):
        return "reproduction"
    return "bundle"


def main() -> None:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in EXCLUDE for part in path.relative_to(ROOT).parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == OUT.name:
            continue
        files.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": digest(path), "scope": scope(relative)})
    payload = {
        "schema_version": "kl-180826-portable-bundle-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "bundle_root": "{BUNDLE_ROOT}",
        "file_count": len(files),
        "total_size_bytes": sum(item["size_bytes"] for item in files),
        "files": files,
        "notes": [
            "Frozen canonical and UI artifacts are preserved byte-for-byte.",
            "Restricted internal news is included in the internal archive but excluded by Git.",
            "Do not compare legacy runs with canonical_150_v7 as a common benchmark.",
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"path": str(OUT), "file_count": len(files), "total_size_bytes": payload["total_size_bytes"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
