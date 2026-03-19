# Writer Handoff Memo

## 1) Study purpose (one-paragraph version)
This package evaluates whether team-level AI-assistance adoption is associated with changes in junior developers’ share of measurable output. The design is a benchmark-to-synthetic workflow: moments are extracted from a sparse public proxy panel, then used to calibrate a larger synthetic team-week panel for econometric estimation. The resulting estimates are useful for disciplined scenario analysis and draft writing, but they are not definitive causal effects. (Artifacts: `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`; `outputs/tables/table_baseline_results.csv`)

## 2) Data architecture and what is observed vs assumed
- **Proxy pilot input:** `data/raw/real_proxy/repo_week_panel_pilot.csv`
- **Benchmark moments output:** `data/processed/benchmark_moments.csv`
- **Benchmark metadata / placeholder policy:** `data/processed/benchmark_moments_metadata.json`
- **Synthetic calibrated panel:** `data/synthetic/synthetic_team_week_panel.csv`
- **Calibration diagnostics:** `data/synthetic/synthetic_calibration_diagnostics.csv`

Important interpretation point for prose: the included proxy pilot does not contain observed adopter switches for timing identification, so timing moments in calibration are explicitly placeholder-based and documented as such. (Artifacts: `data/processed/benchmark_moments.csv`; `data/processed/benchmark_moments_metadata.json`; `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`)

## 3) Estimation setup (for methods section)
- Baseline model: two-way fixed effects (team FE + week FE), SE clustered by team.
- Primary outcome: `junior_output_share`.
- Primary regressor: `treated` (post-adoption indicator).
- Robustness set:
  - `junior_merged_pr_share` outcome
  - `junior_ticket_share` outcome
  - winsorized primary outcome
  - placebo lead term (`lead3_treated`)
  - large-team subsample (`team_size >= 8`)
- Event study: leads/lags with reference period at event time -1 (lead max 6, lag max 8).

(Artifacts: `outputs/tables/table_baseline_model_summary.txt`; `outputs/tables/table_robustness_model_summaries.txt`; `outputs/tables/table_event_study_metadata.json`; `outputs/tables/table_event_study_summary.txt`)

## 4) Core quantitative results to report conservatively
### Baseline
- Treated coefficient: **0.0151**
- SE: **0.0100**
- p-value: **0.131**
- 95% CI: **[-0.0045, 0.0348]**
- N: **2,140 team-weeks** across **72 teams** and **30 weeks**

(Artifact: `outputs/tables/table_baseline_results.csv`)

### Robustness snapshot
- Merged-PR-share outcome: **0.0243** (p=0.102)
- Ticket-share outcome: **-0.00004** (p=0.998)
- Winsorized primary outcome: **0.0161** (p=0.102)
- Placebo lead term: **0.0032** (p=0.805)
- Large-team subsample: **0.0127** (p=0.312)

(Artifact: `outputs/tables/table_robustness_results.csv`)

### Event-time diagnostics
- Joint pretrend p-value: **0.963**
- Pre-period coefficients: generally near zero and imprecise
- Post-period coefficients: mixed sign and mostly imprecise; event time +7 is borderline (p=0.059)

(Artifacts: `outputs/tables/table_event_study_coefficients.csv`; `outputs/tables/table_event_study_metadata.json`)

## 5) Suggested wording discipline (important)
Use phrases such as:
- “associated with”
- “consistent with”
- “calibrated scenario evidence”

Avoid phrases such as:
- “caused by”
- “proves that”
- “establishes causal impact”

(Artifact: `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`)

## 6) Figure/table production map
- **Table A1 (descriptives):** `outputs/tables/table_a1_descriptive_stats.csv`
- **Baseline table:** `outputs/tables/table_baseline_results.csv`
- **Robustness table:** `outputs/tables/table_robustness_results.csv`
- **Event-study table:** `outputs/tables/table_event_study_coefficients.csv`
- **Figure 1 (adoption timing):** `outputs/figures/figure_1_adoption_timing_histogram.png`
- **Figure 2 (group trends):** `outputs/figures/figure_2_group_trends.png`
- **Figure 3 (event study):** `outputs/figures/figure_3_event_study.png`

## 7) Publication-ready caption and notes starter text
### Figure 1
**Caption:** Distribution of adoption week among adopter teams in the synthetic analysis sample.

**Notes:** Never-adopter teams are excluded from the histogram. Timing reflects calibrated synthetic design inputs/outputs, not direct firm telemetry.

### Figure 2
**Caption:** Weekly mean junior output share for ever-adopter versus never-adopter teams.

**Notes:** Lines are unadjusted descriptive means and should not be read as regression-adjusted treatment effects.

### Figure 3
**Caption:** Event-time coefficients for junior output share with event time -1 omitted as reference; 95% confidence intervals shown.

**Notes:** Estimates come from a TWFE model with team-clustered standard errors. Pretrend evidence is diagnostic and not sufficient for causal identification.

### Table A1
**Caption:** Descriptive statistics for the synthetic analysis sample.

**Notes:** Statistics are computed on `analysis_sample == 1`; includes sample size, outcome moments, adoption rate, and treated share.

### Baseline table
**Caption:** Baseline TWFE estimate for junior output share.

**Notes:** Includes team and week fixed effects with team-clustered SE. Coefficient sign is positive, but confidence intervals include zero.

### Robustness table
**Caption:** Sensitivity checks across alternative outcomes, sample definitions, and placebo timing.

**Notes:** Intended to assess directional stability and precision under alternative specifications.

### Event-study table
**Caption:** Lead/lag coefficients around adoption relative to event time -1.

**Notes:** Include joint pretrend p-value in footnote; individual coefficients are noisy and should be interpreted cautiously.

## 8) Reproducibility references to keep unchanged in manuscript package
- `docs/REPLICATION_GUIDE.md`
- `README.md`

Retain command sequences exactly as documented.
