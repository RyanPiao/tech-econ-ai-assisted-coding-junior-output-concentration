#!/usr/bin/env python3
"""Generate paper-ready figures and supplemental tables."""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore", message=r"covariance of constraints does not have full rank.*")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.econometrics import build_event_dummies, pretrend_pvalue, twfe_ols
from src.io_helpers import write_json
from src.visualization import (
    save_adoption_histogram,
    save_event_study_plot,
    save_group_trends,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate figures and non-regression tables")
    parser.add_argument("--input", default="data/synthetic/synthetic_team_week_panel.csv")
    parser.add_argument("--lead-max", type=int, default=6)
    parser.add_argument("--lag-max", type=int, default=8)
    args = parser.parse_args()

    df = pd.read_csv(ROOT / args.input)
    df = df.loc[df["analysis_sample"] == 1].copy()

    # Table A1: core descriptive stats
    desc = pd.DataFrame(
        [
            {
                "metric": "n_team_week",
                "value": int(df.shape[0]),
            },
            {
                "metric": "n_teams",
                "value": int(df["team_id"].nunique()),
            },
            {
                "metric": "n_weeks",
                "value": int(df["week_index"].nunique()),
            },
            {
                "metric": "mean_junior_output_share",
                "value": float(df["junior_output_share"].mean()),
            },
            {
                "metric": "sd_junior_output_share",
                "value": float(df["junior_output_share"].std(ddof=1)),
            },
            {
                "metric": "mean_total_output",
                "value": float(df["total_output"].mean()),
            },
            {
                "metric": "adoption_rate",
                "value": float(df.groupby("team_id")["adoption_week"].first().notna().mean()),
            },
            {
                "metric": "treated_share",
                "value": float(df["treated"].mean()),
            },
        ]
    )
    desc_path = ROOT / "outputs/tables/table_a1_descriptive_stats.csv"
    desc_path.parent.mkdir(parents=True, exist_ok=True)
    desc.to_csv(desc_path, index=False)

    # Event-study table + figure
    event_df, mapping = build_event_dummies(df, lead_max=args.lead_max, lag_max=args.lag_max)
    event_terms = list(mapping.keys()) + ["event_lead_far", "event_lag_far"]
    result = twfe_ols(
        df=event_df,
        outcome="junior_output_share",
        rhs_terms=event_terms,
    )

    ci = result.conf_int()
    rows = []
    for term, k in mapping.items():
        if term not in result.params.index:
            continue
        rows.append(
            {
                "term": term,
                "event_time": int(k),
                "coef": float(result.params[term]),
                "se": float(result.bse[term]),
                "tstat": float(result.tvalues[term]),
                "pvalue": float(result.pvalues[term]),
                "ci_low_95": float(ci.loc[term, 0]),
                "ci_high_95": float(ci.loc[term, 1]),
                "n_event_team_weeks": int((event_df[term] == 1).sum()),
            }
        )

    coef_df = pd.DataFrame(rows).sort_values("event_time")
    coef_path = ROOT / "outputs/tables/table_event_study_coefficients.csv"
    coef_df.to_csv(coef_path, index=False)

    pretrend = pretrend_pvalue(result, mapping)
    event_meta = {
        "lead_max": args.lead_max,
        "lag_max": args.lag_max,
        "reference_period": -1,
        "pretrend_joint_pvalue": pretrend,
        "nobs": int(result.nobs),
    }
    write_json(ROOT / "outputs/tables/table_event_study_metadata.json", event_meta)

    summary_path = ROOT / "outputs/tables/table_event_study_summary.txt"
    summary_path.write_text(str(result.summary()), encoding="utf-8")

    # Figures
    fig1 = ROOT / "outputs/figures/figure_1_adoption_timing_histogram.png"
    fig2 = ROOT / "outputs/figures/figure_2_group_trends.png"
    fig3 = ROOT / "outputs/figures/figure_3_event_study.png"
    fig1.parent.mkdir(parents=True, exist_ok=True)

    save_adoption_histogram(df, fig1)
    save_group_trends(df, fig2)
    save_event_study_plot(coef_df, fig3)

    print(f"Wrote {desc_path}")
    print(f"Wrote {coef_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {fig1}")
    print(f"Wrote {fig2}")
    print(f"Wrote {fig3}")


if __name__ == "__main__":
    main()
