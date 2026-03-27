#!/usr/bin/env python3
"""
End-to-end: create campaign → wait for Celery job → verify 12-agent pipeline output.

Requires API + worker + Redis + DB (e.g. docker compose up).

Usage:
  export AIMOS_API_BASE=http://localhost:8000
  export AIMOS_E2E_TOKEN=...   # optional Bearer; else uses AUTH_DISABLED or login
  python3 scripts/test_full_campaign.py

With JWT (default dev user from db_init):
  python3 scripts/test_full_campaign.py --email aimos-dev@example.com --password devpass123

Expected success output is documented in: docs/E2E_TESTING.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

import httpx

AGENT_KEYS = (
    "business_analyzer",
    "brand_builder",
    "content_studio",
    "campaign_builder",
    "social_media_manager",
    "lead_capture",
    "sales_agent",
    "customer_engagement",
    "analytics_engine",
    "optimization_engine",
    "growth_planner",
    "business_dashboard",
)

_ALLOWED = frozenset(AGENT_KEYS)


def _coerce_task_result(raw: Any) -> Optional[dict]:
    """Celery / JSON may return dict, or a JSON string; normalize to dict."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _extract_agent_outputs(state: dict) -> Dict[str, Any]:
    """Graph state uses agent_outputs: dict[str, Any]."""
    raw = state.get("agent_outputs")
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _normalize_agent_output_keys(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map legacy keys like business_analyzer_agent -> business_analyzer.
    Do NOT strip the suffix from canonical ids like sales_agent (that would wrongly become sales).
    """
    out: Dict[str, Any] = {}
    for key, val in raw.items():
        if key in _ALLOWED:
            canon = key
        elif key.endswith("_agent"):
            candidate = key[:-6]
            canon = candidate if candidate in _ALLOWED else key
        else:
            canon = key
        out[canon] = val
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.environ.get("AIMOS_API_BASE", "http://127.0.0.1:8000"))
    ap.add_argument("--email", default=os.environ.get("AIMOS_E2E_EMAIL"))
    ap.add_argument("--password", default=os.environ.get("AIMOS_E2E_PASSWORD"))
    ap.add_argument("--timeout", type=int, default=600, help="Max seconds to wait for job")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    headers: dict[str, str] = {}

    with httpx.Client(timeout=60.0) as client:
        try:
            r = client.get(f"{base}/health/ready")
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            print(
                f"ERROR: cannot reach API at {base} ({exc}).\n"
                "Start the stack first, e.g.:\n"
                "  docker compose up -d --build\n"
                "  ./setup.sh\n"
                "Then wait until: curl -s http://127.0.0.1:8000/health/ready",
                file=sys.stderr,
            )
            return 1
        if r.status_code != 200:
            print(f"ERROR: /health/ready -> {r.status_code} {r.text}", file=sys.stderr)
            return 1

        token = os.environ.get("AIMOS_E2E_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            email = args.email or "aimos-dev@example.com"
            password = args.password or "devpass123"
            lr = client.post(
                f"{base}/auth/login",
                json={"email": email, "password": password},
            )
            if lr.status_code == 200:
                token = lr.json().get("access_token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    print(f"INFO: logged in as {email}")
            else:
                print(
                    "INFO: login failed — assuming AUTH_DISABLED=1 for /campaign "
                    f"({lr.status_code}). Run: docker compose exec api python /app/scripts/db_init.py (creates aimos-dev@example.com).",
                )

        brief = {
            "product": "E2E test product",
            "audience": "Small business owners",
            "goal": "Validate 12-agent pipeline",
        }
        cr = client.post(
            f"{base}/campaign/create",
            json={"name": "E2E full campaign", "input": brief},
            headers=headers,
        )
        if cr.status_code not in (200, 201):
            print(f"ERROR: campaign/create -> {cr.status_code} {cr.text}", file=sys.stderr)
            return 1

        body = cr.json()
        task_id = body.get("task_id")
        campaign_id = body.get("campaign_id")
        if not task_id:
            print(f"ERROR: no task_id in response: {body}", file=sys.stderr)
            return 1

        print(f"Campaign {campaign_id} task_id={task_id} — polling job…")

        deadline = time.time() + args.timeout
        result = None
        while time.time() < deadline:
            jr = client.get(f"{base}/job/{task_id}")
            if jr.status_code != 200:
                print(f"WARN: job status {jr.status_code}", file=sys.stderr)
                time.sleep(2)
                continue
            st = jr.json()
            status = st.get("status")
            if status == "SUCCESS":
                result = st.get("result")
                break
            if status == "FAILURE":
                print(f"ERROR: task failed: {st.get('result')}", file=sys.stderr)
                return 1
            time.sleep(3)

        if result is None:
            print("ERROR: timeout waiting for job SUCCESS", file=sys.stderr)
            return 1

        state = _coerce_task_result(result)
        if state is None:
            print(
                f"ERROR: task result is not a dict (got {type(result).__name__}). "
                f"First 500 chars: {str(result)[:500]!r}",
                file=sys.stderr,
            )
            return 1

        outputs = _normalize_agent_output_keys(_extract_agent_outputs(state))
        missing = [k for k in AGENT_KEYS if k not in outputs]

        if missing:
            print(
                f"ERROR: agent_outputs missing {len(missing)} keys: {missing}\n"
                f"  agent_outputs type={type(state.get('agent_outputs')).__name__} "
                f"keys_sample={list(outputs.keys())[:20]}",
                file=sys.stderr,
            )
            return 1

        print(f"OK — pipeline returned all {len(AGENT_KEYS)} agent_outputs keys.")

        gr = client.get(f"{base}/campaign/{campaign_id}", headers=headers)
        if gr.status_code == 200 and gr.json().get("status") == "completed":
            print("OK — campaign row status=completed")
        else:
            print(f"WARN: campaign GET -> {gr.status_code} {gr.text}")

    print("E2E campaign pipeline: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
