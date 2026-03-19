# Replication Guide

## Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Exact run order

### Option A: single command
```bash
make all
```

### Option B: explicit script sequence
```bash
python3 scripts/01_prepare_benchmark_moments.py
python3 scripts/02_generate_synthetic_data.py
python3 scripts/03_run_baseline_analysis.py
python3 scripts/04_run_robustness_checks.py
python3 scripts/05_generate_figures_tables.py
```

## Expected generated files

### Processed benchmark layer
- `data/processed/benchmark_panel_clean.csv`
- `data/processed/benchmark_moments.csv`
- `data/processed/benchmark_moments_metadata.json`

### Synthetic layer
- `data/synthetic/synthetic_team_week_panel.csv`
- `data/synthetic/synthetic_calibration_diagnostics.csv`
- `data/synthetic/synthetic_calibration_metadata.json`

### Tables
- `outputs/tables/table_baseline_results.csv`
- `outputs/tables/table_baseline_model_summary.txt`
- `outputs/tables/table_robustness_results.csv`
- `outputs/tables/table_robustness_model_summaries.txt`
- `outputs/tables/table_a1_descriptive_stats.csv`
- `outputs/tables/table_event_study_coefficients.csv`
- `outputs/tables/table_event_study_metadata.json`
- `outputs/tables/table_event_study_summary.txt`

### Figures
- `outputs/figures/figure_1_adoption_timing_histogram.png`
- `outputs/figures/figure_2_group_trends.png`
- `outputs/figures/figure_3_event_study.png`

## Determinism notes
- Synthetic generation uses fixed seed (`DEFAULT_SEED = 20260319` unless overridden).
- Dependency versions are pinned in `requirements.txt`.
- If changing seed or sample size, record the change in the paper appendix and rerun full pipeline.
