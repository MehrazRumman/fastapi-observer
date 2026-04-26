from fastapi_inspector.filters import (
    FilterPipeline,
    exclude_paths,
    min_duration_ms,
    min_status_code,
    only_errors,
)
from fastapi_inspector.models import LogEvent


def test_only_errors_filter():
    success = LogEvent(message="ok", method="GET", path="/items", level="INFO")
    failure = LogEvent(message="boom", method="GET", path="/items", level="ERROR")

    assert only_errors(success) is False
    assert only_errors(failure) is True


def test_min_status_code_filter():
    filter_fn = min_status_code(500)
    assert filter_fn(LogEvent(message="ok", method="GET", path="/x", status_code=200)) is False
    assert filter_fn(LogEvent(message="bad", method="GET", path="/x", status_code=503)) is True


def test_min_duration_filter():
    filter_fn = min_duration_ms(100.0)
    assert filter_fn(LogEvent(message="fast", method="GET", path="/x", duration_ms=12.3)) is False
    assert filter_fn(LogEvent(message="slow", method="GET", path="/x", duration_ms=250.0)) is True


def test_exclude_paths_filter():
    filter_fn = exclude_paths(["/health", "metrics"])
    assert filter_fn(LogEvent(message="ok", method="GET", path="/health")) is False
    assert filter_fn(LogEvent(message="ok", method="GET", path="/metrics")) is False
    assert filter_fn(LogEvent(message="ok", method="GET", path="/api/items")) is True


def test_pipeline_applies_all_filters():
    pipeline = FilterPipeline([only_errors, min_status_code(500)])
    allowed = LogEvent(message="err", method="GET", path="/x", level="ERROR", status_code=500)
    denied = LogEvent(message="warn", method="GET", path="/x", level="WARNING", status_code=500)

    assert pipeline.should_log(allowed) is True
    assert pipeline.should_log(denied) is False


def test_pipeline_ignores_filter_exceptions():
    def exploding_filter(_event: LogEvent) -> bool:
        raise RuntimeError("broken filter")

    pipeline = FilterPipeline([exploding_filter])
    event = LogEvent(message="ok", method="GET", path="/x")
    assert pipeline.should_log(event) is True


def test_pipeline_add_filter():
    pipeline = FilterPipeline()
    pipeline.add_filter(only_errors)
    denied = LogEvent(message="ok", method="GET", path="/x", level="INFO")
    assert pipeline.should_log(denied) is False


def test_exclude_paths_normalizes_trailing_slash():
    filter_fn = exclude_paths(["/health/"])
    assert filter_fn(LogEvent(message="ok", method="GET", path="/health")) is False


def test_pipeline_continues_after_error_and_applies_next_filter():
    def exploding_filter(_event: LogEvent) -> bool:
        raise RuntimeError("boom")

    pipeline = FilterPipeline([exploding_filter, min_status_code(400)])
    event = LogEvent(message="ok", method="GET", path="/x", status_code=200)
    assert pipeline.should_log(event) is False
