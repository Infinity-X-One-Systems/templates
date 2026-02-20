"""Authentication endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from ..auth import (
    TokenPair,
    TokenPayload,
    create_token_pair,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter()

# In-memory user store for scaffold — replace with DB in production
_USERS: dict[str, dict] = {}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest) -> UserResponse:
    if body.email in _USERS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    import uuid
    uid = str(uuid.uuid4())
    _USERS[body.email] = {"id": uid, "email": body.email, "name": body.name, "role": "user", "password_hash": hash_password(body.password)}
    return UserResponse(id=uid, email=body.email, name=body.name, role="user")


@router.post("/login", response_model=TokenPair)
async def login(body: LoginRequest) -> TokenPair:
    user = _USERS.get(body.email)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return create_token_pair(subject=user["id"], role=user["role"])


@router.get("/me", response_model=UserResponse)
async def me(current: TokenPayload = Depends(get_current_user)) -> UserResponse:
    for user in _USERS.values():
        if user["id"] == current.sub:
            return UserResponse(**{k: v for k, v in user.items() if k != "password_hash"})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
