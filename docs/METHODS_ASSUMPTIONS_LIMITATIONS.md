# Methods, Assumptions, Limitations, and Identification Caveats (Real Data)

## Methods overview
1. **Real-data ingest/cleaning:** use observed GH Archive–derived repo-week panel.
2. **Treatment proxy construction:** infer adoption timing from observed AI-signal intensity thresholds.
3. **Econometric analysis:** estimate TWFE models with team and week fixed effects; SE clustered by team.
4. **Robustness checks:** alternative outcomes, alternative control sets, placebo lead, high-output subsample.
5. **Dynamic diagnostics:** event-study coefficients and joint pretrend test.
6. **Identification diagnostics:** switcher counts and treatment-timing coverage tables.

## Core variable definitions
- **Outcome (primary):** `junior_output_share = junior_output / total_output` when `total_output > 0`.
- **Treatment proxy trigger (`ai_proxy_trigger`):**
  - `ai_intensity >= 0.02`
  - `ai_signal_events >= 2`
  - `ai_eligible_events > 0`
- **Adoption timing (`adoption_week`):** first week with trigger = 1.
- **Post indicator (`treated`):** 1 if `week_index >= adoption_week`, else 0.

## Baseline model
\[
Y_{it} = \beta\,\text{treated}_{it} + \theta_1\log(1+\text{total\_output}_{it}) + \theta_2\,\text{post\_merge\_bug\_proxy}_{it} + \alpha_i + \gamma_t + \varepsilon_{it}
\]

where \(\alpha_i\) are team FE and \(\gamma_t\) are week FE.

## Identification diagnostics (current dataset)
- Analysis sample: 68 team-weeks, 9 teams, 11 weeks.
- Switchers: 5 teams.
- Adoption timing concentration: 4 adopters switch in week 2, 1 adopter in week 6.
- Event-study lead support is sparse (lead -3 count = 1, lead -2 count = 1).

Artifacts:
- `outputs/tables/table_identification_diagnostics.csv`
- `outputs/tables/table_identification_timing_coverage.csv`
- `outputs/tables/table_event_study_metadata.json`

## Main limitations
- **Proxy treatment measurement:** adoption is inferred from public-text AI mentions, not seat/license telemetry.
- **Small effective panel:** few teams and short window reduce precision.
- **Timing concentration:** most switches occur early (week 2), limiting event-time leverage.
- **Sparse pre-period lead cells:** pretrend tests are statistically unstable with very low lead counts.
- **Associational design:** estimates are not interpreted as clean causal effects.

## Recommended language for paper
Use terms like **"associated with"**, **"proxy-based"**, **"suggestive"**, and **"identification-limited"**.
Avoid causal verbs such as **"caused"**, **"proves"**, **"establishes impact"**.
