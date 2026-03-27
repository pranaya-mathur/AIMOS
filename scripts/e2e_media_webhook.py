#!/usr/bin/env python3
"""
End-to-end: POST /media/{provider}/create → signed webhook → poll GET /job/{task_id}.

For local runs without real provider keys, set MOCK_MEDIA_PROVIDER=1 on api + worker
(see README). With real keys, omit mock and use provider APIs as normal.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from webhook_common import post_signed_webhook

CREATE_PATH = {
    "adcreative": "/media/adcreative/create",
    "pictory": "/media/pictory/create",
    "elevenlabs": "/media/elevenlabs/create",
}

SUCCESS_STATES = {"SUCCESS"}


def http_json(method: str, url: str, body: dict | None = None, timeout: float = 60.0) -> tuple[int, dict]:
    data = None
    headers = {"accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["content-type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            parsed = {"detail": raw}
        return exc.code, parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="E2E: create media job, webhook, verify Celery result.")
    parser.add_argument("--provider", choices=["adcreative", "pictory", "elevenlabs"], required=True)
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--webhook-secret", required=True, help="Same as ADCREATIVE_WEBHOOK_SECRET / etc.")
    parser.add_argument(
        "--input",
        default="{}",
        help='JSON object for create body under "input", e.g. \'{"script":"hello"}\'',
    )
    parser.add_argument("--asset-url", default="https://example.com/e2e-asset.mp4")
    parser.add_argument("--webhook-delay", type=float, default=0.4, help="Seconds after create before webhook")
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    try:
        input_obj = json.loads(args.input)
    except json.JSONDecodeError as exc:
        print(f"Invalid --input JSON: {exc}", file=sys.stderr)
        raise SystemExit(2)

    base = args.url.rstrip("/")
    create_url = f"{base}{CREATE_PATH[args.provider]}"
    print(f"POST {create_url}")
    status, create_body = http_json("POST", create_url, {"input": input_obj})
    print(f"create HTTP {status}: {json.dumps(create_body)}")
    if status >= 400:
        raise SystemExit(1)

    task_id = create_body.get("task_id")
    request_id = create_body.get("request_id")
    if not task_id or not request_id:
        print("Missing task_id or request_id in response", file=sys.stderr)
        raise SystemExit(1)

    time.sleep(args.webhook_delay)
    webhook_payload = {
        "request_id": request_id,
        "status": "completed",
        "asset_url": args.asset_url,
        "provider": args.provider,
    }
    wh_status, wh_body = post_signed_webhook(
        base_url=base,
        provider=args.provider,
        secret=args.webhook_secret,
        payload=webhook_payload,
    )
    print(f"webhook HTTP {wh_status}: {wh_body}")
    if wh_status >= 400:
        raise SystemExit(1)

    job_url = f"{base}/job/{task_id}"
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        st, job_body = http_json("GET", job_url)
        if st >= 400:
            print(f"poll HTTP {st}: {job_body}")
            time.sleep(args.poll_interval)
            continue
        state = job_body.get("status")
        print(f"job {state}: {json.dumps(job_body)}")
        if state in SUCCESS_STATES:
            print("E2E OK: Celery task completed.")
            raise SystemExit(0)
        if state in {"FAILURE", "REVOKED"}:
            print("E2E FAIL: task did not succeed.", file=sys.stderr)
            raise SystemExit(1)
        time.sleep(args.poll_interval)

    print("E2E FAIL: timeout waiting for SUCCESS", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
