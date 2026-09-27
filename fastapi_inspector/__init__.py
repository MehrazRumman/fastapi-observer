from importlib.metadata import PackageNotFoundError, version as _pkg_version

from .config import ObserverConfig
from .dashboard import build_dashboard_app, create_dashboard_app
from .filters import (
    FilterPipeline,
    exclude_paths,
    min_duration_ms,
    min_status_code,
    only_errors,
)
from .formatters import JsonFormatter
from .logger import build_logger, log_event
from .middleware import ObserverMiddleware
from .models import LogEvent
from .storage import (
    EventStore,
    InMemoryEventStore,
    JsonFileEventStore,
    JsonLinesEventStore,
    SQLiteEventStore,
)

try:
    __version__ = _pkg_version("fastapi-inspector")
except PackageNotFoundError:  # pragma: no cover - source checkout without install
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "ObserverConfig",
    "ObserverMiddleware",
    "LogEvent",
    "JsonFormatter",
    "FilterPipeline",
    "only_errors",
    "min_status_code",
    "min_duration_ms",
    "exclude_paths",
    "EventStore",
    "InMemoryEventStore",
    "JsonLinesEventStore",
    "JsonFileEventStore",
    "SQLiteEventStore",
    "build_dashboard_app",
    "create_dashboard_app",
    "build_logger",
    "log_event",
]
