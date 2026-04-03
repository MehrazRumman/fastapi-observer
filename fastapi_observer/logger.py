from __future__ import annotations

import logging

from .config import ObserverConfig
from .formatters import JsonFormatter
from .formatters.text import TextFormatter
from .handlers import build_handlers
from .models import LogEvent

_LEVEL_TO_INT: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def build_logger(
    config: ObserverConfig, *, logger_name: str = "fastapi_observer"
) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(config.log_level)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        try:
            handler.close()
        except Exception:
            pass
    formatter = _build_formatter(config)
    for handler in build_handlers(config, formatter):
        logger.addHandler(handler)

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
    return TextFormatter()


__all__ = ["build_logger", "log_event", "JsonFormatter"]
