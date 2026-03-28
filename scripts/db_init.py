#!/usr/bin/env python3
"""
Idempotent DB helper: ensure tables exist and seed a dev agency user.

Run inside the API container:
  docker compose exec api python /app/scripts/db_init.py

Or locally (venv, Postgres reachable):
  python scripts/db_init.py
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Resolve backend package root: /app in Docker, or ./backend from repo
_here = Path(__file__).resolve().parent.parent
if (_here / "main.py").is_file():
    sys.path.insert(0, str(_here))
else:
    sys.path.insert(0, str(_here / "backend"))

from sqlalchemy import text

from db import Base, SessionLocal, apply_schema_patches, engine
import models  # noqa: F401 — register ORM models (Campaign, JobAudit, …)
from models import Organization, User
from services.auth import hash_password


# Must pass EmailStr validation (avoid .local — pydantic/email-validator often returns 422)
DEV_EMAIL = "aimos-dev@example.com"
DEV_PASSWORD = "devpass123"


def main() -> int:
    Base.metadata.create_all(bind=engine)
    apply_schema_patches()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    db = SessionLocal()
    try:
        # Seed default organization
        org_id = "org-default"
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            org = Organization(id=org_id, name="Default Organization")
            db.add(org)
            db.commit()
            print(f"Seeded organization: {org.name}")

        existing = db.query(User).filter(User.email == DEV_EMAIL).first()
        if existing:
            if not existing.organization_id:
                existing.organization_id = org_id
                db.commit()
                print(f"Updated existing seed user with org_id: {org_id}")
            print(f"Seed user already exists: {DEV_EMAIL}")
            return 0
        uid = str(uuid.uuid4())
        user = User(
            id=uid,
            email=DEV_EMAIL,
            hashed_password=hash_password(DEV_PASSWORD),
            role="platform_admin",
            full_name="AIMOS Dev User",
            organization_id=org_id,
        )
        db.add(user)
        db.commit()
        print(f"Created dev user: {DEV_EMAIL} / {DEV_PASSWORD} (platform_admin, org: {org_id})")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        db.rollback()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
