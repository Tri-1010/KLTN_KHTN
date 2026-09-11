"""Launch the local EvidenceTrace Streamlit research prototype."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch EvidenceTrace with a validated UI bundle.")
    parser.add_argument("--bundle", type=Path, default=ROOT / "ui_artifacts" / "current")
    parser.add_argument("--port", type=int, default=8501)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = args.bundle.resolve()
    if not (bundle / "manifest.json").is_file():
        raise FileNotFoundError(f"Missing validated UI bundle: {bundle}. Run build_research_ui_bundle.py first.")
    environment = dict(os.environ)
    environment["EVIDENCETRACE_BUNDLE"] = str(bundle)
    environment.setdefault("EVIDENCETRACE_ENABLE_LIVE", "0")
    command = [sys.executable, "-m", "streamlit", "run", str(ROOT / "research_ui" / "app.py"), "--server.port", str(args.port)]
    return subprocess.call(command, cwd=ROOT, env=environment)


if __name__ == "__main__":
    raise SystemExit(main())
