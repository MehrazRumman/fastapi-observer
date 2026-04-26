from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypeVar

T = TypeVar("T")


def dedupe_preserve_order(values: Iterable[T]) -> list[T]:
    seen: set[T] = set()
    unique: list[T] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique


def normalize_path(path: object, *, allow_blank_root: bool = False) -> str:
    if path is None:
        if allow_blank_root:
            return "/"
        raise ValueError("path values must be non-empty")

    cleaned = str(path).strip()
    if not cleaned:
        if allow_blank_root:
            return "/"
        raise ValueError("path values must be non-empty")

    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    if len(cleaned) > 1 and cleaned.endswith("/"):
        cleaned = cleaned.rstrip("/")
    return cleaned


def redact_sensitive(value: Any, redact_fields: set[str]) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested_value in value.items():
            if str(key).lower() in redact_fields:
                redacted[key] = "***"
            else:
                redacted[key] = redact_sensitive(nested_value, redact_fields)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item, redact_fields) for item in value]
    return value


def redact_headers(headers: Mapping[str, str], redact_headers: set[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in redact_headers:
            result[key] = "***"
        else:
            result[key] = value
    return result


def status_code_to_level(status_code: int) -> str:
    if status_code >= 500:
        return "ERROR"
    if status_code >= 400:
        return "WARNING"
    return "INFO"


__all__ = [
    "dedupe_preserve_order",
    "normalize_path",
    "redact_sensitive",
    "redact_headers",
    "status_code_to_level",
]
