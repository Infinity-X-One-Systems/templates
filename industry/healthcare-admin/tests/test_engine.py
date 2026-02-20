"""Tests for HealthcareAdminEngine."""
import pytest
from src.engine import HealthcareAdminEngine


@pytest.fixture
def engine():
    return HealthcareAdminEngine()


def test_schedule_appointment(engine):
    appt = engine.schedule_appointment("P001", "DR001", "2025-06-10T09:00", "annual-checkup")
    assert appt.patient_id == "P001"
    assert appt.provider_id == "DR001"
    assert appt.status == "scheduled"
    assert appt.type == "annual-checkup"


def test_get_daily_schedule(engine):
    engine.schedule_appointment("P001", "DR001", "2025-06-10T09:00", "checkup")
    engine.schedule_appointment("P002", "DR001", "2025-06-10T10:00", "followup")
    engine.schedule_appointment("P003", "DR002", "2025-06-10T09:00", "checkup")
    schedule = engine.get_daily_schedule("DR001", "2025-06-10")
    assert len(schedule) == 2
    assert all(a.provider_id == "DR001" for a in schedule)


def test_check_appointment_conflict(engine):
    engine.schedule_appointment("P001", "DR001", "2025-06-10T09:00", "checkup", duration_mins=60)
    # Overlapping appointment
    assert engine.check_appointment_conflict("DR001", "2025-06-10T09:30", 30) is True
    # Non-overlapping appointment
    assert engine.check_appointment_conflict("DR001", "2025-06-10T11:00", 30) is False


def test_generate_billing_record(engine):
    appt = engine.schedule_appointment("P001", "DR001", "2025-06-10T09:00", "checkup")
    billing = engine.generate_billing_record(appt.id, ["99213", "93000"], [150.00, 75.50])
    assert billing.appointment_id == appt.id
    assert billing.total == 225.50
    assert len(billing.procedure_codes) == 2
