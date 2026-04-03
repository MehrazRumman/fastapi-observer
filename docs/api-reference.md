# API Reference

## Top-level exports

The package root exports the main entry points:

- `ObserverConfig`
- `ObserverMiddleware`
- `LogEvent`
- `FilterPipeline`
- `only_errors`
- `min_status_code`
- `min_duration_ms`
- `exclude_paths`
- `build_logger`
- `log_event`
- `build_dashboard_app`
- `create_dashboard_app`
- `InMemoryEventStore`
- `JsonLinesEventStore`
- `JsonFileEventStore`
- `SQLiteEventStore`

## Models

`LogEvent` is the structured event model used across the package.

## Configuration

`ObserverConfig` defines filtering, formatting, and redaction behavior.

## Storage

The storage package provides:

- `InMemoryEventStore`
- `JsonLinesEventStore`
- `JsonFileEventStore`
- `SQLiteEventStore`

## Filters

- `only_errors(event)`
- `min_status_code(code)`
- `min_duration_ms(ms)`
- `exclude_paths(paths)`

## Logger helpers

- `build_logger(config, logger_name="fastapi_observer")`
- `log_event(logger, config, event)`
