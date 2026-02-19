# fastapi-observer

FastAPI Observer provides structured logging and observability helpers for FastAPI applications.

## Python compatibility

- Supported Python versions: `3.10`, `3.11`, `3.12`, `3.13`, `3.14`
- Enforced in CI with tox matrix: `py310`, `py311`, `py312`, `py313`, `py314`

## Package versions

### Runtime

- `pydantic>=2.0,<3.0`

### Testing

- `pytest>=8.0`
- `pytest-cov>=5.0`

### Documentation

- `mkdocs>=1.6`
- `mkdocs-material>=9.5`

### Development

- `pre-commit>=3.7`
- `black>=24.10`

## Install

```bash
pip install fastapi-observer
```

For development:

```bash
pip install -e ".[test,docs,dev]"
```

## Tests and coverage

Run tests:

```bash
pytest -q
```

Run tests with coverage:

```bash
pytest -q --cov=fastapi_observer --cov-report=term-missing --cov-report=xml
```

Run full Python version matrix locally:

```bash
tox
```

## Docs

Build docs:

```bash
mkdocs build --strict
```

Serve docs locally:

```bash
mkdocs serve
```
