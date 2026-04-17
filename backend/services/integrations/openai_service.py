
import logging

from openai import OpenAI

from core.config import get_settings
from db import SessionLocal
from services.usage.context import get_usage_context
from services.usage.quotas import assert_can_consume_tokens, compute_openai_cost_usd, record_openai_usage

logger = logging.getLogger(__name__)


def _get_client():
    api_key = get_settings().openai_api_key
    if not api_key:
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
