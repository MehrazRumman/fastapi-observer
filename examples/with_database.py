from fastapi import FastAPI

from fastapi_observer import ObserverConfig, ObserverMiddleware
from fastapi_observer.storage import SQLiteEventStore

app = FastAPI(title="FastAPI Observer Database Example")
store = SQLiteEventStore(":memory:")

app.add_middleware(ObserverMiddleware, config=ObserverConfig(), storage=store)


@app.get("/items")
async def list_items() -> dict[str, list[str]]:
    return {"items": ["persisted", "observed"]}


@app.get("/events")
async def list_events() -> list[dict[str, object]]:
    return [event.model_dump(mode="json") for event in store.list_events(limit=25)]
