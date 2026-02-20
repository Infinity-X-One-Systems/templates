from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    steps: List[str]
    approvers: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StepRecord(BaseModel):
    step_index: int
    step_name: str
    approver: str
    approved: bool
    comment: str
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowInstance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    initiator: str
    data: Dict[str, Any]
    current_step: int = 0
    status: str = "in_progress"
    step_records: List[StepRecord] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class BottleneckReport(BaseModel):
    step: str
    avg_duration_hours: float
    count: int


class EnterpriseWorkflowEngine:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}
        self._instances: dict[str, WorkflowInstance] = {}

    def define_workflow(
        self,
        name: str,
        steps: list[str],
        approvers: list[str],
    ) -> Workflow:
        wf = Workflow(name=name, steps=steps, approvers=approvers)
        self._workflows[wf.id] = wf
        return wf

    def create_instance(
        self,
        workflow_id: str,
        initiator: str,
        data: dict[str, Any],
    ) -> WorkflowInstance:
        if workflow_id not in self._workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        inst = WorkflowInstance(
            workflow_id=workflow_id,
            initiator=initiator,
            data=data,
            current_step=0,
        )
        self._instances[inst.id] = inst
        return inst

    def advance_step(
        self,
        instance_id: str,
        approver: str,
        approved: bool,
        comment: str = "",
    ) -> WorkflowInstance:
        if instance_id not in self._instances:
            raise ValueError(f"Instance {instance_id} not found")
        inst = self._instances[instance_id]
        if inst.status == "complete":
            raise ValueError("Workflow instance is already complete")
        wf = self._workflows[inst.workflow_id]
        expected_approver = wf.approvers[inst.current_step % len(wf.approvers)]
        if approver != expected_approver:
            raise ValueError(
                f"Wrong approver: expected {expected_approver}, got {approver}"
            )
        record = StepRecord(
            step_index=inst.current_step,
            step_name=wf.steps[inst.current_step],
            approver=approver,
            approved=approved,
            comment=comment,
        )
        inst.step_records.append(record)
        if not approved:
            inst.status = "rejected"
        else:
            inst.current_step += 1
            if inst.current_step >= len(wf.steps):
                inst.status = "complete"
                inst.completed_at = datetime.utcnow()
        self._instances[instance_id] = inst
        return inst

    def get_bottlenecks(self, instances: list[WorkflowInstance]) -> list[BottleneckReport]:
        step_durations: dict[str, list[float]] = {}
        for inst in instances:
            for i, record in enumerate(inst.step_records):
                step = record.step_name
                if i == 0:
                    duration = (record.completed_at - inst.created_at).total_seconds() / 3600
                else:
                    prev = inst.step_records[i - 1]
                    duration = (record.completed_at - prev.completed_at).total_seconds() / 3600
                step_durations.setdefault(step, []).append(duration)
        reports = []
        for step, durations in step_durations.items():
            reports.append(
                BottleneckReport(
                    step=step,
                    avg_duration_hours=sum(durations) / len(durations),
                    count=len(durations),
                )
            )
        return sorted(reports, key=lambda r: r.avg_duration_hours, reverse=True)

    def calculate_completion_rate(
        self, workflow_id: str, instances: list[WorkflowInstance]
    ) -> float:
        relevant = [i for i in instances if i.workflow_id == workflow_id]
        if not relevant:
            return 0.0
        completed = sum(1 for i in relevant if i.status == "complete")
        return completed / len(relevant)
