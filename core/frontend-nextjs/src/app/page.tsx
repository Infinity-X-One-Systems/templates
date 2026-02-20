import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">
          Infinity X One
        </h1>
        <p className="mt-4 text-xl text-gray-600 dark:text-gray-300">
          Production-grade AI Command Center
        </p>
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/dashboard"
            className="px-6 py-3 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors"
          >
            Open Dashboard
          </Link>
          <Link
            href="/docs"
            className="px-6 py-3 rounded-lg border border-indigo-600 text-indigo-600 font-semibold hover:bg-indigo-50 transition-colors"
          >
            Documentation
          </Link>
        </div>
      </div>
    </main>
  );
}
