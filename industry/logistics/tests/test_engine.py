"""Tests for LogisticsEngine."""
import pytest
from src.engine import LogisticsEngine


@pytest.fixture
def engine():
    return LogisticsEngine(total_fleet=50)


def test_create_shipment(engine):
    shipment = engine.create_shipment("Chicago", "Miami", 25.0, "express")
    assert shipment.origin == "Chicago"
    assert shipment.destination == "Miami"
    assert shipment.status == "created"
    assert shipment.tracking_id is not None


def test_update_status(engine):
    shipment = engine.create_shipment("Seattle", "Denver", 10.0, "standard")
    updated = engine.update_status(shipment.tracking_id, "in_transit", "Salt Lake City")
    assert updated.status == "in_transit"
    assert updated.location == "Salt Lake City"


def test_calculate_eta(engine):
    express = engine.create_shipment("NYC", "LA", 5.0, "express")
    economy = engine.create_shipment("NYC", "LA", 5.0, "economy")
    eta_express = engine.calculate_eta(express.tracking_id)
    eta_economy = engine.calculate_eta(economy.tracking_id)
    assert eta_express < eta_economy


def test_fleet_utilization(engine):
    s1 = engine.create_shipment("A", "B", 1.0, "express")
    s2 = engine.create_shipment("C", "D", 2.0, "standard")
    engine.update_status(s2.tracking_id, "delivered", "D")
    metrics = engine.get_fleet_utilization()
    assert metrics.active == 1
    assert metrics.total == 50
    assert metrics.utilization_pct == 2.0
