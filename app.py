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
        "Allocate a fixed public budget across regions using a transparent need-based rule, "
        "with a clear executive view of trade-offs and priority areas."
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
    scores = pd.to_numeric(result["need_score"], errors="coerce").fillna(0.0)
    if len(scores) >= 3 and scores.nunique() >= 3:
        q1, q2 = scores.quantile([1 / 3, 2 / 3])
        result["priority_band"] = np.where(
            scores <= q1, "Low", np.where(scores <= q2, "Medium", "High")
        )
    else:
        result["priority_band"] = "Medium"
    result["priority_area"] = result["priority_band"].map(
        {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}
    )

    # --- Key indicators ---
    st.subheader("Key indicators")
    total_pop = int(result["population"].sum())
    top_share = float(result.iloc[0]["share_of_budget"])
    top_region = str(result.iloc[0]["region"])
    top_band = str(result.iloc[0]["priority_band"])

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
    st.caption(f"Current highest-priority band in this run: **{top_band}**")

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

    st.subheader("Recommendations")
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
