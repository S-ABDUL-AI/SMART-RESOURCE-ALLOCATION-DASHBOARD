"""
Budget allocation logic: share of total budget is proportional to need_score.

No Streamlit imports here, so this module is easy to test and reuse.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def validate_regions(regions: list[dict]) -> None:
    if not regions:
        raise ValueError("At least one region is required.")
    for i, row in enumerate(regions):
        if "region" not in row or not str(row["region"]).strip():
            raise ValueError(f"Row {i}: missing or empty region name.")
        need = float(row.get("need_score", 0.0))
        if need < 0 or np.isnan(need):
            raise ValueError(f"Row {i}: need_score must be a non-negative number.")
        pop = float(row.get("population", 0.0))
        if pop <= 0 or np.isnan(pop):
            raise ValueError(f"Row {i}: population must be positive.")
        pr = float(row.get("poverty_rate", 0.0))
        if pr < 0 or pr > 1 or np.isnan(pr):
            raise ValueError(f"Row {i}: poverty_rate must be between 0 and 1.")


def allocate_budget(budget: float, regions: list[dict]) -> pd.DataFrame:
    """
    Split budget across regions in proportion to need_score.

    If every need_score is zero, split the budget equally (last-resort rule).
    """
    validate_regions(regions)
    if budget < 0 or np.isnan(budget):
        raise ValueError("Budget must be a non-negative finite number.")

    df = pd.DataFrame(regions).copy()
    df["need_score"] = df["need_score"].astype(float)
    total_need = float(df["need_score"].sum())
    if total_need <= 0.0:
        weights = np.ones(len(df), dtype=float) / len(df)
    else:
        weights = df["need_score"].values.astype(float) / total_need

    df["allocation"] = budget * weights
    df["share_of_budget"] = 100.0 * weights
    df["population"] = df["population"].astype(int)
    df["poverty_rate"] = df["poverty_rate"].astype(float)

    return df.sort_values("need_score", ascending=False).reset_index(drop=True)


def priority_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Same as input order after allocate_budget (already sorted by need_score)."""
    return df.assign(priority_rank=np.arange(1, len(df) + 1))


def recommendation_lines(df: pd.DataFrame, top_n: int = 3) -> list[str]:
    """Short policy-style lines for the highest-need regions."""
    lines: list[str] = []
    head = df.head(top_n)
    for _, row in head.iterrows():
        lines.append(
            f"**{row['region']}** should receive priority funding in this toy picture: "
            f"need score **{row['need_score']:.0f}** (population **{row['population']:,}**, "
            f"poverty rate **{row['poverty_rate'] * 100:.1f}%**)."
        )
    return lines
