"""Tests for the webhook connector."""
from __future__ import annotations

import hashlib
import hmac
import json

import httpx
import pytest
import respx

from src.connector import (
    ConnectorError,
    DeliveryError,
    SendRequest,
    SendResult,
    SignatureError,
    VerifyRequest,
    WebhookConfig,
    WebhookConnector,
    WebhookTarget,
)

SLACK_URL = "https://hooks.slack.com/services/T000/B000/xxxx"
DISCORD_URL = "https://discord.com/api/webhooks/123/abc"
GENERIC_URL = "https://example.com/webhook"


def _make_connector() -> WebhookConnector:
    c = WebhookConnector(max_retries=3, backoff_base=0.0)
    c.register(WebhookConfig(name="slack", url=SLACK_URL, target=WebhookTarget.SLACK))
    c.register(
        WebhookConfig(
            name="slack-signed",
            url=SLACK_URL,
            target=WebhookTarget.SLACK,
            secret="mysecret",
        )
    )
    c.register(
        WebhookConfig(name="discord", url=DISCORD_URL, target=WebhookTarget.DISCORD)
    )
    c.register(
        WebhookConfig(name="generic", url=GENERIC_URL, target=WebhookTarget.GENERIC)
    )
    return c


# ---------------------------------------------------------------------------
# send() — basic
# ---------------------------------------------------------------------------


async def test_send_slack(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(SLACK_URL).mock(return_value=httpx.Response(200, text="ok"))
    connector = _make_connector()

    result = await connector.send(
        SendRequest(webhook_name="slack", payload={"text": "Hello Slack!"})
    )

    assert isinstance(result, SendResult)
    assert result.status_code == 200
    assert result.attempts == 1


async def test_send_discord(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(DISCORD_URL).mock(return_value=httpx.Response(204, text=""))
    connector = _make_connector()

    result = await connector.send(
        SendRequest(webhook_name="discord", payload={"content": "Hello Discord!"})
    )

    assert result.status_code == 204


async def test_send_generic(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(GENERIC_URL).mock(return_value=httpx.Response(200, text="received"))
    connector = _make_connector()

    result = await connector.send(
        SendRequest(webhook_name="generic", payload={"event": "deploy", "env": "prod"})
    )

    assert result.status_code == 200
    assert result.body == "received"


# ---------------------------------------------------------------------------
# send() — auto-wraps bare payload for Slack / Discord
# ---------------------------------------------------------------------------


async def test_send_slack_wraps_bare_payload(respx_mock: respx.MockRouter) -> None:
    captured: list[dict] = []

    def _capture(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content))
        return httpx.Response(200, text="ok")

    respx_mock.post(SLACK_URL).mock(side_effect=_capture)
    connector = _make_connector()

    await connector.send(
        SendRequest(webhook_name="slack", payload={"key": "value"})
    )
    assert "text" in captured[0]


async def test_send_discord_wraps_bare_payload(respx_mock: respx.MockRouter) -> None:
    captured: list[dict] = []

    def _capture(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content))
        return httpx.Response(204, text="")

    respx_mock.post(DISCORD_URL).mock(side_effect=_capture)
    connector = _make_connector()

    await connector.send(
        SendRequest(webhook_name="discord", payload={"key": "value"})
    )
    assert "content" in captured[0]


# ---------------------------------------------------------------------------
# send() — HMAC signature header
# ---------------------------------------------------------------------------


async def test_send_with_signature_header(respx_mock: respx.MockRouter) -> None:
    captured_headers: dict[str, str] = {}

    def _capture(request: httpx.Request) -> httpx.Response:
        captured_headers.update(dict(request.headers))
        return httpx.Response(200, text="ok")

    respx_mock.post(SLACK_URL).mock(side_effect=_capture)
    connector = _make_connector()

    await connector.send(
        SendRequest(webhook_name="slack-signed", payload={"text": "signed"})
    )

    assert "x-hub-signature-256" in captured_headers
    sig = captured_headers["x-hub-signature-256"]
    assert sig.startswith("sha256=")


# ---------------------------------------------------------------------------
# send() — retry on 5xx
# ---------------------------------------------------------------------------


async def test_send_retries_on_5xx(respx_mock: respx.MockRouter) -> None:
    call_count = 0

    def _flaky(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(503, text="unavailable")
        return httpx.Response(200, text="ok")

    respx_mock.post(GENERIC_URL).mock(side_effect=_flaky)
    connector = _make_connector()

    result = await connector.send(
        SendRequest(webhook_name="generic", payload={"event": "test"})
    )

    assert result.status_code == 200
    assert result.attempts == 3
    assert call_count == 3


async def test_send_raises_after_max_retries(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(GENERIC_URL).mock(return_value=httpx.Response(503, text="unavailable"))
    connector = _make_connector()

    with pytest.raises(DeliveryError):
        await connector.send(
            SendRequest(webhook_name="generic", payload={"event": "test"})
        )


# ---------------------------------------------------------------------------
# send() — unknown webhook name
# ---------------------------------------------------------------------------


async def test_send_unknown_name_raises() -> None:
    connector = _make_connector()
    with pytest.raises(ConnectorError, match="No webhook registered"):
        await connector.send(SendRequest(webhook_name="nope", payload={}))


# ---------------------------------------------------------------------------
# verify_signature()
# ---------------------------------------------------------------------------


def _make_signature(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_verify_signature_valid() -> None:
    c = WebhookConnector()
    body = b'{"event":"push"}'
    secret = "s3cr3t"
    sig = _make_signature(body, secret)

    req = VerifyRequest(body=body, signature=sig, secret=secret)
    assert c.verify_signature(req) is True


def test_verify_signature_invalid() -> None:
    c = WebhookConnector()
    body = b'{"event":"push"}'
    req = VerifyRequest(body=body, signature="sha256=badhash", secret="s3cr3t")

    with pytest.raises(SignatureError):
        c.verify_signature(req)


# ---------------------------------------------------------------------------
# register()
# ---------------------------------------------------------------------------


def test_register_and_overwrite() -> None:
    c = WebhookConnector()
    cfg1 = WebhookConfig(name="hook", url="https://a.example.com/webhook")
    cfg2 = WebhookConfig(name="hook", url="https://b.example.com/webhook")
    c.register(cfg1)
    c.register(cfg2)
    assert c._registry["hook"].url == "https://b.example.com/webhook"


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


async def test_context_manager(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(GENERIC_URL).mock(return_value=httpx.Response(200, text="ok"))
    connector = _make_connector()

    async with connector as c:
        result = await c.send(
            SendRequest(webhook_name="generic", payload={"ping": True})
        )
    assert result.status_code == 200
