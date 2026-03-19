# Step 5 — Robustness Checks Note

## Scope
Step 5 tests whether the Step 4 positive treatment estimate is sensitive to outcome definition, weighting, outlier handling, and a short pre-adoption placebo window.

## Artifacts
- `outputs/step5_robustness_results.csv`
- `outputs/step5_robustness_model_summaries.txt`

## Checks and results
All models include team and week fixed effects with team-clustered standard errors.

1. **Alternate outcome: `junior_merged_pr_share`**
   - `treated` = **0.0502** (p = 0.0031)
2. **Alternate outcome: `junior_ticket_share`**
   - `treated` = **0.0692** (p < 0.001)
3. **Weighted by `total_output`**
   - `treated` = **0.0584** (p < 0.001)
4. **Winsorized outcome (1st/99th percentile)**
   - `treated` = **0.0599** (p < 0.001)
5. **Placebo lead window (`lead4_treated`)**
   - `treated` = **0.0637** (p < 0.001)
   - `lead4_treated` = **0.0055** (p = 0.556)

## Interpretation
The treatment effect remains positive and stable across practical specification changes. The placebo lead term is small and statistically weak, which supports the Step 4 direction in this synthetic panel.
