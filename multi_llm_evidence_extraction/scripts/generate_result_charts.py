from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import CATEGORICAL_FIELDS, OUTPUT_DIR, REPORT_DIR, ensure_dirs
from analyze_annotation_agreement import cohen_kappa, load_labels

CHART_DIR = REPORT_DIR / "charts"
COLORS = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e34948"]
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"


def style() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": "#c3c2b7", "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.6, "font.family": "DejaVu Sans", "font.size": 9,
    })


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError, UnicodeDecodeError):
        return pd.DataFrame()


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(CHART_DIR / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def agreement_heatmap() -> bool:
    data = load_labels()
    pairs = [("a", "b"), ("a", "c"), ("b", "c")]
    if any(not data.get(annotator) for pair in pairs for annotator in pair):
        return False
    values = np.array([
        [np.nan if (value := cohen_kappa(data[a], data[b], field)) is None else value for a, b in pairs]
        for field in CATEGORICAL_FIELDS
    ])
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    image = ax.imshow(values, vmin=0, vmax=1, cmap="Blues")
    ax.set_xticks(range(len(pairs)), [f"{a.upper()}–{b.upper()}" for a, b in pairs])
    ax.set_yticks(range(len(CATEGORICAL_FIELDS)), CATEGORICAL_FIELDS)
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            label = "NA" if np.isnan(values[row, col]) else f"{values[row, col]:.2f}"
            ax.text(col, row, label, ha="center", va="center", color=INK)
    ax.set_title("Cohen's kappa by annotation field")
    fig.colorbar(image, ax=ax, label="Kappa")
    save(fig, "agreement_heatmap.png")
    return True


def rule_confusion() -> bool:
    frame = read_csv(OUTPUT_DIR / "rule_vs_semantic_confusion_matrices.csv")
    required = {"field", "actual", "predicted_rule", "count"}
    if frame.empty or not required.issubset(frame.columns):
        return False
    fields = list(frame["field"].dropna().unique())[:4]
    if not fields:
        return False
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax in axes.flat:
        ax.set_visible(False)
    for ax, field in zip(axes.flat, fields):
        ax.set_visible(True)
        sub = frame[frame["field"].eq(field)]
        matrix = sub.pivot(index="actual", columns="predicted_rule", values="count").fillna(0)
        image = ax.imshow(matrix, cmap="Blues")
        ax.set_xticks(range(len(matrix.columns)), matrix.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(matrix.index)), matrix.index)
        ax.set_title(field.replace("consensus_", ""))
        ax.set_xlabel("Rule label")
        ax.set_ylabel("Semantic consensus")
        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                value = int(matrix.iloc[row, col])
                if value:
                    ax.text(col, row, str(value), ha="center", va="center", color=INK)
        fig.colorbar(image, ax=ax, fraction=0.046)
    save(fig, "rule_vs_semantic_confusion.png")
    return True


def event_window_chart() -> bool:
    frame = read_csv(OUTPUT_DIR / "event_window_outcomes.csv")
    required = {"direction", "window", "market_adjusted_return"}
    if frame.empty or not required.issubset(frame.columns):
        return False
    order = ["T+1", "T+5", "T+20", "T+60"]
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    plotted = 0
    for color, marker, direction in zip(COLORS, ["o", "s", "^"], ["support", "risk", "neutral"]):
        values = pd.to_numeric(frame.loc[frame["direction"].eq(direction), "market_adjusted_return"], errors="coerce")
        sub = frame.loc[values.index].assign(_value=values).groupby("window")["_value"].agg(["mean", "sem"]).reindex(order)
        if sub["mean"].notna().any():
            ax.errorbar(order, sub["mean"], yerr=1.96 * sub["sem"].fillna(0), marker=marker, linewidth=2, markersize=7, capsize=3, label=direction, color=color)
            plotted += 1
    if not plotted:
        plt.close(fig)
        return False
    ax.axhline(0, color="#c3c2b7", linewidth=1)
    ax.set_title("VNINDEX-adjusted return by semantic direction")
    ax.set_ylabel("Mean adjusted return (95% normal CI)")
    if plotted >= 2:
        ax.legend(frameon=False)
    save(fig, "event_window_adjusted_returns.png")
    return True


def ml_comparison() -> bool:
    frame = read_csv(OUTPUT_DIR / "ml_predictions_outperform.csv")
    required = {"config", "model", "fold_id", "pred_label", "label_outperform_T20"}
    if frame.empty or not required.issubset(frame.columns):
        return False
    work = frame.assign(_correct=(frame["pred_label"] == frame["label_outperform_T20"]).astype(float))
    folds = work.groupby(["config", "model", "fold_id"], as_index=False)["_correct"].mean()
    baseline = folds[folds["config"].eq("A_technical")][["model", "fold_id", "_correct"]].rename(columns={"_correct": "_baseline"})
    deltas = folds.merge(baseline, on=["model", "fold_id"], how="inner")
    deltas = deltas[~deltas["config"].eq("A_technical")].assign(delta=lambda value: value["_correct"] - value["_baseline"])
    if deltas.empty:
        return False
    summary = deltas.groupby(["config", "model"], as_index=False)["delta"].agg(["mean", "std"]).reset_index()
    summary["label"] = summary["config"] + "\n" + summary["model"]
    config_colors = {config: COLORS[index] for index, config in enumerate(sorted(summary["config"].unique()))}
    fig, ax = plt.subplots(figsize=(9, 4.8))
    positions = range(len(summary))
    ax.bar(positions, summary["mean"], yerr=summary["std"].fillna(0), color=[config_colors[value] for value in summary["config"]], capsize=3)
    ax.axhline(0, color="#c3c2b7", linewidth=1)
    ax.set_xticks(positions, summary["label"], rotation=30, ha="right")
    ax.set_ylabel("Fold accuracy delta vs technical-only")
    ax.set_title("Purged walk-forward ML delta by matched fold")
    save(fig, "ml_walk_forward_comparison.png")
    return True


def topk_equity() -> bool:
    frame = read_csv(OUTPUT_DIR / "topk_portfolio_simulation.csv")
    required = {"config", "model", "entry_date", "exit_date", "top_k", "strategy", "net_return", "net_excess_return"}
    if frame.empty or not required.issubset(frame.columns):
        return False
    subset = frame[(frame["top_k"] == 5) & frame["strategy"].isin(["model_topk", "equal_weight_universe"])].copy()
    if subset.empty:
        return False
    ranking = subset[subset["strategy"].eq("model_topk")].groupby(["config", "model"])["net_excess_return"].mean().nlargest(3).index
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    plotted = 0
    for color, keys in zip(COLORS, ranking):
        group = subset[(subset["config"] == keys[0]) & (subset["model"] == keys[1]) & subset["strategy"].eq("model_topk")].sort_values("entry_date")
        if group.empty:
            continue
        curve = (1 + pd.to_numeric(group["net_return"], errors="coerce").fillna(0)).cumprod() - 1
        ax.plot(pd.to_datetime(group["entry_date"]), curve, linewidth=2, label=f"{keys[0]} / {keys[1]}", color=color)
        plotted += 1
    benchmark = subset[subset["strategy"].eq("equal_weight_universe")].sort_values("entry_date").drop_duplicates("entry_date")
    if not benchmark.empty:
        curve = (1 + pd.to_numeric(benchmark["net_return"], errors="coerce").fillna(0)).cumprod() - 1
        ax.plot(pd.to_datetime(benchmark["entry_date"]), curve, linewidth=2, linestyle="--", label="equal-weight universe", color=COLORS[3])
        plotted += 1
    if not plotted:
        plt.close(fig)
        return False
    ax.axhline(0, color="#c3c2b7", linewidth=1)
    ax.set_title("Top-5 OOS non-overlapping cumulative net return")
    ax.set_ylabel("Cumulative net return")
    if plotted >= 2:
        ax.legend(frameon=False, fontsize=8)
    save(fig, "topk_oos_equity_curves.png")
    return True


def main() -> int:
    ensure_dirs()
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    style()
    results = {
        "agreement": agreement_heatmap(),
        "rule_confusion": rule_confusion(),
        "event_window": event_window_chart(),
        "ml_delta": ml_comparison(),
        "topk_equity": topk_equity(),
    }
    print(f"saved charts to {CHART_DIR}; generated={sum(results.values())}/{len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
