"""
Research Agent — Infinity Template Library
Autonomous web research agent with memory integration, tool use, and safety guardrails.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ToolCall(BaseModel):
    tool: str
    args: dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None


class AgentMemory(BaseModel):
    """Persistent memory interface contract."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    facts: list[str] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

    def add_fact(self, fact: str) -> None:
        self.facts.append(fact)
        self.updated_at = datetime.now(tz=timezone.utc).isoformat()

    def to_context(self) -> str:
        if not self.facts:
            return "No prior context."
        return "\n".join(f"- {f}" for f in self.facts[-20:])  # Cap at 20 most recent


class ResearchTask(BaseModel):
    query: str
    depth: int = Field(default=2, ge=1, le=5)
    max_sources: int = Field(default=10, ge=1, le=50)
    output_format: str = "markdown"  # "markdown" | "json" | "plain"
    safety_level: str = "standard"  # "strict" | "standard" | "permissive"


class ResearchResult(BaseModel):
    task_id: str
    query: str
    summary: str
    sources: list[dict[str, str]]
    facts: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    status: AgentStatus
    memory: AgentMemory
    created_at: str


class ResearchAgent:
    """
    Autonomous research agent that:
    1. Decomposes queries into sub-tasks
    2. Executes web/database searches
    3. Synthesises findings
    4. Stores facts in memory
    5. Applies safety guardrails
    """

    SAFETY_BLOCKED_PATTERNS = [
        "how to make weapons",
        "illegal activities",
        "personal information of individuals",
    ]

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        memory: Optional[AgentMemory] = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.memory = memory or AgentMemory()
        self._tools: dict[str, Any] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self._tools = {
            "web_search": self._tool_web_search,
            "summarize": self._tool_summarize,
            "extract_facts": self._tool_extract_facts,
        }

    def register_tool(self, name: str, fn: Any) -> None:
        """Extend the agent with custom tools."""
        self._tools[name] = fn

    def _check_safety(self, query: str) -> Optional[str]:
        """Return a blocked reason string if the query fails safety checks."""
        q_lower = query.lower()
        for pattern in self.SAFETY_BLOCKED_PATTERNS:
            if pattern in q_lower:
                return f"Query blocked by safety guardrails: matches pattern '{pattern}'"
        return None

    async def _tool_web_search(self, query: str, max_results: int = 5) -> list[dict[str, str]]:
        """
        Placeholder for actual web search integration.
        Replace with SerpAPI, Brave Search, or similar in production.
        """
        await asyncio.sleep(0)  # Simulate async IO
        return [
            {"title": f"Result for: {query}", "url": f"https://example.com/search?q={query}", "snippet": f"Relevant content about {query}"}
        ]

    async def _tool_summarize(self, text: str, max_tokens: int = 500) -> str:
        """Summarize text using the configured LLM."""
        await asyncio.sleep(0)
        return f"Summary of {len(text)} chars: {text[:200]}..."

    async def _tool_extract_facts(self, text: str) -> list[str]:
        """Extract key facts from text."""
        await asyncio.sleep(0)
        return [f"Fact extracted from research: {text[:100]}"]

    async def run(self, task: ResearchTask) -> ResearchResult:
        """Execute a research task end-to-end."""
        task_id = str(uuid4())

        # Safety check
        blocked = self._check_safety(task.query)
        if blocked:
            return ResearchResult(
                task_id=task_id,
                query=task.query,
                summary=blocked,
                sources=[],
                facts=[],
                confidence=0.0,
                status=AgentStatus.FAILED,
                memory=self.memory,
                created_at=datetime.now(tz=timezone.utc).isoformat(),
            )

        # Execute research pipeline
        search_results = await self._tool_web_search(task.query, max_results=task.max_sources)
        combined_text = " ".join(r.get("snippet", "") for r in search_results)
        summary = await self._tool_summarize(combined_text)
        facts = await self._tool_extract_facts(combined_text)

        # Store in memory
        for fact in facts:
            self.memory.add_fact(fact)

        return ResearchResult(
            task_id=task_id,
            query=task.query,
            summary=summary,
            sources=search_results,
            facts=facts,
            confidence=0.85,
            status=AgentStatus.COMPLETED,
            memory=self.memory,
            created_at=datetime.now(tz=timezone.utc).isoformat(),
        )

    async def stream(self, task: ResearchTask) -> AsyncIterator[str]:
        """Stream research progress as JSON lines."""
        yield json.dumps({"event": "start", "task_id": str(uuid4()), "query": task.query}) + "\n"
        result = await self.run(task)
        yield json.dumps({"event": "complete", "result": result.model_dump()}) + "\n"
