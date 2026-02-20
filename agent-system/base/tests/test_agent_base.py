import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from agent_base import AgentBase, CapabilityRef, AgentState


def test_agent_creation():
    agent = AgentBase(name="TestAgent", role="tester")
    assert agent.state.name == "TestAgent"
    assert agent.state.role == "tester"
    assert agent.state.status == "idle"
    assert agent.state.iteration == 0
    assert isinstance(agent.state.agent_id, str)
    assert len(agent.state.agent_id) == 36  # UUID length


def test_add_remove_capability():
    agent = AgentBase(name="CapAgent", role="worker")
    cap = CapabilityRef(category="skills", name="code-generation")
    agent.add_capability(cap)
    assert agent.has_capability("skills", "code-generation")
    assert len(agent.get_capabilities_by_category("skills")) == 1

    removed = agent.remove_capability("skills", "code-generation")
    assert removed is True
    assert not agent.has_capability("skills", "code-generation")

    not_removed = agent.remove_capability("skills", "nonexistent")
    assert not_removed is False


def test_memory_remember_recall():
    agent = AgentBase(name="MemAgent", role="memorizer")
    agent.remember("project", "infinity")
    assert agent.recall("project") == "infinity"

    # Update existing key
    agent.remember("project", "infinity-v2")
    assert agent.recall("project") == "infinity-v2"
    assert len(agent.state.memory) == 1  # no duplicate entries

    # Default for missing key
    assert agent.recall("missing", default="fallback") == "fallback"


def test_execute_task():
    agent = AgentBase(name="TaskAgent", role="executor")
    task = {"id": "task-001", "name": "echo-test", "input": "hello world"}
    result = agent.execute_task(task)

    assert result.success is True
    assert result.task_id == "task-001"
    assert result.output == {"echo": "hello world"}
    assert result.error is None
    assert result.duration_ms >= 0
    assert agent.state.status == "idle"
    assert agent.state.iteration == 1


def test_manifest_roundtrip():
    agent = AgentBase(
        name="ManifestAgent",
        role="architect",
        capabilities=[CapabilityRef(category="tools", name="openai-llm", version="2.0.0")],
    )
    agent.remember("goal", "build systems")
    agent.state.metadata["owner"] = "team-alpha"

    manifest = agent.to_manifest()
    assert manifest["name"] == "ManifestAgent"
    assert manifest["role"] == "architect"
    assert len(manifest["capabilities"]) == 1
    assert manifest["capabilities"][0]["name"] == "openai-llm"

    restored = AgentBase.from_manifest(manifest)
    assert restored.state.name == "ManifestAgent"
    assert restored.state.agent_id == agent.state.agent_id
    assert restored.has_capability("tools", "openai-llm")
    assert restored.recall("goal") == "build systems"
    assert restored.state.metadata["owner"] == "team-alpha"
