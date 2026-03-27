# Bubble workflow templates (step-by-step)

Replicate these in **Bubble** using **Plugins → API Connector** and **Workflows**. Names are suggestions; map them to your app’s pages.

---

## Template A — Login and store JWT

**Goal:** User signs in; store token for later API calls.

1. **Button “Log in”** → workflow:
   - **API Connector:** `POST /auth/login`  
     Body (JSON): `{ "email": input_email's value, "password": input_password's value }`
   - **Action:** Set state `jwt` = `result's access_token` (or save to Current User if you mirror identity in Bubble only as a cache).

2. **API Connector shared headers** (for all authenticated calls):

   - Header: `Authorization`  
   - Value: `Bearer ` **append** `jwt` (use “Append” in Bubble dynamic expression).

**Screenshot hint:** In API Connector, open your API → Shared headers → add `Authorization` with dynamic value built from `Bearer ` + your state variable.

---

## Template B — Create campaign (starts 12-agent pipeline)

**Goal:** Send brief → receive `campaign_id` and `task_id` → poll job.

1. **Button “Generate campaign”** →  
   - `POST /campaign/create`  
   - Headers: shared `Authorization`.  
   - Body: `{ "name": "My campaign", "input": { "goal": "...", "audience": "..." } }`

2. Store `campaign_id` and `task_id` from the response in custom states.

3. **Recurring event or “Check status” button** →  
   - `GET /job/{task_id}` (use dynamic segment bound to stored `task_id`).  
   - Stop when `status` is `SUCCESS` (or show error if `FAILURE`).

4. **When job succeeds** →  
   - `GET /campaign/{campaign_id}` to load `output` / `status` for UI.

---

## Template C — Health check (admin / diagnostics)

1. **Page load** or **admin button** → `GET /health/ready`.  
2. Display `status` or show alert if request fails (API down / DB issue).

---

## Template D — Stripe checkout

**Goal:** Paid campaign flow.

1. **Button “Pay”** → `POST /billing/checkout/session` with `campaign_id`, `success_url`, `cancel_url` (Bubble page URLs with query params if needed).

2. **Open external website** to `url` from the response (Stripe Checkout).

3. On return URL page, optionally `GET /campaign/{id}` to confirm `status` after webhook marks `paid` (may take a few seconds).

---

## Notes

- Use **HTTPS** for production API base URLs.
- **Preview vs Live** Bubble apps may use different origins — add **both** to `CORS_ORIGINS` if you test both.
- Long-running jobs: prefer **polling** `GET /job/{task_id}` every few seconds instead of blocking the workflow.
