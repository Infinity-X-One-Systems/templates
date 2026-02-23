"""
Autonomous Loop Template
=========================
A self-running agent loop that executes tasks until a goal is achieved
or governance limits are hit (budget, iterations, time).
Implements the OODA loop: Observe → Orient → Decide → Act
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Callable
from datetime import datetime, timezone
from enum import Enum
import uuid

class LoopStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETE = "complete"
    FAILED = "failed"
    BUDGET_EXCEEDED = "budget_exceeded"
    HUMAN_REQUIRED = "human_required"

class GovernanceLimits(BaseModel):
    max_iterations: int = 10
    max_cost_usd: float = 1.0
    max_duration_seconds: float = 300.0
    require_human_above_cost: float = 0.50
    allow_irreversible_actions: bool = False

class LoopObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    iteration: int
    data: Any
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class LoopAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    iteration: int
    action_type: str
    parameters: dict = Field(default_factory=dict)
    cost_usd: float = 0.0
    reversible: bool = True
    executed: bool = False
    result: Optional[Any] = None

class LoopState(BaseModel):
    loop_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    status: LoopStatus = LoopStatus.IDLE
    iteration: int = 0
    total_cost_usd: float = 0.0
    observations: list[LoopObservation] = Field(default_factory=list)
    actions: list[LoopAction] = Field(default_factory=list)
    goal_achieved: bool = False
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class AutonomousLoop:
    """
    OODA-based autonomous execution loop with hard governance limits.
    The loop will STOP if: goal achieved, budget exceeded, max iterations hit,
    or an irreversible action is encountered when not allowed.
    """

    def __init__(self, goal: str, limits: GovernanceLimits | None = None):
        self.state = LoopState(goal=goal)
        self.limits = limits or GovernanceLimits()

    def observe(self, data: Any) -> LoopObservation:
        obs = LoopObservation(iteration=self.state.iteration, data=data)
        self.state.observations.append(obs)
        return obs

    def decide_action(self, action_type: str, parameters: dict,
                      cost_usd: float = 0.0, reversible: bool = True) -> LoopAction:
        action = LoopAction(
            iteration=self.state.iteration,
            action_type=action_type,
            parameters=parameters,
            cost_usd=cost_usd,
            reversible=reversible,
        )
        return action

    def execute_action(self, action: LoopAction,
                       executor_fn: Callable[[LoopAction], Any] | None = None) -> LoopAction:
        """Execute an action, checking governance limits first."""
        if not action.reversible and not self.limits.allow_irreversible_actions:
            self.state.status = LoopStatus.HUMAN_REQUIRED
            raise PermissionError(f"Irreversible action '{action.action_type}' requires human approval")
        projected_cost = self.state.total_cost_usd + action.cost_usd
        if projected_cost > self.limits.max_cost_usd:
            self.state.status = LoopStatus.BUDGET_EXCEEDED
            raise ValueError(f"Action would exceed budget: ${projected_cost:.3f} > ${self.limits.max_cost_usd}")
        if executor_fn:
            action.result = executor_fn(action)
        else:
            action.result = {"status": "simulated", "action": action.action_type}
        action.executed = True
        self.state.total_cost_usd += action.cost_usd
        self.state.actions.append(action)
        return action

    def advance_iteration(self) -> bool:
        """Move to next iteration. Returns False if limits are hit."""
        self.state.iteration += 1
        if self.state.iteration >= self.limits.max_iterations:
            self.state.status = LoopStatus.FAILED
            return False
        return True

    def mark_complete(self, goal_achieved: bool = True) -> LoopState:
        self.state.goal_achieved = goal_achieved
        self.state.status = LoopStatus.COMPLETE if goal_achieved else LoopStatus.FAILED
        self.state.completed_at = datetime.now(timezone.utc).isoformat()
        return self.state

    def start(self) -> LoopState:
        self.state.status = LoopStatus.RUNNING
        self.state.started_at = datetime.now(timezone.utc).isoformat()
        return self.state

    def get_summary(self) -> dict:
        return {
            "goal": self.state.goal,
            "status": self.state.status,
            "iterations": self.state.iteration,
            "total_cost_usd": self.state.total_cost_usd,
            "goal_achieved": self.state.goal_achieved,
            "actions_taken": len([a for a in self.state.actions if a.executed]),
        }
