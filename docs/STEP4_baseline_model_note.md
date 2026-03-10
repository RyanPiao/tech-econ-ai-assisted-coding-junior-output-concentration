# Step 4 — Baseline Econometric Model Note

## Model
Two-way fixed-effects panel model on the Step 2 analysis sample:

\[
\text{junior\_output\_share}_{it} = \beta \cdot \text{treated}_{it} + \alpha_i + \gamma_t + \varepsilon_{it}
\]

- Team fixed effects: \(\alpha_i\)
- Week fixed effects: \(\gamma_t\)
- Standard errors: clustered at team level
- Estimator: `linearmodels.PanelOLS`

## Artifacts
- `outputs/step4_baseline_results.csv`
- `outputs/step4_baseline_model_summary.txt`

## Result snapshot
- Outcome: `junior_output_share`
- `treated` coefficient: **0.0609**
- Clustered SE: **0.0109**
- p-value: **3.14e-08**
- 95% CI: **[0.0394, 0.0824]**
- Observations: **1,440**

## Interpretation
The baseline specification estimates a positive and statistically precise treatment effect: after adoption, junior output share rises by roughly **6.1 percentage points** on average in this synthetic panel.
