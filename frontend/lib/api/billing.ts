import { apiFetchJson } from "./client";

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
