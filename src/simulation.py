from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class SimulationConfig:
    seed: int
    n_teams: int
    n_weeks: int
    treatment_effect: float


def logistic(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def _calibrate_intercept_logit(base: np.ndarray, target_mean: float) -> float:
    lo, hi = -8.0, 8.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        m = logistic(base + mid).mean()
        if m < target_mean:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _calibrate_intercept_log(base: np.ndarray, target_mean: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        m = np.exp(base + mid).mean()
        if m < target_mean:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def generate_adoption_weeks(
    rng: np.random.Generator,
    n_teams: int,
    n_weeks: int,
    adoption_rate: float,
    target_median_adoption_week: float,
) -> np.ndarray:
    n_adopters = int(round(np.clip(adoption_rate, 0.05, 0.95) * n_teams))
    is_adopter = np.zeros(n_teams, dtype=bool)
    adopter_idx = rng.choice(n_teams, size=n_adopters, replace=False)
    is_adopter[adopter_idx] = True

    # Use a compact distribution so the treated share remains informative.
    center = int(round(np.clip(target_median_adoption_week, 4, max(4, n_weeks - 4))))
    draws = np.round(rng.normal(loc=center, scale=2.0, size=n_teams)).astype(int)
    draws = np.clip(draws, 3, max(3, n_weeks - 2))

    adoption_week = np.where(is_adopter, draws, np.nan)
    return adoption_week


def build_synthetic_panel(targets: dict[str, float], cfg: SimulationConfig) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(cfg.seed)

    team_ids = [f"T{t:03d}" for t in range(1, cfg.n_teams + 1)]
    team_df = pd.DataFrame(
        {
            "team_id": team_ids,
            "team_size": rng.integers(4, 15, size=cfg.n_teams),
            "baseline_complexity": rng.beta(2.5, 2.3, size=cfg.n_teams),
            "baseline_junior_mix": rng.beta(2.2, 2.1, size=cfg.n_teams),
            "manager_quality": rng.normal(0.0, 1.0, size=cfg.n_teams),
        }
    )

    adoption_week = generate_adoption_weeks(
        rng=rng,
        n_teams=cfg.n_teams,
        n_weeks=cfg.n_weeks,
        adoption_rate=targets["adoption_rate"],
        target_median_adoption_week=targets["median_adoption_week"],
    )
    team_df["adoption_week"] = adoption_week

    weeks = np.arange(1, cfg.n_weeks + 1)
    panel = pd.MultiIndex.from_product([team_df["team_id"], weeks], names=["team_id", "week_index"]).to_frame(index=False)
    panel = panel.merge(team_df, on="team_id", how="left")
    panel["calendar_week"] = pd.to_datetime("2025-01-06") + pd.to_timedelta((panel["week_index"] - 1) * 7, unit="D")
    panel["treated"] = (
        panel["adoption_week"].notna() & (panel["week_index"] >= panel["adoption_week"])
    ).astype(int)
    panel["post_period"] = panel["treated"]
    panel["event_time"] = panel["week_index"] - panel["adoption_week"]
    panel.loc[panel["adoption_week"].isna(), "event_time"] = np.nan

    week_cycle = 0.15 * np.sin(panel["week_index"] / 2.7) + 0.05 * np.cos(panel["week_index"] / 4.3)
    share_noise_scale = np.clip(targets["junior_output_share_sd"], 0.08, 0.30)
    share_noise = rng.normal(0.0, share_noise_scale, len(panel))
    team_random = rng.normal(0.0, 0.25, cfg.n_teams)
    team_re = panel["team_id"].str.replace("T", "", regex=False).astype(int).to_numpy() - 1

    base_share = (
        1.00 * panel["baseline_junior_mix"].to_numpy()
        - 0.75 * panel["baseline_complexity"].to_numpy()
        + 0.15 * panel["manager_quality"].to_numpy()
        + cfg.treatment_effect * panel["treated"].to_numpy()
        + week_cycle.to_numpy()
        + team_random[team_re]
        + share_noise
    )

    target_share = np.clip(targets["junior_output_share_mean"], 0.20, 0.85)
    share_intercept = _calibrate_intercept_logit(base_share, target_share)
    panel["junior_share_latent"] = logistic(base_share + share_intercept)

    output_noise_scale = np.clip(targets["total_output_sd"] / max(targets["total_output_mean"], 1.0), 0.15, 0.55)
    output_noise = rng.normal(0.0, output_noise_scale, len(panel))
    base_output = (
        0.10 * panel["team_size"].to_numpy()
        - 0.40 * panel["baseline_complexity"].to_numpy()
        + 0.20 * panel["manager_quality"].to_numpy()
        + 0.06 * panel["treated"].to_numpy()
        + 0.25 * week_cycle.to_numpy()
        + 0.20 * team_random[team_re]
        + output_noise
    )
    target_total = max(targets["total_output_mean"], 8.0)
    out_intercept = _calibrate_intercept_log(base_output, target_total)
    expected_output = np.exp(base_output + out_intercept)
    total_output = rng.poisson(expected_output)
    total_output = np.clip(total_output, 1, None)

    merge_share = np.clip(0.45 + 0.05 * np.sin(panel["week_index"] / 5.0), 0.30, 0.70)
    total_merged = rng.binomial(total_output, merge_share)
    total_tickets = total_output - total_merged

    share = panel["junior_share_latent"].to_numpy()
    junior_merged = rng.binomial(total_merged, share)
    junior_tickets = rng.binomial(total_tickets, share)

    panel["total_merged_prs"] = total_merged
    panel["total_completed_tickets"] = total_tickets
    panel["total_output"] = total_output
    panel["junior_merged_prs"] = junior_merged
    panel["junior_completed_tickets"] = junior_tickets
    panel["junior_output"] = junior_merged + junior_tickets
    panel["junior_merged_pr_share"] = panel["junior_merged_prs"] / panel["total_merged_prs"].replace(0, np.nan)
    panel["junior_ticket_share"] = panel["junior_completed_tickets"] / panel["total_completed_tickets"].replace(0, np.nan)
    panel["junior_output_share"] = panel["junior_output"] / panel["total_output"]
    panel["analysis_sample"] = ((panel["total_output"] >= 3) & panel["junior_output_share"].notna()).astype(int)

    diag = {
        "target_junior_output_share_mean": float(targets["junior_output_share_mean"]),
        "realized_junior_output_share_mean": float(panel["junior_output_share"].mean()),
        "target_junior_output_share_sd": float(targets["junior_output_share_sd"]),
        "realized_junior_output_share_sd": float(panel["junior_output_share"].std(ddof=1)),
        "target_total_output_mean": float(targets["total_output_mean"]),
        "realized_total_output_mean": float(panel["total_output"].mean()),
        "target_total_output_sd": float(targets["total_output_sd"]),
        "realized_total_output_sd": float(panel["total_output"].std(ddof=1)),
        "target_adoption_rate": float(targets["adoption_rate"]),
        "realized_adoption_rate": float(panel.groupby("team_id")["adoption_week"].first().notna().mean()),
        "target_treated_share": float(targets["treated_share"]),
        "realized_treated_share": float(panel["treated"].mean()),
    }

    columns = [
        "team_id",
        "calendar_week",
        "week_index",
        "adoption_week",
        "treated",
        "post_period",
        "event_time",
        "team_size",
        "baseline_complexity",
        "baseline_junior_mix",
        "manager_quality",
        "total_merged_prs",
        "total_completed_tickets",
        "total_output",
        "junior_merged_prs",
        "junior_completed_tickets",
        "junior_output",
        "junior_merged_pr_share",
        "junior_ticket_share",
        "junior_output_share",
        "analysis_sample",
    ]

    return panel[columns].sort_values(["team_id", "week_index"]).reset_index(drop=True), diag
