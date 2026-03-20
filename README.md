# AI-Assisted Coding and Junior Output Concentration (Real-Data-First)

This repository is a publication-facing economics package where **all core estimates come from observed data**.

## Research question
How is a repo-week proxy for AI-assisted coding adoption associated with the junior share of observable output?

## Economic framing (applied micro + innovation)
The project studies a distributional technology-adoption question: whether AI-tool adoption periods are associated with shifts in within-team contribution shares, rather than only changes in aggregate output. The current version is an **identification-limited associational baseline** designed to be transparent, reproducible, and explicit about inference limits.

## Real-data-first design
Primary pipeline (core claims):
1. Ingest and clean observed GH Archive–derived repo-week panel.
2. Construct transparent treatment proxy from observed AI-signal intensity.
3. Construct outcomes and controls from observed fields only.
4. Run baseline TWFE model (team FE + week FE, clustered by team).
5. Run robustness checks and event-study diagnostics on observed data.
6. Export tables/figures and identification diagnostics.

No synthetic data are used in core estimates.

## Interpretation guardrails
- Treat estimates as **proxy-based associations**, not causal effects.
- Keep identification diagnostics alongside all coefficient reporting.
- Use conservative language: “associated with,” “suggestive,” “identification-limited.”

## Primary data source
- `data/raw/real_proxy/repo_week_panel_q2_2025_more_data.csv`
- Metadata: `data/raw/real_proxy/repo_week_panel_q2_2025_more_data_metadata.json`
- Dictionary: `data/raw/real_proxy/repo_week_panel_q2_2025_more_data_dictionary.csv`

The panel is derived from public GH Archive events for a fixed repo list and fixed sampling configuration (see metadata JSON).

## Treatment proxy definition (primary)
Repo-week `ai_proxy_trigger = 1` iff:
- `ai_intensity >= 0.02`, and
- `ai_signal_events >= 2`, and
- `ai_eligible_events > 0`.

Team-level `adoption_week` is the first week with `ai_proxy_trigger = 1` (with a week-1 burn-in shift to week 2 when week 2 exists); `treated = 1` for weeks `>= adoption_week`.

## One-command run (from clean clone)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
make all
```

Alternative orchestrator:
```bash
python3 scripts/run_pipeline.py
```

## V3 long-horizon identification sweep (multi-proxy × multi-method)
This repo now includes a publication-facing v3 sweep that keeps the same real-data-first principle while expanding identification diagnostics.

### Reproducible run
```bash
# Full run: fetch long-horizon panel + run sweep
python3 scripts/run_v3_pipeline.py

# Or split steps
python3 scripts/00_fetch_long_horizon_panel.py
python3 scripts/06_run_v3_identification_sweep.py
```

### Key v3 artifacts
- `data/raw/real_proxy/repo_week_panel_v3_long_h18.csv`
- `data/raw/real_proxy/repo_week_panel_v3_long_h18_metadata.json`
- `outputs/tables/table_v3_horizon_data_expansion.csv`
- `outputs/tables/table_v3_proxy_definitions.csv`
- `outputs/tables/table_v3_identification_sweep_results.csv`
- `outputs/tables/table_v3_event_study_coefficients.csv`
- `outputs/tables/table_v3_defensibility_ranking.csv`
- `outputs/tables/table_v3_identification_summary.json`

Interpretation guardrail remains unchanged: these are proxy-based associational diagnostics, not causal proof.

## Claim-to-artifact map
| Claim | Artifact(s) |
|---|---|
| Real-data cleaning + treatment-proxy construction is explicit | `data/processed/real_panel_clean.csv`, `data/processed/real_panel_metadata.json` |
| Baseline TWFE estimate on observed data | `outputs/tables/table_baseline_results.csv`, `outputs/tables/table_baseline_model_summary.txt` |
| Robustness results on observed data | `outputs/tables/table_robustness_results.csv`, `outputs/tables/table_robustness_model_summaries.txt` |
| Dynamic/event-time diagnostics on observed data | `outputs/tables/table_event_study_coefficients.csv`, `outputs/tables/table_event_study_metadata.json`, `outputs/tables/table_event_study_summary.txt`, `outputs/figures/figure_3_event_study.png` |
| Identification strength diagnostics (switchers/timing support) | `outputs/tables/table_identification_diagnostics.csv`, `outputs/tables/table_identification_timing_coverage.csv`, `outputs/tables/table_sample_expansion_diagnostics.csv` |
| Sample composition and descriptive stats | `outputs/tables/table_a1_descriptive_stats.csv`, `outputs/figures/figure_1_adoption_timing_histogram.png`, `outputs/figures/figure_2_group_trends.png` |
| Methods, assumptions, and limitations language | `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md` |
| Writer-ready narrative summary and framing | `docs/WRITER_HANDOFF_MEMO.md`, `paper/working_paper_draft.md` |

## Main scripts (execution order)
1. `scripts/01_prepare_real_panel.py`
2. `scripts/02_run_baseline_analysis.py`
3. `scripts/03_run_robustness_checks.py`
4. `scripts/04_generate_figures_tables.py`
5. `scripts/05_build_expansion_diagnostics.py`

## Documentation index
- Replication: `docs/REPLICATION_GUIDE.md`
- Methods/assumptions/limitations: `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`
- Writer handoff memo: `docs/WRITER_HANDOFF_MEMO.md`
- Working paper draft: `paper/working_paper_draft.md`
- Synthetic appendix boundary: `docs/APPENDIX_SYNTHETIC_SCOPE.md`

## Next-step research design priorities
- Extend panel horizon and switcher support.
- Improve treatment measurement with direct usage telemetry (or validation sample) where feasible.
- Pre-specify minimum event-time support and outcome hierarchy for stronger inferential discipline.

## Appendix-only synthetic materials
Synthetic scripts are retained **only for appendix/mechanism exercises**:
- `scripts/appendix_synthetic/01_prepare_benchmark_moments.py`
- `scripts/appendix_synthetic/02_generate_synthetic_data.py`

They are not part of `make all` and must not be used for core claims.
