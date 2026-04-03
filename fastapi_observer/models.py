from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .config import LogLevel


class LogEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: LogLevel = "INFO"
    message: str
    method: str
    path: str
    status_code: int | None = None
    duration_ms: float | None = None
    correlation_id: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"str_strip_whitespace": True}

    @field_validator("method")
    @classmethod
    def _normalize_method(cls, value: str) -> str:
        method = value.upper()
        if not method:
            raise ValueError("method must be non-empty")
        return method

    @field_validator("path")
    @classmethod
    def _normalize_path(cls, value: str) -> str:
        if not value:
            raise ValueError("path must be non-empty")
        path = value if value.startswith("/") else f"/{value}"
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")
        return path

    @field_validator("duration_ms")
    @classmethod
    def _validate_duration(cls, value: float | None) -> float | None:
        if value is not None and value < 0:
            raise ValueError("duration_ms must be non-negative")
        return value

    def to_payload(self, *, service_name: str, environment: str) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "service_name": service_name,
            "environment": environment,
            "level": self.level,
            "message": self.message,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "correlation_id": self.correlation_id,
            "error": self.error,
            "metadata": self.metadata,
        }


__all__ = ["LogEvent"]
