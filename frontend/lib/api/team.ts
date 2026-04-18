import { getSettings } from "@/lib/settings";
import { getStoredToken } from "./token-store";

export interface TeamMember {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  created_at: string;
}

export interface TeamInvite {
  id: string;
  email: string;
  role: string;
  expires_at: string;
}

export interface TeamListing {
  members: TeamMember[];
  pending_invites: TeamInvite[];
}

export async function getTeam(): Promise<TeamListing> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/team/members`, {
    headers: {
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch team members");
  return res.json();
}

export async function inviteMember(email: string, role: string = "agency_client"): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/team/invite`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
    body: JSON.stringify({ email, role }),
  });
  if (!res.ok) {
     const err = await res.json();
     throw new Error(err.detail || "Failed to invite member");
  }
}

export async function removeMember(userId: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/team/members/${userId}`, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
  });
  if (!res.ok) throw new Error("Failed to remove member");
}
