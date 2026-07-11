from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import REPORT_DIR, ensure_dirs
from write_claim_evidence_table import build_artifact_snapshot, markdown_table

NEG = REPORT_DIR / "news_feature_negative_findings_summary.md"
MAIN = REPORT_DIR / "ket_qua_luan_van_semantic_news_materiality.md"
PITCH = REPORT_DIR / "advisor_pitch_one_page.md"


def render_negative_findings(snapshot: dict[str, Any]) -> str:
    counts = snapshot["counts"]
    consensus = snapshot["consensus"]
    event = snapshot["event_tests"]
    return "\n".join([
        "# News feature negative findings summary",
        "",
        "Existing keyword/news-count experiments should be interpreted as representation limits, not proof that news is useless. Keyword frequency can miss relevance, materiality, direction, ticker mismatch, market-wide context, and boilerplate noise.",
        "",
        f"Current semantic audit contains {counts.get('consensus_labels')} consensus pseudo-label rows, of which {consensus['eligible']} are analysis-eligible. These are controlled pseudo-labels, not human ground truth.",
        "",
        f"Corrected event tests: rows={event['rows']}; BH-FDR significant={event['fdr_significant']}; robust positive effects={event['robust_results']}; positive claim gate pass={event['claim_gate_pass']}.",
        "",
        "Referenced prior artifacts: `reports/H1_experiment_report.md`, `reports/H2_H3_validation_report.md`, `reports/experiment_A6_report.md`, `reports/experiment_B1_report.md`, `docs/keyword_features_note.md`.",
        "",
    ])


def render_main_report(snapshot: dict[str, Any]) -> str:
    counts = snapshot["counts"]
    consensus = snapshot["consensus"]
    agreement = snapshot["agreement"]
    manual = snapshot["manual_sanity"]
    rule = snapshot["rule_comparison"]
    event = snapshot["event_tests"]
    ml = snapshot["ml"]
    topk = snapshot["topk"]
    count_rows = [[name, value] for name, value in counts.items()]
    method_rows = [[method, count] for method, count in sorted(consensus["methods"].items())]
    provenance_rows = [
        [
            row["annotator"], row["api_provider"], row["requested_model"], row["response_models"],
            row["model_vendor"], row["route_mode"], row["provenance_status"], row["prompt_version"],
            row["schema_version"], row["labels_hash_match"], row["manifest_sha256"],
        ]
        for row in snapshot["provenance"]
    ]
    artifact_rows = []
    summaries = {"consensus": consensus, "event_tests": event, "ml_predictions": ml, "topk": topk}
    for name, metadata in snapshot["artifacts"].items():
        summary = summaries.get(name, {})
        artifact_rows.append([
            name,
            metadata.get("path"),
            ", ".join(summary.get("schema_versions", [])) or "unavailable",
            metadata.get("sha256"), metadata.get("modified_utc"), metadata.get("latest_upstream_utc"), metadata.get("freshness"),
        ])
    fold_rows = [
        [fold.get(key) for key in ("fold_id", "train_start", "train_end", "test_start", "test_end", "purge_trading_days")]
        for fold in ml["folds"]
    ]
    agreement_rows = [
        [row["field"], row["pair"], row["agree"], row["total"], f"{row['agreement']:.4f}", None if row["cohen_kappa"] is None else f"{row['cohen_kappa']:.4f}"]
        for row in agreement["pairwise"]
    ]
    manual_rows = [
        [field, values["ok"], values["not_ok"], values["reviewed"], None if values["ok_rate"] is None else f"{values['ok_rate']:.4f}"]
        for field, values in manual["checks"].items()
    ]
    rule_rows = [
        [row["rule_field"], row["consensus_field"], row["n"], f"{row['accuracy']:.4f}", f"{row['macro_f1']:.4f}"]
        for row in rule["metrics"]
    ]
    topk_status = "verified" if topk["status"] == "verified_nonoverlap_turnover_cost" else "not verified"
    event_claim = "exploratory positive evidence present" if event["claim_gate_pass"] else "no robust positive evidence after correction"
    return "\n".join([
        "# Semantic news materiality study report",
        "",
        "## Data and current artifact counts",
        "",
        markdown_table(["artifact", "rows"], count_rows),
        "",
        "## Semantic annotation schema",
        "",
        "Semantic annotation schema separates ticker relevance, materiality, direction, event type, uncertainty, novelty, and exact evidence span.",
        "",
        "## Pseudo-label protocol and consensus",
        "",
        f"Consensus rows={consensus['rows']}; analysis-eligible={consensus['eligible']}; ineligible={consensus['ineligible']}; schema={', '.join(consensus['schema_versions']) or 'unavailable'}.",
        "",
        markdown_table(["consensus method", "rows"], method_rows) if method_rows else "_Consensus methods unavailable._",
        "",
        "Offline prompt packs are pending annotations, not synthetic labels. Future/outcome fields are blocked from annotation prompts. Consensus labels remain pseudo-labels, not ground truth.",
        "",
        "## Annotator provenance",
        "",
        markdown_table(["annotator", "API provider", "requested model", "response model", "vendor", "route", "status", "prompt version", "schema version", "label hash match", "manifest SHA256"], provenance_rows) if provenance_rows else "_Annotation provenance manifests unavailable._",
        "",
        "Provider and model vendor are separate fields. A routed response keeps its actual vendor and is not relabeled as a native provider model.",
        "",
        "## Annotation agreement",
        "",
        f"Available={agreement['available']}; valid labels={agreement['valid_counts']}; error rows={agreement['error_counts']}; mean pairwise agreement={agreement['mean_agreement']:.4f}." if agreement["mean_agreement"] is not None else f"Available={agreement['available']}; valid labels={agreement['valid_counts']}; error rows={agreement['error_counts']}; mean pairwise agreement=unavailable.",
        "",
        markdown_table(["field", "pair", "agree", "total", "agreement", "Cohen kappa"], agreement_rows) if agreement_rows else "_Agreement metrics unavailable._",
        "",
        "Agreement measures annotator consistency; it does not turn pseudo-labels into human ground truth.",
        "",
        "## Manual sanity check",
        "",
        f"Rows={manual['rows']}; rows with any check filled={manual['filled_rows']}; status={manual['status']}; missing columns={manual.get('missing_columns', [])}.",
        "",
        markdown_table(["field", "ok", "not ok", "reviewed", "ok rate"], manual_rows) if manual_rows else "_Manual sanity-check data unavailable._",
        "",
        "This is a small quality-control sample, not full human ground truth.",
        "",
        "## Keyword/rule baseline versus semantic pseudo-labels",
        "",
        f"Analysis-eligible merged rows={rule['compared_rows']}; available={rule['available']}.",
        "",
        markdown_table(["rule field", "consensus field", "n", "accuracy", "macro-F1"], rule_rows) if rule_rows else "_Rule comparison data unavailable._",
        "",
        "Error taxonomy includes missing context/materiality, ticker mismatch, market-wide versus direct confusion, boilerplate noise, mixed direction, and overlapping event types. Semantic labels remain a controlled pseudo-label reference, not ground truth.",
        "",
        "## Artifact schema, hash, and freshness",
        "",
        markdown_table(["artifact", "path", "schema version", "SHA256", "modified UTC", "latest upstream UTC", "freshness"], artifact_rows),
        "",
        "Freshness compares each artifact mtime with newest available upstream reference; SHA256 identifies exact bytes used by this report run.",
        "",
        "## Semantic signal audit and corrected event-window tests",
        "",
        f"Gate rule: `{event['gate_rule']}`. Tests={event['rows']}; BH-FDR significant={event['fdr_significant']}; positive-CI={event['positive_ci']}; robust-positive={event['robust_results']}; claim gate pass={event['claim_gate_pass']}. Interpretation: {event_claim}.",
        "",
        f"Consistency checks: FDR flag mismatches={event['reported_flag_mismatches']}; robust-positive flag mismatches={event.get('robust_flag_mismatches')}. Negative robust effects are not counted as support for a positive claim.",
        "",
        "## Point-in-time ML experiment",
        "",
        f"Prediction rows={ml['rows']}; unique folds={ml['fold_count']}; purge trading days={ml['purge_trading_days']}; purged OOS verification={ml['purged_oos_verified']}; status={ml['status']}; configs={', '.join(ml['configs']) or 'unavailable'}; models={', '.join(ml['models']) or 'unavailable'}.",
        "",
        markdown_table(["fold", "train start", "train end", "test start", "test end", "purge trading days"], fold_rows) if fold_rows else "_Purged OOS fold metadata unavailable._",
        "",
        "## Non-overlap turnover-cost Top-K simulation",
        "",
        f"Rows={topk['rows']}; entry periods={topk['periods']}; top-K={topk['top_k']}; strategies={', '.join(topk['strategies']) or 'unavailable'}; holding days={topk.get('holding_period_days', [])}; cost rates={topk.get('round_trip_cost_rates', [])}.",
        "",
        f"Non-overlap={topk['non_overlapping']}; turnover-cost equation={topk['turnover_cost_verified']}; net-return equations={topk['net_return_verified']}; overall status={topk['status']} ({topk_status}).",
        "",
        "## Evidence cards and outcome review",
        "",
        f"Case candidates={counts.get('case_candidates')}; outcome-review labels={counts.get('outcome_reviews')}. These are post-hoc evidence audits, not trading recommendations.",
        "",
        "## Claim-vs-evidence summary",
        "",
        f"Consensus eligible={consensus['eligible']}/{consensus['rows']}; robust-positive event tests={event['robust_results']}; purged OOS verified={ml['purged_oos_verified']}; Top-K methodology status={topk['status']}; outcome-review rows={counts.get('outcome_reviews')}.",
        "",
        "## Interpretation rules and limitations",
        "",
        "- LLM consensus labels are pseudo-labels, not ground truth.",
        "- Event results require BH-FDR significance and a strictly positive bootstrap CI before supporting a positive exploratory claim.",
        "- ML claims require fold metadata to verify purged, out-of-sample predictions.",
        "- Top-K claims require non-overlap plus turnover-scaled cost and net-return equation checks.",
        "- Weak or failed gates remain valid negative findings.",
        "- No artifact establishes causal impact, persistent alpha, or investment suitability.",
        "",
        "## Conclusion",
        "",
        "Structured semantic annotation improves auditability of relevance, materiality, direction, and evidence compared with keyword counts. Statistical, ML, and portfolio results remain exploratory and must be interpreted through recorded claim gates and limitations.",
        "",
    ])


def render_advisor_pitch(snapshot: dict[str, Any]) -> str:
    consensus = snapshot["consensus"]
    event = snapshot["event_tests"]
    ml = snapshot["ml"]
    topk = snapshot["topk"]
    methods = ", ".join(f"{key}={value}" for key, value in sorted(consensus["methods"].items())) or "unavailable"
    return "\n".join([
        "# Advisor pitch — Semantic News Materiality Study",
        "",
        "Goal: move from keyword frequency to evidence-grounded semantic materiality for Vietnamese stock news.",
        "",
        f"Current evidence: consensus rows={consensus['rows']} ({methods}); eligible={consensus['eligible']}; robust-positive corrected event tests={event['robust_results']}; purged OOS folds={ml['fold_count']} with verification={ml['purged_oos_verified']}; Top-K status={topk['status']} over {topk['periods']} entry periods.",
        "",
        "Contribution: schema, controlled pseudo-label consensus, explicit annotation provenance, corrected event-test gate, purged walk-forward metadata, turnover-cost simulation checks, and byte-level artifact traceability.",
        "",
        "Claim discipline: no ground-truth claim for LLM labels, no causal or alpha claim, and no investment recommendation.",
        "",
    ])


def main() -> int:
    ensure_dirs()
    snapshot = build_artifact_snapshot()
    NEG.write_text(render_negative_findings(snapshot), encoding="utf-8")
    MAIN.write_text(render_main_report(snapshot), encoding="utf-8")
    PITCH.write_text(render_advisor_pitch(snapshot), encoding="utf-8")
    print(f"saved {NEG}")
    print(f"saved {MAIN}")
    print(f"saved {PITCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
