import importlib
from pathlib import Path

import pytest

from fastapi_inspector.models import LogEvent
from fastapi_inspector.storage import (
    InMemoryEventStore,
    JsonFileEventStore,
    SQLiteEventStore,
)


def test_storage_package_is_importable():
    module = importlib.import_module("fastapi_inspector.storage")
    assert module.__name__ == "fastapi_inspector.storage"


def test_storage_package_has_init_file():
    module = importlib.import_module("fastapi_inspector.storage")
    module_path = Path(module.__file__)
    assert module_path.name == "__init__.py"


def _event(message: str) -> LogEvent:
    return LogEvent(message=message, method="GET", path="/items")


def test_in_memory_event_store_appends_and_limits():
    store = InMemoryEventStore()
    first = _event("first")
    second = _event("second")

    store.append(first)
    store.append(second)

    assert store.count() == 2
    assert store.list_events() == [first, second]
    assert store.list_events(limit=1) == [second]

    store.clear()
    assert store.count() == 0


def test_in_memory_event_store_rejects_negative_limit():
    store = InMemoryEventStore([_event("first")])

    with pytest.raises(ValueError):
        store.list_events(limit=-1)


def test_json_file_event_store_persists_events(tmp_path):
    store = JsonFileEventStore(tmp_path / "events.jsonl")
    event = _event("stored")

    store.append(event)

    assert store.count() == 1
    assert store.list_events() == [event]
    assert store.list_events(limit=1) == [event]


def test_sqlite_event_store_persists_events(tmp_path):
    event = _event("stored")

    with SQLiteEventStore(tmp_path / "events.db") as store:
        store.append(event)

        assert store.count() == 1
        assert store.list_events() == [event]

        store.clear()
        assert store.count() == 0
