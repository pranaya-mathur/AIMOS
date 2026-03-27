
import logging

from celery_app import celery
from db import SessionLocal
from models import Campaign
from services.orchestrator import run_agents
from services.usage.context import clear_usage_context, set_usage_context
from services.integrations.media_clients import (
    create_adcreative,
    create_elevenlabs_voiceover,
    create_pictory_video,
)

logger = logging.getLogger(__name__)

_MEDIA_DISPATCH = {
    "adcreative": create_adcreative,
    "pictory": create_pictory_video,
    "elevenlabs": create_elevenlabs_voiceover,
}


def _with_request_metadata(data: dict | None, request_id: str | None) -> dict:
    payload = dict(data or {})
    payload.setdefault("metadata", {})
    if request_id:
        payload["metadata"]["request_id"] = request_id
    return payload


def _persist_campaign_result(campaign_id: str, result: object) -> None:
    db = SessionLocal()
    try:
        row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not row:
            logger.warning("campaign %s not found for result persistence", campaign_id)
            return
        if isinstance(result, dict):
            row.output = result
        else:
            row.output = {"result": str(result)}
        row.status = "completed"
        db.commit()
    except Exception:
        logger.exception("failed to persist campaign %s", campaign_id)
        try:
            row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if row:
                row.status = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@celery.task
def run_campaign(data):
    campaign_id = None
    if isinstance(data, dict):
        campaign_id = data.get("campaign_id")
        inner = data["input"] if "input" in data else data
    else:
        inner = data

    ctx_user_id = None
    if campaign_id:
        db = SessionLocal()
        try:
            row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if row:
                ctx_user_id = row.user_id
        finally:
            db.close()

    try:
        set_usage_context(user_id=ctx_user_id, campaign_id=campaign_id)
        result = run_agents(inner)
    except Exception:
        if campaign_id:
            db = SessionLocal()
            try:
                row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
                if row:
                    row.status = "failed"
                    db.commit()
            finally:
                db.close()
        raise
    finally:
        clear_usage_context()

    if campaign_id:
        _persist_campaign_result(campaign_id, result)
    return result


@celery.task(name="media.run_provider")
def run_media_provider_job(provider: str, data=None, request_id=None):
    payload = _with_request_metadata(data, request_id)
    if provider not in _MEDIA_DISPATCH:
        raise ValueError(f"Unknown media provider: {provider}")
    return _MEDIA_DISPATCH[provider](payload, request_id=request_id)


@celery.task
def launch_meta_campaign_task(payload: dict):
    from services.integrations.meta_marketing import create_draft_campaign_on_meta

    return create_draft_campaign_on_meta(
        name=payload.get("name") or "AIMOS campaign",
        objective=payload.get("objective") or "OUTCOME_AWARENESS",
    )


@celery.task
def send_whatsapp_task(to_e164: str, body: str):
    from services.integrations.whatsapp_cloud import send_text_message

    return send_text_message(to_e164=to_e164, body=body)


@celery.task
def send_google_ads_placeholder_task(campaign_name: str, customer_id=None):
    from services.integrations.google_ads_stub import enqueue_google_ads_placeholder

    return enqueue_google_ads_placeholder(campaign_name=campaign_name, customer_id=customer_id)


@celery.task
def generate_variation(brief: str, index: int, user_id: str | None = None):
    from services.integrations.openai_service import generate_text

    try:
        set_usage_context(user_id=user_id, campaign_id=None)
        prompt = (
            f"Write one creative marketing copy variation #{index + 1} for this brief. "
            "Return plain text only.\n\nBrief:\n"
            f"{brief}"
        )
        return {"index": index, "copy": generate_text(prompt)}
    finally:
        clear_usage_context()


@celery.task
def optimization_tick():
    """Scheduled job: placeholder for pause/scale rules; extend with real metrics."""
    db = SessionLocal()
    try:
        active = db.query(Campaign).filter(Campaign.status == "active").count()
        processing = db.query(Campaign).filter(Campaign.status == "processing").count()
        logger.info("optimization_tick active=%s processing=%s", active, processing)
        return {"ok": True, "active_campaigns": active, "processing": processing}
    finally:
        db.close()
