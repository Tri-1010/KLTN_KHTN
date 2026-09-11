#!/usr/bin/env python
"""Create a Windows-compatible internal ZIP release of the portable bundle."""
from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ZIP = ROOT.parent / "KL_180826_final_internal.zip"
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".hypothesis", ".claude"}
SKIP_NAMES = {".env"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files() -> list[Path]:
    return [
        path for path in sorted(ROOT.rglob("*"))
        if path.is_file()
        and path.name not in SKIP_NAMES
        and path.suffix.lower() not in SKIP_SUFFIXES
        and not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_ZIP)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("output archive must be outside the bundle root")
    output.unlink(missing_ok=True)
    payload = files()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as archive:
        for index, path in enumerate(payload, start=1):
            archive.write(path, arcname=(Path(ROOT.name) / path.relative_to(ROOT)).as_posix())
            if index % 100 == 0 or index == len(payload):
                print(f"archived {index}/{len(payload)}", flush=True)
    checksum_path = output.with_suffix(output.suffix + ".sha256")
    checksum_path.write_text(f"{sha256(output)}  {output.name}\n", encoding="utf-8")
    print(f"archive={output}")
    print(f"files={len(payload)}")
    print(f"bytes={output.stat().st_size}")
    print(f"sha256={checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
