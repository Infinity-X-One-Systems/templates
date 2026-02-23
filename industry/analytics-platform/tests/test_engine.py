"""Tests for AnalyticsPlatformEngine."""

from datetime import datetime, timedelta, timezone

import pytest
from src.engine import AnalyticsPlatformEngine


@pytest.fixture
def engine():
    return AnalyticsPlatformEngine()


def test_ingest_event(engine):
    event = engine.ingest_event("web", "page_view", "user-1", {"page": "/home"})
    assert event.id is not None
    assert event.event_type == "page_view"
    assert event.timestamp is not None


def test_get_event_count(engine):
    now = datetime.now(timezone.utc)
    engine.ingest_event("web", "click", "u1")
    engine.ingest_event("web", "click", "u2")
    engine.ingest_event("web", "page_view", "u1")
    count = engine.get_event_count(
        "web", "click", now - timedelta(seconds=10), now + timedelta(seconds=10)
    )
    assert count == 2


def test_calculate_funnel(engine):
    events = []
    for uid in ["u1", "u2", "u3"]:
        events.append(engine.ingest_event("app", "visit", uid))
    for uid in ["u1", "u2"]:
        events.append(engine.ingest_event("app", "signup", uid))
    for uid in ["u1"]:
        events.append(engine.ingest_event("app", "purchase", uid))

    funnel = engine.calculate_funnel(events, ["visit", "signup", "purchase"])
    assert funnel.step_counts == [3, 2, 1]
    assert funnel.overall_rate == pytest.approx(33.33, abs=0.01)


def test_generate_dashboard_data(engine):
    engine.ingest_event("mobile", "open", "u1")
    engine.ingest_event("mobile", "open", "u2")
    engine.ingest_event("mobile", "close", "u1")
    dashboard = engine.generate_dashboard_data("mobile", 1)
    assert dashboard.total_events == 3
    assert dashboard.unique_users == 2
    assert dashboard.breakdown["open"] == 2


def test_compute_cohort_retention(engine):
    now = datetime.now(timezone.utc)
    # Day-0 cohort: u1, u2, u3 join
    for uid in ["u1", "u2", "u3"]:
        e = engine.ingest_event("app", "join", uid)
        e.timestamp = now
    # Period 1 (day+1): u1 and u2 return
    for uid in ["u1", "u2"]:
        e = engine.ingest_event("app", "return", uid)
        e.timestamp = now + timedelta(days=1)
    # Period 2 (day+2): only u1 returns
    e = engine.ingest_event("app", "return", "u1")
    e.timestamp = now + timedelta(days=2)

    all_events = engine._events
    retention = engine.compute_cohort_retention(all_events, now, 2)
    assert len(retention) == 2
    assert retention[0] == pytest.approx(66.67, abs=0.01)
    assert retention[1] == pytest.approx(33.33, abs=0.01)
