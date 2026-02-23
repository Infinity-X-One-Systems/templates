"""Analytics Platform Engine - core engine."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class AnalyticsEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    event_type: str
    user_id: str
    properties: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FunnelMetrics(BaseModel):
    steps: list[str]
    step_counts: list[int]
    conversion_rates: list[float]
    overall_rate: float


class DashboardData(BaseModel):
    source: str
    date_range_days: int
    total_events: int
    unique_users: int
    breakdown: dict[str, int]
    trend: list[dict[str, Any]]
    generated_at: datetime


class AnalyticsPlatformEngine:
    def __init__(self) -> None:
        self._events: list[AnalyticsEvent] = []

    def ingest_event(
        self,
        source: str,
        event_type: str,
        user_id: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> AnalyticsEvent:
        event = AnalyticsEvent(
            source=source,
            event_type=event_type,
            user_id=user_id,
            properties=properties or {},
        )
        self._events.append(event)
        return event

    def get_event_count(
        self,
        source: str,
        event_type: str,
        start_date: datetime,
        end_date: datetime,
    ) -> int:
        return sum(
            1
            for e in self._events
            if e.source == source
            and e.event_type == event_type
            and start_date <= e.timestamp <= end_date
        )

    def calculate_funnel(
        self, events: list[AnalyticsEvent], steps: list[str]
    ) -> FunnelMetrics:
        users_per_step: list[set[str]] = []
        for step in steps:
            users = {e.user_id for e in events if e.event_type == step}
            if users_per_step:
                users = users & users_per_step[-1]
            users_per_step.append(users)

        step_counts = [len(s) for s in users_per_step]
        conversion_rates: list[float] = []
        for i, count in enumerate(step_counts):
            if i == 0:
                conversion_rates.append(100.0)
            else:
                prev = step_counts[i - 1]
                conversion_rates.append(round(count / prev * 100.0, 2) if prev > 0 else 0.0)

        overall_rate = (
            round(step_counts[-1] / step_counts[0] * 100.0, 2)
            if steps and step_counts[0] > 0
            else 0.0
        )
        return FunnelMetrics(
            steps=steps,
            step_counts=step_counts,
            conversion_rates=conversion_rates,
            overall_rate=overall_rate,
        )

    def compute_cohort_retention(
        self,
        events: list[AnalyticsEvent],
        cohort_date: datetime,
        periods: int,
    ) -> list[float]:
        cohort_users = {
            e.user_id
            for e in events
            if e.timestamp.date() == cohort_date.date()
        }
        if not cohort_users:
            return [0.0] * periods

        retention: list[float] = []
        for period in range(1, periods + 1):
            period_start = cohort_date + timedelta(days=period)
            period_end = period_start + timedelta(days=1)
            returning = {
                e.user_id
                for e in events
                if period_start <= e.timestamp < period_end
                and e.user_id in cohort_users
            }
            retention.append(round(len(returning) / len(cohort_users) * 100.0, 2))
        return retention

    def generate_dashboard_data(
        self, source: str, date_range_days: int
    ) -> DashboardData:
        cutoff = datetime.now(timezone.utc) - timedelta(days=date_range_days)
        filtered = [
            e for e in self._events if e.source == source and e.timestamp >= cutoff
        ]

        breakdown: dict[str, int] = defaultdict(int)
        for e in filtered:
            breakdown[e.event_type] += 1

        trend_by_day: dict[str, int] = defaultdict(int)
        for e in filtered:
            day = e.timestamp.date().isoformat()
            trend_by_day[day] += 1
        trend = [{"date": d, "count": c} for d, c in sorted(trend_by_day.items())]

        return DashboardData(
            source=source,
            date_range_days=date_range_days,
            total_events=len(filtered),
            unique_users=len({e.user_id for e in filtered}),
            breakdown=dict(breakdown),
            trend=trend,
            generated_at=datetime.now(timezone.utc),
        )
