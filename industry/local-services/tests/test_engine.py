"""Tests for LocalServicesEngine."""

import pytest
from src.engine import LocalServicesEngine


@pytest.fixture
def engine():
    return LocalServicesEngine()


def test_register_provider(engine):
    p = engine.register_provider("Bob's Plumbing", ["plumbing"], "Downtown", 75.0)
    assert p.name == "Bob's Plumbing"
    assert p.hourly_rate == 75.0
    assert p.avg_rating == 0.0


def test_create_booking(engine):
    p = engine.register_provider("Alice's Electric", ["electrical"], "Midtown", 90.0)
    booking = engine.create_booking(
        "cust-1", p.id, "electrical", "2025-06-15T10:00:00", 2.0
    )
    assert booking.provider_id == p.id
    assert booking.status == "pending"


def test_complete_job(engine):
    p = engine.register_provider("CleanPro", ["cleaning"], "Uptown", 50.0)
    booking = engine.create_booking(
        "cust-2", p.id, "cleaning", "2025-06-16T09:00:00", 3.0
    )
    invoice = engine.complete_job(booking.id, 3.5)
    assert invoice.amount == 175.0
    assert invoice.actual_hours == 3.5


def test_rate_provider(engine):
    p = engine.register_provider("GardenPro", ["gardening"], "Suburbs", 40.0)
    updated = engine.rate_provider(p.id, 5.0, "Excellent!")
    assert updated.avg_rating == 5.0
    assert updated.rating_count == 1
    engine.rate_provider(p.id, 3.0, "Okay.")
    assert updated.avg_rating == 4.0


def test_find_available_providers(engine):
    p1 = engine.register_provider("FastFix", ["plumbing"], "North", 60.0)
    p2 = engine.register_provider("QuickFlow", ["plumbing"], "South", 55.0)
    engine.rate_provider(p1.id, 4.5, "Great")
    engine.rate_provider(p2.id, 3.0, "OK")
    # Book p1 on target date so only p2 is available
    engine.create_booking("c1", p1.id, "plumbing", "2025-07-10T08:00:00", 2.0)
    available = engine.find_available_providers("plumbing", "2025-07-10")
    assert all(prov.id != p1.id for prov in available)
    assert any(prov.id == p2.id for prov in available)
