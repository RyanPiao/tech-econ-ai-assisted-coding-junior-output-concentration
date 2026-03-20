#!/usr/bin/env python3
"""Run robustness checks on real-data panel."""

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


def run_spec(df: pd.DataFrame, name: str, outcome: str, rhs: list[str], term_focus: list[str]):
    sample = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[outcome, *rhs])
    if sample.empty or sample["treated"].nunique() < 2:
        rows = []
        for term in term_focus:
            rows.append(
                {
                    "model": name,
                    "outcome": outcome,
                    "term": term,
                    "coef": np.nan,
                    "se": np.nan,
                    "tstat": np.nan,
                    "pvalue": np.nan,
                    "ci_low_95": np.nan,
                    "ci_high_95": np.nan,
                    "nobs": int(sample.shape[0]),
                    "n_teams": int(sample["team_id"].nunique()) if not sample.empty else 0,
                    "n_weeks": int(sample["week_index"].nunique()) if not sample.empty else 0,
                    "r2": np.nan,
                    "note": "not_estimable_due_to_no_treatment_variation",
                }
            )
        return rows, f"[{name}]\nNot estimable: no treatment variation in sample.\n"

    result = twfe_ols(df=sample, outcome=outcome, rhs_terms=rhs)
    extracted = extract_terms(
        result=result,
        model_name=name,
        outcome=outcome,
        terms=term_focus,
        df=sample,
    )
    return [asdict(r) for r in extracted], f"[{name}]\n{str(result.summary())}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run robustness checks")
    parser.add_argument("--input", default="data/processed/real_panel_clean.csv")
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

    q01, q99 = df["junior_output_share"].quantile([0.01, 0.99])
    df["junior_output_share_winsor"] = df["junior_output_share"].clip(lower=q01, upper=q99)
    df["lead2_treated"] = (
        df["adoption_week"].notna()
        & (df["week_index"] >= (df["adoption_week"] - 2))
        & (df["week_index"] < df["adoption_week"])
    ).astype(int)

    rows: list[dict] = []
    summary_blocks: list[str] = []

    specs = [
        {
            "name": "robust_no_controls",
            "outcome": "junior_output_share",
            "rhs": ["treated"],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_full_controls",
            "outcome": "junior_output_share",
            "rhs": [
                "treated",
                "log_total_output",
                "post_merge_bug_proxy_filled",
                "median_cycle_time_hours_filled",
                "review_latency_hours_filled",
            ],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_alt_outcome_merged_share",
            "outcome": "junior_merged_pr_share",
            "rhs": ["treated", "log_total_output"],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_alt_outcome_ticket_share",
            "outcome": "junior_ticket_share",
            "rhs": ["treated", "log_total_output"],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_winsorized_outcome",
            "outcome": "junior_output_share_winsor",
            "rhs": ["treated", "log_total_output", "post_merge_bug_proxy_filled"],
            "term_focus": ["treated"],
            "sample_query": None,
        },
        {
            "name": "robust_placebo_lead",
            "outcome": "junior_output_share",
            "rhs": ["treated", "lead2_treated", "log_total_output"],
            "term_focus": ["treated", "lead2_treated"],
            "sample_query": None,
        },
        {
            "name": "robust_high_output_subsample",
            "outcome": "junior_output_share",
            "rhs": ["treated", "log_total_output", "post_merge_bug_proxy_filled"],
            "term_focus": ["treated"],
            "sample_query": "total_output >= 5",
        },
    ]

    for spec in specs:
        sample = df if spec["sample_query"] is None else df.query(spec["sample_query"]).copy()
        res_rows, summary = run_spec(
            df=sample,
            name=spec["name"],
            outcome=spec["outcome"],
            rhs=spec["rhs"],
            term_focus=spec["term_focus"],
        )
        rows.extend(res_rows)
        summary_blocks.append(summary)

    pd.DataFrame(rows).to_csv(out_table, index=False)
    out_summary.write_text("\n".join(summary_blocks), encoding="utf-8")

    print(f"Wrote {out_table}")
    print(f"Wrote {out_summary}")


if __name__ == "__main__":
    main()
