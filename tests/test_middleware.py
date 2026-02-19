import logging

# import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_observer.config import ObserverConfig
from fastapi_observer.middleware import ObserverMiddleware

class InMemoryHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _build_memory_logger(name: str) -> tuple[logging.Logger, InMemoryHandler]:
    handler = InMemoryHandler()
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    return logger, handler


def test_middleware_logs_completed_request_and_sets_correlation_id():
    app = FastAPI()

    @app.get("/items")
    async def read_items():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.success")
    config = ObserverConfig(log_headers=True)
    app.add_middleware(ObserverMiddleware, config=config, logger=logger)

    client = TestClient(app)
    response = client.get("/items?limit=10")

    assert response.status_code == 200
    assert config.correlation_id_header in response.headers
    assert len(memory.records) == 1

    event = memory.records[0].event
    assert event["message"] == "HTTP request completed"
    assert event["path"] == "/items"
    assert event["status_code"] == 200
    assert event["correlation_id"] == response.headers[config.correlation_id_header]
    assert event["metadata"]["query_params"] == {"limit": "10"}


def test_middleware_skips_excluded_path():
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.exclude")
    config = ObserverConfig()
    app.add_middleware(ObserverMiddleware, config=config, logger=logger)

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert memory.records == []


def test_middleware_logs_request_and_response_body_with_redaction():
    app = FastAPI()

    @app.post("/echo")
    async def echo(payload: dict):
        return payload

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.body")
    config = ObserverConfig(log_request_body=True, log_response_body=True)
    app.add_middleware(ObserverMiddleware, config=config, logger=logger)

    client = TestClient(app)
    response = client.post("/echo", json={"password": "secret", "name": "alice"})

    assert response.status_code == 200
    assert len(memory.records) == 1

    event = memory.records[0].event
    assert event["metadata"]["request_body"]["password"] == "***"
    assert event["metadata"]["response_body"]["password"] == "***"
    assert event["metadata"]["request_body"]["name"] == "alice"


def test_middleware_logs_exceptions():
    app = FastAPI()

    @app.get("/boom")
    async def boom():
        raise RuntimeError("something failed")

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.error")
    config = ObserverConfig()
    app.add_middleware(ObserverMiddleware, config=config, logger=logger)

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    assert len(memory.records) == 1
    event = memory.records[0].event
    assert event["message"] == "HTTP request failed"
    assert event["status_code"] == 500
    assert "something failed" in event["error"]
