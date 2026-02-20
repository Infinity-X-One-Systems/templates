"""Tests for SaaSAutomationEngine."""

import pytest
from src.engine import SaaSAutomationEngine, SubscriptionError


@pytest.fixture
def engine():
    return SaaSAutomationEngine()


def test_create_subscription(engine):
    sub = engine.create_subscription("cust-1", "pro", "monthly")
    assert sub.status == "trialing"
    assert sub.trial_end > sub.created_at
    assert sub.renewal_date > sub.trial_end


def test_process_renewal(engine):
    sub = engine.create_subscription("cust-2", "starter", "monthly")
    original_renewal = sub.renewal_date
    renewed = engine.process_renewal(sub.id)
    assert renewed.renewal_date > original_renewal
    assert renewed.status == "active"


def test_process_renewal_cancelled_raises(engine):
    sub = engine.create_subscription("cust-3", "pro", "annual")
    sub.status = "cancelled"
    with pytest.raises(SubscriptionError):
        engine.process_renewal(sub.id)


def test_detect_churn_risk_no_usage(engine):
    sub = engine.create_subscription("cust-4", "starter", "monthly")
    risk = engine.detect_churn_risk(sub.id)
    assert "no_usage_14d" in risk.factors
    assert risk.risk_level == "high"
