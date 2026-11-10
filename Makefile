.PHONY: test

# One-command path: install test deps and run pytest.
test:
	uv sync --extra dev && uv run pytest
