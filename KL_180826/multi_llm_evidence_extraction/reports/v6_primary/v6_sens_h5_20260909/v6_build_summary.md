# V6 horizon sensitivity panel build

- Run: `v6_sens_h5_20260909`
- Horizon (benchmark sessions): `5`
- Claim level: `v6_sensitivity_horizon_T5`
- Rows: `93824`
- Eligible: `88782`
- No-news keyword rows: `10054`
- No-news semantic rows: `0`

Primary eligibility uses target_status==ok and lagged technical availability only.
Coverage is audit-only. Keyword/semantic predictors are zero-filled for true no-news rows.
This horizon panel is sensitivity-only and does not replace the locked T+20 primary.