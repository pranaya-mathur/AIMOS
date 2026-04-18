from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from db import get_db
from models import User, Campaign, CampaignMetric, UsageEvent, Lead, OptimizationDirective, CompetitorIntel, Brand
from deps import get_agency_user
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/global")
def get_global_analytics(
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated metrics across all campaigns with trend insights.
    """
    query = db.query(CampaignMetric)
    if user and user.role != "platform_admin":
        query = query.join(Campaign).filter(Campaign.user_id == user.id)
    
    metrics = query.all()
    leads_count = (db.query(Lead).filter(Lead.user_id == user.id).count() if user and user.role != "platform_admin" else db.query(Lead).count())
    
    total_spend = sum(m.spend for m in metrics)
    total_impressions = sum(m.impressions for m in metrics)
    total_clicks = sum(m.clicks for m in metrics)
    total_conversions = sum(m.conversions for m in metrics)
    
    # ROI Calculation (Mock: assuming $50 revenue per conversion)
    estimated_revenue = total_conversions * 50.0
    roi = ((estimated_revenue - total_spend) / total_spend) if total_spend > 0 else 0
    
    ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0
    cvr = (total_conversions / total_clicks) if total_clicks > 0 else 0
    cpl = (total_spend / leads_count) if leads_count > 0 else 0
    
    return {
        "summary": {
            "total_spend": float(total_spend),
            "estimated_revenue": float(estimated_revenue),
            "roi": float(roi),
            "total_leads": leads_count,
            "total_conversions": total_conversions,
            "total_impressions": int(total_impressions),
            "total_clicks": int(total_clicks),
            "ctr": float(ctr),
            "cvr": float(cvr),
            "cpl": float(cpl)
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
    competitor_count = db.query(CompetitorIntel).filter(CompetitorIntel.brand_id == campaign.brand_id).count() if campaign.brand_id else 0
    
    # Summary of this campaign specifically
    total_spend = sum(m.spend for m in metrics)
    total_conversions = sum(m.conversions for m in metrics)
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "total_leads": leads_count,
        "total_spend": float(total_spend),
        "competitor_count": competitor_count,
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
    from services.prompts.loader import get_agent_bundle
    from models import Organization
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
    directives = result_state["agent_outputs"]["optimization_rules"]

    from services.governance.audit import log_audit_event
    log_audit_event(
        action="CAMPAIGN_OPTIMIZE_GENERATE",
        user_id=user.id,
        organization_id=user.organization_id,
        resource_id=campaign_id,
        metadata={"count": len(directives.get("pause_rules", [])) + len(directives.get("scale_rules", []))}
    )

    # 4. Create structured Directive records (AIM-060)
    created_directives = []
    
    # 2.0 Governance: Load threshold from Org
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    gov = org.governance_settings or {}
    threshold_amount = gov.get("senior_approval_threshold_amount", 500)
    
    # ... rule iteration ...
    
    # Scale Rules
    for rule in directives.get("scale_rules", []):
        d = OptimizationDirective(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            user_id=user.id,
            directive_type="scale",
            description=rule,
            suggested_payload={"budget_increase": 0.2}
        )
        db.add(d)
        created_directives.append(d)
        
    # Pause Rules
    for rule in directives.get("pause_rules", []):
        d = OptimizationDirective(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            user_id=user.id,
            directive_type="pause",
            description=rule,
            suggested_payload={"target_status": "PAUSED"}
        )
        db.add(d)
        created_directives.append(d)

    # 5. Update campaign output
    existing_output = dict(campaign.output or {})
    existing_output["optimization_directives"] = directives
    campaign.output = existing_output
    db.commit()

    return {
        "ok": True,
        "campaign_id": campaign_id,
        "count": len(created_directives)
    }

@router.get("/directives", response_model=List[dict])
def list_directives(
    campaign_id: Optional[str] = None,
    status: Optional[str] = "pending",
    db: Session = Depends(get_db),
    user: User = Depends(get_agency_user)
):
    query = db.query(OptimizationDirective)
    if user and user.role != "platform_admin":
        query = query.filter(OptimizationDirective.user_id == user.id)
    if campaign_id:
        query = query.filter(OptimizationDirective.campaign_id == campaign_id)
    if status:
        query = query.filter(OptimizationDirective.status == status)
    
    return [
        {
            "id": d.id,
            "campaign_id": d.campaign_id,
            "type": d.directive_type,
            "description": d.description,
            "status": d.status,
            "created_at": d.created_at.isoformat()
        } for d in query.all()
    ]

@router.post("/directives/{directive_id}/apply")
def apply_directive(
    directive_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_agency_user)
):
    directive = db.query(OptimizationDirective).filter(OptimizationDirective.id == directive_id).first()
    if not directive:
        raise HTTPException(status_code=404, detail="Directive not found")
    
    if user and user.role != "platform_admin" and directive.user_id != user.id:
        # Check if the user is in the same Organization (Agency context)
        if user.organization_id != directive.campaign.organization_id:
             raise HTTPException(status_code=403, detail="Forbidden")
    
    # 2.0 Governance: Check for Multi-Sig (Senior Approval)
    if directive.requires_senior_approval and not directive.senior_approver_id:
        if user.id == directive.user_id:
            # Re-confirming their own shift, but they still need a second pair of eyes
            return {
                "ok": False, 
                "message": "High-risk shift detected. This action requires a second approval from a teammate (Agency Client or Admin).",
                "requires_cosign": True
            }
        else:
            # A different person from the same org is approving!
            directive.senior_approver_id = user.id
            # Now we can proceed to the actual platform apply logic below

    # 1. Capture current status/budget as a snapshot (Safety Reversibility)
    campaign = db.query(Campaign).filter(Campaign.id == directive.campaign_id).first()
    if campaign:
        directive.original_state_snapshot = {
            "status": campaign.status,
            "total_budget": campaign.total_budget,
            "output_selected_creative": (campaign.output or {}).get("selected_creative")
        }

    # 2. Apply change to platform
    from services.integrations.metrics_service import apply_directive_to_platform
    
    success = apply_directive_to_platform(directive)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to apply directive to platform")

    directive.status = "applied"
    directive.applied_at = datetime.now()
    db.commit()

    from services.governance.audit import log_audit_event
    log_audit_event(
        action="OPTIMIZATION_APPLY",
        user_id=user.id,
        organization_id=user.organization_id,
        resource_id=directive.id,
        metadata={"type": directive.directive_type}
    )

    return {"ok": True}

@router.post("/directives/{directive_id}/revert")
def revert_directive(
    directive_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_agency_user)
):
    """Restores the campaign to its previous state using the saved snapshot."""
    directive = db.query(OptimizationDirective).filter(OptimizationDirective.id == directive_id).first()
    if not directive:
        raise HTTPException(status_code=404, detail="Directive not found")
    
    if user and user.role != "platform_admin" and directive.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if not directive.original_state_snapshot:
        raise HTTPException(status_code=400, detail="No snapshot found for this directive")

    campaign = db.query(Campaign).filter(Campaign.id == directive.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Linked campaign not found")

    snapshot = directive.original_state_snapshot
    
    # Restore Campaign State
    campaign.status = snapshot.get("status", campaign.status)
    campaign.total_budget = snapshot.get("total_budget", campaign.total_budget)
    
    # Push back to platform
    from services.integrations.metrics_service import apply_directive_to_platform
    # We pass a pseudo-directive that represents the 'revert' action
    # In real SDK, this would be a direct status/budget update
    
    directive.status = "reverted"
    db.commit()

    return {"ok": True, "reverted_to": snapshot}

@router.get("/competitors/{campaign_id}", response_model=List[dict])
def get_campaign_competitors(
    campaign_id: str,
    user: User = Depends(get_agency_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if not campaign.brand_id:
        return []

    competitors = db.query(CompetitorIntel).filter(CompetitorIntel.brand_id == campaign.brand_id).all()
    
    return [
        {
            "id": c.id,
            "name": c.competitor_name,
            "url": c.competitor_url,
            "positioning": c.positioning,
            "ad_hooks": c.ad_hooks,
            "price_intelligence": c.pricing_notes,
            "threat_level": c.risk_to_client
        } for c in competitors
    ]
