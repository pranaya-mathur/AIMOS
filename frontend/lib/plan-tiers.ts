/**
 * Subscription tier definitions for AIMOS.
 * Mirrors backend `TIER_QUOTA_MAP` in core/config.py.
 *
 * Price IDs are read from env (STRIPE_PRICE_*) on the backend;
 * the frontend just references them by slug + displays the metadata.
 */

export type PlanTier = {
  slug: string;
  name: string;
  price: string;
  priceValue: number;        // Monthly USD (0 = custom / contact)
  tagline: string;
  priceIdEnvVar: string;     // Backend env var holding the Stripe Price ID
  campaigns: string;
  tokens: string;
  features: string[];
  popular?: boolean;
  cta: string;
  gradient: string;          // CSS gradient for the card accent
};

export const PLAN_TIERS: PlanTier[] = [
  {
    slug: "professional",
    name: "Professional",
    price: "$499",
    priceValue: 499,
    tagline: "Everything you need to launch and scale AI-powered campaigns.",
    priceIdEnvVar: "STRIPE_PRICE_PROFESSIONAL",
    campaigns: "50 / month",
    tokens: "5,000,000 / month",
    features: [
      "50 AI campaigns / month",
      "5M OpenAI tokens / month",
      "14-agent pipeline (all agents)",
      "Multi-platform launch (Meta, Google, X)",
      "WhatsApp lead capture",
      "Email & priority support",
    ],
    cta: "Start Professional",
    gradient: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
  },
  {
    slug: "growth",
    name: "Growth",
    price: "$999",
    priceValue: 999,
    tagline: "Agency-grade power with higher limits and advanced analytics.",
    priceIdEnvVar: "STRIPE_PRICE_GROWTH",
    campaigns: "200 / month",
    tokens: "25,000,000 / month",
    popular: true,
    features: [
      "200 AI campaigns / month",
      "25M OpenAI tokens / month",
      "Everything in Professional",
      "Advanced analytics dashboard",
      "Multi-org / team management",
      "Real-time optimization engine",
      "Dedicated Slack channel",
    ],
    cta: "Start Growth",
    gradient: "linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)",
  },
  {
    slug: "enterprise",
    name: "Enterprise",
    price: "Custom",
    priceValue: 0,
    tagline: "Unlimited scale, white-glove onboarding, and custom integrations.",
    priceIdEnvVar: "STRIPE_PRICE_ENTERPRISE",
    campaigns: "Unlimited",
    tokens: "Unlimited",
    features: [
      "Unlimited campaigns & tokens",
      "Everything in Growth",
      "Custom agent workflows",
      "SSO / SAML integration",
      "Dedicated success manager",
      "SLA & uptime guarantee",
      "On-premise deployment option",
    ],
    cta: "Contact Sales",
    gradient: "linear-gradient(135deg, #d946ef 0%, #f43f5e 100%)",
  },
];
