from __future__ import annotations

import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import CATEGORICAL_FIELDS, OUTPUT_DIR, REPORT_DIR, ensure_dirs, infer_model_vendor, markdown_table, read_jsonl

LABEL_FILES = {x: OUTPUT_DIR / f"labels_annotator_{x}.jsonl" for x in ("a", "b", "c")}
CONSENSUS = OUTPUT_DIR / "pseudo_labels_consensus.csv"
REPORT = REPORT_DIR / "annotation_agreement_report.md"


def load_labels() -> dict[str, dict[str, dict[str, Any]]]:
    data = {}
    for ann, path in LABEL_FILES.items():
        rows = [r for r in read_jsonl(path) if r.get("status") == "ok"]
        data[ann] = {str(r.get("news_id")): r for r in rows}
    return data


def pairwise_rate(a: dict[str, Any], b: dict[str, Any], field: str) -> tuple[int, int, float]:
    ids = sorted(set(a) & set(b))
    if not ids:
        return 0, 0, 0.0
    agree = sum(1 for i in ids if a[i].get(field) == b[i].get(field))
    return agree, len(ids), agree / len(ids)


def cohen_kappa(a: dict[str, Any], b: dict[str, Any], field: str) -> float | None:
    ids = sorted(set(a) & set(b))
    if not ids:
        return None
    pairs = [(a[i].get(field), b[i].get(field)) for i in ids]
    n = len(pairs)
    po = sum(1 for x, y in pairs if x == y) / n
    ca = Counter(x for x, _ in pairs)
    cb = Counter(y for _, y in pairs)
    labels = set(ca) | set(cb)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def manifest_provenance(annotator: str, rows_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    manifest_path = OUTPUT_DIR / f"annotation_manifest_{annotator}.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            return {
                "annotator": annotator,
                "api_provider": manifest.get("api_provider", manifest.get("provider", "unknown")),
                "requested_model": manifest.get("requested_model", manifest.get("model", "unknown")),
                "response_model": ",".join(manifest.get("response_models", [])) or manifest.get("response_model", "unknown"),
                "model_vendor": manifest.get("model_vendor", "unknown"),
                "route_mode": manifest.get("route_mode", "unknown"),
                "provenance_status": manifest.get("provenance_status", manifest.get("status", "unknown")),
                "run_id": manifest.get("run_id", "unknown"),
            }
        except (json.JSONDecodeError, OSError):
            pass
    tuples = {
        (
            str(row.get("provider", "unknown")),
            str(row.get("requested_model", "unknown")),
            str(row.get("response_model", row.get("requested_model", "unknown"))),
        )
        for row in rows_by_id.values()
    }
    ordered = sorted(tuples)
    if not ordered:
        provider, requested, response, provenance_status = "unknown", "unknown", "unknown", "missing"
    elif len(ordered) == 1:
        provider, requested, response = ordered[0]
        provenance_status = "legacy_reconstructed"
    else:
        provider, requested, response, provenance_status = "mixed", "mixed", "mixed", "mixed_run_metadata"
    return {
        "annotator": annotator,
        "api_provider": provider,
        "requested_model": requested,
        "response_model": response,
        "model_vendor": infer_model_vendor(response) if response != "mixed" else "mixed",
        "route_mode": "unknown",
        "provenance_status": provenance_status,
        "run_id": "unknown",
    }


def main() -> int:
    ensure_dirs()
    data = load_labels()
    lines = ["# Annotation agreement report", ""]
    provenance_rows = [manifest_provenance(ann, rows_by_id) for ann, rows_by_id in data.items()]
    lines += ["## Annotator provenance", "", markdown_table(pd.DataFrame(provenance_rows)), ""]
    counts = {ann: len(rows) for ann, rows in data.items()}
    lines += ["## Annotator valid-label counts", "", markdown_table(pd.Series(counts)), ""]
    total_invalid = {ann: sum(1 for r in read_jsonl(path) if r.get("status") == "error") for ann, path in LABEL_FILES.items()}
    lines += ["## Invalid/error counts", "", markdown_table(pd.Series(total_invalid)), ""]
    rows = []
    for field in CATEGORICAL_FIELDS:
        for a, b in itertools.combinations(data.keys(), 2):
            agree, total, rate = pairwise_rate(data[a], data[b], field)
            kappa = cohen_kappa(data[a], data[b], field)
            rows.append({"field": field, "pair": f"{a}-{b}", "agree": agree, "total": total, "agreement": round(rate, 4), "cohen_kappa": None if kappa is None else round(kappa, 4)})
    lines += ["## Pairwise agreement", "", markdown_table(pd.DataFrame(rows)) if rows else "No pairwise labels available.", ""]
    if CONSENSUS.exists():
        cons = pd.read_csv(CONSENSUS, encoding="utf-8-sig")
        if not cons.empty:
            lines += ["## Consensus summary", "", f"- Consensus rows: {len(cons)}"]
            if "consensus_method" in cons:
                for method, count in cons["consensus_method"].value_counts().items():
                    lines.append(f"- {method}: {int(count)}")
            if "analysis_eligible" in cons:
                eligible = cons["analysis_eligible"].astype(str).str.lower().isin(["true", "1"])
                lines.append(f"- Analysis eligible: {int(eligible.sum())}/{len(cons)}")
            if "evidence_span" in cons:
                lines.append(f"- Evidence span missing rate: {cons['evidence_span'].isna().mean():.2%}")
            lines.append("")
            examples = cons.head(10)
            lines += ["## Example rows", "", markdown_table(examples), ""]
    else:
        lines += ["## Consensus summary", "", "Consensus file not found. Run `build_consensus_labels.py` after live labels exist.", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
