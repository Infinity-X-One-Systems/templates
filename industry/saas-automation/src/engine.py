"""SaaS Automation Engine - core engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

PLAN_PRICES: dict[str, float] = {
    "starter": 29.0,
    "pro": 99.0,
    "enterprise": 499.0,
}

BILLING_CYCLE_MONTHS: dict[str, int] = {
    "monthly": 1,
    "annual": 12,
}


class SubscriptionError(Exception):
    pass


class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    plan: str
    billing_cycle: str
    status: str = "trialing"
    trial_end: datetime
    renewal_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UsageRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscription_id: str
    metric: str
    value: float
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChurnRisk(BaseModel):
    subscription_id: str
    score: float
    factors: list[str]
    risk_level: str


class SaaSAutomationEngine:
    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}
        self._usage: list[UsageRecord] = []

    def create_subscription(
        self, customer_id: str, plan: str, billing_cycle: str
    ) -> Subscription:
        now = datetime.now(timezone.utc)
        trial_end = now + timedelta(days=14)
        months = BILLING_CYCLE_MONTHS.get(billing_cycle, 1)
        renewal_date = trial_end + timedelta(days=30 * months)
        sub = Subscription(
            customer_id=customer_id,
            plan=plan,
            billing_cycle=billing_cycle,
            status="trialing",
            trial_end=trial_end,
            renewal_date=renewal_date,
        )
        self._subscriptions[sub.id] = sub
        return sub

    def process_renewal(self, subscription_id: str) -> Subscription:
        sub = self._subscriptions[subscription_id]
        if sub.status == "cancelled":
            raise SubscriptionError(f"Subscription {subscription_id} is cancelled.")
        months = BILLING_CYCLE_MONTHS.get(sub.billing_cycle, 1)
        sub.renewal_date = sub.renewal_date + timedelta(days=30 * months)
        sub.status = "active"
        return sub

    def track_usage(
        self, subscription_id: str, metric: str, value: float
    ) -> UsageRecord:
        record = UsageRecord(
            subscription_id=subscription_id, metric=metric, value=value
        )
        self._usage.append(record)
        return record

    def calculate_mrr(self, subscriptions: list[Subscription]) -> float:
        mrr = 0.0
        for sub in subscriptions:
            if sub.status in ("active", "trialing"):
                monthly_price = PLAN_PRICES.get(sub.plan, 0.0)
                if sub.billing_cycle == "annual":
                    monthly_price = monthly_price * 10 / 12
                mrr += monthly_price
        return round(mrr, 2)

    def detect_churn_risk(self, subscription_id: str) -> ChurnRisk:
        sub = self._subscriptions[subscription_id]
        score = 0.0
        factors: list[str] = []

        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        recent = [
            r
            for r in self._usage
            if r.subscription_id == subscription_id and r.recorded_at >= cutoff
        ]
        if not recent:
            score += 50.0
            factors.append("no_usage_14d")

        if sub.status == "trialing":
            score += 20.0
            factors.append("still_trialing")

        if sub.plan == "starter":
            score += 10.0
            factors.append("low_tier_plan")

        risk_level = "low" if score < 30 else "medium" if score < 60 else "high"
        return ChurnRisk(
            subscription_id=subscription_id,
            score=round(score, 2),
            factors=factors,
            risk_level=risk_level,
        )
