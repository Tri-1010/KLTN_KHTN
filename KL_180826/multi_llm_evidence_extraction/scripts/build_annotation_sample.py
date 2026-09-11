from __future__ import annotations

import argparse
import hashlib
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


def build_sample(
    df: pd.DataFrame,
    n: int,
    seed: int,
    base_sample: pd.DataFrame | None = None,
    sample_id: str = "sample150_canonical",
) -> pd.DataFrame:
    forbidden = {"label_outperform_T20", "excess_return_T20", "stock_return_T20", "VNINDEX_return_T20", "target_exit_date", "future_return", "outcome"}
    leaked = forbidden & set(df.columns)
    if leaked:
        raise ValueError(f"sampler input contains future/outcome fields: {sorted(leaked)}")
    groups = load_keyword_groups()
    df = df.copy()
    generated_ids = df.apply(lambda r: stable_news_id(dict(r)), axis=1)
    if "news_id" in df.columns:
        existing_ids = df["news_id"].fillna("").astype(str).str.strip()
        df["news_id"] = existing_ids.where(existing_ids.ne(""), generated_ids)
    else:
        df["news_id"] = generated_ids
    df["content_hash"] = df.apply(lambda r: content_hash(dict(r)), axis=1)
    df["article_text_chars"] = df.apply(lambda r: len(article_text(dict(r))), axis=1)
    df["length_bucket"] = pd.cut(df["article_text_chars"], bins=[-1, 300, 1500, 10**9], labels=["short", "medium", "long"]).astype(str)
    df["sample_bucket"] = df.apply(lambda r: classify_bucket(r, groups), axis=1)
    if base_sample is None and sample_id == "sample150_canonical":
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
    df["calendar_period"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("Q").astype(str)
    df["sample_id"] = sample_id
    base = pd.DataFrame(columns=df.columns)
    if base_sample is not None and not base_sample.empty:
        required_base = {"news_id", "ticker", "content_hash"}
        missing_base = required_base - set(base_sample.columns)
        if missing_base:
            raise ValueError(f"base sample missing required fields: {sorted(missing_base)}")
        base_keys = base_sample[["news_id", "ticker", "content_hash"]].copy()
        base_keys["news_id"] = base_keys["news_id"].fillna("").astype(str).str.strip()
        base_keys["ticker"] = base_keys["ticker"].fillna("").astype(str).str.upper().str.strip()
        base_keys["content_hash"] = base_keys["content_hash"].fillna("").astype(str).str.strip()
        if base_keys[["news_id", "ticker", "content_hash"]].eq("").any().any():
            raise ValueError("base sample requires nonempty news_id/ticker/content_hash")
        if base_keys.duplicated(["news_id", "ticker"]).any():
            raise ValueError("duplicate base sample keys")
        base = df.merge(base_keys, on=["news_id", "ticker"], how="inner", suffixes=("", "_base"), validate="one_to_one")
        if len(base) != len(base_keys):
            raise ValueError("base sample contains untraceable keys")
        if not base["content_hash"].astype(str).eq(base["content_hash_base"].astype(str)).all():
            raise ValueError("base sample content hash mismatch")
        if len(base) > n:
            raise ValueError("n is smaller than preserved base sample")
        base = base.drop(columns=["content_hash_base"])
        base["selection_origin"] = "base_preserved"
    used = set(base["news_id"].astype(str))
    rest = df[~df["news_id"].astype(str).isin(used)].copy()
    # Stable hash randomizes ties without depending on source row order.
    rest["_stable_rank"] = rest["news_id"].apply(lambda value: int(hashlib.sha256(f"{seed}|{value}".encode()).hexdigest()[:16], 16))
    balance = ["calendar_period", "ticker", "source", "sample_bucket", "match_confidence", "length_bucket"]
    for col in balance:
        rest[col] = rest[col].fillna("").astype(str)
    chosen = []
    counts = {col: Counter(base[col].fillna("").astype(str)) if col in base else Counter() for col in balance}
    while len(chosen) < n - len(base) and not rest.empty:
        score = pd.Series(0.0, index=rest.index)
        for col in balance:
            score += rest[col].map(lambda value: counts[col][value])
        pick_idx = rest.assign(_balance_score=score).sort_values(["_balance_score", "_stable_rank", "news_id"]).index[0]
        picked = rest.loc[pick_idx]
        chosen.append(picked)
        for col in balance:
            counts[col][str(picked[col])] += 1
        rest = rest.drop(index=pick_idx)
    added = pd.DataFrame(chosen).drop(columns=["_stable_rank"], errors="ignore") if chosen else pd.DataFrame(columns=df.columns)
    if not added.empty:
        added["selection_origin"] = "balanced_addition"
    out = pd.concat([base, added], ignore_index=True, sort=False)
    if len(out) < n:
        raise ValueError(f"insufficient deduplicated corpus rows: requested={n} available={len(out)}")
    out["selection_rank"] = range(1, len(out) + 1)
    return out.sort_values(["selection_origin", "sample_bucket", "ticker", "date", "news_id"]).reset_index(drop=True)


def write_summary(
    path: Path,
    input_path: Path,
    df: pd.DataFrame,
    sample: pd.DataFrame,
    counts: dict[str, int],
    output_path: Path = OUTPUT,
    sample_id: str = "sample150_canonical",
) -> None:
    lines = [
        "# Annotation sample selection summary",
        "",
        f"- Input: `{input_path}`",
        f"- Input SHA256: `{sha256_file(input_path)}`",
        f"- Rows before dedup: {counts['before']}",
        f"- Rows after URL dedup: {counts['after_url']}",
        f"- Rows after content hash dedup: {counts['after_hash']}",
        f"- Rows after title dedup: {counts['after_title']}",
        f"- Sample ID: `{sample_id}`",
        f"- Output rows: {len(sample)}",
        f"- Base rows preserved: {int(sample.get('selection_origin', pd.Series(dtype=str)).eq('base_preserved').sum())}",
        f"- Balanced additions: {int(sample.get('selection_origin', pd.Series(dtype=str)).eq('balanced_addition').sum())}",
        f"- Output: `{output_path}`",
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
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--base-sample", type=Path)
    parser.add_argument("--sample-id", default="sample150_canonical")
    args = parser.parse_args()
    ensure_dirs()
    input_path = pick_input(args.input)
    df = pd.read_csv(input_path, encoding="utf-8")
    df = normalize_columns(df)
    df = df[df["ticker"].ne("") & df["title"].astype(str).str.strip().ne("")].copy()
    deduped, counts = dedup(df)
    base = None
    if args.base_sample:
        base_path = args.base_sample if args.base_sample.is_absolute() else ROOT / args.base_sample
        base = pd.read_csv(base_path, encoding="utf-8-sig")
    sample = build_sample(deduped, args.n, args.seed, base, args.sample_id)
    legacy_mode = base is None and args.sample_id == "sample150_canonical" and args.n == 150 and args.output == OUTPUT
    legacy_keep = ["news_id", "ticker", "date", "source", "title", "description", "full_text", "article_summary", "key_facts_json", "url", "match_confidence", "content_hash", "article_text_chars", "length_bucket", "sample_bucket"]
    expansion_keep = ["sample_id", "selection_origin", "selection_rank", "news_id", "ticker", "date", "calendar_period", "source", "title", "description", "full_text", "article_summary", "key_facts_json", "url", "match_confidence", "content_hash", "article_text_chars", "length_bucket", "sample_bucket"]
    keep = legacy_keep if legacy_mode else expansion_keep
    for col in keep:
        if col not in sample.columns:
            sample[col] = ""
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    summary_path = args.summary if args.summary.is_absolute() else ROOT / args.summary
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample[keep].to_csv(output_path, index=False, encoding="utf-8-sig")
    write_summary(summary_path, input_path, deduped, sample, counts, output_path, args.sample_id)
    selection_manifest = {
        "artifact_schema_version": "annotation_sample_selection_v1",
        "sample_id": args.sample_id,
        "seed": args.seed,
        "requested_n": args.n,
        "output_rows": len(sample),
        "base_rows_preserved": int(sample.get("selection_origin", pd.Series(dtype=str)).eq("base_preserved").sum()),
        "base_content_hash_validation": "passed" if base is not None and not base.empty else "not_applicable",
        "input_sha256": sha256_file(input_path),
        "output_sha256": sha256_file(output_path),
        "quota_dimensions": ["calendar_period", "ticker", "source", "sample_bucket", "match_confidence", "length_bucket"],
        "selection_rule": "deterministic_greedy_minimum_marginal_stratum_count",
    }
    manifest_path = output_path.with_suffix(".selection_manifest.json")
    manifest_path.write_text(json.dumps(selection_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {output_path} rows={len(sample)}")
    print(f"saved {summary_path}")
    print(f"saved {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
