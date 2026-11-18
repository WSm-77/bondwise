# Offer-refresh evidence (strategy 6)

Scenario (UI defaults): lump **10 000 PLN**, horizon **8y**, inflation **2.5%**, Belka **on**.

| Mode | COI final wallet | EDO final wallet | Δ EDO − COI |
|------|------------------:|-----------------:|------------:|
| Fixed (blind reinvest) | 13 046,01 | 13 269,70 | **+223,69** (EDO ahead) |
| Offer refresh (demo schedule) | 13 540,51 | 13 269,70 | **−270,81** (COI ahead) |

- **Before:** `before-fixed-offers.png` — fixed COI1030 every cycle; EDO wins.
- **After:** `after-offer-refresh.png` — demo schedule refreshes COI terms at the year-4 roll; refreshed COI beats EDO.

Demo schedule: cycle 0 = live COI1030; cycle 1+ = hypothetical `COI-DEMO-NEXT` (year-1 6.5%, margin 2.5%).
