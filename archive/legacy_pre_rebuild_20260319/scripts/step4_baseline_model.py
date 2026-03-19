#!/usr/bin/env python3
"""Step 4 baseline econometric model (TWFE, clustered SE)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from linearmodels.panel import PanelOLS


def fit_twfe(df: pd.DataFrame, outcome: str) -> PanelOLS:
    model_df = df.copy()
    model_df = model_df.set_index(["team_id", "week_index"]).sort_index()

    y = model_df[outcome]
    x = model_df[["treated"]]

    model = PanelOLS(y, x, entity_effects=True, time_effects=True, drop_absorbed=True)
    result = model.fit(cov_type="clustered", cluster_entity=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Step 4 baseline model")
    parser.add_argument("--input", default="outputs/step2_team_week_panel.csv")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    model_df = df.loc[df["analysis_sample"] == 1].copy()

    result = fit_twfe(model_df, "junior_output_share")

    ci = result.conf_int()
    treated_row = {
        "model": "Step4_baseline_twfe",
        "outcome": "junior_output_share",
        "nobs": int(result.nobs),
        "n_teams": int(model_df["team_id"].nunique()),
        "n_weeks": int(model_df["week_index"].nunique()),
        "coef_treated": float(result.params["treated"]),
        "se_treated": float(result.std_errors["treated"]),
        "tstat_treated": float(result.tstats["treated"]),
        "pvalue_treated": float(result.pvalues["treated"]),
        "ci_low_95": float(ci.loc["treated", "lower"]),
        "ci_high_95": float(ci.loc["treated", "upper"]),
        "r2_within": float(result.rsquared_within),
        "r2_overall": float(result.rsquared_overall),
    }

    pd.DataFrame([treated_row]).to_csv(output_dir / "step4_baseline_results.csv", index=False)
    (output_dir / "step4_baseline_model_summary.txt").write_text(str(result.summary), encoding="utf-8")

    print("Wrote Step 4 baseline outputs to outputs/")


if __name__ == "__main__":
    main()
