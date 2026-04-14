import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from deps import get_agency_user
from models import Campaign, User
from services.usage.exceptions import QuotaExceededError
from services.usage.quotas import assert_can_create_campaign
from tasks import run_campaign

router = APIRouter()


@router.get("")
def list_campaigns(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
    limit: int = 20,
):
    """Recent campaigns for the current user / org (or all when AUTH_DISABLED)."""
    cap = max(1, min(limit, 100))
    q = db.query(Campaign).order_by(Campaign.created_at.desc())
    if user is None:
        rows = q.limit(cap).all()
    elif user.role == "platform_admin":
        rows = q.limit(cap).all()
    elif user.organization_id:
        rows = (
            q.filter(Campaign.organization_id == user.organization_id).limit(cap).all()
        )
    else:
        rows = q.filter(Campaign.user_id == user.id).limit(cap).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


class CreateCampaignBody(BaseModel):
    name: Optional[str] = None
    input: dict = Field(default_factory=dict)  # campaign brief / requirements
    platform: str = Field(default="both", description="meta, google, or both")
    objective: str = Field(default="leads", description="leads, sales, or awareness")
    total_budget: float = Field(default=1000.0)
    schedule_start: Optional[str] = None
    schedule_end: Optional[str] = None


@router.post("/create")
def create_campaign(
    body: CreateCampaignBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    if user:
        try:
            assert_can_create_campaign(db, user)
        except QuotaExceededError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc

    from services.governance.audit import log_audit_event
    cid = str(uuid.uuid4())
    
    log_audit_event(
        action="CAMPAIGN_CREATE",
        user_id=user.id if user else None,
        organization_id=user.organization_id if user else None,
        resource_id=cid,
        metadata={"name": body.name, "platform": body.platform}
    )

    row = Campaign(
        id=cid,
        user_id=user.id if user else None,
        organization_id=user.organization_id if user else None,
        name=body.name,
        status="processing",
        input=body.input,
        platform=body.platform,
        objective=body.objective,
        total_budget=body.total_budget,
        schedule_start=datetime.fromisoformat(body.schedule_start) if body.schedule_start else None,
        schedule_end=datetime.fromisoformat(body.schedule_end) if body.schedule_end else None,
    )
    db.add(row)
    db.commit()
    
    # Pass structured context to Celeste/Celery
    task_payload = {
        "campaign_id": cid, 
        "input": body.input,
        "platform": body.platform,
        "objective": body.objective,
        "total_budget": body.total_budget
    }
    task = run_campaign.delay(task_payload)
    row.celery_task_id = task.id
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
    if user and user.role != "platform_admin":
        if row.organization_id:
            if row.organization_id != user.organization_id:
                raise HTTPException(status_code=403, detail="Forbidden: Organization mismatch")
        elif row.user_id and row.user_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden: Ownership mismatch")
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
        "rejected",
    }
)


@router.post("/{campaign_id}/rerun")
def rerun_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Re-queue the 12-agent pipeline with the same stored `input` (clears prior output)."""
    row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if user and user.role != "platform_admin":
        if row.organization_id:
            if row.organization_id != user.organization_id:
                raise HTTPException(status_code=403, detail="Forbidden: Organization mismatch")
        elif row.user_id and row.user_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden: Ownership mismatch")
    if row.status == "processing":
        raise HTTPException(
            status_code=409,
            detail="Campaign is already processing; wait for the current job to finish.",
        )
    inner = row.input if isinstance(row.input, dict) else {}
    row.output = None
    row.status = "processing"
    db.commit()
    task = run_campaign.delay({"campaign_id": row.id, "input": inner})
    row.celery_task_id = task.id
    db.commit()
    return {"task_id": task.id, "campaign_id": row.id}


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
    if user and user.role != "platform_admin":
        if row.organization_id:
            if row.organization_id != user.organization_id:
                raise HTTPException(status_code=403, detail="Forbidden: Organization mismatch")
        elif row.user_id and row.user_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden: Ownership mismatch")
    if body.status:
        if body.status not in _ALLOWED_CAMPAIGN_STATUS:
            raise HTTPException(status_code=400, detail="Invalid status")
        row.status = body.status
    db.commit()
    return {"id": row.id, "status": row.status}
