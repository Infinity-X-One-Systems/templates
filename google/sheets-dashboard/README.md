# Google Sheets Dashboard

A production-ready template for reading and writing metrics to Google Sheets via the Sheets API v4.

## Overview

`GoogleSheetsDashboard` provides:
- Writing a metrics dict as rows into a named sheet
- Reading cell ranges
- Appending rows
- Building chart-ready `ChartData` from a history of metric snapshots

## Configuration

| Environment Variable          | Description                                          |
|-------------------------------|------------------------------------------------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON string of the Google Service Account key file  |

### Service Account Setup

1. Create a Service Account in [Google Cloud Console](https://console.cloud.google.com/).
2. Share the target spreadsheet with the service account's email address.
3. Download the JSON key and export it:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON=$(cat path/to/service-account.json)
```

## Usage

```python
import asyncio
from src.dashboard import GoogleSheetsDashboard

dashboard = GoogleSheetsDashboard(spreadsheet_id="your-spreadsheet-id")

async def main():
    await dashboard.write_metrics("Summary", {"cpu": 72, "memory": 54})
    values = await dashboard.read_metrics("Summary", "A1:B10")
    print(values)

asyncio.run(main())
```

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t sheets-dashboard .
docker run -e GOOGLE_SERVICE_ACCOUNT_JSON="$(cat sa.json)" sheets-dashboard
```
