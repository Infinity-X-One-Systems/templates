"""
Human-AI Co-Driver Template
===========================
A new interaction paradigm: Human and AI co-pilot a task together.
- Human provides: goals, constraints, corrections, approvals
- AI provides: execution, suggestions, analysis, memory
- Both build a shared context that improves over time
"""
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone
import uuid


class HumanIntent(BaseModel):
    """What the human wants to accomplish."""
    goal: str
    constraints: list[str] = Field(default_factory=list)
    approved_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    priority: str = "medium"  # low|medium|high|critical


class AIProposal(BaseModel):
    """AI's proposed next action."""
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    rationale: str
    estimated_impact: str
    risk_level: str  # low|medium|high
    requires_approval: bool
    reversible: bool
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CoDriverDecision(BaseModel):
    """Joint human-AI decision."""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    human_approved: bool
    human_comment: Optional[str] = None
    final_action: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SharedContext(BaseModel):
    """Shared memory that both human and AI update."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    intent: Optional[HumanIntent] = None
    proposals: list[AIProposal] = Field(default_factory=list)
    decisions: list[CoDriverDecision] = Field(default_factory=list)
    learnings: list[str] = Field(default_factory=list)
    iterations: int = 0


class HumanAICoDriver:
    """
    Human-AI Co-Driver: shared control system where human and AI
    collaborate as equal partners on complex tasks.
    """

    def __init__(self):
        self.context = SharedContext()

    def set_intent(
        self,
        goal: str,
        constraints: list[str] | None = None,
        approved_actions: list[str] | None = None,
        blocked_actions: list[str] | None = None,
    ) -> SharedContext:
        """Human sets the goal and guardrails."""
        self.context.intent = HumanIntent(
            goal=goal,
            constraints=constraints or [],
            approved_actions=approved_actions or [],
            blocked_actions=blocked_actions or [],
        )
        return self.context

    def ai_propose(
        self,
        action: str,
        rationale: str,
        estimated_impact: str,
        risk_level: str = "low",
        reversible: bool = True,
    ) -> AIProposal:
        """AI proposes an action. High-risk or irreversible actions require approval."""
        requires_approval = risk_level in ("high",) or not reversible
        # Check against blocked actions
        if self.context.intent:
            for blocked in self.context.intent.blocked_actions:
                if blocked.lower() in action.lower():
                    requires_approval = True
        proposal = AIProposal(
            action=action,
            rationale=rationale,
            estimated_impact=estimated_impact,
            risk_level=risk_level,
            requires_approval=requires_approval,
            reversible=reversible,
        )
        self.context.proposals.append(proposal)
        return proposal

    def human_decide(self, proposal_id: str, approved: bool, comment: str | None = None) -> CoDriverDecision:
        """Human approves or rejects an AI proposal."""
        proposal = next((p for p in self.context.proposals if p.proposal_id == proposal_id), None)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        final_action = proposal.action if approved else f"REJECTED: {proposal.action}"
        decision = CoDriverDecision(
            proposal_id=proposal_id,
            human_approved=approved,
            human_comment=comment,
            final_action=final_action,
        )
        self.context.decisions.append(decision)
        self.context.iterations += 1
        return decision

    def auto_approve(self, proposal_id: str) -> CoDriverDecision:
        """Auto-approve a proposal that doesn't require human input."""
        proposal = next((p for p in self.context.proposals if p.proposal_id == proposal_id), None)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        if proposal.requires_approval:
            raise PermissionError(f"Proposal {proposal_id} requires human approval")
        return self.human_decide(proposal_id, approved=True, comment="auto-approved")

    def learn(self, learning: str) -> None:
        """Add a learning to shared context (both human and AI can call this)."""
        self.context.learnings.append(learning)

    def get_approved_actions(self) -> list[str]:
        return [d.final_action for d in self.context.decisions if d.human_approved]

    def get_session_summary(self) -> dict:
        return {
            "session_id": self.context.session_id,
            "goal": self.context.intent.goal if self.context.intent else None,
            "iterations": self.context.iterations,
            "proposals": len(self.context.proposals),
            "approvals": sum(1 for d in self.context.decisions if d.human_approved),
            "rejections": sum(1 for d in self.context.decisions if not d.human_approved),
            "learnings": len(self.context.learnings),
        }
