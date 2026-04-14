from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from deps import get_agency_user
from models import Organization, User
from pydantic import BaseModel

router = APIRouter()

class WhitelabelConfig(BaseModel):
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    site_name: Optional[str] = None

@router.get("/config", response_model=WhitelabelConfig)
def get_whitelabel_config(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Fetch whitelabel branding for the current organization."""
    if not user or not user.organization_id:
        # Default branding for no org
        return WhitelabelConfig(site_name="AIMOS Enterprise")
    
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    config = org.whitelabel_config or {}
    return WhitelabelConfig(
        logo_url=config.get("logo_url"),
        primary_color=config.get("primary_color"),
        site_name=config.get("site_name", "AIMOS Enterprise")
    )

@router.patch("/config")
def update_whitelabel_config(
    body: WhitelabelConfig,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Update whitelabel branding for the current organization."""
    if not user or not user.organization_id:
        raise HTTPException(status_code=403, detail="Organization required")
    
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    current_config = org.whitelabel_config or {}
    new_config = {**current_config, **body.model_dump(exclude_unset=True)}
    org.whitelabel_config = new_config
    db.commit()
    
    from services.governance.audit import log_audit_event
    log_audit_event(
        action="ORG_WHITELABEL_UPDATE",
        user_id=user.id,
        organization_id=org.id,
        metadata=new_config
    )
    
    return {"ok": True}
