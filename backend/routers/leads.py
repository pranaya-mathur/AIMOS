from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from deps import get_agency_user
from models import Lead, ConversationMessage, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ConversationMessageSchema(BaseModel):
    id: str
    direction: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class LeadSchema(BaseModel):
    id: str
    phone: str
    full_name: Optional[str]
    email: Optional[str]
    status: str
    score: int
    intent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[LeadSchema])
def list_leads(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Fetch all leads for the current user/org."""
    query = db.query(Lead)
    if user and user.role != "platform_admin":
        query = query.filter(Lead.user_id == user.id)
    return query.order_by(Lead.score.desc()).all()

@router.get("/{lead_id}/messages", response_model=List[ConversationMessageSchema])
def get_lead_messages(
    lead_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Fetch conversation history for a lead."""
    # RBAC check
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if user and user.role != "platform_admin" and lead.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return db.query(ConversationMessage).filter(ConversationMessage.lead_id == lead_id).order_by(ConversationMessage.created_at.asc()).all()

@router.patch("/{lead_id}/status")
def update_lead_status(
    lead_id: str,
    status: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if user and user.role != "platform_admin" and lead.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    lead.status = status
    db.commit()
    return {"ok": True}
