import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from db import get_db
from deps import get_agency_user
from models import GrowthPlan, Campaign, User

router = APIRouter()

class GrowthPlanSchema(BaseModel):
    id: str
    campaign_id: str
    brand_id: str
    what_worked: Optional[dict]
    what_failed: Optional[dict]
    next_cycle_budget: Optional[float]
    new_opportunities: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[GrowthPlanSchema])
def list_growth_plans(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    query = db.query(GrowthPlan)
    if user and user.role != "platform_admin":
        if user.organization_id:
            query = query.join(Campaign).filter(Campaign.organization_id == user.organization_id)
        else:
            query = query.join(Campaign).filter(Campaign.user_id == user.id)
    return query.order_by(GrowthPlan.created_at.desc()).all()

@router.get("/campaign/{campaign_id}", response_model=List[GrowthPlanSchema])
def get_campaign_growth_plans(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if user and user.role != "platform_admin" and campaign.user_id != user.id:
        if not (user.organization_id and campaign.organization_id == user.organization_id):
            raise HTTPException(status_code=403, detail="Forbidden")

    return db.query(GrowthPlan).filter(GrowthPlan.campaign_id == campaign_id).order_by(GrowthPlan.created_at.desc()).all()

@router.post("/campaign/{campaign_id}/generate")
def generate_growth_plan(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Manually triggers generation of the end-of-cycle Growth Plan."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if user and user.role != "platform_admin" and campaign.user_id != user.id:
        if not (user.organization_id and campaign.organization_id == user.organization_id):
            raise HTTPException(status_code=403, detail="Forbidden")

    from tasks import generate_growth_plan_task
    task = generate_growth_plan_task.delay(campaign_id)
    
    return {"ok": True, "task_id": task.id, "message": "Growth plan generation started"}
