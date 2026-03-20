PYTHON ?= python3

.PHONY: all prepare baseline robustness figures diagnostics v3-fetch v3-sweep v3-all clean appendix-synthetic

all: prepare baseline robustness figures diagnostics

prepare:
	$(PYTHON) scripts/01_prepare_real_panel.py

baseline: prepare
	$(PYTHON) scripts/02_run_baseline_analysis.py

robustness: baseline
	$(PYTHON) scripts/03_run_robustness_checks.py

figures: robustness
	$(PYTHON) scripts/04_generate_figures_tables.py

diagnostics: figures
	$(PYTHON) scripts/05_build_expansion_diagnostics.py

# V3 long-horizon identification sweep (real-data-first)
v3-fetch:
	$(PYTHON) scripts/00_fetch_long_horizon_panel.py

v3-sweep:
	$(PYTHON) scripts/06_run_v3_identification_sweep.py

v3-all:
	$(PYTHON) scripts/run_v3_pipeline.py

# Optional appendix-only synthetic workflow (not used for primary claims)
appendix-synthetic:
	$(PYTHON) scripts/appendix_synthetic/01_prepare_benchmark_moments.py
	$(PYTHON) scripts/appendix_synthetic/02_generate_synthetic_data.py

clean:
	rm -f data/processed/real_panel_clean.csv \
		data/processed/real_panel_metadata.json \
		data/raw/real_proxy/repo_week_panel_v3_long_h18.csv \
		data/raw/real_proxy/repo_week_panel_v3_long_h18_metadata.json \
		data/raw/real_proxy/repo_week_panel_v3_long_h18_dictionary.csv \
		outputs/tables/*.csv outputs/tables/*.txt outputs/tables/*.json \
		outputs/figures/*.png
