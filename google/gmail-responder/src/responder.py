"""Gmail AI Responder - Template for Google Gmail API integration using OAuth2/Service Account."""

from __future__ import annotations

import base64
import json
import os
from typing import Callable, Optional

import httpx
from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    message_id: str
    thread_id: str
    subject: str
    sender: str
    snippet: str
    body: str = ""


class DraftMessage(BaseModel):
    draft_id: str
    message_id: str
    thread_id: str


class SentMessage(BaseModel):
    message_id: str
    thread_id: str
    label_ids: list[str] = Field(default_factory=list)


class CredentialsError(Exception):
    """Raised when Google credentials are missing or invalid."""


class GmailAIResponder:
    """
    Template class for interacting with the Gmail API via Service Account credentials.

    Credentials are loaded from the GOOGLE_SERVICE_ACCOUNT_JSON environment variable
    (JSON string) or from a file path supplied at construction time.

    The httpx_client parameter enables full test-time mocking without real credentials.
    """

    GMAIL_BASE = "https://gmail.googleapis.com/gmail/v1/users"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPE = "https://www.googleapis.com/auth/gmail.modify"

    def __init__(
        self,
        credentials_path: str = "",
        user_email: str = "",
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.user_email = user_email or os.environ.get("GMAIL_USER_EMAIL", "me")
        self._client = httpx_client
        self._service_account = self._load_credentials(credentials_path)

    # ------------------------------------------------------------------
    # Credential loading
    # ------------------------------------------------------------------

    def _load_credentials(self, credentials_path: str) -> dict:
        """Load service-account JSON from env var or file."""
        env_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        if env_json:
            try:
                return json.loads(env_json)
            except json.JSONDecodeError as exc:
                raise CredentialsError(
                    "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON."
                ) from exc

        if credentials_path and os.path.isfile(credentials_path):
            with open(credentials_path, "r", encoding="utf-8") as fh:
                return json.load(fh)

        raise CredentialsError(
            "No credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON env var "
            "or provide a valid credentials_path."
        )

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient()

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        """Exchange service-account credentials for a short-lived access token."""
        import time

        import jwt  # type: ignore[import-untyped]  # PyJWT

        now = int(time.time())
        payload = {
            "iss": self._service_account["client_email"],
            "sub": self.user_email,
            "scope": self.SCOPE,
            "aud": self.TOKEN_URL,
            "iat": now,
            "exp": now + 3600,
        }
        private_key = self._service_account["private_key"]
        assertion = jwt.encode(payload, private_key, algorithm="RS256")

        response = await client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": assertion,
            },
        )
        response.raise_for_status()
        return response.json()["access_token"]

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def list_unread_messages(
        self,
        max_results: int = 10,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> list[EmailMessage]:
        """Return up to *max_results* unread messages from the inbox."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        list_resp = await client.get(
            f"{self.GMAIL_BASE}/{self.user_email}/messages",
            headers=headers,
            params={"q": "is:unread", "maxResults": max_results},
        )
        list_resp.raise_for_status()
        raw_messages = list_resp.json().get("messages", [])

        messages: list[EmailMessage] = []
        for raw in raw_messages:
            msg_resp = await client.get(
                f"{self.GMAIL_BASE}/{self.user_email}/messages/{raw['id']}",
                headers=headers,
                params={"format": "full"},
            )
            msg_resp.raise_for_status()
            messages.append(self._parse_message(msg_resp.json()))

        return messages

    async def draft_reply(
        self,
        message_id: str,
        reply_content: str,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> DraftMessage:
        """Create a draft reply to *message_id* with *reply_content*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        raw_mime = base64.urlsafe_b64encode(
            f"Content-Type: text/plain\r\n\r\n{reply_content}".encode()
        ).decode()

        body = {
            "message": {
                "raw": raw_mime,
                "threadId": message_id,
            }
        }

        resp = await client.post(
            f"{self.GMAIL_BASE}/{self.user_email}/drafts",
            headers=headers,
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()

        return DraftMessage(
            draft_id=data["id"],
            message_id=data["message"]["id"],
            thread_id=data["message"]["threadId"],
        )

    async def send_reply(
        self,
        draft_id: str,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> SentMessage:
        """Send the draft identified by *draft_id*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        resp = await client.post(
            f"{self.GMAIL_BASE}/{self.user_email}/drafts/send",
            headers=headers,
            json={"id": draft_id},
        )
        resp.raise_for_status()
        data = resp.json()

        return SentMessage(
            message_id=data["id"],
            thread_id=data["threadId"],
            label_ids=data.get("labelIds", []),
        )

    async def process_inbox(
        self,
        messages: list[EmailMessage],
        reply_generator_fn: Callable[[EmailMessage], str],
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> list[SentMessage]:
        """
        Batch-process *messages*: generate a reply for each, draft it, then send it.

        *reply_generator_fn* receives an EmailMessage and returns the reply text.
        """
        client = httpx_client or self._get_client()
        sent: list[SentMessage] = []

        for message in messages:
            reply_text = reply_generator_fn(message)
            draft = await self.draft_reply(
                message.message_id, reply_text, httpx_client=client
            )
            result = await self.send_reply(draft.draft_id, httpx_client=client)
            sent.append(result)

        return sent

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_message(data: dict) -> EmailMessage:
        headers = {
            h["name"].lower(): h["value"]
            for h in data.get("payload", {}).get("headers", [])
        }

        body = ""
        payload = data.get("payload", {})
        if payload.get("body", {}).get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode(
                "utf-8", errors="replace"
            )
        else:
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get(
                    "data"
                ):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8", errors="replace"
                    )
                    break

        return EmailMessage(
            message_id=data["id"],
            thread_id=data.get("threadId", ""),
            subject=headers.get("subject", "(no subject)"),
            sender=headers.get("from", ""),
            snippet=data.get("snippet", ""),
            body=body,
        )
