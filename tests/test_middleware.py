import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from fastapi_observer.config import ObserverConfig
from fastapi_observer.filters import only_errors
from fastapi_observer.middleware import ObserverMiddleware
from fastapi_observer.storage import InMemoryEventStore, SQLiteEventStore


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


def test_middleware_applies_custom_event_filters():
    app = FastAPI()

    @app.get("/ok")
    async def ok():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.filter")
    config = ObserverConfig()
    app.add_middleware(
        ObserverMiddleware,
        config=config,
        logger=logger,
        event_filters=[only_errors],
    )

    client = TestClient(app)
    response = client.get("/ok")

    assert response.status_code == 200
    assert memory.records == []


def test_middleware_disabled_does_not_log():
    app = FastAPI()

    @app.get("/items")
    async def items():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.disabled")
    config = ObserverConfig(enabled=False)
    app.add_middleware(ObserverMiddleware, config=config, logger=logger)

    client = TestClient(app)
    response = client.get("/items")

    assert response.status_code == 200
    assert memory.records == []


def test_middleware_uses_existing_correlation_id_header():
    app = FastAPI()

    @app.get("/items")
    async def items():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.correlation")
    config = ObserverConfig()
    app.add_middleware(ObserverMiddleware, config=config, logger=logger)

    client = TestClient(app)
    response = client.get("/items", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"
    assert memory.records[0].event["correlation_id"] == "req-123"


def test_middleware_does_not_log_headers_when_disabled():
    app = FastAPI()

    @app.get("/items")
    async def items():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.noheaders")
    config = ObserverConfig(log_headers=False)
    app.add_middleware(ObserverMiddleware, config=config, logger=logger)

    client = TestClient(app)
    response = client.get("/items")

    assert response.status_code == 200
    event = memory.records[0].event
    assert "headers" not in event["metadata"]


def test_middleware_stores_logged_events_when_storage_is_provided():
    app = FastAPI()

    @app.get("/items")
    async def items():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.store")
    store = InMemoryEventStore()
    config = ObserverConfig()
    app.add_middleware(ObserverMiddleware, config=config, logger=logger, storage=store)

    client = TestClient(app)
    response = client.get("/items")

    assert response.status_code == 200
    assert len(memory.records) == 1
    assert store.count() == 1
    assert store.list_events()[0].path == "/items"


def test_middleware_stores_logged_events_in_sqlite_storage(tmp_path):
    app = FastAPI()

    @app.get("/items")
    async def items():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.sqlite")
    store = SQLiteEventStore(tmp_path / "events.db")
    config = ObserverConfig()
    app.add_middleware(ObserverMiddleware, config=config, logger=logger, storage=store)

    client = TestClient(app)
    response = client.get("/items")

    assert response.status_code == 200
    assert len(memory.records) == 1
    assert store.count() == 1
    assert store.list_events()[0].path == "/items"

    store.close()


def test_middleware_accepts_event_store_alias(tmp_path):
    app = FastAPI()

    @app.get("/items")
    async def items():
        return {"ok": True}

    logger, memory = _build_memory_logger("fastapi_observer.test.middleware.alias")
    store = SQLiteEventStore(tmp_path / "alias.db")
    config = ObserverConfig()
    app.add_middleware(
        ObserverMiddleware,
        config=config,
        logger=logger,
        event_store=store,
    )

    client = TestClient(app)
    response = client.get("/items")

    assert response.status_code == 200
    assert len(memory.records) == 1
    assert store.count() == 1

    store.close()


def test_middleware_rejects_conflicting_storage_aliases(tmp_path):
    app = FastAPI()

    @app.get("/items")
    async def items():
        return {"ok": True}

    store_a = SQLiteEventStore(tmp_path / "a.db")
    store_b = SQLiteEventStore(tmp_path / "b.db")

    app.add_middleware(
        ObserverMiddleware,
        config=ObserverConfig(),
        storage=store_a,
        event_store=store_b,
    )

    with pytest.raises(ValueError, match="storage and event_store"):
        TestClient(app).get("/items")

    store_a.close()
    store_b.close()
