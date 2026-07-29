"""Tính kích thước tập test (quý >= cutoff) cho từng phân khúc B3.

Mục đích: định lượng statistical power của mỗi phân khúc trong báo cáo B3, bằng
cách đếm số mẫu (ticker × quarter) rơi vào tập test theo cùng quy tắc chia thời
gian của pipeline (time-series split tại Train_Cutoff = 2025Q1).

Chạy:  python -m experiments.compute_segment_testsize
"""

from __future__ import annotations

import pandas as pd

from experiments.common.segments import assign_segments

MASTER_PATH = "data/aggregated/master_with_labels.csv"
CUTOFF = "2025Q1"


def _quarter_key(qid: str) -> tuple[int, int]:
    year, q = qid.split("Q")
    return int(year), int(q)


def compute_segment_test_sizes(
    master_path: str = MASTER_PATH,
    cutoff: str = CUTOFF,
) -> pd.DataFrame:
    """Trả về DataFrame: số mẫu train/test theo từng phân khúc (sector & cap_group)."""
    df = pd.read_csv(master_path)

    # Chỉ giữ mẫu có nhãn hợp lệ (đúng như pipeline huấn luyện dùng label_basic).
    df = df[df["label_basic"].notna()].copy()

    segments = assign_segments()
    df["sector"] = df["ticker"].map(lambda t: segments[t].sector if t in segments else None)
    df["cap_group"] = df["ticker"].map(lambda t: segments[t].cap_group if t in segments else None)
    df = df[df["sector"].notna()].copy()

    cutoff_key = _quarter_key(cutoff)
    df["is_test"] = df["quarter_id"].map(lambda q: _quarter_key(q) >= cutoff_key)

    rows = []
    for seg_type, col in (("sector", "sector"), ("cap_group", "cap_group")):
        for seg_name, grp in df.groupby(col):
            n_total = len(grp)
            n_test = int(grp["is_test"].sum())
            n_train = n_total - n_test
            rows.append(
                {
                    "segment_type": seg_type,
                    "segment_name": seg_name,
                    "n_tickers": grp["ticker"].nunique(),
                    "n_total": n_total,
                    "n_train": n_train,
                    "n_test": n_test,
                    "test_pct": round(100 * n_test / n_total, 1) if n_total else 0.0,
                }
            )

    out = pd.DataFrame(rows).sort_values(["segment_type", "n_test"], ascending=[True, False])
    return out.reset_index(drop=True)


if __name__ == "__main__":
    result = compute_segment_test_sizes()
    out_path = "reports/segment_test_sizes.csv"
    result.to_csv(out_path, index=False)
    print(result.to_string(index=False))
    print(f"\nĐã ghi: {out_path}")
