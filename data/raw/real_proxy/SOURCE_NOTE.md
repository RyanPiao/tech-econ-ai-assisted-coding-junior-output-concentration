# Source note for real proxy panels

## Primary panel used by main pipeline
- `repo_week_panel_q2_2025_more_data.csv`
- `repo_week_panel_q2_2025_more_data_metadata.json`
- `repo_week_panel_q2_2025_more_data_dictionary.csv`

This panel was generated from public GH Archive events (observed data) using the legacy extraction script:
`archive/legacy_pre_rebuild_20260319/scripts/step2_real_pipeline.py`

Generation configuration (see metadata JSON for exact values):
- Window: 2025-01-01 to 2025-04-30
- Repo list: `data/raw/real_proxy/repo_list_q2_2025_more_data.txt`
- Sampling: hourly step = 24, max lines per selected hour = 120000
- Treatment proxy thresholds: `ai_intensity >= 0.02` and `ai_signal_events >= 2`

## V3 long-horizon panel (identification sweep)
- `repo_week_panel_v3_long_h18.csv`
- `repo_week_panel_v3_long_h18_metadata.json`
- `repo_week_panel_v3_long_h18_dictionary.csv`

Generated from the same public GH Archive extraction code path with an extended window:
- Window: 2023-11-01 to 2025-04-30 (~18 months; 79 weeks)
- Repo list: `data/raw/real_proxy/repo_list_q2_2025_more_data.txt`
- Sampling: hourly step = 24, max lines per selected hour = 120000
- Fetch diagnostics (from metadata): hours requested/successful = 547/547, failed = 0

## Prior expanded panel (reference)
- `repo_week_panel_q1_2025_expanded.csv`
- `repo_week_panel_q1_2025_expanded_metadata.json`
- `repo_week_panel_q1_2025_expanded_dictionary.csv`

## Legacy pilot panel (reference only)
- `repo_week_panel_pilot.csv`
- `repo_week_panel_pilot_metadata.json`
- `repo_week_panel_pilot_dictionary.csv`
