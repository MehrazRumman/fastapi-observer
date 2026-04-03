from __future__ import annotations

import json
from html import escape
from typing import Any

from ..storage import EventStore, InMemoryEventStore

try:
    from fastapi import FastAPI, Query
    from fastapi.responses import HTMLResponse
except ModuleNotFoundError as exc:  # pragma: no cover - guarded runtime fallback
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def build_dashboard_app(
    store: EventStore | None = None,
    *,
    title: str = "FastAPI Observer Dashboard",
) -> FastAPI:
    if _IMPORT_ERROR is not None:  # pragma: no cover - import-time guard only
        raise RuntimeError(
            "Dashboard helpers require FastAPI. Install the runtime dependency first."
        ) from _IMPORT_ERROR

    event_store = store or InMemoryEventStore()
    app = FastAPI(title=title)
    app.state.event_store = event_store

    @app.get("/", response_class=HTMLResponse)
    async def dashboard_home() -> str:
        return _render_dashboard_page(title, event_store.list_events())

    @app.get("/events")
    async def list_events(limit: int | None = Query(default=None, ge=0)) -> list[dict[str, Any]]:
        return [event.model_dump(mode="json") for event in event_store.list_events(limit=limit)]

    @app.delete("/events")
    async def clear_events() -> dict[str, int]:
        removed = event_store.count()
        event_store.clear()
        return {"cleared": removed}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def create_dashboard_app(
    store: EventStore | None = None,
    *,
    title: str = "FastAPI Observer Dashboard",
) -> FastAPI:
    return build_dashboard_app(store, title=title)


def _render_dashboard_page(title: str, events: list[Any]) -> str:
    total_events = len(events)
    latest = events[-1].timestamp.isoformat() if events else "n/a"
    rows = _render_event_rows(events)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0f172a;
      --panel: rgba(15, 23, 42, 0.82);
      --panel-border: rgba(148, 163, 184, 0.22);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --accent-soft: rgba(56, 189, 248, 0.14);
      --warning: #f59e0b;
      --error: #ef4444;
      --success: #22c55e;
    }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 32%),
        radial-gradient(circle at top right, rgba(236, 72, 153, 0.14), transparent 28%),
        linear-gradient(180deg, #020617 0%, var(--bg) 100%);
      min-height: 100vh;
    }}
    .shell {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px 56px;
    }}
    header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: end;
      gap: 16px;
      margin-bottom: 28px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.4rem);
      line-height: 1;
      letter-spacing: -0.04em;
    }}
    .lede {{
      margin: 10px 0 0;
      color: var(--muted);
      max-width: 52rem;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 0 0 24px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 18px;
      padding: 16px 18px;
      backdrop-filter: blur(14px);
      box-shadow: 0 18px 48px rgba(2, 6, 23, 0.28);
    }}
    .card-label {{
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      margin-bottom: 8px;
    }}
    .card-value {{
      font-size: 1.6rem;
      font-weight: 700;
    }}
    .table-wrap {{
      overflow: auto;
      border-radius: 20px;
      border: 1px solid var(--panel-border);
      background: rgba(2, 6, 23, 0.42);
      box-shadow: 0 18px 48px rgba(2, 6, 23, 0.28);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 960px;
    }}
    thead {{
      background: rgba(15, 23, 42, 0.96);
    }}
    th, td {{
      padding: 14px 16px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.14);
      text-align: left;
      vertical-align: top;
      font-size: 0.95rem;
    }}
    th {{
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }}
    tbody tr:hover {{
      background: rgba(56, 189, 248, 0.05);
    }}
    code {{
      display: inline-block;
      max-width: 100%;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.85rem;
      color: #cbd5e1;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 0.76rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      border: 1px solid transparent;
    }}
    .pill-info {{ background: rgba(56, 189, 248, 0.16); color: #7dd3fc; border-color: rgba(56, 189, 248, 0.28); }}
    .pill-warning {{ background: rgba(245, 158, 11, 0.15); color: #fcd34d; border-color: rgba(245, 158, 11, 0.25); }}
    .pill-error {{ background: rgba(239, 68, 68, 0.14); color: #fca5a5; border-color: rgba(239, 68, 68, 0.25); }}
    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 48px 16px;
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div>
        <h1>{escape(title)}</h1>
        <p class="lede">A lightweight view of the structured request events captured by FastAPI Observer.</p>
      </div>
    </header>
    <section class="stats">
      <div class="card">
        <div class="card-label">Events</div>
        <div class="card-value">{total_events}</div>
      </div>
      <div class="card">
        <div class="card-label">Latest Event</div>
        <div class="card-value">{escape(latest)}</div>
      </div>
    </section>
    <section class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Level</th>
            <th>Method</th>
            <th>Path</th>
            <th>Status</th>
            <th>Message</th>
            <th>Metadata</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>"""


def _render_event_rows(events: list[Any]) -> str:
    if not events:
        return '<tr><td class="empty" colspan="7">No events captured yet.</td></tr>'

    rows: list[str] = []
    for event in reversed(events):
        payload = event.model_dump(mode="json")
        level = str(payload.get("level", "INFO"))
        level_class = "error" if level.lower() == "critical" else level.lower()
        status_code = payload.get("status_code")
        metadata = payload.get("metadata") or {}
        rows.append(
            "<tr>"
            f"<td>{escape(str(payload.get('timestamp', '')))}</td>"
            f"<td><span class=\"pill pill-{escape(level_class)}\">{escape(level)}</span></td>"
            f"<td>{escape(str(payload.get('method', '')))}</td>"
            f"<td><code>{escape(str(payload.get('path', '')))}</code></td>"
            f"<td>{escape('' if status_code is None else str(status_code))}</td>"
            f"<td>{escape(str(payload.get('message', '')))}</td>"
            f"<td><code>{escape(json.dumps(metadata, sort_keys=True, default=str))}</code></td>"
            "</tr>"
        )
    return "".join(rows)


__all__ = ["build_dashboard_app", "create_dashboard_app"]
