# Local Services

Production-grade local services marketplace engine with bookings, invoicing, and ratings.

## Usage

```python
from src.engine import LocalServicesEngine

engine = LocalServicesEngine()
provider = engine.register_provider("Bob's Plumbing", ["plumbing"], "Downtown", 75.0)
booking = engine.create_booking("cust-1", provider.id, "plumbing", "2025-06-15T10:00:00", 2.0)
invoice = engine.complete_job(booking.id, 2.5)
```

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
