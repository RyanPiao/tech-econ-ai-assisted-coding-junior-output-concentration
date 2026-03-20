#!/usr/bin/env python3
"""Run baseline real-data TWFE analysis."""

from __future__ import annotations

import argparse
import sys
import warnings
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", message=r"covariance of constraints does not have full rank.*")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.econometrics import extract_terms, twfe_ols


def main() -> None:
    parser = argparse.ArgumentParser(description="Run baseline model on real-data panel")
    parser.add_argument("--input", default="data/processed/real_panel_clean.csv")
    parser.add_argument("--out-table", default="outputs/tables/table_baseline_results.csv")
    parser.add_argument("--out-summary", default="outputs/tables/table_baseline_model_summary.txt")
    args = parser.parse_args()

    input_path = ROOT / args.input
    out_table = ROOT / args.out_table
    out_summary = ROOT / args.out_summary

    out_table.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    df = df.loc[df["analysis_sample"] == 1].copy()

    required = ["junior_output_share", "treated", "team_id", "week_index"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Baseline controls are all observed variables.
    rhs_terms = ["treated", "log_total_output", "post_merge_bug_proxy_filled"]
    keep = ["junior_output_share", *rhs_terms, "team_id", "week_index"]
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=keep)

    if df.empty or df["treated"].nunique() < 2:
        rows = [
            {
                "model": "baseline_twfe_real",
                "outcome": "junior_output_share",
                "term": "treated",
                "coef": np.nan,
                "se": np.nan,
                "tstat": np.nan,
                "pvalue": np.nan,
                "ci_low_95": np.nan,
                "ci_high_95": np.nan,
                "nobs": int(df.shape[0]),
                "n_teams": int(df["team_id"].nunique()) if not df.empty else 0,
                "n_weeks": int(df["week_index"].nunique()) if not df.empty else 0,
                "r2": np.nan,
                "note": "not_estimable_due_to_no_treatment_variation",
            }
        ]
        pd.DataFrame(rows).to_csv(out_table, index=False)
        out_summary.write_text(
            "Baseline model not estimable: no treatment variation in analysis sample.\n",
            encoding="utf-8",
        )
    else:
        result = twfe_ols(df=df, outcome="junior_output_share", rhs_terms=rhs_terms)
        rows = extract_terms(
            result=result,
            model_name="baseline_twfe_real",
            outcome="junior_output_share",
            terms=["treated", "log_total_output", "post_merge_bug_proxy_filled"],
            df=df,
        )
        pd.DataFrame([asdict(r) for r in rows]).to_csv(out_table, index=False)
        out_summary.write_text(str(result.summary()), encoding="utf-8")

    print(f"Wrote {out_table}")
    print(f"Wrote {out_summary}")


if __name__ == "__main__":
    main()
