# Google Docs Generator

A production-ready template for creating and editing Google Docs via the Docs API v1.

## Overview

`GoogleDocsGenerator` provides:
- Creating new documents with initial content
- Appending content with named paragraph styles
- Exporting documents as PDF bytes
- Generating structured reports from a `ReportTemplate` and data dict

## Configuration

| Environment Variable          | Description                                          |
|-------------------------------|------------------------------------------------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON string of the Google Service Account key file  |

### Service Account Setup

1. Create a Service Account in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Docs API** and **Google Drive API**.
3. Grant the service account access to the Drive folder where docs will be created.
4. Download the JSON key and export it:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON=$(cat path/to/service-account.json)
```

## Usage

```python
import asyncio
from src.generator import GoogleDocsGenerator, ReportTemplate

gen = GoogleDocsGenerator()

async def main():
    doc = await gen.create_document("My Doc", "Hello, Docs!")
    print(doc.url)

    template = ReportTemplate(title="Status Report", sections=["Summary", "Metrics"])
    report = await gen.generate_report(template, {"Summary": "OK", "Metrics": {"uptime": "99.9%"}})
    pdf = await gen.export_as_pdf(report.doc_id)

asyncio.run(main())
```

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t docs-generator .
docker run -e GOOGLE_SERVICE_ACCOUNT_JSON="$(cat sa.json)" docs-generator
```
