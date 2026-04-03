# Migration

## From a plain FastAPI app

1. Add `ObserverMiddleware`
2. Start with the default `ObserverConfig`
3. Enable request or response body capture only when you need it
4. Add filters to reduce log noise

## Existing loggers

If your app already configures logging, use `build_logger()` to create a dedicated observer logger and keep propagation disabled.

## Storage-backed setups

- Use `JsonFileEventStore` for a simple local trail
- Use `SQLiteEventStore` when you need queryable persistence
- Use `InMemoryEventStore` for tests and ephemeral dashboards
