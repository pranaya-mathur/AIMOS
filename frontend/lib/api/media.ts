import { getSettings } from "@/lib/settings";

export interface MediaAsset {
  id: string;
  provider: string;
  asset_type: string;
  url: string;
  created_at: string;
}

export async function getMediaAssets(): Promise<MediaAsset[]> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/media/assets`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to fetch media assets");
  }
  return res.json();
}

export async function deleteMediaAsset(id: string): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/media/assets/${id}`, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to delete media asset");
  }
}
