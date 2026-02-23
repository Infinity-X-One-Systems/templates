# Marketing Automation

Production-grade marketing campaign engine with ROI calculation and performance reporting.

## Usage

```python
from src.engine import MarketingAutomationEngine

engine = MarketingAutomationEngine()
campaign = engine.create_campaign("Summer Sale", "email", 1000.0, "all", "2025-06-01", "2025-06-30")
engine.record_impression(campaign.id)
engine.record_conversion(campaign.id, 150.0)
roi = engine.calculate_roi(campaign.id)
```

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
