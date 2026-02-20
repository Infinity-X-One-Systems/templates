"""
CRM Automation Engine — Infinity Template Library
Manages leads, contacts, pipeline stages, and automated workflows.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


class PipelineStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Contact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


class Deal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    contact_id: str
    stage: PipelineStage = PipelineStage.LEAD
    value: float = 0.0
    probability: float = Field(default=0.1, ge=0.0, le=1.0)
    expected_close: Optional[str] = None
    notes: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

    @property
    def weighted_value(self) -> float:
        return self.value * self.probability


class CRMEngine:
    """
    CRM automation engine supporting contact management,
    deal pipelines, and automated stage progression.
    """

    STAGE_PROBABILITIES: dict[PipelineStage, float] = {
        PipelineStage.LEAD: 0.10,
        PipelineStage.QUALIFIED: 0.25,
        PipelineStage.PROPOSAL: 0.50,
        PipelineStage.NEGOTIATION: 0.75,
        PipelineStage.CLOSED_WON: 1.00,
        PipelineStage.CLOSED_LOST: 0.00,
    }

    def __init__(self) -> None:
        self._contacts: dict[str, Contact] = {}
        self._deals: dict[str, Deal] = {}

    def create_contact(self, name: str, email: str, **kwargs: object) -> Contact:
        contact = Contact(name=name, email=email, **kwargs)  # type: ignore[arg-type]
        self._contacts[contact.id] = contact
        return contact

    def create_deal(self, title: str, contact_id: str, value: float = 0.0) -> Deal:
        if contact_id not in self._contacts:
            raise ValueError(f"Contact {contact_id} not found")
        deal = Deal(
            title=title,
            contact_id=contact_id,
            value=value,
            probability=self.STAGE_PROBABILITIES[PipelineStage.LEAD],
        )
        self._deals[deal.id] = deal
        return deal

    def advance_stage(self, deal_id: str, new_stage: PipelineStage) -> Deal:
        deal = self._deals.get(deal_id)
        if deal is None:
            raise ValueError(f"Deal {deal_id} not found")
        deal.stage = new_stage
        deal.probability = self.STAGE_PROBABILITIES[new_stage]
        deal.updated_at = datetime.now(tz=timezone.utc).isoformat()
        return deal

    def pipeline_summary(self) -> dict[str, float]:
        total_pipeline = sum(d.weighted_value for d in self._deals.values() if d.stage not in [PipelineStage.CLOSED_LOST])
        closed_won = sum(d.value for d in self._deals.values() if d.stage == PipelineStage.CLOSED_WON)
        return {
            "total_pipeline_weighted": round(total_pipeline, 2),
            "closed_won": round(closed_won, 2),
            "total_deals": len(self._deals),
            "total_contacts": len(self._contacts),
        }

    async def auto_qualify(self, deal_id: str) -> Deal:
        """Run qualification checks and auto-advance if criteria met."""
        await asyncio.sleep(0)  # Simulate async check
        deal = self._deals.get(deal_id)
        if deal is None:
            raise ValueError(f"Deal {deal_id} not found")
        if deal.stage == PipelineStage.LEAD and deal.value > 10_000:
            return self.advance_stage(deal_id, PipelineStage.QUALIFIED)
        return deal
