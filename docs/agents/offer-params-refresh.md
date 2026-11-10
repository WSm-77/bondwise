# Offer-params refresh / verify

Default series **COI1030** / **EDO1036** (October 2026 offer window) live in `src/bondwise/params.py`. Authoritative sources:

1. [obligacjeskarbowe.pl](https://www.obligacjeskarbowe.pl/) — official series pages
2. NotebookLM notebook “Obligacje 10-letnie EDO: Oferta Skarbowa” (cross-check)

Fragile live scraping is not required.

## Detect mismatch without memory

Checked-in snapshot: `tests/fixtures/offer_params_expected.json`.

```bash
make test
# or: uv run pytest tests/test_offer_params_snapshot.py
```

`tests/test_offer_params_snapshot.py` fails when `params.py` drifts from the snapshot. That is the durable signal — not recollection of the last manual check.

## Refresh path

1. Open the official series pages (and NotebookLM if used) for the current offer window.
2. Compare year-1 rates, margins, early-exit fees, maturities, Belka (19%), face value (100 PLN).
3. Update `src/bondwise/params.py` to match the source.
4. Update `tests/fixtures/offer_params_expected.json` to the same numbers (and note `source` / `offer_window` / `verified_at`).
5. Run `make test`. Green means code and snapshot agree; the fixture comment records when a human last verified against the source.
