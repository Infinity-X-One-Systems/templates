"""Tests for the OpenAI connector."""
from __future__ import annotations

import json
import time

import httpx
import pytest
import respx

from src.connector import (
    APIError,
    AuthenticationError,
    ChatRequest,
    ChatResponse,
    EmbedRequest,
    EmbedResponse,
    Message,
    OpenAIConnector,
    RateLimitError,
    StreamChunk,
)

BASE = "https://api.openai.com/v1"
NOW = int(time.time())


def _chat_payload(content: str = "Hello!") -> dict:
    return {
        "id": "chatcmpl-abc",
        "object": "chat.completion",
        "created": NOW,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def _embed_payload() -> dict:
    return {
        "object": "list",
        "data": [{"object": "embedding", "embedding": [0.1, 0.2, 0.3], "index": 0}],
        "model": "text-embedding-3-small",
        "usage": {"prompt_tokens": 4, "total_tokens": 4},
    }


def _sse_lines(*contents: str, finish: bool = True) -> bytes:
    chunks = []
    for content in contents:
        chunk = {
            "id": "chatcmpl-stream",
            "object": "chat.completion.chunk",
            "created": NOW,
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": content},
                    "finish_reason": None,
                }
            ],
        }
        chunks.append(f"data: {json.dumps(chunk)}\n\n")
    if finish:
        chunks.append("data: [DONE]\n\n")
    return "".join(chunks).encode()


# ---------------------------------------------------------------------------
# chat()
# ---------------------------------------------------------------------------


async def test_chat_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/chat/completions").mock(
        return_value=httpx.Response(200, json=_chat_payload("Hi there!"))
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = ChatRequest(
        model="gpt-4o-mini",
        messages=[Message(role="user", content="Hi")],
    )
    result = await connector.chat(req)

    assert isinstance(result, ChatResponse)
    assert result.choices[0].message.content == "Hi there!"
    assert result.usage.total_tokens == 15


async def test_chat_401_raises_authentication_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/chat/completions").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = ChatRequest(messages=[Message(role="user", content="Hi")])
    with pytest.raises(AuthenticationError):
        await connector.chat(req)


async def test_chat_429_raises_rate_limit_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/chat/completions").mock(
        return_value=httpx.Response(429, text="Too Many Requests")
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = ChatRequest(messages=[Message(role="user", content="Hi")])
    with pytest.raises(RateLimitError):
        await connector.chat(req)


async def test_chat_500_raises_api_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/chat/completions").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = ChatRequest(messages=[Message(role="user", content="Hi")])
    with pytest.raises(APIError):
        await connector.chat(req)


# ---------------------------------------------------------------------------
# embed()
# ---------------------------------------------------------------------------


async def test_embed_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/embeddings").mock(
        return_value=httpx.Response(200, json=_embed_payload())
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = EmbedRequest(model="text-embedding-3-small", input="hello world")
    result = await connector.embed(req)

    assert isinstance(result, EmbedResponse)
    assert result.data[0].embedding == [0.1, 0.2, 0.3]


async def test_embed_auth_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/embeddings").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = EmbedRequest(input="hello")
    with pytest.raises(AuthenticationError):
        await connector.embed(req)


# ---------------------------------------------------------------------------
# stream_chat()
# ---------------------------------------------------------------------------


async def test_stream_chat_yields_chunks(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/chat/completions").mock(
        return_value=httpx.Response(200, content=_sse_lines("Hello", " world"))
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = ChatRequest(messages=[Message(role="user", content="Hi")], stream=True)
    chunks: list[StreamChunk] = []
    async for chunk in connector.stream_chat(req):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].choices[0].delta.content == "Hello"
    assert chunks[1].choices[0].delta.content == " world"


async def test_stream_chat_auth_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/chat/completions").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    connector = OpenAIConnector(api_key="sk-test")
    req = ChatRequest(messages=[Message(role="user", content="Hi")])
    with pytest.raises(AuthenticationError):
        async for _ in connector.stream_chat(req):
            pass


# ---------------------------------------------------------------------------
# API key masking
# ---------------------------------------------------------------------------


def test_api_key_not_in_repr() -> None:
    c = OpenAIConnector(api_key="sk-super-secret")
    assert "sk-super-secret" not in repr(c._api_key)


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


async def test_context_manager(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/chat/completions").mock(
        return_value=httpx.Response(200, json=_chat_payload())
    )
    async with OpenAIConnector(api_key="sk-test") as c:
        req = ChatRequest(messages=[Message(role="user", content="Hi")])
        result = await c.chat(req)
    assert result.choices[0].message.role == "assistant"
