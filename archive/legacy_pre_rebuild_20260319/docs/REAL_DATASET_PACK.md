# Real Dataset Pack (v0)

Prepared for extending the synthetic pipeline to public real-world data.

## Goal
Build a team-week panel to estimate whether AI coding-assistant adoption changes:
1) junior output share, and
2) quality-adjusted productivity.

## Source A — GitHub public activity (productivity outcomes)
- Site: https://www.gharchive.org/
- Raw files: `https://data.gharchive.org/YYYY-MM-DD-HH.json.gz`
- Use for: PR events, issue events, push activity, review timing, merge timing.
- Unit (proposed): `repo-week` (or `team-week` if team mapping available).

## Source B — AI-adoption proxy from observed developer behavior
- Repo: https://github.com/NAIST-SE/DevGPT
- Paper: https://arxiv.org/abs/2309.03914
- Use for: identifying repos/dev contexts where ChatGPT shared-link usage appears in PR/issues/commits.
- Role: treatment timing / intensity proxy for AI-assisted workflow adoption.

## Source C — External validation benchmark (self-reported productivity)
- 2024 survey: https://survey.stackoverflow.co/2024/
- Role: calibration/sanity check for direction/magnitude, not causal identification in our panel.

## Proposed merged dataset design

### Primary panel keys
- `repo_id`
- `week_start`

### Core outcomes
- `junior_pr_share` (share of merged PRs authored by juniors)
- `junior_commit_share`
- `merge_count`
- `median_cycle_time_hours`
- `review_latency_hours`
- `post_merge_bug_proxy` (e.g., hotfix/rollback labels or quick revert patterns)

### Treatment variables
- `ai_adopted_it` (0/1 after inferred adoption week)
- `ai_intensity_it` (share of repo-week events with AI-use proxy mention)

### Controls
- repo FE, week FE
- release window indicators
- backlog pressure proxy (open issues)
- task-mix proxies (labels/tags)

## Identification plan
- Event-study + DiD with repo and week fixed effects.
- Staggered adoption estimators (Sun-Abraham / Callaway-Sant'Anna style) if adoption timing differs by repo.
- Require pre-trend checks before interpreting post effects.

## Caveats
- Public data only gives proxy AI adoption, not direct internal-seat usage.
- Team/junior classification may need heuristics (tenure in repo, first-contribution date, etc.).

## Immediate next implementation step
Create `scripts/step2_real_pipeline.py` to:
1) ingest a scoped GH Archive window,
2) derive repo-week productivity outcomes,
3) ingest AI-proxy signals,
4) output `outputs/step2_real_repo_week_panel.csv`.
