"""OpenAI connector using httpx — no openai SDK dependency."""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
from pydantic import BaseModel, Field, SecretStr, model_validator

logger = logging.getLogger(__name__)

_OPENAI_BASE_URL = "https://api.openai.com/v1"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ConnectorError(Exception):
    """Base error for all connector failures."""


class AuthenticationError(ConnectorError):
    """Raised when the API key is rejected."""


class RateLimitError(ConnectorError):
    """Raised when the API rate-limit is hit."""


class APIError(ConnectorError):
    """Raised for any other non-2xx response."""


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class Message(BaseModel):
    role: str
    content: str
    name: str | None = None


class FunctionDefinition(BaseModel):
    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: list[Message]
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: int | None = None
    functions: list[FunctionDefinition] | None = None
    function_call: str | dict[str, str] | None = None
    stream: bool = False


class FunctionCall(BaseModel):
    name: str
    arguments: str


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str | None = None
    function_call: FunctionCall | None = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[Choice]
    usage: Usage


class StreamDelta(BaseModel):
    role: str | None = None
    content: str | None = None
    function_call: FunctionCall | None = None


class StreamChoice(BaseModel):
    index: int
    delta: StreamDelta
    finish_reason: str | None = None


class StreamChunk(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[StreamChoice]


class EmbedRequest(BaseModel):
    model: str = "text-embedding-3-small"
    input: str | list[str]
    dimensions: int | None = None


class EmbedData(BaseModel):
    object: str
    embedding: list[float]
    index: int


class EmbedUsage(BaseModel):
    prompt_tokens: int
    total_tokens: int


class EmbedResponse(BaseModel):
    object: str
    data: list[EmbedData]
    model: str
    usage: EmbedUsage


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


class OpenAIConnector:
    """Async OpenAI connector backed by httpx.

    API key is stored as a :class:`pydantic.SecretStr` and never written to
    logs in plain text.
    """

    def __init__(
        self,
        api_key: str | SecretStr,
        base_url: str = _OPENAI_BASE_URL,
        timeout: float = 60.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key: SecretStr = (
            api_key if isinstance(api_key, SecretStr) else SecretStr(api_key)
        )
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = http_client

        logger.debug("OpenAIConnector initialised (key=****)")

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "OpenAIConnector":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise AuthenticationError(f"Invalid API key (status 401): {response.text}")
        if response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded (status 429): {response.text}")
        if response.status_code >= 400:
            raise APIError(
                f"OpenAI API error (status {response.status_code}): {response.text}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat-completion request and return the full response."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = False

        logger.debug("chat request model=%s messages=%d", request.model, len(request.messages))

        response = await client.post(
            f"{self._base_url}/chat/completions",
            headers=self._headers(),
            json=payload,
        )
        self._raise_for_status(response)
        data = response.json()
        logger.debug("chat response id=%s", data.get("id"))
        return ChatResponse.model_validate(data)

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Stream a chat-completion, yielding :class:`StreamChunk` objects."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = True

        logger.debug(
            "stream_chat request model=%s messages=%d",
            request.model,
            len(request.messages),
        )

        async with client.stream(
            "POST",
            f"{self._base_url}/chat/completions",
            headers=self._headers(),
            json=payload,
        ) as response:
            if response.status_code >= 400:
                await response.aread()
            self._raise_for_status(response)
            async for line in response.aiter_lines():
                line = line.strip()
                if not line or line == "data: [DONE]":
                    continue
                if line.startswith("data: "):
                    raw = line[len("data: "):]
                    try:
                        chunk = StreamChunk.model_validate(json.loads(raw))
                        yield chunk
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Failed to parse stream chunk: %s — %s", raw, exc)

    async def embed(self, request: EmbedRequest) -> EmbedResponse:
        """Request text embeddings."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)

        logger.debug("embed request model=%s", request.model)

        response = await client.post(
            f"{self._base_url}/embeddings",
            headers=self._headers(),
            json=payload,
        )
        self._raise_for_status(response)
        data = response.json()
        return EmbedResponse.model_validate(data)
