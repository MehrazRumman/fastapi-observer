from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from ..config import ObserverConfig


def build_console_handler(formatter: logging.Formatter) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler


def build_file_handler(
    config: ObserverConfig, formatter: logging.Formatter
) -> RotatingFileHandler:
    if not config.file_path:
        raise ValueError("file_path is required for file handler")
    handler = RotatingFileHandler(
        filename=config.file_path,
        maxBytes=config.file_max_bytes,
        backupCount=config.file_backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    return handler


def build_handlers(
    config: ObserverConfig, formatter: logging.Formatter
) -> list[logging.Handler]:
    handlers: list[logging.Handler] = []
    for handler_name in config.handlers:
        if handler_name == "console":
            handlers.append(build_console_handler(formatter))
        elif handler_name == "file":
            handlers.append(build_file_handler(config, formatter))
    return handlers


__all__ = ["build_console_handler", "build_file_handler", "build_handlers"]
