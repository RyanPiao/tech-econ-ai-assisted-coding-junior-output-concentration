## Title & Abstract

**Who Gains When Teams Adopt AI Coding Tools? Junior Developers’ Share of Output in a Synthetic Team-Week Panel**

This paper asks a simple question in plain language: when a software team starts using AI coding assistance, does more of the team’s visible work end up coming from junior developers, or does the technology mainly strengthen the relative position of senior developers? Using a reproducible synthetic panel of 48 teams observed across 30 weeks, the analysis compares the same teams before and after adoption while also comparing them with teams that have not yet adopted. The central result is consistent across the paper: adoption is associated with a higher junior share of team output, on the order of roughly 5 to 7 percentage points depending on the specification. In practical terms, the pattern in these data looks more like partial equalization than winner-take-all concentration. Because the dataset is synthetic rather than drawn from an observed firm, the findings should be read as evidence that the research design is coherent and informative, not as a final claim about real-world labor markets.

## Introduction

The core causal question is whether a treatment—team-level adoption of AI coding assistance—changes an outcome—the share of total team output attributed to junior developers. Framed this way, the paper is not mainly about whether AI raises output in the aggregate. It is about how output is redistributed within teams once the tool is introduced.

That distinction matters. If AI tools mainly help experienced developers move even faster, firms may see higher productivity alongside a more concentrated distribution of meaningful work, with fewer chances for junior contributors to learn by doing. If, instead, AI lowers some of the barriers that slow less experienced developers—such as boilerplate generation, syntax recall, or debugging small issues—then adoption could widen participation in production and make teams less top-heavy in their measured output. The economic importance of the question therefore lies in hiring, training, promotion, and the long-run shape of entry-level work.

This paper studies that distributional question in a setting designed for clarity. The empirical goal is to estimate how junior output share changes after adoption, relative to comparable teams that have not yet adopted in the same period. The broader purpose is to show, in a transparent and reproducible way, what kind of evidence would support an equalization story and what kind of evidence would support a concentration story.

## Data & Institutional Context

The analysis uses a synthetic dataset built to resemble a plausible software-production environment. The unit of observation is the team-week. In each week, output is recorded at the team level and divided into junior and senior contributions using two concrete measures of work: merged pull requests and completed tickets. Those measures are then combined into a broader output count, from which the main outcome, `junior_output_share`, is constructed.

The final panel contains 1,440 team-week observations, covering 48 teams over 30 weeks. Of those 48 teams, 34 adopt AI coding assistance during the sample period and 14 do not. That staggered timing matters because it creates a useful comparison structure: at any given moment, some teams have already adopted, some will adopt later, and some never adopt during the observed window.

Because the data are synthetic, they should be understood as a research scaffold rather than a record of actual behavior at a particular company. The synthetic design allows the paper to define variables cleanly, test the empirical strategy, and check whether the results behave as expected under a transparent setup. For a public reader, the key point is straightforward: the numbers here are not confidential company data and are not meant to describe any single real workplace. They are a realistic simulation used to evaluate how one would study the question with discipline and clarity.

Even in these synthetic data, the raw descriptive patterns are informative. The average junior output share in untreated team-weeks is about 0.508, while in treated team-weeks it is about 0.539. Treated weeks also show somewhat higher total output on average. Those simple contrasts do not establish causality, but they show that adoption and contribution shares move together in a way worth studying more carefully.

## Empirical Strategy

The identification strategy is a panel difference-in-differences design implemented with team and week fixed effects. In plain English, the model asks whether the junior share of output rises within a team after that team adopts AI coding assistance, compared with the same team before adoption, while also netting out time-specific shocks that affect all teams at once.

This approach relies on a familiar assumption: absent adoption, teams that adopt earlier and teams that adopt later would have followed similar short-run paths in the junior share outcome after accounting for team-specific baselines and common week-level shocks. The fixed effects absorb stable differences across teams, such as persistent variation in team composition or managerial style, and the week effects absorb common shifts that hit everyone at once.

The paper then asks whether that baseline result survives several challenges. It replaces the main outcome with narrower alternatives based only on pull requests or only on tickets. It re-estimates the model while giving more weight to higher-output team-weeks. It trims the influence of extreme values through winsorization. It also adds a placebo-style lead term to see whether the apparent effect shows up before adoption, which would weaken a causal interpretation.

Finally, the paper estimates an event-study-style specification around the adoption date. The purpose of that exercise is intuitive: if the design is credible, the coefficients before adoption should be close to zero, while the coefficients after adoption should shift upward if the treatment truly changes the outcome. In a graph, that would appear as a relatively flat pre-adoption path followed by a positive post-adoption step-up.

## Main Findings

The baseline estimate is clear and substantively meaningful. In the two-way fixed-effects model, the coefficient on treatment is 0.0609, with a clustered standard error of 0.0109 and a 95 percent confidence interval from 0.0394 to 0.0824. The simplest reading is that, after adopting AI coding assistance, a team’s junior share of total output rises by about 6.1 percentage points relative to otherwise comparable team-weeks.

That is not a trivial shift. If a team had previously attributed roughly one-half of visible output to junior developers, a six-point increase would move it noticeably toward a more balanced internal distribution of work. In ordinary workplace terms, the result is consistent with a world in which junior developers are able to complete more tickets, land more merged changes, or otherwise claim a larger share of what the team ships after AI tools arrive.

The robustness checks tell the same story. When the outcome is defined as the junior share of merged pull requests, the estimated effect is 0.0502. When the outcome is the junior share of completed tickets, the estimate is 0.0692. Weighting observations by total output yields 0.0584, and winsorizing the outcome yields 0.0599. The magnitude shifts modestly across specifications, but the direction remains positive throughout.

The dynamic evidence is also informative. The pre-adoption coefficients in the event-study specification are small and statistically weak, and the joint test of pretrends yields a p-value of 0.901. That is what one hopes to see if treated teams were not already drifting upward before adoption. After adoption, the coefficients turn positive. The effect at event time 0 is about 0.0457, it rises to about 0.0726 by event time 2, and it remains positive across the post-adoption window, with an average post-adoption coefficient of 0.0534 from event times 0 through 8. Read narratively, the implied graph would show little evidence of pre-existing divergence and then a persistent upward shift once teams begin using the tool.

Taken together, the coefficients suggest that in this synthetic environment AI coding assistance does not merely increase output while leaving internal hierarchy unchanged. Instead, it is associated with a broader redistribution of observed production toward junior contributors.

## Robustness & Limitations

The most convincing feature of the analysis is consistency. The result is positive in the baseline specification, positive when the outcome is measured differently, positive when larger team-weeks receive more weight, and positive after limiting the influence of extreme observations. The placebo-style lead term is small, imprecise, and statistically insignificant, which makes it harder to explain the main finding as a simple anticipatory pattern.

Even so, several alternative explanations remain conceptually important. One possibility is that measured gains for junior developers reflect changes in task assignment rather than deeper capability gains. Managers might redirect smaller or more easily AI-assisted tasks toward junior staff, increasing junior output share even if senior developers still control the most complex work. Another possibility is that pull requests and tickets capture visibility rather than value. A team could show a higher junior share because work has been decomposed into more countable units, not because junior developers are generating proportionately more economically important output.

There are also limits inherent to the design itself. Because the data are synthetic, the treatment effect is generated within a controlled environment. That is useful for validating an empirical workflow, but it cannot settle the real-world debate. In an observed firm, adoption timing might coincide with deadlines, leadership changes, hiring shifts, or product transitions that are harder to net out statistically. Role categories may also blur over time, especially when developers are rapidly gaining experience or when responsibilities differ across teams.

For those reasons, the paper supports a disciplined claim rather than an expansive one. It shows that a transparent research design can detect a stable positive relationship between adoption and junior output share under a realistic simulated setting. It does not yet prove that the same magnitude, or even the same sign, will hold in production environments.

## Conclusion

The practical takeaway is that AI coding tools need not mechanically intensify existing hierarchies inside software teams. In this paper’s synthetic setting, adoption is associated with a meaningful increase in the share of output attributed to junior developers. That pattern is consistent with the idea that AI can reduce some execution bottlenecks that otherwise slow early-career contributors.

For managers, the implication is not that AI automatically solves skill gaps, but that deployment strategy matters. If tools are paired with task design, review practices, and training that let junior developers convert assistance into completed work, the distributional effects of adoption may be broader than many skeptics assume. For researchers, the implication is equally direct: the right question is not only whether AI raises productivity, but also whose productivity becomes more visible, measurable, and valuable after adoption.

The next step is to carry this same design into observed organizational data. Doing so would allow the paper’s central claim to be tested under genuine institutional variation, where the equalization and concentration hypotheses can be judged against real teams rather than a carefully constructed simulation.

## Appendix

### Reproducibility steps

To reproduce the full analysis from the repository root, create or activate the project environment, install the required Python packages, regenerate the synthetic panel, and rerun the analysis scripts in sequence:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas statsmodels linearmodels scikit-learn
python scripts/step2_synthetic_pipeline.py --seed 20260309 --n-teams 48 --n-weeks 30
python scripts/step3_eda.py
python scripts/step4_baseline_model.py
python scripts/step5_robustness.py
python scripts/step6_dynamic_check.py
```

The synthetic build used in this paper relies on seed `20260309`, 48 teams, and 30 weeks. The resulting dataset contains 1,440 team-week observations, with 34 adopting teams and 14 never-adopting teams.

### Evidence links

- Project overview: [`README.md`](../README.md)
- Problem framing: [`docs/STEP1_problem_framing.md`](./STEP1_problem_framing.md)
- Data construction and variable definitions: [`docs/STEP2_data_extraction_spec.md`](./STEP2_data_extraction_spec.md), [`docs/STEP2_preanalysis_lock.md`](./STEP2_preanalysis_lock.md), [`outputs/step2_data_dictionary.csv`](../outputs/step2_data_dictionary.csv), [`outputs/step2_generation_metadata.json`](../outputs/step2_generation_metadata.json)
- Descriptive evidence: [`docs/STEP3_eda_note.md`](./STEP3_eda_note.md), [`outputs/step3_eda_summary_stats.csv`](../outputs/step3_eda_summary_stats.csv), [`outputs/step3_eda_treated_comparison.csv`](../outputs/step3_eda_treated_comparison.csv)
- Baseline model: [`docs/STEP4_baseline_model_note.md`](./STEP4_baseline_model_note.md), [`outputs/step4_baseline_results.csv`](../outputs/step4_baseline_results.csv), [`outputs/step4_baseline_model_summary.txt`](../outputs/step4_baseline_model_summary.txt)
- Robustness checks: [`docs/STEP5_robustness_note.md`](./STEP5_robustness_note.md), [`outputs/step5_robustness_results.csv`](../outputs/step5_robustness_results.csv), [`outputs/step5_robustness_model_summaries.txt`](../outputs/step5_robustness_model_summaries.txt)
- Dynamic timing check: [`docs/STEP6_dynamic_check_note.md`](./STEP6_dynamic_check_note.md), [`outputs/step6_event_study_coefficients.csv`](../outputs/step6_event_study_coefficients.csv), [`outputs/step6_event_study_pretrend_test.csv`](../outputs/step6_event_study_pretrend_test.csv), [`outputs/step6_event_study_summary.txt`](../outputs/step6_event_study_summary.txt)

### Citations

This executive summary synthesizes evidence from the repository’s finalized materials, especially the Step 1 framing document, the Step 2 data and pre-analysis documentation, the Step 3 exploratory note, the Step 4 baseline model note, the Step 5 robustness note, the Step 6 dynamic check note, and the associated output files listed above. All quantitative claims in the summary are drawn directly from those documents and outputs.