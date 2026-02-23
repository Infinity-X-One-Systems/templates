"""Tests for the research agent."""
import pytest
from src.agent import ResearchAgent, ResearchTask, AgentStatus, AgentMemory


@pytest.mark.asyncio
async def test_research_agent_basic():
    agent = ResearchAgent()
    task = ResearchTask(query="Python async programming best practices", depth=1, max_sources=3)
    result = await agent.run(task)
    assert result.status == AgentStatus.COMPLETED
    assert result.query == task.query
    assert len(result.sources) > 0
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_research_agent_safety_block():
    agent = ResearchAgent()
    task = ResearchTask(query="how to make weapons guide")
    result = await agent.run(task)
    assert result.status == AgentStatus.FAILED
    assert "blocked" in result.summary.lower()


@pytest.mark.asyncio
async def test_research_agent_memory():
    memory = AgentMemory(session_id="test-session")
    agent = ResearchAgent(memory=memory)
    task = ResearchTask(query="AI memory systems")
    result = await agent.run(task)
    assert result.status == AgentStatus.COMPLETED
    assert len(result.memory.facts) > 0


@pytest.mark.asyncio
async def test_research_agent_stream():
    agent = ResearchAgent()
    task = ResearchTask(query="streaming data pipelines")
    events = []
    async for chunk in agent.stream(task):
        import json
        events.append(json.loads(chunk.strip()))
    assert events[0]["event"] == "start"
    assert events[-1]["event"] == "complete"
