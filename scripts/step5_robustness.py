#!/usr/bin/env python3
"""Step 5 robustness checks for synthetic panel model."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from linearmodels.panel import PanelOLS


def fit_panel(
    df: pd.DataFrame,
    outcome: str,
    exog_cols: list[str],
    weights_col: str | None = None,
):
    model_df = df.set_index(["team_id", "week_index"]).sort_index()
    y = model_df[outcome]
    x = model_df[exog_cols]
    weights = None if weights_col is None else model_df[weights_col]

    model = PanelOLS(
        y,
        x,
        weights=weights,
        entity_effects=True,
        time_effects=True,
        drop_absorbed=True,
    )
    return model.fit(cov_type="clustered", cluster_entity=True)


def collect_rows(spec: str, outcome: str, result, n_teams: int, n_weeks: int) -> list[dict]:
    ci = result.conf_int()
    rows = []
    for term in result.params.index.tolist():
        rows.append(
            {
                "spec": spec,
                "outcome": outcome,
                "term": term,
                "nobs": int(result.nobs),
                "n_teams": int(n_teams),
                "n_weeks": int(n_weeks),
                "coef": float(result.params[term]),
                "se": float(result.std_errors[term]),
                "tstat": float(result.tstats[term]),
                "pvalue": float(result.pvalues[term]),
                "ci_low_95": float(ci.loc[term, "lower"]),
                "ci_high_95": float(ci.loc[term, "upper"]),
                "r2_within": float(result.rsquared_within),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Step 5 robustness checks")
    parser.add_argument("--input", default="outputs/step2_team_week_panel.csv")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    df = df.loc[df["analysis_sample"] == 1].copy()

    q_low = df["junior_output_share"].quantile(0.01)
    q_high = df["junior_output_share"].quantile(0.99)
    df["junior_output_share_winsor"] = df["junior_output_share"].clip(lower=q_low, upper=q_high)

    df["lead4_treated"] = (
        df["adoption_week"].notna()
        & (df["week_index"] >= (df["adoption_week"] - 4))
        & (df["week_index"] < df["adoption_week"])
    ).astype(int)

    specs = [
        {
            "spec": "alt_outcome_merged_pr_share",
            "outcome": "junior_merged_pr_share",
            "exog": ["treated"],
            "weights": None,
        },
        {
            "spec": "alt_outcome_ticket_share",
            "outcome": "junior_ticket_share",
            "exog": ["treated"],
            "weights": None,
        },
        {
            "spec": "weighted_by_total_output",
            "outcome": "junior_output_share",
            "exog": ["treated"],
            "weights": "total_output",
        },
        {
            "spec": "winsorized_outcome_1pct",
            "outcome": "junior_output_share_winsor",
            "exog": ["treated"],
            "weights": None,
        },
        {
            "spec": "placebo_lead_window",
            "outcome": "junior_output_share",
            "exog": ["treated", "lead4_treated"],
            "weights": None,
        },
    ]

    rows: list[dict] = []
    summary_lines = []

    for spec in specs:
        result = fit_panel(df, spec["outcome"], spec["exog"], spec["weights"])
        rows.extend(
            collect_rows(
                spec=spec["spec"],
                outcome=spec["outcome"],
                result=result,
                n_teams=df["team_id"].nunique(),
                n_weeks=df["week_index"].nunique(),
            )
        )
        summary_lines.append(f"[{spec['spec']}]\n{result.summary}\n")

    pd.DataFrame(rows).to_csv(output_dir / "step5_robustness_results.csv", index=False)
    (output_dir / "step5_robustness_model_summaries.txt").write_text(
        "\n".join(summary_lines), encoding="utf-8"
    )

    print("Wrote Step 5 robustness outputs to outputs/")


if __name__ == "__main__":
    main()
