from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "thesis_submission"
COLORS = {"baseline": "#2563EB", "comparison": "#C2410C", "audit": "#15803D"}
TEXT = "#0F172A"
MUTED = "#475569"
GRID = "#CBD5E1"


plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelcolor": TEXT,
    "axes.titlecolor": TEXT,
    "xtick.color": MUTED,
    "ytick.color": TEXT,
})


def generate_figures(run_id: str, bundle: Path = BUNDLE) -> None:
    summary_path = bundle / "canonical_results" / "canonical_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError("build submission before figures")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("run_id") != run_id or summary.get("run_tier") != "canonical":
        raise ValueError("bundled summary does not match requested canonical run")
    primary = summary["primary"]
    figure_dir = BUNDLE / "artifacts" / "figures"
    data_dir = BUNDLE / "artifacts" / "figure_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    primary_data = pd.DataFrame([{
        "comparison": "Semantic − Keyword",
        "delta": primary["improvement_delta"],
        "ci_low": primary["bootstrap_ci_low"],
        "ci_high": primary["bootstrap_ci_high"],
        "gate_pass": primary["gate_pass"],
    }])
    primary_data.to_csv(data_dir / "primary_delta_ci.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    row = primary_data.iloc[0]
    delta = float(row["delta"])
    low = float(row["ci_low"])
    high = float(row["ci_high"])
    ax.errorbar(
        [delta], [0], xerr=[[delta - low], [high - delta]], fmt="o",
        color=COLORS["comparison"], ecolor=COLORS["comparison"],
        markeredgecolor="white", markeredgewidth=1.5,
        markersize=10, linewidth=2.2, capsize=6,
    )
    ax.axvline(0, color=MUTED, linewidth=1.2, linestyle="--")
    ax.set_xlim(min(-0.065, low - 0.005), max(0.03, high + 0.005))
    ax.set_ylim(-0.55, 0.7)
    ax.set_yticks([0], ["Semantic − Keyword"])
    ax.set_xlabel("Chênh lệch Balanced Accuracy")
    ax.set_title("So sánh primary trên cùng mẫu", loc="left", fontweight="semibold", pad=16)
    ax.text(
        0, 1.015,
        f"{primary['model']} · T+20 · {primary['n_paired_dates']} ngày ghép cặp · "
        f"{primary['n_folds']} folds",
        transform=ax.transAxes, color=MUTED, fontsize=9, va="bottom",
    )
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.text(
        delta, 0.28,
        f"Δ = {delta:.4f}\n95% CI [{low:.4f}; {high:.4f}]",
        ha="center", va="bottom", color=TEXT, fontsize=9,
    )
    ci_status = "CI chứa 0" if low <= 0 <= high else "CI không chứa 0"
    gate_status = "primary gate pass" if primary["gate_pass"] else "primary gate không pass"
    ax.text(1, -0.3, f"{ci_status} · {gate_status}",
            transform=ax.transAxes, ha="right", color=MUTED, fontsize=9)
    fig.subplots_adjust(left=0.24, right=0.97, top=0.78, bottom=0.25)
    fig.savefig(figure_dir / "primary_delta_ci.png", dpi=220, facecolor="white")
    plt.close(fig)

    attrition_labels = {
        "sampled_articles": "Bài được lấy mẫu",
        "joined_articles": "Bài ghép consensus",
        "eligible_articles": "Bài đủ điều kiện",
        "mapped_eligible_articles": "Bài mapping thành công",
        "analytic_spine_articles": "Bài trong analytic spine",
        "panel_target_available_rows": "Panel rows có target",
        "panel_eligible_rows": "Panel rows đủ điều kiện",
    }
    attrition = pd.DataFrame([
        {"stage": key, "label": attrition_labels.get(key, key.replace("_", " ").title()), "count": value}
        for key, value in summary["attrition"].items()
    ])
    attrition["scope"] = attrition["stage"].map(
        lambda stage: "article" if stage.endswith("articles") else "panel"
    )
    attrition["retention_from_previous"] = attrition.groupby("scope")["count"].transform(
        lambda counts: counts / counts.shift(1)
    )
    attrition.to_csv(data_dir / "canonical_attrition.csv", index=False, encoding="utf-8-sig")
    article_attrition = attrition[attrition["scope"] == "article"]
    panel_attrition = attrition[attrition["scope"] == "panel"]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.1))
    for ax, data, title, color in (
        (axes[0], article_attrition, "Article spine", COLORS["baseline"]),
        (axes[1], panel_attrition, "Observation panel", COLORS["audit"]),
    ):
        bars = ax.barh(data["label"], data["count"], color=color, height=0.54)
        labels = []
        for value, retention in zip(data["count"], data["retention_from_previous"]):
            count_label = f"{value:,.0f}".replace(",", ".")
            labels.append(count_label if pd.isna(retention) else f"{count_label}  ({retention:.1%})")
        ax.bar_label(bars, labels=labels, padding=5, color=TEXT, fontsize=9)
        ax.set_xlim(0, data["count"].max() * 1.32)
        ax.invert_yaxis()
        ax.set_xlabel("Số quan sát")
        ax.set_title(title, loc="left", fontweight="semibold", pad=10)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
    fig.suptitle("Suy giảm mẫu canonical", x=0.06, ha="left", fontsize=13, fontweight="semibold")
    fig.text(0.06, 0.895, "Nhãn trong ngoặc: tỷ lệ giữ lại so với bước trước trong cùng scope",
             color=MUTED, fontsize=9)
    fig.subplots_adjust(left=0.2, right=0.97, top=0.8, bottom=0.16, wspace=0.62)
    fig.savefig(figure_dir / "canonical_attrition.png", dpi=220, facecolor="white")
    plt.close(fig)



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="canonical_150_v7")
    args = parser.parse_args()
    generate_figures(args.run_id)
    print(json.dumps({"status": "generated", "run_id": args.run_id, "figures": 2}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
