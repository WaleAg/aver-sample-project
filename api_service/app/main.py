from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routers import laptime_forecasting, tyre_degradation, yellow_flag

from .core.logging_config import setup_logging
import uuid
import logging
import time

logger = logging.getLogger(__name__)
setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Race Strategy Demo API",
        version="0.1.0",
        description="Demo FastAPI service showcasing validated endpoints, auth, and structured logging."
    )

    # Mount routers
    app.include_router(laptime_forecasting.router, prefix="/v1", tags=["lap-time"])
    app.include_router(tyre_degradation.router, prefix="/v1", tags=["tyre"])
    app.include_router(yellow_flag.router, prefix="/v1", tags=["yellow-flag"])

    @app.get("/healthz")
    def healthz():
        # Basic liveness probe
        return {"ok": True}

    @app.get("/readyz")
    def readyz():
       # Readiness probe (checks dependencies before serving traffic)
        return {"ok": True}

    # Basic error handler to avoid leaking stack traces
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    # Simple latency logging middleware
    @app.middleware("http")
    async def latency_logging(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "latency_ms": round(duration_ms, 2),
            }
        )
        return response

    return app

app = create_app()
