"""Grouped tags for OpenAPI (Bubble API Connector + API documentation)."""

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Liveness/readiness for load balancers and uptime checks.",
    },
    {
        "name": "auth",
        "description": "JWT registration and login. Send `Authorization: Bearer <token>` on protected routes.",
    },
    {
        "name": "billing",
        "description": "Stripe Checkout session creation and webhooks. Point Stripe webhook to `POST /billing/stripe/webhook`.",
    },
    {
        "name": "campaign",
        "description": "Campaign CRUD and AI pipeline runs (12 BRD modules).",
    },
    {
        "name": "job",
        "description": "Celery async job status by `task_id`.",
    },
    {
        "name": "agents",
        "description": "Run a single BRD agent by graph name (e.g. `business_analyzer`).",
    },
    {
        "name": "media",
        "description": "AdCreative / Pictory / ElevenLabs async jobs and signed webhooks.",
    },
    {
        "name": "launch",
        "description": "Meta Marketing API, WhatsApp Cloud API, Google Ads placeholder; GET /launch/status for env flags.",
    },
    {
        "name": "creatives",
        "description": "Parallel OpenAI creative variations via Celery (`POST /creatives/variations`).",
    },
    {
        "name": "usage",
        "description": "Per-user monthly quotas and OpenAI token / cost estimates (UTC month).",
    },
]
