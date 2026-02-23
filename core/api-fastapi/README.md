# Core FastAPI API Scaffold

Production-grade REST API built with FastAPI, featuring JWT auth, structured logging, OTEL telemetry, and health endpoints.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest --cov=app
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_NAME` | `infinity-api` | Service identifier |
| `ENV` | `development` | Runtime environment |
| `SECRET_KEY` | `change-me` | JWT signing secret |
| `DATABASE_URL` | SQLite | Database connection URL |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `` | OTEL collector endpoint |

## Architecture

```
app/
├── main.py          # FastAPI app, middleware, router registration
├── config.py        # Pydantic-settings configuration
├── auth.py          # JWT creation/verification
├── errors.py        # Custom exceptions + handlers
├── logging.py       # Structlog structured logging
├── telemetry.py     # OpenTelemetry hooks
└── routers/
    ├── health.py    # /health liveness + readiness
    ├── auth.py      # /auth register/login/me
    └── v1.py        # /api/v1 domain routes
```

## Composing Into a System

This template is listed in the [template manifest schema](../../engine/schema/manifest.schema.json) under `backend.fastapi`.
