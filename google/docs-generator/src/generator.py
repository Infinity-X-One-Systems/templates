"""Google Docs Generator – Template for Google Docs API integration."""

from __future__ import annotations

import json
import os
from typing import Optional

import httpx
from pydantic import BaseModel, Field


class Document(BaseModel):
    doc_id: str
    title: str
    url: str = ""


class ReportTemplate(BaseModel):
    title: str
    sections: list[str] = Field(default_factory=list)
    include_timestamp: bool = True


class CredentialsError(Exception):
    """Raised when Google credentials are missing or invalid."""


class GoogleDocsGenerator:
    """
    Template class for creating and editing Google Docs via the Docs API.

    Credentials are loaded from the environment variable named by *credentials_env*
    (default ``GOOGLE_SERVICE_ACCOUNT_JSON``).

    Pass an *httpx_client* to inject a mock client for testing.
    """

    DOCS_BASE = "https://docs.googleapis.com/v1/documents"
    DRIVE_BASE = "https://www.googleapis.com/drive/v3/files"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPE = (
        "https://www.googleapis.com/auth/documents "
        "https://www.googleapis.com/auth/drive"
    )

    def __init__(
        self,
        credentials_env: str = "GOOGLE_SERVICE_ACCOUNT_JSON",
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._client = httpx_client
        self._service_account = self._load_credentials(credentials_env)

    # ------------------------------------------------------------------
    # Credential loading
    # ------------------------------------------------------------------

    def _load_credentials(self, env_var: str) -> dict:
        env_json = os.environ.get(env_var, "")
        if env_json:
            try:
                return json.loads(env_json)
            except json.JSONDecodeError as exc:
                raise CredentialsError(
                    f"Environment variable {env_var!r} is not valid JSON."
                ) from exc
        raise CredentialsError(
            f"No credentials found. Set the {env_var!r} environment variable."
        )

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient()

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        import time

        import jwt  # type: ignore[import-untyped]

        now = int(time.time())
        payload = {
            "iss": self._service_account["client_email"],
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

    async def create_document(
        self,
        title: str,
        content: str,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> Document:
        """Create a new Google Doc with *title* and initial *content*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        create_resp = await client.post(
            self.DOCS_BASE,
            headers=headers,
            json={"title": title},
        )
        create_resp.raise_for_status()
        doc_data = create_resp.json()
        doc_id = doc_data["documentId"]

        if content:
            await self.append_content(doc_id, content, httpx_client=client)

        url = f"https://docs.google.com/document/d/{doc_id}/edit"
        return Document(doc_id=doc_id, title=title, url=url)

    async def append_content(
        self,
        doc_id: str,
        content: str,
        style: str = "NORMAL_TEXT",
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> bool:
        """Append *content* to the document *doc_id* using the batchUpdate API."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": content + "\n",
                }
            }
        ]

        if style != "NORMAL_TEXT":
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": 1, "endIndex": len(content) + 2},
                        "paragraphStyle": {"namedStyleType": style},
                        "fields": "namedStyleType",
                    }
                }
            )

        resp = await client.post(
            f"{self.DOCS_BASE}/{doc_id}:batchUpdate",
            headers=headers,
            json={"requests": requests},
        )
        resp.raise_for_status()
        return True

    async def export_as_pdf(
        self,
        doc_id: str,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> bytes:
        """Export a Google Doc as a PDF and return the raw bytes."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get(
            f"{self.DRIVE_BASE}/{doc_id}/export",
            headers=headers,
            params={"mimeType": "application/pdf"},
        )
        resp.raise_for_status()
        return resp.content

    async def generate_report(
        self,
        template: ReportTemplate,
        data: dict,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> Document:
        """
        Render a *template* with *data* and create a new Google Doc.

        Each key in *data* whose name matches a section in *template.sections* is
        written as a section body after the section heading.
        """
        import datetime

        client = httpx_client or self._get_client()

        lines: list[str] = []
        if template.include_timestamp:
            ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            lines.append(f"Generated: {ts}\n")

        for section in template.sections:
            lines.append(f"\n{section}\n")
            section_data = data.get(section, "")
            if isinstance(section_data, dict):
                for k, v in section_data.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(str(section_data))

        full_content = "\n".join(lines)
        return await self.create_document(
            template.title, full_content, httpx_client=client
        )
