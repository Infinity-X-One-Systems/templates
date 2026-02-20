import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

// Schema mirrors the JSON manifest schema
const ManifestSchema = z.object({
  manifest_version: z.literal("1.0"),
  system_name: z.string().min(3).max(63).regex(/^[a-z][a-z0-9-]+$/),
  org: z.string().min(1),
  description: z.string().max(500).optional(),
  components: z.object({
    backend: z.object({ template: z.string() }).optional(),
    frontend: z.object({ template: z.string(), pwa: z.boolean().optional() }).optional(),
    ai_agents: z.array(z.object({ template: z.string(), instance_name: z.string().optional() })).optional(),
    infrastructure: z.record(z.boolean()).optional(),
    governance: z.record(z.boolean()).optional(),
  }),
  memory: z.object({ backend: z.string(), ttl_seconds: z.number() }).optional(),
  integrations: z.object({
    mobile_api: z.boolean().optional(),
    openai_compatible: z.boolean().optional(),
    webhook_dispatch: z.boolean().optional(),
    cors_origins: z.array(z.string()).optional(),
  }).optional(),
});

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const parsed = ManifestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: "Manifest validation failed", details: parsed.error.flatten() }, { status: 422 });
  }

  // In production: trigger GitHub repository_dispatch to scaffold the system
  const dispatchPayload = {
    event_type: "scaffold-system",
    client_payload: {
      manifest: parsed.data,
      manifest_path: `manifests/${parsed.data.system_name}.json`,
      initiated_at: new Date().toISOString(),
    },
  };

  // Optionally trigger GitHub Actions dispatch
  const githubToken = process.env.GITHUB_TOKEN;
  const githubOrg = parsed.data.org;
  const githubRepo = process.env.TEMPLATE_REPO ?? "templates";

  let dispatchStatus = "skipped (no GITHUB_TOKEN)";
  if (githubToken) {
    try {
      const dispatchRes = await fetch(
        `https://api.github.com/repos/${githubOrg}/${githubRepo}/dispatches`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${githubToken}`,
            "Content-Type": "application/json",
            Accept: "application/vnd.github+json",
          },
          body: JSON.stringify(dispatchPayload),
        }
      );
      if (!dispatchRes.ok) {
        const errText = await dispatchRes.text().catch(() => dispatchRes.statusText);
        console.error(`GitHub dispatch failed: ${dispatchRes.status} ${errText}`);
        dispatchStatus = `failed (${dispatchRes.status})`;
      } else {
        dispatchStatus = "triggered";
      }
    } catch (err) {
      console.error("GitHub dispatch error:", err);
      dispatchStatus = "error (network)";
    }
  }

  return NextResponse.json({
    success: true,
    system_name: parsed.data.system_name,
    manifest: parsed.data,
    dispatch: dispatchStatus,
    created_at: new Date().toISOString(),
  });
}

export async function GET() {
  return NextResponse.json({
    endpoint: "/api/compose",
    description: "Compose a full production system from a manifest",
    method: "POST",
    body_schema: "See engine/schema/manifest.schema.json",
  });
}
