import { getSettings } from "@/lib/settings";

export interface WhitelabelConfig {
  logo_url?: string;
  primary_color?: string;
  site_name?: string;
}

export async function getOrgConfig(): Promise<WhitelabelConfig> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/org/config`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch org config");
  return res.json();
}

export async function updateOrgConfig(config: WhitelabelConfig): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/org/config`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify(config),
  });
  if (!res.ok) throw new Error("Failed to update org config");
}
