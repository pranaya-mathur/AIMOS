
import logging

from openai import OpenAI

from core.config import get_settings
from db import SessionLocal
from services.usage.context import get_usage_context
from services.usage.quotas import assert_can_consume_tokens, compute_openai_cost_usd, record_openai_usage

logger = logging.getLogger(__name__)


def _get_client():
    settings = get_settings()
    api_key = settings.openai_api_key
    if not api_key:
        if settings.mock_llm_enabled:
            return None # Signal to use mock
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your environment before calling AI agents.")
    return OpenAI(api_key=api_key)


def generate_text(prompt: str) -> str:
    ctx = get_usage_context() or {}
    user_id = ctx.get("user_id")
    campaign_id = ctx.get("campaign_id")

    if user_id:
        db = SessionLocal()
        try:
            assert_can_consume_tokens(db, user_id)
        finally:
            db.close()

    client = _get_client()
    if client is None:
        import json as _json
        logger.info("[MOCK LLM] generate_text bypassed — returning structured mock JSON")
        mock_data = {
            "analysis": "Mock AI analysis: strong market fit and clear value proposition.",
            "strategy": "Focus on digital-first outreach targeting high-intent segments.",
            "brand_positioning": "Premium quality at accessible pricing",
            "confidence_score": 85,
            "strategic_fit": "Excellent",
            "red_flags": [],
            "improvement_tips": ["Expand target audience", "Add seasonal promotions"],
            "competitors": [{"name": "MockCo", "url": "https://mockco.example.com", "positioning": "Budget leader"}],
            "headline": "Grow Your Business with AI-Powered Marketing",
            "body": "Reach the right audience at the right time with intelligent automation.",
            "cta": "Get Started Free",
            "campaign_strategy": "Multi-channel approach with strong social media presence",
            "content_pillars": ["Education", "Inspiration", "Promotion"],
            "target_segment": "Professional services SMBs aged 28-45",
            "budget_allocation": {"social": 40, "search": 35, "display": 25},
            "predicted_roas": 3.2,
            # Brand builder fields
            "brand_narrative": "We exist to empower ambitious brands with intelligent automation, helping them reach the right audiences at the right moment — faster, smarter, and with greater precision than ever before.",
            "brand_voice": "Bold & Authoritative",
            "tone_guidelines": ["Confident", "Innovative", "Direct"],
            "color_palette": ["#8B5CF6", "#06B6D4", "#F59E0B"],
            "typography": "Modern sans-serif with strong contrast",
            "taglines": ["Intelligence. Amplified.", "Automate the Advantage", "Your Brand, Unleashed"],
            "mock": True,
        }
        return _json.dumps(mock_data)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    usage = getattr(resp, "usage", None)
    model_name = getattr(resp, "model", None) or "gpt-4o-mini"
    pt = int(getattr(usage, "prompt_tokens", None) or 0) if usage else 0
    ct = int(getattr(usage, "completion_tokens", None) or 0) if usage else 0
    tt = int(getattr(usage, "total_tokens", None) or (pt + ct)) if usage else 0
    if usage is not None:
        logger.info(
            "openai_usage model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            model_name,
            pt,
            ct,
            tt,
        )

    if user_id and usage is not None:
        cost = compute_openai_cost_usd(prompt_tokens=pt, completion_tokens=ct)
        db = SessionLocal()
        try:
            record_openai_usage(
                db,
                user_id=user_id,
                campaign_id=campaign_id,
                model=model_name,
                prompt_tokens=pt,
                completion_tokens=ct,
                total_tokens=tt,
                cost_usd=cost,
            )
        except Exception:
            logger.exception("failed to record OpenAI usage for user=%s", user_id)
        finally:
            db.close()

    return resp.choices[0].message.content


def generate_json(prompt: str) -> dict:
    """Convenience wrapper for JSON mode with usage tracking."""
    ctx = get_usage_context() or {}
    user_id = ctx.get("user_id")
    campaign_id = ctx.get("campaign_id")

    if user_id:
        db = SessionLocal()
        try:
            assert_can_consume_tokens(db, user_id)
        finally:
            db.close()

    client = _get_client()
    if client is None:
        logger.info("Using mock JSON generation for prompt.")
        # Try to parse the required schema from the prompt
        import json
        schema_hint_start = prompt.find("Required JSON schema shape:\n")
        if schema_hint_start != -1:
            schema_hint = prompt[schema_hint_start + 28:]
            # find end of schema (assuming it's before "Task:")
            schema_end = schema_hint.find("\n\nTask:\n")
            if schema_end != -1:
                schema_str = schema_hint[:schema_end]
                try:
                    schema_def = json.loads(schema_str)
                    mock_result = _generate_mock_from_schema(schema_def)
                    return mock_result
                except json.JSONDecodeError:
                    pass
        return {"mock_status": "enabled", "raw_text": "Mock JSON bypass active."}

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    usage = getattr(resp, "usage", None)
    model_name = getattr(resp, "model", None) or "gpt-4o-mini"
    pt = int(getattr(usage, "prompt_tokens", None) or 0) if usage else 0
    ct = int(getattr(usage, "completion_tokens", None) or 0) if usage else 0
    tt = int(getattr(usage, "total_tokens", None) or (pt + ct)) if usage else 0
    
    if user_id and usage is not None:
        cost = compute_openai_cost_usd(prompt_tokens=pt, completion_tokens=ct)
        db = SessionLocal()
        try:
            record_openai_usage(
                db,
                user_id=user_id,
                campaign_id=campaign_id,
                model=model_name,
                prompt_tokens=pt,
                completion_tokens=ct,
                total_tokens=tt,
                cost_usd=cost,
            )
        except Exception:
            logger.exception("failed to record OpenAI usage for user=%s", user_id)
        finally:
            db.close()

    raw = resp.choices[0].message.content or "{}"
    try:
        import json
        return json.loads(raw)
    except Exception:
        logger.error("failed to parse JSON response from OpenAI: %s", raw)
        return {"raw_text": raw}


def _generate_mock_from_schema(schema: dict) -> dict:
    """Recursively generates mock data conforming to a JSON schema dictionary."""
    result = {}
    for key, val_type in schema.items():
        if isinstance(val_type, dict):
            result[key] = _generate_mock_from_schema(val_type)
        elif isinstance(val_type, list):
            if len(val_type) > 0 and isinstance(val_type[0], str):
                result[key] = [f"Mock {key} 1", f"Mock {key} 2"]
            elif len(val_type) > 0 and isinstance(val_type[0], dict):
                result[key] = [_generate_mock_from_schema(val_type[0])]
            else:
                result[key] = []
        elif val_type == "string":
            if "url" in key.lower():
                result[key] = "https://example.com/mock"
            else:
                result[key] = f"Mock generated {key}"
        elif val_type == "integer" or val_type == "number":
            if "score" in key.lower() or "confidence" in key.lower():
                result[key] = 85
            else:
                result[key] = 42
        elif val_type == "boolean":
            result[key] = True
        else:
            result[key] = str(val_type) # Fallback for literals
    return result
