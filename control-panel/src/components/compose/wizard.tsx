"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const manifestSchema = z.object({
  system_name: z.string().min(3).max(63).regex(/^[a-z][a-z0-9-]+$/, "Must be kebab-case"),
  org: z.string().min(1, "Organization is required"),
  description: z.string().max(500).optional(),
  backend_template: z.enum(["fastapi", "express", "graphql", "websocket", "ai-inference", "event-worker"]),
  frontend_template: z.enum(["nextjs-pwa", "vite-react", "dashboard", "admin-panel", "saas-landing", "ai-console", "chat-ui"]),
  ai_agents: z.array(z.string()).default([]),
  include_docker: z.boolean().default(true),
  include_github_actions: z.boolean().default(true),
  include_governance: z.boolean().default(true),
  memory_backend: z.enum(["in-memory", "redis", "postgres"]).default("in-memory"),
  mobile_api: z.boolean().default(true),
});

type ManifestForm = z.infer<typeof manifestSchema>;

const AI_AGENT_OPTIONS = [
  { value: "research", label: "Research Agent" },
  { value: "builder", label: "Builder Agent" },
  { value: "financial", label: "Financial Analyzer" },
  { value: "real-estate", label: "Real Estate Distress Analyzer" },
  { value: "orchestrator", label: "Workflow Orchestrator" },
];

interface WizardProps {
  onComplete?: (manifest: object) => void;
}

export function CompositionWizard({ onComplete }: WizardProps) {
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generatedManifest, setGeneratedManifest] = useState<object | null>(null);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<ManifestForm>({
    resolver: zodResolver(manifestSchema),
    defaultValues: {
      backend_template: "fastapi",
      frontend_template: "nextjs-pwa",
      ai_agents: [],
      include_docker: true,
      include_github_actions: true,
      include_governance: true,
      memory_backend: "in-memory",
      mobile_api: true,
    },
  });

  const selectedAgents = watch("ai_agents");

  const toggleAgent = (value: string) => {
    const current = selectedAgents ?? [];
    setValue("ai_agents", current.includes(value) ? current.filter((a) => a !== value) : [...current, value]);
  };

  const onSubmit = async (data: ManifestForm) => {
    setIsSubmitting(true);
    const manifest = buildManifest(data);
    try {
      const res = await fetch("/api/compose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(manifest),
      });
      if (res.ok) {
        setGeneratedManifest(manifest);
        onComplete?.(manifest);
        setStep(4);
      }
    } catch {
      // Show error
    } finally {
      setIsSubmitting(false);
    }
  };

  if (step === 4 && generatedManifest) {
    return <SuccessStep manifest={generatedManifest} onReset={() => { setStep(1); setGeneratedManifest(null); }} />;
  }

  return (
    <div className="max-w-2xl mx-auto">
      <StepIndicator current={step} total={3} />
      <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white">System Identity</h2>
            <Field label="System Name" error={errors.system_name?.message}>
              <input {...register("system_name")} placeholder="my-ai-platform" className="input-field" />
            </Field>
            <Field label="Organization" error={errors.org?.message}>
              <input {...register("org")} placeholder="Infinity-X-One-Systems" className="input-field" />
            </Field>
            <Field label="Description" error={errors.description?.message}>
              <textarea {...register("description")} rows={2} placeholder="What does this system do?" className="input-field" />
            </Field>
          </div>
        )}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white">Select Templates</h2>
            <Field label="Backend Template">
              <select {...register("backend_template")} className="input-field">
                <option value="fastapi">FastAPI (Python)</option>
                <option value="express">Express (Node.js)</option>
                <option value="graphql">GraphQL API</option>
                <option value="websocket">WebSocket Server</option>
                <option value="ai-inference">AI Inference Server</option>
                <option value="event-worker">Event Worker</option>
              </select>
            </Field>
            <Field label="Frontend Template">
              <select {...register("frontend_template")} className="input-field">
                <option value="nextjs-pwa">Next.js PWA</option>
                <option value="dashboard">Dashboard</option>
                <option value="admin-panel">Admin Panel</option>
                <option value="saas-landing">SaaS Landing</option>
                <option value="ai-console">AI Command Console</option>
                <option value="chat-ui">Chat UI</option>
              </select>
            </Field>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">AI Agents</label>
              <div className="space-y-2">
                {AI_AGENT_OPTIONS.map((opt) => (
                  <label key={opt.value} className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedAgents?.includes(opt.value) ?? false}
                      onChange={() => toggleAgent(opt.value)}
                      className="rounded border-gray-600"
                    />
                    <span className="text-gray-300 text-sm">{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white">Infrastructure & Governance</h2>
            {[
              { name: "include_docker" as const, label: "Docker Configuration" },
              { name: "include_github_actions" as const, label: "GitHub Actions CI" },
              { name: "include_governance" as const, label: "TAP Governance" },
              { name: "mobile_api" as const, label: "Mobile API Bridge (Copilot/ChatGPT/Gemini)" },
            ].map(({ name, label }) => (
              <label key={name} className="flex items-center justify-between cursor-pointer">
                <span className="text-gray-300">{label}</span>
                <input type="checkbox" {...register(name)} className="rounded border-gray-600" />
              </label>
            ))}
            <Field label="Memory Backend">
              <select {...register("memory_backend")} className="input-field">
                <option value="in-memory">In-Memory (dev)</option>
                <option value="redis">Redis</option>
                <option value="postgres">PostgreSQL</option>
              </select>
            </Field>
          </div>
        )}

        <div className="flex gap-3 justify-between pt-4">
          {step > 1 && (
            <button type="button" onClick={() => setStep(s => s - 1)} className="px-6 py-2 rounded-lg border border-gray-700 text-gray-300 hover:border-indigo-500">
              ← Back
            </button>
          )}
          {step < 3 ? (
            <button type="button" onClick={() => setStep(s => s + 1)} className="ml-auto px-6 py-2 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-500">
              Next →
            </button>
          ) : (
            <button type="submit" disabled={isSubmitting} className="ml-auto px-8 py-2 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-500 disabled:opacity-50">
              {isSubmitting ? "Composing..." : "🚀 Compose System"}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

function StepIndicator({ current, total }: { current: number; total: number }) {
  return (
    <div className="flex items-center gap-2">
      {Array.from({ length: total }, (_, i) => i + 1).map((n) => (
        <div key={n} className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${n <= current ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-500"}`}>{n}</div>
          {n < total && <div className={`h-0.5 w-12 ${n < current ? "bg-indigo-600" : "bg-gray-700"}`} />}
        </div>
      ))}
    </div>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-1">{label}</label>
      {children}
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
}

function buildManifest(data: ManifestForm): object {
  return {
    manifest_version: "1.0",
    system_name: data.system_name,
    org: data.org,
    description: data.description ?? "",
    components: {
      backend: { template: data.backend_template },
      frontend: { template: data.frontend_template, pwa: true },
      ai_agents: data.ai_agents.map((a) => ({ template: a, instance_name: a })),
      infrastructure: {
        docker: data.include_docker,
        github_actions: data.include_github_actions,
        github_projects: true,
      },
      governance: {
        tap_enforcement: data.include_governance,
        test_coverage_gate: data.include_governance,
        security_scan: data.include_governance,
      },
    },
    memory: { backend: data.memory_backend, ttl_seconds: 3600 },
    integrations: {
      mobile_api: data.mobile_api,
      openai_compatible: true,
      webhook_dispatch: true,
      cors_origins: ["https://infinityxai.com", "https://vizual-x.com"],
    },
  };
}

function SuccessStep({ manifest, onReset }: { manifest: object; onReset: () => void }) {
  return (
    <div className="max-w-2xl mx-auto text-center space-y-6">
      <div className="w-16 h-16 rounded-full bg-green-600 flex items-center justify-center mx-auto">
        <span className="text-white text-2xl">✓</span>
      </div>
      <h2 className="text-2xl font-bold text-white">System Composed!</h2>
      <p className="text-gray-400">Your system manifest has been generated and scaffolding has begun.</p>
      <div className="text-left bg-gray-900 rounded-xl p-4 overflow-auto max-h-64 border border-gray-700">
        <pre className="text-xs text-gray-300">{JSON.stringify(manifest, null, 2)}</pre>
      </div>
      <button onClick={onReset} className="px-6 py-2 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-500">
        Compose Another
      </button>
    </div>
  );
}
