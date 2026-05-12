import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AliasChoices, BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from db import get_db
from deps import get_agency_user
from models import Brand, User

router = APIRouter()


class BrandUpsertBody(BaseModel):
    name: str
    # Legacy / frontend-sent fields
    category: Optional[str] = None
    description: Optional[str] = None
    # Seller Profile (AIM-001-005)
    business_type: Optional[str] = None
    industry: Optional[str] = None
    primary_goal: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("primary_goal", "marketing_goal"),
    )
    monthly_budget: Optional[float] = None
    platform_preference: Optional[list] = Field(default_factory=list)

    @field_validator("platform_preference", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [p.strip() for p in v.split(",") if p.strip()]
        if v is None:
            return []
        return v
    
    # Context & Strategy
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    social_links: dict = Field(default_factory=dict)
    target_audience: dict = Field(default_factory=dict)
    product_details: list = Field(default_factory=list)
    pricing_range: Optional[str] = None
    ai_generated_kit: Optional[dict] = None
    analysis_report: Optional[dict] = None


class BrandResponse(BrandUpsertBody):
    id: str
    user_id: str
    organization_id: Optional[str] = None
    
    @field_validator("platform_preference", mode="before")
    @classmethod
    def ensure_list_from_db(cls, v):
        if isinstance(v, str):
            return [p.strip() for p in v.split(",") if p.strip()]
        if v is None:
            return []
        return v


@router.get("", response_model=BrandResponse)
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


@router.post("", response_model=BrandResponse)
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
    brand.business_type = body.business_type
    brand.industry = body.industry
    brand.primary_goal = body.primary_goal
    brand.monthly_budget = body.monthly_budget
    brand.platform_preference = ", ".join(body.platform_preference) if body.platform_preference else None
    
    brand.logo_url = body.logo_url
    brand.website_url = body.website_url
    brand.social_links = body.social_links
    brand.target_audience = body.target_audience
    brand.product_details = body.product_details
    brand.pricing_range = body.pricing_range
    brand.ai_generated_kit = body.ai_generated_kit
    brand.analysis_report = body.analysis_report
    # Preserve legacy fields
    if hasattr(brand, 'category'): brand.category = body.category or body.business_type
    if hasattr(brand, 'description'): brand.description = body.description

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
    brand_builder_result = run_single_agent("brand_builder", {**brand_context, "business_analyzer": analyzer_result})
    
    kit = brand_builder_result if isinstance(brand_builder_result, dict) else {}
    if not kit:
        kit = {"brand_narrative": "Mock brand narrative generated.", "mock": True}
    
    # 3. Persist the generated kit back to the brand record (AIM-026 to AIM-032 Integration)
    brand.ai_generated_kit = kit
    brand.analysis_report = analyzer_result
    db.commit()
    db.refresh(brand)
    
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

    # Optimized logo prompt: prioritize name and category for cleaner visual identity
    prompt = f"Professional minimalist logo for '{brand.name}'. Industry: {brand.category}. Concept: {brand.description[:100]}..."
    logo_data_uri = generate_logo_tool(prompt)
    if not logo_data_uri:
         raise HTTPException(status_code=500, detail="Logo generation failed")
    
    # Optional: autodownload/persist? For now just return the URI
    return {"logo_url": logo_data_uri}
