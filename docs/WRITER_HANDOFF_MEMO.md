# Writer Handoff Memo (Real-Data-First, Economics Framing)

## 1) One-paragraph purpose
This package estimates whether a **repo-week proxy** for AI-assisted coding adoption is associated with the junior share of observable output in public software repositories. All core estimates use observed GH Archive–derived panel data. The empirical posture is intentionally conservative: this draft is an identification-limited associational study, not a causal impact paper.

## 2) Contribution positioning (how to frame in intro)
Use this three-part positioning:
1. **Applied micro/labor angle:** distribution of output within teams during technology adoption.
2. **Innovation measurement angle:** practical measurement of AI-adoption intensity in software production environments.
3. **Methods angle:** transparent reporting of identification constraints (switchers/timing/lead support), not only coefficient headlines.

Recommended contribution sentence:
> “The main contribution of this version is a transparent real-data workflow with explicit identification diagnostics that clarifies what can and cannot be learned from current public proxy data.”

## 3) Data architecture and path map (observed core only)
- Raw panel: `data/raw/real_proxy/repo_week_panel_q2_2025_more_data.csv`
- Raw metadata: `data/raw/real_proxy/repo_week_panel_q2_2025_more_data_metadata.json`
- Dictionary: `data/raw/real_proxy/repo_week_panel_q2_2025_more_data_dictionary.csv`
- Clean panel: `data/processed/real_panel_clean.csv`
- Clean metadata + coverage + diagnostics: `data/processed/real_panel_metadata.json`

Coverage values to use (from processed metadata):
- Total: 360 team-weeks, 20 teams, 18 weeks
- Analysis: 165 team-weeks, 16 teams, 18 weeks

## 4) Treatment/outcome definitions (keep explicit)
### Treatment proxy
`ai_proxy_trigger = 1` iff all hold:
- `ai_intensity >= 0.02`
- `ai_signal_events >= 2`
- `ai_eligible_events > 0`

`adoption_week` = first trigger week (with week-1 burn-in shift to week 2 when available). `treated = 1` for weeks >= `adoption_week`.

### Outcomes
- Primary: `junior_output_share`
- Alternatives: `junior_merged_pr_share`, `junior_ticket_share`

## 5) Estimation setup and current quantitative results
### Baseline model
TWFE (team FE + week FE), team-clustered SE, baseline controls: `log_total_output`, `post_merge_bug_proxy_filled`.

Baseline estimate (from `outputs/tables/table_baseline_results.csv`):
- Treated coefficient: **+0.0462**
- SE: **0.0608**
- p-value: **0.447**
- 95% CI: **[-0.0730, 0.1654]**
- N: **165**

### Robustness snapshot (from `outputs/tables/table_robustness_results.csv`)
- No-controls: +0.0573 (p=0.278)
- Full-controls: +0.0433 (p=0.462)
- Alt merged-PR share: +0.1304 (p=0.111)
- Alt ticket share: -0.0707 (p=0.308)
- Placebo lead (`lead2_treated`): -0.0746 (p=0.562)

## 6) V3 long-horizon identification sweep (new publication-facing diagnostics)
V3 extends the panel and estimates strict/balanced/broad treatment proxies across four methods (TWFE, event-study, stacked DiD, reweighted DiD).

Long-horizon coverage (from `outputs/tables/table_v3_horizon_data_expansion.csv`):
- Window: 2023-10-30 to 2025-04-28
- 79 weeks (~18.2 months), 1,580 team-weeks, 20 teams
- Expansion vs prior 18-week panel: +61 weeks, +1,220 rows

Most defensible proxy family for narrative (from `outputs/tables/table_v3_defensibility_ranking.csv`):
- **Balanced proxy ranked #1**
- Reason: best combined profile of measurement plausibility + method agreement + diagnostics (event-study pretrend p=0.160, placebo checks broadly non-significant, stacked/reweighted estimable)

Balanced-proxy method snapshot (from `outputs/tables/table_v3_identification_sweep_results.csv`):
- TWFE: -0.149 (SE 0.108, p=0.167)
- Event-study average post: -0.326 (SE 0.139, p=0.019), pretrend p=0.160
- Stacked DiD: -0.158 (SE 0.039, p<0.001)
- Reweighted DiD: -0.147 (SE 0.107, p=0.170)

Interpretation line to use: results are **directionally consistent under balanced proxy across methods but remain proxy-based and identification-limited**.

Artifacts:
- `outputs/tables/table_v3_horizon_data_expansion.csv`
- `outputs/tables/table_v3_proxy_definitions.csv`
- `outputs/tables/table_v3_identification_sweep_results.csv`
- `outputs/tables/table_v3_event_study_coefficients.csv`
- `outputs/tables/table_v3_defensibility_ranking.csv`

## 7) Identification diagnostics language (must stay prominent)
Use these facts explicitly:
- Support improved with longer horizon, but treatment remains proxy-measured from public text signals.
- Strict and broad event-study lead diagnostics show non-trivial pre-period signal (pretrend p-values < 0.01), so those variants are weaker for headline inference.
- Broad proxy leaves very few never-adopters in analysis support (1 team), limiting counterfactual comparability.

Additional artifacts:
- `outputs/tables/table_event_study_metadata.json`
- `outputs/tables/table_identification_diagnostics.csv`
- `outputs/tables/table_identification_timing_coverage.csv`
- `outputs/tables/table_sample_expansion_diagnostics.csv`

## 8) Interpretation discipline (editorial guardrails)
Preferred language:
- “associated with”
- “proxy-based”
- “identification-limited”
- “suggestive, not causal”

Avoid:
- “caused,” “impact,” “proves,” “establishes effect”
- any welfare or policy claims not directly estimated

## 9) Suggested narrative flow for paper/blog versions
1. Motivation: distributional AI-and-work question
2. Data construction and transparent proxy definition
3. Baseline estimate and confidence interval
4. Diagnostics showing why causal interpretation is limited
5. Clear conclusion: what is learned now vs what requires better data/design

## 9) Credible next-step design (concise section to include)
Include a short “Next-step identification design” section with:
- richer panel horizon and larger switcher set,
- telemetry-based treatment measurement (or validation sample) to reduce proxy error,
- pre-analysis thresholds for minimum event-time support,
- pre-committed outcome hierarchy and diagnostics.

## 10) Publication-ready appendix roadmap (v2/v3)
### v2
- Data provenance and quality-check appendix
- Full robustness coefficient appendix
- Event-time support appendix with minimum-support flags
- Treatment-threshold sensitivity appendix

### v3
- Proxy-vs-telemetry concordance appendix (if telemetry available)
- External-validity appendix by repo activity strata
- Pre-analysis-plan compliance appendix
- Synthetic mechanism appendix kept explicitly out of core claims (`docs/APPENDIX_SYNTHETIC_SCOPE.md`)

