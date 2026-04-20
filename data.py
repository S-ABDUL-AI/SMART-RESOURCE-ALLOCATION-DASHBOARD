"""
Sample regions for the Smart Resource Allocation Dashboard.

Fields are illustrative only, not official statistics.
"""

from __future__ import annotations

from typing import Any

# need_score: higher means greater priority in this toy model (same units across regions).
SAMPLE_REGIONS: list[dict[str, Any]] = [
    {
        "region": "North Delta",
        "need_score": 88.0,
        "population": 1_240_000,
        "poverty_rate": 0.34,
    },
    {
        "region": "Central Highlands",
        "need_score": 72.0,
        "population": 890_000,
        "poverty_rate": 0.28,
    },
    {
        "region": "Coastal Metro East",
        "need_score": 54.0,
        "population": 2_100_000,
        "poverty_rate": 0.17,
    },
    {
        "region": "South River Valley",
        "need_score": 91.0,
        "population": 670_000,
        "poverty_rate": 0.39,
    },
    {
        "region": "Western Plateau",
        "need_score": 63.0,
        "population": 510_000,
        "poverty_rate": 0.22,
    },
    {
        "region": "Capital Ring",
        "need_score": 41.0,
        "population": 3_400_000,
        "poverty_rate": 0.12,
    },
]
