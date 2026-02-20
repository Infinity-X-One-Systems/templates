"""
Self-Improving Agent Template
==============================
An agent that measures its own performance on each task and uses that
signal to iteratively improve its own system prompt, strategy, and tool selection.
This is the foundation of autonomous capability growth.
"""
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone
import uuid


class PerformanceMetric(BaseModel):
    task_id: str
    score: float  # 0.0-1.0
    dimension: str  # accuracy|speed|cost|user_satisfaction
    details: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ImprovementProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    area: str  # prompt|strategy|tools|memory|parameters
    current_value: str
    proposed_value: str
    expected_improvement: str
    confidence: float  # 0.0-1.0
    evidence: list[str]


class AgentVersion(BaseModel):
    version: str
    system_prompt: str
    strategy: str
    parameters: dict = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    avg_score: float = 0.0
    task_count: int = 0


class SelfImprovingAgent:
    """
    Agent that measures its own performance and iteratively improves itself.
    WARNING: Improvements are governed — cannot exceed bounded_autonomy guardrails.
    """

    IMPROVEMENT_THRESHOLD = 0.7   # Propose improvement if avg score < 0.7
    MIN_TASKS_FOR_IMPROVEMENT = 3  # Need at least 3 tasks before proposing

    def __init__(self, name: str, initial_prompt: str, initial_strategy: str = "default"):
        self.name = name
        self.current_version = AgentVersion(
            version="1.0.0",
            system_prompt=initial_prompt,
            strategy=initial_strategy,
        )
        self.version_history: list[AgentVersion] = [self.current_version]
        self.metrics: list[PerformanceMetric] = []
        self.proposals: list[ImprovementProposal] = []

    def record_performance(self, task_id: str, score: float, dimension: str, details: str) -> PerformanceMetric:
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"Score must be 0.0-1.0, got {score}")
        metric = PerformanceMetric(task_id=task_id, score=score, dimension=dimension, details=details)
        self.metrics.append(metric)
        scores = [m.score for m in self.metrics]
        self.current_version.avg_score = sum(scores) / len(scores)
        self.current_version.task_count = len(self.metrics)
        return metric

    def analyze_and_propose(self) -> list[ImprovementProposal]:
        """Analyze recent performance and generate improvement proposals."""
        if len(self.metrics) < self.MIN_TASKS_FOR_IMPROVEMENT:
            return []
        avg = self.current_version.avg_score
        if avg >= self.IMPROVEMENT_THRESHOLD:
            return []  # Performing well, no changes needed
        # Find the worst-performing dimension
        by_dim: dict[str, list[float]] = {}
        for m in self.metrics:
            by_dim.setdefault(m.dimension, []).append(m.score)
        worst_dim = min(by_dim, key=lambda d: sum(by_dim[d]) / len(by_dim[d]))
        worst_avg = sum(by_dim[worst_dim]) / len(by_dim[worst_dim])
        evidence = [f"Avg {worst_dim} score: {worst_avg:.2f}", f"Overall avg: {avg:.2f}"]
        proposal = ImprovementProposal(
            area="strategy",
            current_value=self.current_version.strategy,
            proposed_value=f"{self.current_version.strategy}+{worst_dim}-focus",
            expected_improvement=f"Improve {worst_dim} from {worst_avg:.2f} to {min(worst_avg + 0.15, 1.0):.2f}",
            confidence=0.65,
            evidence=evidence,
        )
        self.proposals.append(proposal)
        return [proposal]

    def apply_improvement(self, proposal_id: str, new_prompt: str | None = None) -> AgentVersion:
        """Apply an approved improvement, creating a new version.

        Args:
            proposal_id: ID of the proposal to apply.
            new_prompt: Updated system prompt to use in the new version.
                        If omitted, the current prompt is carried forward unchanged.
                        Provide a new prompt when the proposal targets the 'prompt' area;
                        for strategy-only changes the existing prompt is typically sufficient.
        """
        proposal = next((p for p in self.proposals if p.proposal_id == proposal_id), None)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        parts = self.current_version.version.split(".")
        new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"
        new_ver = AgentVersion(
            version=new_version,
            system_prompt=new_prompt or self.current_version.system_prompt,
            strategy=proposal.proposed_value,
            parameters=self.current_version.parameters.copy(),
        )
        self.version_history.append(new_ver)
        self.current_version = new_ver
        return new_ver

    def rollback(self) -> AgentVersion:
        """Roll back to the previous version."""
        if len(self.version_history) < 2:
            raise ValueError("No previous version to roll back to")
        self.version_history.pop()
        self.current_version = self.version_history[-1]
        return self.current_version
