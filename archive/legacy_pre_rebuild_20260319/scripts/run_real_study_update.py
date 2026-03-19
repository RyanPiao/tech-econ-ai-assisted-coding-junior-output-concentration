#!/usr/bin/env python3
"""Run end-to-end real-data study update (pilot + expanded) in one shot.

Pipeline:
1) Step 2 real ingestion (GH Archive + AI-adoption proxy)
2) Step 3-6 analysis for pilot sample
3) Step 3-6 analysis for expanded sample
4) Cross-sample comparison tables and figures
5) Executive summary note for Ryan
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class SampleConfig:
    name: str
    start_date: str
    end_date: str
    repos_file: str
    hour_step: int
    hour_offset: int
    max_lines_per_hour: int
    junior_threshold: int
    ai_intensity_threshold: float
    ai_min_signal_events: int
    min_total_output: int
    lead_max: int
    lag_max: int


def run_cmd(cmd: list[str], workdir: Path) -> None:
    rendered = " ".join(cmd)
    print(f"\n$ {rendered}")
    subprocess.run(cmd, cwd=workdir, check=True)


def run_sample(root: Path, cfg: SampleConfig) -> dict:
    py = sys.executable
    sample_out = root / "outputs" / f"real_{cfg.name}"
    sample_out.mkdir(parents=True, exist_ok=True)

    panel_path = sample_out / f"step2_real_repo_week_panel_{cfg.name}.csv"

    run_cmd(
        [
            py,
            "scripts/step2_real_pipeline.py",
            "--start-date",
            cfg.start_date,
            "--end-date",
            cfg.end_date,
            "--repos-file",
            cfg.repos_file,
            "--output-dir",
            str(sample_out),
            "--tag",
            cfg.name,
            "--hour-step",
            str(cfg.hour_step),
            "--hour-offset",
            str(cfg.hour_offset),
            "--max-lines-per-hour",
            str(cfg.max_lines_per_hour),
            "--junior-threshold",
            str(cfg.junior_threshold),
            "--ai-intensity-threshold",
            str(cfg.ai_intensity_threshold),
            "--ai-min-signal-events",
            str(cfg.ai_min_signal_events),
            "--min-total-output",
            str(cfg.min_total_output),
        ],
        workdir=root,
    )

    run_cmd([py, "scripts/step3_eda.py", "--input", str(panel_path), "--output-dir", str(sample_out)], workdir=root)
    run_cmd([py, "scripts/step4_baseline_model.py", "--input", str(panel_path), "--output-dir", str(sample_out)], workdir=root)
    run_cmd([py, "scripts/step5_robustness.py", "--input", str(panel_path), "--output-dir", str(sample_out)], workdir=root)
    run_cmd(
        [
            py,
            "scripts/step6_dynamic_check.py",
            "--input",
            str(panel_path),
            "--output-dir",
            str(sample_out),
            "--lead-max",
            str(cfg.lead_max),
            "--lag-max",
            str(cfg.lag_max),
        ],
        workdir=root,
    )

    return {
        "name": cfg.name,
        "output_dir": str(sample_out),
        "panel_path": str(panel_path),
        "metadata_path": str(sample_out / f"step2_real_metadata_{cfg.name}.json"),
        "baseline_path": str(sample_out / "step4_baseline_results.csv"),
        "robustness_path": str(sample_out / "step5_robustness_results.csv"),
        "event_path": str(sample_out / "step6_event_study_coefficients.csv"),
        "event_meta_path": str(sample_out / "step6_event_study_metadata.json"),
    }


def maybe_make_figures(out_dir: Path, baseline: pd.DataFrame, event_compare: pd.DataFrame) -> list[str]:
    figure_paths: list[str] = []
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[warn] matplotlib unavailable, skipping figures: {exc}")
        return figure_paths

    # Figure 1: baseline coefficient comparison
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(baseline))
    ax.errorbar(
        x,
        baseline["coef_treated"],
        yerr=1.96 * baseline["se_treated"],
        fmt="o",
        capsize=4,
        color="#1f77b4",
    )
    ax.axhline(0.0, linestyle="--", color="gray", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(baseline["sample"].tolist())
    ax.set_ylabel("Treatment effect on junior_output_share")
    ax.set_title("Baseline TWFE: Pilot vs Expanded")
    fig.tight_layout()
    p1 = out_dir / "figure_baseline_pilot_vs_expanded.png"
    fig.savefig(p1, dpi=160)
    plt.close(fig)
    figure_paths.append(str(p1))

    # Figure 2: event-study overlay
    fig, ax = plt.subplots(figsize=(7, 4))
    for sample in sorted(event_compare["sample"].unique()):
        s = event_compare.loc[event_compare["sample"] == sample].sort_values("event_time")
        ax.plot(s["event_time"], s["coef"], marker="o", label=sample)
    ax.axhline(0.0, linestyle="--", color="gray", linewidth=1)
    ax.axvline(-1, linestyle=":", color="gray", linewidth=1)
    ax.set_xlabel("Event time (weeks relative to proxy adoption)")
    ax.set_ylabel("Coefficient")
    ax.set_title("Event-study coefficients by sample")
    ax.legend()
    fig.tight_layout()
    p2 = out_dir / "figure_event_study_overlay.png"
    fig.savefig(p2, dpi=160)
    plt.close(fig)
    figure_paths.append(str(p2))

    return figure_paths


def build_comparison(root: Path, sample_runs: list[dict], note_out: Path) -> dict:
    comp_dir = root / "outputs" / "real_comparison"
    comp_dir.mkdir(parents=True, exist_ok=True)

    baseline_rows = []
    step2_meta_rows = []
    event_meta_rows = []
    robust_rows = []
    event_long = []

    for run in sample_runs:
        sample = run["name"]

        b = pd.read_csv(run["baseline_path"])
        if b.empty:
            raise ValueError(f"Baseline output empty for sample={sample}")
        b = b.assign(sample=sample)
        baseline_rows.append(b)

        r = pd.read_csv(run["robustness_path"])
        r = r.assign(sample=sample)
        robust_rows.append(r)

        e = pd.read_csv(run["event_path"])
        e = e.assign(sample=sample)
        event_long.append(e)

        step2_meta = json.loads(Path(run["metadata_path"]).read_text(encoding="utf-8"))
        step2_meta_rows.append(
            {
                "sample": sample,
                "n_rows": step2_meta["summary"]["n_rows"],
                "n_teams": step2_meta["summary"]["n_teams"],
                "n_weeks": step2_meta["summary"]["n_weeks"],
                "analysis_sample_rows": step2_meta["summary"]["analysis_sample_rows"],
                "adoption_rate_team_level": step2_meta["summary"]["adoption_rate_team_level"],
                "treated_share": step2_meta["summary"]["treated_share"],
                "mean_junior_output_share": step2_meta["summary"]["mean_junior_output_share"],
                "mean_ai_intensity": step2_meta["summary"]["mean_ai_intensity"],
            }
        )

        e_meta = json.loads(Path(run["event_meta_path"]).read_text(encoding="utf-8"))
        event_meta_rows.append(
            {
                "sample": sample,
                "average_post_event_coef": e_meta.get("average_post_event_coef"),
                "pretrend_pvalue": e_meta.get("pretrend_pvalue"),
                "nobs": e_meta.get("nobs"),
            }
        )

    baseline = pd.concat(baseline_rows, ignore_index=True)
    baseline = baseline[
        [
            "sample",
            "model",
            "outcome",
            "nobs",
            "n_teams",
            "n_weeks",
            "coef_treated",
            "se_treated",
            "pvalue_treated",
            "ci_low_95",
            "ci_high_95",
            "r2_within",
        ]
    ]
    baseline.to_csv(comp_dir / "table_baseline_pilot_vs_expanded.csv", index=False)

    robust = pd.concat(robust_rows, ignore_index=True)
    robust_treated = robust.loc[robust["term"] == "treated", ["sample", "spec", "outcome", "coef", "se", "pvalue"]]
    robust_pivot = robust_treated.pivot_table(index=["spec", "outcome"], columns="sample", values="coef").reset_index()
    if {"pilot", "expanded"}.issubset(set(robust_treated["sample"])):
        robust_pivot["coef_diff_expanded_minus_pilot"] = robust_pivot["expanded"] - robust_pivot["pilot"]
    robust_pivot.to_csv(comp_dir / "table_robustness_treated_comparison.csv", index=False)
    robust_treated.to_csv(comp_dir / "table_robustness_treated_long.csv", index=False)

    event_compare = pd.concat(event_long, ignore_index=True)
    event_compare.to_csv(comp_dir / "table_event_study_coefficients_long.csv", index=False)

    event_wide = event_compare.pivot_table(index="event_time", columns="sample", values="coef").reset_index()
    if {"pilot", "expanded"}.issubset(set(event_compare["sample"])):
        event_wide["coef_diff_expanded_minus_pilot"] = event_wide["expanded"] - event_wide["pilot"]
    event_wide.to_csv(comp_dir / "table_event_study_coef_comparison.csv", index=False)

    step2_meta_df = pd.DataFrame(step2_meta_rows)
    step2_meta_df.to_csv(comp_dir / "table_sample_construction_summary.csv", index=False)

    event_meta_df = pd.DataFrame(event_meta_rows)
    event_meta_df.to_csv(comp_dir / "table_event_meta_summary.csv", index=False)

    figs = maybe_make_figures(comp_dir, baseline=baseline, event_compare=event_compare)

    summary = {
        "samples": [r["name"] for r in sample_runs],
        "baseline_table": str(comp_dir / "table_baseline_pilot_vs_expanded.csv"),
        "robustness_table": str(comp_dir / "table_robustness_treated_comparison.csv"),
        "event_coef_table": str(comp_dir / "table_event_study_coef_comparison.csv"),
        "sample_summary_table": str(comp_dir / "table_sample_construction_summary.csv"),
        "event_meta_table": str(comp_dir / "table_event_meta_summary.csv"),
        "figures": figs,
        "ai_proxy_disclaimer": "AI adoption is inferred from public-text proxy signals and is not direct tool telemetry.",
    }
    (comp_dir / "real_update_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Executive summary for Ryan (concise note).
    step2_map = {r["sample"]: r for r in step2_meta_rows}
    base_map = {r["sample"]: r for r in baseline.to_dict(orient="records")}
    event_map = {r["sample"]: r for r in event_meta_rows}

    lines = [
        "# Real-Data Study Update (Pilot vs Expanded) — Note for Ryan",
        "",
        "## What we ran",
        "- End-to-end real-data path using GH Archive events with an AI-adoption *proxy* built from public text mentions.",
        "- Same econometric pipeline as synthetic path (Step 3-6): EDA, TWFE baseline, robustness, and dynamic event-time check.",
        "",
        "## Sample construction snapshot",
    ]
    for sample in ["pilot", "expanded"]:
        s = step2_map[sample]
        lines.append(
            f"- **{sample.title()}**: {int(s['n_teams'])} repos × {int(s['n_weeks'])} weeks = {int(s['n_rows'])} repo-weeks "
            f"(analysis rows={int(s['analysis_sample_rows'])}, adoption-rate={s['adoption_rate_team_level']:.2f}, treated-share={s['treated_share']:.2f})."
        )

    lines.extend(
        [
            "",
            "## Baseline estimate (junior_output_share)",
            f"- **Pilot**: coef={base_map['pilot']['coef_treated']:.4f}, se={base_map['pilot']['se_treated']:.4f}, p={base_map['pilot']['pvalue_treated']:.4f}",
            f"- **Expanded**: coef={base_map['expanded']['coef_treated']:.4f}, se={base_map['expanded']['se_treated']:.4f}, p={base_map['expanded']['pvalue_treated']:.4f}",
            f"- **Difference (expanded - pilot)**: {base_map['expanded']['coef_treated'] - base_map['pilot']['coef_treated']:.4f}",
            "",
            "## Dynamic check",
            f"- Pilot average post-event coefficient: {event_map['pilot']['average_post_event_coef']:.4f} (pretrend p={event_map['pilot']['pretrend_pvalue']:.4f})",
            f"- Expanded average post-event coefficient: {event_map['expanded']['average_post_event_coef']:.4f} (pretrend p={event_map['expanded']['pretrend_pvalue']:.4f})",
            "",
            "## Interpretation limits",
            "- AI adoption here is *proxy-based* (keyword mentions in public text) and should not be read as verified enterprise tool usage.",
            "- Repo-level public events are a proxy for team behavior and likely omit private/internal workflow.",
            "- Junior classification is heuristic (prior contribution count threshold), not HR role data.",
            "",
            "## Output locations",
            "- Pilot artifacts: `outputs/real_pilot/`",
            "- Expanded artifacts: `outputs/real_expanded/`",
            "- Comparison tables/figures: `outputs/real_comparison/`",
            "",
            "## Recommended next step",
            "- Scale to a longer horizon and denser hour sampling, then stress-test treatment coding with alternative keyword dictionaries and thresholds.",
        ]
    )
    note_out.write_text("\n".join(lines), encoding="utf-8")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full real-data study update (pilot + expanded)")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--pilot-start", default="2025-02-01")
    parser.add_argument("--pilot-end", default="2025-02-21")
    parser.add_argument("--expanded-start", default="2025-01-15")
    parser.add_argument("--expanded-end", default="2025-03-15")
    parser.add_argument("--pilot-hour-step", type=int, default=24)
    parser.add_argument("--expanded-hour-step", type=int, default=24)
    parser.add_argument("--pilot-hour-offset", type=int, default=0)
    parser.add_argument("--expanded-hour-offset", type=int, default=12)
    parser.add_argument("--max-lines-per-hour", type=int, default=120000)
    args = parser.parse_args()

    root = Path(args.root).resolve()

    pilot_cfg = SampleConfig(
        name="pilot",
        start_date=args.pilot_start,
        end_date=args.pilot_end,
        repos_file="scripts/config/pilot_repos.txt",
        hour_step=args.pilot_hour_step,
        hour_offset=args.pilot_hour_offset,
        max_lines_per_hour=args.max_lines_per_hour,
        junior_threshold=25,
        ai_intensity_threshold=0.02,
        ai_min_signal_events=2,
        min_total_output=3,
        lead_max=2,
        lag_max=3,
    )

    expanded_cfg = SampleConfig(
        name="expanded",
        start_date=args.expanded_start,
        end_date=args.expanded_end,
        repos_file="scripts/config/expanded_repos.txt",
        hour_step=args.expanded_hour_step,
        hour_offset=args.expanded_hour_offset,
        max_lines_per_hour=args.max_lines_per_hour,
        junior_threshold=25,
        ai_intensity_threshold=0.02,
        ai_min_signal_events=2,
        min_total_output=3,
        lead_max=3,
        lag_max=5,
    )

    runs = [run_sample(root, pilot_cfg), run_sample(root, expanded_cfg)]

    note_out = root / "docs" / "REAL_EXECUTIVE_SUMMARY_RYAN.md"
    summary = build_comparison(root, runs, note_out=note_out)

    print("\nDone. Real-data update summary:")
    print(json.dumps(summary, indent=2))
    print(f"\nExecutive note: {note_out}")


if __name__ == "__main__":
    main()
