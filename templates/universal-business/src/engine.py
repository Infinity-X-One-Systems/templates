"""
Universal Business Automation Engine
======================================
A single engine that can model, automate, and replace
ANY business's existing workflow system.

Philosophy: Every business is a pipeline of:
  Inputs → Processes → Outputs → Feedback

This engine captures that universal pattern and provides
automation hooks for every stage.
"""
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid


class ProcessType(str, Enum):
    INTAKE = "intake"           # Receiving inputs (leads, orders, requests)
    QUALIFICATION = "qualification"  # Filtering/scoring inputs
    PROCESSING = "processing"   # Core value-adding work
    REVIEW = "review"           # Quality check / approval
    DELIVERY = "delivery"       # Delivering output to customer
    FOLLOWUP = "followup"       # Post-delivery engagement
    REPORTING = "reporting"     # Analytics and insights


class BusinessProcess(BaseModel):
    process_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: ProcessType
    description: str
    inputs: list[str]
    outputs: list[str]
    automation_level: str = "manual"  # manual|semi-auto|full-auto
    estimated_hours_per_unit: float = 1.0
    cost_per_unit: float = 0.0


class WorkItem(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    data: dict = Field(default_factory=dict)
    current_process: str
    status: str = "pending"  # pending|in_progress|complete|blocked|cancelled
    priority: int = 5  # 1=highest, 10=lowest
    assigned_to: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    history: list[dict] = Field(default_factory=list)


class AutomationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    trigger_process: str
    trigger_condition: str  # e.g., "status == 'complete'", "priority < 3"
    action: str             # e.g., "advance_to:review", "notify:slack", "assign:agent"
    enabled: bool = True


class BusinessMetrics(BaseModel):
    total_items: int = 0
    items_by_status: dict[str, int] = Field(default_factory=dict)
    items_by_process: dict[str, int] = Field(default_factory=dict)
    avg_cycle_time_hours: float = 0.0
    automation_rate: float = 0.0  # 0.0-1.0
    throughput_per_day: float = 0.0


class UniversalBusinessEngine:
    """
    Models and automates any business as a configurable process pipeline.
    
    Usage:
        engine = UniversalBusinessEngine(business_name="Acme Corp")
        engine.add_process("intake", ProcessType.INTAKE, ...)
        engine.add_process("qualify", ProcessType.QUALIFICATION, ...)
        item = engine.create_work_item("New lead", data={...}, process="intake")
        engine.advance_item(item.item_id, "qualify")
        metrics = engine.get_metrics()
    """

    def __init__(self, business_name: str, industry: str = "general"):
        self.business_name = business_name
        self.industry = industry
        self.processes: dict[str, BusinessProcess] = {}
        self.work_items: dict[str, WorkItem] = {}
        self.automation_rules: list[AutomationRule] = []

    def add_process(self, name: str, process_type: ProcessType, description: str,
                    inputs: list[str], outputs: list[str],
                    automation_level: str = "manual",
                    estimated_hours: float = 1.0, cost_per_unit: float = 0.0) -> BusinessProcess:
        process = BusinessProcess(
            name=name, type=process_type, description=description,
            inputs=inputs, outputs=outputs, automation_level=automation_level,
            estimated_hours_per_unit=estimated_hours, cost_per_unit=cost_per_unit,
        )
        self.processes[name] = process
        return process

    def create_work_item(self, title: str, data: dict,
                         process: str, priority: int = 5) -> WorkItem:
        if process not in self.processes:
            raise ValueError(f"Process '{process}' not defined. Add it first.")
        item = WorkItem(title=title, data=data, current_process=process, priority=priority)
        self.work_items[item.item_id] = item
        return item

    def advance_item(self, item_id: str, next_process: str,
                     assigned_to: str | None = None) -> WorkItem:
        item = self.work_items.get(item_id)
        if not item:
            raise ValueError(f"Work item {item_id} not found")
        if next_process not in self.processes:
            raise ValueError(f"Process '{next_process}' not defined")
        item.history.append({
            "from": item.current_process,
            "to": next_process,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "assigned_to": assigned_to,
        })
        item.current_process = next_process
        item.status = "in_progress"
        item.updated_at = datetime.now(timezone.utc).isoformat()
        if assigned_to:
            item.assigned_to = assigned_to
        return item

    def complete_item(self, item_id: str) -> WorkItem:
        item = self.work_items.get(item_id)
        if not item:
            raise ValueError(f"Work item {item_id} not found")
        item.status = "complete"
        item.updated_at = datetime.now(timezone.utc).isoformat()
        return item

    def add_automation_rule(self, name: str, trigger_process: str,
                             trigger_condition: str, action: str) -> AutomationRule:
        rule = AutomationRule(
            name=name, trigger_process=trigger_process,
            trigger_condition=trigger_condition, action=action,
        )
        self.automation_rules.append(rule)
        return rule

    def get_items_in_process(self, process_name: str) -> list[WorkItem]:
        return [i for i in self.work_items.values() if i.current_process == process_name]

    def get_metrics(self) -> BusinessMetrics:
        items = list(self.work_items.values())
        by_status: dict[str, int] = {}
        by_process: dict[str, int] = {}
        for item in items:
            by_status[item.status] = by_status.get(item.status, 0) + 1
            by_process[item.current_process] = by_process.get(item.current_process, 0) + 1
        auto_processes = sum(1 for p in self.processes.values() if p.automation_level == "full-auto")
        auto_rate = auto_processes / len(self.processes) if self.processes else 0.0
        return BusinessMetrics(
            total_items=len(items),
            items_by_status=by_status,
            items_by_process=by_process,
            automation_rate=auto_rate,
        )

    def export_process_map(self) -> dict:
        """Export the full business process map as a dict (for documentation/visualization)."""
        return {
            "business": self.business_name,
            "industry": self.industry,
            "processes": {name: p.model_dump() for name, p in self.processes.items()},
            "automation_rules": [r.model_dump() for r in self.automation_rules],
            "work_item_count": len(self.work_items),
        }
