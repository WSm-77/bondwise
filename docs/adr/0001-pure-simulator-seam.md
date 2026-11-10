# ADR-0001: Pure simulator seam

## Status

Accepted (shipped MVP)

## Context

Bond math must be regression-tested without driving Streamlit or matplotlib.

## Decision

Put portfolio simulation in `src/bondwise/simulator.py` as a pure function (`simulate`). Streamlit (`app.py`) and matplotlib (`chart.py`) are thin adapters only. Pytest covers the simulator seam.

## Consequences

UI changes do not require browser tests for bond math. Spec slips in the UI still need a separate reviewer checklist.
