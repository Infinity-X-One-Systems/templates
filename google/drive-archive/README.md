# Google Drive Archive

A production-ready template for uploading and managing files in Google Drive via the Drive API v3.

## Overview

`GoogleDriveArchive` provides:
- Uploading arbitrary binary content as named Drive files
- Creating nested folder structures
- Listing files in a folder with optional query filtering
- Archiving system state dicts as timestamped JSON snapshots

## Configuration

| Environment Variable          | Description                                          |
|-------------------------------|------------------------------------------------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON string of the Google Service Account key file  |

### Service Account Setup

1. Create a Service Account in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Drive API**.
3. Share the root Drive folder with the service account's email address.
4. Download the JSON key and export it:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON=$(cat path/to/service-account.json)
```

## Usage

```python
import asyncio
from src.archive import GoogleDriveArchive

archive = GoogleDriveArchive(root_folder_id="your-drive-folder-id")

async def main():
    # Upload a file
    file = await archive.upload_file("report.pdf", pdf_bytes, "application/pdf")
    print(file.web_view_link)

    # Archive system state
    state = {"service": "payments", "status": "healthy", "queue_depth": 42}
    snapshot = await archive.archive_system_state(state, "payments")
    print(snapshot.file_id)

asyncio.run(main())
```

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t drive-archive .
docker run -e GOOGLE_SERVICE_ACCOUNT_JSON="$(cat sa.json)" drive-archive
```
