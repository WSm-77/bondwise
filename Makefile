.PHONY: test site serve

# One-command path: install test deps and run pytest.
test:
	uv sync --extra dev && uv run pytest

# Build static Pages tree into gitignored dist/ (web assets + sim zip).
site:
	rm -rf dist
	mkdir -p dist/css dist/js dist/pkg dist/.pkg-src/bondwise
	cp web/index.html dist/index.html
	cp web/css/app.css dist/css/app.css
	cp web/js/app.js dist/js/app.js
	cp src/bondwise/__init__.py dist/.pkg-src/bondwise/__init__.py
	cp src/bondwise/params.py dist/.pkg-src/bondwise/params.py
	cp src/bondwise/simulator.py dist/.pkg-src/bondwise/simulator.py
	( cd dist/.pkg-src && zip -qr ../pkg/bondwise-sim.zip bondwise )
	rm -rf dist/.pkg-src

# Serve the built site from dist/ (local root `/`).
serve:
	python3 -m http.server 8000 --directory dist
