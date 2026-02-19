from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Any

from .config import ObserverConfig
from .models import LogEvent

_BASE_RECORD_ATTRS = set(logging.makeLogRecord({}).__dict__.keys())
_LEVEL_TO_INT: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _BASE_RECORD_ATTRS and key != "message":
                payload[key] = value
        return json.dumps(payload, default=str)


def build_logger(
    config: ObserverConfig, *, logger_name: str = "fastapi_observer"
) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(config.log_level)
    logger.propagate = False

    logger.handlers.clear()
    formatter = _build_formatter(config)

    if "console" in config.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if "file" in config.handlers:
        file_handler = RotatingFileHandler(
            filename=config.file_path,
            maxBytes=config.file_max_bytes,
            backupCount=config.file_backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_event(logger: logging.Logger, config: ObserverConfig, event: LogEvent) -> None:
    level = _LEVEL_TO_INT.get(event.level, logging.INFO)
    payload = event.to_payload(
        service_name=config.service_name,
        environment=config.environment,
    )
    logger.log(level, event.message, extra={"event": payload})


def _build_formatter(config: ObserverConfig) -> logging.Formatter:
    if config.log_format == "json":
        return JsonFormatter()
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


__all__ = ["build_logger", "log_event", "JsonFormatter"]
