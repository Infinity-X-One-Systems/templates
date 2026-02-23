"""Healthcare Administration Engine – scheduling, billing, and provider utilization."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Dict, List

from pydantic import BaseModel, Field


class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    provider_id: str
    scheduled_at: str
    type: str
    duration_mins: int = 30
    status: str = "scheduled"


class BillingRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    appointment_id: str
    procedure_codes: List[str]
    amounts: List[float]
    total: float
    status: str = "pending"


class HealthcareAdminEngine:
    """Manages appointments, billing records, and provider utilization metrics."""

    WORK_HOURS = 8

    def __init__(self) -> None:
        self._appointments: Dict[str, Appointment] = {}
        self._billing: Dict[str, BillingRecord] = {}

    def schedule_appointment(
        self,
        patient_id: str,
        provider_id: str,
        datetime_str: str,
        type: str,
        duration_mins: int = 30,
    ) -> Appointment:
        appt = Appointment(
            patient_id=patient_id,
            provider_id=provider_id,
            scheduled_at=datetime_str,
            type=type,
            duration_mins=duration_mins,
        )
        self._appointments[appt.id] = appt
        return appt

    def get_daily_schedule(self, provider_id: str, date_str: str) -> List[Appointment]:
        return [
            a
            for a in self._appointments.values()
            if a.provider_id == provider_id and a.scheduled_at.startswith(date_str)
        ]

    def check_appointment_conflict(
        self, provider_id: str, datetime_str: str, duration_mins: int
    ) -> bool:
        new_start = datetime.fromisoformat(datetime_str)
        new_end = new_start + timedelta(minutes=duration_mins)
        for appt in self._appointments.values():
            if appt.provider_id != provider_id or appt.status == "cancelled":
                continue
            existing_start = datetime.fromisoformat(appt.scheduled_at)
            existing_end = existing_start + timedelta(minutes=appt.duration_mins)
            if new_start < existing_end and new_end > existing_start:
                return True
        return False

    def generate_billing_record(
        self, appointment_id: str, procedure_codes: List[str], amounts: List[float]
    ) -> BillingRecord:
        if len(procedure_codes) != len(amounts):
            raise ValueError("procedure_codes and amounts must have the same length")
        record = BillingRecord(
            appointment_id=appointment_id,
            procedure_codes=procedure_codes,
            amounts=amounts,
            total=round(sum(amounts), 2),
        )
        self._billing[record.id] = record
        return record

    def calculate_provider_utilization(self, provider_id: str, date_str: str) -> float:
        schedule = self.get_daily_schedule(provider_id, date_str)
        booked_mins = sum(a.duration_mins for a in schedule if a.status != "cancelled")
        capacity_mins = self.WORK_HOURS * 60
        if capacity_mins == 0:
            return 0.0
        return round(min(booked_mins / capacity_mins, 1.0), 4)


if __name__ == "__main__":
    engine = HealthcareAdminEngine()
    appt = engine.schedule_appointment("P001", "DR001", "2025-06-01T09:00", "checkup")
    print(f"Appointment scheduled: {appt.id} at {appt.scheduled_at}")
