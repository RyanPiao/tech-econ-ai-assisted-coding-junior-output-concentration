# AI-Assisted Coding Adoption and Junior-Developer Output Concentration

**Draft status:** publication-facing working-paper draft (calibrated synthetic design)

## Abstract
This paper studies whether team-level adoption of AI coding assistance is associated with changes in the share of measurable output produced by junior developers. The empirical design uses a transparent benchmark-to-synthetic workflow: benchmark moments are extracted from a sparse public proxy panel, then used to calibrate a larger synthetic team-week panel for estimation. We estimate two-way fixed-effects models with team and week fixed effects and team-clustered standard errors, and we report robustness and event-time diagnostics. In the baseline specification, the estimated post-adoption association is positive in sign (0.015) but statistically imprecise (95% CI: -0.004 to 0.035; p=0.131). Robustness specifications are directionally mixed but generally modest in magnitude, and event-time coefficients show no strong pre-period pattern with a high joint pretrend p-value. Taken together, the results are best interpreted as calibrated scenario evidence consistent with a possible increase in junior output share after AI-assistance adoption, not as definitive causal evidence. (Artifacts: `outputs/tables/table_baseline_results.csv`; `outputs/tables/table_robustness_results.csv`; `outputs/tables/table_event_study_coefficients.csv`; `outputs/tables/table_event_study_metadata.json`; `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`)

**Keywords:** AI assistance, software productivity, junior developers, task allocation, panel methods, calibration

---

## 1. Motivation and framing
A central question in AI-and-work research is whether new tools broaden contribution opportunities for less-experienced workers or primarily amplify already high-productivity workers. In software teams, this question can be operationalized as a distributional one: after AI-assistance adoption, does the junior share of observable output increase, decrease, or remain unchanged?

This repository does not include firm-internal seat telemetry or a broad proprietary panel. Instead, it provides a fully reproducible empirical scaffold that separates (i) what is observed in the proxy data, (ii) what is assumed for calibration, and (iii) what is estimated in downstream regressions. That transparency is the paper’s main contribution at this stage. (Artifacts: `docs/REPLICATION_GUIDE.md`; `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`; `docs/WRITER_HANDOFF_MEMO.md`)

Related empirical literatures include technology adoption, worker-task reallocation, and productivity dispersion. Canonical references include task-based technological change frameworks (Autor, Levy, and Murnane 2003; Acemoglu and Autor 2011), evidence on diffusion and heterogeneous adoption responses (Comin and Mestieri 2018), and emerging evidence on generative AI productivity effects in knowledge work and software contexts (Noy and Zhang 2023; Peng et al. 2023; Brynjolfsson, Li, and Raymond 2023). This draft uses that framing for interpretation but does not claim to settle those literatures with the current data package.

## 2. Data
### 2.1 Benchmark layer and observed limitations
The benchmark layer is constructed from a public proxy pilot panel and then summarized into moments for calibration. The project documentation explicitly notes that direct adoption switches are not observed in the included pilot sample, so timing moments are partly supplied by transparent placeholders rather than estimated from observed adoption transitions. (Artifacts: `docs/WRITER_HANDOFF_MEMO.md`; `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`)

### 2.2 Synthetic analysis panel
The estimation sample is a synthetic team-week panel with 2,140 team-week observations, 72 teams, and 30 weeks. In this panel, team-level adoption is 55.6% and treated exposure is 36.4% of team-weeks. The main outcome (`junior_output_share`) has mean 0.850 and standard deviation 0.132 in the analysis sample. (Artifact: `outputs/tables/table_a1_descriptive_stats.csv`)

### 2.3 Why this data design is useful (and what it cannot do)
The synthetic design allows an internally consistent panel for method benchmarking and writing-ready figures/tables under explicit assumptions. However, because timing moments are partially assumed and outcomes are generated through a calibrated data-generating process, estimated coefficients should be interpreted as design-conditional associations rather than reduced-form causal effects from observed real-world variation. (Artifacts: `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`; `docs/WRITER_HANDOFF_MEMO.md`)

## 3. Empirical strategy
### 3.1 Baseline specification
The baseline model is:

\[
Y_{it} = \beta\,\text{Treated}_{it} + \alpha_i + \gamma_t + \varepsilon_{it},
\]

where \(Y_{it}\) is `junior_output_share`, \(\alpha_i\) are team fixed effects, and \(\gamma_t\) are week fixed effects. Standard errors are clustered at the team level. (Artifacts: `outputs/tables/table_baseline_model_summary.txt`; `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`)

### 3.2 Robustness and diagnostic specifications
Robustness checks include: alternative outcomes (`junior_merged_pr_share`, `junior_ticket_share`), winsorized outcome, placebo lead term, and a large-team subsample (`team_size >= 8`). Dynamic diagnostics use an event-study-style setup with lead max 6, lag max 8, and event time -1 as the omitted reference period. (Artifacts: `outputs/tables/table_robustness_results.csv`; `outputs/tables/table_robustness_model_summaries.txt`; `outputs/tables/table_event_study_metadata.json`; `outputs/tables/table_event_study_summary.txt`)

## 4. Results
### 4.1 Baseline estimate
The baseline treated coefficient is 0.0151 (SE 0.0100; p=0.131; 95% CI: -0.0045 to 0.0348). The sign is positive, but the confidence interval includes economically small negative and positive values, so this estimate is suggestive rather than conclusive. (Artifact: `outputs/tables/table_baseline_results.csv`)

### 4.2 Robustness estimates
Robustness results are mixed but generally modest in magnitude:
- Alternative merged-PR-share outcome: +0.0243 (p=0.102), positive but imprecise.
- Alternative ticket-share outcome: approximately 0.0000 (p=0.998), near zero.
- Winsorized main outcome: +0.0161 (p=0.102), close to baseline.
- Placebo lead term: +0.0032 (p=0.805), not distinguishable from zero.
- Large-team subsample: +0.0127 (p=0.312), positive but less precise.

These patterns are consistent with a small positive association in some specifications, but they do not provide stable high-precision evidence of a common effect size across outcomes and samples. (Artifact: `outputs/tables/table_robustness_results.csv`)

### 4.3 Dynamic pattern
Event-time coefficients in pre-periods are close to zero overall, and the joint pretrend test is non-rejecting (p=0.963). Post-period coefficients vary in sign and precision; one later coefficient (event time +7) approaches conventional thresholds (p=0.059), but most post-period estimates are imprecise. This pattern is consistent with weakly positive post-adoption movements without sharp dynamic discontinuities. (Artifacts: `outputs/tables/table_event_study_coefficients.csv`; `outputs/tables/table_event_study_metadata.json`)

## 5. How to read these results (non-technical)
This study is best read as a **structured scenario test**, not as a final causal estimate for real firms.

A practical reading guide:
1. **Direction:** Several models point in a positive direction for junior share after adoption.
2. **Precision:** Uncertainty is substantial; many intervals include zero.
3. **Credibility:** Diagnostics do not show obvious pre-period divergence, but that alone is not causal proof.
4. **Use case:** Treat magnitudes as planning-relevant ranges for future data collection, not as policy-ready treatment effects.

(Artifacts: `outputs/tables/table_baseline_results.csv`; `outputs/tables/table_robustness_results.csv`; `outputs/tables/table_event_study_metadata.json`; `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`)

## 6. Robustness, limitations, and identification caveats
Three limitations are first-order:

1. **Proxy measurement limits:** AI adoption in the source benchmark layer is not direct seat/license telemetry.
2. **Sparse pilot identification for timing:** adoption timing moments needed placeholder assumptions in the benchmark stage.
3. **Synthetic dependence:** regression estimates are conditional on calibration and data-generating assumptions.

Accordingly, coefficients should be described as **“associated with”** and **“consistent with”** rather than causal impacts. Event-study diagnostics are useful checks, but they do not by themselves establish identification. (Artifacts: `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`; `docs/WRITER_HANDOFF_MEMO.md`)

## 7. Conclusion and next-step roadmap
The current calibrated evidence is consistent with a modest increase in junior output share following AI-assistance adoption, but precision is limited and causal interpretation remains restricted.

A conservative roadmap for the next version:
1. Replace proxy timing placeholders with observed adoption telemetry where possible.
2. Expand real panel coverage in teams and weeks to improve precision.
3. Pre-register a narrower primary estimand and robustness hierarchy.
4. Add outcome-quality metrics (not only output-share quantities) to test mechanism relevance.

(Artifacts: `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`; `docs/REPLICATION_GUIDE.md`; `docs/WRITER_HANDOFF_MEMO.md`)

---

## 8. Publication-ready captions and table notes

### Figure 1. Distribution of team adoption timing
**Caption:** Histogram of adoption week among adopter teams in the synthetic analysis sample.

**Notes:** The histogram excludes never-adopting teams. Adoption timing reflects the calibrated synthetic panel used for estimation and should be interpreted as design input/output rather than observed firm telemetry. (Artifacts: `outputs/figures/figure_1_adoption_timing_histogram.png`; `outputs/tables/table_a1_descriptive_stats.csv`; `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`)

### Figure 2. Mean junior output share by ever-treatment status
**Caption:** Weekly mean junior output share for ever-adopter teams versus never-adopter teams.

**Notes:** Series are unadjusted group means, shown for descriptive orientation. Differences in levels or slopes in this figure are not regression-adjusted treatment effects. (Artifact: `outputs/figures/figure_2_group_trends.png`)

### Figure 3. Event-study estimates around adoption
**Caption:** Event-time coefficients for junior output share, with event time -1 omitted as the reference period and 95% confidence intervals shown.

**Notes:** Coefficients are from a model with team and week fixed effects and team-clustered standard errors. Pre-period estimates and the joint pretrend test are diagnostic, not definitive evidence of identification. (Artifacts: `outputs/figures/figure_3_event_study.png`; `outputs/tables/table_event_study_coefficients.csv`; `outputs/tables/table_event_study_metadata.json`)

### Table A1. Descriptive statistics for the synthetic analysis sample
**Caption:** Summary statistics for sample size, outcome moments, and treatment exposure.

**Notes:** Statistics are computed on observations with `analysis_sample == 1`. `adoption_rate` is the team-level share ever adopting; `treated_share` is the team-week share in post-adoption periods. (Artifact: `outputs/tables/table_a1_descriptive_stats.csv`)

### Baseline table. Two-way fixed-effects estimate
**Caption:** Baseline association between post-adoption treatment status and junior output share.

**Notes:** Specification includes team and week fixed effects with standard errors clustered by team. The treated coefficient is positive but statistically imprecise in this run. Report confidence intervals alongside p-values. (Artifacts: `outputs/tables/table_baseline_results.csv`; `outputs/tables/table_baseline_model_summary.txt`)

### Robustness table. Alternative outcomes and samples
**Caption:** Robustness estimates across alternative outcomes, winsorization, placebo lead, and large-team subsample.

**Notes:** All models retain team and week fixed effects with team-clustered standard errors. The table is designed to assess directional stability and sensitivity, not to identify a single preferred causal estimate. (Artifacts: `outputs/tables/table_robustness_results.csv`; `outputs/tables/table_robustness_model_summaries.txt`)

### Event-study table. Lead/lag coefficients
**Caption:** Event-time coefficients for weeks relative to adoption, excluding event time -1 as the reference period.

**Notes:** Include the joint pretrend p-value in the table footer for context. Individual lead/lag coefficients are noisy in this sample and should be interpreted as pattern diagnostics rather than standalone causal effects. (Artifacts: `outputs/tables/table_event_study_coefficients.csv`; `outputs/tables/table_event_study_metadata.json`; `outputs/tables/table_event_study_summary.txt`)

---

## Appendix roadmap (next writing pass)
- A. Variable definitions and construction notes
- B. Additional robustness hierarchy and multiple-testing discussion
- C. Data pipeline checksums and deterministic run verification

---

## References
- Acemoglu, Daron, and David Autor. 2011. “Skills, Tasks and Technologies: Implications for Employment and Earnings.” In *Handbook of Labor Economics*, Vol. 4B, edited by Orley Ashenfelter and David Card, 1043–1171. Elsevier.
- Autor, David H., Frank Levy, and Richard J. Murnane. 2003. “The Skill Content of Recent Technological Change: An Empirical Exploration.” *Quarterly Journal of Economics* 118(4): 1279–1333.
- Brynjolfsson, Erik, Danielle Li, and Lindsey R. Raymond. 2023. “Generative AI at Work.” NBER Working Paper 31161.
- Comin, Diego, and Martí Mestieri. 2018. “If Technology Has Arrived Everywhere, Why Has Income Diverged?” *American Economic Journal: Macroeconomics* 10(3): 137–178.
- Noy, Shakked, and Whitney Zhang. 2023. “Experimental Evidence on the Productivity Effects of Generative Artificial Intelligence.” Working paper.
- Peng, Sida, Eirini Kalliamvakou, Peter Cihon, and Mert Demirer. 2023. “The Impact of AI on Developer Productivity: Evidence from GitHub Copilot.” arXiv preprint arXiv:2302.06590.
