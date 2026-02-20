# Infinity Template Library

> **Build production AI systems in under one hour.**
> 
> A fully modular, composable template library enabling agents to assemble complete frontend + backend + AI systems autonomously.

[![CI](https://github.com/Infinity-X-One-Systems/templates/actions/workflows/ci.yml/badge.svg)](https://github.com/Infinity-X-One-Systems/templates/actions/workflows/ci.yml)

---

## Quick Start

### Option 1: PWA Control Panel (Recommended)

```bash
cd control-panel
npm install
npm run dev
# Open http://localhost:3001
```

Select your templates, click "Compose System", and get a fully scaffolded repository.

### Option 2: CLI Composition Engine

```bash
pip install jsonschema
python engine/scripts/compose.py \
  --manifest manifests/example-ai-platform.json \
  --output ./generated
```

### Option 3: API / Mobile Access

The control panel exposes an **OpenAI-compatible** endpoint at `/api/v1/chat`:

```bash
curl -X POST https://your-control-panel.com/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"infinity-v1","messages":[{"role":"user","content":"List available templates"}]}'
```

Compatible with: **GitHub Copilot Mobile**, **ChatGPT**, **Google Gemini**, **vizual-x.com**, **infinityxai.com**

---

## Template Categories

| Category | Templates | Description |
|----------|-----------|-------------|
| **Core** | FastAPI, Next.js PWA | Mandatory primitives for every system |
| **Backend** | Express, FastAPI, GraphQL, WebSocket, AI Inference | API patterns |
| **Frontend** | Next.js PWA, Dashboard, Admin, SaaS, AI Console, Chat UI | UI patterns |
| **AI Agents** | Research, Builder, Financial, Real Estate, Orchestrator | Autonomous agents |
| **Business** | CRM, Lead Gen, Billing, SaaS Subscription, Marketplace | Workflow engines |
| **Infrastructure** | Docker Mesh, K8s, GitHub Actions, GitOps, Observability | Deployment |
| **Governance** | TAP Enforcement, Coverage Gate, Security Scan | Quality gates |

---

## System Manifest

Every system is defined by a JSON manifest:

```json
{
  "manifest_version": "1.0",
  "system_name": "my-ai-platform",
  "org": "Infinity-X-One-Systems",
  "components": {
    "backend": { "template": "fastapi" },
    "frontend": { "template": "nextjs-pwa", "pwa": true },
    "ai_agents": [
      { "template": "research", "instance_name": "market-researcher" },
      { "template": "orchestrator", "instance_name": "workflow-engine" }
    ],
    "infrastructure": { "docker": true, "github_actions": true },
    "governance": { "tap_enforcement": true, "test_coverage_gate": true }
  },
  "memory": { "backend": "redis", "ttl_seconds": 3600 },
  "integrations": {
    "mobile_api": true,
    "openai_compatible": true,
    "webhook_dispatch": true
  }
}
```

See [`engine/schema/manifest.schema.json`](engine/schema/manifest.schema.json) for the full schema.

---

## Auto-Scaffolding via GitHub Actions

Commit a manifest to `manifests/` and the scaffold workflow triggers automatically:

```bash
# Add your manifest
cp engine/schema/system-manifest.example.json manifests/my-system.json
# Edit it, then commit
git add manifests/my-system.json
git commit -m "feat: add my-system manifest"
git push
# GitHub Actions will scaffold the system and upload it as an artifact
```

Or trigger manually:

```bash
gh workflow run scaffold-on-manifest.yml \
  -f manifest_path=manifests/my-system.json \
  -f output_org=Infinity-X-One-Systems
```

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full architecture documentation.

## Security

See [SECURITY.md](SECURITY.md) for the security policy and implementation details.

---

## Template Constraints

All templates in this library satisfy:

- ✅ Compilable (no placeholder stubs)
- ✅ Tests included (pytest / jest)
- ✅ Docker configuration
- ✅ CI workflow (.github/workflows/)
- ✅ README + ARCHITECTURE + SECURITY docs
- ✅ Composable via manifest
- ✅ PWA capability (frontend templates)
- ✅ GitHub Actions integration
- ✅ repository_dispatch support
- ✅ Memory interface contract
- ✅ TAP governance enforced
