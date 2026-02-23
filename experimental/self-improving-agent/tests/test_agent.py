import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from agent import SelfImprovingAgent


def test_record_performance_updates_avg_score():
    """Recording multiple tasks correctly updates the running average."""
    agent = SelfImprovingAgent("test-agent", "You are a helpful assistant.")
    agent.record_performance("t1", 0.8, "accuracy", "Good result")
    agent.record_performance("t2", 0.6, "accuracy", "Mediocre result")
    assert agent.current_version.avg_score == pytest.approx(0.7)
    assert agent.current_version.task_count == 2


def test_no_proposal_when_too_few_tasks():
    """No proposals generated when fewer than MIN_TASKS_FOR_IMPROVEMENT tasks exist."""
    agent = SelfImprovingAgent("test-agent", "You are a helpful assistant.")
    agent.record_performance("t1", 0.3, "accuracy", "Bad")
    agent.record_performance("t2", 0.3, "speed", "Bad")
    proposals = agent.analyze_and_propose()
    assert proposals == []


def test_propose_improvement_when_below_threshold():
    """An improvement proposal is generated when avg score is below 0.7."""
    agent = SelfImprovingAgent("test-agent", "You are a helpful assistant.")
    for i in range(3):
        agent.record_performance(f"t{i}", 0.4, "accuracy", "Low accuracy")
    proposals = agent.analyze_and_propose()
    assert len(proposals) == 1
    assert proposals[0].area == "strategy"
    assert "accuracy" in proposals[0].proposed_value


def test_apply_improvement_bumps_version():
    """Applying a proposal creates a new version with an incremented minor version."""
    agent = SelfImprovingAgent("test-agent", "You are a helpful assistant.")
    for i in range(3):
        agent.record_performance(f"t{i}", 0.4, "speed", "Slow")
    proposals = agent.analyze_and_propose()
    assert proposals
    new_ver = agent.apply_improvement(proposals[0].proposal_id, new_prompt="Improved prompt")
    assert new_ver.version == "1.1.0"
    assert new_ver.system_prompt == "Improved prompt"
    assert len(agent.version_history) == 2


def test_rollback_restores_previous_version():
    """Rollback returns the agent to the version before the last improvement."""
    agent = SelfImprovingAgent("test-agent", "Original prompt")
    for i in range(3):
        agent.record_performance(f"t{i}", 0.4, "cost", "Expensive")
    proposals = agent.analyze_and_propose()
    agent.apply_improvement(proposals[0].proposal_id)
    assert agent.current_version.version == "1.1.0"
    rolled = agent.rollback()
    assert rolled.version == "1.0.0"
    assert agent.current_version.version == "1.0.0"
    assert len(agent.version_history) == 1
