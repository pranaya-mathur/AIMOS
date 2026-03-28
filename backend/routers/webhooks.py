import os
import logging
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import Response

# Deferred import to avoid circular dependency issues if any
from tasks import process_whatsapp_inbound

router = APIRouter()
logger = logging.getLogger(__name__)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "aimos-default-verify-token")

@router.get("/whatsapp")
async def verify_whatsapp(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Meta Webhook verification loop.
    Meta sends a GET request to verify the webhook URL.
    """
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return Response(content=hub_challenge)
    
    logger.warning("WhatsApp webhook verification failed: %s vs %s", hub_verify_token, VERIFY_TOKEN)
    raise HTTPException(status_code=403, detail="Verification token mismatch")

@router.post("/whatsapp")
async def receive_whatsapp(request: Request):
    """
    Receive incoming messages from WhatsApp Cloud API.
    Enqueues the processing to a background Celery worker.
    """
    try:
        body = await request.json()
    except Exception:
        logger.error("Failed to parse WhatsApp webhook JSON")
        return {"status": "error", "message": "invalid JSON"}

    # Log briefly for debugging
    logger.debug("WhatsApp webhook received: %s", body)

    # Process asynchronously to ensure we return 200 OK to Meta quickly
    process_whatsapp_inbound.delay(body)
    
    return {"status": "ok"}
