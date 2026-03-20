#!/usr/bin/env python3
"""Build before/after diagnostics for the real-data sample expansion."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.econometrics import build_event_dummies


def prepare_panel(raw: pd.DataFrame, ai_intensity_threshold: float = 0.02, ai_min_signal_events: int = 2) -> pd.DataFrame:
    out = raw.copy()
    out["team_id"] = out["team_id"].astype(str).str.lower()
    out["calendar_week"] = pd.to_datetime(out["calendar_week"]).dt.date
    out = out.sort_values(["team_id", "week_index"]).drop_duplicates(["team_id", "week_index"], keep="last")

    out["ai_proxy_trigger"] = (
        (out["ai_intensity"] >= ai_intensity_threshold)
        & (out["ai_signal_events"] >= ai_min_signal_events)
        & (out["ai_eligible_events"] > 0)
    ).astype(int)

    adoption = (
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
    out = out.merge(adoption, on="team_id", how="left")

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

    out["analysis_sample"] = ((out["total_output"] >= 1) & out["junior_output_share"].notna()).astype(int)
    return out


def switcher_count(df: pd.DataFrame) -> int:
    return int(
        sum(
            ((g["treated"] == 0).any() and (g["treated"] == 1).any())
            for _, g in df.groupby("team_id")
        )
    )


def adoption_dispersion(df: pd.DataFrame) -> float:
    ad = (
        df.loc[df["adoption_week"].notna(), ["team_id", "adoption_week"]]
        .drop_duplicates()["adoption_week"]
        .astype(float)
    )
    if ad.empty:
        return float("nan")
    return float(ad.std(ddof=0))


def pretrend_support(df: pd.DataFrame, lead_max: int = 3, lag_max: int = 4) -> tuple[int, int, dict[str, int]]:
    event_df, mapping = build_event_dummies(df, lead_max=lead_max, lag_max=lag_max)
    lead_terms = [term for term, k in mapping.items() if k < -1]
    lead_counts = {term: int((event_df[term] == 1).sum()) for term in lead_terms}
    supported_bins = int(sum(v > 0 for v in lead_counts.values()))
    total_cells = int(sum(lead_counts.values()))
    return supported_bins, total_cells, lead_counts


def collect_metrics(label: str, panel: pd.DataFrame) -> dict:
    sample = panel.loc[panel["analysis_sample"] == 1].copy()
    bins_supported, total_cells, lead_counts = pretrend_support(sample)

    row = {
        "sample": label,
        "n_teams": int(sample["team_id"].nunique()),
        "n_team_weeks": int(sample.shape[0]),
        "switcher_count": int(switcher_count(sample)),
        "adoption_timing_dispersion_sd": float(adoption_dispersion(sample)),
        "pretrend_supported_lead_bins": bins_supported,
        "pretrend_support_cell_count": total_cells,
    }
    for term, count in sorted(lead_counts.items()):
        row[f"pretrend_{term}_count"] = int(count)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Build old-vs-expanded diagnostics table")
    parser.add_argument("--old-input", default="data/raw/real_proxy/repo_week_panel_q1_2025_expanded.csv")
    parser.add_argument("--new-input", default="data/raw/real_proxy/repo_week_panel_q2_2025_more_data.csv")
    parser.add_argument("--out", default="outputs/tables/table_sample_expansion_diagnostics.csv")
    args = parser.parse_args()

    old_raw = pd.read_csv(ROOT / args.old_input)
    new_raw = pd.read_csv(ROOT / args.new_input)

    old_panel = prepare_panel(old_raw)
    new_panel = prepare_panel(new_raw)

    old_metrics = collect_metrics("old_q1_2025_expanded", old_panel)
    new_metrics = collect_metrics("expanded_q2_2025_more_data", new_panel)

    delta = {"sample": "delta_new_minus_old"}
    for key in old_metrics:
        if key == "sample":
            continue
        old_val = old_metrics.get(key)
        new_val = new_metrics.get(key)
        if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
            delta[key] = float(new_val) - float(old_val)

    out = pd.DataFrame([old_metrics, new_metrics, delta])

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
