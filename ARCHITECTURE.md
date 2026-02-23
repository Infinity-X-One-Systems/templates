# Architecture — Infinity Template Library

## Overview

The Infinity Template Library is a composable, production-grade collection of templates enabling complete frontend + backend + AI systems to be assembled in under one hour.

## Directory Structure

```
infinity-template-library/
├── core/                     # Mandatory primitives for every system
│   ├── api-fastapi/          # FastAPI REST API scaffold
│   └── frontend-nextjs/      # Next.js PWA frontend scaffold
├── backend/                  # Backend patterns
│   └── express-api/          # Express.js REST API
├── frontend/                 # Frontend patterns
├── ai/                       # AI agent templates
│   ├── research-agent/       # Autonomous research agent
│   ├── builder-agent/        # Code generation agent
│   ├── financial-agent/      # Financial prediction agent
│   ├── real-estate-agent/    # Distressed property analyzer
│   └── orchestrator/         # Multi-step workflow orchestrator
├── business/                 # Business workflow templates
│   └── crm-automation/       # CRM pipeline automation
├── infrastructure/           # Infrastructure templates
│   └── docker-local-mesh/    # Full Docker development mesh
├── governance/               # TAP governance templates
│   ├── tap-enforcement/      # Policy-Authority-Truth CI workflow
│   ├── test-coverage-gate/   # 80% coverage enforcement
│   └── security-gate/        # SAST + dependency + secret scanning
├── engine/                   # Template composition engine
│   ├── schema/               # JSON manifest schema
│   └── scripts/              # Composition scripts
├── control-panel/            # PWA control panel (template selector UI)
├── manifests/                # Example system manifests
└── docs/                     # Documentation
```

## Composition Flow

```
User selects components in Control Panel
           │
           ▼
    System Manifest JSON
    (manifest.schema.json)
           │
           ▼
    Composition Engine
    (engine/scripts/compose.py)
           │
           ▼
    Dependency Resolution
           │
           ▼
    Template Scaffolding
    (copies + configures templates)
           │
           ▼
    GitHub repository_dispatch
    (triggers scaffold-on-manifest.yml)
           │
           ▼
    Generated Repository
    (fully scaffolded, CI-ready)
```

## Memory Interface Contract

All AI agents implement the `AgentMemory` interface:

```python
class AgentMemory(BaseModel):
    session_id: str           # Unique session identifier
    facts: list[str]          # Extracted knowledge (capped at 20 for context)
    tool_calls: list[ToolCall]  # Audit log of tool invocations
    created_at: str
    updated_at: str
```

## Mobile/Web App Access

The Control Panel exposes an OpenAI-compatible API at `/api/v1/chat` enabling access from:

- **GitHub Copilot Mobile App** — via HTTPS + Bearer auth
- **ChatGPT iOS/Android** — via Custom GPT Actions
- **Google Gemini** — via Gemini Extensions
- **vizual-x.com** — direct HTTPS integration
- **infinityxai.com** — Infinity Orchestrator integration

## TAP Governance (Policy → Authority → Truth)

Every generated system enforces:
- **Policy**: Required docs (README, ARCHITECTURE, SECURITY), test files, Docker config
- **Authority**: CODEOWNERS, branch protection, required reviews
- **Truth**: Conventional commits, signed commits (optional), coverage gates

## Dependencies

```
Engine:      Python 3.12 + jsonschema
Core API:    Python 3.12 + FastAPI + pydantic-settings + structlog + jose
Core UI:     Node 20 + Next.js 15 + React 19 + Tailwind CSS 3
AI Agents:   Python 3.12 + pydantic
Control Panel: Node 20 + Next.js 15 + React 19 + next-pwa
```
