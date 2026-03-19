# Audit and Restructure Report

Date: 2026-03-19

## 1) Audit findings from pre-rebuild repository

### Structural issues
- Flat, step-numbered layout (`scripts/stepX_...`, `outputs/stepX_...`) mixed production artifacts with temporary experiments.
- No canonical `data/raw -> data/processed -> data/synthetic` flow.
- No single deterministic run target from clean clone.

### Stale or potentially misleading artifacts
- Multiple temp output directories (`outputs/tmp_smoke`, `outputs/tmp_test*`) with unclear status.
- Legacy outputs and notes coexisted without a clear statement of canonical vs exploratory results.
- Real-proxy pilot panel had sparse support and no observed adoption switches, but this limitation was not surfaced as a calibration blocker in a centralized benchmark protocol.

### Reproducibility gaps
- Dependency install instructions were unpinned.
- No explicit benchmark-moment extraction stage before synthetic calibration.
- No consolidated replication guide with expected output list.

## 2) Restructure actions implemented

### New research architecture
- Added canonical directories:
  - `data/raw`, `data/processed`, `data/synthetic`
  - `src/`
  - `outputs/figures`, `outputs/tables`
  - `paper/`
  - `docs/`
  - `scripts/`

### Legacy cleanup
- Moved old step-based docs/scripts/outputs into:
  - `archive/legacy_pre_rebuild_20260319/`
- Cleared non-canonical temporary output directories from active `outputs/`.

### Pipeline rebuild
- Introduced sequential scripts for:
  - benchmark moment preparation
  - synthetic calibration
  - baseline analysis
  - robustness checks
  - figure/table export
- Added reproducible orchestration via `Makefile` and `scripts/run_pipeline.py`.

## 3) Remaining caveat after restructure
- The currently included real proxy pilot panel is sparse and does not identify adoption-timing moments directly.
- Pipeline addresses this transparently with explicit placeholders recorded in `benchmark_moments_metadata.json`.
