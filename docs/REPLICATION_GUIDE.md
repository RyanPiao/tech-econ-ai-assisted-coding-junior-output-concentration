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
python3 scripts/05_build_expansion_diagnostics.py
```

## V3 long-horizon identification sweep

### Option A: single command
```bash
python3 scripts/run_v3_pipeline.py
```

### Option B: explicit sequence
```bash
python3 scripts/00_fetch_long_horizon_panel.py
python3 scripts/06_run_v3_identification_sweep.py
```

### Makefile shortcuts
```bash
make v3-fetch
make v3-sweep
make v3-all
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
- `outputs/tables/table_sample_expansion_diagnostics.csv`

### Figures
- `outputs/figures/figure_1_adoption_timing_histogram.png`
- `outputs/figures/figure_2_group_trends.png`
- `outputs/figures/figure_3_event_study.png`

### V3 long-horizon sweep outputs
- `data/raw/real_proxy/repo_week_panel_v3_long_h18.csv`
- `data/raw/real_proxy/repo_week_panel_v3_long_h18_metadata.json`
- `data/raw/real_proxy/repo_week_panel_v3_long_h18_dictionary.csv`
- `outputs/tables/table_v3_horizon_data_expansion.csv`
- `outputs/tables/table_v3_proxy_definitions.csv`
- `outputs/tables/table_v3_identification_sweep_results.csv`
- `outputs/tables/table_v3_event_study_coefficients.csv`
- `outputs/tables/table_v3_defensibility_ranking.csv`
- `outputs/tables/table_v3_identification_summary.json`

## Determinism notes
- Primary pipeline is deterministic conditional on included raw input files.
- Dependency versions are pinned in `requirements.txt`.
- If you refresh the raw data from GH Archive (outside the primary pipeline), record the exact fetch window, repo list, and thresholds in the raw metadata JSON.
