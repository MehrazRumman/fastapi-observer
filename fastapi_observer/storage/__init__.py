from __future__ import annotations

import sqlite3
import threading
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol, runtime_checkable

from ..models import LogEvent


@runtime_checkable
class EventStore(Protocol):
    def append(self, event: LogEvent) -> None: ...

    def list_events(self, *, limit: int | None = None) -> list[LogEvent]: ...

    def clear(self) -> None: ...

    def count(self) -> int: ...


def _slice_recent(events: list[LogEvent], limit: int | None) -> list[LogEvent]:
    if limit is None:
        return list(events)
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if limit == 0:
        return []
    return list(events[-limit:])


class InMemoryEventStore:
    def __init__(self, events: Iterable[LogEvent] | None = None) -> None:
        self._events = list(events or [])
        self._lock = threading.RLock()

    def append(self, event: LogEvent) -> None:
        with self._lock:
            self._events.append(event)

    def list_events(self, *, limit: int | None = None) -> list[LogEvent]:
        with self._lock:
            return _slice_recent(self._events, limit)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def count(self) -> int:
        with self._lock:
            return len(self._events)


class JsonLinesEventStore:
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)
        self._lock = threading.RLock()

    def append(self, event: LogEvent) -> None:
        with self._lock:
            with self.file_path.open("a", encoding="utf-8") as handle:
                handle.write(event.model_dump_json())
                handle.write("\n")

    def list_events(self, *, limit: int | None = None) -> list[LogEvent]:
        with self._lock:
            return _slice_recent(self._read_events(), limit)

    def clear(self) -> None:
        with self._lock:
            self.file_path.write_text("", encoding="utf-8")

    def count(self) -> int:
        with self._lock:
            return len(self._read_events())

    def _read_events(self) -> list[LogEvent]:
        if not self.file_path.exists():
            return []
        content = self.file_path.read_text(encoding="utf-8").splitlines()
        events: list[LogEvent] = []
        for line in content:
            if line.strip():
                events.append(LogEvent.model_validate_json(line))
        return events


class JsonFileEventStore(JsonLinesEventStore):
    pass


class SQLiteEventStore:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        # The store is shared between the app thread and request worker threads.
        self._connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
        )
        with self._lock:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT NOT NULL
                )
                """
            )
            self._connection.commit()

    def append(self, event: LogEvent) -> None:
        with self._lock:
            self._ensure_open()
            self._connection.execute(
                "INSERT INTO events (payload) VALUES (?)",
                (event.model_dump_json(),),
            )
            self._connection.commit()

    def list_events(self, *, limit: int | None = None) -> list[LogEvent]:
        with self._lock:
            self._ensure_open()
            if limit is not None and limit < 0:
                raise ValueError("limit must be non-negative")
            if limit == 0:
                return []

            if limit is None:
                cursor = self._connection.execute(
                    "SELECT payload FROM events ORDER BY id ASC"
                )
                rows = cursor.fetchall()
            else:
                cursor = self._connection.execute(
                    "SELECT payload FROM events ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
                rows = list(reversed(cursor.fetchall()))

            return [LogEvent.model_validate_json(row[0]) for row in rows]

    def clear(self) -> None:
        with self._lock:
            self._ensure_open()
            self._connection.execute("DELETE FROM events")
            self._connection.commit()

    def count(self) -> int:
        with self._lock:
            self._ensure_open()
            cursor = self._connection.execute("SELECT COUNT(*) FROM events")
            row = cursor.fetchone()
            return int(row[0] if row is not None else 0)

    def close(self) -> None:
        with self._lock:
            if self._connection is None:
                return
            self._connection.close()
            self._connection = None

    def _ensure_open(self) -> None:
        if self._connection is None:
            raise RuntimeError("SQLiteEventStore is closed")

    def __enter__(self) -> SQLiteEventStore:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def __del__(self) -> None:  # pragma: no cover - best-effort resource cleanup
        try:
            self.close()
        except Exception:
            pass


__all__ = [
    "EventStore",
    "InMemoryEventStore",
    "JsonLinesEventStore",
    "JsonFileEventStore",
    "SQLiteEventStore",
]
