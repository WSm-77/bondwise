"""Streamlit UI adapter — thin shell over the pure simulator."""

from __future__ import annotations

import streamlit as st

from bondwise.simulator import simulate


def main() -> None:
    st.set_page_config(page_title="Bondwise", layout="wide")
    st.title("Bondwise")
    st.caption("COI vs EDO retail bond profit simulator")

    amount = st.number_input(
        "Lump sum (PLN)",
        min_value=0.0,
        value=10_000.0,
        step=100.0,
    )
    belka = st.checkbox("Apply Belka tax (19%)", value=True)

    result = simulate(lump_sum=amount, horizon_years=1, inflation=0.0, belka=belka)

    c1, c2, c3 = st.columns(3)
    c1.metric("COI final wallet", f"{result.coi.final_wallet:,.2f} PLN")
    c2.metric("EDO final wallet", f"{result.edo.final_wallet:,.2f} PLN")
    c3.metric("Δ EDO − COI", f"{result.delta_edo_minus_coi:,.2f} PLN")

    st.write(
        {
            "COI profit": result.coi.profit,
            "EDO profit": result.edo.profit,
            "COI income (y1)": result.coi.years[0].income if result.coi.years else 0.0,
            "EDO income (y1)": result.edo.years[0].income if result.edo.years else 0.0,
        }
    )


if __name__ == "__main__":
    main()
