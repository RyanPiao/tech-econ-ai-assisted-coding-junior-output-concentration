# Synthetic Materials Scope (Appendix-Only)

Synthetic scripts are retained for mechanism illustration and robustness sandboxing only.

## Not allowed
- Do **not** use synthetic outputs for any primary estimate or headline claim.
- Do **not** mix synthetic coefficients into baseline, robustness, or event-study tables in the main text.

## Allowed
- Appendix-only sensitivity/mechanism demonstrations with explicit synthetic labeling.

## Scripts
- `scripts/appendix_synthetic/01_prepare_benchmark_moments.py`
- `scripts/appendix_synthetic/02_generate_synthetic_data.py`

## Reporting requirement
Any synthetic appendix result must include a note: "Synthetic, calibration-dependent, non-primary evidence."
