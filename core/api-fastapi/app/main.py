"""
Infinity Template Library — Core FastAPI Scaffold
Production-grade API with auth, telemetry, health, and structured logging.
"""
from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .errors import register_exception_handlers
from .logging import configure_logging, get_logger
from .routers import auth, health, v1
from .telemetry import init_telemetry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    configure_logging(level=settings.LOG_LEVEL)
    init_telemetry(service_name=settings.SERVICE_NAME, env=settings.ENV)
    logger.info("startup", service=settings.SERVICE_NAME, env=settings.ENV)
    yield
    logger.info("shutdown", service=settings.SERVICE_NAME)


app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.API_VERSION,
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url="/redoc" if settings.ENV != "production" else None,
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next: Any) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()
    response: Response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        elapsed_ms=round(elapsed, 2),
        request_id=request_id,
    )
    return response


# ── Exception Handlers ────────────────────────────────────────────────────────

register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(v1.router, prefix="/api/v1", tags=["v1"])
