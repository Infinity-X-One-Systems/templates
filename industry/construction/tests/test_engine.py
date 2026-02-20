"""Tests for ConstructionWorkflowEngine."""
import pytest
from src.engine import ConstructionWorkflowEngine


@pytest.fixture
def engine():
    return ConstructionWorkflowEngine()


def test_create_project(engine):
    project = engine.create_project("Bridge Renovation", 2_000_000.0, "2025-03-01", "2026-03-01")
    assert project.name == "Bridge Renovation"
    assert project.budget == 2_000_000.0
    assert project.status == "active"
    assert len(project.phases) == 3


def test_add_milestone(engine):
    project = engine.create_project("Warehouse Build", 800_000.0, "2025-01-01", "2025-12-31")
    milestone = engine.add_milestone(project.id, "Foundation Complete", "2025-04-01", 25.0)
    assert milestone.name == "Foundation Complete"
    assert milestone.budget_pct == 25.0
    assert milestone.status == "pending"
    assert len(engine._projects[project.id].milestones) == 1


def test_budget_variance(engine):
    project = engine.create_project("Road Paving", 1_000_000.0, "2025-01-01", "2025-10-01")
    m1 = engine.add_milestone(project.id, "Phase 1", "2025-04-01", 50.0)
    engine.update_milestone_status(project.id, m1.id, "complete")
    variance = engine.calculate_budget_variance(project.id)
    assert variance.planned == 500_000.0
    assert variance.actual == 500_000.0
    assert variance.variance_pct == 0.0


def test_critical_path(engine):
    project = engine.create_project("Tower Block", 5_000_000.0, "2025-01-01", "2027-01-01")
    m_critical = engine.add_milestone(project.id, "Steel Frame", "2025-08-01", 30.0)
    m_float = engine.add_milestone(project.id, "Landscaping", "2026-10-01", 5.0)
    project = engine._projects[project.id]
    project.milestones[1].float_days = 30
    critical = engine.get_critical_path(project.id)
    assert len(critical) == 1
    assert critical[0].name == "Steel Frame"
