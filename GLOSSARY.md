# Glossary

Terms from the shipped MVP (README, public `params` / `simulator` API). No speculative fill.

| Term | Meaning |
|------|---------|
| **Belka** | 19% capital-gains tax on interest (`BELKA_RATE`); UI default on, with a gross (pre-Belka) toggle. |
| **COI / COI1030** | 4-year Polish Treasury inflation-linked retail bond series simulated by default. |
| **EDO / EDO1036** | 10-year Polish Treasury inflation-linked retail bond series simulated by default. |
| **Early-exit fee** | Per-bond premature-redemption fee (`early_exit_fee_per_bond`); COI uncapped after year 1, EDO capped at accrued interest. |
| **Face value** | 100 PLN per bond (`FACE_VALUE`); purchases floored to whole bonds. |
| **Idle cash** | Remainder under 100 PLN that earns 0% and is included in wallet totals. |
| **Margin** | Post-year-1 additive rate used with inflation (`margin + max(inflation, 0)`). |
| **ProductParams** | Injectable offer constants for one series (`code`, `year1_rate`, `margin`, fees, maturity, fee-cap flag). |
| **Roll** | At maturity, reinvest available proceeds into a new cycle of the same product (COI every 4y, EDO every 10y). |
| **Wallet** | Portfolio value at a year point (bonds + idle cash); income is the fee-reduced payout metric for that year. |
| **Year-1 rate** | Fixed coupon/interest rate for the first year of a cycle (`year1_rate`); later years use margin + inflation. |
