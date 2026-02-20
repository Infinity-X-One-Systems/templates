"""Tests for the validator agent."""
import pytest
from src.agent import ValidatorAgent, ValidationRule


@pytest.mark.asyncio
async def test_validate_valid_json():
    agent = ValidatorAgent()
    schema = {"required": ["name", "email"], "properties": {"name": {"type": "string"}, "email": {"type": "string"}}}
    result = await agent.validate_json({"name": "Alice", "email": "alice@example.com"}, schema)
    assert result.passed
    assert result.errors == 0


@pytest.mark.asyncio
async def test_validate_missing_required_field():
    agent = ValidatorAgent()
    schema = {"required": ["name", "email"], "properties": {}}
    result = await agent.validate_json({"name": "Alice"}, schema)
    assert not result.passed
    assert result.errors > 0


@pytest.mark.asyncio
async def test_validate_code_security():
    agent = ValidatorAgent()
    bad_code = 'api_key = "sk-abc123secretkey"'
    result = await agent.validate_code(bad_code, language="python")
    assert not result.passed


@pytest.mark.asyncio
async def test_validate_clean_code():
    agent = ValidatorAgent()
    good_code = 'import os\napi_key = os.environ["API_KEY"]\n'
    result = await agent.validate_code(good_code, language="python")
    assert result.passed


@pytest.mark.asyncio
async def test_validate_manifest():
    agent = ValidatorAgent()
    manifest = {"manifest_version": "1.0", "system_name": "test", "org": "test-org", "components": {}}
    result = await agent.validate_manifest(manifest)
    assert result.passed
