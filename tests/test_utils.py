from fastapi_inspector.utils import (
    dedupe_preserve_order,
    normalize_path,
    redact_headers,
    redact_sensitive,
    status_code_to_level,
)


def test_normalize_path_handles_common_forms():
    assert normalize_path("api/items") == "/api/items"
    assert normalize_path("/api/items/") == "/api/items"
    assert normalize_path("", allow_blank_root=True) == "/"


def test_dedupe_preserve_order_keeps_first_occurrence():
    assert dedupe_preserve_order(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]


def test_redaction_helpers():
    assert redact_headers(
        {"Authorization": "secret", "X-Request-ID": "abc"},
        {"authorization"},
    ) == {"Authorization": "***", "X-Request-ID": "abc"}

    assert redact_sensitive(
        {"password": "secret", "nested": {"token": "abc"}, "items": ["ok"]},
        {"password", "token"},
    ) == {"password": "***", "nested": {"token": "***"}, "items": ["ok"]}


def test_status_code_to_level():
    assert status_code_to_level(200) == "INFO"
    assert status_code_to_level(404) == "WARNING"
    assert status_code_to_level(503) == "ERROR"
