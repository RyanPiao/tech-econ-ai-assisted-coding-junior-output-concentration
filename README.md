# AI-Assisted Coding Adoption and Junior Output Concentration

Publication-facing economics working-paper package with a deterministic, end-to-end pipeline.

## Research question
How is team-level adoption of AI coding assistance associated with the share of measurable output produced by junior developers?

## What this repository does
1. Ingests and cleans available **real-data proxy moments** from a pilot panel (`data/raw/real_proxy/...`).
2. Builds a **synthetic team-week panel calibrated to those benchmark moments**.
3. Runs baseline and robustness panel specifications with team-clustered standard errors.
4. Produces manuscript-ready figures/tables and supporting documentation for replication and writing.

## Interpretation guardrails
- This package does **not** claim direct causal identification from the real proxy pilot data.
- If key timing moments are not identified in the raw panel (e.g., no observed adoption switches), the pipeline uses explicitly labeled placeholders.
- Results should be interpreted as calibrated, design-conditional evidence that can guide further data collection and model refinement.

## Repository structure
```text
.
├── data/
│   ├── raw/
│   ├── processed/
│   └── synthetic/
├── src/
├── scripts/
├── outputs/
│   ├── figures/
│   └── tables/
├── paper/
├── docs/
└── archive/
```

## One-command run (from clean clone)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
make all
```

Alternative orchestrator command:
```bash
python3 scripts/run_pipeline.py
```

## Claim-to-artifact map
| Claim | Artifact(s) |
|---|---|
| Benchmark moments and placeholder logic are explicit | `data/processed/benchmark_moments.csv`, `data/processed/benchmark_moments_metadata.json` |
| Synthetic data are calibrated to benchmark moments | `data/synthetic/synthetic_calibration_diagnostics.csv`, `data/synthetic/synthetic_calibration_metadata.json` |
| Baseline FE estimate for treatment association | `outputs/tables/table_baseline_results.csv`, `outputs/tables/table_baseline_model_summary.txt` |
| Robustness and sensitivity checks | `outputs/tables/table_robustness_results.csv`, `outputs/tables/table_robustness_model_summaries.txt` |
| Dynamic/event-time pattern and pretrend diagnostic | `outputs/tables/table_event_study_coefficients.csv`, `outputs/tables/table_event_study_metadata.json`, `outputs/tables/table_event_study_summary.txt`, `outputs/figures/figure_3_event_study.png` |
| Sample composition and treatment-timing visuals | `outputs/tables/table_a1_descriptive_stats.csv`, `outputs/figures/figure_1_adoption_timing_histogram.png`, `outputs/figures/figure_2_group_trends.png` |
| Identification caveats and recommended language | `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md` |

## Main scripts (execution order)
1. `scripts/01_prepare_benchmark_moments.py`
2. `scripts/02_generate_synthetic_data.py`
3. `scripts/03_run_baseline_analysis.py`
4. `scripts/04_run_robustness_checks.py`
5. `scripts/05_generate_figures_tables.py`

## Documentation index
- Replication: `docs/REPLICATION_GUIDE.md`
- Methods, assumptions, limitations, identification caveats: `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`
- Audit + restructure log: `docs/AUDIT_AND_RESTRUCTURE_REPORT.md`
- Writer handoff memo: `docs/WRITER_HANDOFF_MEMO.md`
- Working-paper draft: `paper/working_paper_draft.md`

## Legacy materials
Pre-rebuild step-by-step artifacts were moved to:
`archive/legacy_pre_rebuild_20260319/`
