import importlib
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from fastapi_inspector.dashboard import build_dashboard_app
from fastapi_inspector.models import LogEvent
from fastapi_inspector.storage import InMemoryEventStore


def test_dashboard_package_is_importable():
    module = importlib.import_module("fastapi_inspector.dashboard")
    assert module.__name__ == "fastapi_inspector.dashboard"


def test_dashboard_package_has_init_file():
    module = importlib.import_module("fastapi_inspector.dashboard")
    module_path = Path(module.__file__)
    assert module_path.name == "__init__.py"


def test_dashboard_app_lists_and_clears_events():
    store = InMemoryEventStore()
    event = LogEvent(message="request complete", method="GET", path="/items")
    store.append(event)

    app = build_dashboard_app(store, title="Observer Dashboard")
    client = TestClient(app)

    response = client.get("/events")
    assert response.status_code == 200
    assert response.json()[0]["message"] == "request complete"

    html = client.get("/").text
    assert "Observer Dashboard" in html
    assert "request complete" in html

    cleared = client.delete("/events")
    assert cleared.status_code == 200
    assert cleared.json() == {"cleared": 1}
    assert store.count() == 0


def test_dashboard_page_shows_only_most_recent_events():
    store = InMemoryEventStore()
    for index in range(5):
        store.append(LogEvent(message=f"event-{index}", method="GET", path="/items"))

    app = build_dashboard_app(store, max_page_events=2)
    html = TestClient(app).get("/").text

    assert "event-4" in html
    assert "event-3" in html
    assert "event-2" not in html
    assert '<div class="card-value">5</div>' in html


def test_dashboard_rejects_non_positive_page_limit():
    with pytest.raises(ValueError):
        build_dashboard_app(max_page_events=0)
