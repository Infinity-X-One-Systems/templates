"""Tests for GoogleDriveArchive – all Google API calls are mocked with respx."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from src.archive import CredentialsError, DriveFile, GoogleDriveArchive

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FAKE_SA = {
    "type": "service_account",
    "client_email": "drive-sa@project.iam.gserviceaccount.com",
    "private_key": "fake-key",
}

ROOT_FOLDER = "folder-root-001"
UPLOAD_BASE = "https://www.googleapis.com/upload/drive/v3/files"
FILES_BASE = "https://www.googleapis.com/drive/v3/files"

FAKE_FILE_RESPONSE = {
    "id": "file-abc123",
    "name": "test.json",
    "mimeType": "application/json",
    "webViewLink": "https://drive.google.com/file/d/file-abc123/view",
    "parents": [ROOT_FOLDER],
}

FAKE_FOLDER_RESPONSE = {
    "id": "folder-child-001",
    "name": "archive-2024",
    "mimeType": "application/vnd.google-apps.folder",
    "webViewLink": "https://drive.google.com/drive/folders/folder-child-001",
    "parents": [ROOT_FOLDER],
}

FAKE_FILES_LIST = {
    "files": [
        {
            "id": "file-001",
            "name": "state_001.json",
            "mimeType": "application/json",
            "webViewLink": "https://drive.google.com/file/d/file-001/view",
            "parents": [ROOT_FOLDER],
        },
        {
            "id": "file-002",
            "name": "state_002.json",
            "mimeType": "application/json",
            "webViewLink": "https://drive.google.com/file/d/file-002/view",
            "parents": [ROOT_FOLDER],
        },
    ]
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_upload_file_returns_drive_file(monkeypatch):
    """upload_file should POST to the upload endpoint and return a DriveFile."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.post(UPLOAD_BASE).mock(
            return_value=httpx.Response(200, json=FAKE_FILE_RESPONSE)
        )

        archive = GoogleDriveArchive(ROOT_FOLDER, httpx_client=client)

        async def fake_token(c):
            return "ya29.drive_token"

        archive._get_access_token = fake_token

        result = await archive.upload_file(
            name="test.json",
            content=b'{"key": "value"}',
            mime_type="application/json",
        )

    assert isinstance(result, DriveFile)
    assert result.file_id == "file-abc123"
    assert result.name == "test.json"
    assert ROOT_FOLDER in result.parents


@respx.mock
@pytest.mark.asyncio
async def test_create_folder_returns_drive_file(monkeypatch):
    """create_folder should POST folder metadata and return a DriveFile with folder MIME type."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.post(FILES_BASE).mock(
            return_value=httpx.Response(200, json=FAKE_FOLDER_RESPONSE)
        )

        archive = GoogleDriveArchive(ROOT_FOLDER, httpx_client=client)

        async def fake_token(c):
            return "ya29.drive_token"

        archive._get_access_token = fake_token

        folder = await archive.create_folder("archive-2024")

    assert isinstance(folder, DriveFile)
    assert folder.file_id == "folder-child-001"
    assert folder.mime_type == "application/vnd.google-apps.folder"


@respx.mock
@pytest.mark.asyncio
async def test_list_files_returns_drive_files(monkeypatch):
    """list_files should GET files from the API and return a list of DriveFile objects."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    async with httpx.AsyncClient() as client:
        respx.get(FILES_BASE).mock(
            return_value=httpx.Response(200, json=FAKE_FILES_LIST)
        )

        archive = GoogleDriveArchive(ROOT_FOLDER, httpx_client=client)

        async def fake_token(c):
            return "ya29.drive_token"

        archive._get_access_token = fake_token

        files = await archive.list_files(ROOT_FOLDER)

    assert len(files) == 2
    assert all(isinstance(f, DriveFile) for f in files)
    assert files[0].file_id == "file-001"
    assert files[1].name == "state_002.json"


@respx.mock
@pytest.mark.asyncio
async def test_archive_system_state_uploads_json(monkeypatch):
    """archive_system_state should serialize state to JSON and upload it."""
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps(FAKE_SA))

    state = {"service": "api-gateway", "status": "healthy", "requests": 1024}

    async with httpx.AsyncClient() as client:
        upload_mock = respx.post(UPLOAD_BASE).mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "file-state-001",
                    "name": "api-gateway_state_20240101T000000Z.json",
                    "mimeType": "application/json",
                    "webViewLink": "https://drive.google.com/file/d/file-state-001/view",
                    "parents": [ROOT_FOLDER],
                },
            )
        )

        archive = GoogleDriveArchive(ROOT_FOLDER, httpx_client=client)

        async def fake_token(c):
            return "ya29.drive_token"

        archive._get_access_token = fake_token

        result = await archive.archive_system_state(state, "api-gateway")

    assert isinstance(result, DriveFile)
    assert result.file_id == "file-state-001"
    assert result.mime_type == "application/json"
    assert upload_mock.called
