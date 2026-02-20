import { Metadata } from "next";
import { DashboardLayout } from "@/components/dashboard/layout";
import { StatusCards } from "@/components/dashboard/status-cards";

export const metadata: Metadata = { title: "Dashboard — Infinity X One" };

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">System Dashboard</h1>
        <StatusCards />
      </div>
    </DashboardLayout>
  );
}
