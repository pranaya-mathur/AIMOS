import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from deps import get_agency_user
from models import LandingPage, User, Brand
from services.orchestrator import run_single_agent

router = APIRouter()

class LandingPageSchema(BaseModel):
    id: str
    slug: str
    title: str
    description: Optional[str]
    content_json: dict
    is_published: str
    views_count: int
    conversions_count: int

    class Config:
        from_attributes = True

class CreateLandingPageBody(BaseModel):
    title: str
    slug: Optional[str] = None
    content_json: Optional[dict] = Field(default_factory=dict)

class UpdateLandingPageBody(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content_json: Optional[dict] = None
    is_published: Optional[str] = None

@router.get("", response_model=List[LandingPageSchema])
def list_landing_pages(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    query = db.query(LandingPage)
    if user and user.role != "platform_admin":
        query = query.filter(LandingPage.user_id == user.id)
    return query.all()

@router.post("/generate")
def generate_landing_page(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Uses AI to generate a high-converting landing page based on brand context."""
    if not user:
        raise HTTPException(status_code=401, detail="Auth required")
    
    brand = db.query(Brand).filter(Brand.user_id == user.id).first()
    if not brand:
        raise HTTPException(status_code=400, detail="Brand profile required before generation")

    # Call AI agent for lead capture strategy
    # We pass the brand kit to the agent
    agent_input = {
        "brand_profile": {
            "name": brand.name,
            "category": brand.category,
            "description": brand.description,
            "ai_brand_kit": brand.ai_generated_kit
        }
    }
    
    ai_result = run_single_agent("lead_capture", agent_input)
    lead_system = ai_result.get("agent_outputs", {}).get("lead_system", {})
    
    if not lead_system:
        raise HTTPException(status_code=500, detail="AI generation failed to produce lead system")

    # Map AI output to LandingPage structure
    # Above fold copy usually has headline/subhead
    copy = lead_system.get("above_the_fold_copy", ["Join Us", "Success awaits", "Get Started"])
    headline = copy[0] if len(copy) > 0 else "Welcome"
    subhead = copy[1] if len(copy) > 1 else ""
    cta = copy[2] if len(copy) > 2 else "Contact Us"

    sections = [
        {
            "type": "hero",
            "content": {
                "headline": headline,
                "subheadline": subhead,
                "cta_text": cta,
                "background_color": brand.ai_generated_kit.get("color_palette", ["#6366f1"])[0] if brand.ai_generated_kit else "#6366f1"
            }
        },
        {
            "type": "features",
            "content": {
                "title": "Why Choose Us",
                "items": lead_system.get("landing_page_outline", ["Premium Service", "Global Reach", "Expert Support"])
            }
        },
        {
            "type": "form",
            "content": {
                "title": "Claim Your Offer",
                "fields": lead_system.get("form_fields", ["Name", "Email", "Phone"])
            }
        }
    ]

    new_id = str(uuid.uuid4())
    slug = f"page-{str(uuid.uuid4())[:8]}"
    
    page = LandingPage(
        id=new_id,
        user_id=user.id,
        organization_id=user.organization_id,
        slug=slug,
        title=f"AI Generated: {headline[:30]}...",
        content_json={"sections": sections, "theme": "premium"},
        is_published="false"
    )
    
    db.add(page)
    db.commit()
    return {"id": new_id, "slug": slug, "preview": lead_system}

@router.patch("/{page_id}")
def update_landing_page(
    page_id: str,
    body: UpdateLandingPageBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    page = db.query(LandingPage).filter(LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if user and user.role != "platform_admin" and page.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if body.title is not None: page.title = body.title
    if body.slug is not None: page.slug = body.slug
    if body.content_json is not None: page.content_json = body.content_json
    if body.is_published is not None: page.is_published = body.is_published

    db.commit()
    return {"ok": True}

@router.delete("/{page_id}")
def delete_landing_page(
    page_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    page = db.query(LandingPage).filter(LandingPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if user and user.role != "platform_admin" and page.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db.delete(page)
    db.commit()
    return {"ok": True}
