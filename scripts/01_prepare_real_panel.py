#!/usr/bin/env python3
"""Prepare cleaned real-data analysis panel and treatment proxy.

Core principle: use observed data only. No synthetic generation in the primary pipeline.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io_helpers import write_json


REQUIRED_COLUMNS = {
    "team_id",
    "calendar_week",
    "week_index",
    "total_merged_prs",
    "total_completed_tickets",
    "total_output",
    "junior_merged_prs",
    "junior_completed_tickets",
    "junior_output",
    "junior_merged_pr_share",
    "junior_ticket_share",
    "junior_output_share",
    "median_cycle_time_hours",
    "review_latency_hours",
    "post_merge_bug_proxy",
    "ai_signal_events",
    "ai_eligible_events",
    "ai_intensity",
}


def _build_adoption_proxy(
    df: pd.DataFrame,
    ai_intensity_threshold: float,
    ai_min_signal_events: int,
) -> pd.DataFrame:
    out = df.copy()
    out["ai_proxy_trigger"] = (
        (out["ai_intensity"] >= ai_intensity_threshold)
        & (out["ai_signal_events"] >= ai_min_signal_events)
        & (out["ai_eligible_events"] > 0)
    ).astype(int)

    adoption_week = (
        out.sort_values(["team_id", "week_index"])
        .groupby("team_id", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "adoption_week": (
                        float(g.loc[g["ai_proxy_trigger"] == 1, "week_index"].min())
                        if (g["ai_proxy_trigger"] == 1).any()
                        else np.nan
                    )
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    out = out.drop(columns=[c for c in ["adoption_week", "treated", "event_time", "post_period"] if c in out.columns])
    out = out.merge(adoption_week, on="team_id", how="left")

    # One-week burn-in adjustment: if trigger appears in the first sample week,
    # move adoption to week 2 to preserve at least one pre-period for switchers.
    max_week = int(out["week_index"].max()) if not out.empty else 0
    if max_week >= 2:
        out.loc[out["adoption_week"] == 1, "adoption_week"] = 2

    out["treated"] = (
        out["adoption_week"].notna() & (out["week_index"] >= out["adoption_week"])
    ).astype(int)
    out["post_period"] = out["treated"]
    out["event_time"] = np.where(
        out["adoption_week"].notna(),
        out["week_index"] - out["adoption_week"],
        np.nan,
    )

    return out


def _fill_controls(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["log_total_output"] = np.log1p(out["total_output"])
    out["log_ai_eligible_events"] = np.log1p(out["ai_eligible_events"])

    for col in ["median_cycle_time_hours", "review_latency_hours", "post_merge_bug_proxy"]:
        team_median = out.groupby("team_id")[col].transform("median")
        global_median = float(out[col].median()) if out[col].notna().any() else 0.0
        out[f"{col}_filled"] = out[col].fillna(team_median).fillna(global_median)

    return out


def _switcher_count(df: pd.DataFrame) -> int:
    return int(
        sum(
            ((g["treated"] == 0).any() and (g["treated"] == 1).any())
            for _, g in df.groupby("team_id")
        )
    )


def build_clean_panel(
    df: pd.DataFrame,
    ai_intensity_threshold: float,
    ai_min_signal_events: int,
    min_total_output_for_sample: int,
) -> tuple[pd.DataFrame, dict]:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Input panel missing required columns: {sorted(missing)}")

    out = df.copy()
    out["team_id"] = out["team_id"].astype(str).str.lower()
    out["calendar_week"] = pd.to_datetime(out["calendar_week"]).dt.date
    out = out.sort_values(["team_id", "week_index"]).drop_duplicates(["team_id", "week_index"], keep="last")

    out = _build_adoption_proxy(
        df=out,
        ai_intensity_threshold=ai_intensity_threshold,
        ai_min_signal_events=ai_min_signal_events,
    )
    out = _fill_controls(out)

    out["analysis_sample"] = (
        (out["total_output"] >= min_total_output_for_sample)
        & out["junior_output_share"].notna()
    ).astype(int)

    sample = out.loc[out["analysis_sample"] == 1].copy()

    timing_counts = (
        sample.loc[sample["adoption_week"].notna(), ["team_id", "adoption_week"]]
        .drop_duplicates()
        .groupby("adoption_week", as_index=False)
        .size()
        .rename(columns={"size": "n_teams"})
        .sort_values("adoption_week")
    )

    metadata = {
        "data_type": "real_public_proxy",
        "pipeline": "real-data-first_primary",
        "treatment_proxy_definition": {
            "name": "ai_proxy_trigger",
            "definition": "1 if weekly ai_intensity >= threshold AND ai_signal_events >= minimum AND ai_eligible_events > 0",
            "ai_intensity_threshold": ai_intensity_threshold,
            "ai_min_signal_events": ai_min_signal_events,
            "burn_in_rule": "if first trigger week is 1, set adoption_week to 2 when week 2 exists",
        },
        "analysis_sample_rule": {
            "min_total_output": min_total_output_for_sample,
            "requires_nonmissing_junior_output_share": True,
        },
        "coverage": {
            "n_rows_total": int(out.shape[0]),
            "n_teams_total": int(out["team_id"].nunique()),
            "n_weeks_total": int(out["week_index"].nunique()),
            "n_rows_analysis": int(sample.shape[0]),
            "n_teams_analysis": int(sample["team_id"].nunique()),
            "n_weeks_analysis": int(sample["week_index"].nunique()),
        },
        "identification_diagnostics": {
            "adoption_rate_team_level_total": float(out.groupby("team_id")["adoption_week"].first().notna().mean()),
            "treated_share_total": float(out["treated"].mean()),
            "treated_share_analysis": float(sample["treated"].mean()) if not sample.empty else None,
            "switchers_total": _switcher_count(out),
            "switchers_analysis": _switcher_count(sample) if not sample.empty else 0,
            "adoption_timing_counts_analysis": [
                {"adoption_week": float(r.adoption_week), "n_teams": int(r.n_teams)}
                for r in timing_counts.itertuples(index=False)
            ],
        },
    }

    return out, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare cleaned real-data panel")
    parser.add_argument(
        "--input",
        default="data/raw/real_proxy/repo_week_panel_q1_2025_expanded.csv",
        help="Path to raw real-data panel",
    )
    parser.add_argument(
        "--out-clean",
        default="data/processed/real_panel_clean.csv",
        help="Output cleaned panel path",
    )
    parser.add_argument(
        "--out-meta",
        default="data/processed/real_panel_metadata.json",
        help="Output metadata JSON path",
    )
    parser.add_argument("--ai-intensity-threshold", type=float, default=0.02)
    parser.add_argument("--ai-min-signal-events", type=int, default=2)
    parser.add_argument("--min-total-output", type=int, default=1)
    args = parser.parse_args()

    in_path = ROOT / args.input
    out_clean = ROOT / args.out_clean
    out_meta = ROOT / args.out_meta

    out_clean.parent.mkdir(parents=True, exist_ok=True)
    out_meta.parent.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(in_path)
    clean, metadata = build_clean_panel(
        df=raw,
        ai_intensity_threshold=args.ai_intensity_threshold,
        ai_min_signal_events=args.ai_min_signal_events,
        min_total_output_for_sample=args.min_total_output,
    )

    clean.to_csv(out_clean, index=False)
    write_json(out_meta, metadata)

    print(f"Wrote {out_clean}")
    print(f"Wrote {out_meta}")


if __name__ == "__main__":
    main()
