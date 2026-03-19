#!/usr/bin/env python3
"""Run baseline econometric analysis (TWFE-style OLS with clustered SEs)."""

from __future__ import annotations

import argparse
import sys
import warnings
from dataclasses import asdict
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore", message=r"covariance of constraints does not have full rank.*")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.econometrics import extract_terms, twfe_ols


def main() -> None:
    parser = argparse.ArgumentParser(description="Run baseline model")
    parser.add_argument("--input", default="data/synthetic/synthetic_team_week_panel.csv")
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

    result = twfe_ols(df=df, outcome="junior_output_share", rhs_terms=["treated"])
    rows = extract_terms(
        result=result,
        model_name="baseline_twfe",
        outcome="junior_output_share",
        terms=["treated"],
        df=df,
    )

    pd.DataFrame([asdict(r) for r in rows]).to_csv(out_table, index=False)
    out_summary.write_text(str(result.summary()), encoding="utf-8")

    print(f"Wrote {out_table}")
    print(f"Wrote {out_summary}")


if __name__ == "__main__":
    main()
