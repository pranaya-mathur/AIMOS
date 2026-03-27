#!/usr/bin/env python3
"""
Validate `.env` before `docker compose up` (or local runs).

Usage:
  python3 scripts/validate_env.py
  python3 scripts/validate_env.py --strict   # also require non-placeholder OpenAI key
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _load_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            out[k] = v
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="Fail if OPENAI_API_KEY looks like a placeholder")
    args = ap.parse_args()

    env_path = _ROOT / ".env"
    if not env_path.is_file():
        print(f"ERROR: {_ROOT}/.env not found. Copy .env.example to .env and fill values.", file=sys.stderr)
        return 1

    env = _load_env(env_path)
    required = ("DATABASE_URL", "REDIS_URL", "JWT_SECRET")
    missing = [k for k in required if not env.get(k)]
    if missing:
        print(f"ERROR: missing keys in .env: {', '.join(missing)}", file=sys.stderr)
        return 1

    if not env.get("OPENAI_API_KEY"):
        print("WARN: OPENAI_API_KEY is empty — campaign / agent runs will fail until set.", file=sys.stderr)

    oai = env.get("OPENAI_API_KEY", "")
    placeholder = bool(
        args.strict
        and (
            not oai
            or oai == "your_key_here"
            or oai.startswith("sk-your-")
            or oai.startswith("sk-placeholder")
        )
    )
    if placeholder:
        print("ERROR: OPENAI_API_KEY must be a real key in --strict mode.", file=sys.stderr)
        return 1

    du = env.get("DATABASE_URL", "")
    if "postgresql://" in du and "@db:" not in du and "localhost" not in du and "127.0.0.1" not in du:
        print(
            "WARN: DATABASE_URL host may not match docker-compose (use hostname `db` inside containers).",
            file=sys.stderr,
        )

    ru = env.get("REDIS_URL", "")
    if "redis://" in ru and "redis:" not in ru.split("@")[-1] and "localhost" not in ru and "127.0.0.1" not in ru:
        print(
            "WARN: REDIS_URL host may not match docker-compose (use hostname `redis` inside containers).",
            file=sys.stderr,
        )

    if env.get("JWT_SECRET") and len(env["JWT_SECRET"]) < 16:
        print("WARN: JWT_SECRET is short — use a long random string in production.", file=sys.stderr)

    print(f"OK — {_ROOT}/.env looks usable for AIMOS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
