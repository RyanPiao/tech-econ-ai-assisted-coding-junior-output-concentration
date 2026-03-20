# Audit and Restructure Report

Date: 2026-03-19 (updated real-data-first conversion)

## 1) Main conversion decision
Repository was converted from a synthetic-first estimation package to a **real-data-first** package.

## 2) Structural changes
- Primary pipeline now runs only real-data scripts:
  - `scripts/01_prepare_real_panel.py`
  - `scripts/02_run_baseline_analysis.py`
  - `scripts/03_run_robustness_checks.py`
  - `scripts/04_generate_figures_tables.py`
- `Makefile` and `scripts/run_pipeline.py` updated to exclude synthetic steps from core flow.
- Synthetic scripts moved to `scripts/appendix_synthetic/` and labeled appendix-only.

## 3) Data changes
- Added expanded observed panel:
  - `data/raw/real_proxy/repo_week_panel_q1_2025_expanded.csv`
  - matching metadata and dictionary files.
- Primary processed artifact changed to:
  - `data/processed/real_panel_clean.csv`
  - `data/processed/real_panel_metadata.json`

## 4) Documentation rewrite
Main narrative docs rewritten for real-data-first framing:
- `README.md`
- `docs/REPLICATION_GUIDE.md`
- `docs/METHODS_ASSUMPTIONS_LIMITATIONS.md`
- `docs/WRITER_HANDOFF_MEMO.md`
- `paper/working_paper_draft.md`
- Added `docs/APPENDIX_SYNTHETIC_SCOPE.md`

## 5) Identification status after conversion
The real-data panel includes switchers, but timing support is concentrated and pretrend lead cells are sparse. Claims were downgraded to conservative associational language and explicit identification diagnostics were added.
