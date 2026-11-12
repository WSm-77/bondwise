## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues on `WSm-77/bondwise` (via `gh`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`GLOSSARY.md` + `docs/adr/`). See `docs/agents/domain.md`.

### Code map

- `src/bondwise/simulator.py` — pure bond portfolio simulator (`simulate`)
- `src/bondwise/params.py` — offer constants / injectable `ProductParams` (COI1030, EDO1036)
- `web/` — static Pages shell (HTML/CSS/JS + Chart.js); Pyodide loads `simulate`

### Tests

One command (installs test deps + pytest): `make test`

### Review

Offer-params refresh: `docs/agents/offer-params-refresh.md`.
