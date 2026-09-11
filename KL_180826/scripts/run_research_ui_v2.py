"""Launch the standalone V6 study-results Dashboard V2 from a V2-only bundle."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_ui_v2.repository import validate_v2_bundle_directory

DEFAULT_BUNDLE = ROOT / "ui_artifacts" / "v2" / "default"
APP_PATH = ROOT / "research_ui_v2" / "app.py"


def _v2_bundle_path(value: Path) -> Path:
    return validate_v2_bundle_directory(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the non-executing V6 study-results Dashboard V2.")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--port", type=int, default=8502)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = _v2_bundle_path(args.bundle)
    if not (bundle / "manifest.json").is_file():
        raise FileNotFoundError(f"Missing V2 public-release bundle: {bundle}. Run build_research_ui_v2_bundle.py first.")
    environment = dict(os.environ)
    environment["V6_RESULTS_V2_BUNDLE"] = str(bundle)
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", str(APP_PATH), "--server.port", str(args.port)],
        cwd=ROOT,
        env=environment,
    )


if __name__ == "__main__":
    raise SystemExit(main())
