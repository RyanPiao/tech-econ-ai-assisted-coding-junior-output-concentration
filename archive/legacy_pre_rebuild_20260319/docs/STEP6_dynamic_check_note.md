# Step 6 — Dynamic Check (Event-Study Style) Note

## Scope
Step 6 adds a dynamic check around adoption timing using event-time indicators with team and week fixed effects.

## Specification
- Outcome: `junior_output_share`
- Event window: leads \(-6\) to lags \(+8\)
- Omitted reference period: event time \(-1\)
- Additional bins: far leads and far lags
- Estimator: `statsmodels.OLS` with team-clustered covariance

## Artifacts
- `outputs/step6_event_study_coefficients.csv`
- `outputs/step6_event_study_pretrend_test.csv`
- `outputs/step6_event_study_metadata.json`
- `outputs/step6_event_study_summary.txt`

## Findings
- Joint pretrend test on leads \(-6\) through \(-2\):
  - p-value = **0.901**
- Average post-adoption coefficient across event times \(0\) to \(8\):
  - **0.0534**
- Most post-adoption coefficients are positive; several are statistically distinguishable from zero (notably event times 1, 2, 3, 4, 6, and 8).

## Interpretation
The dynamic check is directionally consistent with Step 4 and Step 5: no visible pre-adoption pattern in the selected lead window and a positive post-adoption shift in junior output share.
