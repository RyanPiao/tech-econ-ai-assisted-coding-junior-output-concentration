PYTHON ?= python3

.PHONY: all prepare baseline robustness figures clean appendix-synthetic

all: prepare baseline robustness figures

prepare:
	$(PYTHON) scripts/01_prepare_real_panel.py

baseline: prepare
	$(PYTHON) scripts/02_run_baseline_analysis.py

robustness: baseline
	$(PYTHON) scripts/03_run_robustness_checks.py

figures: robustness
	$(PYTHON) scripts/04_generate_figures_tables.py

# Optional appendix-only synthetic workflow (not used for primary claims)
appendix-synthetic:
	$(PYTHON) scripts/appendix_synthetic/01_prepare_benchmark_moments.py
	$(PYTHON) scripts/appendix_synthetic/02_generate_synthetic_data.py

clean:
	rm -f data/processed/real_panel_clean.csv \
		data/processed/real_panel_metadata.json \
		outputs/tables/*.csv outputs/tables/*.txt outputs/tables/*.json \
		outputs/figures/*.png
