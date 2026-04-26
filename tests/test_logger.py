import json
import logging

from fastapi_inspector.config import ObserverConfig
from fastapi_inspector.formatters import JsonFormatter as PackageJsonFormatter
from fastapi_inspector.formatters.text import TextFormatter
from fastapi_inspector.logger import JsonFormatter, build_logger, log_event
from fastapi_inspector.models import LogEvent


def test_build_logger_console_handler_only():
    config = ObserverConfig(handlers=["console"], log_format="text")
    logger = build_logger(config, logger_name="fastapi_inspector.test.console")

    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_build_logger_resets_handlers_between_calls(tmp_path):
    config = ObserverConfig(
        handlers=["console", "file"],
        file_path=str(tmp_path / "api.log"),
    )
    logger_name = "fastapi_inspector.test.rebuild"
    first = build_logger(config, logger_name=logger_name)
    second = build_logger(config, logger_name=logger_name)

    assert first is second
    assert len(second.handlers) == 2


def test_build_logger_closes_replaced_handlers(tmp_path):
    config = ObserverConfig(
        handlers=["file"],
        file_path=str(tmp_path / "api.log"),
    )
    logger_name = "fastapi_inspector.test.handler_cleanup"
    logger = build_logger(config, logger_name=logger_name)
    first_handler = logger.handlers[0]

    build_logger(config, logger_name=logger_name)

    assert first_handler.stream is None or first_handler.stream.closed


def test_log_event_writes_json_payload_to_file(tmp_path):
    file_path = tmp_path / "observer.log"
    config = ObserverConfig(
        handlers=["file"],
        file_path=str(file_path),
        log_format="json",
    )
    logger = build_logger(config, logger_name="fastapi_inspector.test.file")

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


def test_build_logger_uses_json_formatter_by_default():
    config = ObserverConfig(handlers=["console"])
    logger = build_logger(config, logger_name="fastapi_inspector.test.logger.format")
    assert isinstance(logger.handlers[0].formatter, JsonFormatter)


def test_build_logger_uses_text_formatter_when_requested():
    config = ObserverConfig(handlers=["console"], log_format="text")
    logger = build_logger(config, logger_name="fastapi_inspector.test.logger.text")
    assert isinstance(logger.handlers[0].formatter, TextFormatter)


def test_json_formatter_includes_extra_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.extra_key = "extra-value"
    parsed = json.loads(formatter.format(record))
    assert parsed["message"] == "hello"
    assert parsed["extra_key"] == "extra-value"


def test_json_formatter_is_exported_from_formatters_package():
    assert PackageJsonFormatter is JsonFormatter
