# Tech-Econ Study: AI-Assisted Coding Adoption × Junior-Developer Output Concentration

Canonical project repo for approved topic:
`tech-econ-ai-assisted-coding-junior-output-concentration`

## Status
- ✅ Step 1: problem framing
- ✅ Step 2: synthetic data-generation + ingestion pipeline
- ✅ Step 3: EDA artifacts and note
- ✅ Step 4: baseline econometric model and note
- ✅ Step 5: robustness checks and note
- ✅ Step 6: dynamic event-time check and note
- ⏳ Step 7: pending

## Research question
Does team-level adoption of AI coding assistance change how output is distributed between junior and senior developers?

## Core variables
- **Outcome variable:** share of merged commits or completed tickets attributable to junior developers
- **Treatment variable:** team-level adoption of AI coding assistance

## Data type
Synthetic

## Data note
This project uses a synthetic dataset for the current research cycle so the design, variables, and empirical workflow can be developed cleanly before any future extension to public real-world data.

## Repository structure
```text
.
├── README.md
├── docs/
├── notebooks/
├── outputs/
└── scripts/
```

## Step artifacts

### Step 2
- Script: `scripts/step2_synthetic_pipeline.py`
- Docs:
  - `docs/STEP2_data_extraction_spec.md`
  - `docs/STEP2_preanalysis_lock.md`
- Outputs:
  - `outputs/step2_synthetic_team_role_week.csv`
  - `outputs/step2_team_week_panel.csv`
  - `outputs/step2_data_dictionary.csv`
  - `outputs/step2_generation_metadata.json`

### Step 3
- Script: `scripts/step3_eda.py`
- Doc: `docs/STEP3_eda_note.md`
- Outputs:
  - `outputs/step3_eda_summary_stats.csv`
  - `outputs/step3_eda_treated_comparison.csv`
  - `outputs/step3_eda_adoption_timing.csv`
  - `outputs/step3_eda_event_time_counts.csv`
  - `outputs/step3_eda_correlation_matrix.csv`
  - `outputs/step3_eda_snapshot.json`

### Step 4
- Script: `scripts/step4_baseline_model.py`
- Doc: `docs/STEP4_baseline_model_note.md`
- Outputs:
  - `outputs/step4_baseline_results.csv`
  - `outputs/step4_baseline_model_summary.txt`

### Step 5
- Script: `scripts/step5_robustness.py`
- Doc: `docs/STEP5_robustness_note.md`
- Outputs:
  - `outputs/step5_robustness_results.csv`
  - `outputs/step5_robustness_model_summaries.txt`

### Step 6
- Script: `scripts/step6_dynamic_check.py`
- Doc: `docs/STEP6_dynamic_check_note.md`
- Outputs:
  - `outputs/step6_event_study_coefficients.csv`
  - `outputs/step6_event_study_pretrend_test.csv`
  - `outputs/step6_event_study_metadata.json`
  - `outputs/step6_event_study_summary.txt`

## Reproduction
From repo root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas statsmodels linearmodels scikit-learn
python scripts/step2_synthetic_pipeline.py --seed 20260309 --n-teams 48 --n-weeks 30
python scripts/step3_eda.py
python scripts/step4_baseline_model.py
python scripts/step5_robustness.py
python scripts/step6_dynamic_check.py
```

If the environment already exists, use:

```bash
. .venv/bin/activate
python scripts/step2_synthetic_pipeline.py --seed 20260309 --n-teams 48 --n-weeks 30
python scripts/step3_eda.py
python scripts/step4_baseline_model.py
python scripts/step5_robustness.py
python scripts/step6_dynamic_check.py
```
