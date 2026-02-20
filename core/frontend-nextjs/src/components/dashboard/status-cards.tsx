"use client";
import { useQuery } from "@tanstack/react-query";

interface SystemStatus {
  status: string;
  service: string;
  version: string;
  env: string;
}

async function fetchHealth(): Promise<SystemStatus> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${base}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export function StatusCards() {
  const { data, isLoading, isError } = useQuery({ queryKey: ["health"], queryFn: fetchHealth });

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <StatusCard
        title="API Status"
        value={isLoading ? "Loading..." : isError ? "Error" : data?.status ?? "Unknown"}
        color={isError ? "red" : "green"}
      />
      <StatusCard title="Environment" value={data?.env ?? "—"} color="blue" />
      <StatusCard title="Version" value={data?.version ?? "—"} color="purple" />
    </div>
  );
}

function StatusCard({ title, value, color }: { title: string; value: string; color: string }) {
  const colorMap: Record<string, string> = {
    green: "bg-green-50 border-green-200 text-green-700",
    red: "bg-red-50 border-red-200 text-red-700",
    blue: "bg-blue-50 border-blue-200 text-blue-700",
    purple: "bg-purple-50 border-purple-200 text-purple-700",
  };
  return (
    <div className={`rounded-lg border p-4 ${colorMap[color] ?? colorMap.blue}`}>
      <p className="text-xs font-medium uppercase tracking-wide opacity-70">{title}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  );
}
