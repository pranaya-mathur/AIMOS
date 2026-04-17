import { getSettings } from "@/lib/settings";

export interface Message {
  id: string;
  direction: string;
  content: string;
  created_at: string;
}

export interface Lead {
  id: string;
  phone: string;
  full_name: string;
  email: string;
  status: string;
  score: number;
  intent: string;
  created_at: string;
}

export async function getLeads(): Promise<Lead[]> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/leads`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch leads");
  return res.json();
}

export async function getLeadMessages(id: string): Promise<Message[]> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/leads/${id}/messages`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch messages");
  return res.json();
}

export async function updateLeadStatus(id: string, status: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/leads/${id}/status?status=${status}`, {
    method: "PATCH",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to update status");
}

export interface LandingPage {
  id: string;
  slug: string;
  title: string;
  description?: string;
  content_json: any;
  is_published: string;
  views_count: number;
  conversions_count: number;
}

export async function getLandingPages(): Promise<LandingPage[]> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/landing-pages`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch landing pages");
  return res.json();
}

export async function generateLandingPage(): Promise<{ id: string; slug: string }> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/landing-pages/generate`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to generate landing page");
  return res.json();
}

export async function updateLandingPage(id: string, data: Partial<LandingPage>): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/landing-pages/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update landing page");
}

export async function deleteLandingPage(id: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/landing-pages/${id}`, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to delete landing page");
}
