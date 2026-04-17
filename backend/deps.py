from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.config import get_settings
from db import get_db
from models import User
from services.auth.tokens import decode_token

security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    settings = get_settings()
    if settings.auth_disabled_flag:
        return None
    if not creds:
        return None
    try:
        payload = decode_token(creds.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user(user: Optional[User] = Depends(get_current_user_optional)) -> User:
    settings = get_settings()
    if settings.auth_disabled_flag:
        return user  # type: ignore
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def get_agency_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Agency client or platform admin; returns first user when AUTH_DISABLED=1."""
    settings = get_settings()
    if settings.auth_disabled_flag:
        return db.query(User).filter(User.role == "platform_admin").first() or db.query(User).first()
    if not creds:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = decode_token(creds.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.role not in ("agency_client", "platform_admin"):
        raise HTTPException(status_code=403, detail="Agency or admin role required")
    return user


def get_admin_user(user: User = Depends(get_current_user)) -> User:
    """Strictly platform_admin; None only when AUTH_DISABLED=1."""
    settings = get_settings()
    if settings.auth_disabled_flag:
        return user  # type: ignore
    if user.role != "platform_admin":
        raise HTTPException(status_code=403, detail="Platform admin role required")
    return user


def get_end_customer(user: User = Depends(get_current_user)) -> User:
    """End customers only (direct brand owners)."""
    if user.role not in ("end_customer", "agency_client", "platform_admin"):
        raise HTTPException(status_code=403, detail="Customer role required")
    return user


def check_org_access(user: User, target_org_id: str):
    """
    Hardened 2.0 Phase 7: Enforce organization-level silos.
    Ensures that users from Org A cannot access resources in Org B.
    """
    if user.role == "platform_admin":
        return True
    
    if not user.organization_id or user.organization_id != target_org_id:
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Resource belongs to a different organization silo."
        )
    return True

def can_access_brand(user: User, brand_id: str, db: Session):
    """
    Policy: 
    - End Customer: Only their own brand.
    - Agency Client: Any brand in their Organization.
    - Admin: Everything.
    """
    from models import Brand
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        return False
        
    if user.role == "platform_admin":
        return True
        
    if user.role == "end_customer":
        return brand.user_id == user.id
        
    if user.role == "agency_client":
        return brand.organization_id == user.organization_id
        
    return False
