import { apiFetchJson } from "./client";

export type GlobalAnalytics = {
  summary: {
    total_spend: number;
    total_impressions: number;
    total_clicks: number;
    total_conversions: number;
    ctr: number;
    cvr: number;
  };
  campaign_count: number;
};

export type UsageAnalytics = {
  total_tokens: number;
  total_cost_usd: number;
  breakdown: Record<string, { tokens: number; cost: number }>;
};

export type UsageMe = {
  period_utc: { start: string; end: string };
  campaigns: {
    used: number;
    limit: number | null;
    remaining: number | null;
  };
  tokens: {
    used: number;
    limit: number | null;
    remaining: number | null;
  };
  estimated_openai_cost_usd: string;
  quota_overrides?: Record<string, unknown>;
  note?: string;
};

export async function getGlobalAnalytics(): Promise<GlobalAnalytics> {
  return apiFetchJson("/analytics/global");
}

export async function getUsageAnalytics(): Promise<UsageAnalytics> {
  return apiFetchJson("/analytics/usage");
}

export async function getUsageMe(): Promise<UsageMe> {
  return apiFetchJson("/usage/me");
}

export type AgentsListResponse = {
  agents: string[];
  count: number;
  prompt_bundles: string[];
};

export async function listAgents(): Promise<AgentsListResponse> {
  return apiFetchJson("/agents");
}

export type CampaignAnalytics = {
  campaign_id: string;
  campaign_name: string | null;
  total_leads: number;
  total_spend: number;
  cost_per_lead: number;
  daily_performance: Array<{
    day: string;
    platform: string;
    spend: number;
    conversions: number;
  }>;
};

export async function getCampaignAnalytics(
  campaignId: string,
): Promise<CampaignAnalytics> {
  return apiFetchJson(`/analytics/campaign/${campaignId}`);
}
