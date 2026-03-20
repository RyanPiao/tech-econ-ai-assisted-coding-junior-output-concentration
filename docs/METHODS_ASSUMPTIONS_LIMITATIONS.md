# Methods, Assumptions, Limitations, and Identification Caveats (Real-Data-First)

## 1) Empirical objective and estimand
The empirical objective is to estimate whether weeks classified as post-adoption under an observed AI-assistance proxy are associated with changes in junior developers’ output share.

This is an **associational estimand** in the current data/design. It is not interpreted as a causal average treatment effect.

## 2) Data construction pipeline
1. Ingest observed GH Archive–derived repo-week panel.
2. Construct treatment proxy from observed AI-signal fields.
3. Build outcome/control variables from observed columns.
4. Apply explicit analysis sample filters.
5. Estimate baseline and robustness models.
6. Export diagnostics on identification quality.

Core data artifacts:
- `data/raw/real_proxy/repo_week_panel_q2_2025_more_data.csv`
- `data/raw/real_proxy/repo_week_panel_q2_2025_more_data_metadata.json`
- `data/processed/real_panel_clean.csv`
- `data/processed/real_panel_metadata.json`

## 3) Variable definitions
### 3.1 Outcome
- **Primary:** `junior_output_share = junior_output / total_output` when `total_output > 0`
- **Alternatives:** `junior_merged_pr_share`, `junior_ticket_share`

### 3.2 Treatment proxy
`ai_proxy_trigger = 1` when all conditions hold:
- `ai_intensity >= 0.02`
- `ai_signal_events >= 2`
- `ai_eligible_events > 0`

`adoption_week` is the first trigger week, with burn-in logic shifting week-1 first triggers to week 2 when week 2 exists. `treated = 1` for `week_index >= adoption_week`.

### 3.3 Sample rule
Analysis sample requires:
- `total_output >= 1`
- non-missing `junior_output_share`

Coverage in processed metadata:
- Total panel: 360 rows, 20 teams, 18 weeks
- Analysis panel: 165 rows, 16 teams, 18 weeks

## 4) Baseline model and implementation
Baseline TWFE:

\[
Y_{it} = \beta\,\text{treated}_{it} + \theta_1\log(1+\text{total\_output}_{it}) + \theta_2\,\text{post\_merge\_bug\_proxy}_{it} + \alpha_i + \gamma_t + \varepsilon_{it}
\]

- \(\alpha_i\): team fixed effects
- \(\gamma_t\): week fixed effects
- standard errors: clustered by team

Baseline output artifact:
- `outputs/tables/table_baseline_results.csv`

## 5) Robustness and diagnostic suite
### 5.1 Robustness variants
- No-controls model
- Full-controls model
- Alternative outcomes
- Winsorized-outcome check
- Placebo-lead specification
- High-output subsample

Artifact:
- `outputs/tables/table_robustness_results.csv`

### 5.2 Dynamic/event-time diagnostics
- Event-study leads/lags (lead/lag windows vary by run; reference -1)
- Joint pretrend test

Artifacts:
- `outputs/tables/table_event_study_coefficients.csv`
- `outputs/tables/table_event_study_metadata.json`
- `outputs/tables/table_v3_event_study_coefficients.csv`

### 5.3 V3 multi-proxy × multi-method sweep (long horizon)
For publication-facing stress tests, v3 estimates each treatment-proxy variant (strict/balanced/broad) with:
- TWFE baseline
- event-study dynamic specification
- stacked DiD (when cohort/control support is sufficient)
- matched/reweighted comparison (implemented as team-level propensity reweighted TWFE; closest valid alternative when exact matching support is thin)
- placebo diagnostics where feasible (timing-shift placebo or pre-period placebo)

Artifacts:
- `outputs/tables/table_v3_proxy_definitions.csv`
- `outputs/tables/table_v3_horizon_data_expansion.csv`
- `outputs/tables/table_v3_identification_sweep_results.csv`
- `outputs/tables/table_v3_defensibility_ranking.csv`

### 5.4 Identification support diagnostics
- Switcher counts
- Adoption-timing concentration
- Timing coverage tables

Artifacts:
- `outputs/tables/table_identification_diagnostics.csv`
- `outputs/tables/table_identification_timing_coverage.csv`

## 6) Identification assumptions and where they are weakest
For causal interpretation, TWFE/event-time approaches rely on strong support and comparability assumptions. In this dataset, the binding constraints are empirical support, not model algebra.

### 6.1 Measurement assumption (treatment)
Assumption: text-derived AI-signal intensity is a reasonable proxy for true AI-tool usage intensity.

Weakness: treatment is measured indirectly; no direct seat/license/telemetry exposure variable is observed.

### 6.2 Timing/comparability assumption
Assumption: untreated and not-yet-treated units provide informative counterfactual timing variation.

Weakness: only 7 switchers in analysis sample, with adoption still concentrated early (week 2 has 5 teams; later adoptions at weeks 5, 6, and 9), so timing leverage remains limited.

### 6.3 Pretrend diagnostic usefulness
Assumption: lead-period estimates can probe pre-treatment comparability.

Weakness: lead support improved but is still thin (event -3 count = 3; event -2 count = 3), so pretrend tests should still be read as low-power diagnostics.

## 7) Current empirical implication
With this support profile, estimates should be treated as **descriptive panel associations** under proxy measurement. They are informative about observed correlation patterns and identification gaps, but not sufficient for clean causal claims.

## 8) Interpretation rules for all outputs
Use:
- “associated with”
- “proxy-based”
- “identification-limited”
- “suggestive, not causal”

Avoid:
- “caused” / “impact” / “proves”
- policy-welfare conclusions not directly identified

## 9) Next-step research design priorities (stronger identification)
1. Extend panel length and increase number of switchers.
2. Add direct treatment telemetry (or a validation sample linking proxy to telemetry).
3. Pre-specify minimum event-time support thresholds before dynamic inference.
4. Pre-register outcome hierarchy and diagnostic decision rules.
5. Retain explicit claim-to-artifact mapping for all substantive statements.

## 10) Appendix roadmap (publication path)
### v2
- Data quality and denominator diagnostics appendix
- Full robustness table appendix
- Event-time support appendix with low-support flags
- Treatment-threshold sensitivity appendix

### v3
- Proxy-vs-telemetry concordance appendix
- External-validity appendix across repo activity strata
- Pre-analysis-plan compliance appendix
- Synthetic mechanism appendix, separated from core claims per `docs/APPENDIX_SYNTHETIC_SCOPE.md`
