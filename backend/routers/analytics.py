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
