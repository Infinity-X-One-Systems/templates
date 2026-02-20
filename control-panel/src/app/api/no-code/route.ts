import { NextRequest, NextResponse } from "next/server";

// No-Code API Contract — connects frontend to the template library
// Compatible with: Copilot Mobile, ChatGPT, Gemini, vizual-x.com, infinityxai.com
// This is the single REST contract that the Infinity Admin Control Plane calls

export const runtime = "edge";

type NoCodeOperation =
  | "list_categories"
  | "list_templates"
  | "get_template"
  | "compose_system"
  | "get_pipeline_stage"
  | "get_capabilities"
  | "get_blueprint";

interface NoCodeRequest {
  operation: NoCodeOperation;
  params?: Record<string, unknown>;
}

const TEMPLATE_CATEGORIES = [
  { id: "core", name: "Core Primitives", count: 2, description: "FastAPI + Next.js PWA foundations" },
  { id: "ai", name: "AI Agents", count: 6, description: "Research, Builder, Financial, Real Estate, Orchestrator, Validator" },
  { id: "industry", name: "Industry Templates", count: 20, description: "Construction to Portfolio Management" },
  { id: "business", name: "Business Automation", count: 5, description: "CRM, Lead Gen, Billing, SaaS, Marketplace" },
  { id: "connectors", name: "Connectors", count: 5, description: "OpenAI, Ollama, GitHub, Webhooks, Ingestion" },
  { id: "google", name: "Google Workspace", count: 4, description: "Gmail, Sheets, Docs, Drive" },
  { id: "infrastructure", name: "Infrastructure", count: 3, description: "Docker, GitHub Actions, Projects" },
  { id: "governance", name: "Governance", count: 4, description: "TAP, Coverage Gate, Security Scan, Guardian" },
  { id: "pipelines", name: "Pipeline Stages", count: 8, description: "Discovery→Design→Build→Test→Deploy→Monitor→Optimize→Scale" },
  { id: "agent-system", name: "Agent Capabilities", count: 10, description: "Upgrades, Skills, Knowledge, Blueprints..." },
  { id: "templates/github", name: "GitHub Templates", count: 6, description: "Repo, PR, Issue, Discussion templates" },
  { id: "templates/vscode", name: "VS Code Templates", count: 4, description: "Snippets, workspace, launch configs" },
  { id: "templates/autonomous-ai", name: "Autonomous AI", count: 3, description: "Self-running AI system templates" },
  { id: "templates/llm-chat", name: "LLM Chat", count: 3, description: "Chat interface templates" },
  { id: "templates/universal-business", name: "Universal Business", count: 1, description: "Replace any business system" },
  { id: "experimental", name: "Experimental", count: 3, description: "Game-changing AI/human collaboration" },
];

const PIPELINE_STAGES = ["discovery", "design", "build", "test", "deploy", "monitor", "optimize", "scale"];

const CAPABILITY_CATEGORIES = [
  "upgrades", "skills", "knowledge", "capabilities",
  "accessibility", "communication", "blueprints", "tools", "memory", "governance",
];

function handleOperation(op: NoCodeOperation, params: Record<string, unknown>) {
  switch (op) {
    case "list_categories":
      return { categories: TEMPLATE_CATEGORIES, total: TEMPLATE_CATEGORIES.length };

    case "list_templates": {
      const category = params.category as string | undefined;
      if (!category) return { error: "params.category is required" };
      const cat = TEMPLATE_CATEGORIES.find((c) => c.id === category);
      if (!cat) return { error: `Unknown category: ${category}` };
      return { category: cat, templates: [] }; // Real list comes from engine
    }

    case "get_template": {
      const id = params.template_id as string | undefined;
      if (!id) return { error: "params.template_id is required" };
      return { template_id: id, status: "available", source: `${id}/README.md` };
    }

    case "compose_system":
      return {
        status: "accepted",
        message: "System composition queued. Use /api/compose for full manifest submission.",
        compose_endpoint: "/api/compose",
      };

    case "get_pipeline_stage": {
      const stage = params.stage as string | undefined;
      if (!stage || !PIPELINE_STAGES.includes(stage)) {
        return { error: `Invalid stage. Valid: ${PIPELINE_STAGES.join(", ")}` };
      }
      return {
        stage,
        order: PIPELINE_STAGES.indexOf(stage) + 1,
        next: PIPELINE_STAGES[(PIPELINE_STAGES.indexOf(stage) + 1) % PIPELINE_STAGES.length],
      };
    }

    case "get_capabilities":
      return { categories: CAPABILITY_CATEGORIES };

    case "get_blueprint": {
      const name = params.blueprint_name as string | undefined;
      if (!name) return { error: "params.blueprint_name is required" };
      return { blueprint: name, source: `agent-system/capabilities/blueprints/manifest.json` };
    }

    default:
      return { error: `Unknown operation: ${op}` };
  }
}

export async function GET() {
  return NextResponse.json({
    service: "Infinity No-Code API",
    version: "1.0.0",
    operations: [
      "list_categories",
      "list_templates",
      "get_template",
      "compose_system",
      "get_pipeline_stage",
      "get_capabilities",
      "get_blueprint",
    ],
    docs: "https://github.com/Infinity-X-One-Systems/templates/blob/main/docs/admin-control-plane-contract.md",
  });
}

export async function POST(req: NextRequest) {
  let body: NoCodeRequest;
  try {
    body = (await req.json()) as NoCodeRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.operation) {
    return NextResponse.json({ error: "operation field is required" }, { status: 400 });
  }

  const result = handleOperation(body.operation, body.params ?? {});
  return NextResponse.json(result);
}
