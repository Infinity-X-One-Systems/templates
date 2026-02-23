"""Lead Ingestion Pipeline - core engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float = 0.0
    status: str = "new"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineStats(BaseModel):
    total: int
    qualified: int
    rejected: int
    conversion_rate: float


class CRMPayload(BaseModel):
    lead_id: str
    email: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    score: float
    status: str
    source: str
    exported_at: datetime


class LeadIngestionPipeline:
    def __init__(self) -> None:
        self._leads: dict[str, Lead] = {}

    def ingest_lead(
        self,
        source: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Lead:
        lead = Lead(
            source=source,
            email=email,
            name=name,
            phone=phone,
            metadata=metadata or {},
            status="new",
        )
        lead.score = self._compute_score(lead)
        self._leads[lead.id] = lead
        return lead

    def _compute_score(self, lead: Lead) -> float:
        score = 0.0
        if lead.email:
            score += 20.0
        if lead.phone:
            score += 15.0
        if lead.source == "organic":
            score += 25.0
        elif lead.source == "paid":
            score += 20.0
        if lead.metadata:
            filled = sum(1 for v in lead.metadata.values() if v is not None and v != "")
            completeness = filled / len(lead.metadata) if lead.metadata else 0.0
            score += completeness * 20.0
        return round(score, 2)

    def score_lead(self, lead_id: str) -> float:
        lead = self._leads[lead_id]
        lead.score = self._compute_score(lead)
        return lead.score

    def qualify_lead(self, lead_id: str, threshold: float = 60.0) -> Lead:
        lead = self._leads[lead_id]
        lead.status = "qualified" if lead.score >= threshold else "rejected"
        return lead

    def get_pipeline_stats(self) -> PipelineStats:
        total = len(self._leads)
        qualified = sum(1 for l in self._leads.values() if l.status == "qualified")
        rejected = sum(1 for l in self._leads.values() if l.status == "rejected")
        conversion_rate = (qualified / total * 100.0) if total > 0 else 0.0
        return PipelineStats(
            total=total,
            qualified=qualified,
            rejected=rejected,
            conversion_rate=round(conversion_rate, 2),
        )

    def export_to_crm(self, lead_ids: list[str]) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        payloads = []
        for lid in lead_ids:
            lead = self._leads[lid]
            payloads.append(
                CRMPayload(
                    lead_id=lead.id,
                    email=lead.email,
                    name=lead.name,
                    phone=lead.phone,
                    score=lead.score,
                    status=lead.status,
                    source=lead.source,
                    exported_at=now,
                ).model_dump()
            )
        return payloads
