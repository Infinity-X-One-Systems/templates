"""Universal webhook connector with HMAC-SHA256 verification and retry."""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
import time
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field, SecretStr

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ConnectorError(Exception):
    """Base error for all webhook connector failures."""


class SignatureError(ConnectorError):
    """Raised when HMAC signature verification fails."""


class DeliveryError(ConnectorError):
    """Raised when a webhook delivery fails after all retries."""


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class WebhookTarget(str, Enum):
    SLACK = "slack"
    DISCORD = "discord"
    GENERIC = "generic"


class WebhookConfig(BaseModel):
    """Registration descriptor for a named webhook endpoint."""

    name: str
    url: str
    secret: SecretStr | None = None
    target: WebhookTarget = WebhookTarget.GENERIC
    headers: dict[str, str] = Field(default_factory=dict)


class SendRequest(BaseModel):
    """Payload envelope for :meth:`WebhookConnector.send`."""

    webhook_name: str
    payload: dict[str, Any]
    content_type: str = "application/json"


class SendResult(BaseModel):
    status_code: int
    body: str
    attempts: int


class VerifyRequest(BaseModel):
    body: bytes
    signature: str
    secret: str
    algorithm: str = "sha256"


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------

_DEFAULT_MAX_RETRIES = 3
_DEFAULT_BACKOFF_BASE = 1.0
_DEFAULT_TIMEOUT = 15.0


class WebhookConnector:
    """Send webhooks to Slack, Discord, or arbitrary HTTP endpoints.

    Features
    --------
    * HMAC-SHA256 signature generation and verification
    * Exponential back-off retry (configurable)
    * Runtime endpoint registration via :meth:`register`
    * No hardcoded credentials — secrets passed in at construction or per-request
    """

    def __init__(
        self,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        backoff_base: float = _DEFAULT_BACKOFF_BASE,
        timeout: float = _DEFAULT_TIMEOUT,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._timeout = timeout
        self._client = http_client
        self._registry: dict[str, WebhookConfig] = {}

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

    async def __aenter__(self) -> "WebhookConnector":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, config: WebhookConfig) -> None:
        """Register a named webhook endpoint for later use with :meth:`send`."""
        self._registry[config.name] = config
        logger.debug("Registered webhook name=%s target=%s", config.name, config.target)

    def _get_config(self, name: str) -> WebhookConfig:
        try:
            return self._registry[name]
        except KeyError:
            raise ConnectorError(f"No webhook registered with name={name!r}") from None

    # ------------------------------------------------------------------
    # Signature helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sign(body: bytes, secret: str, algorithm: str = "sha256") -> str:
        """Return ``algorithm=<hex-digest>`` signature string."""
        digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return f"{algorithm}={digest}"

    def verify_signature(self, request: VerifyRequest) -> bool:
        """Verify that *request.signature* matches the HMAC of *request.body*.

        Returns ``True`` on success, raises :class:`SignatureError` on mismatch.
        """
        expected = self._sign(request.body, request.secret, request.algorithm)
        if not hmac.compare_digest(expected, request.signature):
            raise SignatureError(
                "Webhook signature verification failed: digest mismatch."
            )
        return True

    # ------------------------------------------------------------------
    # Payload builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_slack_body(payload: dict[str, Any]) -> dict[str, Any]:
        if "text" in payload or "blocks" in payload or "attachments" in payload:
            return payload
        return {"text": str(payload)}

    @staticmethod
    def _build_discord_body(payload: dict[str, Any]) -> dict[str, Any]:
        if "content" in payload or "embeds" in payload:
            return payload
        return {"content": str(payload)}

    def _build_body(
        self, target: WebhookTarget, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if target == WebhookTarget.SLACK:
            return self._build_slack_body(payload)
        if target == WebhookTarget.DISCORD:
            return self._build_discord_body(payload)
        return payload

    # ------------------------------------------------------------------
    # Send with retry
    # ------------------------------------------------------------------

    async def send(self, request: SendRequest) -> SendResult:
        """Deliver a webhook payload to a registered endpoint.

        Retries up to *max_retries* times with exponential back-off on
        transient errors (5xx, network failures).
        """
        config = self._get_config(request.webhook_name)
        client = await self._get_client()
        body = self._build_body(config.target, request.payload)

        headers: dict[str, str] = {
            "Content-Type": request.content_type,
            **config.headers,
        }

        if config.secret is not None:
            import json as _json
            raw = _json.dumps(body, separators=(",", ":")).encode()
            headers["X-Hub-Signature-256"] = self._sign(
                raw, config.secret.get_secret_value()
            )

        last_exc: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                logger.debug(
                    "send webhook name=%s attempt=%d/%d",
                    request.webhook_name,
                    attempt,
                    self._max_retries,
                )
                response = await client.post(
                    config.url,
                    headers=headers,
                    json=body,
                )
                if response.status_code < 500:
                    return SendResult(
                        status_code=response.status_code,
                        body=response.text,
                        attempts=attempt,
                    )
                last_exc = DeliveryError(
                    f"Server error {response.status_code}: {response.text}"
                )
            except httpx.TransportError as exc:
                last_exc = exc
                logger.warning(
                    "Webhook send transport error attempt=%d: %s", attempt, exc
                )

            if attempt < self._max_retries:
                delay = self._backoff_base * (2 ** (attempt - 1))
                logger.debug("Retrying in %.1fs…", delay)
                await asyncio.sleep(delay)

        raise DeliveryError(
            f"Webhook delivery failed after {self._max_retries} attempts: {last_exc}"
        ) from last_exc
