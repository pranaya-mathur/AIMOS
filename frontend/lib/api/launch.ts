import { apiFetchJson } from "./client";

export type LaunchStatus = Record<string, boolean | string | number | unknown>;

export async function getLaunchStatus(): Promise<LaunchStatus> {
  return apiFetchJson("/launch/status");
}

export async function launchMeta(body: {
  name: string;
  objective?: string;
  async_job?: boolean;
}): Promise<{ task_id?: string; mode: string; result?: unknown }> {
  return apiFetchJson("/launch/meta", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: body.name,
      objective: body.objective ?? "OUTCOME_AWARENESS",
      async_job: body.async_job ?? true,
    }),
  });
}

export async function launchWhatsApp(body: {
  to_e164: string;
  body: string;
  async_job?: boolean;
}): Promise<{ task_id?: string; mode: string; result?: unknown }> {
  return apiFetchJson("/launch/whatsapp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ async_job: true, ...body }),
  });
}

export async function launchGoogle(body: {
  campaign_name: string;
  customer_id?: string | null;
  async_job?: boolean;
}): Promise<{ task_id?: string; mode: string; result?: unknown }> {
  return apiFetchJson("/launch/google", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ async_job: true, ...body }),
  });
}

export async function launchSocial(body: {
  text: string;
  async_job?: boolean;
}): Promise<{ task_id?: string; mode: string; result?: unknown }> {
  return apiFetchJson("/launch/social", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ async_job: true, ...body }),
  });
}

export async function launchEmail(body: {
  to_email: string;
  subject: string;
  body: string;
  async_job?: boolean;
}): Promise<{ task_id?: string; mode: string; result?: unknown }> {
  return apiFetchJson("/launch/email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ async_job: true, ...body }),
  });
}

export async function launchSms(body: {
  to_phone: string;
  body: string;
  async_job?: boolean;
}): Promise<{ task_id?: string; mode: string; result?: unknown }> {
  return apiFetchJson("/launch/sms", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ async_job: true, ...body }),
  });
}
