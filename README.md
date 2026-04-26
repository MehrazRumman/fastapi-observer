# fastapi-inspector

Structured logging and observability middleware for FastAPI applications.

[![Test](https://github.com/MehrazRumman/fastapi-observer/actions/workflows/tests.yml/badge.svg)](https://github.com/MehrazRumman/fastapi-observer/actions/workflows/tests.yml)
[![coverage](https://raw.githubusercontent.com/MehrazRumman/fastapi-observer/main/assets/coverage.svg)](https://github.com/MehrazRumman/fastapi-observer/actions/workflows/coverage-badge.yml)
[![pypi package](https://img.shields.io/pypi/v/fastapi-inspector?logo=pypi&label=pypi%20package)](https://pypi.org/project/fastapi-inspector/)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-brightgreen?logo=python&logoColor=white)](#python-compatibility)

**[Documentation](https://mehrazrumman.github.io/fastapi-inspector/)** · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)

---

## Features

- **Zero-boilerplate middleware** — one line to log every request and response
- **Structured events** — typed `LogEvent` objects with method, path, status code, latency, and more
- **Pluggable storage** — in-memory, JSON file, JSON Lines, or SQLite backends
- **Filter pipeline** — drop health-check noise, log only errors, or set a minimum latency threshold
- **Built-in dashboard** — mount an event-inspector UI at any path in your app
- **Multiple formatters** — plain-text or JSON output
- **Python 3.10–3.14** with full CI coverage across all versions

---

## Install

```bash
pip install fastapi-inspector
```

---

## Quick start

### Basic logging

```python
from fastapi import FastAPI
from fastapi_inspector import ObserverConfig, ObserverMiddleware

app = FastAPI()
app.add_middleware(ObserverMiddleware, config=ObserverConfig())

@app.get("/items")
async def list_items():
    return {"items": ["alpha", "beta", "gamma"]}
```

Every request is now logged to the console with method, path, status code, and latency.

### Persist events and open the dashboard

```python
from fastapi import FastAPI
from fastapi_inspector import ObserverConfig, ObserverMiddleware, build_dashboard_app
from fastapi_inspector.storage import InMemoryEventStore

app = FastAPI()
store = InMemoryEventStore()

app.add_middleware(ObserverMiddleware, config=ObserverConfig(), storage=store)
app.mount("/dashboard", build_dashboard_app(store, title="Observer Dashboard"))
```

Open `http://localhost:8000/dashboard` to browse and inspect logged events.

### Filter out noise

```python
from fastapi_inspector import ObserverConfig, ObserverMiddleware, only_errors, min_duration_ms

app.add_middleware(
    ObserverMiddleware,
    config=ObserverConfig(handlers=["console"], log_format="json"),
    event_filters=[
        only_errors,           # log 4xx/5xx responses only
        min_duration_ms(50.0), # ignore fast responses
    ],
)
```

See the [examples/](examples/) directory for more patterns including SQLite storage and custom filters.

---

## Storage backends

| Backend | Class | Use case |
|---|---|---|
| In-memory | `InMemoryEventStore` | Development, testing |
| JSON file | `JsonFileEventStore` | Simple persistence |
| JSON Lines | `JsonLinesEventStore` | Append-only log files |
| SQLite | `SQLiteEventStore` | Queryable local storage |

---

## Python compatibility

- Supported versions: `3.10`, `3.11`, `3.12`, `3.13`, `3.14`
- Enforced in CI with a tox matrix across all versions

---

## Development

Install all dependencies:

```bash
pip install -e ".[test,docs,dev]"
pre-commit install
```

Run tests:

```bash
pytest -q
pytest -q --cov=fastapi_inspector --cov-report=term-missing   # with coverage
tox                                                           # full version matrix
```

Build and preview docs:

```bash
mkdocs serve        # http://127.0.0.1:8000
mkdocs build --strict
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.
