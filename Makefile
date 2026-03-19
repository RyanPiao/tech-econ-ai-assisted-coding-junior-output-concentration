PYTHON ?= python3

.PHONY: all benchmark synthetic baseline robustness figures clean

all: benchmark synthetic baseline robustness figures

benchmark:
	$(PYTHON) scripts/01_prepare_benchmark_moments.py

synthetic: benchmark
	$(PYTHON) scripts/02_generate_synthetic_data.py

baseline: synthetic
	$(PYTHON) scripts/03_run_baseline_analysis.py

robustness: baseline
	$(PYTHON) scripts/04_run_robustness_checks.py

figures: robustness
	$(PYTHON) scripts/05_generate_figures_tables.py

clean:
	rm -f data/processed/benchmark_panel_clean.csv \
		data/processed/benchmark_moments.csv \
		data/processed/benchmark_moments_metadata.json \
		data/synthetic/synthetic_team_week_panel.csv \
		data/synthetic/synthetic_calibration_metadata.json \
		data/synthetic/synthetic_calibration_diagnostics.csv \
		outputs/tables/*.csv outputs/tables/*.txt outputs/tables/*.json \
		outputs/figures/*.png
