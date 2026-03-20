# Source note for real proxy panels

## Primary panel used by main pipeline
- `repo_week_panel_q1_2025_expanded.csv`
- `repo_week_panel_q1_2025_expanded_metadata.json`
- `repo_week_panel_q1_2025_expanded_dictionary.csv`

This panel was generated from public GH Archive events (observed data) using the legacy extraction script:
`archive/legacy_pre_rebuild_20260319/scripts/step2_real_pipeline.py`

Generation configuration (see metadata JSON for exact values):
- Window: 2025-01-01 to 2025-03-15
- Repo list: `archive/legacy_pre_rebuild_20260319/scripts/config/expanded_repos.txt`
- Sampling: hourly step = 24, max lines per selected hour = 120000
- Treatment proxy thresholds: `ai_intensity >= 0.02` and `ai_signal_events >= 2`

## Legacy pilot panel (reference only)
- `repo_week_panel_pilot.csv`
- `repo_week_panel_pilot_metadata.json`
- `repo_week_panel_pilot_dictionary.csv`
