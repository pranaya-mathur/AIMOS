from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from deps import get_agency_user
from models import User, AdCreative, Campaign
from db import get_db
from sqlalchemy.orm import Session
from tasks import generate_variation

router = APIRouter()


class VariationsBody(BaseModel):
    brief: str = Field(..., min_length=1, description="Campaign / creative brief")
    n: int = Field(default=3, ge=1, le=10, description="Number of parallel variations")
    campaign_id: Optional[str] = None


@router.post("/variations")
def creative_variations(
    body: VariationsBody,
    user: Optional[User] = Depends(get_agency_user),
):
    """Queues N parallel OpenAI creative copy tasks (Celery). Poll GET /job/{task_id} for each."""
    uid = user.id if user else None
    task_ids = []
    for i in range(body.n):
        task_ids.append(generate_variation.delay(body.brief, i, user_id=uid, campaign_id=body.campaign_id).id)
    return {"task_ids": task_ids, "count": body.n}


class CreativeUpdateBody(BaseModel):
    headline: Optional[str] = None
    body_copy: Optional[str] = None
    cta_text: Optional[str] = None
    is_favorite: Optional[str] = None


@router.get("")
def list_creatives(
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    query = db.query(AdCreative)
    if user and user.role != "platform_admin":
        query = query.filter(AdCreative.user_id == user.id)
    if campaign_id:
        query = query.filter(AdCreative.campaign_id == campaign_id)
    return query.order_by(AdCreative.created_at.desc()).all()


@router.patch("/{creative_id}")
def update_creative(
    creative_id: str,
    body: CreativeUpdateBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    row = db.query(AdCreative).filter(AdCreative.id == creative_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Creative not found")
    if user and user.role != "platform_admin" and row.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if body.headline is not None: row.headline = body.headline
    if body.body_copy is not None: row.body_copy = body.body_copy
    if body.cta_text is not None: row.cta_text = body.cta_text
    if body.is_favorite is not None: row.is_favorite = body.is_favorite

    db.commit()
    return {"ok": True}


@router.post("/{creative_id}/approve")
def approve_creative(
    creative_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Marks a creative as approved for its linked campaign."""
    row = db.query(AdCreative).filter(AdCreative.id == creative_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Creative not found")
    if user and user.role != "platform_admin" and row.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Mark as approved
    row.status = "approved"

    # If linked to a campaign, update campaign output to reflect selection
    if row.campaign_id:
        campaign = db.query(Campaign).filter(Campaign.id == row.campaign_id).first()
        if campaign:
            output = dict(campaign.output or {})
            output["selected_creative_id"] = creative_id
            output["selected_creative"] = {
                "headline": row.headline,
                "body_copy": row.body_copy,
                "cta_text": row.cta_text
            }
            campaign.output = output
            # Move status to next logical step if it was in 'draft' or 'processing'
            if campaign.status in {"draft", "processing"}:
                campaign.status = "pending_approval"

    db.commit()
    return {"ok": True}
