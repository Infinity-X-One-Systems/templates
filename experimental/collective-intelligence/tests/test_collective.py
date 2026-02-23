import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from collective import CollectiveIntelligence, AgentRole


def test_add_agents():
    """Agents are registered and retrievable from the collective."""
    ci = CollectiveIntelligence()
    a1 = ci.add_agent("Alice", AgentRole.ANALYST, "finance")
    a2 = ci.add_agent("Bob", AgentRole.CRITIC, "engineering")
    assert len(ci.agents) == 2
    assert ci.agents[0].name == "Alice"
    assert ci.agents[1].role == AgentRole.CRITIC


def test_submit_opinion():
    """An opinion can be submitted for a specific round of a decision."""
    from collective import CollectiveDecision
    ci = CollectiveIntelligence()
    agent = ci.add_agent("Carol", AgentRole.DOMAIN_EXPERT, "medicine")
    decision = CollectiveDecision(question="Is treatment X safe?")
    opinion = ci.submit_opinion(decision, 1, agent.agent_id, "yes", 0.9, "Clinical trials show safety")
    assert opinion.answer == "yes"
    assert opinion.confidence == 0.9
    assert len(decision.rounds) == 1
    assert len(decision.rounds[0].opinions) == 1


def test_consensus_reached_with_agreement():
    """Consensus is reached when agents strongly agree on the same answer."""
    ci = CollectiveIntelligence()
    a1 = ci.add_agent("A", AgentRole.ANALYST, "data", weight=1.0)
    a2 = ci.add_agent("B", AgentRole.CRITIC, "data", weight=1.0)
    a3 = ci.add_agent("C", AgentRole.SYNTHESIZER, "data", weight=1.0)
    from collective import CollectiveDecision
    decision = CollectiveDecision(question="Best framework?")
    ci.submit_opinion(decision, 1, a1.agent_id, "FastAPI", 0.95, "High performance")
    ci.submit_opinion(decision, 1, a2.agent_id, "FastAPI", 0.90, "Well-maintained")
    ci.submit_opinion(decision, 1, a3.agent_id, "FastAPI", 0.85, "Ecosystem fit")
    reached = ci.check_consensus(decision, 1)
    assert reached
    assert decision.final_answer == "FastAPI"
    assert decision.confidence >= 0.70


def test_no_consensus_when_split():
    """No consensus when agents are evenly split."""
    ci = CollectiveIntelligence()
    a1 = ci.add_agent("A", AgentRole.ANALYST, "ops", weight=1.0)
    a2 = ci.add_agent("B", AgentRole.CRITIC, "ops", weight=1.0)
    from collective import CollectiveDecision
    decision = CollectiveDecision(question="Deploy now?")
    ci.submit_opinion(decision, 1, a1.agent_id, "yes", 1.0, "All tests pass")
    ci.submit_opinion(decision, 1, a2.agent_id, "no", 1.0, "Risk too high")
    reached = ci.check_consensus(decision, 1)
    assert not reached
    assert decision.final_answer is None


def test_deliberate_reaches_decision():
    """Full deliberation cycle always produces a final answer."""
    ci = CollectiveIntelligence()
    ci.add_agent("Analyst", AgentRole.ANALYST, "general", weight=1.0)
    ci.add_agent("Synthesizer", AgentRole.SYNTHESIZER, "general", weight=1.0)

    def opinion_fn(agent, question, round_num, prior):
        # All agents agree — fast consensus
        return ("42", 0.95, f"{agent.name} reasoning for round {round_num}")

    decision = ci.deliberate("What is the answer?", opinion_fn)
    assert decision.final_answer is not None
    assert len(decision.rounds) >= 1
