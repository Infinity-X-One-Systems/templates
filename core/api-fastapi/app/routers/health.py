"""Health check endpoints."""
from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    env: str
    timestamp: str
    python: str


class ReadinessResponse(BaseModel):
    ready: bool
    checks: dict[str, str]


@router.get("", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.SERVICE_NAME,
        version=settings.API_VERSION,
        env=settings.ENV,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        python=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    checks: dict[str, str] = {"api": "ok"}
    ready = all(v == "ok" for v in checks.values())
    return ReadinessResponse(ready=ready, checks=checks)
