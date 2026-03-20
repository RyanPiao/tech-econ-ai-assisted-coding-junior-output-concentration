# AI-Assisted Coding Adoption and Junior-Developer Output Concentration

**Draft status:** real-data-first working paper (core results use observed data only)

## Abstract
This paper studies whether a repo-week proxy for AI-assisted coding adoption is associated with changes in junior developers’ share of observable output. Using an observed GH Archive–derived panel, we run a long-horizon identification sweep over ~18 months (79 weeks) and estimate two-way fixed-effects, event-study, stacked DiD, and reweighted DiD specifications across strict/balanced/broad treatment-proxy variants. Results are heterogeneous across proxy definitions: the balanced proxy family shows directionally consistent negative associations across methods (for example, TWFE -0.149, stacked DiD -0.158), while strict and broad variants each exhibit diagnostic weaknesses (notably pretrend signal for strict/broad event studies or limited control support under broad coding). We therefore interpret all estimates as proxy-based and identification-limited associations rather than causal effects. The contribution of this version is transparent real-data provenance, multi-method stability reporting, and an explicit defensibility ranking for publication-facing narrative choices.

**Keywords:** AI assistance, software productivity, junior developers, labor economics, innovation measurement, panel methods

---

## 1. Introduction and research question
AI coding tools raise a distributional labor question, not only an average-productivity question: do these tools broaden opportunities for less-experienced contributors, or do they increase concentration of measured output among more experienced contributors?

This paper examines that question using a public repo-week panel and a transparent treatment proxy based on observed AI-signal intensity in repository activity. The empirical target is whether post-proxy-adoption periods are associated with changes in junior output share.

This version is intentionally conservative. The design is useful for documenting patterns and measurement constraints, but not for making strong causal claims.

## 2. Positioning and contribution
This study sits at the intersection of three applied literatures:

1. **Applied micro labor economics:** technology adoption and within-team distribution of work/output.
2. **Innovation and productivity measurement:** software development as an increasingly measurable production environment.
3. **Program evaluation under staggered timing:** fixed-effects/event-time diagnostics when switcher support is limited.

Relative to those literatures, this draft contributes in a narrower but concrete way:
- It provides a **fully observed, reproducible data pipeline** for a public proxy design.
- It reports **diagnostics-first identification evidence** rather than only headline coefficients.
- It offers a **publication-facing associational baseline** that can anchor a stronger future design.

## 3. Data construction and measurement

### 3.1 Source data and panel construction
The primary data are repo-week observations derived from public GH Archive events for a fixed repository list and fixed sample configuration.

Primary artifacts (baseline panel):
- `data/raw/real_proxy/repo_week_panel_q2_2025_more_data.csv`
- `data/raw/real_proxy/repo_week_panel_q2_2025_more_data_metadata.json`
- `data/raw/real_proxy/repo_week_panel_q2_2025_more_data_dictionary.csv`

V3 long-horizon artifacts:
- `data/raw/real_proxy/repo_week_panel_v3_long_h18.csv`
- `data/raw/real_proxy/repo_week_panel_v3_long_h18_metadata.json`
- `data/raw/real_proxy/repo_week_panel_v3_long_h18_dictionary.csv`

Processed analysis artifacts:
- `data/processed/real_panel_clean.csv`
- `data/processed/real_panel_metadata.json`

Long-horizon v3 coverage indicates 1,580 total team-weeks (20 teams, 79 weeks), an expansion of +61 weeks relative to the prior 18-week panel.

### 3.2 Outcome construction
Primary outcome:
- `junior_output_share = junior_output / total_output` when `total_output > 0`.

Alternative outcomes used in robustness:
- `junior_merged_pr_share`
- `junior_ticket_share`

Sample inclusion for core estimation requires:
- `total_output >= 1`
- non-missing `junior_output_share`

### 3.3 Treatment proxy definition
Weekly treatment trigger (`ai_proxy_trigger`) equals 1 when all conditions hold:
1. `ai_intensity >= 0.02`
2. `ai_signal_events >= 2`
3. `ai_eligible_events > 0`

Repo/team adoption week is the first trigger week, with a burn-in rule shifting week-1 first triggers to week 2 when week 2 exists. `treated = 1` for weeks at or after adoption week.

This is a practical measurement proxy, not a direct usage measure (for example, not seat/license or IDE telemetry).

## 4. Empirical strategy and identification

### 4.1 Baseline specification
We estimate:

\[
Y_{it} = \beta\,\text{treated}_{it} + \theta_1\log(1+\text{total\_output}_{it}) + \theta_2\text{post\_merge\_bug\_proxy}_{it} + \alpha_i + \gamma_t + \varepsilon_{it}
\]

where \(\alpha_i\) are repo/team fixed effects, \(\gamma_t\) are week fixed effects, and standard errors are clustered by team.

### 4.2 Robustness and diagnostics
We report baseline robustness checks and a v3 multi-proxy × multi-method sweep.

Baseline robustness:
- no-controls and full-controls variants,
- alternative outcomes,
- winsorized-outcome check,
- placebo-lead specification,
- high-output subsample.

V3 sweep:
- strict / balanced / broad treatment-proxy variants,
- TWFE baseline,
- event-study leads/lags (lead max 6, lag max 8; reference -1),
- stacked DiD (cohort-stacked with not-yet-treated/never controls),
- matched/reweighted comparison (implemented as team-level propensity reweighted DiD),
- placebo diagnostics where feasible.

Artifacts:
- `outputs/tables/table_baseline_results.csv`
- `outputs/tables/table_robustness_results.csv`
- `outputs/tables/table_v3_horizon_data_expansion.csv`
- `outputs/tables/table_v3_proxy_definitions.csv`
- `outputs/tables/table_v3_identification_sweep_results.csv`
- `outputs/tables/table_v3_event_study_coefficients.csv`
- `outputs/tables/table_v3_defensibility_ranking.csv`

### 4.3 Identification limits in current panel
Longer horizon improves support, but key limits remain:
- treatment is still proxy-measured from public text signals,
- diagnostics vary materially by proxy definition,
- broad proxy coding can exhaust control support (high treated share),
- strict and broad event-study leads show non-trivial pre-period signal.

These constraints materially limit causal interpretation even when some method-specific coefficients are statistically non-zero.

## 5. Results

### 5.1 V3 cross-proxy, cross-method pattern
Main v3 results (long-horizon panel) show meaningful heterogeneity by proxy family:

- **Strict proxy:** TWFE and reweighted DiD are near zero and imprecise; stacked DiD also imprecise; event-study average post is positive but accompanied by strong lead-period signal (pretrend p-value < 0.001), weakening interpretability.
- **Balanced proxy:** all four methods are negative in sign; event-study average post is -0.326 (p=0.019), stacked DiD is -0.158 (p<0.001), while TWFE/reweighted estimates are negative but less precise.
- **Broad proxy:** TWFE/reweighted are negative and statistically non-zero; stacked DiD is also negative; however event-study pretrend diagnostics fail (p=0.0039) and treated share is very high (0.84), leaving thin control support.

### 5.2 Stability and placebo diagnostics
- Placebo timing-shift checks in TWFE/reweighted models are generally non-significant across proxies.
- Stacked-DiD placebo checks are non-significant where estimable.
- Event-study lead diagnostics are proxy-dependent and central for interpretation:
  - balanced pretrend p=0.160 (passes a conventional diagnostic threshold),
  - strict pretrend p<0.001 and broad pretrend p=0.0039 (fail).

### 5.3 Publication-facing defensibility ranking
Given measurement plausibility + diagnostics + support, the v3 ranking is:
1. **Balanced proxy family** (top recommendation)
2. Strict proxy family
3. Broad proxy family

The balanced family is preferred for headline narrative because it combines directional agreement across methods with comparatively better pretrend diagnostics and without the extreme treated-share support problem seen in broad coding.

## 6. Interpretation discipline
What this version supports:
- A transparent, reproducible associational estimate under explicit proxy measurement.
- A clear statement that current panel support is thin for causal claims.

What this version does **not** support:
- Claims that AI assistance causally increases or decreases junior contribution concentration.
- Welfare or policy conclusions about net labor-market effects.

Recommended language: “associated with,” “proxy-based,” “identification-limited,” and “suggestive.”

## 7. Credible next-step design for stronger identification
A stronger next phase should prioritize identification before adding model complexity.

### 7.1 Data expansion priorities
- Extend panel length (more pre and post periods).
- Increase repository/team count and switcher count.
- Preserve transparent inclusion logic in `data/processed/real_panel_metadata.json` style outputs.

### 7.2 Treatment measurement priorities
- Replace/augment text-based proxy with direct telemetry where feasible (for example, measured tool-usage intensity by repo-week).
- Keep proxy and telemetry side-by-side to quantify measurement error and attenuation risk.

### 7.3 Pre-analysis priorities
- Register outcome hierarchy (primary, secondary, exploratory).
- Pre-commit minimum support thresholds for event-time cells before running dynamic inference.
- Define primary identification diagnostics ex ante (switchers, timing dispersion, lead-cell counts).

### 7.4 Estimation roadmap
- Continue FE-based panel models for comparability.
- Add designs that reduce timing-composition bias once richer support exists (for example, better-balanced adoption windows and explicit design-based checks).

## 8. Conclusion
In this real-data-first working-paper version, the long-horizon v3 sweep suggests that under a balanced treatment-proxy definition, post-adoption periods are associated with lower junior output share across several methods. But inference quality remains identification-limited and proxy-dependent, so these patterns should not be framed as causal effects. The main value is transparent empirical workflow, explicit diagnostics, and a defensibility-ranked narrative for future stronger designs.

## 9. Appendix roadmap (publication-ready v2/v3)

### v2 appendix targets
- Expanded data provenance and quality checks (missingness, outlier, and denominator diagnostics).
- Full coefficient tables and model-summary exports for all robustness variants.
- Event-time support tables by cohort/week and explicit “minimum support” flags.
- Measurement appendix comparing alternative treatment-proxy thresholds.

### v3 appendix targets
- Telemetry-linked treatment validation (if available) and proxy-vs-telemetry concordance.
- Extended panel external-validity checks (by repo size/activity strata).
- Pre-analysis-plan compliance table (planned vs executed tests).
- Synthetic appendix retained only for mechanism illustrations, clearly separated from core claims (`docs/APPENDIX_SYNTHETIC_SCOPE.md`).
