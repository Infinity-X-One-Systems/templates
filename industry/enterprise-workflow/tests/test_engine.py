import pytest
from src.engine import EnterpriseWorkflowEngine


def test_define_workflow():
    engine = EnterpriseWorkflowEngine()
    wf = engine.define_workflow(
        "Budget Approval",
        ["Draft", "Review", "Approve"],
        ["manager", "director", "cfo"],
    )
    assert wf.name == "Budget Approval"
    assert len(wf.steps) == 3


def test_create_instance():
    engine = EnterpriseWorkflowEngine()
    wf = engine.define_workflow("Onboarding", ["HR Check", "IT Setup"], ["hr", "it"])
    inst = engine.create_instance(wf.id, "employee-1", {"name": "Alice"})
    assert inst.workflow_id == wf.id
    assert inst.current_step == 0
    assert inst.status == "in_progress"


def test_advance_step_to_completion():
    engine = EnterpriseWorkflowEngine()
    wf = engine.define_workflow("Purchase", ["Review", "Approve"], ["reviewer", "approver"])
    inst = engine.create_instance(wf.id, "requester", {"amount": 500})
    inst = engine.advance_step(inst.id, "reviewer", True, "Looks good")
    assert inst.current_step == 1
    inst = engine.advance_step(inst.id, "approver", True, "Approved")
    assert inst.status == "complete"


def test_advance_step_wrong_approver():
    engine = EnterpriseWorkflowEngine()
    wf = engine.define_workflow("Expense", ["Check"], ["finance"])
    inst = engine.create_instance(wf.id, "employee", {"amount": 200})
    with pytest.raises(ValueError, match="Wrong approver"):
        engine.advance_step(inst.id, "wrongperson", True)
