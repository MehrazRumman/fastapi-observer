from __future__ import annotations

import json
import logging
from typing import Any


_BASE_RECORD_ATTRS = set(logging.makeLogRecord({}).__dict__.keys())


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


__all__ = ["JsonFormatter"]
