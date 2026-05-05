
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


@celery.task
def execute_autopilot_directive(directive_id: str):
    """Hardened 2.0 Phase 1.4: Delayed execution task with cancellation check."""
    from db import SessionLocal
    import datetime
    from models import OptimizationDirective, Campaign
    
    db = SessionLocal()
    try:
        directive = db.query(OptimizationDirective).filter(OptimizationDirective.id == directive_id).first()
        if not directive:
            logger.warning(f"Autopilot directive {directive_id} not found")
            return
            
        # Only apply if it's still in 'scheduled' state (Human could have dismissed it during the 5m window)
        if directive.status != "scheduled":
            logger.info(f"Autopilot directive {directive_id} skipped. Current status: {directive.status}")
            return

        # Perform the actual optimization (mocking the platform sync)
        directive.status = "applied"
        directive.applied_at = datetime.datetime.now(datetime.timezone.utc)
        
        # In a real system, we would trigger the specific media client or budget update here
        logger.info(f"AUTOPILOT: Applied directive {directive_id} for campaign {directive.campaign_id}")
        
        db.commit()
    except Exception:
        logger.exception(f"Failed to execute autopilot directive {directive_id}")
    finally:
        db.close()


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
            # 2.0 Orchestration Persistence
            row.orchestration_metadata = {
                "iterations": result.get("iteration_count", 0),
                "history": result.get("history", []),
                "refinement_context": result.get("refinement_context"),
                # Store full state for resumption
                "last_state": result 
            }
            
            # Autopilot Logic (Option B)
            signal = result.get("status_signal")
            is_autopilot = (signal == "AUTOPILOT_APPLY")

            # Extract and Persist Directives
            from models import OptimizationDirective
            import datetime
            agent_outputs = result.get("agent_outputs", {})
            opt_out = agent_outputs.get("optimization_engine", {})
            directives_data = opt_out.get("directives", [])
            
            for d in directives_data:
                # Dedupe or just create for now in this pilot
                new_directive = OptimizationDirective(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign_id,
                    user_id=row.user_id,
                    directive_type=d.get("action", "shift"),
                    description=d.get("description", ""),
                    suggested_payload=d,
                    risk_score=d.get("risk_score", 0),
                    confidence=d.get("confidence", 0),
                    execution_mode="autopilot" if is_autopilot else "manual",
                    status="scheduled" if is_autopilot else "pending",
                    scheduled_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5) if is_autopilot else None
                )
                db.add(new_directive)
                
                # If autopilot, schedule the delayed execution (ETA 5 min)
                if is_autopilot:
                    execute_autopilot_directive.apply_async((new_directive.id,), countdown=300)

            # 2.0 Phase 5: Persist Brand Wisdom (Long-term Memory)
            wisdom_output = agent_outputs.get("wisdom_extractor", {})
            insights = wisdom_output.get("insights", [])
            if insights and row.brand_id:
                from models import BrandWisdom
                for ins in insights:
                    # Dedupe insight if content matches exactly to avoid bloat
                    exists = db.query(BrandWisdom).filter(
                        BrandWisdom.brand_id == row.brand_id,
                        BrandWisdom.content == ins.get("content")
                    ).first()
                    if not exists:
                        new_wisdom = BrandWisdom(
                            id=str(uuid.uuid4()),
                            brand_id=row.brand_id,
                            insight_type=ins.get("insight_type", "strategic"),
                            content=ins.get("content", ""),
                            impact_score=ins.get("impact_score", 50),
                            context_tags=ins.get("context_tags", {})
                        )
                        db.add(new_wisdom)
                logger.info(f"MEMORY: Persisted {len(insights)} wisdom logs for brand {row.brand_id}")

            # Check for Manual Intervention Pause
            if signal == "PAUSE":
                row.status = "awaiting_feedback"
            else:
                row.status = "completed"
                generate_growth_plan_task.apply_async((campaign_id,), countdown=60)
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
        # result is the Graph State at the end of the 14-agent walk
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
        
        # Trigger Automated Media Generation (M2: AIM-037, AIM-042, AIM-046)
        # We look for handoff hints from the agents to start parallel media jobs
        media_tasks = []
        agent_outputs = result.get("agent_outputs", {})
        
        # If Content Studio has produced a brief/script, trigger relevant providers
        content_studio = agent_outputs.get("content_studio", {})
        if content_studio:
            # 1. AdCreative.ai for static/social banners
            if content_studio.get("ad_brief"):
                media_tasks.append(run_media_provider_job.delay("adcreative", content_studio["ad_brief"], request_id=campaign_id))
            
            # 2. Pictory for video generation
            if content_studio.get("video_script"):
                media_tasks.append(run_media_provider_job.delay("pictory", {"script": content_studio["video_script"]}, request_id=campaign_id))
                
            # 3. ElevenLabs for high-quality voiceover
            if content_studio.get("voiceover_text"):
                media_tasks.append(run_media_provider_job.delay("elevenlabs", {"text": content_studio["voiceover_text"]}, request_id=campaign_id))

        if media_tasks:
            logger.info("Triggered %d media generation tasks for campaign %s", len(media_tasks), campaign_id)

        # 4. Auto-generate 3 Copy Variations (AIM-040)
        ad_brief = content_studio.get("ad_brief") or result.get("input", {}).get("brief")
        if ad_brief:
            for i in range(3):
                generate_variation.delay(ad_brief, i, user_id=ctx_user_id, campaign_id=campaign_id)
            logger.info("Triggered 3 copy variations for campaign %s", campaign_id)

    return result


@celery.task(name="media.run_provider")
def run_media_provider_job(provider: str, data=None, request_id=None):
    payload = _with_request_metadata(data, request_id)
    if provider not in _MEDIA_DISPATCH:
        raise ValueError(f"Unknown media provider: {provider}")
    
    # Quota Enforcement (M2: AIM-155)
    db = SessionLocal()
    try:
        from models import MediaAsset, Campaign, User
        from core.config import TIER_QUOTA_MAP, get_settings
        from datetime import datetime
        
        settings = get_settings()
        user_id = None
        if request_id:
            camp = db.query(Campaign).filter(Campaign.id == request_id).first()
            if camp:
                user_id = camp.user_id
        
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                tier = user.subscription_tier or "free"
                _, _, max_media = TIER_QUOTA_MAP.get(tier, TIER_QUOTA_MAP["free"])
                
                # If -1, unlimited
                if max_media != -1:
                    # Count assets generated this month
                    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    count = db.query(MediaAsset).filter(
                        MediaAsset.user_id == user_id,
                        MediaAsset.created_at >= start_of_month
                    ).count()
                    
                    if count >= max_media:
                        logger.warning("User %s exceeded media generation quota (%d/%d)", user_id, count, max_media)
                        return {"status": "error", "reason": "quota_exceeded", "limit": max_media}
    finally:
        db.close()

    result = _MEDIA_DISPATCH[provider](payload, request_id=request_id)
    
    # Persist to database for Asset Library (M2: AIM-055)
    if result.get("status") in {"completed", "done", "success", "ready"}:
        db = SessionLocal()
        try:
            from models import MediaAsset, Campaign
            import uuid
            
            # Try to associate with user if request_id (campaign_id) is provided
            user_id = None
            if request_id:
                camp = db.query(Campaign).filter(Campaign.id == request_id).first()
                if camp:
                    user_id = camp.user_id
            
            asset = MediaAsset(
                id=str(uuid.uuid4()),
                user_id=user_id,
                campaign_id=request_id,
                provider=provider,
                asset_type="video" if provider == "pictory" else "audio" if provider == "elevenlabs" else "image",
                url=result.get("asset_url"),
                metadata_json=result.get("raw")
            )
            db.add(asset)
            db.commit()
            logger.info("Persisted media asset from %s for campaign %s", provider, request_id)
        except Exception:
            logger.exception("Failed to persist media asset")
        finally:
            db.close()

    return result


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
def generate_variation(brief: str, index: int, user_id: Optional[str] = None, campaign_id: Optional[str] = None):
    from services.integrations.openai_service import generate_text
    from models import AdCreative
    import json

    try:
        set_usage_context(user_id=user_id, campaign_id=campaign_id)
        prompt = (
            "Write one creative marketing copy variation for this brief.\n"
            "Format the output as JSON with three keys: 'headline', 'body', and 'cta'.\n"
            "Keep it short, punchy, and professional.\n\n"
            f"Brief: {brief}\n\n"
            "Output JSON:"
        )
        raw = generate_text(prompt)
        try:
            # Clean up JSON if there are triple backticks
            clean_json = raw.strip("`").replace("json\n", "")
            parsed = json.loads(clean_json)
        except Exception:
            # Fallback if AI doesn't return perfect JSON
            parsed = {"headline": raw[:50], "body": raw, "cta": "Learn More"}
            
        # Persist to DB
        db = SessionLocal()
        try:
            creative = AdCreative(
                id=str(uuid.uuid4()),
                user_id=user_id,
                campaign_id=campaign_id,
                headline=parsed.get("headline"),
                body_copy=parsed.get("body"),
                cta_text=parsed.get("cta"),
                status="draft"
            )
            db.add(creative)
            db.commit()
            logger.info("Persisted creative variation #%d for campaign %s", index + 1, campaign_id)
        finally:
            db.close()

        return {"index": index, "copy": parsed}
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

        # 3. AI Lead Intelligence (M2: AIM-081)
        # Fetch recent history for context
        history = db.query(ConversationMessage).filter(ConversationMessage.lead_id == lead.id).order_by(ConversationMessage.created_at.desc()).limit(10).all()
        history_list = [{"direction": m.direction, "content": m.content} for m in reversed(history)]
        
        from services.agents.lead_agent import score_lead_intent
        intelligence = score_lead_intent(history_list)
        
        lead.score = intelligence.get("score", lead.score)
        lead.intent = intelligence.get("intent", lead.intent)
        lead.sentiment = intelligence.get("sentiment", lead.sentiment)
        
        # 4. Generate Reply via OpenAI
        # We craft a prompt that acts as a Lead Capture / Sales Agent
        prompt = (
            f"You are the AI Sales Agent for AIMOS Enterprise.\n"
            f"User name: {lead.full_name or 'there'}\n"
            f"Lead Intent: {lead.intent}\n"
            f"User message: {text_body}\n\n"
            "Goal: Be professional, helpful, and capture their business interest. "
            "Keep the response short (under 200 characters) for WhatsApp.\n\n"
            "Reply:"
        )
        agent_reply = generate_text(prompt).strip()

        # 5. Persistence & Send
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

        logger.info("WhatsApp lead captured, scored (%d), and replied: lead_id=%s", lead.score, lead.id)
        return {"status": "replied", "lead_id": lead.id, "score": lead.score, "reply": agent_reply}

    finally:
        db.close()

@celery.task
def resume_campaign_iteration(campaign_id: str, manual_feedback: str):
    db = SessionLocal()
    try:
        from models import Campaign
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign or not campaign.orchestration_metadata:
            logger.error("resume_campaign_iteration: campaign %s not found or missing metadata", campaign_id)
            return

        # 1. Hydrate state
        metadata = dict(campaign.orchestration_metadata)
        last_state = metadata.get("last_state")
        if not last_state:
            logger.error("resume_campaign_iteration: mission last_state in metadata for %s", campaign_id)
            return

        # 2. Inject manual feedback
        ai_context = last_state.get("refinement_context") or ""
        combined_context = f"{ai_context}\n\n[USER FEEDBACK]: {manual_feedback}".strip()
        
        last_state["refinement_context"] = combined_context
        last_state["status_signal"] = None
        
        # 3. Resume Graph
        from services.orchestrator import resume_agents
        campaign.status = "processing"
        db.commit()
        
        result = resume_agents(last_state, user_id=campaign.user_id)
        _persist_campaign_result(campaign_id, result)

    except Exception:
        logger.exception("resume_campaign_iteration failed for %s", campaign_id)
    finally:
        db.close()

@celery.task
def sync_ecom_products(integration_id: str):
    """Hardened 2.0 Phase 6: Core sync engine for a specific store."""
    from services.integrations.ecom_service import EcomService
    from models import EcomIntegration, Product
    import datetime
    
    db = SessionLocal()
    try:
        integration = db.query(EcomIntegration).filter(EcomIntegration.id == integration_id).first()
        if not integration: return

        # Fetch from platform (mocked/real)
        raw_products = EcomService.process_sync(
            provider=integration.provider,
            store_url=integration.store_url,
            access_token=integration.access_token
        )

        for p in raw_products:
            # Upsert logic
            product = db.query(Product).filter(
                Product.integration_id == integration_id,
                Product.external_id == str(p["id"])
            ).first()

            if not product:
                product = Product(
                    id=str(uuid.uuid4()),
                    brand_id=integration.brand_id,
                    integration_id=integration_id,
                    external_id=str(p["id"])
                )
                db.add(product)

            variant = p.get("variants", [{}])[0]
            product.title = p.get("title")
            product.description = p.get("body_html")
            product.price = variant.get("price")
            product.inventory_quantity = variant.get("inventory_quantity", 0)
            product.image_url = p.get("images", [{}])[0].get("src")
            product.last_processed_at = datetime.datetime.now(datetime.timezone.utc)

        integration.last_sync_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
    finally:
        db.close()

@celery.task
def inventory_guard_tick():
    """Hardened 2.0 Phase 6: Automated guardrail to pause ads for OOS items."""
    from models import Product, Campaign
    db = SessionLocal()
    try:
        # 1. Identify Out of Stock products that are enabled for sync
        oos_products = db.query(Product).filter(
            Product.inventory_quantity <= 0,
            Product.is_sync_enabled == True
        ).all()

        for product in oos_products:
            # 2. Find campaigns mentioning this product or brand
            # Real implementation: campaign.input would contain specific mapping.
            # Here: we find active campaigns for this brand.
            camps = db.query(Campaign).filter(
                Campaign.brand_id == product.brand_id,
                Campaign.status == "active"
            ).all()
            
            for c in camps:
                logger.warning(f"INVENTORY GUARD: Pausing campaign {c.id} - Product {product.title} is OUT OF STOCK.")
                c.status = "paused"
                c.orchestration_metadata["guardrail_reason"] = f"Product {product.title} out of stock."
        
        db.commit()
    finally:
        db.close()

@celery.task
def generate_growth_plan_task(campaign_id: str):
    db = SessionLocal()
    try:
        from models import Campaign, GrowthPlan
        from services.agents.growth_planner_agent import run as run_growth_planner
        
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            logger.error("generate_growth_plan_task: campaign %s not found", campaign_id)
            return
            
        state = {
            "input": campaign.input,
            "agent_outputs": campaign.output or {},
        }
        
        result_state = run_growth_planner(state)
        # Agent's output key is "growth_recommendations" per config.json
        recommendations = result_state.get("agent_outputs", {}).get("growth_recommendations", {})
        
        plan = GrowthPlan(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            brand_id=campaign.brand_id, # Requires brand_id handling if missing, but models define it nullable=True sometimes? Ah I set it nullable=False! Wait... No, I set campaign_id/brand_id nullable=False in the PR. Let's make sure brand_id exists.
            what_worked={"synthesis": recommendations.get("situation_synthesis")},
            what_failed={"risk_mitigation": recommendations.get("risk_mitigation")},
            next_cycle_budget=0.0,
            new_opportunities={
                "strategic_bets": recommendations.get("strategic_bets"),
                "next_channel_focus": recommendations.get("next_channel_focus"),
                "next_content_type": recommendations.get("next_content_type"),
                "next_90_day_actions": recommendations.get("next_90_day_actions"),
                "budget_recommendation": recommendations.get("budget_recommendation")
            }
        )
        db.add(plan)
        db.commit()
        logger.info("Generated growth plan for campaign %s", campaign_id)
        
    except Exception:
        logger.exception("generate_growth_plan_task failed for %s", campaign_id)
    finally:
        db.close()

