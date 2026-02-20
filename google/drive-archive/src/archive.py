"""Google Drive Archive – Template for Google Drive API integration."""

from __future__ import annotations

import json
import os
from typing import Optional

import httpx
from pydantic import BaseModel, Field


class DriveFile(BaseModel):
    file_id: str
    name: str
    mime_type: str
    web_view_link: str = ""
    parents: list[str] = Field(default_factory=list)


class CredentialsError(Exception):
    """Raised when Google credentials are missing or invalid."""


class GoogleDriveArchive:
    """
    Template class for uploading files and managing folders in Google Drive.

    Credentials are loaded from the environment variable named by *credentials_env*
    (default ``GOOGLE_SERVICE_ACCOUNT_JSON``).

    Pass an *httpx_client* to inject a mock client for testing.
    """

    UPLOAD_BASE = "https://www.googleapis.com/upload/drive/v3/files"
    FILES_BASE = "https://www.googleapis.com/drive/v3/files"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPE = "https://www.googleapis.com/auth/drive"
    FOLDER_MIME = "application/vnd.google-apps.folder"

    def __init__(
        self,
        root_folder_id: str,
        credentials_env: str = "GOOGLE_SERVICE_ACCOUNT_JSON",
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.root_folder_id = root_folder_id
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

    async def upload_file(
        self,
        name: str,
        content: bytes,
        mime_type: str,
        folder_id: Optional[str] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> DriveFile:
        """Upload *content* as a file named *name* to Drive."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        parent = folder_id or self.root_folder_id
        metadata = {
            "name": name,
            "parents": [parent],
        }

        # Multipart upload
        import email.mime.multipart
        import email.mime.base
        import email.mime.application

        boundary = "drive_upload_boundary"
        body = (
            f"--{boundary}\r\n"
            f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{json.dumps(metadata)}\r\n"
            f"--{boundary}\r\n"
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode() + content + f"\r\n--{boundary}--".encode()

        upload_headers = {
            **headers,
            "Content-Type": f"multipart/related; boundary={boundary}",
        }

        resp = await client.post(
            self.UPLOAD_BASE,
            headers=upload_headers,
            params={"uploadType": "multipart", "fields": "id,name,mimeType,webViewLink,parents"},
            content=body,
        )
        resp.raise_for_status()
        data = resp.json()

        return DriveFile(
            file_id=data["id"],
            name=data["name"],
            mime_type=data["mimeType"],
            web_view_link=data.get("webViewLink", ""),
            parents=data.get("parents", []),
        )

    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> DriveFile:
        """Create a Drive folder named *name* under *parent_id*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        parent = parent_id or self.root_folder_id
        metadata = {
            "name": name,
            "mimeType": self.FOLDER_MIME,
            "parents": [parent],
        }

        resp = await client.post(
            self.FILES_BASE,
            headers=headers,
            params={"fields": "id,name,mimeType,webViewLink,parents"},
            json=metadata,
        )
        resp.raise_for_status()
        data = resp.json()

        return DriveFile(
            file_id=data["id"],
            name=data["name"],
            mime_type=data["mimeType"],
            web_view_link=data.get("webViewLink", ""),
            parents=data.get("parents", []),
        )

    async def list_files(
        self,
        folder_id: str,
        query: str = "",
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> list[DriveFile]:
        """List files inside *folder_id*, optionally filtered by *query*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        q = f"'{folder_id}' in parents and trashed=false"
        if query:
            q += f" and {query}"

        resp = await client.get(
            self.FILES_BASE,
            headers=headers,
            params={"q": q, "fields": "files(id,name,mimeType,webViewLink,parents)"},
        )
        resp.raise_for_status()
        files_data = resp.json().get("files", [])

        return [
            DriveFile(
                file_id=f["id"],
                name=f["name"],
                mime_type=f["mimeType"],
                web_view_link=f.get("webViewLink", ""),
                parents=f.get("parents", []),
            )
            for f in files_data
        ]

    async def archive_system_state(
        self,
        state: dict,
        system_name: str,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> DriveFile:
        """Serialize *state* to JSON and upload it to Drive under the root folder."""
        import datetime

        client = httpx_client or self._get_client()
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        file_name = f"{system_name}_state_{ts}.json"
        content = json.dumps(state, indent=2).encode("utf-8")

        return await self.upload_file(
            name=file_name,
            content=content,
            mime_type="application/json",
            folder_id=self.root_folder_id,
            httpx_client=client,
        )
