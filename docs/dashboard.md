# Dashboard

`build_dashboard_app()` creates a small FastAPI application for inspecting stored events.

## Features

- `/` renders an HTML dashboard of the most recent events (200 by default, set with `max_page_events`)
- `/events` returns structured event data
- `DELETE /events` clears the store
- `/health` reports service health

## Storage

The dashboard works with any object that implements the `EventStore` protocol.

```python
from fastapi_inspector.dashboard import build_dashboard_app
from fastapi_inspector.storage import InMemoryEventStore

app = build_dashboard_app(InMemoryEventStore())
```

## Notes

- The dashboard is intentionally lightweight
- It is useful for local inspection and test fixtures
- `/events?limit=N` returns the latest `N` events; omit `limit` to fetch all of them
- For persistent dashboards, use `JsonFileEventStore` or `SQLiteEventStore`
