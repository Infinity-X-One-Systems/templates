# Infinity Agent System

The **Agent System** is the core capability framework of the Infinity Template Library. It provides a structured, composable architecture that agents use to assemble themselves — or other agents — from a curated catalog of capabilities.

## What Is This?

Every Infinity agent is built from three parts:

1. **`AgentBase`** — A universal Python base class (Pydantic v2) that defines agent identity, memory, capability references, task execution, and manifest serialization.
2. **Capability Manifests** — JSON catalogs organized into 10 categories that enumerate every building block an agent can use.
3. **Contracts** — JSON Schema files that enforce the agent interface and capability manifest structure.

---

## Capability Categories

| Category | Description |
|---|---|
| `upgrades` | Runtime enhancements: streaming, vision, web search, autonomous loop |
| `skills` | Executable skills: code generation, data analysis, market research |
| `knowledge` | Domain knowledge: real estate, financial markets, legal, AI/ML |
| `capabilities` | Core cognitive functions: reasoning, planning, summarization, orchestration |
| `accessibility` | How the agent is invoked: REST API, CLI, webhooks, GitHub Actions |
| `communication` | How the agent reports: Slack, GitHub PRs, Google Docs, webhooks |
| `blueprints` | Pre-wired role bundles ready to deploy: research-analyst, code-builder, etc. |
| `tools` | LLM providers and external APIs: OpenAI, Ollama, GitHub, vector-db |
| `memory` | Persistence backends: in-process, Redis, JSON file, vector semantic |
| `governance` | Behavioral constraints: cost budgets, human approval, audit logs |

---

## Building an Agent from Capabilities

```python
from src.agent_base import AgentBase, CapabilityRef

agent = AgentBase(
    name="MarketScout",
    role="research-analyst",
    capabilities=[
        CapabilityRef(category="skills",        name="market-research"),
        CapabilityRef(category="skills",        name="data-analysis"),
        CapabilityRef(category="knowledge",     name="financial-markets"),
        CapabilityRef(category="capabilities",  name="reasoning"),
        CapabilityRef(category="tools",         name="openai-llm"),
        CapabilityRef(category="communication", name="google-docs-report"),
        CapabilityRef(category="governance",    name="cost-budget", config={"max_usd": 0.50}),
        CapabilityRef(category="memory",        name="redis-kv"),
    ]
)
```

---

## Using AgentBase

```python
# Execute a task
result = agent.execute_task({"id": "t1", "name": "research", "input": "Analyze SaaS churn trends"})
print(result.success, result.output)

# Agent memory
agent.remember("last_report", "Q4-2024-churn-analysis.pdf")
doc = agent.recall("last_report")

# Introspect capabilities
tools = agent.get_capabilities_by_category("tools")
has_vision = agent.has_capability("upgrades", "vision")

# Serialize / deserialize
manifest = agent.to_manifest()
restored_agent = AgentBase.from_manifest(manifest)
```

---

## Loading a Blueprint

Blueprints in `capabilities/blueprints/manifest.json` define pre-wired capability bundles. To instantiate one, read the manifest and map each bundle entry to `CapabilityRef` objects:

```python
import json

with open("capabilities/blueprints/manifest.json") as f:
    blueprints = json.load(f)["capabilities"]

blueprint = next(b for b in blueprints if b["name"] == "code-builder")
caps = [
    CapabilityRef(category=cat, name=skill)
    for cat, skills in blueprint["bundle"].items()
    for skill in skills
]
agent = AgentBase(name="CodeBot", role="code-builder", capabilities=caps)
```

---

## Connecting to the Control Plane

Agents report status to the Infinity Control Plane by:

1. Calling `agent.to_manifest()` and POSTing to the control plane's agent registry endpoint.
2. Using the `communication/dashboard-update` capability to push task results.
3. Writing decisions to `memory/decision-log` and telemetry to `memory/telemetry-stream`.

---

## Capability Category Links

- [`capabilities/upgrades/`](capabilities/upgrades/) — Runtime upgrades
- [`capabilities/skills/`](capabilities/skills/) — Executable skills
- [`capabilities/knowledge/`](capabilities/knowledge/) — Domain knowledge
- [`capabilities/capabilities/`](capabilities/capabilities/) — Core capabilities
- [`capabilities/accessibility/`](capabilities/accessibility/) — Access interfaces
- [`capabilities/communication/`](capabilities/communication/) — Output channels
- [`capabilities/blueprints/`](capabilities/blueprints/) — Pre-wired blueprints
- [`capabilities/tools/`](capabilities/tools/) — Pluggable tools
- [`capabilities/memory/`](capabilities/memory/) — Memory backends
- [`capabilities/governance/`](capabilities/governance/) — Governance rules
- [`base/`](base/) — AgentBase Python package
- [`contracts/`](contracts/) — JSON Schema contracts

---

## Directory Structure

```
agent-system/
  base/                   ← AgentBase Python package
  capabilities/           ← 10 capability category catalogs
  contracts/              ← JSON Schema interface contracts
  README.md               ← This file
```
