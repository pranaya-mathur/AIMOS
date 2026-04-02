/**
 * Mirrors backend `Settings.get_quotas_for_price` (substring match on Stripe Price ID).
 * Create Prices in Stripe Dashboard whose IDs contain these keywords, or set
 * STRIPE_DEFAULT_PRICE_ID in `.env`.
 */
export type PlanTier = {
  slug: string;
  name: string;
  tagline: string;
  priceIdHint: string;
  campaigns: string;
  tokens: string;
};

export const PLAN_TIERS: PlanTier[] = [
  {
    slug: "starter",
    name: "Starter",
    tagline: "Try the full pipeline on a small scale.",
    priceIdHint: 'Stripe Price ID should contain "starter" (e.g. price_abc_starter_xyz)',
    campaigns: "5 / month",
    tokens: "500,000 / month",
  },
  {
    slug: "pro",
    name: "Pro",
    tagline: "Agency workloads with higher caps.",
    priceIdHint: 'Price ID should contain "pro"',
    campaigns: "100 / month",
    tokens: "10,000,000 / month",
  },
  {
    slug: "enterprise",
    name: "Enterprise",
    tagline: "Unlimited campaigns & tokens (per backend mapping).",
    priceIdHint: 'Price ID should contain "enterprise"',
    campaigns: "Unlimited",
    tokens: "Unlimited",
  },
];
