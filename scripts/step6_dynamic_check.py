#!/usr/bin/env python3
"""Step 6 dynamic check: event-study style specification with team/week fixed effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


def event_name(k: int) -> str:
    if k < 0:
        return f"event_m{abs(k)}"
    return f"event_p{k}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Step 6 dynamic event-study check")
    parser.add_argument("--input", default="outputs/step2_team_week_panel.csv")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--lead-max", type=int, default=6)
    parser.add_argument("--lag-max", type=int, default=8)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    df = df.loc[df["analysis_sample"] == 1].copy()

    lead_max = args.lead_max
    lag_max = args.lag_max

    event_cols: list[str] = []
    event_map: dict[str, int] = {}

    for k in range(-lead_max, lag_max + 1):
        if k == -1:
            continue  # omitted reference period
        col = event_name(k)
        df[col] = (df["event_time"] == k).astype(int)
        event_cols.append(col)
        event_map[col] = k

    df["event_lead_far"] = (df["event_time"] <= -(lead_max + 1)).fillna(False).astype(int)
    df["event_lag_far"] = (df["event_time"] >= (lag_max + 1)).fillna(False).astype(int)

    team_fe = pd.get_dummies(df["team_id"], prefix="team", drop_first=True)
    week_fe = pd.get_dummies(df["week_index"], prefix="week", drop_first=True)

    x = pd.concat([
        df[event_cols + ["event_lead_far", "event_lag_far"]],
        team_fe,
        week_fe,
    ], axis=1)
    x = sm.add_constant(x, has_constant="add").astype(float)
    y = df["junior_output_share"].astype(float)

    model = sm.OLS(y, x)
    result = model.fit(cov_type="cluster", cov_kwds={"groups": df["team_id"]})

    coef_rows = []
    ci = result.conf_int()
    for col in event_cols:
        coef_rows.append(
            {
                "term": col,
                "event_time": int(event_map[col]),
                "coef": float(result.params[col]),
                "se": float(result.bse[col]),
                "tstat": float(result.tvalues[col]),
                "pvalue": float(result.pvalues[col]),
                "ci_low_95": float(ci.loc[col, 0]),
                "ci_high_95": float(ci.loc[col, 1]),
                "n_event_team_weeks": int(df[col].sum()),
            }
        )

    coef_df = pd.DataFrame(coef_rows).sort_values("event_time")
    coef_df.to_csv(output_dir / "step6_event_study_coefficients.csv", index=False)

    lead_terms = [event_name(k) for k in range(-lead_max, -1)]
    lead_terms = [c for c in lead_terms if c in result.params.index]

    if lead_terms:
        hypothesis = ", ".join(f"{term} = 0" for term in lead_terms)
        wt = result.wald_test(hypothesis, scalar=True)
        pretrend_df = pd.DataFrame(
            [
                {
                    "test": "joint_pretrend_zero",
                    "n_constraints": len(lead_terms),
                    "statistic": float(wt.statistic),
                    "pvalue": float(wt.pvalue),
                }
            ]
        )
    else:
        pretrend_df = pd.DataFrame(
            [
                {
                    "test": "joint_pretrend_zero",
                    "n_constraints": 0,
                    "statistic": np.nan,
                    "pvalue": np.nan,
                }
            ]
        )

    pretrend_df.to_csv(output_dir / "step6_event_study_pretrend_test.csv", index=False)

    summary_lines = [
        "Step 6 dynamic check (event-study style)",
        f"nobs: {int(result.nobs)}",
        f"R-squared: {float(result.rsquared):.6f}",
        f"window: leads -{lead_max} to lags +{lag_max}, reference = -1",
        "See step6_event_study_coefficients.csv for coefficient-level output.",
    ]
    (output_dir / "step6_event_study_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    post_coefs = coef_df.loc[coef_df["event_time"] >= 0, "coef"]
    metadata = {
        "step": "Step 6",
        "nobs": int(result.nobs),
        "n_teams": int(df["team_id"].nunique()),
        "n_weeks": int(df["week_index"].nunique()),
        "event_window": {"lead_max": int(lead_max), "lag_max": int(lag_max), "reference": -1},
        "average_post_event_coef": float(post_coefs.mean()) if not post_coefs.empty else None,
        "pretrend_pvalue": (
            None
            if pretrend_df["pvalue"].isna().all()
            else float(pretrend_df["pvalue"].iloc[0])
        ),
    }
    (output_dir / "step6_event_study_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("Wrote Step 6 dynamic check outputs to outputs/")


if __name__ == "__main__":
    main()
