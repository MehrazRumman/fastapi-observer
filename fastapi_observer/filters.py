from __future__ import annotations

from collections.abc import Callable, Iterable

from .models import LogEvent
from .utils import normalize_path

EventFilter = Callable[[LogEvent], bool]


def only_errors(event: LogEvent) -> bool:
    return event.level in {"ERROR", "CRITICAL"}


def min_status_code(min_code: int) -> EventFilter:
    def _filter(event: LogEvent) -> bool:
        if event.status_code is None:
            return False
        return event.status_code >= min_code

    return _filter


def min_duration_ms(min_ms: float) -> EventFilter:
    def _filter(event: LogEvent) -> bool:
        if event.duration_ms is None:
            return False
        return event.duration_ms >= min_ms

    return _filter


def exclude_paths(paths: Iterable[str]) -> EventFilter:
    normalized_paths = {normalize_path(path) for path in paths}

    def _filter(event: LogEvent) -> bool:
        return normalize_path(event.path, allow_blank_root=True) not in normalized_paths

    return _filter


class FilterPipeline:
    def __init__(self, filters: Iterable[EventFilter] | None = None) -> None:
        self._filters: list[EventFilter] = list(filters or [])

    @property
    def filters(self) -> tuple[EventFilter, ...]:
        return tuple(self._filters)

    def add_filter(self, event_filter: EventFilter) -> None:
        self._filters.append(event_filter)

    def should_log(self, event: LogEvent) -> bool:
        for event_filter in self._filters:
            try:
                if not event_filter(event):
                    return False
            except Exception:
                # A bad user filter should never break request handling.
                continue
        return True


__all__ = [
    "EventFilter",
    "FilterPipeline",
    "only_errors",
    "min_status_code",
    "min_duration_ms",
    "exclude_paths",
]
