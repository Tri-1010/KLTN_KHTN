from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


outcome = load("run_outcome_review")
manual = load("build_manual_review_sheet")
summary = load("summarize_manual_sanity_check")


def test_outcome_dimensions_keep_legacy_label():
    assert outcome.label("support", 0.01) == "confirmed"
    assert outcome.outcome_direction("support", 0.01) == "aligned"
    assert outcome.outcome_direction("support", -0.01) == "opposed"
    assert outcome.outcome_direction("risk", -0.01) == "aligned"
    assert outcome.outcome_direction("neutral", 0.01) == "unavailable"
    assert outcome.outcome_salience(0.01) == "not_salient"
    assert outcome.outcome_salience(0.06) == "salient"


def test_preserve_human_values_normalizes_numeric_keys():
    selected = pd.DataFrame({"news_id": [1], "ticker": ["AAA"], "title": ["new"]})
    previous = pd.DataFrame({
        "news_id": ["1"], "ticker": ["AAA"], "reviewer_id": ["human-1"],
        "human_direction_label": ["support"], "human_relevance_ok": ["yes"],
    })
    result = manual.preserve_human_values(selected, previous)
    assert result.loc[0, "reviewer_id"] == "human-1"
    assert result.loc[0, "human_direction_label"] == "support"
    assert result.loc[0, "human_materiality_label"] == ""


def test_manual_summary_statuses_and_legacy_support():
    pending = summary.summarize(pd.DataFrame({"news_id": ["1", "2"]}))
    assert pending["status"] == "pending"
    partial = summary.summarize(pd.DataFrame({"human_relevance_ok": ["yes", ""]}))
    assert partial["status"] == "partial"
    complete = summary.summarize(pd.DataFrame({
        "reviewer_id": ["h1", "h1"],
        "human_direction_label": ["support", "risk"],
    }))
    assert complete["status"] == "complete_small_qc"
    assert complete["reviewer_backed_rows"] == 2
