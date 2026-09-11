# Bundle Scope and Claim Boundaries

## 1. Package classes

| Class | Location | Purpose | Interpretation boundary |
|---|---|---|---|
| V6 prospective primary | `multi_llm_evidence_extraction/config/v6_technical_primary_v1.json`, `multi_llm_evidence_extraction/outputs/v6_primary/<run_id>/`, `multi_llm_evidence_extraction/reports/v6_primary/<run_id>/` | Full-price-panel A/B/C evaluation for the active V6 protocol | H1 is Tech+Keyword versus Tech and H2 is Tech+Semantic versus Tech; only a completed run under a new run ID may support these claims |
| Frozen canonical | `thesis_submission/`, `multi_llm_evidence_extraction/outputs/harmonized/canonical_150_v7/` | Historical same-spine keyword--semantic study | Applies only to the declared common stratified article spine and its fixed B→C protocol; it is not V6 H1/H2 evidence |
| Legacy quarterly pipeline | `pipeline/`, `config/pipeline_config.yaml` | Earlier quarterly `label_basic` experiments | News-filtered Config A/B/C meanings differ from V6 and must not be cited as V6 primary evidence |
| Runtime | `research_ui/`, `ui_artifacts/current/` | Frozen EvidenceTrace dashboard | Historical research prototype; no investment advice or live-market claim |
| Reproduction inputs | `data/prices/`, `data/features/`, selected `multi_llm_evidence_extraction/` source/data | Processed inputs and source for verification/rebuild | Rebuild only in a new workspace/run ID |
| Supplementary | `docs/supplementary_evidence/` | Evidence for semantic quality, event study, card rubric, traceability | Read each subfolder README before citing |
| Restricted | `data/news/`, `restricted_internal_data/` | Full internal news corpus | Internal research only; never public redistribution without rights review |
| Archived | `docs/archive/`, `STRUCTURE_KLTN.md` | Historical planning/reference material | Not canonical final evidence |

## 2. V6 prospective primary protocol

The active V6 print-form proposal is evaluated only through the new `v6_primary/<run_id>` lane. Its primary sample starts from the full price/target panel and requires only `target_status == ok` plus available lagged technical features. It does **not** filter on article count or news coverage. Keyword and semantic values are zero-filled for rows identified as no-news, while timing, mapping or extraction problems remain separately audited. Coverage fields such as `news_count`, `news_count_log` and `has_min_news` are audit-only and are excluded from both predictors and eligibility.

The locked configurations and hypotheses are:

- `A_technical`: lagged technical features;
- `B_technical_keyword`: lagged technical plus keyword features;
- `C_technical_semantic`: lagged technical plus semantic features;
- H1: B versus A;
- H2: C versus A;
- C versus B: supplemental only.

H1 and H2 form the V6 primary multiple-testing family. Their Random Forest / Balanced Accuracy results must be interpreted with the joint Benjamini–Hochberg adjustment recorded by the run. A smoke run or an incomplete run is not primary evidence.

## 3. Frozen canonical finding

The frozen canonical contract compares `B_technical_coverage_keyword` with `C_technical_coverage_semantic` using Random Forest and Balanced Accuracy under run `canonical_150_v7`.

- Same-row, coverage and fold audits passed.
- The primary gate did **not** pass.
- The frozen canonical primary result does **not** support a claim that semantic features are superior to keyword features in that setting.

Never overwrite `canonical_150_v7`, and do not replace or “rescue” its result with the V6 rerun, legacy sweeps, other horizons, other universes or other models. The V6 H1/H2 lane and the frozen B→C lane answer different registered questions.

## 4. Supplementary claim boundaries

### Semantic annotation

Pseudo-label consensus, agreement, rule comparison and limited sanity checks support claims about representation, provenance and error taxonomy only. They do not establish human gold-standard correctness. The three annotation runs represent two model families, and some provenance is legacy reconstructed.

### Event association

Event-window files support exploratory association between semantic categories and adjusted outcomes. They do not support causality, alpha or investment recommendations.

### Decision cards and dashboard

The selected `router_claude2` materials support automated rubric comparisons within their stated generator/judge condition. They do not measure return or human decision quality. Review-only outcomes must never be treated as input to an initial decision card.

## 5. Excluded material

This package deliberately excludes:

- harmonized runs `canonical_150_v1` through `canonical_150_v6`;
- legacy data experiments, models, notebooks, old backtests and unrelated result sweeps;
- logs, caches, worktrees, environments and secrets;
- failed provider trials and mixed rubric runs not selected as coherent evidence;
- public distribution rights for raw/full-text news.

## 6. Internal data warning

The raw news corpus is included only because this archive is an internal research package. It must not be pushed to public Git, released publicly, attached to a public thesis appendix, or placed in public cloud storage before data rights, retention, PII and provider-transfer governance are reviewed.
