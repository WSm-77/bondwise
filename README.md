# Bondwise

EDO vs COI retail bond profit simulator (Polish Treasury inflation-linked bonds).

## Run

```bash
uv sync --extra dev
uv run pytest
uv run streamlit run src/bondwise/app.py
```

Series parameters: COI1030 / EDO1036 (official obligacjeskarbowe.pl offer; research notebook notes).
