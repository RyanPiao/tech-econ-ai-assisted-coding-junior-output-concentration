from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def save_adoption_histogram(df: pd.DataFrame, path):
    adopters = df.groupby("team_id", as_index=False)["adoption_week"].first()["adoption_week"].dropna()
    plt.figure(figsize=(7, 4))
    if adopters.empty:
        plt.text(0.5, 0.5, "No adopters in sample", ha="center", va="center")
        plt.xlim(0, 1)
        plt.ylim(0, 1)
    else:
        bins = range(int(adopters.min()), int(adopters.max()) + 2)
        plt.hist(adopters, bins=bins, edgecolor="black", alpha=0.8)
        plt.xlabel("Adoption week")
        plt.ylabel("Number of teams")
    plt.title("Figure 1. Distribution of team adoption timing")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()


def save_group_trends(df: pd.DataFrame, path):
    tmp = df.copy()
    tmp["ever_treated"] = tmp.groupby("team_id")["adoption_week"].transform(lambda s: int(s.notna().any()))
    grp = (
        tmp.groupby(["week_index", "ever_treated"], as_index=False)["junior_output_share"]
        .mean()
        .rename(columns={"ever_treated": "group"})
    )
    grp["group"] = grp["group"].map({0: "Never-adopter teams", 1: "Ever-adopter teams"})

    plt.figure(figsize=(7, 4))
    for g, part in grp.groupby("group"):
        plt.plot(part["week_index"], part["junior_output_share"], marker="o", linewidth=1.5, label=g)
    plt.xlabel("Week index")
    plt.ylabel("Mean junior output share")
    plt.title("Figure 2. Average junior output share by treatment group")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()


def save_event_study_plot(coef_df: pd.DataFrame, path):
    plot_df = coef_df.sort_values("event_time")
    plt.figure(figsize=(7.5, 4.5))
    plt.axhline(0.0, color="black", linewidth=1)
    plt.axvline(-1.0, color="gray", linestyle="--", linewidth=1)

    x = plot_df["event_time"]
    y = plot_df["coef"]
    yerr_low = y - plot_df["ci_low_95"]
    yerr_high = plot_df["ci_high_95"] - y
    plt.errorbar(x, y, yerr=[yerr_low, yerr_high], fmt="o", capsize=3)

    plt.xlabel("Event time (weeks relative to adoption)")
    plt.ylabel("Coefficient on event-time dummy")
    plt.title("Figure 3. Event-study estimates (reference week = -1)")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
