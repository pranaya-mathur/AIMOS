# Bubble.io integration kit

Use this when wiring **Bubble** (UI + workflows) to the AIMOS API.

## 1. OpenAPI spec

- **Live import:** In API Connector, import from `https://<your-api-host>/openapi.json`.
- **Offline snapshot:** With the API running locally or in staging, run from the repo root:

  ```bash
  make openapi
  # or: python3 scripts/export_openapi.py http://localhost:8000 docs/bubble/openapi-snapshot.json
  ```

  Paste or upload `docs/bubble/openapi-snapshot.json` into Bubble if you cannot use a public URL.

## 2. Environment on the AIMOS side

In `.env` (or AWS Secrets Manager in production):

| Variable | Purpose |
|----------|---------|
| `CORS_ORIGINS` | Your Bubble app origin, e.g. `https://yourapp.bubbleapps.io` |
| `PUBLIC_API_BASE_URL` | Same public API base you put in Bubble (OpenAPI `servers` entry) |

## 3. Auth

1. **Register / login** — `POST /auth/register` or `POST /auth/login`.
2. Store `access_token` in a Bubble custom state or secure field.
3. API Connector **shared header:** `Authorization` = `Bearer <access_token>`.

For automated tests, seed user `dev@aimos.local` is created by `./setup.sh` + `db_init` (password in `scripts/db_init.py`).

## 4. Workflow templates (conceptual)

Step-by-step flows are in **[WORKFLOWS.md](WORKFLOWS.md)**. Bubble does not export portable workflow JSON here; replicate the steps in the Bubble editor (API Connector calls + workflows).

## 5. Stripe

- `POST /billing/checkout/session` returns `url` — open in **“Open external website”** or redirect.
- Webhook is **server-to-server** (`POST /billing/stripe/webhook` on AIMOS), not to Bubble.

## 6. Troubleshooting

| Symptom | Check |
|---------|--------|
| CORS error in browser | `CORS_ORIGINS` includes exact Bubble origin (scheme + host, no trailing slash). |
| 401 on API | Token expired or missing `Authorization: Bearer …`. |
| OpenAPI import fails | Use `/openapi.json` over HTTPS; or import saved `openapi-snapshot.json`. |
