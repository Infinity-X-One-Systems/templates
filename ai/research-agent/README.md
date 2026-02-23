# Research Agent Template

Autonomous research agent with memory, tool use, and safety guardrails.

## Features
- Query decomposition and multi-step research
- Pluggable tool interface (web search, database, custom)
- Persistent memory interface contract
- Streaming output via async iterator
- Safety guardrails (configurable levels)
- OpenAI-compatible LLM backend

## Quick Start

```bash
pip install -r requirements.txt
python -c "import asyncio; from src.agent import ResearchAgent, ResearchTask; asyncio.run(ResearchAgent().run(ResearchTask(query='AI trends 2025')))"
```

## Memory Interface Contract

The `AgentMemory` model is the universal memory contract used across all agents:
- `session_id`: Unique session identifier
- `facts`: List of extracted facts (capped at 20 for context)
- `tool_calls`: Audit log of all tool invocations

## Prompt Schema

```python
ResearchTask(
    query="Your research question",
    depth=2,           # 1-5: research depth
    max_sources=10,    # 1-50: max sources to consult
    output_format="markdown",  # markdown|json|plain
    safety_level="standard"    # strict|standard|permissive
)
```
