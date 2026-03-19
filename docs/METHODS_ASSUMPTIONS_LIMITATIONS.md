# Methods, Assumptions, Limitations, and Identification Caveats

## Methods overview
1. **Benchmark extraction:** compute moments from a real-data proxy pilot panel.
2. **Synthetic calibration:** generate team-week synthetic data so key moments align with benchmark targets.
3. **Econometric analysis:** estimate treatment association using two-way fixed effects (team and week FE) with SE clustered by team.
4. **Robustness:** alternative outcomes, winsorized outcome, placebo-lead check, and large-team subsample.
5. **Dynamic pattern:** event-study style specification around adoption timing.

## Core assumptions
- Team and week fixed effects absorb time-invariant team heterogeneity and common aggregate shocks.
- Remaining treatment variation captures within-team shifts in post-adoption periods.
- Synthetic DGP is a stylized approximation, not a structural model of firm production.

## Calibration assumptions
- Real benchmark moments come from a public proxy panel and may be sparse.
- If timing moments are unidentifiable in observed data, placeholders are used and explicitly logged.
- Total-output benchmark is floor-adjusted in sparse pilot windows to avoid degenerate simulation regimes.

## Limitations
- **Proxy measurement error:** AI adoption in the real panel is not directly observed seat/license telemetry.
- **Sparse pilot data:** weak support for adoption timing in the included pilot sample.
- **Synthetic dependence:** inference is conditional on design choices in the synthetic generator.
- **External validity:** estimates should not be read as direct magnitudes for any specific firm or platform.

## Identification caveats
- Baseline estimates are associational, not causal proof.
- Event-study pretrend tests provide diagnostic evidence but do not guarantee identification.
- Any policy implication should be framed as scenario-based and contingent on stronger future data.

## Recommended language for paper
Use terms like **"associated with"**, **"consistent with"**, and **"illustrative under calibration assumptions"** rather than definitive causal claims.
