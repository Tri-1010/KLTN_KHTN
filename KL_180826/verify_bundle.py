#!/usr/bin/env python
"""Read-only integrity checks for the KL_180826 portable internal bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI = ROOT / "ui_artifacts" / "current"
CANONICAL = ROOT / "multi_llm_evidence_extraction" / "outputs" / "harmonized" / "canonical_150_v7"

REQUIRED = (
    "README.md",
    "BUNDLE_SCOPE.md",
    "path_mapping.json",
    "requirements-runtime.txt",
    "requirements-reproduction.txt",
    ".env.example",
    "thesis_submission/thesis/luan_van.md",
    "thesis_submission/proposal/de_cuong.md",
    "thesis_submission/canonical_results/canonical_summary.json",
    "data/prices/all_vn30_prices.csv",
    "data/prices_extended/VNINDEX.csv",
    "data/features/technical_features.csv",
    "multi_llm_evidence_extraction/config/harmonized_comparison_v5.json",
    "multi_llm_evidence_extraction/data/sample_news_for_annotation.csv",
    "multi_llm_evidence_extraction/outputs/pseudo_labels_consensus.jsonl",
    "research_ui/app.py",
    "scripts/run_research_ui.py",
    "run_dashboard.bat",
)
SECRET_PATTERN = re.compile(r"(?:sk-ant-|AIza[0-9A-Za-z_-]{20,}|ANTHROPIC_API_KEY\s*=\s*[^\s#]|GEMINI_API_KEY\s*=\s*[^\s#]|DEEPSEEK_API_KEY\s*=\s*[^\s#])")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_ui_manifest(errors: list[str]) -> None:
    manifest_path = UI / "manifest.json"
    if not manifest_path.is_file():
        errors.append("missing validated UI manifest")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid UI manifest: {exc}")
        return
    for item in manifest.get("runtime_members", []):
        relative = item.get("path")
        expected = item.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append("invalid UI runtime member declaration")
            continue
        member = (UI / relative).resolve()
        try:
            member.relative_to(UI.resolve())
        except ValueError:
            errors.append(f"UI runtime member escapes bundle: {relative}")
            continue
        if not member.is_file():
            errors.append(f"missing UI runtime member: {relative}")
        elif sha256(member) != expected:
            errors.append(f"UI runtime hash mismatch: {relative}")


def check_bundle_manifest(errors: list[str], warnings: list[str]) -> None:
    manifest_path = ROOT / "bundle_manifest.json"
    if not manifest_path.is_file():
        warnings.append("bundle_manifest.json not generated yet")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid bundle manifest: {exc}")
        return
    for item in manifest.get("files", []):
        relative, expected = item.get("path"), item.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            errors.append("invalid bundle manifest file item")
            continue
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"bundle manifest path escapes root: {relative}")
            continue
        if not path.is_file():
            errors.append(f"bundle manifest file missing: {relative}")
        elif sha256(path) != expected:
            errors.append(f"bundle manifest hash mismatch: {relative}")


def check_nonrestricted_secrets(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT).as_posix()
        if not path.is_file() or relative.startswith(("data/news/", "restricted_internal_data/", "tests/")):
            continue
        if path.name == ".env" or path.suffix.lower() not in {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".csv", ".bat"}:
            continue
        if path.resolve() in {
            Path(__file__).resolve(),
            (ROOT / "thesis_submission" / "reproduction" / "validate_submission.py").resolve(),
        }:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        if SECRET_PATTERN.search(text):
            errors.append(f"possible secret outside restricted data: {path.relative_to(ROOT).as_posix()}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="fail when optional manifest is absent")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"required file missing: {relative}")
    if (ROOT / ".env").exists():
        errors.append("real .env is present in bundle")
    if not CANONICAL.is_dir():
        errors.append("frozen canonical_150_v7 directory missing")
    for legacy in range(1, 7):
        if (ROOT / "multi_llm_evidence_extraction" / "outputs" / "harmonized" / f"canonical_150_v{legacy}").exists():
            errors.append(f"legacy canonical run included: canonical_150_v{legacy}")
    check_ui_manifest(errors)
    check_bundle_manifest(errors, warnings)
    check_nonrestricted_secrets(errors)
    if args.strict and warnings:
        errors.extend(warnings)
    status = "passed" if not errors else "failed"
    print(json.dumps({"status": status, "root": str(ROOT), "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
