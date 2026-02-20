# Construction Workflow Engine

Production-grade Python module for managing construction projects, milestones, and budget tracking.

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
docker build -t construction-engine .
docker run --rm construction-engine
```

## Features

- Create and manage construction projects with defined phases
- Track milestones with budget allocation percentages
- Calculate budget variance between planned and actual spend
- Identify critical path milestones (zero float)
