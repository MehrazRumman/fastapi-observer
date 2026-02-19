import json
import logging

from fastapi_observer.config import ObserverConfig
from fastapi_observer.logger import build_logger, log_event
from fastapi_observer.models import LogEvent


def test_build_logger_console_handler_only():
    config = ObserverConfig(handlers=["console"], log_format="text")
    logger = build_logger(config, logger_name="fastapi_observer.test.console")

    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_build_logger_resets_handlers_between_calls(tmp_path):
    config = ObserverConfig(
        handlers=["console", "file"],
        file_path=str(tmp_path / "api.log"),
    )
    logger_name = "fastapi_observer.test.rebuild"
    first = build_logger(config, logger_name=logger_name)
    second = build_logger(config, logger_name=logger_name)

    assert first is second
    assert len(second.handlers) == 2


def test_log_event_writes_json_payload_to_file(tmp_path):
    file_path = tmp_path / "observer.log"
    config = ObserverConfig(
        handlers=["file"],
        file_path=str(file_path),
        log_format="json",
    )
    logger = build_logger(config, logger_name="fastapi_observer.test.file")

    event = LogEvent(
        level="INFO",
        message="request complete",
        method="get",
        path="api/users",
        status_code=200,
        duration_ms=12.3,
        correlation_id="abc-123",
        metadata={"user_id": 42},
    )
    log_event(logger, config, event)

    lines = file_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["message"] == "request complete"
    assert payload["event"]["service_name"] == "fastapi-app"
    assert payload["event"]["environment"] == "development"
    assert payload["event"]["method"] == "GET"
    assert payload["event"]["path"] == "/api/users"
    assert payload["event"]["status_code"] == 200
    assert payload["event"]["metadata"] == {"user_id": 42}
