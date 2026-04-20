"""
Smart Resource Allocation Dashboard — Streamlit entry point.

Core allocation rules live in allocation.py; sample regions live in data.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import streamlit as st

import allocation as alloc
from data import SAMPLE_REGIONS


def _default_budget() -> float:
    return 120_000_000.0


def _coerce_budget(raw: object, *, lo: float, hi: float) -> float:
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return _default_budget()
    if np.isnan(v):
        return _default_budget()
    return float(min(hi, max(lo, v)))


def _inject_styles() -> None:
    """Professional but lightweight styling for readability."""
    st.markdown(
        """
        <style>
        div.block-container { padding-top: 0.95rem; padding-bottom: 1.65rem; }
        h1 {
            font-size: clamp(1.65rem, 2.1vw, 2rem) !important;
            letter-spacing: -0.005em;
            font-weight: 600;
            margin-bottom: 0.2rem;
            line-height: 1.2;
        }
        h3 { margin-top: 0.35rem; margin-bottom: 0.45rem; }
        .app-purpose { font-size: 0.95rem; line-height: 1.4; margin-bottom: 0.25rem; }
        .designer-attribution {
            font-size: 0.85rem;
            opacity: 0.85;
            margin-top: 1.7rem;
            padding-top: 0.85rem;
            border-top: 1px solid rgba(128,128,128,0.35);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _assign_priority_band(result: pd.DataFrame) -> pd.Series:
    """Assign Low/Medium/High priority bands from need_score tertiles."""
    scores = pd.to_numeric(result["need_score"], errors="coerce").fillna(0.0)
    if len(scores) >= 3 and scores.nunique() >= 3:
        q1, q2 = scores.quantile([1 / 3, 2 / 3])
        labels = np.where(scores <= q1, "Low", np.where(scores <= q2, "Medium", "High"))
        return pd.Series(labels, index=result.index)
    return pd.Series(["Medium"] * len(result), index=result.index)


def _ministerial_brief(result: pd.DataFrame, budget: float) -> tuple[str, str, str]:
    """Return executive brief in Risk / Implication / Action now format."""
    high = result[result["priority_band"] == "High"]
    high_share = float(high["share_of_budget"].sum()) if len(high) else 0.0
    high_count = int(len(high))
    top_two_share = float(result["share_of_budget"].head(2).sum()) if len(result) else 0.0
    mean_poverty_top3 = float(result["poverty_rate"].head(3).mean() * 100) if len(result) else 0.0
    top_region = str(result.iloc[0]["region"]) if len(result) else "N/A"
    top_share = float(result.iloc[0]["share_of_budget"]) if len(result) else 0.0

    risk = (
        f"Budget concentration risk is elevated: {high_share:.1f}% of the {budget / 1_000_000:,.0f}M envelope "
        f"flows to {high_count} high-priority region(s), and the top two regions absorb {top_two_share:.1f}%."
    )
    implication = (
        f"The allocation is strongly targeted, which improves focus but raises delivery dependency on a small set of regions. "
        f"{top_region} alone receives {top_share:.1f}%, while top-3 average poverty remains {mean_poverty_top3:.1f}%."
    )

    if high_share >= 50:
        action_now = (
            "Protect service continuity in high-priority regions immediately, assign monthly execution reviews for the top two regions, "
            "and reserve a rapid-response buffer for underperforming programs."
        )
    else:
        action_now = (
            "Validate whether high-priority regions are receiving enough depth, tighten implementation tracking in top-funded areas, "
            "and link disbursements to measurable poverty-reduction milestones."
        )

    return risk, implication, action_now


def _focus_region_text(result: pd.DataFrame, region_name: str) -> tuple[str, str]:
    """Return concise 'why' and 'action' text for the selected region."""
    match = result.loc[result["region"].astype(str) == str(region_name)]
    row = match.iloc[0] if len(match) else result.iloc[0]
    region = str(row["region"])

    med_need = float(result["need_score"].median())
    med_poverty = float(result["poverty_rate"].median())
    med_share = float(result["share_of_budget"].median())

    why_parts: list[str] = []
    why_parts.append(
        "need level is above the regional midpoint"
        if float(row["need_score"]) >= med_need
        else "need level is below the regional midpoint"
    )
    why_parts.append(
        "poverty pressure is above the regional midpoint"
        if float(row["poverty_rate"]) >= med_poverty
        else "poverty pressure is below the regional midpoint"
    )
    why_parts.append(
        "its budget share is above the midpoint"
        if float(row["share_of_budget"]) >= med_share
        else "its budget share is below the midpoint"
    )
    why = f"For {region}: " + "; ".join(why_parts) + "."

    band = str(row.get("priority_band", "Medium"))
    if band == "High":
        action = (
            f"For {region}, prioritize immediate service continuity, strengthen delivery capacity, "
            "and monitor monthly execution risks."
        )
    elif band == "Medium":
        action = (
            f"For {region}, protect core services and target bottlenecks early so pressure does not escalate."
        )
    else:
        action = (
            f"For {region}, maintain baseline support and monitor indicators for early signs of deterioration."
        )
    return why, action


def main() -> None:
    st.set_page_config(
        page_title="Smart Resource Allocation Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_styles()

    budget_lo = 0.0
    budget_hi = 500_000_000.0
    if "budget_value" not in st.session_state:
        st.session_state.budget_value = _default_budget()
    st.session_state.budget_value = _coerce_budget(
        st.session_state.budget_value, lo=budget_lo, hi=budget_hi
    )

    # --- Header ---
    st.title("Smart Resource Allocation Dashboard")
    st.markdown(
        '<p class="app-purpose"><strong>Challenge / problem statement:</strong> '
        "Public leaders must distribute a limited budget across regions with unequal need, while balancing fairness, "
        "impact, and delivery risk under resource constraints."
        "</p>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Executive-style view · Illustrative sample regions · Budget split by need score"
    )
    st.info(
        "**Scope note:** numbers below are **illustrative** sample rows, not census or treasury figures. "
        "Pair any real decision with official statistics, law, and cabinet process."
    )

    # --- Sidebar input ---
    st.sidebar.markdown("### Budget input")
    budget_m = st.sidebar.slider(
        "Total budget to allocate (millions)",
        min_value=0.0,
        max_value=float(budget_hi / 1_000_000),
        value=float(st.session_state.budget_value / 1_000_000),
        step=5.0,
        help="Move the slider to change the total envelope. Value is in millions of currency units.",
    )
    budget = float(budget_m * 1_000_000)
    st.session_state.budget_value = budget

    region_options = [str(r.get("region", "")) for r in SAMPLE_REGIONS if str(r.get("region", ""))]
    selected_region = st.sidebar.selectbox(
        "Region to highlight",
        options=region_options,
        index=0,
        help="Changes the focus brief in the main panel.",
    )

    st.sidebar.divider()
    with st.sidebar.expander("Sample region data", expanded=False):
        st.caption("Each region has need_score, population, and poverty_rate (illustrative).")
        st.dataframe(
            pd.DataFrame(SAMPLE_REGIONS),
            use_container_width=True,
            hide_index=True,
        )

    st.sidebar.markdown(
        '<p class="designer-attribution">Designed by: Sherriff Abdul-Hamid</p>',
        unsafe_allow_html=True,
    )

    # --- Core table + chart (errors surfaced clearly) ---
    try:
        result = alloc.allocate_budget(budget, SAMPLE_REGIONS)
        result = alloc.priority_ranking(result)
    except ValueError as err:
        st.error(str(err))
        st.stop()
    except Exception:
        st.error("Could not compute allocations. Please reload the page or contact support.")
        st.stop()

    # Add priority band for cleaner executive interpretation.
    result["priority_band"] = _assign_priority_band(result)
    result["priority_area"] = result["priority_band"].map(
        {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}
    )

    # --- Key indicators ---
    st.subheader("Key indicators")
    total_pop = int(result["population"].sum())
    top_region = str(result.iloc[0]["region"])
    top_share = float(result.iloc[0]["share_of_budget"])
    top_band = str(result.iloc[0]["priority_band"])
    high_count = int((result["priority_band"] == "High").sum())
    high_share = float(result.loc[result["priority_band"] == "High", "share_of_budget"].sum())

    kpi = st.container(border=True)
    with kpi:
        k1, k2, k3, k4 = st.columns(4, gap="medium")
        with k1:
            st.metric(
                label="Budget envelope",
                value=f"{budget / 1_000_000:,.0f} M",
                help="Total budget you set on the slider (millions of currency units).",
            )
        with k2:
            st.metric(
                label="High-priority regions",
                value=high_count,
                help="Regions in the top priority band under this budget run.",
            )
        with k3:
            st.metric(
                label="Budget share to high-priority regions",
                value=f"{high_share:.1f}%",
                help="Total budget directed to high-priority regions in this run.",
            )
        with k4:
            st.metric(
                label="Top need region",
                value=top_region[:18] + ("…" if len(top_region) > 18 else ""),
                help="Region with the highest need score in the sample.",
            )
    st.caption(
        f"Current highest-priority band in this run: **{top_band}** · "
        f"Top region share: **{top_share:.1f}%** · Population covered (sample): **{total_pop / 1_000_000:.2f} M**"
    )

    st.subheader("Focus region brief")
    fcol1, fcol2 = st.columns((1, 1), gap="large")
    focus_why, focus_action = _focus_region_text(result, selected_region)
    with fcol1:
        st.markdown(f"#### Why **{selected_region}** is positioned this way")
        st.write(focus_why)
    with fcol2:
        st.markdown("#### Recommendation for this region")
        st.write(focus_action)

    st.subheader("Ministerial brief")
    st.caption("Decision summary in three parts: risk, implication, and immediate action.")
    risk_text, implication_text, action_now_text = _ministerial_brief(result, budget)
    policy_box = st.container(border=True)
    with policy_box:
        b1, b2, b3 = st.columns((1, 1, 1), gap="medium")
        with b1:
            st.markdown("#### Risk")
            st.write(risk_text)
        with b2:
            st.markdown("#### Implication")
            st.write(implication_text)
        with b3:
            st.markdown("#### Action now")
            st.write(action_now_text)

    st.subheader("Allocation and ranking")
    st.caption(
        "Allocations follow **need_score / sum(need_score)**. When every need score is zero, "
        "the model falls back to **equal** shares (last-resort rule)."
    )

    body = st.container(border=True)
    with body:
        left, right = st.columns((1, 1), gap="large")
        with left:
            st.markdown("#### Allocation table")
            display_cols = [
                "priority_rank",
                "region",
                "priority_area",
                "need_score",
                "population",
                "poverty_rate",
                "allocation",
                "share_of_budget",
            ]
            view = result[display_cols].copy()
            view["poverty_rate"] = (view["poverty_rate"] * 100).round(1)
            view = view.rename(
                columns={
                    "priority_rank": "Rank",
                    "region": "Region",
                    "priority_area": "Priority area",
                    "need_score": "Need score",
                    "population": "Population",
                    "poverty_rate": "Poverty rate (%)",
                    "allocation": "Allocation",
                    "share_of_budget": "Share (%)",
                }
            )
            st.dataframe(
                view,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Allocation": st.column_config.NumberColumn(format="%.0f"),
                    "Population": st.column_config.NumberColumn(format="%d"),
                    "Need score": st.column_config.NumberColumn(format="%.0f"),
                    "Share (%)": st.column_config.NumberColumn(format="%.1f"),
                    "Poverty rate (%)": st.column_config.NumberColumn(format="%.1f"),
                },
            )
        with right:
            st.markdown("#### Allocation by region")
            chart_df = result.set_index("region")[["allocation"]].sort_values(
                "allocation", ascending=True
            )
            st.bar_chart(chart_df, height=360)

    st.subheader("Regional recommendation notes")
    rec_box = st.container(border=True)
    with rec_box:
        for line in alloc.recommendation_lines(result, top_n=3):
            st.markdown(f"- {line}")

    with st.expander("Model note (technical)", expanded=False):
        st.markdown(
            """
Each region receives **budget × (need_score / sum(need_scores))**. Poverty rate and population
are shown for context but **do not** enter the split in this version. See `allocation.py` to change the rule.
            """.strip()
        )


if __name__ == "__main__":
    main()
