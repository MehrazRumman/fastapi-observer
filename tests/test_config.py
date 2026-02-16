import pytest
from pydantic import ValidationError

from fastapi_observer.config import ObserverConfig


def test_defaults():
    config = ObserverConfig()

    assert config.enabled is True
    assert config.service_name == "fastapi-app"
    assert config.environment == "development"
    assert config.log_level == "INFO"
    assert config.log_format == "json"
    assert config.handlers == ["console"]
    assert config.file_path is None
    assert config.file_max_bytes == 10_485_760
    assert config.file_backup_count == 5
    assert config.include_paths == ["/"]
    assert config.exclude_paths == ["/health", "/metrics"]
    assert config.exclude_methods == ["OPTIONS"]
    assert config.log_request_body is False
    assert config.log_response_body is False
    assert config.max_body_bytes == 4096
    assert config.log_headers is True
    assert config.correlation_id_header == "X-Request-ID"
    assert config.generate_correlation_id is True
    assert config.redact_headers == {"authorization", "cookie", "set-cookie"}
    assert config.redact_fields == {
        "password",
        "token",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
    }


def test_file_handler_requires_file_path():
    with pytest.raises(ValidationError):
        ObserverConfig(handlers=["file"])

    config = ObserverConfig(handlers=["file"], file_path="logs/api.log")
    assert config.file_path == "logs/api.log"


def test_path_normalization_and_deduplication():
    config = ObserverConfig(
        include_paths=["api", "/api", "api/", "/v1"],
        exclude_paths=["health", "/health", "/health/"],
    )

    assert config.include_paths == ["/api", "/v1"]
    assert config.exclude_paths == ["/health"]


def test_method_normalization_and_deduplication():
    config = ObserverConfig(exclude_methods=["get", "POST", "get"])
    assert config.exclude_methods == ["GET", "POST"]


def test_redaction_sets_are_lowercased():
    config = ObserverConfig(
        redact_headers={"Authorization", "COOKIE"},
        redact_fields={"Password", "API_KEY", "api_key"},
    )

    assert config.redact_headers == {"authorization", "cookie"}
    assert config.redact_fields == {"password", "api_key"}


def test_should_log_path_include_then_exclude_precedence():
    config = ObserverConfig(
        include_paths=["/api"],
        exclude_paths=["/api/internal"],
    )

    assert config.should_log_path("/api/users") is True
    assert config.should_log_path("/api/internal") is False
    assert config.should_log_path("/api/internal/status") is False
    assert config.should_log_path("/metrics") is False


def test_should_log_method():
    config = ObserverConfig(exclude_methods=["OPTIONS", "HEAD"])

    assert config.should_log_method("GET") is True
    assert config.should_log_method("options") is False
    assert config.should_log_method("HEAD") is False


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("file_max_bytes", 0),
        ("file_max_bytes", -1),
        ("file_backup_count", 0),
        ("file_backup_count", -1),
        ("max_body_bytes", 0),
        ("max_body_bytes", -1),
    ],
)
def test_numeric_fields_must_be_positive(field_name: str, value: int):
    with pytest.raises(ValidationError):
        ObserverConfig(**{field_name: value})


def test_handlers_must_be_unique_and_non_empty():
    with pytest.raises(ValidationError):
        ObserverConfig(handlers=[])
    with pytest.raises(ValidationError):
        ObserverConfig(handlers=["console", "console"])
