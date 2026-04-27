# End-to-end campaign test

Validates the full path: **login → `POST /campaign/create` → Celery `run_campaign` → 14-agent LangGraph pipeline → `agent_outputs` + campaign `completed`.**

## Prerequisites

- Docker Compose running: **api**, **worker**, **redis**, **db** (e.g. `./setup.sh` or `docker compose up -d --build`).
- Valid **`OPENAI_API_KEY`** in `.env`; after changing it: `docker compose restart api worker`.
- Dev user seeded: `docker compose exec api python /app/scripts/db_init.py`.

## Run

From the repository root:

```bash
python3 scripts/test_full_campaign.py
```

## Expected successful output

When everything is wired correctly, you should see log lines similar to:

```text
INFO: logged in as aimos-dev@example.com
Campaign <uuid> task_id=<celery-uuid> — polling job…
OK — pipeline returned all 14 agent_outputs keys.
OK — campaign row status=completed
E2E campaign pipeline: PASSED
```

Meaning:

| Line | Meaning |
|------|--------|
| `logged in as aimos-dev@example.com` | JWT obtained via `POST /auth/login`. |
| `Campaign … task_id=…` | Campaign row created and Celery task id returned. |
| `all 14 agent_outputs keys` | Final graph state includes outputs for all 14 agent ids (competitive_spy … wisdom_extractor). |
| `status=completed` | Campaign row updated after the task finishes. |
| `PASSED` | Script exits with code **0**. |
