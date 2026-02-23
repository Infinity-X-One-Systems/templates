"""Tests for the real estate distress agent."""
import pytest
from src.agent import RealEstateDistressAgent, Property, PropertySignal, DistressLevel


@pytest.mark.asyncio
async def test_no_signals_no_distress():
    agent = RealEstateDistressAgent()
    prop = Property(address="123 Main St", city="Dallas", state="TX", zip_code="75201")
    result = await agent.analyze(prop)
    assert result.distress_level == DistressLevel.NONE


@pytest.mark.asyncio
async def test_foreclosure_signal_high_distress():
    agent = RealEstateDistressAgent()
    prop = Property(
        address="456 Oak Ave", city="Houston", state="TX", zip_code="77001",
        signals=[
            PropertySignal(signal_type="foreclosure", value=1.0),
            PropertySignal(signal_type="tax_delinquency", value=1.0),
        ],
    )
    result = await agent.analyze(prop)
    assert result.distress_level in [DistressLevel.HIGH, DistressLevel.CRITICAL]
    assert result.estimated_discount_pct >= 25.0


@pytest.mark.asyncio
async def test_recommended_action_populated():
    agent = RealEstateDistressAgent()
    prop = Property(address="789 Elm Dr", city="Austin", state="TX", zip_code="78701")
    result = await agent.analyze(prop)
    assert len(result.recommended_action) > 0
