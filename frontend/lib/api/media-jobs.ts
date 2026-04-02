import { apiFetchJson } from "./client";

export type MediaEnqueueResponse = {
  task_id: string;
  provider: string;
  request_id: string;
};

export async function enqueueAdcreative(
  input: Record<string, unknown>,
): Promise<MediaEnqueueResponse> {
  return apiFetchJson("/media/adcreative/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input }),
  });
}

export async function enqueuePictory(
  input: Record<string, unknown>,
): Promise<MediaEnqueueResponse> {
  return apiFetchJson("/media/pictory/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input }),
  });
}

export async function enqueueElevenlabs(
  input: Record<string, unknown>,
): Promise<MediaEnqueueResponse> {
  return apiFetchJson("/media/elevenlabs/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input }),
  });
}
