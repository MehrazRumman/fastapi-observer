# Best Practices

- Exclude noisy endpoints such as `/health` and `/metrics`
- Redact secrets in both headers and bodies
- Keep `max_body_bytes` small enough to avoid logging large payloads
- Use `SQLiteEventStore` or `JsonFileEventStore` when you want to inspect events after the request finishes
- Close long-lived stores explicitly when a process shuts down
- Start with `log_format="json"` if logs will be shipped to another system

## Recommended baseline

```python
from fastapi_inspector import ObserverConfig

config = ObserverConfig(
    exclude_paths=["/health", "/metrics"],
    redact_headers={"authorization", "cookie"},
    redact_fields={"password", "token", "secret"},
)
```
