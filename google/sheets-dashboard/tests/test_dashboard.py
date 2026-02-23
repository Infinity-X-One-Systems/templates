"""Tests for GoogleSheetsDashboard – all Google API calls are mocked with respx."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from src.dashboard import ChartData, CredentialsError, GoogleSheetsDashboard

# ---------------------------------------------------------------------------
# Fixtures / constants
# ---------------------------------------------------------------------------

FAKE_SA = {
    "type": "service_account",
    "client_email": "sheets-sa@project.iam.gserviceaccount.com",
    "private_key": "fake-key",
}

SPREADSHEET_ID = "spreadsheet-abc123"
TOKEN_RESPONSE = {"access_token": "ya29.sheets_token", "expires_in": 3600}

BASE = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}"


async def fake_token(self, client):  # noqa: D401
    return "ya29.sheets_token"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_write_metrics_sends_put(monkeypatch):
    """write_metrics should PUT values to the Sheets API and return True."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.put(f"{BASE}/values/Metrics%21A1").mock(
            return_value=httpx.Response(200, json={"updatedCells": 4})
        )

        dashboard = GoogleSheetsDashboard(SPREADSHEET_ID, httpx_client=client)
        dashboard._get_access_token = lambda c: _fake_token()

        result = await dashboard.write_metrics(
            "Metrics", {"cpu": 42, "memory": 88, "latency_ms": 120}
        )

    assert result is True


@respx.mock
@pytest.mark.asyncio
async def test_read_metrics_returns_values(monkeypatch):
    """read_metrics should GET and return the nested values list."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    expected_values = [["cpu", "memory"], ["42", "88"]]

    async with httpx.AsyncClient() as client:
        respx.get(f"{BASE}/values/Metrics%21A1%3AB10").mock(
            return_value=httpx.Response(200, json={"values": expected_values})
        )

        dashboard = GoogleSheetsDashboard(SPREADSHEET_ID, httpx_client=client)
        dashboard._get_access_token = lambda c: _fake_token()

        values = await dashboard.read_metrics("Metrics", "A1:B10")

    assert values == expected_values


@respx.mock
@pytest.mark.asyncio
async def test_append_row_posts_data(monkeypatch):
    """append_row should POST a row to the append endpoint and return True."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.post(f"{BASE}/values/Metrics%21A1:append").mock(
            return_value=httpx.Response(200, json={"updates": {"updatedRows": 1}})
        )

        dashboard = GoogleSheetsDashboard(SPREADSHEET_ID, httpx_client=client)
        dashboard._get_access_token = lambda c: _fake_token()

        result = await dashboard.append_row("Metrics", ["2024-01-01", "55", "90"])

    assert result is True


@pytest.mark.asyncio
async def test_create_chart_data_builds_series(monkeypatch):
    """create_chart_data should build ChartData with correct labels and series without API calls."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    history = [
        {"timestamp": "2024-01-01", "cpu": 30, "memory": 60},
        {"timestamp": "2024-01-02", "cpu": 45, "memory": 70},
        {"timestamp": "2024-01-03", "cpu": 50, "memory": 80},
    ]

    dashboard = GoogleSheetsDashboard(SPREADSHEET_ID)
    chart = await dashboard.create_chart_data(history)

    assert isinstance(chart, ChartData)
    assert chart.labels == ["2024-01-01", "2024-01-02", "2024-01-03"]
    assert len(chart.series) == 2
    cpu_series = next(s for s in chart.series if s["name"] == "cpu")
    assert cpu_series["data"] == [30, 45, 50]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _fake_token():
    return "ya29.sheets_token"
