"""Tests for LeadIngestionPipeline."""

import pytest
from src.engine import LeadIngestionPipeline


@pytest.fixture
def pipeline():
    return LeadIngestionPipeline()


def test_ingest_lead(pipeline):
    lead = pipeline.ingest_lead(
        source="organic",
        email="alice@example.com",
        name="Alice",
        phone="555-1234",
        metadata={"company": "Acme", "role": "CTO"},
    )
    assert lead.status == "new"
    assert lead.email == "alice@example.com"
    assert lead.id is not None


def test_score_lead(pipeline):
    lead = pipeline.ingest_lead(
        source="organic",
        email="bob@example.com",
        phone="555-9999",
        metadata={"size": "50"},
    )
    score = pipeline.score_lead(lead.id)
    # email=+20, phone=+15, organic=+25, metadata(1/1 filled)=+20 → 80
    assert score == 80.0


def test_qualify_lead(pipeline):
    lead = pipeline.ingest_lead(
        source="organic",
        email="carol@example.com",
        phone="555-0000",
        metadata={"industry": "tech"},
    )
    # score = 80 → above default threshold 60
    qualified = pipeline.qualify_lead(lead.id)
    assert qualified.status == "qualified"


def test_pipeline_stats(pipeline):
    l1 = pipeline.ingest_lead(source="organic", email="d@x.com", phone="1")
    l2 = pipeline.ingest_lead(source="direct")
    pipeline.qualify_lead(l1.id)
    pipeline.qualify_lead(l2.id)
    stats = pipeline.get_pipeline_stats()
    assert stats.total == 2
    assert stats.qualified == 1
    assert stats.rejected == 1
    assert stats.conversion_rate == 50.0


def test_export_to_crm(pipeline):
    lead = pipeline.ingest_lead(source="paid", email="e@x.com", name="Eve")
    pipeline.qualify_lead(lead.id)
    payloads = pipeline.export_to_crm([lead.id])
    assert len(payloads) == 1
    p = payloads[0]
    assert p["lead_id"] == lead.id
    assert p["email"] == "e@x.com"
    assert p["source"] == "paid"
    assert "exported_at" in p
