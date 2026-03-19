#!/usr/bin/env python3
"""Step 3 EDA artifacts for synthetic team-week panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_VARS = [
    "junior_output_share",
    "junior_merged_pr_share",
    "junior_ticket_share",
    "treated",
    "total_output",
    "total_merged_prs",
    "total_completed_tickets",
    "adoption_week",
    "event_time",
]


def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in KEY_VARS:
        s = df[col]
        rows.append(
            {
                "variable": col,
                "n": int(s.notna().sum()),
                "missing_rate": float(s.isna().mean()),
                "mean": float(s.mean()),
                "std": float(s.std(ddof=1)),
                "min": float(s.min()),
                "p25": float(s.quantile(0.25)),
                "median": float(s.median()),
                "p75": float(s.quantile(0.75)),
                "max": float(s.max()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Step 3 EDA outputs")
    parser.add_argument("--input", default="outputs/step2_team_week_panel.csv")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)

    summary = compute_summary(df)
    summary.to_csv(output_dir / "step3_eda_summary_stats.csv", index=False)

    treated_comparison = (
        df.groupby("treated", as_index=False)[
            [
                "junior_output_share",
                "junior_merged_pr_share",
                "junior_ticket_share",
                "total_output",
            ]
        ]
        .mean()
        .rename(columns={"treated": "treated_group"})
    )
    treated_comparison.to_csv(output_dir / "step3_eda_treated_comparison.csv", index=False)

    team_adoption = (
        df.groupby("team_id", as_index=False)["adoption_week"]
        .first()
        .assign(adopter=lambda x: x["adoption_week"].notna().astype(int))
    )
    adoption_timing = (
        team_adoption.groupby("adoption_week", dropna=False, as_index=False)
        .agg(n_teams=("team_id", "count"))
        .sort_values("adoption_week")
    )
    adoption_timing.to_csv(output_dir / "step3_eda_adoption_timing.csv", index=False)

    event_counts = (
        df.loc[df["event_time"].notna(), ["event_time"]]
        .groupby("event_time", as_index=False)
        .size()
        .rename(columns={"size": "n_team_weeks"})
        .sort_values("event_time")
    )
    event_counts.to_csv(output_dir / "step3_eda_event_time_counts.csv", index=False)

    corr_vars = [
        "junior_output_share",
        "treated",
        "total_output",
        "total_merged_prs",
        "total_completed_tickets",
        "junior_merged_pr_share",
        "junior_ticket_share",
    ]
    corr = df[corr_vars].corr(numeric_only=True)
    corr.to_csv(output_dir / "step3_eda_correlation_matrix.csv", index=True)

    snapshot = {
        "step": "Step 3",
        "n_rows": int(len(df)),
        "n_teams": int(df["team_id"].nunique()),
        "n_weeks": int(df["week_index"].nunique()),
        "adoption_rate_team_level": float(team_adoption["adopter"].mean()),
        "mean_junior_output_share": float(df["junior_output_share"].mean()),
        "treated_share_team_weeks": float(df["treated"].mean()),
        "analysis_sample_rate": float(df["analysis_sample"].mean()),
        "corr_treated_junior_share": float(corr.loc["treated", "junior_output_share"]),
    }
    (output_dir / "step3_eda_snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    print("Wrote Step 3 EDA artifacts to outputs/")


if __name__ == "__main__":
    main()
