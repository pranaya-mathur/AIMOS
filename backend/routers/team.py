import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from db import get_db
from deps import get_current_user
from models import User, TeamInvite, Organization
from services.usage.quotas import assert_can_add_seat
from services.usage.exceptions import QuotaExceededError

router = APIRouter()

class InviteBody(BaseModel):
    email: EmailStr
    role: str = "agency_client"

@router.post("/invite")
def invite_member(
    body: InviteBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="Only organization members can invite others")

    # Enforce seat quota
    try:
        assert_can_add_seat(db, user.organization_id)
    except QuotaExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))

    # Check if user already exists
    existing = db.query(User).filter(User.email == body.email).first()
    if existing and existing.organization_id:
        raise HTTPException(status_code=400, detail="User is already in an organization")

    invite = TeamInvite(
        id=str(uuid.uuid4()),
        organization_id=user.organization_id,
        email=body.email,
        role=body.role,
        status="pending",
        token=str(uuid.uuid4()),
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(invite)
    db.commit()

    return {"ok": True, "invite_id": invite.id, "invite_url": f"/join?token={invite.token}"}

@router.get("/members")
def list_members(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="Organization required")

    members = db.query(User).filter(User.organization_id == user.organization_id).all()
    invites = db.query(TeamInvite).filter(TeamInvite.organization_id == user.organization_id, TeamInvite.status == "pending").all()

    return {
        "members": [
            {
                "id": m.id,
                "email": m.email,
                "full_name": m.full_name,
                "role": m.role,
                "created_at": m.created_at.isoformat()
            } for m in members
        ],
        "pending_invites": [
            {
                "id": i.id,
                "email": i.email,
                "role": i.role,
                "expires_at": i.expires_at.isoformat()
            } for i in invites
        ]
    }

@router.delete("/members/{user_id}")
def remove_member(
    user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    target = db.query(User).filter(User.id == user_id, User.organization_id == user.organization_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    if target.id == user.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself")

    # Disconnect from organization
    target.organization_id = None
    db.commit()

    return {"ok": True}
