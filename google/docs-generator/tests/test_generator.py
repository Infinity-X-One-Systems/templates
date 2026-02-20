"""Tests for GoogleDocsGenerator – all Google API calls are mocked with respx."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from src.generator import CredentialsError, Document, GoogleDocsGenerator, ReportTemplate

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FAKE_SA = {
    "type": "service_account",
    "client_email": "docs-sa@project.iam.gserviceaccount.com",
    "private_key": "fake-key",
}

TOKEN_RESPONSE = {"access_token": "ya29.docs_token", "expires_in": 3600}

DOCS_BASE = "https://docs.googleapis.com/v1/documents"
DRIVE_BASE = "https://www.googleapis.com/drive/v3/files"

CREATE_DOC_RESPONSE = {
    "documentId": "doc-abc123",
    "title": "Test Report",
}

BATCH_UPDATE_RESPONSE = {"documentId": "doc-abc123", "replies": [{}]}

PDF_BYTES = b"%PDF-1.4 fake pdf content"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_create_document_returns_document(monkeypatch):
    """create_document should create a doc via API and return a Document object."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.post(DOCS_BASE).mock(
            return_value=httpx.Response(200, json=CREATE_DOC_RESPONSE)
        )
        respx.post(f"{DOCS_BASE}/doc-abc123:batchUpdate").mock(
            return_value=httpx.Response(200, json=BATCH_UPDATE_RESPONSE)
        )

        gen = GoogleDocsGenerator(httpx_client=client)

        async def fake_token(c):
            return "ya29.docs_token"

        gen._get_access_token = fake_token

        doc = await gen.create_document("Test Report", "Hello, world!")

    assert isinstance(doc, Document)
    assert doc.doc_id == "doc-abc123"
    assert doc.title == "Test Report"
    assert "doc-abc123" in doc.url


@respx.mock
@pytest.mark.asyncio
async def test_append_content_calls_batch_update(monkeypatch):
    """append_content should POST to the batchUpdate endpoint and return True."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.post(f"{DOCS_BASE}/doc-abc123:batchUpdate").mock(
            return_value=httpx.Response(200, json=BATCH_UPDATE_RESPONSE)
        )

        gen = GoogleDocsGenerator(httpx_client=client)

        async def fake_token(c):
            return "ya29.docs_token"

        gen._get_access_token = fake_token

        result = await gen.append_content("doc-abc123", "New paragraph", style="HEADING_1")

    assert result is True


@respx.mock
@pytest.mark.asyncio
async def test_export_as_pdf_returns_bytes(monkeypatch):
    """export_as_pdf should GET the export endpoint and return raw bytes."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.get(f"{DRIVE_BASE}/doc-abc123/export").mock(
            return_value=httpx.Response(200, content=PDF_BYTES)
        )

        gen = GoogleDocsGenerator(httpx_client=client)

        async def fake_token(c):
            return "ya29.docs_token"

        gen._get_access_token = fake_token

        pdf = await gen.export_as_pdf("doc-abc123")

    assert isinstance(pdf, bytes)
    assert pdf == PDF_BYTES


@respx.mock
@pytest.mark.asyncio
async def test_generate_report_creates_doc(monkeypatch):
    """generate_report should render the template, create a doc, and return a Document."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    template = ReportTemplate(
        title="Monthly Report",
        sections=["Summary", "Details"],
        include_timestamp=False,
    )
    data = {
        "Summary": "All systems operational.",
        "Details": {"errors": 0, "warnings": 3},
    }

    async with httpx.AsyncClient() as client:
        respx.post(DOCS_BASE).mock(
            return_value=httpx.Response(
                200, json={"documentId": "doc-report-001", "title": "Monthly Report"}
            )
        )
        respx.post(f"{DOCS_BASE}/doc-report-001:batchUpdate").mock(
            return_value=httpx.Response(
                200, json={"documentId": "doc-report-001", "replies": [{}]}
            )
        )

        gen = GoogleDocsGenerator(httpx_client=client)

        async def fake_token(c):
            return "ya29.docs_token"

        gen._get_access_token = fake_token

        doc = await gen.generate_report(template, data)

    assert isinstance(doc, Document)
    assert doc.doc_id == "doc-report-001"
