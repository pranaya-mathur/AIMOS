import { getSettings } from "@/lib/settings";

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
}

export async function getBrand(): Promise<BrandData> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/brand`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
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
  const res = await fetch(`${settings.apiBaseUrl}/brand`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error("Failed to save brand");
  }
  return res.json();
}

export async function completeOnboarding(): Promise<void> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/onboarding/complete`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to complete onboarding");
  }
}

export async function getOnboardingStatus(): Promise<{ is_onboarded: boolean }> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/onboarding/status`, {
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) {
    return { is_onboarded: true }; // Default to true on error to avoid loops
  }
  return res.json();
}


export async function generateBrandKit(): Promise<{ strategy: any; brand_kit: any }> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/brand/generate-kit`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to generate brand kit");
  }
  return res.json();
}


export async function generateLogo(): Promise<{ logo_url: string }> {
  const settings = getSettings();
  const res = await fetch(`${settings.apiBaseUrl}/brand/logo`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
  });
  if (!res.ok) {
    throw new Error("Failed to generate logo");
  }
  return res.json();
}
