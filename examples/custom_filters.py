from fastapi import FastAPI

from fastapi_inspector import ObserverConfig, ObserverMiddleware, min_duration_ms, only_errors

app = FastAPI()

config = ObserverConfig(
    handlers=["console"],
    log_format="json",
)

app.add_middleware(
    ObserverMiddleware,
    config=config,
    event_filters=[
        only_errors,
        min_duration_ms(50.0),
    ],
)


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}
