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
