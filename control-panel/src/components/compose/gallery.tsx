"use client";

interface TemplateCard {
  id: string;
  name: string;
  category: string;
  description: string;
  tags: string[];
  color: string;
}

const TEMPLATES: TemplateCard[] = [
  { id: "fastapi", name: "FastAPI", category: "Backend", description: "Production REST API with JWT auth, logging, and health checks", tags: ["Python", "REST", "Auth"], color: "from-green-500 to-emerald-600" },
  { id: "nextjs-pwa", name: "Next.js PWA", category: "Frontend", description: "Full-stack frontend with PWA, Tailwind, React Query", tags: ["TypeScript", "PWA", "React"], color: "from-blue-500 to-indigo-600" },
  { id: "research-agent", name: "Research Agent", category: "AI", description: "Autonomous web research with memory and safety guardrails", tags: ["Python", "AI", "Memory"], color: "from-purple-500 to-violet-600" },
  { id: "orchestrator", name: "Workflow Orchestrator", category: "AI", description: "Multi-step workflow engine with parallel execution and retry", tags: ["Python", "Workflow", "Async"], color: "from-orange-500 to-amber-600" },
  { id: "financial-agent", name: "Financial Analyzer", category: "AI", description: "Market signal aggregation and risk assessment", tags: ["Python", "Finance", "Risk"], color: "from-yellow-500 to-orange-600" },
  { id: "real-estate-agent", name: "Distress Analyzer", category: "AI", description: "Property distress detection with multi-signal scoring", tags: ["Python", "Real Estate", "Scoring"], color: "from-red-500 to-rose-600" },
  { id: "docker-local-mesh", name: "Docker Mesh", category: "Infrastructure", description: "Full local dev mesh with Traefik, Postgres, Redis, Prometheus", tags: ["Docker", "DevOps", "Local"], color: "from-cyan-500 to-teal-600" },
  { id: "tap-enforcement", name: "TAP Governance", category: "Governance", description: "Policy-Authority-Truth enforcement via GitHub Actions", tags: ["CI/CD", "Policy", "Security"], color: "from-gray-500 to-slate-600" },
];

const CATEGORY_COLORS: Record<string, string> = {
  Backend: "bg-green-900/50 text-green-300 border-green-700",
  Frontend: "bg-blue-900/50 text-blue-300 border-blue-700",
  AI: "bg-purple-900/50 text-purple-300 border-purple-700",
  Infrastructure: "bg-cyan-900/50 text-cyan-300 border-cyan-700",
  Governance: "bg-gray-800/50 text-gray-300 border-gray-700",
};

export function TemplateGallery() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-7xl mx-auto">
      {TEMPLATES.map((tpl) => (
        <div key={tpl.id} className="rounded-xl border border-gray-800 bg-gray-900/50 p-5 hover:border-indigo-600 transition-all hover:-translate-y-1 cursor-pointer">
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${tpl.color} mb-3 flex items-center justify-center`}>
            <span className="text-white font-bold text-xs">{tpl.category[0]}</span>
          </div>
          <span className={`text-xs px-2 py-0.5 rounded-full border ${CATEGORY_COLORS[tpl.category] ?? "bg-gray-800 text-gray-300 border-gray-700"}`}>
            {tpl.category}
          </span>
          <h3 className="mt-2 text-white font-semibold">{tpl.name}</h3>
          <p className="mt-1 text-gray-400 text-sm">{tpl.description}</p>
          <div className="mt-3 flex flex-wrap gap-1">
            {tpl.tags.map((tag) => (
              <span key={tag} className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">{tag}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
