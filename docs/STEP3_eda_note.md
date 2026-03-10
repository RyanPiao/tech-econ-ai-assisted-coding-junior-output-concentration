# Step 3 — Exploratory Data Analysis Note

## Scope
Step 3 validates panel shape, treatment timing coverage, and outcome distributions before formal modeling.

## Artifacts
- `outputs/step3_eda_summary_stats.csv`
- `outputs/step3_eda_treated_comparison.csv`
- `outputs/step3_eda_adoption_timing.csv`
- `outputs/step3_eda_event_time_counts.csv`
- `outputs/step3_eda_correlation_matrix.csv`
- `outputs/step3_eda_snapshot.json`

## Key checks
- Panel size: **1,440** team-week rows (**48 teams × 30 weeks**).
- Team-level adoption rate: **70.8%** (34 adopters, 14 never adopters).
- Mean `junior_output_share`: **0.520**.
- Mean `junior_output_share` by treatment status:
  - untreated: **0.508**
  - treated: **0.539**
- Mean `total_output` by treatment status:
  - untreated: **31.58**
  - treated: **35.73**
- Analysis-sample coverage: **100%** of rows satisfy Step 2 sample filter.

## Interpretation for next step
EDA is consistent with the synthetic design lock from Step 2: treatment and outcome vary over time, adoption is staggered, and treated observations show a modestly higher junior share in raw comparisons. This supports moving to fixed-effects estimation in Step 4.
