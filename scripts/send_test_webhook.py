#!/usr/bin/env python3
import argparse
import sys
import uuid
from pathlib import Path

# Allow `python3 scripts/send_test_webhook.py` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from webhook_common import post_signed_webhook


def main():
    parser = argparse.ArgumentParser(description="Send signed test webhook to local AIMOS API.")
    parser.add_argument("--provider", choices=["adcreative", "pictory", "elevenlabs"], required=True)
    parser.add_argument("--secret", required=True, help="Provider webhook secret")
    parser.add_argument("--request-id", default=str(uuid.uuid4()))
    parser.add_argument("--status", default="completed")
    parser.add_argument("--asset-url", default="https://example.com/generated-asset")
    parser.add_argument("--url", default="http://localhost:8000")
    args = parser.parse_args()

    payload = {
        "request_id": args.request_id,
        "status": args.status,
        "asset_url": args.asset_url,
        "provider": args.provider,
    }
    status, body = post_signed_webhook(
        base_url=args.url,
        provider=args.provider,
        secret=args.secret,
        payload=payload,
    )
    print(f"HTTP {status}")
    print(body)
    print(f"request_id={args.request_id}")
    if status >= 400:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
