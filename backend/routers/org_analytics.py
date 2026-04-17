from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from db import get_db
from models import User, Campaign, CampaignMetric, Brand
from deps import get_agency_user

router = APIRouter()

@router.get("/summary")
def get_enterprise_summary(
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    """
    Hardened 2.0 Phase 7: Aggregated Enterprise Dashboard.
    Shows performance across all Brands in the Organization.
    """
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="Organization required for enterprise analytics")

    # 1. Fetch all Brands in Org
    brand_ids = [b.id for b in db.query(Brand.id).filter(Brand.organization_id == user.organization_id).all()]
    
    # 2. Fetch all Campaigns for these brands
    campaign_ids = [c.id for c in db.query(Campaign.id).filter(Campaign.brand_id.in_(brand_ids)).all()]
    
    # 3. Aggregate Metrics
    summary = db.query(
        func.sum(CampaignMetric.spend).label("total_spend"),
        func.sum(CampaignMetric.impressions).label("total_impressions"),
        func.sum(CampaignMetric.clicks).label("total_clicks"),
        func.sum(CampaignMetric.conversions).label("total_conversions")
    ).filter(CampaignMetric.campaign_id.in_(campaign_ids)).first()

    total_spend = float(summary.total_spend or 0)
    total_conversions = int(summary.total_conversions or 0)
    
    # 4. ROAS Calculation (Mock: $50 per conversion)
    revenue = total_conversions * 50.0
    roas = (revenue / total_spend) if total_spend > 0 else 0

    return {
        "organization_id": user.organization_id,
        "brand_count": len(brand_ids),
        "campaign_count": len(campaign_ids),
        "metrics": {
            "total_spend": total_spend,
            "total_conversions": total_conversions,
            "total_revenue": revenue,
            "roas": roas,
            "avg_cpa": (total_spend / total_conversions) if total_conversions > 0 else 0
        }
    }

@router.get("/portfolio")
def get_brand_portfolio(
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    """Lists all brands in the org with their high-level health score."""
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="Organization required")

    brands = db.query(Brand).filter(Brand.organization_id == user.organization_id).all()
    
    portfolio = []
    for b in brands:
        campaign_count = db.query(Campaign).filter(Campaign.brand_id == b.id).count()
        portfolio.append({
            "brand_id": b.id,
            "name": b.name,
            "industry": b.industry,
            "campaign_count": campaign_count,
            "status": "healthy" if campaign_count > 0 else "onboarding"
        })
        
    return portfolio
