# Lead Ingestion

Production-grade lead ingestion pipeline with scoring, qualification, and CRM export.

## Usage

```python
from src.engine import LeadIngestionPipeline

pipeline = LeadIngestionPipeline()
lead = pipeline.ingest_lead(source="organic", email="user@example.com", phone="555-0000")
pipeline.qualify_lead(lead.id)
stats = pipeline.get_pipeline_stats()
```

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
