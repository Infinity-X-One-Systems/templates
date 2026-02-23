"""Tests for the builder agent."""
import pytest
import tempfile
from pathlib import Path
from src.agent import BuilderAgent, BuildTask


@pytest.mark.asyncio
async def test_build_api():
    with tempfile.TemporaryDirectory() as tmp:
        agent = BuilderAgent()
        task = BuildTask(system_type="api", name="test-api", description="Test API", output_dir=tmp)
        result = await agent.build(task)
        assert result.success
        assert len(result.files_generated) > 0
        assert (Path(tmp) / "test-api" / "README.md").exists()


@pytest.mark.asyncio
async def test_build_frontend():
    with tempfile.TemporaryDirectory() as tmp:
        agent = BuilderAgent()
        task = BuildTask(system_type="frontend", name="test-frontend", description="Test Frontend", output_dir=tmp)
        result = await agent.build(task)
        assert result.success
        assert "package.json" in result.files_generated


@pytest.mark.asyncio
async def test_build_agent():
    with tempfile.TemporaryDirectory() as tmp:
        agent = BuilderAgent()
        task = BuildTask(system_type="agent", name="test-agent", description="Test Agent", output_dir=tmp)
        result = await agent.build(task)
        assert result.success
        assert "src/agent.py" in result.files_generated
