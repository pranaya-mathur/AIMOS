import json
import logging
import os
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from models import JobAudit
from services.integrations.media_store import save_webhook_result
from services.integrations.webhook_constants import PROVIDER_WEBHOOK_SECRET_ENV, SUPPORTED_MEDIA_PROVIDERS
from services.integrations.webhook_security import verify_provider_signature
from tasks import run_media_provider_job

logger = logging.getLogger(__name__)

router = APIRouter()


class MediaRequest(BaseModel):
    input: dict = Field(default_factory=dict)


def _enqueue(provider: str, input_payload: dict, db: Session) -> dict:
    if provider not in SUPPORTED_MEDIA_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unknown provider")
    request_id = str(uuid.uuid4())
    task = run_media_provider_job.delay(provider, input_payload, request_id)
    audit = JobAudit(
        id=str(uuid.uuid4()),
        celery_task_id=task.id,
        provider=provider,
        request_id=request_id,
        input_snapshot=input_payload or {},
    )
    db.add(audit)
    db.commit()
    logger.info(
        "media.job_enqueued provider=%s celery_task_id=%s request_id=%s",
        provider,
        task.id,
        request_id,
    )
    return {"task_id": task.id, "provider": provider, "request_id": request_id}


@router.post("/adcreative/create")
def create_adcreative(payload: MediaRequest, db: Session = Depends(get_db)):
    return _enqueue("adcreative", payload.input, db)


@router.post("/pictory/create")
def create_pictory(payload: MediaRequest, db: Session = Depends(get_db)):
    return _enqueue("pictory", payload.input, db)


@router.post("/elevenlabs/create")
def create_elevenlabs(payload: MediaRequest, db: Session = Depends(get_db)):
    return _enqueue("elevenlabs", payload.input, db)


@router.post("/webhook/{provider}")
async def media_webhook(
    provider: str,
    request: Request,
    x_webhook_token: str | None = Header(default=None),
):
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    provider_key = provider.lower()
    if provider_key not in SUPPORTED_MEDIA_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported provider")

    signature_ok, signature_reason = verify_provider_signature(provider_key, raw_body, request.headers)
    provider_secret_is_configured = bool(os.getenv(PROVIDER_WEBHOOK_SECRET_ENV[provider_key]))
    if provider_secret_is_configured and not signature_ok:
        raise HTTPException(status_code=401, detail=f"Signature check failed: {signature_reason}")

    if not provider_secret_is_configured:
        expected_token = os.getenv("MEDIA_WEBHOOK_TOKEN")
        if expected_token and x_webhook_token != expected_token:
            raise HTTPException(status_code=401, detail="Invalid webhook token")

    request_id = payload.get("request_id")
    meta = payload.get("metadata")
    if not request_id and isinstance(meta, dict):
        request_id = meta.get("request_id")
    _meta = payload.get("_meta")
    if not request_id and isinstance(_meta, dict):
        request_id = _meta.get("request_id")
    if not request_id:
        raise HTTPException(status_code=400, detail="request_id missing from webhook payload")

    save_webhook_result(provider=provider_key, request_id=request_id, payload=payload)
    logger.info("media.webhook_accepted provider=%s request_id=%s", provider_key, request_id)
    return {"status": "accepted", "provider": provider_key, "request_id": request_id}
