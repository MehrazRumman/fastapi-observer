import importlib
from pathlib import Path

from fastapi.testclient import TestClient

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
