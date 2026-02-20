from __future__ import annotations
import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class Engagement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    project_type: str
    budget: float
    start_date: date
    team_size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TimeEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    engagement_id: str
    consultant_id: str
    hours: float
    activity: str
    logged_at: datetime = Field(default_factory=datetime.utcnow)


class InvoiceLineItem(BaseModel):
    description: str
    hours: float
    rate: float
    amount: float


class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    engagement_id: str
    period_start: date
    period_end: date
    line_items: List[InvoiceLineItem]
    total: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class Deliverable(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    engagement_id: str
    name: str
    due_date: date
    status: str


class ProfitMetrics(BaseModel):
    engagement_id: str
    revenue: float
    cost: float
    margin_pct: float


class ConsultingWorkflowEngine:
    def __init__(self) -> None:
        self._engagements: dict[str, Engagement] = {}
        self._time_entries: list[TimeEntry] = []
        self._deliverables: list[Deliverable] = []

    def create_engagement(
        self,
        client_name: str,
        project_type: str,
        budget: float,
        start_date: date,
        team_size: int,
    ) -> Engagement:
        eng = Engagement(
            client_name=client_name,
            project_type=project_type,
            budget=budget,
            start_date=start_date,
            team_size=team_size,
        )
        self._engagements[eng.id] = eng
        return eng

    def log_hours(
        self,
        engagement_id: str,
        consultant_id: str,
        hours: float,
        activity: str,
    ) -> TimeEntry:
        if engagement_id not in self._engagements:
            raise ValueError(f"Engagement {engagement_id} not found")
        entry = TimeEntry(
            engagement_id=engagement_id,
            consultant_id=consultant_id,
            hours=hours,
            activity=activity,
        )
        self._time_entries.append(entry)
        return entry

    def generate_invoice(
        self,
        engagement_id: str,
        period_start: date,
        period_end: date,
        hourly_rate: float = 150.0,
    ) -> Invoice:
        if engagement_id not in self._engagements:
            raise ValueError(f"Engagement {engagement_id} not found")
        entries = [e for e in self._time_entries if e.engagement_id == engagement_id]
        line_items: list[InvoiceLineItem] = []
        for entry in entries:
            amount = entry.hours * hourly_rate
            line_items.append(
                InvoiceLineItem(
                    description=entry.activity,
                    hours=entry.hours,
                    rate=hourly_rate,
                    amount=amount,
                )
            )
        total = sum(li.amount for li in line_items)
        return Invoice(
            engagement_id=engagement_id,
            period_start=period_start,
            period_end=period_end,
            line_items=line_items,
            total=total,
        )

    def track_deliverable(
        self,
        engagement_id: str,
        name: str,
        due_date: date,
        status: str,
    ) -> Deliverable:
        if engagement_id not in self._engagements:
            raise ValueError(f"Engagement {engagement_id} not found")
        d = Deliverable(
            engagement_id=engagement_id,
            name=name,
            due_date=due_date,
            status=status,
        )
        self._deliverables.append(d)
        return d

    def calculate_profitability(
        self,
        engagement_id: str,
        cost_per_hour: float,
    ) -> ProfitMetrics:
        if engagement_id not in self._engagements:
            raise ValueError(f"Engagement {engagement_id} not found")
        entries = [e for e in self._time_entries if e.engagement_id == engagement_id]
        total_hours = sum(e.hours for e in entries)
        eng = self._engagements[engagement_id]
        revenue = eng.budget
        cost = total_hours * cost_per_hour
        margin_pct = ((revenue - cost) / revenue * 100) if revenue else 0.0
        return ProfitMetrics(
            engagement_id=engagement_id,
            revenue=revenue,
            cost=cost,
            margin_pct=round(margin_pct, 2),
        )
