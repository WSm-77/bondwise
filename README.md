# Bondwise

Compare Polish Treasury inflation-linked retail bonds — **4-year COI** vs **10-year EDO** — for a lump-sum investment. Adjust amount, horizon (1–20 years), assumed future inflation, and Belka tax. The app shows wallet growth, fee-reduced income, roll markers, KPIs, and a year-by-year table.

## Run

```bash
uv sync --extra dev
uv run pytest
uv run streamlit run src/bondwise/app.py
```

## Series source

Default product parameters match the official October 2026 offer window for series **COI1030** and **EDO1036** on [obligacjeskarbowe.pl](https://www.obligacjeskarbowe.pl/), cross-checked against the NotebookLM research notebook “Obligacje 10-letnie EDO: Oferta Skarbowa”. Year-1 rates, margins, early-exit fees, and Belka (19%) live in `src/bondwise/params.py`.

## Model limits (v1)

- Whole-year steps only (no mid-year day-count)
- Lump sum only (no DCA / recurring contributions)
- Idle cash under 100 PLN sits at 0% and is included in wallet totals
