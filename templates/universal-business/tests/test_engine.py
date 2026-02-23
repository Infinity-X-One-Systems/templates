import pytest
from src.engine import UniversalBusinessEngine, ProcessType


def _make_engine() -> UniversalBusinessEngine:
    engine = UniversalBusinessEngine(business_name="Test Corp", industry="test")
    engine.add_process(
        "intake", ProcessType.INTAKE,
        description="Receive new requests",
        inputs=["request_form"], outputs=["intake_record"],
    )
    engine.add_process(
        "review", ProcessType.REVIEW,
        description="Review and approve",
        inputs=["intake_record"], outputs=["decision"],
        automation_level="full-auto",
    )
    return engine


def test_add_process():
    engine = UniversalBusinessEngine(business_name="Acme", industry="retail")
    proc = engine.add_process(
        "intake", ProcessType.INTAKE,
        description="Intake step",
        inputs=["order"], outputs=["order_record"],
        automation_level="semi-auto", estimated_hours=0.5,
    )
    assert proc.name == "intake"
    assert proc.type == ProcessType.INTAKE
    assert "intake" in engine.processes
    assert engine.processes["intake"].automation_level == "semi-auto"


def test_create_work_item_invalid_process():
    engine = UniversalBusinessEngine(business_name="Acme", industry="retail")
    with pytest.raises(ValueError, match="Process 'nonexistent' not defined"):
        engine.create_work_item("Task 1", data={}, process="nonexistent")


def test_advance_item():
    engine = _make_engine()
    item = engine.create_work_item("Lead #1", data={"source": "web"}, process="intake")
    assert item.current_process == "intake"
    assert item.status == "pending"

    advanced = engine.advance_item(item.item_id, "review", assigned_to="agent-1")
    assert advanced.current_process == "review"
    assert advanced.status == "in_progress"
    assert advanced.assigned_to == "agent-1"
    assert len(advanced.history) == 1
    assert advanced.history[0]["from"] == "intake"
    assert advanced.history[0]["to"] == "review"


def test_complete_item():
    engine = _make_engine()
    item = engine.create_work_item("Lead #2", data={}, process="intake")
    completed = engine.complete_item(item.item_id)
    assert completed.status == "complete"


def test_get_metrics():
    engine = _make_engine()
    engine.create_work_item("Item A", data={}, process="intake")
    engine.create_work_item("Item B", data={}, process="intake")
    item_c = engine.create_work_item("Item C", data={}, process="intake")
    engine.advance_item(item_c.item_id, "review")

    metrics = engine.get_metrics()
    assert metrics.total_items == 3
    assert metrics.items_by_process["intake"] == 2
    assert metrics.items_by_process["review"] == 1
    assert metrics.items_by_status["pending"] == 2
    assert metrics.items_by_status["in_progress"] == 1
    # 1 of 2 processes is full-auto
    assert metrics.automation_rate == pytest.approx(0.5)
