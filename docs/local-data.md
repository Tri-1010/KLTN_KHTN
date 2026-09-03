# Local data and worktrees

Large datasets, experiment caches, checkpoint sweeps, and generated prediction files are local artifacts. They are excluded from Git so that a code checkout or worktree does not materialize several gigabytes of data.

## Data sections

The local sections are declared in `config/local_data_layout.json`:

- `data/news` — restricted source news and annotations;
- `data/experiments` — local derived tables, caches, and checkpoints;
- `data/aggregated` — derived aggregate datasets;
- `data/prices` and `data/prices_extended` — local market data.

These directories must be restored from an approved internal backup or rebuilt with the corresponding pipeline before a data-dependent experiment is run. Do not commit their contents, raw news, checkpoints, or generated prediction sweeps.

## Share data with a worktree

Choose an approved external/shared data root that contains the sections directly. For example, if the root is `D:\KLTN-shared-data`, it should contain `news`, `experiments`, `aggregated`, `prices`, and `prices_extended`.

From a worktree, create directory junctions into that root:

```powershell
.\scripts\setup_shared_data.ps1 -DataRoot "D:\KLTN-shared-data" -ForceReplace
```

The script refuses to replace a non-empty real data directory. Run it only in a new worktree or after confirming that its `data` directories can safely be replaced by links.

Verify links without changing files:

```powershell
.\scripts\verify_local_data.ps1 -DataRoot "D:\KLTN-shared-data"
```

Existing runners continue to use their normal `data/...` paths. A worktree junction keeps those paths compatible while pointing them to shared local data.

## Frozen artifacts

Do not move, overwrite, or regenerate frozen canonical artifacts, `thesis_submission/`, or provenance files merely to save space. Their paths and hashes can be part of the research evidence. The local-data arrangement applies to source data, derived datasets, caches, checkpoints, and large generated prediction outputs.
