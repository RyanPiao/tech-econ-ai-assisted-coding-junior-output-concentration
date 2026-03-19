#!/usr/bin/env python3
"""Run robustness and sensitivity checks for the synthetic benchmarked panel."""

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
    parser = argparse.ArgumentParser(description="Run robustness checks")
    parser.add_argument("--input", default="data/synthetic/synthetic_team_week_panel.csv")
    parser.add_argument("--out-table", default="outputs/tables/table_robustness_results.csv")
    parser.add_argument("--out-summary", default="outputs/tables/table_robustness_model_summaries.txt")
    args = parser.parse_args()

    input_path = ROOT / args.input
    out_table = ROOT / args.out_table
    out_summary = ROOT / args.out_summary

    out_table.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    df = df.loc[df["analysis_sample"] == 1].copy()

    # Derived variables for robustness variants.
    q01, q99 = df["junior_output_share"].quantile([0.01, 0.99])
    df["junior_output_share_winsor"] = df["junior_output_share"].clip(lower=q01, upper=q99)
    df["lead3_treated"] = (
        df["adoption_week"].notna()
        & (df["week_index"] >= (df["adoption_week"] - 3))
        & (df["week_index"] < df["adoption_week"])
    ).astype(int)

    rows = []
    summary_blocks: list[str] = []

    specs = [
        {
            "name": "robust_alt_outcome_merged_share",
            "outcome": "junior_merged_pr_share",
            "rhs": ["treated"],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_alt_outcome_ticket_share",
            "outcome": "junior_ticket_share",
            "rhs": ["treated"],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_winsorized_outcome",
            "outcome": "junior_output_share_winsor",
            "rhs": ["treated"],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_placebo_lead",
            "outcome": "junior_output_share",
            "rhs": ["treated", "lead3_treated"],
            "term_focus": ["treated", "lead3_treated"],
            "sample_query": None,
        },
        {
            "name": "robust_large_teams_only",
            "outcome": "junior_output_share",
            "rhs": ["treated"],
            "term_focus": ["treated"],
            "sample_query": "team_size >= 8",
        },
    ]

    for spec in specs:
        sample = df if spec["sample_query"] is None else df.query(spec["sample_query"]).copy()
        sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=[spec["outcome"]])
        result = twfe_ols(df=sample, outcome=spec["outcome"], rhs_terms=spec["rhs"])
        extracted = extract_terms(
            result=result,
            model_name=spec["name"],
            outcome=spec["outcome"],
            terms=spec["term_focus"],
            df=sample,
        )
        rows.extend(extracted)
        summary_blocks.append(f"[{spec['name']}]\n{str(result.summary())}\n")

    pd.DataFrame([asdict(r) for r in rows]).to_csv(out_table, index=False)
    out_summary.write_text("\n".join(summary_blocks), encoding="utf-8")

    print(f"Wrote {out_table}")
    print(f"Wrote {out_summary}")


if __name__ == "__main__":
    main()
