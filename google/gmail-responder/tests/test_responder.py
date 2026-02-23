"""Tests for GmailAIResponder – all Google API calls are mocked with respx."""

from __future__ import annotations

import base64
import json
import os

import pytest
import respx
import httpx

from src.responder import (
    CredentialsError,
    DraftMessage,
    EmailMessage,
    GmailAIResponder,
    SentMessage,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_SA = {
    "type": "service_account",
    "client_email": "test@project.iam.gserviceaccount.com",
    "private_key": "fake-key",
    "private_key_id": "key-id",
    "project_id": "test-project",
    "token_uri": "https://oauth2.googleapis.com/token",
}

FAKE_TOKEN_RESPONSE = {"access_token": "ya29.test_token", "expires_in": 3600}

FAKE_MESSAGE_LIST = {
    "messages": [
        {"id": "msg-001", "threadId": "thread-001"},
        {"id": "msg-002", "threadId": "thread-002"},
    ]
}

FAKE_MESSAGE_DETAIL = {
    "id": "msg-001",
    "threadId": "thread-001",
    "snippet": "Hello world",
    "payload": {
        "headers": [
            {"name": "Subject", "value": "Test Subject"},
            {"name": "From", "value": "sender@example.com"},
        ],
        "body": {
            "data": base64.urlsafe_b64encode(b"Hello body content").decode()
        },
    },
}

FAKE_DRAFT_RESPONSE = {
    "id": "draft-001",
    "message": {"id": "msg-draft-001", "threadId": "thread-001"},
}

FAKE_SEND_RESPONSE = {
    "id": "msg-sent-001",
    "threadId": "thread-001",
    "labelIds": ["SENT"],
}


@pytest.fixture
def sa_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))
    yield


def make_responder(monkeypatch, httpx_client: httpx.AsyncClient) -> GmailAIResponder:
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))
    return GmailAIResponder(
        user_email="me",
        httpx_client=httpx_client,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@respx.mock
@pytest.mark.asyncio
async def test_list_messages_parses_response(monkeypatch):
    """list_unread_messages should parse the Gmail API response into EmailMessage objects."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.post("https://oauth2.googleapis.com/token").mock(
            return_value=httpx.Response(200, json=FAKE_TOKEN_RESPONSE)
        )
        respx.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        ).mock(return_value=httpx.Response(200, json=FAKE_MESSAGE_LIST))

        for msg in FAKE_MESSAGE_LIST["messages"]:
            respx.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}",
            ).mock(return_value=httpx.Response(200, json={**FAKE_MESSAGE_DETAIL, "id": msg["id"], "threadId": msg["threadId"]}))

        # Patch JWT encoding so we don't need a real private key
        import src.responder as responder_module
        monkeypatch.setattr(
            responder_module,
            "__builtins__",
            responder_module.__builtins__,
        )

        responder = GmailAIResponder(user_email="me", httpx_client=client)
        # Patch _get_access_token to skip JWT
        async def fake_token(c):
            return "ya29.test_token"
        responder._get_access_token = fake_token

        messages = await responder.list_unread_messages(max_results=2)

    assert len(messages) == 2
    assert all(isinstance(m, EmailMessage) for m in messages)
    assert messages[0].message_id == "msg-001"
    assert messages[0].subject == "Test Subject"
    assert messages[0].sender == "sender@example.com"
    assert "Hello body content" in messages[0].body


@respx.mock
@pytest.mark.asyncio
async def test_draft_reply_creates_draft(monkeypatch):
    """draft_reply should POST to the drafts endpoint and return a DraftMessage."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
        ).mock(return_value=httpx.Response(201, json=FAKE_DRAFT_RESPONSE))

        responder = GmailAIResponder(user_email="me", httpx_client=client)

        async def fake_token(c):
            return "ya29.test_token"
        responder._get_access_token = fake_token

        draft = await responder.draft_reply("msg-001", "Thank you for your email!")

    assert isinstance(draft, DraftMessage)
    assert draft.draft_id == "draft-001"
    assert draft.message_id == "msg-draft-001"
    assert draft.thread_id == "thread-001"


@respx.mock
@pytest.mark.asyncio
async def test_process_inbox_batch(monkeypatch):
    """process_inbox should draft and send replies for every message."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    messages = [
        EmailMessage(
            message_id=f"msg-00{i}",
            thread_id=f"thread-00{i}",
            subject="Hello",
            sender="user@example.com",
            snippet="snippet",
        )
        for i in range(1, 4)
    ]

    async with httpx.AsyncClient() as client:
        # Mock drafts endpoint for all 3 messages
        for i, msg in enumerate(messages, start=1):
            respx.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
            ).mock(
                return_value=httpx.Response(
                    201,
                    json={
                        "id": f"draft-00{i}",
                        "message": {"id": f"msg-draft-00{i}", "threadId": f"thread-00{i}"},
                    },
                )
            )
            respx.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/drafts/send"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "id": f"msg-sent-00{i}",
                        "threadId": f"thread-00{i}",
                        "labelIds": ["SENT"],
                    },
                )
            )

        responder = GmailAIResponder(user_email="me", httpx_client=client)

        async def fake_token(c):
            return "ya29.test_token"
        responder._get_access_token = fake_token

        sent = await responder.process_inbox(
            messages,
            reply_generator_fn=lambda m: f"Auto-reply to {m.sender}",
        )

    assert len(sent) == 3
    assert all(isinstance(s, SentMessage) for s in sent)
    assert all("SENT" in s.label_ids for s in sent)


def test_missing_credentials_raises(monkeypatch):
    """GmailAIResponder should raise CredentialsError when no credentials are available."""
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)

    with pytest.raises(CredentialsError):
        GmailAIResponder(credentials_path="", user_email="me")
