"""Construction Workflow Engine – manages projects, milestones, and budget tracking."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Milestone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    due_date: str
    budget_pct: float
    status: str = "pending"
    float_days: int = 0


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    budget: float
    start_date: str
    end_date: str
    status: str = "active"
    phases: List[str] = Field(default_factory=lambda: ["planning", "execution", "closeout"])
    milestones: List[Milestone] = Field(default_factory=list)
    actual_spend: float = 0.0


class BudgetVariance(BaseModel):
    project_id: str
    planned: float
    actual: float
    variance_pct: float


class ConstructionWorkflowEngine:
    """Manages construction projects, milestones, and budget analysis."""

    def __init__(self) -> None:
        self._projects: Dict[str, Project] = {}

    def create_project(
        self, name: str, budget: float, start_date: str, end_date: str
    ) -> Project:
        project = Project(name=name, budget=budget, start_date=start_date, end_date=end_date)
        self._projects[project.id] = project
        return project

    def add_milestone(
        self, project_id: str, name: str, due_date: str, budget_pct: float
    ) -> Milestone:
        project = self._get_project(project_id)
        milestone = Milestone(name=name, due_date=due_date, budget_pct=budget_pct)
        project.milestones.append(milestone)
        return milestone

    def update_milestone_status(
        self, project_id: str, milestone_id: str, status: str
    ) -> Milestone:
        project = self._get_project(project_id)
        for milestone in project.milestones:
            if milestone.id == milestone_id:
                milestone.status = status
                if status == "complete":
                    project.actual_spend += project.budget * (milestone.budget_pct / 100.0)
                return milestone
        raise KeyError(f"Milestone {milestone_id} not found in project {project_id}")

    def calculate_budget_variance(self, project_id: str) -> BudgetVariance:
        project = self._get_project(project_id)
        completed_pct = sum(
            m.budget_pct for m in project.milestones if m.status == "complete"
        )
        planned = project.budget * (completed_pct / 100.0) if project.milestones else 0.0
        actual = project.actual_spend
        variance_pct = ((actual - planned) / planned * 100.0) if planned else 0.0
        return BudgetVariance(
            project_id=project_id,
            planned=planned,
            actual=actual,
            variance_pct=round(variance_pct, 2),
        )

    def get_critical_path(self, project_id: str) -> List[Milestone]:
        project = self._get_project(project_id)
        return [m for m in project.milestones if m.float_days == 0]

    def _get_project(self, project_id: str) -> Project:
        if project_id not in self._projects:
            raise KeyError(f"Project {project_id} not found")
        return self._projects[project_id]


if __name__ == "__main__":
    engine = ConstructionWorkflowEngine()
    p = engine.create_project("Office Tower", 5_000_000.0, "2025-01-01", "2026-12-31")
    print(f"Project created: {p.name} (id={p.id})")
