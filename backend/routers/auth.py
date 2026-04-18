import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from core.config import get_settings
from db import get_db
from deps import get_current_user, get_current_user_optional
from models import User
from services.auth import (
    create_access_token,
    create_password_reset_token,
    hash_password,
    verify_password,
)

router = APIRouter()
_refresh_bearer = HTTPBearer(auto_error=True)


class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    role: Literal["agency_client", "end_customer"] = "agency_client"


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequestBody(BaseModel):
    email: EmailStr


class PasswordResetConfirmBody(BaseModel):
    token: str
    password: str = Field(min_length=8)


@router.post("/register")
def register(body: RegisterBody, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    uid = str(uuid.uuid4())
    user = User(
        id=uid,
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
        full_name=body.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "role": user.role}


@router.post("/password-reset/request")
def password_reset_request(
    body: PasswordResetRequestBody, db: Session = Depends(get_db)
):
    """
    Request a password reset. Always returns ok=true (no email enumeration).
    When PASSWORD_RESET_TOKEN_IN_RESPONSE=1, includes reset_token for local/dev
    (no email is sent — integrate SES/SendGrid for production).
    """
    settings = get_settings()
    user = db.query(User).filter(User.email == body.email).first()
    out: dict = {"ok": True}
    if user and settings.password_reset_token_in_response:
        out["reset_token"] = create_password_reset_token(subject=user.id)
    return out


@router.post("/password-reset/confirm")
def password_reset_confirm(
    body: PasswordResetConfirmBody, db: Session = Depends(get_db)
):
    """Set a new password using a JWT from /password-reset/request (typ=pwd_reset)."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            body.token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token") from None
    if payload.get("typ") != "pwd_reset":
        raise HTTPException(status_code=400, detail="Invalid token type")
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        raise HTTPException(status_code=400, detail="Invalid token payload")
    user = db.query(User).filter(User.id == sub).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user.hashed_password = hash_password(body.password)
    db.commit()
    return {"ok": True}


@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "role": user.role}


@router.post("/refresh")
def refresh_token(
    creds: HTTPAuthorizationCredentials = Depends(_refresh_bearer),
    db: Session = Depends(get_db),
):
    """
    Issue a new access token from a still-valid signature. Allows renewal within
    a short grace period after `exp` so active sessions can slide without re-login.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token") from None

    sub = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")
    if not sub or not email or not role:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    exp_ts = payload.get("exp")
    now = datetime.now(timezone.utc)
    if exp_ts is not None:
        exp_dt = datetime.fromtimestamp(float(exp_ts), tz=timezone.utc)
        if now > exp_dt + timedelta(days=7):
            raise HTTPException(status_code=401, detail="Refresh window expired")

    user = db.query(User).filter(User.id == sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "role": user.role}


@router.get("/me")
def me(user: Optional[User] = Depends(get_current_user_optional)):
    settings = get_settings()
    if user is None:
        if settings.auth_disabled_flag:
            return {
                "id": None,
                "email": None,
                "role": None,
                "full_name": None,
                "note": "AUTH_DISABLED: no user context.",
            }
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
    }
