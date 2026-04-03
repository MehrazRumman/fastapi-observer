import pytest
from pydantic import ValidationError

from fastapi_observer.models import LogEvent


def test_log_event_normalizes_method_and_path():
    event = LogEvent(message="ok", method="post", path="v1/items")
    assert event.method == "POST"
    assert event.path == "/v1/items"


def test_log_event_rejects_negative_duration():
    with pytest.raises(ValidationError):
        LogEvent(message="bad", method="GET", path="/x", duration_ms=-1)


def test_log_event_trims_trailing_slash_in_path():
    event = LogEvent(message="ok", method="GET", path="/items/")
    assert event.path == "/items"


def test_to_payload_includes_service_and_environment():
    event = LogEvent(message="done", method="GET", path="/items", status_code=200)
    payload = event.to_payload(service_name="svc-a", environment="prod")
    assert payload["service_name"] == "svc-a"
    assert payload["environment"] == "prod"
    assert payload["status_code"] == 200
