# Bondwise

Compare Polish Treasury inflation-linked retail bonds — **4-year COI** vs **10-year EDO** — for a lump-sum investment. Adjust amount, horizon (1–20 years), assumed future inflation, and Belka tax. The app shows wallet growth, fee-reduced income, roll markers, KPIs, and a year-by-year table.

Interactive UI: https://wsm-77.github.io/bondwise/

## Run

```bash
make test
make site && make serve
```

`make test` runs `uv sync --extra dev && uv run pytest`.  
`make site` builds the static shell + Pyodide sim zip into gitignored `dist/`.  
`make serve` serves `dist/` at http://127.0.0.1:8000/ .

## Series source

Default product parameters match the official October 2026 offer window for series **COI1030** and **EDO1036** on [obligacjeskarbowe.pl](https://www.obligacjeskarbowe.pl/), cross-checked against the NotebookLM research notebook “Obligacje 10-letnie EDO: Oferta Skarbowa”. Year-1 rates, margins, early-exit fees, and Belka (19%) live in `src/bondwise/params.py`. To refresh or verify those constants against the source, see `docs/agents/offer-params-refresh.md`.

## Model limits (v1)

- Whole-year steps only (no mid-year day-count)
- Lump sum only (no DCA / recurring contributions)
- Idle cash under 100 PLN sits at 0% and is included in wallet totals
