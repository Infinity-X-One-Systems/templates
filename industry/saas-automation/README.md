# SaaS Automation

Production-grade SaaS subscription automation with MRR calculation and churn detection.

## Usage

```python
from src.engine import SaaSAutomationEngine

engine = SaaSAutomationEngine()
sub = engine.create_subscription("cust-1", "pro", "monthly")
engine.track_usage(sub.id, "api_calls", 150)
risk = engine.detect_churn_risk(sub.id)
```

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
