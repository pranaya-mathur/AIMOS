import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db import get_db
from models import LandingPage, Lead, User

router = APIRouter()

@router.get("/{slug}")
def get_public_page(slug: str, db: Session = Depends(get_db)):
    """Fetch landing page data for public rendering."""
    page = db.query(LandingPage).filter(LandingPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Increment view count
    page.views_count += 1
    db.commit()
    
    return {
        "title": page.title,
        "description": page.description,
        "content": page.content_json,
        "brand_id": page.user_id # Could be used to fetch global brand colors if needed
    }

@router.post("/{slug}/submit")
async def submit_lead_form(slug: str, request: Request, db: Session = Depends(get_db)):
    """Handle form submission from a landing page."""
    page = db.query(LandingPage).filter(LandingPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Create the lead
    lead_id = str(uuid.uuid4())
    
    # Map fields (Generic for MVP)
    # We look for common keys: name, email, phone
    full_name = data.get("full_name") or data.get("name") or data.get("Full Name")
    email = data.get("email") or data.get("Email")
    phone = data.get("phone") or data.get("Phone") or data.get("whatsapp")
    
    new_lead = Lead(
        id=lead_id,
        user_id=page.user_id,
        organization_id=page.organization_id,
        full_name=full_name,
        email=email,
        phone=phone or "unknown", # Lead model requires phone
        status="new",
        score=50, # Initial score
        landing_page_id=page.id,
        source="landing_page",
        lead_metadata=data # Store all raw fields
    )
    
    db.add(new_lead)
    
    # Increment conversions
    page.conversions_count += 1
    db.commit()
    
    return {"status": "ok", "lead_id": lead_id}
