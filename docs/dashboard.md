# Dashboard

`build_dashboard_app()` creates a small FastAPI application for inspecting stored events.

## Features

- `/` renders an HTML dashboard
- `/events` returns structured event data
- `DELETE /events` clears the store
- `/health` reports service health

## Storage

The dashboard works with any object that implements the `EventStore` protocol.

```python
from fastapi_observer.dashboard import build_dashboard_app
from fastapi_observer.storage import InMemoryEventStore

app = build_dashboard_app(InMemoryEventStore())
```

## Notes

- The dashboard is intentionally lightweight
- It is useful for local inspection and test fixtures
- For persistent dashboards, use `JsonFileEventStore` or `SQLiteEventStore`
