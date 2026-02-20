"""API v1 router — extend with domain-specific sub-routers."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..auth import TokenPayload, get_current_user

router = APIRouter()


class PingResponse(BaseModel):
    pong: bool
    user_id: str


@router.get("/ping", response_model=PingResponse)
async def ping(current: TokenPayload = Depends(get_current_user)) -> PingResponse:
    return PingResponse(pong=True, user_id=current.sub)
