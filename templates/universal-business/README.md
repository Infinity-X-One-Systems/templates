# Universal Business Automation Template

A production-ready template that models and automates **any business** as a configurable process pipeline.

## Concept

Every business, regardless of industry, is a pipeline:

```
Inputs → Processes → Outputs → Feedback
```

This template captures that universal pattern with three core abstractions:

| Abstraction | Description |
|---|---|
| `BusinessProcess` | A named stage in your pipeline (intake, review, delivery, …) |
| `WorkItem` | A unit of work moving through the pipeline (lead, order, ticket, …) |
| `AutomationRule` | A trigger → action rule that fires when conditions are met |

Seven built-in `ProcessType` values cover the full lifecycle: `INTAKE`, `QUALIFICATION`, `PROCESSING`, `REVIEW`, `DELIVERY`, `FOLLOWUP`, `REPORTING`.

## Quick Start

```bash
pip install -r requirements.txt
python - <<'EOF'
from src.engine import UniversalBusinessEngine, ProcessType

engine = UniversalBusinessEngine(business_name="Acme Corp", industry="saas")

engine.add_process("intake", ProcessType.INTAKE,
    description="Capture new trial sign-ups",
    inputs=["signup_form"], outputs=["lead_record"])

engine.add_process("qualify", ProcessType.QUALIFICATION,
    description="Score and qualify leads",
    inputs=["lead_record"], outputs=["qualified_lead"],
    automation_level="full-auto")

engine.add_process("close", ProcessType.DELIVERY,
    description="Convert qualified lead to customer",
    inputs=["qualified_lead"], outputs=["contract"])

lead = engine.create_work_item("ACME Trial", data={"email": "ceo@acme.com"}, process="intake")
engine.advance_item(lead.item_id, "qualify")
engine.advance_item(lead.item_id, "close", assigned_to="sales-rep-1")
engine.complete_item(lead.item_id)

metrics = engine.get_metrics()
print(metrics)
print(engine.export_process_map())
EOF
```

## Requirements

- Python 3.10+ (uses `X | Y` union syntax; tested on 3.12)
- pydantic 2.x


```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -q
```

## Project Structure

```
universal-business/
├── src/
│   ├── __init__.py
│   └── engine.py          # UniversalBusinessEngine + all models
├── tests/
│   ├── __init__.py
│   └── test_engine.py     # 5 tests covering core engine behaviour
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── requirements-dev.txt
```

## Infinity Protocol Compliance

- **TAP**: Policy (process definitions) > Authority (engine rules) > Truth (work item state)
- **110% Protocol**: No placeholder code; all methods are fully implemented
- **Security First**: No secrets in code; all configuration is runtime-injectable
