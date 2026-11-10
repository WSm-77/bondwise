"""Matplotlib combo twin-axis chart for COI vs EDO paths."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from bondwise.simulator import SimulationResult

COI_COLOR = "#1f77b4"
EDO_COLOR = "#d62728"


def build_chart(result: SimulationResult) -> Figure:
    years = [p.year for p in result.coi.years]
    coi_wallet = [p.wallet for p in result.coi.years]
    edo_wallet = [p.wallet for p in result.edo.years]
    coi_income = [p.income for p in result.coi.years]
    edo_income = [p.income for p in result.edo.years]
    coi_rolls = [p.year for p in result.coi.years if p.is_roll]
    edo_rolls = [p.year for p in result.edo.years if p.is_roll]

    fig, ax_wallet = plt.subplots(figsize=(10, 5))
    ax_income = ax_wallet.twinx()

    ax_wallet.plot(years, coi_wallet, color=COI_COLOR, linewidth=2, label="COI wallet")
    ax_wallet.plot(years, edo_wallet, color=EDO_COLOR, linewidth=2, label="EDO wallet")
    ax_income.plot(
        years,
        coi_income,
        color=COI_COLOR,
        linestyle="--",
        alpha=0.7,
        label="COI income",
    )
    ax_income.plot(
        years,
        edo_income,
        color=EDO_COLOR,
        linestyle="--",
        alpha=0.7,
        label="EDO income",
    )

    for y in coi_rolls:
        ax_wallet.axvline(y, color=COI_COLOR, alpha=0.25, linestyle=":")
    for y in edo_rolls:
        ax_wallet.axvline(y, color=EDO_COLOR, alpha=0.25, linestyle=":")

    ax_wallet.set_xlabel("Year")
    ax_wallet.set_ylabel("Wallet (PLN)")
    ax_income.set_ylabel("Fee-reduced income (PLN)")
    ax_wallet.set_title("COI vs EDO — wallet and income")

    lines_l, labels_l = ax_wallet.get_legend_handles_labels()
    lines_r, labels_r = ax_income.get_legend_handles_labels()
    ax_wallet.legend(lines_l + lines_r, labels_l + labels_r, loc="upper left")
    fig.tight_layout()
    return fig
