import { getApiBaseUrl } from "./api/client-base";

/** Product modules mapped to app routes and API surface (Bubble-style hub). */
export const SERVICE_MODULES: {
  id: string;
  title: string;
  description: string;
  href: string;
  methods: string[];
}[] = [
  {
    id: "pipeline",
    title: "14-agent pipeline",
    description:
      "Spy → analyzer → brand → content → benchmarker → campaign → social → leads → sales → engagement → performance → growth → dashboard → wisdom.",
    href: "/campaigns",
    methods: ["POST /campaign/create", "POST /campaign/{id}/rerun", "GET /job/{task_id}"],
  },
  {
    id: "creatives",
    title: "Creative variations",
    description: "Parallel OpenAI copy variants via Celery.",
    href: "/library",
    methods: ["POST /creatives/variations"],
  },
  {
    id: "launch",
    title: "Launch & ads",
    description: "Meta, Google Ads, X — triggers from backend integrations.",
    href: "/launch",
    methods: ["POST /launch/* (see OpenAPI)"],
  },
  {
    id: "media",
    title: "Media providers",
    description: "AdCreative, Pictory, ElevenLabs-style hooks + webhooks.",
    href: "/media-studio",
    methods: ["POST /media/*"],
  },
  {
    id: "billing",
    title: "Billing & checkout",
    description: "Stripe Checkout session; webhook marks campaign paid.",
    href: "/billing",
    methods: ["POST /billing/checkout/session"],
  },
  {
    id: "webhooks",
    title: "Webhooks",
    description: "Inbound provider callbacks (Stripe, media, WhatsApp).",
    href: "/services",
    methods: ["POST /webhooks/*"],
  },
];

export function swaggerUrl(): string {
  return `${getApiBaseUrl()}/docs`;
}

export function openapiUrl(): string {
  return `${getApiBaseUrl()}/openapi.json`;
}
