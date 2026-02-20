import type { Metadata } from "next";
import { CompositionWizard } from "@/components/compose/wizard";

export const metadata: Metadata = {
  title: "Compose System — Infinity X One",
  description: "Build a production AI system from templates in under one hour",
};

export default function ComposePage() {
  return (
    <main className="min-h-screen bg-gray-950 px-6 py-16">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-black text-white text-center mb-2">Compose Your System</h1>
        <p className="text-gray-400 text-center mb-12">Select your components and we'll scaffold a production-ready repository.</p>
        <CompositionWizard />
      </div>
    </main>
  );
}
