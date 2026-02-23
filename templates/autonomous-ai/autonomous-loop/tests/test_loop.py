import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from loop import AutonomousLoop, GovernanceLimits, LoopStatus


def test_start_loop():
    loop = AutonomousLoop(goal="Search the web for AI news")
    state = loop.start()
    assert state.status == LoopStatus.RUNNING
    assert state.started_at is not None
    assert state.goal == "Search the web for AI news"


def test_observe_and_act():
    loop = AutonomousLoop(goal="Process data")
    loop.start()
    obs = loop.observe({"data": "some sensor reading"})
    assert obs.iteration == 0
    assert obs.data == {"data": "some sensor reading"}

    action = loop.decide_action("process", {"key": "value"}, cost_usd=0.01)
    executed = loop.execute_action(action)
    assert executed.executed is True
    assert executed.result == {"status": "simulated", "action": "process"}
    assert loop.state.total_cost_usd == pytest.approx(0.01)


def test_budget_limit_blocks_action():
    limits = GovernanceLimits(max_cost_usd=0.50)
    loop = AutonomousLoop(goal="Expensive task", limits=limits)
    loop.start()
    action = loop.decide_action("llm_call", {}, cost_usd=0.60)
    with pytest.raises(ValueError, match="exceed budget"):
        loop.execute_action(action)
    assert loop.state.status == LoopStatus.BUDGET_EXCEEDED


def test_irreversible_action_blocked_by_default():
    loop = AutonomousLoop(goal="Delete files")
    loop.start()
    action = loop.decide_action("delete_files", {"path": "/tmp/data"}, reversible=False)
    with pytest.raises(PermissionError, match="human approval"):
        loop.execute_action(action)
    assert loop.state.status == LoopStatus.HUMAN_REQUIRED


def test_advance_and_complete():
    limits = GovernanceLimits(max_iterations=3)
    loop = AutonomousLoop(goal="Finite task", limits=limits)
    loop.start()
    assert loop.advance_iteration() is True   # iteration → 1
    assert loop.advance_iteration() is True   # iteration → 2
    assert loop.advance_iteration() is False  # iteration → 3, hits max
    assert loop.state.status == LoopStatus.FAILED

    # mark_complete can override to success
    loop.state.status = LoopStatus.RUNNING
    final = loop.mark_complete(goal_achieved=True)
    assert final.goal_achieved is True
    assert final.status == LoopStatus.COMPLETE
    assert final.completed_at is not None
