#!/usr/bin/env python3
"""Prepare benchmark moments from the available real-data proxy panel.

This script is intentionally conservative: if a benchmark moment is not identified
from the raw proxy panel (e.g., no observed adoptions), it uses clearly-labeled
placeholder assumptions and records that decision in metadata.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io_helpers import write_json


def compute_benchmark_moments(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {
        "team_id",
        "week_index",
        "adoption_week",
        "treated",
        "total_output",
        "junior_output_share",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input panel missing required columns: {sorted(missing)}")

    work = df.copy()
    work = work.sort_values(["team_id", "week_index"]).reset_index(drop=True)

    observed_share = work["junior_output_share"].dropna()
    raw_adoption = work.groupby("team_id", as_index=False)["adoption_week"].first()["adoption_week"]

    raw_adoption_rate = float(raw_adoption.notna().mean())
    raw_treated_share = float(work["treated"].mean())
    raw_median_adoption = float(raw_adoption.dropna().median()) if raw_adoption.notna().any() else np.nan

    # Conservative placeholders if the pilot panel cannot identify timing moments.
    fallback = {
        "adoption_rate": 0.55,
        "treated_share": 0.33,
        "median_adoption_week": 11.0,
        "total_output_mean": 14.0,
    }

    if raw_adoption.notna().sum() < 2:
        adoption_rate = fallback["adoption_rate"]
        treated_share = fallback["treated_share"]
        median_adoption_week = fallback["median_adoption_week"]
        timing_source = "placeholder_assumption_due_to_insufficient_adopter_observations"
    else:
        adoption_rate = raw_adoption_rate
        treated_share = raw_treated_share
        median_adoption_week = raw_median_adoption
        timing_source = "observed_from_proxy_panel"

    # Extremely low measured output in sparse pilot windows can destabilize calibration.
    raw_total_mean = float(work["total_output"].mean())
    total_output_mean = max(raw_total_mean, fallback["total_output_mean"])
    total_output_source = (
        "observed_from_proxy_panel"
        if raw_total_mean >= fallback["total_output_mean"]
        else "observed_with_floor_adjustment_for_sparse_pilot_window"
    )

    moments = pd.DataFrame(
        [
            {
                "moment": "junior_output_share_mean",
                "target_value": float(observed_share.mean()) if not observed_share.empty else 0.50,
                "source": "observed_from_proxy_panel",
                "n_obs": int(observed_share.shape[0]),
                "definition": "Mean junior output share among non-missing real-proxy observations",
            },
            {
                "moment": "junior_output_share_sd",
                "target_value": float(observed_share.std(ddof=1)) if observed_share.shape[0] > 1 else 0.12,
                "source": "observed_from_proxy_panel" if observed_share.shape[0] > 1 else "placeholder_due_to_single_observation",
                "n_obs": int(observed_share.shape[0]),
                "definition": "Standard deviation of junior output share",
            },
            {
                "moment": "total_output_mean",
                "target_value": float(total_output_mean),
                "source": total_output_source,
                "n_obs": int(work.shape[0]),
                "definition": "Mean team-week total output (floor-adjusted when pilot window is too sparse)",
            },
            {
                "moment": "total_output_sd",
                "target_value": float(work["total_output"].std(ddof=1)) if work.shape[0] > 1 else 6.0,
                "source": "observed_from_proxy_panel" if work.shape[0] > 1 else "placeholder_due_to_single_observation",
                "n_obs": int(work.shape[0]),
                "definition": "Standard deviation of team-week total output",
            },
            {
                "moment": "adoption_rate",
                "target_value": float(adoption_rate),
                "source": timing_source,
                "n_obs": int(raw_adoption.shape[0]),
                "definition": "Share of teams that adopt AI assistance",
            },
            {
                "moment": "treated_share",
                "target_value": float(treated_share),
                "source": timing_source,
                "n_obs": int(work.shape[0]),
                "definition": "Share of team-week observations in post-adoption period",
            },
            {
                "moment": "median_adoption_week",
                "target_value": float(median_adoption_week),
                "source": timing_source,
                "n_obs": int(raw_adoption.notna().sum()),
                "definition": "Median adoption week among adopter teams",
            },
        ]
    )

    metadata = {
        "input_rows": int(work.shape[0]),
        "input_teams": int(work["team_id"].nunique()),
        "raw_observed_adoption_rate": raw_adoption_rate,
        "raw_observed_treated_share": raw_treated_share,
        "raw_observed_median_adoption_week": None if np.isnan(raw_median_adoption) else raw_median_adoption,
        "raw_total_output_mean": raw_total_mean,
        "placeholder_policy": {
            "fallback_adoption_rate": fallback["adoption_rate"],
            "fallback_treated_share": fallback["treated_share"],
            "fallback_median_adoption_week": fallback["median_adoption_week"],
            "total_output_mean_floor": fallback["total_output_mean"],
        },
    }
    return moments, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare benchmark moments from real-proxy panel")
    parser.add_argument(
        "--input",
        default="data/raw/real_proxy/repo_week_panel_pilot.csv",
        help="Path to raw real-proxy team-week panel",
    )
    parser.add_argument(
        "--out-moments",
        default="data/processed/benchmark_moments.csv",
        help="Output CSV with benchmark moments",
    )
    parser.add_argument(
        "--out-clean-panel",
        default="data/processed/benchmark_panel_clean.csv",
        help="Output cleaned benchmark panel",
    )
    parser.add_argument(
        "--out-meta",
        default="data/processed/benchmark_moments_metadata.json",
        help="Output JSON metadata",
    )
    args = parser.parse_args()

    in_path = ROOT / args.input
    out_moments = ROOT / args.out_moments
    out_clean = ROOT / args.out_clean_panel
    out_meta = ROOT / args.out_meta

    out_moments.parent.mkdir(parents=True, exist_ok=True)
    out_clean.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)
    moments, metadata = compute_benchmark_moments(df)

    keep_cols = [
        c
        for c in [
            "team_id",
            "calendar_week",
            "week_index",
            "adoption_week",
            "treated",
            "total_output",
            "junior_output",
            "junior_output_share",
        ]
        if c in df.columns
    ]
    df[keep_cols].to_csv(out_clean, index=False)
    moments.to_csv(out_moments, index=False)
    write_json(out_meta, metadata)

    print(f"Wrote {out_clean}")
    print(f"Wrote {out_moments}")
    print(f"Wrote {out_meta}")


if __name__ == "__main__":
    main()
