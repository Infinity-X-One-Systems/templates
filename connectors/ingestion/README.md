# Async Ingestion Pipeline

High-throughput async HTTP ingestion pipeline for the Infinity Template Library.

## Overview

A fully async, production-ready HTTP data ingestion pipeline built on `httpx` and `pydantic`. Features token-bucket rate limiting, configurable exponential-backoff retries, and automatic `robots.txt` compliance.

## Components

| Class | Purpose |
|-------|---------|
| `IngestionPipeline` | Orchestrates fetch, retry, and rate-limiting |
| `RateLimiter` | Token-bucket limiting (configurable rps) |
| `RobotsTxtChecker` | Robots.txt compliance with per-domain caching |
| `IngestionJob` | Input model for a single fetch task |
| `IngestionResult` | Output model carrying status, content, and timing |
| `RetryConfig` | Retry policy (attempts, base, max-wait) |
| `PipelineStats` | Aggregated run statistics |

## Quick Start

```bash
pip install -r requirements.txt
python src/pipeline.py
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Docker

```bash
docker build -t ingestion-pipeline .
docker run --rm ingestion-pipeline
```

## Usage Example

```python
import asyncio
from pipeline import IngestionPipeline, IngestionJob, RetryConfig

async def main():
    pipeline = IngestionPipeline(
        rate_limit_rps=5.0,
        retry_config=RetryConfig(max_attempts=3, backoff_base=1.0, max_wait=30.0),
        respect_robots=True,
    )

    jobs = [
        IngestionJob(url="https://api.example.com/data/1"),
        IngestionJob(url="https://api.example.com/data/2", priority=10),
    ]

    results = await pipeline.fetch_batch(jobs)
    for result in results:
        if result.error:
            print(f"Failed: {result.url} — {result.error}")
        else:
            print(f"OK [{result.status_code}]: {result.url} ({result.duration_ms:.0f} ms)")

    stats = pipeline.get_stats()
    print(f"Success rate: {stats.jobs_success}/{stats.jobs_total}")

asyncio.run(main())
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `rate_limit_rps` | `2.0` | Maximum requests per second |
| `retry_config.max_attempts` | `3` | Maximum fetch attempts per job |
| `retry_config.backoff_base` | `2.0` | Multiplier for exponential back-off |
| `retry_config.max_wait` | `60.0` | Maximum seconds to wait between retries |
| `respect_robots` | `True` | Honour `robots.txt` Disallow rules |
