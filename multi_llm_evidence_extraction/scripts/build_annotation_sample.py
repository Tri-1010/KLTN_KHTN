from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import DATA_DIR, REPORT_DIR, ROOT, article_text, content_hash, ensure_dirs, markdown_table, sha256_file, stable_news_id

INPUT_CANDIDATES = [
    ROOT / "data" / "news" / "enriched" / "all_news_enriched.csv",
    ROOT / "data" / "news" / "processed" / "all_news_processed.csv",
    ROOT / "data" / "news" / "matched" / "all_news_matched.csv",
]
OUTPUT = DATA_DIR / "sample_news_for_annotation.csv"
SUMMARY = REPORT_DIR / "sample_selection_summary.md"
KEYWORD_GROUPS = ROOT / "config" / "keywords_by_group.json"

GROUP_TO_BUCKET = {
    "A": "earnings_business_result",
    "B": "dividend_capital",
    "C": "debt_legal_governance_risk",
    "D": "project_business_expansion",
    "E": "debt_legal_governance_risk",
    "F": "generic_company_announcement",
}
BUCKET_QUOTAS = {
    "earnings_business_result": 25,
    "dividend_capital": 20,
    "debt_legal_governance_risk": 25,
    "project_business_expansion": 20,
    "market_sector_macro": 25,
    "generic_company_announcement": 20,
    "noisy_low_confidence": 15,
}
MARKET_TERMS = ["vn-index", "vnindex", "thị trường", "vĩ mô", "lãi suất", "ngành", "cổ phiếu", "chứng khoán"]


def pick_input(path: str | None) -> Path:
    if path:
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        if not p.exists():
            raise FileNotFoundError(p)
        return p
    for p in INPUT_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError("No news input found")


def load_keyword_groups() -> dict[str, dict[str, list[str]]]:
    if not KEYWORD_GROUPS.exists():
        return {}
    raw = json.loads(KEYWORD_GROUPS.read_text(encoding="utf-8"))
    out: dict[str, dict[str, list[str]]] = {}
    for gid, data in raw.items():
        if not isinstance(data, dict):
            continue
        out[gid] = {}
        for direction in ("positive", "negative", "neutral"):
            vals = data.get(direction) or []
            out[gid][direction] = [str(v).lower() for v in vals]
    return out


def classify_bucket(row: pd.Series, groups: dict[str, dict[str, list[str]]]) -> str:
    text = f"{row.get('title', '')} {row.get('description', '')} {row.get('article_summary', '')} {row.get('full_text', '')}".lower()
    match_conf = str(row.get("match_confidence", "")).lower()
    ticker = str(row.get("ticker", "")).upper()
    if ticker in {"", "UNKNOWN", "NAN"} or match_conf in {"none", "low"}:
        return "noisy_low_confidence"
    if any(term in text for term in MARKET_TERMS):
        if not any(str(row.get("ticker", "")).lower() in text for _ in [0]):
            return "market_sector_macro"
    hits: Counter[str] = Counter()
    for gid, directions in groups.items():
        for kws in directions.values():
            if any(kw and kw in text for kw in kws):
                hits[GROUP_TO_BUCKET.get(gid, "generic_company_announcement")] += 1
    if hits:
        return hits.most_common(1)[0][0]
    if any(term in text for term in MARKET_TERMS):
        return "market_sector_macro"
    return "generic_company_announcement"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" not in df.columns and "published_at" in df.columns:
        df["date"] = df["published_at"]
    if "date" not in df.columns and "published_at_detail" in df.columns:
        df["date"] = df["published_at_detail"]
    for col in ["ticker", "date", "source", "title", "description", "full_text", "article_summary", "key_facts_json", "url", "match_confidence", "content_hash"]:
        if col not in df.columns:
            df[col] = ""
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["date"] = df["date"].fillna("")
    return df


def dedup(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    before = len(df)
    if "url" in df:
        url_text = df["url"].fillna("").astype(str).str.strip()
        df_url = df[url_text.ne("")].drop_duplicates(subset=["url"], keep="first")
        df_no_url = df[url_text.eq("")]
        df = pd.concat([df_url, df_no_url], ignore_index=True)
    after_url = len(df)
    if "content_hash" in df.columns:
        hash_text = df["content_hash"].fillna("").astype(str).str.strip()
        non_empty = hash_text.ne("") & hash_text.str.lower().ne("nan")
        df_hash = df[non_empty].drop_duplicates(subset=["content_hash"], keep="first")
        df_no_hash = df[~non_empty]
        df = pd.concat([df_hash, df_no_hash], ignore_index=True)
    after_hash = len(df)
    title_key = df["title"].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    df = df.assign(_title_key=title_key).drop_duplicates(subset=["ticker", "date", "_title_key"], keep="first").drop(columns=["_title_key"])
    return df, {"before": before, "after_url": after_url, "after_hash": after_hash, "after_title": len(df)}


def build_sample(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    groups = load_keyword_groups()
    df = df.copy()
    df["news_id"] = df.apply(lambda r: stable_news_id(dict(r)), axis=1)
    df["content_hash"] = df.apply(lambda r: content_hash(dict(r)), axis=1)
    df["article_text_chars"] = df.apply(lambda r: len(article_text(dict(r))), axis=1)
    df["length_bucket"] = pd.cut(df["article_text_chars"], bins=[-1, 300, 1500, 10**9], labels=["short", "medium", "long"]).astype(str)
    df["sample_bucket"] = df.apply(lambda r: classify_bucket(r, groups), axis=1)
    selected = []
    used: set[str] = set()
    for bucket, quota in BUCKET_QUOTAS.items():
        part = df[df["sample_bucket"] == bucket]
        if part.empty:
            continue
        take = min(quota, len(part))
        sampled = part.sample(n=take, random_state=seed) if len(part) > take else part
        selected.append(sampled)
        used.update(sampled["news_id"].tolist())
    out = pd.concat(selected, ignore_index=True) if selected else pd.DataFrame(columns=df.columns)
    if len(out) < n:
        rest = df[~df["news_id"].isin(used)]
        take = min(n - len(out), len(rest))
        if take > 0:
            out = pd.concat([out, rest.sample(n=take, random_state=seed)], ignore_index=True)
    if len(out) > n:
        out = out.sample(n=n, random_state=seed).reset_index(drop=True)
    return out.sort_values(["sample_bucket", "ticker", "date", "news_id"]).reset_index(drop=True)


def write_summary(path: Path, input_path: Path, df: pd.DataFrame, sample: pd.DataFrame, counts: dict[str, int]) -> None:
    lines = [
        "# Annotation sample selection summary",
        "",
        f"- Input: `{input_path}`",
        f"- Input SHA256: `{sha256_file(input_path)}`",
        f"- Rows before dedup: {counts['before']}",
        f"- Rows after URL dedup: {counts['after_url']}",
        f"- Rows after content hash dedup: {counts['after_hash']}",
        f"- Rows after title dedup: {counts['after_title']}",
        f"- Output rows: {len(sample)}",
        f"- Output: `{OUTPUT}`",
        "",
        "## Bucket counts",
        "",
        markdown_table(sample["sample_bucket"].value_counts(dropna=False)),
        "",
        "## Source counts",
        "",
        markdown_table(sample["source"].value_counts(dropna=False).head(20)),
        "",
        "## Match confidence counts",
        "",
        markdown_table(sample["match_confidence"].value_counts(dropna=False)),
        "",
        "## Missing field counts in sample",
        "",
    ]
    miss = {c: int(sample[c].astype(str).str.strip().eq("").sum()) for c in ["ticker", "date", "source", "title", "description", "full_text", "url", "match_confidence"] if c in sample}
    lines.append(markdown_table(pd.Series(miss)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build stratified semantic annotation sample.")
    parser.add_argument("--input", default=None)
    parser.add_argument("--n", type=int, default=150)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    ensure_dirs()
    input_path = pick_input(args.input)
    df = pd.read_csv(input_path, encoding="utf-8")
    df = normalize_columns(df)
    df = df[df["ticker"].ne("") & df["title"].astype(str).str.strip().ne("")].copy()
    deduped, counts = dedup(df)
    sample = build_sample(deduped, args.n, args.seed)
    keep = ["news_id", "ticker", "date", "source", "title", "description", "full_text", "article_summary", "key_facts_json", "url", "match_confidence", "content_hash", "article_text_chars", "length_bucket", "sample_bucket"]
    for col in keep:
        if col not in sample.columns:
            sample[col] = ""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sample[keep].to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    write_summary(SUMMARY, input_path, deduped, sample, counts)
    print(f"saved {OUTPUT} rows={len(sample)}")
    print(f"saved {SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
