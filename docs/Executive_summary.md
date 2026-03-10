## 1. Title & Abstract

**AI Coding Assistants and the Distribution of Team Output: Evidence from a Synthetic Team-Week Panel**

This study asks a practical question with broad labor-market relevance: when software teams adopt AI coding assistants, does output become more concentrated among senior developers, or do junior developers gain relative ground? Using a reproducible synthetic panel of 48 teams observed over 30 weeks, we estimate how adoption timing is associated with changes in the junior share of total output. The main specification compares teams to themselves over time while accounting for common weekly shocks. Across baseline, robustness, and dynamic timing checks, the estimated effect is consistently positive: adoption is associated with an increase of roughly 5–7 percentage points in junior output share. In this synthetic environment, the evidence aligns more with an equalization channel than a pure senior-amplification story. At the same time, because the data are simulated by design, the results should be interpreted as a validated empirical workflow and a directional benchmark, not as a claim about real firms.

## 2. Introduction

Debates about AI in knowledge work often turn on a distributional question, not just a productivity question. It is one thing to show that a team ships more after adopting AI tools. It is another to ask who benefits inside the team: experienced developers, early-career developers, or both.

Software development is an unusually useful setting for this question because output can be tracked at high frequency, roles are clearly defined, and adoption can occur at different times across teams. If AI assistants reduce implementation frictions, junior contributors may be able to complete more work and claim a larger share of team output. If instead AI mostly magnifies architectural leverage and review authority, output may tilt further toward senior contributors.

This project builds a full end-to-end empirical pipeline around that question. The purpose of this cycle is methodological discipline: lock definitions, estimate a baseline model, test robustness, and examine dynamics in a transparent sequence. The resulting Step 7 synthesis provides a reader-friendly account of what the pipeline shows and what it does not show.

## 3. Data & Institutional Context

The analysis uses a synthetic team-week panel constructed to mirror a plausible organizational setting. The core dataset contains 1,440 observations (48 teams × 30 weeks), with role-level activity aggregated into team-week outcomes. Output is measured through merged pull requests and completed tickets, then split into junior and senior contributions.

Adoption is staggered and non-universal. Thirty-four teams adopt AI coding assistance during the sample window, while fourteen teams remain never-adopters, yielding a team-level adoption rate of 70.8%. This variation creates the institutional contrast needed for difference-in-differences style inference: at each point in time, newly treated teams can be compared to teams not yet treated.

The primary outcome is `junior_output_share`, defined as junior output divided by total team output. In raw comparisons, treated team-weeks already show a higher mean junior share (0.539) than untreated team-weeks (0.508), and treated teams also exhibit higher total output on average. These descriptive patterns motivate—but do not by themselves identify—a causal interpretation.

## 4. Empirical Strategy

The baseline model is a two-way fixed-effects panel regression of junior output share on a treatment indicator for post-adoption team-weeks. Team fixed effects absorb time-invariant differences in team composition and culture; week fixed effects absorb common shocks affecting all teams in a given week. Standard errors are clustered at the team level.

To test whether conclusions depend on specific measurement choices, the study pre-specifies several robustness checks: alternative junior-share outcomes (PR share and ticket share), output-weighted estimation, and winsorization of the dependent variable to limit outlier influence. A placebo-style lead term is also introduced to probe whether estimated effects appear before adoption.

Finally, the analysis adds an event-study-style dynamic specification with leads and lags around adoption (reference period: one week before adoption). This allows a direct visual and statistical check for pre-adoption drift and for the timing profile of post-adoption effects.

## 5. Main Findings

The baseline estimate indicates a clear positive shift in junior contribution after adoption. The treatment coefficient is 0.0609 (SE 0.0109; p < 0.001), implying an increase of about 6.1 percentage points in junior output share relative to not-yet-adopted teams in the same period.

Robustness exercises preserve this central pattern. The effect remains positive when the outcome is junior PR share (0.0502) and junior ticket share (0.0692), when observations are weighted by total output (0.0584), and when the outcome is winsorized (0.0599). In each case, inference remains statistically strong.

The dynamic check reinforces the baseline interpretation. The joint pretrend test across lead coefficients is not significant (p = 0.901), suggesting no detectable pre-adoption divergence within the tested window. Post-adoption coefficients are mostly positive, with an average effect of 0.0534 over event times 0 through 8.

## 6. Robustness & Limitations

The strongest internal result is consistency: different outcome definitions, weighting choices, and timing checks all point in the same direction. The placebo lead term is small and imprecise (0.0055, p = 0.556), which further reduces concern that the main estimate is driven by a simple anticipatory pattern in this simulated panel.

Still, limitations are substantial and should be read first, not last. The dataset is synthetic, so the treatment effect is generated under explicit design assumptions. That makes this study excellent for testing workflow integrity and model behavior, but insufficient for external claims about the real software labor market.

There are also structural measurement caveats that will matter in future real-data work. Commit and ticket shares can reflect task granularity, review bottlenecks, and managerial assignment choices rather than pure productivity. The junior/senior taxonomy may blur over time, and real adoption timing could be correlated with unobserved shocks that are harder to net out than in a controlled synthetic environment.

## 7. Conclusion

Taken as a methodological exercise, the project succeeds: the research design is coherent from data construction through dynamic inference, and the results are stable across multiple specification choices. In this synthetic setting, AI coding adoption is associated with a meaningful increase in junior developers’ share of team output.

Taken as substantive evidence about real organizations, the findings are best treated as a directional prior. They suggest that an equalization mechanism is plausible and empirically testable, but they do not establish it beyond the simulation. The next research step is therefore straightforward: port the same design logic to observed organizational data, preserve the transparency discipline used here, and re-evaluate the question under genuine institutional heterogeneity.

## 8. Appendix

**Selected quantitative results**

- Sample size: 1,440 team-week observations (48 teams, 30 weeks)
- Team adoption: 34 adopters, 14 never-adopters (70.8% adopters)
- Baseline TWFE treatment effect on `junior_output_share`: 0.0609 (95% CI: 0.0394 to 0.0824)
- Robustness treatment effects:
  - `junior_merged_pr_share`: 0.0502
  - `junior_ticket_share`: 0.0692
  - weighted baseline: 0.0584
  - winsorized outcome: 0.0599
- Dynamic check:
  - Joint pretrend test (leads -6 to -2): p = 0.901
  - Average post-adoption effect (event times 0 to 8): 0.0534

**Reproducibility note**

All estimates are drawn from finalized Step 2–6 artifacts in `docs/` and `outputs/`, generated under the locked synthetic build configuration (seed 20260309).