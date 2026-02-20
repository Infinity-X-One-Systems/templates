# Infinity Template Library — Operational Runbook

> **Version:** 2.0.0 | **Status:** Production | **Owner:** Infinity-X-One-Systems

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Prerequisites](#2-prerequisites)
3. [Repository Structure Quick Reference](#3-repository-structure-quick-reference)
4. [Composition Engine Operations](#4-composition-engine-operations)
5. [Running Templates Locally](#5-running-templates-locally)
6. [Agent System Operations](#6-agent-system-operations)
7. [Pipeline Execution](#7-pipeline-execution)
8. [Control Panel Operations](#8-control-panel-operations)
9. [GitHub Actions Operations](#9-github-actions-operations)
10. [Memory System Operations](#10-memory-system-operations)
11. [Guardian System Operations](#11-guardian-system-operations)
12. [Google Workspace Operations](#12-google-workspace-operations)
13. [Connector Configuration](#13-connector-configuration)
14. [Invention Factory Workflow](#14-invention-factory-workflow)
15. [Troubleshooting](#15-troubleshooting)
16. [Security Procedures](#16-security-procedures)
17. [Cost Management](#17-cost-management)
18. [Escalation Procedures](#18-escalation-procedures)

---

## 1. System Overview

The Infinity Template Library is a manifest-driven, agent-readable template ecosystem that enables the assembly of complete production-grade systems — frontend, backend, AI agents, governance, and infrastructure — in under 60 minutes.

### Core Capabilities

| Capability | Implementation |
|---|---|
| **Manifest-driven composition** | `engine/scripts/compose.py` reads JSON manifests and scaffolds full repos |
| **PWA Control Panel** | Next.js 15 app at `control-panel/` exposing REST + OpenAI-compatible APIs |
| **8-Stage Pipeline** | `pipelines/` — Discovery → Design → Build → Test → Deploy → Monitor → Optimize → Scale |
| **Memory & Rehydration** | `memory/` — repo-backed state, decisions, architecture map, telemetry |
| **Guardian System** | `governance/guardian/` — continuous health monitoring and auto-fix suggestions |
| **TAP Governance** | Policy → Authority → Truth enforced via `.github/workflows/` |
| **AI Agents** | 6 production agents in `ai/`: research, builder, validator, financial, real-estate, orchestrator |
| **Industry Templates** | 20+ vertical templates in `industry/` |
| **Connectors** | OpenAI, Ollama, GitHub API, Webhooks, Ingestion in `connectors/` |
| **Google Workspace** | Sheets Dashboard, Gmail, Docs integration in `google/` |

### System Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                   Infinity Admin Control Plane              │
│              (infinity-admin-control-plane repo)            │
└───────────────────────────┬────────────────────────────────┘
                            │ repository_dispatch / REST API
┌───────────────────────────▼────────────────────────────────┐
│              Control Panel (control-panel/)                  │
│     /api/health  /api/no-code  /api/v1/chat  /api/compose   │
└───────────┬───────────────────────────────────┬────────────┘
            │ compose manifest                  │ OpenAI-compat
┌───────────▼───────────────┐      ┌────────────▼────────────┐
│  Composition Engine        │      │  External Clients        │
│  engine/scripts/compose.py │      │  Copilot / ChatGPT /    │
│                            │      │  Gemini / vizual-x.com  │
└───────────┬───────────────┘      └─────────────────────────┘
            │ scaffolds
┌───────────▼───────────────────────────────────────────────┐
│                    Template Library                         │
│  core/ ai/ backend/ business/ industry/ connectors/        │
│  governance/ infrastructure/ memory/ pipelines/ google/    │
└───────────────────────────────────────────────────────────┘
```

### Key Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_KEY` | Yes (prod) | Bearer token for Control Panel API authentication |
| `GITHUB_TOKEN` | Yes | GitHub PAT for repository_dispatch and workflow triggers |
| `OPENAI_API_KEY` | For AI agents | OpenAI API key for agent LLM calls |
| `OLLAMA_BASE_URL` | For local LLM | Ollama server URL (default: `http://localhost:11434`) |
| `DATABASE_URL` | For FastAPI core | PostgreSQL URL (e.g., `postgresql+asyncpg://user:pass@host/db`) |
| `REDIS_URL` | For memory cache | Redis URL (default: `redis://localhost:6379/0`) |
| `SECRET_KEY` | Yes | JWT signing secret for FastAPI core |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | For Google templates | Service account JSON (stringified) |
| `NEXT_PUBLIC_API_URL` | For frontend | Backend API base URL |
| `NEXT_PUBLIC_CONTROL_PANEL_URL` | For chat intent | Control panel public URL |
| `TEMPLATE_REPO` | Optional | GitHub repo name for dispatch (default: `templates`) |

---

## 2. Prerequisites

### System Requirements

| Tool | Minimum Version | Purpose |
|---|---|---|
| Python | 3.12 | Engine, agents, memory scripts, governance |
| Node.js | 20 LTS | Control panel, frontend templates |
| npm | 10+ | Node package management |
| Docker | 24+ | Container builds and local mesh |
| Docker Compose | v2 (Compose V2) | Local development mesh |
| Git | 2.40+ | Repository operations |
| GitHub CLI (`gh`) | 2.40+ | Workflow dispatch, PR management |
| `jq` | 1.6+ | JSON manipulation in shell scripts |

### Python Environment Setup

```bash
# 1. Verify Python version
python --version  # Must be 3.12.x

# 2. Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install engine dependencies
pip install -r engine/requirements.txt -r engine/requirements-dev.txt

# 4. Install memory system dependencies
pip install -r memory/requirements.txt -r memory/requirements-dev.txt

# 5. Install core FastAPI dependencies
pip install -r core/api-fastapi/requirements.txt -r core/api-fastapi/requirements-dev.txt

# 6. Verify installation
python -c "import jsonschema, pydantic, fastapi; print('OK')"
```

### Node Environment Setup

```bash
# 1. Verify Node version
node --version  # Must be 20.x

# 2. Install control panel dependencies
cd control-panel && npm install && cd ..

# 3. Install core frontend dependencies
cd core/frontend-nextjs && npm install && cd ../..

# 4. Install backend Express dependencies
cd backend/express-api && npm install && cd ../..
```

### GitHub CLI Authentication

```bash
# Authenticate with GitHub
gh auth login

# Verify authentication
gh auth status

# Set default repository (run from repo root)
gh repo set-default Infinity-X-One-Systems/templates
```

### Environment File Setup

```bash
# Copy example env files
cp core/api-fastapi/.env.example core/api-fastapi/.env  # if present
# OR create manually:
cat > .env << 'EOF'
API_KEY=your-control-panel-api-key
GITHUB_TOKEN=ghp_your_github_token
OPENAI_API_KEY=sk-your-openai-key
SECRET_KEY=your-jwt-secret-key-min-32-chars
DATABASE_URL=postgresql+asyncpg://infinity:infinity@localhost:5432/infinity
REDIS_URL=redis://localhost:6379/0
NEXT_PUBLIC_API_URL=http://localhost:8000
OLLAMA_BASE_URL=http://localhost:11434
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
EOF
```

---

## 3. Repository Structure Quick Reference

```
templates/
├── ARCHITECTURE.md              # System architecture documentation
├── README.md                    # Quick start and overview
├── RUNBOOK.md                   # ← This file
├── SECURITY.md                  # Security policy
│
├── engine/                      # Template composition engine
│   ├── scripts/compose.py       # Main composition script
│   ├── schema/
│   │   ├── manifest.schema.json         # JSON Schema for manifests
│   │   └── system-manifest.example.json # Example manifest
│   ├── tests/test_compose.py
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── manifests/                   # System manifest definitions
│   └── example-ai-platform.json
│
├── control-panel/               # PWA operator interface
│   ├── src/app/
│   │   ├── api/health/route.ts
│   │   ├── api/no-code/route.ts
│   │   ├── api/v1/chat/route.ts
│   │   └── api/compose/route.ts
│   ├── package.json
│   └── next.config.ts
│
├── core/                        # Mandatory primitives
│   ├── api-fastapi/             # FastAPI + auth + telemetry
│   └── frontend-nextjs/         # Next.js 15 + PWA + Tailwind
│
├── ai/                          # AI agent templates
│   ├── research-agent/
│   ├── builder-agent/
│   ├── validator-agent/
│   ├── financial-agent/
│   ├── real-estate-agent/
│   └── orchestrator/
│
├── agent-system/                # Agent infrastructure
│   ├── base/src/agent_base.py   # Universal AgentBase class
│   ├── capabilities/            # 10 capability categories
│   └── contracts/               # agent-interface.json schema
│
├── backend/                     # Backend patterns
│   └── express-api/
│
├── business/                    # Business workflow templates
│   └── crm-automation/
│
├── connectors/                  # External service connectors
│   ├── openai/
│   ├── ollama/
│   ├── github-api/
│   ├── webhooks/
│   └── ingestion/
│
├── google/                      # Google Workspace templates
│   └── sheets-dashboard/
│
├── governance/                  # Quality and compliance
│   ├── guardian/                # Health monitoring system
│   ├── tap-enforcement/
│   ├── test-coverage-gate/
│   └── security-gate/
│
├── industry/                    # 20+ vertical templates
│   ├── financial-trading/
│   ├── real-estate/
│   ├── healthcare-admin/
│   ├── analytics-platform/
│   └── ... (16 more)
│
├── infrastructure/              # Deployment infrastructure
│   ├── docker-local-mesh/
│   ├── github-actions/
│   └── github-projects/
│
├── memory/                      # Memory & rehydration system
│   ├── scripts/
│   │   ├── rehydrate.py
│   │   ├── write_state.py
│   │   ├── log_decision.py
│   │   └── log_telemetry.py
│   └── schemas/
│
├── pipelines/                   # 8-stage pipeline definitions
│   ├── pipeline.json
│   └── stages/{discovery,design,build,test,deploy,monitor,optimize,scale}/
│
├── experimental/                # Advanced AI templates
│   ├── collective-intelligence/
│   ├── human-ai-codriver/
│   └── self-improving-agent/
│
├── templates/                   # Meta-templates (GitHub, VSCode)
│   ├── github/
│   └── universal-business/
│
└── .github/workflows/           # CI/CD and automation
    ├── ci.yml
    ├── guardian.yml
    └── scaffold-on-manifest.yml
```

---

## 4. Composition Engine Operations

The composition engine (`engine/scripts/compose.py`) is the primary tool for generating complete system repositories from JSON manifests.

### Basic Usage

```bash
# Install dependencies
pip install -r engine/requirements.txt

# Compose a system from the example manifest
python engine/scripts/compose.py \
  --manifest manifests/example-ai-platform.json \
  --output ./generated

# Compose with a custom manifest
python engine/scripts/compose.py \
  --manifest my-system.json \
  --output /tmp/my-system

# Dry run — validates manifest and shows plan without writing files
python engine/scripts/compose.py \
  --manifest manifests/example-ai-platform.json \
  --output ./generated \
  --dry-run

# Use explicit template root (for non-standard working directory)
python engine/scripts/compose.py \
  --manifest my-system.json \
  --output ./output \
  --template-root /home/runner/work/templates/templates
```

### Manifest Authoring

Create a manifest file following the schema at `engine/schema/manifest.schema.json`:

```json
{
  "manifest_version": "1.0",
  "system_name": "my-ai-crm",
  "description": "AI-powered CRM with research and orchestration agents",
  "org": "Infinity-X-One-Systems",
  "version": "0.1.0",
  "components": {
    "backend": { "template": "fastapi" },
    "frontend": { "template": "nextjs-pwa", "pwa": true },
    "ai_agents": [
      { "template": "research", "instance_name": "market-researcher" },
      { "template": "orchestrator", "instance_name": "workflow-engine" },
      { "template": "validator", "instance_name": "data-validator" }
    ],
    "business": { "template": "crm" },
    "infrastructure": {
      "docker": true,
      "github_actions": true,
      "github_projects": true
    },
    "governance": {
      "tap_enforcement": true,
      "test_coverage_gate": true,
      "security_scan": true
    }
  },
  "memory": {
    "backend": "redis",
    "ttl_seconds": 3600,
    "max_facts": 100
  },
  "integrations": {
    "mobile_api": true,
    "openai_compatible": true,
    "webhook_dispatch": true,
    "cors_origins": ["https://infinityxai.com", "https://vizual-x.com"]
  },
  "metadata": {
    "created_by": "infinity-orchestrator",
    "created_at": "2026-02-20T04:00:00Z",
    "tags": ["ai", "crm", "business"]
  }
}
```

### Manifest Validation

```bash
# Validate a manifest against the JSON Schema
python -c "
import json, jsonschema
with open('engine/schema/manifest.schema.json') as f:
    schema = json.load(f)
with open('my-system.json') as f:
    manifest = json.load(f)
jsonschema.validate(manifest, schema)
print('Manifest is valid')
"

# Validate using the engine's built-in validator (dry-run)
python engine/scripts/compose.py --manifest my-system.json --output /dev/null --dry-run
```

### Supported Templates

| Component Type | Available Templates |
|---|---|
| `backend` | `fastapi`, `express`, `graphql`, `websocket`, `ai-inference`, `event-worker` |
| `frontend` | `nextjs-pwa`, `vite-react`, `dashboard`, `admin-panel`, `saas-landing`, `ai-console`, `chat-ui` |
| `ai_agents` | `research`, `builder`, `validator`, `financial`, `real-estate`, `orchestrator`, `content-gen`, `social-automation` |
| `business` | `crm`, `lead-gen`, `billing`, `saas-subscription`, `marketplace`, `portfolio-mgmt` |

### Engine Tests

```bash
cd engine
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/test_compose.py -v
pytest tests/test_compose.py --cov=scripts --cov-report=term-missing
```

---

## 5. Running Templates Locally

### Core FastAPI Backend

```bash
cd core/api-fastapi
pip install -r requirements.txt

# Set required environment variables
export SECRET_KEY="dev-secret-key-change-in-production"
export ENV="development"
export DATABASE_URL="sqlite+aiosqlite:///./dev.db"

# Start the API server
uvicorn app.main:app --reload --port 8000

# Verify health endpoint
curl http://localhost:8000/health

# API documentation (development only)
# Open http://localhost:8000/docs
# Open http://localhost:8000/redoc
```

### Core Next.js Frontend

```bash
cd core/frontend-nextjs
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL="http://localhost:8000"

# Start development server
npm run dev
# Opens at http://localhost:3000
```

### AI Agents

Each agent follows the same pattern:

```bash
# Research agent
cd ai/research-agent
pip install -r requirements.txt
python -c "from src.agent import ResearchAgent; a = ResearchAgent('my-researcher'); print(a.state.status)"

# Builder agent
cd ai/builder-agent
pip install -r requirements.txt
python -c "from src.agent import BuilderAgent; a = BuilderAgent('builder'); print(a.state.agent_id)"

# Financial agent
cd ai/financial-agent
pip install -r requirements.txt
python -c "from src.agent import FinancialAgent; a = FinancialAgent('fin-agent'); print('OK')"

# Real estate agent
cd ai/real-estate-agent
pip install -r requirements.txt
python -c "from src.agent import RealEstateAgent; a = RealEstateAgent('re-agent'); print('OK')"

# Orchestrator
cd ai/orchestrator
pip install -r requirements.txt
python -c "from src.orchestrator import Orchestrator; o = Orchestrator('orchestrator'); print('OK')"

# Validator agent
cd ai/validator-agent
pip install -r requirements.txt
python -c "from src.agent import ValidatorAgent; v = ValidatorAgent('validator'); print('OK')"
```

### Business Module — CRM Automation

```bash
cd business/crm-automation
pip install -r requirements.txt
python -c "from src.crm import CRMAutomation; crm = CRMAutomation(); print('CRM ready')"
```

### Industry Templates

```bash
# Financial Trading
cd industry/financial-trading
pip install -r requirements.txt
python -c "from src.simulator import TradingSimulator; s = TradingSimulator(); print('Simulator ready')"

# Analytics Platform
cd industry/analytics-platform
pip install -r requirements.txt
python -c "from src.engine import AnalyticsEngine; e = AnalyticsEngine(); print('Analytics ready')"

# Healthcare Admin
cd industry/healthcare-admin
pip install -r requirements.txt
python -c "from src.engine import HealthcareAdminEngine; e = HealthcareAdminEngine(); print('Healthcare ready')"
```

### Full Docker Local Mesh

```bash
# Set secrets (never commit these)
export SECRET_KEY="dev-secret-change-me"
export OPENAI_API_KEY="sk-your-key"

# Start the complete local mesh (API + Frontend + Redis + Postgres + Traefik + Prometheus + Grafana)
docker compose -f infrastructure/docker-local-mesh/templates/docker-compose.full.yml up -d

# Verify all services are healthy
docker compose -f infrastructure/docker-local-mesh/templates/docker-compose.full.yml ps

# Access services
# API:         http://api.localhost
# Frontend:    http://app.localhost
# Traefik UI:  http://localhost:8080
# Prometheus:  http://prometheus.localhost
# Grafana:     http://grafana.localhost (admin/admin)

# Stop the mesh
docker compose -f infrastructure/docker-local-mesh/templates/docker-compose.full.yml down

# Stop and remove volumes (reset state)
docker compose -f infrastructure/docker-local-mesh/templates/docker-compose.full.yml down -v
```

### Docker Builds for Individual Templates

```bash
# Build FastAPI core
docker build -t infinity/api-fastapi:local core/api-fastapi
docker run -p 8000:8000 -e SECRET_KEY=dev-secret -e ENV=development infinity/api-fastapi:local

# Build research agent
docker build -t infinity/research-agent:local ai/research-agent
docker run infinity/research-agent:local

# Build validator agent
docker build -t infinity/validator-agent:local ai/validator-agent
docker run infinity/validator-agent:local
```

---

## 6. Agent System Operations

### Agent Base Framework

All agents inherit from `AgentBase` in `agent-system/base/src/agent_base.py`.

```bash
# Install agent-system base dependencies
cd agent-system/base
pip install -r requirements.txt -r requirements-dev.txt

# Run agent-system tests
python -m pytest tests/ -v -q

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Creating a New Agent

```python
# Pattern for all Infinity agents
from agent_system.base.src.agent_base import AgentBase, CapabilityRef, TaskResult
import time

class MyCustomAgent(AgentBase):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            role="custom-processor",
            capabilities=[
                CapabilityRef(category="skills", name="data-processing"),
                CapabilityRef(category="tools", name="http-client"),
            ]
        )

    async def run_task(self, task: dict) -> TaskResult:
        self.state.status = "running"
        start = time.time()
        try:
            result = await self._process(task)
            self.state.status = "complete"
            return TaskResult(
                task_id=task["id"],
                agent_id=self.state.agent_id,
                success=True,
                output=result,
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            self.state.status = "error"
            return TaskResult(
                task_id=task["id"],
                agent_id=self.state.agent_id,
                success=False,
                output=None,
                error=str(e),
                duration_ms=(time.time() - start) * 1000,
            )
```

### Agent Registration Contract

Every deployed agent must satisfy `agent-system/contracts/agent-interface.json`:

```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "market-researcher",
  "role": "research",
  "capabilities": [
    { "category": "skills", "name": "web-search", "version": "1.0.0" },
    { "category": "knowledge", "name": "financial-markets", "version": "1.0.0" },
    { "category": "memory", "name": "session-memory", "version": "1.0.0" }
  ],
  "status": "idle",
  "iteration": 0
}
```

### Capability Categories

| Category | Description | Example Skills |
|---|---|---|
| `upgrades` | Self-improvement mechanisms | model-upgrade, prompt-tuning |
| `skills` | Task-specific abilities | web-search, code-gen, data-analysis |
| `knowledge` | Domain knowledge bases | financial-markets, real-estate, healthcare |
| `capabilities` | Cross-cutting capabilities | async-execution, retry-logic |
| `accessibility` | Multi-modal access | voice, screen-reader, mobile |
| `communication` | Inter-agent messaging | event-bus, direct-call |
| `blueprints` | Reusable execution patterns | discovery-loop, validation-chain |
| `tools` | External tool integrations | http-client, git-ops, docker |
| `memory` | Memory backends | session-memory, redis-memory, postgres-memory |
| `governance` | Compliance and audit | tap-check, budget-guard, audit-log |

---

## 7. Pipeline Execution

The Infinity pipeline is an 8-stage lifecycle defined in `pipelines/pipeline.json`.

### Stage Overview

| Stage | Order | Duration | Trigger | Key Outputs |
|---|---|---|---|---|
| **discovery** | 1 | ~15 min | manual / webhook / api | system_brief, architecture_map |
| **design** | 2 | ~10 min | discovery_complete | system_manifest, ARCHITECTURE.md |
| **build** | 3 | ~20 min | design_complete | generated_repo, docker_images |
| **test** | 4 | ~15 min | build_complete | test_report, coverage_report |
| **deploy** | 5 | ~10 min | test_complete | sandbox_url, production_url |
| **monitor** | 6 | ~5 min | deploy_complete / schedule | health_report, telemetry.json |
| **optimize** | 7 | ~20 min | monitor_alert / schedule | optimization_pr, cost_reduction |
| **scale** | 8 | ~30 min | optimize_complete / manual | scaled_infrastructure |

### Pipeline Execution via Memory State

```bash
# Initialize pipeline memory
mkdir -p .memory

# Stage 1: Discovery
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase planning \
  --action "pipeline_start" \
  --health-score 100 \
  --system-name my-system

python memory/scripts/log_decision.py \
  --state-dir .memory \
  --type architecture \
  --description "Selected FastAPI + Next.js + Research Agent stack" \
  --rationale "Team expertise and 60-min delivery target" \
  --made-by human \
  --component backend \
  --component frontend

# Stage 2: Design — compose manifest
python engine/scripts/compose.py \
  --manifest my-system.json \
  --output ./generated \
  --dry-run

# Update state after design
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase building \
  --action "design_complete" \
  --health-score 95

# Stage 3: Build — compose for real
python engine/scripts/compose.py \
  --manifest my-system.json \
  --output ./generated

python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase building \
  --action "scaffold_complete" \
  --health-score 90 \
  --component backend \
  --status healthy

# Emit build telemetry
python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type workflow_run \
  --component engine \
  --value 45.2 \
  --unit s \
  --metadata '{"manifest":"my-system.json","components":4}'

# Rehydrate context at any point
python memory/scripts/rehydrate.py \
  --state-dir .memory \
  --output .memory/context.json

cat .memory/context.json | python3 -m json.tool
```

### Pipeline Stage Files

```bash
# Inspect individual stage definitions
cat pipelines/stages/discovery/stage.json
cat pipelines/stages/design/stage.json
cat pipelines/stages/build/stage.json
cat pipelines/stages/test/stage.json
cat pipelines/stages/deploy/stage.json
cat pipelines/stages/monitor/stage.json
cat pipelines/stages/optimize/stage.json
cat pipelines/stages/scale/stage.json
```

### Running Pipeline Tests

```bash
cd pipelines
pip install pytest pytest-asyncio pydantic
python -m pytest tests/test_pipeline_stages.py -v
```

---

## 8. Control Panel Operations

The Control Panel is a Next.js 15 PWA at `control-panel/` that provides both a web UI and API endpoints for system composition.

### Starting the Control Panel

```bash
cd control-panel
npm install
npm run dev
# Starts at http://localhost:3001

# Production build
npm run build
npm run start
# Starts at http://localhost:3001
```

### API Endpoints

#### `GET /api/health`

Returns service health status.

```bash
curl http://localhost:3001/api/health
# {"status":"ok","service":"infinity-control-panel","timestamp":"2026-02-20T04:00:00.000Z"}
```

#### `GET /api/no-code`

Returns available operations.

```bash
curl http://localhost:3001/api/no-code
```

#### `POST /api/no-code`

No-code operations interface — the primary machine-readable API.

```bash
# List all template categories
curl -X POST http://localhost:3001/api/no-code \
  -H "Content-Type: application/json" \
  -d '{"operation": "list_categories"}'

# List templates in a category
curl -X POST http://localhost:3001/api/no-code \
  -H "Content-Type: application/json" \
  -d '{"operation": "list_templates", "params": {"category": "ai"}}'

# Get a specific template
curl -X POST http://localhost:3001/api/no-code \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_template", "params": {"template_id": "ai/research-agent"}}'

# Get pipeline stage info
curl -X POST http://localhost:3001/api/no-code \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_pipeline_stage", "params": {"stage": "build"}}'

# Get agent capabilities
curl -X POST http://localhost:3001/api/no-code \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_capabilities"}'

# Get a blueprint
curl -X POST http://localhost:3001/api/no-code \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_blueprint", "params": {"blueprint_name": "discovery-loop"}}'

# Queue a system composition
curl -X POST http://localhost:3001/api/no-code \
  -H "Content-Type: application/json" \
  -d '{"operation": "compose_system", "params": {"system_name": "my-crm"}}'
```

#### `POST /api/v1/chat`

OpenAI-compatible chat completions endpoint.

```bash
# With API key (if API_KEY env var is set)
curl -X POST http://localhost:3001/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "infinity-v1",
    "messages": [
      {"role": "user", "content": "List available templates"}
    ]
  }'

# Compose intent
curl -X POST http://localhost:3001/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "infinity-v1",
    "messages": [
      {"role": "user", "content": "Compose a FastAPI and Next.js system with a research agent"}
    ]
  }'

# System health check
curl -X POST http://localhost:3001/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "infinity-v1",
    "messages": [{"role": "user", "content": "status"}]
  }'
```

#### `POST /api/compose`

Full manifest submission and system composition.

```bash
curl -X POST http://localhost:3001/api/compose \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d @manifests/example-ai-platform.json
```

### Control Panel Tests

```bash
cd control-panel
npm run test
npm run test:ci  # CI mode with coverage

# Type checking
npm run type-check

# Linting
npm run lint
```

### Connecting to infinity-admin-control-plane

The Control Panel is the template-side interface. To connect to the Admin Control Plane:

```bash
# 1. Set required environment variables
export GITHUB_TOKEN="ghp_your_github_pat"
export TEMPLATE_REPO="templates"
export NEXT_PUBLIC_CONTROL_PANEL_URL="https://your-control-plane.infinityxai.com"

# 2. The control panel will send repository_dispatch events to trigger scaffolding
# This happens automatically when /api/compose receives a valid manifest

# 3. Verify the dispatch configuration
cat control-panel/src/app/api/compose/route.ts | grep -A5 "dispatchPayload"
```

---

## 9. GitHub Actions Operations

### Workflow Summary

| Workflow | File | Trigger | Purpose |
|---|---|---|---|
| CI | `.github/workflows/ci.yml` | push / PR | Tests, builds, manifest validation |
| Guardian | `.github/workflows/guardian.yml` | schedule / manual | Health monitoring |
| Scaffold | `.github/workflows/scaffold-on-manifest.yml` | manifest push / dispatch / manual | System scaffolding |

### Running Workflows Manually

```bash
# Trigger CI workflow on current branch
gh workflow run ci.yml

# Trigger scaffold workflow with specific manifest
gh workflow run scaffold-on-manifest.yml \
  -f manifest_path=manifests/example-ai-platform.json \
  -f output_org=Infinity-X-One-Systems \
  -f dry_run=false

# Trigger scaffold with dry run
gh workflow run scaffold-on-manifest.yml \
  -f manifest_path=manifests/my-system.json \
  -f dry_run=true

# Trigger guardian health check
gh workflow run guardian.yml
```

### Triggering via repository_dispatch

```bash
# Trigger scaffold via API (from Admin Control Plane or external system)
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/Infinity-X-One-Systems/templates/dispatches \
  -d '{
    "event_type": "scaffold-system",
    "client_payload": {
      "manifest_path": "manifests/my-system.json",
      "output_org": "Infinity-X-One-Systems"
    }
  }'

# Using GitHub CLI
gh api repos/Infinity-X-One-Systems/templates/dispatches \
  --method POST \
  --field event_type="scaffold-system" \
  --field client_payload[manifest_path]="manifests/my-system.json"
```

### Monitoring Workflow Runs

```bash
# List recent workflow runs
gh run list --limit 20

# List runs for a specific workflow
gh run list --workflow=ci.yml --limit 10

# Watch a run in real time
gh run watch

# View run logs
gh run view --log <run-id>

# List failed runs
gh run list --status failure --limit 10

# Re-run failed jobs
gh run rerun --failed <run-id>
```

### Adding a New Manifest and Auto-Scaffolding

```bash
# 1. Create your manifest
cp engine/schema/system-manifest.example.json manifests/my-new-system.json
# Edit manifests/my-new-system.json with your system definition

# 2. Validate locally
python engine/scripts/compose.py \
  --manifest manifests/my-new-system.json \
  --output /tmp/preview \
  --dry-run

# 3. Commit the manifest — this auto-triggers scaffold-on-manifest.yml
git add manifests/my-new-system.json
git commit -m "feat(manifest): add my-new-system manifest"
git push origin main

# 4. Monitor the scaffold workflow
gh run watch
```

---

## 10. Memory System Operations

The memory system provides repo-backed state persistence for all agents and workflows.

### Directory Structure

```
.memory/                         # Runtime state directory (gitignored)
├── system_state.json
├── decision_log.json
├── architecture_map.json
├── telemetry.json
└── context.json                 # Rehydrated consolidated context
```

### Installation

```bash
pip install -r memory/requirements.txt -r memory/requirements-dev.txt
# Installs: jsonschema, pydantic, pytest, pytest-asyncio
```

### Rehydration — Load All State

```bash
# Rehydrate to stdout (inspect current state)
python memory/scripts/rehydrate.py --state-dir .memory

# Rehydrate to file
python memory/scripts/rehydrate.py \
  --state-dir .memory \
  --output .memory/context.json

# Pretty-print the context
python memory/scripts/rehydrate.py --state-dir .memory | python3 -m json.tool

# Check for warnings
python memory/scripts/rehydrate.py --state-dir .memory 2>&1 | grep WARNING
```

### Writing System State

```bash
# Update phase and action
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase building \
  --action "scaffold_complete" \
  --health-score 95 \
  --system-name my-system

# Mark a component as healthy
python memory/scripts/write_state.py \
  --state-dir .memory \
  --component backend \
  --status healthy

# Mark a component as degraded with error
python memory/scripts/write_state.py \
  --state-dir .memory \
  --component frontend \
  --status degraded

# Set phase to deployed
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase deployed \
  --action "production_deploy_complete" \
  --health-score 100 \
  --system-name my-system
```

### Logging Decisions

```bash
# Log an architectural decision
python memory/scripts/log_decision.py \
  --state-dir .memory \
  --type architecture \
  --description "Use PostgreSQL for primary persistence" \
  --rationale "ACID compliance required for financial data" \
  --made-by human \
  --component backend \
  --outcome "Adopted in v1, performance acceptable"

# Log a tooling decision
python memory/scripts/log_decision.py \
  --state-dir .memory \
  --type tooling \
  --description "Switched from pip-tools to uv for dependency management" \
  --rationale "10x faster installs in CI" \
  --made-by agent \
  --component engine

# Log a process decision
python memory/scripts/log_decision.py \
  --state-dir .memory \
  --type process \
  --description "Enabled nightly guardian health checks" \
  --rationale "Catch regressions before business hours" \
  --made-by human \
  --component governance
```

### Logging Telemetry

```bash
# Log a test pass event
python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type test_pass \
  --component backend \
  --value 120 \
  --unit ms \
  --metadata '{"test": "test_api_health", "run_id": "abc123"}'

# Log a test failure
python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type test_fail \
  --component frontend \
  --metadata '{"test": "test_dashboard_render", "error": "timeout"}'

# Log a deployment event
python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type deploy \
  --component backend \
  --metadata '{"environment": "production", "version": "1.2.0"}'

# Log a health check
python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type health_check \
  --component guardian \
  --value 98 \
  --unit percent
```

### Memory System Tests

```bash
cd memory
pytest tests/ -v
pytest tests/ --cov=scripts --cov-report=term-missing
```

### system_state.json Schema

```json
{
  "manifest_version": "1.0",
  "system_name": "my-system",
  "org": "Infinity-X-One-Systems",
  "phase": "building",
  "components_status": {
    "backend": "healthy",
    "frontend": "healthy",
    "agents": "building"
  },
  "last_action": "scaffold_complete",
  "last_action_at": "2026-02-20T04:00:00Z",
  "health_score": 95,
  "errors": [],
  "warnings": ["redis not configured, using in-memory fallback"]
}
```

---

## 11. Guardian System Operations

The Guardian monitors system health, detects issues, and generates auto-fix suggestions.

### Running Guardian Locally

```bash
cd governance/guardian
pip install -r requirements.txt -r requirements-dev.txt

# Run guardian tests
python -m pytest tests/test_guardian.py -v

# Import and use the guardian
python -c "
from src.guardian import GuardianSystem, GuardianReport
guardian = GuardianSystem()

# Simulate workflow run data (from GitHub API)
runs = [
    {'id': '123', 'name': 'CI', 'conclusion': 'success', 'status': 'completed'},
    {'id': '456', 'name': 'Deploy', 'conclusion': 'failure', 'status': 'completed'},
]
alerts = guardian.check_workflow_health(runs)
print(f'Alerts: {len(alerts)}')
for alert in alerts:
    print(f'  [{alert.severity}] {alert.title}')
"
```

### Guardian Health Check Workflow

```bash
# Trigger guardian workflow manually
gh workflow run guardian.yml

# View guardian results
gh run list --workflow=guardian.yml --limit 5
gh run view --log $(gh run list --workflow=guardian.yml -L 1 --json databaseId -q '.[0].databaseId')
```

### Guardian Alert Types

| Alert Type | Severity | Description |
|---|---|---|
| `failed_workflow` | critical | A CI/CD workflow has failed |
| `stale_workflow` | warning | A workflow has been running for > 2 hours |
| `no_recent_runs` | warning | No workflow runs in > 7 days |
| `repeated_failures` | critical | Same workflow failed 3+ times consecutively |
| `coverage_regression` | warning | Test coverage dropped below threshold |
| `security_finding` | critical | Security scan found a vulnerability |

---

## 12. Google Workspace Operations

### Google Sheets Dashboard

```bash
cd google/sheets-dashboard
pip install -r requirements.txt

# Set credentials
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"your-project",...}'

# Run tests
python -m pytest tests/test_dashboard.py -v

# Use the dashboard
python -c "
import asyncio
from src.dashboard import GoogleSheetsDashboard

async def main():
    dashboard = GoogleSheetsDashboard(spreadsheet_id='your-spreadsheet-id')
    # Read metrics from sheet
    data = await dashboard.read_range('Sheet1!A1:Z100')
    print(data)

asyncio.run(main())
"
```

### Google Service Account Setup

1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Create a new service account with `Sheets API` and `Drive API` enabled
3. Download the JSON key file
4. Share your Google Sheet with the service account email
5. Set the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON=$(cat service-account-key.json)
```

---

## 13. Connector Configuration

### OpenAI Connector

```bash
cd connectors/openai
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="sk-your-openai-api-key"

# Run tests
python -m pytest tests/test_connector.py -v

# Use the connector
python -c "
import asyncio
from src.connector import OpenAIConnector

async def main():
    connector = OpenAIConnector()
    response = await connector.chat([
        {'role': 'user', 'content': 'Hello, what can you do?'}
    ])
    print(response)

asyncio.run(main())
"
```

### Ollama Connector (Local LLM)

```bash
# Start Ollama server first
# ollama serve

cd connectors/ollama
pip install -r requirements.txt

export OLLAMA_BASE_URL="http://localhost:11434"

# Run tests
python -m pytest tests/test_connector.py -v

# Use the connector
python -c "
import asyncio
from src.connector import OllamaConnector

async def main():
    connector = OllamaConnector(model='llama3.2')
    response = await connector.generate('What is 2+2?')
    print(response)

asyncio.run(main())
"
```

### GitHub API Connector

```bash
cd connectors/github-api
pip install -r requirements.txt

export GITHUB_TOKEN="ghp_your_github_token"

# Run tests
python -m pytest tests/test_connector.py -v
```

### Webhooks Connector

```bash
cd connectors/webhooks
pip install -r requirements.txt

# Run tests
python -m pytest tests/test_connector.py -v
```

### Ingestion Pipeline Connector

```bash
cd connectors/ingestion
pip install -r requirements.txt

# Run tests
python -m pytest tests/test_pipeline.py -v
```

---

## 14. Invention Factory Workflow

The Invention Factory is the end-to-end workflow from idea to production system in under 60 minutes.

See [`docs/invention-factory.md`](docs/invention-factory.md) for complete documentation.

### Quick Reference: Full E2E Flow

```bash
# Step 1: Discovery (15 min) — define the problem
mkdir -p .memory
python memory/scripts/write_state.py \
  --state-dir .memory --phase planning \
  --action "discovery_start" --health-score 100 --system-name my-system

# Step 2: Design (10 min) — create the manifest
cat > manifests/my-system.json << 'EOF'
{
  "manifest_version": "1.0",
  "system_name": "my-system",
  "org": "Infinity-X-One-Systems",
  "components": {
    "backend": {"template": "fastapi"},
    "frontend": {"template": "nextjs-pwa"},
    "ai_agents": [{"template": "research", "instance_name": "researcher"}],
    "governance": {"tap_enforcement": true, "test_coverage_gate": true}
  }
}
EOF

python engine/scripts/compose.py \
  --manifest manifests/my-system.json --output /tmp/preview --dry-run

# Step 3: Build (20 min) — scaffold and push
python engine/scripts/compose.py \
  --manifest manifests/my-system.json --output ./generated

python memory/scripts/write_state.py \
  --state-dir .memory --phase building --action "scaffold_complete" --health-score 90

# Step 4: Test (15 min) — run all tests
cd ./generated/my-system/backend && pip install -r requirements.txt -r requirements-dev.txt && pytest -q
cd ./generated/my-system/frontend && npm install && npm test

# Step 5: Deploy — commit and trigger CI
git add manifests/my-system.json
git commit -m "feat: add my-system manifest"
git push origin main
gh run watch
```

---

## 15. Troubleshooting

### Engine Issues

**Problem:** `ManifestValidationError: Missing required fields`
```bash
# Check which fields are missing
python -c "
import json, jsonschema
schema = json.load(open('engine/schema/manifest.schema.json'))
manifest = json.load(open('my-system.json'))
try:
    jsonschema.validate(manifest, schema)
except jsonschema.ValidationError as e:
    print('ERROR:', e.message)
    print('PATH:', list(e.absolute_path))
"
```

**Problem:** `Template not found` during composition
```bash
# List available templates
ls ai/
ls core/
ls backend/
# Check your manifest's template names against SUPPORTED_*_TEMPLATES in compose.py
grep -A5 "SUPPORTED_" engine/scripts/compose.py
```

**Problem:** `jsonschema` not found
```bash
pip install jsonschema==4.23.0
```

### Control Panel Issues

**Problem:** Control panel won't start
```bash
cd control-panel
rm -rf node_modules .next
npm install
npm run dev
```

**Problem:** API returns 401 Unauthorized
```bash
# Verify API_KEY is set and matches
echo $API_KEY
# Ensure Authorization header format: "Bearer <key>"
curl -H "Authorization: Bearer $API_KEY" http://localhost:3001/api/health
```

**Problem:** TypeScript errors in control panel
```bash
cd control-panel
npm run type-check 2>&1 | head -50
```

### Agent Issues

**Problem:** Agent tests failing with import errors
```bash
# Ensure you're in the right directory with requirements installed
cd ai/research-agent
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v 2>&1 | head -30
```

**Problem:** OpenAI connector 401 error
```bash
# Verify API key
echo $OPENAI_API_KEY | head -c 10
# Check key validity
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" | python3 -m json.tool | head -10
```

### Memory System Issues

**Problem:** `state-dir does not exist`
```bash
mkdir -p .memory
# The scripts will initialize state files on first write
python memory/scripts/write_state.py --state-dir .memory --phase planning --action "init"
```

**Problem:** Schema validation warnings in rehydrate
```bash
# Check which fields are invalid
python memory/scripts/rehydrate.py --state-dir .memory 2>&1
# Fix the invalid state file manually or delete and reinitialize
python memory/scripts/write_state.py --state-dir .memory --phase planning --action "reset" --health-score 100 --system-name my-system
```

### GitHub Actions Issues

**Problem:** Scaffold workflow not triggering on manifest push
```bash
# Verify the manifest is in the manifests/ directory
ls manifests/*.json
# Check workflow trigger condition
grep "paths:" .github/workflows/scaffold-on-manifest.yml
# Manually trigger
gh workflow run scaffold-on-manifest.yml -f manifest_path=manifests/my-system.json
```

**Problem:** CI failing on coverage gate
```bash
# Check current coverage
cd core/api-fastapi && pytest --cov=app --cov-report=term-missing
# Identify uncovered lines and add tests
```

### Docker Issues

**Problem:** Docker build fails for FastAPI core
```bash
# Check Docker version
docker --version  # Must be 24+
# Try building with no cache
docker build --no-cache -t test core/api-fastapi
# Check build logs
docker build -t test core/api-fastapi 2>&1 | tail -30
```

**Problem:** Local mesh services not healthy
```bash
docker compose -f infrastructure/docker-local-mesh/templates/docker-compose.full.yml ps
docker compose -f infrastructure/docker-local-mesh/templates/docker-compose.full.yml logs api --tail=50
docker compose -f infrastructure/docker-local-mesh/templates/docker-compose.full.yml logs postgres --tail=20
```

---

## 16. Security Procedures

### Secrets Management

**Never commit secrets to source control.** All secrets are managed via environment variables.

```bash
# Verify no secrets are tracked
git log --all --full-history -- '**/.env' '**/*.pem' '**/*secret*'

# Scan for accidentally committed secrets
gh secret scan  # If GitHub Advanced Security is enabled

# Rotate a compromised API key
# 1. Revoke the old key immediately in the respective service dashboard
# 2. Generate a new key
# 3. Update GitHub repository secrets
gh secret set API_KEY
gh secret set GITHUB_TOKEN
gh secret set OPENAI_API_KEY

# View configured secrets (names only, not values)
gh secret list
```

### Required GitHub Repository Secrets

```
API_KEY             — Control panel authentication
GITHUB_TOKEN        — Auto-provided by GitHub Actions
OPENAI_API_KEY      — For AI agent templates (if used)
SECRET_KEY          — JWT signing key for FastAPI core
DATABASE_URL        — Production database connection
```

### Security Scanning

```bash
# Run security scan workflow
gh workflow run .github/workflows/guardian.yml

# Manual Bandit scan (Python)
pip install bandit
bandit -r engine/ memory/ governance/ ai/ connectors/ -ll

# Dependency vulnerability scan
pip install pip-audit
pip-audit -r engine/requirements.txt
pip-audit -r core/api-fastapi/requirements.txt

# npm audit for Node.js templates
cd control-panel && npm audit
cd core/frontend-nextjs && npm audit
```

### TAP Governance Compliance Check

```bash
# Verify TAP workflows are present
ls .github/workflows/
cat governance/tap-enforcement/templates/tap-workflow.yml

# Check that required docs exist
for doc in README.md ARCHITECTURE.md SECURITY.md; do
  [ -f "$doc" ] && echo "✓ $doc" || echo "✗ MISSING: $doc"
done

# Check coverage gate configuration
cat governance/test-coverage-gate/templates/coverage-gate.yml
```

---

## 17. Cost Management

### AI API Cost Controls

```bash
# Set token limits in manifests
# In system manifest, governance section:
{
  "governance": {
    "tap_enforcement": true,
    "test_coverage_gate": true,
    "security_scan": true
  }
}

# The guardian monitors for cost overruns via the bounded-autonomy governance rule
# Pipelines include "cost-budget" governance at design, monitor, and scale stages
```

### GitHub Actions Minute Tracking

```bash
# Check billable minutes for current month
gh api /repos/Infinity-X-One-Systems/templates/actions/cache/usage
gh api /orgs/Infinity-X-One-Systems/settings/billing/actions

# List workflows by run frequency to identify cost drivers
gh run list --limit 100 --json workflowName | python3 -c "
import json, sys
from collections import Counter
runs = json.load(sys.stdin)
counts = Counter(r['workflowName'] for r in runs)
for wf, n in counts.most_common():
    print(f'{n:4d}  {wf}')
"
```

### Docker Image Optimization

```bash
# Check image sizes before pushing
docker images | grep infinity
# Target: API < 200MB, agents < 150MB
# Use multi-stage builds (already configured in Dockerfiles)

# Clean up unused images
docker image prune -f
docker system prune -f  # WARNING: removes all unused resources
```

---

## 18. Escalation Procedures

### Severity Levels

| Level | Response Time | Definition |
|---|---|---|
| **P0 — Critical** | Immediate | Production system down, security breach, data loss |
| **P1 — High** | < 1 hour | Core API down, CI completely broken, secret exposed |
| **P2 — Medium** | < 4 hours | Single workflow failing, test coverage regression |
| **P3 — Low** | < 24 hours | Documentation outdated, non-critical test flake |

### Escalation Path

```
P0/P1: GitHub Issue → @Infinity-X-One-Systems/core-team → Direct message
P2:    GitHub Issue → Workflow comment → Next standup
P3:    GitHub Issue → Backlog triage
```

### Creating a Proper Escalation Issue

```bash
# Use the guardian alert template
gh issue create \
  --title "P1: CI workflow failing — scaffold-on-manifest.yml" \
  --label "priority:P1,type:incident" \
  --body "
## Incident Summary
[Describe what is broken]

## Impact
[What systems/users are affected]

## Steps to Reproduce
[Commands run, workflow links]

## System State
\`\`\`json
$(python memory/scripts/rehydrate.py --state-dir .memory 2>/dev/null || echo 'state unavailable')
\`\`\`

## Recent Workflow Runs
$(gh run list --limit 5 --json databaseId,workflowName,conclusion,createdAt 2>/dev/null)
"
```

### Emergency Rollback

```bash
# Roll back a failed scaffold
# 1. Find the last known good commit
git log --oneline manifests/ | head -10

# 2. Revert the manifest change
git revert HEAD --no-edit
git push origin main

# 3. Reset memory state
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase planning \
  --action "emergency_rollback" \
  --health-score 50 \
  --system-name my-system

python memory/scripts/log_decision.py \
  --state-dir .memory \
  --type process \
  --description "Emergency rollback to previous manifest version" \
  --rationale "Scaffold workflow failure — P1 incident" \
  --made-by human \
  --component engine
```

---

*Runbook maintained by Infinity-X-One-Systems Engineering.*  
*For questions, open an issue using the guardian_alert template in `templates/github/ISSUE_TEMPLATE/guardian_alert.md`.*
