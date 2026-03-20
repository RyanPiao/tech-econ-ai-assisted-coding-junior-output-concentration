#!/usr/bin/env python3
"""Run v3 long-horizon, multi-proxy, multi-method identification sweep (real-data-first).

Outputs are publication-facing diagnostics tables only; interpretation remains associational.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import norm
from statsmodels.tools.sm_exceptions import ConvergenceWarning

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.econometrics import build_event_dummies, pretrend_pvalue, twfe_ols
from src.io_helpers import write_json


@dataclass(frozen=True)
class ProxySpec:
    name: str
    ai_intensity_threshold: float
    ai_min_signal_events: int
    ai_min_eligible_events: int
    rationale: str


PROXY_SPECS: list[ProxySpec] = [
    ProxySpec(
        name="strict",
        ai_intensity_threshold=0.10,
        ai_min_signal_events=5,
        ai_min_eligible_events=5,
        rationale=(
            "High-precision proxy: requires relatively high mention intensity and multiple AI-signal events "
            "with non-trivial eligible text volume."
        ),
    ),
    ProxySpec(
        name="balanced",
        ai_intensity_threshold=0.02,
        ai_min_signal_events=2,
        ai_min_eligible_events=1,
        rationale=(
            "Baseline-like proxy aligned with prior pipeline defaults; balances false positives and false negatives."
        ),
    ),
    ProxySpec(
        name="broad",
        ai_intensity_threshold=0.005,
        ai_min_signal_events=1,
        ai_min_eligible_events=1,
        rationale=(
            "High-recall proxy: allows low-intensity single-signal weeks to test sensitivity to wider treatment coding."
        ),
    ),
]


def switcher_count(df: pd.DataFrame) -> int:
    return int(sum(((g["treated"] == 0).any() and (g["treated"] == 1).any()) for _, g in df.groupby("team_id")))


def adoption_dispersion(df: pd.DataFrame) -> float:
    ad = df.loc[df["adoption_week"].notna(), ["team_id", "adoption_week"]].drop_duplicates()["adoption_week"]
    if ad.empty:
        return float("nan")
    return float(ad.std(ddof=0))


def _build_proxy_panel(raw: pd.DataFrame, spec: ProxySpec, min_total_output_for_sample: int) -> pd.DataFrame:
    out = raw.copy()
    out["team_id"] = out["team_id"].astype(str).str.lower()
    out["calendar_week"] = pd.to_datetime(out["calendar_week"]).dt.date
    out = out.sort_values(["team_id", "week_index"]).drop_duplicates(["team_id", "week_index"], keep="last")

    out["ai_proxy_trigger"] = (
        (out["ai_intensity"] >= spec.ai_intensity_threshold)
        & (out["ai_signal_events"] >= spec.ai_min_signal_events)
        & (out["ai_eligible_events"] >= spec.ai_min_eligible_events)
    ).astype(int)

    adoption = (
        out.groupby("team_id", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "adoption_week": (
                        float(g.loc[g["ai_proxy_trigger"] == 1, "week_index"].min())
                        if (g["ai_proxy_trigger"] == 1).any()
                        else np.nan
                    )
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    out = out.drop(columns=[c for c in ["adoption_week", "treated", "event_time", "post_period"] if c in out.columns])
    out = out.merge(adoption, on="team_id", how="left")

    max_week = int(out["week_index"].max()) if not out.empty else 0
    if max_week >= 2:
        out.loc[out["adoption_week"] == 1, "adoption_week"] = 2

    out["treated"] = (out["adoption_week"].notna() & (out["week_index"] >= out["adoption_week"])).astype(int)
    out["post_period"] = out["treated"]
    out["event_time"] = np.where(out["adoption_week"].notna(), out["week_index"] - out["adoption_week"], np.nan)

    out["log_total_output"] = np.log1p(out["total_output"])
    out["log_ai_eligible_events"] = np.log1p(out["ai_eligible_events"])

    for col in ["median_cycle_time_hours", "review_latency_hours", "post_merge_bug_proxy"]:
        team_median = out.groupby("team_id")[col].transform("median")
        global_median = float(out[col].median()) if out[col].notna().any() else 0.0
        out[f"{col}_filled"] = out[col].fillna(team_median).fillna(global_median)

    out["analysis_sample"] = ((out["total_output"] >= min_total_output_for_sample) & out["junior_output_share"].notna()).astype(int)
    return out


def _panel_summary(panel: pd.DataFrame) -> dict[str, Any]:
    sample = panel.loc[panel["analysis_sample"] == 1].copy()
    ad = sample.loc[sample["adoption_week"].notna(), ["team_id", "adoption_week"]].drop_duplicates()

    return {
        "n_team_weeks": int(sample.shape[0]),
        "n_teams": int(sample["team_id"].nunique()),
        "n_weeks": int(sample["week_index"].nunique()),
        "switchers": int(switcher_count(sample)) if not sample.empty else 0,
        "treated_share": float(sample["treated"].mean()) if not sample.empty else float("nan"),
        "adopter_teams": int(ad["team_id"].nunique()),
        "never_adopter_teams": int(sample["team_id"].nunique() - ad["team_id"].nunique()),
        "adoption_timing_dispersion_sd": float(adoption_dispersion(sample)) if not sample.empty else float("nan"),
    }


def _empty_result(proxy: str, method: str, summary: dict[str, Any], note: str) -> dict[str, Any]:
    return {
        "proxy": proxy,
        "method": method,
        "coef": np.nan,
        "se": np.nan,
        "pvalue": np.nan,
        "ci_low_95": np.nan,
        "ci_high_95": np.nan,
        "pretrend_joint_pvalue": np.nan,
        "placebo_coef": np.nan,
        "placebo_pvalue": np.nan,
        "nobs": int(summary["n_team_weeks"]),
        "n_teams": int(summary["n_teams"]),
        "n_weeks": int(summary["n_weeks"]),
        "switchers": int(summary["switchers"]),
        "timing_dispersion_sd": float(summary["adoption_timing_dispersion_sd"]),
        "note": note,
    }


def _extract_term(result, term: str) -> tuple[float, float, float, float, float]:
    ci = result.conf_int()
    return (
        float(result.params[term]),
        float(result.bse[term]),
        float(result.pvalues[term]),
        float(ci.loc[term, 0]),
        float(ci.loc[term, 1]),
    )


def _placebo_shift_treated(df: pd.DataFrame, shift_weeks: int = 8) -> pd.Series:
    ad = df["adoption_week"]
    return (ad.notna() & (df["week_index"] >= (ad + shift_weeks))).astype(int)


def _run_twfe(panel: pd.DataFrame, proxy: str, summary: dict[str, Any]) -> dict[str, Any]:
    sample = panel.loc[panel["analysis_sample"] == 1].copy()
    keep = [
        "junior_output_share",
        "treated",
        "log_total_output",
        "post_merge_bug_proxy_filled",
        "team_id",
        "week_index",
    ]
    sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=keep)

    if sample.empty or sample["treated"].nunique() < 2:
        return _empty_result(proxy, "twfe", summary, "not_estimable_due_to_treatment_variation")

    res = twfe_ols(
        df=sample,
        outcome="junior_output_share",
        rhs_terms=["treated", "log_total_output", "post_merge_bug_proxy_filled"],
    )
    coef, se, pval, cil, cih = _extract_term(res, "treated")

    # Placebo timing shift
    sample["placebo_treated"] = _placebo_shift_treated(sample, shift_weeks=8)
    placebo_coef = placebo_p = np.nan
    if sample["placebo_treated"].nunique() > 1:
        p_res = twfe_ols(
            df=sample,
            outcome="junior_output_share",
            rhs_terms=["placebo_treated", "log_total_output", "post_merge_bug_proxy_filled"],
        )
        placebo_coef = float(p_res.params.get("placebo_treated", np.nan))
        placebo_p = float(p_res.pvalues.get("placebo_treated", np.nan))

    return {
        "proxy": proxy,
        "method": "twfe",
        "coef": coef,
        "se": se,
        "pvalue": pval,
        "ci_low_95": cil,
        "ci_high_95": cih,
        "pretrend_joint_pvalue": np.nan,
        "placebo_coef": placebo_coef,
        "placebo_pvalue": placebo_p,
        "nobs": int(res.nobs),
        "n_teams": int(sample["team_id"].nunique()),
        "n_weeks": int(sample["week_index"].nunique()),
        "switchers": int(summary["switchers"]),
        "timing_dispersion_sd": float(summary["adoption_timing_dispersion_sd"]),
        "note": "baseline_twfe_clustered_team",
    }


def _linear_combo(result, terms: list[str]) -> tuple[float, float, float]:
    params = result.params
    cov = result.cov_params()
    valid = [t for t in terms if t in params.index]
    if not valid:
        return (float("nan"), float("nan"), float("nan"))

    L = np.zeros(len(params))
    idx = {name: i for i, name in enumerate(params.index)}
    for t in valid:
        L[idx[t]] = 1.0 / len(valid)

    beta = float(np.dot(L, params.values))
    var = float(np.dot(L, np.dot(cov.values, L)))
    se = math.sqrt(max(var, 0.0))
    p = float(2 * (1 - norm.cdf(abs(beta / se)))) if se > 0 else float("nan")
    return beta, se, p


def _run_event_study(
    panel: pd.DataFrame,
    proxy: str,
    summary: dict[str, Any],
    lead_max: int,
    lag_max: int,
) -> tuple[dict[str, Any], pd.DataFrame]:
    sample = panel.loc[panel["analysis_sample"] == 1].copy()
    keep = [
        "junior_output_share",
        "treated",
        "event_time",
        "log_total_output",
        "post_merge_bug_proxy_filled",
        "team_id",
        "week_index",
    ]
    sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=keep)

    if sample.empty or sample["treated"].nunique() < 2:
        return _empty_result(proxy, "event_study", summary, "not_estimable_due_to_treatment_variation"), pd.DataFrame()

    event_df, mapping = build_event_dummies(sample, lead_max=lead_max, lag_max=lag_max)
    rhs = list(mapping.keys()) + ["event_lead_far", "event_lag_far", "log_total_output", "post_merge_bug_proxy_filled"]
    res = twfe_ols(df=event_df, outcome="junior_output_share", rhs_terms=rhs)
    ci = res.conf_int()

    rows: list[dict[str, Any]] = []
    for term, k in mapping.items():
        if term not in res.params.index:
            continue
        rows.append(
            {
                "proxy": proxy,
                "term": term,
                "event_time": int(k),
                "coef": float(res.params[term]),
                "se": float(res.bse[term]),
                "pvalue": float(res.pvalues[term]),
                "ci_low_95": float(ci.loc[term, 0]),
                "ci_high_95": float(ci.loc[term, 1]),
                "n_event_team_weeks": int((event_df[term] == 1).sum()),
            }
        )

    coef_df = pd.DataFrame(rows).sort_values("event_time") if rows else pd.DataFrame()
    post_terms = [term for term, k in mapping.items() if k >= 0]
    lead_terms = [term for term, k in mapping.items() if k < -1]

    post_beta, post_se, post_p = _linear_combo(res, post_terms)
    pre_beta, _, _ = _linear_combo(res, lead_terms)
    pretrend = pretrend_pvalue(res, mapping)

    ci_low = post_beta - 1.96 * post_se if pd.notna(post_beta) and pd.notna(post_se) else np.nan
    ci_high = post_beta + 1.96 * post_se if pd.notna(post_beta) and pd.notna(post_se) else np.nan

    result_row = {
        "proxy": proxy,
        "method": "event_study",
        "coef": post_beta,
        "se": post_se,
        "pvalue": post_p,
        "ci_low_95": ci_low,
        "ci_high_95": ci_high,
        "pretrend_joint_pvalue": pretrend if pretrend is not None else np.nan,
        "placebo_coef": pre_beta,
        "placebo_pvalue": pretrend if pretrend is not None else np.nan,
        "nobs": int(res.nobs),
        "n_teams": int(sample["team_id"].nunique()),
        "n_weeks": int(sample["week_index"].nunique()),
        "switchers": int(summary["switchers"]),
        "timing_dispersion_sd": float(summary["adoption_timing_dispersion_sd"]),
        "note": "coef_is_average_post_event_time_effect; placebo_is_average_lead",
    }
    return result_row, coef_df


def _build_stacked_sample(panel: pd.DataFrame, pre_window: int, post_window: int) -> pd.DataFrame:
    base = panel.loc[panel["analysis_sample"] == 1].copy()
    keep = [
        "team_id",
        "week_index",
        "adoption_week",
        "junior_output_share",
        "log_total_output",
        "post_merge_bug_proxy_filled",
    ]
    base = base.replace([np.inf, -np.inf], np.nan).dropna(subset=keep)
    if base.empty:
        return pd.DataFrame()

    adop = base[["team_id", "adoption_week"]].drop_duplicates()
    cohorts = sorted([int(x) for x in adop["adoption_week"].dropna().unique()])

    stacks: list[pd.DataFrame] = []
    for g in cohorts:
        treated_teams = set(adop.loc[adop["adoption_week"] == g, "team_id"])
        if not treated_teams:
            continue

        control_teams = set(adop.loc[(adop["adoption_week"].isna()) | (adop["adoption_week"] > (g + post_window)), "team_id"])
        if not control_teams:
            continue

        candidates = treated_teams | control_teams
        wmin, wmax = g - pre_window, g + post_window
        s = base.loc[
            base["team_id"].isin(candidates) & (base["week_index"] >= wmin) & (base["week_index"] <= wmax)
        ].copy()
        if s.empty:
            continue

        s["rel_week"] = s["week_index"] - g

        valid_treated = []
        for t in treated_teams:
            gt = s.loc[s["team_id"] == t]
            if gt.empty:
                continue
            has_pre = bool((gt["rel_week"] < 0).any())
            has_post = bool((gt["rel_week"] >= 0).any())
            if has_pre and has_post:
                valid_treated.append(t)

        valid_treated_set = set(valid_treated)
        if not valid_treated_set:
            continue

        s = s.loc[s["team_id"].isin(valid_treated_set | control_teams)].copy()
        if s.empty:
            continue

        s["stack_id"] = int(g)
        s["cohort_treated"] = s["team_id"].isin(valid_treated_set).astype(int)
        s["did"] = (s["cohort_treated"] == 1) & (s["rel_week"] >= 0)
        s["did"] = s["did"].astype(int)
        s["stack_team"] = s["stack_id"].astype(str) + "__" + s["team_id"].astype(str)
        s["stack_rel_week"] = s["stack_id"].astype(str) + "__" + s["rel_week"].astype(int).astype(str)

        if s["did"].nunique() < 2:
            continue

        stacks.append(s)

    if not stacks:
        return pd.DataFrame()

    out = pd.concat(stacks, ignore_index=True)
    return out


def _run_stacked_did(panel: pd.DataFrame, proxy: str, summary: dict[str, Any], pre_window: int, post_window: int) -> dict[str, Any]:
    stacked = _build_stacked_sample(panel, pre_window=pre_window, post_window=post_window)
    if stacked.empty or stacked["did"].nunique() < 2:
        return _empty_result(proxy, "stacked_did", summary, "not_estimable_due_to_insufficient_stack_support")

    res = smf.ols(
        formula=(
            "junior_output_share ~ did + log_total_output + post_merge_bug_proxy_filled "
            "+ C(stack_team) + C(stack_rel_week)"
        ),
        data=stacked,
    ).fit(cov_type="cluster", cov_kwds={"groups": stacked["team_id"]})

    if "did" not in res.params.index:
        return _empty_result(proxy, "stacked_did", summary, "did_term_dropped_collinearity")

    coef, se, pval, cil, cih = _extract_term(res, "did")

    # Placebo on pre-period only
    placebo_coef = placebo_p = np.nan
    pre_only = stacked.loc[stacked["rel_week"] < 0].copy()
    if not pre_only.empty:
        pre_only["placebo"] = ((pre_only["cohort_treated"] == 1) & (pre_only["rel_week"] >= -3)).astype(int)
        if pre_only["placebo"].nunique() > 1:
            p_res = smf.ols(
                formula=(
                    "junior_output_share ~ placebo + log_total_output + post_merge_bug_proxy_filled "
                    "+ C(stack_team) + C(stack_rel_week)"
                ),
                data=pre_only,
            ).fit(cov_type="cluster", cov_kwds={"groups": pre_only["team_id"]})
            placebo_coef = float(p_res.params.get("placebo", np.nan))
            placebo_p = float(p_res.pvalues.get("placebo", np.nan))

    return {
        "proxy": proxy,
        "method": "stacked_did",
        "coef": coef,
        "se": se,
        "pvalue": pval,
        "ci_low_95": cil,
        "ci_high_95": cih,
        "pretrend_joint_pvalue": np.nan,
        "placebo_coef": placebo_coef,
        "placebo_pvalue": placebo_p,
        "nobs": int(res.nobs),
        "n_teams": int(stacked["team_id"].nunique()),
        "n_weeks": int(stacked["week_index"].nunique()),
        "switchers": int(summary["switchers"]),
        "timing_dispersion_sd": float(summary["adoption_timing_dispersion_sd"]),
        "note": (
            "stacked_by_adoption_cohort_with_not_yet_treated_and_never_controls; "
            f"stacks={int(stacked['stack_id'].nunique())}"
        ),
    }


def _build_ipw_weights(sample: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    adop = sample[["team_id", "adoption_week"]].drop_duplicates().copy()
    adop["ever_treated"] = adop["adoption_week"].notna().astype(int)

    med_adopt = float(adop["adoption_week"].dropna().median()) if adop["adoption_week"].notna().any() else float(sample["week_index"].median())

    rows = []
    for team, g in sample.groupby("team_id"):
        aw = float(g["adoption_week"].dropna().iloc[0]) if g["adoption_week"].notna().any() else np.nan
        if pd.notna(aw):
            pre = g.loc[g["week_index"] < aw].copy()
        else:
            pre = g.loc[g["week_index"] <= med_adopt].copy()
        if pre.empty:
            pre = g.copy()

        rows.append(
            {
                "team_id": team,
                "ever_treated": int(pd.notna(aw)),
                "pre_mean_outcome": float(pre["junior_output_share"].mean()),
                "pre_mean_log_output": float(pre["log_total_output"].mean()),
                "pre_mean_bug": float(pre["post_merge_bug_proxy_filled"].mean()),
                "pre_mean_ai_intensity": float(pre["ai_intensity"].mean()),
                "pre_weeks": int(pre["week_index"].nunique()),
            }
        )

    team_df = pd.DataFrame(rows)
    feature_cols = [
        "pre_mean_outcome",
        "pre_mean_log_output",
        "pre_mean_bug",
        "pre_mean_ai_intensity",
        "pre_weeks",
    ]
    for c in feature_cols:
        team_df[c] = team_df[c].replace([np.inf, -np.inf], np.nan)
        team_df[c] = team_df[c].fillna(team_df[c].median())

    if team_df["ever_treated"].nunique() < 2:
        team_df["ipw"] = 1.0
        return team_df[["team_id", "ipw"]], "ipw_fallback_no_ever_treated_variation"

    X = sm.add_constant(team_df[feature_cols], has_constant="add")
    y = team_df["ever_treated"]

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=ConvergenceWarning)
            warnings.filterwarnings("error", category=RuntimeWarning)
            logit = sm.Logit(y, X).fit(disp=False)
        if hasattr(logit, "mle_retvals") and not bool(logit.mle_retvals.get("converged", True)):
            raise RuntimeError("logit_not_converged")
        ps = pd.Series(logit.predict(X), index=team_df.index)
        method_note = "ipw_logit"
    except Exception:
        # Closest valid fallback in small samples: regularized binomial GLM.
        glm = sm.GLM(y, X, family=sm.families.Binomial())
        fit = glm.fit_regularized(alpha=1e-6, L1_wt=0.0, maxiter=200)
        ps = pd.Series(fit.predict(X), index=team_df.index)
        method_note = "ipw_glm_regularized_fallback"

    ps = ps.clip(0.05, 0.95)
    team_df["ipw"] = np.where(team_df["ever_treated"] == 1, 1.0 / ps, 1.0 / (1.0 - ps))

    # Winsorize extreme weights for stability.
    hi = float(team_df["ipw"].quantile(0.99))
    team_df["ipw"] = team_df["ipw"].clip(lower=0.1, upper=hi)

    return team_df[["team_id", "ipw"]], method_note


def _run_reweighted_twfe(panel: pd.DataFrame, proxy: str, summary: dict[str, Any]) -> dict[str, Any]:
    sample = panel.loc[panel["analysis_sample"] == 1].copy()
    keep = [
        "junior_output_share",
        "treated",
        "log_total_output",
        "post_merge_bug_proxy_filled",
        "ai_intensity",
        "team_id",
        "week_index",
    ]
    sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=keep)

    if sample.empty or sample["treated"].nunique() < 2:
        return _empty_result(proxy, "reweighted_did", summary, "not_estimable_due_to_treatment_variation")

    wdf, w_note = _build_ipw_weights(sample)
    sample = sample.merge(wdf, on="team_id", how="left")
    sample["ipw"] = sample["ipw"].fillna(1.0)

    res = smf.wls(
        formula=(
            "junior_output_share ~ treated + log_total_output + post_merge_bug_proxy_filled + "
            "C(team_id) + C(week_index)"
        ),
        data=sample,
        weights=sample["ipw"],
    ).fit(cov_type="cluster", cov_kwds={"groups": sample["team_id"]})

    if "treated" not in res.params.index:
        return _empty_result(proxy, "reweighted_did", summary, "treated_term_dropped_collinearity")

    coef, se, pval, cil, cih = _extract_term(res, "treated")

    placebo_coef = placebo_p = np.nan
    sample["placebo_treated"] = _placebo_shift_treated(sample, shift_weeks=8)
    if sample["placebo_treated"].nunique() > 1:
        p_res = smf.wls(
            formula=(
                "junior_output_share ~ placebo_treated + log_total_output + post_merge_bug_proxy_filled + "
                "C(team_id) + C(week_index)"
            ),
            data=sample,
            weights=sample["ipw"],
        ).fit(cov_type="cluster", cov_kwds={"groups": sample["team_id"]})
        placebo_coef = float(p_res.params.get("placebo_treated", np.nan))
        placebo_p = float(p_res.pvalues.get("placebo_treated", np.nan))

    return {
        "proxy": proxy,
        "method": "reweighted_did",
        "coef": coef,
        "se": se,
        "pvalue": pval,
        "ci_low_95": cil,
        "ci_high_95": cih,
        "pretrend_joint_pvalue": np.nan,
        "placebo_coef": placebo_coef,
        "placebo_pvalue": placebo_p,
        "nobs": int(res.nobs),
        "n_teams": int(sample["team_id"].nunique()),
        "n_weeks": int(sample["week_index"].nunique()),
        "switchers": int(summary["switchers"]),
        "timing_dispersion_sd": float(summary["adoption_timing_dispersion_sd"]),
        "note": f"{w_note}; proxy_for_matched_did_via_team_level_ipw",
    }


def _defensibility_ranking(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame(columns=["rank", "proxy", "score", "justification"])

    clean = results.copy()

    ranking_rows: list[dict[str, Any]] = []
    for proxy, g in clean.groupby("proxy"):
        g_est = g.loc[g["coef"].notna()].copy()
        if g_est.empty:
            ranking_rows.append(
                {"proxy": proxy, "score": -999.0, "justification": "No estimable methods under this proxy."}
            )
            continue

        signs = np.sign(g_est["coef"].replace(0, np.nan).dropna())
        sign_consistency = float(signs.value_counts(normalize=True).max()) if not signs.empty else 0.0

        pretrend_vals = g.loc[g["method"] == "event_study", "pretrend_joint_pvalue"].dropna()
        pretrend_pass = bool((pretrend_vals > 0.10).any())

        placebo_vals = g["placebo_pvalue"].dropna()
        placebo_pass_share = float((placebo_vals > 0.10).mean()) if not placebo_vals.empty else 0.0

        has_stack = bool((g["method"] == "stacked_did").any() and (g.loc[g["method"] == "stacked_did", "coef"].notna().any()))
        has_reweighted = bool((g["method"] == "reweighted_did").any() and (g.loc[g["method"] == "reweighted_did", "coef"].notna().any()))

        switchers = float(g["switchers"].max()) if g["switchers"].notna().any() else 0.0
        timing_disp = float(g["timing_dispersion_sd"].max()) if g["timing_dispersion_sd"].notna().any() else float("nan")

        treated_share = float(g["treated_share"].dropna().iloc[0]) if g["treated_share"].notna().any() else float("nan")

        measurement_prior = {"strict": 1.5, "balanced": 2.0, "broad": -1.0}.get(proxy, 0.5)
        extreme_treated_penalty = -1.0 if (pd.notna(treated_share) and (treated_share > 0.60 or treated_share < 0.15)) else 0.0

        score = measurement_prior
        score += 1.0 if sign_consistency >= 0.75 else 0.0
        score += 1.0 if pretrend_pass else 0.0
        score += 1.0 if placebo_pass_share >= 0.67 else 0.0
        score += 1.0 if has_stack else 0.0
        score += 1.0 if has_reweighted else 0.0
        score += 1.0 if switchers >= 5 else 0.0
        score += 1.0 if (pd.notna(timing_disp) and timing_disp >= 4.0) else 0.0
        score += extreme_treated_penalty

        justification = (
            f"measurement_prior={measurement_prior:.1f}; sign_consistency={sign_consistency:.2f}; "
            f"pretrend_pass={pretrend_pass}; placebo_pass_share={placebo_pass_share:.2f}; "
            f"switchers={int(switchers)}; treated_share={treated_share:.2f}; "
            f"stacked_estimable={has_stack}; reweighted_estimable={has_reweighted}"
        )

        ranking_rows.append({"proxy": proxy, "score": score, "justification": justification})

    ranking = pd.DataFrame(ranking_rows).sort_values(["score", "proxy"], ascending=[False, True]).reset_index(drop=True)
    ranking["rank"] = np.arange(1, len(ranking) + 1)
    return ranking[["rank", "proxy", "score", "justification"]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v3 long-horizon multi-proxy identification sweep")
    parser.add_argument("--input", default="data/raw/real_proxy/repo_week_panel_v3_long_h18.csv")
    parser.add_argument("--input-meta", default="data/raw/real_proxy/repo_week_panel_v3_long_h18_metadata.json")
    parser.add_argument("--out-methods", default="outputs/tables/table_v3_identification_sweep_results.csv")
    parser.add_argument("--out-event", default="outputs/tables/table_v3_event_study_coefficients.csv")
    parser.add_argument("--out-proxies", default="outputs/tables/table_v3_proxy_definitions.csv")
    parser.add_argument("--out-horizon", default="outputs/tables/table_v3_horizon_data_expansion.csv")
    parser.add_argument("--out-ranking", default="outputs/tables/table_v3_defensibility_ranking.csv")
    parser.add_argument("--out-summary-json", default="outputs/tables/table_v3_identification_summary.json")
    parser.add_argument("--compare-input", default="data/raw/real_proxy/repo_week_panel_q2_2025_more_data.csv")
    parser.add_argument("--compare-meta", default="data/raw/real_proxy/repo_week_panel_q2_2025_more_data_metadata.json")
    parser.add_argument("--lead-max", type=int, default=6)
    parser.add_argument("--lag-max", type=int, default=8)
    parser.add_argument("--stack-pre", type=int, default=6)
    parser.add_argument("--stack-post", type=int, default=8)
    parser.add_argument("--min-total-output", type=int, default=1)
    args = parser.parse_args()

    input_path = ROOT / args.input
    meta_path = ROOT / args.input_meta
    compare_input_path = ROOT / args.compare_input
    compare_meta_path = ROOT / args.compare_meta

    if not input_path.exists():
        raise FileNotFoundError(f"Input panel not found: {input_path}")

    raw = pd.read_csv(input_path)
    raw["calendar_week"] = pd.to_datetime(raw["calendar_week"]).dt.date

    out_methods = ROOT / args.out_methods
    out_event = ROOT / args.out_event
    out_proxies = ROOT / args.out_proxies
    out_horizon = ROOT / args.out_horizon
    out_ranking = ROOT / args.out_ranking
    out_summary_json = ROOT / args.out_summary_json

    for p in [out_methods, out_event, out_proxies, out_horizon, out_ranking, out_summary_json]:
        p.parent.mkdir(parents=True, exist_ok=True)

    # Horizon/provenance diagnostics
    horizon_rows: list[dict[str, Any]] = []
    meta: dict[str, Any] = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

    start_date = str(min(raw["calendar_week"])) if not raw.empty else None
    end_date = str(max(raw["calendar_week"])) if not raw.empty else None
    weeks_total = int(raw["week_index"].nunique()) if "week_index" in raw.columns else int(raw["calendar_week"].nunique())

    horizon_rows.extend(
        [
            {"metric": "panel_start_date", "value": start_date},
            {"metric": "panel_end_date", "value": end_date},
            {"metric": "panel_weeks", "value": weeks_total},
            {"metric": "panel_months_approx", "value": round(weeks_total / 4.345, 2)},
            {"metric": "panel_rows", "value": int(raw.shape[0])},
            {"metric": "panel_teams", "value": int(raw["team_id"].nunique())},
        ]
    )

    fetch_stats = meta.get("fetch_stats", {}) if isinstance(meta, dict) else {}
    for key in ["hours_requested", "hours_successful", "hours_failed", "events_scanned", "events_repo_matched"]:
        if key in fetch_stats:
            horizon_rows.append({"metric": f"fetch_{key}", "value": fetch_stats[key]})

    if compare_input_path.exists():
        old = pd.read_csv(compare_input_path)
        old["calendar_week"] = pd.to_datetime(old["calendar_week"]).dt.date
        old_weeks = int(old["week_index"].nunique()) if "week_index" in old.columns else int(old["calendar_week"].nunique())
        old_rows = int(old.shape[0])
        old_teams = int(old["team_id"].nunique())

        horizon_rows.extend(
            [
                {"metric": "compare_old_panel_weeks", "value": old_weeks},
                {"metric": "compare_old_panel_rows", "value": old_rows},
                {"metric": "compare_old_panel_teams", "value": old_teams},
                {"metric": "delta_weeks_new_minus_old", "value": weeks_total - old_weeks},
                {"metric": "delta_rows_new_minus_old", "value": int(raw.shape[0]) - old_rows},
                {"metric": "delta_months_new_minus_old_approx", "value": round((weeks_total - old_weeks) / 4.345, 2)},
            ]
        )

        if compare_meta_path.exists():
            old_meta = json.loads(compare_meta_path.read_text(encoding="utf-8"))
            old_fetch = old_meta.get("fetch_stats", {}) if isinstance(old_meta, dict) else {}
            for key in ["hours_requested", "hours_successful", "hours_failed", "events_scanned", "events_repo_matched"]:
                if key in old_fetch and key in fetch_stats:
                    horizon_rows.append(
                        {
                            "metric": f"delta_fetch_{key}_new_minus_old",
                            "value": fetch_stats[key] - old_fetch[key],
                        }
                    )

    pd.DataFrame(horizon_rows).to_csv(out_horizon, index=False)

    # Proxy definitions table
    proxy_def_rows = []
    for spec in PROXY_SPECS:
        proxy_def_rows.append(
            {
                "proxy": spec.name,
                "ai_intensity_threshold": spec.ai_intensity_threshold,
                "ai_min_signal_events": spec.ai_min_signal_events,
                "ai_min_eligible_events": spec.ai_min_eligible_events,
                "rationale": spec.rationale,
            }
        )
    pd.DataFrame(proxy_def_rows).to_csv(out_proxies, index=False)

    method_rows: list[dict[str, Any]] = []
    event_rows: list[pd.DataFrame] = []
    proxy_summary_rows: list[dict[str, Any]] = []

    for spec in PROXY_SPECS:
        panel = _build_proxy_panel(raw=raw, spec=spec, min_total_output_for_sample=args.min_total_output)
        summary = _panel_summary(panel)
        proxy_summary_rows.append({"proxy": spec.name, **summary})

        method_rows.append(_run_twfe(panel=panel, proxy=spec.name, summary=summary))

        event_row, event_df = _run_event_study(
            panel=panel,
            proxy=spec.name,
            summary=summary,
            lead_max=args.lead_max,
            lag_max=args.lag_max,
        )
        method_rows.append(event_row)
        if not event_df.empty:
            event_rows.append(event_df)

        method_rows.append(
            _run_stacked_did(
                panel=panel,
                proxy=spec.name,
                summary=summary,
                pre_window=args.stack_pre,
                post_window=args.stack_post,
            )
        )

        method_rows.append(_run_reweighted_twfe(panel=panel, proxy=spec.name, summary=summary))

    methods_df = pd.DataFrame(method_rows)

    # Merge panel support metrics for explicit comparison in one table.
    proxy_summary_df = pd.DataFrame(proxy_summary_rows)
    methods_df = methods_df.merge(proxy_summary_df, on="proxy", how="left", suffixes=("", "_proxy"))
    methods_df.to_csv(out_methods, index=False)

    if event_rows:
        pd.concat(event_rows, ignore_index=True).to_csv(out_event, index=False)
    else:
        pd.DataFrame(
            columns=[
                "proxy",
                "term",
                "event_time",
                "coef",
                "se",
                "pvalue",
                "ci_low_95",
                "ci_high_95",
                "n_event_team_weeks",
            ]
        ).to_csv(out_event, index=False)

    ranking = _defensibility_ranking(methods_df)
    ranking.to_csv(out_ranking, index=False)

    summary_payload = {
        "horizon": {
            "start_date": start_date,
            "end_date": end_date,
            "weeks": weeks_total,
            "months_approx": round(weeks_total / 4.345, 2),
            "rows": int(raw.shape[0]),
            "teams": int(raw["team_id"].nunique()),
            "fetch_stats": fetch_stats,
        },
        "proxy_definitions": proxy_def_rows,
        "proxy_support": proxy_summary_rows,
        "method_results": methods_df.to_dict(orient="records"),
        "defensibility_ranking": ranking.to_dict(orient="records"),
        "notes": [
            "All estimates are associational proxy-based DiD diagnostics on observed public data.",
            "Matched DiD implemented as team-level propensity reweighted TWFE (closest valid alternative with available data).",
        ],
    }
    write_json(out_summary_json, summary_payload)

    print(f"Wrote {out_horizon}")
    print(f"Wrote {out_proxies}")
    print(f"Wrote {out_methods}")
    print(f"Wrote {out_event}")
    print(f"Wrote {out_ranking}")
    print(f"Wrote {out_summary_json}")


if __name__ == "__main__":
    main()
