# Contributing

1. Create a virtual environment and install `pip install -e ".[ui,dev]"`.
2. Run tests with `pytest`.
3. Run lint checks with `ruff check .`.
4. For scientific changes, document the method and its assumptions in `docs/scientific-methods.md`.
5. Do not present heuristic thresholds as universal rules. Include tests for changes to calculations.
