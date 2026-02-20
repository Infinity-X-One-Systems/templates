from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone
import uuid


class CapabilityRef(BaseModel):
    category: str  # upgrades|skills|knowledge|capabilities|accessibility|communication|blueprints|tools|memory|governance
    name: str
    version: str = "1.0.0"
    config: dict = Field(default_factory=dict)


class AgentMemoryEntry(BaseModel):
    key: str
    value: Any
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentState(BaseModel):
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    capabilities: list[CapabilityRef] = Field(default_factory=list)
    memory: list[AgentMemoryEntry] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "idle"  # idle|running|paused|error|complete
    iteration: int = 0
    metadata: dict = Field(default_factory=dict)


class TaskResult(BaseModel):
    task_id: str
    agent_id: str
    success: bool
    output: Any
    error: Optional[str] = None
    duration_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentBase:
    """Universal agent base. All Infinity agents inherit from this."""

    def __init__(self, name: str, role: str, capabilities: list[CapabilityRef] | None = None):
        self.state = AgentState(name=name, role=role, capabilities=capabilities or [])

    def add_capability(self, cap: CapabilityRef) -> None:
        """Add a capability to this agent."""
        self.state.capabilities.append(cap)

    def remove_capability(self, category: str, name: str) -> bool:
        """Remove a capability. Returns True if found and removed."""
        before = len(self.state.capabilities)
        self.state.capabilities = [
            c for c in self.state.capabilities
            if not (c.category == category and c.name == name)
        ]
        return len(self.state.capabilities) < before

    def remember(self, key: str, value: Any) -> None:
        """Write a value to agent memory."""
        for entry in self.state.memory:
            if entry.key == key:
                entry.value = value
                entry.timestamp = datetime.now(timezone.utc).isoformat()
                return
        self.state.memory.append(AgentMemoryEntry(key=key, value=value))

    def recall(self, key: str, default: Any = None) -> Any:
        """Read a value from agent memory."""
        for entry in self.state.memory:
            if entry.key == key:
                return entry.value
        return default

    def execute_task(self, task: dict) -> TaskResult:
        """
        Override in subclasses. Base implementation validates task schema.
        task must have: {id, name, input}
        """
        import time
        start = time.monotonic()
        task_id = task.get("id", str(uuid.uuid4()))
        self.state.status = "running"
        self.state.iteration += 1
        try:
            result = self._run(task)
            self.state.status = "idle"
            return TaskResult(
                task_id=task_id,
                agent_id=self.state.agent_id,
                success=True,
                output=result,
                duration_ms=(time.monotonic() - start) * 1000,
            )
        except Exception as exc:
            self.state.status = "error"
            return TaskResult(
                task_id=task_id,
                agent_id=self.state.agent_id,
                success=False,
                output=None,
                error=str(exc),
                duration_ms=(time.monotonic() - start) * 1000,
            )

    def _run(self, task: dict) -> Any:
        """Override this method in subclasses."""
        return {"echo": task.get("input")}

    def get_capabilities_by_category(self, category: str) -> list[CapabilityRef]:
        return [c for c in self.state.capabilities if c.category == category]

    def has_capability(self, category: str, name: str) -> bool:
        return any(c.category == category and c.name == name for c in self.state.capabilities)

    def to_manifest(self) -> dict:
        """Export agent state as a manifest dict."""
        return self.state.model_dump()

    @classmethod
    def from_manifest(cls, manifest: dict) -> "AgentBase":
        """Reconstruct agent from a manifest dict."""
        state = AgentState(**manifest)
        agent = cls.__new__(cls)
        agent.state = state
        return agent
