# Replication Guide (Real-Data-First)

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
python3 scripts/01_prepare_real_panel.py
python3 scripts/02_run_baseline_analysis.py
python3 scripts/03_run_robustness_checks.py
python3 scripts/04_generate_figures_tables.py
```

## Expected generated files

### Processed real-data layer
- `data/processed/real_panel_clean.csv`
- `data/processed/real_panel_metadata.json`

### Tables
- `outputs/tables/table_baseline_results.csv`
- `outputs/tables/table_baseline_model_summary.txt`
- `outputs/tables/table_robustness_results.csv`
- `outputs/tables/table_robustness_model_summaries.txt`
- `outputs/tables/table_a1_descriptive_stats.csv`
- `outputs/tables/table_identification_diagnostics.csv`
- `outputs/tables/table_identification_timing_coverage.csv`
- `outputs/tables/table_event_study_coefficients.csv`
- `outputs/tables/table_event_study_metadata.json`
- `outputs/tables/table_event_study_summary.txt`

### Figures
- `outputs/figures/figure_1_adoption_timing_histogram.png`
- `outputs/figures/figure_2_group_trends.png`
- `outputs/figures/figure_3_event_study.png`

## Determinism notes
- Primary pipeline is deterministic conditional on included raw input files.
- Dependency versions are pinned in `requirements.txt`.
- If you refresh the raw data from GH Archive (outside the primary pipeline), record the exact fetch window, repo list, and thresholds in the raw metadata JSON.
