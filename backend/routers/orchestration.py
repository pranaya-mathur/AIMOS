from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from db import get_db
from deps import get_agency_user
from models import Campaign, User
from tasks import resume_campaign_iteration

router = APIRouter()

class ResumeBody(BaseModel):
    feedback: str

@router.post("/{campaign_id}/resume")
def resume_campaign(
    campaign_id: str,
    body: ResumeBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.status != "awaiting_feedback":
        raise HTTPException(status_code=400, detail="Campaign is not awaiting feedback")

    # Authorization Check
    if user and user.role != "platform_admin":
        if campaign.organization_id and campaign.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Forbidden")

    # Trigger resumption task
    resume_campaign_iteration.delay(campaign_id, body.feedback)
    
    return {"ok": True, "message": "Resumption triggered"}
