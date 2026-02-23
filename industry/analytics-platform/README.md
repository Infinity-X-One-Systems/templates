# Analytics Platform

Production-grade analytics engine with event ingestion, funnel analysis, cohort retention, and dashboards.

## Usage

```python
from src.engine import AnalyticsPlatformEngine

engine = AnalyticsPlatformEngine()
engine.ingest_event("web", "page_view", "user-1", {"page": "/home"})
dashboard = engine.generate_dashboard_data("web", 7)
```

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
