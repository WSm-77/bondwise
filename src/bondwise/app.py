"""Streamlit UI adapter — thin shell over the pure simulator."""

from __future__ import annotations

import streamlit as st

from bondwise.simulator import simulate


def main() -> None:
    st.set_page_config(page_title="Bondwise", layout="wide")
    st.title("Bondwise")
    st.caption("COI vs EDO retail bond profit simulator")

    with st.sidebar:
        amount = st.number_input(
            "Lump sum (PLN)",
            min_value=0.0,
            value=10_000.0,
            step=100.0,
        )
        horizon = st.slider("Horizon (years)", min_value=1, max_value=20, value=1)
        inflation_pct = st.slider(
            "Assumed future inflation (%)",
            min_value=-5.0,
            max_value=15.0,
            value=2.5,
            step=0.1,
        )
        belka = st.checkbox("Apply Belka tax (19%)", value=True)

    result = simulate(
        lump_sum=amount,
        horizon_years=horizon,
        inflation=inflation_pct / 100.0,
        belka=belka,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("COI final wallet", f"{result.coi.final_wallet:,.2f} PLN")
    c2.metric("EDO final wallet", f"{result.edo.final_wallet:,.2f} PLN")
    c3.metric("Δ EDO − COI", f"{result.delta_edo_minus_coi:,.2f} PLN")

    rows = []
    for coi_y, edo_y in zip(result.coi.years, result.edo.years, strict=True):
        rows.append(
            {
                "Year": coi_y.year,
                "COI wallet": coi_y.wallet,
                "COI income": coi_y.income,
                "EDO wallet": edo_y.wallet,
                "EDO income": edo_y.income,
            }
        )
    st.subheader("Year-by-year")
    st.dataframe(rows, use_container_width=True)


if __name__ == "__main__":
    main()
