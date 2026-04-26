# Contributing to fastapi-inspector

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/fastapi-inspector.git
   cd fastapi-inspector
   ```

2. Install all development dependencies:
   ```bash
   pip install -e ".[test,docs,dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Running Tests

```bash
# Run the full test suite
pytest -q

# Run with coverage report
pytest --cov=fastapi_observer --cov-report=term-missing

# Run a specific test file
pytest tests/test_middleware.py -v
```

Maintain coverage above 85% for any new code you add.

## Code Style

This project uses [Black](https://black.readthedocs.io/) for formatting.

```bash
# Format all files
black .

# Check formatting without changing files
black --check .
```

Pre-commit hooks run Black automatically on every commit. If a commit is rejected, run `black .` and re-stage the files.

## Building Documentation

```bash
mkdocs serve        # preview locally at http://127.0.0.1:8000
mkdocs build        # build static site into /site
```

## Submitting a Pull Request

1. Make sure all tests pass and coverage has not dropped.
2. Update documentation if you changed public APIs or added new features.
3. Add an entry to [CHANGELOG.md](CHANGELOG.md) under the `Unreleased` section.
4. Open a pull request against the `main` branch with a clear description of the change.

## Reporting Bugs

Open an issue at <https://github.com/MehrazRumman/fastapi-inspector/issues> with:

- A minimal reproducible example
- Expected vs. actual behaviour
- Python version and fastapi-inspector version

## Security Issues

Please do **not** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md) for the responsible disclosure process.
