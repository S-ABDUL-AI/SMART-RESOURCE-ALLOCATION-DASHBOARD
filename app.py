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


def main() -> None:
    st.set_page_config(
        page_title="Smart Resource Allocation Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    budget_lo = 0.0
    budget_hi = 500_000_000.0
    if "budget_value" not in st.session_state:
        st.session_state.budget_value = _default_budget()
    st.session_state.budget_value = _coerce_budget(
        st.session_state.budget_value, lo=budget_lo, hi=budget_hi
    )

    # --- Header ---
    st.title("Smart Resource Allocation Dashboard")
    st.caption("Executive-style view · Illustrative sample regions · Budget split by need score")

    hero = st.container()
    with hero:
        h_left, h_right = st.columns((3, 1), gap="large")
        with h_left:
            st.markdown(
                """
**One-line read:** set a total budget, then see how it would flow to each region if shares
follow **need scores only** in this toy model. Use it to open a conversation, not to replace
official allocation rules or data systems.
                """.strip()
            )
        with h_right:
            st.metric(
                label="Sample regions loaded",
                value=len(SAMPLE_REGIONS),
                help="Fixed illustrative dataset. Swap in your own table for a real process.",
            )

    st.markdown("")

    st.markdown(
        """
### Policy Purpose

This tool helps policymakers make data-driven decisions to reduce poverty and improve economic outcomes.
        """.strip()
    )
    st.info(
        "**Scope note:** numbers below are **illustrative** sample rows, not census or treasury figures. "
        "Pair any real decision with official statistics, law, and cabinet process."
    )

    st.markdown("")

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

    st.sidebar.divider()
    with st.sidebar.expander("Sample region data", expanded=False):
        st.caption("Each region has need_score, population, and poverty_rate (illustrative).")
        st.dataframe(
            pd.DataFrame(SAMPLE_REGIONS),
            use_container_width=True,
            hide_index=True,
        )

    st.sidebar.divider()
    st.sidebar.markdown("**Designed by:** Sherriff Abdul-Hamid")

    # --- Core table + chart (errors surfaced clearly) ---
    st.subheader("Key indicators")
    try:
        result = alloc.allocate_budget(budget, SAMPLE_REGIONS)
        result = alloc.priority_ranking(result)
    except ValueError as err:
        st.error(str(err))
        st.stop()
    except Exception:
        st.error("Could not compute allocations. Please reload the page or contact support.")
        st.stop()

    total_pop = int(result["population"].sum())
    top_share = float(result.iloc[0]["share_of_budget"])
    top_region = str(result.iloc[0]["region"])

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
                label="Population (sample)",
                value=f"{total_pop / 1_000_000:.2f} M",
                help="Sum of illustrative population across sample regions.",
            )
        with k3:
            st.metric(
                label="Top need region",
                value=top_region[:18] + ("…" if len(top_region) > 18 else ""),
                help="Region with the highest need_score in the sample.",
            )
        with k4:
            st.metric(
                label="Top region budget share",
                value=f"{top_share:.1f}%",
                help="Share of the envelope going to the highest-need region under proportional rule.",
            )

    st.markdown("")

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

    st.markdown("")

    st.subheader("Recommendations")
    rec_box = st.container(border=True)
    with rec_box:
        for line in alloc.recommendation_lines(result, top_n=3):
            st.markdown(f"- {line}")

    st.divider()
    with st.expander("Model note (technical)", expanded=False):
        st.markdown(
            """
Each region receives **budget × (need_score / sum(need_scores))**. Poverty rate and population
are shown for context but **do not** enter the split in this version. See `allocation.py` to change the rule.
            """.strip()
        )


if __name__ == "__main__":
    main()
