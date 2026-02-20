# Logistics Engine

Production-grade Python module for shipment tracking, fleet management, and route optimization.

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
docker build -t logistics-engine .
docker run --rm logistics-engine
```

## Features

- Create shipments with tracking IDs and priority levels (express/standard/economy)
- Update shipment status and current location
- Calculate ETA based on priority (express=1d, standard=5d, economy=10d)
- Monitor fleet utilization metrics
- Optimize routes by sorting shipments by priority and ETA
