# Glossary

Terms from the shipped MVP (README, public `params` / `simulator` API). No speculative fill.

| Term | Meaning |
|------|---------|
| **Belka** | 19% capital-gains tax on interest (`BELKA_RATE`); UI default on, with a gross (pre-Belka) toggle. |
| **COI / COI1030** | 4-year Polish Treasury inflation-linked retail bond series simulated by default. |
| **EDO / EDO1036** | 10-year Polish Treasury inflation-linked retail bond series simulated by default. |
| **Early-exit fee** | Per-bond premature-redemption fee (`early_exit_fee_per_bond`); COI uncapped after year 1, EDO capped at accrued interest. |
| **Exit cash-out** | Counterfactual redeem-at-end-of-year-N total: bond face + pre-reinvest idle + interest after **Exit fee** and **Exit tax** (`ExitSnapshot.cash_out`). |
| **Exit fee** | Early-exit fee on the redeem-at-N path (0 at maturity); not the hold-path coupon. |
| **Exit tax** | Belka withheld on (interest_or_accrued − exit fee); 0 when Belka is off or the after-fee base is ≤ 0. |
| **Exit profit** | Exit cash-out − initial lump sum (what-if redeem at N). Distinct from held **Profit** and hold-path **income**. |
| **Face value** | 100 PLN per bond (`FACE_VALUE`); purchases floored to whole bonds. |
| **Idle cash** | Cash not held as whole bonds; earns 0% and is included in wallet totals. With **Reinvest** on, usually the sub-100 PLN remainder after buys; with **Reinvest** off, also holds net coupons/interest and post-maturity proceeds. |
| **Margin** | Post-year-1 additive rate used with inflation (`margin + max(inflation, 0)`). |
| **ProductParams** | Injectable offer constants for one series (`code`, `year1_rate`, `margin`, fees, maturity, fee-cap flag). |
| **Reinvest** | When on (default), hold-path net coupons buy more whole bonds and maturity rolls into a new cycle. When off, net coupon/interest stays in **Idle cash** and maturity converts bonds + net to idle with no rebuy (`simulate(..., reinvest=)`). |
| **Roll** | At maturity with **Reinvest** on, reinvest available proceeds into a new cycle of the same product (COI every 4y, EDO every 10y). With **Reinvest** off there is no roll (`is_roll` false, bonds 0). |
| **Profit** | Cumulative gain: wallet − initial lump sum. Distinct from **income** (that year’s fee-reduced payout). |
| **Wallet** | Portfolio value at a year point (bonds + idle cash); income is the fee-reduced payout metric for that year. |
| **Year-1 rate** | Fixed coupon/interest rate for the first year of a cycle (`year1_rate`); later years use margin + inflation. |
