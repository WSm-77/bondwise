# PR reinvest-toggle live UI evidence

Defaults for shots unless noted: lump 10 000 PLN, horizon 8y, inflation 2.5%, Belka on.

| File | What it shows |
|------|----------------|
| `01-before-main-no-reinvest-control.png` | `main` before this change: Belka only; COI wallet 13 046,01 |
| `02-after-reinvest-on.png` | New control checked (default); KPIs match main |
| `03-after-reinvest-off.png` | Control unchecked; COI wallet drops to 11 356,75 (EDO unchanged pre-maturity) |
| `03b-after-reinvest-off-table.png` | Year table with reinvest off (bonds stay flat; idle holds coupons) |
| `04-after-reinvest-off-12y.png` | Horizon 12y, reinvest off — EDO past maturity stays cash |
| `04b-after-reinvest-on-12y.png` | Horizon 12y, reinvest on — both products roll |

Used in the pull request description; safe to delete after merge if undesired in tree.
