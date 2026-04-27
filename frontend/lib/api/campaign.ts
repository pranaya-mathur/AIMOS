import { apiFetchJson } from "./client";

/** Matches `GET /campaign` row shape from FastAPI. */
export type CampaignSummary = {
  id: string;
  name: string | null;
  status: string;
  created_at: string | null;
};

export type JobStatusResponse = {
  status: string;
  result?: unknown;
};

export type CampaignResponse = {
  id: string;
  name: string | null;
  status: string;
  input: Record<string, unknown>;
  output: unknown;
  celery_task_id: string | null;
  orchestration_metadata?: {
    iterations: number;
    history: string[];
    refinement_context?: string;
  };
};

export async function listCampaigns(
  limit = 20,
): Promise<CampaignSummary[]> {
  const q = new URLSearchParams({ limit: String(limit) });
  return apiFetchJson(`/campaign?${q.toString()}`) as Promise<
    CampaignSummary[]
  >;
}

export async function createCampaign(body: {
  name?: string;
  input: Record<string, unknown>;
  track?: string;
}): Promise<{ task_id: string; campaign_id: string }> {
  return apiFetchJson("/campaign/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function getCampaign(
  campaignId: string,
): Promise<CampaignResponse> {
  return apiFetchJson(`/campaign/${campaignId}`);
}

export async function getJobStatus(taskId: string): Promise<JobStatusResponse> {
  return apiFetchJson(`/job/${taskId}`);
}

export async function patchCampaign(
  campaignId: string,
  body: { status: string },
): Promise<{ id: string; status: string }> {
  return apiFetchJson(`/campaign/${campaignId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function rerunCampaign(
  campaignId: string,
): Promise<{ task_id: string; campaign_id: string }> {
  return apiFetchJson(`/campaign/${campaignId}/rerun`, {
    method: "POST",
  });
}

export const LAST_CAMPAIGN_KEY = "aimos_last_campaign_id";

export function rememberLastCampaignId(id: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LAST_CAMPAIGN_KEY, id);
}

export function readLastCampaignId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(LAST_CAMPAIGN_KEY);
}
