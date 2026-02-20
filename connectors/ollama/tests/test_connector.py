"""Tests for the Ollama connector."""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from src.connector import (
    APIError,
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
    ListModelsResponse,
    Message,
    ModelNotFoundError,
    OllamaConnector,
    PullRequest,
    PullStatus,
)

BASE = "http://localhost:11434"
CREATED = "2024-01-01T00:00:00Z"


def _chat_payload(content: str = "Hi!") -> dict:
    return {
        "model": "llama3",
        "created_at": CREATED,
        "message": {"role": "assistant", "content": content},
        "done": True,
        "total_duration": 1000000,
        "eval_count": 10,
    }


def _generate_payload(response: str = "Sure!") -> dict:
    return {
        "model": "llama3",
        "created_at": CREATED,
        "response": response,
        "done": True,
        "total_duration": 2000000,
        "eval_count": 8,
    }


def _stream_lines(*contents: str) -> bytes:
    lines = []
    for i, c in enumerate(contents):
        done = i == len(contents) - 1
        lines.append(
            json.dumps(
                {
                    "model": "llama3",
                    "created_at": CREATED,
                    "message": {"role": "assistant", "content": c},
                    "done": done,
                }
            )
        )
    return "\n".join(lines).encode()


def _pull_lines(*statuses: dict) -> bytes:
    return "\n".join(json.dumps(s) for s in statuses).encode()


# ---------------------------------------------------------------------------
# chat()
# ---------------------------------------------------------------------------


async def test_chat_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/api/chat").mock(
        return_value=httpx.Response(200, json=_chat_payload("Hello!"))
    )
    connector = OllamaConnector(base_url=BASE)
    req = ChatRequest(model="llama3", messages=[Message(role="user", content="Hi")])
    result = await connector.chat(req)

    assert isinstance(result, ChatResponse)
    assert result.message.content == "Hello!"
    assert result.done is True


async def test_chat_model_not_found(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/api/chat").mock(
        return_value=httpx.Response(404, text="model not found")
    )
    connector = OllamaConnector(base_url=BASE)
    req = ChatRequest(model="unknown", messages=[Message(role="user", content="hi")])
    with pytest.raises(ModelNotFoundError):
        await connector.chat(req)


async def test_chat_api_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/api/chat").mock(
        return_value=httpx.Response(500, text="Internal error")
    )
    connector = OllamaConnector(base_url=BASE)
    req = ChatRequest(model="llama3", messages=[Message(role="user", content="hi")])
    with pytest.raises(APIError):
        await connector.chat(req)


# ---------------------------------------------------------------------------
# generate()
# ---------------------------------------------------------------------------


async def test_generate_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/api/generate").mock(
        return_value=httpx.Response(200, json=_generate_payload("42"))
    )
    connector = OllamaConnector(base_url=BASE)
    req = GenerateRequest(model="llama3", prompt="What is the answer?")
    result = await connector.generate(req)

    assert isinstance(result, GenerateResponse)
    assert result.response == "42"
    assert result.done is True


async def test_generate_model_not_found(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/api/generate").mock(
        return_value=httpx.Response(404, text="model not found")
    )
    connector = OllamaConnector(base_url=BASE)
    req = GenerateRequest(model="ghost", prompt="hello")
    with pytest.raises(ModelNotFoundError):
        await connector.generate(req)


# ---------------------------------------------------------------------------
# list_models()
# ---------------------------------------------------------------------------


async def test_list_models(respx_mock: respx.MockRouter) -> None:
    payload = {
        "models": [
            {
                "name": "llama3",
                "modified_at": CREATED,
                "size": 4000000000,
                "digest": "abc123",
                "details": {
                    "format": "gguf",
                    "family": "llama",
                    "parameter_size": "8B",
                    "quantization_level": "Q4_0",
                },
            }
        ]
    }
    respx_mock.get(f"{BASE}/api/tags").mock(
        return_value=httpx.Response(200, json=payload)
    )
    connector = OllamaConnector(base_url=BASE)
    result = await connector.list_models()

    assert isinstance(result, ListModelsResponse)
    assert len(result.models) == 1
    assert result.models[0].name == "llama3"


# ---------------------------------------------------------------------------
# pull_model() — streaming
# ---------------------------------------------------------------------------


async def test_pull_model_streams_status(respx_mock: respx.MockRouter) -> None:
    lines = _pull_lines(
        {"status": "pulling manifest"},
        {"status": "downloading", "digest": "sha256:abc", "total": 100, "completed": 50},
        {"status": "success"},
    )
    respx_mock.post(f"{BASE}/api/pull").mock(
        return_value=httpx.Response(200, content=lines)
    )
    connector = OllamaConnector(base_url=BASE)
    req = PullRequest(model="llama3")
    statuses: list[PullStatus] = []
    async for status in connector.pull_model(req):
        statuses.append(status)

    assert len(statuses) == 3
    assert statuses[0].status == "pulling manifest"
    assert statuses[1].completed == 50
    assert statuses[2].status == "success"


# ---------------------------------------------------------------------------
# stream_chat()
# ---------------------------------------------------------------------------


async def test_stream_chat(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/api/chat").mock(
        return_value=httpx.Response(200, content=_stream_lines("Hello", " world"))
    )
    connector = OllamaConnector(base_url=BASE)
    req = ChatRequest(
        model="llama3",
        messages=[Message(role="user", content="Hi")],
        stream=True,
    )
    chunks = []
    async for chunk in connector.stream_chat(req):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].message.content == "Hello"
    assert chunks[1].done is True


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


async def test_context_manager(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/api/chat").mock(
        return_value=httpx.Response(200, json=_chat_payload())
    )
    async with OllamaConnector(base_url=BASE) as c:
        req = ChatRequest(model="llama3", messages=[Message(role="user", content="hi")])
        result = await c.chat(req)
    assert result.done is True
