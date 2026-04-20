"""
Policy recommendations, plain-language explanations, and auto-generated briefs.
"""

from __future__ import annotations

import pandas as pd

from modeling import compute_risk_score


def recommendation_for_tier(tier: str) -> str:
    """One-line actionable recommendation by risk tier."""
    t = tier.strip().title()
    if t == "High":
        return "Expand Medicaid, increase subsidies, invest in rural clinics."
    if t == "Medium":
        return "Improve insurance coverage and affordability."
    return "Maintain and monitor access."


def focus_recommendation_row(row: pd.Series) -> str:
    """
    Build a more human-like recommendation for one highlighted state.

    The message updates whenever the selected state changes and blends
    broad tier guidance with state-specific context.
    """
    state = str(row.get("state", "This state"))
    tier = str(row.get("predicted_risk_tier", "Medium")).title()

    uninsured = float(row.get("uninsured_rate", 0.0))
    cost = float(row.get("healthcare_cost_index", 0.0))
    rural = float(row.get("rural_population", 0.0))
    income = float(row.get("median_income", 0.0))

    med_uninsured = float(row.get("_panel_median_uninsured", uninsured))
    med_cost = float(row.get("_panel_median_cost", cost))
    med_rural = float(row.get("_panel_median_rural", rural))
    med_income = float(row.get("_panel_median_income", income))

    pressures: list[str] = []
    if uninsured >= med_uninsured:
        pressures.append("insurance gaps are above the middle of this group")
    if cost >= med_cost:
        pressures.append("care costs are running higher than most peers")
    if rural >= med_rural:
        pressures.append("rural access challenges are likely to be more visible")
    if income <= med_income:
        pressures.append("household income is below the group midpoint")

    if not pressures:
        pressures.append("current access signals are relatively stable")

    if tier == "High":
        action = (
            "Recommended next steps are immediate coverage expansion, stronger subsidy reach, "
            "and near-term funding for rural clinics and transport support."
        )
    elif tier == "Medium":
        action = (
            "Recommended next steps are to improve affordability first, strengthen enrollment support, "
            "and close service gaps before they become high-risk."
        )
    else:
        action = (
            "Recommended next steps are to keep current programs in place, continue routine monitoring, "
            "and prepare contingency support if affordability or coverage starts to weaken."
        )

    return (
        f"For {state}, the current {tier.lower()}-priority rating suggests that "
        + ", ".join(pressures[:3])
        + ". "
        + action
    )


def policy_insight_row(row: pd.Series) -> str:
    """
    Short plain-English explanation of *why* modeled risk is elevated or subdued
    for a single state, based on feature values vs panel medians.
    """
    state = str(row.get("state", "This state"))
    parts: list[str] = []
    med_income = float(row["median_income"])
    unins = float(row["uninsured_rate"])
    cost = float(row["healthcare_cost_index"])
    rural = float(row["rural_population"])

    if unins >= float(row.get("_panel_median_uninsured", unins)):
        parts.append("the share without insurance is higher than the typical state in this view")
    else:
        parts.append("the share without insurance is lower than the typical state in this view")

    if cost >= float(row.get("_panel_median_cost", cost)):
        parts.append("relative care costs are higher than the typical state in this view")
    else:
        parts.append("relative care costs are moderate compared with the typical state in this view")

    if med_income <= float(row.get("_panel_median_income", med_income)):
        parts.append("typical income is below the middle of this group")
    else:
        parts.append("typical income is above the middle of this group")

    if rural >= float(row.get("_panel_median_rural", rural)):
        parts.append("the rural share is on the high side, which can strain clinics and travel")
    else:
        parts.append("the rural share is lower than for many states here")

    # Use all four signals so wording differs more often between states.
    return (
        f"For {state}: "
        + "; ".join(parts)
        + ". Together these shape this state’s access risk score."
    )


def attach_panel_medians(df: pd.DataFrame) -> pd.DataFrame:
    """Add median columns for insight comparisons (prefixed to avoid collisions)."""
    out = df.copy()
    out["_panel_median_income"] = out["median_income"].median()
    out["_panel_median_uninsured"] = out["uninsured_rate"].median()
    out["_panel_median_cost"] = out["healthcare_cost_index"].median()
    out["_panel_median_rural"] = out["rural_population"].median()
    return out


def policy_brief(df: pd.DataFrame, predictions: pd.Series) -> str:
    """
    Auto-generate a 3–4 sentence policy brief from aggregate panel statistics.
    """
    n = len(df)
    high_share = (predictions == "High").mean()
    med_share = (predictions == "Medium").mean()
    low_share = (predictions == "Low").mean()
    risk = compute_risk_score(df)
    top = df.loc[risk.idxmax(), "state"] if len(df) else "N/A"
    mean_risk = float(risk.mean())

    s1 = (
        f"In this view, {n} states are scored for access pressure. "
        f"About {high_share:.0%} land in the high band, {med_share:.0%} in medium, and {low_share:.0%} in low."
    )
    s2 = (
        f"The average score is {mean_risk:.1f} on a 0–100 scale (higher means more pressure). "
        f"{top} shows the highest score in this run."
    )
    s3 = (
        "States in the high band are good candidates for stronger coverage help, subsidies people can actually use, "
        "and extra support for rural clinics and transport."
    )
    s4 = (
        "Treat these results as a starting view—pair them with local enrollment, hospital, and budget facts before large commitments."
    )
    return " ".join([s1, s2, s3, s4])
