# Quickstart

Add the middleware to a FastAPI app and choose the logging behavior through `ObserverConfig`.

```python
from fastapi import FastAPI
from fastapi_observer import ObserverConfig, ObserverMiddleware

app = FastAPI()

config = ObserverConfig(
    log_request_body=True,
    log_response_body=True,
    exclude_paths=["/health", "/metrics"],
)

app.add_middleware(ObserverMiddleware, config=config)
```

## What gets captured

- Request method and path
- Status code and duration
- Correlation ID
- Headers and metadata
- Optional request and response bodies

## Minimal example

```python
from fastapi import FastAPI
from fastapi_observer import ObserverConfig, ObserverMiddleware

app = FastAPI()
app.add_middleware(ObserverMiddleware, config=ObserverConfig())
```
