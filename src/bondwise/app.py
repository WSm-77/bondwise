"""Streamlit UI adapter — thin shell over the pure simulator."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

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


def _snap_to_step(value: Any, min_value: Any, max_value: Any, step: Any) -> Any:
    """Nearest in-range step value (for slider widgets that cannot hold every int)."""
    steps = round((float(value) - float(min_value)) / float(step))
    snapped = float(min_value) + steps * float(step)
    snapped = max(float(min_value), min(float(max_value), snapped))
    if isinstance(step, int) and isinstance(min_value, int):
        return int(round(snapped))
    return snapped


def _synced_slider_number(
    *,
    label: str,
    canonical_key: str,
    slider_key: str,
    number_key: str,
    min_value: Any,
    max_value: Any,
    slider_step: Any,
    number_step: Any,
    coerce: Callable[[Any], Any],
    number_format: str | None = None,
) -> Any:
    """Render a slider paired with a synced number_input; return canonical value."""

    def _from_slider() -> None:
        st.session_state[canonical_key] = coerce(st.session_state[slider_key])

    def _from_number() -> None:
        st.session_state[canonical_key] = coerce(st.session_state[number_key])

    canonical = coerce(st.session_state[canonical_key])
    st.session_state[slider_key] = _snap_to_step(
        canonical, min_value, max_value, slider_step
    )
    st.session_state[number_key] = canonical
    cols = st.columns([3, 1])
    cols[0].slider(
        label,
        min_value=min_value,
        max_value=max_value,
        step=slider_step,
        key=slider_key,
        on_change=_from_slider,
    )
    number_kwargs: dict[str, Any] = {
        "label": f"{label} exact",
        "min_value": min_value,
        "max_value": max_value,
        "step": number_step,
        "key": number_key,
        "on_change": _from_number,
        "label_visibility": "collapsed",
    }
    if number_format is not None:
        number_kwargs["format"] = number_format
    cols[1].number_input(**number_kwargs)
    return coerce(st.session_state[canonical_key])


def main() -> None:
    st.set_page_config(page_title="Bondwise", layout="wide")
    st.title("Bondwise")
    st.caption("COI vs EDO retail bond profit simulator")

    _init_control_state()

    with st.sidebar:
        amount = _synced_slider_number(
            label="Lump sum (PLN)",
            canonical_key="lump_sum",
            slider_key="lump_sum_slider",
            number_key="lump_sum_number",
            min_value=_AMOUNT_MIN,
            max_value=_AMOUNT_MAX,
            slider_step=_AMOUNT_STEP,
            number_step=1,
            coerce=int,
        )
        horizon = st.slider("Horizon (years)", min_value=1, max_value=20, value=8)
        inflation_pct = _synced_slider_number(
            label="Assumed future inflation (%)",
            canonical_key="inflation_pct",
            slider_key="inflation_pct_slider",
            number_key="inflation_pct_number",
            min_value=_INFLATION_MIN,
            max_value=_INFLATION_MAX,
            slider_step=_INFLATION_STEP,
            number_step=_INFLATION_STEP,
            coerce=float,
            number_format="%.1f",
        )
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
