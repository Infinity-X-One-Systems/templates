"""Local Services Engine - core engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Provider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    services: list[str]
    service_area: str
    hourly_rate: float
    avg_rating: float = 0.0
    rating_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    provider_id: str
    service: str
    scheduled_at: datetime
    duration_hours: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    provider_id: str
    customer_id: str
    service: str
    actual_hours: float
    hourly_rate: float
    amount: float
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LocalServicesEngine:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}
        self._bookings: dict[str, Booking] = {}

    def register_provider(
        self,
        name: str,
        services: list[str],
        service_area: str,
        hourly_rate: float,
    ) -> Provider:
        provider = Provider(
            name=name,
            services=services,
            service_area=service_area,
            hourly_rate=hourly_rate,
        )
        self._providers[provider.id] = provider
        return provider

    def create_booking(
        self,
        customer_id: str,
        provider_id: str,
        service: str,
        datetime_str: str,
        duration_hours: float,
    ) -> Booking:
        scheduled_at = datetime.fromisoformat(datetime_str)
        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
        booking = Booking(
            customer_id=customer_id,
            provider_id=provider_id,
            service=service,
            scheduled_at=scheduled_at,
            duration_hours=duration_hours,
        )
        self._bookings[booking.id] = booking
        return booking

    def complete_job(self, booking_id: str, actual_hours: float) -> Invoice:
        booking = self._bookings[booking_id]
        booking.status = "completed"
        provider = self._providers[booking.provider_id]
        amount = round(actual_hours * provider.hourly_rate, 2)
        return Invoice(
            booking_id=booking_id,
            provider_id=booking.provider_id,
            customer_id=booking.customer_id,
            service=booking.service,
            actual_hours=actual_hours,
            hourly_rate=provider.hourly_rate,
            amount=amount,
        )

    def rate_provider(
        self, provider_id: str, rating: float, review: str
    ) -> Provider:
        provider = self._providers[provider_id]
        total = provider.avg_rating * provider.rating_count + rating
        provider.rating_count += 1
        provider.avg_rating = round(total / provider.rating_count, 2)
        return provider

    def find_available_providers(
        self, service: str, date_str: str
    ) -> list[Provider]:
        booked_provider_ids = {
            b.provider_id
            for b in self._bookings.values()
            if b.scheduled_at.date().isoformat() == date_str
            and b.service == service
            and b.status != "completed"
        }
        available = [
            p
            for p in self._providers.values()
            if service in p.services and p.id not in booked_provider_ids
        ]
        return sorted(available, key=lambda p: p.avg_rating, reverse=True)
