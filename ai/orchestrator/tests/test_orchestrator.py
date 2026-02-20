"""Tests for the workflow orchestrator."""
import pytest
from src.orchestrator import WorkflowOrchestrator, WorkflowDefinition, WorkflowStep, StepStatus


async def success_handler(step, ctx):
    return {"step": step.name, "done": True}


async def fail_handler(step, ctx):
    raise ValueError("Intentional failure")


@pytest.mark.asyncio
async def test_simple_workflow():
    orch = WorkflowOrchestrator()
    orch.register_handler("step-a", success_handler)
    orch.register_handler("step-b", success_handler)

    workflow = WorkflowDefinition(
        name="Test Workflow",
        description="Simple two-step workflow",
        steps=[
            WorkflowStep(name="step-a"),
            WorkflowStep(name="step-b", depends_on=["step-a"]),
        ],
    )
    run = await orch.execute(workflow)
    assert run.status == StepStatus.COMPLETED
    assert all(s.status == StepStatus.COMPLETED for s in run.steps)


@pytest.mark.asyncio
async def test_parallel_steps():
    orch = WorkflowOrchestrator()
    orch.register_handler("step-1", success_handler)
    orch.register_handler("step-2", success_handler)
    orch.register_handler("step-3", success_handler)

    workflow = WorkflowDefinition(
        name="Parallel Workflow",
        description="Steps 1 and 2 run in parallel, step 3 depends on both",
        steps=[
            WorkflowStep(name="step-1"),
            WorkflowStep(name="step-2"),
            WorkflowStep(name="step-3", depends_on=["step-1", "step-2"]),
        ],
    )
    run = await orch.execute(workflow)
    assert run.status == StepStatus.COMPLETED


@pytest.mark.asyncio
async def test_failed_step_stops_workflow():
    orch = WorkflowOrchestrator()
    orch.register_handler("step-ok", success_handler)
    orch.register_handler("step-fail", fail_handler)

    workflow = WorkflowDefinition(
        name="Failure Workflow",
        description="Step fail causes downstream skip",
        on_failure="stop",
        steps=[
            WorkflowStep(name="step-fail", max_retries=0),
            WorkflowStep(name="step-ok", depends_on=["step-fail"]),
        ],
    )
    run = await orch.execute(workflow)
    assert run.status == StepStatus.FAILED
