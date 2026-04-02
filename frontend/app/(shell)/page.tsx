import Link from "next/link";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { DashboardPipeline } from "@/components/dashboard/DashboardPipeline";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <p className="text-sm text-slate-600">
        <Link href="/campaigns" className="text-violet-600 hover:text-violet-700">
          Campaigns
        </Link>
        <span className="text-gray-600"> · </span>
        <Link href="/analytics" className="text-violet-600 hover:text-violet-700">
          Analytics
        </Link>
        <span className="text-gray-600"> · </span>
        <Link href="/services" className="text-violet-600 hover:text-violet-700">
          Services
        </Link>
        <span className="text-gray-600"> · </span>
        <Link href="/billing" className="text-violet-600 hover:text-violet-700">
          Billing
        </Link>
        <span className="text-gray-600"> · </span>
        <Link href="/launch" className="text-violet-600 hover:text-violet-700">
          Launch
        </Link>
        <span className="text-gray-600"> · </span>
        <Link href="/settings" className="text-violet-600 hover:text-violet-700">
          Settings
        </Link>
        <span className="text-gray-600"> — </span>
        pipeline, metrics, checkout, integrations, profile.
      </p>
      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
          Overview
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard title="Active campaigns" value="—" change="From API list" />
          <MetricCard
            title="Creatives ready"
            value="—"
            change="Use Library →"
            changeTone="neutral"
          />
          <MetricCard
            title="Avg. time to launch"
            value="—"
            change="Per org"
            changeTone="neutral"
          />
          <MetricCard
            title="Spend (MTD)"
            value="—"
            change="Wire analytics"
            changeTone="neutral"
          />
        </div>
      </section>

      <DashboardPipeline />
    </div>
  );
}
