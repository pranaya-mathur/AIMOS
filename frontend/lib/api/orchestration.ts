import { getSettings } from "@/lib/settings";

export async function resumeCampaign(campaignId: string, feedback: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/orchestration/${campaignId}/resume`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify({ feedback }),
  });
  if (!res.ok) {
     const err = await res.json();
     throw new Error(err.detail || "Failed to resume campaign");
  }
}
