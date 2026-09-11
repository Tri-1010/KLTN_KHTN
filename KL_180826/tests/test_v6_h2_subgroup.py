from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import pytest


BUNDLE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = BUNDLE_ROOT / "multi_llm_evidence_extraction" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


subgroup = load("v6_subgroup_analysis")


def protocol(**overrides) -> dict:
    value = json.loads(
        (BUNDLE_ROOT / "multi_llm_evidence_extraction/config/v6_h2_materiality_interaction_v1.json").read_text(encoding="utf-8")
    )
    value["inference"] = value["inference"] | {"bootstrap_samples": 20, "permutation_samples": 20, "block_dates": 1}
    value["gates"] = value["gates"] | {"required_folds": 1, "min_paired_dates": 2, "min_observations_per_group": 2}
    for key, item in overrides.items():
        value[key] = item
    return value


def test_exposure_uses_only_completed_prior_sessions():
    panel = pd.DataFrame(
        {
            "ticker": ["AAA"] * 4,
            "date": pd.to_datetime(["2026-06-02", "2026-06-03", "2026-06-04", "2026-06-05"]),
            "sem_daily__high_materiality_count": [0, 1, 0, 0],
            "sem_daily__medium_materiality_count": [0, 0, 0, 0],
            "semantic_source_status": ["no_valid_news", "valid_source_event", "no_valid_news", "no_valid_news"],
        }
    )
    result = subgroup.build_prior_materiality_exposure(panel)

    assert not bool(result.loc[0, subgroup.EXPOSURE_COLUMN])
    # Same-day high materiality must not expose the decision session.
    assert not bool(result.loc[1, subgroup.EXPOSURE_COLUMN])
    assert bool(result.loc[2, subgroup.EXPOSURE_COLUMN])
    assert bool(result.loc[3, subgroup.EXPOSURE_COLUMN])


def test_exposure_refuses_untrusted_source_status():
    panel = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "date": pd.to_datetime(["2026-06-02"]),
            "sem_daily__high_materiality_count": [0],
            "sem_daily__medium_materiality_count": [0],
            "semantic_source_status": ["extraction_failed"],
        }
    )
    with pytest.raises(ValueError, match="untrusted source-status"):
        subgroup.build_prior_materiality_exposure(panel)


@pytest.mark.parametrize("value", [float("nan"), -1, 1.5, "invalid"])
def test_exposure_refuses_malformed_materiality_counts(value):
    panel = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "date": pd.to_datetime(["2026-06-02"]),
            "sem_daily__high_materiality_count": [value],
            "sem_daily__medium_materiality_count": [0],
            "semantic_source_status": ["no_valid_news"],
        }
    )
    with pytest.raises(ValueError, match="finite nonnegative integers"):
        subgroup.build_prior_materiality_exposure(panel)


def _predictions() -> pd.DataFrame:
    rows = []
    dates = pd.date_range("2026-06-02", periods=3, freq="B")
    for date_index, date in enumerate(dates):
        for ticker, label in (("AAA", 1), ("BBB", 0), ("CCC", 1), ("DDD", 0)):
            # Vary the exposed C probabilities by date so the bootstrap is not
            # degenerate while C remains more calibrated than A in that stratum.
            exposed_probability = (0.85 + 0.03 * date_index) if ticker == "AAA" else (0.15 - 0.03 * date_index)
            for config, probability in (("A_technical", 0.5), ("C_technical_semantic", exposed_probability if ticker in {"AAA", "BBB"} else 0.5)):
                rows.append(
                    {
                        "row_id": f"{ticker}-{date_index}",
                        "ticker": ticker,
                        "date": date,
                        "fold_id": 1,
                        "target_exit_date": date + pd.offsets.BDay(20),
                        "label_outperform_T20": label,
                        "config": config,
                        "model": "RandomForest",
                        "pred_proba_outperform": probability,
                    }
                )
    return pd.DataFrame(rows)


def _exposure() -> pd.DataFrame:
    rows = []
    for date_index, date in enumerate(pd.date_range("2026-06-02", periods=3, freq="B")):
        for ticker in ("AAA", "BBB", "CCC", "DDD"):
            rows.append(
                {
                    "row_id": f"{ticker}-{date_index}",
                    "ticker": ticker,
                    "date": date,
                    subgroup.EXPOSURE_COLUMN: ticker in {"AAA", "BBB"},
                }
            )
    return pd.DataFrame(rows)


def test_brier_interaction_is_exploratory_not_primary_support():
    daily, result = subgroup.analyze_materiality_interaction(_predictions(), _exposure(), protocol())

    assert not daily.empty
    assert result["state"] == "exploratory"
    assert result["metric"] == "brier_improvement_C_minus_A_exposed_minus_comparator"
    assert result["improvement_delta"] > 0
    assert result["gates"]["group_observation_minimum"] is True
    assert "exploratory_only_does_not_replace_v6_primary" in result["limitations"]


def test_interaction_fails_closed_when_group_minimum_is_not_met():
    strict = protocol(gates={"required_folds": 1, "min_paired_dates": 2, "min_observations_per_group": 99})
    _, result = subgroup.analyze_materiality_interaction(_predictions(), _exposure(), strict)

    assert result["state"] == "not_estimable"
    assert result["status"] == "not_estimable_count_or_fold_gate"
    assert result["gates"]["group_observation_minimum"] is False


def test_confirmation_requires_frozen_oos_boundary_and_never_promotes_without_robustness():
    confirmed_protocol = json.loads(
        (BUNDLE_ROOT / "multi_llm_evidence_extraction/config/v6_h2_confirmation_20260602_20260810_v1.json").read_text(encoding="utf-8")
    )
    confirmed_protocol["inference"] = confirmed_protocol["inference"] | {"bootstrap_samples": 20, "permutation_samples": 20, "block_dates": 1}
    confirmed_protocol["gates"] = confirmed_protocol["gates"] | {"required_folds": 1, "min_paired_dates": 2, "min_observations_per_group": 2}
    _, unsupported = subgroup.analyze_materiality_interaction(
        _predictions(), _exposure(), confirmed_protocol, robustness_aligned=False
    )
    assert unsupported["state"] == "unsupported"
    assert unsupported["gates"]["named_robustness_alignment"] is False

    outside = _predictions()
    outside.loc[outside.index[0], "date"] = pd.Timestamp("2026-08-11")
    with pytest.raises(ValueError, match="outside frozen OOS boundary"):
        subgroup.analyze_materiality_interaction(outside, _exposure(), confirmed_protocol, robustness_aligned=True)


def test_paired_observations_reject_target_mismatch():
    broken = _predictions()
    broken.loc[(broken["config"] == "C_technical_semantic") & (broken["row_id"] == "AAA-0"), "label_outperform_T20"] = 0
    with pytest.raises(ValueError, match="targets are not identical"):
        subgroup.paired_brier_observations(broken)


def test_paired_observations_reject_missing_or_malformed_prediction_rows():
    missing = _predictions()
    missing = missing[~((missing["config"] == "C_technical_semantic") & (missing["row_id"] == "AAA-0"))]
    with pytest.raises(ValueError, match="key sets are not identical"):
        subgroup.paired_brier_observations(missing)

    malformed_probability = _predictions()
    malformed_probability.loc[
        (malformed_probability["config"] == "C_technical_semantic") & (malformed_probability["row_id"] == "AAA-0"),
        "pred_proba_outperform",
    ] = 1.1
    with pytest.raises(ValueError, match="probabilities"):
        subgroup.paired_brier_observations(malformed_probability)

    malformed_target = _predictions()
    malformed_target.loc[
        (malformed_target["config"] == "A_technical") & (malformed_target["row_id"] == "AAA-0"),
        "label_outperform_T20",
    ] = 2
    with pytest.raises(ValueError, match="binary"):
        subgroup.paired_brier_observations(malformed_target)


def test_interaction_rejects_duplicate_missing_or_non_boolean_exposure():
    duplicate = pd.concat([_exposure(), _exposure().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="keys must be unique"):
        subgroup.analyze_materiality_interaction(_predictions(), duplicate, protocol())

    missing = _exposure().iloc[1:].copy()
    with pytest.raises(ValueError, match="join is incomplete"):
        subgroup.analyze_materiality_interaction(_predictions(), missing, protocol())

    non_boolean = _exposure().copy()
    non_boolean[subgroup.EXPOSURE_COLUMN] = non_boolean[subgroup.EXPOSURE_COLUMN].astype(object)
    non_boolean.loc[non_boolean.index[0], subgroup.EXPOSURE_COLUMN] = "unknown"
    with pytest.raises(ValueError, match="must be boolean"):
        subgroup.analyze_materiality_interaction(_predictions(), non_boolean, protocol())
