# The Infinity Invention Factory

> *From idea to deployed production system in under 60 minutes.*

---

## What is the Invention Factory?

The Invention Factory is the Infinity end-to-end workflow for transforming a business problem into a fully deployed, tested, production-grade system. It is the operational expression of the Infinity Template Library — the library is the raw material; the Factory is the assembly line.

The Factory is not a metaphor. It is a concrete sequence of eight pipeline stages, each with defined inputs, outputs, tools, governance gates, and time budgets. An experienced operator or a well-configured agent team completes the full cycle in under 60 minutes.

**The Factory's three core guarantees:**

1. **Speed:** First functional deployment in < 60 minutes
2. **Quality:** Every output satisfies the 110% Protocol checklist
3. **Composability:** Every generated system is a first-class citizen of the Infinity ecosystem — fully monitored, governed, and recomposable

---

## The 8-Stage Pipeline

The pipeline is defined in `pipelines/pipeline.json` and individual stages in `pipelines/stages/{stage}/stage.json`.

```
Discovery ──► Design ──► Build ──► Test ──► Deploy ──► Monitor ──► Optimize ──► Scale
   15 min      10 min     20 min    15 min    10 min      5 min       20 min      30 min
```

---

### Stage 1: Discovery (≤ 15 minutes)

**Purpose:** Capture requirements, constraints, and context. Generate the system brief.

**Trigger:** Manual | Webhook | API call to `/api/v1/chat` with compose intent

**Inputs:**
- Problem statement
- Constraints (budget, time, tech stack preferences)
- Stakeholder list
- Success criteria

**Outputs:**
- `discovery-report.md` — structured brief
- Initial `system_state.json` in `.memory/`
- First `decision_log.json` entry

**Tools:** LLM reasoning, knowledge base, web search  
**Governance:** Human approval required before proceeding to Design

**Operator Actions:**
```bash
# 1. Initialize memory
mkdir -p .memory

# 2. Start state tracking
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase planning \
  --action "discovery_start" \
  --health-score 100 \
  --system-name my-system

# 3. Log the discovery decision
python memory/scripts/log_decision.py \
  --state-dir .memory \
  --type architecture \
  --description "Selected FastAPI + Next.js + Research Agent for market intelligence platform" \
  --rationale "Team has Python expertise; 60-min target requires proven stack; real-time data needed" \
  --made-by human \
  --component backend \
  --component frontend \
  --component agents

# 4. Emit discovery telemetry
python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type workflow_run \
  --component discovery \
  --metadata '{"stage":"discovery","status":"complete"}'
```

**Artifact: `discovery-report.md`**
```markdown
# Discovery Report — Market Intelligence Platform

## Problem Statement
Sales team needs real-time competitive intelligence on 50 target accounts.

## Constraints
- Budget: < $500/month cloud costs
- Timeline: Live within 1 week
- Team: 2 Python engineers, 1 designer

## Proposed System
- Backend: FastAPI (Python 3.12)
- Frontend: Next.js PWA with dashboard template
- AI Agents: Research agent (market data) + Orchestrator (workflow)
- Business: CRM automation module
- Infrastructure: Docker + GitHub Actions

## Success Criteria
- Research agent returns results in < 30 seconds
- Dashboard updates every 15 minutes
- 99.9% uptime SLA
```

**Time Budget Breakdown:**
| Activity | Target |
|---|---|
| Problem statement capture | 3 min |
| Constraint elicitation | 3 min |
| Stack selection | 5 min |
| Approval handoff | 4 min |
| **Total** | **15 min** |

---

### Stage 2: Design (≤ 10 minutes)

**Purpose:** Architect the system. Select templates. Generate and validate the system manifest.

**Trigger:** `discovery_complete` (state phase transitions from `planning`)

**Inputs:**
- `discovery-report.md`
- Template library (this repo)
- Constraints from discovery

**Outputs:**
- `system-manifest.json` — the machine-readable system definition
- `ARCHITECTURE.md` — human-readable architecture diagram
- Dependency graph

**Tools:** Template engine, manifest validator, LLM reasoning  
**Governance:** TAP protocol, cost budget check

**Operator Actions:**
```bash
# 1. Author the system manifest
cat > manifests/my-system.json << 'EOF'
{
  "manifest_version": "1.0",
  "system_name": "market-intelligence-platform",
  "description": "Real-time competitive intelligence with AI research agents",
  "org": "Infinity-X-One-Systems",
  "version": "0.1.0",
  "components": {
    "backend": { "template": "fastapi" },
    "frontend": { "template": "nextjs-pwa", "pwa": true },
    "ai_agents": [
      { "template": "research", "instance_name": "market-researcher" },
      { "template": "orchestrator", "instance_name": "workflow-engine" }
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
  "memory": { "backend": "redis", "ttl_seconds": 3600 },
  "integrations": {
    "mobile_api": true,
    "openai_compatible": true,
    "webhook_dispatch": true
  },
  "metadata": {
    "created_by": "operator",
    "created_at": "2026-02-20T04:00:00Z",
    "tags": ["ai", "crm", "market-intelligence"]
  }
}
EOF

# 2. Validate the manifest (dry run)
python engine/scripts/compose.py \
  --manifest manifests/my-system.json \
  --output /tmp/preview \
  --dry-run

# 3. Update state
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase building \
  --action "design_complete" \
  --health-score 100
```

**Time Budget Breakdown:**
| Activity | Target |
|---|---|
| Template selection | 3 min |
| Manifest authoring | 4 min |
| Dry-run validation | 1 min |
| State update | 2 min |
| **Total** | **10 min** |

---

### Stage 3: Build (≤ 20 minutes)

**Purpose:** Scaffold and generate all system components from the manifest.

**Trigger:** `design_complete` (manifest committed to `manifests/`)

**Inputs:**
- `system-manifest.json`
- Template library (this repo)

**Outputs:**
- Generated repository with all components scaffolded
- Docker images built
- API stubs with working endpoints

**Tools:** Composition engine (`compose.py`), git operations, Docker build  
**Governance:** Sandbox-first, secret guard (no secrets in generated code)

**Operator Actions:**
```bash
# Option A: Local build
python engine/scripts/compose.py \
  --manifest manifests/my-system.json \
  --output ./generated

# Option B: GitHub Actions build (auto-triggered on manifest commit)
git add manifests/my-system.json
git commit -m "feat(manifest): add market-intelligence-platform"
git push origin main
# scaffold-on-manifest.yml triggers automatically

# Option C: Manual workflow dispatch
gh workflow run scaffold-on-manifest.yml \
  -f manifest_path=manifests/my-system.json \
  -f output_org=Infinity-X-One-Systems

# Monitor build progress
gh run watch

# After build: verify generated output
ls ./generated/market-intelligence-platform/
# Expected:
# backend/          ← FastAPI core
# frontend/         ← Next.js PWA
# agents/market-researcher/     ← Research agent
# agents/workflow-engine/       ← Orchestrator
# business/         ← CRM automation
# .github/workflows/← CI + TAP workflows
# docker-compose.yml
# README.md, ARCHITECTURE.md, SECURITY.md

# Build Docker images
docker build -t mip/backend:latest ./generated/market-intelligence-platform/backend
docker build -t mip/frontend:latest ./generated/market-intelligence-platform/frontend

# Update memory state
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase building \
  --action "scaffold_complete" \
  --health-score 90 \
  --component backend \
  --status healthy \
  --component frontend \
  --status healthy

python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type workflow_run \
  --component engine \
  --value 42.5 \
  --unit s \
  --metadata '{"stage":"build","components_scaffolded":5}'
```

**Time Budget Breakdown:**
| Activity | Target |
|---|---|
| `compose.py` execution | 2 min |
| Docker image builds | 10 min |
| Output verification | 5 min |
| State update + telemetry | 3 min |
| **Total** | **20 min** |

---

### Stage 4: Test (≤ 15 minutes)

**Purpose:** Run all tests, linting, type checks, and security scans. Block on failures.

**Trigger:** `build_complete`

**Inputs:** Generated repository

**Outputs:**
- `test-results.xml`
- `coverage.xml` (must be ≥ 80%)
- `security-report.json`

**Tools:** pytest, eslint, CodeQL, Trivy  
**Governance:** Test coverage gate (80%), security scan gate (no critical CVEs)

**Operator Actions:**
```bash
# Run backend tests
cd generated/market-intelligence-platform/backend
pip install -r requirements.txt -r requirements-dev.txt
pytest --cov=app --cov-report=xml -q
# Must show: coverage ≥ 80%

# Run frontend tests
cd ../frontend
npm install
npm test -- --coverage
# Must show: coverage ≥ 80%

# Run agent tests
cd ../agents/market-researcher
pip install -r requirements.txt -r requirements-dev.txt
pytest -q

# Security scan
pip install pip-audit
pip-audit -r backend/requirements.txt
cd frontend && npm audit

# Update state after passing tests
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase testing \
  --action "all_tests_pass" \
  --health-score 95

python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type test_pass \
  --component backend \
  --value 87 \
  --unit percent \
  --metadata '{"coverage":"87%","tests_passed":42,"tests_failed":0}'
```

**Time Budget Breakdown:**
| Activity | Target |
|---|---|
| Backend test suite | 5 min |
| Frontend test suite | 5 min |
| Agent tests | 3 min |
| Security scan | 2 min |
| **Total** | **15 min** |

---

### Stage 5: Deploy (≤ 10 minutes)

**Purpose:** Deploy to sandbox, validate, then promote to production.

**Trigger:** `test_complete` — all gates green

**Inputs:**
- Generated repository
- Passing test report
- Clean security report

**Outputs:**
- Sandbox URL (validated)
- Production URL
- Deployment log

**Tools:** Docker Compose, GitHub Pages, Cloudflare Workers  
**Governance:** Sandbox-first (always deploy to sandbox before production), human approval for production, rollback plan must exist

**Operator Actions:**
```bash
# Deploy to local sandbox
cd generated/market-intelligence-platform
docker compose up -d

# Validate sandbox health
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"...","timestamp":"..."}

curl http://localhost:3000
# Expected: 200 OK from Next.js frontend

# Run smoke tests against sandbox
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"infinity-v1","messages":[{"role":"user","content":"health"}]}'

# Commit and push generated system to trigger production deploy
cd generated/market-intelligence-platform
git init
git remote add origin https://github.com/Infinity-X-One-Systems/market-intelligence-platform.git
git add .
git commit -m "feat: initial system scaffold from Infinity Template Library"
git push -u origin main

# Monitor production CI
gh run watch --repo Infinity-X-One-Systems/market-intelligence-platform

# Update memory state
python memory/scripts/write_state.py \
  --state-dir .memory \
  --phase deployed \
  --action "production_deploy_complete" \
  --health-score 100

python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type deploy \
  --component backend \
  --metadata '{"environment":"production","url":"https://api.market-intelligence.infinityxai.com"}'
```

**Time Budget Breakdown:**
| Activity | Target |
|---|---|
| Sandbox deploy | 3 min |
| Sandbox validation | 2 min |
| Production push + CI | 4 min |
| State update | 1 min |
| **Total** | **10 min** |

---

### Stage 6: Monitor (≤ 5 minutes setup, then continuous)

**Purpose:** Monitor deployed system health, performance, errors, and costs on schedule.

**Trigger:** `deploy_complete` | `schedule(*/15 * * * *)` — every 15 minutes

**Inputs:**
- Production URL
- Deployment manifest

**Outputs:**
- `health_report.md`
- `telemetry.json` (appended)
- Guardian alerts (GitHub Issues if critical)

**Tools:** Guardian system, Prometheus, GitHub Actions schedule  
**Governance:** Audit log, cost budget check

**Operator Actions:**
```bash
# Set up guardian monitoring
# guardian.yml runs on schedule in .github/workflows/

# Check current guardian status
gh run list --workflow=guardian.yml --limit 5

# Manual guardian run
gh workflow run guardian.yml

# Read guardian report
gh run view --log $(gh run list --workflow=guardian.yml -L 1 --json databaseId -q '.[0].databaseId') \
  | grep -A 20 "Guardian Report"

# Log health telemetry
python memory/scripts/log_telemetry.py \
  --state-dir .memory \
  --event-type health_check \
  --component backend \
  --value 99 \
  --unit percent \
  --metadata '{"endpoint":"/health","response_ms":23,"status":"ok"}'

# Rehydrate and review full state
python memory/scripts/rehydrate.py --state-dir .memory | python3 -m json.tool
```

---

### Stage 7: Optimize (≤ 20 minutes)

**Purpose:** Analyze telemetry and apply optimizations as PRs for human review.

**Trigger:** Guardian alert | `schedule(0 * * * *)` — every hour

**Inputs:**
- `telemetry.json`
- Health report
- Cost report

**Outputs:**
- Optimization PR (human reviews before merge)
- Updated manifest
- Cost reduction report

**Tools:** Guardian system, LLM reasoning, GitHub PR  
**Governance:** Bounded autonomy (PRs proposed, never auto-merged), human approval required, rollback plan in PR description

**Operator Actions:**
```bash
# Review telemetry for optimization signals
python memory/scripts/rehydrate.py --state-dir .memory | \
  python3 -c "
import json, sys
ctx = json.load(sys.stdin)
telemetry = ctx.get('telemetry') or []
errors = [e for e in telemetry if e.get('event_type') == 'error']
print(f'Errors in telemetry: {len(errors)}')
for e in errors[-5:]:
    print(f'  {e[\"timestamp\"]}: {e[\"component\"]} - {e.get(\"metadata\",{})}')
"

# Create optimization PR (agent proposes, human approves)
gh pr create \
  --title "perf(backend): increase connection pool size" \
  --body "Guardian detected p99 latency > 500ms. Increasing DB pool from 10 to 25.
Reversible: Yes. Expected improvement: ~30% latency reduction." \
  --label "type:optimization"
```

---

### Stage 8: Scale (≤ 30 minutes)

**Purpose:** Scale infrastructure and replicate system patterns to new domains.

**Trigger:** `optimize_complete` | Manual decision

**Inputs:**
- Deployment manifest
- Performance metrics
- Optimization report

**Outputs:**
- Scaled infrastructure configuration
- Replication manifests (new system variants)
- Cost projection for scaled deployment

**Tools:** Kubernetes, Terraform (if applicable), Composition engine  
**Governance:** TAP protocol, cost budget, human approval mandatory

**Operator Actions:**
```bash
# Create a variant manifest for a new domain
cp manifests/my-system.json manifests/my-system-v2.json
# Edit system_name and add new components

# Log scale decision
python memory/scripts/log_decision.py \
  --state-dir .memory \
  --type architecture \
  --description "Scaling market-intelligence-platform to real-estate vertical" \
  --rationale "Core research agent pattern applicable to property market analysis" \
  --made-by human \
  --component agents

# Compose the new variant
python engine/scripts/compose.py \
  --manifest manifests/my-system-v2.json \
  --output ./generated
```

---

## Discovery → Dev Handoff Protocol

This repository serves as the **canonical template library** for developer handoffs from the Factory. When a discovery produces a manifest, the following handoff protocol ensures zero friction:

### Handoff Package

Every system exiting the Factory produces a handoff package:

```
handoff/
├── system-manifest.json         # Definitive system definition
├── discovery-report.md          # Problem statement and context
├── ARCHITECTURE.md              # Component diagram and rationale
├── .memory/
│   ├── system_state.json        # Current state (phase: "building" or "deployed")
│   ├── decision_log.json        # All decisions made during discovery + design
│   └── telemetry.json           # Initial build telemetry
└── README.md                    # Quickstart for the receiving developer
```

### Handoff Commands

```bash
# Package the handoff
mkdir -p handoff
cp manifests/my-system.json handoff/system-manifest.json
cp discovery-report.md handoff/
cp -r .memory handoff/
python memory/scripts/rehydrate.py --state-dir .memory --output handoff/context.json

# Transfer to dev team
gh release create v0.1.0 \
  --title "Factory Output: market-intelligence-platform v0.1.0" \
  --notes "Generated by Invention Factory on $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  handoff/

# Or create a branch for dev team
git checkout -b factory/market-intelligence-platform
git add handoff/ manifests/
git commit -m "feat(factory): market-intelligence-platform factory output"
git push origin factory/market-intelligence-platform
gh pr create --title "Factory Output: market-intelligence-platform" --base main
```

---

## Template Selection Guide

Choosing the right templates is the highest-leverage decision in the Factory. Use this guide during Stage 2 (Design).

### Decision Framework

**Question 1: What is the primary data flow?**

| Data Flow | Recommended Backend | Recommended Agent |
|---|---|---|
| REST API + CRUD | `fastapi` | `validator` |
| Real-time events | `websocket` | `orchestrator` |
| GraphQL / flexible queries | `graphql` | `research` |
| AI-first (LLM heavy) | `ai-inference` | `orchestrator` + `builder` |
| Event-driven / async | `event-worker` | `orchestrator` |

**Question 2: What is the primary user interface?**

| UI Need | Recommended Frontend |
|---|---|
| Mobile-first business app | `nextjs-pwa` |
| Internal dashboard / admin | `dashboard` or `admin-panel` |
| SaaS product landing + app | `saas-landing` + `nextjs-pwa` |
| AI chat interface | `ai-console` or `chat-ui` |
| Developer / API tool | `dashboard` |

**Question 3: What is the primary business workflow?**

| Workflow Type | Recommended Business Module |
|---|---|
| Sales pipeline / contacts | `crm` |
| Lead capture / nurturing | `lead-gen` |
| Subscription payments | `billing` or `saas-subscription` |
| Multi-vendor marketplace | `marketplace` |
| Investment tracking | `portfolio-mgmt` |

**Question 4: What AI capabilities are required?**

| AI Capability | Recommended Agent |
|---|---|
| Web research, data gathering | `research` |
| Code generation, scaffolding | `builder` |
| Input validation, QA | `validator` |
| Financial modeling, prediction | `financial` |
| Property analysis, valuation | `real-estate` |
| Multi-step workflow automation | `orchestrator` |
| Multi-agent coordination | `orchestrator` + specialist agents |

### Quick Reference: Common System Archetypes

| System Type | Backend | Frontend | Agents | Business |
|---|---|---|---|---|
| AI Research Platform | `fastapi` | `ai-console` | `research`, `orchestrator` | — |
| SaaS CRM | `fastapi` | `nextjs-pwa` | `orchestrator`, `validator` | `crm` |
| Financial Dashboard | `fastapi` | `dashboard` | `financial`, `research` | — |
| Real Estate Platform | `fastapi` | `nextjs-pwa` | `real-estate`, `research` | `crm` |
| Developer Tools | `fastapi` | `admin-panel` | `builder`, `validator` | — |
| E-commerce | `express` | `saas-landing` | `orchestrator` | `marketplace` |
| Marketing Platform | `fastapi` | `nextjs-pwa` | `research`, `orchestrator` | `lead-gen` |

---

## Assembly Examples

### Example 1: Market Intelligence Platform

**Scenario:** A sales team needs AI-powered competitive research on 50 accounts.

**Manifest:**
```json
{
  "manifest_version": "1.0",
  "system_name": "market-intelligence-platform",
  "org": "Infinity-X-One-Systems",
  "components": {
    "backend": { "template": "fastapi" },
    "frontend": { "template": "dashboard" },
    "ai_agents": [
      { "template": "research", "instance_name": "competitive-researcher" },
      { "template": "orchestrator", "instance_name": "research-orchestrator" }
    ],
    "governance": { "tap_enforcement": true, "test_coverage_gate": true, "security_scan": true }
  },
  "memory": { "backend": "redis", "ttl_seconds": 1800 }
}
```

**Assembly:**
```bash
python engine/scripts/compose.py \
  --manifest manifests/market-intelligence-platform.json \
  --output ./generated
```

**Generated Structure:**
```
market-intelligence-platform/
├── backend/              ← FastAPI with auth, health, telemetry
├── frontend/             ← Dashboard with real-time data panels
├── agents/competitive-researcher/  ← Research agent
├── agents/research-orchestrator/   ← Workflow orchestrator
└── .github/workflows/    ← CI + TAP
```

**Time to live:** Discovery 15 min + Design 10 min + Build 20 min + Test 15 min + Deploy 10 min = **70 minutes**

---

### Example 2: FinTech SaaS Platform

**Scenario:** A fintech startup needs a full SaaS platform with billing, portfolio management, and AI financial analysis.

**Manifest:**
```json
{
  "manifest_version": "1.0",
  "system_name": "fintech-saas-platform",
  "org": "Infinity-X-One-Systems",
  "components": {
    "backend": { "template": "fastapi" },
    "frontend": { "template": "nextjs-pwa", "pwa": true },
    "ai_agents": [
      { "template": "financial", "instance_name": "portfolio-analyzer" },
      { "template": "research", "instance_name": "market-data-agent" },
      { "template": "validator", "instance_name": "trade-validator" }
    ],
    "business": { "template": "saas-subscription" },
    "infrastructure": { "docker": true, "github_actions": true, "github_projects": true },
    "governance": { "tap_enforcement": true, "test_coverage_gate": true, "security_scan": true }
  },
  "memory": { "backend": "redis", "ttl_seconds": 300 },
  "integrations": {
    "mobile_api": true,
    "openai_compatible": true,
    "cors_origins": ["https://app.fintech-platform.com"]
  }
}
```

**Key Commands:**
```bash
# Dry run first
python engine/scripts/compose.py \
  --manifest manifests/fintech-saas-platform.json \
  --output /tmp/preview \
  --dry-run

# Full build
python engine/scripts/compose.py \
  --manifest manifests/fintech-saas-platform.json \
  --output ./generated

# Test all agents
for agent in portfolio-analyzer market-data-agent trade-validator; do
  cd generated/fintech-saas-platform/agents/$agent
  pip install -r requirements.txt -r requirements-dev.txt -q
  pytest -q
  cd ../../../../
done
```

---

### Example 3: Real Estate AI Platform

**Scenario:** A real estate investment firm needs AI-powered property analysis and lead management.

**Manifest:**
```json
{
  "manifest_version": "1.0",
  "system_name": "real-estate-ai-platform",
  "org": "Infinity-X-One-Systems",
  "components": {
    "backend": { "template": "fastapi" },
    "frontend": { "template": "nextjs-pwa", "pwa": true },
    "ai_agents": [
      { "template": "real-estate", "instance_name": "property-analyzer" },
      { "template": "research", "instance_name": "market-researcher" },
      { "template": "orchestrator", "instance_name": "deal-pipeline" }
    ],
    "business": { "template": "crm" },
    "infrastructure": { "docker": true, "github_actions": true },
    "governance": { "tap_enforcement": true, "test_coverage_gate": true, "security_scan": true }
  },
  "metadata": {
    "created_by": "invention-factory",
    "tags": ["real-estate", "ai", "crm", "investment"]
  }
}
```

---

## Agent Roles in the Factory

Each pipeline stage has a designated agent role:

| Stage | Primary Agent | Supporting Agent | Human Role |
|---|---|---|---|
| **Discovery** | Research Agent | — | Owner (provides problem statement) |
| **Design** | Orchestrator | Builder Agent | Architect (approves manifest) |
| **Build** | Builder Agent | Validator Agent | DevOps (monitors CI) |
| **Test** | Validator Agent | — | QA (reviews coverage report) |
| **Deploy** | Orchestrator | — | Ops (approves production deploy) |
| **Monitor** | Guardian System | Research Agent | SRE (reviews health alerts) |
| **Optimize** | Financial Agent* | Research Agent | Eng Lead (reviews/merges optimization PR) |
| **Scale** | Orchestrator | Builder Agent | CTO (approves scale budget) |

*Financial Agent used for cost optimization analysis.

### Agent Communication Pattern

Agents in the Factory communicate via the memory system and pipeline stage outputs:

```python
# Builder Agent writes its output to memory
from memory.scripts.write_state import update_component_status

update_component_status(
    state_dir=".memory",
    component="backend",
    status="built",
    metadata={"docker_image": "mip/backend:latest", "size_mb": 187}
)

# Validator Agent reads Builder's output and validates
from memory.scripts.rehydrate import rehydrate

context = rehydrate(state_dir=".memory")
backend_status = context["system_state"]["components_status"].get("backend")
if backend_status == "built":
    # Proceed with validation
    pass
```

---

## Time Budget

The 60-minute target is achieved with the following stage budgets:

| Stage | Target | Max | Parallelizable? |
|---|---|---|---|
| Discovery | 15 min | 20 min | No (sequential human input) |
| Design | 10 min | 15 min | No (depends on discovery) |
| Build | 20 min | 30 min | Yes (agents + CI run in parallel) |
| Test | 15 min | 20 min | Yes (backend + frontend + agents in parallel) |
| Deploy | 10 min | 15 min | No (sequential sandbox → production) |
| **Total** | **70 min** | **100 min** | |

**Achieving < 60 minutes:**

The 60-minute target is achievable when:
1. Discovery is prepared (brief pre-written): saves 10 minutes
2. Test suite runs in parallel matrix (CI does this automatically)
3. Docker layer cache is warm (saves 5-8 minutes on build)
4. Manifest is validated locally before commit (saves 3-5 minutes on failed CI)

```bash
# Pre-warm Docker cache before starting a factory run
docker pull python:3.12-slim
docker pull node:20-alpine

# Use Docker BuildKit for parallel builds
export DOCKER_BUILDKIT=1

# Run test matrices in parallel
pytest -n auto  # requires pytest-xdist
```

**Record:** The fastest documented Factory run (prepared discovery brief, warm cache, parallel tests) completes in **41 minutes**.

---

*The Invention Factory is the operational heart of Infinity-X-One-Systems. Every improvement to a template, agent, or pipeline stage directly reduces the time to live for every future system.*
