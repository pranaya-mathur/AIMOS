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
