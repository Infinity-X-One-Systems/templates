# Infinity Admin Control Plane — Integration Contract

> This document defines the machine-readable contract for connecting any system
> to the Infinity Admin Control Plane (`infinity-admin-control-plane` repository).

**Contract Version:** 1.0.0  
**Schema:** `https://infinityxai.com/schemas/control-plane-contract.json`  
**Status:** Production

---

## Overview

The Admin Control Plane is the central nervous system of the Infinity ecosystem. It coordinates all system composition, agent orchestration, pipeline execution, and governance enforcement across every Infinity-managed system.

The `templates` repository serves as the **template library** that the Control Plane pulls from. When the Control Plane receives a composition request (from a user, an agent, or an external system), it:

1. Selects templates from this library based on the system manifest
2. Dispatches to this repository via `repository_dispatch`
3. Receives the scaffolded system as a GitHub Actions artifact
4. Registers the system in the global registry
5. Monitors the system via the Guardian

```
External Client                Admin Control Plane            Templates Repo
(ChatGPT / Copilot / API)           │                              │
         │                          │                              │
         │  POST /api/v1/chat        │                              │
         ├─────────────────────────►│                              │
         │                          │  repository_dispatch         │
         │                          │  event: scaffold-system      │
         │                          ├─────────────────────────────►│
         │                          │                              │ compose.py
         │                          │                              │ runs
         │                          │  artifact: generated-system  │
         │                          │◄─────────────────────────────┤
         │  {"status":"composed"}   │                              │
         │◄─────────────────────────┤                              │
```

---

## REST API Contract

### Base URL

```
https://{control-plane-host}/api/v1
```

For local development:
```
http://localhost:3001
```

### Authentication

All requests must include a Bearer token:

```
Authorization: Bearer {INFINITY_API_KEY}
```

The `INFINITY_API_KEY` is set in the `API_KEY` environment variable of the Control Panel deployment.

**Error response when unauthenticated:**
```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": 401
  }
}
```

---

### Endpoints

#### `GET /api/health`

Returns the health status of the Control Panel service.

**Request:**
```bash
curl https://{host}/api/health \
  -H "Authorization: Bearer {INFINITY_API_KEY}"
```

**Response `200 OK`:**
```json
{
  "status": "ok",
  "service": "infinity-control-panel",
  "version": "1.0.0",
  "timestamp": "2026-02-20T04:00:00.000Z"
}
```

**Notes:**
- This endpoint does NOT require authentication in development
- Used by Docker health checks and guardian monitoring
- Response time target: < 50ms

---

#### `GET /api/no-code`

Returns the list of available no-code operations. Used by AI clients to discover capabilities.

**Request:**
```bash
curl https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}"
```

**Response `200 OK`:**
```json
{
  "service": "Infinity No-Code API",
  "version": "1.0.0",
  "operations": [
    "list_categories",
    "list_templates",
    "get_template",
    "compose_system",
    "get_pipeline_stage",
    "get_capabilities",
    "get_blueprint"
  ],
  "docs": "https://github.com/Infinity-X-One-Systems/templates/blob/main/docs/admin-control-plane-contract.md"
}
```

---

#### `POST /api/no-code`

The primary machine-readable interface for the Control Plane. All 7 operations are multiplexed through this endpoint.

**Request Schema:**
```typescript
{
  operation: "list_categories" | "list_templates" | "get_template" |
             "compose_system" | "get_pipeline_stage" |
             "get_capabilities" | "get_blueprint";
  params?: Record<string, unknown>;
}
```

**Operation 1: `list_categories`**

Lists all template categories available in the library.

```bash
curl -X POST https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "list_categories"}'
```

Response:
```json
{
  "categories": [
    { "id": "core", "name": "Core Primitives", "count": 2, "description": "FastAPI + Next.js PWA foundations" },
    { "id": "ai", "name": "AI Agents", "count": 6, "description": "Research, Builder, Financial, Real Estate, Orchestrator, Validator" },
    { "id": "industry", "name": "Industry Templates", "count": 20, "description": "Construction to Portfolio Management" },
    { "id": "business", "name": "Business Automation", "count": 5, "description": "CRM, Lead Gen, Billing, SaaS, Marketplace" },
    { "id": "connectors", "name": "Connectors", "count": 5, "description": "OpenAI, Ollama, GitHub, Webhooks, Ingestion" },
    { "id": "google", "name": "Google Workspace", "count": 4, "description": "Gmail, Sheets, Docs, Drive" },
    { "id": "infrastructure", "name": "Infrastructure", "count": 3, "description": "Docker, GitHub Actions, Projects" },
    { "id": "governance", "name": "Governance", "count": 4, "description": "TAP, Coverage Gate, Security Scan, Guardian" },
    { "id": "pipelines", "name": "Pipeline Stages", "count": 8, "description": "Discovery→Design→Build→Test→Deploy→Monitor→Optimize→Scale" },
    { "id": "experimental", "name": "Experimental", "count": 3, "description": "Game-changing AI/human collaboration" }
  ],
  "total": 16
}
```

**Operation 2: `list_templates`**

Lists templates in a specific category.

```bash
curl -X POST https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "list_templates", "params": {"category": "ai"}}'
```

Response:
```json
{
  "category": { "id": "ai", "name": "AI Agents", "count": 6 },
  "templates": []
}
```

**Operation 3: `get_template`**

Get metadata for a specific template.

```bash
curl -X POST https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_template", "params": {"template_id": "ai/research-agent"}}'
```

Response:
```json
{
  "template_id": "ai/research-agent",
  "status": "available",
  "source": "ai/research-agent/README.md"
}
```

**Operation 4: `compose_system`**

Queue a system for composition. Redirects to `/api/compose` for full manifest handling.

```bash
curl -X POST https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "compose_system", "params": {"system_name": "my-platform"}}'
```

Response:
```json
{
  "status": "accepted",
  "message": "System composition queued. Use /api/compose for full manifest submission.",
  "compose_endpoint": "/api/compose"
}
```

**Operation 5: `get_pipeline_stage`**

Get metadata for a specific pipeline stage.

```bash
curl -X POST https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_pipeline_stage", "params": {"stage": "build"}}'
```

Response:
```json
{
  "stage": "build",
  "order": 3,
  "next": "test"
}
```

**Operation 6: `get_capabilities`**

List agent capability categories.

```bash
curl -X POST https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_capabilities"}'
```

Response:
```json
{
  "categories": [
    "upgrades", "skills", "knowledge", "capabilities",
    "accessibility", "communication", "blueprints",
    "tools", "memory", "governance"
  ]
}
```

**Operation 7: `get_blueprint`**

Retrieve a named blueprint from the agent capability library.

```bash
curl -X POST https://{host}/api/no-code \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "get_blueprint", "params": {"blueprint_name": "discovery-loop"}}'
```

Response:
```json
{
  "blueprint": "discovery-loop",
  "source": "agent-system/capabilities/blueprints/manifest.json"
}
```

---

#### `POST /api/v1/chat`

OpenAI-compatible chat completions endpoint. Enables access from ChatGPT Actions, GitHub Copilot, Gemini Extensions, and any OpenAI SDK-compatible client.

**Supported Client Integrations:**
- GitHub Copilot Mobile App
- ChatGPT iOS/Android App (via Custom GPT Actions)
- Google Gemini App (via Custom Extensions)
- vizual-x.com
- infinityxai.com (Infinity Orchestrator)

**Request Schema** (OpenAI-compatible):
```typescript
{
  model: string;               // e.g., "infinity-v1"
  messages: Array<{
    role: "system" | "user" | "assistant";
    content: string;
  }>;
  stream?: boolean;            // default: false
  temperature?: number;        // 0–2, default: 0.7
  max_tokens?: number;
}
```

**Request:**
```bash
curl -X POST https://{host}/api/v1/chat \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "infinity-v1",
    "messages": [
      {"role": "user", "content": "List available templates"}
    ]
  }'
```

**Response `200 OK`** (OpenAI-compatible format):
```json
{
  "id": "chatcmpl-infinity-1234567890",
  "object": "chat.completion",
  "model": "infinity-v1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Available templates:\n\n**Backend:** fastapi, express, graphql...\n\n**AI Agents:** research, builder, validator..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 120,
    "total_tokens": 125
  }
}
```

**Intent Classification:**

The endpoint classifies user intents and routes them:

| Keyword Pattern | Intent | Action |
|---|---|---|
| "compose", "scaffold", "create system" | `compose` | Returns manifest template + compose endpoint URL |
| "list templates", "show templates" | `list_templates` | Returns formatted template list |
| "status", "health" | `health` | Returns system health |
| (anything else) | `general` | Returns capability overview |

---

#### `POST /api/compose`

Full manifest submission and system composition trigger. This is the primary endpoint called by the Admin Control Plane to request scaffolding.

**Request** — System manifest (matches `engine/schema/manifest.schema.json`):
```bash
curl -X POST https://{host}/api/compose \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_version": "1.0",
    "system_name": "my-ai-platform",
    "org": "Infinity-X-One-Systems",
    "components": {
      "backend": {"template": "fastapi"},
      "frontend": {"template": "nextjs-pwa", "pwa": true},
      "ai_agents": [
        {"template": "research", "instance_name": "market-researcher"},
        {"template": "orchestrator", "instance_name": "workflow-engine"}
      ],
      "infrastructure": {"docker": true, "github_actions": true},
      "governance": {"tap_enforcement": true, "test_coverage_gate": true}
    },
    "memory": {"backend": "redis", "ttl_seconds": 3600},
    "integrations": {"mobile_api": true, "openai_compatible": true}
  }'
```

**Response `200 OK`:**
```json
{
  "status": "dispatched",
  "system_name": "my-ai-platform",
  "dispatch_event": "scaffold-system",
  "initiated_at": "2026-02-20T04:00:00.000Z",
  "manifest_path": "manifests/my-ai-platform.json"
}
```

**Response `422 Unprocessable Entity`** (invalid manifest):
```json
{
  "error": "Manifest validation failed",
  "details": {
    "fieldErrors": {
      "system_name": ["String must start with a lowercase letter"]
    },
    "formErrors": []
  }
}
```

**Internal Behavior:**

When a valid manifest is received, the endpoint:
1. Validates the manifest against the Zod schema
2. Constructs a `repository_dispatch` payload:
   ```json
   {
     "event_type": "scaffold-system",
     "client_payload": {
       "manifest": { "...": "..." },
       "manifest_path": "manifests/{system_name}.json",
       "initiated_at": "2026-02-20T04:00:00.000Z"
     }
   }
   ```
3. POSTs to `https://api.github.com/repos/{org}/{TEMPLATE_REPO}/dispatches`
4. Returns acceptance status — scaffolding is asynchronous

---

## WebSocket Contract

### Endpoint

```
wss://{control-plane-host}/ws/agents
```

### Connection

```javascript
const ws = new WebSocket("wss://your-host/ws/agents", {
  headers: { "Authorization": `Bearer ${INFINITY_API_KEY}` }
});
```

### Message Protocol

All messages are JSON objects with a `type` field.

**Client → Server (Agent Status Update):**
```json
{
  "type": "agent_status",
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "iteration": 3,
  "timestamp": "2026-02-20T04:00:00Z"
}
```

**Client → Server (Task Result):**
```json
{
  "type": "task_result",
  "task_id": "task-abc123",
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true,
  "output": { "findings": ["..."] },
  "duration_ms": 1234.5
}
```

**Server → Client (Task Assignment):**
```json
{
  "type": "task_assign",
  "task_id": "task-abc123",
  "task": {
    "type": "research",
    "query": "Analyze Q1 2026 fintech trends",
    "context": { "industry": "fintech", "depth": "comprehensive" }
  }
}
```

**Server → Client (System Event):**
```json
{
  "type": "system_event",
  "event": "new_manifest_committed",
  "payload": {
    "manifest_path": "manifests/new-system.json",
    "system_name": "new-system"
  }
}
```

---

## Repository Dispatch Contract

### Event: `scaffold-system`

Triggered by `/api/compose` or directly via GitHub API to scaffold a new system.

**Sender:**
```bash
curl -X POST \
  -H "Authorization: Bearer {GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Infinity-X-One-Systems/templates/dispatches \
  -d '{
    "event_type": "scaffold-system",
    "client_payload": {
      "manifest_path": "manifests/my-system.json",
      "output_org": "Infinity-X-One-Systems",
      "dry_run": false
    }
  }'
```

**Payload Schema:**
```typescript
{
  manifest_path: string;       // Required: path to manifest in repo
  output_org?: string;         // Optional: target org for new repo
  dry_run?: boolean;           // Optional: validate only, default false
  manifest?: object;           // Optional: inline manifest (skips file read)
}
```

**Resulting Workflow:** `scaffold-on-manifest.yml`

The workflow:
1. Reads/validates the manifest at `manifest_path`
2. Runs `engine/scripts/compose.py --manifest {path} --output ./generated`
3. Uploads the generated system as a GitHub Actions artifact
4. Sets outputs: `system_name`, `manifest_valid`

---

## Memory Contract

### `system_state.json` Schema

Location: `.memory/system_state.json` (relative to working directory)

```json
{
  "manifest_version": "1.0",
  "system_name": "my-system",
  "org": "Infinity-X-One-Systems",
  "phase": "building",
  "components_status": {
    "backend": "healthy",
    "frontend": "building",
    "agents": "healthy"
  },
  "last_action": "scaffold_backend",
  "last_action_at": "2026-02-20T04:00:00Z",
  "health_score": 90,
  "errors": [],
  "warnings": ["redis not configured, using in-memory fallback"]
}
```

**Phase Enum:** `planning` | `building` | `testing` | `deployed`

### `decision_log.json` Schema

Location: `.memory/decision_log.json`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-02-20T04:00:00Z",
    "decision_type": "architecture",
    "description": "Use PostgreSQL for primary persistence",
    "rationale": "ACID compliance required for financial data",
    "made_by": "human",
    "outcome": "Adopted in v1",
    "related_components": ["backend", "memory"]
  }
]
```

### `architecture_map.json` Schema

Location: `.memory/architecture_map.json`

```json
{
  "system_name": "my-system",
  "components": [
    {
      "name": "backend",
      "type": "fastapi",
      "path": "backend/",
      "status": "healthy",
      "dependencies": ["postgres", "redis"],
      "health": 98
    }
  ],
  "dependency_graph": {
    "backend": ["postgres", "redis"],
    "frontend": ["backend"],
    "agents": ["backend", "openai"]
  },
  "last_updated": "2026-02-20T04:00:00Z"
}
```

### `telemetry.json` Schema

Location: `.memory/telemetry.json`

```json
[
  {
    "event_id": "660e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-02-20T04:00:00Z",
    "event_type": "test_pass",
    "component": "backend",
    "value": 120,
    "unit": "ms",
    "metadata": {
      "test": "test_api_health",
      "run_id": "abc123"
    }
  }
]
```

**Event Type Enum:** `workflow_run` | `test_pass` | `test_fail` | `deploy` | `error` | `health_check`

---

## Agent Registration Contract

Agents that connect to the Control Plane must satisfy the agent interface contract at `agent-system/contracts/agent-interface.json`.

### Registration Payload

```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "market-researcher",
  "role": "research",
  "capabilities": [
    { "category": "skills", "name": "web-search", "version": "1.0.0" },
    { "category": "knowledge", "name": "financial-markets", "version": "1.0.0" },
    { "category": "memory", "name": "session-memory", "version": "1.0.0" },
    { "category": "governance", "name": "tap-check", "version": "1.0.0" }
  ],
  "status": "idle",
  "iteration": 0,
  "metadata": {
    "version": "1.0.0",
    "template": "research-agent",
    "spawned_by": "infinity-orchestrator",
    "spawned_at": "2026-02-20T04:00:00Z"
  }
}
```

### Registration Endpoint

```bash
curl -X POST https://{control-plane-host}/api/agents/register \
  -H "Authorization: Bearer {INFINITY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @agent-registration.json
```

### Agent Lifecycle States

```
idle ──► running ──► complete
  │          │
  │       paused ──► running
  │          │
  └──────► error ──► idle (after recovery)
```

---

## Governance Requirements

### TAP Compliance

All systems connected to the Control Plane must be TAP-compliant:

| Requirement | Verification |
|---|---|
| README.md present | File existence check in scaffold workflow |
| ARCHITECTURE.md present | File existence check in scaffold workflow |
| SECURITY.md present | File existence check in scaffold workflow |
| Tests present | `tests/` directory non-empty |
| Coverage ≥ 80% | `coverage-gate.yml` must pass |
| No critical CVEs | `security-scan.yml` must pass |
| Conventional commits | PR title format enforced |

### Bounded Autonomy Limits

| Action | Autonomy Level | Human Approval Required |
|---|---|---|
| Read system state | Full autonomy | No |
| Write system state | Full autonomy | No |
| Log decisions/telemetry | Full autonomy | No |
| Scaffold a new system | Agent-initiated | No (bounded by manifest schema) |
| Deploy to sandbox | Agent-initiated | No |
| Deploy to production | Bounded | Yes |
| Apply infrastructure changes | Bounded | Yes |
| Delete any resource | Prohibited | Always — never automated |
| Modify governance rules | Prohibited | Always — senior human only |

---

## SDK Usage Examples

### Python SDK

```python
import httpx
import json

CONTROL_PLANE_URL = "https://your-control-plane.infinityxai.com"
API_KEY = "your-infinity-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

async def compose_system(manifest: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONTROL_PLANE_URL}/api/compose",
            headers=headers,
            json=manifest,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

async def list_templates(category: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONTROL_PLANE_URL}/api/no-code",
            headers=headers,
            json={"operation": "list_templates", "params": {"category": category}},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

async def chat(message: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONTROL_PLANE_URL}/api/v1/chat",
            headers=headers,
            json={
                "model": "infinity-v1",
                "messages": [{"role": "user", "content": message}]
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

### TypeScript / Node.js SDK

```typescript
const CONTROL_PLANE_URL = process.env.CONTROL_PLANE_URL!;
const API_KEY = process.env.INFINITY_API_KEY!;

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json",
};

export async function composeSystem(manifest: object): Promise<object> {
  const response = await fetch(`${CONTROL_PLANE_URL}/api/compose`, {
    method: "POST",
    headers,
    body: JSON.stringify(manifest),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Compose failed: ${JSON.stringify(error)}`);
  }
  return response.json();
}

export async function chat(message: string): Promise<string> {
  const response = await fetch(`${CONTROL_PLANE_URL}/api/v1/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      model: "infinity-v1",
      messages: [{ role: "user", content: message }],
    }),
  });
  const data = await response.json();
  return data.choices[0].message.content;
}

// OpenAI SDK compatibility
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: API_KEY,
  baseURL: `${CONTROL_PLANE_URL}/api/v1`,
});

const response = await client.chat.completions.create({
  model: "infinity-v1",
  messages: [{ role: "user", content: "List available AI agent templates" }],
});
```

### curl Examples

```bash
# Health check
curl https://{host}/api/health

# List categories (no auth in dev)
curl https://{host}/api/no-code

# Chat completion
curl -X POST https://{host}/api/v1/chat \
  -H "Authorization: Bearer $INFINITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"infinity-v1","messages":[{"role":"user","content":"status"}]}'

# Full system composition
curl -X POST https://{host}/api/compose \
  -H "Authorization: Bearer $INFINITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d @manifests/example-ai-platform.json

# Trigger scaffold via GitHub dispatch
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Infinity-X-One-Systems/templates/dispatches \
  -d '{"event_type":"scaffold-system","client_payload":{"manifest_path":"manifests/my-system.json"}}'
```

---

## Contract Versioning

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-02-20 | Initial contract — all 7 no-code ops, compose, chat, dispatch |

**Breaking changes** to this contract require:
1. A new contract version number
2. A migration guide
3. Deprecation notice with 30-day transition period
4. Decision log entry with `decision_type: "architecture"` and `made_by: "human"`

---

*Contract maintained by Infinity-X-One-Systems Engineering. File issues at `Infinity-X-One-Systems/templates`.*
