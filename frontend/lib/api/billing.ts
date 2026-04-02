import { apiFetchJson } from "./client";

// ── One-time checkout (existing) ──

export type CheckoutSessionResponse = {
  checkout_session_id: string;
  url: string;
  campaign_id: string;
};

export async function createCheckoutSession(body: {
  campaign_id: string;
  success_url: string;
  cancel_url: string;
  price_id?: string | null;
}): Promise<CheckoutSessionResponse> {
  return apiFetchJson("/billing/checkout/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      campaign_id: body.campaign_id,
      success_url: body.success_url,
      cancel_url: body.cancel_url,
      price_id: body.price_id || undefined,
    }),
  });
}

// ── Recurring subscription ──

export type SubscribeResponse = {
  checkout_session_id: string;
  url: string;
};

export async function createSubscription(body: {
  price_id: string;
  success_url: string;
  cancel_url: string;
}): Promise<SubscribeResponse> {
  return apiFetchJson("/billing/subscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export type SubscriptionInfo = {
  tier: string;
  status: string;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  quotas: {
    monthly_campaigns: number | "unlimited";
    monthly_tokens: number | "unlimited";
  };
  available_tiers: Record<
    string,
    { campaigns: number | "unlimited"; tokens: number | "unlimited" }
  >;
};

export async function getSubscription(): Promise<SubscriptionInfo> {
  return apiFetchJson("/billing/subscription");
}

export type PortalResponse = {
  url: string;
};

export async function createPortalSession(
  return_url: string,
): Promise<PortalResponse> {
  return apiFetchJson("/billing/portal", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ return_url }),
  });
}
