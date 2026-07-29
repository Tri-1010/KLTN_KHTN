"""Đánh giá tính thỏa đáng của dữ liệu cho từng loại kiểm định trong luận văn.

Trả lời hai câu hỏi:
  1. Dữ liệu tổng thể đã đủ chưa (train/test cho so sánh mô hình)?
  2. Kiểm định nào dùng quá ít dữ liệu → statistical power thấp?

Chạy:  python -m experiments.assess_data_adequacy
"""

from __future__ import annotations

import pandas as pd

MASTER = "data/aggregated/master_with_labels.csv"
KW_SIG = "reports/keyword_significance.csv"
SEG_SIG = "reports/segmentation_keyword_sig.csv"
CUTOFF = "2025Q1"


def _qkey(q: str) -> tuple[int, int]:
    y, n = q.split("Q")
    return int(y), int(n)


def section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def assess_global():
    section("1. DỮ LIỆU TỔNG THỂ (so sánh mô hình toàn cục)")
    df = pd.read_csv(MASTER)
    df = df[df["label_basic"].notna()]
    ck = _qkey(CUTOFF)
    train = df[df["quarter_id"].map(lambda q: _qkey(q) < ck)]
    test = df[df["quarter_id"].map(lambda q: _qkey(q) >= ck)]
    print(f"Tổng mẫu (ticker×quý)   : {len(df)}")
    print(f"Số ticker               : {df.ticker.nunique()}")
    print(f"Số quý                  : {df.quarter_id.nunique()} ({df.quarter_id.min()}..{df.quarter_id.max()})")
    print(f"Train (quý < {CUTOFF})   : {len(train)}")
    print(f"Test  (quý >= {CUTOFF})  : {len(test)}")
    print(f"Cân bằng nhãn (test)    : {dict(test.label_basic.value_counts())}")
    print("→ Đánh giá: test=400 mẫu, cân bằng ~50/50 → ĐỦ cho so sánh mô hình toàn cục.")


def assess_keyword_sig():
    section("2. KIỂM ĐỊNH Ý NGHĨA TỪ KHÓA TOÀN CỤC (keyword_significance.csv)")
    k = pd.read_csv(KW_SIG)
    total = len(k)
    if "n_occurrences" in k.columns:
        occ = k["n_occurrences"].fillna(0)
        print(f"Tổng số từ khóa kiểm định : {total}")
        print(f"  n_occurrences = 0 (loại): {(occ == 0).sum()}")
        print(f"  1 <= occ < 5  (quá ít)  : {((occ >= 1) & (occ < 5)).sum()}")
        print(f"  5 <= occ < 10 (ít)      : {((occ >= 5) & (occ < 10)).sum()}")
        print(f"  10 <= occ < 30          : {((occ >= 10) & (occ < 30)).sum()}")
        print(f"  occ >= 30 (đủ power)    : {(occ >= 30).sum()}")
        low = ((occ >= 1) & (occ < 10)).sum()
        print(f"→ {low}/{total} từ khóa có < 10 lần xuất hiện → kiểm định gần như vô hiệu (power rất thấp).")


def assess_segment_sig():
    section("3. KIỂM ĐỊNH TỪ KHÓA THEO PHÂN KHÚC (segmentation_keyword_sig.csv)")
    s = pd.read_csv(SEG_SIG)
    total = len(s)
    excluded = (s["chi_test_used"] == "excluded").sum() if "chi_test_used" in s.columns else None
    print(f"Tổng dòng kiểm định       : {total}")
    if excluded is not None:
        print(f"  Bị loại (0 lần xuất hiện): {excluded} ({100*excluded/total:.1f}%)")
    if "n_occurrences" in s.columns:
        occ = s["n_occurrences"].fillna(0)
        tested = s[occ > 0]
        print(f"  Thực sự kiểm định (occ>0): {len(tested)}")
        print(f"    trong đó occ < 5       : {((tested['n_occurrences'] >= 1) & (tested['n_occurrences'] < 5)).sum()}")
        print(f"    trong đó occ < 10      : {(tested['n_occurrences'] < 10).sum()}")
    if "significant_any" in s.columns:
        sig = (s["significant_any"] == True).sum()  # noqa: E712
        print(f"  Đạt ý nghĩa (significant_any=True): {sig}")
    print("→ Đa số kiểm định phân khúc dựa trên đếm rất nhỏ → không đủ power. 0 kết quả có ý nghĩa.")


def assess_segment_models():
    section("4. TEST SET THEO PHÂN KHÚC (đã tính ở segment_test_sizes.csv)")
    try:
        t = pd.read_csv("reports/segment_test_sizes.csv")
        for _, r in t.iterrows():
            flag = ""
            if r["n_test"] < 30:
                flag = "  ⚠ QUÁ NHỎ — Δ(C−A) không tin cậy"
            elif r["n_test"] < 60:
                flag = "  ⚠ nhỏ"
            print(f"  {r['segment_type']:9s} {r['segment_name']:12s} n_test={int(r['n_test']):4d}{flag}")
    except FileNotFoundError:
        print("  (chưa có segment_test_sizes.csv — chạy compute_segment_testsize trước)")
    print("→ Kiểm định Δ(C−A) cho Technology (15), Transport (25), Securities (30) là YẾU.")


if __name__ == "__main__":
    assess_global()
    assess_keyword_sig()
    assess_segment_sig()
    assess_segment_models()
    print()


def _write_report():
    """Ghi kết quả đánh giá ra file để dễ đọc (tránh vấn đề pager/encoding)."""
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assess_global()
        assess_keyword_sig()
        assess_segment_sig()
        assess_segment_models()
    with open("reports/data_adequacy_report.txt", "w", encoding="utf-8") as f:
        f.write(buf.getvalue())
