import uuid
from datetime import datetime, timedelta, timezone as tz
from typing import Any, Optional

import jwt

from core.config import get_settings


def create_access_token(*, subject: str, email: str, role: str) -> str:
    settings = get_settings()
    now = datetime.now(tz.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "email": email,
        "role": role,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def parse_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.split(" ", 1)[1].strip() or None
