# Gmail AI Responder

A production-ready template for integrating with the Gmail API using Google Service Account credentials.

## Overview

The `GmailAIResponder` class provides:
- Listing unread inbox messages
- Drafting replies
- Sending drafted replies
- Batch-processing an inbox with a custom reply generator function

All Google API communication is done over HTTP (via `httpx`), making every method fully mockable for testing.

## Configuration

| Environment Variable            | Description                                           |
|---------------------------------|-------------------------------------------------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON`   | JSON string of the Google Service Account key file   |
| `GMAIL_USER_EMAIL`              | The Gmail address to act on behalf of (default: `me`)|

### Service Account Setup

1. Create a Service Account in [Google Cloud Console](https://console.cloud.google.com/).
2. Grant it **Gmail API** access (`https://www.googleapis.com/auth/gmail.modify`).
3. Enable **Domain-Wide Delegation** if acting on behalf of Workspace users.
4. Download the JSON key and set it as `GOOGLE_SERVICE_ACCOUNT_JSON`.

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON=$(cat path/to/service-account.json)
export GMAIL_USER_EMAIL="user@yourdomain.com"
```

## Usage

```python
import asyncio
from src.responder import GmailAIResponder

responder = GmailAIResponder(user_email="user@yourdomain.com")

async def main():
    messages = await responder.list_unread_messages(max_results=5)
    sent = await responder.process_inbox(
        messages,
        reply_generator_fn=lambda msg: f"Thanks for writing: {msg.subject}",
    )
    print(f"Sent {len(sent)} replies.")

asyncio.run(main())
```

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t gmail-responder .
docker run -e GOOGLE_SERVICE_ACCOUNT_JSON="$(cat sa.json)" \
           -e GMAIL_USER_EMAIL="user@yourdomain.com" \
           gmail-responder
```
