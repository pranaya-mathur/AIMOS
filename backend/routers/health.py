from fastapi import APIRouter, HTTPException
from redis import Redis
from sqlalchemy import text

from core.config import get_settings
from db import engine

router = APIRouter()


@router.get("/live")
def live():
    return {"status": "alive"}


@router.get("/ready")
def ready():
    """Verifies Postgres and Redis connectivity (for orchestrators / load balancers)."""
    errors: list[str] = []
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        errors.append(f"database:{exc}")

    try:
        Redis.from_url(get_settings().redis_url).ping()
    except Exception as exc:
        errors.append(f"redis:{exc}")

    if errors:
        raise HTTPException(status_code=503, detail={"status": "not_ready", "errors": errors})
    return {"status": "ready"}
