# Consulting Workflow Engine

A production-grade Python module for managing consulting engagements, time tracking, invoicing, deliverables, and profitability analysis.

## Features
- Create and manage client engagements
- Log consultant hours by activity
- Generate itemized invoices for billing periods
- Track project deliverables and status
- Calculate engagement profitability metrics

## Usage
```python
from src.engine import ConsultingWorkflowEngine
from datetime import date

engine = ConsultingWorkflowEngine()
eng = engine.create_engagement("Acme Corp", "strategy", 50000.0, date(2024, 1, 1), 3)
engine.log_hours(eng.id, "consultant-1", 8.0, "Workshop facilitation")
invoice = engine.generate_invoice(eng.id, date(2024, 1, 1), date(2024, 1, 31), hourly_rate=150.0)
metrics = engine.calculate_profitability(eng.id, cost_per_hour=75.0)
```
