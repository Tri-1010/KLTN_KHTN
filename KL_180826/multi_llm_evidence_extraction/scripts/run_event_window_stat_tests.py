from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, REPORT_DIR, ensure_dirs, markdown_table

AUDIT = OUTPUT_DIR / "event_window_outcomes.csv"
OUT = OUTPUT_DIR / "event_window_stat_tests.csv"
REPORT = REPORT_DIR / "event_window_stat_tests_report.md"
BOOTSTRAP_SEED = 42
BOOTSTRAP_SAMPLES = 2000


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def mann_whitney_u(x: list[float], y: list[float]) -> tuple[float, float, float, float]:
    n1, n2 = len(x), len(y)
    values = np.asarray(x + y, dtype=float)
    ranks = pd.Series(values).rank(method="average").to_numpy()
    rank_sum = float(ranks[:n1].sum())
    u1 = rank_sum - n1 * (n1 + 1) / 2.0
    total = n1 + n2
    tie_counts = pd.Series(values).value_counts().to_numpy(dtype=float)
    tie_term = float(np.sum(tie_counts**3 - tie_counts))
    variance = n1 * n2 / 12.0 * ((total + 1) - tie_term / (total * (total - 1))) if total > 1 else 0.0
    if variance <= 0:
        return u1, float("nan"), float("nan"), 0.0
    mean_u = n1 * n2 / 2.0
    continuity = 0.5 * np.sign(u1 - mean_u)
    z = (u1 - mean_u - continuity) / math.sqrt(variance)
    p = 2 * (1 - normal_cdf(abs(z)))
    return u1, p, z, variance


def cliffs_delta(x: list[float], y: list[float]) -> float:
    if not x or not y:
        return float("nan")
    first = np.asarray(x)[:, None]
    second = np.asarray(y)[None, :]
    return float((np.sum(first > second) - np.sum(first < second)) / (len(x) * len(y)))


def bootstrap_ci(x: list[float], y: list[float], samples: int = BOOTSTRAP_SAMPLES, seed: int = BOOTSTRAP_SEED) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    x_array, y_array = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    differences, deltas = [], []
    for _ in range(samples):
        xs = rng.choice(x_array, size=len(x_array), replace=True)
        ys = rng.choice(y_array, size=len(y_array), replace=True)
        differences.append(float(xs.mean() - ys.mean()))
        deltas.append(cliffs_delta(xs.tolist(), ys.tolist()))
    return {
        "diff_ci_low": float(np.percentile(differences, 2.5)),
        "diff_ci_high": float(np.percentile(differences, 97.5)),
        "cliffs_delta_ci_low": float(np.percentile(deltas, 2.5)),
        "cliffs_delta_ci_high": float(np.percentile(deltas, 97.5)),
    }


def benjamini_hochberg(values: list[float]) -> list[float]:
    size = len(values)
    if not size:
        return []
    order = np.argsort(values)
    adjusted = np.empty(size, dtype=float)
    running = 1.0
    for rank_index in range(size - 1, -1, -1):
        original_index = int(order[rank_index])
        rank = rank_index + 1
        running = min(running, values[original_index] * size / rank)
        adjusted[original_index] = min(1.0, running)
    return adjusted.tolist()


def non_overlapping_events(frame: pd.DataFrame, horizon: int) -> pd.DataFrame:
    rows = []
    for _, group in frame.sort_values("effective_date").groupby("ticker", sort=False):
        next_allowed = None
        for _, row in group.iterrows():
            effective = pd.to_datetime(row["effective_date"], errors="coerce")
            end = pd.to_datetime(row.get("window_end_date"), errors="coerce")
            if pd.isna(effective) or pd.isna(end):
                continue
            if next_allowed is None or effective > next_allowed:
                rows.append(row)
                next_allowed = end
    return pd.DataFrame(rows) if rows else frame.iloc[0:0].copy()


def compare(df: pd.DataFrame, window: str, group_a: str, values_a: set[str], group_b: str, values_b: set[str], field: str = "market_adjusted_return") -> dict[str, object] | None:
    sub = df[df["window"].eq(window)].copy()
    horizon = int(window.split("+")[-1])
    sub = non_overlapping_events(sub, horizon)
    first = pd.to_numeric(sub[sub[group_a].isin(values_a)][field], errors="coerce").dropna().tolist()
    second = pd.to_numeric(sub[sub[group_b].isin(values_b)][field], errors="coerce").dropna().tolist()
    if len(first) < 3 or len(second) < 3:
        return None
    u, p, z, variance = mann_whitney_u(first, second)
    ci = bootstrap_ci(first, second)
    difference = float(np.mean(first) - np.mean(second))
    return {
        "window": window,
        "comparison": f"{group_a}={'+'.join(sorted(values_a))} vs {group_b}={'+'.join(sorted(values_b))}",
        "metric": field, "n_a": len(first), "n_b": len(second),
        "mean_a": float(np.mean(first)), "mean_b": float(np.mean(second)), "diff_mean": difference,
        "mann_whitney_u": u, "z_score": z, "tie_corrected_variance": variance,
        "p_value_raw": p, "cliffs_delta": cliffs_delta(first, second), **ci,
    }


def main() -> int:
    ensure_dirs()
    lines = ["# Event-window statistical tests", "", "Primary metric: VNINDEX-adjusted return. Non-overlapping event sample, tie-corrected Mann–Whitney, BH-FDR, deterministic bootstrap CI. Exploratory only; no causal claim.", ""]
    if not AUDIT.exists():
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        lines.append("Event-window outcomes unavailable.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0
    try:
        df = pd.read_csv(AUDIT, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()
    rows = []
    if not df.empty and "market_adjusted_return" in df:
        for window in ["T+1", "T+5", "T+20", "T+60"]:
            for item in [
                compare(df, window, "direction", {"support"}, "direction", {"risk"}),
                compare(df, window, "materiality", {"high", "medium"}, "materiality", {"low"}),
            ]:
                if item:
                    rows.append(item)
    out = pd.DataFrame(rows)
    if not out.empty:
        out["p_value_bh"] = benjamini_hochberg(out["p_value_raw"].fillna(1.0).tolist())
        out["reject_fdr_05"] = out["p_value_bh"] <= 0.05
        out["robust_positive_effect"] = out["reject_fdr_05"] & (out["diff_ci_low"] > 0)
        out["robust_negative_effect"] = out["reject_fdr_05"] & (out["diff_ci_high"] < 0)
        out["correction_method"] = "Benjamini-Hochberg"
        out["artifact_schema_version"] = "event_window_tests_v3"
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    lines += ["## Results", "", markdown_table(out.round(4)) if not out.empty else "Insufficient data for tests.", ""]
    if not out.empty and not (out["robust_positive_effect"] | out["robust_negative_effect"]).any():
        lines.append("No comparison survives BH-FDR 5% with a bootstrap CI excluding zero. Observed raw differences are not robust evidence.")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {OUT} rows={len(out)}")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
