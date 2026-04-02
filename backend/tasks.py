
import logging
from typing import Optional, Union

import uuid
from celery_app import celery
from db import SessionLocal
from models import Campaign, Lead, ConversationMessage, CampaignMetric
from services.orchestrator import run_agents
from services.usage.context import clear_usage_context, set_usage_context
from services.integrations.media_clients import (
    create_adcreative,
    create_elevenlabs_voiceover,
    create_pictory_video,
)
from services.integrations.google_ads import create_campaign
from services.integrations.social_x import post_tweet
from services.integrations.engagement_email import send_email
from services.integrations.engagement_sms import send_sms

logger = logging.getLogger(__name__)

_MEDIA_DISPATCH = {
    "adcreative": create_adcreative,
    "pictory": create_pictory_video,
    "elevenlabs": create_elevenlabs_voiceover,
}


def _with_request_metadata(data: Optional[dict], request_id: Optional[str]) -> dict:
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
    import time
    start_time = time.time()
    
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
        # result is the Graph State at the end of the 12-agent walk
        result = run_agents(inner, user_id=ctx_user_id)
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

    # Calculate duration and build a professional summary for the Bubble/Dashboard response
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Extract total tokens and cost from the UsageEvent table for this campaign
    tokens = 0
    cost = 0
    db = SessionLocal()
    try:
        from sqlalchemy import func
        from models import UsageEvent
        row = db.query(
            func.sum(UsageEvent.total_tokens).label("tokens"),
            func.sum(UsageEvent.cost_usd).label("cost")
        ).filter(UsageEvent.campaign_id == campaign_id).first()
        if row and row.tokens:
            tokens = int(row.tokens)
            cost = float(row.cost or 0)
    except Exception:
        logger.warning("Could not calculate usage for campaign %s", campaign_id)
    finally:
        db.close()

    # Enrichment for the final JSON result
    result["status"] = "SUCCESS"
    result["duration_ms"] = duration_ms
    result["campaign_id"] = campaign_id
    
    # Generate a professional summary string
    roi_hint = "high" # Fallback if ROI is not easily parsed
    result["summary"] = f"Campaign processed successfully. Total tokens: {tokens:,}. Estimated cost: ${cost:.2f}. Strategy ready for launch."

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
def send_google_ads_task(campaign_name: str, customer_id=None):
    return create_campaign(campaign_name=campaign_name, customer_id=customer_id)


@celery.task
def post_social_task(text: str):
    return post_tweet(text=text)


@celery.task
def send_engagement_email_task(to_email: str, subject: str, body: str):
    return send_email(to_email=to_email, subject=subject, body=body)


@celery.task
def send_engagement_sms_task(to_phone: str, body: str):
    return send_sms(to_phone=to_phone, body=body)


@celery.task
def generate_variation(brief: str, index: int, user_id: Optional[str] = None):
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
    """
    Scheduled job: Fetch real metrics for all active campaigns and run AI optimization.
    """
    from services.integrations.metrics_service import fetch_campaign_performance, get_platform_for_campaign
    from services.agents.agent_runner import run_agent
    from services.prompts.loader import get_agent_bundle

    db = SessionLocal()
    try:
        active_campaigns = db.query(Campaign).filter(Campaign.status == "active").all()
        logger.info("optimization_tick found %s active campaigns", len(active_campaigns))

        results = []
        for campaign in active_campaigns:
            # 1. Fetch metrics
            platform = get_platform_for_campaign(campaign.input)
            perf = fetch_campaign_performance(campaign.id, platform)

            # 2. Persist metrics
            metric_row = CampaignMetric(
                id=str(uuid.uuid4()),
                campaign_id=campaign.id,
                day=perf["day"],
                platform=perf["platform"],
                spend=perf["spend"],
                impressions=perf["impressions"],
                clicks=perf["clicks"],
                conversions=perf["conversions"],
            )
            db.add(metric_row)

            # 3. Run Optimization Engine
            bundle = get_agent_bundle("optimization_engine")

            # Context for the agent: current input + current metrics
            state = {
                "input": campaign.input,
                "agent_outputs": {
                    "current_metrics": perf
                }
            }

            result_state = run_agent(
                state,
                name=bundle["agent_name"],
                output_key=bundle["output_key"],
                schema=bundle["schema"],
                prompt_template=bundle["task_template"]
            )

            directives = result_state["agent_outputs"]["optimization_engine"]

            # 4. Update campaign output with directives
            existing_output = dict(campaign.output or {})
            existing_output["optimization_directives"] = directives
            campaign.output = existing_output

            results.append({"campaign_id": campaign.id, "status": "optimized"})

        db.commit()
        return {"ok": True, "optimized_count": len(results), "results": results}
    except Exception:
        logger.exception("optimization_tick failed")
        raise
    finally:
        db.close()


@celery.task
def process_whatsapp_inbound(body: dict):
    """
    Handle incoming WhatsApp message JSON from Meta.
    1. Extract message & sender
    2. Upsert Lead
    3. Save Inbound Message
    4. Generate AI Reply
    5. Save & Send Outbound Message
    """
    from services.integrations.whatsapp_cloud import send_text_message
    from services.integrations.openai_service import generate_text

    # Meta JSON navigation: entry[0].changes[0].value.messages[0]
    try:
        # Standard Meta Webhook structure for WhatsApp Cloud API
        value = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        message = value.get("messages", [{}])[0]
        contacts = value.get("contacts", [{}])[0]

        sender_phone = message.get("from")
        sender_name = contacts.get("profile", {}).get("name")
        text_body = message.get("text", {}).get("body")

        if not sender_phone or not text_body:
            logger.info("WhatsApp webhook: no text body/sender found in data, ignoring.")
            return {"status": "ignored"}

    except (IndexError, KeyError, TypeError):
        logger.error("WhatsApp webhook: failed to parse Meta message structure")
        return {"status": "error", "reason": "parse_failure"}

    db = SessionLocal()
    try:
        # 1. Lead Management
        lead = db.query(Lead).filter(Lead.phone == sender_phone).first()
        if not lead:
            lead = Lead(
                id=str(uuid.uuid4()),
                phone=sender_phone,
                full_name=sender_name,
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)

        # 2. Save Inbound Message
        inbound = ConversationMessage(
            id=str(uuid.uuid4()),
            lead_id=lead.id,
            direction="inbound",
            content=text_body,
        )
        db.add(inbound)

        # 3. Generate Reply via OpenAI
        # We craft a prompt that acts as a Lead Capture / Sales Agent
        prompt = (
            f"You are the AI Sales Agent for AIMOS Enterprise.\n"
            f"User name: {lead.full_name or 'there'}\n"
            f"User message: {text_body}\n\n"
            "Goal: Be professional, helpful, and capture their business interest. "
            "Keep the response short (under 200 characters) for WhatsApp.\n\n"
            "Reply:"
        )
        agent_reply = generate_text(prompt).strip()

        # 4. Persistence & Send
        outbound = ConversationMessage(
            id=str(uuid.uuid4()),
            lead_id=lead.id,
            direction="outbound",
            content=agent_reply,
        )
        db.add(outbound)
        db.commit()

        # Call the real/mock WhatsApp service
        send_text_message(to_e164=sender_phone, body=agent_reply)

        logger.info("WhatsApp lead captured and replied: lead_id=%s", lead.id)
        return {"status": "replied", "lead_id": lead.id, "reply": agent_reply}

    finally:
        db.close()
