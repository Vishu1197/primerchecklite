# Contributing

Contributions are welcome, especially bug reports, reproducible examples, documentation fixes, and tests that improve scientific correctness.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,ui]"
pytest
ruff check .
```

On Windows, activate the virtual environment with `.venv\Scripts\activate`.

## Contribution expectations

- Include a minimal test for bug fixes.
- Explain the biological or computational assumptions behind new checks.
- Do not label heuristic warnings as clinical or experimental conclusions.
- Keep calculations reproducible and include relevant settings in reports.
- Do not add network calls without documenting privacy, provenance, and reproducibility implications.
- Use synthetic sequences or clearly licensed reference data in tests.
