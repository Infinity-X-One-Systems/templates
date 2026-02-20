import { CompositionWizard } from "@/components/compose/wizard";
import { TemplateGallery } from "@/components/compose/gallery";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950 to-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">∞</span>
          </div>
          <span className="text-white font-semibold text-lg">Infinity X One Control Panel</span>
        </div>
        <nav className="hidden md:flex items-center gap-6 text-sm text-gray-400">
          <a href="/compose" className="hover:text-white transition-colors">Compose</a>
          <a href="/gallery" className="hover:text-white transition-colors">Gallery</a>
          <a href="/docs" className="hover:text-white transition-colors">Docs</a>
          <a href="/api/health" className="hover:text-white transition-colors">API</a>
        </nav>
      </header>

      {/* Hero */}
      <section className="px-6 py-16 text-center">
        <h1 className="text-4xl md:text-6xl font-black text-white leading-tight">
          Build Production AI Systems
          <br />
          <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            In Under One Hour
          </span>
        </h1>
        <p className="mt-6 text-xl text-gray-400 max-w-2xl mx-auto">
          Select your frontend, backend, AI agents, and business modules. Get a fully scaffolded, production-ready repository.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/compose"
            className="px-8 py-4 rounded-xl bg-indigo-600 text-white font-bold text-lg hover:bg-indigo-500 transition-colors"
          >
            Start Composing →
          </a>
          <a
            href="/gallery"
            className="px-8 py-4 rounded-xl border border-gray-700 text-gray-300 font-bold text-lg hover:border-indigo-500 transition-colors"
          >
            Browse Templates
          </a>
        </div>
      </section>

      {/* Template Gallery Preview */}
      <section className="px-6 py-12">
        <h2 className="text-2xl font-bold text-white text-center mb-8">Available Templates</h2>
        <TemplateGallery />
      </section>
    </main>
  );
}
