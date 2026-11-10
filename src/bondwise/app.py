"""Streamlit UI adapter — thin shell over the pure simulator."""

from __future__ import annotations

import streamlit as st

from bondwise.chart import build_chart
from bondwise.simulator import simulate

_AMOUNT_MIN = 0
_AMOUNT_MAX = 500_000
_AMOUNT_STEP = 100
_AMOUNT_DEFAULT = 10_000

_INFLATION_MIN = 0.0
_INFLATION_MAX = 15.0
_INFLATION_STEP = 0.1
_INFLATION_DEFAULT = 2.5


def _init_control_state() -> None:
    if "lump_sum" not in st.session_state:
        st.session_state.lump_sum = _AMOUNT_DEFAULT
    if "inflation_pct" not in st.session_state:
        st.session_state.inflation_pct = _INFLATION_DEFAULT


def _sync_lump_from_slider() -> None:
    st.session_state.lump_sum = st.session_state.lump_sum_slider


def _sync_lump_from_number() -> None:
    st.session_state.lump_sum = int(st.session_state.lump_sum_number)


def _sync_inflation_from_slider() -> None:
    st.session_state.inflation_pct = float(st.session_state.inflation_pct_slider)


def _sync_inflation_from_number() -> None:
    st.session_state.inflation_pct = float(st.session_state.inflation_pct_number)


def main() -> None:
    st.set_page_config(page_title="Bondwise", layout="wide")
    st.title("Bondwise")
    st.caption("COI vs EDO retail bond profit simulator")

    _init_control_state()

    with st.sidebar:
        st.session_state.lump_sum_slider = st.session_state.lump_sum
        st.session_state.lump_sum_number = st.session_state.lump_sum
        amount_cols = st.columns([3, 1])
        amount_cols[0].slider(
            "Lump sum (PLN)",
            min_value=_AMOUNT_MIN,
            max_value=_AMOUNT_MAX,
            step=_AMOUNT_STEP,
            key="lump_sum_slider",
            on_change=_sync_lump_from_slider,
        )
        amount_cols[1].number_input(
            "Lump sum exact",
            min_value=_AMOUNT_MIN,
            max_value=_AMOUNT_MAX,
            step=_AMOUNT_STEP,
            key="lump_sum_number",
            on_change=_sync_lump_from_number,
            label_visibility="collapsed",
        )
        amount = int(st.session_state.lump_sum)

        horizon = st.slider("Horizon (years)", min_value=1, max_value=20, value=8)

        st.session_state.inflation_pct_slider = st.session_state.inflation_pct
        st.session_state.inflation_pct_number = st.session_state.inflation_pct
        inflation_cols = st.columns([3, 1])
        inflation_cols[0].slider(
            "Assumed future inflation (%)",
            min_value=_INFLATION_MIN,
            max_value=_INFLATION_MAX,
            step=_INFLATION_STEP,
            key="inflation_pct_slider",
            on_change=_sync_inflation_from_slider,
        )
        inflation_cols[1].number_input(
            "Inflation exact",
            min_value=_INFLATION_MIN,
            max_value=_INFLATION_MAX,
            step=_INFLATION_STEP,
            key="inflation_pct_number",
            on_change=_sync_inflation_from_number,
            label_visibility="collapsed",
            format="%.1f",
        )
        inflation_pct = float(st.session_state.inflation_pct)

        belka = st.checkbox("Apply Belka tax (19%)", value=True)

    result = simulate(
        lump_sum=float(amount),
        horizon_years=horizon,
        inflation=inflation_pct / 100.0,
        belka=belka,
    )

    wallet_coi, wallet_edo, profit_coi, profit_edo, delta = st.columns(5)
    wallet_coi.metric("COI final wallet", f"{result.coi.final_wallet:,.2f} PLN")
    wallet_edo.metric("EDO final wallet", f"{result.edo.final_wallet:,.2f} PLN")
    profit_coi.metric("COI profit", f"{result.coi.profit:,.2f} PLN")
    profit_edo.metric("EDO profit", f"{result.edo.profit:,.2f} PLN")
    delta.metric("Δ EDO − COI", f"{result.delta_edo_minus_coi:,.2f} PLN")

    st.pyplot(build_chart(result, lump_sum=float(amount)), clear_figure=True)

    rows = []
    for coi_y, edo_y in zip(result.coi.years, result.edo.years, strict=True):
        rows.append(
            {
                "Year": coi_y.year,
                "COI wallet": coi_y.wallet,
                "COI income": coi_y.income,
                "COI bonds": coi_y.bonds,
                "COI idle": coi_y.idle_cash,
                "COI roll": coi_y.is_roll,
                "EDO wallet": edo_y.wallet,
                "EDO income": edo_y.income,
                "EDO bonds": edo_y.bonds,
                "EDO idle": edo_y.idle_cash,
                "EDO roll": edo_y.is_roll,
            }
        )
    with st.expander("Year-by-year table", expanded=False):
        st.dataframe(rows, use_container_width=True)


if __name__ == "__main__":
    main()
