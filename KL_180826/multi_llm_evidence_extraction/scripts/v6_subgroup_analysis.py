"""Pre-specified V6 H2 materiality interaction analysis.

This module evaluates a paired C-minus-A probability-performance interaction. It
never filters or retrains the V6 primary sample, so its discovery result cannot
replace the locked V6 primary H2 conclusion.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from run_harmonized_comparison import bh_adjust, bootstrap_draws_estimable, fold_local_block_draws

EXPOSURE_COLUMN = "materiality_hm_prior_20_sessions"


def build_prior_materiality_exposure(
    panel: pd.DataFrame,
    *,
    high_column: str = "sem_daily__high_materiality_count",
    medium_column: str = "sem_daily__medium_materiality_count",
    status_column: str = "semantic_source_status",
    window: int = 20,
) -> pd.DataFrame:
    """Calculate high/medium exposure using completed prior sessions only."""
    required = {"ticker", "date", high_column, medium_column}
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"subgroup exposure missing panel columns: {sorted(missing)}")
    work = panel.copy()
    work["ticker"] = work["ticker"].astype(str).str.upper()
    work["date"] = pd.to_datetime(work["date"], errors="coerce").dt.normalize()
    if work[["ticker", "date"]].isna().any().any() or work.duplicated(["ticker", "date"]).any():
        raise ValueError("subgroup exposure requires unique valid ticker/date rows")
    if status_column in work:
        trusted = work[status_column].fillna("").astype(str).isin({"valid_source_event", "no_valid_news"})
        if not trusted.all():
            raise ValueError("subgroup exposure has untrusted source-status rows")
    frames: list[pd.DataFrame] = []
    for _, group in work.sort_values(["ticker", "date"]).groupby("ticker", sort=False):
        item = group.copy()
        high = pd.to_numeric(item[high_column], errors="coerce")
        medium = pd.to_numeric(item[medium_column], errors="coerce")
        if (
            high.isna().any()
            or medium.isna().any()
            or not np.isfinite(high.to_numpy()).all()
            or not np.isfinite(medium.to_numpy()).all()
            or (high < 0).any()
            or (medium < 0).any()
            or not np.equal(high.to_numpy(), np.floor(high.to_numpy())).all()
            or not np.equal(medium.to_numpy(), np.floor(medium.to_numpy())).all()
        ):
            raise ValueError("subgroup materiality counts must be finite nonnegative integers")
        current = (high.gt(0) | medium.gt(0)).astype(int)
        prior_count = current.shift(1).rolling(int(window), min_periods=1).sum().fillna(0).astype(int)
        item["materiality_hm_prior_20_sessions_count"] = prior_count
        item[EXPOSURE_COLUMN] = prior_count.gt(0)
        frames.append(item)
    return pd.concat(frames, ignore_index=True).sort_values(["ticker", "date"]).reset_index(drop=True)


def paired_brier_observations(predictions: pd.DataFrame, *, model: str = "RandomForest") -> pd.DataFrame:
    """Return row-level C-minus-A Brier improvement, where higher is better."""
    required = {
        "row_id", "ticker", "date", "fold_id", "target_exit_date",
        "label_outperform_T20", "config", "model", "pred_proba_outperform",
    }
    missing = required - set(predictions.columns)
    if missing:
        raise ValueError(f"subgroup predictions missing columns: {sorted(missing)}")
    subset = predictions[predictions["model"].eq(model)].copy()
    keys = ["row_id", "ticker", "date", "fold_id", "target_exit_date"]
    left = subset[subset["config"].eq("A_technical")].copy()
    right = subset[subset["config"].eq("C_technical_semantic")].copy()
    if left.empty or right.empty:
        raise ValueError("subgroup requires nonempty A_technical and C_technical_semantic predictions")
    if left.duplicated(keys).any() or right.duplicated(keys).any():
        raise ValueError("subgroup A/C prediction keys must be unique")
    left_keys = left.loc[:, keys].sort_values(keys).reset_index(drop=True)
    right_keys = right.loc[:, keys].sort_values(keys).reset_index(drop=True)
    if not left_keys.equals(right_keys):
        raise ValueError("subgroup A/C prediction key sets are not identical")
    merged = left.merge(right, on=keys, suffixes=("_a", "_c"), validate="one_to_one")
    a_y = pd.to_numeric(merged["label_outperform_T20_a"], errors="coerce")
    c_y = pd.to_numeric(merged["label_outperform_T20_c"], errors="coerce")
    if a_y.isna().any() or c_y.isna().any() or not a_y.isin([0, 1]).all() or not c_y.isin([0, 1]).all():
        raise ValueError("subgroup A/C targets must be finite binary values")
    if not np.array_equal(a_y.to_numpy(), c_y.to_numpy(), equal_nan=True):
        raise ValueError("subgroup A/C targets are not identical")
    a_probability = pd.to_numeric(merged["pred_proba_outperform_a"], errors="coerce")
    c_probability = pd.to_numeric(merged["pred_proba_outperform_c"], errors="coerce")
    if (
        a_probability.isna().any()
        or c_probability.isna().any()
        or not np.isfinite(a_probability.to_numpy()).all()
        or not np.isfinite(c_probability.to_numpy()).all()
        or not a_probability.between(0, 1).all()
        or not c_probability.between(0, 1).all()
    ):
        raise ValueError("subgroup A/C probabilities must be finite values in [0, 1]")
    result = merged[keys].copy()
    result["label_outperform_T20"] = a_y.astype(int)
    result["brier_a"] = (a_probability - a_y) ** 2
    result["brier_c"] = (c_probability - a_y) ** 2
    result["c_minus_a_brier_improvement"] = result["brier_a"] - result["brier_c"]
    return result


def _aggregate_by_date(observations: pd.DataFrame, exposure_column: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (fold_id, date, exposed), group in observations.groupby(["fold_id", "date", exposure_column], sort=True):
        rows.append({
            "fold_id": int(fold_id),
            "date": pd.Timestamp(date),
            "exposed": bool(exposed),
            "n_observations": int(len(group)),
            "improvement_delta": float(group["c_minus_a_brier_improvement"].mean()),
        })
    return pd.DataFrame(rows)


def _interaction_date_rows(daily: pd.DataFrame) -> pd.DataFrame:
    exposed = daily[daily["exposed"]].rename(columns={"improvement_delta": "exposed_improvement", "n_observations": "n_exposed"})
    comparator = daily[~daily["exposed"]].rename(columns={"improvement_delta": "comparator_improvement", "n_observations": "n_comparator"})
    merged = exposed.merge(comparator, on=["fold_id", "date"], validate="one_to_one")
    merged["improvement_delta"] = merged["exposed_improvement"] - merged["comparator_improvement"]
    return merged


def _validate_confirmation_window(
    predictions: pd.DataFrame,
    protocol: dict[str, Any],
    *,
    target_exit_dates: dict[pd.Timestamp, pd.Timestamp] | None = None,
) -> None:
    window = protocol.get("confirmation_oos") or {}
    start = pd.Timestamp(window.get("start_date")).normalize()
    end = pd.Timestamp(window.get("end_date")).normalize()
    if pd.isna(start) or pd.isna(end) or start > end:
        raise ValueError("confirmation protocol has invalid OOS date boundary")
    dates = pd.to_datetime(predictions["date"], errors="coerce").dt.normalize()
    exits = pd.to_datetime(predictions["target_exit_date"], errors="coerce").dt.normalize()
    if dates.isna().any() or not dates.between(start, end).all():
        raise ValueError("confirmation predictions fall outside frozen OOS boundary")
    if exits.isna().any():
        raise ValueError("confirmation predictions lack complete T+20 target exits")
    if target_exit_dates is not None:
        expected = dates.map(target_exit_dates)
        if expected.isna().any() or not exits.equals(expected):
            raise ValueError("confirmation predictions do not use frozen T+20 target exits")


def frozen_t20_exit_dates(
    prices: pd.DataFrame,
    benchmark: pd.DataFrame,
    protocol: dict[str, Any],
) -> dict[pd.Timestamp, pd.Timestamp]:
    """Return exact benchmark-session T+20 exits after validating stock coverage."""
    window = protocol.get("confirmation_oos") or {}
    start = pd.Timestamp(window.get("start_date")).normalize()
    end = pd.Timestamp(window.get("end_date")).normalize()
    horizon = int(window.get("label_horizon_benchmark_sessions", 0))
    if pd.isna(start) or pd.isna(end) or start > end or horizon < 1:
        raise ValueError("confirmation protocol has invalid T+20 target contract")
    required_price_columns = {"ticker", "date", "close"}
    if not required_price_columns.issubset(prices.columns) or not {"date", "close"}.issubset(benchmark.columns):
        raise ValueError("confirmation frozen price inputs lack required T+20 columns")
    stock = prices.loc[:, ["ticker", "date", "close"]].copy()
    stock["ticker"] = stock["ticker"].astype(str).str.upper().str.strip()
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce").dt.normalize()
    stock["close"] = pd.to_numeric(stock["close"], errors="coerce")
    bench = benchmark.loc[:, ["date", "close"]].copy()
    bench["date"] = pd.to_datetime(bench["date"], errors="coerce").dt.normalize()
    bench["close"] = pd.to_numeric(bench["close"], errors="coerce")
    if (
        stock[["ticker", "date", "close"]].isna().any().any()
        or bench[["date", "close"]].isna().any().any()
        or stock.duplicated(["ticker", "date"]).any()
        or bench.duplicated(["date"]).any()
    ):
        raise ValueError("confirmation frozen price inputs have invalid T+20 rows")
    benchmark_dates = list(bench.sort_values("date")["date"])
    position = {date: index for index, date in enumerate(benchmark_dates)}
    entries = [date for date in benchmark_dates if start <= date <= end]
    exits: dict[pd.Timestamp, pd.Timestamp] = {}
    stock_dates = set(zip(stock["ticker"], stock["date"]))
    for entry in entries:
        index = position[entry]
        if index + horizon >= len(benchmark_dates):
            raise ValueError("confirmation frozen price inputs lack complete T+20 benchmark coverage")
        exit_date = benchmark_dates[index + horizon]
        if not all((ticker, entry) in stock_dates and (ticker, exit_date) in stock_dates for ticker in stock["ticker"].unique()):
            raise ValueError("confirmation frozen price inputs lack complete T+20 stock coverage")
        exits[entry] = exit_date
    return exits


def validate_confirmation_prediction_targets(
    predictions: pd.DataFrame,
    prices: pd.DataFrame,
    benchmark: pd.DataFrame,
    protocol: dict[str, Any],
) -> None:
    """Verify each frozen prediction row's T+20 exit and binary label from prices."""
    exits = frozen_t20_exit_dates(prices, benchmark, protocol)
    _validate_confirmation_window(predictions, protocol, target_exit_dates=exits)
    stock = prices.loc[:, ["ticker", "date", "close"]].copy()
    stock["ticker"] = stock["ticker"].astype(str).str.upper().str.strip()
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce").dt.normalize()
    stock["close"] = pd.to_numeric(stock["close"], errors="coerce")
    bench = benchmark.loc[:, ["date", "close"]].copy()
    bench["date"] = pd.to_datetime(bench["date"], errors="coerce").dt.normalize()
    bench["close"] = pd.to_numeric(bench["close"], errors="coerce")
    stock_lookup = stock.set_index(["ticker", "date"])["close"]
    benchmark_lookup = bench.set_index("date")["close"]
    work = predictions.copy()
    work["ticker"] = work["ticker"].astype(str).str.upper().str.strip()
    work["date"] = pd.to_datetime(work["date"], errors="coerce").dt.normalize()
    for row in work.itertuples(index=False):
        entry = row.date
        exit_date = exits.get(entry)
        entry_stock = stock_lookup.get((row.ticker, entry))
        exit_stock = stock_lookup.get((row.ticker, exit_date))
        entry_benchmark = benchmark_lookup.get(entry)
        exit_benchmark = benchmark_lookup.get(exit_date)
        if any(value is None or not np.isfinite(value) or value == 0 for value in (entry_stock, exit_stock, entry_benchmark, exit_benchmark)):
            raise ValueError("confirmation predictions cannot be reconciled to frozen T+20 prices")
        label = int((exit_stock / entry_stock - 1) > (exit_benchmark / entry_benchmark - 1))
        if int(row.label_outperform_T20) != label:
            raise ValueError("confirmation prediction label does not match frozen T+20 prices")


def analyze_materiality_interaction(
    predictions: pd.DataFrame,
    exposure: pd.DataFrame,
    protocol: dict[str, Any],
    *,
    robustness_aligned: bool | None = None,
    target_exit_dates: dict[pd.Timestamp, pd.Timestamp] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run the frozen Brier interaction with honest result states."""
    state_mode = str(protocol.get("state", "exploratory"))
    if state_mode not in {"exploratory", "confirmation"}:
        raise ValueError("subgroup protocol state must be exploratory or confirmation")
    if state_mode == "confirmation":
        _validate_confirmation_window(predictions, protocol, target_exit_dates=target_exit_dates)

    exposure_column = str(protocol["exposure"]["column"])
    keys = ["row_id", "ticker", "date"]
    if not set(keys + [exposure_column]).issubset(exposure.columns):
        raise ValueError("subgroup exposure artifact missing required columns")
    paired = paired_brier_observations(predictions, model=str(protocol["comparison"]["model"]))
    paired["ticker"] = paired["ticker"].astype(str).str.upper()
    paired["date"] = pd.to_datetime(paired["date"], errors="coerce").dt.normalize()
    exposure_join = exposure[keys + [exposure_column]].copy()
    exposure_join["ticker"] = exposure_join["ticker"].astype(str).str.upper()
    exposure_join["date"] = pd.to_datetime(exposure_join["date"], errors="coerce").dt.normalize()
    if paired["date"].isna().any() or exposure_join["date"].isna().any():
        raise ValueError("subgroup exposure/prediction dates are invalid")
    if exposure_join.duplicated(keys).any():
        raise ValueError("subgroup exposure keys must be unique")
    if not exposure_join[exposure_column].map(lambda value: isinstance(value, (bool, np.bool_))).all():
        raise ValueError("subgroup exposure values must be boolean")
    work = paired.merge(exposure_join, on=keys, how="left", validate="one_to_one", indicator=True)
    if not work["_merge"].eq("both").all() or len(work) != len(paired):
        raise ValueError("subgroup exposure join is incomplete")
    work = work.drop(columns=["_merge"])
    work[exposure_column] = work[exposure_column].astype(bool)
    daily = _aggregate_by_date(work, exposure_column)
    interaction = _interaction_date_rows(daily)

    gates_config = protocol["gates"]
    required_folds = int(gates_config["required_folds"])
    min_dates = int(gates_config["min_paired_dates"])
    min_group_observations = int(gates_config["min_observations_per_group"])
    group_counts = work.groupby(exposure_column).size().to_dict()
    group_minimum = bool(group_counts.get(True, 0) >= min_group_observations and group_counts.get(False, 0) >= min_group_observations)
    full_folds = int(interaction["fold_id"].nunique()) == required_folds if not interaction.empty else False
    enough_dates = len(interaction) >= min_dates
    estimable = group_minimum and full_folds and enough_dates

    inference = protocol["inference"]
    bootstrap_count = int(inference["bootstrap_samples"])
    permutation_count = int(inference["permutation_samples"])
    block, seed = int(inference["block_dates"]), int(inference["seed"])
    bootstrap = fold_local_block_draws(interaction, bootstrap_count, block, seed) if estimable else np.array([])
    permutation = fold_local_block_draws(interaction, permutation_count, block, seed, True) if estimable else np.array([])
    if estimable and not bootstrap_draws_estimable(bootstrap):
        estimable, status = False, "not_estimable_degenerate_bootstrap"
        bootstrap, permutation = np.array([]), np.array([])
    else:
        status = "ok" if estimable else "not_estimable_count_or_fold_gate"

    effect = float(interaction["improvement_delta"].mean()) if not interaction.empty else np.nan
    p_value = (np.sum(np.abs(permutation) >= abs(effect)) + 1) / (len(permutation) + 1) if len(permutation) else np.nan
    alpha = float(inference["alpha"])
    ci_low = float(np.percentile(bootstrap, 2.5)) if len(bootstrap) else np.nan
    ci_high = float(np.percentile(bootstrap, 97.5)) if len(bootstrap) else np.nan
    p_value_bh = float(bh_adjust(pd.Series([p_value])).iloc[0]) if pd.notna(p_value) else np.nan
    positive = bool(pd.notna(effect) and effect > 0)
    ci_positive = bool(pd.notna(ci_low) and ci_low > 0)
    p_pass = bool(pd.notna(p_value_bh) and p_value_bh <= alpha)
    robustness_required = bool(gates_config.get("require_named_robustness_alignment", False))
    robustness_pass = True if not robustness_required else robustness_aligned is True

    if not estimable:
        state = "not_estimable"
    elif state_mode == "exploratory":
        state = "exploratory"
    elif positive and ci_positive and p_pass and robustness_pass:
        state = "confirmed"
    else:
        state = "unsupported"

    summary = {
        "artifact_schema_version": "v6_h2_materiality_interaction_v1",
        "protocol_id": protocol["protocol_id"],
        "state": state,
        "status": status,
        "metric": "brier_improvement_C_minus_A_exposed_minus_comparator",
        "improvement_delta": effect,
        "bootstrap_ci_low": ci_low,
        "bootstrap_ci_high": ci_high,
        "p_value": p_value,
        "p_value_bh": p_value_bh,
        "n_interaction_dates": int(len(interaction)),
        "n_folds": int(interaction["fold_id"].nunique()) if not interaction.empty else 0,
        "n_exposed_observations": int(group_counts.get(True, 0)),
        "n_comparator_observations": int(group_counts.get(False, 0)),
        "gates": {
            "group_observation_minimum": group_minimum,
            "required_fold_coverage": full_folds,
            "paired_date_minimum": enough_dates,
            "bootstrap_estimable": bool(estimable),
            "positive_effect": positive,
            "ci_lower_bound_positive": ci_positive,
            "adjusted_p_pass": p_pass,
            "named_robustness_alignment": robustness_pass,
        },
        "limitations": [
            "exploratory_only_does_not_replace_v6_primary" if state_mode == "exploratory" else "confirmation_does_not_replace_locked_v6_primary",
            "no_causal_or_investment_advice_claim",
        ],
    }
    return interaction, summary


def load_protocol(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("subgroup protocol must be a JSON object")
    return value
