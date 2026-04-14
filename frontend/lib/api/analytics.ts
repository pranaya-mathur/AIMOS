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
