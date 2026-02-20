from datetime import date
from src.engine import ConsultingWorkflowEngine


def test_create_engagement():
    engine = ConsultingWorkflowEngine()
    eng = engine.create_engagement("Acme Corp", "strategy", 50000.0, date(2024, 1, 1), 3)
    assert eng.client_name == "Acme Corp"
    assert eng.budget == 50000.0
    assert eng.team_size == 3


def test_log_hours():
    engine = ConsultingWorkflowEngine()
    eng = engine.create_engagement("Beta LLC", "audit", 20000.0, date(2024, 2, 1), 2)
    entry = engine.log_hours(eng.id, "consultant-1", 8.0, "Workshop facilitation")
    assert entry.hours == 8.0
    assert entry.engagement_id == eng.id


def test_generate_invoice():
    engine = ConsultingWorkflowEngine()
    eng = engine.create_engagement("Gamma Inc", "transformation", 100000.0, date(2024, 3, 1), 5)
    engine.log_hours(eng.id, "c1", 10.0, "Analysis")
    engine.log_hours(eng.id, "c2", 5.0, "Report writing")
    invoice = engine.generate_invoice(eng.id, date(2024, 3, 1), date(2024, 3, 31), hourly_rate=200.0)
    assert invoice.total == 3000.0
    assert len(invoice.line_items) == 2


def test_calculate_profitability():
    engine = ConsultingWorkflowEngine()
    eng = engine.create_engagement("Delta Co", "IT", 10000.0, date(2024, 4, 1), 1)
    engine.log_hours(eng.id, "c1", 20.0, "Development")
    metrics = engine.calculate_profitability(eng.id, cost_per_hour=100.0)
    assert metrics.revenue == 10000.0
    assert metrics.cost == 2000.0
    assert metrics.margin_pct == 80.0
