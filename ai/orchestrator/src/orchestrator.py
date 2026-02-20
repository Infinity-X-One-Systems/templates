"""
Business Workflow Orchestrator — Infinity Template Library
Coordinates multiple agents and services into a unified workflow pipeline.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    depends_on: list[str] = Field(default_factory=list)
    timeout_seconds: int = 60
    retry_count: int = 0
    max_retries: int = 3
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class WorkflowDefinition(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    steps: list[WorkflowStep]
    on_failure: str = "stop"  # "stop" | "continue" | "rollback"


class WorkflowRun(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    status: StepStatus = StepStatus.PENDING
    steps: list[WorkflowStep]
    context: dict[str, Any] = Field(default_factory=dict)
    started_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    completed_at: Optional[str] = None


StepHandler = Callable[[WorkflowStep, dict[str, Any]], Coroutine[Any, Any, Any]]


class WorkflowOrchestrator:
    """
    Orchestrates multi-step workflows with dependency resolution,
    parallel execution, retry logic, and failure handling.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, StepHandler] = {}
        self._runs: dict[str, WorkflowRun] = {}

    def register_handler(self, step_name: str, handler: StepHandler) -> None:
        """Register an async handler function for a named step."""
        self._handlers[step_name] = handler

    async def execute(self, workflow: WorkflowDefinition, context: Optional[dict[str, Any]] = None) -> WorkflowRun:
        """Execute a workflow definition and return the run record."""
        run = WorkflowRun(
            workflow_id=workflow.workflow_id,
            steps=[s.model_copy() for s in workflow.steps],
            context=context or {},
        )
        self._runs[run.run_id] = run

        step_map = {s.name: s for s in run.steps}
        completed: set[str] = set()
        failed: set[str] = set()

        run.status = StepStatus.RUNNING
        pending = list(run.steps)

        while pending:
            # Find steps whose dependencies are satisfied
            ready = [
                s for s in pending
                if all(dep in completed for dep in s.depends_on)
                and s.name not in failed
                and s.status == StepStatus.PENDING
            ]

            if not ready:
                # Deadlock or all remaining steps depend on failed steps
                for s in pending:
                    if s.status == StepStatus.PENDING:
                        s.status = StepStatus.SKIPPED
                break

            # Execute ready steps in parallel
            await asyncio.gather(*[self._run_step(s, run.context) for s in ready])

            for s in ready:
                pending.remove(s)
                if s.status == StepStatus.COMPLETED:
                    completed.add(s.name)
                else:
                    failed.add(s.name)
                    if workflow.on_failure == "stop":
                        for remaining in pending:
                            remaining.status = StepStatus.SKIPPED
                        pending.clear()

        run.completed_at = datetime.now(tz=timezone.utc).isoformat()
        run.status = StepStatus.FAILED if failed else StepStatus.COMPLETED
        return run

    async def _run_step(self, step: WorkflowStep, context: dict[str, Any]) -> None:
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(tz=timezone.utc).isoformat()

        handler = self._handlers.get(step.name)
        if handler is None:
            step.status = StepStatus.FAILED
            step.error = f"No handler registered for step '{step.name}'"
            return

        for attempt in range(step.max_retries + 1):
            try:
                result = await asyncio.wait_for(handler(step, context), timeout=step.timeout_seconds)
                step.result = result
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now(tz=timezone.utc).isoformat()
                return
            except asyncio.TimeoutError:
                step.error = f"Step timed out after {step.timeout_seconds}s (attempt {attempt + 1})"
            except Exception as exc:
                step.error = str(exc)
                step.retry_count = attempt + 1
                if attempt < step.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        step.status = StepStatus.FAILED
