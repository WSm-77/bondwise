"""Matplotlib grouped stacked-bar chart: lump sum + profit for COI vs EDO."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from bondwise.simulator import SimulationResult

COI_COLOR = "#1f77b4"
EDO_COLOR = "#d62728"
LUMP_COLOR = "#c7c7c7"


def build_chart(result: SimulationResult, *, lump_sum: float) -> Figure:
    years = [p.year for p in result.coi.years]
    coi_wallet = [p.wallet for p in result.coi.years]
    edo_wallet = [p.wallet for p in result.edo.years]
    # Presentation stack: profit = wallet − initial lump sum (GLOSSARY Profit).
    coi_profit = [w - lump_sum for w in coi_wallet]
    edo_profit = [w - lump_sum for w in edo_wallet]
    coi_rolls = [p.year for p in result.coi.years if p.is_roll]
    edo_rolls = [p.year for p in result.edo.years if p.is_roll]

    n = len(years)
    x = list(range(n))
    width = 0.35
    lump_sum_heights = [lump_sum] * n

    fig, ax = plt.subplots(figsize=(10, 5))

    coi_x = [i - width / 2 for i in x]
    edo_x = [i + width / 2 for i in x]

    ax.bar(
        coi_x,
        lump_sum_heights,
        width,
        color=LUMP_COLOR,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.bar(
        coi_x,
        coi_profit,
        width,
        bottom=lump_sum_heights,
        color=COI_COLOR,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.bar(
        edo_x,
        lump_sum_heights,
        width,
        color=LUMP_COLOR,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.bar(
        edo_x,
        edo_profit,
        width,
        bottom=lump_sum_heights,
        color=EDO_COLOR,
        edgecolor="white",
        linewidth=0.5,
    )

    for y in coi_rolls:
        ax.axvline(years.index(y), color=COI_COLOR, alpha=0.25, linestyle=":")
    for y in edo_rolls:
        ax.axvline(years.index(y), color=EDO_COLOR, alpha=0.25, linestyle=":")

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_xlabel("Year")
    ax.set_ylabel("Wallet (PLN)")
    ax.set_title("COI vs EDO — wallet composition (lump sum + profit)")

    legend = [
        Patch(facecolor=LUMP_COLOR, edgecolor="white", label="lump sum"),
        Patch(facecolor=COI_COLOR, edgecolor="white", label="COI profit"),
        Patch(facecolor=EDO_COLOR, edgecolor="white", label="EDO profit"),
    ]
    ax.legend(handles=legend, loc="upper left")
    fig.tight_layout()
    return fig
