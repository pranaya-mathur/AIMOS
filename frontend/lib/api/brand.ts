import { getSettings } from "@/lib/settings";
import { apiFetch } from "./client-base";
import { getStoredToken } from "./token-store";

async function readApiError(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const j = JSON.parse(text) as { detail?: unknown };
    if (j.detail != null) {
      return typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
    }
  } catch {
    /* not JSON */
  }
  return text.slice(0, 200) || res.statusText || String(res.status);
}

export interface BrandData {
  id?: string;
  name: string;
  category?: string;
  description?: string;
  logo_url?: string;
  website_url?: string;
  social_links?: Record<string, string>;
  target_audience?: Record<string, any>;
  product_details?: any[];
  pricing_range?: string;
  business_type?: string;
  industry?: string;
  marketing_goal?: string;
  monthly_budget?: number;
  platform_preference?: string[];
  ai_generated_kit?: Record<string, any>;
  analysis_report?: Record<string, any>;
}

export async function getBrand(): Promise<BrandData> {
  const settings = getSettings();
  const res = await apiFetch(`${settings.apiBaseUrl}/brand`, {
    headers: {
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
  });
  if (!res.ok) {
    if (res.status === 404) return {} as BrandData;
    throw new Error("Failed to fetch brand");
  }
  return res.json();
}

export async function upsertBrand(data: BrandData): Promise<BrandData> {
  const settings = getSettings();
  const res = await apiFetch(`${settings.apiBaseUrl}/brand`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const detail = await readApiError(res);
    throw new Error(`Could not save brand (${res.status}): ${detail}`);
  }
  return res.json();
}

export async function completeOnboarding(): Promise<void> {
  const settings = getSettings();
  const res = await apiFetch(`${settings.apiBaseUrl}/onboarding/complete`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
  });
  if (!res.ok) {
    const detail = await readApiError(res);
    throw new Error(`Could not complete onboarding (${res.status}): ${detail}`);
  }
}

export async function getOnboardingStatus(): Promise<{ is_onboarded: boolean }> {
  const settings = getSettings();
  const res = await apiFetch(`${settings.apiBaseUrl}/onboarding/status`, {
    headers: {
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
  });
  if (!res.ok) {
    return { is_onboarded: true }; // Default to true on error to avoid loops
  }
  return res.json();
}


export async function generateBrandKit(): Promise<{ strategy: any; brand_kit: any }> {
  const settings = getSettings();
  const res = await apiFetch(`${settings.apiBaseUrl}/brand/generate-kit`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to generate brand kit");
  }
  return res.json();
}


export async function generateLogo(): Promise<{ logo_url: string }> {
  const settings = getSettings();
  const res = await apiFetch(`${settings.apiBaseUrl}/brand/logo`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${getStoredToken() ?? ""}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to generate logo");
  }
  return res.json();
}
