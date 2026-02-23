"""Ollama local LLM connector using httpx."""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "http://localhost:11434"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ConnectorError(Exception):
    """Base error for all Ollama connector failures."""


class ModelNotFoundError(ConnectorError):
    """Raised when the requested model is not available."""


class APIError(ConnectorError):
    """Raised for non-2xx responses."""


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = False
    temperature: float | None = None
    options: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    model: str
    created_at: str
    message: Message
    done: bool
    total_duration: int | None = None
    eval_count: int | None = None


class ChatStreamChunk(BaseModel):
    model: str
    created_at: str
    message: Message
    done: bool


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False
    system: str | None = None
    template: str | None = None
    options: dict[str, Any] | None = None


class GenerateResponse(BaseModel):
    model: str
    created_at: str
    response: str
    done: bool
    total_duration: int | None = None
    eval_count: int | None = None


class GenerateStreamChunk(BaseModel):
    model: str
    created_at: str
    response: str
    done: bool


class ModelDetails(BaseModel):
    format: str | None = None
    family: str | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None


class ModelInfo(BaseModel):
    name: str
    modified_at: str | None = None
    size: int | None = None
    digest: str | None = None
    details: ModelDetails | None = None


class ListModelsResponse(BaseModel):
    models: list[ModelInfo]


class PullRequest(BaseModel):
    model: str
    insecure: bool = False
    stream: bool = True


class PullStatus(BaseModel):
    status: str
    digest: str | None = None
    total: int | None = None
    completed: int | None = None


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


class OllamaConnector:
    """Async connector for the Ollama local LLM server."""

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 120.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = http_client

        logger.debug("OllamaConnector initialised base_url=%s", self._base_url)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "OllamaConnector":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 404:
            raise ModelNotFoundError(
                f"Model not found (status 404): {response.text}"
            )
        if response.status_code >= 400:
            raise APIError(
                f"Ollama API error (status {response.status_code}): {response.text}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Non-streaming chat completion."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = False

        logger.debug("chat model=%s messages=%d", request.model, len(request.messages))

        response = await client.post(
            f"{self._base_url}/api/chat",
            json=payload,
        )
        self._raise_for_status(response)
        return ChatResponse.model_validate(response.json())

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[ChatStreamChunk]:
        """Streaming chat — yields :class:`ChatStreamChunk` objects."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = True

        logger.debug(
            "stream_chat model=%s messages=%d", request.model, len(request.messages)
        )

        async with client.stream(
            "POST",
            f"{self._base_url}/api/chat",
            json=payload,
        ) as response:
            if response.status_code >= 400:
                await response.aread()
            self._raise_for_status(response)
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                try:
                    yield ChatStreamChunk.model_validate(json.loads(line))
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse stream chunk: %s — %s", line, exc)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Non-streaming text generation."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = False

        logger.debug("generate model=%s", request.model)

        response = await client.post(
            f"{self._base_url}/api/generate",
            json=payload,
        )
        self._raise_for_status(response)
        return GenerateResponse.model_validate(response.json())

    async def stream_generate(
        self, request: GenerateRequest
    ) -> AsyncIterator[GenerateStreamChunk]:
        """Streaming text generation — yields :class:`GenerateStreamChunk` objects."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = True

        async with client.stream(
            "POST",
            f"{self._base_url}/api/generate",
            json=payload,
        ) as response:
            if response.status_code >= 400:
                await response.aread()
            self._raise_for_status(response)
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                try:
                    yield GenerateStreamChunk.model_validate(json.loads(line))
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse generate chunk: %s — %s", line, exc)

    async def list_models(self) -> ListModelsResponse:
        """Return all locally available models."""
        client = await self._get_client()
        logger.debug("list_models")
        response = await client.get(f"{self._base_url}/api/tags")
        self._raise_for_status(response)
        return ListModelsResponse.model_validate(response.json())

    async def pull_model(self, request: PullRequest) -> AsyncIterator[PullStatus]:
        """Pull a model from the Ollama registry, streaming progress."""
        client = await self._get_client()
        payload = request.model_dump(exclude_none=True)
        payload["stream"] = True

        logger.debug("pull_model model=%s", request.model)

        async with client.stream(
            "POST",
            f"{self._base_url}/api/pull",
            json=payload,
        ) as response:
            if response.status_code >= 400:
                await response.aread()
            self._raise_for_status(response)
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue
                try:
                    yield PullStatus.model_validate(json.loads(line))
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse pull status: %s — %s", line, exc)
