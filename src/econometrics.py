from __future__ import annotations

from dataclasses import dataclass
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.tools.sm_exceptions import ValueWarning

warnings.filterwarnings("ignore", category=ValueWarning, message=r"covariance of constraints does not have full rank.*")


@dataclass
class RegressionRow:
    model: str
    outcome: str
    term: str
    coef: float
    se: float
    tstat: float
    pvalue: float
    ci_low_95: float
    ci_high_95: float
    nobs: int
    n_teams: int
    n_weeks: int
    r2: float


def twfe_ols(
    df: pd.DataFrame,
    outcome: str,
    rhs_terms: list[str],
    cluster_col: str = "team_id",
):
    rhs = " + ".join(rhs_terms + ["C(team_id)", "C(week_index)"])
    formula = f"{outcome} ~ {rhs}"
    model = smf.ols(formula=formula, data=df)
    result = model.fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})
    return result


def extract_terms(result, model_name: str, outcome: str, terms: list[str], df: pd.DataFrame) -> list[RegressionRow]:
    rows: list[RegressionRow] = []
    ci = result.conf_int()
    for term in terms:
        if term not in result.params.index:
            continue
        rows.append(
            RegressionRow(
                model=model_name,
                outcome=outcome,
                term=term,
                coef=float(result.params[term]),
                se=float(result.bse[term]),
                tstat=float(result.tvalues[term]),
                pvalue=float(result.pvalues[term]),
                ci_low_95=float(ci.loc[term, 0]),
                ci_high_95=float(ci.loc[term, 1]),
                nobs=int(result.nobs),
                n_teams=int(df["team_id"].nunique()),
                n_weeks=int(df["week_index"].nunique()),
                r2=float(result.rsquared),
            )
        )
    return rows


def build_event_dummies(df: pd.DataFrame, lead_max: int, lag_max: int) -> tuple[pd.DataFrame, dict[str, int]]:
    out = df.copy()
    mapping: dict[str, int] = {}
    for k in range(-lead_max, lag_max + 1):
        if k == -1:
            continue
        name = f"event_{k:+d}".replace("+", "p").replace("-", "m")
        out[name] = (out["event_time"] == k).astype(int)
        mapping[name] = k
    out["event_lead_far"] = (out["event_time"] <= -(lead_max + 1)).fillna(False).astype(int)
    out["event_lag_far"] = (out["event_time"] >= (lag_max + 1)).fillna(False).astype(int)
    return out, mapping


def pretrend_pvalue(result, mapping: dict[str, int]) -> float | None:
    lead_terms = [term for term, k in mapping.items() if k < -1 and term in result.params.index]
    if not lead_terms:
        return None
    hyp = ", ".join(f"{term}=0" for term in lead_terms)
    wt = result.wald_test(hyp, scalar=True)
    return float(wt.pvalue)


def safe_share(numer: pd.Series, denom: pd.Series) -> pd.Series:
    out = pd.Series(np.nan, index=numer.index, dtype=float)
    mask = denom > 0
    out.loc[mask] = numer.loc[mask] / denom.loc[mask]
    return out
