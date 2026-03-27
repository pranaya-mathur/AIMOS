# End-to-end campaign test

Validates the full path: **login → `POST /campaign/create` → Celery `run_campaign` → 12-agent LangGraph pipeline → `agent_outputs` + campaign `completed`.**

## Prerequisites

- Docker Compose running: **api**, **worker**, **redis**, **db** (e.g. `./setup.sh` or `docker compose up -d --build`).
- Valid **`OPENAI_API_KEY`** in `.env`; after changing it: `docker compose restart api worker`.
- Dev user seeded: `docker compose exec api python /app/scripts/db_init.py` (creates **`aimos-dev@example.com`** / **`devpass123`**).

## Run

From the repository root (with **httpx** installed — use `pip install -r backend/requirements.txt` in a venv, or run against a host that has it):

```bash
python3 scripts/test_full_campaign.py
```

Optional:

```bash
make e2e
```

Override base URL:

```bash
export AIMOS_API_BASE=http://127.0.0.1:8000
python3 scripts/test_full_campaign.py
```

## Expected successful output

When everything is wired correctly, you should see log lines similar to:

```text
INFO: logged in as aimos-dev@example.com
Campaign <uuid> task_id=<celery-uuid> — polling job…
OK — pipeline returned all 12 agent_outputs keys.
OK — campaign row status=completed
E2E campaign pipeline: PASSED
```

Meaning:

| Line | Meaning |
|------|--------|
| `logged in as aimos-dev@example.com` | JWT obtained via `POST /auth/login` (or set `AIMOS_E2E_TOKEN` / `AUTH_DISABLED=1`). |
| `Campaign … task_id=…` | Campaign row created and Celery task id returned. |
| `all 12 agent_outputs keys` | Final graph state includes outputs for all BRD agent ids (`business_analyzer` … `business_dashboard`). |
| `status=completed` | Campaign row updated after the task finishes. |
| `PASSED` | Script exits with code **0**. |

## Failure modes

- **`Connection refused`** — API not listening on port 8000; start Compose first.
- **`401`** — Auth required; run **`db_init`**, or set **`AUTH_DISABLED=1`** for local-only.
- **`agent_outputs missing …`** — Pipeline or prompts out of sync; see **`scripts/test_full_campaign.py`** and **`prompts/agents/*/config.json`** (`agent_name` must match graph node ids).

## CI / automation

Exit code **0** = success; non-zero = failure. Suitable for CI once the stack is reachable from the runner (or use a staging URL via `AIMOS_API_BASE`).
