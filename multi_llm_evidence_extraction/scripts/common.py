from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STUDY_DIR = ROOT / "multi_llm_evidence_extraction"
SCHEMA_DIR = STUDY_DIR / "schemas"
PROMPT_DIR = STUDY_DIR / "prompts"
DATA_DIR = STUDY_DIR / "data"
OUTPUT_DIR = STUDY_DIR / "outputs"
REPORT_DIR = STUDY_DIR / "reports"
SCRIPT_DIR = STUDY_DIR / "scripts"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import llm_provider  # noqa: E402

PROMPT_VERSION = "semantic_news_materiality_v1"
SCHEMA_VERSION = "semantic_news_annotation_v1"
CONSENSUS_SCHEMA_VERSION = "pseudo_label_consensus_v2"
MAPPING_POLICY = "next_trading_day_missing_publication_time"

FORBIDDEN_PROMPT_TOKENS = (
    "label_basic",
    "label_threshold",
    "label_outperform",
    "future_return",
    "next_close",
    "next_avg_close",
    "realized",
    "outcome",
    "excess_return",
    "pred_proba",
    "prediction",
    "shap",
)

CATEGORICAL_FIELDS = ["ticker_relevance", "materiality", "direction", "event_type", "time_horizon"]
NUMERIC_FIELDS = ["materiality_score", "expected_impact_score", "uncertainty_score", "novelty_score", "reasoning_confidence"]
TEXT_FIELDS = ["news_id", "ticker", "company_name", "article_date", "source", "title", "url", "event_subtype", "summary", "reason"]


def ensure_dirs() -> None:
    for path in (SCHEMA_DIR, PROMPT_DIR, DATA_DIR, OUTPUT_DIR, REPORT_DIR, SCRIPT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm(value: Any) -> str:
    if value is None:
        return ""
    try:
        import pandas as pd  # local import: scripts can run without pandas until data work
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return re.sub(r"\s+", " ", str(value)).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_news_id(row: dict[str, Any]) -> str:
    parts = [
        norm(row.get("ticker")).upper(),
        norm(row.get("date") or row.get("article_date") or row.get("published_at"))[:10],
        norm(row.get("url")).lower(),
        norm(row.get("title")).lower(),
    ]
    return sha256_text("|".join(parts))[:16]


def content_hash(row: dict[str, Any]) -> str:
    existing = norm(row.get("content_hash"))
    if existing:
        return existing
    parts = [
        norm(row.get("ticker")).upper(),
        norm(row.get("date") or row.get("article_date"))[:10],
        norm(row.get("url")).lower(),
        norm(row.get("title")).lower(),
        norm(row.get("description")).lower(),
        article_text(row).lower(),
    ]
    return sha256_text("\n".join(parts))


def article_text(row: dict[str, Any]) -> str:
    for col in ("full_text", "article_text", "article_summary", "lead", "description", "text_clean", "text_tokenized"):
        value = norm(row.get(col))
        if value:
            if col == "description":
                return f"{norm(row.get('title'))}. {value}".strip()
            return value
    return norm(row.get("title"))


def article_payload(row: dict[str, Any], max_chars: int = 12000) -> dict[str, Any]:
    text = article_text(row)
    date = norm(row.get("article_date") or row.get("date") or row.get("published_at"))[:10]
    return {
        "news_id": norm(row.get("news_id")) or stable_news_id(row),
        "ticker": norm(row.get("ticker")).upper(),
        "company_name": norm(row.get("company_name")),
        "article_date": date,
        "source": norm(row.get("source")),
        "title": norm(row.get("title")),
        "description": norm(row.get("description")),
        "article_summary": norm(row.get("article_summary")),
        "key_facts_json": norm(row.get("key_facts_json")),
        "article_text": text[:max_chars],
        "article_text_chars": len(text),
        "truncated": len(text) > max_chars,
        "url": norm(row.get("url")),
        "match_confidence": norm(row.get("match_confidence")),
        "content_hash": content_hash(row),
    }


def assert_no_prompt_leakage(payload: Any) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True).lower()
    leaked = [token for token in FORBIDDEN_PROMPT_TOKENS if token in serialized]
    if leaked:
        raise ValueError(f"Prompt payload contains forbidden future/outcome token(s): {leaked}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def load_schema(name: str = "semantic_news_annotation_schema.json") -> dict[str, Any]:
    return load_json(SCHEMA_DIR / name)


def _fallback_validate(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    required = schema.get("required", [])
    missing = [field for field in required if field not in instance]
    if missing:
        raise ValueError(f"Missing required field(s): {missing}")
    props = schema.get("properties", {})
    if not schema.get("additionalProperties", True):
        extra = sorted(set(instance) - set(props))
        if extra:
            raise ValueError(f"Unexpected field(s): {extra}")
    for field, rules in props.items():
        if field not in instance:
            continue
        value = instance[field]
        allowed_types = rules.get("type")
        if isinstance(allowed_types, str):
            allowed_types = [allowed_types]
        if allowed_types:
            ok = False
            for t in allowed_types:
                if t == "null" and value is None:
                    ok = True
                elif t == "string" and isinstance(value, str):
                    ok = True
                elif t == "boolean" and isinstance(value, bool):
                    ok = True
                elif t == "integer" and isinstance(value, int) and not isinstance(value, bool):
                    ok = True
                elif t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
                    ok = True
                elif t == "array" and isinstance(value, list):
                    ok = True
                elif t == "object" and isinstance(value, dict):
                    ok = True
            if not ok:
                raise ValueError(f"Invalid type for {field}: {type(value).__name__}, expected {allowed_types}")
        enum = rules.get("enum")
        if enum is not None and value not in enum:
            raise ValueError(f"Invalid enum for {field}: {value!r}; allowed={enum}")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rules and value < rules["minimum"]:
                raise ValueError(f"{field} below minimum {rules['minimum']}: {value}")
            if "maximum" in rules and value > rules["maximum"]:
                raise ValueError(f"{field} above maximum {rules['maximum']}: {value}")


def validate_json(instance: dict[str, Any], schema: dict[str, Any] | None = None) -> None:
    schema = schema or load_schema()
    try:
        import jsonschema  # type: ignore
    except ModuleNotFoundError:
        _fallback_validate(instance, schema)
        return
    jsonschema.validate(instance=instance, schema=schema)


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.I)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        parsed = json.loads(stripped[start : end + 1])
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("Could not parse one JSON object from LLM output")


def resolve_provider_model(provider: str | None, model: str | None) -> tuple[str, str]:
    llm_provider.load_env_file(ROOT)
    resolved_provider = llm_provider.resolve_provider(provider)
    return resolved_provider, llm_provider.resolve_model(resolved_provider, model)


def make_client(provider: str) -> tuple[Any, Any]:
    return llm_provider.make_llm_client(provider)


def provider_is_auth_error(provider: str, exc: Exception, provider_module: Any | None = None) -> bool:
    return llm_provider.is_auth_error(provider, exc, provider_module)


def clamp_int(value: Any, low: int = 1, high: int = 5, default: int = 3) -> int:
    try:
        parsed = int(round(float(value)))
    except Exception:
        parsed = default
    return max(low, min(high, parsed))


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "có", "co"}


def parse_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    text = norm(value)
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (SyntaxError, ValueError):
            pass
    return [part.strip() for part in text.split(",") if part.strip()]


def infer_model_vendor(model: str) -> str:
    lowered = norm(model).lower()
    if "gpt" in lowered or lowered.startswith(("o1", "o3", "o4")):
        return "openai"
    if "claude" in lowered:
        return "anthropic"
    if "deepseek" in lowered:
        return "deepseek"
    if "gemini" in lowered:
        return "google"
    return "unknown"


def build_trading_calendars(prices: Any) -> dict[str, list[Any]]:
    import pandas as pd

    work = prices.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce").dt.normalize()
    work["ticker"] = work["ticker"].astype(str).str.upper()
    return {
        ticker: sorted(group["date"].dropna().unique())
        for ticker, group in work.groupby("ticker")
    }


def map_articles_to_effective_trading_date(labels: Any, prices: Any) -> Any:
    import numpy as np
    import pandas as pd

    calendars = build_trading_calendars(prices)
    rows: list[dict[str, Any]] = []
    for _, row in labels.iterrows():
        ticker = norm(row.get("ticker")).upper()
        dates = calendars.get(ticker, [])
        article_date = pd.to_datetime(row.get("article_date") or row.get("date"), errors="coerce")
        if not dates or pd.isna(article_date):
            continue
        normalized = article_date.normalize()
        pos = np.searchsorted(dates, np.datetime64(normalized), side="right")
        if pos >= len(dates):
            continue
        item = dict(row)
        item["article_date"] = normalized
        item["effective_date"] = pd.Timestamp(dates[pos])
        item["date"] = item["effective_date"]
        item["mapping_policy"] = MAPPING_POLICY
        rows.append(item)
    return pd.DataFrame(rows)


def markdown_table(obj: Any) -> str:
    """Return markdown-ish table without optional tabulate dependency."""
    try:
        import pandas as pd
        if isinstance(obj, pd.Series):
            df = obj.rename("value").reset_index()
        elif isinstance(obj, pd.DataFrame):
            df = obj.reset_index() if obj.index.name or not isinstance(obj.index, pd.RangeIndex) else obj.copy()
        else:
            df = pd.DataFrame(obj)
        if df.empty:
            return "_empty_"
        cols = [str(c) for c in df.columns]
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in df.iterrows():
            vals = [str(row[c]).replace("|", "\\|") for c in df.columns]
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)
    except Exception:
        return str(obj)
