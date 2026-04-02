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
  });
}
