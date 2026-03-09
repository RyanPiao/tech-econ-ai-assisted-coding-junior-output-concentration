# Step 2 — Pre-analysis Lock (Synthetic Build)

## Objective
Pre-commit to variable definitions, sample construction, treatment timing design, and identification direction before Step 3 estimation.

## Research estimand (directional)
Primary estimand for later steps:

- **Average change in `junior_output_share` after team-level AI coding adoption**, relative to not-yet-adopted teams in the same week.

Intended sign in this synthetic DGP is **positive** (adoption slightly increases junior share), but Step 2 does **not** claim empirical truth. It only fixes a reproducible benchmark dataset.

## Variable lock

### Outcome
- **Primary:** `junior_output_share`
  - `junior_output / total_output`
  - where `junior_output = junior_merged_prs + junior_completed_tickets`

### Alternate outcomes (pre-specified)
- `junior_merged_pr_share`
- `junior_ticket_share`

### Treatment
- `treated = 1` if a team has adopted and `week_index >= adoption_week`; else `0`.
- `post_period` retained as equivalent timing indicator for readability.

### Timing / event-study support
- `event_time = week_index - adoption_week` for adopters.
- never-adopters retain missing `event_time`.

## Sample construction lock
Step 2 analysis sample flag:

- `analysis_sample = 1` if:
  - `total_output >= 10`
  - `junior_output_share` is observed

Planned default in Step 3:
- Run baseline model on `analysis_sample == 1`.
- Sensitivity: rerun with all rows and robust handling for low-volume weeks.

## Synthetic DGP assumptions (explicit)
1. Teams differ in baseline complexity, junior composition, and manager quality.
2. Adoption is staggered and non-universal.
3. Adoption affects both total volume and junior share with modest positive shift in junior share.
4. Weekly common shocks exist (smooth seasonal components).
5. Role-level outputs are generated from team-week totals using binomial splits.

## Intended identification direction
If Step 3 model and data construction are working as expected, treatment coefficients on junior-share outcomes should generally trend positive in sign under this synthetic setup.

This is a **pipeline validation expectation**, not an empirical claim about real organizations.

## Immediate risks and threats
1. **Mechanical endogeneity risk:** generated treatment effects are baked into DGP; passing tests here does not validate real-world identification.
2. **Outcome-definition sensitivity:** commit/ticket shares can be affected by task decomposition conventions.
3. **Small-cell volatility:** low-output weeks can make share outcomes noisy.
4. **Staggered timing complexity:** later estimation must avoid problematic two-way FE weighting pathologies.
5. **Role taxonomy fragility:** junior/senior split is stylized and may not match real HR classifications.

## What is intentionally out of scope in Step 2
- No causal estimation results.
- No hypothesis acceptance/rejection.
- No external validity claims.
- No robustness tables.

Step 2 is complete when data generation, ingestion, and design locks are reproducible and transparent.
