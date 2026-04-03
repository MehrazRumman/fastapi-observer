from fastapi import FastAPI

from fastapi_observer import (
    ObserverConfig,
    ObserverMiddleware,
    build_dashboard_app,
)
from fastapi_observer.storage import InMemoryEventStore

app = FastAPI(title="FastAPI Observer Dashboard Example")
store = InMemoryEventStore()

app.add_middleware(ObserverMiddleware, config=ObserverConfig(), storage=store)
app.mount("/dashboard", build_dashboard_app(store, title="Observer Dashboard"))


@app.get("/items")
async def list_items() -> dict[str, list[str]]:
    return {"items": ["alpha", "beta"]}
