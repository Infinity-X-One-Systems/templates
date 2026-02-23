# Healthcare Admin Engine

Production-grade Python module for appointment scheduling, billing, and provider utilization.

**Note:** This module is designed for synthetic/test data only. Do not store real PHI (Protected Health Information).

## Quick Start

```bash
pip install -r requirements.txt
python -m src.engine
```

## Run Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t healthcare-admin-engine .
docker run --rm healthcare-admin-engine
```

## Features

- Schedule patient appointments and detect conflicts
- Retrieve daily provider schedules
- Generate itemized billing records with procedure codes
- Calculate provider utilization rates (0–1 scale)
