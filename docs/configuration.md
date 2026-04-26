# Configuration

`ObserverConfig` controls request selection, output handlers, body capture, and redaction.

## Key fields

- `enabled`: turn the middleware on or off
- `handlers`: choose `console` and/or `file`
- `file_path`: required when `file` is enabled
- `log_format`: `json` or `text`
- `include_paths` / `exclude_paths`: route filtering
- `exclude_methods`: skip methods such as `OPTIONS`
- `log_request_body` / `log_response_body`: capture payloads
- `max_body_bytes`: cap body capture size
- `redact_headers` / `redact_fields`: sensitive-data masking
- `correlation_id_header`: header used for request correlation

## Path matching

Paths are normalized before matching:

- `api/items` becomes `/api/items`
- trailing slashes are removed, except for the root path

`include_paths` is evaluated first. If the request path does not match any include rule, it is skipped. Then `exclude_paths` is applied.

## Example

```python
from fastapi_inspector import ObserverConfig

config = ObserverConfig(
    handlers=["console", "file"],
    file_path="logs/api.log",
    include_paths=["/api"],
    exclude_paths=["/api/internal"],
    redact_fields={"password", "token"},
)
```
