"""Google Sheets Dashboard – Template for Google Sheets API integration."""

from __future__ import annotations

import json
import os
from typing import Optional

import httpx
from pydantic import BaseModel, Field


class ChartData(BaseModel):
    labels: list[str] = Field(default_factory=list)
    series: list[dict] = Field(default_factory=list)


class CredentialsError(Exception):
    """Raised when Google credentials are missing or invalid."""


class GoogleSheetsDashboard:
    """
    Template class for reading and writing metrics to Google Sheets.

    Credentials are loaded from the environment variable named by *credentials_env*
    (default ``GOOGLE_SERVICE_ACCOUNT_JSON``).

    Pass an *httpx_client* to inject a mock client for testing.
    """

    SHEETS_BASE = "https://sheets.googleapis.com/v4/spreadsheets"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPE = "https://www.googleapis.com/auth/spreadsheets"

    def __init__(
        self,
        spreadsheet_id: str,
        credentials_env: str = "GOOGLE_SERVICE_ACCOUNT_JSON",
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.spreadsheet_id = spreadsheet_id
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

    async def write_metrics(
        self,
        sheet_name: str,
        metrics: dict,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> bool:
        """Write *metrics* (dict) as a single row to *sheet_name*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        row = [list(metrics.keys()), list(str(v) for v in metrics.values())]
        range_name = f"{sheet_name}!A1"

        resp = await client.put(
            f"{self.SHEETS_BASE}/{self.spreadsheet_id}/values/{range_name}",
            headers=headers,
            params={"valueInputOption": "RAW"},
            json={"range": range_name, "majorDimension": "ROWS", "values": row},
        )
        resp.raise_for_status()
        return True

    async def read_metrics(
        self,
        sheet_name: str,
        range_notation: str,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> list[list]:
        """Read cell data for *range_notation* from *sheet_name*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        full_range = f"{sheet_name}!{range_notation}"
        resp = await client.get(
            f"{self.SHEETS_BASE}/{self.spreadsheet_id}/values/{full_range}",
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json().get("values", [])

    async def append_row(
        self,
        sheet_name: str,
        row: list,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> bool:
        """Append a single *row* to *sheet_name*."""
        client = httpx_client or self._get_client()
        token = await self._get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        range_name = f"{sheet_name}!A1"
        resp = await client.post(
            f"{self.SHEETS_BASE}/{self.spreadsheet_id}/values/{range_name}:append",
            headers=headers,
            params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
            json={"range": range_name, "majorDimension": "ROWS", "values": [row]},
        )
        resp.raise_for_status()
        return True

    async def create_chart_data(
        self,
        metrics_history: list[dict],
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> ChartData:
        """
        Build chart-ready data from a list of metric snapshot dicts.

        Each dict should share the same keys; the key ``timestamp`` (if present)
        is used as the label.
        """
        if not metrics_history:
            return ChartData()

        labels: list[str] = [
            str(entry.get("timestamp", i)) for i, entry in enumerate(metrics_history)
        ]
        keys = [k for k in metrics_history[0] if k != "timestamp"]
        series = [
            {
                "name": key,
                "data": [entry.get(key) for entry in metrics_history],
            }
            for key in keys
        ]

        return ChartData(labels=labels, series=series)
