#!/usr/bin/env python3
"""Step 2 synthetic data generation + ingestion pipeline.

Builds a reproducible team-week panel for studying AI-assisted coding adoption
and junior-developer output concentration.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class PipelineConfig:
    seed: int = 20260309
    n_teams: int = 48
    n_weeks: int = 30
    adoption_rate: float = 0.7
    adoption_min_week: int = 8
    adoption_max_week: int = 22


def logistic(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def generate_team_level(rng: np.random.Generator, cfg: PipelineConfig) -> pd.DataFrame:
    team_ids = [f"T{idx:03d}" for idx in range(1, cfg.n_teams + 1)]

    team_df = pd.DataFrame(
        {
            "team_id": team_ids,
            "team_size": rng.integers(4, 13, size=cfg.n_teams),
            "baseline_complexity": rng.beta(2.2, 2.0, size=cfg.n_teams),
            "baseline_junior_mix": rng.beta(2.0, 2.4, size=cfg.n_teams),
            "manager_quality": rng.normal(0.0, 1.0, size=cfg.n_teams),
        }
    )

    # Fixed-count staggered adoption: approximately cfg.adoption_rate of teams adopt.
    n_adopters = int(round(cfg.adoption_rate * cfg.n_teams))
    adopted_flag = np.zeros(cfg.n_teams, dtype=bool)
    adopter_idx = rng.choice(cfg.n_teams, size=n_adopters, replace=False)
    adopted_flag[adopter_idx] = True

    adoption_week = np.where(
        adopted_flag,
        rng.integers(cfg.adoption_min_week, cfg.adoption_max_week + 1, size=cfg.n_teams),
        np.nan,
    )
    team_df["adoption_week"] = adoption_week

    return team_df


def generate_raw_team_role_week(rng: np.random.Generator, cfg: PipelineConfig, team_df: pd.DataFrame) -> pd.DataFrame:
    weeks = np.arange(1, cfg.n_weeks + 1)
    panel_idx = pd.MultiIndex.from_product(
        [team_df["team_id"], weeks], names=["team_id", "week_index"]
    )

    base = panel_idx.to_frame(index=False).merge(team_df, on="team_id", how="left")
    base["calendar_week"] = pd.to_datetime("2026-01-05") + pd.to_timedelta((base["week_index"] - 1) * 7, unit="D")

    base["treated"] = (
        (~base["adoption_week"].isna())
        & (base["week_index"] >= base["adoption_week"])
    ).astype(int)

    # Data-generating process for total output volume and junior share.
    # Intended direction: adoption modestly raises junior output share.
    week_shock = 0.12 * np.sin(base["week_index"] / 2.5) + 0.04 * np.cos(base["week_index"] / 3.8)
    noise_share = rng.normal(0.0, 0.18, len(base))
    noise_volume = rng.normal(0.0, 0.10, len(base))

    share_latent = (
        -0.6
        + 2.1 * base["baseline_junior_mix"]
        - 0.8 * base["baseline_complexity"]
        + 0.25 * base["manager_quality"]
        + 0.30 * base["treated"]
        + week_shock
        + noise_share
    )
    base["junior_share_latent"] = logistic(share_latent).clip(0.05, 0.95)

    volume_latent = (
        2.1
        + 0.08 * base["team_size"]
        + 0.35 * base["manager_quality"]
        - 0.45 * base["baseline_complexity"]
        + 0.12 * base["treated"]
        + 0.3 * week_shock
        + noise_volume
    )

    total_merged_prs = rng.poisson(np.exp(volume_latent)).clip(min=4)
    total_tickets = rng.poisson(np.exp(volume_latent + 0.22)).clip(min=6)

    junior_merged_prs = rng.binomial(total_merged_prs, base["junior_share_latent"].to_numpy())
    junior_tickets = rng.binomial(total_tickets, base["junior_share_latent"].to_numpy())

    senior_merged_prs = total_merged_prs - junior_merged_prs
    senior_tickets = total_tickets - junior_tickets

    common_cols = [
        "team_id",
        "calendar_week",
        "week_index",
        "adoption_week",
        "treated",
        "team_size",
        "baseline_complexity",
        "baseline_junior_mix",
        "manager_quality",
    ]

    juniors = base[common_cols].copy()
    juniors["role"] = "junior"
    juniors["merged_prs"] = junior_merged_prs
    juniors["completed_tickets"] = junior_tickets

    seniors = base[common_cols].copy()
    seniors["role"] = "senior"
    seniors["merged_prs"] = senior_merged_prs
    seniors["completed_tickets"] = senior_tickets

    raw = pd.concat([juniors, seniors], ignore_index=True)
    raw["role_output"] = raw["merged_prs"] + raw["completed_tickets"]

    return raw.sort_values(["team_id", "week_index", "role"]).reset_index(drop=True)


def ingest_to_team_week_panel(raw: pd.DataFrame) -> pd.DataFrame:
    totals = (
        raw.groupby(
            ["team_id", "calendar_week", "week_index", "adoption_week", "treated"],
            as_index=False,
            dropna=False,
        )[["merged_prs", "completed_tickets", "role_output"]]
        .sum()
        .rename(
            columns={
                "merged_prs": "total_merged_prs",
                "completed_tickets": "total_completed_tickets",
                "role_output": "total_output",
            }
        )
    )

    juniors = (
        raw.loc[raw["role"] == "junior", ["team_id", "calendar_week", "week_index", "merged_prs", "completed_tickets", "role_output"]]
        .rename(
            columns={
                "merged_prs": "junior_merged_prs",
                "completed_tickets": "junior_completed_tickets",
                "role_output": "junior_output",
            }
        )
    )

    panel = totals.merge(juniors, on=["team_id", "calendar_week", "week_index"], how="left")
    panel["junior_merged_pr_share"] = panel["junior_merged_prs"] / panel["total_merged_prs"]
    panel["junior_ticket_share"] = panel["junior_completed_tickets"] / panel["total_completed_tickets"]
    panel["junior_output_share"] = panel["junior_output"] / panel["total_output"]
    panel["event_time"] = panel["week_index"] - panel["adoption_week"]
    panel.loc[panel["adoption_week"].isna(), "event_time"] = np.nan

    panel["post_period"] = (
        (~panel["adoption_week"].isna())
        & (panel["week_index"] >= panel["adoption_week"])
    ).astype(int)

    panel["analysis_sample"] = (
        (panel["total_output"] >= 10)
        & panel["junior_output_share"].notna()
    ).astype(int)

    return panel.sort_values(["team_id", "week_index"]).reset_index(drop=True)


def write_data_dictionary(path: Path) -> None:
    dictionary_rows = [
        ("team_id", "string", "Team identifier"),
        ("calendar_week", "date", "Week start date (Monday)"),
        ("week_index", "int", "Sequential week index in panel"),
        ("adoption_week", "float", "Team-specific AI adoption week; NaN for never adopters"),
        ("treated", "int", "1 if team-week is on/after adoption week"),
        ("post_period", "int", "Alias of treatment timing for design clarity"),
        ("event_time", "float", "week_index - adoption_week; NaN for never adopters"),
        ("total_merged_prs", "int", "Total merged PRs in team-week"),
        ("total_completed_tickets", "int", "Total completed tickets in team-week"),
        ("total_output", "int", "total_merged_prs + total_completed_tickets"),
        ("junior_merged_prs", "int", "Junior-attributed merged PRs"),
        ("junior_completed_tickets", "int", "Junior-attributed completed tickets"),
        ("junior_output", "int", "junior_merged_prs + junior_completed_tickets"),
        ("junior_merged_pr_share", "float", "junior_merged_prs / total_merged_prs"),
        ("junior_ticket_share", "float", "junior_completed_tickets / total_completed_tickets"),
        ("junior_output_share", "float", "Primary outcome: junior_output / total_output"),
        ("analysis_sample", "int", "1 if sample filter is met (total_output >= 10)"),
    ]
    dict_df = pd.DataFrame(dictionary_rows, columns=["variable", "type", "definition"])
    dict_df.to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Step 2 synthetic data generation + ingestion pipeline")
    parser.add_argument("--seed", type=int, default=PipelineConfig.seed)
    parser.add_argument("--n-teams", type=int, default=PipelineConfig.n_teams)
    parser.add_argument("--n-weeks", type=int, default=PipelineConfig.n_weeks)
    parser.add_argument("--output-dir", type=str, default="outputs")
    args = parser.parse_args()

    cfg = PipelineConfig(seed=args.seed, n_teams=args.n_teams, n_weeks=args.n_weeks)
    rng = np.random.default_rng(cfg.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    team_df = generate_team_level(rng=rng, cfg=cfg)
    raw = generate_raw_team_role_week(rng=rng, cfg=cfg, team_df=team_df)
    panel = ingest_to_team_week_panel(raw)

    raw_path = output_dir / "step2_synthetic_team_role_week.csv"
    panel_path = output_dir / "step2_team_week_panel.csv"
    dictionary_path = output_dir / "step2_data_dictionary.csv"
    meta_path = output_dir / "step2_generation_metadata.json"

    raw.to_csv(raw_path, index=False)
    panel.to_csv(panel_path, index=False)
    write_data_dictionary(dictionary_path)

    metadata = {
        "step": "Step 2",
        "data_type": "Synthetic",
        "seed": cfg.seed,
        "n_teams": cfg.n_teams,
        "n_weeks": cfg.n_weeks,
        "n_team_week_rows": int(panel.shape[0]),
        "n_team_role_week_rows": int(raw.shape[0]),
        "analysis_sample_rows": int(panel["analysis_sample"].sum()),
        "adoption_rate_realized": float(team_df["adoption_week"].notna().mean()),
        "mean_junior_output_share": float(panel["junior_output_share"].mean()),
        "median_adoption_week": (
            None
            if team_df["adoption_week"].dropna().empty
            else float(team_df["adoption_week"].dropna().median())
        ),
    }

    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Wrote: {raw_path}")
    print(f"Wrote: {panel_path}")
    print(f"Wrote: {dictionary_path}")
    print(f"Wrote: {meta_path}")


if __name__ == "__main__":
    main()
