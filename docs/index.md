# FastAPI Observer

FastAPI Observer provides structured logging building blocks for FastAPI projects.

## Current scope

- Typed and validated configuration via `ObserverConfig`
- Structured event model via `LogEvent`
- Logger factory with console/file handlers and JSON/text formatting
- Optional in-memory, JSONL, and SQLite event storage
- Minimal dashboard helpers for inspecting captured events

## Compatibility

- Python: `3.10` to `3.14`
- Test matrix: `py310`, `py311`, `py312`, `py313`, `py314` via `tox` and GitHub Actions

## Quick start

```bash
pip install fastapi-observer
```

See [Installation](installation.md) for development, docs, and test commands.

## Documentation

- [Quickstart](quickstart.md)
- [Configuration](configuration.md)
- [Handlers](handlers.md)
- [Dashboard](dashboard.md)
- [API Reference](api-reference.md)
- [Best Practices](best-practices.md)
- [Migration](migration.md)
