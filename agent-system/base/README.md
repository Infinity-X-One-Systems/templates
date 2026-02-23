# AgentBase

The universal Python base class for all Infinity agents.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.agent_base import AgentBase, CapabilityRef

agent = AgentBase(name="MyAgent", role="worker")
agent.add_capability(CapabilityRef(category="skills", name="code-generation"))
agent.remember("task_count", 0)

result = agent.execute_task({"id": "t1", "name": "test", "input": "hello"})
print(result.success, result.output)

# Serialize to dict (for storage or transport)
manifest = agent.to_manifest()

# Restore from dict
restored = AgentBase.from_manifest(manifest)
```

## Subclassing

Override `_run(self, task: dict) -> Any` to implement custom agent logic:

```python
class SummaryAgent(AgentBase):
    def _run(self, task: dict):
        text = task.get("input", "")
        return {"summary": text[:100] + "..."}
```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```
