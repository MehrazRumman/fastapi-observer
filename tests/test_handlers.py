import logging
from logging.handlers import RotatingFileHandler

import pytest

from fastapi_inspector.config import ObserverConfig
from fastapi_inspector.handlers import (
    build_console_handler,
    build_file_handler,
    build_handlers,
)


def test_build_console_handler():
    formatter = logging.Formatter("%(message)s")
    handler = build_console_handler(formatter)
    assert isinstance(handler, logging.StreamHandler)
    assert handler.formatter is formatter


def test_build_file_handler(tmp_path):
    formatter = logging.Formatter("%(message)s")
    log_path = tmp_path / "api.log"
    config = ObserverConfig(handlers=["file"], file_path=str(log_path))
    handler = build_file_handler(config, formatter)

    assert isinstance(handler, RotatingFileHandler)
    assert handler.baseFilename == str(log_path)
    assert handler.maxBytes == config.file_max_bytes
    assert handler.backupCount == config.file_backup_count
    assert handler.formatter is formatter


def test_build_file_handler_requires_path():
    formatter = logging.Formatter("%(message)s")
    config = ObserverConfig()
    with pytest.raises(ValueError):
        build_file_handler(config, formatter)


def test_build_handlers_preserves_config_order(tmp_path):
    formatter = logging.Formatter("%(message)s")
    config = ObserverConfig(handlers=["file", "console"], file_path=str(tmp_path / "api.log"))
    handlers = build_handlers(config, formatter)

    assert len(handlers) == 2
    assert isinstance(handlers[0], RotatingFileHandler)
    assert isinstance(handlers[1], logging.StreamHandler)


def test_build_handlers_console_only():
    formatter = logging.Formatter("%(message)s")
    config = ObserverConfig(handlers=["console"])
    handlers = build_handlers(config, formatter)
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)


def test_build_handlers_file_only(tmp_path):
    formatter = logging.Formatter("%(message)s")
    config = ObserverConfig(handlers=["file"], file_path=str(tmp_path / "api.log"))
    handlers = build_handlers(config, formatter)
    assert len(handlers) == 1
    assert isinstance(handlers[0], RotatingFileHandler)
