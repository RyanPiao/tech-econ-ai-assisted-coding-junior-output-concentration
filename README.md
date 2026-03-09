# Tech-Econ Study: AI-Assisted Coding Adoption × Junior-Developer Output Concentration

Canonical project repo for approved topic:
`tech-econ-ai-assisted-coding-junior-output-concentration`

## Status
- ✅ Step 1: problem framing
- ✅ Step 2: synthetic data-generation + ingestion pipeline complete
- ⏳ Step 3: pending
- ⏳ Step 4: pending
- ⏳ Step 5: pending
- ⏳ Step 6: pending
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

## Step 2 artifacts
### Script
- `scripts/step2_synthetic_pipeline.py`

### Documentation
- `docs/STEP2_data_extraction_spec.md`
- `docs/STEP2_preanalysis_lock.md`

### Generated outputs
- `outputs/step2_synthetic_team_role_week.csv`
- `outputs/step2_team_week_panel.csv`
- `outputs/step2_data_dictionary.csv`
- `outputs/step2_generation_metadata.json`

## Reproduce Step 2
From repo root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas
python scripts/step2_synthetic_pipeline.py --seed 20260309 --n-teams 48 --n-weeks 30
```

This command sequence regenerates all Step 2 output artifacts in `outputs/` from a clean local environment.

If you already have the virtual environment created, the short form is:

```bash
. .venv/bin/activate
python scripts/step2_synthetic_pipeline.py --seed 20260309 --n-teams 48 --n-weeks 30
```
