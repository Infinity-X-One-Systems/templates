/**
 * OpenAI-compatible /v1/chat/completions endpoint.
 * Enables access from ChatGPT Actions, GitHub Copilot, Gemini Extensions,
 * mobile apps, and any OpenAI-SDK-compatible client.
 *
 * Supported clients:
 *  - GitHub Copilot Mobile App
 *  - ChatGPT iOS/Android App (via Custom GPT Actions)
 *  - Google Gemini App (via Custom Extensions)
 *  - vizual-x.com
 *  - infinityxai.com (Infinity Orchestrator)
 */
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

const MessageSchema = z.object({
  role: z.enum(["system", "user", "assistant"]),
  content: z.string(),
});

const ChatRequestSchema = z.object({
  model: z.string().default("infinity-v1"),
  messages: z.array(MessageSchema).min(1),
  stream: z.boolean().optional().default(false),
  temperature: z.number().min(0).max(2).optional().default(0.7),
  max_tokens: z.number().positive().optional(),
});

// Simple intent classifier for system commands
function classifyIntent(message: string): string {
  const m = message.toLowerCase();
  if (m.includes("compose") || m.includes("scaffold") || m.includes("create system")) return "compose";
  if (m.includes("list templates") || m.includes("show templates")) return "list_templates";
  if (m.includes("status") || m.includes("health")) return "health";
  return "general";
}

function handleIntent(intent: string, message: string): string {
  switch (intent) {
    case "compose":
      return `To compose a new system, visit ${process.env.NEXT_PUBLIC_CONTROL_PANEL_URL ?? "https://infinityxai.com"}/compose or POST to /api/compose with a system manifest.\n\nExample manifest:\n\`\`\`json\n{\n  "manifest_version": "1.0",\n  "system_name": "my-system",\n  "org": "your-org",\n  "components": {\n    "backend": {"template": "fastapi"},\n    "frontend": {"template": "nextjs-pwa"}\n  }\n}\n\`\`\``;
    case "list_templates":
      return "Available templates:\n\n**Backend:** fastapi, express, graphql, websocket, ai-inference, event-worker\n\n**Frontend:** nextjs-pwa, dashboard, admin-panel, saas-landing, ai-console, chat-ui\n\n**AI Agents:** research, builder, validator, financial, real-estate, orchestrator\n\n**Governance:** tap-enforcement, test-coverage-gate, security-scan";
    case "health":
      return `System status: ✅ OK\nService: infinity-control-panel\nTimestamp: ${new Date().toISOString()}`;
    default:
      return `I'm the Infinity X One Orchestrator. I can help you:\n\n1. **Compose systems** — "Compose a FastAPI + Next.js system"\n2. **List templates** — "Show available templates"\n3. **Check status** — "System health"\n\nWhat would you like to build today?`;
  }
}

export async function POST(request: NextRequest) {
  // API key validation
  const authHeader = request.headers.get("Authorization");
  const apiKey = process.env.API_KEY;
  if (apiKey && (!authHeader || authHeader !== `Bearer ${apiKey}`)) {
    return NextResponse.json({ error: { message: "Invalid API key", type: "invalid_request_error" } }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ error: { message: "Invalid JSON", type: "invalid_request_error" } }, { status: 400 });
  }

  const parsed = ChatRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: { message: "Invalid request", type: "invalid_request_error", details: parsed.error.flatten() } }, { status: 422 });
  }

  const { messages, model } = parsed.data;
  const lastUserMessage = [...messages].reverse().find((m) => m.role === "user");
  const userContent = lastUserMessage?.content ?? "";
  const intent = classifyIntent(userContent);
  const responseContent = handleIntent(intent, userContent);

  // OpenAI-compatible response format
  return NextResponse.json({
    id: `chatcmpl-${crypto.randomUUID().replace(/-/g, "").slice(0, 20)}`,
    object: "chat.completion",
    created: Math.floor(Date.now() / 1000),
    model,
    choices: [
      {
        index: 0,
        message: { role: "assistant", content: responseContent },
        finish_reason: "stop",
      },
    ],
    usage: {
      // Note: word count is used as an approximation. For accurate token counts,
      // integrate a proper tokenizer (e.g., tiktoken for OpenAI-compatible models).
      prompt_tokens: userContent.split(/\s+/).filter(Boolean).length,
      completion_tokens: responseContent.split(/\s+/).filter(Boolean).length,
      total_tokens:
        userContent.split(/\s+/).filter(Boolean).length +
        responseContent.split(/\s+/).filter(Boolean).length,
    },
  });
}

export async function GET() {
  return NextResponse.json({
    endpoint: "/api/v1/chat",
    description: "OpenAI-compatible chat endpoint for Infinity X One Orchestrator",
    compatible_with: ["ChatGPT Actions", "GitHub Copilot", "Gemini Extensions", "OpenAI SDK", "vizual-x.com", "infinityxai.com"],
    model: "infinity-v1",
    capabilities: ["system-composition", "template-listing", "health-check", "general-qa"],
  });
}
