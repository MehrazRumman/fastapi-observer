# Installation

## Runtime install

```bash
pip install fastapi-observer
```

## Development install

```bash
pip install -e ".[test,docs,dev]"
```

## Run tests locally

```bash
pytest -q --cov=fastapi_observer --cov-report=term-missing --cov-report=xml
```

## Run multi-version tests with tox

```bash
tox
```

## Build docs

```bash
mkdocs build --strict
mkdocs serve
```
