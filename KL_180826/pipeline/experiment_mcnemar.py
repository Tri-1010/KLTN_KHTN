"""
McNemar significance test: is the Random Forest improvement of Config_C over
Config_A statistically significant at the 1-month time granularity?

McNemar's test compares two classifiers on the SAME test set by looking only at
the cases where they disagree:
    - b = #(A correct, C wrong)
    - c = #(A wrong, C correct)
The null hypothesis is that both models have the same error rate (b == c).
A small p-value means the disagreement is asymmetric, i.e. one model is
genuinely better rather than the gap being random noise.

We use the exact binomial test (recommended when b + c is small) and also report
the chi-square form with continuity correction.

Usage:
    python -m pipeline.experiment_mcnemar
"""

from __future__ import annotations

import sys

for _stream in (sys.stdout, sys.stderr):
    _rc = getattr(_stream, "reconfigure", None)
    if _rc is not None:
        try:
            _rc(encoding="utf-8", errors="replace")
        except Exception:
            pass

import argparse

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score
from statsmodels.stats.contingency_tables import mcnemar

from pipeline.experiment_period import (
    build_labels,
    build_period_keyword_features,
    build_period_news,
    build_period_technical,
    make_period_funcs,
    PRICES_PATH,
    NEWS_PATH,
)
from pipeline.task10_train import build_ml_models, fit_imputer, prepare_features

UNIT = "month"
MODEL_NAME = "Random_Forest"


def _build_monthly_dataset(unit: str = UNIT):
    assign_fn, next_fn = make_period_funcs(unit)
    prices = pd.read_csv(PRICES_PATH, encoding="utf-8")
    news = pd.read_csv(NEWS_PATH, encoding="utf-8")

    tech = build_period_technical(prices, assign_fn)
    news_agg = build_period_news(news, assign_fn)
    kw = build_period_keyword_features(news_agg)
    labels = build_labels(tech, next_fn)

    tech_cols = [
        "return_p", "return_mean_daily", "return_std_daily", "volatility_p",
        "price_range_p", "volume_mean_p", "volume_change_p", "sma20_end",
        "ema20_end", "price_vs_sma20", "rsi_mean_p", "rsi_end_p",
        "macd_hist_mean_p", "bb_position_p", "return_prev_p", "return_2p_ago",
    ]
    merged = tech.merge(labels, on=["ticker", "period_id"], how="inner")
    merged = merged.merge(kw, on=["ticker", "period_id"], how="inner")
    merged = merged.dropna(subset=["label_basic"])
    kw_cols = [c for c in kw.columns if c not in ("ticker", "period_id")]
    return merged, tech_cols, kw_cols


def _period_split(df):
    periods = sorted(df["period_id"].unique())
    n_test = max(1, int(len(periods) * 0.2))
    test_set = set(periods[-n_test:])
    return (
        df[~df["period_id"].isin(test_set)].copy(),
        df[df["period_id"].isin(test_set)].copy(),
    )


def _train_predict(train_df, test_df, cols, y_train, y_test):
    avail = [c for c in cols if c in train_df.columns]
    imp, _ = fit_imputer(train_df, avail)
    X_tr, _ = prepare_features(train_df, avail, imputer=imp)
    X_te, _ = prepare_features(test_df, avail, imputer=imp)
    common = [c for c in X_tr.columns if c in X_te.columns]
    X_tr, X_te = X_tr[common], X_te[common]
    model = build_ml_models(y_train)[MODEL_NAME]
    model.fit(X_tr, y_train)
    return model.predict(X_te)


def main() -> None:
    parser = argparse.ArgumentParser(description="McNemar test at a chosen period unit")
    parser.add_argument(
        "--unit",
        default=UNIT,
        choices=["2week", "month", "2month", "quarter"],
        help="Period granularity to test (default: month).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output report path (default: reports/mcnemar_{unit}_rf.txt).",
    )
    args = parser.parse_args()
    unit = args.unit
    out_path = args.out or f"reports/mcnemar_{unit}_rf.txt"

    merged, tech_cols, kw_cols = _build_monthly_dataset(unit)
    train_df, test_df = _period_split(merged)

    y_train = train_df["label_basic"].astype(int)
    y_test = test_df["label_basic"].astype(int).to_numpy()

    pred_a = _train_predict(train_df, test_df, tech_cols, y_train, y_test)
    pred_c = _train_predict(train_df, test_df, tech_cols + kw_cols, y_train, y_test)

    correct_a = (pred_a == y_test)
    correct_c = (pred_c == y_test)

    ba_a = balanced_accuracy_score(y_test, pred_a)
    ba_c = balanced_accuracy_score(y_test, pred_c)

    # McNemar contingency on correctness
    both_correct = int(np.sum(correct_a & correct_c))
    a_only = int(np.sum(correct_a & ~correct_c))   # A correct, C wrong (b)
    c_only = int(np.sum(~correct_a & correct_c))   # A wrong,  C correct (c)
    both_wrong = int(np.sum(~correct_a & ~correct_c))

    table = [[both_correct, a_only], [c_only, both_wrong]]

    # Exact binomial test (best when discordant count is small)
    res_exact = mcnemar(table, exact=True)
    # Chi-square with continuity correction (large-sample form)
    res_chi2 = mcnemar(table, exact=False, correction=True)

    lines = []
    lines.append("=" * 64)
    lines.append(f"McNemar test — Random Forest, {unit} granularity")
    lines.append("Config_A (technical) vs Config_C (technical + keyword)")
    lines.append("=" * 64)
    lines.append(f"Test samples: {len(y_test)}")
    lines.append(f"Balanced Accuracy — Config_A: {ba_a:.4f}")
    lines.append(f"Balanced Accuracy — Config_C: {ba_c:.4f}")
    lines.append(f"Delta (C - A): {ba_c - ba_a:+.4f}")
    lines.append(f"Raw accuracy  — Config_A: {correct_a.mean():.4f}")
    lines.append(f"Raw accuracy  — Config_C: {correct_c.mean():.4f}")
    lines.append("")
    lines.append("Contingency table (correctness):")
    lines.append(f"  both correct          : {both_correct}")
    lines.append(f"  A correct, C wrong (b): {a_only}")
    lines.append(f"  A wrong,  C correct(c): {c_only}")
    lines.append(f"  both wrong            : {both_wrong}")
    lines.append(f"  discordant (b + c)    : {a_only + c_only}")
    lines.append("")
    lines.append(f"Exact binomial McNemar : statistic={res_exact.statistic:.4f}, "
                 f"p-value={res_exact.pvalue:.4f}")
    lines.append(f"Chi-square (corrected) : statistic={res_chi2.statistic:.4f}, "
                 f"p-value={res_chi2.pvalue:.4f}")
    lines.append("")
    alpha = 0.05
    p = res_exact.pvalue
    if p < alpha:
        verdict = (
            f"p = {p:.4f} < {alpha}: REJECT null. The difference between "
            "Config_C and Config_A is statistically significant."
        )
    else:
        verdict = (
            f"p = {p:.4f} >= {alpha}: FAIL TO REJECT null. The observed "
            "improvement is NOT statistically significant — it is within the "
            "range expected from random variation on this test set."
        )
    lines.append(verdict)
    lines.append("=" * 64)

    report = "\n".join(lines)
    print(report)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report + "\n")


if __name__ == "__main__":
    main()
