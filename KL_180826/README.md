# KL_180826 — Final Internal Thesis Bundle

Portable internal bundle for thesis research:

> **Hệ thống hỗ trợ quyết định cổ phiếu dựa trên tín hiệu học máy và bằng chứng tin tức ngữ nghĩa có truy vết**

This folder is a self-contained **project root** for thesis evidence, historical EvidenceTrace review, V6 reproducibility work, and constrained research workflows.

## Read first

| Need | Start here |
|---|---|
| Thesis source | `thesis_submission/thesis/luan_van.md` |
| Canonical research contract | `thesis_submission/proposal/de_cuong.md` |
| Active V6 print-form proposal | `docs/final/de_cuong_do_an_tot_nghiep_thac_si_v6_technical_primary.md` |
| Bundle scope and limitations | `BUNDLE_SCOPE.md` |
| Claim/evidence matrix | `thesis_submission/governance/claim_evidence_matrix.md` |
| V6 primary protocol | `multi_llm_evidence_extraction/config/v6_technical_primary_v1.json` |
| Locked V6 attestation | `multi_llm_evidence_extraction/audits/v6_primary_20260909/v6_retrospective_attestation.json` |
| New V6 result lane | `multi_llm_evidence_extraction/outputs/v6_primary/<run_id>/v6_run_summary.json`, `v6_inference.csv`, and matching report |
| Dashboard V2 public release | `ui_artifacts/v2/default/` via `scripts/run_research_ui_v2.py` |
| Frozen canonical result | `thesis_submission/canonical_results/canonical_summary.json` |

## Claim boundary

- The active V6 primary lane is `outputs/v6_primary/<run_id>/`: H1 is Technical+Keyword versus Technical, and H2 is Technical+Semantic versus Technical. H1/H2 share the Random Forest/Balanced Accuracy BH family; C-versus-B is supplemental.
- The locked historical V6 attestation classifies H1 and H2 as **unsupported**. `status: ok` means estimable, not supported.
- `canonical_150_v7` is immutable historical B→C evidence and is not V6 H1/H2 evidence.
- The legacy quarterly pipeline has incompatible Config A/B/C meanings and cannot support V6 claims.
- Pseudo-labels are not human ground truth. Event association is exploratory, not causal. The software is not investment advice or an automated trading system.

## Requirements

Target environment: **Windows + Python 3.10 or newer**.

Do not copy a real `.env` into this bundle. `.env.example` is secret-free. Offline dashboards require no API key or network connection.

```powershell
cd C:\path\to\KL_180826
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-runtime.txt
```

## Run historical EvidenceTrace

```powershell
run_dashboard.bat
```

Or:

```powershell
.\.venv\Scripts\python scripts\run_research_ui.py --bundle ui_artifacts\current --port 8501
```

Open `http://localhost:8501`.

## V6 integrity and new prospective runs

`v6_primary_20260909` is a **locked historical run ID**. Do not rebuild it. Its attestation is already published at the path listed above. The audit publisher intentionally refuses a nonempty attestation directory, so do not rerun it in place.

New V6 runs require a new safe ID and an explicit workspace root. The builder validates every declared input hash, separates source failures from verified no-news zero fill, binds target reuse to source/code hashes, and writes intent/build/run/release manifests. A completed manifest makes the run immutable.

```powershell
.\.venv\Scripts\python multi_llm_evidence_extraction\scripts\build_v6_primary_panel.py `
  --workspace-root C:\path\to\workspace `
  --run-id v6_primary_new_YYYYMMDD
.\.venv\Scripts\python multi_llm_evidence_extraction\scripts\run_v6_technical_primary.py `
  --workspace-root C:\path\to\workspace `
  --run-id v6_primary_new_YYYYMMDD
```

`--fast` is only smoke mode. Its resulting claims are marked non-primary and cannot be cited as primary evidence.

## H2 confirmation workspace

The only planned independent H2 confirmation interval is **2026-06-02 through 2026-08-10**. Create an isolated workspace outside this bundle; run preflight; freeze the exact source snapshot, strict A/B/C annotation-consensus provenance, predictions, panel, and robustness artifact; then run the confirmation estimator from that frozen input manifest only.

The confirmation fails closed when coverage, input hash, source status, strict consensus, count gate, or inference gate fails. The local OpenAI-compatible router is restricted to `http://localhost` or `http://127.0.0.1`, an approved alias, and the 2,000-article / 6,000-call cap. Never persist `URL_LOCAL` or `API_LOCAL` in logs, manifests, or public artifacts.

## Dashboard V2

Dashboard V2 is a separate, bilingual, read-only results-review application. It uses only the hash-checked aggregate bundle under `ui_artifacts/v2/default`; it does not alter EvidenceTrace and it cannot execute collection, annotation, or confirmation jobs.

```powershell
.\.venv\Scripts\python scripts\build_research_ui_v2_bundle.py
.\.venv\Scripts\python scripts\run_research_ui_v2.py --bundle ui_artifacts\v2\default --port 8502
```

Open `http://localhost:8502`. The default public release visibly labels the locked H2 comparison as **unsupported**.

## Verify frozen bundle

```powershell
.\.venv\Scripts\python verify_bundle.py --strict
.\.venv\Scripts\python thesis_submission\reproduction\validate_submission.py --run-id canonical_150_v7
```

These validate historical canonical material; they do not promote canonical evidence into V6 H1/H2 evidence.

## Reproduction rules

- Never overwrite `canonical_150_v7`, `v6_primary_20260909`, `thesis_submission/`, or `ui_artifacts/current/`.
- Use a new run ID and a separate workspace for every recomputation or confirmation attempt.
- `data/news/` is internal/restricted research data. Do not upload raw news/full text to a public host without rights review.
- LLM, crawl, and live features require separate authorization and credentials; they are not needed to view frozen historical bundles.
