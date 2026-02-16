from __future__ import annotations

from typing import Iterable, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

HandlerName = Literal["console", "file"]
LogFormat = Literal["text", "json"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique


class ObserverConfig(BaseModel):
    enabled: bool = True
    service_name: str = "fastapi-app"
    environment: str = "development"

    log_level: LogLevel = "INFO"
    log_format: LogFormat = "json"
    handlers: list[HandlerName] = Field(default_factory=lambda: ["console"])

    file_path: str | None = None
    file_max_bytes: int = Field(default=10_485_760, gt=0)
    file_backup_count: int = Field(default=5, gt=0)

    include_paths: list[str] = Field(default_factory=lambda: ["/"])
    exclude_paths: list[str] = Field(default_factory=lambda: ["/health", "/metrics"])
    exclude_methods: list[str] = Field(default_factory=lambda: ["OPTIONS"])

    log_request_body: bool = False
    log_response_body: bool = False
    max_body_bytes: int = Field(default=4096, gt=0)

    log_headers: bool = True
    correlation_id_header: str = "X-Request-ID"
    generate_correlation_id: bool = True

    redact_headers: set[str] = Field(
        default_factory=lambda: {"authorization", "cookie", "set-cookie"}
    )
    redact_fields: set[str] = Field(
        default_factory=lambda: {
            "password",
            "token",
            "secret",
            "api_key",
            "access_token",
            "refresh_token",
        }
    )

    model_config = {"str_strip_whitespace": True}

    @field_validator("handlers")
    @classmethod
    def _validate_handlers(cls, value: list[HandlerName]) -> list[HandlerName]:
        if not value:
            raise ValueError("handlers must be non-empty")
        if len(value) != len(set(value)):
            raise ValueError("handlers must be unique")
        return value

    @field_validator("file_path")
    @classmethod
    def _validate_file_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("file_path cannot be blank")
        return cleaned

    @field_validator("include_paths", "exclude_paths", mode="before")
    @classmethod
    def _normalize_paths(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            items = [value]
        else:
            items = list(value)

        normalized = [cls._normalize_single_path(item) for item in items]
        return _dedupe_preserve_order(normalized)

    @field_validator("exclude_methods", mode="before")
    @classmethod
    def _normalize_methods(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            items = [value]
        else:
            items = list(value)

        normalized: list[str] = []
        for item in items:
            method = str(item).strip().upper()
            if not method:
                raise ValueError("exclude_methods cannot contain blank values")
            normalized.append(method)
        return _dedupe_preserve_order(normalized)

    @field_validator("redact_headers", "redact_fields", mode="before")
    @classmethod
    def _normalize_redaction_sets(cls, value: object) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            items = [value]
        else:
            items = list(value)

        normalized: set[str] = set()
        for item in items:
            cleaned = str(item).strip().lower()
            if cleaned:
                normalized.add(cleaned)
        return normalized

    @field_validator("correlation_id_header")
    @classmethod
    def _validate_correlation_id_header(cls, value: str) -> str:
        if not value:
            raise ValueError("correlation_id_header must be non-empty")
        return value

    @model_validator(mode="after")
    def _validate_handler_combinations(self) -> "ObserverConfig":
        if "file" in self.handlers and not self.file_path:
            raise ValueError("file_path is required when 'file' handler is configured")
        return self

    def should_log_path(self, path: str) -> bool:
        normalized_path = "/" if not path else self._normalize_single_path(path)

        include_match = any(
            self._path_matches(normalized_path, include_path)
            for include_path in self.include_paths
        )
        if not include_match:
            return False

        exclude_match = any(
            self._path_matches(normalized_path, exclude_path)
            for exclude_path in self.exclude_paths
        )
        return not exclude_match

    def should_log_method(self, method: str) -> bool:
        normalized_method = method.strip().upper()
        return normalized_method not in self.exclude_methods

    @staticmethod
    def _normalize_single_path(path: object) -> str:
        normalized = str(path).strip()
        if not normalized:
            raise ValueError("path values must be non-empty")
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        if len(normalized) > 1 and normalized.endswith("/"):
            normalized = normalized.rstrip("/")
        return normalized

    @staticmethod
    def _path_matches(path: str, pattern: str) -> bool:
        if pattern == "/":
            return True
        return path == pattern or path.startswith(f"{pattern}/")


__all__ = ["ObserverConfig", "HandlerName", "LogFormat", "LogLevel"]
