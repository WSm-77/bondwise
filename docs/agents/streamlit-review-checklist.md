# Reviewer checklist: Streamlit AC + injectable ProductParams

Use when reviewing UI or simulator wiring changes. Scope is only Streamlit acceptance and injectable offer params — not a general process doc.

## Streamlit acceptance

- [ ] Sidebar has lump-sum slider, horizon 1–20 (integers), assumed future inflation (%), Belka checkbox (default on)
- [ ] Inflation slider floor is 0% (UI cannot send negative inflation); simulator also floors post-year-1 inflation at 0
- [ ] KPI row shows COI/EDO final wallet, COI/EDO profit, and Δ EDO − COI
- [ ] Chart is twin-axis (wallet lines + fee-reduced income); roll years marked; idle cash not a separate series
- [ ] Expandable year-by-year table includes idle cash columns for COI and EDO
- [ ] App stays a thin adapter: call `simulate(...)`; no bond math in `app.py` / `chart.py`

## Injectable ProductParams

- [ ] Offer constants live in `src/bondwise/params.py` (`ProductParams`, `COI`, `EDO`, `BELKA_RATE`, `FACE_VALUE`)
- [ ] `simulate(..., coi=, edo=)` accepts injectable `ProductParams` (defaults to module constants)
- [ ] UI may keep default series; any new UI/edit path must not hard-code rates/margins/fees outside `params.py`
- [ ] Changing series codes or offer numbers updates `params.py` (and the offer-params snapshot — see `docs/agents/offer-params-refresh.md`)
