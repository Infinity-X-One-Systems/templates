import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from codriver import HumanAICoDriver


def test_set_intent():
    """Human sets goal and constraints; context reflects them."""
    driver = HumanAICoDriver()
    ctx = driver.set_intent(
        goal="Build a REST API",
        constraints=["no external APIs", "Python only"],
        blocked_actions=["delete production database"],
    )
    assert ctx.intent is not None
    assert ctx.intent.goal == "Build a REST API"
    assert "Python only" in ctx.intent.constraints
    assert "delete production database" in ctx.intent.blocked_actions


def test_ai_propose_low_risk():
    """Low-risk, reversible proposal does not require approval."""
    driver = HumanAICoDriver()
    driver.set_intent(goal="Optimise query")
    proposal = driver.ai_propose(
        action="Add database index",
        rationale="Speeds up queries by 10x",
        estimated_impact="high",
        risk_level="low",
        reversible=True,
    )
    assert not proposal.requires_approval
    assert proposal.risk_level == "low"


def test_ai_propose_high_risk_requires_approval():
    """High-risk proposal must require human approval."""
    driver = HumanAICoDriver()
    driver.set_intent(goal="Migrate database")
    proposal = driver.ai_propose(
        action="Drop old tables",
        rationale="Clean up after migration",
        estimated_impact="irreversible data loss if wrong",
        risk_level="high",
        reversible=False,
    )
    assert proposal.requires_approval


def test_human_decide_approve():
    """Approved proposal appears in the approved-actions list."""
    driver = HumanAICoDriver()
    driver.set_intent(goal="Deploy service")
    proposal = driver.ai_propose(
        action="run docker-compose up",
        rationale="Starts all services",
        estimated_impact="services become available",
        risk_level="low",
        reversible=True,
    )
    decision = driver.human_decide(proposal.proposal_id, approved=True, comment="LGTM")
    assert decision.human_approved
    assert "run docker-compose up" in driver.get_approved_actions()
    assert driver.context.iterations == 1


def test_auto_approve_requires_approval_raises():
    """auto_approve raises PermissionError for a proposal that needs human review."""
    driver = HumanAICoDriver()
    driver.set_intent(goal="Nuke cache")
    proposal = driver.ai_propose(
        action="flush all Redis keys",
        rationale="Clear stale cache",
        estimated_impact="temporary latency spike",
        risk_level="high",
        reversible=False,
    )
    assert proposal.requires_approval
    with pytest.raises(PermissionError):
        driver.auto_approve(proposal.proposal_id)
