"""Tests for MarketingAutomationEngine."""

import pytest
from src.engine import MarketingAutomationEngine


@pytest.fixture
def engine():
    return MarketingAutomationEngine()


def test_create_campaign(engine):
    c = engine.create_campaign(
        "Summer Sale", "email", 1000.0, "millennials", "2025-06-01", "2025-06-30"
    )
    assert c.name == "Summer Sale"
    assert c.impressions == 0
    assert c.status == "active"


def test_record_impression(engine):
    c = engine.create_campaign("Ad1", "social", 500.0, "gen-z", "2025-07-01", "2025-07-31")
    for _ in range(5):
        engine.record_impression(c.id)
    assert c.impressions == 5


def test_record_conversion(engine):
    c = engine.create_campaign("Ad2", "ppc", 800.0, "all", "2025-08-01", "2025-08-31")
    engine.record_conversion(c.id, 150.0)
    engine.record_conversion(c.id, 200.0)
    assert c.conversions == 2
    assert c.revenue == 350.0


def test_calculate_roi(engine):
    c = engine.create_campaign("Ad3", "display", 1000.0, "all", "2025-09-01", "2025-09-30")
    engine.record_conversion(c.id, 500.0)
    engine.record_conversion(c.id, 800.0)
    roi = engine.calculate_roi(c.id)
    assert roi.roas == 1.3
    assert roi.roi_pct == 30.0
    assert roi.cpa == 500.0
