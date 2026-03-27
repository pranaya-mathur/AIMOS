import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from deps import get_agency_user
from models import Campaign, User
from tasks import run_campaign

router = APIRouter()


class CreateCampaignBody(BaseModel):
    name: Optional[str] = None
    input: dict = Field(default_factory=dict)  # campaign brief / requirements


@router.post("/create")
def create_campaign(
    body: CreateCampaignBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    cid = str(uuid.uuid4())
    row = Campaign(
        id=cid,
        user_id=user.id if user else None,
        name=body.name,
        status="pending_approval",
        input=body.input,
    )
    db.add(row)
    db.commit()
    task = run_campaign.delay({"campaign_id": cid, "input": body.input})
    row.celery_task_id = task.id
    row.status = "processing"
    db.commit()
    return {"task_id": task.id, "campaign_id": cid}


@router.get("/{campaign_id}")
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if user and row.user_id and row.user_id != user.id and user.role != "platform_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {
        "id": row.id,
        "name": row.name,
        "status": row.status,
        "input": row.input,
        "output": row.output,
        "celery_task_id": row.celery_task_id,
        "user_id": row.user_id,
    }


class PatchCampaignBody(BaseModel):
    status: Optional[str] = None


_ALLOWED_CAMPAIGN_STATUS = frozenset(
    {
        "draft",
        "pending_approval",
        "pending_payment",
        "paid",
        "processing",
        "active",
        "paused",
        "completed",
        "failed",
    }
)


@router.patch("/{campaign_id}")
def patch_campaign(
    campaign_id: str,
    body: PatchCampaignBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Manual status transitions (e.g. approval) before payment integration is wired in Bubble."""
    row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if user and row.user_id and row.user_id != user.id and user.role != "platform_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    if body.status:
        if body.status not in _ALLOWED_CAMPAIGN_STATUS:
            raise HTTPException(status_code=400, detail="Invalid status")
        row.status = body.status
    db.commit()
    return {"id": row.id, "status": row.status}
