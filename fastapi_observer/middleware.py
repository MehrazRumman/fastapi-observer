from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Iterable
from typing import Any, Callable

from .config import ObserverConfig
from .filters import EventFilter, FilterPipeline
from .logger import build_logger, log_event
from .models import LogEvent
from .storage import EventStore
from .utils import redact_headers, redact_sensitive, status_code_to_level

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
except ModuleNotFoundError as exc:  # pragma: no cover - guarded runtime fallback
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None
if _IMPORT_ERROR is None:

    class ObserverMiddleware(BaseHTTPMiddleware):
        def __init__(
            self,
            app: Any,
            *,
            config: ObserverConfig | None = None,
            logger: logging.Logger | None = None,
            storage: EventStore | None = None,
            event_store: EventStore | None = None,
            event_filters: Iterable[EventFilter] | None = None,
        ) -> None:
            super().__init__(app)
            self.config = config or ObserverConfig()
            self.logger = logger or build_logger(self.config)
            if storage is not None and event_store is not None and storage is not event_store:
                raise ValueError("storage and event_store refer to different objects")
            self.event_store = event_store if event_store is not None else storage
            self.filter_pipeline = FilterPipeline(event_filters)

        async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], Any],
        ) -> Response:
            if not self.config.enabled:
                return await call_next(request)

            path = request.url.path
            method = request.method
            if not self.config.should_log_method(method) or not self.config.should_log_path(path):
                return await call_next(request)

            correlation_id = self._resolve_correlation_id(request)
            request_body_for_log: Any | None = None
            request_for_next = request
            if self.config.log_request_body:
                body = await request.body()
                request_body_for_log = self._format_body_for_log(body)
                request_for_next = Request(request.scope, receive=_build_body_replay_receive(body))

            start = time.perf_counter()
            try:
                response = await call_next(request_for_next)
            except Exception as exc:
                duration_ms = round((time.perf_counter() - start) * 1000, 3)
                self._log_if_allowed(
                    LogEvent(
                        level="ERROR",
                        message="HTTP request failed",
                        method=method,
                        path=path,
                        status_code=500,
                        duration_ms=duration_ms,
                        correlation_id=correlation_id,
                        error=str(exc),
                        metadata=self._build_metadata(
                            request,
                            request_body=request_body_for_log,
                        ),
                    )
                )
                raise

            duration_ms = round((time.perf_counter() - start) * 1000, 3)
            response_body_for_log: Any | None = None
            if self.config.log_response_body:
                response, response_body_for_log = await self._capture_response_for_log(response)

            self._log_if_allowed(
                LogEvent(
                    level=status_code_to_level(response.status_code),
                    message="HTTP request completed",
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    correlation_id=correlation_id,
                    metadata=self._build_metadata(
                        request,
                        request_body=request_body_for_log,
                        response_body=response_body_for_log,
                    ),
                )
            )

            if correlation_id:
                response.headers.setdefault(self.config.correlation_id_header, correlation_id)
            return response

        def _resolve_correlation_id(self, request: Request) -> str | None:
            value = request.headers.get(self.config.correlation_id_header)
            if value:
                request.state.correlation_id = value
                return value
            if self.config.generate_correlation_id:
                generated = str(uuid.uuid4())
                request.state.correlation_id = generated
                return generated
            return None

        def _build_metadata(
            self,
            request: Request,
            *,
            request_body: Any | None = None,
            response_body: Any | None = None,
        ) -> dict[str, Any]:
            metadata: dict[str, Any] = {
                "query_params": dict(request.query_params),
            }
            if request.client:
                metadata["client"] = {
                    "host": request.client.host,
                    "port": request.client.port,
                }
            if self.config.log_headers:
                metadata["headers"] = redact_headers(
                    dict(request.headers),
                    self.config.redact_headers,
                )
            if request_body is not None:
                metadata["request_body"] = request_body
            if response_body is not None:
                metadata["response_body"] = response_body
            return metadata

        def _log_if_allowed(self, event: LogEvent) -> None:
            if self.filter_pipeline.should_log(event):
                log_event(self.logger, self.config, event)
                self._store_event(event)

        def _store_event(self, event: LogEvent) -> None:
            if self.event_store is None:
                return
            try:
                self.event_store.append(event)
            except Exception:
                # Storage is optional; logging should not fail because persistence did.
                pass

        async def _capture_response_for_log(
            self, response: Response
        ) -> tuple[Response, Any | None]:
            body = getattr(response, "body", None)
            if isinstance(body, bytes):
                return response, self._format_body_for_log(body)
            if isinstance(body, str):
                return response, self._format_body_for_log(body.encode("utf-8"))

            body_iterator = getattr(response, "body_iterator", None)
            if body_iterator is None:
                return response, None

            chunks: list[bytes] = []
            async for chunk in body_iterator:
                if isinstance(chunk, bytes):
                    chunks.append(chunk)
                else:
                    chunks.append(str(chunk).encode("utf-8"))
            body_bytes = b"".join(chunks)

            headers = dict(response.headers)
            headers.pop("content-length", None)
            replay_response = Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
                background=response.background,
            )
            return replay_response, self._format_body_for_log(body_bytes)

        def _format_body_for_log(self, body: bytes) -> Any:
            body_size = len(body)
            body_for_parse = body[: self.config.max_body_bytes]
            parsed: Any
            try:
                parsed = json.loads(body_for_parse.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                parsed = body_for_parse.decode("utf-8", errors="replace")

            redacted = redact_sensitive(parsed, self.config.redact_fields)
            if body_size <= self.config.max_body_bytes:
                return redacted
            return {
                "truncated": True,
                "original_size": body_size,
                "content": redacted,
            }


    def _build_body_replay_receive(body: bytes) -> Callable[[], Any]:
        sent = False

        async def receive() -> dict[str, Any]:
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        return receive


else:

    class ObserverMiddleware:  # pragma: no cover - import-time guard only
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError(
                "ObserverMiddleware requires FastAPI/Starlette. "
                "Install optional runtime dependencies first."
            ) from _IMPORT_ERROR


__all__ = ["ObserverMiddleware"]
