"""Tests for the CRM automation engine."""
import pytest
from src.crm import CRMEngine, PipelineStage


def test_create_contact_and_deal():
    crm = CRMEngine()
    contact = crm.create_contact("Alice Smith", "alice@example.com", company="Acme Corp")
    deal = crm.create_deal("Enterprise Deal", contact.id, value=50_000)
    assert deal.stage == PipelineStage.LEAD
    assert deal.probability == 0.10


def test_advance_stage():
    crm = CRMEngine()
    contact = crm.create_contact("Bob Jones", "bob@example.com")
    deal = crm.create_deal("SaaS Deal", contact.id, value=20_000)
    advanced = crm.advance_stage(deal.id, PipelineStage.QUALIFIED)
    assert advanced.stage == PipelineStage.QUALIFIED
    assert advanced.probability == 0.25


def test_pipeline_summary():
    crm = CRMEngine()
    contact = crm.create_contact("Carol White", "carol@example.com")
    deal1 = crm.create_deal("Deal A", contact.id, value=10_000)
    crm.advance_stage(deal1.id, PipelineStage.CLOSED_WON)
    crm.create_deal("Deal B", contact.id, value=50_000)
    summary = crm.pipeline_summary()
    assert summary["closed_won"] == 10_000
    assert summary["total_deals"] == 2


@pytest.mark.asyncio
async def test_auto_qualify_large_deal():
    crm = CRMEngine()
    contact = crm.create_contact("Dave Brown", "dave@example.com")
    deal = crm.create_deal("Big Deal", contact.id, value=50_000)
    qualified = await crm.auto_qualify(deal.id)
    assert qualified.stage == PipelineStage.QUALIFIED


def test_invalid_contact_raises():
    crm = CRMEngine()
    with pytest.raises(ValueError, match="not found"):
        crm.create_deal("Invalid Deal", "nonexistent-id", value=1000)
