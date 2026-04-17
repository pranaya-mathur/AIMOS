import { getSettings } from "@/lib/settings";

export interface AnalyticsSummary {
  total_spend: number;
  estimated_revenue: number;
  roi: number;
  total_leads: number;
  total_conversions: number;
  ctr: number;
  cvr: number;
  cpl: number;
}

export interface GlobalAnalytics {
  summary: AnalyticsSummary;
  campaign_count: number;
}

export async function getGlobalAnalytics(): Promise<GlobalAnalytics> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/analytics/global`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch global analytics");
  }
  return res.json();
}

export async function getCampaignAnalytics(id: string): Promise<any> {
    const settings = getSettings();
    const res = await fetch(`${settings.apiBaseUrl}/analytics/campaign/${id}`, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`,
      },
    });
    if (!res.ok) {
      throw new Error("Failed to fetch campaign analytics");
    }
    return res.json();
}

export interface OptimizationDirective {
  id: string;
  campaign_id: string;
  directive_type: string;
  description: string;
  status: string;
  created_at: string;
  // Hardened 2.0
  execution_mode: "manual" | "autopilot";
  risk_score: number;
  confidence: number;
}

export async function getOptimizationDirectives(campaignId?: string): Promise<OptimizationDirective[]> {
  const settings = getSettings();
  const url = campaignId 
    ? `${settings.apiBaseUrl}/analytics/directives?campaign_id=${campaignId}`
    : `${settings.apiBaseUrl}/analytics/directives`;
    
  const res = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch directives");
  return res.json();
}

export async function applyOptimizationDirective(id: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/analytics/directives/${id}/apply`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to apply directive");
}

export async function revertOptimizationDirective(id: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/analytics/directives/${id}/revert`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to revert directive");
}

export async function triggerOptimization(campaignId: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/analytics/optimize/${campaignId}`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to trigger optimization");
}
