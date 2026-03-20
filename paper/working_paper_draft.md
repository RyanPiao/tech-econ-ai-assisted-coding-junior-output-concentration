# AI-Assisted Coding Adoption and Junior-Developer Output Concentration

**Draft status:** real-data-first working paper (core results from observed data only)

## Abstract
This paper examines whether a repo-week proxy for AI-assisted coding adoption is associated with changes in junior developers’ share of observable output. The analysis uses an observed public GH Archive–derived panel and estimates two-way fixed-effects models (repo FE and week FE) with team-clustered standard errors. In the baseline specification, the post-adoption proxy coefficient is -0.0729 (SE 0.0957; p=0.446; 95% CI: -0.2605 to 0.1148), indicating no precise evidence of a directional effect in this sample. Robustness estimates are similarly imprecise for most outcomes, while placebo-lead and pretrend diagnostics indicate weak identification quality in the current panel. We therefore interpret findings as proxy-based associations, not causal effects.

**Keywords:** AI assistance, software productivity, junior developers, panel methods, treatment proxies

---

## 1. Motivation
A central AI-and-work question is whether new coding tools broaden contribution opportunities for less-experienced contributors or instead reinforce incumbent productivity concentration. We study this as a distributional outcome: changes in junior share of observable output around proxy adoption periods.

## 2. Data
### 2.1 Source and unit of analysis
The primary panel is repo-week data derived from public GH Archive events for a fixed set of public repositories and a fixed sample window/configuration (see raw metadata JSON).

Primary files:
- `data/raw/real_proxy/repo_week_panel_q1_2025_expanded.csv`
- `data/raw/real_proxy/repo_week_panel_q1_2025_expanded_metadata.json`

### 2.2 Treatment proxy
Weekly AI-proxy trigger equals 1 when:
1. `ai_intensity >= 0.02`,
2. `ai_signal_events >= 2`,
3. `ai_eligible_events > 0`.

Repo adoption week is first trigger week (with week-1 burn-in shifted to week 2), and `treated=1` after adoption week.

### 2.3 Outcomes and controls
- Primary outcome: `junior_output_share`.
- Alternative outcomes: `junior_merged_pr_share`, `junior_ticket_share`.
- Baseline controls: `log_total_output`, `post_merge_bug_proxy_filled`.

Analysis sample requires `total_output >= 1` and non-missing `junior_output_share`.

## 3. Empirical strategy
### 3.1 Baseline TWFE
\[
Y_{it} = \beta\,\text{treated}_{it} + \theta_1\log(1+\text{total\_output}_{it}) + \theta_2\text{post\_merge\_bug\_proxy}_{it} + \alpha_i + \gamma_t + \varepsilon_{it}
\]

with repo FE (\(\alpha_i\)), week FE (\(\gamma_t\)), and team-clustered SE.

### 3.2 Diagnostics and robustness
- Event-study leads/lags (lead max 3, lag max 4; reference -1).
- Robustness: no-controls, full-controls, alternative outcomes, winsorization, placebo lead, high-output subsample.
- Identification diagnostics: switcher counts and adoption timing coverage.

## 4. Results
### 4.1 Baseline
Estimated treated coefficient: **-0.0729** (SE 0.0957, p=0.446, 95% CI [-0.2605, 0.1148], N=68).

Artifact: `outputs/tables/table_baseline_results.csv`

### 4.2 Robustness
- No-controls: -0.0179 (p=0.767)
- Full-controls: -0.0489 (p=0.666)
- Alt merged-PR share: +0.0149 (p=0.808)
- Alt ticket share: -0.0699 (p=0.300)
- Placebo lead: -0.4620 (p<0.001)

Artifact: `outputs/tables/table_robustness_results.csv`

### 4.3 Event-time diagnostics
Joint pretrend p-value is 3.68e-06, but lead support is very sparse (1 observation each for event -3 and -2). This combination indicates that dynamic diagnostics are unstable and identification is weak in the current sample.

Artifacts:
- `outputs/tables/table_event_study_coefficients.csv`
- `outputs/tables/table_event_study_metadata.json`
- `outputs/tables/table_identification_diagnostics.csv`

## 5. Identification assessment
Current design has observed switchers (5 teams), but timing is heavily concentrated (4 switches in week 2, 1 in week 6) and pre-period support is thin. These constraints materially limit causal credibility.

## 6. Conclusion
In this real-data-first version, we find no precise evidence that proxy AI-adoption periods systematically increase junior output concentration. Given proxy treatment measurement and sparse event-time support, claims should remain associational and conservative. The primary contribution of this version is transparent real-data construction and explicit identification diagnostics.

## 7. Appendix boundary
Synthetic workflows are retained only for appendix mechanism/sensitivity demonstrations and are excluded from core claims (`docs/APPENDIX_SYNTHETIC_SCOPE.md`).
