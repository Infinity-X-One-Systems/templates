# Education Platform Engine

Production-grade Python module for course management, student enrollment, and certification.

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
docker build -t education-engine .
docker run --rm education-engine
```

## Features

- Create courses with modules, duration, and difficulty level
- Enroll students and track per-module progress scores
- Automatically mark enrollments complete when all modules are scored
- Calculate course-wide completion rates
- Issue verifiable certificates with unique credential IDs
