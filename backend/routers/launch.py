from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from deps import get_agency_user
from models import User
from services.integrations.google_ads_stub import GoogleAdsNotConfiguredError, enqueue_google_ads_placeholder
from services.integrations.integration_status import snapshot
from services.integrations.meta_marketing import MetaMarketingError, create_draft_campaign_on_meta
from services.integrations.whatsapp_cloud import WhatsAppCloudError, send_text_message
from tasks import launch_meta_campaign_task, send_google_ads_placeholder_task, send_whatsapp_task

router = APIRouter()


@router.get("/status")
def launch_status():
    """Shows which integration env vars are set (boolean flags only)."""
    return snapshot()


class MetaLaunchBody(BaseModel):
    name: str = Field(..., min_length=1)
    objective: str = Field(default="OUTCOME_AWARENESS")
    async_job: bool = Field(default=True, description="If true, enqueue Celery task and return task_id")


class WhatsAppBody(BaseModel):
    to_e164: str = Field(..., description="Recipient WhatsApp number with country code, no +")
    body: str = Field(..., min_length=1)
    async_job: bool = True


class GoogleAdsBody(BaseModel):
    campaign_name: str
    customer_id: Optional[str] = None
    async_job: bool = True


@router.post("/meta")
def launch_meta(
    body: MetaLaunchBody,
    user: Optional[User] = Depends(get_agency_user),
):
    del user
    payload = body.model_dump(exclude={"async_job"})
    if body.async_job:
        task = launch_meta_campaign_task.delay(payload)
        return {"task_id": task.id, "mode": "async"}
    try:
        return {"mode": "sync", "result": create_draft_campaign_on_meta(name=body.name, objective=body.objective)}
    except MetaMarketingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/whatsapp")
def launch_whatsapp(
    body: WhatsAppBody,
    user: Optional[User] = Depends(get_agency_user),
):
    del user
    if body.async_job:
        task = send_whatsapp_task.delay(body.to_e164, body.body)
        return {"task_id": task.id, "mode": "async"}
    try:
        return {"mode": "sync", "result": send_text_message(to_e164=body.to_e164, body=body.body)}
    except WhatsAppCloudError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/google")
def launch_google(
    body: GoogleAdsBody,
    user: Optional[User] = Depends(get_agency_user),
):
    del user
    if body.async_job:
        task = send_google_ads_placeholder_task.delay(body.campaign_name, body.customer_id)
        return {"task_id": task.id, "mode": "async", "note": "Placeholder task until google-ads RPC is wired"}
    try:
        return {
            "mode": "sync",
            "result": enqueue_google_ads_placeholder(
                campaign_name=body.campaign_name,
                customer_id=body.customer_id,
            ),
        }
    except GoogleAdsNotConfiguredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
