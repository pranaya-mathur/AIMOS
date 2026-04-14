import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from deps import get_agency_user
from models import Brand, User

router = APIRouter()


class BrandUpsertBody(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    social_links: dict = Field(default_factory=dict)
    target_audience: dict = Field(default_factory=dict)
    product_details: list = Field(default_factory=list)
    pricing_range: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    marketing_goal: Optional[str] = None
    monthly_budget: Optional[float] = None
    platform_preference: list = Field(default_factory=list)


@router.get("")
def get_brand(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Retrieve the brand profile for the current user/org."""
    if user is None:
        # For local dev with AUTH_DISABLED
        brand = db.query(Brand).first()
    elif user.organization_id:
        brand = db.query(Brand).filter(Brand.organization_id == user.organization_id).first()
    else:
        brand = db.query(Brand).filter(Brand.user_id == user.id).first()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    return brand


@router.post("")
def upsert_brand(
    body: BrandUpsertBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Create or update the brand profile."""
    if user is None:
        # Local dev fallback
        brand = db.query(Brand).first()
    elif user.organization_id:
        brand = db.query(Brand).filter(Brand.organization_id == user.organization_id).first()
    else:
        brand = db.query(Brand).filter(Brand.user_id == user.id).first()

    if not brand:
        fallback_user_id = "dev-user"
        if not user:
            first_user = db.query(User).first()
            if first_user:
                fallback_user_id = first_user.id
        
        brand = Brand(
            id=str(uuid.uuid4()),
            user_id=user.id if user else fallback_user_id,
            organization_id=user.organization_id if user else None,
        )
        db.add(brand)

    # Update fields
    brand.name = body.name
    brand.category = body.category
    brand.description = body.description
    brand.logo_url = body.logo_url
    brand.website_url = body.website_url
    brand.social_links = body.social_links
    brand.target_audience = body.target_audience
    brand.product_details = body.product_details
    brand.pricing_range = body.pricing_range
    brand.business_type = body.business_type
    brand.industry = body.industry
    brand.marketing_goal = body.marketing_goal
    brand.monthly_budget = body.monthly_budget
    brand.platform_preference = body.platform_preference

    db.commit()
    db.refresh(brand)
    return brand


@router.post("/generate-kit")
def generate_brand_kit(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """
    Runs the AI Business Analyzer and AI Brand Builder agents to generate a 
    consistent brand identity based on existing profile data.
    """
    from services.orchestrator import run_single_agent
    
    if user is None:
        brand = db.query(Brand).first()
    elif user.organization_id:
        brand = db.query(Brand).filter(Brand.organization_id == user.organization_id).first()
    else:
        brand = db.query(Brand).filter(Brand.user_id == user.id).first()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found. Complete onboarding first.")

    from services.governance.audit import log_audit_event
    log_audit_event(
        action="BRAND_KIT_GENERATE",
        user_id=user.id if user else "dev-user",
        organization_id=user.organization_id if user else None,
        resource_id=brand.id
    )

    # 1. Gather context
    brand_context = {
        "name": brand.name,
        "category": brand.category,
        "description": brand.description,
        "target_audience": brand.target_audience,
        "marketing_goal": brand.marketing_goal,
        "business_type": brand.business_type,
        "industry": brand.industry,
        "pricing_range": brand.pricing_range
    }

    # 2. Run agents sequentially to build strategy then brand
    # Business Analyzer (Strategy)
    analyzer_result = run_single_agent("business_analyzer", brand_context)
    
    # Brand Builder (Identity) - consumes analyzer output via context
    agent_outputs = {"business_analyzer": analyzer_result}
    brand_builder_state = {"input": brand_context, "agent_outputs": agent_outputs}
    
    from services.agents.brand_builder_agent import run as run_brand_builder
    final_state = run_brand_builder(brand_builder_state)
    
    kit = final_state["brand_kit"]
    
    # 3. Persist the generated kit back to the brand record
    # For now we'll store specific fields or just a generic 'ai_generated_kit' JSON
    # Let's add an 'ai_generated_kit' field to models.py if not there, or reuse existing fields.
    # Since we don't have that field, I'll update the existing description and other fields 
    # if they are empty, but it's better to return it to the frontend for approval.
    
    return {
        "strategy": analyzer_result,
        "brand_kit": kit
    }


@router.post("/logo")
def generate_brand_logo(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Generates a logo based on the brand description using Stability AI."""
    from services.integrations.stability_ai import generate_logo_tool
    
    if user is None:
        brand = db.query(Brand).first()
    elif user.organization_id:
        brand = db.query(Brand).filter(Brand.organization_id == user.organization_id).first()
    else:
        brand = db.query(Brand).filter(Brand.user_id == user.id).first()

    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found.")

    prompt = f"Logo for {brand.name}: {brand.category}. {brand.description}"
    logo_data_uri = generate_logo_tool(prompt)
    if not logo_data_uri:
         raise HTTPException(status_code=500, detail="Logo generation failed")
    
    # Optional: autodownload/persist? For now just return the URI
    return {"logo_url": logo_data_uri}
