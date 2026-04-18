import { getSettings } from "@/lib/settings";
import { getStoredToken } from "./token-store";

function authHeaders(): HeadersInit {
  const t = getStoredToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export interface AnalyticsSummary {
  total_spend: number;
  estimated_revenue: number;
  roi: number;
  total_leads: number;
  total_conversions: number;
  total_impressions: number;
  total_clicks: number;
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
      ...authHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch global analytics");
  }
  return res.json();
}

export type DailyPerformanceRow = {
  day: string;
  platform: string;
  spend: number;
  conversions: number;
};

export type CampaignAnalytics = {
  campaign_id: string;
  campaign_name: string | null;
  total_leads: number;
  total_spend: number;
  competitor_count?: number;
  cost_per_lead: number;
  daily_performance: DailyPerformanceRow[];
};

export async function getCampaignAnalytics(
  id: string,
): Promise<CampaignAnalytics> {
    const settings = getSettings();
    const res = await fetch(`${settings.apiBaseUrl}/analytics/campaign/${id}`, {
      headers: {
        ...authHeaders(),
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
      ...authHeaders(),
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
      ...authHeaders(),
    },
  });
  if (!res.ok) throw new Error("Failed to apply directive");
}

export async function revertOptimizationDirective(id: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/analytics/directives/${id}/revert`, {
    method: "POST",
    headers: {
      ...authHeaders(),
    },
  });
  if (!res.ok) throw new Error("Failed to revert directive");
}

export async function triggerOptimization(campaignId: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/analytics/optimize/${campaignId}`, {
    method: "POST",
    headers: {
      ...authHeaders(),
    },
  });
  if (!res.ok) throw new Error("Failed to trigger optimization");
}

export type UsageMe = {
  period_utc: { start: string; end: string };
  campaigns: { used: number; limit: number | null; remaining: number | null };
  tokens: { used: number; limit: number | null; remaining: number | null };
  estimated_openai_cost_usd: string;
  quota_overrides?: {
    monthly_campaign_quota: number | null;
    monthly_token_quota: number | null;
  };
  note?: string;
};

export async function getUsageMe(): Promise<UsageMe> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/usage/me`, {
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error("Failed to fetch usage");
  return res.json();
}

export type UsageAnalytics = {
  total_tokens: number;
  total_cost_usd: number;
  breakdown: Record<string, { tokens: number; cost: number }>;
};

export async function getUsageAnalytics(): Promise<UsageAnalytics> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/analytics/usage`, {
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error("Failed to fetch usage analytics");
  return res.json();
}

export type AgentsListResponse = {
  agents: string[];
  count: number;
  prompt_bundles?: string[];
};

export async function listAgents(): Promise<AgentsListResponse> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/agents`, {
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error("Failed to load agents");
  return res.json();
}
