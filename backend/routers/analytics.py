from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from db import get_db
from models import User, Campaign, CampaignMetric, UsageEvent, Lead
from deps import get_agency_user

router = APIRouter()

@router.get("/global")
def get_global_analytics(
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated metrics across all campaigns the user has access to.
    Useful for top-level Bubble dashboards.
    """
    query = db.query(CampaignMetric)
    
    # RBAC: Organization-level filtering logic
    if user and user.role != "platform_admin":
        query = query.join(Campaign).filter(Campaign.user_id == user.id)
    # If no user (AUTH_DISABLED=1), we return all metrics in this test environment.
    
    metrics = query.all()
    
    total_spend = sum(m.spend for m in metrics)
    total_impressions = sum(m.impressions for m in metrics)
    total_clicks = sum(m.clicks for m in metrics)
    total_conversions = sum(m.conversions for m in metrics)
    
    ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0
    cvr = (total_conversions / total_clicks) if total_clicks > 0 else 0
    
    return {
        "summary": {
            "total_spend": float(total_spend),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "ctr": float(ctr),
            "cvr": float(cvr)
        },
        "campaign_count": (db.query(Campaign).filter(Campaign.user_id == user.id).count() if user and user.role != "platform_admin" else db.query(Campaign).count())
    }

@router.get("/usage")
def get_usage_analytics(
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    """
    Aggregates AI token usage and estimated costs.
    """
    query = db.query(UsageEvent)
    if user and user.role != "platform_admin":
        query = query.filter(UsageEvent.user_id == user.id)
    
    events = query.all()
    total_tokens = sum(e.total_tokens for e in events)
    total_cost = sum(e.cost_usd or 0 for e in events)
    
    # Grouping by provider and model
    breakdown = {}
    for e in events:
        key = f"{e.provider}/{e.model or 'unknown'}"
        if key not in breakdown:
            breakdown[key] = {"tokens": 0, "cost": 0.0}
        breakdown[key]["tokens"] += e.total_tokens
        breakdown[key]["cost"] += float(e.cost_usd or 0)
        
    return {
        "total_tokens": total_tokens,
        "total_cost_usd": float(total_cost),
        "breakdown": breakdown
    }

@router.get("/campaign/{campaign_id}")
def get_campaign_analytics(
    campaign_id: str,
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    """
    Returns detailed metrics and lead counts for a specific campaign.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if user and user.role != "platform_admin" and campaign.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    metrics = db.query(CampaignMetric).filter(CampaignMetric.campaign_id == campaign_id).order_by(CampaignMetric.day).all()
    leads_count = db.query(Lead).filter(Lead.campaign_id == campaign_id).count()
    
    # Summary of this campaign specifically
    total_spend = sum(m.spend for m in metrics)
    total_conversions = sum(m.conversions for m in metrics)
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "total_leads": leads_count,
        "total_spend": float(total_spend),
        "cost_per_lead": float(total_spend / leads_count) if leads_count > 0 else 0,
        "daily_performance": [
            {
                "day": m.day.isoformat(),
                "platform": m.platform,
                "spend": float(m.spend),
                "conversions": m.conversions
            } for m in metrics
        ]
    }

@router.post("/optimize/{campaign_id}", tags=["analytics"])
def trigger_campaign_optimization(
    campaign_id: str,
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    """
    Manually triggers the AI Optimization Engine for a campaign.
    Fetches latest metrics and runs the 'optimization_engine' agent.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if user and user.role != "platform_admin" and campaign.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    from services.integrations.metrics_service import fetch_campaign_performance, get_platform_for_campaign
    from services.agents.agent_runner import run_agent
    from services.prompts.loader import get_agent_bundle
    import uuid

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

    # 4. Update
    existing_output = dict(campaign.output or {})
    existing_output["optimization_directives"] = directives
    campaign.output = existing_output
    db.commit()

    return {
        "ok": True,
        "campaign_id": campaign_id,
        "directives": directives
    }
