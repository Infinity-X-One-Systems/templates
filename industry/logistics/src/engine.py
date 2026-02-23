"""Logistics Engine – shipment tracking, fleet utilization, and route optimization."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

PRIORITY_DAYS = {"express": 1, "standard": 5, "economy": 10}


class Shipment(BaseModel):
    tracking_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str
    destination: str
    weight_kg: float
    priority: str
    status: str = "created"
    location: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FleetMetrics(BaseModel):
    active: int
    total: int
    utilization_pct: float


class LogisticsEngine:
    """Manages shipments, fleet metrics, and route planning."""

    def __init__(self, total_fleet: int = 100) -> None:
        self._shipments: Dict[str, Shipment] = {}
        self._total_fleet = total_fleet

    def create_shipment(
        self, origin: str, destination: str, weight_kg: float, priority: str
    ) -> Shipment:
        if priority not in PRIORITY_DAYS:
            raise ValueError(f"priority must be one of {list(PRIORITY_DAYS)}")
        shipment = Shipment(
            origin=origin, destination=destination, weight_kg=weight_kg, priority=priority
        )
        self._shipments[shipment.tracking_id] = shipment
        return shipment

    def update_status(self, tracking_id: str, status: str, location: str) -> Shipment:
        shipment = self._get_shipment(tracking_id)
        shipment.status = status
        shipment.location = location
        return shipment

    def calculate_eta(self, tracking_id: str) -> str:
        shipment = self._get_shipment(tracking_id)
        created = datetime.fromisoformat(shipment.created_at)
        days = PRIORITY_DAYS[shipment.priority]
        eta = created + timedelta(days=days)
        return eta.isoformat()

    def get_fleet_utilization(self) -> FleetMetrics:
        active = sum(
            1 for s in self._shipments.values() if s.status not in ("delivered", "cancelled")
        )
        utilization_pct = round((active / self._total_fleet) * 100, 2) if self._total_fleet else 0.0
        return FleetMetrics(active=active, total=self._total_fleet, utilization_pct=utilization_pct)

    def route_optimize(self, shipments: List[Shipment]) -> List[Shipment]:
        priority_order = {"express": 0, "standard": 1, "economy": 2}
        return sorted(
            shipments,
            key=lambda s: (priority_order.get(s.priority, 99), self.calculate_eta(s.tracking_id)),
        )

    def _get_shipment(self, tracking_id: str) -> Shipment:
        if tracking_id not in self._shipments:
            raise KeyError(f"Shipment {tracking_id} not found")
        return self._shipments[tracking_id]


if __name__ == "__main__":
    engine = LogisticsEngine()
    s = engine.create_shipment("New York", "Los Angeles", 12.5, "express")
    print(f"Shipment created: {s.tracking_id}")
