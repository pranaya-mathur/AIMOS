import { apiFetchJson } from "./client";

export type CreativeVariationsResponse = {
  task_ids: string[];
  count: number;
};

export async function queueCreativeVariations(body: {
  brief: string;
  n?: number;
}): Promise<CreativeVariationsResponse> {
  return apiFetchJson("/creatives/variations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brief: body.brief, n: body.n ?? 3 }),
export interface AdCreative {
  id: string;
  campaign_id?: string;
  headline?: string;
  body_copy?: string;
  cta_text?: string;
  media_asset_id?: string;
  status: string;
  is_favorite: string;
  created_at: string;
}

export async function listCreatives(campaignId?: string): Promise<AdCreative[]> {
  const url = campaignId ? `/creatives?campaign_id=${campaignId}` : "/creatives";
  return apiFetchJson(url);
}

export async function updateCreative(id: string, body: Partial<AdCreative>): Promise<void> {
  return apiFetchJson(`/creatives/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function approveCreative(id: string): Promise<void> {
  return apiFetchJson(`/creatives/${id}/approve`, {
    method: "POST"
  });
}
