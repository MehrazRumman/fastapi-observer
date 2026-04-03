from fastapi import FastAPI

from fastapi_observer import ObserverConfig, ObserverMiddleware

app = FastAPI(title="FastAPI Observer Example")

app.add_middleware(ObserverMiddleware, config=ObserverConfig())


@app.get("/items")
async def list_items() -> dict[str, list[str]]:
    return {"items": ["alpha", "beta", "gamma"]}
