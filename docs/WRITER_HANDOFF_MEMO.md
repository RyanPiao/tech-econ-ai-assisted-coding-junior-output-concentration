# Writer Handoff Memo (Real-Data-First Version)

## 1) Study purpose (one paragraph)
This package estimates the association between a real-data proxy for repo-week AI-assistance adoption and junior developers’ share of observable output. All core estimates now come from observed GH Archive–derived panel data; synthetic outputs are removed from the main narrative and restricted to appendix-only scope.

## 2) Data architecture (observed only for core analysis)
- Raw real panel: `data/raw/real_proxy/repo_week_panel_q1_2025_expanded.csv`
- Raw metadata: `data/raw/real_proxy/repo_week_panel_q1_2025_expanded_metadata.json`
- Cleaned analysis panel: `data/processed/real_panel_clean.csv`
- Panel metadata + identification diagnostics: `data/processed/real_panel_metadata.json`

## 3) Estimation setup (main text)
- Baseline: TWFE (team FE + week FE), team-clustered SE.
- Outcome: `junior_output_share`.
- Treatment: `treated` from proxy adoption timing (`ai_intensity >= 0.02` and `ai_signal_events >= 2`).
- Baseline controls: `log_total_output`, `post_merge_bug_proxy_filled`.
- Robustness: no-controls variant, full-controls variant, alternative outcomes, winsorized outcome, placebo lead, high-output subsample.
- Dynamic: event-study with lead max 3, lag max 4.

## 4) Core quantitative results (current run)
### Baseline
- Treated coefficient: **-0.0729**
- SE: **0.0957**
- p-value: **0.446**
- 95% CI: **[-0.2605, 0.1148]**
- N: **68 team-weeks**, **9 teams**, **11 weeks**

Artifact: `outputs/tables/table_baseline_results.csv`

### Robustness snapshot
- No-controls: -0.0179 (p=0.767)
- Full-controls: -0.0489 (p=0.666)
- Alt merged-PR-share: +0.0149 (p=0.808)
- Alt ticket-share: -0.0699 (p=0.300)
- Placebo lead term: -0.4620 (p<0.001) [diagnostic concern]

Artifact: `outputs/tables/table_robustness_results.csv`

### Dynamic and identification diagnostics
- Joint pretrend p-value: **3.68e-06**
- Lead support is sparse (event -3: 1 observation, event -2: 1 observation)
- Switchers: **5 teams**
- Adoption timing clustered at week 2 (4 teams) and week 6 (1 team)

Artifacts:
- `outputs/tables/table_event_study_metadata.json`
- `outputs/tables/table_identification_diagnostics.csv`
- `outputs/tables/table_identification_timing_coverage.csv`

## 5) Interpretation discipline for text
Recommended: “proxy-based association”, “identification-limited”, “not causally identified in current sample”.
Avoid: causal verbs and definitive welfare/productivity conclusions.

## 6) Synthetic boundary (appendix only)
If synthetic material is included, explicitly place it in appendix and cite:
`docs/APPENDIX_SYNTHETIC_SCOPE.md`
