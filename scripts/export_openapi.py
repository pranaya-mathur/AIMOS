#!/usr/bin/env python3
"""
Download OpenAPI JSON from a running AIMOS API (for Bubble / Postman).

  python3 scripts/export_openapi.py
  python3 scripts/export_openapi.py http://localhost:8000 docs/bubble/openapi-snapshot.json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

_DEFAULT_URL = "http://127.0.0.1:8000/openapi.json"
_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_OUT = _ROOT / "docs" / "bubble" / "openapi-snapshot.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default=_DEFAULT_URL, help="OpenAPI JSON URL")
    ap.add_argument("outfile", nargs="?", default=str(_DEFAULT_OUT), help="Output path")
    args = ap.parse_args()

    out = Path(args.outfile)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        with urllib.request.urlopen(args.url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"ERROR: could not fetch {args.url}: {exc}", file=sys.stderr)
        print("Start the API first (e.g. docker compose up).", file=sys.stderr)
        return 1

    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(data.get('paths', {}))} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
